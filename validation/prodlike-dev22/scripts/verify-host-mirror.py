#!/usr/bin/env python3
import hashlib, json, tarfile, time
from pathlib import Path
from control_common import load_control

CONTROL=load_control()
TARGET = Path(CONTROL['host_backup_root'])
MAX_AGE = 30 * 3600

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def fail(reason):
    print('AIFILM_HOST_MIRROR_VERIFY_FAIL ' + reason)
    raise SystemExit(2)

def main():
    idx_path = TARGET / 'mirror-index.json'
    if not idx_path.is_file(): fail('index-missing')
    try: idx = json.loads(idx_path.read_text(encoding='utf-8'))
    except Exception: fail('index-invalid')
    if idx.get('kind') != 'AIFILM_P00_HOST_BACKUP_MIRROR': fail('index-kind')
    if idx.get('native_authority_included') is not False: fail('native-authority-flag')
    if idx.get('protected_identity_included') is not False: fail('protected-identity-flag')
    archive = TARGET / str(idx.get('archive',''))
    sidecar = archive.with_suffix(archive.suffix + '.sha256')
    if not archive.is_file() or not sidecar.is_file(): fail('archive-or-sidecar-missing')
    age = time.time() - archive.stat().st_mtime
    if age < 0 or age > MAX_AGE: fail('archive-stale')
    digest = sha256(archive)
    if digest != idx.get('archive_sha256'): fail('index-sha-mismatch')
    parts = sidecar.read_text(encoding='utf-8').strip().split()
    if not parts or parts[0] != digest: fail('sidecar-sha-mismatch')
    try:
        with tarfile.open(archive, 'r:gz') as tar:
            names = tar.getnames()
            if len(names) != len(set(names)): fail('duplicate-member')
            for name in names:
                p = Path(name)
                if p.is_absolute() or '..' in p.parts: fail('unsafe-member-path')
            if 'backup-manifest.json' not in names: fail('manifest-missing')
            manifest = json.load(tar.extractfile('backup-manifest.json'))
            if manifest.get('native_authority_included') is not False: fail('manifest-native-authority')
            if manifest.get('protected_identity_included') is not False: fail('manifest-protected-identity')
            records = manifest.get('files')
            if not isinstance(records, dict): fail('manifest-files')
            expected = {'backup-manifest.json', *records.keys()}
            if set(names) != expected: fail('member-set-drift')
            for name, rec in records.items():
                member = tar.extractfile(name)
                if member is None: fail('member-missing')
                raw = member.read()
                if hashlib.sha256(raw).hexdigest() != rec.get('sha256'): fail('member-hash-' + name)
                if len(raw) != rec.get('size'): fail('member-size-' + name)
    except (tarfile.TarError, OSError, json.JSONDecodeError):
        fail('archive-invalid')
    print(f'AIFILM_HOST_MIRROR_VERIFY_PASS files={len(records)} age={int(age)}s sha256={digest}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
