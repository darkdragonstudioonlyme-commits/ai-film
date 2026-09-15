"""Concrete fixed guest-agent transport. No agent installation, no dynamic code."""
from __future__ import annotations
import base64
from pathlib import Path
from ..codec import canonical,loads,sha256,distro_name,user_name,windows_path
from ..errors import require
from .process import Command

AGENT_OPERATIONS={'INVENTORY','ADMIN','WORKSPACE','ASSERT_CONTENT'}


def agent_command(system_directory,target,user,script,request):
    target=distro_name(target);user=user_name(user)
    require(type(request) is dict and request.get('operation') in AGENT_OPERATIONS
            and request.get('user')==user,10,'GUEST_REQUEST_SCOPE')
    data=base64.b64encode(canonical(request)).decode('ascii')
    require(len(data)<=20000,10,'GUEST_REQUEST_CAP')
    return Command((windows_path(system_directory)+'\\wsl.exe','--distribution',target,'--user',user,
                    '--exec','/usr/bin/python3','-I','-S','-B','-',data),
                   'GUEST_'+request['operation'],30,script,request['operation']=='WORKSPACE')


def parse_agent(raw,operation):
    require(type(raw) is bytes and len(raw)<=10*1024**2 and raw.endswith(b'\n'),22,'GUEST_CAPTURE_INCOMPLETE')
    d=loads(raw)
    require(type(d) is dict and set(d)=={'schema_version','operation','status','actual','duration_ms'}
            and d['schema_version']==1 and d['operation']==operation and d['status']=='OBSERVED'
            and type(d['actual']) is dict and type(d['duration_ms']) is int and 0<=d['duration_ms']<=30000,
            15,'GUEST_AGENT_SCHEMA')
    return d


class GuestTransport:
    def __init__(self,root,supervisor,system_directory,environment,sources):
        self.root=Path(root);self.supervisor=supervisor;self.system_directory=system_directory;self.environment=environment;self.sources=sources
    def run(self,target,user,request,coordinator):
        require(coordinator.held and coordinator.fence is not None,12,'GUEST_ADMISSION_REQUIRED')
        require(coordinator.admission.purpose!='RECONCILIATION_ONLY',12,'RECOVERY_CANNOT_LAUNCH_GUEST')
        script=self.sources.read('native/guest-agent.py')
        command=agent_command(self.system_directory,target,user,script,request)
        def before(w):
            if coordinator.fence['state']=='INTENT':coordinator.native_started(w)
            else:coordinator.native_child_started(w)
        result=self.supervisor.run(command,before_resume=before,environment=self.environment,cwd=self.system_directory)
        require(result.exit_code==0,11 if result.exit_code==127 else 19,'GUEST_ACTION_FAILED')
        value=parse_agent(result.stdout,request['operation'])
        return {'capture':value,'process':result,'agent_digest':sha256(script),'stdout_digest':sha256(result.stdout)}
