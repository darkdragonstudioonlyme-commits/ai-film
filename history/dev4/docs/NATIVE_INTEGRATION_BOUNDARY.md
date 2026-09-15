# Native integration boundary — dev4

## Production wiring vs author-test ports

The production factory still constructs NativeGuard/NativeJournal/NativeStore/NativeSupervisor/NativeDriver. No MemoryGuard, fixture observation, fixture approval or process-exit shortcut is registered in primary native CLI. Primary active commands remain explicitly blocked because full source integration is not finished.

Workspace tests instantiate real session/recovery/policy functions with explicitly synthetic ports. New native helper tests exercise Python logic with fake system/guest/proof/pinning ports. They do not instantiate or run Windows, PowerShell, WSL, guest agents or real network transport. No result is a native observation or qualification receipt.

## Original-fence path

A RECONCILIATION_ONLY request binds an unchanged original plan/fence. The native refresh uses C0-only observations; it does not launch a guest or install/repair a prerequisite. Recovery intent selects an operation but is not proof. The driver separately measures process/service/pending state and verifies current scoped revocation or postcheck artifacts. Protected diagnostic output never becomes a public raw error dump. Cancellation/pause never calls kill, unregister or cleanup and never commits the mutation as successful.

Detached read processes receive distinct durable journal identities. Unresolved reads block ordinary admission even if no mutation fence is present. Recovery helpers exist, but a full original-request recovery entry for the no-mutation-fence case is still not integrated. This is explicit source work, not an environmental prerequisite.

## Committed-run revalidation path

A completed run has an immutable original progress map. The session checks current prerequisites and output reservation, journals a distinct LIVE_REVALIDATION intent, observes current state, captures fresh evidence, refreshes authority and only then records terminal/CLEAR. Revalidation records do not overwrite original mutation completion. No-op does not mean zero diagnostics/evidence writes; it means no repeated provisioning/lifecycle/workspace mutation.

Guest-facing purposes require the guest already running before read-only guest assertions. Export/clone purposes keep targets stopped, hash/read existing VHD/archive content and reject drift instead of starting a clone. Bundle revalidation reads original bytes, preserves non-success/partial outcome and does not republish. Full cross-stage proof/evidence catalog correctness and public entry still need integration.

## Script and executable boundaries

SourcePins checks approved build inventory digest before trusting member hashes. Script bytes are read through pinned handles and checked against that inventory. Path-executed fixed PowerShell scripts keep their pinned file/ancestor handles during execution. This does not establish native ABI behavior or prove that the complete executable/dependency/bootstrap trust chain is implemented or tested.

## Not execution authorization

A source file containing a native actuator is not authorization to execute it. Code review, actual lab qualification and site bindings are separate future gates. No native work is executed by this authoring package creation. Unfinished CLI/evidence/harness work is tracked in REMAINING_IMPLEMENTATION.md.
