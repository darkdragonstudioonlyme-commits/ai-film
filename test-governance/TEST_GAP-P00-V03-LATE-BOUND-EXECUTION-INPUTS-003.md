# TEST_GAP-P00-V03-LATE-BOUND-EXECUTION-INPUTS-003

TEST_GAP_ID: TEST_GAP-P00-V03-LATE-BOUND-EXECUTION-INPUTS-003
RUN_ID: RUN-P00-VALIDATION-002
DISCOVERED_IN_MODE: TEST_DESIGN
PHASE: 00 - Host / WSL
STATUS: OPEN
BUSINESS_RISK: A signed V03 suite can become impossible to execute faithfully when a later plan requires an exact value produced by an earlier native stage, leading either to guessed authority, post-sign mutation, or a test that no longer proves the reviewed source-to-destination behavior.
MISSING_CAPABILITY: Reviewed representation for late-bound execution inputs whose exact values are produced by prior native stages but are consumed by a concrete execution_plan pinned by the pre-V03 LAB suite.
WHY_BLOCKED: The accepted restore flow seals a source export before import and requires exact checkpoint linkage. Current suite rows pin concrete plan_ref values before V03, while RESTORE_IMPORT requires expected_checkpoint plus checkpoint_payload bound to the exact checkpoint digest that RESTORE_EXPORT only reveals after execution.
TEMPORARY_COVERAGE: None. Do not guess checkpoint hashes, substitute unrelated checkpoints, execute export before V02, or mutate signed suite/plan authority after export.
OWNER_WORKFLOW: WORKFLOW_REVIEW
RETURN_TO: RUN-P00-VALIDATION-002/V02B_LOCAL_AUTHORITY_PACKAGE
EXIT_CONDITION: Workflow review determines the smallest authority/test architecture that represents export-produced checkpoint identity without weakening T09/T07 restore semantics, and identifies whether validation-only tooling is sufficient or accepted harness/product authority schema must change.

## Exact contract and source boundary

The normative infrastructure design requires source export to seal before transfer/import, and post-apply T00-09 must restore the exact checkpoint state being handed off. The acceptance matrix requires full checkpoint bytes, source identity and destination to be linked through E00-15; T07-I explicitly tests a source-to-destination restore sequence with immutable checkpoint linkage.

Exact accepted procedures include:
- T00-09: RESTORE_EXPORT -> RESTORE_IMPORT -> RESTORE_VERIFY;
- T07-I: RESTORE_EXPORT -> RESTORE_IMPORT;
- T09-A: RESTORE_EXPORT -> RESTORE_IMPORT -> RESTORE_VERIFY.

The current LAB suite schema contains a fixed hash-addressed plan_ref for each stage. V02 intake loads and checks every referenced execution_plan before V03, and harness execute_stage later resolves that same fixed plan_ref.

RESTORE_IMPORT accepted code requires semantic.refs.checkpoint_payload and verifies its payload_digest equals semantic.expected_checkpoint. The import payload bytes are pinned against that digest. Terminal/evidence code also requires the committed RESTORE_EXPORT checkpoint SHA to equal expected_checkpoint for lifecycle/restore provenance.

Therefore the import plan cannot truthfully contain the digest of the export produced by an earlier stage unless that digest is already known. It is not legitimate to predict it, rename arbitrary bytes to it, or replace the tested source-export checkpoint with an unrelated pre-existing artifact while claiming source-to-destination linkage.

## Why proof slots alone are insufficient

TEST_GAP-P00-V03-LATE-BOUND-PROOF-SLOTS-002 concerns receipts selected after runtime facts exist. This gap is different: the late value is part of execution authority itself. A concrete product plan and suite plan_ref already exist before V03.

A validation-only late-proof augmentation cannot change expected_checkpoint or checkpoint_payload in the signed execution_plan. A design that permits a late-bound execution-plan slot may require an accepted harness/authority schema change; that requirement is intentionally left UNRESOLVED until WORKFLOW_REVIEW.

Machine-readable evidence: validation/evidence/V03-LATE-BOUND-EXECUTION-GAP-20260922/analysis.json.
