#!/usr/bin/env python3
"""Pure V03 base-authority graph compiler. It signs nothing and performs no native action."""
from __future__ import annotations
import argparse,json
from copy import deepcopy
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile
from v03_binding_producer_common import (V03Error,EXPECTED_COUNTS,canonical,load_catalog,manifest_contains,
    rule_map,validate_base_manifest,validate_request_shape,validate_slot_obj,write_object)

class CompileError(RuntimeError):pass
def require(c,r):
    if not c:raise CompileError(r)

DYNAMIC_ROLES=frozenset({'lab_authority_generation','lab_authority_lineage','checkpoint_copy_receipt',
    'source_manifest','protection','restore_envelope','user_init_receipt','c3_postchecks',
    'operation_postcheck','run_revocation','read_absence_observation','restore_result'})

def resolve(value,refs):
    if type(value) is dict:
        if set(value)=={'$ref'}:
            name=value['$ref'];require(isinstance(name,str) and name in refs,'FORWARD_OR_UNKNOWN_REF:'+str(name))
            return refs[name]
        return {k:resolve(v,refs) for k,v in value.items()}
    if type(value) is list:return [resolve(v,refs) for v in value]
    return value

def validate_suite(suite,profile,catalog):
    require(type(suite) is dict and suite.get('role')=='lab_acceptance_suite','SUITE_ROLE')
    for sk,pk in (('build_digest','build_digest'),('test_set_digest','test_set_digest'),('contract_digest','contract_digest')):
        require(suite.get(sk)==profile[pk],'SUITE_CANDIDATE:'+sk)
    cases=suite.get('cases');require(type(cases) is dict,'SUITE_CASES')
    rules=rule_map(catalog);seen=0
    for row in catalog['stage_dependencies']:
        cid=row['case_id'];idx=row['stage_index'];require(cid in cases,'SUITE_CASE_MISSING:'+cid)
        reqs=cases[cid].get('requests');require(type(reqs) is list and idx<len(reqs),'SUITE_STAGE_MISSING')
        validate_request_shape(reqs[idx],rules[(cid,idx)]);seen+=1
    require(seen==133,'SUITE_STAGE_COUNT')
    return True

def compile_graph(binding,binding_sha256,catalog_path,spec_path,objects_root,receipt_path):
    profile,profile_sha=load_profile(binding,binding_sha256);catalog=load_catalog(catalog_path)
    spec=json.loads(Path(spec_path).read_text());require(type(spec) is dict and set(spec)=={'schema_version','objects','suite_id','descriptor_id'},'SPEC_SCHEMA')
    require(spec['schema_version']==1 and type(spec['objects']) is list and spec['objects'],'SPEC_SCHEMA')
    refs={};roles={};values={}
    for item in spec['objects']:
        require(type(item) is dict and set(item)=={'id','value'},'SPEC_OBJECT')
        name=item['id'];require(isinstance(name,str) and name and name not in refs,'SPEC_ID')
        value=resolve(deepcopy(item['value']),refs);role=value.get('role') if type(value) is dict else None
        require(isinstance(role,str) and role not in DYNAMIC_ROLES,'BASE_ROLE_FORBIDDEN')
        ref=write_object(objects_root,value);refs[name]=ref;roles[name]=role;values[name]=value
    require(spec['suite_id'] in refs and roles[spec['suite_id']]=='lab_acceptance_suite','SUITE_ID')
    require(spec['descriptor_id'] in refs and roles[spec['descriptor_id']]=='lab_campaign_descriptor','DESCRIPTOR_ID')
    suite_ref=refs[spec['suite_id']];descriptor_ref=refs[spec['descriptor_id']]
    suite=values[spec['suite_id']];desc=values[spec['descriptor_id']]
    validate_suite(suite,profile,catalog)
    require(desc.get('build_digest')==profile['build_digest'] and desc.get('test_set_digest')==profile['test_set_digest'] and
            desc.get('contract_digest')==profile['contract_digest'],'DESCRIPTOR_CANDIDATE')
    entries=sorted([{'role':roles[name],'ref':refs[name]} for name in refs],key=lambda x:(x['role'],x['ref']))
    manifest={'role':'lab_base_manifest','schema_version':1,'withdrawn':False,'source_kind':'LAB',
              'descriptor_ref':descriptor_ref,'entries':entries}
    manifest_ref=write_object(objects_root,manifest);validate_base_manifest(manifest,suite_ref)
    require(not manifest_contains(manifest,'lab_base_manifest',manifest_ref),'BASE_MANIFEST_SELF_REFERENCE')
    # Validate every non-concrete slot against reviewed row after manifest exists.
    rules=rule_map(catalog)
    for row in catalog['stage_dependencies']:
        req=suite['cases'][row['case_id']]['requests'][row['stage_index']]
        if row['authority_mode'] in ('STAGE_DERIVED','FENCE_BOUND_RECONCILIATION'):
            key='derivation_slot_ref' if row['authority_mode']=='STAGE_DERIVED' else 'reconciliation_slot_ref'
            slot=next((v for n,v in values.items() if refs[n]==req[key]),None);require(slot is not None,'SLOT_OBJECT_MISSING')
            validate_slot_obj(slot,rules[(row['case_id'],row['stage_index'])],profile,manifest)
    receipt={'schema_version':1,'kind':'V03_BASE_GRAPH_COMPILE','status':'PASS','candidate_id':profile['candidate_id'],
             'candidate_profile_sha256':profile_sha,'source_commit':profile['source_commit'],
             'suite_ref':suite_ref,'descriptor_ref':descriptor_ref,'base_manifest_ref':manifest_ref,
             'immutable_partition_digest':manifest_ref,'object_count':len(refs)+1,
             'native_stage_count':133,'authority_mode_counts':EXPECTED_COUNTS,
             'signing_performed':False,'native_execution_started':False}
    Path(receipt_path).parent.mkdir(parents=True,exist_ok=True);Path(receipt_path).write_bytes(canonical(receipt)+b'\n')
    return receipt

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--catalog',required=True);ap.add_argument('--spec',required=True);ap.add_argument('--objects-root',required=True);ap.add_argument('--receipt',required=True);a=ap.parse_args()
    try:o=compile_graph(a.binding,a.binding_sha256,a.catalog,a.spec,a.objects_root,a.receipt);rc=0
    except (ProfileError,V03Error,CompileError,OSError,ValueError,json.JSONDecodeError) as e:
        o={'schema_version':1,'kind':'V03_BASE_GRAPH_COMPILE','status':'FAIL','reason':str(e),'signing_performed':False,'native_execution_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
