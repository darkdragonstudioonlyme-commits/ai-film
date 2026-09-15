"""Validate required native bindings and actual physical output-volume coverage.

A well-formed binding is not observation/permission. NativeStore authentication,
current Windows handles and per-step authorization are still mandatory.
"""
from pathlib import PureWindowsPath
from ..codec import windows_path,integer,hash_value
from ..errors import require

COMMON={'schema_version','host_id','owner_sid','withdrawn','profile_catalog_ref','executable_policy_ref','volume_paths',
        'allocation_lifetimes','scratch_directory','after_by_action','snapshot_maximum_bytes'}
BY_PURPOSE={
 'ENGINE':{'features','dism_log_path','runtime_signers','installed_runtime_versions','timeout_seconds'},
 'CREATE':{'workspace','critical_files','timeout_seconds'},
 'ADOPT':{'workspace','critical_files'},
 'RESTORE_EXPORT':{'export_path','timeout_seconds'},
 'RESTORE_IMPORT':{'timeout_seconds'},
 'RESTORE_VERIFY':{'critical_files','timeout_seconds'},
 'TARGET_LIFECYCLE':{'critical_files'},
 'HOST_RESTART':set(),'DISCOVERY':set(),'PASSIVE':set(),
 'RECONCILIATION_ONLY':set(),
 'SITE_VERIFY':{'critical_files','endpoint_roles','windows_download_required','offline_payload_refs'},
 'SUPPORT_BUNDLE':{'snapshot_selector','bundle_context','bundle_output','incomplete_bundle_output','assessment_output'}}


def validate_binding(binding,s):
    require(type(binding) is dict and COMMON|BY_PURPOSE[s['purpose']]<=set(binding),10,'NATIVE_BINDING_FIELDS')
    require(binding['schema_version']==1 and binding['withdrawn'] is False
            and binding['host_id']==s['host_id'] and binding['owner_sid']==s['owner_sid'],12,'NATIVE_BINDING_SCOPE')
    hash_value(binding['profile_catalog_ref']);hash_value(binding['executable_policy_ref']);windows_path(binding['scratch_directory'])
    integer(binding['snapshot_maximum_bytes'],1024,100*1024**2)
    require(type(binding['after_by_action']) is dict and set(binding['after_by_action'])=={o['action'] for o in s['operations']},10,'AFTER_BINDING_ACTION_SET')
    for row in binding['after_by_action'].values():
        require(type(row) is dict and set(row)=={'material','captures'} and type(row['material']) is dict
                and type(row['captures']) is list,10,'AFTER_STATE_BINDING_SCHEMA')
    for path in ('dism_log_path','export_path','bundle_output','incomplete_bundle_output','assessment_output'):
        if path in binding:windows_path(binding[path])
    timeouts=binding.get('timeout_seconds',{})
    require(type(timeouts) is dict,10,'TIMEOUT_BINDING')
    from .actuator import SUPPORTED_ACTIONS
    for op in s['operations']:
        if op['action'] in SUPPORTED_ACTIONS:integer(timeouts.get(op['action']),1,7200)
    return binding


def verify_volume_coverage(paths,system_directory,binding,s,remaining,*,pending_snapshots=1):
    """Every actual writing volume must be budgeted, including C0 evidence.

    Read-only payloads may reside elsewhere. A clone allocation is DISTRO; a
    backup-only volume may use BACKUP. OS/distro roles retain 20 GiB reserve.
    """
    budgets={v['volume_id']:v for v in remaining};checked={}
    locations=[('OS',system_directory),('EVIDENCE',paths.root),('EVIDENCE',binding['scratch_directory'])]
    target=s['target']['base_path']
    if target is not None:locations.append(('DISTRO',str(PureWindowsPath(target).parent)))
    for key,role in (('export_path','BACKUP'),('dism_log_path','EVIDENCE'),('bundle_output','EVIDENCE'),
                     ('incomplete_bundle_output','EVIDENCE'),('assessment_output','EVIDENCE')):
        if key in binding:locations.append((role,str(PureWindowsPath(binding[key]).parent)))
    for role,path in locations:
        volume=paths.volume(path);vid=volume['volume_id']
        require(vid in budgets,13,'WRITING_VOLUME_NOT_BUDGETED')
        require(role in budgets[vid]['roles'],13,'WRITING_VOLUME_ROLE_MISSING')
        checked[path]={'volume_id':vid,'role':role,'filesystem':volume['filesystem']}
    metadata_volume=paths.volume(paths.root)['volume_id']
    remaining_peak=sum(budgets[metadata_volume]['allocations'].values())
    integer(pending_snapshots,0,len(s['operations']))
    require(remaining_peak>=binding['snapshot_maximum_bytes']*pending_snapshots
            +binding.get('journal_maximum_additional_bytes',0),13,'EVIDENCE_ALLOCATION_MISSING')
    return checked
