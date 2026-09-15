"""Actual final source sweep; no cross-host/epoch PASS aggregation.

Historical lifecycle steps come from verified durable journal commits. Restored
content/envelope is an authenticated destination observation, not a fixture or
source-host substitution. This module does not grant HOST_READY.
"""
from copy import deepcopy
from datetime import datetime,timezone
from .. import CONTRACT_DIGEST
from ..codec import digest,instant
from ..errors import require
from ..plans import check_plan
from ..policy import terminal_conditions,TERMINAL_ASSERTIONS,floors,guest_profile,c3_postconditions
from ..authority import authorize
from ..resume import completed_steps
from .network import NativeNetwork


def committed_history(store,rows,ref,current):
    s=current['semantic'];chain=store.get('verification_chain',ref)
    require(chain.get('withdrawn') is False and chain.get('host_id')==s['host_id']
            and chain.get('target_registration')==s['target']['registration_id']
            and chain.get('contract_digest')==CONTRACT_DIGEST,16,'VERIFICATION_CHAIN_SCOPE')
    required={'target_lifecycle':'TARGET_LIFECYCLE','host_restart':'HOST_RESTART','checkpoint':'RESTORE_EXPORT'}
    require(type(chain.get('plans')) is dict and set(chain['plans'])==set(required),15,'LIFECYCLE_CHAIN_MISSING')
    result={}
    for role,purpose in required.items():
        original=store.get('original_plan',chain['plans'][role])['plan'];old=check_plan(original)
        require(old['purpose']==purpose and old['host_id']==s['host_id'] and old['owner_sid']==s['owner_sid']
                and old['target']==s['target'] and old['build_digest']==s['build_digest']
                and old['contract_digest']==s['contract_digest'] and old['execution_class']==s['execution_class'],16,'LIFECYCLE_PLAN_MISMATCH')
        committed=completed_steps(rows,original)
        require(len(committed)==len(old['operations']),19,'LIFECYCLE_NOT_COMMITTED')
        observed=committed[max(committed)]['observations']
        require(observed.get('kind')=='NATIVE_OPERATION_AFTER' and observed.get('source_kind')==s['execution_class']
                and observed.get('plan_digest')==original['plan_digest'],15,'LIFECYCLE_NOT_NATIVE')
        result[role]={'plan_digest':original['plan_digest'],'evidence_digest':digest(observed),'observation':observed}
    times=[instant(result[r]['observation']['timestamp_utc']) for r in required]
    require(times==sorted(times),19,'LIFECYCLE_ORDER')
    checkpoint=result['checkpoint']['observation']['details']['checkpoint']['sha256']
    require(checkpoint==s.get('expected_checkpoint'),15,'LIFECYCLE_CHECKPOINT_MISMATCH')
    return {'entries':result,'checkpoint_digest':checkpoint,'last_source_effect':max(times).isoformat()}


def restore_actual(receipt,plan,critical_files,export_time):
    claim=receipt['claim'];s=plan['semantic']
    require(claim.get('checkpoint_digest')==s['expected_checkpoint']
            and claim.get('source_host_id')==s['host_id']
            and claim.get('source_target_registration')==s['target']['registration_id'],16,'RESTORE_SOURCE_MISMATCH')
    require(claim.get('restore_pass') is True and claim.get('stopped_retained') is True
            and claim.get('preboot_envelope_verified') is True and claim.get('outside_observer_verified') is True,
            19,'RESTORE_ACTUAL_INCOMPLETE')
    require(instant(claim['completed_at'])>=instant(export_time),19,'RESTORE_PRECEDES_EXPORT')
    require(type(claim.get('destination_host_id')) is str and type(claim.get('destination_registration')) is str,
            15,'RESTORE_DESTINATION_MISSING')
    actual=claim.get('critical_files');require(type(actual) is list and len(actual)==len(critical_files),19,'RESTORE_CONTENT_SET')
    bypath={x['path']:x for x in actual};require(len(bypath)==len(actual),15,'RESTORE_CONTENT_DUPLICATE')
    for expected in critical_files:
        found=bypath.get(expected['path']);require(found is not None,19,'RESTORE_CONTENT_MISSING')
        require({k:found.get(k) for k in ('sha256','bytes','uid','gid','mode')}==expected['expected'],19,'RESTORE_CONTENT_MISMATCH')
    return claim


def epoch(fresh,guest,activation_sequence):
    actual=guest['actual'];row=fresh.observed['target']
    return {'host_boot':fresh.observed['host']['boot_utc'],
        'runtime':digest(fresh.observed['material']['runtime']),
        'target_registration':row['registration_id'],'guest_boot':actual['kernel_boot_id'],
        'init_session':actual['pid1_start_ticks'],
        'config_digest':digest({'host':fresh.observed['material']['wslconfig'],'guest':actual['wsl_conf_sha256']}),
        'activation_sequence':activation_sequence}


def endpoint_matrix(plan,binding):
    rows=plan['semantic'].get('endpoints',[]);roles=binding.get('endpoint_roles')
    require(type(rows) is list and bool(rows) and type(roles) is dict,10,'TERMINAL_ENDPOINT_MATRIX')
    ids=[r['endpoint_id'] for r in rows]
    require(len(ids)==len(set(ids)) and set(roles)==set(ids),10,'ENDPOINT_ROLE_COVERAGE')
    required={'UBUNTU_ARCHIVE','UBUNTU_SECURITY'}
    covered={roles[r['endpoint_id']] for r in rows if r['context']=='GUEST'}
    require(required<=covered,10,'GUEST_PACKAGE_ENDPOINTS_MISSING')
    windows_required=binding.get('windows_download_required')
    require(type(windows_required) is bool,10,'WINDOWS_ENDPOINT_APPLICABILITY')
    if windows_required:require(any(r['context']=='WINDOWS' for r in rows),10,'WINDOWS_ENDPOINT_MISSING')
    else:require(type(binding.get('offline_payload_refs')) is list and bool(binding['offline_payload_refs']),15,'OFFLINE_APPLICABILITY_PROOF_MISSING')
    return rows


class NativeTerminalSweep:
    def __init__(self,driver):self.d=driver
    def run(self,plan,coordinator,fresh):
        d=self.d;s=plan['semantic'];b=d.binding
        require(s['purpose']=='SITE_VERIFY' and coordinator.fence['action']=='VERIFY_TERMINAL',12,'TERMINAL_SCOPE')
        history=committed_history(fresh.store,coordinator.storage.read_events(),s['refs']['verification_chain'],plan)
        restore=d._receipt('restore_result',plan,fresh,{'host_id':s['host_id'],
            'checkpoint_digest':s['expected_checkpoint'],'source_target_registration':s['target']['registration_id']})
        restored=restore_actual(restore,plan,b['critical_files'],history['last_source_effect'])
        source=d.proofs['source'];eligible=d._eligible_guest(plan,coordinator,source)
        # Initial guest launch can activate stopped WSL settings; sweep begins
        # only AFTER launch. The start witness comes from a new actual inventory.
        fresh=d.refresh(plan,coordinator=coordinator);authorize('verify',plan,fresh.context,fresh.store)
        first=d._guest(plan,'INVENTORY',coordinator)['capture']
        sequence=digest({'host_restart':history['entries']['host_restart']['evidence_digest'],
                         'target_lifecycle':history['entries']['target_lifecycle']['evidence_digest']})
        start=epoch(fresh,first,sequence);started=datetime.now(timezone.utc)
        require(first['actual']['wsl_conf_sha256']==source['claim']['wsl_conf_sha256'],16,'TERMINAL_GUEST_CONFIG_DRIFT')
        content=d._guest(plan,'ASSERT_CONTENT',coordinator,{'critical_files':b['critical_files']})['capture']
        network=[]
        for spec in endpoint_matrix(plan,b):
            renewed=d.refresh(plan,coordinator=coordinator);authorize('verify',plan,renewed.context,renewed.store)
            require(renewed.observed['material']==fresh.observed['material'],16,'TERMINAL_MATERIAL_DRIFT')
            measured=NativeNetwork(d).run(plan,coordinator,spec)
            require(measured['capture']['actual']['status']=='OBSERVED',14,'TERMINAL_NETWORK_FAILED')
            network.append(measured)
        last=d._guest(plan,'INVENTORY',coordinator)['capture']
        final=d.refresh(plan,coordinator=coordinator);authorize('verify',plan,final.context,final.store)
        end=epoch(final,last,sequence);ended=datetime.now(timezone.utc)
        require(start==end,19,'TERMINAL_EPOCH_CHANGED')
        require(final.observed['material']==fresh.observed['material'],16,'TERMINAL_MATERIAL_DRIFT')
        floors(final.observed['resources']);floors(last['actual']['resources'],guest=True)
        require(s['target']['name'] in final.observed['running'],19,'TERMINAL_SOURCE_NOT_RUNNING')
        writers=d.system.all_writers(coordinator.fence['native'])
        restart=history['entries']['host_restart']['observation']['details']['affected_resources']
        # Actual owner postchecks are linked to the earlier protection pack;
        # no new health PASS is inferred from config preservation alone.
        renewed_post=d._reader(final).selected('c3_postchecks',{'host_id':s['host_id'],
            'plan_digest':history['entries']['host_restart']['plan_digest'],'host_boot':final.observed['host']['boot_utc']},
            owner_assertion=True,not_before=instant(final.observed['host']['boot_utc']))
        require(renewed_post['claim']['rows']==restart['claim']['rows'],19,'TERMINAL_AFFECTED_EVIDENCE_MISMATCH')
        restart=renewed_post
        evidence={
            'identity':{'principal':final.observed['principal'],'target':final.observed['target']},
            'profile':{'profile':final.context.profile,'guest':eligible},
            'resources':{'host':final.observed['resources'],'guest':last['actual']['resources'],'volumes':final.observed['volumes']},
            'network':{'matrix':network,'roles':b['endpoint_roles'],'windows_download_required':b['windows_download_required']},
            'config_preserved':{'material':final.observed['material'],'guest_config_digest':last['actual']['wsl_conf_sha256']},
            'sentinel':content,'affected_resources':restart,
            'source_running':{'running':final.observed['running'],'witness':end},
            'clone_stopped_retained':restore}
        require(set(evidence)==TERMINAL_ASSERTIONS,19,'TERMINAL_ASSERTION_COVERAGE')
        report={'schema_version':1,'source_kind':s['execution_class'],'host_id':s['host_id'],
            'target_id':s['target']['registration_id'],'build_digest':s['build_digest'],'contract_digest':CONTRACT_DIGEST,
            'started_at':started.isoformat(),'ended_at':ended.isoformat(),'start_witness':start,'end_witness':end,
            'checkpoint_digest':s['expected_checkpoint'],'observed_boundary_during_sweep':False,
            'unresolved_source_operations':0,'assertions':{k:{'status':'PASS','evidence_digest':digest(v),'epoch_digest':digest(start)} for k,v in evidence.items()}}
        # Own current VERIFY fence is accounted for; any other pending native
        # writer is impossible to waive via this record and blocks all_writers.
        terminal_conditions(report,ended,s['host_id'],s['target']['registration_id'],s['build_digest'],
            CONTRACT_DIGEST,instant(history['last_source_effect']),s['expected_checkpoint'],source_kind=s['execution_class'])
        return {'state':'OBSERVED','terminal':report,'assertion_evidence':evidence,'history':history,
                'last_source_effect':history['last_source_effect'],'writers':writers,'guest_final':last,
                'host_ready':False,'assessment_status':'NOT_REQUESTED'}
