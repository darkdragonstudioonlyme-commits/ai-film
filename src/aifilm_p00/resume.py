"""Bind renewed read-only reconciliation authority to an immutable original plan.

Never rewrite the original plan's purpose/hash. The new authorization is recorded
separately, while the derived Admission keeps the original fence identity. This
module proves authorization linkage only; native terminal proof is still needed.
"""
from dataclasses import dataclass,replace
from copy import deepcopy
from .authority import authorize
from .plans import check_plan
from .codec import digest
from .errors import require

@dataclass(frozen=True)
class ReconciliationBinding:
    authority:object
    original_plan:dict
    reconciliation_plan_digest:str
    original_document_ref:str


def bind_reconciliation(request,ctx,store,fence):
    auth=authorize('verify',request,ctx,store)
    s=check_plan(request)
    require(s['purpose']=='RECONCILIATION_ONLY' and auth.classes==frozenset({'C0'}),12,'RECONCILIATION_SCOPE')
    require('original_plan' in s['refs'],12,'ORIGINAL_PLAN_REQUIRED')
    ref=s['refs']['original_plan']; document=store.get('original_plan',ref)
    original=document.get('plan');old=check_plan(original)
    for k in ('run_id','host_id','owner_sid','execution_class','target'):
        require(s[k]==old[k],12,'RECONCILIATION_ACTOR')
    require(all(fence.get(k)==old[k] for k in ('run_id','host_id','owner_sid')),12,'RECONCILIATION_ACTOR')
    require(fence.get('plan_digest')==original['plan_digest'],15,'ORIGINAL_FENCE_PLAN_MISMATCH')
    require(fence.get('action') in [op['action'] for op in old['operations']],15,'ORIGINAL_FENCE_ACTION_MISMATCH')
    require(old['contract_digest']==s['contract_digest'],16,'RECONCILIATION_CONTRACT_MISMATCH')
    # Reconciliation may inspect an older build's intent; it does not grant
    # permission to replay old mutations under the new build or changed profile.
    bridged=replace(auth,plan_digest=original['plan_digest'],run_id=old['run_id'])
    return ReconciliationBinding(bridged,deepcopy(original),request['plan_digest'],ref)


def completed_steps(rows,plan):
    """Recover committed progress only from terminal + CLEAR frames.

    Rows must first pass durable journal replay/hash-chain verification. Does not
    infer completion from a marker, process exit, INTENT or old APPLIED report.
    """
    s=check_plan(plan); completed={};candidate=None
    for row in rows:
        e=row.get('event',{})
        if e.get('kind')=='READ_RECOVERY_RUN_REVOKED' and e.get('plan_digest')==plan['plan_digest']:
            require(e.get('evidence_digest')==digest(e.get('revocation')),15,'RUN_REVOCATION_INTEGRITY')
            require(False,12,'ORIGINAL_RUN_REVOKED')
        if e.get('kind')=='SET_FENCE':
            f=e.get('record',{})
            candidate=f if f.get('plan_digest')==plan['plan_digest'] and f.get('run_id')==s['run_id'] else None
        elif e.get('kind')=='CLEAR_FENCE' and candidate is not None:
            require(e.get('fence_digest')==digest(candidate),15,'PROGRESS_NOT_COMMITTED')
            require(candidate.get('state')!='SAFE_PAUSE',12,'ORIGINAL_RUN_REVOKED')
            require(candidate.get('state')=='TERMINAL',15,'PROGRESS_NOT_COMMITTED')
            step=candidate.get('witness',{}).get('step_id')
            require(type(step) is str and step.startswith('step-') and step[5:].isdigit(),15,'PROGRESS_STEP_ID')
            index=int(step[5:]);require(index<len(s['operations']),15,'PROGRESS_STEP_RANGE')
            require(candidate.get('action')==s['operations'][index]['action'],15,'PROGRESS_ACTION')
            if candidate.get('witness',{}).get('execution_phase')=='LIVE_REVALIDATION':
                require(len(completed)==len(s['operations']),15,'REVALIDATION_BEFORE_COMMIT')
                observed=candidate.get('terminal_observation',{})
                raw=observed.get('observations',{})
                require(raw.get('kind')=='NATIVE_LIVE_REVALIDATION'
                        and observed.get('evidence_digest')==digest(raw)
                        and raw.get('baseline_digest')==progress_digest(completed)
                        and candidate['witness'].get('original_progress_digest')==progress_digest(completed),
                        15,'REVALIDATION_BASELINE_INTEGRITY')
                candidate=None
                continue
            require(index not in completed,15,'DUPLICATE_COMMITTED_STEP')
            completed[index]=deepcopy(candidate['terminal_observation']);candidate=None
    require(sorted(completed)==list(range(len(completed))),15,'PROGRESS_GAP')
    return completed


def progress_digest(completed):
    """JSON-safe deterministic identity of integer-indexed internal progress."""
    require(type(completed) is dict and all(type(k) is int and k>=0 for k in completed),
            15,'PROGRESS_INDEX_SCHEMA')
    return digest({str(k):v for k,v in sorted(completed.items())})
