#!/usr/bin/env python3
"""Build immutable candidate-bound prodlike release bytes. No live deployment or native execution."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class ReleaseError(RuntimeError): pass
def require(c,r):
    if not c: raise ReleaseError(r)
def sha_bytes(raw): return hashlib.sha256(raw).hexdigest()
def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
def safe_rel(name):
    p=Path(name); return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name
def clean_env(app):
    return {'HOME':str(app.parent/'home'),'USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
            'PATH':'/usr/bin:/bin','PYTHONPATH':str(app/'src'),'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1',
            'PYTHONUNBUFFERED':'1','TMPDIR':str(app.parent/'var/tmp')}
def run(args,cwd,env):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env)
    if p.returncode: raise ReleaseError('COMMAND:'+((p.stderr or p.stdout).strip()[-400:]))
    return p.stdout.strip()

def build(binding,binding_sha256,package,wheel,output):
    profile,profile_sha=load_profile(binding,binding_sha256)
    pkg=Path(package);wh=Path(wheel);out=Path(output)
    require(not out.exists(),'OUTPUT_EXISTS')
    require(pkg.is_file() and sha_file(pkg)==profile['package_sha256'],'PACKAGE_IDENTITY')
    require(wh.is_file() and sha_file(wh)==profile['wheel_sha256'],'WHEEL_IDENTITY')
    out.mkdir(parents=True,mode=0o700);app=out/'app';app.mkdir()
    with zipfile.ZipFile(pkg) as z:
        pm=json.loads(z.read('MANIFEST.json'))
        expected={'source_commit':profile['source_commit'],'implementation_version':profile['implementation_version'],
                  'source_content_digest':profile['build_digest'],'test_content_digest':profile['test_set_digest'],
                  'contract_digest':profile['contract_digest']}
        for k,v in expected.items(): require(pm.get(k)==v,'PACKAGE_MANIFEST:'+k)
        files=pm.get('files');require(isinstance(files,list) and files,'PACKAGE_FILES')
        seen=set();lines=[]
        for row in files:
            name=row.get('path');require(isinstance(name,str) and safe_rel(name) and name not in seen,'PACKAGE_PATH')
            seen.add(name);raw=z.read(name)
            require(len(raw)==row.get('bytes') and sha_bytes(raw)==row.get('sha256'),'PACKAGE_MEMBER:'+name)
            p=app/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);lines.append(f"{sha_bytes(raw)}  {name}\n")
    modules=0
    with zipfile.ZipFile(wh) as z:
        names=set(z.namelist())
        for p in sorted((app/'src/aifilm_p00').rglob('*.py')):
            rel='aifilm_p00/'+p.relative_to(app/'src/aifilm_p00').as_posix();modules+=1
            require(rel in names and z.read(rel)==p.read_bytes(),'WHEEL_MODULE:'+rel)
    am=out/'app-manifest.sha256';am.write_text(''.join(lines),encoding='utf-8')
    (out/'dist').mkdir();shutil.copy2(wh,out/'dist'/wh.name)
    for d in ('home','var/tmp','evidence'):(out/d).mkdir(parents=True,exist_ok=True,mode=0o700)
    env=clean_env(app)
    version=run([sys.executable,'-m','aifilm_p00','--version'],app,env);require(version==profile['implementation_version'],'VERSION')
    pre=json.loads(run([sys.executable,'-m','aifilm_p00','preflight','--workspace-only'],app,env));require(pre.get('host_ready') is False,'PREFLIGHT_HOST_READY')
    inv=json.loads(run([sys.executable,'tools/run_native_acceptance_tests.py','--list'],app,env))
    require(inv.get('case_count')==86 and inv.get('actual_status')=='NOT_RUN' and inv.get('parent_cases_executed')==0
            and inv.get('qualification_issued') is False,'NATIVE_INVENTORY')
    ip=out/'evidence/native-inventory.json';ip.write_text(json.dumps(inv,indent=2,sort_keys=True)+'\n');os.chmod(ip,0o600)
    for p in sorted(app.rglob('*'),reverse=True):
        if p.is_file(): os.chmod(p,0o444)
        elif p.is_dir(): os.chmod(p,0o555)
    os.chmod(app,0o555);os.chmod(am,0o444);os.chmod(out/'dist'/wh.name,0o444)
    manifest={'schema_version':1,'kind':'P00_WSL_PRODLIKE_RUNTIME_V2','candidate_id':profile['candidate_id'],
              'candidate_binding_sha256':profile_sha,'release_name':profile['implementation_version'].split('.')[-1],
              'implementation_version':profile['implementation_version'],'source_commit':profile['source_commit'],
              'source_digest':profile['build_digest'],'test_digest':profile['test_set_digest'],'contract_digest':profile['contract_digest'],
              'package_name':pkg.name,'package_sha256':profile['package_sha256'],'wheel_name':wh.name,'wheel_sha256':profile['wheel_sha256'],
              'app_file_count':len(seen),'app_manifest_sha256':sha_file(am),'wheel_module_count':modules,
              'inventory_sha256':sha_file(ip),'inventory_case_count':86,'inventory_status':'NOT_RUN',
              'status':'READY_NON_NATIVE_CANDIDATE','authority_model':profile['authority_model'],
              'native_lab_authority':False,'native_execution_started':False,'qualification_issued':False,'host_ready':False}
    mp=out/'runtime-manifest.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');os.chmod(mp,0o444)
    return {'kind':'AIFILM_P00_PRODLIKE_RELEASE_BUILD_V2','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_binding_sha256':profile_sha,'runtime_manifest_sha256':sha_file(mp),'app_manifest_sha256':sha_file(am),
            'app_files':len(seen),'wheel_modules':modules,'inventory_case_count':86,'inventory_status':'NOT_RUN',
            'native_execution_started':False,'deployment_started':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True)
    ap.add_argument('--package',required=True);ap.add_argument('--wheel',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    try:o=build(a.binding,a.binding_sha256,a.package,a.wheel,a.output);rc=0
    except (ProfileError,ReleaseError,OSError,ValueError,json.JSONDecodeError,zipfile.BadZipFile) as e:
        o={'kind':'AIFILM_P00_PRODLIKE_RELEASE_BUILD_V2','status':'FAIL','reason':str(e),'native_execution_started':False,'deployment_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
