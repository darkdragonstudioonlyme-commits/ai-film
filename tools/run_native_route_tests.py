"""Native registered-LAB route controller, no approval or qualification issuer.

One explicit case per invocation. It calls the production native factory, reads
its protected journal and applies route oracles. It does not fabricate fixture
conditions, reboot the host, delete artifacts or run arbitrary commands. Paused
runs must exit this process before subsequent approved recovery/resume requests.

This is supported-route orchestration, NOT the full T/F fault-injection suite.
"""
import argparse
from datetime import datetime,timezone,timedelta
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from aifilm_p00.codec import canonical,hash_value,instant,token
from aifilm_p00.errors import require,P00Error
from aifilm_p00.plans import OPERATIONS,interface_check
from aifilm_p00.route_observation import route_observation


def authorize_case(root,suite_ref,case_id):
    from aifilm_p00.native.entry import _entry
    from aifilm_p00.native.request_entry import requested_plan
    api,store,facts,identity,reg=_entry(root)
    require(reg.get('execution_class')=='LAB',12,'REGISTERED_LAB_REQUIRED')
    require(all(reg.get(k) is True for k in ('controller_external','disposable','no_real_credentials','no_production_mappings')),
            12,'LAB_REGISTRATION_INCOMPLETE')
    suite=store.get('lab_route_suite',suite_ref);now=datetime.now(timezone.utc)
    require(suite.get('schema_version')==1 and suite.get('withdrawn') is False
            and suite.get('approved') is True and suite.get('fixture_only') is not True,12,'LAB_SUITE_AUTHORITY')
    for key,value in [('host_id',store.host_id),('owner_sid',facts['principal']['execution_sid']),
                      ('build_digest',identity['source_content_digest']),('test_set_digest',identity['test_content_digest'])]:
        require(suite.get(key)==value,16,'LAB_SUITE_SCOPE')
    start=instant(suite['issued_at']);end=instant(suite['expires_at'])
    require(start<=now<=end and end-start<=timedelta(hours=24),12,'LAB_SUITE_EXPIRED')
    cases=suite.get('cases');require(type(cases) is dict and case_id in cases,12,'LAB_CASE_NOT_APPROVED')
    row=cases[case_id]
    require(type(row) is dict and set(row)=={'interface','purpose','plan_ref','expectation'},10,'LAB_CASE_SCHEMA')
    require(row['purpose'] in OPERATIONS,10,'LAB_CASE_PURPOSE')
    plan=requested_plan(store,row['plan_ref'],row['interface'])
    require(plan['semantic']['execution_class']=='LAB' and plan['semantic']['purpose']==row['purpose'],12,'LAB_CASE_PLAN_SCOPE')
    return row,plan,suite,store


def run_case(root,suite_ref,case_id):
    from aifilm_p00.native.session_driver import native_session
    from aifilm_p00.observation_binding import C0CaptureRunner
    row,plan,suite,store=authorize_case(root,suite_ref,case_id)
    original=store.get('original_plan',plan['semantic']['refs']['original_plan'])['plan'] if row['purpose']=='RECONCILIATION_ONLY' else None
    session=native_session(root)
    # This is the concrete factory; the CLI has no plugin/fake injection point.
    if row['purpose']=='PASSIVE':result=C0CaptureRunner(session).execute(plan)
    elif row['purpose']=='RECONCILIATION_ONLY':result=session.reconcile(plan)
    else:result=session.execute(row['interface'],plan)
    c=session.coordinator;guard=c.guard
    # A waiting/uncertain controller retains its guard until process exit.
    # Reuse that held handle only for this read; never recursive mutex admission.
    held_before=guard.held
    if not held_before:require(guard.acquire(),21,'LOCK_BUSY')
    try:
        rows=c.storage.read_events();fence=c.storage.load_fence()
        observed=route_observation(plan,result,rows,fence,row['expectation'],original_plan=original)
    finally:
        if not held_before:guard.release()
    return {'case_id':case_id,'source_kind':'LAB','actual_status':'ROUTE_EXPECTATION_OBSERVED',
            'source_plan_digest':plan['plan_digest'],'suite_ref':suite_ref,'actual':observed,
            'full_acceptance_harness':False,'qualification_issued':False,'host_ready':False,
            'requires_controller_stdout_capture':True,'controller_must_exit':held_before}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--list',action='store_true');p.add_argument('--suite-ref');p.add_argument('--case-id')
    a=p.parse_args(argv)
    try:
        if a.list:
            require(a.suite_ref is None and a.case_id is None,10,'LIST_NOT_EXECUTION')
            value={'source_kind':'DOCUMENT','supported_route_purposes':sorted(OPERATIONS),
                   'actual_status':'NOT_RUN','full_acceptance_harness':False,'qualification_issued':False,'host_ready':False}
        else:
            hash_value(a.suite_ref);token(a.case_id);value=run_case(ROOT,a.suite_ref,a.case_id)
        sys.stdout.buffer.write(canonical(value)+b'\n');return 0
    except P00Error as e:
        sys.stdout.buffer.write(canonical({**e.safe(),'actual_status':'BLOCKED_OR_FAILED','qualification_issued':False})+b'\n');return int(e.code)
    except (KeyError,TypeError,ValueError,OSError):
        sys.stdout.buffer.write(canonical({'exit':18,'reason':'HARNESS_IO_OR_SCHEMA','host_ready':False,'qualification_issued':False})+b'\n');return 18
if __name__=='__main__':raise SystemExit(main())
