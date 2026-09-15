# Dev12 publication recovery update

E16 bundle and separate E17 assessment now use deterministic protected staging paths bound in write-ahead intent before any file write. Recovery is strictly observational: it does not rename/delete a retained temp, overwrite a final path, regenerate bundle/assessment bytes, or retry publication.

For expected output, final-only exact bytes can be re-observed; temp-only exact bytes remain retained `FAILED_OUTPUT/18`; both final+temp block as ambiguous; neither remains missing/output failure. For a durable no-archive E16 outcome, recovery requires no unexpected final file. For a recovered GATE_HANDOFF component eligible for E17, reconciliation requires an existing E17 intent and exact output bytes; a missing E17 intent cannot be invented. The recovered E17 artifact remains a proposal and cannot set HOST_READY/MASTER acceptance.

---

# Recovery notes — dev4 source, not execution authorization

Do not delete/truncate a fence or journal, kill native work, replay uncertain mutation, edit the original plan hash/purpose, unregister a distro or mark an exit code as a postcondition.

## Original-fence operations

Recovery uses an ordinary approved `verify` request with purpose `RECONCILIATION_ONLY`, linked to the original immutable plan/fence. With no additional pinned intent it remains RECONCILE. An existing `refs` slot can reference a role-pinned `recovery_request` selecting DIAGNOSE, RECONCILE, PAUSE or CANCEL; this is intent only, not evidence, approval or revocation. See RECOVERY_INTENT_BINDING.md.

DIAGNOSE collects current bounded C0 observations under the existing host guard, records raw diagnostic data only in the protected journal and returns safe references. It retains the original fence. Ordinary support-bundle admission does not bypass that fence.

PAUSE/CANCEL require measured absence of pending writers, accounted detached reads/servicing/reboot and an authenticated current `run_revocation` proof covering the exact original run/fence and requested disposition. They durably write SAFE_PAUSE before CLEAR. They return **20**, not successful step completion. The old plan is revoked and must not be replayed; continuing later requires a newly bound/approved plan, not removing the marker. No process termination, destructive cleanup or rollback is performed.

RECONCILE requires actual postconditions under renewed authority. A paused record cannot be reinterpreted as success. Interrupted LIVE_REVALIDATION has its own C0 reconciliation checks and may finish that verification record without duplicating any original mutation step.

## Failure accounting

If diagnostic, authorization, observation, terminal or CLEAR write fails, retain the original uncertainty/progress. After a durable SAFE_PAUSE but failed CLEAR, ordinary admission remains blocked; recovery must bind the exact current fence and check current proof rather than assuming that a previous response succeeded.

Detached C0 process witnesses are separate from mutation witnesses and use unique identities. Unresolved read operations block admission even without a mutation fence. **The complete original-request recovery entry for a detached read that failed before any mutation fence exists remains unfinished source.** Never resolve this by deleting its journal or treating a vanished process handle as proof.

## Committed rerun

A completed run is not trusted merely because an old terminal record exists. Live revalidation checks current identity/content/assets, source pins, authority and output capacity; it journals separate evidence without rerunning installation, workspace mutation, restart or clone boot. Pending servicing, drift or unavailable observations block. A NOOP result never substitutes for the terminal Phase00 gate.

## Still incomplete

Full native lifecycle/OOBE/reboot dispatch, journal-capacity management, failure-stage support bundle/publication recovery and E17 integration remain implementation work. No complete native recovery CLI or later execution authority is supplied. Actual validation failures are recorded only in VALIDATION; author test failures are retained as author history.

## Dev5: original request without mutation fence

A pending detached C0 read is handled by a new RECONCILIATION_ONLY request that references the exact immutable original plan and exact pending-read-set digest. The native coordinator selects this path only when no mutation fence exists; it does not invent a fence or remove journal records. Diagnosis retains uncertainty. Release requires native PID/start/job terminal observation or a current independently measured missing-witness absence proof with collector/raw provenance. Authority is checked again before release. Cancellation/pause additionally requires current revocation; neither commits the original mutation step.

The controller reserves native journal and physical output space before reads/diagnostics. A torn journal or missing legacy witness without sufficient independent evidence remains blocked; no automatic truncation, stale-lock deletion or false absence proof is provided. Partial release after an append failure requires a subsequent request bound to the remaining read set.

Publication interrupted after final output can be re-observed from exact bytes and ZIP manifest, linked to the original publish intent. It never retries publication, replaces output or uses an intended hash alone. Missing/partial final output and an interrupted separate E17 proposal still have open implementation work; do not delete output or claim they were recovered.
