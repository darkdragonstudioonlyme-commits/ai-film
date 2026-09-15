"""Deterministic D00-08 plans. This module never invokes a host command."""
from copy import deepcopy
from . import CONTRACT_DIGEST
from .codec import fields,token,hash_value,integer,digest,windows_path,distro_name,user_name
from .errors import require

OPERATIONS={
 'PASSIVE': [('OBSERVE_HOST','C0')],
 'DISCOVERY': [('PROBE_GUEST','C1')],
 'ENGINE': [('ENABLE_PREREQUISITES','C3'),('INSTALL_RUNTIME','C3'),('AWAIT_OWNER_RESTART','C3')],
 'CREATE': [('INSTALL_DISTRO','C2'),('AWAIT_OWNER_USER_INIT','C2'),('CREATE_WORKSPACE','C2')],
 'ADOPT': [('CREATE_WORKSPACE','C2')],
 'RESTORE_EXPORT': [('EXPORT_CHECKPOINT','C1')],
 'RESTORE_IMPORT': [('IMPORT_NEW_CLONE','C2')],
 'SITE_VERIFY': [('VERIFY_TERMINAL','C1')],
 'TARGET_LIFECYCLE': [('STOP_START_TARGET','C1')],
 'HOST_RESTART': [('AWAIT_OWNER_RESTART','C3')],
 'RESTORE_VERIFY': [('VERIFY_CLONE','C1'),('STOP_RETAIN_CLONE','C1')],
 'RECONCILIATION_ONLY': [('OBSERVE_PENDING_ACTION','C0')],
 'SUPPORT_BUNDLE': [('PUBLISH_SAFE_BUNDLE','C0')],
}
INTERFACES={
 'preflight':{'PASSIVE','DISCOVERY'},
 'apply':{'ENGINE','CREATE','ADOPT','RESTORE_EXPORT','RESTORE_IMPORT'},
 'verify':{'SITE_VERIFY','TARGET_LIFECYCLE','HOST_RESTART','RESTORE_VERIFY','RECONCILIATION_ONLY'},
 'support-bundle':{'SUPPORT_BUNDLE'},
}
REQUIRED={'schema_version','run_id','work_item','execution_class','host_id','owner_sid','target',
          'purpose','contract_digest','build_digest','test_set_digest','profile','before',
          'expected_after','budgets','payload_digest','source_class','refs','final_state'}
OPTIONAL={'endpoints','bundle_scope','expected_checkpoint','expected_envelope','scratch_bytes'}

def check_plan(plan:dict)->dict:
    fields(plan,{'semantic','plan_digest','report'},{'approval_ref'})
    s=fields(plan['semantic'],REQUIRED|{'operations'},OPTIONAL)
    require(s['schema_version']==1,10,'UNSUPPORTED_SCHEMA')
    for key in ('run_id','work_item','host_id'): token(s[key])
    require(s['execution_class'] in ('LAB','SITE'),10,'EXECUTION_CLASS_REQUIRED')
    for sid in [s['owner_sid']]:
        require(type(sid) is str and sid.startswith('S-1-') and all(c.isdigit() or c in 'S-' for c in sid),10,'INVALID_SID')
    for key in ('contract_digest','build_digest','test_set_digest'): hash_value(s[key])
    require(s['contract_digest']==CONTRACT_DIGEST,16,'CONTRACT_MISMATCH')
    require(s['purpose'] in OPERATIONS,10,'PURPOSE_NOT_ALLOWED')
    require(s['operations']==[{'action':a,'class':c} for a,c in OPERATIONS[s['purpose']]],10,'OPERATION_SCOPE_MISMATCH')
    fields(s['target'],{'name','base_path','registration_id','user'})
    absent=all(v is None for v in s['target'].values())
    if s['purpose']=='ENGINE':
        require(absent,10,'ENGINE_TARGET_MUST_BE_ABSENT')
    elif absent:
        require(s['purpose'] in ('PASSIVE','SUPPORT_BUNDLE','RECONCILIATION_ONLY'),10,'TARGET_MUST_BE_BOUND')
    else:
        distro_name(s['target']['name']); windows_path(s['target']['base_path']); user_name(s['target']['user'])
        rid=s['target']['registration_id']
        require(rid is None or type(rid) is str,10,'INVALID_REGISTRATION_ID')
        if s['purpose'] in ('CREATE','RESTORE_IMPORT'):
            require(rid is None,16,'NEW_TARGET_ALREADY_BOUND')
    for key in ('profile','before','expected_after','refs'):
        require(type(s[key]) is dict,10,'OBJECT_REQUIRED')
    require(s['final_state'] in ('RUNNING','STOPPED_RETAINED','OPERATOR_PENDING'),10,'INVALID_FINAL_STATE')
    require(s['source_class'] in ('NOT_YET_CREATED','CLEAN_P00','ADOPT_NONSENSITIVE_QUIESCED','SYNTHETIC_LAB','UNKNOWN','SENSITIVE'),10,'INVALID_SOURCE_CLASS')
    if s['payload_digest'] is not None: hash_value(s['payload_digest'])
    require(type(s['budgets']) is list and bool(s['budgets']),10,'BUDGET_REQUIRED')
    seen=set()
    for b in s['budgets']:
        fields(b,{'volume_id','roles','allocations'})
        token(b['volume_id']); require(b['volume_id'] not in seen,10,'DUPLICATE_VOLUME'); seen.add(b['volume_id'])
        require(type(b['roles']) is list and bool(b['roles']) and set(b['roles'])<={'OS','DISTRO','EVIDENCE','BACKUP'},10,'INVALID_VOLUME_ROLE')
        require(type(b['allocations']) is dict and bool(b['allocations']),10,'ALLOCATION_REQUIRED')
        for name,size in b['allocations'].items(): token(name); integer(size)
    require('approval' not in s['refs'],10,'APPROVAL_MUST_BE_DETACHED')
    for role,ref in s['refs'].items(): token(role); hash_value(ref)
    if 'approval_ref' in plan: hash_value(plan['approval_ref'])
    require(type(s.get('scratch_bytes',0)) is int and 0<=s.get('scratch_bytes',0)<=64*1024**2,10,'SCRATCH_LIMIT')
    require(plan['plan_digest']==digest(s),15,'PLAN_INTEGRITY')
    fields(plan['report'],{'created_at'})
    return s

def make_plan(binding:dict,created_at:str)->dict:
    fields(binding,REQUIRED,OPTIONAL)
    s=deepcopy(binding)
    require(s['purpose'] in OPERATIONS,10,'PURPOSE_NOT_ALLOWED')
    s['operations']=[{'action':a,'class':c} for a,c in OPERATIONS[s['purpose']]]
    plan={'semantic':s,'plan_digest':digest(s),'report':{'created_at':created_at}}
    check_plan(plan)
    return plan

def interface_check(interface:str,plan:dict):
    s=check_plan(plan)
    require(interface in INTERFACES and s['purpose'] in INTERFACES[interface],10,'PURPOSE_NOT_ALLOWED')
    return s

def semantic_diff(before:dict,after:dict)->list:
    """Actual structural difference; no interpolation or shell expressions."""
    result=[]
    for key in sorted(set(before)|set(after)):
        if before.get(key)!=after.get(key) or (key in before)!=(key in after):
            result.append({'field':key,'before_present':key in before,'after_present':key in after,
                           'before':before.get(key),'after':after.get(key)})
    return result
