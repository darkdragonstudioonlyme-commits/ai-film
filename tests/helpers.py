"""SYNTHETIC WORKSPACE FIXTURES ONLY. Not LAB registration or SITE evidence.
Every receipt, SID, host identifier and measurement below is fabricated test input.
There is NO host backend in this revision that can accept this store as authority.
"""
from copy import deepcopy
from datetime import datetime,timezone
from aifilm_p00 import CONTRACT_DIGEST
from aifilm_p00.codec import canonical,sha256,digest
from aifilm_p00.plans import make_plan
from aifilm_p00.authority import PinnedStore,Context
from aifilm_p00.evidence import Collected
from aifilm_p00.errors import P00Error
from aifilm_p00.policy import GIB,TERMINAL_ASSERTIONS
NOW=datetime(2026,9,14,0,0,0,tzinfo=timezone.utc)
B=sha256(b'SYNTHETIC BUILD'); T=sha256(b'SYNTHETIC TEST SET'); CP=sha256(b'SYNTHETIC CHECKPOINT')
SID='S-1-5-21-101-202-303-1001'
PROFILE={'windows_build':'SYNTHETIC_BUILD','wsl_version':'2.7.14','kernel':'SYNTHETIC_KERNEL','network':'NAT','storage':'NTFS','startup':'CLEAN_P00'}

def binding(purpose='CREATE',execution_class='SITE'):
    return {'schema_version':1,'run_id':'synthetic-run','work_item':'IMPL-P00-001','execution_class':execution_class,
        'host_id':'synthetic-host','owner_sid':SID,'target':{'name':'AI Film thử','base_path':r'D:\Phim thử\Control','registration_id':None if purpose in ('CREATE','RESTORE_IMPORT') else 'SYNTHETIC-REG','user':'film'},
        'purpose':purpose,'contract_digest':CONTRACT_DIGEST,'build_digest':B,'test_set_digest':T,'profile':deepcopy(PROFILE),
        'before':{'target':'ABSENT','config_digest':sha256(b'config')},'expected_after':{'target':'SYNTHETIC-REG','config_digest':sha256(b'config')},
        'budgets':[{'volume_id':'volume1','roles':['OS','DISTRO'],'allocations':{'distro':20*GIB,'logs':1024}}],
        'payload_digest':None,'source_class':'CLEAN_P00','refs':{},'final_state':'RUNNING'}

def authority_case(purpose='CREATE',execution_class='SITE',omit=None,modify=None):
    pins={}; blobs={}
    def put(role,obj):
        value={'role':role,**deepcopy(obj)}; raw=canonical(value); ref=sha256(raw)
        blobs[ref]=raw; pins.setdefault(role,set()).add(ref); return ref
    reg={'host_id':'synthetic-host','execution_class':execution_class,'operator_sids':[SID],'withdrawn':False,
         'controller_external':True,'disposable':True,'no_real_credentials':True,'no_production_mappings':True}
    if modify and modify[0]=='registration': modify[1](reg)
    refs={
        'registration':put('registration',reg),
        'design':put('design',{'verdict':'PASS','contract_digest':CONTRACT_DIGEST,'withdrawn':False}),
        'code':put('code',{'verdict':'PASS','build_digest':B,'test_set_digest':T,'contract_digest':CONTRACT_DIGEST,'withdrawn':False})}
    mandatory=[f'T00-{i:02d}' for i in range(1,15)]+[f'F00-{i:02d}' for i in range(1,17)]
    refs['test_set']=put('test_set',{'test_set_digest':T,'mandatory_cases':mandatory,'native_required_cases':['T00-07']})
    results={}
    for case in mandatory:
        actual=put('measurement',{'source_kind':'LAB','lab_id':'SYNTHETIC_LAB','test_id':case,'fixture_only':True})
        obj={'test_id':case,'source_kind':'LAB','status':'PASS','actual_evidence_digest':actual,'build_digest':B,'test_set_digest':T,'contract_digest':CONTRACT_DIGEST,'lab_id':'SYNTHETIC_LAB','environment_kind':'WINDOWS_WSL_NATIVE','fixture_only':True}
        if modify and modify[0]=='test_result': modify[1](obj)
        results[case]=put('test_result',obj)
    q={'source_kind':'LAB','issuer_role':'VALIDATION','master_recorded':True,'status':'PASS','withdrawn':False,'gate_blockers':[],
       'issued_at':'2026-09-13T00:00:00Z','build_digest':B,'test_set_digest':T,'contract_digest':CONTRACT_DIGEST,
       'code_review_ref':refs['code'],'profile_rows':[{'purpose':purpose,'profile':deepcopy(PROFILE),'payload_digest':None}],
       'results':results,'lab_id':'SYNTHETIC_LAB','fixture_only':True}
    if modify and modify[0]=='qualification': modify[1](q)
    if omit!='qualification': refs['qualification']=put('qualification',q)
    refs['lab_plan']=put('lab_plan',{'host_id':'synthetic-host','build_digest':B,'approved':True,'withdrawn':False,'purposes':[purpose],'fixture_only':True})
    s=binding(purpose,execution_class); s['refs']=refs
    if purpose=='ENGINE': s['target']={k:None for k in s['target']}
    plan=make_plan(s,'2026-09-13T23:00:00Z')
    interface={'PASSIVE':'preflight','DISCOVERY':'preflight','SITE_VERIFY':'verify','TARGET_LIFECYCLE':'verify','HOST_RESTART':'verify','RESTORE_VERIFY':'verify','RECONCILIATION_ONLY':'verify','SUPPORT_BUNDLE':'support-bundle'}.get(purpose,'apply')
    approval={'plan_digest':plan['plan_digest'],'owner_sid':SID,'interface':interface,'purpose':purpose,
              'classes':sorted({op['class'] for op in s.get('operations',plan['semantic']['operations'])}),
              'issued_at':'2026-09-13T23:00:00Z','expires_at':'2026-09-14T23:00:00Z',
              'maintenance_start':'2026-09-13T23:00:00Z','maintenance_end':'2026-09-14T23:00:00Z','withdrawn':False}
    if modify and modify[0]=='approval': modify[1](approval)
    plan['approval_ref']=put('approval',approval)
    store=PinnedStore({k:frozenset(v) for k,v in pins.items()},blobs,'SYNTHETIC_WORKSPACE_ONLY')
    ctx=Context('synthetic-host',SID,execution_class,B,T,deepcopy(PROFILE),True,NOW)
    return interface,plan,ctx,store

def host():
    return {'os':'Windows 11','architecture':'x64','edition':'Pro','channel':'stable','support_end':'2027-09-14T00:00:00Z','virtualization':True}
def host_resources(): return {'installed_ram_bytes':8*GIB,'logical_cpu':4,'available_ram_bytes':2*GIB}
def guest_resources(): return {'logical_cpu':2,'mem_total_bytes':3*GIB,'mem_available_bytes':GIB,'fs_available_bytes':20*GIB}
def protection_pack():
    return {'host_id':'synthetic-host','coverage_complete':True,'owner_authorized':True,'source_witness':'quiesced','sealed_at':'2026-09-13T23:00:00Z','windows_writers_safe':True,'rows':[
        {'resource_id':'reg','authorized':True,'disposition':'DATA_BEARING_NONSENSITIVE','post_assertions':['content','health'],'post_actor':'owner',
         'no_writes_since_boundary':True,'retention_bound':True,'checkpoint_digest':CP,'restore_checkpoint_digest':CP,'restore_pass':True,'independent_ready':True,
         'accessible_without_source_runtime':True,'restore_environment':'ISO-EXTERNAL','proof_completed_at':'2026-09-13T22:00:00Z'}]}

def envelope(kind='ISO-EXTERNAL'):
    p={'kind':kind,'data_authorized':True,'controller_authorized':True,'checkpoint_digest':CP,'envelope_digest':sha256(b'envelope'),
       'no_auto_launch_qualified':True,'issued_at':'2026-09-13T23:00:00Z'}
    for k in ('controller_external','network_uplinks_blocked','no_production_writable_mapping','backup_of_record_protected','no_credential_forwarding','device_inventory_verified','allowed_write_surfaces_bound','registered_session','unused_destination','trusted_seed','complete_provenance','allowlisted_changes_only','no_custom_startup','no_credentials','ordinary_access_consented'): p[k]=True
    return p

def terminal_report():
    w={'host_boot':'b','runtime':'r','target_registration':'reg','guest_boot':'gb','init_session':'init','config_digest':sha256(b'config'),'activation_sequence':2}
    return {'source_kind':'SITE','host_id':'synthetic-host','target_id':'reg','build_digest':B,'contract_digest':CONTRACT_DIGEST,
            'started_at':'2026-09-13T23:40:00Z','ended_at':'2026-09-13T23:50:00Z','start_witness':w,'end_witness':deepcopy(w),
            'observed_boundary_during_sweep':False,'unresolved_source_operations':0,'checkpoint_digest':CP,
            'assertions':{name:{'status':'PASS','evidence_digest':sha256(name.encode()),'epoch_digest':digest(w)} for name in TERMINAL_ASSERTIONS}}

def evidence_record(eid,status='PASS'):
    return {'schema_version':1,'evidence_id':eid,'record_id':'synthetic-record-'+eid,'status':status,'source_kind':'DOCUMENT','work_item':'IMPL-P00-001',
            'run_id':'synthetic-run','step_id':'s0','operation':'FIXTURE','host_alias':'synthetic-host','target_alias':'synthetic-target',
            'collector_digest':B,'build_digest':B,'contract_digest':CONTRACT_DIGEST,'timestamp_utc':'2026-09-14T00:00:00Z','stage':'TERMINAL','route':'CREATE',
            'expected_ref':'synthetic/expected','actual_ref':'synthetic/actual','native_exit':0,'normalized_exit':0,'epoch_ref':None,
            'protected_ref':'synthetic/protected','protected_digest':CP,'safe_summary':{'status':status,'passed':status=='PASS'},'sensitivity':'PROTECTED'}

def collected(eid,status='PASS',summary=None,**kw):
    record=evidence_record(eid,status)
    if summary is not None: record['safe_summary']=summary
    raw=canonical(record)
    values={'evidence_id':eid,'record':record,'expected_bytes_digest':sha256(raw),'duration_ms':1,'bytes_seen':len(raw),'eof':True,'status':'COMPLETE','protected_access':True,'protected_integrity':True}
    values.update(kw); return Collected(**values)

class MemoryGuard:
    def __init__(self): self.busy=False
    def acquire(self):
        if self.busy: return False
        self.busy=True; return True
    def release(self): self.busy=False

class MemoryStorage:
    def __init__(self): self.fence=None; self.events=[]; self.fail_append=False; self.fail_write=False; self.fail_clear=False
    def load_fence(self): return deepcopy(self.fence)
    def write_fence(self,record):
        if self.fail_write: raise P00Error(18,'JOURNAL_IO')
        self.fence=deepcopy(record)
    def append_event(self,event):
        if self.fail_append: raise P00Error(18,'JOURNAL_IO')
        self.events.append(deepcopy(event))
    def clear_fence(self):
        if self.fail_clear: raise P00Error(18,'JOURNAL_IO')
        self.fence=None
