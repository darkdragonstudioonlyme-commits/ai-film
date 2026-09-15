"""Detached metadata probes survive crashes independently of the mutation fence."""
from ..codec import digest
from ..errors import require


def pending_reads(rows):
    pending = {}; seen = set()
    for row in rows:
        event = row.get('event', {})
        kind = event.get('kind')
        if kind not in ('READ_PROBE_INTENT','READ_PROBE_STARTED','READ_PROBE_RESULT',
                        'READ_PROBE_UNRESOLVED','READ_PROBE_RECONCILED','READ_PROBE_RECOVERY_COMMITTED'):
            continue
        key = event.get('read_id')
        require(type(key) is str and bool(key), 15, 'READ_PROBE_ID')
        if kind == 'READ_PROBE_INTENT':
            # Dev3 counters could repeat; an ambiguous journal cannot prove
            # which process ended. Do not silently accept the most recent row.
            require(key not in seen, 15, 'READ_PROBE_ID_REUSED')
            seen.add(key); pending[key] = dict(event)
        elif kind == 'READ_PROBE_STARTED':
            require(key in pending and 'witness' not in pending[key], 15, 'READ_PROBE_ORPHAN')
            pending[key]['witness'] = event.get('witness')
        elif kind == 'READ_PROBE_UNRESOLVED':
            require(key in pending, 15, 'READ_PROBE_ORPHAN')
        elif kind == 'READ_PROBE_RECOVERY_COMMITTED':
            require(key in pending, 15, 'READ_PROBE_ORPHAN')
            from ..read_recovery import check_read_release
            check_read_release(pending[key], event)
            del pending[key]
        else:
            require(key in pending and isinstance(pending[key].get('witness'),dict),
                    15, 'READ_PROBE_ORPHAN')
            witness = pending[key]['witness']
            if kind == 'READ_PROBE_RESULT':
                require(event.get('native_witness') == witness and event.get('tree_terminal') is True,
                        21, 'READ_PROBE_NOT_TERMINAL')
            else:
                require(event.get('witness_digest') == digest(witness)
                        and event.get('writer_observed_terminal') is True,
                        21, 'READ_PROBE_NOT_TERMINAL')
            del pending[key]
    return pending


def reconcile_detached_reads(system, coordinator):
    require(coordinator.held and coordinator.admission.purpose == 'RECONCILIATION_ONLY',
            12, 'RECONCILIATION_SCOPE')
    observed = []
    for key, entry in pending_reads(coordinator.storage.read_events()).items():
        require(isinstance(entry.get('witness'),dict), 21, 'READ_PROBE_WITNESS_MISSING')
        actual = system.writer(entry['witness'])
        coordinator.storage.append_event({'kind': 'READ_PROBE_RECONCILED','read_id':key,
            'witness_digest': digest(entry['witness']), 'writer_observed_terminal':True,
            'observations':actual})
        observed.append({'read_id':key,'observations':actual})
    return observed
