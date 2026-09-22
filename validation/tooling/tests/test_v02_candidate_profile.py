import hashlib,json,tempfile,unittest
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOL))
from v02_candidate_profile import ProfileError,canonical,load_profile
BASE={'authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','build_digest':'1'*64,'candidate_id':'acf18da3-4969-451c-8a4b-a7e46ad89c98','code_review_record':'reviews/code.md','contract_digest':'2'*64,'implementation_version':'0.1.0.dev23','package_sha256':'3'*64,'schema_version':1,'source_commit':'a'*40,'status':'CANDIDATE_BOUND','test_review_record':'test-governance/review.md','test_set_digest':'4'*64,'wheel_sha256':'5'*64}
class ProfileTests(unittest.TestCase):
 def make(self,v=BASE,raw=None):
  td=tempfile.TemporaryDirectory();p=Path(td.name)/'b.json';data=raw if raw is not None else canonical(v)+b'\n';p.write_bytes(data);return td,p,hashlib.sha256(data).hexdigest()
 def test_exact_canonical_binding(self):
  td,p,h=self.make();self.addCleanup(td.cleanup);v,actual=load_profile(p,h);self.assertEqual(v['source_commit'],'a'*40);self.assertEqual(actual,h)
 def test_wrong_hash_rejected(self):
  td,p,h=self.make();self.addCleanup(td.cleanup)
  with self.assertRaisesRegex(ProfileError,'BINDING_SHA256_MISMATCH'):load_profile(p,'0'*64)
 def test_noncanonical_rejected(self):
  td,p,h=self.make(raw=json.dumps(BASE,indent=2).encode());self.addCleanup(td.cleanup)
  with self.assertRaisesRegex(ProfileError,'BINDING_NOT_CANONICAL'):load_profile(p,h)
 def test_bool_schema_rejected(self):
  v=dict(BASE);v['schema_version']=True;td,p,h=self.make(v);self.addCleanup(td.cleanup)
  with self.assertRaisesRegex(ProfileError,'BINDING_VERSION_STATUS'):load_profile(p,h)
 def test_wrong_candidate_fields_rejected(self):
  for key,val,reason in [('source_commit','x','BINDING_SOURCE_COMMIT'),('build_digest','x','BINDING_HASH'),('authority_model','OTHER','BINDING_AUTHORITY_MODEL')]:
   v=dict(BASE);v[key]=val;td,p,h=self.make(v);self.addCleanup(td.cleanup)
   with self.assertRaisesRegex(ProfileError,reason):load_profile(p,h)
if __name__=='__main__':unittest.main()
