import hashlib,importlib.util,json,os,shutil,tempfile,unittest
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOL))
from v02_candidate_profile import canonical
def load(name,file):
 s=importlib.util.spec_from_file_location(name,TOOL/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
build=load('build','build_prodlike_control_bundle-v2.py');verify=load('verify','verify_prodlike_control_bundle-v2.py')
class BundleTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.r=Path(self.td.name)
  self.p={'authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','build_digest':'1'*64,'candidate_id':'11111111-2222-4333-8444-555555555555','code_review_record':'reviews/x.md','contract_digest':'3'*64,'implementation_version':'0.1.0.dev99','package_sha256':'4'*64,'schema_version':1,'source_commit':'a'*40,'status':'CANDIDATE_BOUND','test_review_record':'test-governance/x.md','test_set_digest':'2'*64,'wheel_sha256':'5'*64}
  self.binding=self.r/'b.json';self.binding.write_bytes(canonical(self.p)+b'\n');self.bsha=hashlib.sha256(self.binding.read_bytes()).hexdigest()
  self.rm=self.r/'runtime.json';self.rm.write_text(json.dumps({'candidate_id':self.p['candidate_id'],'candidate_binding_sha256':self.bsha,'implementation_version':self.p['implementation_version'],'source_commit':self.p['source_commit'],'source_digest':self.p['build_digest'],'test_digest':self.p['test_set_digest'],'contract_digest':self.p['contract_digest'],'package_sha256':self.p['package_sha256'],'wheel_sha256':self.p['wheel_sha256']}))
 def tearDown(self):self.td.cleanup()
 def make(self):
  out=self.r/'bundle';res=build.build(self.binding,self.bsha,self.rm,TOOL/'prodlike_control_templates_v2.json',out,'/runtime/dev99','/rebuild/dev99','/backup','/offhost','/authority/dev99');return out,res
 def test_build_and_verify_source(self):
  out,res=self.make();self.assertEqual(res['file_count'],64);v=verify.verify(self.binding,self.bsha,out,self.rm);self.assertEqual(v['status'],'PASS');self.assertEqual(v['timer_count'],11);self.assertFalse(v['live_systemd_checked'])
 def test_source_byte_and_mode_drift_rejected(self):
  out,_=self.make();p=out/'scripts/runtime-health.py';p.write_text(p.read_text()+'# drift\n')
  with self.assertRaisesRegex(Exception,'SOURCE_BYTE_DRIFT'):verify.verify(self.binding,self.bsha,out,self.rm)
  shutil.rmtree(out);out,_=self.make();p=out/'scripts/runtime-health.py';os.chmod(p,0o755)
  with self.assertRaisesRegex(Exception,'SOURCE_MODE_DRIFT'):verify.verify(self.binding,self.bsha,out,self.rm)
 def test_template_stale_identity_rejected(self):
  x=json.loads((TOOL/'prodlike_control_templates_v2.json').read_text());x['files'][0]['content']+='dev22';x['files'][0]['sha256']=hashlib.sha256(x['files'][0]['content'].encode()).hexdigest();p=self.r/'bad.json';p.write_text(json.dumps(x))
  with self.assertRaisesRegex(Exception,'TEMPLATE_STALE_IDENTITY'):build.load_templates(p)
 def test_extra_member_rejected(self):
  out,_=self.make();(out/'extra.txt').write_text('x')
  with self.assertRaisesRegex(Exception,'SOURCE_MEMBER_SET'):verify.verify(self.binding,self.bsha,out,self.rm)
 def test_deployed_mixed_candidate_rejected(self):
  out,_=self.make();db=self.r/'bin';du=self.r/'units';cfg=self.r/'release-control.json';rr=self.r/'release';db.mkdir();du.mkdir();rr.mkdir()
  m=json.loads((out/'CONTROL_BUNDLE_MANIFEST.json').read_text())
  for rel,rec in m['files'].items():
   if rel=='release-control.json':shutil.copy2(out/rel,cfg);os.chmod(cfg,0o600)
   elif rel.startswith('scripts/'):
    p=db/rel.removeprefix('scripts/');p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/rel,p);os.chmod(p,int(rec['deploy_mode'],8))
   elif rel.startswith('systemd/'):
    parts=Path(rel).parts;p=du/Path(*parts[1:]);p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/rel,p);os.chmod(p,int(rec['deploy_mode'],8))
  bad={'candidate_id':'other'};(rr/'runtime-manifest.json').write_text(json.dumps(bad))
  with self.assertRaises(Exception):verify.verify(self.binding,self.bsha,out,None,db,du,cfg,rr)
if __name__=='__main__':unittest.main()
