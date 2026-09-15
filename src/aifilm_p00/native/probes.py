"""Fixed native probe compilers and strict output decoding.

These return observations, not PASS attestations. Membership of sudo alone does
not prove sudo readiness; observed PID1 alone does not establish startup safety.
"""
from __future__ import annotations
import base64
import re
from pathlib import Path,PureWindowsPath
from ..codec import windows_path,distro_name,user_name,loads,sha256,canonical
from ..errors import require,P00Error
from .process import Command

GUEST_KEYS=frozenset({'uid','gid','user','groups','home','home_access_writable','os_id','version_id',
    'architecture','kernel','kernel_boot_id','pid1_start_ticks','pid1_comm','logical_cpu',
    'mem_total_kib','mem_available_kib','fs_available_kib','wsl_conf_sha256','completed'})
INTEGER_KEYS={'uid','gid','pid1_start_ticks','logical_cpu','mem_total_kib','mem_available_kib','fs_available_kib'}


def parse_guest(data:bytes):
    require(type(data) is bytes and len(data)<=10*1024**2 and data.endswith(b'\n'),22,'GUEST_CAPTURE_INCOMPLETE')
    result={}
    for line in data.splitlines():
        require(line.count(b'\t')==1,15,'GUEST_FRAME')
        key,value=line.split(b'\t')
        try:
            key=key.decode('ascii'); value=base64.b64decode(value,validate=True).decode('utf-8')
        except (ValueError,UnicodeError): raise P00Error(15,'GUEST_FRAME') from None
        require(key in GUEST_KEYS and key not in result,15,'GUEST_FIELD')
        require(len(value)<=4096 and '\0' not in value,15,'GUEST_VALUE_LIMIT')
        result[key]=value
    require(set(result)==GUEST_KEYS and result['completed']=='1',22,'GUEST_FIELDS_INCOMPLETE')
    for key in INTEGER_KEYS:
        require(re.fullmatch('[0-9]{1,20}',result[key]) is not None,15,'GUEST_NUMBER')
        result[key]=int(result[key]);require(result[key]<2**63,15,'GUEST_NUMBER')
    require(result['home_access_writable'] in ('0','1'),15,'GUEST_BOOLEAN')
    require(re.fullmatch('[0-9a-f-]{36}',result['kernel_boot_id']) is not None,15,'GUEST_BOOT_WITNESS')
    if result['wsl_conf_sha256']!='ABSENT':require(re.fullmatch('[0-9a-f]{64}',result['wsl_conf_sha256']) is not None,15,'GUEST_CONFIG_HASH')
    result['home_access_writable']=result['home_access_writable']=='1'
    result['resources']={'logical_cpu':result['logical_cpu'],'mem_total_bytes':result['mem_total_kib']*1024,
                         'mem_available_bytes':result['mem_available_kib']*1024,'fs_available_bytes':result['fs_available_kib']*1024}
    result['admin_ready']='UNKNOWN';result['startup_known']='UNKNOWN';result['quiesce_possible']='UNKNOWN'
    return result


def guest_command(system_directory,target,user,script:bytes):
    user=user_name(user);target=distro_name(target);system_directory=windows_path(system_directory)
    return Command((system_directory+'\\wsl.exe','--distribution',target,'--user',user,'--exec',
                    '/bin/sh','-s','--','INVENTORY',user),'PROBE_GUEST',30,script,False)


def host_command(system_directory,script_path,operation,path=None):
    require(operation in ('HOST','FEATURES','AUTHENTICODE'),10,'HOST_PROBE_SCOPE')
    system_directory=windows_path(system_directory);script_path=windows_path(script_path)
    data={'operation':operation}
    if operation=='AUTHENTICODE':data['path']=windows_path(path)
    exe=system_directory+'\\WindowsPowerShell\\v1.0\\powershell.exe'
    return Command((exe,'-NoLogo','-NoProfile','-NonInteractive','-File',script_path),
                   'HOST_'+operation,30,canonical(data),False)


def parse_host(data,operation):
    try:data=data.decode('utf-8-sig').encode('utf-8')
    except UnicodeError:raise P00Error(15,'HOST_CAPTURE_ENCODING') from None
    result=loads(data)
    require(type(result) is dict and result.get('operation')==operation,11,'HOST_COLLECTOR_UNAVAILABLE')
    allowed={
        'HOST':{'operation','status','boot_utc','caption','build','architecture','hypervisor_present','virtualization','runtime_packages'},
        'FEATURES':{'operation','status','features'},
        'AUTHENTICODE':{'operation','status','thumbprint'},
    }
    require(set(result)==allowed[operation],15,'HOST_CAPTURE_SCHEMA')
    if operation!='AUTHENTICODE':require(result['status']=='OBSERVED',11,'HOST_COLLECTOR_UNAVAILABLE')
    if operation=='HOST':
        require(type(result['runtime_packages']) is list and len(result['runtime_packages'])<=8,15,'HOST_CAPTURE_SCHEMA')
        require(type(result['virtualization']) is bool and type(result['hypervisor_present']) is bool,15,'HOST_CAPTURE_SCHEMA')
    return result


def parse_wsl_list(data):
    """WSL redirects UTF-16LE on some locked builds; never use lossy decode."""
    require(type(data) is bytes and len(data)<=1024**2,22,'WSL_LIST_CAP')
    try:
        text=data.decode('utf-16') if data.startswith((b'\xff\xfe',b'\xfe\xff')) else data.decode('utf-16-le') if b'\0' in data else data.decode('utf-8-sig')
    except UnicodeError:raise P00Error(15,'WSL_LIST_ENCODING') from None
    names=[line.strip() for line in text.splitlines() if line.strip()]
    require(len(names)<=256 and len({n.casefold() for n in names})==len(names),15,'WSL_LIST_DUPLICATE')
    for name in names:distro_name(name)
    return names
