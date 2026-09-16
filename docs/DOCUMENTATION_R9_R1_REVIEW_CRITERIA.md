# DOCSYS-V2-R9 Correction R1 — detailed review criteria

1. The only executable governance behavior change is adversarial-test fixture isolation; lifecycle checker semantics are unchanged from promoted R9.
2. Promotion-simulation tests derive current release/verdict IDs/paths from `PROJECT_STATE` instead of hard-coding R1 paths.
3. Each partial/mismatched promotion scenario removes ambient current verdict files inside its temporary copied fixture before adding simulated verdicts.
4. The identical adversarial suite passes on an already-promoted R9 repository and still rejects partial/mismatched promotion states.
5. Promotion CI failure `35089621367` is preserved in immutable health/learning evidence and not rewritten away.
6. `LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003` is registered and evidence-gated; its activation depends on R2 review/audit.
7. Previously promoted `LEARNING-LIFECYCLE-CONSISTENCY-002` transitions to evidence-backed ACTIVE using immutable R1 review/audit + V33 evidence.
8. State V34 derives learning aggregates: pending activation 0, unresolved ineffective 0, pending measurement 2, overdue measurement 0.
9. R1 review/audit records remain immutable historical evidence; correction uses new R2 review/audit IDs and paths.
10. No Phase00 source/native/test-oracle changes occur and `RUN-P00-VALIDATION-001/V02` remains unchanged.
11. Exact correction design CI must PASS all five portable governance steps before R2 review verdict.
12. Post-correction promotion must add only predeclared R2 review/audit verdict records and post-promotion CI must PASS on main.
