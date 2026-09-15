# AI-FILM-SERVER — WSL Development Workspace

Current prepared environment for independent IMPLEMENT and REVIEW execution lanes.

## Identity

```yaml
DEVICE: DESKTOP-LCISMET
WSL_DISTRO: Ubuntu 24.04.4 LTS
USER: dragon
WORKSPACE_ROOT: /home/dragon/ai-film-dev
BASE_DELIVERY: 0.1.0.dev8
```

## Layout

```text
/home/dragon/ai-film-dev/
├── repo/                 # clone of canonical GitHub main/state
├── source-dev8/          # immutable exact dev8 recovery baseline
├── source-dev7/          # immutable dev7 rollback baseline
├── implement/            # writable source worktree, branch impl/p00
├── review/               # detached exact review candidate worktree
├── artifacts/            # exact delivery ZIPs
├── run-evidence/
│   ├── implement/        # IMPLEMENT author evidence
│   └── review/           # REVIEW rerun/scenario evidence
├── .venv/                # isolated Python 3.12 no-pip environment
├── implement-env.sh
├── review-env.sh
├── lane-test.sh
├── env.sh                # compatibility alias → IMPLEMENT
└── test.sh               # compatibility alias → IMPLEMENT tests
```

## Source identities

Immutable dev8 baseline:

```text
/home/dragon/ai-film-dev/source-dev8
branch: dev8-baseline
commit: c44c2f87084f8082ce29af5935c6b47d03f7b96c
package SHA-256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
```

IMPLEMENT lane:

```text
/home/dragon/ai-film-dev/implement
branch: impl/p00
initial commit: c44c2f87084f8082ce29af5935c6b47d03f7b96c
```

REVIEW lane:

```text
/home/dragon/ai-film-dev/review
detached HEAD: c44c2f87084f8082ce29af5935c6b47d03f7b96c
candidate: exact dev8
last verdict: FAIL
```

The REVIEW worktree does not follow `impl/p00`. A new candidate must be handed off explicitly and REVIEW must be reset/recreated at that exact commit.

## Enter a lane

IMPLEMENT:

```bash
source /home/dragon/ai-film-dev/implement-env.sh
```

REVIEW:

```bash
source /home/dragon/ai-film-dev/review-env.sh
```

Both use the isolated `/home/dragon/ai-film-dev/.venv`. Current package dependencies are empty; the no-pip venv remains valid only while that remains true.

## Run lane verification

```bash
/home/dragon/ai-film-dev/lane-test.sh implement
/home/dragon/ai-film-dev/lane-test.sh review
```

At lane creation both independently reproduced:

```text
683 workspace tests PASS
92 static checks PASS
source digest e793fc78d622c987343d1b5e5d3909cb4c19d7b0bcbafbc32909f137a1894c08
test digest   f91b422b6ce4ffeee9fc516bff0dc00c8e4a6216ae98e94b977ac2ef00949021
```

`lane-test.sh` stores actual outputs under `run-evidence/<lane>/<UTC timestamp>/`, restores tracked generated evidence before exit, and prints final Git status only after restoration. Verification-only runs must leave each worktree clean.

These results are author/review workspace evidence only, not native Windows/WSL/LAB/SITE proof.

## Canonical repo and remote lane branches

```text
canonical clone: /home/dragon/ai-film-dev/repo
main: canonical global state/gates
lane/implement-p00: IMPLEMENT operational state
lane/review-p00: REVIEW operational state
```

Direct WSL HTTPS push remains unauthenticated. Local source Git is used for diff/commit/rollback; connected GitHub tools persist remote state/lane records. Do not write PATs/tokens to plaintext files.

## Lane safety

- IMPLEMENT may edit `/implement`; REVIEW must not.
- REVIEW source is detached/frozen to the candidate identity.
- Do not run formal review against uncommitted `/implement` changes.
- Do not copy implementation fixes into `/review` during review.
- Candidate exchange is by exact commit/package identity only.
- Neither lane may run native Windows/WSL/LAB/SITE provisioning/validation during current authoring unless a later authorized work item explicitly changes that.

## Future-chat startup

1. Read `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, `EXECUTION_LANES.md`.
2. Choose IMPLEMENT or REVIEW from the requested task.
3. Read that remote branch's `LANE_STATE.md`.
4. Pull `/home/dragon/ai-film-dev/repo` and verify `main`.
5. Check Git status of the selected local worktree.
6. Run the selected lane test helper when appropriate.
7. Keep permissions isolated and persist reusable discoveries via Documentation Sync Gate.
