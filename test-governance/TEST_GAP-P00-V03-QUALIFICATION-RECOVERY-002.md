# TEST_GAP-P00-V03-QUALIFICATION-RECOVERY-002

TEST_GAP_ID: TEST_GAP-P00-V03-QUALIFICATION-RECOVERY-002
RUN_ID: RUN-P00-VALIDATION-002
DISCOVERED_IN_MODE: IMPLEMENTATION
PHASE: 00 — Host / WSL
STATUS: OPEN
BUSINESS_RISK: "Accepted SITE recovery can authorize RECONCILIATION_ONLY without qualification even though approved T14-A/B/C require recovery entry to reject missing, invalid or mismatched qualification."
MISSING_CAPABILITY: "A product authority predicate that applies the approved qualification gate to SITE recovery/reconciliation entry without imposing qualification on LAB evidence generation."
WHY_BLOCKED: "Exact dev22 diagnostic shows DISCOVERY rejects all T14-A/B/C qualification faults as required, while RECONCILIATION_ONLY authorizes all ten reviewed missing/invalid/mismatch variants because its C0 operations make active=false."
TEMPORARY_COVERAGE: "None. Do not weaken the T14 recovery oracle and do not fabricate a fixture that bypasses the actual authorize path."
OWNER_WORKFLOW: WORKFLOW_REVIEW_PRODUCT_CODE_TEST
RETURN_TO: IMPL-P00-V03-AUTHORITY-BINDING-PRODUCER-001
EXIT_CONDITION: "A reviewed product/test change makes every approved T14-A/B/C recovery probe reject with its existing normalized exit before recovery side effects, preserves LAB no-qualification evidence generation, and passes independent code/test review."

## Exact evidence

Machine-readable evidence: validation/evidence/V03-QUALIFICATION-RECOVERY-GAP-20260921/diagnostic.json
SHA256: 0fd73e3290fae0b08f603885e7115ce345e5531805b5874107dd8a8098eba5ed.

The diagnostic uses only the accepted package's explicitly synthetic workspace helper. No host/native operation ran. It evaluates 20 rows: ten reviewed T14-A/B/C qualification fault variants against active DISCOVERY and against SITE RECONCILIATION_ONLY.
All ten DISCOVERY rows block with the approved class: T14-A/T14-B exit 11 and T14-C exit 16. All ten RECONCILIATION_ONLY rows return AUTHORIZED/0.

The source cause is direct: authority.py qualifies SITE only under elif active, while RECONCILIATION_ONLY has only C0 OBSERVE_PENDING_ACTION and therefore active=false. The accepted matrix explicitly requires "apply/active-preflight/active-verify/recovery đều chặn" for T14-A and retains the same qualification validity/scope requirements for T14-B/C.

## Constraint

The already reviewed binding-producer TEST_CHANGE contains an explicit escape clause: if implementation proves accepted product source or harness schema must change, stop and return to WORKFLOW_REVIEW plus the applicable product code/test path. This finding triggers that clause.

Do not resolve this by changing ENTRY_ONLY recipe expectations, deleting the recovery probe, adding a fake native binding, or changing the expected exit set. Product and test authority must be reconciled first.
