# DOCSYS-V2-R9 V41 External Authenticity — A13 Holistic Audit Criteria

A13 may PASS only after R13 PASS exists for the same exact design SHA and the review-bearing commit itself passes REVIEW-stage CI.

1. Exact-tree chain is design → one R13 review record → one A13 audit record; no state/policy/checker edit occurs after the reviewed design SHA.
2. Validation head provenance is exact and the documentation faithfully represents deployed pending-anchor behavior rather than merely copying intended design.
3. The external-authority model distinguishes integrity (ACL/hash) from authenticity (external cryptographic provenance) and never lets the constrained operator self-issue the external trust root.
4. The private external key is explicitly out of scope for the host/repository; current trust config remains pending.
5. V02 remains BLOCKED; V03/native/qualification/SITE/HOST_READY boundaries remain unchanged.
6. Learning lifecycle retains failure provenance, finalizes old activation without current-verdict coupling and adds learning 009 without claiming effectiveness.
7. Markdown/JSON/checkpoint/NEXT routing are mutually consistent and current R13/A13 authority is machine-checkable.
8. CI covers all standing governance checks and the exact review-bearing commit.
9. GitHub main protection/ruleset enforcement is not falsely claimed.
10. Post-promotion main CI is mandatory; any edit after A13 reopens review/audit.

Any false closure of V02, external-key self-generation, unsigned authority path, stale truth, erased finding or native/product drift requires A13 FAIL.
