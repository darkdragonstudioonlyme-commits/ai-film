"""Bounded, deterministic data handling. JSON is data, never code."""
import hashlib
import json
import re
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath,PureWindowsPath
from .errors import P00Error,Exit,require

MAX_JSON=10*1024*1024
HEX=re.compile(r'[0-9a-f]{64}')
TOKEN=re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}')

def _pairs(pairs):
    obj={}
    for k,v in pairs:
        require(k not in obj,Exit.INPUT,'DUPLICATE_JSON_KEY')
        obj[k]=v
    return obj

def _finite(_):
    raise P00Error(Exit.INPUT,'NONFINITE_JSON')

def loads(data: bytes|str):
    if isinstance(data,str):
        try: data=data.encode('utf-8')
        except UnicodeError: raise P00Error(10,'INVALID_UNICODE') from None
    require(isinstance(data,bytes) and len(data)<=MAX_JSON,10,'JSON_SIZE_LIMIT')
    try:
        obj=json.loads(data.decode('utf-8'),object_pairs_hook=_pairs,parse_constant=_finite)
        _depth(obj)
        return obj
    except P00Error: raise
    except (UnicodeError,ValueError,RecursionError,TypeError):
        raise P00Error(10,'INVALID_JSON') from None

def _depth(obj,level=0):
    require(level<=32,10,'JSON_DEPTH_LIMIT')
    if isinstance(obj,dict):
        for k,v in obj.items():
            require(isinstance(k,str),10,'INVALID_JSON_KEY')
            _depth(v,level+1)
    elif isinstance(obj,list):
        require(len(obj)<=10000,10,'JSON_ITEMS_LIMIT')
        for v in obj: _depth(v,level+1)

def canonical(obj) -> bytes:
    _depth(obj)
    try:
        return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
    except (ValueError,TypeError,UnicodeError,RecursionError):
        raise P00Error(10,'NONCANONICAL_JSON') from None

def sha256(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def digest(obj)->str:
    return sha256(canonical(obj))

def read_bytes(path:Path,limit=MAX_JSON)->bytes:
    try:
        size=path.stat().st_size
        require(size<=limit,10,'FILE_SIZE_LIMIT')
        with path.open('rb') as handle: data=handle.read(limit+1)
        require(len(data)<=limit,10,'FILE_SIZE_LIMIT')
        return data
    except P00Error: raise
    except OSError: raise P00Error(10,'FILE_READ_FAILED') from None

def read_json(path:Path):
    return loads(read_bytes(path))

def instant(value:str):
    require(isinstance(value,str) and len(value)<=64,10,'INVALID_TIMESTAMP')
    try:
        dt=datetime.fromisoformat(value.replace('Z','+00:00'))
        require(dt.tzinfo is not None,10,'TIMESTAMP_REQUIRES_OFFSET')
        return dt.astimezone(timezone.utc)
    except P00Error: raise
    except (ValueError,OverflowError): raise P00Error(10,'INVALID_TIMESTAMP') from None

def token(value:str):
    require(isinstance(value,str) and TOKEN.fullmatch(value) is not None,10,'INVALID_IDENTIFIER')
    return value

def hash_value(value:str):
    require(isinstance(value,str) and HEX.fullmatch(value) is not None,10,'INVALID_DIGEST')
    return value

def win_abs(value:str,*,allow_root=False):
    require(isinstance(value,str) and 1<=len(value)<=240 and '\x00' not in value,10,'INVALID_WINDOWS_PATH')
    p=PureWindowsPath(value)
    require(p.is_absolute() and p.drive and not str(p).startswith('\\\\'),10,'PATH_NOT_LOCAL_ABSOLUTE')
    require('..' not in p.parts,10,'PATH_TRAVERSAL')
    if not allow_root: require(len(p.parts)>1,10,'ROOT_PATH_FORBIDDEN')
    return str(p)

def relpath(value:str):
    require(isinstance(value,str) and 1<=len(value)<=200 and '\x00' not in value,10,'INVALID_RELATIVE_PATH')
    p=PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and '.' not in p.parts,10,'PATH_TRAVERSAL')
    return str(p)

def fields(obj,expected:set[str]):
    require(isinstance(obj,dict) and set(obj)==expected,10,'SCHEMA_FIELD_SET')
    return obj

def bounded_text(value,limit=4096):
    require(isinstance(value,str) and len(value)<=limit and '\x00' not in value,10,'INVALID_TEXT')
    return value
