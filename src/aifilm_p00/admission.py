"""D00-07 durable journal/fence protocol with injected storage and guard ports.
MemoryGuard/MemoryStorage are test doubles only, not Windows host coordination.
No wall-clock expiry or automatic deletion of unresolved fences.
"""
from copy import deepcopy
from dataclasses import asdict
from typing import Protocol
from .authority import Admission
from .codec import digest,token
from .errors import P00Error,require

GUARD_NAME='AI-FILM-P00-HOST-ADMISSION'
TERMINAL_STATES={'TERMINAL','SAFE_PAUSE'}

class Guard(Protocol):
    def acquire(self)->bool: ...
    def release(self)->None: ...

class Storage(Protocol):
    def load_fence(self)->dict|None: ...
    def write_fence(self,record:dict)->None: ...
    def append_event(self,event:dict)->None: ...
    def clear_fence(self)->None: ...

class Coordinator:
    """Synchronous admission. Only original run may inspect/reconcile a live fence."""
    def __init__(self,guard:Guard,storage:Storage):
        self.guard=guard; self.storage=storage; self.held=False; self.admission=None; self.fence=None

    def acquire(self,authority:Admission,*,reconciliation=False):
        require(not self.held,21,'NESTED_ADMISSION_FORBIDDEN')
        require(self.guard.acquire(),21,'LOCK_BUSY')
        self.held=True; self.admission=authority
        try:
            self.fence=self.storage.load_fence()
            if self.fence is not None:
                require(reconciliation,21,'UNRESOLVED_FENCE')
                require(self.fence.get('run_id')==authority.run_id and self.fence.get('owner_sid')==authority.owner_sid and self.fence.get('host_id')==authority.host_id and self.fence.get('plan_digest')==authority.plan_digest,12,'RECONCILIATION_ACTOR')
                require(authority.purpose=='RECONCILIATION_ONLY',12,'RECONCILIATION_SCOPE')
            else:
                require(not reconciliation,11,'NO_FENCE_TO_RECONCILE')
                if hasattr(self.storage,'admission_check'):self.storage.admission_check()
        except BaseException:
            self.guard.release(); self.held=False; raise
        return self

    def acquire_bound_reconciliation(self, preliminary, request, context, store, *, allow_detached=False):
        """Acquire once, then bind the immutable original fence under that guard.

        No unlocked journal read and no temporarily cleared fence. No active
        original operation is executed by this read-only reconciliation entry.
        """
        from .resume import bind_reconciliation
        require(not self.held,21,'NESTED_ADMISSION_FORBIDDEN')
        require(preliminary.purpose=='RECONCILIATION_ONLY',12,'RECONCILIATION_SCOPE')
        require(self.guard.acquire(),21,'LOCK_BUSY')
        self.held=True
        try:
            self.fence=self.storage.load_fence()
            if self.fence is None and allow_detached:
                from .read_recovery import bind_read_recovery
                binding=bind_read_recovery(request,context,store,self.storage.read_events())
                self.read_recovery_binding=binding
            else:
                require(self.fence is not None,11,'NO_FENCE_TO_RECONCILE')
                binding=bind_reconciliation(request,context,store,self.fence)
                self.reconciliation_binding=binding
            self.admission=binding.authority
        except BaseException:
            self.guard.release(); self.held=False; raise
        return self

    def acquire_bound_read_recovery(self, preliminary, request, context, store):
        """Original-request C0 reconciliation when no mutation fence exists.

        Never invent a fence to satisfy another entry's assumptions. New reads
        on another run may not be cleaned up by an actor owning only this run.
        """
        from .read_recovery import bind_read_recovery
        require(not self.held, 21, 'NESTED_ADMISSION_FORBIDDEN')
        require(preliminary.purpose == 'RECONCILIATION_ONLY', 12, 'RECONCILIATION_SCOPE')
        require(self.guard.acquire(), 21, 'LOCK_BUSY')
        self.held = True
        try:
            self.fence = self.storage.load_fence()
            require(self.fence is None, 21, 'MUTATION_FENCE_REQUIRES_ORIGINAL_RECOVERY')
            bound = bind_read_recovery(request, context, store, self.storage.read_events())
            self.read_recovery_binding = bound
            self.admission = bound.authority
        except BaseException:
            self.guard.release(); self.held = False
            raise
        return self

    def intent(self,action:str,reservations:list,witness:dict):
        require(self.held and self.admission is not None,18,'GUARD_NOT_HELD')
        require(self.fence is None,21,'UNRESOLVED_FENCE')
        token(action)
        required={'host_boot','controller_pid','controller_start','build_digest','step_id'}
        require(type(witness) is dict and required<=set(witness) and all(witness[k] is not None for k in required),11,'PROCESS_WITNESS_MISSING')
        a=self.admission
        self.fence={'schema_version':1,'guard_name':GUARD_NAME,'run_id':a.run_id,'host_id':a.host_id,'owner_sid':a.owner_sid,
                    'plan_digest':a.plan_digest,'action':action,'state':'INTENT','reservations':deepcopy(reservations),'witness':deepcopy(witness),'native':None,'event_sequence':0}
        self.storage.write_fence(self.fence)
        self._event('INTENT')

    def native_started(self,native_witness:dict):
        self._require_fence()
        require(self.fence['state']=='INTENT',18,'INVALID_FENCE_TRANSITION')
        require(type(native_witness) is dict and {'pid','start','action_id'}<=set(native_witness),11,'NATIVE_WITNESS_MISSING')
        self.fence['native']=deepcopy(native_witness); self.fence['state']='RUNNING'; self._persist('NATIVE_STARTED')

    def native_child_started(self,native_witness:dict):
        self._require_fence()
        require(self.fence['state']=='RUNNING' and self.fence['native'] is not None,18,'INVALID_FENCE_TRANSITION')
        require(type(native_witness) is dict and {'pid','start','action_id'}<=set(native_witness),11,'NATIVE_WITNESS_MISSING')
        witnesses=[self.fence['native'],*self.fence['native'].get('additional',[])]
        require(all((w['pid'],w['start'])!=(native_witness['pid'],native_witness['start']) for w in witnesses),15,'DUPLICATE_NATIVE_WITNESS')
        require(len(witnesses)<64,18,'NATIVE_WITNESS_CAP')
        self.fence['native'].setdefault('additional',[]).append(deepcopy(native_witness))
        self._persist('NATIVE_CHILD_STARTED')

    def uncertain(self,reason='NATIVE_TIMEOUT'):
        self._require_fence(); token(reason)
        self.fence['state']='UNCERTAIN'; self.fence['reason']=reason; self._persist('UNCERTAIN')

    def awaiting(self,kind:str):
        self._require_fence()
        require(kind in ('AWAITING_REBOOT','AWAITING_USER_INIT','AWAITING_OWNER_VERIFICATION'),10,'INVALID_PAUSE')
        self.fence['state']=kind; self._persist(kind)

    def terminal(self,observation:dict):
        self._require_fence()
        self._terminal_proof(observation)
        self.fence['state']='TERMINAL'; self.fence['terminal_observation']=deepcopy(observation)
        self._persist('TERMINAL')
        self.storage.clear_fence(); self.fence=None

    def reconcile(self,observation:dict):
        self._require_fence()
        require(self.admission.purpose=='RECONCILIATION_ONLY',12,'RECONCILIATION_SCOPE')
        self.terminal(observation)

    def safe_pause(self, observation: dict):
        self._require_fence()
        require(self.admission.purpose == 'RECONCILIATION_ONLY', 12,'RECONCILIATION_SCOPE')
        require(type(observation) is dict and observation.get('action') == self.fence['action'],19, 'PAUSE_ACTION_MISMATCH')
        require(observation.get('disposition') in ('PAUSE', 'CANCEL'), 10, 'PAUSE_DISPOSITION')
        require(observation.get('no_pending_writer') is True and observation.get('pending_operations_revoked') is True and observation.get('terminal_observed') is False and observation.get('postconditions_observed') is False,21, 'SAFE_PAUSE_NOT_PROVEN')
        from .codec import hash_value
        for key in ('evidence_digest', 'revocation_ref', 'request_digest'):
            hash_value(observation.get(key))
        require(observation.get('native_witness') == self.fence.get('native'),19, 'NATIVE_WITNESS_MISMATCH')
        self.fence['state'] = 'SAFE_PAUSE'
        self.fence['pause_observation'] = deepcopy(observation)
        self._persist('SAFE_PAUSE')
        self.storage.clear_fence()
        self.fence = None

    def _terminal_proof(self,observation):
        require(type(observation) is dict and observation.get('action')==self.fence['action'],19,'TERMINAL_ACTION_MISMATCH')
        require(observation.get('no_pending_writer') is True and observation.get('terminal_observed') is True and observation.get('postconditions_observed') is True and bool(observation.get('evidence_digest')),21,'NATIVE_STATE_UNCERTAIN')
        require(observation.get('native_witness')==self.fence.get('native'),19,'NATIVE_WITNESS_MISMATCH')

    def _require_fence(self): require(self.held and self.fence is not None,18,'NO_ACTIVE_FENCE')
    def _persist(self,kind):
        self.storage.write_fence(self.fence); self._event(kind)
    def _event(self,kind):
        event={'kind':kind,'run_id':self.admission.run_id,'plan_digest':self.admission.plan_digest,'fence_digest':digest(self.fence)}
        self.storage.append_event(event)
    def close(self):
        if self.held:
            pending = self.fence is not None
            if not pending and hasattr(self.storage, 'has_pending_reads'):
                try: pending = self.storage.has_pending_reads()
                except BaseException: pending = True
            if pending and hasattr(self.guard,'defer_until_process_exit'):
                self.guard.defer_until_process_exit()
            else:
                self.guard.release()
            self.held=False
    def __enter__(self): return self
    def __exit__(self,*exc): self.close()
