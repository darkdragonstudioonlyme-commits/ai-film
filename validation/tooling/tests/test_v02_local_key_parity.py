#!/usr/bin/env python3
import base64,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,PublicFormat,NoEncryption
TOOL=Path(__file__).resolve().parents[1]/'verify_local_authority_key_parity.py'
ASSURANCE='LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN'
def write(root,key=None,key_id='TEST-KEY',trust_changes=None,meta_changes=None,public_key=None):
    key=key or Ed25519PrivateKey.generate();pub=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);public_key=public_key if public_key is not None else pub
    priv=root/'private.pem';raw=key.private_bytes(Encoding.PEM,PrivateFormat.PKCS8,NoEncryption());priv.write_bytes(raw);os.chmod(priv,0o600)
    pp=root/'public.raw';pp.write_bytes(public_key);os.chmod(pp,0o600)
    sha=hashlib.sha256(pub).hexdigest();b64=base64.b64encode(pub).decode();prov='WSL_LOCAL_OPERATOR_SELF_MANAGED:'+sha
    meta={'schema_version':1,'authority_model':ASSURANCE,'assurance_note':'test','created_at_utc':'2026-09-18T00:00:00+00:00','key_id':key_id,'private_key_committed':False,'private_key_path':str(priv),'provenance_ref':prov,'public_key_b64':b64,'public_key_sha256':sha};meta.update(meta_changes or {})
    mp=root/'metadata.json';mp.write_text(json.dumps(meta));
    trust={'schema_version':1,'status':'ACTIVE','algorithm':'ED25519','assurance_class':ASSURANCE,'key_id':key_id,'public_key_b64':b64,'public_key_sha256':sha,'provenance_ref':prov,'note':'test'};trust.update(trust_changes or {})
    tp=root/'trust.json';tp.write_text(json.dumps(trust));return priv,pp,mp,tp
def run(paths):
    p=subprocess.run([sys.executable,str(TOOL),'--private-key',str(paths[0]),'--public-key',str(paths[1]),'--metadata',str(paths[2]),'--trust-anchor',str(paths[3])],text=True,capture_output=True)
    try: out=json.loads(p.stdout.strip().splitlines()[-1])
    except Exception: raise AssertionError((p.returncode,p.stdout,p.stderr))
    return p.returncode,out
def expect(reason,mutator=None):
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);paths=write(root)
        if mutator: mutator(root,paths)
        rc,out=run(paths);assert rc==1 and out['reason']==reason,(rc,out,reason);print('PASS',reason)
def main():
    with tempfile.TemporaryDirectory() as td:
        paths=write(Path(td));rc,out=run(paths);assert rc==0 and out['status']=='PASS';print('PASS valid_parity')
    expect('PRIVATE_KEY_MODE',lambda r,p:os.chmod(p[0],0o640))
    expect('PUBLIC_KEY_MODE',lambda r,p:os.chmod(p[1],0o644))
    def wrong_pub(r,p):
        other=Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);p[1].write_bytes(other)
    expect('PUBLIC_KEY_PARITY_MISMATCH',wrong_pub)
    def bad_meta(r,p):
        x=json.loads(p[2].read_text());x['public_key_sha256']='0'*64;p[2].write_text(json.dumps(x))
    expect('KEY_METADATA_PUBLIC_MISMATCH',bad_meta)
    def bad_trust(r,p):
        x=json.loads(p[3].read_text());x['key_id']='OTHER';p[3].write_text(json.dumps(x))
    expect('TRUST_ANCHOR_KEY_PARITY',bad_trust)
    print('V02_LOCAL_KEY_PARITY_TEST_PASS 6 cases')
if __name__=='__main__':main()
