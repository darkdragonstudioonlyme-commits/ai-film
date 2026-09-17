#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path

TOOL=Path(__file__).resolve().parents[1]
MANIFEST=TOOL/'V02_TOOLING_MANIFEST.json'

def h(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    m=json.loads(MANIFEST.read_text())
    assert m.get('schema_version')==1 and m.get('status')=='CANDIDATE_SOURCE_FROZEN'
    rows=m.get('files');assert isinstance(rows,dict) and rows
    for rel,want in sorted(rows.items()):
        p=TOOL/rel; assert p.is_file(),rel; got=h(p);assert got==want,(rel,got,want)
        print('PASS',rel)
    local_sha=m.get('local_identity_context_expected_sha256')
    assert isinstance(local_sha,str) and re.fullmatch(r'[0-9a-f]{64}',local_sha)
    source=(TOOL/'v02_local_identity.py').read_text()
    assert f"EXPECTED_CONTEXT_SHA256='{local_sha}'" in source
    trust_sha=m.get('pending_trust_config_sha256');assert trust_sha==h(TOOL/'external-authority-trust-anchor.json')
    auth=(TOOL/'v02_external_authenticity.py').read_text();assert f"EXPECTED_TRUST_CONFIG_SHA256='{trust_sha}'" in auth
    print('V02_TOOLING_MANIFEST_TEST_PASS',len(rows),'files')

if __name__=='__main__': main()
