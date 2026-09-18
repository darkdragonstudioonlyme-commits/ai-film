#!/usr/bin/env python3
import base64,hashlib,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from v02_local_authority_signature import verify_local_authority_signature,ASSURANCE_CLASS

class GateFailure(Exception):
    def __init__(self,reason,extra): super().__init__(reason);self.reason=reason;self.extra=extra

def fail(reason,**extra): raise GateFailure(reason,extra)
def write_json(path,obj):
    raw=(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode();path.write_bytes(raw);return raw,hashlib.sha256(raw).hexdigest()
def expect(reason,fn):
    try: fn()
    except GateFailure as e:
        assert e.reason==reason,(e.reason,reason);print('PASS',reason);return
    raise AssertionError('expected '+reason)

def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);(root/'objects').mkdir();env_raw=b'{"decision":"APPROVE","schema_version":1}\n'
        pending={'schema_version':1,'status':'PENDING_LOCAL_KEY','algorithm':'ED25519','assurance_class':ASSURANCE_CLASS,
                 'key_id':None,'public_key_b64':None,'public_key_sha256':None,'provenance_ref':None,'note':'test pending local key'}
        _,pending_sha=write_json(root/'trust-pending.json',pending)
        expect('LOCAL_AUTHORITY_ANCHOR_PENDING',lambda:verify_local_authority_signature(root,env_raw,fail,trust_path=root/'trust-pending.json',expected_trust_sha256=pending_sha))
        private=Ed25519PrivateKey.generate();public=private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        active={'schema_version':1,'status':'ACTIVE','algorithm':'ED25519','assurance_class':ASSURANCE_CLASS,
                'key_id':'TEST-LOCAL-KEY-001','public_key_b64':base64.b64encode(public).decode(),
                'public_key_sha256':hashlib.sha256(public).hexdigest(),
                'provenance_ref':'WSL_LOCAL_OPERATOR_SELF_MANAGED:TEST_ONLY','note':'synthetic local test key'}
        _,active_sha=write_json(root/'trust-active.json',active)
        sigdoc={'schema_version':1,'algorithm':'ED25519','key_id':active['key_id'],
                'payload_sha256':hashlib.sha256(env_raw).hexdigest(),
                'signature_b64':base64.b64encode(private.sign(env_raw)).decode()}
        write_json(root/'approval-envelope.sig.json',sigdoc)
        got=verify_local_authority_signature(root,env_raw,fail,trust_path=root/'trust-active.json',expected_trust_sha256=active_sha)
        assert got['key_id']==active['key_id'] and got['assurance_class']==ASSURANCE_CLASS;print('PASS valid_local_signature')
        expect('LOCAL_AUTHORITY_PAYLOAD_DIGEST_MISMATCH',lambda:verify_local_authority_signature(root,env_raw+b' ',fail,trust_path=root/'trust-active.json',expected_trust_sha256=active_sha))
        bad=dict(sigdoc);bad['key_id']='OTHER';write_json(root/'approval-envelope.sig.json',bad)
        expect('LOCAL_AUTHORITY_KEY_ID_MISMATCH',lambda:verify_local_authority_signature(root,env_raw,fail,trust_path=root/'trust-active.json',expected_trust_sha256=active_sha))
        write_json(root/'approval-envelope.sig.json',sigdoc)
        expect('LOCAL_AUTHORITY_ANCHOR_DRIFT',lambda:verify_local_authority_signature(root,env_raw,fail,trust_path=root/'trust-active.json',expected_trust_sha256='0'*64))
        badprov=dict(active);badprov['provenance_ref']='EXTERNAL_OR_FAKE';_,badprov_sha=write_json(root/'trust-badprov.json',badprov)
        expect('LOCAL_AUTHORITY_PROVENANCE_SCHEMA',lambda:verify_local_authority_signature(root,env_raw,fail,trust_path=root/'trust-badprov.json',expected_trust_sha256=badprov_sha))
        badsig=dict(sigdoc);badsig['signature_b64']=base64.b64encode(b'0'*64).decode();write_json(root/'approval-envelope.sig.json',badsig)
        expect('LOCAL_AUTHORITY_SIGNATURE_INVALID',lambda:verify_local_authority_signature(root,env_raw,fail,trust_path=root/'trust-active.json',expected_trust_sha256=active_sha))
    print('V02_LOCAL_AUTHORITY_SIGNATURE_TEST_PASS 7 cases')
if __name__=='__main__':main()
