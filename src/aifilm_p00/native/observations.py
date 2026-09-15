"""Live native observation broker and exact observation-to-profile normalization.

Read-only metadata commands can run before a step INTENT under the already-held
host guard. They never launch a distro, install tools or emit arbitrary stdout.
Guest actions always use the step's durable fence. The broker does not infer
service completion from a successful command.
"""
from __future__ import annotations
import ctypes as C
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

from ..codec import canonical, digest, sha256, loads, instant, windows_path, hash_value
from ..errors import require, P00Error
from .process import Command
from .probes import host_command, parse_host, parse_wsl_list
from .inventory import PassiveCollector
from .filesystem import same_path


def wsl_text(raw):
    require(type(raw) is bytes and len(raw) <= 1024*1024, 22, 'WSL_CAPTURE_CAP')
    try:
        return (raw.decode('utf-16') if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else
                raw.decode('utf-16-le') if b'\0' in raw else raw.decode('utf-8-sig'))
    except UnicodeError:
        raise P00Error(15, 'WSL_CAPTURE_ENCODING') from None


def parse_runtime(raw):
    """Locked WSL --version line order, no localized label/substring guessing.

    Parser/capability eligibility still needs actual native qualification for
    each runtime. Unknown formats block; no `latest` fallback or version coercion.
    """
    lines = [line.strip() for line in wsl_text(raw).splitlines() if line.strip()]
    require(3 <= len(lines) <= 12, 11, 'RUNTIME_VERSION_FORMAT')
    versions = []
    for line in lines[:3]:
        require(':' in line, 11, 'RUNTIME_VERSION_FORMAT')
        value = line.rsplit(':', 1)[1].strip()
        require(re.fullmatch(r'\d+(?:\.\d+){2,5}(?:[-+][A-Za-z0-9.-]+)?', value) is not None,
                11, 'RUNTIME_VERSION_FORMAT')
        versions.append(value)
    return {'version': versions[0], 'kernel': versions[1], 'wslg': versions[2],
            'raw_digest': sha256(raw)}


def _rv(row, name):
    v = row.get(name)
    require(type(v) is dict and v.get('status') == 'OBSERVED', 11, 'HOST_FIELD_UNAVAILABLE')
    return v['value']


def normalize_host(passive, live, catalog):
    raw = passive['host']
    require(live.get('status') == 'OBSERVED' and live.get('operation') == 'HOST',
            11, 'HOST_LIVE_REQUIRED')
    build = str(_rv(raw, 'CurrentBuildNumber'))
    require(build == live['build'], 16, 'HOST_CAPTURE_DRIFT')
    edition = _rv(raw, 'EditionID')
    release = _rv(raw, 'DisplayVersion')
    branch = raw.get('insider', {})
    require(branch.get('status') == 'ABSENT', 11, 'INSIDER_OR_UNKNOWN_CHANNEL')
    rows = catalog.get('windows')
    require(type(rows) is list, 15, 'SUPPORT_CATALOG_SCHEMA')
    matches = [r for r in rows if r.get('build') == build and r.get('release') == release
               and r.get('registry_edition') == edition]
    require(len(matches) == 1, 11, 'SUPPORT_PROFILE_UNBOUND')
    row = matches[0]
    require(row.get('os') == 'Windows 11' and row.get('channel') == 'stable'
            and row.get('architecture') == passive['principal']['architecture'] == 'x64'
            and row.get('document_ref') is not None, 15, 'SUPPORT_CATALOG_INVALID')
    instant(row['support_end']); hash_value(row['document_ref'])
    return {'os': row['os'], 'architecture': 'x64', 'edition': row['edition'],
            'channel': 'stable', 'support_end': row['support_end'],
            'virtualization': live['virtualization'], 'build': build,
            'ubr': _rv(raw, 'UBR'), 'release': release, 'host_id': raw['host_id'],
            'boot_utc': live['boot_utc']}


def match_profile(catalog, facts):
    """Key from authenticated catalogue, matched to ACTUAL values, not plan.profile.

    A transition profile may name multiple exact permitted native fact rows.
    Missing fields and unknown observations cannot match by omission/wildcard.
    """
    rows = catalog.get('profiles')
    require(type(rows) is list and bool(rows), 15, 'PROFILE_CATALOG_EMPTY')
    found = []
    for row in rows:
        match = row.get('match')
        require(type(match) is dict and set(match) == {'host','runtime','config_digest'},
                15, 'PROFILE_MATCH_SCHEMA')
        if match == facts:
            require(type(row.get('key')) is dict and bool(row['key']), 15, 'PROFILE_KEY_SCHEMA')
            found.append(row['key'])
    require(len(found) == 1, 16, 'LIVE_PROFILE_NOT_UNIQUE')
    return deepcopy(found[0])


def normalize_distros(raw):
    require(raw.get('status') in ('OBSERVED','ABSENT') and raw.get('coverage') == 'CURRENT_SID_ONLY',
            11, 'DISTRO_INVENTORY_UNAVAILABLE')
    rows = []
    for item in raw['distros']:
        require(type(item.get('name')) is str and type(item.get('base_path')) is str
                and type(item.get('registration_id')) is str, 11, 'DISTRO_ROW_INCOMPLETE')
        path = item['base_path']
        if path.startswith('\\\\?\\') and not path.startswith('\\\\?\\UNC\\'):
            path = path[4:]
        row = {k:item.get(k) for k in ('registration_id','name','wsl_version','default_uid','package_family')}
        row['base_path'] = windows_path(path)
        rows.append(row)
    require(len({r['name'].casefold() for r in rows}) == len(rows)
            and len({r['registration_id'] for r in rows}) == len(rows), 16, 'DISTRO_IDENTITY_COLLISION')
    default = raw.get('default')
    require(default is None or default in {r['registration_id'] for r in rows},
            16, 'DEFAULT_NOT_IN_INVENTORY')
    return {'default': default, 'rows': sorted(rows, key=lambda r:r['registration_id'])}


def target_row(material, target):
    if target['name'] is None:
        return None
    rows = [r for r in material['distros']['rows'] if r['name'].casefold() == target['name'].casefold()]
    require(len(rows) <= 1, 16, 'TARGET_AMBIGUOUS')
    if not rows: return None
    row = rows[0]
    require(row['name'] == target['name'] and same_path(row['base_path'], target['base_path']),
            16, 'TARGET_IDENTITY_MISMATCH')
    if target['registration_id'] is not None:
        require(row['registration_id'] == target['registration_id'], 16, 'TARGET_REGISTRATION_DRIFT')
    return row


class ReadBroker:
    def __init__(self, root, api, paths, supervisor, environment, coordinator, sources):
        self.root=Path(root); self.api=api; self.paths=paths
        self.supervisor=supervisor; self.environment=environment; self.c=coordinator
        self.captures=[]; self.sources=sources

    def run(self, command):
        require(self.c.held and self.c.admission is not None and not command.mutation,
                12, 'READ_ADMISSION_REQUIRED')
        from uuid import uuid4
        ident = 'read-' + uuid4().hex
        detached = self.c.fence is None or self.c.admission.purpose=='RECONCILIATION_ONLY'
        if detached:
            self.c.storage.append_event({'kind':'READ_PROBE_INTENT','read_id':ident,
                 'plan_digest':self.c.admission.plan_digest,'action_id':command.action_id,
                 'origin':{'run_id':self.c.admission.run_id,'host_id':self.c.admission.host_id,
                           'owner_sid':self.c.admission.owner_sid,
                           'execution_class':self.c.admission.execution_class},
                 'command_digest':digest({'argv':list(command.argv),'stdin_digest':sha256(command.stdin),
                                          'mutation':command.mutation}),
                 'issued_at':datetime.now(timezone.utc).isoformat()})
        def before(w):
            if detached:
                self.c.storage.append_event({'kind':'READ_PROBE_STARTED','read_id':ident,'witness':w})
            elif self.c.fence['state']=='INTENT': self.c.native_started(w)
            else: self.c.native_child_started(w)
        try:
            result=self.supervisor.run(command,before_resume=before,environment=self.environment,
                                       cwd=self.api.system_directory())
        except BaseException:
            if detached:
                self.c.storage.append_event({'kind':'READ_PROBE_UNRESOLVED','read_id':ident,
                     'plan_digest':self.c.admission.plan_digest})
            raise
        record={'read_id':ident,'action_id':command.action_id,'native_exit':result.exit_code,
                'stdout_digest':sha256(result.stdout),'stderr_digest':sha256(result.stderr),
                'tree_terminal':result.tree_terminal,'native_witness':result.native_witness,
                'timestamp_utc':datetime.now(timezone.utc).isoformat()}
        self.c.storage.append_event({'kind':'READ_PROBE_RESULT' if detached else 'ACTION_READ_RESULT',**record})
        self.captures.append(record)
        return result

    def host(self, operation, path=None):
        with self.sources.path('native/host-observe.ps1') as script:
            result=self.run(host_command(self.api.system_directory(),script,operation,path))
        require(result.exit_code==0,11,'HOST_COLLECTOR_UNAVAILABLE')
        return parse_host(result.stdout,operation)

    def running(self):
        command=Command((self.api.system_directory()+'\\wsl.exe','--list','--running','--quiet'),
                        'WSL_RUNNING',30)
        result=self.run(command)
        require(result.exit_code==0,11,'WSL_RUNNING_UNAVAILABLE')
        return parse_wsl_list(result.stdout)

    def runtime(self, packaged_evidence):
        command=Command((self.api.system_directory()+'\\wsl.exe','--version'),'WSL_VERSION',30)
        result=self.run(command)
        if result.exit_code!=0:
            require(not packaged_evidence,11,'RUNTIME_QUERY_FAILED')
            return {'status':'ABSENT','version':None,'kernel':None,'package_identity':None}
        runtime=parse_runtime(result.stdout)
        require(type(packaged_evidence) is dict and packaged_evidence.get('installed') is True,
                15,'RUNTIME_PACKAGING_UNPROVEN')
        require(runtime['version'].split('.')[:3] == packaged_evidence['version'].split('.')[:3],
                16,'RUNTIME_PACKAGE_VERSION_MISMATCH')
        return {'status':'PRESENT','version':runtime['version'],'kernel':runtime['kernel'],
                'package_identity':packaged_evidence['identity'],'packaged':True,'channel':'stable'}


def file_presence(paths, path):
    path=windows_path(path); attributes=paths.api.file_attributes(path)
    if attributes == 0xffffffff:
        error=C.get_last_error()
        require(error in (2,3),12 if error==5 else 18,'PATH_STATUS_UNAVAILABLE')
        return False
    require(not attributes & 0x400,12,'REPARSE_POINT_FORBIDDEN')
    return True


def config_observation(paths, path):
    if not file_presence(paths,path): return {'status':'ABSENT','sha256':None}
    with paths.pin(path,confidential=False) as p:
        raw=paths.api.read(p.handle,1024*1024)
        return {'status':'OBSERVED','sha256':sha256(raw),'bytes':len(raw)}


def volume_observations(paths, bindings, budgets):
    require(type(bindings) is dict and set(bindings) == {b['volume_id'] for b in budgets},
            10,'VOLUME_BINDING_SET')
    rows={}
    for key,path in bindings.items():
        value=paths.volume(windows_path(path))
        require(value['volume_id']==key and value['filesystem']=='NTFS' and value['drive_type']==3,
                16,'PHYSICAL_VOLUME_BINDING')
        rows[key]=value
    return rows
