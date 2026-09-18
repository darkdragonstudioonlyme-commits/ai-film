#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
TOOL=Path(__file__).resolve().parents[1];MANIFEST=TOOL/'V02_TOOLING_MANIFEST.json'
def h(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 m=json.loads(MANIFEST.read_text());assert m.get('schema_version')==1 and m.get('status')=='LOCAL_KEY_ACTIVATION_CANDIDATE'
 rows=m.get('files');assert isinstance(rows,dict) and rows
 for rel,want in sorted(rows.items()):
  p=TOOL/rel;assert p.is_file(),rel;got=h(p);assert got==want,(rel,got,want);print('PASS',rel)
 local_sha=m.get('local_identity_context_expected_sha256');assert isinstance(local_sha,str) and re.fullmatch(r'[0-9a-f]{64}',local_sha)
 assert f"EXPECTED_CONTEXT_SHA256='{local_sha}'" in (TOOL/'v02_local_identity.py').read_text()
 trust_sha=m.get('local_trust_config_sha256');assert trust_sha==h(TOOL/'local-operator-trust-anchor.json')
 sig=(TOOL/'v02_local_authority_signature.py').read_text();assert f"EXPECTED_TRUST_CONFIG_SHA256='{trust_sha}'" in sig
 bind_sha=m.get('candidate_binding_sha256');assert bind_sha==h(TOOL/'dev22-candidate-binding.json')
 binding=json.loads((TOOL/'dev22-candidate-binding.json').read_text());assert binding['candidate_id']==m['candidate_id']
 intake=(TOOL/'v02-authority-intake.py').read_text();assert f"CANDIDATE_BINDING_SHA256='{bind_sha}'" in intake;assert f"CANDIDATE_ID='{m['candidate_id']}'" in intake
 assert 'P00_LAB_EXTERNAL_AUTHORITY_INTAKE' not in json.dumps(json.loads((TOOL/'approval-envelope.template.json').read_text()))
 print('V02_TOOLING_MANIFEST_TEST_PASS',len(rows),'files')
if __name__=='__main__':main()