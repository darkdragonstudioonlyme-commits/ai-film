# Phase00 dev21 — LAB artifact seal

```yaml
SEAL_ID: LAB-ARTIFACT-SEAL-P00-DEV21-001
CANDIDATE_ID: 336b12af-cada-4968-8083-8a5b41e479a2
SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
PENDING_BUNDLE_INDEX_SHA256: fa38540df54df9ebb87929c43e9fe8fbcd09e290e93d8c5d53d7af991df8f615
SEAL_SHA256: 97051c1e9286e5d65cbc78feef1943ed3e312e45638cd2f256df2ef62000e6ec
VERIFIER_SHA256: 769ec4e3c8c85cd78105c1466d8c854cc87cf362d5c01e80fe4a9d285e09afc8
VERIFIER_STATUS: PASS
ARTIFACT_COUNT: 6
ALL_ARTIFACTS_READ_ONLY: true
NATIVE_EXECUTION_STARTED: false
```

## Sealed artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `AI-FILM-P00-DEV21_APP.sha256` | 30,519 | `2282f89da136ca54838379bdae8d9edc4b8e9c6a66770c732d8b3555eb4276f5` |
| `AI-FILM-P00-DEV21_APP.tar` | 6,359,040 | `f0276084ad99906ddeee75b5923704fa0833f17909b7e46dd4c62badd8ee3d06` |
| `AI-FILM-P00-LAB_BASELINE_UBUNTU24.tar.gz` | 491,407,360 | `0b91d4947754be40bdb4fd3d07c8eb452dde1b6bc160829923c8e0ef005dfffd` |
| `AI-FILM-P00-LAB_DEV21_PRISTINE.tar.gz` | 499,660,800 | `552d6cf0ec7158ebebc5385f7dfeb7b0b3216f3536d2915877bc9425ad02127d` |
| `LAB_AUTHORITY_DRAFT-P00-DEV21.json` | 63,056 | `746a2939d2b8983a952dcedf69ff173cc05f458ac7032a7001aff96c911450b5` |
| `LAB_CANDIDATE_TECHNICAL_FACTS.json` | 1,743 | `bca858e356faa2430a04ca2c8a069d02f3f4468927b130ef5a860fa844ecec79` |

The seal manifest and every listed artifact are mode `0400`. `verify-lab-artifact-seal.py` recomputes streaming SHA-256, byte sizes, candidate/source/bundle bindings, restore-probe state and write-bit absence. The full verification passed after sealing.

This is integrity preparation only. It does not approve the pending authority bundle, install an HKLM trust anchor, start the stopped LAB, execute any native case, or issue qualification/HOST_READY.
