import unittest
from types import SimpleNamespace
from aifilm_p00.errors import P00Error
from aifilm_p00.native.session_driver import NativeDriver

class Storage:
    def __init__(self):self.events=[]
    def append_event(self,e):self.events.append(e)

class EarlyFailureTests(unittest.TestCase):
    def test_failure_before_first_snapshot_is_journaled_without_fake_e00(self):
        d=object.__new__(NativeDriver);d.last=None
        s=Storage();c=SimpleNamespace(held=True,fence={'action':'INSTALL_RUNTIME','state':'UNCERTAIN'},storage=s)
        p={'plan_digest':'a'*64,'semantic':{'run_id':'r1'}}
        r=d.record_failure(p,P00Error(17,'NATIVE_TIMEOUT'),c)
        self.assertEqual(r['status'],'JOURNAL_ONLY');self.assertFalse(r['host_ready'])
        self.assertEqual(s.events[0]['kind'],'EARLY_FAILURE_CAPTURED')
        self.assertEqual(s.events[0]['failure'],{'exit':17,'reason':'NATIVE_TIMEOUT'})
        self.assertNotIn('observations',s.events[0]);self.assertFalse(s.events[0]['qualification_issued'])
    def test_no_admission_or_fence_means_no_capture(self):
        d=object.__new__(NativeDriver);d.last=None
        c=SimpleNamespace(held=False,fence=None,storage=Storage())
        p={'plan_digest':'a'*64,'semantic':{'run_id':'r1'}}
        self.assertIsNone(d.record_failure(p,P00Error(11,'BLOCKED'),c));self.assertEqual(c.storage.events,[])
