"""Passive native identity/registry facts, never launches a distro.

The returned snapshot is protected data. It is NOT automatically gate evidence,
not a qualified active probe and not proof of cross-user inventory completeness.
"""
from __future__ import annotations
import os
from datetime import datetime,timezone
from ..codec import sha256,canonical
from ..errors import require,P00Error


def registry_value(reg,hive,path,name,view=None):
    try:
        with reg.OpenKey(hive,path,0,reg.KEY_READ|(reg.KEY_WOW64_64KEY if view is None else view)) as key:
            value,kind=reg.QueryValueEx(key,name)
            return {'status':'OBSERVED','value':value,'registry_type':kind}
    except FileNotFoundError: return {'status':'ABSENT','value':None}
    except PermissionError: return {'status':'UNAVAILABLE','value':None}


def distro_registry(reg):
    path=r'Software\Microsoft\Windows\CurrentVersion\Lxss'; rows=[]
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER,path,0,reg.KEY_READ) as key:
            try: default=reg.QueryValueEx(key,'DefaultDistribution')[0]
            except FileNotFoundError: default=None
            count=reg.QueryInfoKey(key)[0]
            require(count<=256,11,'DISTRO_INVENTORY_CAP')
            for i in range(count):
                name=reg.EnumKey(key,i)
                with reg.OpenKey(key,name,0,reg.KEY_READ) as child:
                    row={'registration_id':name,'status':'OBSERVED','running':'UNKNOWN'}
                    for source,target in [('DistributionName','name'),('BasePath','base_path'),('Version','wsl_version'),
                                          ('DefaultUid','default_uid'),('PackageFamilyName','package_family')]:
                        try: row[target]=reg.QueryValueEx(child,source)[0]
                        except FileNotFoundError: row[target]=None
                    rows.append(row)
            return {'status':'OBSERVED','default':default,'distros':rows,'coverage':'CURRENT_SID_ONLY'}
    except FileNotFoundError: return {'status':'ABSENT','default':None,'distros':[],'coverage':'CURRENT_SID_ONLY'}
    except PermissionError: return {'status':'UNAVAILABLE','default':None,'distros':[],'coverage':'UNKNOWN'}


def registry_host(reg):
    path=r'SOFTWARE\Microsoft\Windows NT\CurrentVersion'
    out={}
    for name in ('ProductName','EditionID','DisplayVersion','CurrentBuildNumber','UBR','InstallationType','BuildLabEx'):
        out[name]=registry_value(reg,reg.HKEY_LOCAL_MACHINE,path,name)
    guid=registry_value(reg,reg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Microsoft\Cryptography','MachineGuid')
    require(guid['status']=='OBSERVED' and type(guid['value']) is str,11,'HOST_ID_UNAVAILABLE')
    out['host_id']='host_'+sha256(guid['value'].casefold().encode())[:32]
    # Channel is UNKNOWN until trusted support/profile data and actual branch
    # facts have been matched. ProductName alone may not identify Windows 11.
    out['channel']='UNKNOWN'
    out['insider']=registry_value(reg,reg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Microsoft\WindowsSelfHost\Applicability','BranchName')
    return out


class PassiveCollector:
    def __init__(self,api): self.api=api
    def collect(self):
        require(os.name=='nt',11,'WINDOWS_X64_REQUIRED')
        import winreg
        principal=self.api.principal(); host=registry_host(winreg)
        return {'schema_version':1,'source_kind':'NATIVE_OBSERVATION','timestamp_utc':datetime.now(timezone.utc).isoformat(),
                'principal':principal,'host':host,'resources':self.api.resources(),
                'distros':distro_registry(winreg),'guest_status':'REQUIRES_ACTIVE_PROBE',
                'consistent_snapshot':False,'overlap_status':'UNVERIFIED','host_ready':False}


def observed_target(snapshot,bound):
    rows=snapshot['distros']['distros']
    matches=[r for r in rows if r['name'] is not None and r['name'].casefold()==bound['name'].casefold()]
    require(len(matches)<=1,16,'AMBIGUOUS_TARGET')
    if not matches: return {'status':'ABSENT','registration_id':None}
    row=matches[0]
    require(row['name']==bound['name'] and row['base_path'] is not None,16,'TARGET_IDENTITY_MISMATCH')
    if bound.get('registration_id') is not None:
        require(row['registration_id']==bound['registration_id'],16,'TARGET_REGISTRATION_DRIFT')
    return row
