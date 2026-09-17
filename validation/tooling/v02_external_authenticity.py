#!/usr/bin/env python3
"""Fail-closed external-authenticity verification for V02 approval envelopes."""
import base64, hashlib, json, re
from pathlib import Path

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    _CRYPTO_IMPORT_ERROR=None
except Exception as exc:  # normalized at verification time
    InvalidSignature=Exception
    Ed25519PublicKey=None
    _CRYPTO_IMPORT_ERROR=type(exc).__name__

DEFAULT_TRUST_CONFIG=Path(__file__).resolve().with_name('external-authority-trust-anchor.json')
EXPECTED_TRUST_CONFIG_SHA256='d59292473a58dd87bb9172ed6c8daedbfa6bdf8c4f5edb13ce6d567a904e22cb'
SIGNATURE_FILENAME='approval-envelope.sig.json'


def _sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _read_json_bytes(path, fail, unreadable_reason):
    try:
        raw=path.read_bytes()
        obj=json.loads(raw.decode('utf-8'))
    except (OSError,UnicodeError,json.JSONDecodeError):
        fail(unreadable_reason)
    if not isinstance(obj,dict):
        fail(unreadable_reason)
    return obj,raw


def verify_external_authenticity(root, envelope_raw, fail, *, trust_path=DEFAULT_TRUST_CONFIG,
                                 expected_trust_sha256=EXPECTED_TRUST_CONFIG_SHA256):
    trust,trust_raw=_read_json_bytes(Path(trust_path),fail,'EXTERNAL_AUTHENTICITY_ANCHOR_UNREADABLE')
    if _sha256(trust_raw)!=expected_trust_sha256:
        fail('EXTERNAL_AUTHENTICITY_ANCHOR_DRIFT')
    required_trust={'schema_version','status','algorithm','key_id','public_key_b64','public_key_sha256','provenance_ref','note'}
    if set(trust)!=required_trust or trust.get('schema_version')!=1 or trust.get('algorithm')!='ED25519':
        fail('EXTERNAL_AUTHENTICITY_ANCHOR_SCHEMA')
    if trust.get('status')!='ACTIVE':
        fail('EXTERNAL_AUTHENTICITY_ANCHOR_PENDING')
    if Ed25519PublicKey is None:
        fail('EXTERNAL_SIGNATURE_VERIFIER_UNAVAILABLE',error_type=_CRYPTO_IMPORT_ERROR)
    key_id=trust.get('key_id'); pub_b64=trust.get('public_key_b64'); pub_sha=trust.get('public_key_sha256')
    provenance=trust.get('provenance_ref')
    if not all(isinstance(v,str) and v for v in (key_id,pub_b64,pub_sha,provenance)):
        fail('EXTERNAL_AUTHENTICITY_ANCHOR_INCOMPLETE')
    if not re.fullmatch(r'[A-Za-z0-9._:-]{1,128}',key_id):
        fail('EXTERNAL_AUTHORITY_KEY_ID_SCHEMA')
    if not re.fullmatch(r'[0-9a-f]{64}',pub_sha):
        fail('EXTERNAL_AUTHENTICITY_PUBLIC_KEY_HASH_SCHEMA')
    try:
        pub_raw=base64.b64decode(pub_b64,validate=True)
    except Exception:
        fail('EXTERNAL_AUTHENTICITY_PUBLIC_KEY_ENCODING')
    if len(pub_raw)!=32 or _sha256(pub_raw)!=pub_sha:
        fail('EXTERNAL_AUTHENTICITY_PUBLIC_KEY_MISMATCH')

    sig_path=Path(root)/SIGNATURE_FILENAME
    sigdoc,_=_read_json_bytes(sig_path,fail,'EXTERNAL_AUTHORITY_SIGNATURE_MISSING')
    required={'schema_version','algorithm','key_id','payload_sha256','signature_b64'}
    if set(sigdoc)!=required or sigdoc.get('schema_version')!=1 or sigdoc.get('algorithm')!='ED25519':
        fail('EXTERNAL_AUTHORITY_SIGNATURE_SCHEMA')
    if sigdoc.get('key_id')!=key_id:
        fail('EXTERNAL_AUTHORITY_KEY_ID_MISMATCH')
    payload_sha=_sha256(envelope_raw)
    if sigdoc.get('payload_sha256')!=payload_sha:
        fail('EXTERNAL_AUTHORITY_PAYLOAD_DIGEST_MISMATCH')
    try:
        signature=base64.b64decode(sigdoc.get('signature_b64',''),validate=True)
        Ed25519PublicKey.from_public_bytes(pub_raw).verify(signature,envelope_raw)
    except Exception as exc:
        # Keep one normalized failure reason; never expose signature bytes or key material.
        fail('EXTERNAL_AUTHORITY_SIGNATURE_INVALID',error_type=type(exc).__name__)
    return {'key_id':key_id,'payload_sha256':payload_sha,'provenance_ref':provenance}
