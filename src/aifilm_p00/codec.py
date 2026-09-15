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
        raise P00Error(10,'NONCANONICAL_VALUE') from None

def digest(obj) -> str: return hashlib.sha256(canonical(obj)).hexdigest()
def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def fields(obj: dict,required:set,optional:set=frozenset()) -> dict:
    require(type(obj) is dict,10,'OBJECT_REQUIRED')
    require(required<=obj.keys() and obj.keys()<=required|optional,10,'SCHEMA_FIELDS')
    return obj

def token(value) -> str:
    require(type(value) is str and TOKEN.fullmatch(value) is not None,10,'INVALID_TOKEN')
    return value

def hash_value(value) -> str:
    require(type(value) is str and HEX.fullmatch(value) is not None,10,'INVALID_DIGEST')
    return value

def integer(value,minimum=0,maximum=2**63-1):
    require(type(value) is int and minimum<=value<=maximum,10,'INVALID_INTEGER')
    return value

def instant(value: str) -> datetime:
    require(type(value) is str,10,'INVALID_TIMESTAMP')
    try:
        dt=datetime.fromisoformat(value.replace('Z','+00:00'))
        require(dt.tzinfo is not None and dt.utcoffset().total_seconds()==0,10,'UTC_REQUIRED')
        return dt.astimezone(timezone.utc)
    except (ValueError,TypeError,OverflowError):
        raise P00Error(10,'INVALID_TIMESTAMP') from None

def relative(value: str) -> str:
    require(type(value) is str and 0<len(value)<=240,10,'INVALID_RELATIVE_PATH')
    require('\\' not in value and ':' not in value and '#' not in value,10,'INVALID_RELATIVE_PATH')
    p=PurePosixPath(value)
    require(not p.is_absolute() and p.as_posix()==value and all(x not in ('','.','..') for x in value.split('/')),10,'PATH_ESCAPE')
    require(all(ord(c)>=32 and ord(c)!=127 for c in value),10,'PATH_CONTROL')
    return value

def windows_path(value: str) -> str:
    require(type(value) is str and 3<=len(value)<=240,10,'INVALID_WINDOWS_PATH')
    require(not any(ord(c)<32 or ord(c)==127 for c in value),10,'PATH_CONTROL')
    require(not any(c in value for c in '"<>|?*'),10,'PATH_SYNTAX')
    require(re.match(r'^[A-Za-z]:\\',value) is not None and '/' not in value,10,'LOCAL_ABSOLUTE_PATH_REQUIRED')
    require(':' not in value[2:] and '\\\\' not in value,10,'PATH_DEVICE_OR_ADS')
    parts=PureWindowsPath(value).parts[1:]
    require(bool(parts),10,'VOLUME_ROOT_FORBIDDEN')
    for part in parts:
        require(part not in ('.','..') and not part.endswith(('.', ' ')),10,'PATH_AMBIGUOUS')
        require(re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\..*)?',part) is None,10,'RESERVED_PATH')
    require('\\.\\' not in value and '\\..\\' not in value and not value.endswith(('\\.','\\..')),10,'PATH_ESCAPE')
    return str(PureWindowsPath(value))

def distro_name(value):
    require(type(value) is str and 1<=len(value)<=64,10,'INVALID_DISTRO_NAME')
    require(not value.startswith(('-', ' ')) and value==value.strip(),10,'INVALID_DISTRO_NAME')
    require(all(c.isalnum() or c in ' _-.' for c in value),10,'INVALID_DISTRO_NAME')
    return value

def user_name(value):
    require(type(value) is str and re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}',value) is not None,10,'INVALID_USER_NAME')
    require(value!='root',10,'NONROOT_USER_REQUIRED')
    return value

def read_json(path: Path):
    # Workspace input only. Host ACL/reparse-safe reader is not registered in this revision.
    require(not path.is_symlink() and path.is_file(),10,'INPUT_FILE_REQUIRED')
    try:
        with path.open('rb') as f: data=f.read(MAX_JSON+1)
        return loads(data)
    except OSError: raise P00Error(18,'INPUT_IO') from None
