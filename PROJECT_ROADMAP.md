# AI-FILM-SERVER — Project and Control-Plane Roadmap

## Product roadmap

```text
requirements/frozen decisions
→ reviewed Phase00 design
→ Phase00 implementation source/harness closure
→ formal CODE_REVIEW
→ native VALIDATION
→ qualification/gate assessment
→ HOST_READY when evidence supports it
→ later platform/model/data/workflow phases through the same state machine
```

Each node advances only through its exit gate; a lower-level PASS never promotes the next node automatically.

## Continuous control-plane roadmap

The documentation/testing/learning system evolves alongside product work:

```text
state persistence
→ independent source review
→ deterministic routing
→ business-first test governance
→ self-learning + deadlock retrospectives
→ knowledge pruning
→ environment/model-evaluation identity
→ periodic holistic governance audit
```

Material governance changes use DOC-DESIGN → DOC-REVIEW → DOC-AUDIT.

## Model-evaluation future node

When project scope reaches model evaluation/selection, first satisfy `SERVER_ENVIRONMENT.md` readiness. Benchmark campaigns bind model identity + environment fingerprint + run parameters + performance/quality evidence. Do not compare results across unidentified environments.

## Roadmap maintenance

Roadmap owns milestone order/exit criteria, not current dev version or dirty files. Current position belongs to `PROJECT_STATE.md` and exact executable work to `NEXT_WORK_ITEM.md`.
