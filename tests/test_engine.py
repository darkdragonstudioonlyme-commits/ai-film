"""Actual workspace execution of orchestration with a strictly in-memory fixture backend.
No native registration, network access, process launch or synthetic qualification export.
"""
from copy import deepcopy
from helpers import *
from test_core import Checks
from aifilm_p00.engine import OperationEngine
from aifilm_p00.admission import Coordinator
from aifilm_p00.errors import P00Error
from aifilm_p00.evidence import assemble,Sanitizer,bundle_integrity

class FixtureBackend:
    source_kind='DOCUMENT'
    def __init__(self,plan,fail=None,noop=False):
        self.plan=plan; self.fail=fail; self.noop=noop; self.calls=[]; self.material=deepcopy(plan['semantic']['before']); self.finished=False; self.native=None
    def refresh(self,s):
        self.calls.append('refresh')
        return {'material':deepcopy(self.material),'host':host(),'resources':host_resources(),
                'free_bytes':{'volume1':100*GIB},'runtime':{'status':'PRESENT','packaged':True,'channel':'stable','version':'2.7.14'}}
    def postconditions_hold(self,s): return self.noop or self.finished
    def controller_witness(self,s,n): return {'host_boot':'boot','controller_pid':1,'controller_start':'start','build_digest':B,'step_id':f's{n}'}
    def run(self,operation,s,on_native):
        self.calls.append(operation['action']); self.native={'pid':2,'start':'synthetic-start','action_id':operation['action']}; on_native(self.native)
        if self.fail=='timeout': raise P00Error(17,'NATIVE_TIMEOUT')
        if self.fail=='pause': return {'state':'AWAITING_USER_INIT'}
        if self.fail=='unknown_exit': return {'exit':1000}
        self.material=deepcopy(s['expected_after']); self.finished=True
        return {'exit':0,'material_after':deepcopy(self.material)}
    def terminal_observation(self,op,s,result):
        return {'action':op['action'],'native_witness':self.native,'no_pending_writer':True,'terminal_observed':True,'postconditions_observed':True,'evidence_digest':CP}

class EngineTests(Checks):
    def setup(self,fail=None,omit=None,noop=False):
        i,p,c,s=authority_case(purpose='RESTORE_EXPORT',omit=omit); backend=FixtureBackend(p,fail,noop)
        storage=MemoryStorage();guard=MemoryGuard();engine=OperationEngine(backend,Coordinator(guard,storage),s)
        return engine,backend,storage,guard,i,p,c
    def test_authorization_before_any_backend_action(self):
        e,b,st,g,i,p,c=self.setup(omit='qualification');self.reject(11,e.execute,i,p,c);self.assertEqual(b.calls,[]);self.assertIsNone(st.fence)
    def test_actual_fixture_execution_with_journal(self):
        e,b,st,g,i,p,c=self.setup();r=e.execute(i,p,c);self.assertEqual(r['state'],'APPLIED');self.assertFalse(r['host_ready']);self.assertIsNone(st.fence);self.assertIn('EXPORT_CHECKPOINT',b.calls)
    def test_timeout_preserves_fence(self):
        e,b,st,g,i,p,c=self.setup(fail='timeout');self.reject(17,e.execute,i,p,c);self.assertEqual(st.fence['state'],'UNCERTAIN');self.assertFalse(g.busy)
    def test_new_run_blocked_on_uncertainty(self):
        e,b,st,g,i,p,c=self.setup(fail='timeout');self.reject(17,e.execute,i,p,c);b.calls.clear();self.reject(21,e.execute,i,p,c);self.assertEqual(b.calls,[])
    def test_noop_does_not_invoke_mutation(self):
        e,b,st,g,i,p,c=self.setup(noop=True);r=e.execute(i,p,c);self.assertEqual(r['state'],'NOOP');self.assertEqual(b.calls,['refresh']);self.assertIsNone(st.fence)
    def test_pending_oobe_not_success(self):
        e,b,st,g,i,p,c=self.setup(fail='pause');r=e.execute(i,p,c);self.assertEqual(r['exit'],20);self.assertEqual(st.fence['state'],'AWAITING_USER_INIT')
    def test_unknown_native_exit_never_zero(self):
        e,b,st,g,i,p,c=self.setup(fail='unknown_exit');self.reject(18,e.execute,i,p,c);self.assertIsNotNone(st.fence)
    def test_wrong_before_rejected_before_mutation(self):
        e,b,st,g,i,p,c=self.setup();b.material={'different':'state'};self.reject(16,e.execute,i,p,c);self.assertEqual(b.calls,['refresh']);self.assertIsNone(st.fence)
    def test_verify_cannot_dispatch_export(self):
        e,b,st,g,i,p,c=self.setup();self.reject(10,e.execute,'verify',p,c);self.assertEqual(b.calls,[])
    def test_scanner_exception_blocks_publication(self):
        def broken(_):raise RuntimeError('CANARY_SECRET')
        r=assemble('FAILED_RUN',[collected('E00-10')],Sanitizer(b'x'*16),context={},scanner=broken)
        self.assertEqual(r.exit,23);self.assertIsNone(r.archive);self.assertNotIn('CANARY_SECRET',str(r.report))
    def test_invalid_zip_normalized(self):self.reject(15,bundle_integrity,b'not a zip')
