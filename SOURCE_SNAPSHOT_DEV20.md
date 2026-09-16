# Dev20 source snapshot

This branch is a browseable, **partial and non-authoritative** source snapshot for the Phase00 dev20 author-complete candidate.

- Exact local source commit: `51c9d3f7373a2922c1ea6a3e973d817bb4e16523`
- Exact package: `IMPL-P00-001_IMPLEMENTATION_PACKAGE_V20.zip`
- Package SHA-256: `8104985b355815d58fbc28fec3e1b9b17c72dbf9d5a9c6dc8f7eb66f77a67fff`
- Package size: `1175249` bytes
- Author checks: 760 tests PASS; 101 static checks PASS
- Native Windows/WSL/LAB/SITE validation: NOT_RUN
- CODE_REVIEW: pending

## Byte-reverified materialized paths

The following GitHub blob identities were independently compared with `git ls-tree` for exact local commit `51c9d3f...` and match:

- `src/aifilm_p00/__init__.py` — blob `7387aaf8c441d76002b918c89bb45594dccc20ab`
- `src/aifilm_p00/native/actuator.py` — blob `c3e131dbe8eec3eafed443301fad022177755512`
- `tests/test_dev20_factory_integration.py` — blob `508a12e14109c77fbd7815ea6a20c58cf2c9aaa2`

An independent S07 visibility recheck found four earlier manually materialized browse copies did not match the exact local Git blobs (`session.py`, `admission.py`, `native/request_entry.py`, `native/trust.py`). Those copies were removed rather than left as misleading review material.

## Authority boundary

`SNAPSHOT_BYTE_REVERIFY` for the paths that remain materialized is **PASS**. `FULL_SOURCE_GIT_MIRROR=false` remains true. This branch improves browseability only; the immutable candidate authority remains the exact source commit/package identity above. Formal CODE_REVIEW must not infer full-source identity from this partial snapshot.
