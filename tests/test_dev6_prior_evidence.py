import unittest
from aifilm_p00.codec import digest
from aifilm_p00.errors import P00Error
from aifilm_p00.native.evidence_pipeline import _prior_guest_from_events,_history_plan_digests

D='a'*64
G={'uid':1000,'gid':1000,'user':'film','home':'/home/film','os_id':'ubuntu','version_id':'24.04',
   'architecture':'x86_64','kernel':'6.6','kernel_boot_id':'boot','pid1_start_ticks':'1','pid1_comm':'systemd',
   'home_access_writable':True,'resources':{'cpu':4},'wsl_conf_sha256':'b'*64}

def plan(pd=D):return {'plan_digest':pd}
def event(pd=D,step='step-1',guest=G):
    evidence={'details':{'actual_result':{'guest':{'inventory':{'actual':guest},'admin':{'actual':{'ready':True}}}}}}
    return {'event':{'kind':'OPERATION_AFTER_OBSERVED','plan_digest':pd,'step_id':step,
                     'evidence':evidence,'evidence_digest':digest(evidence)}}

class PriorEvidenceTests(unittest.TestCase):
    def reject(self,code,fn,*a):
        with self.assertRaises(P00Error) as cm:fn(*a)
        self.assertEqual(cm.exception.code,code)
    def test_history_plan_graph_bounded_and_deduplicated(self):
        r={'history':{'entries':{'a':{'plan_digest':'b'*64},'b':{'plan_digest':'b'*64}}}}
        self.assertEqual(_history_plan_digests(plan(),r),(D,'b'*64))
    def test_prior_guest_selected_from_current_or_exact_history(self):
        r={'history':{'entries':{'host_restart':{'plan_digest':'b'*64}}}}
        g,a,ref=_prior_guest_from_events([event('c'*64),event('b'*64)],plan(),r)
        self.assertEqual(g['uid'],1000);self.assertEqual(ref['plan_digest'],'b'*64);self.assertTrue(a['ready'])
    def test_unrelated_plan_not_selected(self):
        self.assertEqual(_prior_guest_from_events([event('c'*64)],plan(),{}),(None,None,None))
    def test_tampered_evidence_digest_rejected(self):
        row=event();row['event']['evidence_digest']='0'*64
        self.reject(15,_prior_guest_from_events,[row],plan(),{})
    def test_duplicate_same_step_conflicting_evidence_rejected(self):
        a=event();b=event();b['event']['evidence']['details']['actual_result']['guest']['inventory']['actual']=dict(G,uid=1001)
        b['event']['evidence_digest']=digest(b['event']['evidence'])
        self.reject(15,_prior_guest_from_events,[a,b],plan(),{})
