#!/usr/bin/env python3
"""Candidate-profile driven V02 intake; reuses historical common authority semantics."""
from __future__ import annotations
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import timedelta
import argparse,importlib.util,io,json,sys
from pathlib import Path

TOOL=Path(__file__).resolve().parent; ROOT=TOOL.parents[1]
sys.path.insert(0,str(TOOL))
from v02_candidate_profile import ProfileError,load_profile
from v03_binding_producer_common import (V03Error,load_catalog,rule_map,validate_request_shape,
    validate_base_manifest,manifest_contains,validate_slot_obj)

def load_legacy():
    path=TOOL/'v02-authority-intake.py'
    spec=importlib.util.spec_from_file_location('_aifilm_v02_legacy_intake',path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod); return mod

def _get_path(value,parts):
    cur=value
    for p in parts:
        if type(cur) is not dict or p not in cur: raise V03Error('TEMPLATE_PATH')
        cur=cur[p]
    return cur

def _descriptor(legacy,store,manifest,suite,ref,profile):
    d=store.get('lab_campaign_descriptor',ref)
    req={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','build_digest','test_set_digest','contract_digest','execution_id','host_roles','issued_at','expires_at'}
    legacy.require(set(d)==req and d['schema_version']==1 and d['withdrawn'] is False and d['source_kind']=='LAB','CAMPAIGN_DESCRIPTOR_SCHEMA')
    for k in ('host_id','owner_sid','execution_id'): legacy.require(d[k]==suite[k],'CAMPAIGN_DESCRIPTOR_SCOPE')
    for k,pk in [('build_digest','build_digest'),('test_set_digest','test_set_digest'),('contract_digest','contract_digest')]:legacy.require(d[k]==profile[pk],'CAMPAIGN_DESCRIPTOR_SCOPE')
    legacy.require(type(d['host_roles']) is dict and bool(d['host_roles']) and d['issued_at']==suite['issued_at'] and d['expires_at']==suite['expires_at'],'CAMPAIGN_DESCRIPTOR_SCOPE')
    legacy.require(manifest_contains(manifest,'lab_campaign_descriptor',ref),'CAMPAIGN_DESCRIPTOR_MANIFEST');return d

def _manifest_for_suite(legacy,store,suite_ref):
    rows=[]
    for ref in sorted(store.pins.get('lab_base_manifest',frozenset())-getattr(store,'withdrawn',frozenset())):
        try:m=validate_base_manifest(store.get('lab_base_manifest',ref),suite_ref)
        except Exception:continue
        rows.append((ref,m))
    legacy.require(len(rows)==1,'BASE_MANIFEST_SELECTION');return rows[0]

def _validate_plan_template(legacy,store,ref,slot,manifest):
    v=store.get('lab_stage_plan_template',ref)
    req={'role','schema_version','withdrawn','source_kind','campaign_descriptor_ref','case_id','procedure_digest','stage_index','route','interface','semantic_template','created_at'}
    legacy.require(set(v)==req and v['schema_version']==1 and v['withdrawn'] is False and v['source_kind']=='LAB','PLAN_TEMPLATE_SCHEMA')
    legacy.require(v['campaign_descriptor_ref']==slot['campaign_descriptor_ref'] and (v['case_id'],v['procedure_digest'],v['stage_index'],v['route'],v['interface'])==(slot['case_id'],slot['procedure_digest'],slot['stage_index'],slot['route'],slot['interface']),'PLAN_TEMPLATE_SCOPE')
    legacy.require(manifest_contains(manifest,'lab_stage_plan_template',ref) and type(v['semantic_template']) is dict,'PLAN_TEMPLATE_MANIFEST');legacy.parse_time(v['created_at'])
    auto={'semantic.expected_after','semantic.expected_envelope','semantic.refs.restore_envelope','semantic.refs.native_binding','semantic.refs.checkpoint_payload'}
    legacy.require(set(slot['semantic_selectors'])==set(slot['late_fields'])-auto,'SELECTOR_COVERAGE')
    producers={x['producer_stage_index'] for x in slot['producer_dependencies']}
    for path in slot['late_fields']:
        parts=path[len('semantic.'):].split('.');legacy.require(path.startswith('semantic.') and _get_path(v['semantic_template'],parts)=={'$late':path},'PLAN_TEMPLATE_LATE_MARKER')
    for path,sel in slot['semantic_selectors'].items(): legacy.require(type(sel) is dict and set(sel)=={'producer_stage_index','actual_path'} and sel['producer_stage_index'] in producers and type(sel['actual_path']) is list and bool(sel['actual_path']),'SELECTOR_SCHEMA')
    return v

def _validate_binding_template(legacy,store,ref,slot,manifest):
    v=store.get('lab_native_binding_template',ref)
    req={'role','schema_version','withdrawn','source_kind','campaign_descriptor_ref','case_id','procedure_digest','stage_index','route','binding_template','selectors'}
    legacy.require(set(v)==req and v['schema_version']==1 and v['withdrawn'] is False and v['source_kind']=='LAB','BINDING_TEMPLATE_SCHEMA')
    legacy.require(v['campaign_descriptor_ref']==slot['campaign_descriptor_ref'] and (v['case_id'],v['procedure_digest'],v['stage_index'],v['route'])==(slot['case_id'],slot['procedure_digest'],slot['stage_index'],slot['route']),'BINDING_TEMPLATE_SCOPE')
    legacy.require(manifest_contains(manifest,'lab_native_binding_template',ref) and type(v['binding_template']) is dict and type(v['selectors']) is dict,'BINDING_TEMPLATE_MANIFEST')
    producers={x['producer_stage_index'] for x in slot['producer_dependencies']}
    for path,sel in v['selectors'].items(): legacy.require(path.startswith('binding.after_by_action.') and type(sel) is dict and set(sel)=={'producer_stage_index','actual_path'} and sel['producer_stage_index'] in producers and type(sel['actual_path']) is list and bool(sel['actual_path']),'BINDING_SELECTOR')
    return v

def configure(legacy,profile,catalog):
    rules=rule_map(catalog)
    legacy.CANDIDATE_ID=profile['candidate_id']; legacy.CANDIDATE_BINDING_SHA256=PROFILE_SHA
    legacy.SOURCE_COMMIT=profile['source_commit']; legacy.BUILD=profile['build_digest']; legacy.TEST=profile['test_set_digest']; legacy.AUTHORITY_MODEL=profile['authority_model']

    def verify_suite(suite,objects,now):
        required={'role','schema_version','withdrawn','approved','source_kind','host_id','owner_sid','build_digest','test_set_digest','contract_digest','execution_id','issued_at','expires_at','cases'}
        legacy.require(set(suite)==required and suite['schema_version']==1,'SUITE_SCHEMA');legacy.require(suite['withdrawn'] is False and suite['approved'] is True and suite['source_kind']=='LAB','SUITE_STATUS')
        legacy.require(suite['host_id']==legacy.HOST_ID and suite['build_digest']==profile['build_digest'] and suite['test_set_digest']==profile['test_set_digest'] and suite['contract_digest']==profile['contract_digest'],'SUITE_SCOPE')
        issued=legacy.parse_time(suite['issued_at']);expires=legacy.parse_time(suite['expires_at']);legacy.require(issued<=now<=expires and expires-issued<=timedelta(hours=24),'SUITE_TIME')
        legacy.require(isinstance(suite['execution_id'],str) and suite['execution_id'],'SUITE_EXECUTION_ID');legacy.require(isinstance(suite['cases'],dict) and set(suite['cases'])==set(legacy.PROCEDURES),'SUITE_CASE_COVERAGE')
        for cid,proc in legacy.PROCEDURES.items():
            row=suite['cases'][cid];legacy.require(isinstance(row,dict) and set(row)=={'procedure_digest','fixture_spec_ref','requests'} and row['procedure_digest']==proc.procedure_digest and isinstance(row['requests'],list),'SUITE_CASE_SCHEMA',case_id=cid)
            if proc.actual_native_required: legacy.require(isinstance(row['fixture_spec_ref'],str) and legacy.H64.fullmatch(row['fixture_spec_ref']) and len(row['requests'])==len(proc.routes),'SUITE_REQUEST_COUNT',case_id=cid)
            else: legacy.require(row['fixture_spec_ref'] is None and row['requests']==[],'SUITE_DOCUMENT_CASE',case_id=cid)
            for i,req in enumerate(row['requests']):
                rule=rules.get((cid,i));legacy.require(rule is not None and rule['procedure_digest']==proc.procedure_digest and rule['route']==proc.routes[i],'TEMPORAL_RULE_MISSING',case_id=cid,stage=i)
                try: refkey=validate_request_shape(req,rule)
                except V03Error as e: legacy.fail(str(e),case_id=cid,stage=i)
                role={'plan_ref':'execution_plan','derivation_slot_ref':'lab_stage_derivation_slot','entry_probe_ref':'entry_probe_set','reconciliation_slot_ref':'lab_stage_derivation_slot'}[refkey]
                legacy.load_object(objects,req[refkey],role)

    def verify_plan_authorities(suite,store,objects,now):
        srefs=[r for r in store.pins.get('lab_acceptance_suite',frozenset()) if store.get('lab_acceptance_suite',r)==suite];legacy.require(len(srefs)==1,'SUITE_PIN_SELECTION');suite_ref=srefs[0]
        mref,manifest=_manifest_for_suite(legacy,store,suite_ref);desc=_descriptor(legacy,store,manifest,suite,manifest['descriptor_ref'],profile)
        legacy.require(desc['host_id']==legacy.HOST_ID and desc['owner_sid']==suite['owner_sid'],'CAMPAIGN_DESCRIPTOR_SCOPE')
        count=0
        for cid,proc in legacy.PROCEDURES.items():
            for i,req in enumerate(suite['cases'][cid]['requests']):
                rule=rules[(cid,i)];mode=rule['authority_mode']
                if mode=='CONCRETE_PRE_V03':
                    legacy.require(manifest_contains(manifest,'execution_plan',req['plan_ref']),'CONCRETE_PLAN_MANIFEST');refs=[req['plan_ref']]
                elif mode=='ENTRY_PROBE_AUTHORITY':
                    p=store.get('entry_probe_set',req['entry_probe_ref']);need={'role','schema_version','withdrawn','source_kind','host_id','owner_sid','build_digest','test_set_digest','contract_digest','execution_id','case_id','procedure_digest','stage_index','route','interface','plan_ref'}
                    legacy.require(set(p)==need and p['schema_version']==1 and p['withdrawn'] is False and p['source_kind']=='LAB' and (p['host_id'],p['owner_sid'],p['build_digest'],p['test_set_digest'],p['contract_digest'],p['execution_id'])==(suite['host_id'],suite['owner_sid'],suite['build_digest'],suite['test_set_digest'],suite['contract_digest'],suite['execution_id']) and (p['case_id'],p['procedure_digest'],p['stage_index'],p['route'],p['interface'])==(cid,proc.procedure_digest,i,rule['route'],req['interface']),'ENTRY_PROBE_SCHEMA')
                    legacy.require(manifest_contains(manifest,'entry_probe_set',req['entry_probe_ref']) and manifest_contains(manifest,'execution_plan',p['plan_ref']),'ENTRY_PROBE_MANIFEST');refs=[p['plan_ref']]
                else:
                    slot=store.get('lab_stage_derivation_slot',req['derivation_slot_ref'] if mode=='STAGE_DERIVED' else req['reconciliation_slot_ref'])
                    try:validate_slot_obj(slot,rule,profile,manifest)
                    except V03Error as e:legacy.fail(str(e),case_id=cid,stage=i)
                    legacy.require((slot['host_id'],slot['owner_sid'],slot['execution_id'])==(suite['host_id'],suite['owner_sid'],suite['execution_id']),'DERIVATION_SLOT_SCOPE')
                    _descriptor(legacy,store,manifest,suite,slot['campaign_descriptor_ref'],profile)
                    if mode=='STAGE_DERIVED':
                        _validate_plan_template(legacy,store,slot['plan_template_ref'],slot,manifest)
                        if slot['native_binding_template_ref'] is not None:_validate_binding_template(legacy,store,slot['native_binding_template_ref'],slot,manifest)
                        refs=[]
                    else: refs=list(slot['reconciliation_plan_refs'])
                for ref in refs:
                    legacy.require(ref in store.pins.get('execution_plan',frozenset()),'EXECUTION_PLAN_NOT_PINNED',case_id=cid,stage=i);doc,_=legacy.load_object(objects,ref,'execution_plan');plan=doc.get('plan');semantic=legacy.interface_check(req['interface'],plan)
                    if req['route']!='ENTRY_ONLY':legacy.require(semantic['purpose']==req['route'],'PLAN_ROUTE_PURPOSE',case_id=cid,stage=i)
                    ctx=legacy.Context(legacy.HOST_ID,suite['owner_sid'],'LAB',profile['build_digest'],profile['test_set_digest'],semantic['profile'],True,now);legacy.authorize(req['interface'],plan,ctx,store)
                count+=1
        legacy.require(count==133,'TEMPORAL_STAGE_COUNT');return count

    legacy.verify_suite=verify_suite;legacy.verify_plan_authorities=verify_plan_authorities

def main():
    global PROFILE_SHA
    ap=argparse.ArgumentParser();ap.add_argument('--binding',required=True);ap.add_argument('--binding-sha256',required=True);ap.add_argument('--inbox',required=True);ap.add_argument('--catalog',default=str(ROOT/'docs/PHASE00_STAGE_DERIVED_AUTHORITY_DEPENDENCY_CATALOG_V1.json'));args=ap.parse_args()
    try:profile,PROFILE_SHA=load_profile(args.binding,args.binding_sha256);catalog=load_catalog(args.catalog)
    except (ProfileError,V03Error) as e: print(json.dumps({'kind':'V02_AUTHORITY_INTAKE','status':'BLOCKED','reason':str(e),'ready_to_advance':False,'native_execution_started':False},sort_keys=True,separators=(',',':')));return 12
    legacy=load_legacy();configure(legacy,profile,catalog);old=sys.argv;buf=io.StringIO()
    try:
        sys.argv=[str(TOOL/'v02-authority-intake.py'),'--inbox',args.inbox]
        with redirect_stdout(buf): legacy.main()
    except SystemExit as e:
        text=buf.getvalue();
        if text: print(text.rstrip())
        return int(e.code or 1)
    finally:sys.argv=old
    lines=[x for x in buf.getvalue().splitlines() if x.strip()];out=json.loads(lines[-1]);out['candidate_profile_sha256']=PROFILE_SHA;out['temporal_authority_mode_counts']=catalog['authority_mode_counts'];print(json.dumps(out,sort_keys=True,separators=(',',':')));return 0

if __name__=='__main__': raise SystemExit(main())
