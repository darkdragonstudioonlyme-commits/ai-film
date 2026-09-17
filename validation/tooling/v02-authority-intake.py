#!/usr/bin/env python3
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

APP=Path('/home/dragon/ai-film-dev/validation')
sys.path.insert(0,str(APP/'src'))
from aifilm_p00 import CONTRACT_DIGEST
from aifilm_p00.authority import PinnedStore, Context, authorize
from aifilm_p00.codec import sha256
from aifilm_p00.native.harness_cases import PROCEDURES
from aifilm_p00.plans import interface_check
from v02_external_authenticity import verify_external_authenticity
from v02_local_identity import load_local_identity

CANDIDATE_ID='336b12af-cada-4968-8083-8a5b41e479a2'
PENDING_BUNDLE='fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615'
SOURCE_COMMIT='934659f535d81d9a4a07389531acc2b9c304fa6d'
BUILD='a284645e9eb60661f27eba1ea436d7ff7bbe60d6cd3e312850f1b108d32b1c62'
TEST='c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383'
HOST_ID=None
OPERATOR_DIGEST=None
BASELINE='0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd'
PRISTINE='552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d'
H64=re.compile(r'^[0-9a-f]{64}$')

def fail(reason, **extra):
    out={'kind':'V02_AUTHORITY_INTAKE','status':'BLOCKED','reason':reason,
         'candidate_id':CANDIDATE_ID,'pending_bundle_index_sha256':PENDING_BUNDLE,
         'native_execution_started':False,'ready_to_advance':False,**extra}
    print(json.dumps(out,sort_keys=True,separators=(',',':')))
    raise SystemExit(12)

def parse_time(value):
    if not isinstance(value,str): fail('TIME_SCHEMA')
    try:
        return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc)
    except ValueError: fail('TIME_SCHEMA')

def read_json(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,UnicodeError,json.JSONDecodeError): fail('JSON_UNREADABLE',path=path.name)

def hash_bytes(raw): return hashlib.sha256(raw).hexdigest()

def identity_digest(sid):
    return hashlib.sha256(('AI-FILM-P00|operator|'+sid).encode()).hexdigest()

def load_object(objects,ref,expected_role=None):
    if not isinstance(ref,str) or not H64.fullmatch(ref): fail('REF_SCHEMA',ref_name=str(ref)[:16])
    path=objects/(ref+'.json')
    try: raw=path.read_bytes()
    except OSError: fail('OBJECT_MISSING',ref=ref)
    if hash_bytes(raw)!=ref: fail('OBJECT_HASH_MISMATCH',ref=ref)
    try: obj=json.loads(raw)
    except (UnicodeDecodeError,json.JSONDecodeError): fail('OBJECT_JSON_INVALID',ref=ref)
    if not isinstance(obj,dict): fail('OBJECT_SCHEMA',ref=ref)
    if expected_role is not None and obj.get('role')!=expected_role:
        fail('OBJECT_ROLE_MISMATCH',ref=ref,expected_role=expected_role)
    return obj,raw

def require(cond,reason,**extra):
    if not cond: fail(reason,**extra)

def ref_field(env,name):
    ref=env.get(name)
    require(isinstance(ref,str) and H64.fullmatch(ref), 'ENVELOPE_REF_MISSING',field=name)
    return ref

def verify_attestation(obj,role):
    require(obj.get('role')==role,'ATTESTATION_ROLE',role=role)
    require(obj.get('candidate_id')==CANDIDATE_ID,'ATTESTATION_CANDIDATE',role=role)
    require(obj.get('pending_bundle_index_sha256')==PENDING_BUNDLE,'ATTESTATION_BUNDLE',role=role)
    require(obj.get('approved') is True and obj.get('withdrawn') is False,'ATTESTATION_STATUS',role=role)

def verify_registration(reg):
    require(reg.get('role')=='registration','REGISTRATION_ROLE')
    require(reg.get('host_id')==HOST_ID,'REGISTRATION_HOST')
    require(reg.get('execution_class')=='LAB','REGISTRATION_CLASS')
    require(reg.get('withdrawn') is False,'REGISTRATION_WITHDRAWN')
    for k in ('controller_external','disposable','no_real_credentials','no_production_mappings'):
        require(reg.get(k) is True,'REGISTRATION_CONTAINMENT',field=k)
    sids=reg.get('operator_sids')
    require(isinstance(sids,list) and sids,'REGISTRATION_OPERATORS')
    require(any(identity_digest(x)==OPERATOR_DIGEST for x in sids if isinstance(x,str)),
            'REGISTRATION_OPERATOR_SCOPE')
    return sids

def verify_recovery(obj):
    require(obj.get('role')=='management_isolation_recovery','RECOVERY_ROLE')
    require(obj.get('candidate_id')==CANDIDATE_ID,'RECOVERY_CANDIDATE')
    require(obj.get('baseline_snapshot_sha256')==BASELINE,'RECOVERY_BASELINE')
    require(obj.get('pristine_snapshot_sha256')==PRISTINE,'RECOVERY_PRISTINE')
    require(obj.get('restore_probe')=='PASS','RECOVERY_PROBE')
    require(obj.get('approved') is True and obj.get('withdrawn') is False,'RECOVERY_STATUS')

def verify_fixture_set(obj,suite,objects):
    require(obj.get('role')=='lab_fixture_set','FIXTURE_SET_ROLE')
    require(obj.get('candidate_id')==CANDIDATE_ID,'FIXTURE_SET_CANDIDATE')
    require(obj.get('approved') is True and obj.get('withdrawn') is False,'FIXTURE_SET_STATUS')
    refs=obj.get('case_fixture_spec_refs')
    require(isinstance(refs,dict),'FIXTURE_SET_SCHEMA')
    native_ids={k for k,p in PROCEDURES.items() if p.actual_native_required}
    require(set(refs)==native_ids,'FIXTURE_SET_COVERAGE')
    for cid,ref in refs.items():
        require(suite['cases'][cid]['fixture_spec_ref']==ref,'FIXTURE_SUITE_BINDING',case_id=cid)
        spec,_=load_object(objects,ref,'lab_case_fixture_spec')
        proc=PROCEDURES[cid]
        required={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id',
                  'procedure_digest','preparations','controller_external','disposable',
                  'no_real_credentials','no_production_mappings'}
        require(set(spec)==required and spec['schema_version']==1 and spec['withdrawn'] is False,
                'FIXTURE_SPEC_SCHEMA',case_id=cid)
        require(spec['source_kind']=='LAB' and spec['host_id']==HOST_ID and spec['owner_sid']==suite['owner_sid'],
                'FIXTURE_SPEC_SCOPE',case_id=cid)
        require(spec['case_id']==cid and spec['procedure_digest']==proc.procedure_digest,
                'FIXTURE_SPEC_PROCEDURE',case_id=cid)
        require(tuple(spec['preparations'])==proc.preparations,'FIXTURE_SPEC_PREPARATIONS',case_id=cid)
        for k in ('controller_external','disposable','no_real_credentials','no_production_mappings'):
            require(spec[k] is True,'FIXTURE_SPEC_CONTAINMENT',case_id=cid,field=k)

def verify_suite(suite,objects,now):
    required={'role','schema_version','withdrawn','approved','source_kind','host_id','owner_sid',
              'build_digest','test_set_digest','contract_digest','execution_id','issued_at','expires_at','cases'}
    require(set(suite)==required and suite['schema_version']==1,'SUITE_SCHEMA')
    require(suite['withdrawn'] is False and suite['approved'] is True and suite['source_kind']=='LAB','SUITE_STATUS')
    require(suite['host_id']==HOST_ID and suite['build_digest']==BUILD and suite['test_set_digest']==TEST,
            'SUITE_SCOPE')
    require(suite['contract_digest']==CONTRACT_DIGEST,'SUITE_CONTRACT')
    issued=parse_time(suite['issued_at']); expires=parse_time(suite['expires_at'])
    require(issued<=now<=expires and expires-issued<=timedelta(hours=24),'SUITE_TIME')
    require(isinstance(suite['execution_id'],str) and suite['execution_id'],'SUITE_EXECUTION_ID')
    require(isinstance(suite['cases'],dict) and set(suite['cases'])==set(PROCEDURES),'SUITE_CASE_COVERAGE')
    for cid,proc in PROCEDURES.items():
        row=suite['cases'][cid]
        require(isinstance(row,dict) and set(row)=={'procedure_digest','fixture_spec_ref','requests'},
                'SUITE_CASE_SCHEMA',case_id=cid)
        require(row['procedure_digest']==proc.procedure_digest,'SUITE_PROCEDURE_DRIFT',case_id=cid)
        require(isinstance(row['requests'],list),'SUITE_REQUESTS_SCHEMA',case_id=cid)
        if proc.actual_native_required:
            require(isinstance(row['fixture_spec_ref'],str) and H64.fullmatch(row['fixture_spec_ref']),
                    'SUITE_FIXTURE_REF',case_id=cid)
            require(len(row['requests'])==len(proc.routes),'SUITE_REQUEST_COUNT',case_id=cid)
        else:
            require(row['fixture_spec_ref'] is None and row['requests']==[],
                    'SUITE_DOCUMENT_CASE',case_id=cid)
        for i,req in enumerate(row['requests']):
            require(isinstance(req,dict) and set(req)=={'route','interface','plan_ref'},
                    'SUITE_REQUEST_SCHEMA',case_id=cid,stage=i)
            require(req['route']==proc.routes[i],'SUITE_ROUTE_DRIFT',case_id=cid,stage=i)
            require(isinstance(req['plan_ref'],str) and H64.fullmatch(req['plan_ref']),
                    'SUITE_PLAN_REF',case_id=cid,stage=i)
            load_object(objects,req['plan_ref'],'execution_plan')

def build_store(env,objects):
    pins=env.get('role_pins')
    require(isinstance(pins,dict),'ROLE_PINS_SCHEMA')
    outpins={}; blobs={}
    for role,refs in pins.items():
        require(isinstance(role,str) and isinstance(refs,list) and refs,'ROLE_PINS_SCHEMA',role=str(role))
        seen=[]
        for ref in refs:
            obj,raw=load_object(objects,ref,role)
            blobs[ref]=raw; seen.append(ref)
        require(len(seen)==len(set(seen)),'ROLE_PIN_DUPLICATE',role=role)
        outpins[role]=frozenset(seen)
    return PinnedStore(outpins,blobs,'EXTERNAL_AUTHORITY_INTAKE')

def verify_plan_authorities(suite,store,objects,now):
    count=0
    for cid,proc in PROCEDURES.items():
        for i,req in enumerate(suite['cases'][cid]['requests']):
            require(req['plan_ref'] in store.pins.get('execution_plan',frozenset()),
                    'EXECUTION_PLAN_NOT_PINNED',case_id=cid,stage=i)
            doc,_=load_object(objects,req['plan_ref'],'execution_plan')
            require(doc.get('schema_version')==1 and doc.get('withdrawn') is False and doc.get('fixture_only') is not True,
                    'EXECUTION_PLAN_DOCUMENT',case_id=cid,stage=i)
            plan=doc.get('plan'); semantic=interface_check(req['interface'],plan)
            if req['route']!='ENTRY_ONLY':
                require(semantic['purpose']==req['route'],'PLAN_ROUTE_PURPOSE',case_id=cid,stage=i)
            ctx=Context(HOST_ID,suite['owner_sid'],'LAB',BUILD,TEST,semantic['profile'],True,now)
            authorize(req['interface'],plan,ctx,store)
            count+=1
    return count

def main():
    global HOST_ID,OPERATOR_DIGEST
    ap=argparse.ArgumentParser()
    ap.add_argument('--inbox',default='/mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev21')
    args=ap.parse_args(); root=Path(args.inbox); env_path=root/'approval-envelope.json'
    if not env_path.is_file(): fail('APPROVAL_ENVELOPE_MISSING',inbox=str(root))
    identity=load_local_identity(fail); HOST_ID=identity['host_id']; OPERATOR_DIGEST=identity['operator_digest']
    try:
        env_raw=env_path.read_bytes(); env=json.loads(env_raw.decode('utf-8'))
    except (OSError,UnicodeError,json.JSONDecodeError):
        fail('JSON_UNREADABLE',path=env_path.name)
    require(isinstance(env,dict),'ENVELOPE_SCHEMA')
    objects=root/'objects'
    require(env.get('schema_version')==1 and env.get('kind')=='P00_LAB_EXTERNAL_AUTHORITY_INTAKE',
            'ENVELOPE_SCHEMA')
    require(env.get('decision')=='APPROVE' and env.get('approved_by_external_authority') is True,
            'EXTERNAL_DECISION_NOT_APPROVE')
    require(env.get('candidate_id')==CANDIDATE_ID and env.get('pending_bundle_index_sha256')==PENDING_BUNDLE,
            'ENVELOPE_CANDIDATE_BINDING')
    require(env.get('source_commit')==SOURCE_COMMIT and env.get('build_digest')==BUILD,
            'ENVELOPE_BUILD_BINDING')
    require(env.get('test_set_digest')==TEST and env.get('contract_digest')==CONTRACT_DIGEST,
            'ENVELOPE_CONTENT_BINDING')
    external_auth=verify_external_authenticity(root,env_raw,fail)
    now=datetime.now(timezone.utc)
    reg_ref=ref_field(env,'lab_registration_ref'); suite_ref=ref_field(env,'lab_acceptance_suite_ref')
    owner_ref=ref_field(env,'owner_attestation_ref'); ctrl_ref=ref_field(env,'controller_attestation_ref')
    fixture_ref=ref_field(env,'fixture_set_ref'); recovery_ref=ref_field(env,'management_isolation_recovery_ref')
    labplan_ref=ref_field(env,'lab_test_plan_approval_ref')
    reg,_=load_object(objects,reg_ref,'registration'); sids=verify_registration(reg)
    owner,_=load_object(objects,owner_ref,'owner_attestation'); verify_attestation(owner,'owner_attestation')
    ctrl,_=load_object(objects,ctrl_ref,'controller_attestation'); verify_attestation(ctrl,'controller_attestation')
    recovery,_=load_object(objects,recovery_ref,'management_isolation_recovery'); verify_recovery(recovery)
    labplan,_=load_object(objects,labplan_ref,'lab_plan')
    require(labplan.get('host_id')==HOST_ID and labplan.get('build_digest')==BUILD,'LAB_PLAN_SCOPE')
    require(labplan.get('approved') is True and labplan.get('withdrawn') is False,'LAB_PLAN_STATUS')
    suite,_=load_object(objects,suite_ref,'lab_acceptance_suite'); verify_suite(suite,objects,now)
    require(suite['owner_sid'] in sids,'SUITE_OWNER_NOT_REGISTERED')
    store=build_store(env,objects)
    for role in ('registration','design','code'):
        require(len(store.pins.get(role,frozenset()))==1,'SINGLE_PIN_REQUIRED',role=role)
    require(store.pins['registration']==frozenset({reg_ref}),'REGISTRATION_PIN_MISMATCH')
    for role,ref in [('lab_plan',labplan_ref),('lab_acceptance_suite',suite_ref)]:
        require(ref in store.pins.get(role,frozenset()),'REQUIRED_PIN_MISSING',role=role)
    for cid,proc in PROCEDURES.items():
        if proc.actual_native_required:
            ref=suite['cases'][cid]['fixture_spec_ref']
            require(ref in store.pins.get('lab_case_fixture_spec',frozenset()),
                    'FIXTURE_SPEC_NOT_PINNED',case_id=cid)
    fixtures,_=load_object(objects,fixture_ref,'lab_fixture_set'); verify_fixture_set(fixtures,suite,objects)
    plan_count=verify_plan_authorities(suite,store,objects,now)
    out={'kind':'V02_AUTHORITY_INTAKE','status':'READY_TO_ADVANCE','ready_to_advance':True,
         'candidate_id':CANDIDATE_ID,'pending_bundle_index_sha256':PENDING_BUNDLE,
         'registration_ref':reg_ref,'lab_plan_ref':labplan_ref,'lab_acceptance_suite_ref':suite_ref,
         'suite_execution_id':suite['execution_id'],'suite_expires_at':suite['expires_at'],
         'case_count':len(suite['cases']),'authorized_plan_count':plan_count,
         'external_authority_key_id':external_auth['key_id'],
         'external_authority_payload_sha256':external_auth['payload_sha256'],
         'external_authority_provenance_ref':external_auth['provenance_ref'],
         'native_execution_started':False}
    print(json.dumps(out,sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    main()
