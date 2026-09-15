"""Pure command-vector compiler, NOT a command executor. Native lab proof pending.
Inputs are literal argument elements. No shell, eval, script interpolation or fallbacks.
"""
from .codec import windows_path,distro_name,user_name
from .errors import P00Error,require

def compile_wsl(action:str,*,system_directory:str,target:str,payload:str|None=None,base_path:str|None=None,user:str|None=None)->list[str]:
    system_directory=windows_path(system_directory); target=distro_name(target)
    exe=system_directory+'\\wsl.exe'
    if action=='INSTALL_DISTRO':
        require(payload is not None and base_path is not None,10,'PAYLOAD_AND_LOCATION_REQUIRED')
        payload=windows_path(payload); base_path=windows_path(base_path)
        require(payload.lower().endswith('.wsl'),10,'WSL_PAYLOAD_EXTENSION')
        return [exe,'--install','--from-file',payload,'--name',target,'--location',base_path,'--no-launch']
    if action=='EXPORT_CHECKPOINT':
        require(payload is not None,10,'CHECKPOINT_PATH_REQUIRED')
        return [exe,'--export',target,windows_path(payload)]
    if action=='IMPORT_NEW_CLONE':
        require(payload is not None and base_path is not None,10,'CHECKPOINT_AND_LOCATION_REQUIRED')
        return [exe,'--import',target,windows_path(base_path),windows_path(payload),'--version','2']
    if action in ('STOP_TARGET','STOP_RETAIN_CLONE'):
        return [exe,'--terminate',target]
    if action=='PROBE_GUEST':
        require(user is not None,10,'NONROOT_USER_REQUIRED')
        return [exe,'--distribution',target,'--user',user_name(user),'--exec','/usr/bin/id','-u']
    raise P00Error(10,'PURPOSE_NOT_ALLOWED')

def compile_feature(feature:str,system_directory:str)->list[str]:
    require(feature in ('VirtualMachinePlatform','Microsoft-Windows-Subsystem-Linux'),10,'FEATURE_NOT_ALLOWED')
    return [windows_path(system_directory)+'\\dism.exe','/Online','/Enable-Feature','/FeatureName:'+feature,'/All','/NoRestart']

def compile_runtime(payload:str,system_directory:str)->list[str]:
    payload=windows_path(payload); require(payload.lower().endswith('.msi'),10,'RUNTIME_PAYLOAD_EXTENSION')
    return [windows_path(system_directory)+'\\msiexec.exe','/i',payload,'/qn','/norestart']


def compile_features(features,system_directory,*,log_path,scratch_directory):
    """One servicing transaction for the two Windows Foundation prerequisites.

    Explicit bounded output paths; no implicit DISM scratch/log locations, online
    repair, source download, reboot or unrelated feature selection.
    """
    require(type(features) is list and features and len(features)==len(set(features))
            and set(features)<={'VirtualMachinePlatform','Microsoft-Windows-Subsystem-Linux'},10,'FEATURE_NOT_ALLOWED')
    return [windows_path(system_directory)+'\\dism.exe','/Online','/Enable-Feature',
            *['/FeatureName:'+f for f in features],'/All','/NoRestart','/LimitAccess',
            '/LogPath:'+windows_path(log_path),'/ScratchDir:'+windows_path(scratch_directory)]
