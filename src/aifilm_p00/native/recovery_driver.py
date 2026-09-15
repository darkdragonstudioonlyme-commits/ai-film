"""Concrete C0 recovery observations on the original fence.

Recovery can diagnose unsupported/broken/low-resource hosts without installing
anything to make them eligible. It still enforces principal, trusted code,
physical output scope and budgets before persistent diagnostics. Queue revocation
is authenticated separately from both caller intent and measured writer state.
"""
from copy import deepcopy
from datetime import datetime, timezone

from ..codec import digest
from ..errors import P00Error, require
from ..plans import check_plan
from ..policy import budget_check
from ..recovery import PauseObservation
from ..session import Refresh
from .observations import (ReadBroker, normalize_host, normalize_distros,
                           target_row, config_observation, volume_observations, match_profile)


def refresh_recovery(d, plan, ctx, passive, catalog, c):
    require(c.held and c.admission.purpose in ('RECONCILIATION_ONLY','PASSIVE'), 12, 'RECONCILIATION_SCOPE')
    s = check_plan(plan)
    d._reserve_journal(plan,c)
    d.environment = d._environment(d.binding)
    if d.broker is None or d.broker.c is not c:
        d.broker = ReadBroker(d.root, d.api, d.paths, d.supervisor, d.environment, c, d.source_pins)
    else:
        d.broker.environment = d.environment
        d.broker.sources = d.source_pins
    volumes = volume_observations(d.paths, d.binding['volume_paths'], s['budgets'])
    free = {k: v['free_bytes'] for k, v in volumes.items()}
    budget_check(s['budgets'], free)
    from .bindings import verify_volume_coverage
    coverage = verify_volume_coverage(d.paths, d.api.system_directory(), d.binding, s,
                                     s['budgets'], pending_snapshots=0)
    capture_start=len(d.broker.captures)
    errors = {}
    def get(key, function):
        try:
            return function()
        except P00Error as error:
            # Integrity/access/scope failures are not ordinary missing facts.
            if error.code in (12, 15, 16, 23):
                raise
            errors[key] = {'exit': int(error.code), 'reason': error.reason}
            return None
    live = get('host', lambda: d.broker.host('HOST'))
    host = get('host_profile', lambda: normalize_host(passive, live, catalog)) if live else None
    packaged = get('packaging', lambda: d._packaged(live, catalog)) if live else None
    if packaged:
        runtime = get('runtime', lambda: d.broker.runtime(packaged))
    elif live is not None and 'packaging' not in errors:
        runtime = {'status':'PACKAGED_ABSENT','version':None,'kernel':None,'package_identity':None}
    else:
        runtime = None
    running = get('running', d.broker.running) if packaged and runtime else None
    features = get('features', lambda: d.broker.host('FEATURES'))
    config = get('wslconfig', lambda: config_observation(d.paths, d.system.user_profile()+'\\.wslconfig'))
    distros = get('distros', lambda: normalize_distros(passive['distros']))
    material = None
    target = None
    profile_verified = False
    if host and features and config and distros is not None and runtime is not None:
        material = {'schema_version': 1,
                    'host': {k: host[k] for k in ('host_id','build','ubr','edition','release','architecture')},
                    'execution_sid': passive['principal']['execution_sid'], 'runtime': runtime,
                    'features': sorted([{'name':row['name'],'state':row['state']} for row in features['features']], key=lambda row: row['name']),
                    'distros': distros, 'wslconfig': config}
        target = target_row(material, s['target'])
        actual_profile = get('profile_match', lambda: match_profile(catalog,
            {'host': material['host'], 'runtime': runtime, 'config_digest': digest(config)}))
        profile_verified = actual_profile == ctx.profile
    elif distros is not None:
        target = target_row({'distros': distros}, s['target'])
    observed = {'material': material, 'resources': deepcopy(passive['resources']),
        'free_bytes': free, 'remaining_budgets': deepcopy(s['budgets']), 'volumes': volumes,
        'host': host, 'principal': passive['principal'], 'packaging': packaged, 'running': running,
        'target': target, 'physical_write_coverage': coverage, 'profile_verified': profile_verified,
        'collection_errors': errors, 'collection_kind': 'WINDOWS_NATIVE_METADATA',
        'read_captures':deepcopy(d.broker.captures[capture_start:]),
        'timestamp_utc': datetime.now(timezone.utc).isoformat()}
    d.last = Refresh(ctx, d.store, observed, d.store.generation, 'WINDOWS_NATIVE_METADATA')
    return d.last


def diagnose(d, original, step, fresh, c):
    errors = {}
    def read(name, action):
        try:
            return action()
        except P00Error as error:
            # Denial is recorded as unavailable, never interpreted as quiescence.
            errors[name] = {'exit': int(error.code), 'reason': error.reason}
            return None
    writers = read('writers', lambda: d.system.all_writers(c.fence['native']))
    services = {name: read(name, lambda name=name: d.system.service(name))
                for name in ('WslService','LxssManager','msiserver','TrustedInstaller')}
    pending = read('reboot', d.system.pending_reboot)
    return {'kind': 'ORIGINAL_FENCE_DIAGNOSTIC', 'source_kind': d.source_kind,
        'original_plan_digest': original['plan_digest'], 'fence_digest': digest(c.fence),
        'step': step, 'metadata': deepcopy(fresh.observed), 'writers': writers,
        'services': services, 'pending_reboot': pending, 'errors': errors,
        'host_ready': False, 'postconditions_observed': False}


def pause_observation(d, original, step, fresh, c, *, request, disposition):
    require(disposition in ('PAUSE','CANCEL'), 10, 'PAUSE_DISPOSITION')
    # All native children must be measured terminal; a process exit code and
    # owner intention are not substitutes for process/job/service-level proof.
    writers = d.system.all_writers(c.fence['native'])
    from .read_recovery import reconcile_detached_reads
    reads = reconcile_detached_reads(d.system, c)
    action = c.fence['action']
    servicing = None
    if action in ('ENABLE_PREREQUISITES','INSTALL_RUNTIME'):
        servicing = d.system.installer_idle(action)
    pending = d.system.pending_reboot()
    require(not any(pending.values()), 20, 'REBOOT_STILL_PENDING')
    scope = {'host_id': original['semantic']['host_id'],
        'original_plan_digest': original['plan_digest'], 'original_fence_digest': digest(c.fence),
        'recovery_request_digest': request['plan_digest'], 'disposition': disposition}
    # This consumes an externally-authorized measured record, never emits one.
    # The actual claim graph is verified by ProofReader (measurement/raw/owner).
    receipt = d._reader(fresh).selected('run_revocation', scope, owner_assertion=True)
    claim = receipt['claim']
    require(claim.get('revoked_plan_digest') == original['plan_digest']
            and claim.get('revoked_run_id') == original['semantic']['run_id']
            and claim.get('pending_operations') == []
            and claim.get('servicing_queue_empty') is True,
            21, 'REVOCATION_NOT_PROVEN')
    if c.fence['state'] == 'AWAITING_REBOOT':
        require(claim.get('restart_request_withdrawn') is True, 21, 'RESTART_REQUEST_NOT_REVOKED')
    proof = {'kind': 'OBSERVED_SAFE_PAUSE', 'source_kind': d.source_kind,
        'writers': writers, 'detached_reads': reads, 'servicing': servicing,
        'pending_reboot': pending, 'revocation': receipt,
        'timestamp_utc': fresh.context.now.isoformat(), 'original_step': step,
        'metadata': deepcopy(fresh.observed), 'mutation_replayed': False}
    return PauseObservation(proof, True, True, receipt['ref'], deepcopy(c.fence['native']))
