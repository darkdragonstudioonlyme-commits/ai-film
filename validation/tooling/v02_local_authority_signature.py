#!/usr/bin/env python3
"""Fail-closed same-WSL local-operator signature verification for V02 approval envelopes."""
import base64, hashlib, json, re
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    _CRYPTO_IMPORT_ERROR=None
except Exception as exc:
    Ed25519PublicKey=None
    _CRYPTO_IMPORT_ERROR=type(exc).__name__

DEFAULT_TRUST_CONFIG=Path(__file__).resolve().with_name('local-operator-trust-anchor.json')
EXPECTED_TRUST_CONFIG_SHA256='93dd4d3d411fe60dc711a13ed010eb6d0e620271ec0c44a101603f2dba4bacf9'
SIGNATURE_FILENAME='approval-envelope.sig.json'
ASSURANCE_CLASS='LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN'

def _sha256(raw): return hashlib.sha256(raw).hexdigest()

def _read_json_bytes(path,fail,reason):
    try:
        raw=Path(path).read_bytes(); obj=json.loads(raw.decode('utf-8'))
    except (OSError,UnicodeError,json.JSONDecodeError): fail(reason)
    if not isinstance(obj,dict): fail(reason)
    return obj,raw

def verify_local_authority_signature(root,envelope_raw,fail,*,trust_path=DEFAULT_TRUST_CONFIG,
                                     expected_trust_sha256=EXPECTED_TRUST_CONFIG_SHA256):
    trust,trust_raw=_read_json_bytes(trust_path,fail,'LOCAL_AUTHORITY_ANCHOR_UNREADABLE')
    if _sha256(trust_raw)!=expected_trust_sha256: fail('LOCAL_AUTHORITY_ANCHOR_DRIFT')
    required={'schema_version','status','algorithm','assurance_class','key_id','public_key_b64',
              'public_key_sha256','provenance_ref','note'}
    if set(trust)!=required or trust.get('schema_version')!=1 or trust.get('algorithm')!='ED25519' or trust.get('assurance_class')!=ASSURANCE_CLASS:
        fail('LOCAL_AUTHORITY_ANCHOR_SCHEMA')
    if trust.get('status')!='ACTIVE': fail('LOCAL_AUTHORITY_ANCHOR_PENDING')
    if Ed25519PublicKey is None: fail('LOCAL_SIGNATURE_VERIFIER_UNAVAILABLE',error_type=_CRYPTO_IMPORT_ERROR)
    key_id=trust.get('key_id'); pub_b64=trust.get('public_key_b64'); pub_sha=trust.get('public_key_sha256'); provenance=trust.get('provenance_ref')
    if not all(isinstance(v,str) and v for v in (key_id,pub_b64,pub_sha,provenance)):
        fail('LOCAL_AUTHORITY_ANCHOR_INCOMPLETE')
    if not re.fullmatch(r'[A-Za-z0-9._:-]{1,128}',key_id): fail('LOCAL_AUTHORITY_KEY_ID_SCHEMA')
    if not re.fullmatch(r'[0-9a-f]{64}',pub_sha): fail('LOCAL_AUTHORITY_PUBLIC_KEY_HASH_SCHEMA')
    if not provenance.startswith('WSL_LOCAL_OPERATOR_SELF_MANAGED:'): fail('LOCAL_AUTHORITY_PROVENANCE_SCHEMA')
    try: pub_raw=base64.b64decode(pub_b64,validate=True)
    except Exception: fail('LOCAL_AUTHORITY_PUBLIC_KEY_ENCODING')
    if len(pub_raw)!=32 or _sha256(pub_raw)!=pub_sha: fail('LOCAL_AUTHORITY_PUBLIC_KEY_MISMATCH')
    sigdoc,_=_read_json_bytes(Path(root)/SIGNATURE_FILENAME,fail,'LOCAL_AUTHORITY_SIGNATURE_MISSING')
    required_sig={'schema_version','algorithm','key_id','payload_sha256','signature_b64'}
    if set(sigdoc)!=required_sig or sigdoc.get('schema_version')!=1 or sigdoc.get('algorithm')!='ED25519':
        fail('LOCAL_AUTHORITY_SIGNATURE_SCHEMA')
    if sigdoc.get('key_id')!=key_id: fail('LOCAL_AUTHORITY_KEY_ID_MISMATCH')
    payload_sha=_sha256(envelope_raw)
    if sigdoc.get('payload_sha256')!=payload_sha: fail('LOCAL_AUTHORITY_PAYLOAD_DIGEST_MISMATCH')
    try:
        sig=base64.b64decode(sigdoc.get('signature_b64',''),validate=True)
        Ed25519PublicKey.from_public_bytes(pub_raw).verify(sig,envelope_raw)
    except Exception as exc:
        fail('LOCAL_AUTHORITY_SIGNATURE_INVALID',error_type=type(exc).__name__)
    return {'key_id':key_id,'payload_sha256':payload_sha,'provenance_ref':provenance,'assurance_class':ASSURANCE_CLASS}