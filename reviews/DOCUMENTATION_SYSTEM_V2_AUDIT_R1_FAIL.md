# Documentation System V2 — Holistic Audit R1

```yaml
AUDIT_ID: DOC-V2-AUDIT-R1
TARGET_COMMIT: 4753de63e24977ee2229ad6c3985231ebab1dc3e
PREREQUISITE_REVIEW: DOC-V2-REVIEW-R2 / PASS
AUDIT_BRANCH: lane/docs-audit-v2
SOURCE_MODIFIED_DURING_AUDIT: false
VERDICT: FAIL
```

## Audit method

DOC-AUDIT-V2 checked out detached exact candidate `4753de63...`, verified the detailed-review record targets the same commit, ran all governance/static checks, fresh-fetched runtime state, and then inspected the entire active control plane plus actual prepared WSL entrypoints. It intentionally did not trust the prior PASS.

## Findings

### D2A-F01 — HIGH — legacy `test.sh` bypasses the business-governed test workflow

Actual `/home/dragon/ai-film-dev/test.sh` still executes `/home/dragon/ai-film-dev/lane-test.sh implement` directly. The V2 policy names `tools/run_test_workflow.py` as the canonical business/test-contract wrapper and correctly describes `lane-test.sh` as a low-level executor.

**Impact:** a normal/familiar test entrypoint bypasses test-contract authority, lane/environment preflight and knowledge/runtime checks. Policy is therefore not enforced at the real workspace boundary.

**Required fix:** make the legacy/default workspace entrypoint delegate to the canonical wrapper; add a reviewed sync/install mechanism and runtime check that detects helper drift. Keep `lane-test.sh` as an explicit low-level executor only.

### D2A-F02 — HIGH — `FULL_COMMAND` overclaims what it executes

`NEXT_WORK_ITEM.md` says `FULL_COMMAND: python3 tools/run_test_workflow.py docs` and `PASS_MEANS` says documentation/control-plane V2 criteria are satisfied. But docs mode runs test-strategy, knowledge, runtime and project-doc checks only; it does not run `tools/audit_control_plane.py`.

**Impact:** the declared full test command can pass while the documented holistic static audit has not run. The test contract therefore overstates its evidence.

**Required fix:** make docs `FULL_COMMAND` execute the full non-recursive control-plane audit suite, or narrow `PASS_MEANS`/rename the command. Prevent recursion between wrapper, governance checks and audit script.

### D2A-F03 — HIGH — obsolete unowned current-looking status document remains at root

`SOURCE_IMPORT_STATUS.md` is a dev6-era persistence-status document with resolved/retired semantics. It is not owned by `DOCUMENTATION_MAP.md`, yet remains at repository root beside current control-plane files. Historical checkpoints are versioned and explicitly historical; this file is not.

**Impact:** a cold chat or tool discovering root Markdown can mistake obsolete dev6 persistence guidance for current state, violating V2 knowledge-pruning and anti-drift goals.

**Required fix:** remove the obsolete root document from the active tree (Git history already preserves it), or move it to an explicitly historical archive. Add a root-document ownership checker: every root MD must be an active mapped document or an allowed immutable checkpoint pattern.

## D2A disposition

D2A-01/02/03/05/06/07/08/09/10/11/12/13 passed in the examined areas, but D2A-04 and D2A-14 fail because of D2A-F03 and the analogous operational bypasses D2A-F01/F02. Overall audit FAIL.

Return to DOC-DESIGN-V2. Detailed review must re-run after the fixes because test/persistence governance changes materially; final audit must then re-run on the new exact candidate.
