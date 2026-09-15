"""Synthetic author tests for staged E16/E17 crash recovery; no native execution."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from helpers import authority_case
from test_session_integration import Storage
from aifilm_p00.errors import P00Error
from aifilm_p00.native.publication_recovery import staged_output_path
from aifilm_p00.native.session_driver import NativeDriver


class RecoveryIntegrationTests(unittest.TestCase):
    def setup_case(self,scope='GATE_HANDOFF'):
        _,plan,_,_=authority_case('SUPPORT_BUNDLE')
        plan=deepcopy(plan);plan['semantic']['bundle_scope']=scope
        d=NativeDriver.__new__(NativeDriver);d.binding={'assessment_output':r'C:\Evidence\gate.json'};d.paths=object()
        d.system=SimpleNamespace(all_writers=lambda witness:[]);d.source_kind='WORKSPACE_TEST';d.actual_steps={}
        st=Storage();c=SimpleNamespace(fence={'native':None,'action':'PUBLISH_SAFE_BUNDLE'},storage=st)
        fresh=SimpleNamespace(context=SimpleNamespace(now=SimpleNamespace(isoformat=lambda:'2026-09-15T00:00:00+00:00')),
            observed={'material':{'x':1},'host':{'boot_utc':'boot'},'target':None})
        return d,plan,fresh,c
    def reject(self,code,fn,*a,**kw):
        with self.assertRaises(P00Error) as cm:fn(*a,**kw)
        self.assertEqual(int(cm.exception.code),code);return cm.exception.reason
    def test_gate_recovery_requires_existing_assessment_intent(self):
        d,p,f,c=self.setup_case()
        bundle={'published':True,'archive_expected':True,'component_eligible':True,'bundle_digest':'a'*64,'exit':0,'outcome':'COMPLETE'}
        with patch('aifilm_p00.native.publication_recovery.observed_publication',return_value=bundle),\
             patch('aifilm_p00.native.assessment.assessment_intent_count',return_value=0),\
             patch('aifilm_p00.native.session_driver.operation_expected',return_value={'material_after':{'x':1},'captures':{}}):
            self.assertEqual(self.reject(18,d._after,p,0,{},f,c,reconciliation=True),'ASSESSMENT_INTENT_MISSING')
    def test_gate_recovery_attaches_exact_recovered_assessment(self):
        d,p,f,c=self.setup_case();bundle={'published':True,'archive_expected':True,'component_eligible':True,'bundle_digest':'a'*64,'exit':0,'outcome':'COMPLETE'}
        assessment={'published':True,'assessment_digest':'b'*64,'accepted_by_master':False,'host_ready':False}
        with patch('aifilm_p00.native.publication_recovery.observed_publication',return_value=bundle),\
             patch('aifilm_p00.native.assessment.assessment_intent_count',return_value=1),\
             patch('aifilm_p00.native.assessment.recover_assessment',return_value=assessment),\
             patch('aifilm_p00.native.session_driver.operation_expected',return_value={'material_after':{'x':1},'captures':{}}):
            completion=d._after(p,0,{},f,c,reconciliation=True)
        self.assertEqual(completion.raw_evidence['details']['bundle']['assessment'],assessment)
    def test_non_applicable_bundle_rejects_assessment_intent(self):
        d,p,f,c=self.setup_case('FAILED_RUN');bundle={'published':True,'archive_expected':True,'component_eligible':False,'bundle_digest':'a'*64,'exit':0,'outcome':'COMPLETE'}
        with patch('aifilm_p00.native.publication_recovery.observed_publication',return_value=bundle),\
             patch('aifilm_p00.native.assessment.assessment_intent_count',return_value=1),\
             patch('aifilm_p00.native.session_driver.operation_expected',return_value={'material_after':{'x':1},'captures':{}}):
            self.assertEqual(self.reject(16,d._after,p,0,{},f,c,reconciliation=True),'ASSESSMENT_NOT_APPLICABLE')


class StagingIdentityTests(unittest.TestCase):
    def test_stage_identity_is_deterministic_and_sibling(self):
        final=r'C:\Evidence\bundle.zip';plan='1'*64;payload='2'*64
        a=staged_output_path(final,plan,payload,'bundle');b=staged_output_path(final,plan,payload,'bundle')
        self.assertEqual(a,b);self.assertTrue(a.startswith(r'C:\Evidence\p00-pending-bundle-'));self.assertNotEqual(a,final)
    def test_kind_separates_bundle_and_assessment_staging(self):
        final=r'C:\Evidence\out.bin';plan='1'*64;payload='2'*64
        self.assertNotEqual(staged_output_path(final,plan,payload,'bundle'),staged_output_path(final,plan,payload,'assessment'))
    def test_generated_stage_path_must_fit_windows_path_contract(self):
        final='C:\\'+('x'*225)+'\\out.zip'
        with self.assertRaises(P00Error) as cm:staged_output_path(final,'1'*64,'2'*64,'bundle')
        self.assertEqual(int(cm.exception.code),10)


if __name__=='__main__':unittest.main()
