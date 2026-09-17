# Phase00 dev21 — Windows host control-backup mirror

```yaml
MIRROR_RECORD_ID: WSL-PRODLIKE-HOST-MIRROR-P00-DEV21-001
STATUS: PASS
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
HOST_FILESYSTEM: NTFS
MIRROR_TIMER: "enabled active / 2h"
MIRROR_SERVICE_RESULT: success
MIRROR_SYSTEMD_SECURITY: "4.1 OK"
RETENTION: 14
MIRROR_MAX_AGE_HOURS: 30
LATEST_SAMPLE_ARCHIVE: control-state-20260917T090226Z.tar.gz
LATEST_SAMPLE_SHA256: c213efff4aeff5585bf14efea172889dffe3b33af815dabaf30f3b5e14c887d2
LATEST_SAMPLE_FILE_COUNT: 87
MIRROR_VERIFY: PASS
EVIDENCE_LEDGER_RECOVERABLE: true
RESOURCE_DROPINS_RECOVERABLE: 11
TIMER_DEFINITIONS_RECOVERABLE: 11
EXECUTION_FRESHNESS_HEALTH_RECOVERABLE: true
WINDOWS_ACL_INHERITANCE: disabled
NATIVE_AUTHORITY_INCLUDED: false
PROTECTED_IDENTITY_INCLUDED: false
NATIVE_EXECUTION_STARTED: false
```

The NTFS mirror matches the latest locally verified recovery sample SHA `c213efff...` and contains the current 87-file sample. The count is not a fixed schema invariant because bounded evidence-ledger history is part of recovery state and legitimately rotates.

Stable mirror requirements are: source backup verifies, NTFS bytes rehash to the same archive SHA, retention/freshness limits hold, protected authority/identity domains are excluded, and the restored control set contains the required timer/resource/health/recovery tooling. Current full DR verifies those stable requirements before exact-dev21 reconstruction.

This remains same-host second-filesystem recovery, not binary off-host DR or native execution authority.