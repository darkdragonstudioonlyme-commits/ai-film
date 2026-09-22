#!/usr/bin/env python3
"""Strict candidate-binding loader shared by successor V02/V03 tooling."""
from __future__ import annotations
import hashlib,json,re,stat,uuid
from pathlib import Path

H40=re.compile(r'^[0-9a-f]{40}$'); H64=re.compile(r'^[0-9a-f]{64}$')
FIELDS={'authority_model','build_digest','candidate_id','code_review_record','contract_digest',
        'implementation_version','package_sha256','schema_version','source_commit','status',
        'test_review_record','test_set_digest','wheel_sha256'}

class ProfileError(RuntimeError): pass

def _pairs(rows):
    out={}
    for k,v in rows:
        if k in out: raise ProfileError('DUPLICATE_JSON_KEY:'+k)
        out[k]=v
    return out

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')

def sha(raw): return hashlib.sha256(raw).hexdigest()

def load_profile(path,expected_sha256=None):
    path=Path(path)
    try: st=path.lstat()
    except OSError as e: raise ProfileError('BINDING_UNAVAILABLE') from e
    if not stat.S_ISREG(st.st_mode) or path.is_symlink(): raise ProfileError('BINDING_FILE_UNSAFE')
    raw=path.read_bytes()
    try:
        value=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,
                         parse_constant=lambda x: (_ for _ in ()).throw(ProfileError('NONFINITE_JSON')))
    except (UnicodeError,json.JSONDecodeError) as e: raise ProfileError('BINDING_JSON_INVALID') from e
    if type(value) is not dict or set(value)!=FIELDS: raise ProfileError('BINDING_SCHEMA')
    if raw != canonical(value)+b'\n': raise ProfileError('BINDING_NOT_CANONICAL')
    actual=sha(raw)
    if expected_sha256 is not None and (not H64.fullmatch(str(expected_sha256)) or actual!=expected_sha256):
        raise ProfileError('BINDING_SHA256_MISMATCH')
    if type(value['schema_version']) is not int or value['schema_version']!=1 or value['status']!='CANDIDATE_BOUND': raise ProfileError('BINDING_VERSION_STATUS')
    if value['authority_model']!='LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN': raise ProfileError('BINDING_AUTHORITY_MODEL')
    try: uuid.UUID(value['candidate_id'])
    except (ValueError,TypeError,AttributeError) as e: raise ProfileError('BINDING_CANDIDATE_ID') from e
    if not H40.fullmatch(str(value['source_commit'])): raise ProfileError('BINDING_SOURCE_COMMIT')
    for k in ('build_digest','contract_digest','package_sha256','test_set_digest','wheel_sha256'):
        if not H64.fullmatch(str(value[k])): raise ProfileError('BINDING_HASH:'+k)
    if not isinstance(value['implementation_version'],str) or not value['implementation_version']: raise ProfileError('BINDING_VERSION')
    for k in ('code_review_record','test_review_record'):
        if not isinstance(value[k],str) or not value[k] or value[k].startswith('/') or '..' in Path(value[k]).parts: raise ProfileError('BINDING_REVIEW_PATH:'+k)
    return value,actual

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--sha256');a=ap.parse_args()
    try:v,h=load_profile(a.binding,a.sha256)
    except ProfileError as e: print(json.dumps({'kind':'V02_CANDIDATE_PROFILE','status':'FAIL','reason':str(e)},sort_keys=True,separators=(',',':')));return 1
    print(json.dumps({'kind':'V02_CANDIDATE_PROFILE','status':'PASS','candidate_id':v['candidate_id'],'binding_sha256':h,'source_commit':v['source_commit'],'implementation_version':v['implementation_version']},sort_keys=True,separators=(',',':')));return 0

if __name__=='__main__': raise SystemExit(main())
