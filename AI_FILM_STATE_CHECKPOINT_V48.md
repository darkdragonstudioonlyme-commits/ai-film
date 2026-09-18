# AI-FILM-SERVER — State Checkpoint V48

Phase00 product/native state remains unchanged: exact dev21 source `934659f535d81d9a4a07389531acc2b9c304fa6d` is CODE_REVIEW_PASS and remotely browseable; validation evidence head remains `cf819edd0e05ffd8afd4bc2051116d5a4392368b`; `RUN-P00-VALIDATION-001` remains BLOCKED at V02; all 86 native cases remain NOT_RUN.

## Documentation CI credential isolation

Post-promotion V47 Documentation Governance run `35296390094` / job `105449688523` used the default `actions/checkout@v4` behavior `persist-credentials: true`. The log shows a masked GitHub authorization extraheader stored in local Git config while repository-controlled lifecycle/governance/checker Python executed before post-job cleanup.

V48 sets `persist-credentials: false` on the Documentation Governance checkout and inserts a fail-closed no-extraheader check immediately after checkout, before Python setup and before any repository-controlled checker executes. Workflow token permission remains `contents: read`; no custom token or extra secret is introduced.

The checkout action may use masked authorization transiently while performing its own fetch; the protected boundary is that it must remove that config before returning control to subsequent steps.

The first remote V48 design push produced run `35296591786` with no jobs because the regex command used an invalid YAML double-quoted escape. The command is now expressed as a block scalar; the security predicate is unchanged.

## Reusable learning 013

This is the second independently observed workflow with the same default checkout exposure, after V02 validation CI. V48 therefore generalizes the rule into `LEARNING-CI-CREDENTIAL-ISOLATION-013`, predeclared `ACTIVE_ON_PROMOTION / PENDING_MEASUREMENT` under R22/A22. Activation is not effectiveness; a later qualifying CI workflow change or documentation promotion must prove the rule persists.

Continuity learning 001 remains separately PENDING_MEASUREMENT at 0/3 events.

## Current authority

R22/A22 are final verdict identities for this exact V48 semantic tree. Branch role changes verdict-record presence only; the same workflow/state must remain valid after exact fast-forward.
