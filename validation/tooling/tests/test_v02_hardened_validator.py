#!/usr/bin/env python3
import hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]
TEMPLATE=json.loads((SOURCE/'approval-envelope.template.json').read_text())

def prepare_tool_copy(base):
    tool=base/'tool'; tool.mkdir()
    for name in ['v02-authority-intake.py','v02-authority-preflight.py','v02_external_authenticity.py',
                 'v02_local_identity.py','external-authority-trust-anchor.json','approval-envelope.template.json']:
        shutil.copy2(SOURCE/name,tool/name)
    synthetic={'schema_version':1,'host_id':'host_'+'0'*32,'operator_digest':'1'*64}
    raw=(json.dumps(synthetic,sort_keys=True,separators=(',',':'))+'\n').encode()
    (tool/'v02-local-identity-context.json').write_bytes(raw)
    sha=hashlib.sha256(raw).hexdigest()
    lp=tool/'v02_local_identity.py'; text=lp.read_text()
    text=re.sub(r"EXPECTED_CONTEXT_SHA256='[0-9a-f]{64}'",f"EXPECTED_CONTEXT_SHA256='{sha}'",text)
    lp.write_text(text)
    return tool

def run_case(preflight,root):
    p=subprocess.run([str(preflight),'--inbox',str(root),'--json'],text=True,capture_output=True)
    data=json.loads((p.stdout.strip().splitlines() or ['{}'])[-1])
    assert data.get('staging_unchanged') is True
    assert data.get('native_execution_started') is False
    return p.returncode,data

def write_env(root,obj):
    (root/'objects').mkdir(parents=True,exist_ok=True)
    (root/'approval-envelope.json').write_text(json.dumps(obj,sort_keys=True,separators=(',',':')))

def expect(label,preflight,root,rc,reason,status):
    got_rc,data=run_case(preflight,root)
    assert (got_rc,data.get('reason'),data.get('status'))==(rc,reason,status),(label,got_rc,data)
    print('PASS',label,reason)

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); tool=prepare_tool_copy(base); preflight=tool/'v02-authority-preflight.py'; cases=base/'cases'
        r=cases/'missing';(r/'objects').mkdir(parents=True);expect('missing',preflight,r,10,'APPROVAL_ENVELOPE_MISSING','MISSING')
        r=cases/'pending';write_env(r,dict(TEMPLATE));expect('pending',preflight,r,11,'EXTERNAL_DECISION_NOT_APPROVE','INVALID')
        approved=dict(TEMPLATE);approved['decision']='APPROVE';approved['approved_by_external_authority']=True
        r=cases/'flags-only';write_env(r,approved);expect('flags-only',preflight,r,11,'EXTERNAL_AUTHENTICITY_ANCHOR_PENDING','INVALID')
        fake=dict(approved);h='0'*64
        for k in ['lab_registration_ref','owner_attestation_ref','controller_attestation_ref','fixture_set_ref','management_isolation_recovery_ref','lab_test_plan_approval_ref','lab_acceptance_suite_ref']: fake[k]=h
        fake['role_pins']={'registration':[h],'design':[h],'code':[h]}
        r=cases/'fake-refs';write_env(r,fake);expect('fake-refs',preflight,r,11,'EXTERNAL_AUTHENTICITY_ANCHOR_PENDING','INVALID')
        (r/'approval-envelope.sig.json').write_text(json.dumps({'schema_version':1,'algorithm':'ED25519','key_id':'OPERATOR-KEY','payload_sha256':'0'*64,'signature_b64':'AA=='},sort_keys=True,separators=(',',':')))
        expect('operator-signature-with-pending-anchor',preflight,r,11,'EXTERNAL_AUTHENTICITY_ANCHOR_PENDING','INVALID')
        # Tamper the local identity context without updating its pinned hash.
        ctx=tool/'v02-local-identity-context.json'; o=json.loads(ctx.read_text());o['operator_digest']='2'*64;ctx.write_text(json.dumps(o,sort_keys=True,separators=(',',':'))+'\n')
        expect('local-identity-context-drift',preflight,r,11,'LOCAL_IDENTITY_CONTEXT_DRIFT','INVALID')
    print('V02_HARDENED_VALIDATOR_TEST_PASS 6 cases')

if __name__=='__main__': main()
