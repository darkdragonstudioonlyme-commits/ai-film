"""Durable storage exercised in an isolated POSIX workspace only.
Windows ACL, handle/reparse checks and host-global root initialization remain pending.
This storage class is not wired to native entrypoints.
"""
import os
from pathlib import Path
from uuid import uuid4
from .codec import canonical,loads,sha256
from .errors import P00Error,require

class FileJournal:
    def __init__(self,root:Path):
        require(os.name=='posix',11,'WINDOWS_DURABILITY_ADAPTER_PENDING')
        self.root=root
        require(root.is_dir() and not root.is_symlink(),12,'JOURNAL_ROOT_NOT_PREPARED')
        self.fence_path=root/'fence.json'; self.events_path=root/'events.jsonl'
        self._validated_root=root.resolve(strict=True)

    def _path(self,path:Path):
        require(self.root.resolve(strict=True)==self._validated_root and not self.root.is_symlink() and not path.is_symlink(),16,'JOURNAL_PATH_DRIFT')
        require(path.parent.resolve(strict=True)==self._validated_root,16,'JOURNAL_PATH_ESCAPE')

    def _sync_root(self):
        if os.name!='posix':
            raise P00Error(11,'WINDOWS_DURABILITY_ADAPTER_PENDING')
        fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)

    def _atomic(self,path,data):
        self._path(path); tmp=self.root/(uuid4().hex+'.tmp')
        try:
            fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
            self._path(path); os.replace(tmp,path); self._sync_root()
        except P00Error: raise
        except OSError: raise P00Error(18,'JOURNAL_IO') from None
        # Never erase arbitrary leftover artifacts on failure. They remain protected.

    def load_fence(self):
        self._path(self.fence_path)
        if not self.fence_path.exists(): return None
        try:
            fd=os.open(self.fence_path,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd,'rb') as f: raw=f.read(10*1024**2+1)
            wrapper=loads(raw)
            require(wrapper['sha256']==sha256(canonical(wrapper['record'])),15,'FENCE_INTEGRITY')
            return wrapper['record']
        except (KeyError,TypeError): raise P00Error(15,'FENCE_INVALID') from None
        except OSError: raise P00Error(18,'JOURNAL_IO') from None

    def write_fence(self,record):
        self._atomic(self.fence_path,canonical({'record':record,'sha256':sha256(canonical(record))}))

    def read_events(self):
        self._path(self.events_path)
        if not self.events_path.exists(): return []
        try:
            fd=os.open(self.events_path,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd,'rb') as f: raw=f.read(10*1024**2+1)
            require(len(raw)<=10*1024**2 and (not raw or raw.endswith(b'\n')),15,'JOURNAL_TRUNCATED')
            rows=[]; prev=None
            for line in raw.splitlines():
                wrapper=loads(line)
                require(wrapper['prev']==prev and wrapper['sha256']==sha256(canonical({'event':wrapper['event'],'prev':prev})),15,'JOURNAL_CHAIN')
                prev=wrapper['sha256']; rows.append(wrapper)
            return rows
        except (KeyError,TypeError): raise P00Error(15,'JOURNAL_INVALID') from None
        except OSError: raise P00Error(18,'JOURNAL_IO') from None

    def append_event(self,event):
        rows=self.read_events(); prev=rows[-1]['sha256'] if rows else None
        record={'event':event,'prev':prev}; record['sha256']=sha256(canonical(record))
        self._path(self.events_path)
        try:
            fd=os.open(self.events_path,os.O_WRONLY|os.O_APPEND|os.O_CREAT|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'ab') as f: f.write(canonical(record)+b'\n'); f.flush(); os.fsync(f.fileno())
            self._sync_root()
        except P00Error: raise
        except OSError: raise P00Error(18,'JOURNAL_IO') from None

    def clear_fence(self):
        fence=self.load_fence()
        require(fence is not None and fence.get('state') in ('TERMINAL','SAFE_PAUSE'),21,'FENCE_NOT_TERMINAL')
        # Keep a sealed terminal fence, rather than deleting recovery evidence.
        archived=self.root/('terminal-'+sha256(canonical(fence))+'.json')
        self._atomic(archived,canonical(fence))
        self.append_event({'kind':'FENCE_RELEASE','fence_digest':sha256(canonical(fence))})
        try: self.fence_path.unlink(); self._sync_root()
        except OSError: raise P00Error(18,'JOURNAL_IO') from None
