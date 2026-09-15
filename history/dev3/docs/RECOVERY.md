# Recovery notes — dev3 source, not execution authorization

No full native recovery/resume CLI is delivered. Do not delete an unresolved fence, truncate/repair a journal, kill native work, replay an uncertain mutation or edit old plans to fit new approval.

`SessionRunner.reconcile` and NativeDriver's observer link new read-only authority to the original immutable fence under one guard. The observer checks native writer/service state and actual after-state; guest-affecting reconciliation requires scoped actual owner/controller postcheck rather than silently booting a guest. Full cancellation, SAFE_PAUSE (non-success) accounting and pending-fence safe-diagnostic publication are still open implementation work. A normal support-bundle run does not bypass the fence.

Only TERMINAL plus matching CLEAR counts as completed progress. Metadata NOOP initialization remains distinct from operation NOOP: full native operation NOOP currently blocks if fresh effective postconditions are not implemented. Returning a named blocker is not a replacement for implementing the approved idempotency contract.

Before C3, `PRE_C3_PROOF_OBSERVED` binds protected data/config/checkpoint scope at the precondition time; it intentionally does not treat an approved runtime change as unexpected source-data drift. After restart, owner postchecks refer back to that prior proof while honoring current withdrawals. No postdated backup is invented, and no destructive rollback/unregister is supplied.

Protected snapshots use ownership-marked create-only paths. Interrupted/partial captures are retained; only a fully read-back snapshot index committed to the journal can be selected for publication. Privacy failure publishes no collected-content archive. Mandatory incomplete/optional partial/integrity/output outcomes remain distinct. Full publication-crash recovery and safe E17 handoff still require source integration.

Source omissions remain implementation work. A later actual validation mismatch creates VALIDATION_FAILURE with unknown root cause until established. A genuine needed change to reviewed behavior creates DESIGN_GAP. No route here authorizes changing the user's host during source authoring.
