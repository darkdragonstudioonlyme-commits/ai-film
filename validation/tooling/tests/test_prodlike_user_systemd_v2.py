import hashlib,io,json,tarfile,tempfile,unittest
from pathlib import Path
import sys
TOOL=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOL))
from v02_candidate_profile import canonical
import importlib.util
s=importlib.util.spec_from_file_location('v',TOOL/'verify_prodlike_user_systemd-v2.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def h(b):return hashlib.sha256(b).hexdigest()
class SystemdTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.r=Path(self.td.name);self.p={'authority_model':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','build_digest':'1'*64,'candidate_id':'11111111-2222-4333-8444-555555555555','code_review_record':'r','contract_digest':'3'*64,'implementation_version':'0.1.0.dev99','package_sha256':'4'*64,'schema_version':1,'source_commit':'a'*40,'status':'CANDIDATE_BOUND','test_review_record':'t','test_set_digest':'2'*64,'wheel_sha256':'5'*64};self.b=self.r/'b.json';self.b.write_bytes(canonical(self.p)+b'\n');self.bs=hashlib.sha256(self.b.read_bytes()).hexdigest()
 def tearDown(self):self.td.cleanup()
 def fixture(self,candidate=None,drift_archive=False):
  files={'systemd/a.service':b'A','systemd/a.timer':b'T','systemd/a.service.d/resources.conf':b'R'};m={'candidate_id':candidate or self.p['candidate_id'],'candidate_binding_sha256':self.bs,'files':{k:{'sha256':h(x),'size':len(x)} for k,x in files.items()}};arc=self.r/('x'+str(len(list(self.r.glob('*.gz'))))+'.tar.gz')
  with tarfile.open(arc,'w:gz') as tf:
   raw=json.dumps(m).encode();ti=tarfile.TarInfo('backup-manifest.json');ti.size=len(raw);tf.addfile(ti,io.BytesIO(raw))
   for k,x in files.items():
    actual=(b'X' if drift_archive and k.endswith('.timer') else x);ti=tarfile.TarInfo(k);ti.size=len(actual);tf.addfile(ti,io.BytesIO(actual))
  u=self.r/('u'+str(len(list(self.r.glob('u*')))));u.mkdir()
  for k,x in files.items():
   parts=Path(k).parts;p=u/Path(*parts[1:]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(x)
  return arc,u
 def test_static_verify_no_live_systemd(self):
  arc,u=self.fixture();o=v.verify(self.b,self.bs,arc,u);self.assertEqual(o['status'],'PASS');self.assertFalse(o['live_systemd_checked'])
 def test_candidate_and_archive_drift_rejected(self):
  arc,u=self.fixture(candidate='other')
  with self.assertRaisesRegex(Exception,'BACKUP_CANDIDATE'):v.verify(self.b,self.bs,arc,u)
  arc,u=self.fixture(drift_archive=True)
  with self.assertRaisesRegex(Exception,'ARCHIVE_MEMBER_DRIFT'):v.verify(self.b,self.bs,arc,u)
 def test_deployed_drift_rejected(self):
  arc,u=self.fixture();(u/'a.timer').write_text('drift')
  with self.assertRaisesRegex(Exception,'DEPLOYED_SYSTEMD_DRIFT'):v.verify(self.b,self.bs,arc,u)
if __name__=='__main__':unittest.main()
