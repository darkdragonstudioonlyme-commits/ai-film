"""Author tests with synthetic records/IO only. No Windows, guest or network."""
import io
import sys
import subprocess
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
import unittest

from helpers import NOW, B, SID, CP, authority_case, collected
from test_session_integration import Storage
from aifilm_p00.codec import canonical,digest,sha256
from aifilm_p00.errors import P00Error
from aifilm_p00.evidence import assemble,Sanitizer,Bundle
from aifilm_p00.evidence_catalog import Stage
from aifilm_p00.evidence_stage import encode_stage,decode_stage,scoped_stage,require_bundle_context
from aifilm_p00.native.snapshot import strict_safe_scan,NativeBundlePublisher
from aifilm_p00.native.publication_recovery import observed_publication
from aifilm_p00.native.coordination import NativeJournal,frame,LOG_CAP
from aifilm_p00.native.session_driver import native_session,NativeDriver
from aifilm_p00.session import SessionRunner
from aifilm_p00.admission import Coordinator

ROOT=Path(__file__).resolve().parents[1]

class Check(unittest.TestCase):
    def reject(self,code,fn,*a,**kw):
        with self.assertRaises(P00Error) as e:fn(*a,**kw)
        self.assertEqual(e.exception.code,code);return e.exception.reason


def stage_fixture(name='GATE',**kw):
    values=dict(name=name,route='SITE_VERIFY',execution_class='SITE',existing_target=True,
                after_probe=True,c3=True,network_required=True,restore=True)
    values.update(kw);st=Stage(**values);v=encode_stage(st)
    d={'stage_context':v,'stage_digest':digest(v),'stage':name,'source_kind':st.execution_class}
    i={'stage_context':deepcopy(v)}
    r={'stage':name,'route':st.route,'source_kind':st.execution_class,'status':'PASS'}
    return d,i,r

class StageTests(Check):
    def test_roundtrip_preserves_all_flags(self):
        d,_,_=stage_fixture();s=decode_stage(d['stage_context'])
        self.assertTrue(s.c3 and s.after_probe and s.network_required and s.restore)
    def test_missing_flag_not_defaulted(self):
        d,_,_=stage_fixture();del d['stage_context']['after_probe'];self.reject(15,decode_stage,d['stage_context'])
    def test_unknown_flag_rejected(self):
        d,_,_=stage_fixture();d['stage_context']['fake']=True;self.reject(15,decode_stage,d['stage_context'])
    def test_bool_is_not_string(self):
        d,_,_=stage_fixture();d['stage_context']['restore']='false';self.reject(10,decode_stage,d['stage_context'])
    def test_actual_stage_not_envelope_pass(self):
        d,i,r=stage_fixture('C3',route='ENGINE',after_probe=False)
        self.reject(22,scoped_stage,d,i,'GATE_HANDOFF',r)
    def test_lab_cannot_gate_site(self):
        d,i,r=stage_fixture(execution_class='LAB');self.reject(22,scoped_stage,d,i,'GATE_HANDOFF',r)
    def test_inventory_projects_name_only(self):
        d,i,r=stage_fixture();s=scoped_stage(d,i,'INVENTORY',r)
        self.assertEqual(s.name,'C0');self.assertTrue(s.c3 and s.restore and s.existing_target)
    def test_failed_run_preserves_c3(self):
        d,i,r=stage_fixture('C3',route='ENGINE');self.assertEqual(scoped_stage(d,i,'FAILED_RUN',r).name,'C3')
    def test_changed_descriptor_not_allowed(self):
        d,i,r=stage_fixture();d['stage_context']['existing_target']=False
        self.reject(15,scoped_stage,d,i,'GATE_HANDOFF',r)
    def test_status_not_used_to_invent_existing(self):
        d,i,r=stage_fixture('C0',existing_target=False,after_probe=False);r['status']='PASS'
        self.assertFalse(scoped_stage(d,i,'INVENTORY',r).existing_target)
    def test_route_substitution_blocked(self):
        d,i,r=stage_fixture();r['route']='CREATE';self.reject(15,scoped_stage,d,i,'GATE_HANDOFF',r)
    def test_missing_stage_legacy_requires_migration_not_guess(self):
        d,i,r=stage_fixture();i.pop('stage_context');self.reject(15,scoped_stage,d,i,'GATE_HANDOFF',r)
    def test_c3_attempt_cannot_be_hidden(self):
        d,_,_=stage_fixture('C3',route='ENGINE');c={'persistent_output':True,'mutation_attempted':True,'c3_attempted':False,'restore_attempted':False}
        self.reject(16,require_bundle_context,c,d,[{'action':'INSTALL_RUNTIME'}])
    def test_restore_attempt_derived_from_intent(self):
        d,_,_=stage_fixture();c={'persistent_output':True,'mutation_attempted':True,'c3_attempted':False,'restore_attempted':True}
        self.assertEqual(require_bundle_context(c,d,[{'action':'IMPORT_NEW_CLONE'}]),c)
    def test_future_c3_not_claimed_as_attempted(self):
        d,_,_=stage_fixture('C3',route='ENGINE');c={'persistent_output':True,'mutation_attempted':False,'c3_attempted':False,'restore_attempted':False}
        self.assertEqual(require_bundle_context(c,d,[]),c)
    def test_context_boolean_strict(self):
        d,_,_=stage_fixture();c={'persistent_output':True,'mutation_attempted':0,'c3_attempted':False,'restore_attempted':False}
        self.reject(10,require_bundle_context,c,d,[])


class PublicationPaths:
    def __init__(self):self.blobs={};self.writes=[];self.fail=False;self.fail_after_temp=False
    def publish_new(self,path,raw,*,pending_path):
        if self.fail:raise P00Error(18,'SIMULATED_PUBLISH_CRASH')
        if pending_path in self.blobs or path in self.blobs:raise P00Error(16,'EXISTS')
        self.blobs[pending_path]=raw;self.writes.append(pending_path)
        if self.fail_after_temp:raise P00Error(18,'SIMULATED_AFTER_TEMP')
        self.blobs[path]=self.blobs.pop(pending_path);self.writes.append(path)
    def read_blob(self,path,expected=None,cap=10**8):
        if path not in self.blobs:raise P00Error(18,'MISSING')
        raw=self.blobs[path]
        if len(raw)>cap:raise P00Error(22,'CAP')
        if expected and sha256(raw)!=expected:raise P00Error(15,'HASH')
        return raw


def publication_fixture(incomplete=False):
    _,p,_,_=authority_case('SUPPORT_BUNDLE')
    c=SimpleNamespace(held=True,admission=SimpleNamespace(plan_digest=p['plan_digest'],purpose='SUPPORT_BUNDLE'),
                     fence={'action':'PUBLISH_SAFE_BUNDLE','plan_digest':p['plan_digest']},storage=Storage())
    paths=PublicationPaths();b={'bundle_output':r'C:\Evidence\b.zip','incomplete_bundle_output':r'C:\Evidence\b.incomplete.zip'}
    bundle=assemble('FAILED_RUN',[] if incomplete else [collected('E00-10')],Sanitizer(b'x'*16),context={},scanner=strict_safe_scan)
    return p,c,paths,b,bundle

class PublicationTests(Check):
    def publish(self,paths,c,b,bundle):
        return NativeBundlePublisher(paths,c).publish(bundle,approved_path=b['incomplete_bundle_output'] if bundle.exit==22 else b['bundle_output'],
            budgets=[{'volume_id':'v','roles':['EVIDENCE'],'allocations':{'output':1000000}}],free_by_volume={'v':10*1024**3})
    def recover(self,paths,c,p,b):
        with patch('aifilm_p00.native.publication_recovery.file_presence',side_effect=lambda paths,path:path in paths.blobs):
            return observed_publication(paths,c,p,b)
    def test_recovery_reads_existing_final_bytes_no_republish(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle);count=len(x.writes)
        r=self.recover(x,c,p,b);self.assertEqual(len(x.writes),count);self.assertTrue(r['recovered_existing_bytes']);self.assertFalse(r['host_ready'])
    def test_intent_without_file_is_not_proof(self):
        p,c,x,b,bundle=publication_fixture();x.fail=True;self.publish(x,c,b,bundle)
        self.reject(18,self.recover,x,c,p,b)
    def test_file_without_intent_is_not_owned(self):
        p,c,x,b,bundle=publication_fixture();x.blobs[b['bundle_output']]=bundle.archive
        self.reject(21,self.recover,x,c,p,b)
    def test_tampered_final_blocks(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle);x.blobs[b['bundle_output']]+=b'x'
        self.reject(15,self.recover,x,c,p,b)
    def test_tampered_intent_blocks(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle)
        rows=c.storage.read_events();rows[-1]['event']['publication']['bytes']+=1
        c.storage.raw=b'';previous=None
        from aifilm_p00.codec import loads
        for n,row in enumerate(rows):
            raw=frame(row['event'],n,previous);c.storage.raw+=raw;previous=loads(raw)['sha256']
        self.reject(15,self.recover,x,c,p,b)
    def test_changed_approved_path_blocked(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle);b['bundle_output']=r'C:\Other\b.zip'
        self.reject(16,self.recover,x,c,p,b)
    def test_incomplete_remains_incomplete(self):
        p,c,x,b,bundle=publication_fixture(True);self.publish(x,c,b,bundle)
        self.assertEqual(self.recover(x,c,p,b)['exit'],22)
    def test_readback_error_does_not_clear_fence(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle);x.blobs.clear()
        self.reject(18,self.recover,x,c,p,b);self.assertIsNotNone(c.fence)
    def test_temp_only_is_verified_retained_failure_not_republished(self):
        p,c,x,b,bundle=publication_fixture();x.fail_after_temp=True;r=self.publish(x,c,b,bundle)
        self.assertEqual(r['exit'],18);count=len(x.writes)
        self.assertEqual(self.reject(18,self.recover,x,c,p,b),'PUBLISH_TEMP_RETAINED');self.assertEqual(len(x.writes),count)
        self.assertTrue(any(row['event']['kind']=='BUNDLE_PUBLICATION_TEMP_RETAINED' for row in c.storage.read_events()))
    def test_final_and_temp_is_ambiguous(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle)
        intent=[r['event'] for r in c.storage.read_events() if r['event']['kind']=='BUNDLE_PUBLISH_INTENT'][0]
        x.blobs[intent['publication']['temp_path']]=bundle.archive
        self.assertEqual(self.reject(16,self.recover,x,c,p,b),'PUBLISH_OUTPUT_AMBIGUOUS')
    def test_tampered_temp_path_intent_rejected(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle)
        rows=c.storage.read_events();event=[r['event'] for r in rows if r['event']['kind']=='BUNDLE_PUBLISH_INTENT'][0]
        event['publication']['temp_path']=r'C:\Evidence\other.bin';event['publication_digest']=digest(event['publication'])
        c.storage.raw=b'';previous=None
        from aifilm_p00.native.coordination import frame
        from aifilm_p00.codec import loads
        for n,row in enumerate(rows):
            raw=frame(row['event'],n,previous);c.storage.raw+=raw;previous=loads(raw)['sha256']
        self.assertEqual(self.reject(16,self.recover,x,c,p,b),'PUBLISH_TEMP_PATH_DRIFT')
    def test_duplicate_publish_intent_blocks_recovery(self):
        p,c,x,b,bundle=publication_fixture();self.publish(x,c,b,bundle)
        intent=[r['event'] for r in c.storage.read_events() if r['event']['kind']=='BUNDLE_PUBLISH_INTENT'][0]
        c.storage.append_event(deepcopy(intent))
        self.assertEqual(self.reject(21,self.recover,x,c,p,b),'PUBLISH_INTENT_NOT_UNIQUE')
    def test_no_archive_privacy_outcome_is_durable_and_recoverable_without_write(self):
        p,c,x,b,_=publication_fixture();bundle=Bundle(23,'BLOCKED_REDACTION',False,False,None,{'outcome':'BLOCKED_REDACTION'})
        result=self.publish(x,c,b,bundle);self.assertFalse(result['published']);self.assertFalse(result['archive_expected'])
        self.assertEqual(x.writes,[])
        recovered=self.recover(x,c,p,b);self.assertEqual(recovered['exit'],23);self.assertFalse(recovered['published'])
        self.assertTrue(recovered['recovered_no_archive_decision'])
    def test_no_archive_intent_rejects_unexpected_final(self):
        p,c,x,b,_=publication_fixture();bundle=Bundle(23,'BLOCKED_REDACTION',False,False,None,{})
        self.publish(x,c,b,bundle);x.blobs[b['bundle_output']]=b'unowned'
        self.assertEqual(self.reject(16,self.recover,x,c,p,b),'PUBLISH_UNEXPECTED_FINAL')
    def test_no_archive_incomplete_cap_outcome_uses_incomplete_path(self):
        p,c,x,b,_=publication_fixture();bundle=Bundle(22,'INCOMPLETE_MANDATORY',False,False,None,{})
        self.publish(x,c,b,bundle);event=[r['event'] for r in c.storage.read_events() if r['event']['kind']=='BUNDLE_PUBLISH_INTENT'][0]
        self.assertEqual(event['publication']['path'],b['incomplete_bundle_output']);self.assertFalse(event['publication']['archive_expected'])
        self.assertEqual(self.recover(x,c,p,b)['exit'],22)


class JournalPaths:
    root=r'C:\Synthetic\P00'
    def __init__(self):
        self.raw=frame({'kind':'GENESIS','host_id':'synthetic-host','root_identity':{'volume_serial':3,'file_id':2}},0,None);self.appends=0
    @contextmanager
    def pin(self,*a,**kw):yield SimpleNamespace(identity={'volume_serial':3,'file_id':2})
    def read_blob(self,*a,**kw):return self.raw
    def append_flush(self,path,raw):self.raw+=raw;self.appends+=1

class NativeJournalBudgetTests(Check):
    def setup(self):
        p=JournalPaths();return p,NativeJournal(p,SimpleNamespace(held=True),'synthetic-host')
    def test_reservation_used_by_actual_native_journal(self):
        p,j=self.setup();r=j.reserve_capacity(4096);n=len(p.raw)
        j.append_event({'kind':'SYNTHETIC_TEST','value':1})
        self.assertEqual(r.spent,len(p.raw)-n);self.assertEqual(p.appends,1)
    def test_quota_before_write(self):
        p,j=self.setup();j.reserve_capacity(4096)
        self.reject(13,j.append_event,{'kind':'SYNTHETIC_TEST','raw':'x'*5000});self.assertEqual(p.appends,0)
    def test_external_valid_append_is_drift(self):
        p,j=self.setup();j.reserve_capacity(4096);rows=j.read_events()
        p.raw+=frame({'kind':'OTHER_CONTROLLER'},len(rows),rows[-1]['sha256'])
        self.reject(16,j.append_event,{'kind':'OWN'});self.assertEqual(p.appends,0)
    def test_reservation_cannot_expand(self):
        p,j=self.setup();j.reserve_capacity(4096);self.reject(21,j.reserve_capacity,8192)
    def test_root_replacement_rejected_before_append(self):
        p,j=self.setup();j.reserve_capacity(4096)
        p.raw=frame({'kind':'GENESIS','host_id':'synthetic-host','root_identity':{'volume_serial':3,'file_id':99}},0,None)
        self.reject(16,j.append_event,{'kind':'OWN'});self.assertEqual(p.appends,0)


class PrimaryCLITests(Check):
    def call(self,*args):return subprocess.run([sys.executable,'-m','aifilm_p00',*args],capture_output=True,timeout=10)
    def test_valid_reference_still_rejects_posix_before_native(self):
        for interface in ('apply','verify','support-bundle','preflight'):
            r=self.call(interface,'--plan-ref',B)
            self.assertEqual(r.returncode,11);self.assertIn(b'WINDOWS_X64_REQUIRED',r.stdout)
    def test_fake_backend_flag_not_accepted(self):
        r=self.call('apply','--plan-ref',B,'--backend','memory');self.assertEqual(r.returncode,2)
    def test_invalid_reference_no_native_factory(self):
        r=self.call('apply','--plan-ref','not-a-digest');self.assertEqual(r.returncode,10)
    def test_binding_requires_capture_reference(self):
        r=self.call('dry-run','--selection-ref',B);self.assertEqual(r.returncode,10)
    def test_result_exit_preserved(self):
        from aifilm_p00.__main__ import main
        for code in (0,2,20,22,23):
            out=io.BytesIO()
            with patch('aifilm_p00.native.request_entry.execute',return_value={'exit':code,'host_ready':False}),patch('sys.stdout',SimpleNamespace(buffer=out)):
                self.assertEqual(main(['support-bundle','--plan-ref',B]),code)
            self.assertIn(('"exit":'+str(code)).encode(),out.getvalue())

class ProductionConstructionTests(Check):
    def test_real_driver_runner_and_coordinator_bound_to_same_lower_ports(self):
        # Only OS-facing constructors are replaced here; no driver or coordinator
        # substitute is wired. This is construction coverage, not native execution.
        api=object();store=SimpleNamespace(operators=frozenset({SID}),host_id='synthetic-host')
        guard=object();paths=object();journal=object();supervisor=object();system=object()
        prefix='aifilm_p00.native.session_driver.'
        with patch(prefix+'_entry',return_value=(api,store,None,None,None)),patch(prefix+'WindowsPaths',return_value=paths),\
             patch(prefix+'NativeGuard',return_value=guard),patch(prefix+'NativeJournal',return_value=journal),\
             patch(prefix+'NativeSupervisor',return_value=supervisor),patch(prefix+'NativeSystemState',return_value=system):
            session=native_session(ROOT)
        self.assertIs(type(session),SessionRunner);self.assertIs(type(session.driver),NativeDriver)
        self.assertIs(type(session.coordinator),Coordinator);self.assertIs(session.coordinator.storage,journal)
        self.assertIs(session.driver.supervisor,supervisor);self.assertIs(session.driver.paths,paths)
        self.assertIs(session.coordinator.guard,guard)
