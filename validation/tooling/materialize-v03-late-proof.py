#!/usr/bin/env python3
"""Materialize reviewed late-proof receipts from already-pinned evidence; no observation is manufactured."""
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile
from v03_binding_producer_common import V03Error,digest,read_object,validate_proof_scope,write_object

class ProofError(RuntimeError): pass
def req(c,r):
    if not c: raise ProofError(r)
def instant(s):
    try:
        x=str(s); dt=datetime.fromisoformat(x[:-1]+'+00:00' if x.endswith('Z') else x)
        req(dt.tzinfo is not None,'TIMEZONE_REQUIRED'); return dt.astimezone(timezone.utc)
    except (ValueError,TypeError) as e: raise ProofError('TIME_INVALID') from e

def materialize(binding,binding_sha256,objects_root,request_path,out_root):
    profile,profile_sha=load_profile(binding,binding_sha256)
    q=json.loads(Path(request_path).read_text())
    need={'schema_version','role','scope','owner_sid','authorizer_ref','measurement_refs','claim','claim_map',
          'issued_at','expires_at','owner_assertion','not_before'}
    req(type(q) is dict and set(q)==need and q['schema_version']==1,'REQUEST_SCHEMA')
    role=q['role']; spec=validate_proof_scope(role,q['scope'],owner_assertion=q['owner_assertion'])
    issued=instant(q['issued_at']); expires=instant(q['expires_at']); req(issued<=expires,'PROOF_TIME')
    if q['not_before'] is not None: req(issued>=instant(q['not_before']),'PROOF_PRECEDES_OPERATION')
    if role=='c3_postchecks': req(issued>=instant(q['scope']['host_boot']),'PROOF_PRECEDES_HOST_BOOT')
    refs=q['measurement_refs']; req(type(refs) is list and 0<len(refs)<=128 and len(refs)==len(set(refs)),'PROOF_MEASUREMENTS_REQUIRED')
    authorizer=read_object(objects_root,q['authorizer_ref'],'resource_owner')
    req(authorizer.get('withdrawn') is False and authorizer.get('owner_sid')==q['owner_sid']
        and role in authorizer.get('receipt_roles',[]),'PROOF_OWNER_AUTHORITY')
    host=q['scope'].get('host_id'); req(host in authorizer.get('host_ids',[]),'PROOF_OWNER_HOST_SCOPE')
    checked={}
    for ref in refs:
        m=read_object(objects_root,ref,'measurement'); kind=m.get('source_kind')
        req(kind in ('SITE','LAB','OWNER_ASSERTION'),'WORKSPACE_PROOF_FORBIDDEN')
        req(kind!='OWNER_ASSERTION' or spec['owner_assertion'],'NATIVE_PROOF_REQUIRED')
        req(m.get('status')=='OBSERVED' and m.get('contract_digest')==profile['contract_digest']
            and type(m.get('actual')) is dict and bool(m['actual']),'PROOF_MEASUREMENT_SCHEMA')
        req(m.get('host_id')==host and m.get('subject_digest')==digest(q['scope']),'PROOF_MEASUREMENT_SUBJECT')
        mt=instant(m['timestamp_utc']); req(mt<=issued,'PROOF_MEASUREMENT_TIME')
        if role=='read_absence_observation' and q['not_before'] is not None:
            req(mt>=instant(q['not_before']),'READ_ABSENCE_PRECEDES_INTENT')
        collector=read_object(objects_root,m['collector_ref'],'collector_release')
        req(collector.get('withdrawn') is False and collector.get('review_verdict')=='PASS'
            and collector.get('build_digest')==m.get('collector_digest'),'PROOF_COLLECTOR_UNREVIEWED')
        raw=read_object(objects_root,m['raw_artifact_ref'],'measurement_artifact')
        req(raw.get('measurement_actual_digest')==digest(m['actual'])
            and raw.get('subject_digest')==m['subject_digest'] and raw.get('withdrawn') is False,'PROOF_RAW_BINDING')
        checked[ref]=m
    claim=q['claim']; mapping=q['claim_map']
    req(type(claim) is dict and claim and type(mapping) is dict and set(mapping)==set(claim),'PROOF_CLAIM_COVERAGE')
    for key,bound in mapping.items():
        req(type(bound) is dict and set(bound)=={'measurement_ref','actual_key'} and bound['measurement_ref'] in checked,'PROOF_CLAIM_MAP')
        actual=checked[bound['measurement_ref']]['actual']
        req(bound['actual_key'] in actual and actual[bound['actual_key']]==claim[key],'PROOF_CLAIM_NOT_MEASURED')
    receipt={'role':role,'schema_version':1,'withdrawn':False,'fixture_only':False,'source_kind':'LAB',
             'contract_digest':profile['contract_digest'],'scope':q['scope'],'issued_at':q['issued_at'],'expires_at':q['expires_at'],
             'authorizer_ref':q['authorizer_ref'],'owner_sid':q['owner_sid'],'measurements':refs,'claim':claim,'claim_map':mapping}
    ref=write_object(out_root,receipt)
    return {'schema_version':1,'kind':'V03_LATE_PROOF_MATERIALIZATION','status':'PASS','role':role,'proof_ref':ref,
            'candidate_id':profile['candidate_id'],'candidate_profile_sha256':profile_sha,'boundary':spec['boundary'],
            'not_before_checked':q['not_before'] is not None,'signing_performed':False,'native_execution_started':False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--binding',required=True); ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--objects-root',required=True); ap.add_argument('--request',required=True); ap.add_argument('--out-root',required=True)
    a=ap.parse_args()
    try: o=materialize(a.binding,a.binding_sha256,a.objects_root,a.request,a.out_root); rc=0
    except (ProfileError,V03Error,ProofError,OSError,ValueError,json.JSONDecodeError,KeyError) as e:
        o={'schema_version':1,'kind':'V03_LATE_PROOF_MATERIALIZATION','status':'FAIL','reason':str(e),
           'signing_performed':False,'native_execution_started':False}; rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':'))); return rc
if __name__=='__main__': raise SystemExit(main())
