# AI-FILM-SERVER — Historical Source Import / Recovery Status

## Scope

This file records the one-time dev6 recovery/persistence incident. It is **not current source-visibility or CODE_REVIEW handoff policy**. Current persistence/addressability rules are owned by `GIT_WORKFLOW.md`; current candidate/source-visibility facts are owned by `PROJECT_STATE.md` and the owning lane state.

## Status: RESOLVED FOR CROSS-CHAT RECOVERY

The one-time persistence blocker for `0.1.0.dev6` was resolved using a verified hybrid persistence model:

- GitHub repository `darkdragonstudioonlyme-commits/ai-film` is the canonical state/memory/workflow ledger.
- Google Drive raw artifact is the byte-preserving recovery anchor for the exact dev6 implementation package.

Do not claim that the complete dev6 source tree is materialized as ordinary GitHub source files. The exact historical binary delivery is durable/recoverable; current source visibility must be read from current state, not inferred from this dev6 record.

## Exact dev6 recovery anchor

```yaml
WORK_ITEM: IMPL-P00-001
DELIVERY: 0.1.0.dev6 / PARTIAL_SOURCE_DROP_DEV6
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip
PACKAGE_SIZE_BYTES: 1178410
PACKAGE_SHA256: 41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
DRIVE_FILE_ID: 1nYtbxJ3p0A0Oo_QyYgAc3zdyLbQYCSc4
DRIVE_MIME_TYPE: application/zip
DRIVE_SHARED: false
RAW_UPLOAD_SUCCESS: true
RAW_DOWNLOAD_REVERIFIED: true
DOWNLOADED_SIZE_BYTES: 1178410
DOWNLOADED_SHA256: 41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
```

Verification performed at the time:

1. Upload V6 ZIP using a raw/file-reference transfer path.
2. Download the stored file again as raw bytes.
3. Recompute SHA-256.
4. Compare with the original V6 SHA-256.
5. Exact match.

## Historical persistence state

```yaml
EXACT_DEV6_DELIVERY_DURABLE: true
SOURCE_RECOVERY_VERIFIED: true
IMPLEMENTATION_MAY_RESUME: true
GITHUB_STATE_PERSISTENCE: true
GITHUB_FULL_DEV6_SOURCE_TREE_MATERIALIZED: false
DRIVE_BINARY_RECOVERY_ANCHOR: true
PERSISTENCE_BLOCKER: RESOLVED
```

The historical lesson remains valid: durability of exact bytes, canonical state persistence and source-tree browseability are separate properties.

## Recovery procedure for the dev6 anchor

If dev6 itself must be recovered:

1. Verify the raw artifact ID/size/SHA above.
2. Extract into a fresh workspace.
3. Verify package manifest/source identities before modification.
4. Route current work using current `PROJECT_STATE.md` / `NEXT_WORK_ITEM.md`; never use this historical file as a current work cursor.

Never reconstruct dev6 from prose if the exact artifact is available.

## Current-policy pointer

For any current/future implementation candidate, follow `GIT_WORKFLOW.md`:

- exact source/package identity is mandatory;
- remote source addressability/visibility is declared explicitly;
- a partial review snapshot is labeled non-authoritative;
- full Git source materialization is preferred when tooling permits because it improves diff/review ergonomics;
- `CODE_REVIEW_HANDOFF_READY` is determined by the current reviewed handoff policy/state, not by this historical dev6 record.

## Security

The historical Drive artifact is not public. The GitHub repository is public, so never commit credentials, private keys, tokens, private licensed assets or customer data. Synthetic test canaries must remain labeled as fixtures.
