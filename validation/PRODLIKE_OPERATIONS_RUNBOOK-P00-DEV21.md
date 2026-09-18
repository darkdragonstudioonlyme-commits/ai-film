# Phase00 dev21 — Production-Like Operations Runbook

## Scope and invariant

This runbook operates only the non-native production-like control plane for exact dev21. Native workflow remains `RUN-P00-VALIDATION-001 / V02_LAB_EXECUTION_AUTHORITY`. No action may infer approval, create protected authority, write HKLM trust, start LAB for native execution, run native acceptance, issue qualification or claim HOST_READY.

## Healthy baseline

Primary status command:

```bash
/home/dragon/ai-film-runtime/bin/aifilm-prodlike-status.py
```

Expected healthy classification is `READY_NON_NATIVE_PRODLIKE_OPERATIONS` together with `BLOCKED_EXTERNAL_AUTHORITY` while authority is absent.

Core checks:

```bash
/home/dragon/ai-film-runtime/bin/verify-current
/home/dragon/ai-film-runtime/bin/verify-control-backup.py
/home/dragon/ai-film-runtime/bin/verify-host-mirror.py
/home/dragon/ai-film-runtime/bin/verify-rebuild-set.py --cold-probe
/home/dragon/ai-film-runtime/bin/verify-offhost-export.py --drill
/home/dragon/ai-film-runtime/bin/verify-operational-evidence.py
/home/dragon/ai-film-runtime/bin/verify-recovery-state
/home/dragon/ai-film-runtime/bin/runtime-health.py
```

## Supervision, freshness and resources

Eleven user-systemd timers must remain enabled/active/Persistent: integrity 15m, V02 watcher 5m, health 10m, backup 24h, recovery boot+6h, mirror 2h, rebuild boot+12h, transfer export boot+6h, full DR 24h, fail-closed campaign 7d, evidence ledger 24h.

Timer state alone is insufficient. Health also checks each service's last completed execution from `ExecMainExitTimestampMonotonic`. Maximum age is the configured cadence plus bounded accuracy/grace. A service with no completion in the current boot is allowed only through `OnBootSec + AccuracySec + startup grace`; after that it is unhealthy even if its timer is active.

All 11 AI-FILM oneshot services use accounting plus `MemoryMax=256M` and `TasksMax=128`. Kernel-cgroup binding was independently confirmed using a benign transient probe; destructive OOM/fork-exhaustion testing is not required.

## Retention and evidence history

Control backup retention is 14. Evidence-ledger retention is 30. Both policies have been overflow-tested against disposable destinations using the actual producer code.

Ledger prune preserves tamper-evident continuity: `anchor_before_oldest_sha256` must equal the predecessor hash expected by the oldest retained record. Historical FAIL records are valid evidence; health requires chain integrity/freshness rather than all-history-PASS.

## Recovery migration order

When control/recovery schema changes, producers must be regenerated before a stricter consumer may be declared healthy:

1. verify live runtime/health inputs;
2. create and verify a new control backup;
3. mirror the verified backup to NTFS;
4. rebuild deterministic transfer export from new backup + exact rebuild set;
5. run export heavy drill;
6. run full DR rehearsal against the new export;
7. run fail-closed campaign;
8. run evidence-ledger snapshot;
9. run health last and require PASS.

Do not weaken the DR consumer to accept old state. The 44→58, 58→85 and subsequent ledger-history recovery refreshes all follow producer-before-consumer ordering.

## Stable identity vs rotating recovery state

Exact source/package/wheel/app/runtime/rebuild identities are stable. Control backup bytes, embedded ledger-history file count and deterministic-export SHA are **rotating operational samples** because bounded history advances over time.

A current sample may be logged for traceability, but it must not be treated as an immutable release identity. Health/recovery truth is based on verifier PASS, freshness/retention bounds, required timer/resource schema, ledger-chain validity and exact reviewed dev21 reconstruction.

Private Google Drive therefore pins only stable exact-candidate/rebuild identities. Rotating backup/export hashes are deliberately not pinned there.

## User-systemd deployment recovery

The eleven AI-FILM timers are **user-systemd** units owned by the lingering `dragon` user manager. They must not be installed under `/etc/systemd/system`: the runtime verifier intentionally evaluates writability from the unprivileged runtime identity, and root execution can produce `APP_WRITABLE_DRIFT` even when bytes are correct.

Authoritative recovery input is a verified control backup containing `backup-manifest.json` plus `systemd/`. Before any activation, verify the archive and current runtime scripts, restore the exact `systemd/` members to `~/.config/systemd/user` (drop-ins become `<service>.d/`), and require byte-for-byte manifest match. Attach to the lingering user manager with `XDG_RUNTIME_DIR=/run/user/1000` and `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`, then `systemctl --user daemon-reload` and `systemd-analyze --user verify`.

Machine verification command after restore:

```bash
python3 validation/tooling/verify_prodlike_user_systemd.py   --backup-archive /path/to/control-state-*.tar.gz   --unit-dir /home/dragon/.config/systemd/user   --check-timers
```

The verifier validates archive manifest bytes, deployed unit/drop-in hashes, and optionally all timer enabled/active states. After unit verification, execute the real periodic oneshots and run runtime-health last. Recovery is complete only when health reports PASS with every check true, authority remains BLOCKED when no external envelope exists, `native_execution_started=false`, and a fresh control backup/offhost export has been produced and verified.

Never recover by inventing unit text from documentation, by changing hashes to match drifted files, or by installing the user units as root/system services.

## Incident matrix

| Symptom | Required response | Forbidden response |
|---|---|---|
| timer active but execution freshness stale | inspect timer/service/journal and clock/manager state; run real service; require health PASS | treating `active` timer alone as proof of execution |
| service never completed after boot grace | inspect missed trigger/dependency; run service and verify timer schedule | extending boot grace to hide a missed job |
| runtime integrity fails | stop readiness claims; use reviewed rebuild/activation path | editing active app bytes to match hashes |
| backup stale/corrupt | preserve bad evidence; create fresh backup; then mirror→export→DR | rewriting sidecar to hide corruption |
| mirror stale/corrupt | keep local verified backup as truth; rerun mirror and verify | claiming second-filesystem DR with failed mirror |
| rebuild fails | stop reconstruction claims; compare exact reviewed identities | regenerating package/manifests without review |
| export stale/corrupt | rebuild from verified backup + rebuild set; heavy drill | manually editing ZIP/manifest |
| full DR fails | preserve failure; determine schema/tool/app/venv/inventory cause; migrate producers first | removing required-file/timer/resource/ledger checks |
| fail-closed campaign fails | verifier confidence is degraded; inspect wrong acceptance/failure class | disabling negative case |
| retention overflow behaves incorrectly | stop cleanup automation; preserve disposable test evidence; repair producer/prune semantics | deleting current live evidence to force target count |
| evidence-ledger verifier fails | preserve chain files; inspect sidecar/chain/state/freshness | deleting or re-signing incident history to make chain green |
| supervised job fails | inspect journal/root cause; rerun real job; require health PASS | `reset-failed` without rerunning job |
| resource limit hit | inspect measured growth and code path; adjust only with reviewed evidence | disabling bounds to recover green status |
| V02 envelope missing | remain blocked; external handoff/preflight only | creating local approval envelope |
| V02 package invalid/expired | return normalized reason to external owner/controller | editing protected refs/timestamps locally |
| V02 READY appears | independently verify exact validator output/refs then reviewed V02→V03 path | starting LAB/native solely from operator instruction |

## Authority staging preflight

```bash
/home/dragon/ai-film-dev/validation-ops/v02-authority-preflight.py --inbox /path/to/staging --json
```

Return codes: `0` READY_FOR_INTAKE, `10` missing envelope, `11` invalid package, `3` staging changed during preflight. It invokes the exact V02 validator and cannot create authoritative READY/trust/LAB/native state.

## Off-host and recovery limits

Binary payload remains on the original host; there is no off-host binary RPO/RTO claim. Full DR duration is a local regression metric, not a host-replacement RTO.