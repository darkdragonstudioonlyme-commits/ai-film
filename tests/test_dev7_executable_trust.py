"""Workspace author tests for exact executable trust. No Windows/native execution."""
from contextlib import contextmanager
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import ctypes as C

from aifilm_p00 import CONTRACT_DIGEST
from aifilm_p00.errors import P00Error
from aifilm_p00.native.executable_trust import ExecutableTrust
from aifilm_p00.native.process import NativeSupervisor, Command
from aifilm_p00.native.winapi import HANDLE, DWORD, PROCESS_INFORMATION, JOB_ACCOUNTING

REF='a'*64
BUILD='b'*64
PATH=r'C:\Windows\System32\wsl.exe'
HASH='c'*64


def policy(**overrides):
    value={'schema_version':1,'host_id':'host','build_digest':BUILD,
           'contract_digest':CONTRACT_DIGEST,'withdrawn':False,
           'executables':[{'path':PATH,'bytes':123,'sha256':HASH,'kind':'SYSTEM'}]}
    value.update(overrides);return value


class Paths:
    def __init__(self):self.calls=[]
    @contextmanager
    def pinned_executable(self,path,sha,size):
        self.calls.append((path,sha,size))
        yield SimpleNamespace(identity={'file_id':7,'volume_serial':9})
    @contextmanager
    def pin(self,*a,**k):
        yield SimpleNamespace(identity={'file_id':7,'volume_serial':9})


class Store:
    def __init__(self,value):self.value=value
    def get(self,role,ref):
        if role!='executable_policy' or ref!=REF:raise AssertionError((role,ref))
        return self.value


class PolicyTests(unittest.TestCase):
    def reject(self,reason,fn,*a,**k):
        with self.assertRaises(P00Error) as cm:fn(*a,**k)
        self.assertEqual(cm.exception.reason,reason)
    def test_exact_policy_pins_bound_bytes(self):
        paths=Paths();trust=ExecutableTrust.from_store(paths,Store(policy()),REF,host_id='host',build_digest=BUILD)
        with trust.pin(PATH) as pinned:
            self.assertEqual(pinned.sha256,HASH);self.assertEqual(pinned.bytes,123)
            self.assertEqual(pinned.policy_ref,REF);self.assertEqual(pinned.kind,'SYSTEM')
        self.assertEqual(paths.calls,[(PATH,HASH,123)])
    def test_unlisted_binary_rejected(self):
        trust=ExecutableTrust(Paths(),REF,policy(),host_id='host',build_digest=BUILD)
        self.reject('EXECUTABLE_NOT_TRUSTED',lambda: trust.pin(r'C:\Windows\System32\cmd.exe').__enter__())
    def test_scope_and_contract_fail_closed(self):
        self.reject('EXECUTABLE_POLICY_SCOPE',ExecutableTrust,Paths(),REF,policy(host_id='other'),host_id='host',build_digest=BUILD)
        self.reject('EXECUTABLE_POLICY_CONTRACT',ExecutableTrust,Paths(),REF,policy(contract_digest='d'*64),host_id='host',build_digest=BUILD)
    def test_duplicate_alias_rejected_case_insensitive(self):
        p=policy();p['executables'].append({'path':PATH.upper(),'bytes':123,'sha256':HASH,'kind':'SYSTEM'})
        self.reject('EXECUTABLE_POLICY_DUPLICATE',ExecutableTrust,Paths(),REF,p,host_id='host',build_digest=BUILD)
    def test_dependency_kind_allowed_but_only_exact_path(self):
        py=r'C:\Program Files\AI-Film\Python\python.exe';p=policy(executables=[{'path':py,'bytes':456,'sha256':'d'*64,'kind':'PINNED_DEPENDENCY'}])
        trust=ExecutableTrust(Paths(),REF,p,host_id='host',build_digest=BUILD)
        with trust.pin(py) as pin:self.assertEqual(pin.kind,'PINNED_DEPENDENCY')


class ProcessAPI:
    def __init__(self):self.events=[];self.next=10
    def ok(self,v,*a,**k):
        if not v:raise P00Error(18,'FAKE')
        return v
    def create_pipe(self,r,w,*a):
        C.cast(r,C.POINTER(HANDLE))[0]=self.next;C.cast(w,C.POINTER(HANDLE))[0]=self.next+1;self.next+=2;return 1
    def handle_flags(self,*a):return 1
    def init_attributes(self,buf,n,flags,ptr):C.cast(ptr,C.POINTER(C.c_size_t))[0]=128;return bool(buf)
    def update_attributes(self,*a):return 1
    def delete_attributes(self,*a):pass
    def create_job(self,*a):return 80
    def create_process(self,application,line,*args):
        pi=C.cast(args[-1],C.POINTER(PROCESS_INFORMATION)).contents;pi.process=90;pi.thread=91;pi.pid=100;pi.tid=101;self.events.append('create');return 1
    def assign_job(self,*a):return 1
    def process_start(self,*a):return 123
    def resume_thread(self,*a):self.events.append('resume');return 1
    def wait(self,*a):return 0
    def process_exit(self,h,p):C.cast(p,C.POINTER(DWORD))[0]=0;return 1
    def query_job(self,h,k,b,s,p):C.cast(b,C.POINTER(JOB_ACCOUNTING)).contents.active=0;return 1
    def read_file(self,h,b,s,p,o):C.cast(p,C.POINTER(DWORD))[0]=0;return 1
    def write_file(self,h,b,s,p,o):C.cast(p,C.POINTER(DWORD))[0]=s;return 1
    def terminate_process(self,*a):return 1
    def close(self,*a):return 1


class SupervisorTrustTests(unittest.TestCase):
    ENV={'SystemRoot':r'C:\Windows','PATH':r'C:\Windows\System32','TEMP':r'C:\P00\Temp','TMP':r'C:\P00\Temp'}
    def test_production_supervisor_rejects_before_process_without_trust(self):
        api=ProcessAPI();sup=NativeSupervisor(api,Paths(),SimpleNamespace(held=True),require_executable_trust=True)
        with self.assertRaises(P00Error) as cm:
            with patch.object(C,'get_last_error',return_value=0,create=True):
                sup.run(Command((PATH,'--version'),'VERSION',30),before_resume=lambda w:None,environment=self.ENV,cwd=r'C:\Windows\System32')
        self.assertEqual(cm.exception.reason,'EXECUTABLE_TRUST_REQUIRED');self.assertNotIn('create',api.events)
    def test_witness_binds_executable_policy_and_hash(self):
        api=ProcessAPI();paths=Paths();sup=NativeSupervisor(api,paths,SimpleNamespace(held=True),require_executable_trust=True)
        sup.set_executable_trust(ExecutableTrust(paths,REF,policy(),host_id='host',build_digest=BUILD))
        witness=[]
        with patch.object(C,'get_last_error',return_value=0,create=True):
            result=sup.run(Command((PATH,'--version'),'VERSION',30),before_resume=witness.append,environment=self.ENV,cwd=r'C:\Windows\System32')
        self.assertEqual(result.native_witness['binary_sha256'],HASH)
        self.assertEqual(result.native_witness['binary_bytes'],123)
        self.assertEqual(result.native_witness['executable_policy_ref'],REF)
        self.assertEqual(witness[0],result.native_witness)


if __name__=='__main__':unittest.main()
