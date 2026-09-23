#!/usr/bin/env python3
"""Create a candidate-bound LAB rebuild/reseed plan only. This tool performs no WSL operation."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class PlanError(RuntimeError):pass
def req(c,r):
    if not c:raise PlanError(r)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def hash64(v,name):
    req(isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v),name);return v

def plan(binding,binding_sha256,payload_manifest,previous_receipt,lab_state,out):
    profile,profile_sha=load_profile(binding,binding_sha256)
    payload=json.loads(Path(payload_manifest).read_text());prev=json.loads(Path(previous_receipt).read_text());obs=json.loads(Path(lab_state).read_text())
    req(payload.get('kind')=='P00_LAB_CANDIDATE_APP_PAYLOAD','PAYLOAD_KIND')
    expected={'candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,'source_commit':profile['source_commit'],
              'implementation_version':profile['implementation_version'],'contract_digest':profile['contract_digest'],
              'package_sha256':profile['package_sha256'],'wheel_sha256':profile['wheel_sha256']}
    for k,v in expected.items():req(payload.get(k)==v,'PAYLOAD_IDENTITY:'+k)
    req(payload.get('native_execution_started') is False,'PAYLOAD_NATIVE_BOUNDARY')
    req(prev.get('status')=='PASS' and prev.get('lab_state')=='STOPPED' and prev.get('restore_probe')=='PASS','ROLLBACK_BASELINE')
    req(prev.get('candidate_id')!=profile['candidate_id'] and prev.get('source_commit')!=profile['source_commit'],'ROLLBACK_NOT_DISTINCT')
    for k in ('pre_migration_export_sha256','pristine_raw_sha256','pristine_sealed_sha256','artifact_seal_sha256'):hash64(prev.get(k),k)
    req(type(obs) is dict and obs.get('schema_version')==1 and obs.get('distro')=='AI-FILM-P00-LAB'
        and obs.get('observed_state')=='STOPPED' and obs.get('observation_source')=='HOST_WSL_LIST'
        and isinstance(obs.get('observed_at'),str) and obs['observed_at'],'LAB_STOP_OBSERVATION')
    target={'candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,'source_commit':profile['source_commit'],
            'implementation_version':profile['implementation_version'],'package_sha256':profile['package_sha256'],
            'wheel_sha256':profile['wheel_sha256'],'app_tar_sha256':hash64(payload.get('app_tar_sha256'),'PAYLOAD_TAR'),
            'app_manifest_sha256':hash64(payload.get('app_manifest_sha256'),'PAYLOAD_APP_MANIFEST')}
    rollback={'candidate_id':prev['candidate_id'],'candidate_binding_sha256':prev['candidate_binding_sha256'],'source_commit':prev['source_commit'],
              'pre_migration_export_sha256':prev['pre_migration_export_sha256'],'pristine_raw_sha256':prev['pristine_raw_sha256'],
              'pristine_sealed_sha256':prev['pristine_sealed_sha256'],'artifact_seal_sha256':prev['artifact_seal_sha256']}
    operations=['CAPTURE_PRE_REBUILD_EXPORT','STAGE_REVIEWED_PAYLOAD','REBUILD_TARGET_RUNTIME','VERIFY_METADATA_ONLY',
                'TERMINATE_LAB','EXPORT_PRISTINE_RAW','SEAL_PRISTINE_EXPORT','RUN_ISOLATED_RESTORE_PROBE','WRITE_TARGET_FACTS_AND_SEAL']
    evidence=['pre_rebuild_export_sha256','runtime_manifest_sha256','inventory_sha256','pristine_raw_sha256','pristine_sealed_sha256',
              'restore_probe_receipt_sha256','technical_facts_sha256','artifact_seal_sha256']
    result={'schema_version':1,'kind':'P00_LAB_CANDIDATE_REBUILD_PLAN_V2','status':'READY_FOR_SEPARATE_DEPLOYMENT_REVIEW',
            'target':target,'rollback':rollback,'lab_stop_observation':obs,'payload_manifest_sha256':sha(payload_manifest),
            'previous_receipt_sha256':sha(previous_receipt),'operations':operations,'required_evidence':evidence,
            'execution_authorized':False,'lab_mutation_started':False,'native_execution_started':False,'signing_performed':False}
    Path(out).parent.mkdir(parents=True,exist_ok=True);Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--payload-manifest',required=True);ap.add_argument('--previous-receipt',required=True);ap.add_argument('--lab-state',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    try:o=plan(a.binding,a.binding_sha256,a.payload_manifest,a.previous_receipt,a.lab_state,a.out);rc=0
    except (ProfileError,PlanError,OSError,ValueError,json.JSONDecodeError,KeyError) as e:o={'schema_version':1,'kind':'P00_LAB_CANDIDATE_REBUILD_PLAN_V2','status':'FAIL','reason':str(e),'execution_authorized':False,'lab_mutation_started':False,'native_execution_started':False,'signing_performed':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
