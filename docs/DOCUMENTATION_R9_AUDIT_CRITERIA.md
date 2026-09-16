# Documentation R9 holistic audit criteria

Audit the entire active control plane, not only changed files. Confirm:

- learning observation/provenance and current lifecycle status have distinct canonical owners with no circular trust;
- every active durable learning is registered exactly once and project learning aggregates are checker-derived;
- no stale pre-R9 activation/review snapshot can override `learning/LEARNING_STATE.json`;
- active learning has immutable activation evidence; promotion-conditional learning predeclares exact final review and audit evidence paths;
- current-release pending activation, ineffective-without-successor and lifecycle-state drift are fail-closed conditions;
- guarded automation detects/reconciles/calculates due-state/routes but cannot author its own independent review/audit verdict or promote itself;
- session bootstrap executes learning lifecycle reconciliation before health/routing decisions;
- effectiveness evidence is required before a learning is called effective;
- structured `measurement_gate` distinguishes pending measurement from overdue measurement, and only due-without-evidence becomes automatic measurement debt;
- promotion-ready V33 reports pending measurement 1 but overdue measurement 0; the new R9 successor is scheduled for V36 unless earlier inconsistency triggers review;
- historical ineffectiveness remains evidence even after an active successor closes current unresolved debt;
- `POL-LEARN-002` is the only active learning lifecycle policy and `POL-LEARN-001` is clearly superseded;
- documentation checker/audit logic invokes the lifecycle checker rather than checking policy keywords only;
- adversarial tests demonstrate stale activation, ineffective-without-successor, aggregate drift, missing effectiveness/activation evidence and overdue measurement drift fail closed;
- policy growth does not create duplicate mutable state owners (`PROJECT_MEMORY`, immutable learning records, lifecycle register and PROJECT_STATE each have distinct roles);
- continuity/source-visibility/test/governance R8 protections remain intact;
- exact current validation run/blocker is preserved and documentation work does not create or advance native authority;
- promotion-ready `PROJECT_STATE`/checkpoint predeclare final review/audit IDs/paths and post-audit promotion permits no other policy/state/checker mutation;
- final promotion changes no Phase00 source behavior, code-review verdict, LAB/SITE evidence, qualification or HOST_READY.
