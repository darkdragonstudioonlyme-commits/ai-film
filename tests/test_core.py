import unittest
from copy import deepcopy
from dataclasses import replace
from datetime import timedelta
from aifilm_p00.codec import *
from aifilm_p00.errors import P00Error
from aifilm_p00.plans import *
from aifilm_p00.policy import *
from aifilm_p00.authority import authorize
from aifilm_p00.admission import Coordinator
from aifilm_p00.windows_commands import *
from helpers import *

class Checks(unittest.TestCase):
    def reject(self,code,fn,*args,**kwargs):
        with self.assertRaises(P00Error) as cm: fn(*args,**kwargs)
        self.assertEqual(int(cm.exception.code),code)
        return cm.exception.reason

class CodecTests(Checks):
    def test_unicode_round_trip(self): self.assertEqual(loads(canonical({'phim':'Việt Nam'})),{'phim':'Việt Nam'})
    def test_key_order_deterministic(self): self.assertEqual(digest({'a':1,'b':2}),digest({'b':2,'a':1}))
    def test_duplicate_key(self): self.reject(10,loads,b'{"a":1,"a":2}')
    def test_nonfinite(self): self.reject(10,loads,b'{"x":NaN}')
    def test_invalid_utf8(self): self.reject(10,loads,b'\xff')
    def test_size_cap(self): self.reject(10,loads,b' '*(MAX_JSON+1))
    def test_depth_cap(self): self.reject(10,loads,'['*40+'0'+']'*40)
    def test_bool_not_integer(self): self.reject(10,integer,True)
    def test_local_timestamp(self): self.reject(10,instant,'2026-09-14T12:00:00')
    def test_non_utc_timestamp(self): self.reject(10,instant,'2026-09-14T12:00:00+07:00')
    def test_unicode_space_windows_path(self): self.assertEqual(windows_path(r'D:\Phim Việt\Control'),r'D:\Phim Việt\Control')
    def test_safe_error_no_raw_value(self):
        reason=self.reject(10,windows_path,'MY_SECRET\n'); self.assertNotIn('MY_SECRET',reason)

BAD_PATHS=['\\\\server\\share', '\\\\?\\C:\\x', 'C:\\x:secret', 'C:\\..\\x', 'C:\\folder\\..', 'C:\\NUL', 'C:\\CON.txt', 'C:\\COM1', 'C:\\a.', 'C:\\a ', 'C:\\', 'relative', 'C:/x', 'C:\\x\n', 'C:\\a?b', 'C:\\a|b']
for i,p in enumerate(BAD_PATHS):
    setattr(CodecTests,f'test_reject_windows_path_{i:02}',lambda self,p=p:self.reject(10,windows_path,p))
for i,p in enumerate(('../secret','/absolute','dir/../secret','dir//file','dir\\file','file#record','file:ads')):
    setattr(CodecTests,f'test_reject_relative_{i:02}',lambda self,p=p:self.reject(10,relative,p))

class PlanTests(Checks):
    def test_timestamp_not_semantic(self):
        s=binding(); a=make_plan(s,'2026-01-01T00:00:00Z'); b=make_plan(s,'2026-01-02T00:00:00Z'); self.assertEqual(a['plan_digest'],b['plan_digest'])
    def test_approval_detached_no_self_hash(self):
        _,p,_,_=authority_case(); self.assertEqual(check_plan(p),p['semantic'])
    def test_change_semantic_changes_hash(self):
        s=binding(); a=make_plan(s,'x'); s['target']['name']='other'; self.assertNotEqual(a['plan_digest'],make_plan(s,'x')['plan_digest'])
    def test_plan_tamper(self):
        p=make_plan(binding(),'x'); p['semantic']['target']['name']='other'; self.reject(15,check_plan,p)
    def test_no_arbitrary_operation(self):
        p=make_plan(binding(),'x'); p['semantic']['operations']=[{'action':'UNREGISTER','class':'C2'}]; p['plan_digest']=digest(p['semantic']); self.reject(10,check_plan,p)
    def test_verify_cannot_import(self): self.reject(10,interface_check,'verify',make_plan(binding('RESTORE_IMPORT'),'x'))
    def test_create_future_guest_not_required(self): self.assertEqual(make_plan(binding(),'x')['semantic']['target']['registration_id'],None)
    def test_duplicate_volume_rejected(self):
        b=binding(); b['budgets']*=2; self.reject(10,make_plan,b,'x')
    def test_scratch_cap(self):
        b=binding(); b['scratch_bytes']=64*1024**2+1; self.reject(10,make_plan,b,'x')
    def test_approval_inside_semantic_rejected(self):
        b=binding(); b['refs']['approval']=B; self.reject(10,make_plan,b,'x')
    def test_root_user_rejected(self):
        b=binding(); b['target']['user']='root'; self.reject(10,make_plan,b,'x')
    def test_extra_cli_namespace_cannot_bind(self):
        b=binding(); b['lock_path']='fake'; self.reject(10,make_plan,b,'x')

class PolicyTests(Checks):
    def test_host_profile(self): host_profile(host(),NOW)
    def test_support_margin_under(self):
        h=host(); h['support_end']=(NOW+timedelta(days=90,seconds=-1)).isoformat(); self.reject(11,host_profile,h,NOW)
    def test_support_margin_exact(self):
        h=host(); h['support_end']=(NOW+timedelta(days=90)).isoformat(); host_profile(h,NOW)
    def test_runtime_floor(self): runtime_profile({'status':'PRESENT','packaged':True,'channel':'stable','version':'2.4.10'})
    def test_runtime_old(self): self.reject(11,runtime_profile,{'status':'PRESENT','packaged':True,'channel':'stable','version':'2.4.9'})
    def test_no_ttl_plan_drift(self): self.reject(16,drift,{'a':1},{'a':2})
    def test_exact_budget(self):
        b=binding()['budgets']; needed=20*GIB+20*GIB+1024; self.assertEqual(budget_check(b,{'volume1':needed})[0]['reserve'],20*GIB)
    def test_budget_backup_volume_separate(self):
        b=binding()['budgets']+[{'volume_id':'backup','roles':['BACKUP'],'allocations':{'export':GIB}}]; self.reject(13,budget_check,b,{'volume1':100*GIB,'backup':6*GIB-1})
    def test_budget_adds_allocations_not_max(self):
        b=[{'volume_id':'v','roles':['BACKUP'],'allocations':{'export':2*GIB,'clone':2*GIB}}]; self.reject(13,budget_check,b,{'v':8*GIB})
    def test_protection_ok(self): protection(protection_pack(),'synthetic-host','reg',NOW,'quiesced')
    def test_target_not_hidden_by_empty_rows(self):
        p=protection_pack(); p['rows']=[]; p['clean_host_absent']=True; self.reject(11,protection,p,'synthetic-host','reg',NOW,'quiesced')
    def test_no_writes_boundary_drift(self): self.reject(16,protection,protection_pack(),'synthetic-host','reg',NOW,'writer-resumed')
    def test_protection_independent(self):
        p=protection_pack(); p['rows'][0]['accessible_without_source_runtime']=False; self.reject(11,protection,p,'synthetic-host','reg',NOW,'quiesced')
    def test_protection_checkpoint_exact(self):
        p=protection_pack(); p['rows'][0]['restore_checkpoint_digest']=B; self.reject(15,protection,p,'synthetic-host','reg',NOW,'quiesced')
    def test_clean_target_still_needs_backup(self):
        p=protection_pack(); p['rows'][0]['disposition']='CLEAN_REPRODUCIBLE_NON_TARGET'; p['rows'][0]['restore_pass']=False; self.reject(11,protection,p,'synthetic-host','reg',NOW,'quiesced')
    def test_affected_postcheck_missing(self): self.reject(20,c3_postconditions,protection_pack()['rows'],[])
    def test_affected_postcheck_failed(self): self.reject(19,c3_postconditions,protection_pack()['rows'],[{'resource_id':'reg','authorized':True,'status':'FAIL','assertions':['content','health']}])
    def test_restore_external(self):
        p=envelope(); self.assertEqual(restore_envelope(p,'ADOPT_NONSENSITIVE_QUIESCED','SITE',CP,NOW,p['envelope_digest']),'ISO_EXTERNAL_PREBOOT_PROOF')
    def test_restore_dirty_same_host(self):
        p=envelope('SAME_HOST_CLEAN'); p['no_custom_startup']=False; self.reject(11,restore_envelope,p,'CLEAN_P00','SITE',CP,NOW,p['envelope_digest'])
    def test_restore_sensitive_block(self):
        p=envelope(); self.reject(11,restore_envelope,p,'SENSITIVE','SITE',CP,NOW,p['envelope_digest'])
    def test_restore_same_host_not_pre_c3(self):
        p=envelope('SAME_HOST_CLEAN'); self.reject(11,restore_envelope,p,'CLEAN_P00','SITE',CP,NOW,p['envelope_digest'],pre_c3=True)
    def test_restore_synthetic_not_site(self):
        p=envelope(); self.reject(12,restore_envelope,p,'SYNTHETIC_LAB','SITE',CP,NOW,p['envelope_digest'])
    def test_envelope_changed(self):
        p=envelope(); self.reject(16,restore_envelope,p,'CLEAN_P00','SITE',CP,NOW,B)
    def terminal_call(self,r): return terminal(r,NOW,'synthetic-host','reg',B,CONTRACT_DIGEST,NOW-timedelta(hours=1),CP)
    def test_terminal_current(self): self.assertFalse(self.terminal_call(terminal_report())['host_ready'])
    def test_terminal_old_network(self):
        r=terminal_report(); r['assertions']['network']['epoch_digest']=B; self.reject(19,self.terminal_call,r)
    def test_terminal_mixed_epoch(self):
        r=terminal_report(); r['end_witness']['guest_boot']='different'; self.reject(19,self.terminal_call,r)
    def test_terminal_host_mismatch(self):
        r=terminal_report(); r['source_kind']='LAB'; self.reject(19,self.terminal_call,r)
    def test_terminal_expired(self):
        r=terminal_report(); r['started_at']='2026-09-13T23:10:00Z'; r['ended_at']='2026-09-13T23:20:00Z'; self.reject(19,self.terminal_call,r)
    def test_terminal_too_long(self):
        r=terminal_report(); r['started_at']='2026-09-13T23:00:00Z'; self.reject(19,self.terminal_call,r)
    def test_terminal_network_fail(self):
        r=terminal_report(); r['assertions']['network']['status']='FAIL'; self.reject(19,self.terminal_call,r)

for group,factory,thresholds in [('host',host_resources,HOST_FLOORS),('guest',guest_resources,GUEST_FLOORS)]:
    for key,value in thresholds.items():
        for offset in (-1,0,1):
            def check(self,key=key,value=value,offset=offset,factory=factory,guest=(group=='guest')):
                data=factory(); data[key]=value+offset
                if offset<0:self.reject(13,floors,data,guest)
                else:floors(data,guest)
            setattr(PolicyTests,f'test_floor_{group}_{key}_{offset+1}',check)

class AuthorityTests(Checks):
    def test_site_valid_synthetic_chain(self):
        i,p,c,s=authority_case(); self.assertEqual(authorize(i,p,c,s).purpose,'CREATE')
    def test_registered_lab_needs_no_prior_qualification(self):
        i,p,c,s=authority_case(execution_class='LAB',omit='qualification'); authorize(i,p,c,s)
    def test_missing_qualification(self):
        i,p,c,s=authority_case(omit='qualification'); self.reject(11,authorize,i,p,c,s)
    def test_site_faked_lab_flag(self):
        i,p,c,s=authority_case(execution_class='LAB'); c=replace(c,registered_class='SITE'); self.reject(12,authorize,i,p,c,s)
    def test_wrong_sid(self):
        i,p,c,s=authority_case(); c=replace(c,execution_sid='S-1-5-99'); self.reject(12,authorize,i,p,c,s)
    def test_untrusted_receipt(self):
        i,p,c,s=authority_case(); del s.pins['qualification']; self.reject(15,authorize,i,p,c,s)
    def test_receipt_bytes_tampered(self):
        i,p,c,s=authority_case(); s.blobs[p['semantic']['refs']['qualification']]=b'{}'; self.reject(15,authorize,i,p,c,s)
    def test_fake_native_result_no_match(self):
        i,p,c,s=authority_case(modify=('test_result',lambda x:x.update(environment_kind='WORKSPACE'))); self.reject(11,authorize,i,p,c,s)
    def test_lab_id_mismatch(self):
        i,p,c,s=authority_case(modify=('test_result',lambda x:x.update(lab_id='another'))); self.reject(16,authorize,i,p,c,s)
    def test_exact_profile_mismatch(self):
        i,p,c,s=authority_case(); c=replace(c,profile={**c.profile,'network':'mirrored'}); self.reject(16,authorize,i,p,c,s)
    def test_discovery_qualification_not_create(self):
        i,p,c,s=authority_case(modify=('qualification',lambda x:x['profile_rows'][0].update(purpose='DISCOVERY'))); self.reject(16,authorize,i,p,c,s)
    def test_approval_expired(self):
        i,p,c,s=authority_case(modify=('approval',lambda x:x.update(expires_at='2026-09-13T23:59:59Z'))); self.reject(12,authorize,i,p,c,s)
    def test_no_self_extended_approval(self):
        i,p,c,s=authority_case(modify=('approval',lambda x:x.update(expires_at='2026-10-13T23:59:59Z'))); self.reject(12,authorize,i,p,c,s)

for name,changes,expected in [('failed',{'status':'FAIL'},11),('withdrawn',{'withdrawn':True},11),('expired',{'issued_at':'2026-07-01T00:00:00Z'},11),('future',{'issued_at':'2026-09-15T00:00:00Z'},11),('new_blocker',{'gate_blockers':['synthetic']},11),('wrong_build',{'build_digest':T},16),('wrong_testset',{'test_set_digest':B},16),('missing_results',{'results':{}},11)]:
    def check(self,changes=changes,expected=expected):
        i,p,c,s=authority_case(modify=('qualification',lambda x:x.update(changes))); self.reject(expected,authorize,i,p,c,s)
    setattr(AuthorityTests,'test_qualification_'+name,check)
