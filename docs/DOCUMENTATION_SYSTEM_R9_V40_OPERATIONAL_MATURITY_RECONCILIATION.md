# Documentation System R9 — V40 Operational Maturity Reconciliation

## Purpose

V40 reconciles a real validation/control-plane transition rather than advancing native validation. Validation head `c615af57b7216e2fbb0b3c71a9431e442a4def59` records operational maturity M1–M6 after V39: bounded evidence history, measured resource containment, controlled user-manager reexec, supervised incident FAIL→PASS recovery, and a producer-first recovery-schema migration to the 85-file/11-timer control state.

## Native boundary

No product implementation, package, native configuration, test oracle or candidate identity changes. `RUN-P00-VALIDATION-001` remains the only live run and remains BLOCKED at V02. LAB remains unexecuted; all 86 cases are NOT_RUN; qualification/SITE/HOST_READY are absent.

## Operational maturity facts

- 11 persistent enabled/active timers;
- 10 previous-job results supervised by runtime health;
- 11 services with memory/cpu/tasks accounting, `MemoryMax=256M`, `TasksMax=128`;
- daily operational evidence ledger, retention 30, hash-chain verified;
- controlled user-manager `daemon-reexec` preserved timers/dependencies/resource bounds;
- incident drill proved service failure → health FAIL → ledger FAIL record → recovery → health PASS → chained PASS record;
- control backup/mirror now 85 files, SHA `daa43ca4...`;
- deterministic export SHA `b4cf49cd...` embeds the 85-file recovery state;
- full DR restores 85 files, 11 timer definitions, 11 resource drop-ins and ledger history before reconstructing 283 exact app files;
- negative campaign remains 8/8 PASS;
- off-host binary payload remains absent.

## Recovery-state migration evidence

The new DR consumer intentionally failed on the previous payload with `control-required-file`. The accepted migration sequence was backup producer → NTFS mirror → deterministic export → full DR consumer → negative campaign → health/ledger. No consumer predicate was weakened. This is an observed qualifying transition for learning 006, but V40 does not close effectiveness because its structured gate requires state version at least 41.

## Lifecycle finalization

V39 promoted learning 006 through R7/A7. Before V40 replaces the final review/audit contract, V40 normalizes learning 006 from transition-only `PASS_ON_FINAL_REVIEW / ACTIVE_ON_PROMOTION` to durable `PASS / ACTIVE`, preserving V39 activation evidence and the V41 effectiveness gate. No new learning is introduced.

Expected aggregates remain backlog=0, unresolved ineffective=0, pending measurement=1, overdue=0, historical ineffective=3.

## Promotion contract

R8 detailed review and A8 holistic audit must target the same exact final V40 SHA. The reviewed/audited tree must not contain the R8/A8 verdict files. Promotion may add only those two immutable verdict blobs to the exact target and must be followed by post-promotion CI.