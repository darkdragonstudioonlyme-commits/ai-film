#!/usr/bin/env python3
"""Verify WSL-local private/public key identity against metadata and the committed public trust anchor.

Never emits private key bytes. Intended for deployment/recovery parity checks, not authority creation.
"""
import argparse,base64,hashlib,json,os,stat,sys
from pathlib import Path
from cryptography.hazmat.primitives.serialization import load_pem_private_key,Encoding,PublicFormat
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ASSURANCE='LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN'
def sha(raw): return hashlib.sha256(raw).hexdigest()
def fail(reason,**extra):
    print(json.dumps({'kind':'V02_LOCAL_KEY_PARITY','status':'FAIL','reason':reason,**extra},sort_keys=True,separators=(',',':')));raise SystemExit(1)
def read_json(p,reason):
    try: x=json.loads(Path(p).read_text(encoding='utf-8'))
    except (OSError,UnicodeError,json.JSONDecodeError): fail(reason)
    if not isinstance(x,dict): fail(reason)
    return x
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--private-key',required=True);ap.add_argument('--public-key',required=True)
    ap.add_argument('--metadata',required=True);ap.add_argument('--trust-anchor',required=True)
    a=ap.parse_args(); priv=Path(a.private_key); pub=Path(a.public_key)
    for p,label in [(priv,'PRIVATE'),(pub,'PUBLIC')]:
        try: st=p.stat()
        except OSError: fail(label+'_KEY_MISSING')
        if not stat.S_ISREG(st.st_mode): fail(label+'_KEY_NOT_REGULAR')
        if (st.st_mode & 0o777)!=0o600: fail(label+'_KEY_MODE',mode=oct(st.st_mode & 0o777))
        if st.st_uid!=os.getuid(): fail(label+'_KEY_OWNER')
    try: key=load_pem_private_key(priv.read_bytes(),password=None)
    except Exception as e: fail('PRIVATE_KEY_UNREADABLE',error_type=type(e).__name__)
    if not isinstance(key,Ed25519PrivateKey): fail('PRIVATE_KEY_ALGORITHM')
    derived=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    try: public_raw=pub.read_bytes()
    except OSError: fail('PUBLIC_KEY_MISSING')
    if len(public_raw)!=32 or public_raw!=derived: fail('PUBLIC_KEY_PARITY_MISMATCH')
    pub_sha=sha(derived); pub_b64=base64.b64encode(derived).decode()
    meta=read_json(a.metadata,'KEY_METADATA_UNREADABLE')
    required={'schema_version','authority_model','assurance_note','created_at_utc','key_id','private_key_committed','private_key_path','provenance_ref','public_key_b64','public_key_sha256'}
    if set(meta)!=required or meta.get('schema_version')!=1: fail('KEY_METADATA_SCHEMA')
    if meta.get('authority_model')!=ASSURANCE or meta.get('private_key_committed') is not False: fail('KEY_METADATA_AUTHORITY_MODEL')
    if meta.get('public_key_sha256')!=pub_sha or meta.get('public_key_b64')!=pub_b64: fail('KEY_METADATA_PUBLIC_MISMATCH')
    if meta.get('private_key_path')!=str(priv): fail('KEY_METADATA_PRIVATE_PATH_MISMATCH')
    trust=read_json(a.trust_anchor,'TRUST_ANCHOR_UNREADABLE')
    req={'schema_version','status','algorithm','assurance_class','key_id','public_key_b64','public_key_sha256','provenance_ref','note'}
    if set(trust)!=req or trust.get('schema_version')!=1 or trust.get('status')!='ACTIVE' or trust.get('algorithm')!='ED25519' or trust.get('assurance_class')!=ASSURANCE:
        fail('TRUST_ANCHOR_SCHEMA')
    for field,expected in [('key_id',meta.get('key_id')),('public_key_b64',pub_b64),('public_key_sha256',pub_sha),('provenance_ref',meta.get('provenance_ref'))]:
        if trust.get(field)!=expected: fail('TRUST_ANCHOR_KEY_PARITY',field=field)
    print(json.dumps({'kind':'V02_LOCAL_KEY_PARITY','status':'PASS','key_id':trust['key_id'],'public_key_sha256':pub_sha,'private_key_mode':'0600','public_key_mode':'0600','assurance_class':ASSURANCE,'private_key_committed':False},sort_keys=True,separators=(',',':')))
if __name__=='__main__': main()
