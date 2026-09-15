"""Native request dispatch. Inputs are digest-addressed documents in HKLM anchor.

No port/backend factory argument is accepted by the CLI. Registry reads, guard,
process/filesystem operations are only constructed on explicit native paths.
"""
from pathlib import Path
from datetime import datetime,timezone

from ..codec import hash_value, digest, canonical
from ..errors import require
from ..plans import check_plan, interface_check
from ..observation_binding import C0CaptureRunner, load_capture, compose
from .entry import _entry
from .session_driver import native_session


def requested_plan(store,ref,interface):
    hash_value(ref)
    document=store.get('execution_plan',ref)
    require(document.get('schema_version')==1 and document.get('withdrawn') is False
            and document.get('fixture_only') is not True,15,'EXECUTION_PLAN_DOCUMENT')
    plan=document.get('plan');interface_check(interface,plan)
    return plan


def prepare_execution(root,interface,ref):
    """Resolve the exact pinned plan and construct the production session.

    This is an internal composition seam for the native acceptance controller. It
    does not accept a backend/port and is not exposed by the CLI.
    """
    root=Path(root);_,store,_,_,_=_entry(root)
    plan=requested_plan(store,ref,interface)
    return plan,native_session(root)


def execute_prepared(interface,plan,session):
    if interface=='preflight' and plan['semantic']['purpose']=='PASSIVE':
        return C0CaptureRunner(session).execute(plan)
    if plan['semantic']['purpose']=='RECONCILIATION_ONLY':
        return session.reconcile(plan)
    return session.execute(interface,plan)


def execute(root,interface,ref):
    plan,session=prepare_execution(root,interface,ref)
    return execute_prepared(interface,plan,session)


def draft(root,selection_ref,capture_digest):
    from .filesystem import WindowsPaths
    from .coordination import NativeGuard, NativeJournal
    hash_value(selection_ref);hash_value(capture_digest)
    api,store,facts,identity,reg=_entry(Path(root))
    selection=store.get('binding_selection',selection_ref)
    permit=store.metadata_permit(facts['principal'],identity['source_content_digest'],datetime.now(timezone.utc))
    paths=WindowsPaths(api,store.operators);guard=NativeGuard(api,store.operators)
    require(guard.acquire(),21,'LOCK_BUSY')
    journal=NativeJournal(paths,guard,store.host_id)
    try:
        require(journal.load_fence() is None,21,'UNRESOLVED_FENCE');journal.admission_check()
        capture=load_capture(journal.read_events(),capture_digest,host_id=store.host_id,
                owner_sid=facts['principal']['execution_sid'],build_digest=identity['source_content_digest'])
        proposal=compose(selection,capture,datetime.now(timezone.utc))
        event={'kind':'BINDING_PROPOSED','capture_digest':capture_digest,'selection_ref':selection_ref,
               'proposal':proposal,'proposal_digest':digest(proposal),
               'metadata_authority_ref':permit.approval_digest}
        _,meta=store.one('metadata_initialization')
        additional=meta.get('maximum_additional_bytes')
        require(type(additional) is int and len(canonical(event))+1024<=additional,13,'BINDING_OUTPUT_BUDGET')
        quota=min(additional,2*1024*1024)
        journal.reserve_capacity(quota)
        volume=paths.volume(paths.root)
        require(volume['free_bytes']>=20*1024**3+quota,13,'VOLUME_CAPACITY')
        _,fresh,after,identity_after,_=_entry(Path(root))
        require(identity_after==identity and after['principal']==facts['principal']
                and fresh.generation>=store.generation,16,'BINDING_AUTHORITY_DRIFT')
        require(fresh.get('binding_selection',selection_ref)==selection,16,'BINDING_SELECTION_DRIFT')
        fresh.metadata_permit(after['principal'],identity['source_content_digest'],datetime.now(timezone.utc))
        journal.append_event(event)
        return {'exit':0, 'state':proposal['state'],'source_kind':'DOCUMENT',
                'proposal_digest':event['proposal_digest'],'capture_digest':capture_digest,
                'plan_digest':proposal['plan']['plan_digest'] if proposal['plan'] else None,
                'blockers':proposal['blockers'],'approved':False,'host_ready':False,
                'qualification_issued':False,'protected_output':'JOURNAL'}
    finally:guard.release()
