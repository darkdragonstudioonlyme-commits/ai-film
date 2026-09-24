# Continuity Ledger

Machine source: projects/<id>/continuity.json.
Identity is separated from costume, hair, emotion, injury, prop and location state.
Timeline entries are ordered by story time. state_at(character,time) folds events through the requested point.
Intentional changes are events; unrecorded differences in generated output are drift.
Supported initial events: costume, hair, emotion, location, injury add/update/remove, costume damage, prop add/remove.
Acceptance: compiler can reconstruct the expected state for every benchmark shot and tests cover persistence across shots.
