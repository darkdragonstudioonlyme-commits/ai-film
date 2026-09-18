#!/usr/bin/env python3
"""Build an immutable non-native dev22 prodlike release from exact reviewed artifacts."""
import argparse,hashlib,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path

def sha_bytes(raw): return hashlib.sha256(raw).hexdigest()
def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
def safe_rel(name):
    p=Path(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name

def load_control(path):
    x=json.loads(Path(path).read_text(encoding='utf-8'))
    required={'schema_version','kind','release_name','implementation_version','source_commit','source_digest','test_digest','contract_digest','package_name','package_sha256','wheel_name','wheel_sha256','app_file_count','runtime_root','rebuild_root','host_backup_root','offhost_export_root','offhost_export_name','authority_evidence_root','authority_model','verify_service','verify_timer','expected_timer_count','native_authority','native_execution_started'}
    if not isinstance(x,dict) or set(x)!=required or x['schema_version']!=1 or x['kind']!='AIFILM_P00_RELEASE_CONTROL': raise RuntimeError('control-schema')
    if x['native_authority'] is not False or x['native_execution_started'] is not False: raise RuntimeError('control-native-boundary')
    return x

def run(args,cwd=None,env=None):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env)
    if p.returncode: raise RuntimeError((p.stderr or p.stdout).strip())
    return p.stdout.strip()

def write_release_scripts(root):
    bindir=root/'bin'; bindir.mkdir(parents=True,exist_ok=True)
    launcher=bindir/'aifilm-p00'
    launcher.write_text('''#!/bin/sh\nset -eu\nROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)\nexport HOME="$ROOT/home"\nexport USER=dragon LOGNAME=dragon LANG=C.UTF-8 LC_ALL=C.UTF-8\nexport PATH="$ROOT/venv/bin:/usr/bin:/bin"\nexport PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1\nexport TMPDIR="$ROOT/var/tmp"\nunset PYTHONPATH VIRTUAL_ENV CONDA_PREFIX CONDA_DEFAULT_ENV\nexec "$ROOT/venv/bin/python" -m aifilm_p00 "$@"\n''',encoding='utf-8')
    verify=bindir/'verify-runtime'
    verify.write_text(r'''#!/usr/bin/env python3
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; APP=ROOT/'app'; VENV=ROOT/'venv'; MAN=ROOT/'runtime-manifest.json'; AM=ROOT/'app-manifest.sha256'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()
def fail(x): print('PRODLIKE_RUNTIME_VERIFY_FAIL '+x,file=sys.stderr); raise SystemExit(1)
m=json.loads(MAN.read_text(encoding='utf-8'))
if m.get('schema_version')!=1 or m.get('kind')!='P00_WSL_PRODLIKE_RUNTIME': fail('manifest-schema')
if m.get('native_execution_started') is not False or m.get('native_lab_authority') is not False: fail('native-boundary')
if sha(AM)!=m.get('app_manifest_sha256'): fail('app-manifest-hash')
expected={};
for line in AM.read_text(encoding='utf-8').splitlines():
 if not line.strip(): continue
 d,n=line.split(None,1);n=n.strip().lstrip('*')
 if n in expected: fail('app-manifest-duplicate')
 expected[n]=d
if len(expected)!=m.get('app_file_count'): fail('app-count')
actual={p.relative_to(APP).as_posix() for p in APP.rglob('*') if p.is_file()}
if actual!=set(expected): fail('app-member-set')
for n,d in expected.items():
 p=APP/n
 if sha(p)!=d: fail('app-byte-drift:'+n)
 if p.stat().st_mode & 0o222: fail('app-file-writable:'+n)
for p in [APP,*[x for x in APP.rglob('*') if x.is_dir()]]:
 if p.stat().st_mode & 0o222: fail('app-dir-writable:'+p.relative_to(APP).as_posix())
py=VENV/'bin/python'; tmp=ROOT/'var/tmp'; home=ROOT/'home'
env={'HOME':str(home),'USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PATH':f'{VENV}/bin:/usr/bin:/bin','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','TMPDIR':str(tmp)}
def run(args,cwd=APP):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env)
 if p.returncode: fail('command:'+((p.stderr or p.stdout).strip()[-300:]))
 return p.stdout.strip()
version=run([str(py),'-m','aifilm_p00','--version'])
if version!=m.get('implementation_version'): fail('version')
pre=json.loads(run([str(py),'-m','aifilm_p00','preflight','--workspace-only']))
inv=json.loads(run([str(py),'tools/run_native_acceptance_tests.py','--list']))
if pre.get('host_ready') is not False: fail('workspace-host-ready')
if inv.get('case_count')!=86 or inv.get('actual_status')!='NOT_RUN' or inv.get('parent_cases_executed')!=0 or inv.get('qualification_issued') is not False: fail('inventory')
p=subprocess.run([str(py),'-m','pip','check'],text=True,capture_output=True,env=env)
if p.returncode: fail('pip-check')
print(f"PRODLIKE_RUNTIME_VERIFY_PASS {len(expected)} 86 NOT_RUN release={m.get('release_name')}")
''',encoding='utf-8')
    os.chmod(launcher,0o750);os.chmod(verify,0o750)
    return launcher,verify

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--control',required=True);ap.add_argument('--package',required=True);ap.add_argument('--wheel',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();c=load_control(a.control);pkg=Path(a.package);wheel=Path(a.wheel);out=Path(a.output)
    if out.exists(): raise RuntimeError('output-exists')
    if sha_file(pkg)!=c['package_sha256'] or pkg.name!=c['package_name']: raise RuntimeError('package-identity')
    if sha_file(wheel)!=c['wheel_sha256'] or wheel.name!=c['wheel_name']: raise RuntimeError('wheel-identity')
    out.mkdir(parents=True,mode=0o700);app=out/'app';app.mkdir()
    with zipfile.ZipFile(pkg) as z:
        pm=json.loads(z.read('MANIFEST.json'))
        for k,exp in [('source_commit',c['source_commit']),('implementation_version',c['implementation_version']),('source_content_digest',c['source_digest']),('test_content_digest',c['test_digest']),('contract_digest',c['contract_digest'])]:
            if pm.get(k)!=exp: raise RuntimeError('package-manifest:'+k)
        files=pm.get('files')
        if not isinstance(files,list) or len(files)!=c['app_file_count']: raise RuntimeError('package-file-count')
        seen=set(); lines=[]
        for row in files:
            name=row.get('path');
            if not isinstance(name,str) or not safe_rel(name) or name in seen: raise RuntimeError('package-path')
            seen.add(name);raw=z.read(name)
            if len(raw)!=row.get('bytes') or sha_bytes(raw)!=row.get('sha256'): raise RuntimeError('package-member:'+name)
            p=app/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);lines.append(f"{sha_bytes(raw)}  {name}\n")
    # Verify wheel source modules against exact app source.
    modules=0
    with zipfile.ZipFile(wheel) as z:
        names=set(z.namelist())
        for p in sorted((app/'src/aifilm_p00').rglob('*.py')):
            rel='aifilm_p00/'+p.relative_to(app/'src/aifilm_p00').as_posix();modules+=1
            if rel not in names or z.read(rel)!=p.read_bytes(): raise RuntimeError('wheel-module:'+rel)
    am=out/'app-manifest.sha256';am.write_text(''.join(lines),encoding='utf-8')
    (out/'dist').mkdir();shutil.copy2(wheel,out/'dist'/wheel.name)
    for d in ('home','var/tmp','evidence'): (out/d).mkdir(parents=True,exist_ok=True,mode=0o700)
    run([sys.executable,'-m','venv',str(out/'venv')],cwd=out)
    py=out/'venv/bin/python';purelib=Path(run([str(py),'-c','import sysconfig;print(sysconfig.get_paths()["purelib"])'],cwd=out))
    (purelib/'aifilm_current_app.pth').write_text(str(app/'src')+'\n',encoding='utf-8')
    launcher,verify=write_release_scripts(out)
    # Generate native inventory without native execution.
    env={'HOME':str(out/'home'),'USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PATH':f'{out}/venv/bin:/usr/bin:/bin','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','TMPDIR':str(out/'var/tmp')}
    inv=run([str(py),'tools/run_native_acceptance_tests.py','--list'],cwd=app,env=env)
    invobj=json.loads(inv)
    if invobj.get('case_count')!=86 or invobj.get('actual_status')!='NOT_RUN' or invobj.get('parent_cases_executed')!=0: raise RuntimeError('inventory')
    ip=out/'evidence/native-inventory.json';ip.write_text(json.dumps(invobj,indent=2,sort_keys=True)+'\n');os.chmod(ip,0o600)
    # Make exact app source immutable after inventory collection.
    for p in sorted(app.rglob('*'),reverse=True):
        if p.is_file(): os.chmod(p,0o444)
        elif p.is_dir(): os.chmod(p,0o555)
    os.chmod(app,0o555);os.chmod(am,0o444);os.chmod(out/'dist'/wheel.name,0o444)
    manifest={'schema_version':1,'kind':'P00_WSL_PRODLIKE_RUNTIME','release_name':c['release_name'],'implementation_version':c['implementation_version'],'source_commit':c['source_commit'],'source_digest':c['source_digest'],'test_digest':c['test_digest'],'contract_digest':c['contract_digest'],'package_name':c['package_name'],'package_sha256':c['package_sha256'],'wheel_name':c['wheel_name'],'wheel_sha256':c['wheel_sha256'],'app_file_count':c['app_file_count'],'app_manifest_sha256':sha_file(am),'launcher_sha256':sha_file(launcher),'verify_runtime_sha256':sha_file(verify),'wheel_module_count':modules,'runtime_verify':'PASS','status':'READY_NON_NATIVE_CANDIDATE','authority_model':c['authority_model'],'native_lab_authority':False,'native_execution_started':False,'native_site_activation':'BLOCKED_V02_LOCAL_OPERATOR_LAB_AUTHORITY'}
    mp=out/'runtime-manifest.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');os.chmod(mp,0o444)
    verify_out=run([str(verify)],cwd=out)
    receipt={'kind':'AIFILM_P00_PRODLIKE_RELEASE_BUILD','status':'PASS','release_name':c['release_name'],'runtime_manifest_sha256':sha_file(mp),'app_manifest_sha256':sha_file(am),'app_files':c['app_file_count'],'wheel_modules':modules,'verify_stdout':verify_out,'native_execution_started':False}
    print(json.dumps(receipt,sort_keys=True,separators=(',',':')));return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e: print('AIFILM_P00_PRODLIKE_RELEASE_BUILD_FAIL '+str(e),file=sys.stderr);raise SystemExit(1)
