# DOCSYS-V2-R9 Correction R1 — holistic audit criteria

Audit the corrected R9 control plane after the post-promotion CI failure. Confirm:

- the original R9 lifecycle checker/promotion semantics remain unchanged;
- the failure is correctly classified as adversarial-test fixture isolation rather than lifecycle-policy failure;
- the corrected test constructs its own promotion-state baseline and is valid before and after promotion;
- current final verdict paths are derived from canonical state, so future R9 review cycles do not require hard-coded test rewrites;
- immutable R1 review/audit remain historical activation evidence for `LEARNING-LIFECYCLE-CONSISTENCY-002`;
- the new fixture-isolation learning is independently reviewed/audited before activation and has a future effectiveness gate;
- V34 learning aggregates are consistent with the lifecycle register;
- promotion CI failure and correction CI success remain durable evidence;
- R2 promotion is atomic/two-verdict-only and post-promotion CI is required to close recovery;
- product validation, LAB authority, qualification and HOST_READY remain unchanged.
