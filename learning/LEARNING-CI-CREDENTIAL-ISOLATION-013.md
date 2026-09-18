# LEARNING-CI-CREDENTIAL-ISOLATION-013

LEARNING_ID: LEARNING-CI-CREDENTIAL-ISOLATION-013
SCORE: 10
OBSERVED_AT_STATE: V47
TARGET_RELEASE: DOCSYS-V2-R9
CLASS: ci-credential-isolation

## Observation

Two independent CI domains repeated the same default-checkout exposure. Canonical V02 validation CI and Documentation Governance both allowed `actions/checkout@v4` to persist the masked GitHub authorization extraheader in local Git config while repository-controlled Python executed before post-job cleanup. The jobs required only read access and did not need a reusable checkout credential after fetch.

## Generalized learning

Any CI job that executes repository-controlled code after checkout must disable checkout credential persistence, keep token permissions at least privilege, and fail closed if a local `http.*.extraheader` remains before that code runs. Transient masked authorization internal to the checkout fetch is acceptable only when the checkout action removes it before handing control to subsequent steps.

## Success metric

The next qualifying CI workflow change or documentation promotion executes repository-controlled code only after checkout credentials are non-persistent and an explicit no-extraheader check passes; no reviewed workflow reintroduces persisted checkout authorization, while required read-only fetches still succeed.
