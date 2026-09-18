# LEARNING-PRODLIKE-SUPERVISION-DEPLOYABILITY-014

LEARNING_ID: LEARNING-PRODLIKE-SUPERVISION-DEPLOYABILITY-014
SCORE: 10
OBSERVED_AT_STATE: V53
TARGET_RELEASE: DOCSYS-V2-R9
CLASS: prodlike-supervision-deployability

## Observation

A live V53 operational audit found the production-like supervision layer absent: none of the eleven documented AI-FILM timers was deployed in the intended user systemd manager. The runtime/control bytes and portable control backups remained intact, but the scheduled health collector could not report its own scheduler's disappearance because that scheduler was part of the missing layer. Recovery also demonstrated that execution identity is semantic: exact runtime verification PASSed as `dragon` and failed as root with `APP_WRITABLE_DRIFT`, so a byte-correct system-scope restore was still the wrong deployment.

## Generalized learning

A supervision plane must not rely on its own scheduled health job as the only proof that the scheduler exists. Reviewed operational controls need a portable, manifest-bound deployable source; explicit execution/scope identity; an independent verifier that can bind backup bytes to deployed units and live timer state; and a recovery procedure that verifies scope and bytes before activation. Wrong-scope recovery attempts are evidence and must be rolled back rather than normalized away.

## Success metric

The next qualifying prodlike supervision deployment or recovery recheck detects missing, wrong-scope, or byte-drifted supervision before READY_NON_NATIVE_PRODLIKE_OPERATIONS is claimed; verification independently binds a manifest-backed portable control backup to the deployed unprivileged user-systemd files and live timer states without relying on the health timer itself; and recovery preserves V02/native authority boundaries.
