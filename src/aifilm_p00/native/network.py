"""Supervised, fixed-source endpoint probe in the declared Windows/GUEST context.

The agent is assembled from exact reviewed module bytes, never request-supplied
code. No installation occurs. DIRECT requires observed absent proxy overrides;
a configured or unresolvable proxy is blocked, never silently bypassed.
"""
from pathlib import Path
import base64
import sys
from ..codec import canonical,sha256,loads,windows_path,user_name,distro_name
from ..errors import require
from ..network_probe import endpoint,proxy_policy
from .process import Command

# No imports of pwd on Windows. Fixed bootstrap + exact module bytes below.
PRELUDE = '''import base64,sys,types,os,json,ctypes as C
pkg=types.ModuleType('aifilm_p00');pkg.__path__=[];sys.modules['aifilm_p00']=pkg
'''
MAIN = r'''
from aifilm_p00.codec import loads,canonical
from aifilm_p00.errors import require,P00Error
from aifilm_p00.network_probe import measure,endpoint,proxy_policy

def proxy_observation(context):
    names=('http_proxy','https_proxy','all_proxy','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY')
    env={k:bool(os.environ.get(k)) for k in names}
    actual={'environment_overrides':env,'context':context}
    if context=='WINDOWS':
        from ctypes import wintypes as W
        class Default(C.Structure):
            _fields_=[('access_type',W.DWORD),('proxy',C.c_void_p),('bypass',C.c_void_p)]
        class User(C.Structure):
            _fields_=[('auto',W.BOOL),('url',C.c_void_p),('proxy',C.c_void_p),('bypass',C.c_void_p)]
        winhttp=C.WinDLL('winhttp',use_last_error=True);kernel=C.WinDLL('kernel32',use_last_error=True)
        default=winhttp.WinHttpGetDefaultProxyConfiguration;default.argtypes=[C.POINTER(Default)];default.restype=W.BOOL
        user=winhttp.WinHttpGetIEProxyConfigForCurrentUser;user.argtypes=[C.POINTER(User)];user.restype=W.BOOL
        free=kernel.GlobalFree;free.argtypes=[C.c_void_p];free.restype=C.c_void_p
        d=Default();u=User()
        try:
            require(bool(default(C.byref(d))),11,'PROXY_OBSERVATION_UNAVAILABLE')
            ok=user(C.byref(u));error=0 if ok else C.get_last_error()
            require(bool(ok) or error==2,11,'PROXY_OBSERVATION_UNAVAILABLE')
            actual['winhttp']={'access_type':int(d.access_type),'proxy_present':bool(d.proxy),'bypass_present':bool(d.bypass)}
            actual['user']={'status':'OBSERVED' if ok else 'ABSENT','auto_detect':bool(u.auto),
                            'auto_config_url_present':bool(u.url),'proxy_present':bool(u.proxy)}
        finally:
            for value in (d.proxy,d.bypass,u.url,u.proxy,u.bypass):
                if value:free(value)
    return actual

try:
    require(len(sys.argv)==2 and len(sys.argv[1])<=20000,10,'NETWORK_REQUEST_CAP')
    request=loads(base64.b64decode(sys.argv[1],validate=True))
    require(type(request) is dict and set(request)=={'spec','user'},10,'NETWORK_REQUEST_SCHEMA')
    spec=endpoint(request['spec']);context=spec['context']
    require((context=='WINDOWS' and os.name=='nt') or (context=='GUEST' and os.name=='posix'),12,'NETWORK_CONTEXT_MISMATCH')
    if context=='GUEST':
        import pwd
        require(os.geteuid()>0 and pwd.getpwuid(os.geteuid()).pw_name==request['user'],12,'WRONG_GUEST_PRINCIPAL')
    else:require(request['user'] is None,10,'NETWORK_USER_SCOPE')
    proxy=proxy_observation(context);proxy_policy(spec,proxy)
    result=measure(spec);result['proxy_observation']=proxy
    out=canonical({'schema_version':1,'operation':'NETWORK','status':'OBSERVED','actual':result,
                   'duration_ms':result['duration_ms']})
    sys.stdout.buffer.write(out+b'\n')
except P00Error as e:
    sys.stdout.buffer.write(canonical(e.safe())+b'\n');raise SystemExit(e.code)
except (OSError,ValueError,KeyError,TypeError):
    sys.stdout.buffer.write(b'{"exit":18,"reason":"NETWORK_AGENT_FAILURE"}\n');raise SystemExit(18)
'''


def script_bytes(root,*,sources=None):
    root=Path(root);parts=[PRELUDE]
    for name in ('errors','codec','network_probe'):
        source=(sources.read(f'src/aifilm_p00/{name}.py') if sources is not None else
                (root/'src/aifilm_p00'/f'{name}.py').read_bytes())
        encoded=base64.b64encode(source).decode('ascii')
        parts.append(f"m=types.ModuleType('aifilm_p00.{name}');m.__package__='aifilm_p00';sys.modules[m.__name__]=m\n"
                     f"exec(compile(base64.b64decode('{encoded}'),'<reviewed-{name}>','exec'),m.__dict__)\n")
    return (''.join(parts)+MAIN).encode('utf-8')


def network_command(root,system_directory,target,user,spec,python_executable,*,sources=None):
    endpoint(spec);data=canonical({'spec':spec,'user':user if spec['context']=='GUEST' else None})
    request=base64.b64encode(data).decode('ascii');require(len(request)<=20000,10,'NETWORK_REQUEST_CAP')
    if spec['context']=='GUEST':
        argv=(windows_path(system_directory)+'\\wsl.exe','--distribution',distro_name(target),
              '--user',user_name(user),'--exec','/usr/bin/python3','-I','-S','-B','-',request)
    else:argv=(windows_path(python_executable),'-I','-S','-B','-',request)
    return Command(argv,'NETWORK_'+spec['context'],30,script_bytes(root,sources=sources),False)


def parse_network(raw,spec):
    require(type(raw) is bytes and len(raw)<=10*1024**2 and raw.endswith(b'\n'),22,'NETWORK_CAPTURE_INCOMPLETE')
    result=loads(raw)
    require(type(result) is dict and result.get('operation')=='NETWORK' and result.get('status')=='OBSERVED'
            and type(result.get('actual')) is dict,15,'NETWORK_CAPTURE_SCHEMA')
    actual=result['actual']
    require(actual.get('endpoint_id')==spec['endpoint_id'] and actual.get('context')==spec['context'],16,'NETWORK_ENDPOINT_MISMATCH')
    require(type(actual.get('duration_ms')) is int and 0<=actual['duration_ms']<=30000,22,'NETWORK_COLLECTOR_TIMEOUT')
    require(actual.get('proxy_observation',{}).get('context')==spec['context'],15,'NETWORK_PROXY_OBSERVATION_REQUIRED')
    proxy_policy(spec,actual['proxy_observation'])
    if actual.get('status')=='OBSERVED':
        m=actual.get('measurements',{})
        require(all(m.get(k) is True for k in ('dns','tcp','tls_chain_hostname','https','eof'))
                and m.get('http_status')==spec['expected_status'],19,'NETWORK_MEASUREMENT_INCOMPLETE')
    else:require(actual.get('status')=='FAIL' and actual.get('normalized_exit')==14,15,'NETWORK_FAILURE_SCHEMA')
    return result


class NativeNetwork:
    def __init__(self,driver):self.driver=driver
    def run(self,plan,coordinator,spec):
        d=self.driver;s=plan['semantic']
        require(coordinator.held and coordinator.fence is not None,12,'NETWORK_ADMISSION_REQUIRED')
        require(spec in s.get('endpoints',[]),12,'NETWORK_ENDPOINT_NOT_APPROVED')
        import os
        require(not any(os.environ.get(k) for k in ('http_proxy','https_proxy','all_proxy','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY')),
                14,'NETWORK_PROXY_CONTEXT')
        from ..content import content_identity
        require(content_identity(d.root)['source_content_digest']==s['build_digest'],16,'NETWORK_SOURCE_DRIFT')
        # The endpoint list and proxy policy are immutable in the exact plan.
        cmd=network_command(d.root,d.api.system_directory(),s['target']['name'],s['target']['user'],spec,sys.executable,sources=d.source_pins)
        def before(w):
            if coordinator.fence['state']=='INTENT':coordinator.native_started(w)
            else:coordinator.native_child_started(w)
        result=d.supervisor.run(cmd,before_resume=before,environment=d.environment,cwd=d.api.system_directory())
        require(result.exit_code==0,14 if result.exit_code==14 else 11,'NETWORK_AGENT_BLOCKED')
        capture=parse_network(result.stdout,spec)
        return {'capture':capture,'agent_digest':sha256(cmd.stdin),'raw_digest':sha256(result.stdout),
                'process_witness':result.native_witness}
