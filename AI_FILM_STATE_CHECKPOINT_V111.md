# Prodlike authorization 003 preparation checkpoint
STATE_VERSION: 111
STATUS: AUTHORIZATION_002_EXPIRED_UNUSED_PREPARE_003

Authorization 002 passed review but expired before any transaction-002 receipt root was created or command executed. It is not executable and is not renewed in place. Attempt 1 remains permanently non-replayable. Prepare a new immutable authorization 003 with new hash, transaction id, expiry and receipt root from the current exact baseline. No prodlike/LAB/native/signing/HKLM mutation is authorized during preparation.
