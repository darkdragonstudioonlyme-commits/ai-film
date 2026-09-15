# Immutable Environment Records

Each `ENV-*.md` record contains an exact canonical JSON payload, its SHA-256 digest, measurement provenance and limitations. Records are immutable once referenced by a model evaluation.

`SERVER_ENVIRONMENT.md` owns methodology and the current development-environment pointer; it does not accumulate historical snapshots.

New material benchmark environment => new environment record/ID/digest. Do not edit an old record to represent a changed system.
