"""Read-only original-request recovery when no mutation fence was ever written.

Request uses the existing RECONCILIATION_ONLY interface. A pinned recovery_request
selects an exact immutable read set. Intent never proves the writer ended. A
release is a durable evidence record, not deletion/repair of the original log.
"""
from copy import deepcopy
from dataclasses import dataclass, replace

from .authority import authorize
from .codec import canonical, digest, hash_value
from .errors import require
from .plans import check_plan
from .policy import budget_check
from .native.read_recovery import pending_reads


@dataclass(frozen=True)
class ReadRecoveryBinding:
    authority: object
    original_plan: dict
    reads: dict
    intent: dict
    request_digest: str


def _original(request, ctx, store):
    auth = authorize('verify', request, ctx, store)
    s = check_plan(request)
    require(s['purpose'] == 'RECONCILIATION_ONLY' and auth.classes == frozenset({'C0'}),
            12, 'RECONCILIATION_SCOPE')
    require('original_plan' in s['refs'], 12, 'ORIGINAL_PLAN_REQUIRED')
    doc = store.get('original_plan', s['refs']['original_plan'])
    original = doc.get('plan'); old = check_plan(original)
    for key in ('host_id', 'owner_sid', 'run_id', 'execution_class', 'target'):
        require(s[key] == old[key], 12, 'RECONCILIATION_ACTOR')
    require(s['contract_digest'] == old['contract_digest'], 16, 'RECONCILIATION_CONTRACT_MISMATCH')
    return replace(auth, plan_digest=original['plan_digest']), original


def bind_read_recovery(request, ctx, store, rows, *, original_reads=None):
    auth, original = _original(request, ctx, store)
    reads = pending_reads(rows) if original_reads is None else deepcopy(original_reads)
    require(bool(reads), 11, 'NO_READS_TO_RECONCILE')
    s = original['semantic']
    for read in reads.values():
        require(read.get('plan_digest') == original['plan_digest'], 12, 'READ_ORIGINAL_PLAN_SCOPE')
        # Legacy records may lack origin fields, but their exact plan digest is
        # still authenticated. Missing pre-launch witness is NOT fabricated.
        if 'origin' in read:
            require(read['origin'] == {k:s[k] for k in ('run_id','host_id','owner_sid','execution_class')},
                    12, 'READ_ORIGINAL_ACTOR_SCOPE')
    ref = request['semantic']['refs'].get('recovery_request')
    require(ref is not None, 12, 'READ_RECOVERY_REQUEST_REQUIRED')
    item = store.get('recovery_request', ref)
    scope = {'host_id':s['host_id'], 'owner_sid':s['owner_sid'],
             'original_plan_digest':original['plan_digest'], 'original_reads_digest':digest(reads)}
    require(item.get('schema_version') == 1 and item.get('withdrawn') is False
            and item.get('fixture_only') is not True, 15, 'RECOVERY_REQUEST_SCHEMA')
    require(item.get('scope') == scope and item.get('mode') in ('DIAGNOSE','RECONCILE','PAUSE','CANCEL'),
            12, 'RECOVERY_REQUEST_SCOPE')
    return ReadRecoveryBinding(auth, deepcopy(original), deepcopy(reads), deepcopy(item), request['plan_digest'])


@dataclass(frozen=True)
class ReadObservation:
    """Native observer result; no CLI deserialization into a proof object."""
    raw: dict
    terminal: bool
    witness_digest: str | None
    absence_ref: str | None = None

    def release(self, key, entry, request_digest):
        require(self.terminal is True and type(self.raw) is dict and bool(self.raw),
                21, 'READ_PROBE_NOT_TERMINAL')
        witness = entry.get('witness')
        if witness is not None:
            require(self.witness_digest == digest(witness), 19, 'READ_RECOVERY_WITNESS_MISMATCH')
        else:
            hash_value(self.absence_ref)
            require(self.witness_digest is None, 19, 'READ_RECOVERY_WITNESS_MISMATCH')
        value = {'kind':'READ_PROBE_RECOVERY_COMMITTED', 'read_id':key,
                 'original_entry_digest':digest(entry), 'request_digest':request_digest,
                 'witness_digest':self.witness_digest, 'absence_proof_ref':self.absence_ref,
                 'writer_observed_terminal':True, 'observations':deepcopy(self.raw),
                 'evidence_digest':digest(self.raw)}
        check_read_release(entry, value)
        return value


def check_read_release(entry, event):
    """Verify journal linkage. Replaying this is not running a native observer."""
    require(event.get('original_entry_digest') == digest(entry), 15, 'READ_RELEASE_ENTRY_DRIFT')
    hash_value(event.get('request_digest')); hash_value(event.get('evidence_digest'))
    require(type(event.get('observations')) is dict and bool(event['observations'])
            and digest(event['observations']) == event['evidence_digest']
            and event.get('writer_observed_terminal') is True, 15, 'READ_RELEASE_EVIDENCE')
    if entry.get('witness') is not None:
        require(event.get('witness_digest') == digest(entry['witness']), 15, 'READ_RELEASE_WITNESS')
    else:
        require(event.get('witness_digest') is None, 15, 'READ_RELEASE_WITNESS')
        hash_value(event.get('absence_proof_ref'))


class ReadRecoveryRunner:
    """No calls to run(), refresh_recovery(), WSL or a guest collector.

    All candidates are observed before releasing any entry. An append failure
    may commit a subset; a subsequent request must bind the remaining set.
    Previously committed evidence is immutable and never replayed as mutation.
    """
    def __init__(self, session):
        self.session = session; self.d = session.driver; self.c = session.coordinator

    def execute(self, request):
        initial, authority = self.session._fresh('verify', request)
        c = self.c
        with c.acquire_bound_read_recovery(authority, request, initial.context, initial.store):
            return self.execute_admitted(request,initial)

    def execute_admitted(self,request,initial):
        c=self.c
        require(c.held and c.fence is None,12,'READ_RECOVERY_ADMISSION')
        opening = c.read_recovery_binding
        fresh = self.d.refresh_read_recovery(request, c)
        renewed = bind_read_recovery(request, fresh.context, fresh.store, c.storage.read_events())
        require(renewed == opening, 16, 'READ_RECOVERY_AUTHORITY_DRIFT')
        require(fresh.generation >= initial.generation, 15, 'AUTHORITY_ROLLBACK')
        budget_check(request['semantic']['budgets'], fresh.observed['free_bytes'])
        self.d.reserve_read_recovery(request, fresh, c, len(opening.reads))
        mode = opening.intent['mode']; actuals = {}; releases = []
        for key, entry in opening.reads.items():
            actual = self.d.observe_detached_read(entry, fresh, mode == 'DIAGNOSE')
            require(type(actual) is ReadObservation, 19, 'READ_OBSERVER_TYPE')
            require(len(canonical(actual.raw)) <= 256*1024, 22, 'READ_DIAGNOSTIC_CAP')
            actuals[key] = actual.raw
            if mode != 'DIAGNOSE': releases.append(actual.release(key, entry, request['plan_digest']))
        revocation = None
        if mode in ('PAUSE','CANCEL'):
            revocation = self.d.read_run_revocation(opening.original_plan,request,fresh,mode)
            require(type(revocation) is dict and revocation.get('ref') is not None,
                    21,'READ_RUN_REVOCATION_REQUIRED')
            hash_value(revocation['ref'])
        # Check anchor/permission/generation again after potentially slow
        # process observations and before persisting any release.
        final, _ = self.session._fresh('verify', request)
        rebound = bind_read_recovery(request, final.context, final.store, c.storage.read_events())
        require(rebound == opening and final.generation >= fresh.generation,
                16, 'READ_RECOVERY_AUTHORITY_DRIFT')
        require(c.storage.load_fence() is None, 21, 'MUTATION_FENCE_REQUIRES_ORIGINAL_RECOVERY')
        diagnostic = {'kind':'READ_RECOVERY_DIAGNOSTIC', 'request_digest':request['plan_digest'],
                      'original_plan_digest':opening.original_plan['plan_digest'],
                      'read_set_digest':digest(opening.reads), 'mode':mode,
                      'observations':actuals, 'evidence_digest':digest(actuals)}
        c.storage.append_event(diagnostic)
        if revocation is not None:
            c.storage.append_event({'kind':'READ_RECOVERY_RUN_REVOKED',
                'plan_digest':opening.original_plan['plan_digest'],
                'request_digest':request['plan_digest'], 'disposition':mode,
                'revocation':revocation, 'evidence_digest':digest(revocation)})
        for event in releases: c.storage.append_event(event)
        remaining = pending_reads(c.storage.read_events())
        require(mode == 'DIAGNOSE' or not remaining, 21, 'READ_RELEASE_NOT_COMMITTED')
        return {'exit':21 if mode == 'DIAGNOSE' else 20 if mode in ('PAUSE','CANCEL') else 0,
                'state':'READ_DIAGNOSED' if mode == 'DIAGNOSE' else 'READS_RECONCILED',
                'request_digest':request['plan_digest'], 'evidence_digest':digest(actuals),
                'pending_read_count':len(remaining), 'source_kind':self.d.source_kind,
                'mutation_fence_created':False, 'mutation_replayed':False,
                'step_committed':False, 'host_ready':False, 'qualification_issued':False}
