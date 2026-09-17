# AI-FILM-SERVER — State Checkpoint V41

Phase00 product/native state is unchanged: exact dev21 source `934659f535d81d9a4a07389531acc2b9c304fa6d` remains code-review PASS; `RUN-P00-VALIDATION-001` remains BLOCKED at `V02_LAB_EXECUTION_AUTHORITY`; all 86 native procedures remain `NOT_RUN`; qualification is not issued and HOST_READY is not evaluated.

V41 exists because a real post-V40 recovery/control transition occurred. Validation evidence head `8024990809364168f7bd04cde44ccf7b30c60b66` records N1–N6 execution-SLA, retention and rotating-state work.

## Post-V40 evidence

- health now checks last service completion freshness for all 11 services using monotonic timestamps, not merely timer active/enabled state;
- direct negative tests prove `STALE` and `NEVER_COMPLETED_THIS_BOOT` are rejected;
- real backup retention overflow converges to 14 archives;
- real evidence-ledger overflow converges to 30 records and preserves prune-anchor chain continuity;
- benign transient cgroup probe confirms systemd limits are materialized to kernel `memory.max` / `pids.max`;
- producer-first recovery refresh passes backup → mirror → deterministic export → full DR → negative campaign → ledger → health;
- latest observed recovery sample contained 87 backup files at SHA `c213efff4aeff5585bf14efea172889dffe3b33af815dabaf30f3b5e14c887d2`, with transfer-export SHA `023eb0d5275eeb1b27974c908664f17b46a4bbe11a12376d4e085602a7135d11`;
- those bytes/counts are explicitly rotating samples because bounded evidence history advances.

## Learning 006 scheduled measurement

Learning 006 reaches its structured V41 gate and its trigger is satisfied by the real 85→87 recovery-state transition. The success metric is met only if exact V41 checks confirm:

1. recovery producer state was regenerated before stricter consumer success was claimed;
2. no consumer/recovery predicate was weakened;
3. stable exact-candidate identities remain separate from rotating backup/export samples;
4. off-host metadata still pins only stable identities;
5. native authority boundary remains unchanged.

The V41 candidate marks learning 006 EFFECTIVE only subject to exact executable checks, CI, R9 review and A9 audit. Any failure invalidates that candidate conclusion.

## Forensic hardening and R10/A10 contract

- `DOC-V2-R9-REVIEW-010` → `reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R10_PASS.md`
- `DOC-V2-R9-AUDIT-010` → `reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R10_PASS.md`

The forensic hardening adds a semantic-proof contract for learning effectiveness, explicit separation of platform enforcement from project policy, canonical test-governance proposal traceability, and a branch-role requirement for verdict CI. It deliberately does **not** claim those tooling/platform controls are already machine-enforced.

Both R10/A10 verdicts must bind one exact final V41 forensic-hardening design SHA. Promotion may add only those two immutable verdict records and requires post-promotion CI.

Canonical next action remains `RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY`; resilience work cannot substitute for protected external LAB authority.
