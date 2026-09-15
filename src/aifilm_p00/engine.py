"""Legacy explicit-port orchestration retained for contract-level author tests.

The production CLI uses NativeDriver/SessionRunner, not this engine. NativeUnavailable
is an explicit refusing legacy port; it is never registered by the native factory.
Synthetic backends belong only to tests and do not provide native observations.
"""
from .authority import authorize
from .codec import digest
from .plans import interface_check
from .policy import floors,budget_check,drift,protection,restore_envelope,host_profile,runtime_profile,guest_profile
from .errors import P00Error,require

class OperationEngine:
    def __init__(self,backend,coordinator,store):
        self.backend=backend; self.coordinator=coordinator; self.store=store

    def execute(self,interface,plan,ctx):
        s=interface_check(interface,plan)
        admission=authorize(interface,plan,ctx,self.store)
        # No operation can use the workspace backend as a native backend through CLI.
        with self.coordinator.acquire(admission):
            observed=self.backend.refresh(s)
            drift(s['before'],observed['material'])
            host_profile(observed['host'],ctx.now)
            floors(observed['resources'])
            reservations=budget_check(s['budgets'],observed['free_bytes'])
            if s['purpose'] not in ('ENGINE','PASSIVE'):
                runtime_profile(observed['runtime'])
            if s['purpose']=='ADOPT':
                guest_profile(observed['guest']); floors(observed['guest_resources'],guest=True)
            if 'C3' in admission.classes:
                pack=self.store.get('protection',s['refs']['protection']) if 'protection' in s['refs'] else None
                protection(pack,s['host_id'],s['target']['registration_id'],ctx.now,observed.get('source_witness'))
            if s['purpose'] in ('RESTORE_IMPORT','RESTORE_VERIFY'):
                proof=self.store.get('isolation',s['refs']['isolation']) if 'isolation' in s['refs'] else None
                restore_envelope(proof,s['source_class'],s['execution_class'],s.get('expected_checkpoint'),ctx.now,s.get('expected_envelope'))
            if self.backend.postconditions_hold(s):
                # NOOP requires backend assertions of material/content/identity, never a marker alone.
                return {'exit':0,'state':'NOOP','source_kind':self.backend.source_kind,'host_ready':False}
            current_material=s['before']
            for n,operation in enumerate(s['operations']):
                refreshed=self.backend.refresh(s)
                drift(current_material,refreshed['material'])
                floors(refreshed['resources']); reservations=budget_check(s['budgets'],refreshed['free_bytes'])
                witness=self.backend.controller_witness(s,n)
                self.coordinator.intent(operation['action'],reservations,witness)
                try:
                    outcome=self.backend.run(operation,s,self.coordinator.native_started)
                except P00Error as error:
                    self.coordinator.uncertain(error.reason)
                    raise
                except BaseException:
                    # Preserve the write-ahead fence even for cancellation/crash-like interruption.
                    self.coordinator.uncertain('BACKEND_INTERRUPTED')
                    raise
                if outcome.get('state') in ('AWAITING_REBOOT','AWAITING_USER_INIT','AWAITING_OWNER_VERIFICATION'):
                    self.coordinator.awaiting(outcome['state'])
                    return {'exit':20,'state':outcome['state'],'source_kind':self.backend.source_kind,'host_ready':False}
                require(outcome.get('exit')==0,18,'NATIVE_OUTCOME_UNMAPPED')
                self.coordinator.terminal(self.backend.terminal_observation(operation,s,outcome))
                current_material=outcome['material_after']
            require(self.backend.postconditions_hold(s),19,'POSTCONDITIONS_FAILED')
            return {'exit':0,'state':'APPLIED' if interface=='apply' else 'VERIFIED','source_kind':self.backend.source_kind,'host_ready':False}

class NativeUnavailable:
    """Legacy refusing test boundary, unregistered by primary native CLI/factory."""
    source_kind='DOCUMENT'
    def execute(self,*args,**kwargs):
        raise P00Error(11,'NATIVE_BACKEND_NOT_IMPLEMENTED')
