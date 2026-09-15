"""Causal Phase00 native acceptance controller and finalizer.

Catalog presence is never execution proof. Runtime stages use the production
request-entry/session factory. Parent closure consumes only authenticated stage
and oracle records with raw provenance, so process exit alone is never proof.
"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from pathlib import Path
import os

from ..codec import digest,hash_value,instant
from ..errors import P00Error,require
from ..plans import check_plan
from .harness_cases import procedure


def _lab_registration(reg):
    require(reg.get('execution_class')=='LAB',12,'REGISTERED_LAB_REQUIRED')
    require(all(reg.get(k) is True for k in ('controller_external','disposable',
            'no_real_credentials','no_production_mappings')),
            12,'LAB_REGISTRATION_INCOMPLETE')


def authorize_suite(root,suite_ref,case_id):
    from .entry import _entry
    api,store,facts,identity,reg=_entry(Path(root));_lab_registration(reg)
    suite=store.get('lab_acceptance_suite',suite_ref);now=datetime.now(timezone.utc)
    require(suite.get('schema_version')==1 and suite.get('withdrawn') is False
            and suite.get('approved') is True and suite.get('source_kind')=='LAB',
            12,'LAB_SUITE_AUTHORITY')
    for key,value in [('host_id',store.host_id),
                      ('owner_sid',facts['principal']['execution_sid']),
                      ('build_digest',identity['source_content_digest']),
                      ('test_set_digest',identity['test_content_digest'])]:
        require(suite.get(key)==value,16,'LAB_SUITE_SCOPE')
    issued=instant(suite['issued_at']);expires=instant(suite['expires_at'])
    require(issued<=now<=expires and expires-issued<=timedelta(hours=24),
            12,'LAB_SUITE_EXPIRED')
    cases=suite.get('cases')
    require(type(cases) is dict and case_id in cases,12,'LAB_CASE_NOT_APPROVED')
    proc=procedure(case_id);row=cases[case_id]
    require(type(row) is dict and set(row)==
            {'procedure_digest','fixture_ref','requests','stage_refs'},10,'LAB_CASE_SCHEMA')
    require(row['procedure_digest']==proc.procedure_digest,16,'LAB_PROCEDURE_DRIFT')
    require(type(row['requests']) is list and type(row['stage_refs']) is list,
            10,'LAB_CASE_SCHEMA')
    if proc.actual_native_required:
        require(len(row['requests'])==len(proc.routes),12,'LAB_REQUEST_SET')
    else:
        require(row['requests']==[],12,'DOCUMENT_CASE_NATIVE_REQUEST')
    return api,store,facts,identity,reg,suite,row,proc


def _raw_bound(store,raw_ref,actual,subject_digest,reason):
    raw=store.get('lab_case_artifact',raw_ref)
    require(raw.get('schema_version')==1 and raw.get('withdrawn') is False
            and raw.get('actual_digest')==digest(actual)
            and raw.get('subject_digest')==subject_digest,15,reason)


def validate_fixture(store,ref,proc,host_id,owner_sid):
    if not proc.actual_native_required:
        require(ref is None,12,'DOCUMENT_FIXTURE_FORBIDDEN');return None
    hash_value(ref);value=store.get('lab_case_fixture',ref)
    required={'role','schema_version','withdrawn','source_kind','host_id','owner_sid',
              'case_id','procedure_digest','preparations','measurement_refs',
              'controller_external','disposable','no_real_credentials',
              'no_production_mappings'}
    require(set(value)==required and value['schema_version']==1
            and value['withdrawn'] is False and value['source_kind']=='LAB'
            and value['host_id']==host_id and value['owner_sid']==owner_sid
            and value['case_id']==proc.case_id
            and value['procedure_digest']==proc.procedure_digest,
            15,'LAB_FIXTURE_SCHEMA')
    require(tuple(value['preparations'])==proc.preparations
            and type(value['measurement_refs']) is list
            and len(value['measurement_refs'])==len(proc.preparations),
            15,'LAB_FIXTURE_PREPARATIONS')
    require(all(value[k] is True for k in ('controller_external','disposable',
            'no_real_credentials','no_production_mappings')),
            12,'LAB_FIXTURE_ISOLATION')
    observed=[]
    for expected,measurement_ref in zip(proc.preparations,value['measurement_refs']):
        m=store.get('lab_fixture_measurement',measurement_ref)
        req={'role','schema_version','withdrawn','source_kind','host_id','case_id',
             'procedure_digest','preparation','status','actual','raw_artifact_ref',
             'collector_ref','timestamp_utc'}
        require(set(m)==req and m['schema_version']==1 and m['withdrawn'] is False
                and m['source_kind']=='LAB' and m['host_id']==host_id
                and m['case_id']==proc.case_id
                and m['procedure_digest']==proc.procedure_digest
                and m['preparation']==expected and m['status']=='OBSERVED'
                and type(m['actual']) is dict and bool(m['actual']),
                15,'LAB_FIXTURE_MEASUREMENT')
        instant(m['timestamp_utc'])
        collector=store.get('collector_release',m['collector_ref'])
        require(collector.get('withdrawn') is False
                and collector.get('review_verdict')=='PASS',
                15,'LAB_FIXTURE_COLLECTOR')
        subject=digest({'case_id':proc.case_id,
                        'procedure_digest':proc.procedure_digest,
                        'preparation':expected,'host_id':host_id})
        _raw_bound(store,m['raw_artifact_ref'],m['actual'],subject,
                   'LAB_FIXTURE_RAW_BINDING')
        observed.append(deepcopy(m))
    return {'ref':ref,'measurements':observed,'fixture_digest':digest(value)}


def _validate_oracle(store,ref,proc,stage_index,host_id):
    o=store.get('lab_case_oracle',ref)
    req={'role','schema_version','withdrawn','source_kind','host_id','case_id',
         'procedure_digest','stage_index','oracle','status','actual',
         'raw_artifact_ref','collector_ref','timestamp_utc'}
    require(set(o)==req and o['schema_version']==1 and o['withdrawn'] is False
            and o['source_kind']=='LAB' and o['host_id']==host_id
            and o['case_id']==proc.case_id
            and o['procedure_digest']==proc.procedure_digest
            and o['stage_index']==stage_index and o['oracle'] in proc.oracles
            and o['status']=='OBSERVED' and type(o['actual']) is dict
            and bool(o['actual']),15,'LAB_ORACLE_SCHEMA')
    instant(o['timestamp_utc'])
    collector=store.get('collector_release',o['collector_ref'])
    require(collector.get('withdrawn') is False
            and collector.get('review_verdict')=='PASS',
            15,'LAB_ORACLE_COLLECTOR')
    subject=digest({'case_id':proc.case_id,
                    'procedure_digest':proc.procedure_digest,
                    'stage_index':stage_index,'oracle':o['oracle'],'host_id':host_id})
    _raw_bound(store,o['raw_artifact_ref'],o['actual'],subject,
               'LAB_ORACLE_RAW_BINDING')
    return o


def validate_stage(store,ref,proc,index,host_id):
    hash_value(ref);stage=store.get('lab_case_stage',ref)
    req={'role','schema_version','withdrawn','source_kind','host_id','case_id',
         'procedure_digest','stage_index','route','plan_digest','normalized_exit',
         'state','journal_digest','fence_digest','oracle_refs','evidence_ids',
         'timestamp_utc','native_execution_observed','parent_case_executed'}
    require(set(stage)==req and stage['schema_version']==1
            and stage['withdrawn'] is False and stage['host_id']==host_id
            and stage['case_id']==proc.case_id
            and stage['procedure_digest']==proc.procedure_digest
            and stage['stage_index']==index and stage['route']==proc.routes[index]
            and stage['normalized_exit'] in proc.expected_exits
            and stage['parent_case_executed'] is False,
            15,'LAB_STAGE_SCHEMA')
    allowed_sources=('LAB',) if proc.actual_native_required else ('DOCUMENT',)
    require(stage['source_kind'] in allowed_sources
            and stage['native_execution_observed'] is proc.actual_native_required,
            15,'LAB_STAGE_SOURCE')
    instant(stage['timestamp_utc']);hash_value(stage['plan_digest'])
    if stage['journal_digest'] is not None:hash_value(stage['journal_digest'])
    if stage['fence_digest'] is not None:hash_value(stage['fence_digest'])
    require(type(stage['oracle_refs']) is list and bool(stage['oracle_refs'])
            and type(stage['evidence_ids']) is list,15,'LAB_STAGE_EVIDENCE')
    oracles=[_validate_oracle(store,r,proc,index,host_id)
             for r in stage['oracle_refs']]
    require(len({o['oracle'] for o in oracles})==len(oracles),
            15,'LAB_ORACLE_DUPLICATE')
    if proc.actual_native_required:
        entry_oracles={'EXPECTED_REJECTION','ENTRY_GATE','QUALIFICATION_SCOPE'}
        require(stage['journal_digest'] is not None
                or any(o['oracle'] in entry_oracles for o in oracles),
                19,'LAB_STAGE_PROCESS_EXIT_ONLY')
    return {'ref':ref,'stage':stage,'oracles':oracles}


def finalize_case(root,suite_ref,case_id):
    _,store,facts,_,_,_,row,proc=authorize_suite(root,suite_ref,case_id)
    fixture=validate_fixture(store,row['fixture_ref'],proc,store.host_id,
                             facts['principal']['execution_sid'])
    require(len(row['stage_refs'])==len(proc.routes),22,'LAB_CASE_STAGES_INCOMPLETE')
    stages=[validate_stage(store,ref,proc,i,store.host_id)
            for i,ref in enumerate(row['stage_refs'])]
    observed_oracles={o['oracle'] for stage in stages for o in stage['oracles']}
    observed_evidence={eid for stage in stages for eid in stage['stage']['evidence_ids']}
    require(set(proc.oracles)<=observed_oracles,22,'LAB_CASE_ORACLES_INCOMPLETE')
    require(set(proc.required_evidence)<=observed_evidence,
            22,'LAB_CASE_EVIDENCE_INCOMPLETE')
    return {'case_id':case_id,'procedure_digest':proc.procedure_digest,
        'actual_status':'PASS','parent_case_executed':True,
        'native_execution_observed':proc.actual_native_required,
        'stage_refs':list(row['stage_refs']),'fixture_ref':row['fixture_ref'],
        'observed_oracles':sorted(observed_oracles),
        'observed_evidence':sorted(observed_evidence),
        'acceptance_closed':False,'requires_validation_ledger':True,
        'qualification_issued':False,'host_ready':False}


def _request_row(row,proc,index):
    require(0<=index<len(proc.routes) and index<len(row['requests']),
            10,'LAB_STAGE_INDEX')
    request=row['requests'][index]
    require(type(request) is dict
            and set(request)=={'route','interface','plan_ref'}
            and request['route']==proc.routes[index],10,'LAB_STAGE_REQUEST')
    hash_value(request['plan_ref']);return request


def execute_stage(root,suite_ref,case_id,index):
    """Execute one production request stage; never close the parent case."""
    require(os.name=='nt',11,'WINDOWS_X64_REQUIRED')
    _,store,facts,_,_,_,row,proc=authorize_suite(root,suite_ref,case_id)
    validate_fixture(store,row['fixture_ref'],proc,store.host_id,
                     facts['principal']['execution_sid'])
    require(proc.actual_native_required,10,'DOCUMENT_CASE_NO_NATIVE_STAGE')
    request=_request_row(row,proc,index)
    from .request_entry import prepare_execution,execute_prepared
    plan,session=prepare_execution(root,request['interface'],request['plan_ref'])
    s=check_plan(plan)
    if request['route']!='ENTRY_ONLY':
        require(s['purpose']==request['route'],12,'LAB_STAGE_PURPOSE')
    result=None;error=None
    try:result=execute_prepared(request['interface'],plan,session)
    except P00Error as caught:error=caught
    normalized=int(error.code) if error else result.get('exit')
    require(type(normalized) is int and normalized in proc.expected_exits,
            19,'LAB_STAGE_UNEXPECTED_EXIT')
    c=session.coordinator;guard=c.guard;held=guard.held
    rows=[];fence=None;journal_observed=False
    if held:
        rows=c.storage.read_events();fence=c.storage.load_fence();journal_observed=True
    else:
        acquired=guard.acquire()
        if acquired:
            try:
                rows=c.storage.read_events();fence=c.storage.load_fence();journal_observed=True
            finally:guard.release()
    journal_digest=digest([r['sha256'] for r in rows]) if journal_observed else None
    return {'case_id':case_id,'procedure_digest':proc.procedure_digest,
        'stage_index':index,'route':request['route'],'plan_digest':plan['plan_digest'],
        'normalized_exit':normalized,'state':error.reason if error else result.get('state'),
        'journal_digest':journal_digest,'fence_digest':digest(fence) if fence else None,
        'source_kind':'LAB','native_execution_observed':True,
        'parent_case_executed':False,'required_oracles':list(proc.oracles),
        'required_evidence':list(proc.required_evidence),
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'qualification_issued':False,'host_ready':False,'controller_must_exit':held}
