#!/usr/bin/env python3
import argparse, hashlib, io, json, os, subprocess, tarfile, tempfile, zipfile
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

CONTROL=load_control()
ROOT=Path(CONTROL['offhost_export_root'])
NAME=CONTROL['offhost_export_name']
EXPECTED_SOURCE=CONTROL['source_commit']
MAX_AGE_HOURS=30

def digest_bytes(data): return hashlib.sha256(data).hexdigest()
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

def safe_name(name):
    p=Path(name)
    return not p.is_absolute() and '..' not in p.parts and '\\' not in name
def verify_inner_backup(data):
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:
        names=t.getnames()
        if any(not safe_name(n) for n in names): raise RuntimeError('unsafe-inner-path')
        if 'backup-manifest.json' not in names: raise RuntimeError('inner-manifest-missing')
        meta=json.load(t.extractfile('backup-manifest.json'))
        if meta.get('native_authority_included') is not False: raise RuntimeError('inner-native-authority')
        if meta.get('protected_identity_included') is not False: raise RuntimeError('inner-protected-identity')
        records=meta.get('files',{})
        if set(names)!={'backup-manifest.json',*records.keys()}: raise RuntimeError('inner-member-set')
        for arc,rec in records.items():
            raw=t.extractfile(arc).read()
            if len(raw)!=rec['size'] or digest_bytes(raw)!=rec['sha256']: raise RuntimeError('inner-hash:'+arc)
        return len(records)

def run(args,cwd,env):
    p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env)
    if p.returncode: raise RuntimeError((p.stderr or p.stdout).strip())
    return p.stdout.strip()
def drill(z):
    with tempfile.TemporaryDirectory(prefix='offhost-drill.',dir='/home/dragon/ai-film-runtime/state-snapshots') as td:
        td=Path(td); bundle=td/'bundle'; bundle.mkdir()
        z.extractall(bundle)
        app=td/'app'
        with zipfile.ZipFile(bundle/'rebuild'/CONTROL['package_name']) as pkg:
            pm=json.loads(pkg.read('MANIFEST.json'))
            for row in pm['files']: pkg.extract(row['path'],app)
        count=0
        for line in (bundle/'rebuild/app-manifest.sha256').read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            dg,name=line.split(None,1); p=app/name.strip().lstrip('*')
            if not p.is_file() or sha(p)!=dg: raise RuntimeError('app-hash:'+name)
            count+=1
        if count!=CONTROL['app_file_count']: raise RuntimeError('app-count')
        venv=td/'venv'
        subprocess.run(['/usr/bin/python3','-m','venv','--without-pip',str(venv)],check=True,capture_output=True,text=True)
        site=next((venv/'lib').glob('python*/site-packages'))
        (site/'aifilm_current_app.pth').write_text(str(app/'src')+'\n',encoding='utf-8')
        env={'HOME':str(td/'home'),'USER':'dragon','LOGNAME':'dragon','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PATH':'/usr/bin:/bin','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(td/'tmp')}
        Path(env['HOME']).mkdir(); Path(env['TMPDIR']).mkdir()
        py=str(venv/'bin/python')
        version=run([py,'-m','aifilm_p00','--version'],app,env)
        pre=json.loads(run([py,'-m','aifilm_p00','preflight','--workspace-only'],app,env))
        inv=json.loads(run([py,'tools/run_native_acceptance_tests.py','--list'],app,env))
        if version!=CONTROL['implementation_version'] or pre.get('host_ready') is not False: raise RuntimeError('rebuilt-runtime')
        if inv.get('case_count')!=86 or inv.get('actual_status')!='NOT_RUN': raise RuntimeError('rebuilt-inventory')
        return {'app_files':count,'version':version,'inventory':'86 NOT_RUN','host_ready':False}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--drill',action='store_true'); ap.add_argument('--json',action='store_true')
    args=ap.parse_args(); target=ROOT/NAME; side=ROOT/(NAME+'.sha256')
    if not target.is_file() or not side.is_file(): raise RuntimeError('export-missing')
    actual=sha(target); expected=side.read_text(encoding='utf-8').split()[0]
    if actual!=expected: raise RuntimeError('export-sidecar-mismatch')
    with zipfile.ZipFile(target) as z:
        names=z.namelist()
        if any(not safe_name(n) for n in names): raise RuntimeError('unsafe-export-path')
        if 'OFFHOST-DR-MANIFEST.json' not in names: raise RuntimeError('export-manifest-missing')
        meta=json.loads(z.read('OFFHOST-DR-MANIFEST.json'))
        if meta.get('source_commit')!=EXPECTED_SOURCE or meta.get('release_name')!=CONTROL['release_name'] or meta.get('status')!='TRANSFER_READY': raise RuntimeError('export-identity')
        for key in ('native_authority_included','protected_identity_included','credentials_included','off_host_copy_completed'):
            if meta.get(key) is not False: raise RuntimeError('unsafe-flag:'+key)
        created=datetime.fromisoformat(meta['created_at_utc']); age=(datetime.now(timezone.utc)-created).total_seconds()
        if age<0 or age>MAX_AGE_HOURS*3600: raise RuntimeError('export-stale')
        records=meta.get('files',{})
        if len(records)!=7 or set(names)!={'OFFHOST-DR-MANIFEST.json',*records.keys()}: raise RuntimeError('export-member-set')
        for arc,rec in records.items():
            raw=z.read(arc)
            if len(raw)!=rec['size'] or digest_bytes(raw)!=rec['sha256']: raise RuntimeError('export-member-hash:'+arc)
        control=[n for n in records if n.startswith('control/') and n.endswith('.tar.gz')]
        if len(control)!=1: raise RuntimeError('control-archive-count')
        inner_count=verify_inner_backup(z.read(control[0]))
        probe=drill(z) if args.drill else None
    out={'kind':'AIFILM_P00_OFFHOST_EXPORT_VERIFY','status':'PASS','export_sha256':actual,'payload_files':7,
         'control_files':inner_count,'age_seconds':int(age),'drill':probe,'off_host_copy_completed':False}
    print(json.dumps(out,sort_keys=True,separators=(',',':')) if args.json else
          f"AIFILM_OFFHOST_EXPORT_VERIFY_PASS payloads=7 control_files={inner_count} age={int(age)}s drill={bool(probe)} sha256={actual}")
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e:
        print('AIFILM_OFFHOST_EXPORT_VERIFY_FAIL '+str(e)); raise SystemExit(1)
