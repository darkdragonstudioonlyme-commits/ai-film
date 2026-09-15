"""Deterministic fake Win32 API tests. NOT execution of Win32 or a native lab."""
import ctypes as C
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from aifilm_p00.native.process import NativeSupervisor,Command
from aifilm_p00.native.winapi import HANDLE,DWORD,PROCESS_INFORMATION,JOB_ACCOUNTING,SA
from aifilm_p00.native.coordination import NativeGuard,MUTEX_NAME,NativeJournal
from aifilm_p00.native.security import Security,Ace
from aifilm_p00.admission import Coordinator
from aifilm_p00.errors import P00Error,require
from aifilm_p00.codec import canonical,digest
from helpers import SID

class ProcessAPI:
    """No OS calls; records causal sequence and provides fixed pipe bytes."""
    def __init__(self,*,wait_result=0,active=0,assign_ok=True,callback_fail=False):
        self.events=[];self.next=10;self.pipe_reads={};self.wait_result=wait_result;self.active=active;self.assign_ok=assign_ok
    def ok(self,value,reason='WIN32_IO',code=18):require(value,code,reason);return value
    def create_pipe(self,r,w,attr,size):
        read=self.next;write=self.next+1;self.next+=2
        C.cast(r,C.POINTER(HANDLE))[0]=read;C.cast(w,C.POINTER(HANDLE))[0]=write
        self.pipe_reads[read]=b'';return 1
    def handle_flags(self,*a):return 1
    def init_attributes(self,buf,n,flags,ptr):C.cast(ptr,C.POINTER(C.c_size_t))[0]=128;return bool(buf)
    def update_attributes(self,*args):self.events.append('handle_list');return 1
    def delete_attributes(self,*a):self.events.append('attributes_free')
    def create_job(self,*a):self.events.append('job_create');return 80
    def create_process(self,application,line,*args):
        pi=C.cast(args[-1],C.POINTER(PROCESS_INFORMATION)).contents
        pi.process=90;pi.thread=91;pi.pid=100;pi.tid=101
        self.events.append('create_suspended');return 1
    def assign_job(self,*a):self.events.append('job_assign');return self.assign_ok
    def process_start(self,*a):return 123456
    def resume_thread(self,*a):self.events.append('resume');return 1
    def wait(self,*a):self.events.append('wait');return self.wait_result
    def process_exit(self,h,ptr):C.cast(ptr,C.POINTER(DWORD))[0]=0;return 1
    def query_job(self,h,kind,buf,size,ptr):
        value=C.cast(buf,C.POINTER(JOB_ACCOUNTING)).contents;value.active=self.active;return 1
    def read_file(self,h,buf,size,ptr,over):C.cast(ptr,C.POINTER(DWORD))[0]=0;return 1
    def write_file(self,h,buf,size,ptr,over):C.cast(ptr,C.POINTER(DWORD))[0]=size;return 1
    def terminate_process(self,*a):self.events.append('terminate_unresumed');return 1
    def close(self,h):self.events.append(('close',h));return 1

class FakePaths:
    @contextmanager
    def pin(self,*args,**kw):
        yield SimpleNamespace(identity={'file_id':1,'volume_serial':2})

class SupervisorTests(unittest.TestCase):
    def run_case(self,api,callback=None):
        supervisor=NativeSupervisor(api,FakePaths(),SimpleNamespace(held=True))
        def persist(w):api.events.append('durable_witness')
        command=Command((r'C:\Windows\System32\wsl.exe','--version'),'VERSION',30)
        with patch.object(C,'get_last_error',return_value=0,create=True):
            return supervisor.run(command,before_resume=callback or persist,
                                  environment={'SystemRoot':r'C:\Windows','PATH':r'C:\Windows\System32','TEMP':r'C:\P00\Temp','TMP':r'C:\P00\Temp'},cwd=r'C:\Windows\System32')
    def test_suspended_assigned_witnessed_before_resume(self):
        a=ProcessAPI();r=self.run_case(a)
        self.assertLess(a.events.index('create_suspended'),a.events.index('job_assign'))
        self.assertLess(a.events.index('job_assign'),a.events.index('durable_witness'))
        self.assertLess(a.events.index('durable_witness'),a.events.index('resume'))
        self.assertTrue(r.tree_terminal);self.assertFalse(r.service_terminal)
    def test_timeout_does_not_terminate_live_mutation(self):
        a=ProcessAPI(wait_result=258)
        with self.assertRaises(P00Error) as e:self.run_case(a)
        self.assertEqual(int(e.exception.code),17);self.assertNotIn('terminate_unresumed',a.events)
    def test_job_assignment_failure_never_resumes(self):
        a=ProcessAPI(assign_ok=False)
        with self.assertRaises(P00Error):self.run_case(a)
        self.assertNotIn('resume',a.events);self.assertIn('terminate_unresumed',a.events)
    def test_journal_callback_failure_never_resumes(self):
        a=ProcessAPI()
        def fail(_):raise P00Error(18,'JOURNAL_IO')
        with self.assertRaises(P00Error):self.run_case(a,fail)
        self.assertNotIn('resume',a.events);self.assertIn('terminate_unresumed',a.events)
    def test_live_child_not_terminal(self):
        a=ProcessAPI(active=1)
        with self.assertRaises(P00Error) as e:self.run_case(a)
        self.assertEqual(int(e.exception.code),17)
    def test_unexpected_wait_failure_not_kill(self):
        a=ProcessAPI(wait_result=0xffffffff)
        with self.assertRaises(P00Error):self.run_case(a)
        self.assertNotIn('terminate_unresumed',a.events)
    def test_all_pipeline_handles_closed_on_success(self):
        a=ProcessAPI();self.run_case(a)
        closed=[e[1] for e in a.events if isinstance(e,tuple) and e[0]=='close']
        for h in (10,11,12,13,14,15,80,90,91):self.assertEqual(closed.count(h),1)
    def test_environment_injection_rejected(self):
        a=ProcessAPI();sup=NativeSupervisor(a,FakePaths(),SimpleNamespace(held=True))
        with self.assertRaises(P00Error):
            sup.run(Command((r'C:\x.exe',),'X',1),before_resume=lambda w:None,environment={'WSLENV':'LD_PRELOAD/u'},cwd=r'C:\Windows')
        self.assertEqual(a.events,[])

class GuardAPI:
    def __init__(self,state=0):self.state=state;self.names=[];self.released=0;self.closed=0
    @contextmanager
    def attributes(self,*a):yield SA()
    def create_mutex(self,a,name,flags,access):self.names.append(name);return 100
    def security(self,*a):return Security(SID,True,False,True,(Ace(0,0,0x1f0001,SID),))
    def wait(self,*a):return self.state
    def close(self,*a):self.closed+=1
    def get_current_tid(self):return 1
    def release_mutex(self,*a):self.released+=1;return 1
    def ok(self,value,*a):require(value,18,'FAKE_API');return value

class GuardTests(unittest.TestCase):
    def test_fixed_cross_instance_name(self):
        a=GuardAPI();g=NativeGuard(a,{SID});self.assertTrue(g.acquire());g.release()
        b=GuardAPI();h=NativeGuard(b,{'S-1-5-21-999'});h.api.security=lambda *args:Security(SID,True,False,True,())
        # Separately inspect namespace, not claim cross-SID native proof.
        self.assertEqual(a.names,[MUTEX_NAME]);self.assertTrue(MUTEX_NAME.startswith('Global\\'))
    def test_busy_single_try(self):
        a=GuardAPI(258);g=NativeGuard(a,{SID});self.assertFalse(g.acquire());self.assertEqual(a.closed,1)
    def test_abandoned_not_automatic_journal_clear(self):
        a=GuardAPI(0x80);g=NativeGuard(a,{SID});self.assertTrue(g.acquire());self.assertTrue(g.abandoned);g.release()
    def test_uncertain_controller_retains_mutex(self):
        a=GuardAPI();g=NativeGuard(a,{SID});g.acquire();g.defer_until_process_exit()
        with self.assertRaises(P00Error):g.release()
        self.assertEqual(a.released,0);self.assertTrue(g.held)
    def test_reentrant_rejected(self):
        a=GuardAPI();g=NativeGuard(a,{SID});g.acquire()
        with self.assertRaises(P00Error):g.acquire()
        g.release()

class JournalPaths:
    root=r'C:\ProgramData\AI-FILM-P00-HOST-ADMISSION'
    def __init__(self):self.data={};self.created=False
    @contextmanager
    def pin(self,*args,**kw):yield SimpleNamespace(identity={'file_id':1,'volume_serial':2})
    def directory_exists(self,p):return self.created
    def create_directory(self,p):
        require(not self.created,18,'ALREADY_EXISTS');self.created=True
    def write_new(self,p,data):require(p not in self.data,18,'ALREADY_EXISTS');self.data[p]=data
    def read_blob(self,p,**kw):return self.data[p]
    def append_flush(self,p,data):self.data[p]+=data

class JournalAdapterTests(unittest.TestCase):
    def setup(self):
        from aifilm_p00.native.trust import MetadataPermit
        paths=JournalPaths();j=NativeJournal(paths,SimpleNamespace(held=True),'synthetic')
        j.initialize(MetadataPermit('synthetic',SID,'a'*64,'b'*64));return paths,j
    def test_initialized_empty_fence(self):
        paths,j=self.setup();self.assertIsNone(j.load_fence())
    def test_set_reload_clear_is_append_only(self):
        paths,j=self.setup();f={'run_id':'x','host_id':'synthetic','owner_sid':SID,'plan_digest':'a'*64,'action':'X','state':'INTENT'}
        j.write_fence(f);self.assertEqual(j.load_fence(),f)
        f['state']='TERMINAL';j.write_fence(f);old=paths.data[j.path];j.clear_fence()
        self.assertTrue(paths.data[j.path].startswith(old));self.assertIsNone(j.load_fence())
    def test_unheld_guard_blocks_io(self):
        paths,j=self.setup();j.guard.held=False
        with self.assertRaises(P00Error):j.load_fence()
    def test_wrong_host_blocks_replay(self):
        paths,j=self.setup();j.host_id='different'
        with self.assertRaises(P00Error):j.load_fence()

class MetadataIdempotenceTests(unittest.TestCase):
    def setup(self):
        from aifilm_p00.native.trust import MetadataPermit
        paths=JournalPaths();journal=NativeJournal(paths,SimpleNamespace(held=True),'synthetic')
        permit=MetadataPermit('synthetic',SID,'a'*64,'b'*64)
        return paths,journal,permit
    def test_first_initialization(self):
        paths,j,p=self.setup();self.assertEqual(j.initialize_or_verify(p),'METADATA_INITIALIZED')
    def test_rerun_does_not_write(self):
        paths,j,p=self.setup();j.initialize_or_verify(p);before=dict(paths.data)
        self.assertEqual(j.initialize_or_verify(p),'METADATA_NOOP');self.assertEqual(paths.data,before)
    def test_existing_fence_blocks_noop(self):
        paths,j,p=self.setup();j.initialize_or_verify(p)
        j.write_fence({'run_id':'x','host_id':'synthetic','owner_sid':SID,'plan_digest':'a'*64,'action':'X','state':'INTENT'})
        before=dict(paths.data)
        with self.assertRaises(P00Error) as e:j.initialize_or_verify(p)
        self.assertEqual(int(e.exception.code),21);self.assertEqual(paths.data,before)
    def test_partial_root_not_reinitialized(self):
        paths,j,p=self.setup();paths.created=True
        with self.assertRaises((P00Error,KeyError)):j.initialize_or_verify(p)
        self.assertEqual(paths.data,{})
    def test_corrupt_log_not_reinitialized(self):
        paths,j,p=self.setup();j.initialize_or_verify(p);paths.data[j.path]=b'corrupt\n'
        with self.assertRaises(P00Error):j.initialize_or_verify(p)
        self.assertEqual(paths.data[j.path],b'corrupt\n')
    def test_metadata_permission_still_required_on_noop(self):
        paths,j,p=self.setup();j.initialize_or_verify(p)
        with self.assertRaises(P00Error):j.initialize_or_verify({'approved':True})
