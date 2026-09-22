#!/usr/bin/env python3
"""Pure reviewed V03 temporal-authority catalog/schema helpers; no native actions."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,re
from pathlib import Path,PureWindowsPath

MODES=frozenset({'CONCRETE_PRE_V03','STAGE_DERIVED','ENTRY_PROBE_AUTHORITY','FENCE_BOUND_RECONCILIATION'})
EXPECTED_COUNTS={'CONCRETE_PRE_V03':94,'STAGE_DERIVED':15,'ENTRY_PROBE_AUTHORITY':10,'FENCE_BOUND_RECONCILIATION':14}
DOCUMENT_CASES=frozenset({'T00-01'})
H64=re.compile(r'^[0-9a-f]{64}$')
PROOF_SPECS={
 'source_manifest':{'scope_fields':['host_id','target_registration','source_class'],'owner_assertion':True,'boundary':'AFTER_TARGET_IDENTITY_OBSERVED'},
 'protection':{'scope_fields':['host_id','source_witness'],'owner_assertion':True,'boundary':'AFTER_CURRENT_PROTECTION_BOUNDARY_OBSERVED_BEFORE_C3'},
 'restore_envelope':{'scope_fields':['host_id','checkpoint_digest','envelope_digest'],'owner_assertion':False,'boundary':'AFTER_CHECKPOINT_IDENTITY_AND_DESTINATION_ISOLATION_OBSERVED'},
 'user_init_receipt':{'scope_fields':['host_id','plan_digest','target_registration','user'],'owner_assertion':False,'boundary':'AFTER_OWNER_USER_INIT_OBSERVED'},
 'c3_postchecks':{'scope_fields':['host_id','plan_digest','host_boot'],'owner_assertion':True,'boundary':'AFTER_REBOOT_CURRENT_HOST_BOOT_OBSERVED'},
 'operation_postcheck':{'scope_variants':[['host_id','plan_digest','step_id','target_registration','host_boot'],['host_id','plan_digest','execution_phase','baseline_digest','host_boot','target_registration']],'owner_assertion':False,'boundary':'AFTER_OPERATION_EPOCH_OBSERVED_FOR_RECONCILIATION'},
 'run_revocation':{'scope_fields':['host_id','original_plan_digest','recovery_request_digest','disposition'],'owner_assertion':True,'boundary':'AFTER_EXACT_RECOVERY_REQUEST_AND_DISPOSITION'},
 'read_absence_observation':{'scope_fields':['host_id','original_plan_digest','read_id','intent_digest','command_digest'],'owner_assertion':False,'boundary':'AFTER_INTERRUPTED_READ_INTENT_EXISTS'},
 'restore_result':{'scope_fields':['host_id','checkpoint_digest','source_target_registration'],'owner_assertion':False,'boundary':'AFTER_DESTINATION_RESTORE_ACTUAL_COMPLETES'},
}
DESTINATION_FIELDS={'host_id','volume_id','canonical_path','purpose','max_bytes','offline_copy_required'}

class V03Error(RuntimeError): pass
def require(cond,reason):
    if not cond: raise V03Error(reason)
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def digest(v): return hashlib.sha256(canonical(v)).hexdigest()
def hash_value(v,reason='HASH'): require(isinstance(v,str) and H64.fullmatch(v) is not None,reason); return v

def load_json(path):
    try:return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception as e: raise V03Error('JSON_UNREADABLE:'+str(path)) from e

def load_catalog(path):
    x=load_json(path); require(type(x) is dict and x.get('schema_version')==1,'CATALOG_SCHEMA')
    rows=x.get('stage_dependencies'); require(type(rows) is list and len(rows)==133,'CATALOG_STAGE_COUNT')
    counts={m:sum(1 for r in rows if r.get('authority_mode')==m) for m in MODES}
    require(counts==EXPECTED_COUNTS and x.get('authority_mode_counts')==EXPECTED_COUNTS,'CATALOG_MODE_COUNTS')
    require(x.get('native_stage_count')==133 and x.get('native_case_count')==85 and x.get('procedure_count')==86,'CATALOG_POPULATION')
    seen=set()
    for r in rows:
        require(type(r) is dict and r.get('authority_mode') in MODES,'CATALOG_ROW')
        key=(r.get('case_id'),r.get('stage_index')); require(key not in seen,'CATALOG_DUPLICATE');seen.add(key)
        hash_value(r.get('procedure_digest'),'CATALOG_PROCEDURE_DIGEST')
        require(type(r.get('route')) is str and type(r.get('producer_dependencies')) is list and type(r.get('late_fields')) is list and type(r.get('derived_object_roles')) is list,'CATALOG_ROW_SCHEMA')
    return x

def rule_map(catalog): return {(r['case_id'],r['stage_index']):deepcopy(r) for r in catalog['stage_dependencies']}

def validate_proof_scope(role,scope,owner_assertion=None):
    require(role in PROOF_SPECS and type(scope) is dict,'LATE_PROOF_ROLE');spec=PROOF_SPECS[role]
    variants=spec.get('scope_variants') or [spec['scope_fields']]
    require(any(set(scope)==set(v) for v in variants) and all(v is not None for v in scope.values()),'LATE_PROOF_SCOPE')
    if owner_assertion is not None: require(owner_assertion is spec['owner_assertion'],'LATE_PROOF_SOURCE_CLASS')
    return deepcopy(spec)

def validate_destination_locator(v):
    require(type(v) is dict and set(v)==DESTINATION_FIELDS,'DESTINATION_LOCATOR_SCHEMA')
    require(isinstance(v['host_id'],str) and v['host_id'] and isinstance(v['volume_id'],str) and v['volume_id'],'DESTINATION_LOCATOR_SCOPE')
    require(isinstance(v['canonical_path'],str) and len(PureWindowsPath(v['canonical_path']).parts)>=2,'DESTINATION_PATH')
    require(v['purpose']=='STAGING_IMPORT' and type(v['offline_copy_required']) is bool,'DESTINATION_LOCATOR_SCOPE')
    require(type(v['max_bytes']) is int and not isinstance(v['max_bytes'],bool) and 0<v['max_bytes']<2**63,'DESTINATION_MAX_BYTES')
    return deepcopy(v)

def validate_destination_allowlist(rows):
    require(type(rows) is list,'DESTINATION_ALLOWLIST_SCHEMA'); checked=[validate_destination_locator(x) for x in rows]
    keys=[(x['host_id'],x['volume_id'],x['canonical_path']) for x in checked]
    require(keys==sorted(keys) and len(keys)==len(set(keys)),'DESTINATION_ALLOWLIST_ORDER');return checked

def object_path(root,ref): hash_value(ref,'OBJECT_REF');return Path(root)/(ref+'.json')
def read_object(root,ref,role=None):
    p=object_path(root,ref); require(p.is_file() and not p.is_symlink(),'OBJECT_MISSING')
    raw=p.read_bytes(); require(hashlib.sha256(raw).hexdigest()==ref,'OBJECT_HASH_MISMATCH')
    try:v=json.loads(raw.decode('utf-8'))
    except Exception as e: raise V03Error('OBJECT_JSON_INVALID') from e
    require(type(v) is dict and (role is None or v.get('role')==role),'OBJECT_ROLE')
    return v
def write_object(root,obj):
    require(type(obj) is dict and isinstance(obj.get('role'),str),'OBJECT_SCHEMA'); raw=canonical(obj);ref=hashlib.sha256(raw).hexdigest();p=Path(root)/(ref+'.json');Path(root).mkdir(parents=True,exist_ok=True)
    if p.exists(): require(p.read_bytes()==raw,'OBJECT_REF_COLLISION')
    else:p.write_bytes(raw)
    return ref

def validate_base_manifest(m,suite_ref=None):
    require(type(m) is dict and set(m)=={'role','schema_version','withdrawn','source_kind','descriptor_ref','entries'} and m['role']=='lab_base_manifest' and m['schema_version']==1 and m['withdrawn'] is False and m['source_kind']=='LAB','BASE_MANIFEST_SCHEMA')
    hash_value(m['descriptor_ref'],'DESCRIPTOR_REF'); rows=m['entries'];require(type(rows) is list and rows,'BASE_MANIFEST_ENTRIES'); pairs=[]
    for row in rows:
        require(type(row) is dict and set(row)=={'role','ref'} and isinstance(row['role'],str) and row['role'],'BASE_MANIFEST_ENTRY');hash_value(row['ref'],'BASE_MANIFEST_ENTRY');pairs.append((row['role'],row['ref']))
    require(pairs==sorted(pairs) and len(pairs)==len(set(pairs)) and ('lab_campaign_descriptor',m['descriptor_ref']) in pairs,'BASE_MANIFEST_ORDER')
    if suite_ref: require(('lab_acceptance_suite',suite_ref) in pairs,'BASE_MANIFEST_SUITE')
    return m

def manifest_contains(m,role,ref): return {'role':role,'ref':ref} in m['entries']

def validate_slot_obj(slot,rule,profile,manifest):
    req={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','build_digest','test_set_digest','contract_digest','execution_id','case_id','procedure_digest','stage_index','route','interface','authority_mode','campaign_descriptor_ref','plan_template_ref','native_binding_template_ref','producer_dependencies','late_fields','derived_object_roles','maximum_approval_seconds','destination_locator_allowlist','reconciliation_plan_refs','semantic_selectors'}
    require(type(slot) is dict and set(slot)==req and slot['role']=='lab_stage_derivation_slot' and slot['schema_version']==1 and slot['withdrawn'] is False and slot['source_kind']=='LAB','DERIVATION_SLOT_SCHEMA')
    for k,pk in [('build_digest','build_digest'),('test_set_digest','test_set_digest'),('contract_digest','contract_digest')]:require(slot[k]==profile[pk],'DERIVATION_SLOT_CANDIDATE')
    require((slot['case_id'],slot['stage_index'],slot['route'],slot['procedure_digest'],slot['authority_mode'])==(rule['case_id'],rule['stage_index'],rule['route'],rule['procedure_digest'],rule['authority_mode']),'DERIVATION_SLOT_SCOPE')
    require(slot['producer_dependencies']==rule['producer_dependencies'] and slot['late_fields']==rule['late_fields'] and slot['derived_object_roles']==rule['derived_object_roles'],'DERIVATION_SLOT_RULE')
    require(type(slot['maximum_approval_seconds']) is int and 0<slot['maximum_approval_seconds']<=86400,'DERIVATION_APPROVAL_WINDOW'); validate_destination_allowlist(slot['destination_locator_allowlist'])
    hash_value(slot['campaign_descriptor_ref']); require(manifest_contains(manifest,'lab_campaign_descriptor',slot['campaign_descriptor_ref']),'DERIVATION_DESCRIPTOR_MANIFEST')
    if rule['authority_mode']=='STAGE_DERIVED':
        hash_value(slot['plan_template_ref']);require(manifest_contains(manifest,'lab_stage_plan_template',slot['plan_template_ref']),'DERIVATION_TEMPLATE_MANIFEST')
        needs_binding='native_binding' in slot['derived_object_roles']
        require((slot['native_binding_template_ref'] is not None)==needs_binding,'DERIVATION_BINDING_TEMPLATE_SCOPE')
        if slot['native_binding_template_ref'] is not None:hash_value(slot['native_binding_template_ref']);require(manifest_contains(manifest,'lab_native_binding_template',slot['native_binding_template_ref']),'DERIVATION_BINDING_TEMPLATE_MANIFEST')
        if 'checkpoint_payload' in slot['derived_object_roles']:require(bool(slot['destination_locator_allowlist']),'DESTINATION_ALLOWLIST_REQUIRED')
        require(slot['reconciliation_plan_refs']==[],'DERIVATION_RECONCILIATION_SCOPE')
    else:
        require(rule['authority_mode']=='FENCE_BOUND_RECONCILIATION' and slot['plan_template_ref'] is None and slot['native_binding_template_ref'] is None and slot['destination_locator_allowlist']==[],'RECONCILIATION_SLOT_SCHEMA')
        require(type(slot['reconciliation_plan_refs']) is list and slot['reconciliation_plan_refs'] and len(slot['reconciliation_plan_refs'])==len(set(slot['reconciliation_plan_refs'])),'RECONCILIATION_PLAN_SET')
        for r in slot['reconciliation_plan_refs']:hash_value(r);require(manifest_contains(manifest,'execution_plan',r),'RECONCILIATION_PLAN_MANIFEST')
    return slot

def request_keys(mode):
    return {'CONCRETE_PRE_V03':{'route','interface','authority_mode','plan_ref'},'STAGE_DERIVED':{'route','interface','authority_mode','derivation_slot_ref'},'ENTRY_PROBE_AUTHORITY':{'route','interface','authority_mode','entry_probe_ref'},'FENCE_BOUND_RECONCILIATION':{'route','interface','authority_mode','reconciliation_slot_ref'}}[mode]

def validate_request_shape(req,rule):
    mode=rule['authority_mode']; require(type(req) is dict and set(req)==request_keys(mode),'SUITE_REQUEST_SCHEMA');require(req['authority_mode']==mode and req['route']==rule['route'] and isinstance(req['interface'],str) and req['interface'],'SUITE_REQUEST_MODE')
    refkey={'CONCRETE_PRE_V03':'plan_ref','STAGE_DERIVED':'derivation_slot_ref','ENTRY_PROBE_AUTHORITY':'entry_probe_ref','FENCE_BOUND_RECONCILIATION':'reconciliation_slot_ref'}[mode];hash_value(req[refkey]);return refkey

def now_utc(): return datetime.now(timezone.utc).isoformat()


def validate_copy_receipt(value,source,locator):
    req={'role','schema_version','withdrawn','source_kind','source_export_ref','source_host_id','source_volume_id',
         'source_canonical_path','source_checkpoint_sha256','source_checkpoint_bytes','destination','destination_sha256',
         'destination_bytes','collector_ref','raw_artifact_ref','timestamp_utc'}
    require(type(value) is dict and set(value)==req and value['role']=='checkpoint_copy_receipt' and
            value['schema_version']==1 and value['withdrawn'] is False and value['source_kind']=='LAB','CHECKPOINT_COPY_SCHEMA')
    for k in ('source_export_ref','source_checkpoint_sha256','collector_ref','raw_artifact_ref'):hash_value(value[k],k.upper())
    require(value['source_export_ref']==source.get('source_export_ref') and
            value['source_host_id']==source.get('source_host_id') and value['source_volume_id']==source.get('source_volume_id') and
            value['source_canonical_path']==source.get('source_canonical_path'),'CHECKPOINT_COPY_SOURCE')
    require(value['source_checkpoint_sha256']==source.get('checkpoint_sha256') and
            value['source_checkpoint_bytes']==source.get('checkpoint_bytes'),'CHECKPOINT_COPY_SOURCE')
    require(value['destination']==locator and value['destination_sha256']==source.get('checkpoint_sha256') and
            value['destination_bytes']==source.get('checkpoint_bytes'),'CHECKPOINT_COPY_INTEGRITY')
    require(value['destination_bytes']<=locator['max_bytes'],'CHECKPOINT_COPY_SIZE')
    return value
