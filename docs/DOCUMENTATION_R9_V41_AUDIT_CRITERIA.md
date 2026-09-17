# DOCSYS-V2-R9 V41 Forensic Hardening — A10 Holistic Audit Criteria

A10 audit may PASS only if R10 detailed review PASS exists and binds the same exact forensic-hardening SHA, and all of the following hold:

1. The control plane distinguishes claim labels, structural checker results, semantic measurement evidence and cross-run outcomes.
2. No `EFFECTIVE` claim is justified solely by evidence-path existence, state-version progression or unrelated checker PASS.
3. Learning metric ownership cannot drift silently between immutable record and lifecycle register.
4. Measurement receipts make scope and sample cardinality reviewable; metrics requiring multiple events are not under-sampled.
5. Canonical test-governance reviews resolve their exact proposal/gap provenance.
6. The current-state read path cannot mistake stale root package metadata for accepted-candidate authority.
7. Review/audit verdict branch CI contradictions are explicitly classified as process/tooling debt; exact design-target CI and post-promotion CI remain mandatory.
8. Documentation does not claim GitHub branch/ruleset enforcement unless current external configuration was independently verified.
9. CI lifecycle-domain coverage is assessed; uncovered authority-changing paths are recorded as automation debt until fixed.
10. Continuous-improvement claims use comparable measurement populations/windows or are labeled unmeasured rather than inferred from activity/version count.
11. R10/A10 are new immutable verdicts bound to the new SHA; old R9/A9 artifacts remain historical evidence only.
12. Product/native boundaries remain unchanged: no LAB run, qualification, SITE evidence or HOST_READY is invented by documentation hardening.

Any false closure, hidden red CI, unsupported effectiveness claim, unresolved proposal provenance, stale-authority ambiguity or native-state advancement requires audit FAIL.
