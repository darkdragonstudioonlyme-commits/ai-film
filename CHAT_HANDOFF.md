# New Chat Handoff — AI-FILM-SERVER

Use `darkdragonstudioonlyme-commits/ai-film` as the persistent control plane; do not depend on transcript history.

Fresh-fetch relevant refs, then follow the cold-start order in `README.md`. Run `/usr/bin/python3 tools/run_governance_checks.py` when the prepared WSL workspace is available.

When the user says `continue`, use `WORKFLOW_ROUTER.md`. Preserve documented WIP. Do not ask the user to restate context already present in state/work-item/lane records.

Testing follows `TEST_STRATEGY.md`: business/contracts/review evidence define oracles; current code never defines expected behavior. Classify a failure before changing code or tests.

If work repeatedly fails, stalls, becomes inefficient or the user says it is wrong/off-requirement, apply `SELF_LEARNING_SYSTEM.md` before another blind retry. Persist useful learning and promote recurring rules into policy/tooling.

Material documentation governance uses three independent workflows: DOC-DESIGN → DOC-REVIEW → DOC-AUDIT. Source implementation/review remains independently isolated.

Do not infer native validation, qualification, model-evaluation readiness or HOST_READY from author tests, documentation checks or review labels.
