# Stage-derived authority: constructibility correction V2

DESIGN_ID: PHASE00-STAGE-AUTHORITY-FEASIBILITY-002
STATUS: CANDIDATE_REQUIRES_DESIGN_REVIEW
TARGET_DESIGN_COMMIT: 3475c8de57e0cec3a2bb02f488c373366d9e7885
TARGET_DESIGN_RECORD: lane/validation-p00:docs/PHASE00_STAGE_DERIVED_LAB_AUTHORITY_CHANGE.md
PARENT_RUN_ID: RUN-P00-VALIDATION-002
ORACLE_CHANGED: false
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false

## 1. Why the current design needs a bounded correction

The reviewed temporal partition (94 concrete, 15 derived, 10 entry-probe, 14 fence-bound stages) is retained. The exact authority construction is not yet fully specified. Section 4 makes each derivation slot bind the immutable partition digest; section 7 includes those slots and their suite in that partition. Under a literal content-addressed construction this gives partition -> suite -> slot -> partition. No approved acyclic digest projection/exclusion is defined. A coverage count or JSON schema cannot resolve that dependency.

The same design equates the derived import payload path to the producer export path. That is sufficient only for an explicitly selected same-host path arrangement. It does not define an offline working-copy locator on a different destination host as required by the retained external-restore branch.

This supplement proposes precise corrections; it does not overwrite the immutable earlier design/review and is not product implementation authority until its own DESIGN_REVIEW and affected TEST_CHANGE review.

## 2. Acyclic identity construction

Use the following construction order. All JSON is canonicalized using the existing codec; key order and byte scope are part of each schema.

1. `campaign_descriptor`: candidate/build/test/contract, execution_id, fixed host roles, owner and window. It has no suite/root/partition digest.
2. Plan/native-binding templates and derivation slots reference descriptor and already-constructed dependencies. Slots bind exact producer selectors, stage IDs and bounds; they do not embed the eventual signed-root or immutable-partition digest.
3. The suite references concrete plans or slot refs. It has no self-ref or eventual partition digest.
4. A detached `base_manifest` lists exact `(role, ref)` base entries including descriptor/templates/slots/suite. Its digest is the immutable partition identity. It excludes itself, its signature, runtime generations and derived results.
5. The existing local-authority signing transaction signs this manifest/root reference outside the compiler. At admission the consumer proves membership slot -> signed suite -> signed manifest. Absence of the root digest inside the slot is not absence of root verification. No local key is used in this design exercise.

Later derived lineage references the already-known signed root, exact slot and producer evidence, concrete outputs, expected parent-policy digest and target generation. It never embeds the hash of a policy that contains its own ref. A generation record lists parent digest, generation and added refs excluding itself. The full next policy includes that generation record; its hash is written to the publication receipt and becomes the next transaction's parent. Hashing old and new policy bytes remains distinct from constructing the record inside them.

Reject all cycles in the schema's content-addressed dependency graph. Never solve a self-reference with a placeholder, ignored checksum, guessed fixed point or signature bypass. The no-execution witness accompanying this supplement checks graph order only; product schemas/consumers and native admission still need implementation tests.

## 3. Source and destination checkpoint identity

An export supplies immutable source host, source registration, export plan, committed evidence, source locator, bytes and SHA256. An external destination uses a separately bounded destination host/staging locator and a verified offline-copy receipt. The receipt links that exact source evidence to the destination bytes/hash and allowed destination volume/path. Import reads the destination locator; equality of checkpoint bytes/hash is mandatory, equality of path strings across hosts is not.

The destination locator/host/allowed surfaces are fixed or selected by the signed slot's finite allowlist. A caller cannot substitute a new path. Preserve source/backup-of-record, no writable production mapping, pre-boot isolation and no-auto-launch predicates. SAME_HOST_CLEAN retains its original limited semantics and must not stand in for the external branch. No transfer or restore is executed by this supplement.

## 4. Publication, admission and proof boundaries

Before accepting this supplement, DESIGN_REVIEW must provide a concrete call-sequence witness for policy publication, negative overlays, native stage entry and restoration. It must use the existing host-global guard or an explicitly designed same-admission handoff; it cannot assume that a second process can reacquire a guard held by its controller.

A read-check-write-readback sequence without serialization is not compare-and-swap. Enumerate interruption before write, after write but before receipt, before native admission and before restoration. Reconcile exact parent/new digests and durable journal evidence; do not repeat a mutation on timeout. Unexpected parent, duplicate lineage, missing restore or unproven policy state blocks the affected campaign. An old valid generation must not hide a newer revocation.

Nine late-proof roles remain distinct from immutable execution authority. Each concrete schema must name exact scope fields, source type, freshness, producer and consumption boundary. A named role and a boolean 'observed' alone are not verified measurements. Scope-dependent proofs cannot exist before their subject.

## 5. Acceptance and remaining work

The next design review must validate the acyclic projection with exact canonical sample objects, verify same-host and external source/destination mapping, and close the guard/publication sequence witness. Then the affected test-change coverage and source allowlist must be re-reviewed before dev23 implementation resumes. Preserve all 133 stage identities, all current oracles, parent RUN-P00-VALIDATION-002, 86 NOT_RUN procedures and HOST_READY=NOT_EVALUATED.

This correction removes two concrete ambiguities and exposes the outstanding protocol witness in one work item, rather than creating a fresh gap/release for each later symptom.
