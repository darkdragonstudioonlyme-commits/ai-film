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

VERIFY_RUNTIME_SOURCE=r'''#!/usr/bin/python3 -I
from __future__ import annotations
import hashlib,json,os,stat,subprocess,sys
from pathlib import Path

class VerifyError(RuntimeError): pass
def req(c,r):
    if not c: raise VerifyError(r)
def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def safe_rel(name):
    p=Path(name); return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name
def regular(path,reason):
    p=Path(path); req(p.is_file() and not p.is_symlink(),reason); return p
def clean_env(root):
    return {'HOME':str(root/'home'),'USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
            'PATH':'/usr/bin:/bin','PYTHONPATH':str(root/'app/src'),'PYTHONNOUSERSITE':'1',
            'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','TMPDIR':str(root/'var/tmp')}
def run(args,cwd,env):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env)
    req(p.returncode==0,'COMMAND:'+((p.stderr or p.stdout).strip()[-400:]))
    return p.stdout.strip()
def parse_app_manifest(path):
    rows={}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if not line: continue
        parts=line.split('  ',1); req(len(parts)==2,'APP_MANIFEST_LINE')
        digest,name=parts; req(len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'APP_MANIFEST_DIGEST')
        req(safe_rel(name) and name not in rows,'APP_MANIFEST_PATH'); rows[name]=digest
    req(bool(rows),'APP_MANIFEST_EMPTY'); return rows
def main():
    invoked=Path(__file__).absolute()
    req(invoked.is_file() and not invoked.is_symlink(),'VERIFY_RUNTIME_PATH_TYPE')
    req(stat.S_IMODE(invoked.stat().st_mode)==0o750 and os.access(invoked,os.X_OK),'VERIFY_RUNTIME_MODE')
    root=invoked.parent.parent
    mp=regular(root/'runtime-manifest.json','RUNTIME_MANIFEST_PATH')
    manifest=json.loads(mp.read_text(encoding='utf-8'))
    req(manifest.get('schema_version')==1 and manifest.get('kind')=='P00_WSL_PRODLIKE_RUNTIME_V2','RUNTIME_MANIFEST_SCHEMA')
    req(manifest.get('runtime_verify')=='PASS','RUNTIME_VERIFY_STATUS')
    req(manifest.get('native_execution_started') is False and manifest.get('native_lab_authority') is False
        and manifest.get('qualification_issued') is False and manifest.get('host_ready') is False,'RUNTIME_BOUNDARY')
    req(manifest.get('verify_runtime_sha256')==sha_file(invoked),'VERIFY_RUNTIME_SELF_HASH')
    am=regular(root/'app-manifest.sha256','APP_MANIFEST_PATH')
    req(stat.S_IMODE(am.stat().st_mode)==0o444,'APP_MANIFEST_MODE')
    req(manifest.get('app_manifest_sha256')==sha_file(am),'APP_MANIFEST_HASH')
    expected=parse_app_manifest(am); app=root/'app'
    req(app.is_dir() and not app.is_symlink() and stat.S_IMODE(app.stat().st_mode)==0o555,'APP_ROOT_MODE')
    actual={p.relative_to(app).as_posix() for p in app.rglob('*') if p.is_file()}
    req(actual==set(expected),'APP_MEMBER_SET')
    for name,digest in expected.items():
        p=regular(app/name,'APP_FILE_PATH:'+name)
        req(stat.S_IMODE(p.stat().st_mode)==0o444,'APP_FILE_MODE:'+name)
        req(sha_file(p)==digest,'APP_FILE_HASH:'+name)
    for p in app.rglob('*'):
        if p.is_dir():
            req(not p.is_symlink() and stat.S_IMODE(p.stat().st_mode)==0o555,'APP_DIR_MODE:'+p.relative_to(app).as_posix())
    wheel=regular(root/'dist'/manifest.get('wheel_name',''),'WHEEL_PATH')
    req(stat.S_IMODE(wheel.stat().st_mode)==0o444,'WHEEL_MODE')
    req(sha_file(wheel)==manifest.get('wheel_sha256'),'WHEEL_HASH')
    invp=regular(root/'evidence/native-inventory.json','INVENTORY_PATH')
    req(sha_file(invp)==manifest.get('inventory_sha256'),'INVENTORY_HASH')
    inv=json.loads(invp.read_text(encoding='utf-8'))
    req(manifest.get('inventory_case_count')==86 and manifest.get('inventory_status')=='NOT_RUN','INVENTORY_MANIFEST')
    req(inv.get('case_count')==86 and inv.get('actual_status')=='NOT_RUN' and inv.get('parent_cases_executed')==0
        and inv.get('qualification_issued') is False,'INVENTORY_SEMANTICS')
    env=clean_env(root)
    version=run(['/usr/bin/python3','-m','aifilm_p00','--version'],app,env)
    req(version==manifest.get('implementation_version'),'VERSION')
    pre=json.loads(run(['/usr/bin/python3','-m','aifilm_p00','preflight','--workspace-only'],app,env))
    req(pre.get('host_ready') is False,'PREFLIGHT_HOST_READY')
    live=json.loads(run(['/usr/bin/python3','tools/run_native_acceptance_tests.py','--list'],app,env))
    req(live.get('case_count')==86 and live.get('actual_status')=='NOT_RUN' and live.get('parent_cases_executed')==0
        and live.get('qualification_issued') is False,'LIVE_INVENTORY')
    print('PRODLIKE_RUNTIME_VERIFY_PASS version='+version+' native=NOT_RUN')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as exc:
        print('PRODLIKE_RUNTIME_VERIFY_FAIL reason='+type(exc).__name__+':'+str(exc),file=sys.stderr)
        raise SystemExit(1)
'''

def render_verify_runtime():
    return VERIFY_RUNTIME_SOURCE.encode('utf-8')

def validate_verify_runtime_artifact(path,expected_sha256):
    p=Path(path)
    require(p.exists() and p.is_file() and not p.is_symlink(),'VERIFY_RUNTIME_PATH_TYPE')
    require((p.stat().st_mode & 0o777)==0o750 and os.access(p,os.X_OK),'VERIFY_RUNTIME_MODE')
    require(sha_file(p)==expected_sha256,'VERIFY_RUNTIME_HASH')
    return True

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
    bindir=out/'bin';bindir.mkdir(mode=0o755)
    vp=bindir/'verify-runtime';vp.write_bytes(render_verify_runtime());os.chmod(vp,0o750)
    verify_sha=sha_file(vp);validate_verify_runtime_artifact(vp,verify_sha)
    manifest={'schema_version':1,'kind':'P00_WSL_PRODLIKE_RUNTIME_V2','candidate_id':profile['candidate_id'],
              'candidate_binding_sha256':profile_sha,'release_name':profile['implementation_version'].split('.')[-1],
              'implementation_version':profile['implementation_version'],'source_commit':profile['source_commit'],
              'source_digest':profile['build_digest'],'test_digest':profile['test_set_digest'],'contract_digest':profile['contract_digest'],
              'package_name':pkg.name,'package_sha256':profile['package_sha256'],'wheel_name':wh.name,'wheel_sha256':profile['wheel_sha256'],
              'app_file_count':len(seen),'app_manifest_sha256':sha_file(am),'wheel_module_count':modules,
              'inventory_sha256':sha_file(ip),'inventory_case_count':86,'inventory_status':'NOT_RUN',
              'verify_runtime_sha256':verify_sha,'runtime_verify':'PASS',
              'status':'READY_NON_NATIVE_CANDIDATE','authority_model':profile['authority_model'],
              'native_lab_authority':False,'native_execution_started':False,'qualification_issued':False,'host_ready':False}
    mp=out/'runtime-manifest.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');os.chmod(mp,0o444)
    verify_stdout=run([str(vp)],out,clean_env(app))
    require('PRODLIKE_RUNTIME_VERIFY_PASS' in verify_stdout,'VERIFY_RUNTIME_EXECUTION')
    return {'kind':'AIFILM_P00_PRODLIKE_RELEASE_BUILD_V2','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_binding_sha256':profile_sha,'runtime_manifest_sha256':sha_file(mp),'app_manifest_sha256':sha_file(am),
            'verify_runtime_sha256':verify_sha,'verify_runtime_status':'PASS',
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
