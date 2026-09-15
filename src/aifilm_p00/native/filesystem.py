"""Handle-pinned Windows paths and bounded protected I/O.

Ancestors are opened without FILE_SHARE_DELETE and held through the operation.
A leaf read denies write/delete sharing, preventing a hash-to-use rename/write.
The trusted administrator threat model is the one stated by D00-02/07/11.
"""
from __future__ import annotations
import ctypes as C
from contextlib import contextmanager, ExitStack
from dataclasses import dataclass
from pathlib import PureWindowsPath
from ..codec import windows_path, sha256, canonical, loads
from ..errors import require, P00Error
from .security import check_security, ADMIN_OWNERS, metadata_sddl
from .winapi import DWORD, HANDLE, INVALID_HANDLE

READ=0x80000000; WRITE=0x40000000; READ_CONTROL=0x00020000
SHARE_READ=1; SHARE_WRITE=2
OPEN_EXISTING=3; CREATE_NEW=1
FLAGS=0x00200000|0x02000000  # OPEN_REPARSE_POINT | BACKUP_SEMANTICS
REPARSE=0x400; DIRECTORY=0x10
ROOT_NAME='AI-FILM-P00-HOST-ADMISSION'


def same_path(a,b):
    return str(PureWindowsPath(a)).casefold()==str(PureWindowsPath(b)).casefold()


def normalized_handle_path(value):
    require(value.startswith('\\\\?\\') and not value.startswith('\\\\?\\UNC\\'),16,'NONLOCAL_FINAL_PATH')
    return value[4:]


@dataclass
class Pinned:
    path: str
    handle: object
    identity: dict
    volume: dict


class WindowsPaths:
    def __init__(self,api,operators):
        self.api=api; self.operators=frozenset(operators)
        self.writers=ADMIN_OWNERS|self.operators
        self.root=windows_path(api.program_data()+'\\'+ROOT_NAME)

    def directory_exists(self,path):
        """Existence hint only; caller must still pin/validate the opened root.

        Access denied, unsupported paths and reparse points are not absence.
        CREATE_NEW remains the authority for a later initialization race.
        """
        path=windows_path(path)
        attrs=self.api.file_attributes(path)
        if attrs==0xffffffff:
            error=C.get_last_error()
            if error in (2,3):return False
            raise P00Error(12 if error==5 else 18,'PATH_STAT_FAILED')
        require(not attrs&REPARSE,12,'REPARSE_POINT_FORBIDDEN')
        require(bool(attrs&DIRECTORY),16,'PATH_KIND_MISMATCH')
        return True

    def file_exists(self,path):
        """Observed regular-file presence; denied/unknown/reparse is never absence."""
        path=windows_path(path);attrs=self.api.file_attributes(path)
        if attrs==0xffffffff:
            error=C.get_last_error()
            if error in (2,3):return False
            raise P00Error(12 if error==5 else 18,'PATH_STAT_FAILED')
        require(not attrs&REPARSE,12,'REPARSE_POINT_FORBIDDEN')
        require(not attrs&DIRECTORY,16,'PATH_KIND_MISMATCH')
        return True

    def volume(self,path):
        mount=C.create_unicode_buffer(32768)
        self.api.ok(self.api.get_volume_path(path,mount,len(mount)),'VOLUME_PATH',11)
        name=C.create_unicode_buffer(1024)
        self.api.ok(self.api.get_volume_name(mount.value,name,len(name)),'VOLUME_ID',11)
        fs=C.create_unicode_buffer(128); serial=DWORD(); maxlen=DWORD(); flags=DWORD()
        self.api.ok(self.api.get_volume_info(mount.value,None,0,C.byref(serial),C.byref(maxlen),C.byref(flags),fs,len(fs)),'VOLUME_INFORMATION',11)
        free=C.c_uint64(); total=C.c_uint64(); actual=C.c_uint64()
        self.api.ok(self.api.get_disk_free(mount.value,C.byref(free),C.byref(total),C.byref(actual)),'VOLUME_FREE',11)
        kind=self.api.get_drive_type(mount.value)
        return {'volume_id':'v_'+sha256(name.value.casefold().encode())[:32],
                'volume_guid':name.value,'filesystem':fs.value,'drive_type':kind,
                'free_bytes':free.value,'total_bytes':total.value,'flags':flags.value,
                'serial':serial.value,'mount':mount.value}

    def _open(self,path,access=READ_CONTROL,share=SHARE_READ|SHARE_WRITE,creation=OPEN_EXISTING,sa=None):
        handle=self.api.create_file(path,access,share,sa,creation,FLAGS,None)
        if handle in (None,0,INVALID_HANDLE):
            code=C.get_last_error()
            raise P00Error(12 if code==5 else 21 if code in (32,33) else 18,'PATH_OPEN_FAILED')
        return handle

    def _validate_handle(self,h,path,directory):
        info=self.api.info(h)
        require(not info['attributes']&REPARSE,12,'REPARSE_POINT_FORBIDDEN')
        require(bool(info['attributes']&DIRECTORY)==directory,16,'PATH_KIND_MISMATCH')
        buf=C.create_unicode_buffer(32768)
        count=self.api.final_path(h,buf,len(buf),0)
        require(0<count<len(buf) and same_path(normalized_handle_path(buf.value),path),16,'CANONICAL_PATH_MISMATCH')
        if not directory:
            require(info['links']==1,12,'HARDLINK_FORBIDDEN')
        return info

    @contextmanager
    def ancestors(self,path):
        path=windows_path(path); parts=PureWindowsPath(path)
        with ExitStack() as stack:
            # Include volume root. No caller-supplied volume aliases/junctions.
            current=parts.anchor
            for component in ('',*parts.parts[1:-1]):
                if component: current=str(PureWindowsPath(current)/component)
                h=self._open(current)
                stack.callback(self.api.close,h)
                self._validate_handle(h,current,True)
            yield path

    @contextmanager
    def pin(self,path,*,directory=False,confidential=True,owners=None,writers=None,
            protected=False,write=False):
        path=windows_path(path)
        with self.ancestors(path):
            access=READ_CONTROL|(0 if directory else READ)|(WRITE if write else 0)
            h=self._open(path,access,SHARE_READ if not directory else SHARE_READ|SHARE_WRITE)
            with self.api.handle(h):
                identity=self._validate_handle(h,path,directory)
                sec=self.api.security(h)
                check_security(sec,owners=frozenset(owners or self.writers),
                               writers=frozenset(writers or self.writers),
                               readers=self.writers,confidential=confidential,require_protected=protected)
                volume=self.volume(path)
                require(volume['filesystem']=='NTFS' and volume['drive_type']==3,11,'LOCAL_NTFS_REQUIRED')
                yield Pinned(path,h,identity,volume)
                # Detect modifications through a preexisting writable mapped
                # handle too. Successful operations must recheck bytes as needed.
                final=self.api.info(h)
                require(final['file_id']==identity['file_id'] and final['volume_serial']==identity['volume_serial'],16,'FILE_IDENTITY_DRIFT')

    def read_blob(self,path,*,cap=10*1024**2,expected=None):
        with self.pin(path) as pinned:
            require(pinned.identity['bytes']<=cap,22,'READ_CAP_EXCEEDED')
            data=self.api.read(pinned.handle,cap)
            if expected is not None: require(sha256(data)==expected,15,'ARTIFACT_HASH_MISMATCH')
            return data

    @contextmanager
    def pinned_payload(self,path,expected,expected_bytes):
        with self.pin(path,confidential=False) as value:
            require(value.identity['bytes']==expected_bytes,15,'PAYLOAD_SIZE_MISMATCH')
            import hashlib
            h=hashlib.sha256(); total=0
            while True:
                buf=C.create_string_buffer(65536); count=DWORD()
                self.api.ok(self.api.read_file(value.handle,buf,len(buf),C.byref(count),None),'PAYLOAD_READ')
                if not count.value: break
                total+=count.value; h.update(buf.raw[:count.value])
            require(total==expected_bytes and h.hexdigest()==expected,15,'PAYLOAD_HASH_MISMATCH')
            # Keep read-only leaf + ancestor handles across native execution.
            yield value

    @contextmanager
    def pinned_executable(self,path,expected,expected_bytes):
        """Pin exact executable bytes with an administrator-owned write boundary.

        Unlike ordinary project payloads, a native executable is never allowed to
        be operator-writable. The leaf and ancestors remain open across process
        creation/wait, preventing a hash-to-execute rename race.
        """
        from .security import ADMIN_OWNERS
        with self.pin(path,confidential=False,owners=ADMIN_OWNERS,writers=ADMIN_OWNERS) as value:
            require(value.identity['bytes']==expected_bytes,15,'EXECUTABLE_SIZE_MISMATCH')
            import hashlib
            h=hashlib.sha256(); total=0
            while True:
                buf=C.create_string_buffer(65536); count=DWORD()
                self.api.ok(self.api.read_file(value.handle,buf,len(buf),C.byref(count),None),'EXECUTABLE_READ')
                if not count.value: break
                total+=count.value; h.update(buf.raw[:count.value])
            require(total==expected_bytes and h.hexdigest()==expected,15,'EXECUTABLE_HASH_MISMATCH')
            yield value

    def create_directory(self,path):
        path=windows_path(path)
        with self.ancestors(path),self.api.attributes(metadata_sddl(self.operators)) as attr:
            self.api.ok(self.api.create_directory(path,C.byref(attr)),'DIRECTORY_CREATE',18)
        # Never "adopt" an existing directory after an AlreadyExists error.
        with self.pin(path,directory=True,protected=True): pass

    def write_new(self,path,data):
        path=windows_path(path)
        with self.ancestors(path),self.api.attributes(metadata_sddl(self.operators)) as attr:
            h=self._open(path,READ|WRITE|READ_CONTROL,SHARE_READ,CREATE_NEW,C.byref(attr))
            with self.api.handle(h):
                self._validate_handle(h,path,False)
                check_security(self.api.security(h),owners=self.writers,writers=self.writers,
                               readers=self.writers,confidential=True,require_protected=True)
                self.api.write(h,data)
        return sha256(data)

    def append_flush(self,path,data):
        with self.pin(path,write=True,protected=True) as pinned:
            self.api.ok(self.api.seek_file(pinned.handle,0,None,2),'APPEND_SEEK')
            self.api.write(pinned.handle,data)

    def publish_new(self,path,data,*,pending_path):
        """Create exact staged bytes then move without replace; never invent temp identity."""
        path=windows_path(path);pending_path=windows_path(pending_path)
        parent=str(PureWindowsPath(path).parent)
        require(not same_path(path,pending_path) and same_path(parent,str(PureWindowsPath(pending_path).parent)),
                16,'OUTPUT_PENDING_SCOPE')
        with self.pin(parent,directory=True,protected=True):
            self.write_new(pending_path,data)
            # WRITE_THROUGH, deliberately no REPLACE_EXISTING flag.
            self.api.ok(self.api.move_file(pending_path,path,0x8),'OUTPUT_PUBLISH',18)
            require(self.read_blob(path,cap=max(len(data),1))==data,15,'OUTPUT_READBACK_MISMATCH')
        return sha256(data)
