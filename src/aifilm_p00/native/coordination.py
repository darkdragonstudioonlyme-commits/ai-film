"""Fixed Global mutex and append-only Windows durable fence journal.

No automatic TTL, truncation repair, alternate root, file deletion, process kill,
or abandoned-mutex bypass. Journal CLEAR is a flushed record, not an unlink.
"""
import ctypes as C
from pathlib import PureWindowsPath
from ..admission import GUARD_NAME
from ..codec import canonical, loads, sha256, digest
from ..errors import require, P00Error
from .security import check_security, ADMIN_OWNERS, mutex_sddl

MUTEX_NAME='Global\\'+GUARD_NAME
LOG_CAP=10*1024**2

class NativeGuard:
    def __init__(self,api,operators):
        self.api=api; self.operators=frozenset(operators)
        self.handle=None; self.held=False; self.thread=None; self.abandoned=False
    def acquire(self):
        require(self.handle is None and not self.held,21,'NESTED_ADMISSION_FORBIDDEN')
        with self.api.attributes(mutex_sddl(self.operators)) as attr:
            h=self.api.create_mutex(C.byref(attr),MUTEX_NAME,0,0x00100000|0x1|0x00020000)
        require(h not in (None,0),12,'HOST_GUARD_ACCESS')
        self.handle=h
        try:
            sec=self.api.security(h,6)
            check_security(sec,owners=ADMIN_OWNERS|self.operators,writers=ADMIN_OWNERS|self.operators,
                           readers=ADMIN_OWNERS|self.operators,confidential=True,require_protected=True)
            state=self.api.wait(h,0)
            if state==258:
                self.api.close(h); self.handle=None; return False
            require(state in (0,0x80),18,'HOST_GUARD_WAIT')
            self.held=True; self.abandoned=state==0x80; self.thread=self.api.get_current_tid()
            return True
        except BaseException:
            self.api.close(h); self.handle=None; raise
    def defer_until_process_exit(self):
        # Remain owned by the current controller thread. The CLI must terminate
        # this controller, not reuse it for another request. Durable fence is
        # checked by the next process after Windows abandons the mutex.
        require(self.held and self.thread==self.api.get_current_tid(),18,'HOST_GUARD_NOT_HELD')
        self.exit_only=True

    def release(self):
        require(self.handle is not None and self.held,18,'HOST_GUARD_NOT_HELD')
        require(not getattr(self,'exit_only',False),21,'CONTROLLER_EXIT_REQUIRED')
        require(self.thread==self.api.get_current_tid(),18,'HOST_GUARD_THREAD_MISMATCH')
        self.api.ok(self.api.release_mutex(self.handle),'HOST_GUARD_RELEASE')
        self.api.close(self.handle); self.handle=None; self.held=False; self.thread=None


def replay(raw:bytes):
    """All frames must be complete/valid. Torn tail blocks, never auto-truncates."""
    require(isinstance(raw,bytes) and 0<len(raw)<=LOG_CAP and raw.endswith(b'\n'),15,'JOURNAL_TRUNCATED')
    rows=[]; previous=None; fence=None; genesis=None
    for index,line in enumerate(raw.splitlines()):
        row=loads(line)
        require(type(row) is dict and set(row)=={'sequence','previous','event','sha256'},15,'JOURNAL_SCHEMA')
        body={k:row[k] for k in ('sequence','previous','event')}
        require(row['sequence']==index and row['previous']==previous and digest(body)==row['sha256'],15,'JOURNAL_CHAIN')
        e=row['event']; require(type(e) is dict and isinstance(e.get('kind'),str),15,'JOURNAL_EVENT')
        if index==0:
            require(e['kind']=='GENESIS' and bool(e.get('host_id')) and bool(e.get('root_identity')),15,'JOURNAL_GENESIS')
            genesis=e
        else:
            require(e['kind']!='GENESIS',15,'DUPLICATE_GENESIS')
        if e['kind']=='SET_FENCE':
            record=e.get('record'); require(type(record) is dict,15,'FENCE_SCHEMA')
            if fence is not None:
                require(all(record.get(k)==fence.get(k) for k in ('run_id','host_id','owner_sid','plan_digest','action')),15,'FENCE_REPLACEMENT')
            fence=record
        elif e['kind']=='CLEAR_FENCE':
            require(fence is not None and fence.get('state') in ('TERMINAL','SAFE_PAUSE'),15,'FENCE_NOT_TERMINAL')
            require(e.get('fence_digest')==digest(fence),15,'FENCE_RELEASE_MISMATCH')
            fence=None
        previous=row['sha256']; rows.append(row)
    return {'rows':rows,'previous':previous,'fence':fence,'genesis':genesis}


def frame(event,index,previous):
    body={'sequence':index,'previous':previous,'event':event}
    return canonical({**body,'sha256':digest(body)})+b'\n'


class NativeJournal:
    def __init__(self,paths,guard,host_id):
        self.paths=paths; self.guard=guard; self.host_id=host_id
        self.path=str(PureWindowsPath(paths.root)/'journal.jsonl')
        self.reservation=None
    def _held(self): require(self.guard.held,18,'GUARD_NOT_HELD')
    def _read(self):
        self._held()
        with self.paths.pin(self.paths.root,directory=True,protected=True) as root:
            raw=self.paths.read_blob(self.path,cap=LOG_CAP)
            state=replay(raw);state['byte_count']=len(raw)
            genesis=state['genesis']
            require(genesis['host_id']==self.host_id,12,'COORDINATION_HOST_MISMATCH')
            expected={'volume_serial':root.identity['volume_serial'],'file_id':root.identity['file_id']}
            require(genesis['root_identity']==expected,16,'COORDINATION_ROOT_REPLACED')
            return state
    def load_fence(self): return self._read()['fence']
    def read_events(self): return self._read()['rows']
    def has_pending_reads(self):
        from .read_recovery import pending_reads
        return bool(pending_reads(self._read()['rows']))

    def reserve_capacity(self,maximum_additional,*,recovery=False):
        from ..journal_budget import JournalBudget
        self._held()
        require(self.reservation is None,21,'JOURNAL_RESERVATION_ALREADY_HELD')
        self.reservation=JournalBudget.reserve(LOG_CAP,self._read()['byte_count'],
                                               maximum_additional,recovery=recovery)
        return self.reservation

    def admission_check(self):
        from .read_recovery import pending_reads
        require(not pending_reads(self._read()['rows']),21,'DETACHED_READ_RECONCILIATION_REQUIRED')
    def append_event(self,event):
        state=self._read(); data=frame(event,len(state['rows']),state['previous'])
        require(state['byte_count']+len(data)<=LOG_CAP,18,'JOURNAL_CAPACITY')
        if self.reservation is not None:self.reservation.check(state['byte_count'],len(data))
        self.paths.append_flush(self.path,data)
        after=self._read()
        require(after['rows'][-1]['event']==event,15,'JOURNAL_COMMIT_UNPROVEN')
        if self.reservation is not None:
            self.reservation.committed(state['byte_count'],after['byte_count'],len(data))
    def write_fence(self,record): self.append_event({'kind':'SET_FENCE','record':record})
    def clear_fence(self):
        fence=self.load_fence()
        require(fence is not None and fence.get('state') in ('TERMINAL','SAFE_PAUSE'),21,'FENCE_NOT_TERMINAL')
        self.append_event({'kind':'CLEAR_FENCE','fence_digest':digest(fence)})
    def initialize_or_verify(self,metadata_authority):
        """Idempotent C0 initialization; never adopt an arbitrary existing root.

        An existing root must already contain a valid root-bound journal. A
        partial initialization, corrupt log or unresolved fence is a blocker,
        not permission to overwrite or create a replacement journal.
        """
        from .trust import MetadataPermit
        require(type(metadata_authority) is MetadataPermit and metadata_authority.host_id==self.host_id,12,'METADATA_APPROVAL_REQUIRED')
        self._held()
        if self.paths.directory_exists(self.paths.root):
            state=self._read()
            require(state['fence'] is None,21,'RECONCILIATION_REQUIRED')
            self.admission_check()
            return 'METADATA_NOOP'
        self.initialize(metadata_authority)
        return 'METADATA_INITIALIZED'

    def initialize(self,metadata_authority):
        """Authority is a checked MetadataPermit from native.trust, not JSON flags."""
        from .trust import MetadataPermit
        require(type(metadata_authority) is MetadataPermit and metadata_authority.host_id==self.host_id,12,'METADATA_APPROVAL_REQUIRED')
        self._held()
        self.paths.create_directory(self.paths.root)
        with self.paths.pin(self.paths.root,directory=True,protected=True) as root:
            event={'kind':'GENESIS','host_id':self.host_id,
                   'root_identity':{'file_id':root.identity['file_id'],'volume_serial':root.identity['volume_serial']},
                   'authority_digest':metadata_authority.approval_digest,
                   'build_digest':metadata_authority.build_digest}
            self.paths.write_new(self.path,frame(event,0,None))
        self._read()
