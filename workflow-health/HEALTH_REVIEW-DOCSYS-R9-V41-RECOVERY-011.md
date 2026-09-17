# HEALTH_REVIEW-DOCSYS-R9-V41-RECOVERY-011

```yaml
HEALTH_REVIEW_ID: DOCSYS-R9-V41-RECOVERY-011
TARGET_STATE: V41
LEARNING_MEASURED: LEARNING-RECOVERY-STATE-VERSIONING-006
STATUS: PENDING_EXACT_V41_EXECUTION
LEARNING_006_GATE: STATE_VERSION_AT_LEAST_41
VALIDATION_EVIDENCE_HEAD: 8024990809364168f7bd04cde44ccf7b30c60b66
```

## Qualifying evidence

The structured measurement gate is due and the measurement trigger is satisfied by a real post-V40 recovery-state transition.

Health now checks service execution freshness for all eleven scheduled services using monotonic completion timestamps. The production freshness function rejected both stale completion and never-completed-after-boot-grace simulations.

Actual producer retention behavior was exercised in disposable roots: control backups converged to retention 14, evidence ledger converged to retention 30, and the ledger verifier passed after prune with the chain anchor matching the predecessor expected by the oldest retained record.

A safe transient cgroup probe confirmed systemd resource values are materialized in kernel `memory.max` and `pids.max`. No destructive OOM/fork-exhaustion test was used.

The latest recovery refresh followed the required producer-first chain. At observation time the backup/mirror sample had 87 files and SHA `c213efff4aeff5585bf14efea172889dffe3b33af815dabaf30f3b5e14c887d2`; the deterministic export sample SHA was `023eb0d5275eeb1b27974c908664f17b46a4bbe11a12376d4e085602a7135d11`. Full DR, 8/8 fail-closed campaign, ledger verification and health all passed.

The file count and current recovery hashes are explicitly modeled as rotating samples because bounded ledger history advances. Stable exact-candidate/rebuild identities remain separate and the private off-host manifest continues to pin only those stable identities.

## Measurement rule

Learning 006 may be EFFECTIVE only if the exact final V41 design tree passes lifecycle/adversarial/governance/docs/audit/continuity/runtime checks and GitHub Actions without weakening any recovery/native-authority predicate. R9 review and A9 audit must then bind the same exact target.

No evidence in this record creates LAB authority, READY/trust state, native results, qualification, SITE evidence or HOST_READY.
