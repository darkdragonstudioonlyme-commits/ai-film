"""Read-only native process/job/service/MSI state used by reconciliation.

Job absence is not a substitute for service-level after-state. No process/service
is stopped or killed here; unavailable/access-denied is UNKNOWN, never absence.
"""
from __future__ import annotations
import ctypes as C
import os
import re
from .winapi import HANDLE,DWORD,BOOL,LPWSTR,LPVOID,JOB_ACCOUNTING,GUID
from ..errors import require,P00Error

class ServiceStatus(C.Structure):
    _fields_=[(k,DWORD) for k in ('service_type','current_state','controls_accepted','win32_exit',
                                'service_exit','checkpoint','wait_hint','pid','flags')]

class NativeSystemState:
    def __init__(self,api):
        self.api=api
        def bind(lib,name,restype,args):
            f=getattr(lib,name);f.restype=restype;f.argtypes=args;return f
        self.open_job=bind(api.k,'OpenJobObjectW',HANDLE,[DWORD,BOOL,LPWSTR])
        self.scm=bind(api.a,'OpenSCManagerW',HANDLE,[LPWSTR,LPWSTR,DWORD])
        self.open_service=bind(api.a,'OpenServiceW',HANDLE,[HANDLE,LPWSTR,DWORD])
        self.query_service=bind(api.a,'QueryServiceStatusEx',BOOL,[HANDLE,C.c_int,LPVOID,DWORD,C.POINTER(DWORD)])
        self.close_service=bind(api.a,'CloseServiceHandle',BOOL,[HANDLE])
        self.msi=C.WinDLL(api.system_directory()+'\\msi.dll',use_last_error=True)
        self.msi_state=bind(self.msi,'MsiQueryProductStateW',C.c_int,[LPWSTR])
        self.msi_info=bind(self.msi,'MsiGetProductInfoW',DWORD,[LPWSTR,LPWSTR,LPWSTR,C.POINTER(DWORD)])

    def known_folder(self,guid):
        value=GUID.parse(guid);out=LPWSTR()
        require(self.api.known_folder(C.byref(value),0,None,C.byref(out))==0,11,'KNOWN_FOLDER_UNAVAILABLE')
        try:return out.value
        finally:self.api.com_free(C.cast(out,LPVOID))

    def user_profile(self):return self.known_folder('5E6C858F-0E22-4760-9AFE-EA3317B67173')
    def local_app_data(self):return self.known_folder('F1B32785-6FBA-4FCF-9D55-7B8E7F157091')

    def service(self,name):
        require(name in ('msiserver','TrustedInstaller','WslService','LxssManager'),10,'SERVICE_QUERY_SCOPE')
        manager=self.scm(None,None,1)
        require(manager not in (None,0),12,'SCM_QUERY_DENIED')
        try:
            h=self.open_service(manager,name,4)
            if h in (None,0):
                error=C.get_last_error()
                require(error==1060,12 if error==5 else 18,'SERVICE_QUERY_UNAVAILABLE')
                return {'name':name,'status':'ABSENT'}
            try:
                state=ServiceStatus();n=DWORD()
                self.api.ok(self.query_service(h,0,C.byref(state),C.sizeof(state),C.byref(n)),'SERVICE_QUERY',11)
                return {'name':name,'status':'OBSERVED','state':state.current_state,
                        'controls_accepted':state.controls_accepted,'pid':state.pid,
                        'checkpoint':state.checkpoint,'win32_exit':state.win32_exit}
            finally:self.close_service(h)
        finally:self.close_service(manager)

    def installer_idle(self,action):
        names=('TrustedInstaller',) if action=='ENABLE_PREREQUISITES' else ('msiserver',)
        rows=[self.service(n) for n in names]
        # Conservative observed STOPPED, not merely absence of _MSIExecute.
        require(all(r['status']=='OBSERVED' and r['state']==1 for r in rows),21,'INSTALLER_SERVICE_NOT_QUIESCENT')
        return {'services':rows}

    def product(self,code):
        require(type(code) is str and re.fullmatch(r'\{[0-9A-Fa-f-]{36}\}',code),10,'MSI_PRODUCT_CODE')
        state=self.msi_state(code)
        require(state in (-1,1,2,5),11,'MSI_PRODUCT_STATE_UNAVAILABLE')
        if state!=5:return {'installed':False,'state':state,'identity':code,'version':None}
        size=DWORD(256);text=C.create_unicode_buffer(257)
        result=self.msi_info(code,'VersionString',text,C.byref(size))
        require(result==0,11,'MSI_VERSION_UNAVAILABLE')
        return {'installed':True,'state':state,'identity':code,'version':text.value}

    def writer(self,witness):
        require(type(witness) is dict and {'pid','start','job_name'}<=set(witness),11,'WRITER_WITNESS_MISSING')
        require(type(witness['pid']) is int and witness['pid']>0,15,'WRITER_PID')
        handle=self.api.open_process(0x00100000|0x1000,False,witness['pid'])
        if handle in (None,0):
            error=C.get_last_error()
            require(error==87,12 if error==5 else 21,'WRITER_STATE_UNAVAILABLE')
            process={'state':'ABSENT'}
        else:
            with self.api.handle(handle):
                start=str(self.api.process_start(handle))
                if start!=witness['start']:process={'state':'PID_REUSED','current_start':start}
                else:
                    wait=self.api.wait(handle,0)
                    require(wait in (0,258),21,'WRITER_WAIT_UNAVAILABLE')
                    process={'state':'TERMINAL' if wait==0 else 'RUNNING','start':start}
        require(process['state']!='RUNNING',21,'NATIVE_WRITER_RUNNING')
        name=witness['job_name']
        require(type(name) is str and re.fullmatch(r'Global\\AI-FILM-P00-JOB-[0-9a-f]{32}',name),15,'JOB_WITNESS_NAME')
        job=self.open_job(0x4,False,name)
        if job in (None,0):
            error=C.get_last_error()
            require(error==2,12 if error==5 else 21,'JOB_STATE_UNAVAILABLE')
            job_state={'state':'ABSENT'}
        else:
            with self.api.handle(job):
                actual=JOB_ACCOUNTING();n=DWORD()
                self.api.ok(self.api.query_job(job,1,C.byref(actual),C.sizeof(actual),C.byref(n)),'JOB_QUERY',21)
                require(actual.active==0,21,'NATIVE_JOB_RUNNING')
                job_state={'state':'TERMINAL','active':actual.active,'total':actual.total}
        return {'process':process,'job':job_state,'witness':witness}

    def all_writers(self,witness):
        if witness is None:return []
        rows=[{k:v for k,v in witness.items() if k!='additional'}, *witness.get('additional',[])]
        return [self.writer(w) for w in rows]

    def pending_reboot(self):
        require(os.name=='nt',11,'WINDOWS_X64_REQUIRED')
        import winreg
        roots=(r'SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending',
               r'SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired')
        observed=[]
        for path in roots:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,path,0,winreg.KEY_READ|winreg.KEY_WOW64_64KEY):exists=True
            except FileNotFoundError:exists=False
            except PermissionError:raise P00Error(12,'REBOOT_STATE_UNAVAILABLE') from None
            observed.append(exists)
        return {'cbs_reboot_pending':observed[0],'windows_update_reboot_required':observed[1]}
