#!/usr/bin/env python3
import contextlib, hashlib, importlib.util, io, json, os, shutil, sys, tarfile, tempfile, time, zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from control_common import load_control

BASE=Path('/home/dragon/ai-film-runtime')
CONTROL=load_control()
BACKUPS=BASE/'backups'
EXPORT=Path(CONTROL['offhost_export_root'])
REBUILD=Path(CONTROL['rebuild_root'])
SNAP=BASE/'state-snapshots'
EVID=BASE/'run-evidence/prodlike-program/failclosed-campaign'
SCRIPTS={
 'backup':BASE/'bin/verify-control-backup.py',
 'export':BASE/'bin/verify-offhost-export.py',
 'rebuild':BASE/'bin/verify-rebuild-set.py',
}

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def load(name,path):
 spec=importlib.util.spec_from_file_location('fault_'+name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def call(mod,args):
 old=sys.argv[:]; sys.argv=['verifier',*args]; out=io.StringIO(); rc=0
 try:
  with contextlib.redirect_stdout(out): rc=mod.main()
 except SystemExit as e: rc=int(e.code or 0)
 except Exception as e: rc=1; print(type(e).__name__+':'+str(e),file=out)
 finally: sys.argv=old
 return rc,out.getvalue().strip()
def latest_backup(): return max(BACKUPS.glob('control-state-*.tar.gz'),key=lambda p:p.stat().st_mtime)
def copy_backup(dst):
 dst.mkdir(mode=0o700); a=latest_backup(); s=a.with_suffix(a.suffix+'.sha256'); shutil.copy2(a,dst/a.name); shutil.copy2(s,dst/s.name); os.chmod(dst/a.name,0o600); os.chmod(dst/s.name,0o600); return dst/a.name

def rewrite_zip(path,mutator):
 with zipfile.ZipFile(path,'r') as z: members={n:z.read(n) for n in z.namelist()}
 mutator(members)
 tmp=path.with_suffix('.tmp')
 with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for n,b in members.items(): z.writestr(n,b)
 tmp.replace(path)

def case_result(name,rc,out,needle=None):
 ok=rc!=0 and (needle is None or needle in out)
 return {'case':name,'pass':ok,'returncode':rc,'output':out[-500:]}

def main():
 SNAP.mkdir(exist_ok=True,mode=0o700); results=[]
 with tempfile.TemporaryDirectory(prefix='failclosed.',dir=SNAP) as td:
  td=Path(td)
  # backup sidecar mismatch
  root=td/'backup-sidecar'; a=copy_backup(root); (a.with_suffix(a.suffix+'.sha256')).write_text('0'*64+'  '+a.name+'\n'); os.chmod(a.with_suffix(a.suffix+'.sha256'),0o600)
  m=load('b1',SCRIPTS['backup']); m.BACKUPS=root; rc,out=call(m,['--json']); results.append(case_result('backup_sidecar_hash_mismatch',rc,out,'ARCHIVE_HASH_MISMATCH'))
  # backup stale
  root=td/'backup-stale'; a=copy_backup(root); old=time.time()-31*3600; os.utime(a,(old,old)); m=load('b2',SCRIPTS['backup']); m.BACKUPS=root; rc,out=call(m,['--json']); results.append(case_result('backup_stale',rc,out,'BACKUP_STALE'))
  # export sidecar mismatch
  root=td/'export-sidecar'; shutil.copytree(EXPORT,root); target=root/CONTROL['offhost_export_name']; side=root/(target.name+'.sha256'); side.write_text('0'*64+'  '+target.name+'\n'); m=load('e1',SCRIPTS['export']); m.ROOT=root; rc,out=call(m,[]); results.append(case_result('export_sidecar_hash_mismatch',rc,out,'export-sidecar-mismatch'))
  # export stale while preserving outer integrity
  root=td/'export-stale'; shutil.copytree(EXPORT,root); target=root/CONTROL['offhost_export_name']
  def stale(mem):
   meta=json.loads(mem['OFFHOST-DR-MANIFEST.json']); meta['created_at_utc']=(datetime.now(timezone.utc)-timedelta(hours=31)).isoformat(); mem['OFFHOST-DR-MANIFEST.json']=(json.dumps(meta,indent=2,sort_keys=True)+'\n').encode()
  rewrite_zip(target,stale); (root/(target.name+'.sha256')).write_text(sha_file(target)+'  '+target.name+'\n'); m=load('e2',SCRIPTS['export']); m.ROOT=root; rc,out=call(m,[]); results.append(case_result('export_stale',rc,out,'export-stale'))
  # export inner control corruption with outer manifest/hash repaired
  root=td/'export-inner'; shutil.copytree(EXPORT,root); target=root/CONTROL['offhost_export_name']
  def inner_bad(mem):
   meta=json.loads(mem['OFFHOST-DR-MANIFEST.json']); ctrl=next(n for n in meta['files'] if n.startswith('control/') and n.endswith('.tar.gz')); raw=bytearray(mem[ctrl]); raw[len(raw)//2]^=1; mem[ctrl]=bytes(raw); meta['files'][ctrl]={'sha256':sha_bytes(mem[ctrl]),'size':len(mem[ctrl])}; mem['OFFHOST-DR-MANIFEST.json']=(json.dumps(meta,indent=2,sort_keys=True)+'\n').encode()
  rewrite_zip(target,inner_bad); (root/(target.name+'.sha256')).write_text(sha_file(target)+'  '+target.name+'\n'); m=load('e3',SCRIPTS['export']); m.ROOT=root; rc,out=call(m,[]); results.append(case_result('export_inner_control_corruption',rc,out))
  # rebuild index hash mismatch
  root=td/'rebuild-index'; shutil.copytree(REBUILD,root); idx=json.loads((root/'rebuild-index.json').read_text()); first=next(iter(idx['files'])); idx['files'][first]['sha256']='0'*64; (root/'rebuild-index.json').write_text(json.dumps(idx,indent=2,sort_keys=True)+'\n'); m=load('r1',SCRIPTS['rebuild']); m.ROOT=root; m.SNAP=td/'rsnap1'; rc,out=call(m,['--json']); results.append(case_result('rebuild_index_hash_mismatch',rc,out))
  # rebuild artifact corruption
  root=td/'rebuild-artifact'; shutil.copytree(REBUILD,root); idx=json.loads((root/'rebuild-index.json').read_text()); victim=next(n for n in idx['files'] if n!='rebuild-index.json'); p=root/victim; raw=bytearray(p.read_bytes()); raw[len(raw)//2]^=1; p.write_bytes(raw); m=load('r2',SCRIPTS['rebuild']); m.ROOT=root; m.SNAP=td/'rsnap2'; rc,out=call(m,['--json']); results.append(case_result('rebuild_artifact_corruption',rc,out))
  # unsafe authority/protected-domain flags in export
  root=td/'export-unsafe-flag'; shutil.copytree(EXPORT,root); target=root/CONTROL['offhost_export_name']
  def unsafe_flag(mem):
   meta=json.loads(mem['OFFHOST-DR-MANIFEST.json']); meta['native_authority_included']=True; mem['OFFHOST-DR-MANIFEST.json']=(json.dumps(meta,indent=2,sort_keys=True)+'\n').encode()
  rewrite_zip(target,unsafe_flag); (root/(target.name+'.sha256')).write_text(sha_file(target)+'  '+target.name+'\n'); m=load('e4',SCRIPTS['export']); m.ROOT=root; rc,out=call(m,[]); results.append(case_result('export_unsafe_authority_flag',rc,out,'unsafe-flag:native_authority_included'))

  passed=sum(r['pass'] for r in results); out={'kind':'AIFILM_P00_FAILCLOSED_CAMPAIGN','status':'PASS' if passed==len(results) else 'FAIL','timestamp_utc':datetime.now(timezone.utc).isoformat(),'passed':passed,'total':len(results),'results':results}
  EVID.mkdir(parents=True,exist_ok=True,mode=0o700); ep=EVID/'latest.json'; tmp=EVID/'.latest.json.tmp'; tmp.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); os.chmod(tmp,0o600); tmp.replace(ep); side=EVID/'latest.sha256'; side.write_text(sha_file(ep)+'  latest.json\n'); os.chmod(side,0o600)
  print(json.dumps(out,indent=2,sort_keys=True)); return 0 if passed==len(results) else 1
if __name__=='__main__': raise SystemExit(main())
