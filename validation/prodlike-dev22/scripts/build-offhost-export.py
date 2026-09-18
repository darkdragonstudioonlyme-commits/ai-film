#!/usr/bin/env python3
import hashlib, json, os, subprocess, tempfile, zipfile
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

BASE=Path('/home/dragon/ai-film-runtime')
CONTROL=load_control()
OUT=Path(CONTROL['offhost_export_root'])
REBUILD=Path(CONTROL['rebuild_root'])
BACKUP_VERIFY=BASE/'bin/verify-control-backup.py'
REBUILD_VERIFY=BASE/'bin/verify-rebuild-set.py'
EXPORT_NAME=CONTROL['offhost_export_name']
SOURCE_COMMIT=CONTROL['source_commit']

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

def run_json(args):
    p=subprocess.run(args,text=True,capture_output=True)
    if p.returncode: raise RuntimeError((p.stderr or p.stdout).strip())
    return json.loads(p.stdout)
def main():
    backup=run_json([str(BACKUP_VERIFY),'--json'])
    if backup.get('status')!='PASS': raise RuntimeError('backup-not-pass')
    rebuild=run_json([str(REBUILD_VERIFY),'--json'])
    if rebuild.get('status')!='PASS': raise RuntimeError('rebuild-not-pass')
    archive=BASE/'backups'/backup['archive']
    sidecar=archive.with_suffix(archive.suffix+'.sha256')
    if not archive.is_file() or not sidecar.is_file(): raise RuntimeError('backup-files-missing')
    idx=json.loads((REBUILD/'rebuild-index.json').read_text(encoding='utf-8'))
    payloads={
        f'control/{archive.name}':archive,
        f'control/{sidecar.name}':sidecar,
        'rebuild/rebuild-index.json':REBUILD/'rebuild-index.json',
    }
    for name in sorted(idx['files']):
        payloads[f'rebuild/{name}']=REBUILD/name
    records={arc:{'sha256':sha(p),'size':p.stat().st_size} for arc,p in sorted(payloads.items())}
    stamp=archive.name.removeprefix('control-state-').removesuffix('.tar.gz')
    epoch=datetime.strptime(stamp,'%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
    manifest={
        'schema_version':1,'kind':'AIFILM_P00_OFFHOST_DR_EXPORT','status':'TRANSFER_READY',
        'created_at_utc':epoch.isoformat(),'payload_epoch_utc':epoch.isoformat(),
        'deterministic_export':True,'source_commit':SOURCE_COMMIT,
        'control_backup_sha256':backup['archive_sha256'],'package_sha256':rebuild['package_sha256'],'release_name':CONTROL['release_name'],
        'native_authority_included':False,'protected_identity_included':False,
        'credentials_included':False,'off_host_copy_completed':False,'files':records,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/EXPORT_NAME
    tmp=OUT/(EXPORT_NAME+'.tmp')
    manifest_bytes=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    def add(z,arc,data):
        info=zipfile.ZipInfo(arc,date_time=epoch.timetuple()[:6])
        info.create_system=3; info.external_attr=(0o600 & 0xffff)<<16
        info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(tmp,'w') as z:
        add(z,'OFFHOST-DR-MANIFEST.json',manifest_bytes)
        for arc,p in sorted(payloads.items()): add(z,arc,p.read_bytes())
    tmp.replace(target)
    digest=sha(target)
    side=OUT/(EXPORT_NAME+'.sha256')
    side_tmp=OUT/(EXPORT_NAME+'.sha256.tmp')
    side_tmp.write_text(f'{digest}  {EXPORT_NAME}\n',encoding='utf-8')
    side_tmp.replace(side)
    print(f'AIFILM_OFFHOST_EXPORT_BUILD_PASS sha256={digest} payloads={len(records)} archive={EXPORT_NAME}')
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e:
        print('AIFILM_OFFHOST_EXPORT_BUILD_FAIL '+str(e))
        raise SystemExit(1)
