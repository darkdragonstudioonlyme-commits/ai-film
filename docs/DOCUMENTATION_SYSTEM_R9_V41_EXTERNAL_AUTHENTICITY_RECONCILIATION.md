# DOCSYS-V2-R9 V41 — external-authenticity reconciliation

## Purpose

Revision `R12_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION` reconciles canonical documentation with exact validation lane head `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa`. It does not advance native validation. Its purpose is to prevent the canonical router from treating operator-writable protected files as sufficient evidence of an external decision.

## Validation fact change

The LAB candidate, dev21 identities and 86-case inventory are unchanged. What changed is the **trust model** for V02. Validation forensic review established that the approved inbox ACL and SHA-addressed object graph provide integrity, but the current operator has write authority to that local store. Therefore those controls cannot independently prove external authorship.

Reviewed/audited validation tooling now requires:

1. an independently established Ed25519 public-key identity/provenance;
2. a separate reviewed activation transaction for that public trust anchor;
3. a detached Ed25519 signature over the exact raw `approval-envelope.json` bytes;
4. unchanged SHA-addressed protected refs/role pins/suite/fixture/plan semantic checks;
5. fail-closed behavior while the external trust config is `PENDING_EXTERNAL_KEY`.

The external private key must never be generated or stored in the constrained host/operator environment.

## Canonical truth after reconciliation

- validation evidence head: `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa`;
- V02 hardening: `DEPLOYED_PENDING_EXTERNAL_KEY`;
- real approval envelope: MISSING;
- V02 ready-to-advance: false;
- LAB: Stopped / native NOT_RUN;
- qualification: NOT_ISSUED;
- SITE: NOT_RUN;
- HOST_READY: NOT_EVALUATED.

## Learning lifecycle

Historical R12/A12 completed activation evidence for learning 008, so this revision finalizes 008 from `ACTIVE_ON_PROMOTION` to `ACTIVE` without coupling it to R13/A13. New learning 009 captures the external-authenticity boundary and is `ACTIVE_ON_PROMOTION` only after R13/A13; effectiveness remains pending a future external-key activation or signed-approval event.

## Promotion boundary

This tree predeclares new final verdicts `DOC-V2-R9-REVIEW-013` and `DOC-V2-R9-AUDIT-013`. Historical R12/A12 remains immutable evidence for the prior exact documentation tree only. R13/A13 must bind one exact final design SHA; promotion may add only those two verdict records and requires post-promotion main CI.

## Non-claims

No external key is activated by documentation. No approval package exists. No native trust is installed. No LAB case is executed. No product code changes. No qualification, SITE evidence or HOST_READY is produced.
