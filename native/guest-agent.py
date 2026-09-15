#!/usr/bin/python3
"""Fixed isolated-stdlib guest agent; data is a bounded base64 argument.

Never import this file in author tests: it is a target-side executable. The host
invokes python3 -I -S -B - <request> with THESE exact bytes on stdin. It never
installs Python or dependencies. No arbitrary commands, shell, environment dump,
credential collection, repair, automatic delete, or overwritten sentinel.
"""
import base64
import hashlib
import json
import os
import pwd
import re
import stat
import subprocess
import sys
import time

CAP = 10 * 1024 * 1024

class Block(Exception):
    def __init__(self, code, reason): self.code, self.reason = code, reason

def need(value, code, reason):
    if not value: raise Block(code, reason)

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def unique(pairs):
    out = {}
    for k, v in pairs:
        need(k not in out, 10, 'DUPLICATE_KEY'); out[k] = v
    return out

def request():
    need(len(sys.argv) == 2 and len(sys.argv[1]) <= 20000, 10, 'INPUT_CAP')
    try:
        raw = base64.b64decode(sys.argv[1], validate=True)
        value = json.loads(raw, object_pairs_hook=unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(Block(10,'INVALID_NUMBER')))
    except (ValueError, UnicodeError): raise Block(10, 'INPUT_SCHEMA')
    need(type(value) is dict and set(value) <= {'operation','user','workspace','identity','sentinel','critical_files'}, 10, 'INPUT_SCHEMA')
    need({'operation','user'} <= set(value), 10, 'INPUT_SCHEMA')
    need(value['operation'] in {'INVENTORY','ADMIN','WORKSPACE','ASSERT_CONTENT'}, 10, 'OPERATION_SCOPE')
    user = value['user']
    need(type(user) is str and re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', user) and user != 'root', 10, 'USER_SCOPE')
    need(os.geteuid() > 0 and pwd.getpwuid(os.geteuid()).pw_name == user, 12, 'WRONG_GUEST_PRINCIPAL')
    return value

def safe_path(path):
    need(type(path) is str and path.startswith('/') and '\x00' not in path and '\n' not in path and len(path) <= 4096, 10, 'GUEST_PATH')
    parts = path.split('/')[1:]
    need(parts and all(p and p not in ('.','..') for p in parts), 10, 'GUEST_PATH')
    need(not any(p in ('.ssh','.gnupg','.env') or p.startswith('.env.') for p in parts)
         and path not in ('/etc/shadow','/etc/gshadow'), 12, 'SENSITIVE_PATH_FORBIDDEN')
    return parts

def parent_fd(path):
    parts = safe_path(path)
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for name in parts[:-1]:
            nxt = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd); fd = nxt
        return fd, parts[-1]
    except BaseException:
        os.close(fd); raise

def bounded_file(path, cap=CAP):
    parent, name = parent_fd(path)
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)
        try:
            first = os.fstat(fd)
            need(stat.S_ISREG(first.st_mode) and first.st_nlink == 1, 12, 'UNSAFE_FILE_KIND')
            need(first.st_size <= cap, 22, 'FILE_CAP')
            chunks, count = [], 0
            while True:
                chunk = os.read(fd, min(65536, cap + 1 - count))
                if not chunk: break
                count += len(chunk); need(count <= cap, 22, 'FILE_CAP'); chunks.append(chunk)
            last = os.fstat(fd)
            need((first.st_dev,first.st_ino,first.st_size,first.st_mtime_ns,first.st_ctime_ns) ==
                 (last.st_dev,last.st_ino,last.st_size,last.st_mtime_ns,last.st_ctime_ns), 16, 'FILE_CHANGED_DURING_READ')
            return b''.join(chunks), first
        finally: os.close(fd)
    finally: os.close(parent)

def text(path):
    # /proc pseudo-files are intentionally separate from protected regular files.
    with open(path, 'rb') as f:
        raw = f.read(65537); need(len(raw) <= 65536, 22, 'PROC_CAP')
    return raw.decode('utf-8')

def inventory(user):
    account = pwd.getpwnam(user)
    release_path='/etc/os-release'
    if stat.S_ISLNK(os.lstat(release_path).st_mode):
        need(os.readlink(release_path) in ('../usr/lib/os-release','/usr/lib/os-release'),12,'OS_RELEASE_LINK')
        release_path='/usr/lib/os-release'
    raw, _ = bounded_file(release_path,65536)
    release = {}
    for line in raw.decode('utf-8').splitlines():
        if '=' in line:
            k, v = line.split('=',1)
            if k in ('ID','VERSION_ID'):
                need(k not in release, 15, 'OS_RELEASE_DUPLICATE')
                release[k] = v.strip('"\'')
    memory = {line.split(':',1)[0]:int(line.split(':',1)[1].strip().split()[0]) * 1024
              for line in text('/proc/meminfo').splitlines() if line.startswith(('MemTotal:','MemAvailable:'))}
    proc = text('/proc/1/stat'); tail = proc.rsplit(')',1)
    need(len(tail) == 2 and len(tail[1].split()) >= 20, 15, 'PID1_WITNESS')
    info = os.statvfs(account.pw_dir)
    try: conf, _ = bounded_file('/etc/wsl.conf', 1024*1024); conf_hash = hashlib.sha256(conf).hexdigest()
    except FileNotFoundError: conf_hash = 'ABSENT'
    return {'uid':os.geteuid(),'gid':os.getegid(),'user':user,'home':account.pw_dir,
        'home_access_writable':os.access(account.pw_dir,os.W_OK),
        'os_id':release.get('ID'),'version_id':release.get('VERSION_ID'),
        'architecture':os.uname().machine,'kernel':os.uname().release,
        'kernel_boot_id':text('/proc/sys/kernel/random/boot_id').strip(),
        'pid1_start_ticks':int(tail[1].split()[19]),'pid1_comm':text('/proc/1/comm').strip(),
        'wsl_conf_sha256':conf_hash,
        'resources':{'logical_cpu':os.cpu_count(),'mem_total_bytes':memory['MemTotal'],
                     'mem_available_bytes':memory['MemAvailable'],'fs_available_bytes':info.f_bavail*info.f_frsize}}

def file_assert(path, expected):
    need(type(expected) is dict and set(expected)=={'sha256','bytes','uid','gid','mode'}, 10, 'CONTENT_EXPECTATION')
    raw, info = bounded_file(path)
    actual = {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'uid':info.st_uid,
              'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode)}
    need(actual == expected, 19, 'CONTENT_MISMATCH')
    return {'path':path, **actual, 'device':info.st_dev, 'inode':info.st_ino}

def workspace(req):
    path = req.get('workspace'); safe_path(path)
    home = pwd.getpwnam(req['user']).pw_dir
    need(os.path.dirname(path) == home, 12, 'WORKSPACE_NOT_HOME_CHILD')
    identity = req.get('identity'); sentinel = req.get('sentinel')
    need(type(identity) is dict and set(identity)=={'project','owner_uid','source_identity','nonce'},10,'WORKSPACE_IDENTITY')
    need(identity['project']=='AI-FILM-SERVER' and identity['owner_uid']==os.geteuid(),12,'WORKSPACE_IDENTITY')
    need(type(sentinel) is dict and set(sentinel)=={'data_base64','sha256'},10,'SENTINEL_SCHEMA')
    raw = base64.b64decode(sentinel['data_base64'],validate=True)
    need(len(raw)<=65536 and hashlib.sha256(raw).hexdigest()==sentinel['sha256'],15,'SENTINEL_BYTES')
    marker = canonical(identity)
    parent, name = parent_fd(path)
    created = False
    try:
        # Unknown existing directory is never adopted by name alone. Exact
        # authenticated identity + directory/file ownership/mode are required.
        try: os.mkdir(name,0o700,dir_fd=parent); created=True; os.fsync(parent)
        except FileExistsError: pass
        fd = os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        try:
            st = os.fstat(fd)
            need(st.st_uid==os.geteuid() and stat.S_IMODE(st.st_mode)==0o700,12,'WORKSPACE_OWNERSHIP')
            if not created:
                previous, prev = bounded_file(path+'/ownership.json',65536)
                need(previous==marker and prev.st_uid==os.geteuid() and stat.S_IMODE(prev.st_mode)==0o600,16,'WORKSPACE_COLLISION')
            for leaf, data in [('ownership.json',marker),('sentinel.bin',raw)]:
                try:
                    out = os.open(leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=fd)
                except FileExistsError:
                    actual, st = bounded_file(path+'/'+leaf,65536)
                    need(actual==data and st.st_uid==os.geteuid() and stat.S_IMODE(st.st_mode)==0o600,16,'WORKSPACE_COLLISION')
                    continue
                try:
                    offset=0
                    while offset<len(data):
                        count=os.write(out,data[offset:]);need(count>0,18,'SHORT_WRITE');offset+=count
                    os.fsync(out)
                finally: os.close(out)
            os.fsync(fd)
        finally: os.close(fd)
    finally: os.close(parent)
    return {'created':created,'workspace':path,'sentinel':file_assert(path+'/sentinel.bin',
            {'sha256':sentinel['sha256'],'bytes':len(raw),'uid':os.geteuid(),'gid':os.getegid(),'mode':0o600})}

def main():
    req=request(); op=req['operation']; started=time.monotonic()
    if op=='INVENTORY': actual=inventory(req['user'])
    elif op=='WORKSPACE': actual=workspace(req)
    elif op=='ASSERT_CONTENT':
        rows=req.get('critical_files')
        need(type(rows) is list and 0<len(rows)<=64,10,'CRITICAL_LIST')
        need(len({r['path'] for r in rows})==len(rows),10,'CRITICAL_DUPLICATE')
        actual={'files':[file_assert(r['path'],r['expected']) for r in rows]}
    elif op=='ADMIN':
        # Never prompt, change sudo policy, or treat group membership as proof.
        try:
            result=subprocess.run(['/usr/bin/sudo','-n','/usr/bin/id','-u'],stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=10,
                                  env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LC_ALL':'C'},check=False)
            actual={'admin_ready':result.returncode==0 and result.stdout==b'0\n',
                    'procedure':'SUDO_NONINTERACTIVE_ID','native_exit':result.returncode}
        except (FileNotFoundError,subprocess.TimeoutExpired):
            actual={'admin_ready':False,'procedure':'SUDO_NONINTERACTIVE_ID','native_exit':None}
    payload={'schema_version':1,'operation':op,'status':'OBSERVED','actual':actual,
             'duration_ms':int((time.monotonic()-started)*1000)}
    out=canonical(payload);need(len(out)<=CAP,22,'OUTPUT_CAP')
    sys.stdout.buffer.write(out+b'\n');return 0

if __name__=='__main__':
    try: code=main()
    except Block as error:
        code=error.code;sys.stdout.buffer.write(canonical({'status':'BLOCKED','reason':error.reason,'exit':code})+b'\n')
    except (OSError,ValueError,KeyError,TypeError,UnicodeError):
        code=18;sys.stdout.buffer.write(b'{"status":"BLOCKED","reason":"GUEST_AGENT_ERROR","exit":18}\n')
    raise SystemExit(code)
