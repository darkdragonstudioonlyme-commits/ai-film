#!/usr/bin/env python3
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BUNDLE=ROOT/'prodlike-dev22'
TOOL=ROOT/'tooling/verify_prodlike_dev22_control_bundle.py'
def run(bundle,*extra):
 p=subprocess.run([sys.executable,str(TOOL),'--bundle',str(bundle),*map(str,extra)],text=True,capture_output=True)
 try:o=json.loads(p.stdout.strip().splitlines()[-1])
 except Exception:raise AssertionError((p.returncode,p.stdout,p.stderr))
 return p.returncode,o
def expect(reason,mutator):
 with tempfile.TemporaryDirectory() as td:
  b=Path(td)/'bundle';shutil.copytree(BUNDLE,b);mutator(b);rc,o=run(b);assert rc==1 and o['reason']==reason,(rc,o,reason);print('PASS',reason)
def rewrite_manifest(b,rel):
 m=json.loads((b/'CONTROL_BUNDLE_MANIFEST.json').read_text());p=b/rel;m['files'][rel]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();m['files'][rel]['size']=p.stat().st_size;(b/'CONTROL_BUNDLE_MANIFEST.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
def make_deployed(b,root):
 root.mkdir(parents=True,exist_ok=True);db=root/'bin';du=root/'units';cfg=root/'config';rr=root/'release';db.mkdir();du.mkdir();cfg.mkdir();rr.mkdir()
 m=json.loads((b/'CONTROL_BUNDLE_MANIFEST.json').read_text())
 for rel,rec in m['files'].items():
  if rel=='release-control.json':
   p=cfg/'release-control.json';shutil.copy2(b/rel,p);os.chmod(p,int(rec['deploy_mode'],8))
  elif rel.startswith('scripts/'):
   p=db/rel.removeprefix('scripts/');p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(b/rel,p);os.chmod(p,int(rec['deploy_mode'],8))
  elif rel.startswith('systemd/'):
   p=du/rel.removeprefix('systemd/');p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(b/rel,p);os.chmod(p,int(rec['deploy_mode'],8))
 shutil.copy2(b/'CONTROL_BUNDLE_MANIFEST.json',cfg/'control-bundle-manifest.json')
 c=json.loads((b/'release-control.json').read_text());ident={k:c[k] for k in ('release_name','implementation_version','source_commit','source_digest','test_digest','contract_digest','package_sha256','wheel_sha256')};(rr/'runtime-manifest.json').write_text(json.dumps(ident))
 return db,du,cfg/'release-control.json',rr
def main():
 rc,o=run(BUNDLE);assert rc==0 and o['status']=='PASS' and o['file_count']==64 and o['timer_count']==11;print('PASS valid_source_bundle')
 expect('SOURCE_BYTE_DRIFT',lambda b:(b/'scripts/runtime-health.py').write_text((b/'scripts/runtime-health.py').read_text()+'# drift\n'))
 expect('SOURCE_MEMBER_SET',lambda b:(b/'extra.txt').write_text('x'))
 def stale(b):
  p=b/'scripts/runtime-health.py';p.write_text(p.read_text()+'# dev21\n');rewrite_manifest(b,'scripts/runtime-health.py')
 expect('FORBIDDEN_STALE_IDENTITY',stale)
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);b=root/'bundle';shutil.copytree(BUNDLE,b);db,du,dc,rr=make_deployed(b,root/'deployed');rc,o=run(b,'--deployed-bin',db,'--deployed-unit-dir',du,'--deployed-config',dc,'--release-root',rr);assert rc==0 and o['deployed_checked'];print('PASS valid_deployed_bytes_and_modes')
  p=db/'runtime-health.py';os.chmod(p,0o755);rc,o=run(b,'--deployed-bin',db,'--deployed-unit-dir',du,'--deployed-config',dc,'--release-root',rr);assert rc==1 and o['reason']=='DEPLOYED_MODE_DRIFT';print('PASS deployed_mode_drift')
 print('PRODLIKE_DEV22_CONTROL_BUNDLE_TEST_PASS 6 cases')
if __name__=='__main__':main()
