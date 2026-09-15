# IMPL-P00-001 — Delivery dev8

```yaml
DELIVERY: 0.1.0.dev8
STATUS: PARTIAL_SOURCE_DROP_DEV8
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
WORK_ITEM: IMPL-P00-001
AUTHOR_COMPLETE: false
CODE_REVIEW_HANDOFF_READY: false
```

## Exact artifact

```text
Package: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V8.zip
Drive file ID: 125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD
Size: 1091121 bytes
SHA-256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
source_diff.patch SHA-256: c9c519dc4bb0cc99135ffdd6884f31a573bbd191f9141ac9ad2484a4b030560e
```

The Drive artifact was uploaded by file reference, downloaded again as raw bytes, and the size/SHA-256 matched the local package exactly. A duplicate upload created during persistence was deleted; the file ID above is the only canonical dev8 anchor.

## Increment

Dev8 hardens reviewed C3 lifecycle and operator-wait behavior without changing Phase00 plan operations or public contracts:

- a native `ENABLE_PREREQUISITES` / `INSTALL_RUNTIME` process that exits normally cannot continue when current Windows observations show a pending reboot; the step retains `AWAITING_REBOOT/20`;
- an existing `3010 → AWAITING_REBOOT` result remains a wait and is not overwritten;
- reconciliation of a reboot wait requires a changed host boot witness and all observed pending-reboot indicators cleared before the original step can commit;
- post-reboot completion of C3 actions consumes affected-resource postchecks before terminal commit;
- missing owner postcondition evidence may retain/relabel only an existing operator-wait fence as `AWAITING_OWNER_VERIFICATION/20`; it never replays mutation or turns an arbitrary `UNCERTAIN` state into an owner wait;
- OOBE owner-wait does not invent reboot semantics unless it originated from a reboot wait;
- the reviewed final `AWAIT_OWNER_RESTART` step is intentionally retained because Design V2/T00-05 requires an owner-planned host restart lifecycle; dev8 does not deduplicate it with an earlier engine reboot.

## Author evidence

```text
Targeted dev8 lifecycle tests: 10 PASS
Full workspace regression:      683 PASS / 0 failure / 0 error / 0 skip
Static checks:                  92 PASS / 0 failed
Source digest: e793fc78d622c987343d1b5e5d3909cb4c19d7b0bcbafbc32909f137a1894c08
Test digest:   f91b422b6ce4ffeee9fc516bff0dc00c8e4a6216ae98e94b977ac2ef00949021
```

These are author/workspace results only. Windows/WSL native execution, LAB, SITE, qualification, CODE_REVIEW and HOST_READY remain NOT_RUN / NOT_PERFORMED / NOT_EVALUATED as applicable.

## WSL recovery

Exact dev8 is restored at:

```text
/home/dragon/ai-film-dev/source-dev8
local baseline branch: dev8-baseline
local baseline commit: c44c2f87084f8082ce29af5935c6b47d03f7b96c
```

`/home/dragon/ai-film-dev/test.sh` targets dev8 and reproduces 683 PASS + 92 static while preserving actual run evidence under `run-evidence/` and restoring tracked generated evidence to keep the source baseline clean.

## Remaining

`IMPL-REM-01…08` remain OPEN at full-item scope. The next coherent increment is prior pre-C3/checkpoint provenance selection plus nested cross-stage E00 semantics. No code-review or phase-gate promotion is implied by this delivery.
