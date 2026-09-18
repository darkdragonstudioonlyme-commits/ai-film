# HEALTH_REVIEW-DOCSYS-R9-V48-CI-CREDENTIAL-025

HEALTH_REVIEW_ID: HEALTH-DOCSYS-R9-V48-CI-CREDENTIAL-025
STATE_VERSION: 48
BASE_MAIN_COMMIT: 49a4829c879c5964ecad235c79d504bd6ccfc5d0
OBSERVED_MAIN_CI_RUN: 35296390094
OBSERVED_MAIN_CI_JOB: 105449688523
REPEATED_FINDING_CLASS: CI_CHECKOUT_CREDENTIAL_PERSISTENCE
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Finding

After validation CI credential isolation was promoted, the independent Documentation Governance workflow still used checkout's default `persist-credentials: true`. V47 main logs show the masked GitHub authorization extraheader configured in local Git state and removed only at post-job cleanup, while repository-controlled Python checks run earlier.

This is a recurrence across two workflow domains, not a validation-specific exception. Both jobs need read-only fetches but no reusable GitHub credential after checkout.

## Correction

V48 disables credential persistence in Documentation Governance and adds a fail-closed no-extraheader check immediately after checkout. The check examines config-key presence only and never prints the credential. `contents: read` remains the only declared GitHub token permission.

## Pre-review authoring failure

Initial design run `35296591786` failed before job creation (`jobs=0`). The cause was YAML syntax: the regex command was double-quoted and `\.` is not a valid YAML double-quoted escape. The fix changes only scalar syntax to a block form; `persist-credentials: false` and the no-extraheader predicate remain unchanged. This negative run is preserved rather than hidden.

## Learning disposition

The recurrence creates `LEARNING-CI-CREDENTIAL-ISOLATION-013`: code-executing CI must not inherit persisted checkout authorization after fetch. R22/A22 activate the rule only; effectiveness requires a later qualifying workflow change or documentation promotion and an explicit metric-bound receipt.

## Boundaries

V02 remains externally blocked, 86 native cases remain NOT_RUN, continuity remains 0/3, and platform branch protection remains external/not enforced.
