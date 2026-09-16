# Learning Evidence and Lifecycle State

`LEARNING-<scope>-<nnn>.md` files are immutable reusable-learning evidence/provenance: observation, root cause, evidence, reusable rule, score, proposed correction and success metric.

Current review/activation/effectiveness status is **not** owned by those immutable records after creation. The single machine-readable lifecycle owner is:

- `learning/LEARNING_STATE.json`

This separation prevents a historical learning record from remaining `PENDING_ACTIVATION` after its policy was promoted, or from being silently treated as effective without measurement.

`PROJECT_MEMORY.md` is only the compact active lesson index. `PROJECT_STATE.md` carries derived aggregate learning debt, which must equal the lifecycle checker result.

Every fresh session and DOC-AUDIT runs `tools/check_learning_lifecycle.py`. Historical pre-R9 activation/review fields inside older learning records are evidence snapshots, not current authority.

Superseded/retired learning remains available through its immutable record and Git history; its lifecycle register entry names the successor when applicable.
