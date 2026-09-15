"""Journal-based oracles for route harness observations, not phase gate verdicts.

A return code, expected state, or a list of case IDs is never execution proof.
These oracles cover route entry/completion/pause only; the independent native
failure/quality assertions in the acceptance matrix are still separate tests.
"""
from .codec import digest
from .errors import require
from .plans import check_plan
from .resume import completed_steps
from .native.read_recovery import pending_reads



def _pause_release_observed(events,request_digest,original_digest):
    """Match the actual original run/request and durable release, not any pause."""
    for index,event in enumerate(events):
        if event.get('kind')=='READ_RECOVERY_RUN_REVOKED':
            revocation=event.get('revocation')
            if (event.get('request_digest')==request_digest
                and event.get('plan_digest')==original_digest
                and event.get('disposition') in ('PAUSE','CANCEL')
                and type(revocation) is dict and bool(revocation)
                and event.get('evidence_digest')==digest(revocation)
                and any(later.get('kind')=='READ_PROBE_RECOVERY_COMMITTED'
                        and later.get('request_digest')==request_digest
                        for later in events[index+1:])):
                return True
        if event.get('kind')!='SET_FENCE':
            continue
        record=event.get('record',{})
        observation=record.get('pause_observation',{})
        raw=observation.get('observations')
        if not (record.get('state')=='SAFE_PAUSE'
            and record.get('plan_digest')==original_digest
            and observation.get('request_digest')==request_digest
            and observation.get('action')==record.get('action')
            and observation.get('disposition') in ('PAUSE','CANCEL')
            and observation.get('no_pending_writer') is True
            and observation.get('pending_operations_revoked') is True
            and observation.get('terminal_observed') is False
            and observation.get('postconditions_observed') is False
            and type(raw) is dict and bool(raw)
            and observation.get('evidence_digest')==digest(raw)):
            continue
        admitted=any(previous.get('kind')=='RECOVERY_REQUEST_ADMITTED'
            and previous.get('plan_digest')==original_digest
            and previous.get('request_digest')==request_digest
            for previous in events[:index])
        cleared=any(later.get('kind')=='CLEAR_FENCE'
            and later.get('fence_digest')==digest(record)
            for later in events[index+1:])
        if admitted and cleared:
            return True
    return False


def route_observation(plan,result,rows,fence,expectation,*,original_plan=None):
    s=check_plan(plan)
    require(type(result) is dict and result.get('source_kind')=='LAB'
            and result.get('host_ready') is False and result.get('qualification_issued',False) is False,
            19,'HARNESS_RESULT_PROVENANCE')
    require(expectation in ('COMMIT','NOOP','PAUSE','RECONCILE','DIAGNOSE'),10,'HARNESS_EXPECTATION')
    pd=plan['plan_digest'];events=[r['event'] for r in rows]
    reads=pending_reads(rows)
    matched=[e for e in events if e.get('plan_digest')==pd or e.get('request_digest')==pd]
    require(bool(matched),19,'HARNESS_NO_JOURNAL_EVIDENCE')
    count=None
    original_digest=None
    if s['purpose']=='RECONCILIATION_ONLY':
        old=check_plan(original_plan)
        require(all(s[k]==old[k] for k in ('host_id','owner_sid','run_id','target')),19,'HARNESS_ORIGINAL_SCOPE')
        original_digest=original_plan['plan_digest']
    if expectation=='DIAGNOSE':
        require(s['purpose']=='RECONCILIATION_ONLY' and result.get('mutation_replayed') is False,
                19,'HARNESS_DIAGNOSTIC_SCOPE')
        require(any(e['kind'] in ('RECOVERY_DIAGNOSTIC','READ_RECOVERY_DIAGNOSTIC') for e in matched)
                and (fence is not None or bool(reads)),19,'HARNESS_DIAGNOSTIC_EVIDENCE')
        require(result['exit'] in (0,21),19,'HARNESS_DIAGNOSTIC_EXIT')
    elif expectation=='RECONCILE':
        require(s['purpose']=='RECONCILIATION_ONLY' and result['exit']==0 and fence is None and not reads,
                19,'HARNESS_RECONCILIATION_UNRESOLVED')
        # Exact request and original-plan linkage was checked by native recovery;
        # its terminal/read release still must be present, not just output state.
        require(result.get('mutation_replayed') is False and (
            any(e['kind']=='READ_PROBE_RECOVERY_COMMITTED' and e.get('request_digest')==pd for e in events)
            or (result.get('state')=='RECONCILED' and result.get('original_plan_digest')==original_digest
                and bool(completed_steps(rows,original_plan)))),
            19,'HARNESS_RECONCILIATION_EVIDENCE')
    elif expectation=='PAUSE':
        require(result['exit']==20,19,'HARNESS_PAUSE_EXIT')
        if fence is not None:
            require(fence['plan_digest']==pd and fence['state'] in ('AWAITING_REBOOT','AWAITING_USER_INIT','AWAITING_OWNER_VERIFICATION'),
                    19,'HARNESS_PAUSE_FENCE')
        else:
            require(s['purpose']=='RECONCILIATION_ONLY' and result.get('step_committed') is False
                    and result.get('request_digest')==pd and not reads
                    and _pause_release_observed(events,pd,original_digest),
                    19,'HARNESS_PAUSE_REVOCATION')
    elif s['purpose']=='PASSIVE' and expectation=='COMMIT':
        require(result['exit']==0 and fence is None and not reads,19,'HARNESS_C0_UNRESOLVED')
        captures=[e for e in matched if e['kind']=='C0_CAPTURE_COMMITTED']
        require(len(captures)==1 and captures[0]['capture_digest']==result.get('capture_digest')
                and digest(captures[0]['capture'])==result['capture_digest'],19,'HARNESS_C0_CAPTURE')
    else:
        require(s['purpose']!='RECONCILIATION_ONLY' and fence is None and not reads,19,'HARNESS_SESSION_UNRESOLVED')
        complete=completed_steps(rows,plan);count=len(complete)
        require(count==len(s['operations']),19,'HARNESS_STEP_COVERAGE')
        allowed=(0,2,22,23) if s['purpose']=='SUPPORT_BUNDLE' else (0,)
        require(result['exit'] in allowed,19,'HARNESS_ROUTE_EXIT')
        if expectation=='NOOP':
            terminals=[e['record'] for e in events if e['kind']=='SET_FENCE'
                and e['record'].get('plan_digest')==pd and e['record'].get('state')=='TERMINAL'
                and e['record'].get('witness',{}).get('execution_phase')=='LIVE_REVALIDATION']
            require(bool(terminals),19,'HARNESS_NOOP_LIVE_EVIDENCE')
        else:
            require(any(e['kind']=='SESSION_OBSERVED' and e.get('assertions_digest')==digest(e.get('assertions'))
                        for e in matched),19,'HARNESS_FINAL_ASSERTIONS')
    return {'expectation_observed':True,'expectation':expectation,'plan_digest':pd,
            'actual_exit':result['exit'],'journal_digest':digest(rows),
            'completed_step_count':count,'pending_read_count':len(reads),
            'fence_retained':fence is not None,'closes_parent_T_or_F':False,
            'qualification_issued':False,'host_ready':False}
