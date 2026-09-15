"""Synthetic workspace-only catalog, receipt, transition and command tests.

No native driver is constructed. No target scripts, Windows API, WSL, DNS or TLS
connection is executed. Schema-positive test data are NOT approvals/evidence.
"""
import ast
import base64
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from helpers import NOW,B,T,SID,CP,PROFILE,binding,authority_case,terminal_report,collected
from aifilm_p00 import CONTRACT_DIGEST
from aifilm_p00.codec import canonical,digest,sha256
from aifilm_p00.errors import P00Error
from aifilm_p00.plans import make_plan,check_plan
from aifilm_p00.policy import terminal,terminal_conditions,GIB
from aifilm_p00.evidence import assemble,Sanitizer,Collected
from aifilm_p00.evidence_catalog import (Stage,CATALOG,required_fields,new_body,group_check,evaluated,cell,pending,check_cell)
from aifilm_p00.native.network import network_command,script_bytes,parse_network
from aifilm_p00.native.guest import agent_command,parse_agent
from aifilm_p00.native.transitions import resolve_expected,operation_expected
from aifilm_p00.native.proofs import ProofReader
from aifilm_p00.native.snapshot import strict_safe_scan
from aifilm_p00.native.terminal_sweep import endpoint_matrix,restore_actual,epoch
from aifilm_p00.native.session_driver import remaining_budgets
from aifilm_p00.native.bindings import verify_volume_coverage,validate_binding
from aifilm_p00.windows_commands import compile_features

ROOT=Path(__file__).resolve().parents[1]
AT=NOW.isoformat()

class Check(unittest.TestCase):
    def reject(self,code,call,*a,**kw):
        with self.assertRaises(P00Error) as caught:call(*a,**kw)
        self.assertEqual(int(caught.exception.code),code,caught.exception.reason)

def stage(name='GATE',execution='SITE',**kw):
    return Stage(name,kw.pop('route','SITE_VERIFY'),execution,kw.pop('existing',True),**kw)

def values_for(eid):
    out={}
    for name,kinds in CATALOG[eid].items():
        kind=kinds[0] if isinstance(kinds,tuple) else kinds
        out[name]={} if kind is dict else [] if kind is list else True if kind is bool else 'synthetic'
    return out

class CatalogTests(Check):
    def body(self,eid):
        body=new_body(eid,values_for(eid),at=AT,source_ref='SYNTHETIC_ONLY/record',source_kind='SITE')
        return evaluated(body,'SCHEMA_ONLY_FIXTURE_PREDICATE',True,'SYNTHETIC_EXPECTATION')
    def test_gate_all_groups_have_required_fields(self):
        self.assertEqual(set(required_fields(stage())),set(CATALOG))
        self.assertTrue(all(v=='R' for r in required_fields(stage()).values() for v in r.values()))
    def test_inventory_has_guest_future_slots(self):
        r=required_fields(stage('C0',route='PASSIVE',existing=False))
        self.assertEqual(set(r['E00-04'].values()),{'S'});self.assertEqual(r['E00-05']['host'],'R')
    def test_discovery_does_not_require_unknown_guest(self):
        r=required_fields(stage('DISCOVERY',route='DISCOVERY',after_probe=False))
        self.assertEqual(r['E00-04']['identity'],'S');self.assertEqual(r['E00-09']['authority'],'R')
    def test_discovery_after_probe_requires_actual(self):
        r=required_fields(stage('DISCOVERY',route='DISCOVERY',after_probe=True))
        self.assertEqual(r['E00-04']['identity'],'R')
    def test_create_future_guest_not_adopt(self):
        self.assertEqual(required_fields(stage('APPLY',route='CREATE',existing=False))['E00-04']['identity'],'S')
        self.assertEqual(required_fields(stage('APPLY',route='ADOPT'))['E00-04']['identity'],'R')
    def test_c3_existing_independent_restore_required(self):
        r=required_fields(stage('C3',route='HOST_RESTART',c3=True))
        self.assertEqual(set(r['E00-15'].values()),{'R'});self.assertEqual(r['E00-03']['cross_owner_coverage'],'R')
    def test_c3_empty_target_no_fake_restore(self):
        r=required_fields(stage('C3',route='ENGINE',existing=False,c3=True))
        self.assertEqual(set(r['E00-15'].values()),{'N'});self.assertEqual(set(r['E00-12'].values()),{'R'})
    def test_lab_entry_qualification_no_cycle(self):
        r=required_fields(stage('APPLY','LAB',route='CREATE',existing=False))
        self.assertEqual(set(r['E00-13'].values()),{'N'});self.assertEqual(r['E00-10']['actor_class'],'R')
    def test_lab_receipt_still_required_for_site_gate(self):
        self.assertEqual(set(required_fields(stage())['E00-13'].values()),{'R'})
    def test_missing_group_field_not_outer_pass(self):
        b=self.body('E00-01');b['fields'].pop('principal');self.reject(15,group_check,'E00-01',b,stage())
    def test_no_evaluation_is_not_gate_complete(self):
        b=self.body('E00-01');b['evaluations']=[]
        self.assertIn('evaluations',group_check('E00-01',b,stage())['missing_fields'])
    def test_evaluation_must_bind_current_field_bytes(self):
        b=self.body('E00-01');b['fields']['host']['actual']={'changed':True}
        self.reject(15,group_check,'E00-01',b,stage())
    def test_future_not_current_actual(self):
        b=self.body('E00-04');b['fields']['identity']=pending('NOT_YET_CREATED','FUTURE',AT);b['evaluations']=[]
        self.assertFalse(group_check('E00-04',b,stage())['complete_for_stage'])
    def test_document_cannot_replace_source_measurement(self):
        c=cell({},'doc/ref',AT,source_kind='DOCUMENT');self.reject(15,check_cell,'E00-01','host',c)
    def test_not_applicable_requires_proof(self):
        c=pending('NOT_APPLICABLE','NOT_NEEDED',AT);self.reject(15,check_cell,'E00-01','host',c)
    def test_unknown_cannot_hide_actual_value(self):
        c=pending('UNKNOWN','MISSING',AT);c['actual']={};self.reject(15,check_cell,'E00-01','host',c)
    def test_wrong_type_boolean_not_integer(self):
        c=cell(1,'ref',AT,source_kind='SITE');self.reject(15,check_cell,'E00-02','virtualization',c)
    def test_lab_native_report_not_site_group(self):
        b=self.body('E00-01')
        for c in b['fields'].values():c['source_kind']='LAB'
        b['evaluations']=[];self.reject(15,group_check,'E00-01',b,stage())
    def test_e17_not_input_to_e16(self):
        b=self.body('E00-17');self.assertFalse(group_check('E00-17',b,stage())['complete_for_stage'])
        self.assertTrue(group_check('E00-17',b,stage(),downstream=True)['complete_for_stage'])
    def test_invalid_stage_flag_not_truthiness(self):
        self.reject(10,required_fields,Stage('C0','PASSIVE','SITE',1))

# Field-set coverage for every normative E00 group. These test schema plumbing,
# not real group evidence or native semantic outcomes.
for eid in CATALOG:
    def run(self,eid=eid):
        b=self.body(eid)
        self.assertTrue(group_check(eid,b,stage(),downstream=True)['complete_for_stage'])
    setattr(CatalogTests,'test_exact_field_set_'+eid.replace('-','_'),run)

class TransitionTests(Check):
    def setup(self):
        rid='{12345678-1234-1234-1234-123456789abc}'
        target={'name':'Phim thử','base_path':r'D:\Phim thử\Control','registration_id':None,'user':'film'}
        old={'distros':{'default':None,'rows':[]},'config':'unchanged'}
        row={'name':target['name'],'base_path':target['base_path'],'registration_id':rid,'default_uid':1000}
        actual={'distros':{'default':rid,'rows':[row]},'config':'unchanged'}
        expected=deepcopy(actual);expected['distros']['default']={'capture':'FIRST_DEFAULT'}
        expected['distros']['rows'][0]['registration_id']={'capture':'TARGET_REGISTRATION'}
        expected['distros']['rows'][0]['default_uid']={'capture':'INITIAL_UID'}
        return expected,actual,old,target,['FIRST_DEFAULT','TARGET_REGISTRATION','INITIAL_UID']
    def test_future_allocated_ids_are_actual_not_guessed(self):
        e,a,o,t,c=self.setup();r=resolve_expected(e,a,o,t,c);self.assertEqual(r['material_after'],a);self.assertEqual(r['captures']['INITIAL_UID'],1000)
    def test_missing_capture_authority_blocks(self):
        e,a,o,t,c=self.setup();self.reject(10,resolve_expected,e,a,o,t,c[1:])
    def test_existing_target_cannot_recapture(self):
        e,a,o,t,c=self.setup();o['distros']['rows']=deepcopy(a['distros']['rows']);self.reject(10,resolve_expected,e,a,o,t,c)
    def test_existing_default_cannot_first_default(self):
        e,a,o,t,c=self.setup();o['distros']['default']='old';self.reject(10,resolve_expected,e,a,o,t,c)
    def test_capture_not_generic_unknown_wildcard(self):
        e,a,o,t,c=self.setup();a['config']='changed';self.reject(16,resolve_expected,e,a,o,t,c)
    def test_foreign_distro_identity_change_rejected(self):
        e,a,o,t,c=self.setup();a['distros']['rows'].append({'name':'other','base_path':r'D:\Other','registration_id':'other','default_uid':1})
        self.reject(16,resolve_expected,e,a,o,t,c)
    def test_non_guid_registration_rejected(self):
        e,a,o,t,c=self.setup();a['distros']['rows'][0]['registration_id']='not-an-id';self.reject(16,resolve_expected,e,a,o,t,c)
    def test_uid_boolean_not_integer(self):
        e,a,o,t,c=self.setup();a['distros']['rows'][0]['default_uid']=True;self.reject(16,resolve_expected,e,a,o,t,c)
    def test_config_only_exact_transition(self):
        self.assertEqual(resolve_expected({'x':1},{'x':1},{'x':0},{'name':None,'registration_id':None},[])['material_after'],{'x':1})

class PrimitiveCommands(Check):
    def spec(self,context='GUEST'):
        return {'endpoint_id':'archive','url':'https://archive.invalid/InRelease','context':context,'proxy_mode':'DIRECT',
                'expected_status':200,'body_prefix_hex':b'-----BEGIN'.hex(),'maximum_bytes':1024,'redirect_allowlist':[]}
    def test_guest_network_exact_user_and_distribution(self):
        c=network_command(ROOT,r'C:\Windows\System32','Phim thử','film',self.spec(),r'C:\Python\python.exe')
        self.assertEqual(c.argv[2],'Phim thử');self.assertEqual(c.argv[4],'film');self.assertIn('/usr/bin/python3',c.argv)
        self.assertFalse(c.mutation);self.assertNotIn('--install',c.argv)
    def test_windows_network_not_guest_substitution(self):
        c=network_command(ROOT,r'C:\Windows\System32','Phim','film',self.spec('WINDOWS'),r'C:\Python\python.exe')
        self.assertEqual(c.argv[0],r'C:\Python\python.exe');self.assertNotIn('wsl.exe',' '.join(c.argv))
    def test_agent_source_parses_without_execution(self):ast.parse(script_bytes(ROOT))
    def test_agent_request_data_not_executable_source(self):
        spec=self.spec();spec['url']='https://archive.invalid/query?x=evil'
        c=network_command(ROOT,r'C:\Windows\System32','Phim','film',spec,r'C:\Python\python.exe')
        self.assertNotIn(spec['url'].encode(),c.stdin)
    def test_network_ignores_no_arbitrary_proxy_profile(self):
        spec=self.spec();spec['proxy_mode']='IGNORE_POLICY';self.reject(11,network_command,ROOT,r'C:\Windows\System32','Phim','film',spec,r'C:\Python\python.exe')
    def test_guest_agent_has_no_user_command_slot(self):
        self.reject(10,agent_command,r'C:\Windows\System32','Phim','film',b'fixed',{'operation':'SHELL','user':'film'})
    def test_guest_capture_requires_exact_operation(self):
        raw=canonical({'schema_version':1,'operation':'INVENTORY','status':'OBSERVED','actual':{},'duration_ms':1})+b'\n'
        self.reject(15,parse_agent,raw,'ADMIN')
    def test_guest_capture_requires_eof(self):self.reject(22,parse_agent,b'{}','ADMIN')
    def test_dism_single_process_all_features_and_explicit_output(self):
        c=compile_features(['VirtualMachinePlatform','Microsoft-Windows-Subsystem-Linux'],r'C:\Windows\System32',
                           log_path=r'C:\P00\dism.log',scratch_directory=r'C:\P00\Scratch')
        self.assertEqual(sum(x.startswith('/FeatureName:') for x in c),2);self.assertIn('/NoRestart',c);self.assertIn('/LimitAccess',c)
    def test_dism_arbitrary_feature_rejected(self):self.reject(10,compile_features,['Unknown'],r'C:\Windows\System32',log_path=r'C:\P\log',scratch_directory=r'C:\P\scratch')
    def test_no_target_for_failed_engine_support(self):
        b=binding('SUPPORT_BUNDLE');b['target']={k:None for k in b['target']};b['bundle_scope']='FAILED_RUN'
        self.assertIsNone(make_plan(b,AT)['semantic']['target']['name'])
    def test_no_target_for_passive_before_install(self):
        b=binding('PASSIVE');b['target']={k:None for k in b['target']};self.assertIsNone(make_plan(b,AT)['semantic']['target']['name'])
    def test_adopt_absence_still_forbidden(self):
        b=binding('ADOPT');b['target']={k:None for k in b['target']};self.reject(10,make_plan,b,AT)

class BudgetAndOutcomes(Check):
    def test_only_committed_step_releases_future_allocation(self):
        s={'budgets':[{'volume_id':'v','roles':['OS'],'allocations':{'image':10,'logs':2}}],'operations':[{},{}]}
        b={'allocation_lifetimes':{'v':{'image':0,'logs':None}}}
        self.assertEqual(remaining_budgets(s,b,{})[0]['allocations']['image'],10)
        self.assertEqual(remaining_budgets(s,b,{0:{}})[0]['allocations'],{'image':0,'logs':2})
    def test_missing_lifetime_not_implicit_refund(self):
        self.reject(10,remaining_budgets,{'budgets':[],'operations':[]},{}, {})
    def test_missing_writing_volume_cannot_be_hidden(self):
        p=SimpleNamespace(root=r'C:\P00',volume=lambda _: {'volume_id':'actual','filesystem':'NTFS'})
        self.reject(13,verify_volume_coverage,p,r'C:\Windows',{'scratch_directory':r'C:\P00\scratch','snapshot_maximum_bytes':1024},
                    {'target':{'base_path':None}},[{'volume_id':'wrong','roles':['OS','EVIDENCE'],'allocations':{'logs':1024}}])
    def test_metadata_role_is_required(self):
        p=SimpleNamespace(root=r'C:\P00',volume=lambda _: {'volume_id':'v','filesystem':'NTFS'})
        self.reject(13,verify_volume_coverage,p,r'C:\Windows',{'scratch_directory':r'C:\P00\scratch','snapshot_maximum_bytes':1024},
                    {'target':{'base_path':None}},[{'volume_id':'v','roles':['OS'],'allocations':{'logs':1024}}])
    def test_integrity_failure_without_envelope_is_not_plain_missing(self):
        c=Collected('E00-10',None,None,status='INTEGRITY_FAILURE')
        result=assemble('FAILED_RUN',[c],Sanitizer(b'x'*16),context={'persistent_output':True,'mutation_attempted':False,'c3_attempted':False,'restore_attempted':False},scanner=strict_safe_scan)
        self.assertEqual(result.exit,15);self.assertIsNone(result.archive)
    def test_privacy_precedence_over_other_integrity_failure(self):
        cs=[Collected('E00-10',None,None,status='INTEGRITY_FAILURE'),Collected('E00-11',None,None,status='PRIVACY_FAILURE')]
        result=assemble('FAILED_RUN',cs,Sanitizer(b'x'*16),context={'persistent_output':True,'mutation_attempted':True,'c3_attempted':False,'restore_attempted':False},scanner=strict_safe_scan)
        self.assertEqual(result.exit,23);self.assertIsNone(result.archive)
    def test_lab_conditions_do_not_forge_site(self):
        r=terminal_report();r['source_kind']='LAB'
        self.assertFalse(terminal_conditions(r,NOW,'synthetic-host','reg',B,CONTRACT_DIGEST,NOW-timedelta(hours=1),CP,source_kind='LAB')['host_ready'])
        self.reject(19,terminal,r,NOW,'synthetic-host','reg',B,CONTRACT_DIGEST,NOW-timedelta(hours=1),CP)

class EndpointMatrixTests(Check):
    def args(self):
        _,p,_,_=authority_case('SITE_VERIFY');p['semantic']['endpoints']=[{'endpoint_id':'a','context':'GUEST'},{'endpoint_id':'b','context':'GUEST'}]
        b={'endpoint_roles':{'a':'UBUNTU_ARCHIVE','b':'UBUNTU_SECURITY'},'windows_download_required':False,'offline_payload_refs':['SYNTHETIC_ONLY']}
        return p,b
    def test_both_guest_repository_roles(self):
        p,b=self.args();self.assertEqual(len(endpoint_matrix(p,b)),2)
    def test_windows_measurement_cannot_replace_guest(self):
        p,b=self.args();p['semantic']['endpoints'][1]['context']='WINDOWS';self.reject(10,endpoint_matrix,p,b)
    def test_offline_claim_needs_references(self):
        p,b=self.args();b['offline_payload_refs']=[];self.reject(15,endpoint_matrix,p,b)
    def test_declared_windows_download_needs_context(self):
        p,b=self.args();b['windows_download_required']=True;self.reject(10,endpoint_matrix,p,b)
    def test_unused_endpoint_roles_rejected(self):
        p,b=self.args();b['endpoint_roles']['hidden']='WINDOWS';self.reject(10,endpoint_matrix,p,b)

if __name__=='__main__':unittest.main()
