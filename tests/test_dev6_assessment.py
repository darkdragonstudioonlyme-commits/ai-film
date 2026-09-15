import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
from aifilm_p00.codec import canonical,digest,sha256,loads
from aifilm_p00.errors import P00Error
from aifilm_p00.native.assessment import AssessmentPublisher,recover_assessment

D='0'*64

def assessment():
    return {'schema_version':1,'evidence_id':'E00-17','status':'PROPOSAL','accepted_by_master':False,
            'eligible_as_of':'2026-01-01T00:00:00+00:00','sealed_at':'2026-01-01T00:00:01+00:00',
            'host_id':'h','target_id':'t','contract_digest':D,'build_digest':D,
            'e14_digest':D,'e16_digest':D,'snapshot_digest':D,'source_session_digest':D,
            'blockers':[],'host_ready':False,'qualification_issued':False}

class Storage:
    def __init__(self):self.rows=[]
    def append_event(self,e):self.rows.append({'event':e})
    def read_events(self):return self.rows

class Paths:
    def __init__(self):self.blobs={};self.fail=False;self.fail_after_temp=False;self.writes=0
    def publish_new(self,p,raw,*,pending_path):
        if self.fail:raise P00Error(18,'SIMULATED_OUTPUT_FAIL')
        if p in self.blobs or pending_path in self.blobs:raise P00Error(16,'EXISTS')
        self.blobs[pending_path]=raw;self.writes+=1
        if self.fail_after_temp:raise P00Error(18,'SIMULATED_AFTER_TEMP')
        self.blobs[p]=self.blobs.pop(pending_path);self.writes+=1
    def read_blob(self,p,expected=None,cap=10**6):
        if p not in self.blobs:raise P00Error(18,'MISSING')
        raw=self.blobs[p]
        if expected and sha256(raw)!=expected:raise P00Error(15,'HASH')
        return raw

class AssessmentTests(unittest.TestCase):
    def setup(self):
        p={'plan_digest':'1'*64};s=Storage();c=SimpleNamespace(held=True,fence={'plan_digest':p['plan_digest']},
            admission=SimpleNamespace(plan_digest=p['plan_digest']),storage=s);return p,s,c,Paths(),r'C:\evidence\gate.json'
    def reject(self,code,fn,*a):
        with self.assertRaises(P00Error) as cm:fn(*a)
        self.assertEqual(cm.exception.code,code)
    def test_intent_precedes_create_and_success_is_non_authoritative(self):
        p,s,c,x,path=self.setup();r=AssessmentPublisher(x,c).publish(p,assessment(),path)
        self.assertEqual(r['exit'],0);self.assertTrue(r['published']);self.assertFalse(r['host_ready'])
        self.assertEqual([r['event']['kind'] for r in s.rows],['ASSESSMENT_PUBLISH_INTENT','ASSESSMENT_OUTPUT_OBSERVED'])
    def test_output_failure_keeps_intent_for_recovery(self):
        p,s,c,x,path=self.setup();x.fail=True;r=AssessmentPublisher(x,c).publish(p,assessment(),path)
        self.assertEqual(r['exit'],18);self.assertEqual(len(s.rows),1)
    def test_recovery_observes_exact_existing_bytes_without_rewrite(self):
        p,s,c,x,path=self.setup();x.fail=True;AssessmentPublisher(x,c).publish(p,assessment(),path)
        x.fail=False;raw=canonical(assessment());x.blobs[path]=raw;count=x.writes
        with patch('aifilm_p00.native.assessment.file_presence',side_effect=lambda paths,q:q in paths.blobs):r=recover_assessment(x,c,p,path)
        self.assertTrue(r['recovered_existing_bytes']);self.assertEqual(x.writes,count);self.assertFalse(r['host_ready'])
    def test_recovery_without_intent_rejected(self):
        p,s,c,x,path=self.setup();x.blobs[path]=canonical(assessment())
        with patch('aifilm_p00.native.assessment.file_presence',side_effect=lambda paths,q:q in paths.blobs):self.reject(21,recover_assessment,x,c,p,path)
    def test_tampered_existing_bytes_rejected(self):
        p,s,c,x,path=self.setup();x.fail=True;AssessmentPublisher(x,c).publish(p,assessment(),path)
        x.blobs[path]=canonical(assessment())+b'x'
        with patch('aifilm_p00.native.assessment.file_presence',side_effect=lambda paths,q:q in paths.blobs):self.reject(15,recover_assessment,x,c,p,path)
    def test_temp_only_assessment_is_retained_failure(self):
        p,s,c,x,path=self.setup();x.fail_after_temp=True;r=AssessmentPublisher(x,c).publish(p,assessment(),path)
        self.assertEqual(r['exit'],18);writes=x.writes
        with patch('aifilm_p00.native.assessment.file_presence',side_effect=lambda paths,q:q in paths.blobs):
            self.reject(18,recover_assessment,x,c,p,path)
        self.assertEqual(x.writes,writes);self.assertEqual(s.rows[-1]['event']['kind'],'ASSESSMENT_TEMP_RETAINED')
    def test_final_and_temp_assessment_is_ambiguous(self):
        p,s,c,x,path=self.setup();AssessmentPublisher(x,c).publish(p,assessment(),path)
        intent=s.rows[0]['event'];x.blobs[intent['publication']['temp_path']]=canonical(assessment())
        with patch('aifilm_p00.native.assessment.file_presence',side_effect=lambda paths,q:q in paths.blobs):
            self.reject(16,recover_assessment,x,c,p,path)
    def test_tampered_assessment_temp_path_rejected(self):
        p,s,c,x,path=self.setup();AssessmentPublisher(x,c).publish(p,assessment(),path)
        event=s.rows[0]['event'];event['publication']['temp_path']=r'C:\evidence\other.bin';event['publication_digest']=digest(event['publication'])
        with patch('aifilm_p00.native.assessment.file_presence',side_effect=lambda paths,q:q in paths.blobs):
            self.reject(16,recover_assessment,x,c,p,path)
    def test_duplicate_assessment_intent_blocks_recovery(self):
        p,s,c,x,path=self.setup();AssessmentPublisher(x,c).publish(p,assessment(),path);s.rows.append(deepcopy(s.rows[0]))
        with patch('aifilm_p00.native.assessment.file_presence',side_effect=lambda paths,q:q in paths.blobs):
            self.reject(21,recover_assessment,x,c,p,path)
    def test_authority_bits_cannot_be_true(self):
        p,s,c,x,path=self.setup();a=assessment();a['host_ready']=True
        self.reject(15,AssessmentPublisher(x,c).publish,p,a,path)
