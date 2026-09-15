"""Original-fence read-only recovery, without resubmitting a native mutation.

The request is an ordinary reviewed RECONCILIATION_ONLY plan. Its optional pinned
recovery_request document selects DIAGNOSE/RECONCILE/PAUSE/CANCEL; it is intent,
not evidence. Absence preserves the existing RECONCILE behavior. Actual writer,
queue and revocation proof must come from the native driver, never from flags.
"""
from copy import deepcopy
from dataclasses import dataclass

from .authority import authorize
from .codec import canonical, digest, hash_value
from .errors import P00Error, require
from .plans import check_plan, interface_check
from .policy import budget_check
from .resume import bind_reconciliation
from .session import Completion

MODES = frozenset({'DIAGNOSE', 'RECONCILE', 'PAUSE', 'CANCEL'})
DIAGNOSTIC_CAP = 256 * 1024


def recovery_intent(request, store, fence):
    """Pinned instructions bind the exact fence, not just a run name."""
    s = interface_check('verify', request)
    require(s['purpose'] == 'RECONCILIATION_ONLY', 12, 'RECONCILIATION_SCOPE')
    ref = s['refs'].get('recovery_request')
    if ref is None:
        return {'mode': 'RECONCILE', 'ref': None, 'scope': {}}
    item = store.get('recovery_request', ref)
    expected = {'host_id': s['host_id'], 'owner_sid': s['owner_sid'],
                'original_plan_digest': fence['plan_digest'],
                'original_fence_digest': digest(fence)}
    require(type(item) is dict and item.get('schema_version') == 1
            and item.get('withdrawn') is False and item.get('fixture_only') is not True,
            15, 'RECOVERY_REQUEST_SCHEMA')
    require(item.get('mode') in MODES and item.get('scope') == expected,
            12, 'RECOVERY_REQUEST_SCOPE')
    return {'mode': item['mode'], 'ref': ref, 'scope': expected}


@dataclass(frozen=True)
class PauseObservation:
    """Observer-only evidence. A request cannot construct this through JSON."""
    raw_evidence: dict
    no_pending_writer: bool
    pending_operations_revoked: bool
    revocation_ref: str
    native_witness: dict | None

    def record(self, action, disposition, request_digest):
        require(self.no_pending_writer is True and self.pending_operations_revoked is True,
                21, 'SAFE_PAUSE_NOT_PROVEN')
        require(type(self.raw_evidence) is dict and bool(self.raw_evidence),
                19, 'PAUSE_EVIDENCE_MISSING')
        hash_value(self.revocation_ref)
        return {'action': action, 'disposition': disposition,
                'request_digest': request_digest, 'revocation_ref': self.revocation_ref,
                'no_pending_writer': True, 'pending_operations_revoked': True,
                'terminal_observed': False, 'postconditions_observed': False,
                'native_witness': deepcopy(self.native_witness),
                'evidence_digest': digest(self.raw_evidence),
                'observations': deepcopy(self.raw_evidence)}


class RecoveryRunner:
    """A single guarded inspection; no queued action is dispatched on any branch."""
    def __init__(self, session):
        self.session = session
        self.d = session.driver
        self.c = session.coordinator

    def execute(self, request):
        s = interface_check('verify', request)
        require(s['purpose'] == 'RECONCILIATION_ONLY', 12, 'RECONCILIATION_SCOPE')
        initial, auth = self.session._fresh('verify', request)
        c = self.c
        with c.acquire_bound_reconciliation(auth, request, initial.context, initial.store,allow_detached=True):
            if c.fence is None:
                from .read_recovery import ReadRecoveryRunner
                return ReadRecoveryRunner(self.session).execute_admitted(request,initial)
            original = c.reconciliation_binding.original_plan
            old = check_plan(original)
            opening_fence = deepcopy(c.fence)
            intent = recovery_intent(request, initial.store, opening_fence)
            step_id = opening_fence.get('witness', {}).get('step_id', '')
            require(type(step_id) is str and step_id.startswith('step-')
                    and step_id[5:].isdigit(), 15, 'PROGRESS_STEP_ID')
            step = int(step_id[5:])
            require(step < len(old['operations']) and
                    old['operations'][step]['action'] == opening_fence['action'],
                    15, 'PROGRESS_ACTION')
            # Recovery reads do not alter the original mutation's witness. New
            # read-process witnesses must be separately journaled by the broker.
            fresh = self.d.refresh(request, coordinator=c, step=step)
            renewed = bind_reconciliation(request, fresh.context, fresh.store, c.fence)
            require(renewed.authority == c.admission, 12, 'RECONCILIATION_AUTHORITY_CHANGED')
            require(fresh.generation >= initial.generation, 15, 'AUTHORITY_ROLLBACK')
            require(digest(c.fence) == digest(opening_fence), 16, 'RECOVERY_FENCE_DRIFT')
            require(recovery_intent(request, fresh.store, opening_fence) == intent,
                    16, 'RECOVERY_REQUEST_DRIFT')
            # Diagnostics may explain a resource/profile failure, but never
            # bypass the output reservation or mutate the host to repair it.
            budget_check(fresh.observed.get('remaining_budgets', s['budgets']),
                         fresh.observed['free_bytes'])
            self.session._generation = fresh.generation
            mode = intent['mode']
            c.storage.append_event({'kind':'RECOVERY_REQUEST_ADMITTED',
                'plan_digest':original['plan_digest'],'request_digest':request['plan_digest'],
                'original_fence_digest':digest(opening_fence),'mode':mode,
                'authority_refs':list(c.admission.authority_document_digests)})
            if mode == 'DIAGNOSE':
                actual = self.d.diagnose(original, step, fresh, c)
                require(type(actual) is dict and bool(actual), 19, 'DIAGNOSTIC_EVIDENCE_MISSING')
                require(digest(c.fence) == digest(opening_fence), 16, 'RECOVERY_FENCE_DRIFT')
                require(len(canonical(actual)) <= DIAGNOSTIC_CAP, 22, 'DIAGNOSTIC_CAP')
                self._reauthorize(request, intent, opening_fence)
                c.storage.append_event({'kind': 'RECOVERY_DIAGNOSTIC',
                    'plan_digest': original['plan_digest'], 'request_digest': request['plan_digest'],
                    'original_fence_digest': digest(opening_fence),
                    'evidence_digest': digest(actual), 'observations': deepcopy(actual)})
                # Bounded public response: no original raw output, path or secret.
                return self._report(request, original, 0, 'DIAGNOSTICS_RECORDED',
                                    True, evidence_digest=digest(actual))
            if mode in ('PAUSE', 'CANCEL'):
                observed = self.d.pause_observation(original, step, fresh, c,
                                                    request=request, disposition=mode)
                require(type(observed) is PauseObservation, 19, 'PAUSE_ADAPTER_TYPE')
                record = observed.record(opening_fence['action'], mode, request['plan_digest'])
                require(digest(c.fence) == digest(opening_fence), 16, 'RECOVERY_FENCE_DRIFT')
                self._reauthorize(request, intent, opening_fence)
                c.safe_pause(record)
                return self._report(request, original, 20,
                    'CANCELLED' if mode == 'CANCEL' else 'SAFE_PAUSE', False,
                    evidence_digest=record['evidence_digest'], step_committed=False)
            # Preserve the classic successful reconciliation contract. A prior
            # SAFE_PAUSE cannot be reinterpreted as a successful operation.
            require(opening_fence['state'] != 'SAFE_PAUSE', 12, 'ORIGINAL_RUN_REVOKED')
            try:
                completed = self.d.reconcile(original, step, fresh, c)
            except P00Error as error:
                from .native.lifecycle import owner_wait_can_relabel
                if int(error.code)==20 and owner_wait_can_relabel(opening_fence,error.reason):
                    require(digest(c.fence)==digest(opening_fence),16,'RECOVERY_FENCE_DRIFT')
                    self._reauthorize(request,intent,opening_fence)
                    require(digest(c.fence)==digest(opening_fence),16,'RECOVERY_FENCE_DRIFT')
                    from .native.lifecycle import owner_verification_wait
                    wait=owner_verification_wait(opening_fence)
                    c.awaiting('AWAITING_OWNER_VERIFICATION',wait)
                    return self._report(request,original,20,'AWAITING_OWNER_VERIFICATION',True,
                        step_committed=False,previous_wait_state=wait.get('previous_state'))
                raise
            require(type(completed) is Completion, 19, 'COMPLETION_ADAPTER_TYPE')
            record = completed.journal_record(opening_fence['action'])
            require(digest(c.fence) == digest(opening_fence), 16, 'RECOVERY_FENCE_DRIFT')
            self._reauthorize(request, intent, opening_fence)
            c.reconcile(record)
            return self._report(request, original, 0, 'RECONCILED', False,
                                step_committed=opening_fence['witness'].get('execution_phase')!='LIVE_REVALIDATION')

    def _reauthorize(self, request, intent, fence):
        # Permissions may expire while observations run. This snapshot is
        # authority only; it does not replace any measured postcondition.
        fresh = self.d.refresh(request, coordinator=None)
        bound = bind_reconciliation(request, fresh.context, fresh.store, fence)
        require(bound.authority == self.c.admission, 12, 'RECONCILIATION_AUTHORITY_CHANGED')
        require(self.session._generation is None or fresh.generation >= self.session._generation,
                15, 'AUTHORITY_ROLLBACK')
        require(recovery_intent(request, fresh.store, fence) == intent, 16, 'RECOVERY_REQUEST_DRIFT')
        self.session._generation = fresh.generation

    def _report(self, request, original, code, state, retained, **extra):
        return {'exit': code, 'state': state, 'original_plan_digest': original['plan_digest'],
                'request_digest': request['plan_digest'], 'fence_retained': retained,
                'source_kind': self.d.source_kind, 'mutation_replayed': False,
                'host_ready': False, 'qualification_issued': False, **extra}
