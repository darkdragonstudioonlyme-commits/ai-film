# AI-FILM-SERVER — active state v2

PROJECT: AI-FILM-SERVER
STATE_VERSION: PRODUCT_V2_001
STATUS: ACTIVE
CURRENT_PHASE: "Vertical Slice 01"
CURRENT_MODE: PRODUCT_BUILD
CURRENT_TASK: "T-010..T-012 — model pinning + CPU TTS + rental proposal"
CURRENT_WORK_STATUS: READY
HOST_READY_PRACTICAL: PASS
FILM_CORE_TESTS: "22 PASS / 0 fail"
BENCHMARK_SHOTS_COMPILED: 8
MODEL_EVAL_HARNESS: "DRY_RUN_PASS_EXECUTION_GATED"
SLICE01_TIMING: "75.0s_EN_ZH_VI_PASS"
ANIMATIC_SMOKE: "PASS_9X16_16X9_AUDIO"
ACTIVE_ROUTER: CONTINUE_PROTOCOL.md
ACTIVE_BACKLOG: BACKLOG.yaml
ACTIVE_RESUME: RESUME.md
ACTIVE_MILESTONES: MILESTONES.md
ACTIVE_LEARNINGS: FILM_LEARNINGS.md

PRODUCT_TARGET:
- 60–90 second original short
- master 9:16 with 16:9 reframe/render path
- EN/ZH/VI dialogue/subtitles
- photoreal and 3D style candidates benchmarked before selection

HISTORICAL_P00:
- frozen baseline: 15f27a0030fabffa83c40dbae7874b9614c20d49
- archive ref: archive/p00-governance-2026-09-24
- old JSON/checkpoint/review files are historical evidence, not active routing state
- no P00 dev23/prodlike continuation unless explicitly reopened

BLOCKERS: no discrete NVIDIA GPU; model execution remains gated until exact checkpoint/license/runtime review and bounded rental budget.
