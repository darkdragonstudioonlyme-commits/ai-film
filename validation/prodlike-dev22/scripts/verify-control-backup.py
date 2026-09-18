#!/usr/bin/env python3
import argparse, hashlib, json, os, tarfile, time
from pathlib import Path

BASE = Path('/home/dragon/ai-film-runtime')
BACKUPS = BASE / 'backups'
MAX_AGE_SECONDS = 30 * 3600

def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def mode(path):
    return oct(path.stat().st_mode & 0o777)[2:]

def fail(reason, **extra):
    out={'kind':'AIFILM_P00_CONTROL_BACKUP_VERIFY','status':'FAIL','reason':reason,**extra}
    print(json.dumps(out,sort_keys=True,separators=(',',':')))
    raise SystemExit(1)
def safe_member(name):
    p=Path(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    archives=sorted(BACKUPS.glob('control-state-*.tar.gz'),key=lambda p:p.stat().st_mtime,reverse=True)
    if not archives: fail('NO_BACKUP')
    archive=archives[0]
    sidecar=archive.with_suffix(archive.suffix+'.sha256')
    if not sidecar.is_file(): fail('SIDECAR_MISSING',archive=archive.name)
    if mode(BACKUPS)!='700' or mode(archive)!='600' or mode(sidecar)!='600':
        fail('PERMISSION_DRIFT',backup_dir_mode=mode(BACKUPS),archive_mode=mode(archive),sidecar_mode=mode(sidecar))
    age=max(0,int(time.time()-archive.stat().st_mtime))
    if age>MAX_AGE_SECONDS: fail('BACKUP_STALE',age_seconds=age)
    parts=sidecar.read_text(encoding='utf-8').strip().split()
    if len(parts)<2 or parts[1]!=archive.name: fail('SIDECAR_SCHEMA')
    actual=sha256_file(archive)
    if parts[0]!=actual: fail('ARCHIVE_HASH_MISMATCH',expected=parts[0],actual=actual)
    with tarfile.open(archive,'r:gz') as tar:
        names=tar.getnames()
        if len(names)!=len(set(names)) or not all(safe_member(n) for n in names):
            fail('UNSAFE_MEMBER_SET')
        if 'backup-manifest.json' not in names: fail('MANIFEST_MISSING')
        try: meta=json.load(tar.extractfile('backup-manifest.json'))
        except Exception: fail('MANIFEST_INVALID')
        if meta.get('schema_version')!=1 or meta.get('kind')!='AIFILM_P00_CONTROL_STATE_BACKUP':
            fail('MANIFEST_SCHEMA')
        if meta.get('native_authority_included') is not False or meta.get('protected_identity_included') is not False:
            fail('PROTECTED_DOMAIN_INCLUDED')
        records=meta.get('files')
        if not isinstance(records,dict) or set(names)!={'backup-manifest.json',*records.keys()}:
            fail('MEMBER_MANIFEST_MISMATCH')
        for name,rec in records.items():
            if not isinstance(rec,dict) or set(rec)!={'sha256','size'}: fail('RECORD_SCHEMA',member=name)
            raw=tar.extractfile(name).read()
            if len(raw)!=rec['size'] or sha256_bytes(raw)!=rec['sha256']:
                fail('MEMBER_HASH_MISMATCH',member=name)
    out={'kind':'AIFILM_P00_CONTROL_BACKUP_VERIFY','status':'PASS','archive':archive.name,
         'archive_sha256':actual,'age_seconds':age,'file_count':len(records),
         'native_authority_included':False,'protected_identity_included':False}
    if args.json: print(json.dumps(out,sort_keys=True,separators=(',',':')))
    else: print(f"AIFILM_CONTROL_BACKUP_VERIFY_PASS files={len(records)} age={age}s sha256={actual}")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
