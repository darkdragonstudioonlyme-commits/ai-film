# Batch 017 — spec transport, schema compatibility and readiness DAG

T-053 spec transport:
- exports only the files already approved by production_spec_package;
- bundle manifest and every payload file are hash/size bound;
- symlinks, extra files, path traversal, runtime/compiled/delivery/generated/binary/secrets paths are rejected;
- import verifies the entire bundle before creating destination files and carries no execution/publication authority.

T-054 schema compatibility:
- current version is v1;
- slice01 explicitly reports four legacy-v0 shapes: project, casting, continuity and raw-list shots;
- upgrade plans are dry-run by default; mutation requires explicit authorized=True;
- future/unknown schema versions fail UNSUPPORTED rather than silently coercing.

T-055 stage readiness:
- deterministic DAG derives COMPLETE/READY/BLOCKED from evidence and upstream dependencies;
- current project has NO_RUNNABLE_STAGE;
- blocking frontier is exactly casting_reference_generation + voice_eval, both missing paid_gpu_authorized;
- setting paid authority in a synthetic test makes those stages READY but never execution_permitted.
