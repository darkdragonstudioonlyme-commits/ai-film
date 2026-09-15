"""D00-01/02/04/08/10/12/13 pure policy. Observations must come from trusted ports.
These predicates do NOT turn caller-supplied facts into actual host evidence.
"""
from datetime import timedelta
from .codec import integer,instant,digest,fields
from .errors import require,P00Error
GIB=1024**3
HOST_FLOORS={'installed_ram_bytes':8*GIB,'logical_cpu':4,'available_ram_bytes':2*GIB}
GUEST_FLOORS={'logical_cpu':2,'mem_total_bytes':3*GIB,'mem_available_bytes':GIB,'fs_available_bytes':20*GIB}

def floors(actual:dict,guest:bool=False):
    require(type(actual) is dict,11,'RESOURCE_OBSERVATION_MISSING')
    for key,minimum in (GUEST_FLOORS if guest else HOST_FLOORS).items():
        require(key in actual,11,'RESOURCE_OBSERVATION_MISSING')
        integer(actual[key]); require(actual[key]>=minimum,13,'RESOURCE_FLOOR')

def budget_check(budgets:list,free:dict)->list:
    require(type(free) is dict,11,'CAPACITY_OBSERVATION_MISSING')
    result=[]; seen=set()
    for b in budgets:
        volume=b['volume_id']
        require(volume not in seen,10,'DUPLICATE_VOLUME'); seen.add(volume)
        require(volume in free,11,'CAPACITY_OBSERVATION_MISSING'); integer(free[volume])
        reserve=(20 if set(b['roles'])&{'OS','DISTRO'} else 5)*GIB
        peak=sum(integer(x) for x in b['allocations'].values())
        require(free[volume]>=reserve+peak,13,'VOLUME_CAPACITY')
        result.append({'volume_id':volume,'reserve':reserve,'remaining_peak':peak,'free':free[volume]})
    return result

def host_profile(host:dict,now):
    require(host.get('os')=='Windows 11' and host.get('architecture')=='x64',11,'UNSUPPORTED_HOST')
    require(host.get('edition') in ('Home','Pro','Enterprise','Education') and host.get('channel')=='stable',11,'UNSUPPORTED_HOST')
    require(host.get('support_end') is not None,11,'SUPPORT_EVIDENCE_MISSING')
    require(instant(host['support_end'])-now>=timedelta(days=90),11,'SUPPORT_MARGIN')
    require(host.get('virtualization') is True,11,'VIRTUALIZATION_PREREQUISITE')

def runtime_profile(runtime:dict):
    require(runtime.get('status')=='PRESENT' and runtime.get('packaged') is True and runtime.get('channel')=='stable',11,'RUNTIME_PREREQUISITE')
    try:
        version=tuple(int(x) for x in runtime['version'].split('.'))
        require(len(version)>=3 and all(x>=0 for x in version),11,'RUNTIME_VERSION')
    except (ValueError,KeyError,AttributeError): raise P00Error(11,'RUNTIME_VERSION') from None
    require(version[:3]>=(2,4,10),11,'RUNTIME_FLOOR')

def guest_profile(guest:dict):
    require(guest.get('os_id')=='ubuntu' and guest.get('version_id')=='24.04' and guest.get('architecture') in ('amd64','x86_64') and guest.get('wsl_version')==2,11,'GUEST_PROFILE')
    require(type(guest.get('uid')) is int and guest['uid']>0,11,'NONROOT_USER_REQUIRED')
    require(guest.get('home_writable') is True and guest.get('admin_ready') is True,11,'GUEST_USER_PREREQUISITE')
    require(guest.get('startup_known') is True and guest.get('quiesce_possible') is True,11,'GUEST_STARTUP_UNKNOWN')
    require(guest.get('source_class') in ('CLEAN_P00','ADOPT_NONSENSITIVE_QUIESCED'),11,'SOURCE_CLASS_FORBIDDEN')

def drift(expected:dict,observed:dict):
    # Equality is deliberately on material facts only, not free RAM, free disk or IP.
    require(type(observed) is dict and expected==observed,16,'MATERIAL_DRIFT')

def protection(pack:dict|None,host_id:str,target_id:str|None,now,source_witness:str):
    require(type(pack) is dict,11,'PROTECTION_INCOMPLETE')
    require(pack.get('host_id')==host_id and pack.get('coverage_complete') is True,11,'IMPACT_COVERAGE_UNKNOWN')
    require(pack.get('owner_authorized') is True,12,'PROTECTION_OWNER_PERMISSION')
    require(pack.get('source_witness')==source_witness,16,'CONSISTENCY_BOUNDARY_DRIFT')
    require(pack.get('sealed_at') is not None and instant(pack['sealed_at'])<=now,11,'PROTECTION_NOT_PREEXISTING')
    rows=pack.get('rows'); require(type(rows) is list,11,'IMPACT_ROWS_MISSING')
    if not rows:
        require(target_id is None and pack.get('clean_host_absent') is True and pack.get('windows_writers_safe') is True,11,'PROTECTION_INCOMPLETE')
    require(pack.get('windows_writers_safe') is True,11,'WINDOWS_WRITERS_UNPROTECTED')
    seen=set()
    for row in rows:
        rid=row.get('resource_id'); require(type(rid) is str and rid not in seen,11,'IMPACT_ROW_ID'); seen.add(rid)
        require(row.get('authorized') is True,12,'RESOURCE_OWNER_PERMISSION')
        require(bool(row.get('post_assertions')) and bool(row.get('post_actor')),11,'POSTCHECKS_UNDEFINED')
        disposition=row.get('disposition')
        require(disposition in ('CLEAN_REPRODUCIBLE_NON_TARGET','DATA_BEARING_NONSENSITIVE','NON_TARGET_SENSITIVE_OR_MANAGED'),11,'RESOURCE_UNPROTECTED')
        require(row.get('no_writes_since_boundary') is True and row.get('retention_bound') is True,11,'PROTECTION_INCOMPLETE')
        # Target never uses the clean NON_TARGET exception.
        needs_checkpoint=rid==target_id or disposition!='CLEAN_REPRODUCIBLE_NON_TARGET'
        if not needs_checkpoint:
            require(row.get('trusted_seed') is True and row.get('recreation_proof') is True,11,'CLEAN_RECREATION_UNPROVEN')
        else:
            require(row.get('checkpoint_digest') is not None and row.get('restore_checkpoint_digest')==row.get('checkpoint_digest'),15,'CHECKPOINT_PROOF_MISMATCH')
            require(row.get('restore_pass') is True and row.get('independent_ready') is True and row.get('accessible_without_source_runtime') is True,11,'RECOVERY_DEPENDS_ON_SOURCE_RUNTIME')
            require(row.get('restore_environment')=='ISO-EXTERNAL' or disposition=='NON_TARGET_SENSITIVE_OR_MANAGED',11,'INDEPENDENT_PROOF_REQUIRED')
            require(row.get('proof_completed_at') is not None and instant(row['proof_completed_at'])<=instant(pack['sealed_at']),11,'RECOVERY_PROOF_NOT_PREEXISTING')
    require(target_id is None or target_id in seen,11,'TARGET_PROTECTION_MISSING')
    return True

def c3_postconditions(expected_rows:list,actual_rows:list):
    actual={r['resource_id']:r for r in actual_rows}
    for row in expected_rows:
        item=actual.get(row['resource_id'])
        require(item is not None and item.get('authorized') is True,20,'AWAITING_OWNER_VERIFICATION')
        require(item.get('assertions')==row['post_assertions'] and item.get('status')=='PASS',19,'AFFECTED_RESOURCE_POSTCHECK')

def restore_envelope(proof:dict|None,source_class:str,execution_class:str,checkpoint_digest:str,now,expected_envelope:str,pre_c3=False):
    require(source_class in ('CLEAN_P00','ADOPT_NONSENSITIVE_QUIESCED','SYNTHETIC_LAB'),11,'SOURCE_CLASS_FORBIDDEN')
    require(type(proof) is dict,11,'ENVELOPE_MISSING')
    require(proof.get('data_authorized') is True and proof.get('controller_authorized') is True,12,'RESTORE_PERMISSION')
    require(proof.get('checkpoint_digest')==checkpoint_digest,15,'CHECKPOINT_PROOF_MISMATCH')
    require(proof.get('envelope_digest')==expected_envelope,16,'ENVELOPE_DRIFT')
    require(proof.get('no_auto_launch_qualified') is True,11,'NO_AUTO_LAUNCH_UNPROVEN')
    require(proof.get('issued_at') is not None and instant(proof['issued_at'])<=now,11,'PREBOOT_PROOF_MISSING')
    if source_class=='SYNTHETIC_LAB': require(execution_class=='LAB',12,'SYNTHETIC_SITE_FORBIDDEN')
    if proof.get('kind')=='SAME_HOST_CLEAN':
        require(not pre_c3 and source_class=='CLEAN_P00',11,'INDEPENDENT_PROOF_REQUIRED')
        for key in ('trusted_seed','complete_provenance','allowlisted_changes_only','no_custom_startup','no_credentials','ordinary_access_consented','unused_destination'):
            require(proof.get(key) is True,11,'SAME_HOST_DIRTY_OR_UNKNOWN')
        return 'NOT_ISOLATION_SANDBOX'
    require(proof.get('kind')=='ISO-EXTERNAL',11,'ENVELOPE_UNSUPPORTED')
    for key in ('controller_external','network_uplinks_blocked','no_production_writable_mapping','backup_of_record_protected','no_credential_forwarding','device_inventory_verified','allowed_write_surfaces_bound','registered_session','unused_destination'):
        require(proof.get(key) is True,11,'ISOLATION_INCOMPLETE')
    return 'ISO_EXTERNAL_PREBOOT_PROOF'

TERMINAL_ASSERTIONS={'identity','profile','resources','network','config_preserved','sentinel','affected_resources','source_running','clone_stopped_retained'}

def terminal_conditions(report:dict,now,host_id:str,target_id:str,build:str,contract:str,last_source_effect,checkpoint_digest:str,*,source_kind):
    require(source_kind in ('SITE','LAB') and report.get('source_kind')==source_kind and report.get('host_id')==host_id and report.get('target_id')==target_id,19,'TERMINAL_SOURCE_MISMATCH')
    require(report.get('build_digest')==build and report.get('contract_digest')==contract,16,'TERMINAL_BUILD_MISMATCH')
    start=instant(report['started_at']); end=instant(report['ended_at'])
    require(last_source_effect<=start<=end<=now and end-start<=timedelta(minutes=30),19,'TERMINAL_WINDOW')
    require(now-end<=timedelta(minutes=15),19,'TERMINAL_SEAL_EXPIRED')
    required={'host_boot','runtime','target_registration','guest_boot','init_session','config_digest','activation_sequence'}
    a=report.get('start_witness'); b=report.get('end_witness')
    require(type(a) is dict and required==set(a) and a==b and all(v is not None and v!='' for v in a.values()),19,'TERMINAL_EPOCH_UNVERIFIABLE')
    require(report.get('observed_boundary_during_sweep') is False and report.get('unresolved_source_operations')==0,19,'TERMINAL_BOUNDARY')
    require(report.get('checkpoint_digest')==checkpoint_digest,15,'TERMINAL_CHECKPOINT_MISMATCH')
    assertions=report.get('assertions')
    require(type(assertions) is dict and set(assertions)==TERMINAL_ASSERTIONS,19,'TERMINAL_ASSERTIONS_MISSING')
    for v in assertions.values():
        require(type(v) is dict and v.get('status')=='PASS' and v.get('evidence_digest') is not None and v.get('epoch_digest')==digest(a),19,'TERMINAL_ASSERTION')
    return {'eligible_as_of':report['ended_at'],'host_ready':False,'requires_master_acceptance':True}


def terminal(report:dict,now,host_id:str,target_id:str,build:str,contract:str,last_source_effect,checkpoint_digest:str):
    # A LAB report can validate the same actual conditions, never a SITE gate.
    return terminal_conditions(report,now,host_id,target_id,build,contract,last_source_effect,
                               checkpoint_digest,source_kind='SITE')
