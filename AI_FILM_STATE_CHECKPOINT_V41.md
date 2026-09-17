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

## Forensic-hardening promotion history

The finalized forensic-hardening tree was independently reviewed as `DOC-V2-R9-REVIEW-011` and audited as `DOC-V2-R9-AUDIT-011`. Those R11/A11 verdicts remain immutable evidence for their exact prior design SHA only.

The earlier R10/A10 chain is historical evidence only: pre-promotion inspection found stale pending-review state and understated enforcement metadata, so those verdicts were intentionally not used as promotion authority.

## Post-promotion authority-reference correction

A fresh canonical reread found a semantic contradiction that the historical R11/A11 structural checks did not catch: live-authority prose in `PROJECT_STATE.md` and this checkpoint still named superseded R10/A10 as if they could authorize the current tree, even though canonical governance fields correctly selected R11/A11. The forensic design also contained one unqualified sentence assigning semantic-review authority to R10/A10.

`workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015.md` preserves this failure instead of erasing it behind the earlier PASS. Revision `R11_V41_AUTHORITY_REFERENCE_CONSISTENCY` therefore:

1. allocates new exact-tree verdicts R12/A12 rather than reusing R11/A11;
2. adds `DESIGN_RECORD` to canonical governance so the active design surface is machine-addressable;
3. requires Markdown/JSON governance parity for revision, branch roles, design record and final verdict identities;
4. derives the expected live `R<n>/A<n>` pair from canonical final review/audit IDs and rejects a mismatched pair on current authority surfaces unless the line is explicitly historical/superseded context;
5. finalizes learning 007 from conditional `ACTIVE_ON_PROMOTION` to `ACTIVE` using its already-existing historical R11/A11 activation evidence, so it does not depend on the new promotion's verdict fields.

The first detector implementation deliberately failed closed twice on design refinement (`35223022725`, `35223154818`) before line-local historical classification was made precise. Exact detector commit `0d106cbad7e144b737cb43eb17409339d107021d` then passed GitHub Actions run `35223256888` / job `105208358932` across lifecycle, adversarial lifecycle, governance, active-doc consistency, workflow continuity and holistic audit.

That real semantic checker/schema evolution satisfies the trigger for `LEARNING-CONTROL-001`; the candidate receipt `learning/measurements/MEASUREMENT-LEARNING-CONTROL-001-001.md` was later confirmed by historical R12/A12 semantic review. New `LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008` captures the reusable rule and remains pending future effectiveness measurement after conditional R12/A12 activation.

The historical R12/A12 correction was reviewed/audited on its exact prior design SHA. Historical R10/A10, R11/A11 and R12/A12 references remain evidence only and are not live authority for the new tree.

## V02 external-authenticity reconciliation

Validation lane head `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa` records a forensic trust-boundary correction without native execution. The approved local inbox was confirmed writable by the constrained Windows operator, so ACL protection plus content hashes could prove local integrity but not independent external authorship. Reviewed/audited tooling now requires an Ed25519 signature over the exact raw approval-envelope bytes under a hash-pinned external trust config.

Runtime deployment is verified fail-closed: trust config remains `PENDING_EXTERNAL_KEY`, `approval-envelope.json` is missing, READY and native-policy candidates are absent, HKLM native trust is absent, the V02 watcher is enabled/active, and `AI-FILM-P00-LAB` remains Stopped. All 86 native procedures remain `NOT_RUN`; qualification, SITE and HOST_READY remain unchanged.

New `LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009` captures the reusable rule: local ACL ownership and content-addressing are not independent authority when the constrained operator can write the store. External authority must be cryptographically rooted outside that operator boundary, and key activation itself is a separate reviewed transaction.

The exact reconciliation tree must be independently reviewed by R13 and audited by A13. Historical R12/A12 remains authority only for its prior exact documentation tree.

Canonical next action remains `RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY`: obtain external Ed25519 public-key provenance, review/activate only that public key, then require a genuinely externally signed exact approval envelope before V03.
