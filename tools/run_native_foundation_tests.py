"""Executable Windows LAB foundation harness; NEVER a qualification issuer.

Actual native execution requires the read-only external HKLM trust chain, exact
code review, registered disposable LAB and an approved lab plan. This source was
not run on Windows during authoring. --list is metadata only and cross-platform.
The harness covers foundation components, NOT all T00/F00 acceptance cases.
"""
import argparse
import json
import os
import sys
from pathlib import Path,PureWindowsPath
from datetime import datetime,timezone,timedelta

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from aifilm_p00.codec import canonical,digest,sha256,instant,token
from aifilm_p00.errors import P00Error,require

CASES=('NF-IDENTITY','NF-JOURNAL-APPEND','NF-PATH-ROUNDTRIP','NF-HARDLINK-REJECT','NF-GUARD-CONTENDER')


def authorization():
    from aifilm_p00.native.entry import _entry
    api,store,facts,identity,registration=_entry(ROOT)
    require(registration.get('execution_class')=='LAB',12,'REGISTERED_LAB_REQUIRED')
    for key in ('controller_external','disposable','no_real_credentials','no_production_mappings'):
        require(registration.get(key) is True,12,'LAB_REGISTRATION_INCOMPLETE')
    ref,plan=store.one('lab_plan')
    require(plan.get('host_id')==store.host_id and plan.get('build_digest')==identity['source_content_digest']
            and plan.get('test_set_digest')==identity['test_content_digest'] and plan.get('approved') is True
            and plan.get('withdrawn') is False,12,'LAB_PLAN_INVALID')
    issued=instant(plan['issued_at']);expires=instant(plan['expires_at']);now=datetime.now(timezone.utc)
    require(issued<=now<=expires and expires-issued<=timedelta(hours=24),12,'LAB_PLAN_EXPIRED')
    require(facts['principal']['execution_sid']==plan.get('owner_sid'),12,'LAB_ACTOR_MISMATCH')
    return api,store,facts,identity,plan,ref


def run_case(case):
    api,store,facts,identity,plan,ref=authorization()
    require(case in plan.get('foundation_cases',[]),12,'LAB_CASE_NOT_APPROVED')
    from aifilm_p00.native.filesystem import WindowsPaths
    from aifilm_p00.native.coordination import NativeGuard,NativeJournal
    paths=WindowsPaths(api,store.operators);guard=NativeGuard(api,store.operators)
    if case=='NF-GUARD-CONTENDER':
        # A separately authorized controller must already hold this host guard.
        require(plan.get('external_holder_session_ref') is not None,12,'EXTERNAL_HOLDER_REQUIRED')
        acquired=guard.acquire()
        if acquired:guard.release()
        require(not acquired,19,'EXPECTED_HOST_GUARD_BUSY')
        return {'case_id':case,'actual_status':'PASS','expected':'LOCK_BUSY','actual':'LOCK_BUSY',
                'source_kind':'LAB','qualification_issued':False,'host_ready':False,
                'persistence':'CONTROLLER_MUST_RECORD_STDOUT','host_alias':store.host_id}
    require(guard.acquire(),21,'LOCK_BUSY')
    try:
        journal=NativeJournal(paths,guard,store.host_id)
        require(journal.load_fence() is None,21,'UNRESOLVED_FENCE')
        run_id=token(plan['run_id']);name='lab-foundation-'+run_id+'-'+case
        scratch=str(PureWindowsPath(paths.root)/name)
        require(plan.get('scratch_names',{}).get(case)==name,12,'LAB_SCRATCH_SCOPE')
        volume=paths.volume(paths.root)
        budget=plan.get('maximum_additional_bytes')
        require(type(budget) is int and 1024**2<=budget<=100*1024**2,12,'LAB_BUDGET_REQUIRED')
        require(volume['free_bytes']>=20*1024**3+budget,13,'VOLUME_CAPACITY')
        # Explicit fixture scope; never delete an existing path or reuse a failed
        # unowned fixture. Retain both artifacts and report for external review.
        paths.create_directory(scratch)
        event={'kind':'LAB_FOUNDATION_START','run_id':run_id,'case_id':case,'lab_plan_ref':ref,
               'source_content_digest':identity['source_content_digest']}
        journal.append_event(event)
        actual={}
        if case=='NF-IDENTITY':
            second=api.principal()
            require(second==facts['principal'],19,'PRINCIPAL_CHANGED')
            actual={'principal_stable':True,'architecture':second['architecture']}
        elif case=='NF-JOURNAL-APPEND':
            before=journal.read_events()
            marker={'kind':'LAB_ROUNDTRIP','run_id':run_id,'challenge_digest':sha256(os.urandom(32))}
            journal.append_event(marker);after=journal.read_events()
            require(len(after)==len(before)+1 and after[-1]['event']==marker,19,'JOURNAL_ROUNDTRIP')
            actual={'committed_frame_digest':after[-1]['sha256'],'append_only':True}
        elif case in ('NF-PATH-ROUNDTRIP','NF-HARDLINK-REJECT'):
            path=str(PureWindowsPath(scratch)/'Phim thử sentinel.bin')
            content=b'AI-FILM SYNTHETIC NATIVE LAB FIXTURE\n'+os.urandom(32)
            paths.write_new(path,content)
            require(paths.read_blob(path,expected=sha256(content))==content,19,'PATH_ROUNDTRIP')
            if case=='NF-HARDLINK-REJECT':
                linked=str(PureWindowsPath(scratch)/'hardlink.bin')
                os.link(path,linked)
                try:
                    with paths.pin(path):pass
                except P00Error as error:
                    require(error.code==12 and error.reason=='HARDLINK_FORBIDDEN',19,'HARDLINK_WRONG_REJECTION')
                else:raise P00Error(19,'HARDLINK_WAS_ACCEPTED')
                actual={'hardlink_rejected':True,'normalized_exit':12}
            else:actual={'written_readback_sha256':sha256(content),'unicode_path_roundtrip':True}
        result={'case_id':case,'actual_status':'PASS','source_kind':'LAB','run_id':run_id,'host_alias':store.host_id,
                'timestamp_utc':datetime.now(timezone.utc).isoformat(),'actual':actual,'fixture_only_data':True,
                'source_content_digest':identity['source_content_digest'],'test_content_digest':identity['test_content_digest'],
                'qualification_issued':False,'closes_parent_T_or_F':False,'host_ready':False}
        output=str(PureWindowsPath(scratch)/'foundation-result.json');raw=canonical(result)
        pending=str(PureWindowsPath(scratch)/('foundation-pending-'+digest(result)[:24]+'.json'))
        journal.append_event({'kind':'LAB_FOUNDATION_RESULT_INTENT','run_id':run_id,'case_id':case,
            'path':output,'pending_path':pending,'report_digest':digest(result),'bytes':len(raw)})
        paths.publish_new(output,raw,pending_path=pending)
        journal.append_event({'kind':'LAB_FOUNDATION_END','run_id':run_id,'case_id':case,'report_digest':digest(result)})
        return result
    finally:guard.release()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--list',action='store_true');g.add_argument('--case',choices=CASES)
    args=p.parse_args()
    if args.list:
        print(json.dumps({'kind':'HARNESS_INVENTORY','cases':[{'case_id':x,'actual_status':'NOT_RUN'} for x in CASES],
                          'full_acceptance_harness':False,'qualification_issued':False,'host_ready':False}))
        return 0
    try:
        require(os.name=='nt',11,'WINDOWS_X64_REQUIRED')
        result=run_case(args.case);sys.stdout.buffer.write(canonical(result)+b'\n');return 0
    except P00Error as error:
        result={**error.safe(),'case_id':args.case,'actual_status':'BLOCKED_OR_FAILED','qualification_issued':False}
        sys.stdout.buffer.write(canonical(result)+b'\n');return int(error.code)
    except (OSError,KeyError,ValueError,TypeError):
        sys.stdout.buffer.write(canonical({'exit':18,'reason':'NATIVE_HARNESS_IO','actual_status':'ERROR','host_ready':False})+b'\n');return 18
if __name__=='__main__':raise SystemExit(main())
