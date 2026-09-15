"""Native suspended-process supervision with bounded pipe capture.

Create suspended -> assign job -> persist witness callback -> resume. A timeout
never kills a mutating process or proves service-side completion. The caller
keeps its durable fence. Job has deliberately NO KILL_ON_JOB_CLOSE limit.
"""
from __future__ import annotations
import ctypes as C
from dataclasses import dataclass
from threading import Thread,Lock
import subprocess
import time
from uuid import uuid4
from ..codec import windows_path,token,sha256
from ..errors import require,P00Error
from .winapi import (SA,HANDLE,DWORD,STARTUPINFOEX,PROCESS_INFORMATION,
                     JOB_ACCOUNTING)

CAP=10*1024**2
CREATE_SUSPENDED=4
EXTENDED_STARTUPINFO_PRESENT=0x80000
CREATE_UNICODE_ENVIRONMENT=0x400
CREATE_NO_WINDOW=0x08000000
PROC_THREAD_ATTRIBUTE_HANDLE_LIST=0x20002


@dataclass(frozen=True)
class Command:
    argv:tuple[str,...]
    action_id:str
    timeout_seconds:int
    stdin:bytes=b''
    mutation:bool=False

    def validate(self):
        require(type(self.argv) is tuple and bool(self.argv) and len(self.argv)<=64,10,'ARGUMENT_VECTOR')
        windows_path(self.argv[0]); token(self.action_id)
        require(type(self.timeout_seconds) is int and 1<=self.timeout_seconds<=7200,10,'COMMAND_TIMEOUT')
        require(type(self.stdin) is bytes and len(self.stdin)<=1024**2,10,'STDIN_CAP')
        for arg in self.argv:
            require(type(arg) is str and '\0' not in arg and '\r' not in arg and '\n' not in arg,10,'ARGUMENT_CONTROL')
        require(len(subprocess.list2cmdline(self.argv))<32767,10,'COMMAND_LINE_CAP')


@dataclass(frozen=True)
class ProcessResult:
    exit_code:int
    stdout:bytes
    stderr:bytes
    stdout_eof:bool
    stderr_eof:bool
    truncated:bool
    duration_ms:int
    native_witness:dict
    tree_terminal:bool
    # Does not imply MSI/DISM/WSL service-side writes have ended.
    service_terminal:bool=False


class Capture:
    """Drain without retaining arbitrary-sized native output in memory."""
    def __init__(self,cap=CAP):
        self.cap=cap; self.parts=[]; self.kept=0; self.seen=0
        self.eof=False; self.error=False; self.lock=Lock()
    def feed(self,data):
        with self.lock:
            self.seen+=len(data)
            remaining=max(0,self.cap-self.kept)
            if remaining:
                part=data[:remaining];self.parts.append(part);self.kept+=len(part)
    @property
    def truncated(self): return self.seen>self.cap
    def bytes(self):
        with self.lock:return b''.join(self.parts)


class NativeSupervisor:
    def __init__(self,api,paths,guard,*,require_executable_trust=False):
        self.api=api; self.paths=paths; self.guard=guard
        self.require_executable_trust=bool(require_executable_trust)
        self.executable_trust=None

    def set_executable_trust(self,value):
        require(value is not None and callable(getattr(value,'pin',None)),15,'EXECUTABLE_TRUST_ADAPTER')
        self.executable_trust=value

    def _pipe(self):
        read=HANDLE();write=HANDLE();attr=SA(C.sizeof(SA),None,1)
        self.api.ok(self.api.create_pipe(C.byref(read),C.byref(write),C.byref(attr),65536),'PIPE_CREATE')
        return read.value,write.value

    def _drain(self,handle,capture):
        try:
            while True:
                buf=C.create_string_buffer(65536);count=DWORD()
                ok=self.api.read_file(handle,buf,len(buf),C.byref(count),None)
                if not ok:
                    if C.get_last_error()==109: capture.eof=True
                    else: capture.error=True
                    return
                if count.value==0: capture.eof=True;return
                capture.feed(buf.raw[:count.value])
        finally:self.api.close(handle)

    def _input(self,handle,data):
        try:
            offset=0
            while offset<len(data):
                chunk=data[offset:offset+65536];buf=C.create_string_buffer(chunk);count=DWORD()
                if not self.api.write_file(handle,buf,len(chunk),C.byref(count),None) or not count.value:return
                offset+=count.value
        finally:self.api.close(handle)

    def run(self,command:Command,*,before_resume,environment:dict[str,str],cwd:str):
        command.validate()
        require(self.guard.held,18,'GUARD_NOT_HELD')
        require(callable(before_resume),12,'DURABLE_WITNESS_CALLBACK_REQUIRED')
        cwd=windows_path(cwd)
        # Environment values come from protected bindings/OS queries, not the
        # arbitrary caller environment. WSLENV/LD_PRELOAD/PYTHONPATH are excluded.
        allowed={'SystemRoot','WINDIR','SystemDrive','PATH','TEMP','TMP','USERPROFILE','LOCALAPPDATA','ProgramData','COMSPEC'}
        require(type(environment) is dict and set(environment)<=allowed and {'SystemRoot','PATH','TEMP','TMP'}<=set(environment),12,'CHILD_ENVIRONMENT_SCOPE')
        require(all(type(v) is str and '\0' not in v for v in environment.values()),10,'CHILD_ENVIRONMENT_INVALID')
        env=C.create_unicode_buffer('\0'.join(k+'='+v for k,v in sorted(environment.items(),key=lambda x:x[0].casefold()))+'\0\0')
        handles=[]; parent_handles=[]; worker_threads=[]; pi=PROCESS_INFORMATION(); job=None
        attrbuf=None; resumed=False; transferred=set(); started=time.monotonic()
        try:
            stdin_r,stdin_w=self._pipe(); stdout_r,stdout_w=self._pipe(); stderr_r,stderr_w=self._pipe()
            handles=[stdin_r,stdin_w,stdout_r,stdout_w,stderr_r,stderr_w]
            for h in (stdin_w,stdout_r,stderr_r):self.api.ok(self.api.handle_flags(h,1,0),'PIPE_INHERITANCE')
            n=C.c_size_t();self.api.init_attributes(None,1,0,C.byref(n))
            require(0<n.value<65536,18,'ATTRIBUTE_LIST_SIZE')
            attrbuf=C.create_string_buffer(n.value)
            self.api.ok(self.api.init_attributes(attrbuf,1,0,C.byref(n)),'ATTRIBUTE_LIST_INIT')
            inherited=(HANDLE*3)(stdin_r,stdout_w,stderr_w)
            self.api.ok(self.api.update_attributes(attrbuf,0,PROC_THREAD_ATTRIBUTE_HANDLE_LIST,inherited,C.sizeof(inherited),None,None),'ATTRIBUTE_HANDLE_LIST')
            si=STARTUPINFOEX();si.info.cb=C.sizeof(si);si.info.flags=0x100
            si.info.stdin=stdin_r;si.info.stdout=stdout_w;si.info.stderr=stderr_w
            si.attributes=C.cast(attrbuf,C.c_void_p)
            job_name='Global\\AI-FILM-P00-JOB-'+uuid4().hex
            job=self.api.create_job(None,job_name)
            require(bool(job) and C.get_last_error()!=183,18,'JOB_CREATE')
            # The binary and parent directory handles remain pinned through wait.
            # Production requires a trusted exact-byte policy; workspace tests may
            # explicitly construct a supervisor without that production requirement.
            require(not self.require_executable_trust or self.executable_trust is not None,
                    15,'EXECUTABLE_TRUST_REQUIRED')
            binary_context=(self.executable_trust.pin(command.argv[0])
                            if self.executable_trust is not None
                            else self.paths.pin(command.argv[0],confidential=False))
            with binary_context as binary:
                line=C.create_unicode_buffer(subprocess.list2cmdline(command.argv))
                flags=CREATE_SUSPENDED|EXTENDED_STARTUPINFO_PRESENT|CREATE_UNICODE_ENVIRONMENT|CREATE_NO_WINDOW
                self.api.ok(self.api.create_process(command.argv[0],line,None,None,True,flags,env,cwd,C.byref(si),C.byref(pi)),'PROCESS_CREATE')
                self.api.ok(self.api.assign_job(job,pi.process),'PROCESS_JOB_ASSIGN')
                witness={'pid':pi.pid,'start':str(self.api.process_start(pi.process)),
                         'action_id':command.action_id,'job_name':job_name,
                         'binary_file_id':binary.identity['file_id'],'binary_volume_serial':binary.identity['volume_serial']}
                if self.executable_trust is not None:
                    witness.update({'binary_sha256':binary.sha256,'binary_bytes':binary.bytes,
                                    'executable_policy_ref':binary.policy_ref,
                                    'executable_kind':binary.kind})
                before_resume(witness)  # throws -> own still-suspended child is not run
                for h in (stdin_r,stdout_w,stderr_w):self.api.close(h);handles.remove(h)
                stdout=Capture();stderr=Capture()
                for handle,capture in ((stdout_r,stdout),(stderr_r,stderr)):
                    t=Thread(target=self._drain,args=(handle,capture),daemon=True)
                    t.start();worker_threads.append(t);transferred.add(handle)
                t=Thread(target=self._input,args=(stdin_w,command.stdin),daemon=True)
                t.start();worker_threads.append(t);transferred.add(stdin_w)
                require(self.api.resume_thread(pi.thread)!=0xffffffff,18,'PROCESS_RESUME')
                resumed=True
                wait=self.api.wait(pi.process,command.timeout_seconds*1000)
                require(wait!=258,17,'NATIVE_TIMEOUT')
                require(wait==0,18,'PROCESS_WAIT')
                code=DWORD();self.api.ok(self.api.process_exit(pi.process,C.byref(code)),'PROCESS_EXIT_QUERY')
                accounting=JOB_ACCOUNTING();size=DWORD()
                self.api.ok(self.api.query_job(job,1,C.byref(accounting),C.sizeof(accounting),C.byref(size)),'JOB_WITNESS')
                for thread in worker_threads:thread.join(timeout=0.2)
                result=ProcessResult(code.value,stdout.bytes(),stderr.bytes(),stdout.eof,stderr.eof,
                                     stdout.truncated or stderr.truncated,int((time.monotonic()-started)*1000),witness,
                                     accounting.active==0 and stdout.eof and stderr.eof)
                require(not stdout.error and not stderr.error,18,'NATIVE_CAPTURE_IO')
                require(result.tree_terminal,17,'NATIVE_TREE_UNRESOLVED')
                require(not result.truncated,22,'NATIVE_CAPTURE_TRUNCATED')
                return result
        finally:
            # Only a process still suspended before its first resume may be
            # terminated here. NEVER terminate a timed-out installer/WSL process.
            if pi.process and not resumed:
                self.api.terminate_process(pi.process,18)
            for h in handles:
                if h not in transferred:self.api.close(h)
            if pi.thread:self.api.close(pi.thread)
            if pi.process:self.api.close(pi.process)
            if job:self.api.close(job)
            if attrbuf is not None:self.api.delete_attributes(attrbuf)
