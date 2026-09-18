#!/usr/bin/env python3
import hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from control_common import load_control

BASE = Path('/home/dragon/ai-film-runtime')
HEALTH = BASE / 'health/latest.json'
CONTROL=load_control()
AUTH = Path(CONTROL['authority_evidence_root']) / 'latest.json'
BACKUP_VERIFY = BASE / 'bin/verify-control-backup.py'
MIRROR_VERIFY = BASE / 'bin/verify-host-mirror.py'
REBUILD_VERIFY = BASE / 'bin/verify-rebuild-set.py'
OFFHOST_EXPORT_VERIFY = BASE / 'bin/verify-offhost-export.py'
RECOVERY_VERIFY = BASE / 'bin/verify-recovery-state'

def run(args):
    env=os.environ.copy(); env.setdefault('XDG_RUNTIME_DIR',f'/run/user/{os.getuid()}')
    p=subprocess.run(args,text=True,capture_output=True,env=env)
    return p.returncode,p.stdout.strip(),p.stderr.strip()

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    health=read_json(HEALTH) if HEALTH.is_file() else {}
    auth=read_json(AUTH) if AUTH.is_file() else {}
    checks={}
    checks['health_pass']=health.get('status')=='PASS'
    checks['authority_present']=bool(auth)
    checks['native_execution_false']=auth.get('native_execution_started') is False
    brc,bout,berr=run([str(BACKUP_VERIFY),'--json'])
    try: backup=json.loads(bout) if bout else {}
    except json.JSONDecodeError: backup={}
    mrc,mout,merr=run([str(MIRROR_VERIFY)])
    rrc,rout,rerr=run([str(REBUILD_VERIFY),'--json'])
    try: rebuild=json.loads(rout) if rout else {}
    except json.JSONDecodeError: rebuild={}
    crc,cout,cerr=run([str(RECOVERY_VERIFY)])
    erc,eout,eerr=run([str(OFFHOST_EXPORT_VERIFY),'--json'])
    try: export=json.loads(eout) if eout else {}
    except json.JSONDecodeError: export={}
    checks['local_backup_pass']=brc==0 and backup.get('status')=='PASS'
    checks['host_mirror_pass']=mrc==0 and 'AIFILM_HOST_MIRROR_VERIFY_PASS' in mout
    checks['rebuild_set_pass']=rrc==0 and rebuild.get('status')=='PASS'
    checks['recovery_pass']=crc==0 and 'AIFILM_RECOVERY_STATE_VERIFY_PASS' in cout
    checks['offhost_export_pass']=erc==0 and export.get('status')=='PASS'
    op_ready=all(checks.values())
    auth_status=auth.get('status')
    if auth_status=='READY_TO_ADVANCE' and auth.get('ready_to_advance') is True:
        native_gate='AUTHORITY_READY_FOR_REVIEWED_TRANSITION'
    elif auth_status=='BLOCKED':
        native_gate='BLOCKED_LOCAL_OPERATOR_AUTHORITY'
    else:
        native_gate='BLOCKED_AUTHORITY_STATE_UNKNOWN'
    overall='READY_NON_NATIVE_PRODLIKE_OPERATIONS' if op_ready else 'PRODLIKE_DEGRADED'
    out={
        'schema_version':1,'kind':'AIFILM_P00_OPERATOR_STATUS',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'production_like_status':overall,'native_gate':native_gate,
        'authority_status':auth_status,
        'authority_reason':auth.get('reason'),
        'ready_to_advance':bool(auth.get('ready_to_advance')),
        'native_execution_started':bool(auth.get('native_execution_started')),
        'current_release':health.get('current_release'),
        'runtime_manifest_sha256':health.get('runtime_manifest_sha256'),
        'health_snapshot_sha256':sha256(HEALTH) if HEALTH.is_file() else None,
        'health_timestamp_utc':health.get('timestamp_utc'),
        'backup':backup,
        'host_mirror_verify':mout,
        'rebuild':rebuild,
        'recovery_verify':cout,
        'offhost_export':export,
        'checks':checks,
    }
    json_mode='--json' in sys.argv
    if json_mode:
        print(json.dumps(out,sort_keys=True,separators=(',',':')))
    else:
        print(f"production_like={overall}")
        print(f"native_gate={native_gate}")
        print(f"authority={auth_status or 'UNKNOWN'} reason={auth.get('reason') or 'NONE'}")
        print(f"native_execution_started={str(bool(auth.get('native_execution_started'))).lower()}")
        print('checks=' + ','.join(f"{k}:{'PASS' if v else 'FAIL'}" for k,v in sorted(checks.items())))
    return 0 if op_ready else 1

if __name__=='__main__':
    raise SystemExit(main())
