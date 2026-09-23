#!/usr/bin/env python3
"""Verify completed LAB rebuild/reseed evidence against a reviewed plan; performs no LAB/native action."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class ReceiptError(RuntimeError):pass
def req(c,r):
    if not c:raise ReceiptError(r)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def h64(v,r):
    req(isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v),r);return v

def verify(binding,binding_sha256,plan_path,receipt_path,seal_root):
    profile,profile_sha=load_profile(binding,binding_sha256);plan=json.loads(Path(plan_path).read_text());rec=json.loads(Path(receipt_path).read_text())
    req(plan.get('kind')=='P00_LAB_CANDIDATE_REBUILD_PLAN_V2' and plan.get('execution_authorized') is False,'PLAN_SCHEMA')
    t=plan['target'];expected={'candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,'source_commit':profile['source_commit'],
        'implementation_version':profile['implementation_version'],'package_sha256':profile['package_sha256'],'wheel_sha256':profile['wheel_sha256']}
    for k,v in expected.items():req(t.get(k)==v,'PLAN_TARGET:'+k)
    need={'schema_version','kind','status','candidate_id','candidate_binding_sha256','source_commit','implementation_version','package_sha256','wheel_sha256',
          'app_tar_sha256','app_manifest_sha256','runtime_manifest_sha256','inventory_sha256','inventory_case_count','inventory_status','parent_cases_executed',
          'qualification_issued','host_ready','lab_state','pre_rebuild_export_sha256','pristine_raw_sha256','pristine_sealed_sha256',
          'restore_probe','restore_probe_unregistered','restore_probe_receipt_sha256','technical_facts_sha256','artifact_seal_sha256',
          'authority_envelope_created','native_execution_started','v03_started','rollback_source_commit'}
    req(type(rec) is dict and set(rec)==need and rec.get('schema_version')==1 and rec.get('kind')=='P00_LAB_CANDIDATE_REBUILD_DEPLOYMENT_V2' and rec.get('status')=='PASS','RECEIPT_SCHEMA')
    for k,v in expected.items():req(rec.get(k)==v,'RECEIPT_IDENTITY:'+k)
    req(rec.get('app_tar_sha256')==t['app_tar_sha256'] and rec.get('app_manifest_sha256')==t['app_manifest_sha256'],'PAYLOAD_IDENTITY')
    req(rec.get('inventory_case_count')==86 and rec.get('inventory_status')=='NOT_RUN' and rec.get('parent_cases_executed')==0,'INVENTORY_STATE')
    req(rec.get('qualification_issued') is False and rec.get('host_ready') is False and rec.get('lab_state')=='STOPPED','LAB_FINAL_STATE')
    req(rec.get('restore_probe')=='PASS' and rec.get('restore_probe_unregistered') is True,'RESTORE_PROBE')
    req(rec.get('authority_envelope_created') is False and rec.get('native_execution_started') is False and rec.get('v03_started') is False,'NATIVE_BOUNDARY')
    req(rec.get('rollback_source_commit')==plan['rollback']['source_commit'],'ROLLBACK_IDENTITY')
    for k in ('runtime_manifest_sha256','inventory_sha256','pre_rebuild_export_sha256','pristine_raw_sha256','pristine_sealed_sha256',
              'restore_probe_receipt_sha256','technical_facts_sha256','artifact_seal_sha256'):h64(rec.get(k),k.upper())
    seal_path=Path(seal_root)/'LAB_ARTIFACT_SEAL_V1.json';req(seal_path.is_file() and not seal_path.is_symlink(),'SEAL_MISSING')
    req(sha(seal_path)==rec['artifact_seal_sha256'],'SEAL_HASH')
    seal=json.loads(seal_path.read_text());req(seal.get('candidate_id')==profile['candidate_id'] and seal.get('candidate_binding_sha256')==profile_sha and seal.get('source_commit')==profile['source_commit'],'SEAL_CANDIDATE')
    req(seal.get('pristine_restore_probe')=='PASS','SEAL_RESTORE_PROBE')
    return {'kind':'P00_LAB_CANDIDATE_REBUILD_RECEIPT_VERIFY_V2','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_binding_sha256':profile_sha,'inventory_case_count':86,'inventory_status':'NOT_RUN','lab_state':'STOPPED',
            'restore_probe':'PASS','native_execution_started':False,'signing_performed':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--plan',required=True);ap.add_argument('--receipt',required=True);ap.add_argument('--seal-root',required=True);a=ap.parse_args()
    try:o=verify(a.binding,a.binding_sha256,a.plan,a.receipt,a.seal_root);rc=0
    except (ProfileError,ReceiptError,OSError,ValueError,json.JSONDecodeError,KeyError) as e:o={'kind':'P00_LAB_CANDIDATE_REBUILD_RECEIPT_VERIFY_V2','status':'FAIL','reason':str(e),'native_execution_started':False,'signing_performed':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
