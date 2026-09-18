#!/usr/bin/env python3
import hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

BASE = Path('/home/dragon/ai-film-runtime')
CONTROL=load_control()
RELEASE = Path(CONTROL['runtime_root'])
HEALTH = BASE / 'health'
AUTH = Path(CONTROL['authority_evidence_root'])
VERIFY = BASE / 'bin' / 'verify-current'
BACKUP_VERIFY = BASE / 'bin' / 'verify-control-backup.py'
HOST_MIRROR_VERIFY = BASE / 'bin' / 'verify-host-mirror.py'
REBUILD_VERIFY = BASE / 'bin' / 'verify-rebuild-set.py'
OFFHOST_EXPORT_VERIFY = BASE / 'bin' / 'verify-offhost-export.py'
LEDGER_VERIFY = BASE / 'bin' / 'verify-operational-evidence.py'
DR_REHEARSAL_EVID = BASE / 'run-evidence/prodlike-program/recovery-rehearsal/latest.json'
DR_REHEARSAL_MAX_AGE_SECONDS = 30 * 3600
FAILCLOSED_EVID = BASE / 'run-evidence/prodlike-program/failclosed-campaign/latest.json'
FAILCLOSED_MAX_AGE_SECONDS = 8 * 24 * 3600
UNITS = [
    CONTROL['verify_timer'],
    'aifilm-p00-v02-authority-watch.timer',
    'aifilm-p00-runtime-health.timer',
    'aifilm-p00-control-backup.timer',
    'aifilm-p00-recovery-verify.timer',
    'aifilm-p00-host-mirror.timer',
    'aifilm-p00-rebuild-verify.timer',
    'aifilm-p00-offhost-export.timer',
    'aifilm-p00-dr-rehearsal.timer',
    'aifilm-p00-failclosed-campaign.timer',
    'aifilm-p00-evidence-ledger.timer',
]
EXPECTED_TIMEOUTS = {
    CONTROL['verify_service']: '5min',
    'aifilm-p00-v02-authority-watch.service': '2min',
    'aifilm-p00-runtime-health.service': '5min',
    'aifilm-p00-control-backup.service': '10min',
    'aifilm-p00-recovery-verify.service': '10min',
    'aifilm-p00-host-mirror.service': '5min',
    'aifilm-p00-rebuild-verify.service': '10min',
    'aifilm-p00-offhost-export.service': '10min',
    'aifilm-p00-dr-rehearsal.service': '10min',
    'aifilm-p00-failclosed-campaign.service': '10min',
    'aifilm-p00-evidence-ledger.service': '2min',
}

SERVICE_FRESHNESS = {
    CONTROL['verify_service']: (900, 60, 120),
    'aifilm-p00-v02-authority-watch.service': (300, 30, 120),
    'aifilm-p00-control-backup.service': (86400, 300, 600),
    'aifilm-p00-recovery-verify.service': (21600, 120, 180),
    'aifilm-p00-host-mirror.service': (7200, 300, 1200),
    'aifilm-p00-rebuild-verify.service': (43200, 300, 300),
    'aifilm-p00-offhost-export.service': (21600, 120, 1200),
    'aifilm-p00-dr-rehearsal.service': (86400, 600, 1800),
    'aifilm-p00-failclosed-campaign.service': (604800, 1800, 2700),
    'aifilm-p00-evidence-ledger.service': (86400, 300, 1800),
}
FRESHNESS_STARTUP_GRACE_SECONDS = 600
OPS = [
    BASE / 'bin/aifilm-p00', BASE / 'bin/activate-release', BASE / 'bin/verify-current',
    BASE / 'bin/runtime-health.py', BASE / 'bin/control_common.py', BASE / 'bin/backup-control-state.py',
    BASE / 'bin/verify-control-backup.py', BASE / 'bin/verify-recovery-state',
    BASE / 'bin/mirror-control-backup.py', BASE / 'bin/verify-host-mirror.py',
    BASE / 'bin/verify-rebuild-set.py', BASE / 'bin/build-offhost-export.py',
    BASE / 'bin/verify-offhost-export.py', BASE / 'bin/run-failclosed-campaign.py',
    BASE / 'bin/run-dr-recovery-rehearsal.py', BASE / 'bin/archive-operational-evidence.py',
    BASE / 'bin/verify-operational-evidence.py',
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def run(args):
    env = os.environ.copy()
    env.setdefault('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')
    p = subprocess.run(args, text=True, capture_output=True, env=env)
    return p.returncode, p.stdout.strip(), p.stderr.strip()
def mode(path):
    return oct(path.stat().st_mode & 0o777)[2:]

def timer_state(name):
    erc, enabled, _ = run(['systemctl', '--user', 'is-enabled', name])
    arc, active, _ = run(['systemctl', '--user', 'is-active', name])
    return {'enabled': enabled, 'active': active,
            'ok': erc == 0 and arc == 0 and enabled == 'enabled' and active == 'active'}


def timeout_state(name, expected):
    rc, value, _ = run(['systemctl', '--user', 'show', '-p', 'TimeoutStartUSec', '--value', name])
    return {'effective': value, 'expected': expected, 'ok': rc == 0 and value == expected}

def unit_result(name):
    rc, value, _ = run(['systemctl', '--user', 'show', '-p', 'Result', '--value', name])
    return {'result': value, 'ok': rc == 0 and value == 'success'}

def service_freshness(name, spec):
    cadence, accuracy, on_boot = spec
    rc, raw, _ = run(['systemctl', '--user', 'show', '-p', 'ExecMainExitTimestampMonotonic', '--value', name])
    try:
        last_us = int(raw or '0')
    except ValueError:
        last_us = 0
    try:
        uptime = float(Path('/proc/uptime').read_text().split()[0])
    except Exception:
        uptime = 0.0
    max_age = cadence + max(2 * accuracy, 300)
    if rc != 0:
        ok = False; age = None; state = 'QUERY_FAILED'
    elif last_us > 0:
        age = max(0.0, uptime - last_us / 1_000_000.0)
        ok = age <= max_age
        state = 'FRESH' if ok else 'STALE'
    else:
        age = None
        deadline = on_boot + accuracy + FRESHNESS_STARTUP_GRACE_SECONDS
        ok = uptime <= deadline
        state = 'BOOT_GRACE' if ok else 'NEVER_COMPLETED_THIS_BOOT'
    return {'state': state, 'age_seconds': round(age, 1) if age is not None else None,
            'max_age_seconds': max_age, 'cadence_seconds': cadence,
            'accuracy_seconds': accuracy, 'on_boot_seconds': on_boot, 'ok': ok}

def resource_state(name):
    rc, out, _ = run(['systemctl','--user','show',name,'-p','MemoryMax','-p','TasksMax','-p','MemoryAccounting','-p','CPUAccounting','-p','TasksAccounting'])
    vals=dict(line.split('=',1) for line in out.splitlines() if '=' in line)
    ok=(rc==0 and vals.get('MemoryMax')==str(256*1024*1024) and vals.get('TasksMax')=='128' and
        vals.get('MemoryAccounting')=='yes' and vals.get('CPUAccounting')=='yes' and vals.get('TasksAccounting')=='yes')
    return {**vals,'ok':ok}

def main():
    HEALTH.mkdir(parents=True, exist_ok=True, mode=0o700)
    current = (BASE / 'current').resolve()
    vrc, vout, verr = run([str(VERIFY)])
    brc, bout, berr = run([str(BACKUP_VERIFY), '--json'])
    mrc, mout, merr = run([str(HOST_MIRROR_VERIFY)])
    rrc, rout, rerr = run([str(REBUILD_VERIFY), '--json'])
    erc, eout, eerr = run([str(OFFHOST_EXPORT_VERIFY), '--json'])
    lrc, lout, lerr = run([str(LEDGER_VERIFY)])
    try:
        backup_verify = json.loads(bout) if bout else {}
    except json.JSONDecodeError:
        backup_verify = {}
    try:
        rebuild_verify = json.loads(rout) if rout else {}
    except json.JSONDecodeError:
        rebuild_verify = {}
    try:
        export_verify = json.loads(eout) if eout else {}
    except json.JSONDecodeError:
        export_verify = {}
    try:
        ledger_verify = json.loads(lout) if lout else {}
    except json.JSONDecodeError:
        ledger_verify = {}
    rehearsal = json.loads(DR_REHEARSAL_EVID.read_text(encoding='utf-8')) if DR_REHEARSAL_EVID.is_file() else {}
    campaign = json.loads(FAILCLOSED_EVID.read_text(encoding='utf-8')) if FAILCLOSED_EVID.is_file() else {}
    try:
        rehearsal_age = max(0, int((datetime.now(timezone.utc)-datetime.fromisoformat(rehearsal.get('timestamp_utc'))).total_seconds())) if rehearsal else None
    except Exception:
        rehearsal_age = None
    try:
        campaign_age = max(0, int((datetime.now(timezone.utc)-datetime.fromisoformat(campaign.get('timestamp_utc'))).total_seconds())) if campaign else None
    except Exception:
        campaign_age = None
    manifest_path = RELEASE / 'runtime-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    auth_path = AUTH / 'latest.json'
    auth = json.loads(auth_path.read_text(encoding='utf-8')) if auth_path.is_file() else {}
    auth_sha = sha256(auth_path) if auth_path.is_file() else None
    ready_flag = AUTH / 'READY_TO_ADVANCE.flag'
    flag_value = ready_flag.read_text(encoding='utf-8').strip() if ready_flag.is_file() else None
    auth_status = auth.get('status')
    auth_signal_ok = ((auth_status == 'BLOCKED' and not ready_flag.exists()) or
                      (auth_status == 'READY_TO_ADVANCE' and flag_value == auth_sha))
    timers = {name: timer_state(name) for name in UNITS}
    timeouts = {name: timeout_state(name, expected) for name, expected in EXPECTED_TIMEOUTS.items()}
    service_freshness_state = {name: service_freshness(name, spec) for name, spec in SERVICE_FRESHNESS.items()}
    job_results = {name: unit_result(name) for name in [
        CONTROL['verify_service'], 'aifilm-p00-v02-authority-watch.service',
        'aifilm-p00-control-backup.service', 'aifilm-p00-recovery-verify.service',
        'aifilm-p00-host-mirror.service', 'aifilm-p00-rebuild-verify.service',
        'aifilm-p00-offhost-export.service', 'aifilm-p00-dr-rehearsal.service',
        'aifilm-p00-failclosed-campaign.service', 'aifilm-p00-evidence-ledger.service']}
    resources = {name: resource_state(name) for name in EXPECTED_TIMEOUTS}
    ops = {str(p): {'mode': mode(p), 'sha256': sha256(p),
                    'owner_uid': p.stat().st_uid,
                    'not_group_or_other_writable': (p.stat().st_mode & 0o022) == 0}
           for p in OPS}
    disk = os.statvfs(BASE)
    free_bytes = disk.f_bavail * disk.f_frsize
    checks = {
        'current_release_matches_control': current == RELEASE,
        'verify_current': vrc == 0 and 'PRODLIKE_RUNTIME_VERIFY_PASS' in vout,
        'latest_backup_verified_fresh': brc == 0 and backup_verify.get('status') == 'PASS',
        'host_mirror_verified_fresh': mrc == 0 and 'AIFILM_HOST_MIRROR_VERIFY_PASS' in mout,
        'rebuild_set_verified': rrc == 0 and rebuild_verify.get('status') == 'PASS',
        'offhost_export_verified_fresh': erc == 0 and export_verify.get('status') == 'PASS',
        'evidence_ledger_verified_fresh': lrc == 0 and ledger_verify.get('status') == 'PASS',
        'full_dr_rehearsal_fresh': rehearsal.get('status') == 'PASS' and rehearsal_age is not None and rehearsal_age <= DR_REHEARSAL_MAX_AGE_SECONDS,
        'failclosed_campaign_fresh': campaign.get('status') == 'PASS' and campaign.get('passed') == campaign.get('total') and campaign_age is not None and campaign_age <= FAILCLOSED_MAX_AGE_SECONDS,
        'manifest_runtime_verify': manifest.get('runtime_verify') == 'PASS',
        'manifest_native_execution_false': manifest.get('native_execution_started') is False,
        'manifest_native_authority_false': manifest.get('native_lab_authority') is False,
        'manifest_release_identity_matches_control': all([manifest.get('release_name')==CONTROL['release_name'], manifest.get('implementation_version')==CONTROL['implementation_version'], manifest.get('source_commit')==CONTROL['source_commit'], manifest.get('source_digest')==CONTROL['source_digest'], manifest.get('test_digest')==CONTROL['test_digest'], manifest.get('contract_digest')==CONTROL['contract_digest'], manifest.get('package_sha256')==CONTROL['package_sha256'], manifest.get('wheel_sha256')==CONTROL['wheel_sha256']]),
        'authority_signal_consistent': auth_signal_ok,
        'release_history_mode_600': mode(BASE / 'release-history.log') == '600',
        'native_inventory_mode_600': mode(RELEASE / 'evidence/native-inventory.json') == '600',
        'timers_ok': all(v['ok'] for v in timers.values()),
        'service_timeouts_ok': all(v['ok'] for v in timeouts.values()),
        'service_execution_freshness_ok': all(v['ok'] for v in service_freshness_state.values()),
        'service_resource_bounds_ok': all(v['ok'] for v in resources.values()),
        'periodic_jobs_last_result_success': all(v['ok'] for v in job_results.values()),
        'operational_scripts_hardened': all(v['owner_uid'] == os.getuid() and v['not_group_or_other_writable'] for v in ops.values()),
        'disk_free_over_5gib': free_bytes >= 5 * 1024**3,
    }
    status = 'PASS' if all(checks.values()) else 'FAIL'
    out = {
        'schema_version': 1,
        'kind': 'AIFILM_P00_PRODLIKE_HEALTH',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'current_release': str(current),
        'runtime_manifest_sha256': sha256(manifest_path),
        'app_manifest_sha256': manifest.get('app_manifest_sha256'),
        'authority_status': auth_status,
        'authority_reason': auth.get('reason'),
        'authority_latest_sha256': auth_sha,
        'ready_flag_present': ready_flag.exists(),
        'native_execution_started': auth.get('native_execution_started', False),
        'timers': timers,
        'service_timeouts': timeouts,
        'service_execution_freshness': service_freshness_state,
        'service_resources': resources,
        'periodic_job_results': job_results,
        'operational_scripts': ops,
        'disk_free_bytes': free_bytes,
        'checks': checks,
        'verify_stdout': vout,
        'verify_stderr': verr,
        'backup_verify': backup_verify,
        'backup_verify_stderr': berr,
        'host_mirror_verify_stdout': mout,
        'host_mirror_verify_stderr': merr,
        'rebuild_verify': rebuild_verify,
        'rebuild_verify_stderr': rerr,
        'offhost_export_verify': export_verify,
        'offhost_export_verify_stderr': eerr,
        'evidence_ledger_verify': ledger_verify,
        'evidence_ledger_verify_stderr': lerr,
        'full_dr_rehearsal': rehearsal,
        'full_dr_rehearsal_age_seconds': rehearsal_age,
        'failclosed_campaign': campaign,
        'failclosed_campaign_age_seconds': campaign_age,
    }
    tmp = HEALTH / '.latest.json.tmp'
    tmp.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.chmod(tmp, 0o600)
    tmp.replace(HEALTH / 'latest.json')
    digest = sha256(HEALTH / 'latest.json')
    (HEALTH / 'latest.sha256').write_text(digest + '  latest.json\n', encoding='utf-8')
    os.chmod(HEALTH / 'latest.sha256', 0o600)
    print(f'AIFILM_RUNTIME_HEALTH_{status} authority={auth_status} sha256={digest}')
    return 0 if status == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
