#!/usr/bin/env python3
"""Load the exact local V02 host/operator scope without publishing raw identity values."""
import hashlib, json, re
from pathlib import Path

DEFAULT_CONTEXT=Path(__file__).resolve().with_name('v02-local-identity-context.json')
EXPECTED_CONTEXT_SHA256='c56a13e65ac76f6fe59245a5706ec6270c3c85fd69c81aa50fa2e3ce7165acbc'


def load_local_identity(fail, *, path=DEFAULT_CONTEXT, expected_sha256=EXPECTED_CONTEXT_SHA256):
    try:
        raw=Path(path).read_bytes(); data=json.loads(raw.decode('utf-8'))
    except (OSError,UnicodeError,json.JSONDecodeError):
        fail('LOCAL_IDENTITY_CONTEXT_UNREADABLE')
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:
        fail('LOCAL_IDENTITY_CONTEXT_DRIFT')
    if not isinstance(data,dict) or set(data)!={'schema_version','host_id','operator_digest'} or data.get('schema_version')!=1:
        fail('LOCAL_IDENTITY_CONTEXT_SCHEMA')
    host=data.get('host_id'); operator=data.get('operator_digest')
    if not isinstance(host,str) or not re.fullmatch(r'host_[0-9a-f]{32}',host):
        fail('LOCAL_HOST_ID_SCHEMA')
    if not isinstance(operator,str) or not re.fullmatch(r'[0-9a-f]{64}',operator):
        fail('LOCAL_OPERATOR_DIGEST_SCHEMA')
    return {'host_id':host,'operator_digest':operator}
