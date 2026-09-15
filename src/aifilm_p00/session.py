"""Per-step session orchestration for the approved D00-07/08 contracts.

No command execution or authority creation lives here. Production construction
uses native.session_driver.NativeDriver. Workspace tests supply explicit ports;
the CLI never accepts a port, observation dictionary, or completion flag.
"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from typing import Protocol, Any

from .authority import Context, Admission, authorize
from .codec import digest
from .errors import P00Error, require
from .plans import interface_check, check_plan
from .policy import budget_check, floors, drift
from .resume import bind_reconciliation, completed_steps, progress_digest


@dataclass(frozen=True)
class Refresh:
    context: Context
    store: Any
    observed: dict
    generation: int
    collection_kind: str = "WORKSPACE_TEST"


@dataclass(frozen=True)
class Completion:
    """Only an observer may construct this; never deserialize from plan/input.

    The evidence object is written into the durable journal before CLEAR. This
    provides replay with an actual after-state rather than an expected snapshot.
    """
    material_after: dict
    raw_evidence: dict
    no_pending_writer: bool
    postconditions_observed: bool
    native_witness: dict | None
    state: str = 'TERMINAL'

    def journal_record(self, action: str) -> dict:
        require(self.state == 'TERMINAL', 21, 'ACTION_NOT_TERMINAL')
        require(self.no_pending_writer is True, 21, 'NATIVE_STATE_UNCERTAIN')
        require(self.postconditions_observed is True, 19, 'POSTCONDITIONS_FAILED')
        require(type(self.material_after) is dict and type(self.raw_evidence) is dict
                and bool(self.raw_evidence), 19, 'COMPLETION_EVIDENCE_MISSING')
        return {
            'action': action, 'no_pending_writer': True,
            'terminal_observed': True, 'postconditions_observed': True,
            'evidence_digest': digest(self.raw_evidence),
            'native_witness': deepcopy(self.native_witness),
            'material_after': deepcopy(self.material_after),
            'observations': deepcopy(self.raw_evidence),
        }


class Driver(Protocol):
    source_kind: str
    def refresh(self, plan: dict, *, coordinator=None, step: int | None = None) -> Refresh: ...
    def preconditions(self, plan: dict, step: int, fresh: Refresh, coordinator) -> None: ...
    def witness(self, plan: dict, step: int, fresh: Refresh) -> dict: ...
    def run(self, plan: dict, step: int, fresh: Refresh, coordinator) -> dict: ...
    def observe(self, plan: dict, step: int, result: dict, fresh: Refresh, coordinator) -> Completion: ...
    def reconcile(self, original: dict, step: int, fresh: Refresh, coordinator) -> Completion: ...
    def final_assertions(self, plan: dict, fresh: Refresh, coordinator, completed: dict) -> dict: ...


class SessionRunner:
    """One guard, no nested acquire, fresh authorization before each native step.

    Precondition errors before INTENT are ordinary blockers. Errors after INTENT
    retain the exact fence; no retry, blind CLEAR, or phase-gate inference.
    Reconciliation is a separate read-only call. Resume requires newly valid
    authority and only skips journal-committed steps after live revalidation.
    """
    def __init__(self, driver: Driver, coordinator):
        self.driver = driver
        self.coordinator = coordinator
        self._generation = None

    def _fresh(self, interface, plan, *, step=None, held=False):
        fresh = self.driver.refresh(plan, coordinator=self.coordinator if held else None,
                                    step=step)
        require(type(fresh) is Refresh, 18, 'REFRESH_ADAPTER_TYPE')
        require(type(fresh.generation) is int and fresh.generation >= 1,
                15, 'AUTHORITY_GENERATION')
        require(self._generation is None or fresh.generation >= self._generation,
                15, 'AUTHORITY_ROLLBACK')
        self._generation = fresh.generation
        auth = authorize(interface, plan, fresh.context, fresh.store)
        if held:
            require(fresh.collection_kind in ('WINDOWS_NATIVE_METADATA','WORKSPACE_TEST'),
                    11, 'ADMITTED_OBSERVATION_REQUIRED')
            if self.driver.source_kind != 'WORKSPACE_TEST':
                require(fresh.collection_kind == 'WINDOWS_NATIVE_METADATA',
                        12, 'NATIVE_OBSERVATION_REQUIRED')
            old = self.coordinator.admission
            require((auth.plan_digest, auth.run_id, auth.host_id, auth.owner_sid, auth.classes)
                    == (old.plan_digest, old.run_id, old.host_id, old.owner_sid, old.classes),
                    12, 'SESSION_AUTHORITY_DRIFT')
            self.coordinator.admission = auth
        return fresh, auth

    def execute(self, interface: str, plan: dict) -> dict:
        semantic = interface_check(interface, plan)
        fresh, auth = self._fresh(interface, plan)
        c = self.coordinator
        with c.acquire(auth):
            progress = completed_steps(c.storage.read_events(), plan)
            already_complete = len(progress) == len(semantic['operations'])
            current = (progress[len(progress)-1]['material_after'] if progress else semantic['before'])
            fresh, _ = self._fresh(interface, plan, held=True)
            drift(current, fresh.observed['material'])
            floors(fresh.observed['resources'])
            budget_check(fresh.observed.get('remaining_budgets',semantic['budgets']), fresh.observed['free_bytes'])
            if already_complete and hasattr(self.driver,'revalidate_committed'):
                return self._live_noop(interface,plan,fresh,progress)
            for index in range(len(progress), len(semantic['operations'])):
                fresh, _ = self._fresh(interface, plan, step=index, held=True)
                drift(current, fresh.observed['material'])
                floors(fresh.observed['resources'])
                reservation = budget_check(fresh.observed.get('remaining_budgets',semantic['budgets']), fresh.observed['free_bytes'])
                self.driver.preconditions(plan, index, fresh, c)
                c.intent(semantic['operations'][index]['action'], reservation,
                         self.driver.witness(plan, index, fresh))
                try:
                    result = self.driver.run(plan, index, fresh, c)
                    require(type(result) is dict, 18, 'ACTION_RESULT_SCHEMA')
                    if result.get('state') in ('AWAITING_REBOOT', 'AWAITING_USER_INIT',
                                                'AWAITING_OWNER_VERIFICATION'):
                        from .native.lifecycle import wait_observation
                        wait=wait_observation(semantic['operations'][index]['action'],result,c.fence['state'])
                        c.awaiting(result['state'],wait)
                        return self._report(plan, 20, result['state'], progress)
                    completion = self.driver.observe(plan, index, result, fresh, c)
                    require(type(completion) is Completion, 19, 'COMPLETION_ADAPTER_TYPE')
                    terminal = completion.journal_record(semantic['operations'][index]['action'])
                    require(terminal['native_witness'] == c.fence['native'], 19, 'NATIVE_WITNESS_MISMATCH')
                    c.terminal(terminal)
                    current = terminal['material_after']
                    progress[index] = terminal
                except BaseException as error:
                    if c.fence is not None:
                        if c.fence['state'] != 'TERMINAL':
                            try:
                                c.uncertain(error.reason if isinstance(error, P00Error) else 'CONTROLLER_INTERRUPTED')
                            except BaseException:
                                pass
                        if hasattr(self.driver,'record_failure'):
                            try:self.driver.record_failure(plan,error,c)
                            except BaseException: pass
                    raise
            final, _ = self._fresh(interface, plan, held=True)
            drift(current, final.observed['material'])
            floors(final.observed['resources'])
            budget_check(final.observed.get('remaining_budgets',semantic['budgets']), final.observed['free_bytes'])
            final_assertions = self.driver.final_assertions(plan, final, c, progress)
            require(type(final_assertions) is dict and bool(final_assertions), 19, 'FINAL_ASSERTIONS_MISSING')
            c.storage.append_event({'kind': 'SESSION_OBSERVED', 'run_id': semantic['run_id'],
                                    'plan_digest': plan['plan_digest'],
                                    'assertions': final_assertions,
                                    'assertions_digest': digest(final_assertions)})
            code=0;state='NOOP' if already_complete else ('VERIFIED' if interface=='verify' else 'APPLIED')
            outcome=final_assertions.get('interface_outcome',{})
            if outcome:
                allowed={0:'COMPLETE',2:'PARTIAL_OPTIONAL',15:'FAILED_INTEGRITY',
                         18:'FAILED_OUTPUT',22:'INCOMPLETE_MANDATORY',23:'BLOCKED_REDACTION'}
                require(interface=='support-bundle' and type(outcome) is dict
                        and set(outcome)=={'exit','state'} and type(outcome['exit']) is int
                        and outcome['exit'] in allowed and outcome['state']==allowed[outcome['exit']],
                        19,'INTERFACE_OUTCOME_INVALID')
                code=outcome['exit'];state=outcome['state']
            return self._report(plan,code,state,progress,final_assertions)

    def _live_noop(self,interface,plan,fresh,progress):
        c=self.coordinator
        index=len(plan['semantic']['operations'])-1
        self.driver.pre_noop(plan,fresh,c,progress)
        witness=self.driver.witness(plan,index,fresh)
        witness={**witness,'execution_phase':'LIVE_REVALIDATION', 'original_progress_digest':progress_digest(progress)}
        reservation=budget_check(fresh.observed.get('remaining_budgets',plan['semantic']['budgets']), fresh.observed['free_bytes'])
        c.intent(plan['semantic']['operations'][index]['action'],reservation,witness)
        try:
            completion=self.driver.revalidate_committed(plan,fresh,c,progress)
            require(type(completion) is Completion,19,'COMPLETION_ADAPTER_TYPE')
            observed=completion.raw_evidence
            require(observed.get('kind')=='NATIVE_LIVE_REVALIDATION'
                    and observed.get('baseline_digest')==progress_digest(progress),15,'NOOP_BASELINE_MISMATCH')
            assertions=observed.get('assertions')
            require(type(assertions) is dict and bool(assertions),19,'FINAL_ASSERTIONS_MISSING')
            renewed,auth=self._fresh(interface,plan)
            require(auth==c.admission,12,'SESSION_AUTHORITY_DRIFT')
            outcome=assertions.get('interface_outcome',{})
            code=0;state='NOOP'
            if outcome:
                allowed={0:'COMPLETE',2:'PARTIAL_OPTIONAL',15:'FAILED_INTEGRITY',18:'FAILED_OUTPUT',22:'INCOMPLETE_MANDATORY',23:'BLOCKED_REDACTION'}
                require(interface=='support-bundle' and type(outcome.get('exit')) is int
                        and outcome['exit'] in allowed and outcome.get('state')==allowed[outcome['exit']],
                        19,'INTERFACE_OUTCOME_INVALID')
                code=outcome['exit'];state=outcome['state']
            c.terminal(completion.journal_record(c.fence['action']))
            c.storage.append_event({'kind':'SESSION_OBSERVED','run_id':plan['semantic']['run_id'],
                'plan_digest':plan['plan_digest'],'revalidation':True,
                'assertions':assertions,'assertions_digest':digest(assertions)})
            return self._report(plan,code,state,progress,assertions)
        except BaseException as error:
            if c.fence is not None and c.fence['state']!='TERMINAL':
                try:c.uncertain(error.reason if isinstance(error,P00Error) else 'CONTROLLER_INTERRUPTED')
                except BaseException:pass
            raise

    def reconcile(self, request: dict) -> dict:
        from .recovery import RecoveryRunner
        return RecoveryRunner(self).execute(request)

    def _report(self, plan, code, state, progress, assertions=None):
        return {'exit': code, 'state': state, 'plan_digest': plan['plan_digest'],
                'completed_steps': sorted(progress), 'source_kind': self.driver.source_kind,
                'assertions_digest': digest(assertions) if assertions is not None else None,
                'host_ready': False, 'qualification_issued': False}
