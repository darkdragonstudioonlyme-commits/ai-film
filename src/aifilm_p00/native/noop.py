"""Live postcondition revalidation of a fully committed original plan.

No installer/export/import/workspace creation, restart, terminate, or publication
is replayed. Authorized guest reads get their own durable revalidation fence.
Stopped clones are checked by current protected VHD bytes, without booting them.
"""
from copy import deepcopy
from pathlib import PureWindowsPath

from ..authority import authorize
from ..codec import digest, instant
from ..errors import require
from ..policy import floors, budget_check
from ..evidence import bundle_integrity
from ..session import Completion
from ..resume import progress_digest
from .transitions import final_expected

GUEST_PURPOSES = frozenset({'CREATE','ADOPT','DISCOVERY','TARGET_LIFECYCLE','HOST_RESTART','SITE_VERIFY'})


def committed_baseline(plan, completed):
    s = plan['semantic']
    require(sorted(completed) == list(range(len(s['operations']))), 19, 'SESSION_STEPS_INCOMPLETE')
    for index, row in completed.items():
        require(row.get('action') == s['operations'][index]['action']
                and row.get('postconditions_observed') is True
                and row.get('no_pending_writer') is True
                and row.get('evidence_digest') == digest(row.get('observations')), 15, 'NOOP_COMMIT_INTEGRITY')
    return completed[len(s['operations']) - 1]


def preconditions(d, plan, fresh, c, completed):
    baseline = committed_baseline(plan, completed)
    require(c.held and c.fence is None, 12, 'NOOP_ADMISSION_REQUIRED')
    require(fresh.observed['material'] == baseline['material_after'], 16, 'NOOP_MATERIAL_DRIFT')
    final_expected(d.binding, plan, fresh.observed['material'])
    s = plan['semantic']; running = fresh.observed['running']
    if s['target']['name'] is not None:
        require(fresh.observed['target'] is not None, 19, 'TARGET_NOT_PRESENT')
    if s['purpose'] in GUEST_PURPOSES:
        require(s['final_state'] == 'RUNNING' and running is not None
                and s['target']['name'] in running, 19, 'NOOP_GUEST_NOT_RUNNING')
    if s['purpose'] in ('RESTORE_IMPORT','RESTORE_EXPORT','RESTORE_VERIFY'):
        require(running is not None and s['target']['name'] not in running,
                19, 'NOOP_TARGET_NOT_STOPPED')
    # Reruns still need a bounded metadata/snapshot reservation. Consumed distro
    # allocations are not re-applied. Missing output allocation is an ordinary
    # precondition blocker, before a new fence is created.
    from .bindings import verify_volume_coverage
    verify_volume_coverage(d.paths,d.api.system_directory(),d.binding,s,
                          fresh.observed['remaining_budgets'],pending_snapshots=1)


def _same_vhd(d, row, recorded):
    require(isinstance(recorded,dict) and type(recorded.get('sha256')) is str,
            15, 'COMMITTED_VHD_DIGEST_MISSING')
    actual = d._vhd_closed(row)
    require(actual['sha256'] == recorded['sha256']
            and actual['file_identity'] == recorded['file_identity']
            and actual['volume_id'] == recorded['volume_id'], 19, 'NOOP_VHD_CHANGED')
    return actual


def _bundle(d, plan, baseline):
    recorded = baseline['observations']['details']['bundle']
    codes = {0:'COMPLETE',2:'PARTIAL_OPTIONAL',15:'FAILED_INTEGRITY',18:'FAILED_OUTPUT',
             22:'INCOMPLETE_MANDATORY',23:'BLOCKED_REDACTION'}
    require(type(recorded.get('exit')) is int and recorded['exit'] in codes
            and recorded.get('outcome') == codes[recorded['exit']], 15, 'BUNDLE_OUTCOME_REQUIRED')
    observed = {'interface_outcome': {'exit':recorded['exit'],'state':recorded['outcome']},
                'published': recorded.get('published') is True}
    if recorded.get('published'):
        path = d.binding['incomplete_bundle_output'] if recorded['exit']==22 else d.binding['bundle_output']
        raw = d.paths.read_blob(path, expected=recorded['bundle_digest'], cap=150*1024**2)
        require(bundle_integrity(raw)['sha256'] == recorded['bundle_digest'], 15, 'NOOP_BUNDLE_CHANGED')
        observed['bundle_digest'] = recorded['bundle_digest']
        if recorded.get('assessment'):
            expected = recorded['assessment']['assessment_digest']
            raw = d.paths.read_blob(d.binding['assessment_output'], expected=expected)
            observed['assessment_digest'] = expected
    else:
        # Nothing is republished. The original non-success remains non-success;
        # a log record alone cannot certify that an output exists.
        require(recorded['exit'] in (15,18,23), 19, 'BUNDLE_PUBLICATION_NOT_COMMITTED')
    return observed


def revalidate(d, plan, fresh, c, completed):
    s = plan['semantic']; purpose = s['purpose']
    baseline = committed_baseline(plan,completed)
    require(c.fence is not None and c.fence['witness'].get('execution_phase')=='LIVE_REVALIDATION',
            12, 'NOOP_FENCE_REQUIRED')
    row = fresh.observed['target']; details = {}; result = None
    if purpose in GUEST_PURPOSES:
        source = d._source(plan,fresh); d.proofs['source'] = source
        if purpose == 'SITE_VERIFY':
            # A new sweep measures current behavior; it does not replay lifecycle
            # or turn the earlier sweep into a current gate assertion.
            from .terminal_sweep import NativeTerminalSweep
            result = NativeTerminalSweep(d).run(plan,c,fresh)
            details['terminal'] = result['terminal']
        else:
            guest = d._eligible_guest(plan,c,source)
            details['guest'] = guest
            result = {'state':'OBSERVED','guest':guest}
            if purpose != 'DISCOVERY':
                require(bool(d.binding.get('critical_files') or source['claim'].get('critical_files')),
                        15,'NOOP_CRITICAL_FILES_MISSING')
                content = d._guest(plan,'ASSERT_CONTENT',c,
                                  {'critical_files':(d.binding.get('critical_files') or source['claim'].get('critical_files',[]))})['capture']
                details['content'] = content
            if purpose == 'HOST_RESTART':
                details['affected_resources'] = d._post_c3(plan,fresh,c)
    elif purpose == 'ENGINE':
        details['servicing'] = {action:d.system.installer_idle(action)
                               for action in ('ENABLE_PREREQUISITES','INSTALL_RUNTIME')}
        require(not any(d.system.pending_reboot().values()),20,'REBOOT_STILL_PENDING')
        details['affected_resources'] = d._post_c3(plan,fresh,c)
    elif purpose in ('RESTORE_IMPORT','RESTORE_VERIFY'):
        details['vhd'] = _same_vhd(d,row,baseline['observations']['details']['vhd'])
    elif purpose == 'RESTORE_EXPORT':
        recorded = baseline['observations']['details']
        details['vhd'] = _same_vhd(d,row,recorded['source_vhd'])
        actual = d._checkpoint(d.binding['export_path'])
        require(actual['sha256']==recorded['checkpoint']['sha256']
                and actual['bytes']==recorded['checkpoint']['bytes'],19,'NOOP_CHECKPOINT_CHANGED')
        details['checkpoint'] = actual
    elif purpose == 'SUPPORT_BUNDLE':
        details['bundle'] = _bundle(d,plan,baseline)
    else:
        require(purpose=='PASSIVE',10,'NOOP_PURPOSE_NOT_ALLOWED')
        details['metadata'] = deepcopy(fresh.observed)
    # Recheck after all probes. Identity/profile/authority drift during a read
    # cannot be masked by the original committed baseline.
    current = d.refresh(plan,coordinator=c)
    from .session_driver import interface_for
    authorize(interface_for(plan),plan,current.context,current.store)
    require(current.observed['material']==fresh.observed['material'],16,'NOOP_MATERIAL_DRIFT')
    final_expected(d.binding,plan,current.observed['material'])
    floors(current.observed['resources'])
    budget_check(current.observed['remaining_budgets'],current.observed['free_bytes'])
    if purpose in GUEST_PURPOSES:
        require(s['target']['name'] in current.observed['running'],19,'FINAL_TARGET_NOT_RUNNING')
    elif purpose in ('RESTORE_IMPORT','RESTORE_EXPORT','RESTORE_VERIFY'):
        require(s['target']['name'] not in current.observed['running'],19,'FINAL_TARGET_NOT_STOPPED')
    writers = d.system.all_writers(c.fence['native'])
    assertions = {'material_digest':digest(current.observed['material']),
        'completed_step_digests':{str(k):v['evidence_digest'] for k,v in completed.items()},
        'final_running':current.observed['running'],'timestamp_utc':current.context.now.isoformat(),
        'source_kind':d.source_kind, 'host_ready':False,
        'interface_outcome':details.get('bundle',{}).get('interface_outcome',{})}
    evidence = {'kind':'NATIVE_LIVE_REVALIDATION','plan_digest':plan['plan_digest'],
        'source_kind':d.source_kind,'timestamp_utc':current.context.now.isoformat(),
        'baseline_digest':progress_digest(completed),'details':details,'writers':writers,'assertions':assertions}
    # New evidence has its own immutable snapshot, not an overwrite of the old
    # sweep or a regeneration of the original output artifact.
    from .evidence_pipeline import NativeEvidencePipeline
    snapshot = NativeEvidencePipeline(d).capture(plan,c,current,result)
    evidence['snapshot'] = {'index_digest':snapshot['index_digest'],'record_count':snapshot['record_count']}
    return Completion(deepcopy(current.observed['material']),evidence,True,True,deepcopy(c.fence['native']))


def reconcile(d, original, fresh, c):
    """Read-only recovery of interrupted revalidation, never a guest relaunch."""
    from ..resume import completed_steps
    completed=completed_steps(c.storage.read_events(),original)
    committed_baseline(original,completed)
    baseline=progress_digest(completed)
    require(c.fence['witness'].get('original_progress_digest')==baseline,15,'NOOP_BASELINE_MISMATCH')
    require(fresh.observed['material']==completed[max(completed)]['material_after'],16,'NOOP_MATERIAL_DRIFT')
    writers=d.system.all_writers(c.fence['native'])
    row=fresh.observed['target'];host=fresh.observed['host']
    require(host is not None,11,'RECONCILIATION_FACTS_INCOMPLETE')
    scope={'host_id':original['semantic']['host_id'],'plan_digest':original['plan_digest'],
           'execution_phase':'LIVE_REVALIDATION','baseline_digest':baseline,
           'host_boot':host['boot_utc'],
           'target_registration':row['registration_id'] if row else None}
    receipt=d._reader(fresh).selected('operation_postcheck',scope,
                                    not_before=instant(c.fence['witness']['captured_at']))
    claim=receipt['claim']
    require(claim.get('material_digest')==digest(fresh.observed['material'])
            and claim.get('postconditions_observed') is True
            and isinstance(claim.get('assertions'),dict) and bool(claim['assertions']),19,'NOOP_POSTCHECK_INCOMPLETE')
    evidence={'kind':'NATIVE_LIVE_REVALIDATION','baseline_digest':baseline,
              'plan_digest':original['plan_digest'],'assertions':deepcopy(claim['assertions']),
              'postcheck':receipt,'writers':writers,'source_kind':d.source_kind,
              'timestamp_utc':fresh.context.now.isoformat()}
    return Completion(deepcopy(fresh.observed['material']),evidence,True,True,deepcopy(c.fence['native']))
