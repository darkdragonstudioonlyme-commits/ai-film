#!/usr/bin/env python3
"""Static verifier for compiled V03 base graphs and runtime producer-bound derivation inputs."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile
from v03_binding_producer_common import (V03Error,EXPECTED_COUNTS,load_catalog,read_object,rule_map,
    validate_base_manifest,validate_copy_receipt,validate_proof_scope,validate_request_shape,validate_slot_obj,hash_value)

class VerifyError(RuntimeError):pass
def require(c,r):
    if not c:raise VerifyError(r)

def verify(binding,binding_sha256,catalog_path,objects_root,receipt_path):
    profile,profile_sha=load_profile(binding,binding_sha256);catalog=load_catalog(catalog_path)
    receipt=json.loads(Path(receipt_path).read_text());require(receipt.get('status')=='PASS','COMPILE_RECEIPT_STATUS')
    require(receipt.get('candidate_profile_sha256')==profile_sha and receipt.get('source_commit')==profile['source_commit'],'COMPILE_RECEIPT_CANDIDATE')
    suite_ref=receipt['suite_ref'];manifest_ref=receipt['base_manifest_ref']
    suite=read_object(objects_root,suite_ref,'lab_acceptance_suite');manifest=read_object(objects_root,manifest_ref,'lab_base_manifest')
    validate_base_manifest(manifest,suite_ref);require({'role':'lab_base_manifest','ref':manifest_ref} not in manifest['entries'],'BASE_MANIFEST_SELF_REFERENCE')
    rules=rule_map(catalog);seen=0
    for row in catalog['stage_dependencies']:
        cid=row['case_id'];idx=row['stage_index'];req=suite['cases'][cid]['requests'][idx];refkey=validate_request_shape(req,rules[(cid,idx)])
        ref=req[refkey]
        if row['authority_mode']=='CONCRETE_PRE_V03': require(any(x=={'role':'execution_plan','ref':ref} for x in manifest['entries']),'CONCRETE_PLAN_MANIFEST')
        elif row['authority_mode']=='ENTRY_PROBE_AUTHORITY': require(any(x=={'role':'entry_probe_set','ref':ref} for x in manifest['entries']),'ENTRY_PROBE_MANIFEST')
        else:
            slot=read_object(objects_root,ref,'lab_stage_derivation_slot');validate_slot_obj(slot,rules[(cid,idx)],profile,manifest)
        seen+=1
    require(seen==133,'STAGE_COUNT')
    return {'schema_version':1,'kind':'V03_BINDING_PRODUCER_VERIFY','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_profile_sha256':profile_sha,'base_manifest_ref':manifest_ref,'suite_ref':suite_ref,
            'native_stage_count':133,'authority_mode_counts':EXPECTED_COUNTS,'signing_performed':False,'native_execution_started':False}

def verify_runtime_bundle(binding,binding_sha256,catalog_path,compile_receipt_path,runtime_path):
    profile,profile_sha=load_profile(binding,binding_sha256);catalog=load_catalog(catalog_path);rules=rule_map(catalog)
    receipt=json.loads(Path(compile_receipt_path).read_text());bundle=json.loads(Path(runtime_path).read_text())
    need={'schema_version','base_manifest_ref','suite_ref','case_id','stage_index','authority_mode','handoffs','proof_scopes','copy_binding'}
    require(type(bundle) is dict and set(bundle)==need and bundle['schema_version']==1,'RUNTIME_BUNDLE_SCHEMA')
    require(bundle['base_manifest_ref']==receipt['base_manifest_ref'] and bundle['suite_ref']==receipt['suite_ref'],'RUNTIME_BASE_SCOPE')
    key=(bundle['case_id'],bundle['stage_index']);require(key in rules,'RUNTIME_STAGE');rule=rules[key]
    require(bundle['authority_mode']==rule['authority_mode'],'RUNTIME_MODE_SUBSTITUTION')
    expected=rule['producer_dependencies'];handoffs=bundle['handoffs'];require(type(handoffs) is list and len(handoffs)==len(expected),'PRODUCER_LINEAGE_COUNT')
    byidx={}
    for h in handoffs:
        hneed={'producer_stage_index','required_route','required_state','suite_ref','case_id','current','lineage_ref','actual'}
        require(type(h) is dict and set(h)==hneed,'PRODUCER_HANDOFF_SCHEMA');idx=h['producer_stage_index'];require(idx not in byidx,'PRODUCER_HANDOFF_DUPLICATE')
        hash_value(h['lineage_ref'],'PRODUCER_LINEAGE_REF');require(h['suite_ref']==receipt['suite_ref'] and h['case_id']==bundle['case_id'],'FOREIGN_PRODUCER_LINEAGE')
        require(h['current'] is True,'STALE_PRODUCER_LINEAGE');require(type(h['actual']) is dict and bool(h['actual']),'PRODUCER_ACTUAL')
        byidx[idx]=h
    for dep in expected:
        h=byidx.get(dep['producer_stage_index']);require(h is not None,'PRODUCER_LINEAGE_MISSING')
        require(h['required_route']==dep['required_route'] and h['required_state']==dep['required_state'],'PRODUCER_LINEAGE_SCOPE')
    scopes=bundle['proof_scopes'];require(type(scopes) is dict,'PROOF_SCOPES_SCHEMA')
    for role,scope in scopes.items():validate_proof_scope(role,scope)
    cb=bundle['copy_binding']
    if cb is not None:
        require(type(cb) is dict and set(cb)=={'source','locator','receipt'},'COPY_BINDING_SCHEMA')
        validate_copy_receipt(cb['receipt'],cb['source'],cb['locator'])
    return {'schema_version':1,'kind':'V03_RUNTIME_BINDING_VERIFY','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_profile_sha256':profile_sha,'case_id':bundle['case_id'],'stage_index':bundle['stage_index'],
            'authority_mode':bundle['authority_mode'],'producer_count':len(handoffs),'proof_scope_count':len(scopes),
            'copy_binding_checked':cb is not None,'signing_performed':False,'native_execution_started':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--catalog',required=True);ap.add_argument('--objects-root');ap.add_argument('--receipt',required=True);ap.add_argument('--runtime-bundle');a=ap.parse_args()
    try:
        if a.runtime_bundle:o=verify_runtime_bundle(a.binding,a.binding_sha256,a.catalog,a.receipt,a.runtime_bundle)
        else:
            require(a.objects_root is not None,'OBJECTS_ROOT_REQUIRED');o=verify(a.binding,a.binding_sha256,a.catalog,a.objects_root,a.receipt)
        rc=0
    except (ProfileError,V03Error,VerifyError,OSError,ValueError,json.JSONDecodeError,KeyError) as e:
        o={'schema_version':1,'kind':'V03_BINDING_PRODUCER_VERIFY','status':'FAIL','reason':str(e),'signing_performed':False,'native_execution_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
