# DOCSYS-V2-R9 V41 Authority Reference Consistency — A12 Holistic Audit Criteria

A12 may PASS only after R12 PASS exists for the same exact design SHA and the review-bearing commit itself has green REVIEW-stage CI.

1. The correction is exact-tree governed: design → R12 record → A12 record, with no policy/state/checker edit between the audited design SHA and promotion except the two predeclared verdict artifacts.
2. R11/A11 remain immutable historical evidence for their prior exact target and are not represented as authority for the changed tree.
3. Current authority surfaces derive the live verdict pair from canonical final IDs and reject unqualified superseded pairs.
4. Historical provenance remains readable: the detector distinguishes explicit historical context from live authority rather than banning all old verdict text.
5. Governance Markdown/JSON parity includes the active design record and final verdict identity, not only token existence.
6. Persistent adversarial active-doc tests fail on stale live authority and governance parity drift while accepting explicit historical context; workflow trigger coverage includes future `tools/test_*.py` regression files.
7. The incident is retained in health evidence and routed into reusable learning; prior PASS labels are not rewritten to pretend the blind spot never existed.
8. Learning 007 activation is decoupled from the new promotion's final verdict fields, preserving the promotion-finalization lesson.
9. CONTROL-001 EFFECTIVE is accepted only if R12's semantic review of its receipt is valid; structural receipt binding or green CI alone is insufficient.
10. Learning 008 is activated only by exact R12/A12 promotion evidence and remains `PENDING_MEASUREMENT` afterward.
11. Product/native state remains unchanged and protected external LAB authority is still required before V02 can advance.
12. Post-promotion `main` CI remains mandatory; GitHub branch/ruleset protection is not claimed unless separately verified.

Any contradiction between structured governance and current prose, any reused old verdict authority, any erased failure evidence, unsupported effectiveness or any native/product advancement requires A12 FAIL.
