#!/usr/bin/env python3
import base64,hashlib,json,re,shutil,subprocess,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

SOURCE=Path(__file__).resolve().parents[1]
TEMPLATE=json.loads((SOURCE/'approval-envelope.template.json').read_text())

def prepare_tool_copy(base):
    tool=base/'tool';tool.mkdir()
    for name in ['v02-authority-intake.py','v02-authority-preflight.py','v02_local_authority_signature.py',
                 'v02_local_identity.py','local-operator-trust-anchor.json','approval-envelope.template.json']:
        shutil.copy2(SOURCE/name,tool/name)
    synthetic={'schema_version':1,'host_id':'host_'+'0'*32,'operator_digest':'1'*64}
    raw=(json.dumps(synthetic,sort_keys=True,separators=(',',':'))+'\n').encode()
    (tool/'v02-local-identity-context.json').write_bytes(raw)
    lp=tool/'v02_local_identity.py'
    text=lp.read_text()
    text=re.sub(r"EXPECTED_CONTEXT_SHA256='[0-9a-f]{64}'",f"EXPECTED_CONTEXT_SHA256='{hashlib.sha256(raw).hexdigest()}'",text)
    lp.write_text(text)

    private=Ed25519PrivateKey.generate()
    public=private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    key_id='TEST-HARDENED-LOCAL-KEY'
    trust={'schema_version':1,'status':'ACTIVE','algorithm':'ED25519',
           'assurance_class':'LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN','key_id':key_id,
           'public_key_b64':base64.b64encode(public).decode(),
           'public_key_sha256':hashlib.sha256(public).hexdigest(),
           'provenance_ref':'WSL_LOCAL_OPERATOR_SELF_MANAGED:TEST_HARDENED',
           'note':'isolated hardened-validator test key'}
    trust_raw=(json.dumps(trust,sort_keys=True,separators=(',',':'))+'\n').encode()
    (tool/'local-operator-trust-anchor.json').write_bytes(trust_raw)
    sp=tool/'v02_local_authority_signature.py'
    text=sp.read_text()
    text=re.sub(r"EXPECTED_TRUST_CONFIG_SHA256='[0-9a-f]{64}'",f"EXPECTED_TRUST_CONFIG_SHA256='{hashlib.sha256(trust_raw).hexdigest()}'",text)
    sp.write_text(text)
    return tool,private,key_id

def run_case(preflight,root):
    p=subprocess.run([str(preflight),'--inbox',str(root),'--json'],text=True,capture_output=True)
    data=json.loads((p.stdout.strip().splitlines() or ['{}'])[-1])
    assert data.get('staging_unchanged') is True
    assert data.get('native_execution_started') is False
    return p.returncode,data

def write_env(root,obj):
    (root/'objects').mkdir(parents=True,exist_ok=True)
    (root/'approval-envelope.json').write_text(json.dumps(obj,sort_keys=True,separators=(',',':')))

def sign_env(root,private,key_id):
    raw=(root/'approval-envelope.json').read_bytes()
    doc={'schema_version':1,'algorithm':'ED25519','key_id':key_id,
         'payload_sha256':hashlib.sha256(raw).hexdigest(),
         'signature_b64':base64.b64encode(private.sign(raw)).decode()}
    (root/'approval-envelope.sig.json').write_text(json.dumps(doc,sort_keys=True,separators=(',',':')))

def expect(label,preflight,root,rc,reason,status):
    got_rc,data=run_case(preflight,root)
    assert(got_rc,data.get('reason'),data.get('status'))==(rc,reason,status),(label,got_rc,data)
    print('PASS',label,reason)

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td);tool,private,key_id=prepare_tool_copy(base);preflight=tool/'v02-authority-preflight.py';cases=base/'cases'
        r=cases/'missing';(r/'objects').mkdir(parents=True);expect('missing',preflight,r,10,'APPROVAL_ENVELOPE_MISSING','MISSING')
        r=cases/'pending';write_env(r,dict(TEMPLATE));expect('pending',preflight,r,11,'LOCAL_DECISION_NOT_APPROVE','INVALID')
        old=dict(TEMPLATE);old['kind']='P00_LAB_EXTERNAL_AUTHORITY_INTAKE';old['approved_by_external_authority']=True;old.pop('approved_by_local_operator');write_env(cases/'old-external',old)
        expect('old-external-hard-cutover',preflight,cases/'old-external',11,'ENVELOPE_SCHEMA','INVALID')
        approved=dict(TEMPLATE);approved['decision']='APPROVE';approved['approved_by_local_operator']=True
        r=cases/'flags-only';write_env(r,approved);expect('flags-only',preflight,r,11,'LOCAL_AUTHORITY_SIGNATURE_MISSING','INVALID')
        fake=dict(approved);h='0'*64
        for k in ['lab_registration_ref','owner_attestation_ref','local_operator_attestation_ref','fixture_set_ref','management_isolation_recovery_ref','lab_test_plan_approval_ref','lab_acceptance_suite_ref']:fake[k]=h
        fake['role_pins']={'registration':[h],'design':[h],'code':[h]}
        r=cases/'fake-refs';write_env(r,fake);sign_env(r,private,key_id)
        expect('valid-signature-fake-refs',preflight,r,11,'OBJECT_MISSING','INVALID')
        bad=dict(json.loads((r/'approval-envelope.sig.json').read_text()));bad['payload_sha256']='0'*64
        (r/'approval-envelope.sig.json').write_text(json.dumps(bad,sort_keys=True,separators=(',',':')))
        expect('payload-digest-mismatch',preflight,r,11,'LOCAL_AUTHORITY_PAYLOAD_DIGEST_MISMATCH','INVALID')
        ctx=tool/'v02-local-identity-context.json';o=json.loads(ctx.read_text());o['operator_digest']='2'*64
        ctx.write_text(json.dumps(o,sort_keys=True,separators=(',',':'))+'\n')
        expect('local-identity-context-drift',preflight,r,11,'LOCAL_IDENTITY_CONTEXT_DRIFT','INVALID')
    print('V02_HARDENED_VALIDATOR_TEST_PASS 7 cases')

if __name__=='__main__':main()
