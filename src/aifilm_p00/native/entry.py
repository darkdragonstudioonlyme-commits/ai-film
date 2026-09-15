"""Native C0 initialization and optional stdout-only metadata entry.

Digest-bound route entry and capture dispatch are in native.request_entry.
No native entry can use tests.helpers, MemoryGuard or a user-chosen trust root.
"""
from datetime import datetime,timezone
from .. import CONTRACT_DIGEST
from ..codec import sha256,canonical,digest
from ..content import content_identity
from ..errors import require
from .winapi import WinAPI
from .inventory import PassiveCollector
from .trust import read_anchor
from .filesystem import WindowsPaths
from .coordination import NativeGuard,NativeJournal,LOG_CAP


def _entry(root):
    api=WinAPI()  # Windows only; never silently use a POSIX or mock backend.
    store=read_anchor(api,root/'contracts')
    facts=PassiveCollector(api).collect()
    require(store.host_id==facts['host']['host_id'],12,'TRUST_HOST_MISMATCH')
    principal=facts['principal'];require(principal['execution_sid'] in store.operators,12,'OPERATOR_NOT_REGISTERED')
    identity=content_identity(root)
    store.one('design')
    _,code=store.one('code')
    require(code.get('verdict')=='PASS' and code.get('withdrawn') is False,11,'CODE_REVIEW_REQUIRED')
    require(code.get('build_digest')==identity['source_content_digest'] and code.get('test_set_digest')==identity['test_content_digest']
            and code.get('contract_digest')==CONTRACT_DIGEST,16,'CODE_REVIEW_CONTENT_MISMATCH')
    _,registration=store.one('registration')
    require(registration.get('host_id')==store.host_id and principal['execution_sid'] in registration.get('operator_sids',[])
            and registration.get('withdrawn') is False and registration.get('execution_class') in ('SITE','LAB'),12,'HOST_REGISTRATION_MISMATCH')
    return api,store,facts,identity,registration


def passive_preflight(root):
    _,store,facts,identity,registration=_entry(root)
    # stdout-only branch D00-07. No persistent output, no guest/proxy probes,
    # no root initialization or locks falsely claimed to have been acquired.
    # Full private inventory is NOT serialized to stdout as a diagnostics escape.
    return {'source_kind':registration['execution_class'],'interface':'preflight',
            'status':'PARTIAL_PASSIVE_INVENTORY','collection_context':'WINDOWS_NATIVE_C0',
            'host_alias':facts['host']['host_id'],'principal_match':True,
            'resources':facts['resources'],'own_context_distro_count':len(facts['distros']['distros']),
            'cross_user_inventory':'NOT_ESTABLISHED','guest_status':'REQUIRES_ACTIVE_PROBE',
            'runtime_feature_network_storage_completeness':'NOT_ESTABLISHED',
            'concurrent_mutation_excluded':False,'source_content_digest':identity['source_content_digest'],
            'full_native_backend_available':False,'host_ready':False}


def initialize_metadata(root):
    api,store,facts,identity,registration=_entry(root)
    permit=store.metadata_permit(facts['principal'],identity['source_content_digest'],datetime.now(timezone.utc))
    paths=WindowsPaths(api,store.operators);guard=NativeGuard(api,store.operators)
    require(guard.acquire(),21,'LOCK_BUSY')
    try:
        # Initial approved maximum is checked against actual volume free space.
        # No software, distro, feature or tuning settings are installed here.
        volume=paths.volume(api.program_data())
        require(volume['filesystem']=='NTFS' and volume['drive_type']==3,11,'LOCAL_NTFS_REQUIRED')
        _,approval=store.one('metadata_initialization')
        budget=approval.get('maximum_additional_bytes')
        require(type(budget) is int and LOG_CAP<=budget<=100*1024**2,12,'METADATA_BUDGET_REQUIRED')
        require(volume['free_bytes']>=20*1024**3+budget,13,'VOLUME_CAPACITY')
        journal=NativeJournal(paths,guard,store.host_id)
        status=journal.initialize_or_verify(permit)
        from pathlib import PureWindowsPath
        from .observations import file_presence
        # Fixed metadata children are part of this explicit metadata approval,
        # not implicit prerequisites installed by preflight/apply.
        for name in ('scratch','records'):
            path=str(PureWindowsPath(paths.root)/name)
            marker=str(PureWindowsPath(path)/'ownership.json')
            value=canonical({'schema_version':1,'host_id':store.host_id,'role':name,'namespace':'AI-FILM-P00-HOST-ADMISSION'})
            if file_presence(paths,path):
                with paths.pin(path,directory=True,protected=True):
                    require(paths.read_blob(marker,expected=sha256(value))==value,16,'METADATA_CHILD_COLLISION')
            else:
                journal.append_event({'kind':'METADATA_CHILD_INTENT','name':name,'authority_digest':permit.approval_digest})
                paths.create_directory(path);paths.write_new(marker,value)
                require(paths.read_blob(marker,expected=sha256(value))==value,15,'METADATA_CHILD_READBACK')
                journal.append_event({'kind':'METADATA_CHILD_OBSERVED','name':name,'identity_digest':sha256(value)})
        return {'source_kind':registration['execution_class'],'interface':'preflight','status':status,
                'host_alias':store.host_id,'global_namespace':'AI-FILM-P00-HOST-ADMISSION','host_ready':False}
    finally:guard.release()
