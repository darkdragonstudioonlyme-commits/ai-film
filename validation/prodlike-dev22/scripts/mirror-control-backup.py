#!/usr/bin/env python3
import hashlib, json, os, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

BASE = Path('/home/dragon/ai-film-runtime')
LOCAL = BASE / 'backups'
CONTROL=load_control()
TARGET = Path(CONTROL['host_backup_root'])
VERIFY = BASE / 'bin/verify-control-backup.py'
RETENTION = 14

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def atomic_copy(src, dst):
    tmp = dst.with_name('.' + dst.name + f'.tmp.{os.getpid()}')
    shutil.copyfile(src, tmp)
    with open(tmp, 'rb') as f:
        os.fsync(f.fileno())
    os.replace(tmp, dst)

def main():
    p = subprocess.run([str(VERIFY)], text=True, capture_output=True)
    if p.returncode != 0:
        print('AIFILM_HOST_MIRROR_FAIL source-backup-invalid')
        return 2
    archives = sorted(LOCAL.glob('control-state-*.tar.gz'), key=lambda x: x.stat().st_mtime, reverse=True)
    if not archives:
        print('AIFILM_HOST_MIRROR_FAIL no-local-backup')
        return 3
    src = archives[0]
    sidecar = src.with_suffix(src.suffix + '.sha256')
    if not sidecar.is_file():
        print('AIFILM_HOST_MIRROR_FAIL local-sidecar-missing')
        return 4
    digest = sha256(src)
    TARGET.mkdir(parents=True, exist_ok=True)
    dst = TARGET / src.name
    dst_sidecar = TARGET / sidecar.name
    atomic_copy(src, dst)
    atomic_copy(sidecar, dst_sidecar)
    if sha256(dst) != digest:
        print('AIFILM_HOST_MIRROR_FAIL destination-hash')
        return 5
    index = {
        'schema_version': 1,
        'kind': 'AIFILM_P00_HOST_BACKUP_MIRROR',
        'copied_at_utc': datetime.now(timezone.utc).isoformat(),
        'archive': dst.name,
        'archive_sha256': digest,
        'source_verified': True,
        'native_authority_included': False,
        'protected_identity_included': False,
        'retention': RETENTION,
    }
    idx_tmp = TARGET / f'.mirror-index.json.tmp.{os.getpid()}'
    idx_tmp.write_text(json.dumps(index, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(idx_tmp, TARGET / 'mirror-index.json')
    mirrored = sorted(TARGET.glob('control-state-*.tar.gz'), key=lambda x: x.stat().st_mtime, reverse=True)
    for old in mirrored[RETENTION:]:
        old.with_suffix(old.suffix + '.sha256').unlink(missing_ok=True)
        old.unlink(missing_ok=True)
    print(f'AIFILM_HOST_MIRROR_PASS archive={dst.name} sha256={digest} retention={RETENTION}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
