# Stage-derived authority: constructibility correction V3

DESIGN_ID: PHASE00-STAGE-AUTHORITY-FEASIBILITY-003
REVISION: V3
STATUS: CANDIDATE_REQUIRES_DESIGN_REVIEW
TARGET_DESIGN_COMMIT: 3475c8de57e0cec3a2bb02f488c373366d9e7885
TARGET_DESIGN_RECORD: lane/validation-p00:docs/PHASE00_STAGE_DERIVED_LAB_AUTHORITY_CHANGE.md
PARENT_RUN_ID: RUN-P00-VALIDATION-002
ORACLE_CHANGED: false
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_AUTHORIZED: false

## 1. Scope and retained authority

The reviewed temporal partition remains exactly 94 `CONCRETE_PRE_V03`, 15 `STAGE_DERIVED`, 10 `ENTRY_PROBE_AUTHORITY` and 14 `FENCE_BOUND_RECONCILIATION` native stages. This correction changes neither PROCEDURES nor expected exits, oracles, evidence sets or Phase00 business behavior. It closes constructibility gaps in the reviewed stage-authority design before dev23 implementation.

Product implementation remains inside TEST_CHANGE 006's reviewed allowlist: ADD `src/aifilm_p00/native/stage_authority.py`; MODIFY `src/aifilm_p00/native/harness_controller.py`; add/modify only its declared tests. `authority.py`, `plans.py`, `native/harness_cases.py`, `native/request_entry.py`, `resume.py`, `recovery.py`, required-native-test inventory and the four normative Phase00 contracts remain byte-identical. If these rules cannot be implemented within that boundary, return to DESIGN/TEST_REVIEW instead of widening scope.

## 2. Acyclic base authority construction

All content-addressed objects use the existing canonical JSON codec. Construction is a DAG, in this exact order:

1. `campaign_descriptor`: candidate/build/test/contract identities, execution_id, fixed host roles, owner and suite window. It contains no suite, manifest or partition digest.
2. Immutable plan/native-binding templates and derivation slots reference only the descriptor and already-built static dependencies. A slot contains no eventual manifest/root/partition digest.
3. `lab_acceptance_suite` references concrete plan refs or derivation-slot refs according to the normative 133-stage catalog. It contains no self/root/manifest digest.
4. Detached `base_manifest` contains schema version, descriptor ref and a canonically sorted list of exact `(role, ref)` base entries covering descriptor/templates/slots/suite and other immutable V02 base refs. It excludes itself, its signature, future generation records, runtime lineages and derived/proof objects.
5. `immutable_partition_digest = SHA256(canonical(base_manifest))`. The existing local-authority signing transaction signs/binds this detached manifest identity outside the graph compiler. No key is used by this design/review.
6. Static admission proves the selected suite/slot is a member of the signed manifest. Slots do not need to embed the root digest to be root-authorized.
7. Runtime lineage references the already-known signed manifest/root, exact slot, producer evidence, concrete derived refs and the observed parent/new policy generation. It never embeds the hash of a policy that contains that lineage.

A runtime generation record is itself a content-addressed blob whose body contains `role`, schema version, parent policy digest/generation, new generation number, immutable_partition_digest, exact added refs grouped by role, event identity and withdrawn=false. It excludes its own ref and the eventual full-policy digest. The complete next policy pins that generation-record ref; only after full-policy bytes exist is their digest computed and written into the external publication receipt/journal event. Placeholder hashes, ignored fields, fixed-point guesses or checksum bypasses are forbidden.

## 3. Checkpoint source/destination locator contract

Source and destination locator identity are separate. A source export record binds `{source_host_id, source_registration_id, export_plan_ref, export_evidence_ref, source_volume_id, source_canonical_path, checkpoint_sha256, checkpoint_bytes}`. A different destination never inherits the source path string as authority.

Every restore-capable signed slot contains or references a finite, immutable `destination_locator_allowlist`. Each entry is exactly:

```text
{
  host_id,
  volume_id,
  canonical_path,
  purpose: "STAGING_IMPORT",
  max_bytes,
  offline_copy_required: true|false
}
```

`host_id`, `volume_id` and `canonical_path` are exact values, not globs/prefixes; `max_bytes` is a positive slot bound. Entries are sorted canonically before slot hashing. EXTERNAL_RESTORE entries require `offline_copy_required=true`. SAME_HOST_CLEAN may use a separate explicitly signed entry with `offline_copy_required=false`; it never substitutes for the external branch.

An external `checkpoint_copy_receipt` is materialized only after copy completion and binds exact source export evidence/ref + source host/volume/path + source checkpoint hash/bytes to exactly one signed destination allowlist entry + observed destination hash/bytes + collector/raw-artifact refs + timestamp. Import requires source hash == destination hash, source bytes == destination bytes, destination bytes <= allowlist max_bytes, exact locator membership and retained isolation/no-production-mapping/no-auto-launch predicates. Cross-host path-string equality is neither required nor accepted as byte identity.

## 4. Exact late-proof slot contract

`ProofReader` remains unchanged. It selects exactly one current pinned receipt for role + requested scope, checks contract/owner/host, issue/expiry, raw measurement/collector binding and claim coverage. This correction defines the nine late-proof slots so no future scope has to be guessed.

| Role | Exact scope at consumer | Earliest materialization boundary | Temporal/source rule | Consumer |
|---|---|---|---|---|
| `source_manifest` | `{host_id,target_registration,source_class}` | target registration/source class observed | normal issue/expiry; OWNER_ASSERTION allowed exactly as current `_source` | session source precondition |
| `protection` | `{host_id,source_witness}` where witness is digest of exact stopped/quiesced protection boundary | protection boundary measured before C3 | normal issue/expiry; OWNER_ASSERTION allowed | C3 precondition/evidence pipeline |
| `restore_envelope` | `{host_id,checkpoint_digest,envelope_digest}` | exact checkpoint + destination isolation/envelope facts exist | native/LAB/SITE measurement chain; no placeholder checkpoint/envelope | import/verify envelope precondition |
| `user_init_receipt` | `{host_id,plan_digest,target_registration,user}` | target registration and actual user-init/default UID observed | normal issue/expiry; no pre-init receipt | user-init observation/postcondition |
| `c3_postchecks` | `{host_id,plan_digest,host_boot}` | post-reboot/C3 host boot exists | `issued_at >= host_boot`; OWNER_ASSERTION allowed as current code | C3 postcondition and terminal sweep |
| `operation_postcheck` | action scope `{host_id,plan_digest,step_id,target_registration,host_boot}` OR live-revalidation scope `{host_id,plan_digest,execution_phase:"LIVE_REVALIDATION",baseline_digest,host_boot,target_registration}` | exact operation/revalidation subject exists | action scope uses normal issue/expiry; live-revalidation additionally requires `issued_at >= fence.witness.captured_at` | reconciliation/noop postcheck |
| `run_revocation` | `{host_id,original_plan_digest,recovery_request_digest,disposition}` | exact recovery request + disposition fixed | normal issue/expiry; OWNER_ASSERTION allowed | recovery/revocation |
| `read_absence_observation` | `{host_id,original_plan_digest,read_id,intent_digest,command_digest}` | detached read intent exists | every measurement timestamp >= read intent `issued_at`; OWNER_ASSERTION not accepted | detached-read recovery |
| `restore_result` | `{host_id,checkpoint_digest,source_target_registration}` | restore result for exact checkpoint/source target exists | normal issue/expiry; exact measured restore result | terminal restore verification |

The late-proof materializer may add a receipt only after all fields in its exact scope exist and all current ProofReader predicates can be satisfied. It cannot invent a future value, widen a scope, use an ID-only observation, or alter execution authority unless a signed derivation slot explicitly consumes that proof ref/value as an allowlisted late field. Existing ProofReader source/freshness behavior is not weakened.

## 5. Serialized policy publication and native admission witness

The accepted native path already owns one host-global mutex `Global\\AI-FILM-P00-HOST-ADMISSION`; nested acquisition is forbidden. Therefore the publisher must not hold that mutex while calling `prepare_execution`/`execute_prepared`, because `native_session()` creates a fresh `NativeGuard` and `SessionRunner.execute()` acquires it itself.

For a `STAGE_DERIVED` stage, the exact sequence is:

**P0 — producer closure.** Required producer stage(s) are committed terminal/current according to the signed slot. No unresolved native fence or detached read may authorize a new derived stage.

**P1 — enter publisher.** `harness_controller` calls an internal `stage_authority` publisher/resolver. The publisher constructs the existing `NativeGuard`/`NativeJournal` primitives for the same host and acquires the same global guard. It never calls public execution while holding it.

**P2 — guarded parent verification.** Under the guard, read the current HKLM Policy bytes, instantiate/validate them as `NativeStore`, require exact expected parent policy digest/generation, no unresolved mutation fence/pending detached read, signed base-manifest identity unchanged, slot/suite current and all producer evidence committed/current.

**P3 — deterministic derive.** Recompute allowlisted late values, destination locator/copy receipt where applicable, native binding, plan, approval and lineage. Validate each object with existing pure predicates. Construct a generation-record blob and complete next Policy using the existing outer NativeStore schema only: `{schema_version,host_id,operator_sids,role_pins,blobs,withdrawn_refs,generation}`. Generation is exactly parent+1; every immutable base ref remains byte-identical; additions occur only under signed slot/proof-authorized roles.

**P4 — validate then publish.** Instantiate the candidate next-policy bytes as `NativeStore` before mutation. Write the complete Policy REG_SZ at the existing protected anchor while the guard is held. Re-read exact bytes immediately and require byte/digest equality, generation parent+1, unchanged immutable base manifest and exact presence/integrity of all added refs. No temporary negative overlay and no rollback-to-parent write are used.

**P5 — durable publication event.** Still under the guard, scan the journal for publication key `(new_policy_digest,suite_ref,case_id,stage_index,slot_ref)`. If absent, append+flush exactly one `AUTHORITY_GENERATION_PUBLISHED` event containing parent/new digest/generation, immutable_partition_digest and derived lineage/plan refs. If an identical key/event already exists, reuse it; conflicting content blocks. Only after readback + durable event may the publisher release the global guard.

**P6 — fresh resolve after release.** `harness_controller` re-opens current authority through `stage_authority.resolve_current(...)`, selects exactly one unwithdrawn lineage for suite/case/stage/slot, verifies root/slot/producer/derived refs and returns the concrete `execution_plan_ref`. A revocation generation must withdraw lineage + all derived binding/plan/approval refs atomically; partial withdrawal is invalid.

**P7 — accepted production entry.** Only after P6, call existing `request_entry.prepare_execution(root,interface,derived_plan_ref)` and `execute_prepared`. `request_entry.py` remains byte-identical. The new session loads fresh policy, authorizes, then `SessionRunner.execute()` acquires the same global guard itself and refreshes/reauthorizes again while held before `c.intent`. If the derived plan/approval/ref set was withdrawn or authority drifted, this blocks before native INTENT.

**P8 — native durability.** After `c.intent`, existing SessionRunner/fence/journal semantics own execution and recovery. Stage finalization records the exact authority_lineage_ref/plan_digest and rejects output whose lineage does not match the signed suite request.

This is serialization, not compare-and-swap pretending: policy mutation is mutually exclusive under the existing host-global guard, and execution obtains a fresh separate guard acquisition only after publisher release.

## 6. Interruption and recovery witness

Publication has a stable candidate identity `K = (expected_parent_digest,parent_generation,suite_ref,case_id,stage_index,slot_ref,derived_object_set_digest)`. Recovery always acquires the same global guard before reading/reconciling. No timeout or missing response authorizes replay.

| Interruption boundary | Durable observation on next entry | Required action |
|---|---|---|
| before Policy write | anchor still exact parent; no publication event for K | deterministically recompute; one guarded publish attempt allowed |
| write may have completed, before readback/event | read anchor under guard | if anchor == exact candidate bytes/digest/generation, validate and do **not** rewrite; append missing idempotent event. If still parent, write once. If another generation is current, adopt only if exact lineage/object set is already present with unchanged root; otherwise `RECONCILE_REQUIRED`/block, never overwrite newer policy |
| after readback, before event | candidate anchor is exact; event absent | do not rewrite; append one publication event keyed by K after validation |
| event committed, before guard release | candidate anchor + exact event exist | publication complete; next process reuses it after normal guard recovery/abandonment rules |
| after publisher release, before `prepare_execution` | candidate/event durable; no native fence | fresh P6 resolve, then P7; do not republish |
| session guard acquired, before `c.intent` | no native fence yet | process loss has no native mutation; next attempt fresh-authorizes current policy; no authority republish unless P2 says missing |
| after `c.intent` or native start | durable INTENT/RUNNING/UNCERTAIN fence exists | existing reconciliation path only; never republish/re-execute the stage as a normal retry |
| terminal journal committed, CLEAR fails | TERMINAL fence remains | exact reconciliation clears the terminal fence; do not re-run stage |

Journal append is not assumed idempotent by itself: the publisher scans under guard for exact publication key K before appending. A same-key/different-body event, torn journal, unknown parent, generation rollback/skip, duplicate lineage, partial derived-ref set or newer revocation blocks the campaign.

## 7. Constructibility and source-scope consequence

The publisher/resolver fits the reviewed product allowlist: `stage_authority.py` owns registry publication, base-manifest/slot/producer/lineage validation and recovery classification; `harness_controller.py` owns suite request parsing, calls publisher/resolver, then enters the unchanged request path. Existing `NativeStore`, `NativeGuard`, `NativeJournal`, SessionRunner and ProofReader semantics are consumed, not modified.

Validation tooling remains separately test-reviewed and may own graph compilation/static verification, policy-generation construction, fixture controller and late-proof materialization. Product code does not receive private signing-key access. No design step signs authority, mutates HKLM, starts LAB or executes native cases.

TEST_CHANGE 006's production file allowlist remains sufficient, but the newly explicit publication/recovery/proof-scope predicates add test obligations. After DESIGN_REVIEW PASS, an affected TEST_CHANGE successor/addendum must map those predicates to negative/interruption tests before dev23 implementation is authorized. ORACLE_CHANGED remains false unless that independent test review finds an upstream behavior conflict.

## 8. Design-review acceptance

DESIGN_REVIEW may PASS only if it independently verifies all of the following on this exact correction: acyclic object/hash order; signed finite destination locator selection and copy binding; all nine exact late-proof scope/timing rules; no nested-guard/deadlock in P0–P8; every interruption row has a fail-closed non-replay disposition; revocation cannot leave a usable orphan derived plan; Test Change 006 source allowlist remains adequate; and all 133 stage identities/94-15-10-14 authority counts and existing oracles remain unchanged.

Static review is not native proof. Preserve parent `RUN-P00-VALIDATION-002`, all 86 NOT_RUN procedures, qualification NOT_ISSUED and HOST_READY NOT_EVALUATED.
