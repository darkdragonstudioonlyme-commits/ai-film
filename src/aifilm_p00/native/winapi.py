"""Small explicit Win32 FFI. No DLL loading until WinAPI() on Windows x64.

Every API has argtypes/restype to avoid HANDLE truncation. API failures emit fixed
codes only. No shell, WSL, registry writes or installation in this module.
"""
from __future__ import annotations
import ctypes as C
import os
from contextlib import contextmanager
from dataclasses import dataclass
from ..errors import P00Error, require
from .security import Security, Ace

DWORD=C.c_uint32; WORD=C.c_uint16; BYTE=C.c_ubyte; BOOL=C.c_int32
HANDLE=C.c_void_p; LPVOID=C.c_void_p; ULONG_PTR=C.c_size_t
LPWSTR=C.c_wchar_p; LPDWORD=C.POINTER(DWORD)
INVALID_HANDLE=C.c_void_p(-1).value

class SA(C.Structure):
    _fields_=[('nLength',DWORD),('lpSecurityDescriptor',LPVOID),('bInheritHandle',BOOL)]
class FT(C.Structure):
    _fields_=[('low',DWORD),('high',DWORD)]
    @property
    def ticks(self): return self.low | (self.high << 32)
class FileInfo(C.Structure):
    _fields_=[('attributes',DWORD),('created',FT),('accessed',FT),('written',FT),
              ('volume_serial',DWORD),('size_hi',DWORD),('size_lo',DWORD),
              ('links',DWORD),('index_hi',DWORD),('index_lo',DWORD)]
class SID_AND_ATTRIBUTES(C.Structure):
    _fields_=[('Sid',LPVOID),('Attributes',DWORD)]
class ACL(C.Structure):
    _fields_=[('revision',BYTE),('sbz1',BYTE),('size',WORD),('count',WORD),('sbz2',WORD)]
class ACE_HEAD(C.Structure):
    _fields_=[('kind',BYTE),('flags',BYTE),('size',WORD)]
class MEMORYSTATUSEX(C.Structure):
    _fields_=[('length',DWORD),('load',DWORD)]+[(n,C.c_uint64) for n in
        ('total_phys','available_phys','total_page','available_page','total_virtual','available_virtual','available_extended')]
class GUID(C.Structure):
    _fields_=[('a',DWORD),('b',WORD),('c',WORD),('d',BYTE*8)]
    @classmethod
    def parse(cls,value):
        import uuid
        return cls.from_buffer_copy(uuid.UUID(value).bytes_le)
class STARTUPINFO(C.Structure):
    _fields_=[('cb',DWORD),('reserved',LPWSTR),('desktop',LPWSTR),('title',LPWSTR),
              ('x',DWORD),('y',DWORD),('xsize',DWORD),('ysize',DWORD),
              ('xchars',DWORD),('ychars',DWORD),('fill',DWORD),('flags',DWORD),
              ('show',WORD),('reserved2_len',WORD),('reserved2',LPVOID),
              ('stdin',HANDLE),('stdout',HANDLE),('stderr',HANDLE)]
class STARTUPINFOEX(C.Structure):
    _fields_=[('info',STARTUPINFO),('attributes',LPVOID)]
class PROCESS_INFORMATION(C.Structure):
    _fields_=[('process',HANDLE),('thread',HANDLE),('pid',DWORD),('tid',DWORD)]
class JOB_ACCOUNTING(C.Structure):
    _fields_=[('user',C.c_int64),('kernel',C.c_int64),('period_user',C.c_int64),
              ('period_kernel',C.c_int64),('page_faults',DWORD),('total',DWORD),
              ('active',DWORD),('terminated',DWORD)]

class WinAPI:
    def __init__(self):
        require(os.name=='nt' and C.sizeof(C.c_void_p)==8,11,'WINDOWS_X64_REQUIRED')
        self.k=C.WinDLL('kernel32',use_last_error=True)
        self.a=C.WinDLL('advapi32',use_last_error=True)
        self.s=C.WinDLL('shell32',use_last_error=True)
        self.o=C.WinDLL('ole32',use_last_error=True)
        def bind(lib,name,result,args):
            f=getattr(lib,name); f.restype=result; f.argtypes=args; return f
        self.close=bind(self.k,'CloseHandle',BOOL,[HANDLE])
        self.local_free=bind(self.k,'LocalFree',LPVOID,[LPVOID])
        self.get_current_process=bind(self.k,'GetCurrentProcess',HANDLE,[])
        self.get_current_pid=bind(self.k,'GetCurrentProcessId',DWORD,[])
        self.get_current_tid=bind(self.k,'GetCurrentThreadId',DWORD,[])
        self.get_system_directory=bind(self.k,'GetSystemDirectoryW',DWORD,[LPWSTR,DWORD])
        self.get_windows_directory=bind(self.k,'GetWindowsDirectoryW',DWORD,[LPWSTR,DWORD])
        self.get_phys_ram=bind(self.k,'GetPhysicallyInstalledSystemMemory',BOOL,[C.POINTER(C.c_uint64)])
        self.memory_status=bind(self.k,'GlobalMemoryStatusEx',BOOL,[C.POINTER(MEMORYSTATUSEX)])
        self.cpu_count=bind(self.k,'GetActiveProcessorCount',DWORD,[WORD])
        self.wow64=bind(self.k,'IsWow64Process2',BOOL,[HANDLE,C.POINTER(WORD),C.POINTER(WORD)])
        self.open_token=bind(self.a,'OpenProcessToken',BOOL,[HANDLE,DWORD,C.POINTER(HANDLE)])
        self.token_info=bind(self.a,'GetTokenInformation',BOOL,[HANDLE,C.c_int,LPVOID,DWORD,LPDWORD])
        self.sid_string=bind(self.a,'ConvertSidToStringSidW',BOOL,[LPVOID,C.POINTER(LPWSTR)])
        self.convert_sddl=bind(self.a,'ConvertStringSecurityDescriptorToSecurityDescriptorW',BOOL,[LPWSTR,DWORD,C.POINTER(LPVOID),LPDWORD])
        self.security_info=bind(self.a,'GetSecurityInfo',DWORD,[HANDLE,C.c_int,DWORD,C.POINTER(LPVOID),C.POINTER(LPVOID),C.POINTER(LPVOID),C.POINTER(LPVOID),C.POINTER(LPVOID)])
        self.sd_control=bind(self.a,'GetSecurityDescriptorControl',BOOL,[LPVOID,C.POINTER(WORD),LPDWORD])
        self.get_ace=bind(self.a,'GetAce',BOOL,[LPVOID,DWORD,C.POINTER(LPVOID)])
        self.create_mutex=bind(self.k,'CreateMutexExW',HANDLE,[C.POINTER(SA),LPWSTR,DWORD,DWORD])
        self.release_mutex=bind(self.k,'ReleaseMutex',BOOL,[HANDLE])
        self.wait=bind(self.k,'WaitForSingleObject',DWORD,[HANDLE,DWORD])
        self.create_file=bind(self.k,'CreateFileW',HANDLE,[LPWSTR,DWORD,DWORD,C.POINTER(SA),DWORD,DWORD,HANDLE])
        self.file_info=bind(self.k,'GetFileInformationByHandle',BOOL,[HANDLE,C.POINTER(FileInfo)])
        self.file_size=bind(self.k,'GetFileSizeEx',BOOL,[HANDLE,C.POINTER(C.c_int64)])
        self.read_file=bind(self.k,'ReadFile',BOOL,[HANDLE,LPVOID,DWORD,LPDWORD,LPVOID])
        self.write_file=bind(self.k,'WriteFile',BOOL,[HANDLE,LPVOID,DWORD,LPDWORD,LPVOID])
        self.seek_file=bind(self.k,'SetFilePointerEx',BOOL,[HANDLE,C.c_int64,C.POINTER(C.c_int64),DWORD])
        self.flush_file=bind(self.k,'FlushFileBuffers',BOOL,[HANDLE])
        self.final_path=bind(self.k,'GetFinalPathNameByHandleW',DWORD,[HANDLE,LPWSTR,DWORD,DWORD])
        self.file_attributes=bind(self.k,'GetFileAttributesW',DWORD,[LPWSTR])
        self.create_directory=bind(self.k,'CreateDirectoryW',BOOL,[LPWSTR,C.POINTER(SA)])
        self.move_file=bind(self.k,'MoveFileExW',BOOL,[LPWSTR,LPWSTR,DWORD])
        self.delete_file=bind(self.k,'DeleteFileW',BOOL,[LPWSTR])
        self.get_volume_path=bind(self.k,'GetVolumePathNameW',BOOL,[LPWSTR,LPWSTR,DWORD])
        self.get_volume_name=bind(self.k,'GetVolumeNameForVolumeMountPointW',BOOL,[LPWSTR,LPWSTR,DWORD])
        self.get_volume_info=bind(self.k,'GetVolumeInformationW',BOOL,[LPWSTR,LPWSTR,DWORD,LPDWORD,LPDWORD,LPDWORD,LPWSTR,DWORD])
        self.get_drive_type=bind(self.k,'GetDriveTypeW',DWORD,[LPWSTR])
        self.get_disk_free=bind(self.k,'GetDiskFreeSpaceExW',BOOL,[LPWSTR,C.POINTER(C.c_uint64),C.POINTER(C.c_uint64),C.POINTER(C.c_uint64)])
        self.known_folder=bind(self.s,'SHGetKnownFolderPath',C.c_int32,[C.POINTER(GUID),DWORD,HANDLE,C.POINTER(LPWSTR)])
        self.com_free=bind(self.o,'CoTaskMemFree',None,[LPVOID])
        self.create_pipe=bind(self.k,'CreatePipe',BOOL,[C.POINTER(HANDLE),C.POINTER(HANDLE),C.POINTER(SA),DWORD])
        self.handle_flags=bind(self.k,'SetHandleInformation',BOOL,[HANDLE,DWORD,DWORD])
        self.create_process=bind(self.k,'CreateProcessW',BOOL,[LPWSTR,LPWSTR,C.POINTER(SA),C.POINTER(SA),BOOL,DWORD,LPVOID,LPWSTR,LPVOID,C.POINTER(PROCESS_INFORMATION)])
        self.process_times=bind(self.k,'GetProcessTimes',BOOL,[HANDLE,C.POINTER(FT),C.POINTER(FT),C.POINTER(FT),C.POINTER(FT)])
        self.process_exit=bind(self.k,'GetExitCodeProcess',BOOL,[HANDLE,LPDWORD])
        self.resume_thread=bind(self.k,'ResumeThread',DWORD,[HANDLE])
        self.terminate_process=bind(self.k,'TerminateProcess',BOOL,[HANDLE,DWORD])
        self.create_job=bind(self.k,'CreateJobObjectW',HANDLE,[C.POINTER(SA),LPWSTR])
        self.assign_job=bind(self.k,'AssignProcessToJobObject',BOOL,[HANDLE,HANDLE])
        self.query_job=bind(self.k,'QueryInformationJobObject',BOOL,[HANDLE,C.c_int,LPVOID,DWORD,LPDWORD])
        self.init_attributes=bind(self.k,'InitializeProcThreadAttributeList',BOOL,[LPVOID,DWORD,DWORD,C.POINTER(C.c_size_t)])
        self.update_attributes=bind(self.k,'UpdateProcThreadAttribute',BOOL,[LPVOID,DWORD,ULONG_PTR,LPVOID,C.c_size_t,LPVOID,LPVOID])
        self.delete_attributes=bind(self.k,'DeleteProcThreadAttributeList',None,[LPVOID])
        self.open_process=bind(self.k,'OpenProcess',HANDLE,[DWORD,BOOL,DWORD])

    @staticmethod
    def ok(value,reason='WIN32_IO',code=18):
        require(bool(value),code,reason); return value

    @contextmanager
    def handle(self,handle):
        require(handle not in (None,0,INVALID_HANDLE),18,'INVALID_NATIVE_HANDLE')
        try: yield handle
        finally: self.close(handle)

    @contextmanager
    def attributes(self,sddl,inherit=False):
        ptr=LPVOID()
        self.ok(self.convert_sddl(sddl,1,C.byref(ptr),None),'SDDL_INVALID',12)
        try:
            value=SA(C.sizeof(SA),ptr,int(inherit))
            yield value
        finally: self.local_free(ptr)

    def string_sid(self,ptr):
        output=LPWSTR(); self.ok(self.sid_string(ptr,C.byref(output)),'SID_QUERY',12)
        try: return output.value
        finally: self.local_free(C.cast(output,LPVOID))

    def security(self,handle,kind=1):
        """kind SE_FILE_OBJECT=1, SE_REGISTRY_KEY=4, SE_KERNEL_OBJECT=6."""
        owner=LPVOID(); dacl=LPVOID(); sd=LPVOID()
        code=self.security_info(handle,kind,0x1|0x4,C.byref(owner),None,C.byref(dacl),None,C.byref(sd))
        require(code==0,12,'SECURITY_QUERY_DENIED')
        try:
            control=WORD(); revision=DWORD()
            self.ok(self.sd_control(sd,C.byref(control),C.byref(revision)),'SECURITY_DESCRIPTOR_INVALID',12)
            aces=[]
            if dacl.value:
                acl=C.cast(dacl,C.POINTER(ACL)).contents
                require(acl.count<=1024,12,'ACL_TOO_LARGE')
                for i in range(acl.count):
                    ptr=LPVOID(); self.ok(self.get_ace(dacl,i,C.byref(ptr)),'ACE_QUERY',12)
                    header=C.cast(ptr,C.POINTER(ACE_HEAD)).contents
                    require(header.kind in (0,1) and header.size>=12,12,'UNSUPPORTED_ACE')
                    mask=C.cast(ptr.value+4,C.POINTER(DWORD)).contents.value
                    trustee=self.string_sid(LPVOID(ptr.value+8))
                    aces.append(Ace(header.kind,header.flags,mask,trustee))
            return Security(self.string_sid(owner),bool(control.value&4),not bool(dacl.value),bool(control.value&0x1000),tuple(aces))
        finally: self.local_free(sd)

    def principal(self):
        token=HANDLE(); self.ok(self.open_token(self.get_current_process(),0x8,C.byref(token)),'TOKEN_QUERY',12)
        with self.handle(token):
            count=DWORD(); self.token_info(token,1,None,0,C.byref(count))
            require(0<count.value<=65536,12,'TOKEN_SIZE')
            buf=C.create_string_buffer(count.value)
            self.ok(self.token_info(token,1,buf,len(buf),C.byref(count)),'TOKEN_QUERY',12)
            value=C.cast(buf,C.POINTER(SID_AND_ATTRIBUTES)).contents
            identity=self.string_sid(value.Sid)
            elevation=DWORD(); self.ok(self.token_info(token,20,C.byref(elevation),4,C.byref(count)),'TOKEN_ELEVATION',12)
        process_machine=WORD(); native_machine=WORD()
        self.ok(self.wow64(self.get_current_process(),C.byref(process_machine),C.byref(native_machine)),'ARCH_QUERY',11)
        require(process_machine.value==0 and native_machine.value==0x8664,11,'WINDOWS_X64_REQUIRED')
        return {'execution_sid':identity,'elevated':bool(elevation.value),'architecture':'x64'}

    def system_directory(self):
        buf=C.create_unicode_buffer(32768)
        length=self.get_system_directory(buf,len(buf))
        require(0<length<len(buf),11,'SYSTEM_DIRECTORY_QUERY')
        return buf.value

    def program_data(self):
        # Fixed FOLDERID_ProgramData, not an overrideable environment variable.
        guid=GUID.parse('62AB5D82-FDC1-4DC3-A9DD-070D1D495D97'); ptr=LPWSTR()
        require(self.known_folder(C.byref(guid),0,None,C.byref(ptr))==0,11,'PROGRAMDATA_QUERY')
        try: return ptr.value
        finally: self.com_free(C.cast(ptr,LPVOID))

    def resources(self):
        installed=C.c_uint64(); self.ok(self.get_phys_ram(C.byref(installed)),'PHYSICAL_RAM_QUERY',11)
        memory=MEMORYSTATUSEX(); memory.length=C.sizeof(memory)
        self.ok(self.memory_status(C.byref(memory)),'MEMORY_QUERY',11)
        cpu=self.cpu_count(0xffff); require(cpu>0,11,'CPU_QUERY')
        return {'installed_ram_bytes':installed.value*1024,'available_ram_bytes':memory.available_phys,'logical_cpu':cpu}

    def info(self,handle):
        value=FileInfo(); self.ok(self.file_info(handle,C.byref(value)),'FILE_IDENTITY_QUERY',16)
        return {'attributes':value.attributes,'volume_serial':value.volume_serial,
                'file_id':(value.index_hi<<32)|value.index_lo,'bytes':(value.size_hi<<32)|value.size_lo,
                'links':value.links,'created':value.created.ticks,'written':value.written.ticks}

    def process_start(self,handle):
        a=FT(); b=FT(); c=FT(); d=FT()
        self.ok(self.process_times(handle,C.byref(a),C.byref(b),C.byref(c),C.byref(d)),'PROCESS_WITNESS',11)
        return a.ticks

    def read(self,handle,cap):
        parts=[]; total=0
        while total<=cap:
            size=min(65536,cap+1-total); buf=C.create_string_buffer(size); read=DWORD()
            ok=self.read_file(handle,buf,size,C.byref(read),None)
            if not ok:
                require(C.get_last_error()==109,18,'HANDLE_READ')
                break
            if not read.value: break
            parts.append(buf.raw[:read.value]); total+=read.value
        require(total<=cap,22,'READ_CAP_EXCEEDED')
        return b''.join(parts)

    def write(self,handle,data):
        offset=0
        while offset<len(data):
            chunk=data[offset:offset+65536]; buf=C.create_string_buffer(chunk); written=DWORD()
            self.ok(self.write_file(handle,buf,len(chunk),C.byref(written),None),'HANDLE_WRITE')
            require(written.value>0,18,'HANDLE_SHORT_WRITE'); offset+=written.value
        self.ok(self.flush_file(handle),'HANDLE_FLUSH')
