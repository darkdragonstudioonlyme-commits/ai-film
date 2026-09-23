#!/usr/bin/env python3
"""Static user-systemd byte verifier for a candidate-bound control backup. Never calls systemctl."""
from __future__ import annotations
import argparse,hashlib,json,tarfile
from pathlib import Path
from v02_candidate_profile import ProfileError,load_profile

class SystemdError(RuntimeError):pass
def req(c,r):
    if not c:raise SystemdError(r)
def sha(b):return hashlib.sha256(b).hexdigest()
def deployed_target(unit_dir,rel):
    parts=Path(rel).parts;req(parts and parts[0]=='systemd','SYSTEMD_PATH')
    if len(parts)>=3 and parts[1].endswith('.service.d'):return unit_dir/parts[1]/Path(*parts[2:])
    return unit_dir/Path(*parts[1:])

def verify(binding,binding_sha256,backup_archive,unit_dir):
    profile,profile_sha=load_profile(binding,binding_sha256);arc=Path(backup_archive);u=Path(unit_dir)
    with tarfile.open(arc,'r:gz') as tf:
        f=tf.extractfile('backup-manifest.json');req(f is not None,'MANIFEST_MISSING');m=json.loads(f.read())
        req(m.get('candidate_id')==profile['candidate_id'] and m.get('candidate_binding_sha256')==profile_sha,'BACKUP_CANDIDATE')
        files=m.get('files');req(type(files) is dict,'MANIFEST_SCHEMA');rows={k:v for k,v in files.items() if isinstance(k,str) and k.startswith('systemd/')}
        req(rows,'SYSTEMD_ROWS_MISSING')
        for rel,rec in rows.items():
            f=tf.extractfile(rel);req(f is not None,'ARCHIVE_MEMBER_MISSING:'+rel);raw=f.read()
            req(len(raw)==rec.get('size') and sha(raw)==rec.get('sha256'),'ARCHIVE_MEMBER_DRIFT:'+rel)
            p=deployed_target(u,rel);req(p.is_file() and p.read_bytes()==raw,'DEPLOYED_SYSTEMD_DRIFT:'+rel)
    timers=sum(1 for x in rows if x.endswith('.timer'))
    return {'kind':'AIFILM_P00_USER_SYSTEMD_VERIFY_V2','status':'PASS','candidate_id':profile['candidate_id'],
            'candidate_binding_sha256':profile_sha,'unit_file_count':len(rows),'timer_count':timers,
            'live_systemd_checked':False,'native_execution_started':False}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True);ap.add_argument('--backup-archive',required=True);ap.add_argument('--unit-dir',required=True);a=ap.parse_args()
    try:o=verify(a.binding,a.binding_sha256,a.backup_archive,a.unit_dir);rc=0
    except (ProfileError,SystemdError,OSError,ValueError,json.JSONDecodeError,tarfile.TarError) as e:o={'kind':'AIFILM_P00_USER_SYSTEMD_VERIFY_V2','status':'FAIL','reason':str(e),'live_systemd_checked':False,'native_execution_started':False};rc=1
    print(json.dumps(o,sort_keys=True,separators=(',',':')));return rc
if __name__=='__main__':raise SystemExit(main())
