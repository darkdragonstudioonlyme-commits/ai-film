#!/usr/bin/env python3
import hashlib, json, os, tarfile, tempfile
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

BASE = Path('/home/dragon/ai-film-runtime')
CONTROL=load_control()
RELEASE=Path(CONTROL['runtime_root'])
BACKUPS = BASE / 'backups'
AUTH = Path(CONTROL['authority_evidence_root'])
SYSTEMD = Path('/home/dragon/.config/systemd/user')
FILES = {
    'bin/aifilm-p00': RELEASE / 'bin/aifilm-p00',
    'bin/control_common.py': BASE / 'bin/control_common.py',
    'config/release-control.json': BASE / 'config/release-control.json',
    'config/control-bundle-manifest.json': BASE / 'config/control-bundle-manifest.json',
    'bin/activate-release': BASE / 'bin/activate-release',
    'bin/verify-current': BASE / 'bin/verify-current',
    'bin/runtime-health.py': BASE / 'bin/runtime-health.py',
    'bin/backup-control-state.py': BASE / 'bin/backup-control-state.py',
    'bin/verify-control-backup.py': BASE / 'bin/verify-control-backup.py',
    'bin/verify-recovery-state': BASE / 'bin/verify-recovery-state',
    'bin/mirror-control-backup.py': BASE / 'bin/mirror-control-backup.py',
    'bin/verify-host-mirror.py': BASE / 'bin/verify-host-mirror.py',
    'bin/verify-rebuild-set.py': BASE / 'bin/verify-rebuild-set.py',
    'bin/build-offhost-export.py': BASE / 'bin/build-offhost-export.py',
    'bin/verify-offhost-export.py': BASE / 'bin/verify-offhost-export.py',
    'bin/run-failclosed-campaign.py': BASE / 'bin/run-failclosed-campaign.py',
    'bin/run-dr-recovery-rehearsal.py': BASE / 'bin/run-dr-recovery-rehearsal.py',
    'bin/archive-operational-evidence.py': BASE / 'bin/archive-operational-evidence.py',
    'bin/verify-operational-evidence.py': BASE / 'bin/verify-operational-evidence.py',
    'runtime/runtime-manifest.json': RELEASE / 'runtime-manifest.json',
    'runtime/app-manifest.sha256': RELEASE / 'app-manifest.sha256',
    'runtime/native-inventory.json': RELEASE / 'evidence/native-inventory.json',
    'runtime/release-history.log': BASE / 'release-history.log',
    'health/latest.json': BASE / 'health/latest.json',
    'health/latest.sha256': BASE / 'health/latest.sha256',
    'validation/v02-authority-latest.json': AUTH / 'latest.json',
    'validation/v02-authority-latest.sha256': AUTH / 'latest.sha256',
    'evidence/failclosed-campaign/latest.json': BASE / 'run-evidence/prodlike-program/failclosed-campaign/latest.json',
    'evidence/failclosed-campaign/latest.sha256': BASE / 'run-evidence/prodlike-program/failclosed-campaign/latest.sha256',
    'evidence/recovery-rehearsal/latest.json': BASE / 'run-evidence/prodlike-program/recovery-rehearsal/latest.json',
    'evidence/recovery-rehearsal/latest.sha256': BASE / 'run-evidence/prodlike-program/recovery-rehearsal/latest.sha256',
    'systemd/dropins/aifilm-p00-current-verify.service/timeout.conf': SYSTEMD / 'aifilm-p00-current-verify.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-v02-authority-watch.service/timeout.conf': SYSTEMD / 'aifilm-p00-v02-authority-watch.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-runtime-health.service/timeout.conf': SYSTEMD / 'aifilm-p00-runtime-health.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-control-backup.service/timeout.conf': SYSTEMD / 'aifilm-p00-control-backup.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-recovery-verify.service/timeout.conf': SYSTEMD / 'aifilm-p00-recovery-verify.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-host-mirror.service/timeout.conf': SYSTEMD / 'aifilm-p00-host-mirror.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-rebuild-verify.service/timeout.conf': SYSTEMD / 'aifilm-p00-rebuild-verify.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-offhost-export.service/timeout.conf': SYSTEMD / 'aifilm-p00-offhost-export.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-runtime-health.service/ordering.conf': SYSTEMD / 'aifilm-p00-runtime-health.service.d/ordering.conf',
    'systemd/dropins/aifilm-p00-recovery-verify.service/ordering.conf': SYSTEMD / 'aifilm-p00-recovery-verify.service.d/ordering.conf',
    'systemd/dropins/aifilm-p00-dr-rehearsal.service/timeout.conf': SYSTEMD / 'aifilm-p00-dr-rehearsal.service.d/timeout.conf',
    'systemd/dropins/aifilm-p00-failclosed-campaign.service/timeout.conf': SYSTEMD / 'aifilm-p00-failclosed-campaign.service.d/timeout.conf',
}
UNIT_NAMES = [
    'aifilm-p00-current-verify.service',
    'aifilm-p00-current-verify.timer',
    'aifilm-p00-v02-authority-watch.service',
    'aifilm-p00-v02-authority-watch.timer',
    'aifilm-p00-runtime-health.service',
    'aifilm-p00-runtime-health.timer',
    'aifilm-p00-control-backup.service',
    'aifilm-p00-control-backup.timer',
    'aifilm-p00-recovery-verify.service',
    'aifilm-p00-recovery-verify.timer',
    'aifilm-p00-host-mirror.service',
    'aifilm-p00-host-mirror.timer',
    'aifilm-p00-rebuild-verify.service',
    'aifilm-p00-rebuild-verify.timer',
    'aifilm-p00-offhost-export.service',
    'aifilm-p00-offhost-export.timer',
    'aifilm-p00-dr-rehearsal.service',
    'aifilm-p00-dr-rehearsal.timer',
    'aifilm-p00-failclosed-campaign.service',
    'aifilm-p00-failclosed-campaign.timer',
    'aifilm-p00-evidence-ledger.service',
    'aifilm-p00-evidence-ledger.timer',
]
def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def add_units(files):
    for name in UNIT_NAMES:
        p = SYSTEMD / name
        if p.is_file():
            files[f'systemd/{name}'] = p
        if name.endswith('.service'):
            d = SYSTEMD / (name + '.d')
            if d.is_dir():
                for conf in sorted(d.glob('*.conf')):
                    files[f'systemd/dropins/{name}/{conf.name}'] = conf

def add_evidence_history(files):
    root = BASE / 'run-evidence/prodlike-program/history'
    if root.is_dir():
        for p in sorted(root.iterdir()):
            if p.is_file() and (p.suffix in {'.json','.sha256'} or p.name == 'chain-state.json'):
                files[f'evidence/operational-ledger/{p.name}'] = p

def main():
    BACKUPS.mkdir(parents=True, exist_ok=True, mode=0o700)
    files = dict(FILES)
    add_units(files)
    add_evidence_history(files)
    missing = [str(p) for p in files.values() if not p.is_file()]
    if missing:
        print('AIFILM_CONTROL_BACKUP_FAIL missing=' + ','.join(missing))
        return 2
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archive = BACKUPS / f'control-state-{stamp}.tar.gz'
    current_target = str((BASE / 'current').resolve())
    records = {arc: {'sha256': sha256(path), 'size': path.stat().st_size}
               for arc, path in sorted(files.items())}
    meta = {
        'schema_version': 1,
        'kind': 'AIFILM_P00_CONTROL_STATE_BACKUP',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'current_target': current_target,
        'native_authority_included': False,
        'protected_identity_included': False,
        'files': records,
    }
    with tempfile.TemporaryDirectory(prefix='.stage-', dir=BACKUPS) as td:
        stage = Path(td)
        manifest = stage / 'backup-manifest.json'
        manifest.write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        os.chmod(manifest, 0o600)
        with tarfile.open(archive, 'w:gz') as tar:
            tar.add(manifest, arcname='backup-manifest.json', recursive=False)
            for arc, path in sorted(files.items()):
                tar.add(path, arcname=arc, recursive=False)
    os.chmod(archive, 0o600)
    archive_sha = sha256(archive)
    sha_path = archive.with_suffix(archive.suffix + '.sha256')
    sha_path.write_text(f'{archive_sha}  {archive.name}\n', encoding='utf-8')
    os.chmod(sha_path, 0o600)
    with tarfile.open(archive, 'r:gz') as tar:
        names = set(tar.getnames())
        expected = {'backup-manifest.json', *records.keys()}
        if names != expected:
            print('AIFILM_CONTROL_BACKUP_FAIL member-set')
            return 3
        loaded = json.load(tar.extractfile('backup-manifest.json'))
        if loaded != meta:
            print('AIFILM_CONTROL_BACKUP_FAIL manifest-roundtrip')
            return 4
        for arc, rec in records.items():
            h = hashlib.sha256(tar.extractfile(arc).read()).hexdigest()
            if h != rec['sha256']:
                print('AIFILM_CONTROL_BACKUP_FAIL member-hash=' + arc)
                return 5
    archives = sorted(BACKUPS.glob('control-state-*.tar.gz'), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in archives[14:]:
        sidecar = old.with_suffix(old.suffix + '.sha256')
        old.unlink(missing_ok=True)
        sidecar.unlink(missing_ok=True)
    print(f'AIFILM_CONTROL_BACKUP_PASS files={len(records)} sha256={archive_sha} archive={archive.name}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
