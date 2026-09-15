"""Causal Phase00 native acceptance controller and provenance finalizer.

Pre-run authorization and post-run results are separate immutable documents.
Every causal record binds one suite execution_id; a stage cannot be replayed
under another suite/run, and a hash-shaped process/journal claim is never proof.
"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from pathlib import Path
import os

from .. import CONTRACT_DIGEST
from ..codec import digest,hash_value,instant,token
from ..errors import P00Error,require
from ..plans import check_plan
from .harness_cases import procedure


def _lab_registration(reg):
    require(reg.get('execution_class')=='LAB',12,'REGISTERED_LAB_REQUIRED')
    require(all(reg.get(k) is True for k in ('controller_external','disposable',
            'no_real_credentials','no_production_mappings')),
            12,'LAB_REGISTRATION_INCOMPLETE')


def _suite_time(suite,value,reason):
    issued=instant(suite['issued_at']);expires=instant(suite['expires_at']);actual=instant(value)
    require(issued<=actual<=expires,16,reason);return actual


def authorize_suite(root,suite_ref,case_id):
    from .entry import _entry
    hash_value(suite_ref)
    api,store,facts,identity,reg=_entry(Path(root));_lab_registration(reg)
    suite=store.get('lab_acceptance_suite',suite_ref);now=datetime.now(timezone.utc)
    required={'role','schema_version','withdrawn','approved','source_kind','host_id','owner_sid',
              'build_digest','test_set_digest','contract_digest','execution_id',
              'issued_at','expires_at','cases'}
    require(set(suite)==required and suite['schema_version']==1 and suite['withdrawn'] is False
            and suite['approved'] is True and suite['source_kind']=='LAB',12,'LAB_SUITE_AUTHORITY')
    token(suite['execution_id'])
    require(suite['contract_digest']==CONTRACT_DIGEST,16,'LAB_SUITE_SCOPE')
    for key,value in [('host_id',store.host_id),('owner_sid',facts['principal']['execution_sid']),
                      ('build_digest',identity['source_content_digest']),
                      ('test_set_digest',identity['test_content_digest'])]:
        require(suite[key]==value,16,'LAB_SUITE_SCOPE')
    issued=instant(suite['issued_at']);expires=instant(suite['expires_at'])
    require(issued<=now<=expires and expires-issued<=timedelta(hours=24),12,'LAB_SUITE_EXPIRED')
    require(type(suite['cases']) is dict and case_id in suite['cases'],12,'LAB_CASE_NOT_APPROVED')
    proc=procedure(case_id);row=suite['cases'][case_id]
    require(type(row) is dict and set(row)=={'procedure_digest','fixture_spec_ref','requests'},10,'LAB_CASE_SCHEMA')
    require(row['procedure_digest']==proc.procedure_digest,16,'LAB_PROCEDURE_DRIFT')
    require(type(row['requests']) is list,10,'LAB_CASE_SCHEMA')
    if proc.actual_native_required:
        require(len(row['requests'])==len(proc.routes),12,'LAB_REQUEST_SET');hash_value(row['fixture_spec_ref'])
    else:
        require(row['requests']==[] and row['fixture_spec_ref'] is None,12,'DOCUMENT_CASE_NATIVE_REQUEST')
    return api,store,facts,identity,reg,suite,row,proc


def _raw_bound(store,raw_ref,actual,subject_digest,reason):
    raw=store.get('lab_case_artifact',raw_ref)
    require(raw.get('schema_version')==1 and raw.get('withdrawn') is False
            and raw.get('actual_digest')==digest(actual)
            and raw.get('subject_digest')==subject_digest,15,reason)


def _collector(store,ref,reason):
    value=store.get('collector_release',ref)
    require(value.get('withdrawn') is False and value.get('review_verdict')=='PASS',15,reason)
    return value


def validate_fixture_spec(store,ref,proc,host_id,owner_sid):
    if not proc.actual_native_required:
        require(ref is None,12,'DOCUMENT_FIXTURE_FORBIDDEN');return None
    hash_value(ref);value=store.get('lab_case_fixture_spec',ref)
    required={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id',
              'procedure_digest','preparations','controller_external','disposable',
              'no_real_credentials','no_production_mappings'}
    require(set(value)==required and value['schema_version']==1 and value['withdrawn'] is False
            and value['source_kind']=='LAB' and value['host_id']==host_id and value['owner_sid']==owner_sid
            and value['case_id']==proc.case_id and value['procedure_digest']==proc.procedure_digest
            and tuple(value['preparations'])==proc.preparations,15,'LAB_FIXTURE_SPEC')
    require(all(value[k] is True for k in ('controller_external','disposable',
            'no_real_credentials','no_production_mappings')),12,'LAB_FIXTURE_ISOLATION')
    return value


def validate_fixture_result(store,ref,spec_ref,proc,suite_ref,suite,host_id,owner_sid):
    if not proc.actual_native_required:
        require(ref is None,12,'DOCUMENT_FIXTURE_RESULT_FORBIDDEN');return None
    hash_value(ref);value=store.get('lab_case_fixture_result',ref)
    required={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id',
              'procedure_digest','execution_id','suite_ref','fixture_spec_ref','measurement_refs','timestamp_utc'}
    require(set(value)==required and value['schema_version']==1 and value['withdrawn'] is False
            and value['source_kind']=='LAB' and value['host_id']==host_id and value['owner_sid']==owner_sid
            and value['case_id']==proc.case_id and value['procedure_digest']==proc.procedure_digest
            and value['execution_id']==suite['execution_id'] and value['suite_ref']==suite_ref
            and value['fixture_spec_ref']==spec_ref,15,'LAB_FIXTURE_RESULT')
    result_time=_suite_time(suite,value['timestamp_utc'],'LAB_FIXTURE_TIME')
    refs=value['measurement_refs'];require(type(refs) is list and len(refs)==len(proc.preparations),15,'LAB_FIXTURE_PREPARATIONS')
    observed=[]
    for expected,mref in zip(proc.preparations,refs):
        m=store.get('lab_fixture_measurement',mref)
        req={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id','procedure_digest',
             'execution_id','suite_ref','fixture_spec_ref','preparation','status','actual','raw_artifact_ref',
             'collector_ref','timestamp_utc'}
        require(set(m)==req and m['schema_version']==1 and m['withdrawn'] is False and m['source_kind']=='LAB'
                and m['host_id']==host_id and m['owner_sid']==owner_sid and m['case_id']==proc.case_id
                and m['procedure_digest']==proc.procedure_digest and m['execution_id']==suite['execution_id']
                and m['suite_ref']==suite_ref and m['fixture_spec_ref']==spec_ref
                and m['preparation']==expected and m['status']=='OBSERVED'
                and type(m['actual']) is dict and bool(m['actual']),15,'LAB_FIXTURE_MEASUREMENT')
        mt=_suite_time(suite,m['timestamp_utc'],'LAB_FIXTURE_TIME');require(mt<=result_time,16,'LAB_FIXTURE_TIME')
        _collector(store,m['collector_ref'],'LAB_FIXTURE_COLLECTOR')
        subject=digest({'execution_id':suite['execution_id'],'suite_ref':suite_ref,'case_id':proc.case_id,
                        'procedure_digest':proc.procedure_digest,'fixture_spec_ref':spec_ref,
                        'preparation':expected,'host_id':host_id})
        _raw_bound(store,m['raw_artifact_ref'],m['actual'],subject,'LAB_FIXTURE_RAW_BINDING')
        observed.append(deepcopy(m))
    return {'ref':ref,'fixture_digest':digest(value),'timestamp':result_time,'measurements':observed}


def _validate_oracle(store,ref,proc,index,host_id,owner_sid,suite_ref,suite,fixture_result_ref,plan_digest,run_id):
    o=store.get('lab_case_oracle',ref)
    req={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id','procedure_digest',
         'execution_id','suite_ref','fixture_result_ref','stage_index','plan_digest','run_id','oracle','status',
         'actual','raw_artifact_ref','collector_ref','timestamp_utc'}
    source='LAB' if proc.actual_native_required else 'DOCUMENT'
    require(set(o)==req and o['schema_version']==1 and o['withdrawn'] is False and o['source_kind']==source
            and o['host_id']==host_id and o['owner_sid']==owner_sid and o['case_id']==proc.case_id
            and o['procedure_digest']==proc.procedure_digest and o['execution_id']==suite['execution_id']
            and o['suite_ref']==suite_ref and o['fixture_result_ref']==fixture_result_ref
            and o['stage_index']==index and o['plan_digest']==plan_digest and o['run_id']==run_id
            and o['oracle'] in proc.oracles and o['status']=='OBSERVED'
            and type(o['actual']) is dict and bool(o['actual']),15,'LAB_ORACLE_SCHEMA')
    ot=_suite_time(suite,o['timestamp_utc'],'LAB_ORACLE_TIME');_collector(store,o['collector_ref'],'LAB_ORACLE_COLLECTOR')
    subject=digest({'execution_id':suite['execution_id'],'suite_ref':suite_ref,'case_id':proc.case_id,
                    'procedure_digest':proc.procedure_digest,'fixture_result_ref':fixture_result_ref,
                    'stage_index':index,'plan_digest':plan_digest,'run_id':run_id,
                    'oracle':o['oracle'],'host_id':host_id})
    _raw_bound(store,o['raw_artifact_ref'],o['actual'],subject,'LAB_ORACLE_RAW_BINDING')
    return {'record':o,'timestamp':ot}


def _validate_journal(store,ref,proc,index,host_id,owner_sid,suite_ref,suite,fixture_result_ref,plan_digest,run_id):
    hash_value(ref);j=store.get('lab_case_journal',ref)
    req={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id','procedure_digest',
         'execution_id','suite_ref','fixture_result_ref','stage_index','plan_digest','run_id','journal_digest',
         'raw_artifact_ref','collector_ref','timestamp_utc'}
    require(set(j)==req and j['schema_version']==1 and j['withdrawn'] is False and j['source_kind']=='LAB'
            and j['host_id']==host_id and j['owner_sid']==owner_sid and j['case_id']==proc.case_id
            and j['procedure_digest']==proc.procedure_digest and j['execution_id']==suite['execution_id']
            and j['suite_ref']==suite_ref and j['fixture_result_ref']==fixture_result_ref
            and j['stage_index']==index and j['plan_digest']==plan_digest and j['run_id']==run_id,
            15,'LAB_JOURNAL_SCHEMA')
    hash_value(j['journal_digest']);jt=_suite_time(suite,j['timestamp_utc'],'LAB_JOURNAL_TIME')
    _collector(store,j['collector_ref'],'LAB_JOURNAL_COLLECTOR')
    actual={'journal_digest':j['journal_digest'],'plan_digest':plan_digest,'run_id':run_id,'stage_index':index}
    subject=digest({'execution_id':suite['execution_id'],'suite_ref':suite_ref,'case_id':proc.case_id,
                    'procedure_digest':proc.procedure_digest,'fixture_result_ref':fixture_result_ref,
                    'plan_digest':plan_digest,'run_id':run_id,'stage_index':index,'host_id':host_id})
    _raw_bound(store,j['raw_artifact_ref'],actual,subject,'LAB_JOURNAL_RAW_BINDING')
    return {'record':j,'timestamp':jt}


def validate_stage(store,ref,proc,index,host_id,owner_sid,suite_ref,suite,fixture_result_ref):
    hash_value(ref);stage=store.get('lab_case_stage',ref)
    req={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id','procedure_digest',
         'execution_id','suite_ref','fixture_result_ref','stage_index','route','plan_digest','run_id','normalized_exit',
         'state','journal_ref','fence_digest','oracle_refs','evidence_ids','timestamp_utc',
         'native_execution_observed','parent_case_executed'}
    source='LAB' if proc.actual_native_required else 'DOCUMENT'
    require(set(stage)==req and stage['schema_version']==1 and stage['withdrawn'] is False
            and stage['source_kind']==source and stage['host_id']==host_id and stage['owner_sid']==owner_sid
            and stage['case_id']==proc.case_id and stage['procedure_digest']==proc.procedure_digest
            and stage['execution_id']==suite['execution_id'] and stage['suite_ref']==suite_ref
            and stage['fixture_result_ref']==fixture_result_ref and stage['stage_index']==index
            and stage['route']==proc.routes[index] and stage['normalized_exit'] in proc.expected_exits
            and stage['native_execution_observed'] is proc.actual_native_required
            and stage['parent_case_executed'] is False,15,'LAB_STAGE_SCHEMA')
    hash_value(stage['plan_digest']);token(stage['run_id'])
    if stage['fence_digest'] is not None:hash_value(stage['fence_digest'])
    st=_suite_time(suite,stage['timestamp_utc'],'LAB_STAGE_TIME')
    journal=None
    if stage['journal_ref'] is not None:
        journal=_validate_journal(store,stage['journal_ref'],proc,index,host_id,owner_sid,suite_ref,suite,
                                  fixture_result_ref,stage['plan_digest'],stage['run_id'])
        require(journal['timestamp']<=st,16,'LAB_STAGE_TIME')
    require(type(stage['oracle_refs']) is list and bool(stage['oracle_refs']) and type(stage['evidence_ids']) is list,15,'LAB_STAGE_EVIDENCE')
    oracles=[_validate_oracle(store,r,proc,index,host_id,owner_sid,suite_ref,suite,fixture_result_ref,
                              stage['plan_digest'],stage['run_id']) for r in stage['oracle_refs']]
    require(len({o['record']['oracle'] for o in oracles})==len(oracles),15,'LAB_ORACLE_DUPLICATE')
    require(all(o['timestamp']<=st for o in oracles),16,'LAB_STAGE_TIME')
    if proc.actual_native_required:
        entry={'EXPECTED_REJECTION','ENTRY_GATE','QUALIFICATION_SCOPE'}
        require(journal is not None or any(o['record']['oracle'] in entry for o in oracles),19,'LAB_STAGE_PROCESS_EXIT_ONLY')
    return {'ref':ref,'stage':stage,'oracles':[o['record'] for o in oracles],'timestamp':st}


def _result_set(store,ref,proc,suite_ref,suite,host_id,owner_sid):
    hash_value(ref);r=store.get('lab_case_result_set',ref)
    required={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','case_id','procedure_digest',
              'execution_id','suite_ref','fixture_result_ref','stage_refs','timestamp_utc','collector_ref'}
    require(set(r)==required and r['schema_version']==1 and r['withdrawn'] is False and r['source_kind']=='LAB'
            and r['host_id']==host_id and r['owner_sid']==owner_sid and r['case_id']==proc.case_id
            and r['procedure_digest']==proc.procedure_digest and r['execution_id']==suite['execution_id']
            and r['suite_ref']==suite_ref and type(r['stage_refs']) is list,15,'LAB_RESULT_SET')
    rt=_suite_time(suite,r['timestamp_utc'],'LAB_RESULT_TIME');_collector(store,r['collector_ref'],'LAB_RESULT_COLLECTOR')
    if proc.actual_native_required:hash_value(r['fixture_result_ref'])
    else:require(r['fixture_result_ref'] is None,12,'DOCUMENT_FIXTURE_RESULT_FORBIDDEN')
    return {'record':r,'timestamp':rt}


def finalize_case(root,suite_ref,result_ref,case_id):
    _,store,facts,_,_,suite,row,proc=authorize_suite(root,suite_ref,case_id)
    owner=facts['principal']['execution_sid'];spec=validate_fixture_spec(store,row['fixture_spec_ref'],proc,store.host_id,owner)
    result=_result_set(store,result_ref,proc,suite_ref,suite,store.host_id,owner);rr=result['record']
    fixture=validate_fixture_result(store,rr['fixture_result_ref'],row['fixture_spec_ref'],proc,suite_ref,suite,store.host_id,owner)
    require(len(rr['stage_refs'])==len(proc.routes),22,'LAB_CASE_STAGES_INCOMPLETE')
    stages=[validate_stage(store,ref,proc,i,store.host_id,owner,suite_ref,suite,rr['fixture_result_ref'])
            for i,ref in enumerate(rr['stage_refs'])]
    times=[s['timestamp'] for s in stages];require(times==sorted(times),16,'LAB_STAGE_ORDER')
    if fixture is not None and times:require(fixture['timestamp']<=times[0],16,'LAB_FIXTURE_STAGE_ORDER')
    require(not times or times[-1]<=result['timestamp'],16,'LAB_RESULT_TIME')
    observed_oracles={o['oracle'] for stage in stages for o in stage['oracles']}
    observed_evidence={eid for stage in stages for eid in stage['stage']['evidence_ids']}
    require(set(proc.oracles)<=observed_oracles,22,'LAB_CASE_ORACLES_INCOMPLETE')
    require(set(proc.required_evidence)<=observed_evidence,22,'LAB_CASE_EVIDENCE_INCOMPLETE')
    return {'case_id':case_id,'execution_id':suite['execution_id'],'suite_ref':suite_ref,'result_ref':result_ref,
        'procedure_digest':proc.procedure_digest,'actual_status':'PASS','parent_case_executed':True,
        'native_execution_observed':proc.actual_native_required,'stage_refs':list(rr['stage_refs']),
        'fixture_result_ref':rr['fixture_result_ref'],'observed_oracles':sorted(observed_oracles),
        'observed_evidence':sorted(observed_evidence),'acceptance_closed':False,
        'requires_validation_ledger':True,'qualification_issued':False,'host_ready':False}


def _request_row(row,proc,index):
    require(0<=index<len(proc.routes) and index<len(row['requests']),10,'LAB_STAGE_INDEX')
    request=row['requests'][index]
    require(type(request) is dict and set(request)=={'route','interface','plan_ref'}
            and request['route']==proc.routes[index],10,'LAB_STAGE_REQUEST')
    hash_value(request['plan_ref']);return request


def execute_stage(root,suite_ref,fixture_result_ref,case_id,index):
    """Execute one authorized production request stage; never close parent case."""
    require(os.name=='nt',11,'WINDOWS_X64_REQUIRED')
    _,store,facts,_,_,suite,row,proc=authorize_suite(root,suite_ref,case_id)
    owner=facts['principal']['execution_sid'];validate_fixture_spec(store,row['fixture_spec_ref'],proc,store.host_id,owner)
    validate_fixture_result(store,fixture_result_ref,row['fixture_spec_ref'],proc,suite_ref,suite,store.host_id,owner)
    require(proc.actual_native_required,10,'DOCUMENT_CASE_NO_NATIVE_STAGE')
    request=_request_row(row,proc,index)
    from .request_entry import prepare_execution,execute_prepared
    plan,session=prepare_execution(root,request['interface'],request['plan_ref']);s=check_plan(plan)
    if request['route']!='ENTRY_ONLY':require(s['purpose']==request['route'],12,'LAB_STAGE_PURPOSE')
    result=None;error=None
    try:result=execute_prepared(request['interface'],plan,session)
    except P00Error as caught:error=caught
    normalized=int(error.code) if error else result.get('exit')
    require(type(normalized) is int and normalized in proc.expected_exits,19,'LAB_STAGE_UNEXPECTED_EXIT')
    c=session.coordinator;guard=c.guard;held=guard.held;rows=[];fence=None;journal_observed=False
    if held:
        rows=c.storage.read_events();fence=c.storage.load_fence();journal_observed=True
    else:
        acquired=guard.acquire()
        if acquired:
            try:rows=c.storage.read_events();fence=c.storage.load_fence();journal_observed=True
            finally:guard.release()
    journal_digest=digest([r['sha256'] for r in rows]) if journal_observed else None
    return {'case_id':case_id,'execution_id':suite['execution_id'],'suite_ref':suite_ref,
        'fixture_result_ref':fixture_result_ref,'procedure_digest':proc.procedure_digest,'stage_index':index,
        'route':request['route'],'plan_digest':plan['plan_digest'],'run_id':s['run_id'],
        'normalized_exit':normalized,'state':error.reason if error else result.get('state'),
        'journal_digest':journal_digest,'fence_digest':digest(fence) if fence else None,
        'source_kind':'LAB','native_execution_observed':True,'parent_case_executed':False,
        'required_oracles':list(proc.oracles),'required_evidence':list(proc.required_evidence),
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),'qualification_issued':False,
        'host_ready':False,'controller_must_exit':held}
