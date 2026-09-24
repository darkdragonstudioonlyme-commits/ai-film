#!/usr/bin/env python3
"""Render a candidate-bound prodlike control bundle from neutral reviewed templates; no deployment."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class BundleError(RuntimeError):pass
def req(c,r):
    if not c:raise BundleError(r)
def sha_bytes(raw):return hashlib.sha256(raw).hexdigest()
def sha_file(p):return sha_bytes(Path(p).read_bytes())
def safe_rel(name):
    p=Path(name);return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name
def load_templates(path):
    x=json.loads(Path(path).read_text());req(type(x) is dict and x.get('schema_version')==1 and x.get('kind')=='AIFILM_P00_PRODLIKE_CONTROL_TEMPLATES_V2','TEMPLATE_SCHEMA')
    rows=x.get('files');req(type(rows) is list and len(rows)==x.get('template_count')==63,'TEMPLATE_COUNT');seen=set()
    for r in rows:
        req(type(r) is dict and set(r)=={'content','deploy_mode','path','sha256'},'TEMPLATE_ROW')
        req(safe_rel(r['path']) and r['path'] not in seen,'TEMPLATE_PATH');seen.add(r['path'])
        raw=r['content'].encode();req(sha_bytes(raw)==r['sha256'],'TEMPLATE_HASH:'+r['path'])
        req(r['deploy_mode'] in ('600','644','700','750'),'TEMPLATE_MODE')
        if r['path'].startswith(('scripts/','systemd/')):
            low=raw.lower();req(b'dev21' not in low and b'dev22' not in low,'TEMPLATE_STALE_IDENTITY:'+r['path'])
    req(sum(1 for r in rows if r['path'].endswith('.timer'))==x.get('expected_timer_count')==11,'TEMPLATE_TIMER_COUNT')
    return x

def build(binding,binding_sha256,runtime_manifest,templates,output,runtime_root,rebuild_root,host_backup_root,offhost_export_root,authority_evidence_root):
    profile,profile_sha=load_profile(binding,binding_sha256);rm=json.loads(Path(runtime_manifest).read_text());tpl=load_templates(templates);out=Path(output)
    req(not out.exists(),'OUTPUT_EXISTS')
    expected={'candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,'implementation_version':profile['implementation_version'],
              'source_commit':profile['source_commit'],'source_digest':profile['build_digest'],'test_digest':profile['test_set_digest'],
              'contract_digest':profile['contract_digest'],'package_sha256':profile['package_sha256'],'wheel_sha256':profile['wheel_sha256']}
    for k,v in expected.items():req(rm.get(k)==v,'RUNTIME_IDENTITY:'+k)
    out.mkdir(parents=True,mode=0o700);files={}
    for row in tpl['files']:
        p=out/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(row['content']);os.chmod(p,int(row['deploy_mode'],8))
        files[row['path']]={'sha256':sha_file(p),'size':p.stat().st_size,'deploy_mode':row['deploy_mode']}
    release_name=profile['implementation_version'].split('.')[-1]
    control={'schema_version':1,'kind':'AIFILM_P00_RELEASE_CONTROL_V2','release_name':release_name,
             'candidate_id':profile['candidate_id'],'candidate_binding_sha256':profile_sha,
             'implementation_version':profile['implementation_version'],'source_commit':profile['source_commit'],
             'source_digest':profile['build_digest'],'test_digest':profile['test_set_digest'],'contract_digest':profile['contract_digest'],
             'package_sha256':profile['package_sha256'],'wheel_sha256':profile['wheel_sha256'],
             'runtime_root':runtime_root,'rebuild_root':rebuild_root,'host_backup_root':host_backup_root,
             'offhost_export_root':offhost_export_root,'authority_evidence_root':authority_evidence_root,
             'authority_model':profile['authority_model'],'verify_service':'aifilm-p00-current-verify.service',
             'verify_timer':'aifilm-p00-current-verify.timer','expected_timer_count':11,
             'native_authority':False,'native_execution_started':False}
    cp=out/'release-control.json';cp.write_text(json.dumps(control,indent=2,sort_keys=True)+'\n');os.chmod(cp,0o600)
    files['release-control.json']={'sha256':sha_file(cp),'size':cp.stat().st_size,'deploy_mode':'600'}
    manifest={'schema_version':1,'kind':'AIFILM_P00_CONTROL_BUNDLE_V2','candidate_id':profile['candidate_id'],
              'candidate_binding_sha256':profile_sha,'implementation_version':profile['implementation_version'],
              'source_commit':profile['source_commit'],'template_sha256':sha_file(templates),
              'file_count':len(files),'script_count':sum(1 for k in files if k.startswith('scripts/')),
              'systemd_file_count':sum(1 for k in files if k.startswith('systemd/')),
              'timer_count':sum(1 for k in files if k.endswith('.timer')),'files':files,
              'native_execution_started':False,'deployment_started':False}
    mp=out/'CONTROL_BUNDLE_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');os.chmod(mp,0o444)
    req(len(files)==64 and manifest['timer_count']==11,'BUNDLE_POPULATION')
    return {'kind':'AIFILM_P00_CONTROL_BUNDLE_BUILD_V2','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_binding_sha256':profile_sha,'file_count':64,'timer_count':11,'bundle_manifest_sha256':sha_file(mp),
            'native_execution_started':False,'deployment_started':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--runtime-manifest',required=True);ap.add_argument('--templates',required=True);ap.add_argument('--output',required=True)
    ap.add_argument('--runtime-root',required=True);ap.add_argument('--rebuild-root',required=True);ap.add_argument('--host-backup-root',required=True)
    ap.add_argument('--offhost-export-root',required=True);ap.add_argument('--authority-evidence-root',required=True);a=ap.parse_args()
    try:o=build(a.binding,a.binding_sha256,a.runtime_manifest,a.templates,a.output,a.runtime_root,a.rebuild_root,a.host_backup_root,a.offhost_export_root,a.authority_evidence_root);rc=0
    except (ProfileError,BundleError,OSError,ValueError,json.JSONDecodeError) as e:o={'kind':'AIFILM_P00_CONTROL_BUNDLE_BUILD_V2','status':'FAIL','reason':str(e),'native_execution_started':False,'deployment_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
