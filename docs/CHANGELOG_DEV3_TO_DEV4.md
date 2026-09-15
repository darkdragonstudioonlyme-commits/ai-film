# Change log — exact dev3 to dev4

## Scope

IMPL-P00-001 continuation, IMPLEMENTATION, Phase00. Approved V2/FD/D00 unchanged. Parent dev3 ZIP is the comparison source. New source drop remains PARTIAL, unreviewed and unqualified.

## Changes

1. Add RecoveryRunner and native C0 diagnostic/pause/revocation observers. Scope the intent to immutable original plan/current fence. Renew authority before final writes; never replay a mutation. Add SAFE_PAUSE progress accounting and separate cancellation outcome.
2. Track detached C0 reader intents/witnesses durably and block ordinary admission while unresolved. Add writer-measured recovery helpers; retain the missing no-mutation-fence recovery entry as source work.
3. Add committed-run LIVE_REVALIDATION with dedicated intent/snapshot/terminal, purpose-specific guest/content/VHD/archive/bundle checks and fresh authority. No provisioning/workspace/lifecycle replay, no clone boot and no duplicate mutation progress.
4. Pin executed/read script members to approved source inventory, size and hash; retain handles across path execution. No self-hash-as-trust fallback.
5. Add 76 tests: recovery 33; live NOOP 29; source/journal 14. Update the direct metadata-only bypass error expectation; it still must reject and does not test a fake native success.

## Actual defect found during author testing

The first new-NOOP run failed because internal progress maps used integer indexes while canonical JSON requires string object keys. Source now has a checked progress_digest conversion; strict JSON input behavior remains unchanged. Failing run and subsequent successful reports are kept under evidence/dev4-history. This is author-test history, not host VALIDATION_FAILURE.

## Remaining work and non-changes

No primary active CLI enablement, complete C0 binding, full E00/failure/publication integration or complete native harness is claimed. No native Windows/WSL/LAB/SITE/PowerShell/guest/network execution. No new approvals, qualifications, code-review verdicts, design changes or phase gate PASS. Historical V8 was not retroactively advanced during the prior unverified turn; this verifiable source drop creates state V9.
