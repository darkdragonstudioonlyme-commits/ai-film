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

## Supervision and resource contract

Eleven user-systemd timers must remain enabled/active/Persistent: integrity 15m, V02 watcher 5m, health 10m, backup 24h, recovery boot+6h, mirror 2h, rebuild boot+12h, transfer export boot+6h, full DR 24h, fail-closed campaign 7d, and operational evidence ledger 24h.

All 11 AI-FILM oneshot services use accounting plus `MemoryMax=256M` and `TasksMax=128`. These bounds were chosen after observed peak RSS measurements; highest measured peak was ~44 MiB. Health verifies effective resource settings and previous results for ten supervised jobs.

The evidence ledger retains 30 safe hash-chained snapshots. It may preserve FAIL records; health requires ledger integrity/freshness, not that historical snapshots are all PASS.

## Recovery migration order

When control/recovery schema changes, producers must be regenerated before a stricter consumer may be declared healthy:

1. verify live runtime/health inputs;
2. create and verify a new control backup;
3. mirror the verified backup to NTFS;
4. rebuild deterministic transfer export from new backup + exact rebuild set;
5. run export heavy drill;
6. run full DR rehearsal against the new export;
7. run fail-closed campaign;
8. run health;
9. archive a new evidence-ledger snapshot.

Do not weaken the DR consumer to accept an old payload. Both the 44→58 and 58→85 schema migrations intentionally produced `control-required-file` before producer refresh and passed after producer regeneration.

## Incident matrix

| Symptom | Required response | Forbidden response |
|---|---|---|
| runtime integrity fails | stop readiness claims; use reviewed rebuild/activation path | editing active app bytes to match hashes |
| backup stale/corrupt | preserve bad evidence; create fresh backup; then mirror→export→DR | rewriting sidecar to hide corruption |
| mirror stale/corrupt | keep local verified backup as truth; rerun mirror and verify | claiming second-filesystem DR with failed mirror |
| rebuild fails | stop reconstruction claims; compare exact reviewed identities | regenerating package/manifests without review |
| export stale/corrupt | rebuild from verified backup + rebuild set; heavy drill | manually editing ZIP/manifest |
| full DR fails | preserve failure; determine schema/tool/app/venv/inventory cause; migrate producers first | removing required-file/timer/resource/ledger checks |
| fail-closed campaign fails | verifier confidence is degraded; inspect wrong acceptance/failure class | disabling negative case |
| evidence-ledger verifier fails | preserve chain files; inspect sidecar/chain/state/freshness; do not rewrite history | deleting or re-signing incident history to make chain green |
| timer disabled/inactive | reload, enable/start exact timer, run associated job once, rerun health | relying on old fresh evidence |
| supervised job fails | inspect journal/root cause; rerun real job; require health PASS | `reset-failed` without rerunning job |
| resource limit hit | inspect peak/task growth and code path; adjust only with measured evidence/review | disabling bounds to recover green status |
| health FAIL during incident | archive evidence before repair when safe; fix root cause; rerun job+health; archive recovery snapshot | overwriting failure evidence before capture |
| disk <=5 GiB | stop nonessential growth; clean only documented retained safe data | deleting exact package/rebuild/protected authority |
| V02 envelope missing | remain blocked; external handoff/preflight only | creating local approval envelope |
| V02 package invalid/expired | return normalized reason to external owner/controller for reissue | editing protected refs/timestamps locally |
| V02 READY appears | independently verify exact validator output/refs then reviewed V02→V03 path | starting LAB/native solely from operator instruction |

## Incident preservation drill

The supervised failure drill proved the required sequence: inject a temporary service failure → observe `Result=exit-code` → health FAIL → archive ledger FAIL snapshot → remove temporary fault → rerun real service → health PASS → archive next ledger snapshot → verify hash-chain across FAIL→PASS. Temporary drill configuration must never be included in a backup/export.

## Authority staging preflight

```bash
/home/dragon/ai-film-dev/validation-ops/v02-authority-preflight.py --inbox /path/to/staging --json
```

Return codes: `0` READY_FOR_INTAKE, `10` missing envelope, `11` invalid package, `3` staging changed during preflight. It invokes the exact V02 validator and cannot create authoritative READY/trust/LAB/native state.

## Off-host and recovery limits

Private Google Drive stores only stable exact-candidate/rebuild identity metadata. Rotating control/export hashes are intentionally not pinned there. Binary payload remains on the original host; there is still no off-host binary RPO/RTO claim. Full DR rehearsal duration is a local regression metric, not a host-replacement RTO.