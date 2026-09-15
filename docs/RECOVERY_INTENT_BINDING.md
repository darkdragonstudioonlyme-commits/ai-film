# Recovery intent binding — implementation detail in existing refs

The reviewed `verify` / `RECONCILIATION_ONLY` purpose is preserved. Its semantic `refs` may name `recovery_request`, consumed through the same role/digest-pinned store as the other request artifacts. Omission keeps the existing RECONCILE default. No standalone unsigned CLI flag authorizes a diagnostic/pause/cancel operation.

Required fields are `schema_version: 1`, `withdrawn: false`, a mode in DIAGNOSE/RECONCILE/PAUSE/CANCEL, and an exact scope with host_id, owner_sid, original_plan_digest and original_fence_digest. Fixture-marked content is rejected. These fields select intent only and must be bound by the normal plan approval and trusted artifact store.

The request does not assert writer absence, permission revocation or completion. The native observer measures those facts and separately consumes current authenticated, raw-measurement-supported `run_revocation` proof for PAUSE/CANCEL or postcondition evidence for reconciliation. A request created before the fence changes must be renewed and rebound; the old original plan is never edited.

Raw diagnostic evidence is protected and capped. The public result contains safe status/digests, original and request identities, fence-retention state, and explicit false gate/qualification values. SAFE_PAUSE/CANCEL returns 20 and never creates completed mutation progress.

This document describes code in a partial source drop. It does not create the real approvals, registrations, revocations, observations or qualifications required to execute it.
