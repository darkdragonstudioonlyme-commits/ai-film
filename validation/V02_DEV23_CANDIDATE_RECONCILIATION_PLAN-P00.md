# Phase00 dev23 — candidate-specific prerequisite reconciliation plan

RUN_ID: RUN-P00-VALIDATION-002
CANDIDATE_ID: acf18da3-4969-451c-8a4b-a7e46ad89c98
CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
STATUS: PROPOSED_PENDING_BINDING_REVIEW
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false

| Prerequisite | Disposition for dev23 | Rule before V03 |
|---|---|---|
| source/package/wheel/build/test identities | NEW_EXACT_DEV23 | use only reviewed dev23 hashes |
| candidate ID / binding | NEW | exact canonical binding bytes/hash above |
| TEST_REVIEW 006/007 and version TEST_REVIEW 008 | REUSE_DEV23_REVIEW_PROVENANCE | retain exact reviewed records; do not change oracle |
| dev23 CODE_REVIEW + package review | REUSE_DEV23_REVIEW_PROVENANCE | must remain exact PASS targets |
| Phase00 contract digest and 86-procedure inventory content | CONTENT_REUSE_WITH_FRESH_CANDIDATE_BINDING | byte-identical content may be reused; old candidate binding cannot |
| durable local Ed25519 private/public key pair | CONDITIONALLY_REUSABLE_CANDIDATE_INDEPENDENT | fresh key-parity/current-anchor verification required before any signing; private bytes remain outside Git/inbox |
| dev22 signed approval envelope/object graph/signature | REBUILD_REQUIRED | never reuse as dev23 authority |
| authority inbox | NEW_DEV23_NAMESPACE | use a separate dev23 inbox/object graph; do not mix dev22 objects as current authority |
| V02 tooling constants/manifest/templates | REBIND_AND_REVIEW_REQUIRED | create dev23 successor hard-cut to this binding; retain dev22 tooling as history |
| V03 compiler/policy-updater/late-proof tooling from TEST_CHANGE 006/007 | IMPLEMENT_AND_REVIEW_REQUIRED | must satisfy reviewed TD006/TD007 before signing |
| Windows host-support observation | REOBSERVE_BEFORE_SIGNING | historical observation is context, not current dev23 proof |
| prodlike runtime/app deployment | REBUILD_OR_REDEPLOY_DEV23 | dev22 runtime receipts are not dev23 product proof; supervision pattern may be reused only after fresh dev23 evidence |
| stopped/sealed LAB technical base | RESEED_OR_REBUILD_DEV23_REQUIRED | existing distro identity may be used only as a technical base after exact dev23 app deployment/reseal; dev22 app/seal hashes are not dev23 proof |
| LAB app tar/manifest/rebuild index/artifact seal | REBUILD_REQUIRED | bind exact dev23 package and candidate binding |
| V02 authority graph/suite/registration/fixtures/plans | REBUILD_REQUIRED | current <=24h suite, dev23 candidate binding, four-mode stage authority |
| qualification / HOST_READY / SITE | NOT_REUSABLE_NOT_EVALUATED | remain closed until later gates |

The plan separates reusable **content or infrastructure pattern** from reusable **proof**. A dev22 PASS receipt may explain how to perform a dev23 step but cannot satisfy a dev23 candidate-specific gate unless the governing contract explicitly permits content reuse and a fresh binding/evaluation confirms it.

No LAB start, native procedure, signing, HKLM mutation, qualification or SITE action is part of this preparation.
