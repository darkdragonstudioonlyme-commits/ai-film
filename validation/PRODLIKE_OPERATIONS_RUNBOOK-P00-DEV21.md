# Phase00 dev21 — Production-Like Operations Runbook

## Scope and invariant

This runbook operates only the non-native production-like control plane for exact dev21. The native workflow remains `RUN-P00-VALIDATION-001 / V02_LAB_EXECUTION_AUTHORITY`. No runbook action may infer external approval, create protected authority objects, write the HKLM trust anchor, start `AI-FILM-P00-LAB` for native execution, execute acceptance cases, issue qualification, or claim HOST_READY.

## Fast status surface

Primary operator command:

```bash
/home/dragon/ai-film-runtime/bin/aifilm-prodlike-status.py
```

Expected healthy/non-authorized classification is `READY_NON_NATIVE_PRODLIKE_OPERATIONS` together with `BLOCKED_EXTERNAL_AUTHORITY`. A V02 block is governance state, not a runtime-health failure.

Core verification sequence:

```bash
/home/dragon/ai-film-runtime/bin/verify-current
/home/dragon/ai-film-runtime/bin/verify-control-backup.py
/home/dragon/ai-film-runtime/bin/verify-host-mirror.py
/home/dragon/ai-film-runtime/bin/verify-rebuild-set.py --cold-probe
/home/dragon/ai-film-runtime/bin/verify-offhost-export.py --drill
/home/dragon/ai-film-runtime/bin/verify-recovery-state
/home/dragon/ai-film-runtime/bin/runtime-health.py
```

## Supervision contract

Ten user-systemd timers are expected enabled/active: runtime integrity 15m, V02 watcher 5m, runtime health 10m, control backup 24h, recovery verify boot+6h, host mirror 2h, rebuild cold verify boot+12h, transfer export boot+6h, full DR rehearsal 24h, and fail-closed campaign 7d. User linger must remain enabled.

Control backup freshness limit is 30h; host mirror freshness limit is 30h; full DR rehearsal evidence limit is 30h; fail-closed campaign evidence limit is 8d. These are health invariants, not promises of external disaster recovery.

## Recovery chain

Normal refresh order when recovery schema or tooling changes:

1. Run health/integrity checks for the live runtime.
2. Create a new control backup.
3. Verify it locally.
4. Mirror the verified control backup to NTFS.
5. Rebuild the deterministic transfer-ready export from the new backup + exact rebuild set.
6. Run the export heavy drill.
7. Run the full DR rehearsal against the new export.
8. Run the fail-closed campaign against current artifacts.
9. Run health last and require PASS.

Do not run a stricter new recovery rehearsal against an old export and then weaken the rehearsal to make it pass. During the P00 schema expansion, the new rehearsal correctly rejected the old 44-file export; the correct migration was to refresh backup/mirror/export first, yielding a 58-file control state.

## Incident matrix

| Symptom / failure class | Required response | Forbidden response |
|---|---|---|
| `verify-current` fails | Stop release/DR assertions; inspect immutable app/runtime manifest drift; repair only by reviewed release activation/rebuild path. | Editing files inside active dev21 app tree to make hashes match. |
| `BACKUP_STALE` | Run control-backup service; reverify; then mirror/export/rehearsal in recovery-chain order. | Extending freshness threshold to hide stale state. |
| backup hash/member mismatch | Preserve bad archive for diagnosis; create a fresh verified backup from live known-good control state. | Rewriting sidecar to match an unexplained corrupted archive. |
| host mirror stale/corrupt | Keep local verified backup as source of truth; rerun mirror and verify NTFS bytes. | Claiming second-filesystem recovery while mirror verifier fails. |
| rebuild-set verify fails | Stop reconstruction claims; compare exact package/wheel/manifests against reviewed hashes. | Regenerating package/manifests without code review. |
| transfer export stale/corrupt | Rebuild from latest verified backup + exact rebuild set; run heavy drill. | Editing ZIP/manifest manually or calling it off-host DR. |
| full DR rehearsal fails | Inspect journal/evidence; identify whether failure is old-schema export, required-file gap, app-byte drift, venv reconstruction or inventory drift; refresh upstream artifacts if schema changed. | Removing required-file/timer checks to recover green status. |
| fail-closed campaign fails | Treat verifier confidence as degraded; inspect which corrupted artifact was wrongly accepted or wrong failure class was returned; do not trust healthy-path verification alone. | Disabling the failing negative case. |
| timer inactive/disabled | `daemon-reload`, enable/start the exact timer, run associated service once, then rerun health. | Ignoring timer state because last evidence is still fresh. |
| supervised job `Result!=success` | Read service status/journal, correct root cause, rerun job and health. | Resetting failure state without rerunning job. |
| disk free <=5 GiB | Halt nonessential artifact growth; inspect retained safe backups/logs and cleanup only according to documented retention. | Deleting current verified package/rebuild set or protected authority material. |
| V02 `APPROVAL_ENVELOPE_MISSING` | Remain blocked; use external handoff and optional read-only preflight for a staging package. | Creating an approval envelope locally. |
| V02 package INVALID | Return exact normalized reason to external owner/controller; they must correct/reissue protected records. | Editing protected external refs/objects to satisfy validator. |
| acceptance suite expired | External authority must issue a new <=24h suite bound to exact identities. | Changing timestamps or expiry locally. |
| V02 READY appears | Verify validator output and all immutable refs; proceed only through the reviewed V02→V03 staging procedure. | Starting LAB/native execution solely because an operator/user said “continue”. |

## Authority staging preflight

For a proposed external package in a staging directory:

```bash
/home/dragon/ai-film-dev/validation-ops/v02-authority-preflight.py --inbox /path/to/staging --json
```

Return codes: `0` means the exact V02 validator reports READY_FOR_INTAKE; `10` means envelope missing; `11` means invalid package; `3` means the staging tree changed while preflight was running and is rejected. Preflight never creates the authoritative READY flag and never changes V02 itself.

## Off-host metadata semantics

The private Google Drive document is a static identity anchor for exact source/package/wheel/app/runtime/rebuild identities. Rotating control-backup/export hashes are deliberately not pinned there, because daily backup rotation would make such a claim stale. The binary payload remains on the original host; `OFF_HOST_DR_CLAIMED=false` remains mandatory.

## Evidence and recovery limits

The full DR rehearsal duration is useful as a regression metric for the local disposable rehearsal only; it is **not** a host-replacement RTO. Daily control backup and 30h freshness imply bounded local control-state age, but there is no off-host binary RPO until a trusted binary transport actually stores and verifies the payload on another host/provider.
