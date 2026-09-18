#!/usr/bin/env python3
"""Verify AI-FILM prodlike user-systemd deployment against a control backup."""
import argparse, hashlib, io, json, os, subprocess, sys, tarfile
from pathlib import Path, PurePosixPath

KIND='AIFILM_P00_USER_SYSTEMD_VERIFY'

def sha(data): return hashlib.sha256(data).hexdigest()

def fail(reason, **extra):
    out={'kind':KIND,'status':'FAIL','reason':reason,**extra}
    print(json.dumps(out,sort_keys=True,separators=(',',':')))
    return 1

def load_archive(path):
    with tarfile.open(path,'r:gz') as tf:
        try: raw=tf.extractfile('backup-manifest.json').read()
        except Exception as e: raise RuntimeError('MANIFEST_MISSING') from e
        m=json.loads(raw.decode('utf-8'))
        if not isinstance(m,dict) or not isinstance(m.get('files'),dict): raise RuntimeError('MANIFEST_SCHEMA')
        rows={k:v for k,v in m['files'].items() if isinstance(k,str) and k.startswith('systemd/')}
        if not rows: raise RuntimeError('SYSTEMD_ROWS_MISSING')
        archive={}
        for rel,meta in rows.items():
            if not isinstance(meta,dict) or not isinstance(meta.get('sha256'),str) or not isinstance(meta.get('size'),int):
                raise RuntimeError('SYSTEMD_ROW_SCHEMA:'+rel)
            try: data=tf.extractfile(rel).read()
            except Exception as e: raise RuntimeError('ARCHIVE_MEMBER_MISSING:'+rel) from e
            if len(data)!=meta['size'] or sha(data)!=meta['sha256']:
                raise RuntimeError('ARCHIVE_MEMBER_DRIFT:'+rel)
            archive[rel]=(meta,data)
    return rows,archive

def target_for(unit_dir, rel):
    parts=PurePosixPath(rel).parts
    if parts[0]!='systemd': raise ValueError(rel)
    if len(parts)>=4 and parts[1]=='dropins':
        return unit_dir/(parts[2]+'.d')/Path(*parts[3:])
    return unit_dir/Path(*parts[1:])

def timer_state(name):
    enabled=subprocess.run(['systemctl','--user','is-enabled',name],text=True,capture_output=True)
    active=subprocess.run(['systemctl','--user','is-active',name],text=True,capture_output=True)
    return enabled.returncode==0 and enabled.stdout.strip()=='enabled', active.returncode==0 and active.stdout.strip()=='active'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--backup-archive',required=True)
    ap.add_argument('--unit-dir',default=str(Path.home()/'.config/systemd/user'))
    ap.add_argument('--check-timers',action='store_true')
    args=ap.parse_args()
    archive_path=Path(args.backup_archive); unit_dir=Path(args.unit_dir)
    if not archive_path.is_file(): return fail('BACKUP_ARCHIVE_MISSING',backup_archive=str(archive_path))
    try: rows,_=load_archive(archive_path)
    except Exception as e: return fail(str(e))
    bad=[]; checked=0; timers=[]
    for rel,meta in sorted(rows.items()):
        p=target_for(unit_dir,rel); checked+=1
        if not p.is_file(): bad.append({'path':rel,'reason':'DEPLOYED_FILE_MISSING'}); continue
        data=p.read_bytes()
        if len(data)!=meta['size'] or sha(data)!=meta['sha256']:
            bad.append({'path':rel,'reason':'DEPLOYED_FILE_DRIFT'})
        if rel.endswith('.timer') and '/dropins/' not in rel: timers.append(PurePosixPath(rel).name)
    if bad: return fail('DEPLOYED_SYSTEMD_DRIFT',checked=checked,bad=bad)
    timer_rows=[]
    if args.check_timers:
        for name in sorted(timers):
            enabled,active=timer_state(name); timer_rows.append({'timer':name,'enabled':enabled,'active':active})
        if any(not x['enabled'] or not x['active'] for x in timer_rows):
            return fail('TIMER_STATE_DRIFT',checked=checked,timer_count=len(timers),timers=timer_rows)
    out={'kind':KIND,'status':'PASS','backup_archive':archive_path.name,'archive_sha256':sha(archive_path.read_bytes()),'unit_file_count':checked,'timer_count':len(timers),'timer_state_checked':args.check_timers,'native_execution_started':False}
    print(json.dumps(out,sort_keys=True,separators=(',',':')))
    return 0

if __name__=='__main__': raise SystemExit(main())
