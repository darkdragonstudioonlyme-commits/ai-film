# Recovery notes — dev2 source, not an authorization to execute

No full native recovery/resume CLI exists in this partial release. Keep the original host, distro, backup and unresolved metadata intact.

## Interrupted mutation

Do not delete a fence, truncate a journal, retry a native command, kill a potentially active mutation, rename a target or edit an old plan to make it match new approval. The native journal uses append-only frames; incomplete framing, hash mismatch, replaced root or missing genesis blocks. Native process exit does not prove service-level completion.

The new `resume.bind_reconciliation` source relates a separately approved RECONCILIATION_ONLY document to the original immutable plan and fence. It preserves original plan/run identity and records new authorization separately. It grants no permission to replay old mutations. Before terminal/CLEAR, the missing native observer must still establish actor/host/target, original side effects, service/writer state and required data/ownership assertions.

`completed_steps` accepts only properly replayed terminal + matching CLEAR records, rejects gaps and duplicate completion, and never treats INTENT, timeout or APPLIED text as completion.

## Metadata initialization

A previously initialized valid root with no pending fence produces NOOP. An existing root lacking a valid root-bound journal is not adopted. No automatic repair or replacement occurs; resolve through the appropriate approved recovery/design work, preserving forensic bytes.

## C3 and restore

The approved pre-C3 independent protection gate is unchanged. There is no new waiver for a clean target, no sibling-clone isolation claim and no permission to downgrade shared runtime. Restore import/launch/stop must use the approved actors/envelope and names. Default cleanup remains stop-and-retain; never unregister by default.

## Diagnostics

Do not publish raw registry policy, SIDs, local paths, command output, backup contents or credentials. The new native snapshot/publisher components do not constitute a complete support-bundle command. Redaction not proven means no content publication; failed output must not be labeled success.

## Routing

Implementation omission → continue IMPL-P00-001. Actual validation mismatch later → VALIDATION_FAILURE with root cause UNKNOWN until established. Required approved behavior change → DESIGN_GAP and leave implementation for that affected scope. None of these cases authorizes an automatic rollback on the user's host.
