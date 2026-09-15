"""WORKSPACE fixtures only. None of these tests calls a Windows API or WSL."""
import base64
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch
from dataclasses import replace
from helpers import SID,NOW,B,T,authority_case
from aifilm_p00.errors import P00Error
from aifilm_p00.codec import canonical,digest,sha256
from aifilm_p00.native.security import *
from aifilm_p00.native.coordination import replay,frame,NativeGuard,MUTEX_NAME
from aifilm_p00.native.filesystem import same_path,normalized_handle_path
from aifilm_p00.native.trust import NativeStore,normalize_design,validate_payload_graph
from aifilm_p00.native.probes import parse_guest,GUEST_KEYS,parse_wsl_list,guest_command,host_command
from aifilm_p00.native.process import Command,Capture
from aifilm_p00.native.snapshot import logical_ref,extract_record,strict_safe_scan
from aifilm_p00.evidence import Sanitizer
from aifilm_p00.resume import bind_reconciliation,completed_steps
from aifilm_p00.plans import make_plan
from aifilm_p00.content import content_identity
from aifilm_p00.native.winapi import WinAPI

ROOT=Path(__file__).resolve().parents[1]
class Check(unittest.TestCase):
    def reject(self,code,fn,*args,**kwargs):
        with self.assertRaises(P00Error) as caught:fn(*args,**kwargs)
        self.assertEqual(int(caught.exception.code),code)
        return caught.exception.reason

class SecurityTests(Check):
    def sec(self,trustee=SID,mask=0x1f01ff,kind=0,**kwargs):
        values={'owner':SID,'dacl_present':True,'dacl_null':False,'protected':True,
                'aces':(Ace(kind,0,mask,trustee),)};values.update(kwargs);return Security(**values)
    def validate(self,value,**kwargs):
        return check_security(value,owners=ADMIN_OWNERS|{SID},writers=ADMIN_OWNERS|{SID},readers={SID},confidential=kwargs.pop('confidential',True),**kwargs)
    def test_valid_operator(self):self.validate(self.sec())
    def test_null_dacl(self):self.reject(12,self.validate,self.sec(dacl_null=True))
    def test_absent_dacl(self):self.reject(12,self.validate,self.sec(dacl_present=False))
    def test_untrusted_owner(self):self.reject(12,self.validate,self.sec(owner='S-1-1-0'))
    def test_world_writer(self):self.reject(12,self.validate,self.sec('S-1-1-0'))
    def test_world_reader_protected(self):self.reject(12,self.validate,self.sec('S-1-1-0',0x120089))
    def test_world_reader_system_binary_allowed(self):self.validate(self.sec('S-1-1-0',0x120089),confidential=False)
    def test_registry_set_value_denied(self):self.reject(12,self.validate,self.sec('S-1-1-0',2),confidential=False,registry=True)
    def test_registry_create_subkey_denied(self):self.reject(12,self.validate,self.sec('S-1-1-0',4),confidential=False,registry=True)
    def test_unsupported_object_ace(self):self.reject(12,self.validate,self.sec(kind=5))
    def test_deny_ace_does_not_grant(self):self.validate(self.sec('S-1-1-0',0xffffffff,kind=1))
    def test_require_protected(self):self.reject(12,self.validate,self.sec(protected=False),require_protected=True)
    def test_delete_child_right(self):self.reject(12,self.validate,self.sec('S-1-1-0',0x40),confidential=False)
    def test_metadata_acl_fixed(self):
        s=metadata_sddl(frozenset({SID}));self.assertTrue(s.startswith('D:P'));self.assertIn(SID,s);self.assertNotIn(';;;WD)',s)
    def test_mutex_acl_no_inheritance(self):self.assertNotIn('OICI',mutex_sddl(frozenset({SID})))
    def test_sid_injection(self):self.reject(10,metadata_sddl,frozenset({SID+')(A;;GA;;;WD)'}))

class JournalTests(Check):
    def log(self,events):
        raw=b'';prev=None
        for i,e in enumerate(events):
            f=frame(e,i,prev);raw+=f;prev=__import__('json').loads(f)['sha256']
        return raw
    def genesis(self):return {'kind':'GENESIS','host_id':'synthetic','root_identity':{'file_id':1}}
    def fence(self,state='INTENT'):
        return {'run_id':'run','host_id':'synthetic','owner_sid':SID,'plan_digest':'a'*64,'action':'TEST','state':state}
    def test_valid_genesis_no_fence(self):self.assertIsNone(replay(self.log([self.genesis()]))['fence'])
    def test_intent_recovered(self):
        f=self.fence();self.assertEqual(replay(self.log([self.genesis(),{'kind':'SET_FENCE','record':f}]))['fence'],f)
    def test_truncated_newline(self):self.reject(15,replay,self.log([self.genesis()])[:-1])
    def test_truncated_frame(self):self.reject(15,replay,self.log([self.genesis()])+b'{')
    def test_empty_not_no_fence(self):self.reject(15,replay,b'')
    def test_forged_frame(self):self.reject(15,replay,self.log([self.genesis()]).replace(b'synthetic',b'otherhost'))
    def test_duplicate_genesis(self):self.reject(15,replay,self.log([self.genesis(),self.genesis()]))
    def test_nonterminal_clear(self):
        f=self.fence();self.reject(15,replay,self.log([self.genesis(),{'kind':'SET_FENCE','record':f},{'kind':'CLEAR_FENCE','fence_digest':digest(f)}]))
    def test_terminal_clear(self):
        f=self.fence('TERMINAL');self.assertIsNone(replay(self.log([self.genesis(),{'kind':'SET_FENCE','record':f},{'kind':'CLEAR_FENCE','fence_digest':digest(f)}]))['fence'])
    def test_uncertain_never_expires(self):
        f=self.fence('UNCERTAIN');f['expired_at']='1970-01-01T00:00:00Z'
        self.assertEqual(replay(self.log([self.genesis(),{'kind':'SET_FENCE','record':f}]))['fence']['state'],'UNCERTAIN')
    def test_cannot_replace_run(self):
        f=self.fence();g={**f,'run_id':'different'}
        self.reject(15,replay,self.log([self.genesis(),{'kind':'SET_FENCE','record':f},{'kind':'SET_FENCE','record':g}]))
    def test_wrong_release_digest(self):
        f=self.fence('TERMINAL');self.reject(15,replay,self.log([self.genesis(),{'kind':'SET_FENCE','record':f},{'kind':'CLEAR_FENCE','fence_digest':'b'*64}]))

class ProbeTests(Check):
    def fixture(self):
        value={k:'synthetic' for k in GUEST_KEYS}
        value.update(uid='1000',gid='1000',pid1_start_ticks='12',logical_cpu='2',mem_total_kib='4194304',mem_available_kib='2097152',
                     fs_available_kib='33554432',completed='1',home_access_writable='1',kernel_boot_id='01234567-89ab-cdef-0123-456789abcdef',wsl_conf_sha256='ABSENT')
        return value
    def wire(self,data):return b''.join(k.encode()+b'\t'+base64.b64encode(str(v).encode())+b'\n' for k,v in data.items())
    def test_complete_observation_not_asserted_sudo(self):
        v=parse_guest(self.wire(self.fixture()));self.assertEqual(v['uid'],1000);self.assertEqual(v['admin_ready'],'UNKNOWN')
    def test_missing_completed(self):
        v=self.fixture();del v['completed'];self.reject(22,parse_guest,self.wire(v))
    def test_unknown_field(self):
        v=self.fixture();v['password']='secret';self.reject(15,parse_guest,self.wire(v))
    def test_duplicate_field(self):self.reject(15,parse_guest,self.wire(self.fixture())+b'uid\tMTAwMA==\n')
    def test_malformed_base64(self):self.reject(15,parse_guest,b'uid\t!!\n')
    def test_invalid_number(self):
        v=self.fixture();v['uid']='-1';self.reject(15,parse_guest,self.wire(v))
    def test_number_overflow(self):
        v=self.fixture();v['uid']=str(2**63);self.reject(15,parse_guest,self.wire(v))
    def test_incomplete_frame(self):self.reject(22,parse_guest,self.wire(self.fixture())[:-1])
    def test_utf16_wsl_names(self):self.assertEqual(parse_wsl_list('AI Film thử\r\n'.encode('utf-16-le')),['AI Film thử'])
    def test_utf8_wsl_names(self):self.assertEqual(parse_wsl_list('AI Film thử\n'.encode()),['AI Film thử'])
    def test_duplicate_casefold_name(self):self.reject(15,parse_wsl_list,b'Target\ntarget\n')
    def test_root_probe_rejected(self):self.reject(10,guest_command,r'C:\Windows\System32','target','root',b'code')
    def test_static_sh_data_boundaries(self):
        c=guest_command(r'C:\Windows\System32','AI Film thử','film',b'static');self.assertIn('--exec',c.argv);self.assertEqual(c.stdin,b'static');c.validate()
    def test_host_no_policy_bypass(self):
        c=host_command(r'C:\Windows\System32',r'C:\Build\probe.ps1','HOST');self.assertNotIn('-ExecutionPolicy',c.argv);self.assertIn('-NoProfile',c.argv)
    def test_host_operation_scope(self):self.reject(10,host_command,r'C:\Windows\System32',r'C:\Build\p.ps1','INSTALL')

class CommandCaptureTests(Check):
    def test_explicit_executable(self):Command((r'C:\Windows\System32\wsl.exe','--version'),'VERSION',30).validate()
    def test_search_path_forbidden(self):self.reject(10,Command(('wsl.exe','--version'),'VERSION',30).validate)
    def test_newline_argument(self):self.reject(10,Command((r'C:\a.exe','bad\narg'),'A',30).validate)
    def test_null_argument(self):self.reject(10,Command((r'C:\a.exe','x\0y'),'A',30).validate)
    def test_unbounded_timeout(self):self.reject(10,Command((r'C:\a.exe',),'A',7201).validate)
    def test_large_stdin(self):self.reject(10,Command((r'C:\a.exe',),'A',30,b'a'*(1024**2+1)).validate)
    def test_capture_cap(self):
        v=Capture(3);v.feed(b'123456');v.feed(b'789');self.assertEqual(v.bytes(),b'123');self.assertTrue(v.truncated);self.assertEqual(v.seen,9)
    def test_cap_equal_not_truncated_but_requires_eof(self):
        v=Capture(3);v.feed(b'123');self.assertFalse(v.truncated);self.assertFalse(v.eof)
    def test_no_native_api_on_workspace(self):self.reject(11,WinAPI)

class PathRecordTests(Check):
    def test_same_path_casefold(self):self.assertTrue(same_path(r'C:\Phim\Data',r'c:\phim\data'))
    def test_handle_prefix(self):self.assertEqual(normalized_handle_path('\\\\?\\C:\\Data'),r'C:\Data')
    def test_unc_rejected(self):self.reject(16,normalized_handle_path,r'\\?\UNC\server\share')
    def test_logical_ref(self):self.assertEqual(logical_ref('run/observations/host.json#host'),('run','observations/host.json','host'))
    def test_escape_ref(self):self.reject(10,logical_ref,'run/../secret#id')
    def test_multiple_hash_ref(self):self.reject(15,logical_ref,'run/a#id#other')
    def test_missing_record_not_whole_file(self):self.reject(15,extract_record,canonical({'record_id':'x'}),'y')
    def test_duplicate_record(self):self.reject(15,extract_record,canonical({'records':[{'record_id':'x'},{'record_id':'x'}]}),'x')
    def test_valid_record(self):self.assertEqual(extract_record(canonical({'record_id':'x','a':1}),'x')['a'],1)

class TrustTests(Check):
    def policy(self,docs):
        blobs={};pins={}
        for role,value in docs:
            raw=canonical(value);ref=sha256(raw);blobs[ref]=raw.decode();pins.setdefault(role,[]).append(ref)
        return {'schema_version':1,'host_id':'SYNTHETIC','operator_sids':[SID],'role_pins':pins,'blobs':blobs,'withdrawn_refs':[],'generation':1}
    def test_unpinned_document(self):
        p=self.policy([('code',{'role':'code'})]);s=NativeStore(canonical(p),ROOT/'contracts');self.reject(15,s.get,'code','a'*64)
    def test_modified_blob(self):
        p=self.policy([('code',{'role':'code'})]);ref=next(iter(p['blobs']));p['blobs'][ref]+=' ';self.reject(15,NativeStore,canonical(p),ROOT/'contracts')
    def test_withdrawal(self):
        p=self.policy([('code',{'role':'code'})]);ref=next(iter(p['blobs']));p['withdrawn_refs']=[ref];s=NativeStore(canonical(p),ROOT/'contracts');self.reject(11,s.get,'code',ref)
    def test_role_substitution(self):
        p=self.policy([('code',{'role':'design'})]);s=NativeStore(canonical(p),ROOT/'contracts');self.reject(15,s.get,'code',next(iter(p['blobs'])))
    def test_actual_review_normalization(self):
        import json
        raw=json.loads((ROOT/'contracts/DESIGN_REVIEW_APPROVAL_V2.json').read_text());v=normalize_design(raw,ROOT/'contracts')
        self.assertEqual(v['raw_review_id'],'REVIEW-P00-002')
    def test_review_fail_not_normalized(self):
        import json
        raw=json.loads((ROOT/'contracts/DESIGN_REVIEW_APPROVAL_V2.json').read_text());raw['VERDICT']='FAIL';self.reject(15,normalize_design,raw,ROOT/'contracts')
    def test_forged_contract_hash(self):
        import json
        raw=json.loads((ROOT/'contracts/DESIGN_REVIEW_APPROVAL_V2.json').read_text());raw['NORMATIVE_CONTRACT_SET'][0]['sha256']='a'*64;self.reject(15,normalize_design,raw,ROOT/'contracts')
    def test_ambiguous_authority(self):
        p=self.policy([('code',{'role':'code','i':1}),('code',{'role':'code','i':2})]);s=NativeStore(canonical(p),ROOT/'contracts');self.reject(15,s.one,'code')
    def test_native_scripts_in_source_digest(self):
        identity=content_identity(ROOT);paths={r['path'] for r in identity['source_members']};self.assertIn('native/host-observe.ps1',paths);self.assertIn('native/guest-observe.sh',paths)

class ReconciliationTests(Check):
    def setup(self):
        _,original,_,_=authority_case('CREATE')
        interface,request,ctx,store=authority_case('RECONCILIATION_ONLY')
        request['semantic']['target']=deepcopy(original['semantic']['target'])
        blob=canonical({'role':'original_plan','plan':original});ref=sha256(blob)
        pins={k:set(v) for k,v in store.pins.items()};blobs=dict(store.blobs);pins['original_plan']={ref};blobs[ref]=blob
        request['semantic']['refs']['original_plan']=ref;request['plan_digest']=digest(request['semantic'])
        approval=store.get('approval',request['approval_ref']);approval['plan_digest']=request['plan_digest']
        raw=canonical(approval);a=sha256(raw);pins['approval']={a};blobs[a]=raw;request['approval_ref']=a
        # Current qualification profile still matches the same purpose and fixture.
        from aifilm_p00.authority import PinnedStore
        store=PinnedStore({k:frozenset(v) for k,v in pins.items()},blobs,'SYNTHETIC_WORKSPACE_ONLY')
        fence={'run_id':original['semantic']['run_id'],'host_id':ctx.host_id,'owner_sid':SID,'plan_digest':original['plan_digest'],'action':'INSTALL_DISTRO'}
        return original,request,ctx,store,fence
    def test_new_approval_original_fence_no_hash_rewrite(self):
        o,p,c,s,f=self.setup();before=canonical(o);b=bind_reconciliation(p,c,s,f)
        self.assertEqual(b.authority.plan_digest,o['plan_digest']);self.assertEqual(b.authority.purpose,'RECONCILIATION_ONLY')
        self.assertEqual(b.reconciliation_plan_digest,p['plan_digest']);self.assertEqual(canonical(o),before)
    def test_wrong_original_fence(self):
        o,p,c,s,f=self.setup();f['plan_digest']='b'*64;self.reject(15,bind_reconciliation,p,c,s,f)
    def test_wrong_actor(self):
        o,p,c,s,f=self.setup();f['owner_sid']='S-1-5-18';self.reject(12,bind_reconciliation,p,c,s,f)
    def test_unrelated_action(self):
        o,p,c,s,f=self.setup();f['action']='UNREGISTER';self.reject(15,bind_reconciliation,p,c,s,f)
    def test_empty_history_no_progress(self):
        o,p,c,s,f=self.setup();self.assertEqual(completed_steps([],o),{})
