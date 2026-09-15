"""Synthetic author tests for reviewed DIRECT/non-DIRECT context semantics; no network execution."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import os,unittest

from helpers import authority_case
from aifilm_p00.codec import canonical
from aifilm_p00.errors import P00Error
from aifilm_p00.network_probe import proxy_policy
from aifilm_p00.native.network import parse_network,NativeNetwork

NAMES=('http_proxy','https_proxy','all_proxy','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY')

def spec(context='GUEST'):
    return {'endpoint_id':'ubuntu','url':'https://example.invalid/InRelease','context':context,
            'proxy_mode':'DIRECT','expected_status':200,'body_prefix_hex':b'PGP'.hex(),
            'maximum_bytes':1000,'redirect_allowlist':[]}

def direct_proxy(context='GUEST'):
    value={'context':context,'environment_overrides':{k:False for k in NAMES}}
    if context=='WINDOWS':
        value['winhttp']={'access_type':1,'proxy_present':False,'bypass_present':False}
        value['user']={'status':'ABSENT','auto_detect':False,'auto_config_url_present':False,'proxy_present':False}
    return value

def capture(s,proxy=None):
    actual={'endpoint_id':s['endpoint_id'],'url':s['url'],'context':s['context'],'status':'OBSERVED',
            'normalized_exit':0,'duration_ms':1,'attempts':1,'proxy_observation':proxy or direct_proxy(s['context']),
            'measurements':{'dns':True,'tcp':True,'tls_chain_hostname':True,'https':True,
                            'eof':True,'http_status':s['expected_status']},'host_ready':False}
    return canonical({'schema_version':1,'operation':'NETWORK','status':'OBSERVED','actual':actual,'duration_ms':1})+b'\n'

class ProxyPolicyTests(unittest.TestCase):
    def reject(self,code,fn,*a):
        with self.assertRaises(P00Error) as cm:fn(*a)
        self.assertEqual(int(cm.exception.code),code);return cm.exception.reason
    def test_guest_direct_context_allowed(self):
        self.assertEqual(proxy_policy(spec(),direct_proxy())['context'],'GUEST')
    def test_guest_environment_proxy_is_network_failure(self):
        p=direct_proxy();p['environment_overrides']['HTTPS_PROXY']=True
        self.assertEqual(self.reject(14,proxy_policy,spec(),p),'NETWORK_PROXY_CONTEXT')
    def test_windows_system_proxy_is_network_failure(self):
        p=direct_proxy('WINDOWS');p['winhttp']['access_type']=3;p['winhttp']['proxy_present']=True
        self.assertEqual(self.reject(14,proxy_policy,spec('WINDOWS'),p),'NETWORK_PROXY_CONTEXT')
    def test_windows_user_auto_proxy_is_network_failure(self):
        p=direct_proxy('WINDOWS');p['user']['status']='OBSERVED';p['user']['auto_detect']=True
        self.assertEqual(self.reject(14,proxy_policy,spec('WINDOWS'),p),'NETWORK_PROXY_CONTEXT')
    def test_malformed_proxy_observation_is_integrity_failure(self):
        self.assertEqual(self.reject(15,proxy_policy,spec(),{'context':'GUEST'}),'NETWORK_PROXY_OBSERVATION_REQUIRED')
    def test_non_direct_plan_mode_is_not_invented_adapter(self):
        s=spec();s['proxy_mode']='SYSTEM_PROXY'
        self.assertEqual(self.reject(11,proxy_policy,s,direct_proxy()),'PROXY_PROFILE_REQUIRES_ADAPTER')

class ControllerEvidenceTests(unittest.TestCase):
    def reject(self,code,fn,*a):
        with self.assertRaises(P00Error) as cm:fn(*a)
        self.assertEqual(int(cm.exception.code),code);return cm.exception.reason
    def test_parse_revalidates_proxy_context(self):
        s=spec();p=direct_proxy();p['environment_overrides']['https_proxy']=True
        self.assertEqual(self.reject(14,parse_network,capture(s,p),s),'NETWORK_PROXY_CONTEXT')
    def test_parse_accepts_exact_direct_capture(self):
        s=spec();self.assertEqual(parse_network(capture(s),s)['actual']['status'],'OBSERVED')
    def test_controller_environment_proxy_blocks_before_native_child(self):
        s=spec();_,plan,_,_=authority_case('SITE_VERIFY');plan=deepcopy(plan);plan['semantic']['endpoints']=[s]
        driver=SimpleNamespace();c=SimpleNamespace(held=True,fence={'state':'INTENT'})
        with patch.dict(os.environ,{'HTTPS_PROXY':'http://proxy.invalid:8080'},clear=False):
            self.assertEqual(self.reject(14,NativeNetwork(driver).run,plan,c,s),'NETWORK_PROXY_CONTEXT')
    def test_proxy_failure_capture_cannot_be_relabeled_observed(self):
        s=spec();actual={'endpoint_id':s['endpoint_id'],'url':s['url'],'context':'GUEST','status':'FAIL',
            'normalized_exit':14,'duration_ms':1,'attempts':1,'proxy_observation':direct_proxy(),
            'measurements':{},'host_ready':False}
        raw=canonical({'schema_version':1,'operation':'NETWORK','status':'OBSERVED','actual':actual,'duration_ms':1})+b'\n'
        self.assertEqual(parse_network(raw,s)['actual']['normalized_exit'],14)

if __name__=='__main__':unittest.main()
