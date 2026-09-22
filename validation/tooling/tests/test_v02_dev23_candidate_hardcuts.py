import hashlib,json,subprocess,unittest
from pathlib import Path
TOOL=Path(__file__).resolve().parents[1]
SUCCESSORS=['v02_candidate_profile.py','v02-authority-intake-v2.py','v02-authority-preflight-v2.py','materialize-v02-native-policy-v2.py','pre-v03-authority-stage-v2.sh','watch-v02-authority-v2.sh','verify-lab-artifact-seal-v2.py','build_lab_payload-v2.py','v03_binding_producer_common.py','v02b-authority-graph-compiler.py','verify-v03-binding-producer.py','v03-fixture-preparation-controller.py','update-v03-native-policy.py','materialize-v03-late-proof.py']
HIST=['v02-authority-intake.py','v02-authority-preflight.py','materialize-v02-native-policy.py','pre-v03-authority-stage.sh','watch-v02-authority.sh','verify-lab-artifact-seal.py','build_lab_dev22_payload.py','V02_TOOLING_MANIFEST.json','approval-envelope.template.json','AUTHORITY_INBOX_README.txt']
class Hardcuts(unittest.TestCase):
 def test_no_dev22_candidate_defaults_or_native_mutation(self):
  banned=['6f895394-e0b4-5434-bebc-79ee4e576282','4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384','/local-authority/dev22/inbox','winreg.SetValue','wsl.exe --import','wsl.exe --unregister']
  for f in SUCCESSORS:
   text=(TOOL/f).read_text()
   for b in banned:self.assertNotIn(b,text,f'{f}:{b}')
 def test_historical_dev22_files_unmodified_from_validation_base(self):
  root=TOOL.parents[1];base='43c9a687ad3a1f778328f5d1587d789fbb380fd8'
  for f in HIST:self.assertEqual(subprocess.run(['git','-C',str(root),'diff','--quiet',base,'--','validation/tooling/'+f]).returncode,0,f)
 def test_shell_successors_explicit_and_non_native(self):
  for f in ['pre-v03-authority-stage-v2.sh','watch-v02-authority-v2.sh']:
   t=(TOOL/f).read_text();self.assertIn('--binding',t);self.assertIn('--binding-sha256',t);self.assertNotIn('wsl.exe',t);self.assertNotIn('sudo ',t)
 def test_dev23_tooling_manifest_binds_all_dependencies(self):
  m=json.loads((TOOL/'V02_TOOLING_MANIFEST_DEV23.json').read_text())
  self.assertEqual(m['candidate_binding_sha256'],hashlib.sha256((TOOL/'dev23-candidate-binding.json').read_bytes()).hexdigest())
  trust=json.loads((TOOL/'local-operator-trust-anchor.json').read_text())
  self.assertEqual(m['local_trust_key_id'],trust['key_id']);self.assertEqual(m['local_trust_public_key_sha256'],trust['public_key_sha256'])
  b=json.loads((TOOL/'dev23-candidate-binding.json').read_text());self.assertEqual((m['source_content_digest'],m['test_content_digest'],m['contract_digest'],m['package_sha256'],m['wheel_sha256']),(b['build_digest'],b['test_set_digest'],b['contract_digest'],b['package_sha256'],b['wheel_sha256']))
  self.assertIn('verify_local_authority_key_parity.py',m['files'])
  for rel,h in m['files'].items():self.assertEqual(hashlib.sha256((TOOL/rel).read_bytes()).hexdigest(),h,rel)
  self.assertFalse(any('private' in x.lower() or 'secret' in x.lower() for x in m['files']))
  root=TOOL.parents[1]
  self.assertEqual(hashlib.sha256((root/'docs/PHASE00_STAGE_DERIVED_AUTHORITY_DEPENDENCY_CATALOG_V1.json').read_bytes()).hexdigest(),m['dependency_catalog_sha256'])
  self.assertEqual(hashlib.sha256((root/'test-governance/P00_V03_AUTHORITY_BINDING_PRODUCER_RECIPE_CATALOG_V1.json').read_bytes()).hexdigest(),m['recipe_catalog_sha256'])
if __name__=='__main__':unittest.main()
