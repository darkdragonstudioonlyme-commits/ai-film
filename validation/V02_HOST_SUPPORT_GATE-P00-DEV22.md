# Phase00 dev22 — V02/V03 host support gate

GATE_ID: V02-HOST-SUPPORT-GATE-P00-DEV22-001
RUN_ID: RUN-P00-VALIDATION-002
CURRENT_STEP: V02_LOCAL_OPERATOR_LAB_AUTHORITY
OBSERVED_EDITION: Professional
OBSERVED_DISPLAY_VERSION: 23H2
OBSERVED_BUILD: 22631
OBSERVED_UBR: 3296
OBSERVED_AT_DATE: 2026-09-18
PROJECT_SUPPORT_MARGIN_DAYS: 90
STATUS: BLOCKED_USER_WINDOWS_UPDATE
MINIMUM_TARGET: 25H2_OR_LATER_WITH_90_DAY_SUPPORT_MARGIN
AUTHORITY_SUITE_GENERATION: DEFERRED
NATIVE_EXECUTION_STARTED: false

## Evidence

The live host registry was read through the existing private Windows interop from WSL and returned edition Professional, display version 23H2, build 22631, UBR 3296.

Microsoft's current Windows 11 Home/Pro lifecycle identifies 23H2 as out of updates. It lists 24H2 ending in October 2026, which is inside the project's 90-day support margin on 2026-09-18; 25H2 and 26H1 remain beyond that margin.

The exact dev22 policy is stricter than merely being currently serviced: host_profile() requires support_end - now >= 90 days. Native profile matching also requires an exact catalog row for the observed build/release/edition. The authority graph can bind the post-update live facts without product-code change.

## Sequencing decision

Do not create/sign the <=24h V02 suite on the current 23H2 host. Doing so would create ephemeral authority that cannot lead directly into a valid V03 positive run and would need regeneration after the operating-system update.

The user action is intentionally simple: update Windows to 25H2 or later, reboot Windows, and return. After reboot, validation will re-observe exact host facts, build the current authority graph inside WSL, sign it with the already deployed durable local key, and run preflight/intake/pre-V03.

No project policy is weakened and no native case is executed by this gate.
