# AI-FILM-SERVER — Source Import Status

## Status: RESOLVED FOR CROSS-CHAT RECOVERY

The one-time persistence blocker for `0.1.0.dev6` is resolved using a **verified hybrid persistence model**:

- **GitHub repository** `darkdragonstudioonlyme-commits/ai-film` is the canonical state, memory, workflow and commit ledger.
- **Google Drive raw artifact** is the byte-preserving recovery anchor for the exact dev6 implementation package.

This distinction is intentional. Do not claim that the complete dev6 source tree is already materialized as ordinary GitHub source files; the exact binary delivery is durable and recoverable, while future source increments should be committed to Git whenever byte-preserving Git writes are available.

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

Verification procedure actually performed:

1. Upload local V6 ZIP through Google Drive's file-reference upload path, which transfers file bytes rather than rendering them as model text.
2. Fetch/download the stored Drive file again as raw bytes.
3. Recompute SHA-256 on the downloaded artifact in the current runtime.
4. Compare to the original verified V6 SHA-256.
5. Result: **exact match**.

Therefore a future chat with the connected Google Drive plugin can recover the exact dev6 delivery by file ID and verify the same SHA before extraction.

## Persistence state

```yaml
EXACT_DEV6_DELIVERY_DURABLE: true
SOURCE_RECOVERY_VERIFIED: true
IMPLEMENTATION_MAY_RESUME: true
GITHUB_STATE_PERSISTENCE: true
GITHUB_FULL_DEV6_SOURCE_TREE_MATERIALIZED: false
DRIVE_BINARY_RECOVERY_ANCHOR: true
PERSISTENCE_BLOCKER: RESOLVED
DESIGN_GAP: false
VALIDATION_FAILURE: false
CODE_REVIEW_FINDING: false
```

`EXACT_DEV6_SOURCE_MIRRORED` is retired because it incorrectly implied that durability requires the full tree to live only in GitHub. The project now distinguishes:

- **source/delivery durability** — satisfied by an exact byte-verified artifact;
- **Git current-state durability** — satisfied by the repository Markdown/state ledger;
- **Git source-tree materialization** — desirable and required for normal code-review/diff workflows, but not a reason to lose or reconstruct an exact baseline.

## Recovery procedure for a new chat

1. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, `PROJECT_MEMORY.md`, and `GIT_WORKFLOW.md`.
2. Fetch Drive file ID `1nYtbxJ3p0A0Oo_QyYgAc3zdyLbQYCSc4` as raw bytes.
3. Verify size `1178410` and SHA-256 `41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e`.
4. Extract into a fresh workspace.
5. Verify the package manifest/source identities before modification.
6. Continue only the work recorded by `NEXT_WORK_ITEM.md`.

Never reconstruct dev6 from prose if this exact artifact is available.

## GitHub connector lesson

During bootstrap, text-oriented and large base64 payload paths were tested. Git blob uploads were byte-stable at a small payload but larger model-rendered payloads were not reliable enough for a one-time 1.18 MB archive. Experimental incorrect trees were removed rather than accepted.

The reusable lesson is recorded in `PROJECT_MEMORY.md`: use **file-reference/raw-file connectors for binary artifacts**, and use GitHub for source/state commits that can be independently verified.

## Future delivery rule

For every coherent implementation increment:

```text
work on exact recovered/current source
→ targeted tests
→ delivery-boundary regression/static checks
→ Documentation Sync Gate
→ diff review + secret scan
→ persist exact delivery artifact to byte-preserving store when a binary package is produced
→ commit/push GitHub state/source/diffs that can be verified
→ verify remote Git commit and artifact hash
→ only then start the next increment
```

Before CODE_REVIEW, the exact candidate must be addressable by a Git commit and/or exact artifact identity sufficient for the reviewer to review the same bytes. Any source-tree materialization still missing must be resolved before declaring `CODE_REVIEW_HANDOFF_READY=true`.

## Security

The Drive artifact is currently not shared publicly. The GitHub repository was public at bootstrap, so do not commit credentials, private keys, tokens, private licensed assets or customer data. Synthetic test canaries are not credentials but should remain labeled as fixtures.
