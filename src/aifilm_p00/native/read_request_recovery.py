"""Native C0 read recovery without launching another child process.

Missing PID/start witness requires independently measured, scoped absence proof;
intent, current inventory, return code and clock age are never sufficient.
"""
from copy import deepcopy
from ..codec import digest
from ..errors import P00Error, require
from ..session import Refresh
from ..read_recovery import ReadObservation
from .observations import volume_observations


def refresh(d, request, c):
    require(c.held and c.fence is None and c.admission.purpose == 'RECONCILIATION_ONLY',
            12, 'READ_RECOVERY_ADMISSION')
    ctx, passive, _ = d._authority_snapshot(request)
    volumes = volume_observations(d.paths, d.binding['volume_paths'], request['semantic']['budgets'])
    result = Refresh(ctx, d.store, {'free_bytes':{k:v['free_bytes'] for k,v in volumes.items()},
                    'volumes':volumes, 'principal':passive['principal']},
                    d.store.generation, 'WINDOWS_NATIVE_METADATA')
    return result


def reserve(d, request, fresh, c, count):
    # The declared output budget is checked before recovery diagnostics. This
    # reservation is not unlimited use of emergency journal headroom.
    limit = d.binding.get('journal_maximum_additional_bytes')
    require(type(limit) is int and limit >= count*512*1024, 13, 'READ_RECOVERY_BUDGET')
    c.storage.reserve_capacity(limit, recovery=True)
    vid = d.paths.volume(d.paths.root)['volume_id']
    budgets = [v for v in request['semantic']['budgets'] if v['volume_id']==vid]
    require(len(budgets)==1 and sum(budgets[0]['allocations'].values()) >= limit,
            13, 'JOURNAL_ALLOCATION_MISSING')


def observe(d, entry, fresh, diagnostic):
    try:
        if entry.get('witness') is not None:
            actual = d.system.writer(entry['witness'])
            return ReadObservation({'writer':actual, 'read_id':entry['read_id'],
                'observed_at':fresh.context.now.isoformat()}, True, digest(entry['witness']))
        require(entry.get('command_digest') is not None and entry.get('origin') is not None,
                21, 'READ_PROBE_WITNESS_MISSING')
        scope = {'host_id':entry['origin']['host_id'], 'original_plan_digest':entry['plan_digest'],
                 'read_id':entry['read_id'], 'intent_digest':digest(entry),
                 'command_digest':entry['command_digest']}
        proof = d._reader(fresh).selected('read_absence_observation',scope,not_before=None)
        claim = proof['claim']
        require(claim.get('matching_processes') == [] and claim.get('matching_jobs') == []
                and claim.get('scan_complete') is True and claim.get('controller_terminal') is True
                and claim.get('service_writes_possible') is False, 21, 'READ_ABSENCE_NOT_PROVEN')
        # Measurements must not predate the read intent. ProofReader already
        # checked raw/collector/owner chain and excludes OWNER_ASSERTION here.
        from ..codec import instant
        require(all(instant(m['timestamp_utc']) >= instant(entry['issued_at'])
                    for m in proof['measurements']), 16, 'READ_ABSENCE_PRECEDES_INTENT')
        return ReadObservation({'absence_observation':proof, 'read_id':entry['read_id']}, True, None, proof['ref'])
    except P00Error as error:
        if not diagnostic or error.code in (12,15,16,23): raise
        return ReadObservation({'read_id':entry['read_id'], 'status':'UNKNOWN',
                                'exit':int(error.code), 'reason':error.reason}, False, None)


def run_revocation(d, original, request, fresh, disposition):
    scope = {'host_id':original['semantic']['host_id'],
             'original_plan_digest':original['plan_digest'],
             'recovery_request_digest':request['plan_digest'], 'disposition':disposition}
    proof = d._reader(fresh).selected('run_revocation',scope,owner_assertion=True)
    claim = proof['claim']
    require(claim.get('revoked_plan_digest')==original['plan_digest']
            and claim.get('revoked_run_id')==original['semantic']['run_id']
            and claim.get('pending_operations')==[]
            and claim.get('servicing_queue_empty') is True,21,'REVOCATION_NOT_PROVEN')
    return proof
