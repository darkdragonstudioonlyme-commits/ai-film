# AI-FILM-SERVER — Source Import Status

## Purpose

This file prevents a new chat from confusing **repository persistence state** with **implementation state**.

The GitHub repository has been initialized and contains the canonical cross-chat handoff files, but the exact implementation delivery `0.1.0.dev6` has **not yet been accepted as a byte-identical source mirror in GitHub**.

## Verified implementation delivery outside Git

```text
Work item: IMPL-P00-001
Delivery: 0.1.0.dev6 / PARTIAL_SOURCE_DROP_DEV6
Package name: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip
Package SHA-256:
41f8a4ed1d80b87bc84981c3cdb2254a3fbc33f21b822580d7e0788b7b404f7e
Workspace tests: 666 PASS / 0 failure / 0 error / 0 skipped
Static checks: 88 PASS
Author complete: false
Code review: NOT_PERFORMED
Native Windows/WSL: NOT_RUN
LAB/SITE: NOT_RUN
HOST_READY: NOT_EVALUATED
```

The old chat/session had a local copy of this verified package. A future chat must **not invent or reconstruct the source from prose** if the package/source has not yet been seeded into Git.

## What happened during repository bootstrap

GitHub connector access was successfully established for repository:

```text
darkdragonstudioonlyme-commits/ai-film
branch: main
```

The repository was initialized and the detailed state/handoff files were committed successfully.

Two methods were tested for importing the exact dev6 source:

1. Base64/chunked archive through the text-oriented connector.
2. Direct source text mirroring through Git tree/content operations.

Both approaches were checked against local Git-blob/SHA identities. At least one file/blob in each experimental path failed byte-identity verification. The experimental `src/` and `snapshots/` trees were therefore removed from `main` rather than being left as a misleading baseline.

The cleanup is deliberate. **Wrong bytes in Git are worse than an explicit missing-source blocker.**

## Current source-mirror state

```yaml
EXACT_DEV6_SOURCE_MIRRORED: false
SOURCE_IMPORT_VERIFIED: false
IMPLEMENTATION_MAY_RESUME: false
BLOCKER_KIND: REPOSITORY_PERSISTENCE
DESIGN_GAP: false
VALIDATION_FAILURE: false
CODE_REVIEW_FINDING: false
```

This blocker is not evidence that the implementation is missing those components. The implementation exists in verified dev6; the blocker is that the exact bytes have not yet been persisted through a trustworthy Git/file path.

## Required resolution

Before additional implementation is authored, seed the exact dev6 working tree/package through a path that preserves bytes and can be verified, for example one of these:

1. A locally authenticated Git client (`git clone/add/commit/push`) on a connected machine.
2. A GitHub upload/action that accepts an actual file object rather than re-rendering its contents as model text.
3. User seeds the exact `IMPL-P00-001_IMPLEMENTATION_PACKAGE_V6.zip` or extracted dev6 tree into this repository once; ChatGPT then verifies the remote hashes before continuing.

Do not use copy/pasted reconstructed source as the canonical baseline unless **every file** is verified against the local dev6 manifest/blob identity.

## Verification required after source seed

The next chat/session must verify all of the following before changing code:

- repository and branch are correct;
- the seeded source corresponds to `0.1.0.dev6`;
- the original package SHA-256 is recorded and, if the archive itself is stored, matches exactly;
- source file hashes/manifest match the dev6 delivery evidence;
- no experimental/abandoned source is being used;
- author regression baseline remains 666 PASS and static baseline 88 PASS, or any environment-specific inability to rerun is explicitly recorded;
- current mode remains IMPLEMENTATION and current work item remains `IMPL-P00-001`.

Only after exact source persistence is verified should `PROJECT_STATE.md` be changed to:

```yaml
EXACT_DEV6_SOURCE_MIRRORED: true
IMPLEMENTATION_MAY_RESUME: true
```

## Git persistence rule after this one-time seed

After the exact baseline is seeded, do not repeat this bootstrap problem. All future implementation should operate on the Git working tree/repository itself:

```text
read current remote state
→ implement one coherent part
→ targeted tests
→ full author regression for delivery boundary
→ update state/docs/evidence
→ diff review + secret scan
→ commit
→ push
→ verify remote SHA
→ update canonical state if needed
→ next coherent part
```

The source commit/push happens before starting the next coherent implementation increment.

## Security note

The repository was public at initialization. No real credentials may be stored. A bootstrap secret scan of the dev6 package found only synthetic test canaries/token-pattern fixtures, not a private key, GitHub token, or AWS access key. Treat that scan as bootstrap evidence only; repeat secret scanning before every delivery commit.
