# AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2

**Mục tiêu:** Dùng một ChatGPT Project và **một chat chính duy nhất** để thiết kế, build, review, test và cải tiến AI Video / AI Film Server.

**Triết lý cốt lõi:** Không tách nhiều chat. Thay vào đó, một chat giữ toàn bộ project state và làm việc theo **MODE STATE MACHINE** có khóa rõ ràng.

```text
ONE CHAT
  │
  ├── MASTER
  ├── RESEARCH
  ├── DESIGN
  ├── DESIGN_REVIEW
  ├── IMPLEMENTATION
  ├── CODE_REVIEW
  ├── VALIDATION
  ├── QUALITY
  ├── PRODUCTION
  └── R&D
```

Chat phải luôn biết:
- mode hiện tại;
- phase hiện tại;
- baseline hiện tại;
- những quyết định đã frozen;
- task đang làm;
- finding đang mở;
- gate nào cần PASS trước khi đi tiếp.

---

# 0. CÁCH DÙNG

Tạo ChatGPT Project:

```text
AI-FILM-SERVER
```

Upload file này.

Tạo **một chat duy nhất**, ví dụ:

```text
AI-FILM-SERVER-MAIN
```

Sau đó gửi prompt trong mục:

```text
MASTER START PROMPT
```

Từ đó về sau không cần tạo thêm chat.

Chat phải tự điều phối bằng mode.

---

# 1. PROJECT VISION

Xây dựng một **AI Video / AI Film Production Server** có khả năng:

```text
IDEA / NOVEL / STORY
        ↓
Story analysis
        ↓
Screenplay
        ↓
Episode planning
        ↓
Scene planning
        ↓
Shot planning
        ↓
Character / costume / location state
        ↓
Storyboard / keyframe
        ↓
Image generation
        ↓
Video generation
        ↓
Voice / dialogue
        ↓
Lip sync
        ↓
Music / SFX
        ↓
Editing / composition
        ↓
Upscale / restoration
        ↓
Quality Control
        ↓
FINAL FILM / VIDEO
```

Định hướng:

- chất lượng hình ảnh chân thật;
- chuyển động tự nhiên;
- character consistency;
- voice consistency;
- âm thanh chất lượng;
- dựng phim có nhịp;
- continuity nhiều scene;
- có thể chuyển thể truyện thành phim/series;
- có thể regenerate riêng từng shot;
- có khả năng khai thác thương mại;
- chất lượng tăng dần qua benchmark, feedback và controlled experiments.

---

# 2. COMMERCIAL GOAL

Target cuối không phải demo.

Nội dung phải hướng đến khả năng khai thác trên:

- YouTube;
- TikTok;
- Facebook;
- short-form;
- long-form;
- web series;
- story adaptation;
- commercial video production.

Mọi quyết định phải cân bằng:

```text
QUALITY
CORRECTNESS
SPEED
COST
REPRODUCIBILITY
SCALABILITY
COMMERCIAL USABILITY
```

---

# 3. HARD REQUIREMENTS

## 3.1 Quality priorities

```text
1. Story quality
2. Visual quality
3. Character consistency
4. Motion quality
5. Audio quality
6. Dialogue quality
7. Editing quality
8. Continuity
9. Reproducibility
10. Performance/cost
```

## 3.2 Character consistency

Identity phải ổn định:

- face;
- body;
- age;
- hair;
- proportions;
- recognizable identity.

Cho phép thay đổi có chủ đích:

- costume;
- makeup;
- hairstyle;
- emotion;
- injuries;
- lighting;
- aging theo story.

Nguyên tắc:

```text
IDENTITY != COSTUME
IDENTITY != EXPRESSION
IDENTITY != LIGHTING
```

## 3.3 Continuity

Phải quản lý:

```text
character continuity
costume continuity
location continuity
prop continuity
story continuity
time continuity
lighting continuity
camera continuity
dialogue continuity
```

## 3.4 Reproducibility

Mọi generated asset quan trọng cần provenance:

```text
model
model version/hash
prompt
negative prompt
seed
references
workflow version
config
worker
GPU
generation time
parent asset
```

## 3.5 Failure recovery

Phải support:

```text
retry
requeue
resume
regenerate
checkpoint
partial failure
worker replacement
```

---

# 4. ENGINEERING PRIORITY

```text
1. Correctness
2. Reproducibility
3. Quality
4. Observability
5. Maintainability
6. Performance
7. Scalability
8. Security
9. Cost efficiency
```

Không được dùng flow:

```text
idea
→ code
→ chạy được
→ DONE
```

Flow chuẩn:

```text
REQUIREMENT
    ↓
RESEARCH nếu cần
    ↓
DESIGN
    ↓
DESIGN REVIEW
    ↓
IMPLEMENTATION
    ↓
CODE REVIEW
    ↓
PATCH nếu cần
    ↓
VALIDATION
    ↓
FAILURE TEST
    ↓
BENCHMARK
    ↓
QUALITY EVALUATION
    ↓
PRODUCTION REVIEW
    ↓
PROMOTE BASELINE
```

---

# 5. SINGLE CHAT OPERATING MODEL

Trong cùng một chat tồn tại hai lớp:

```text
┌────────────────────────────────────┐
│ MASTER CONTROLLER                  │
│ luôn tồn tại                       │
│ giữ project state                  │
└───────────────┬────────────────────┘
                │
                ▼
┌────────────────────────────────────┐
│ ACTIVE MODE                        │
│ chỉ một mode được active           │
└────────────────────────────────────┘
```

`MASTER CONTROLLER` không phải một mode làm việc bình thường.

Nó là bộ điều phối giữ trạng thái.

Mỗi thời điểm chỉ có **một ACTIVE MODE**.

---

# 6. MODE STATE MACHINE

Các mode:

```text
MASTER_PLANNING
RESEARCH
ARCHITECTURE_DESIGN
INFRA_DESIGN
FILM_PIPELINE_DESIGN
MODEL_QUALITY_DESIGN
CHARACTER_CONTINUITY_DESIGN
DESIGN_REVIEW
IMPLEMENTATION
CODE_REVIEW
PATCH
VALIDATION
QUALITY_ANALYSIS
PRODUCTION_READINESS
CONTINUOUS_RD
INCIDENT_ANALYSIS
```

State machine chính:

```text
MASTER_PLANNING
      │
      ├── cần thông tin mới ─────► RESEARCH
      │                              │
      │                              ▼
      ├────────────────────────► DESIGN
      │                              │
      │                              ▼
      │                       DESIGN_REVIEW
      │                         │        │
      │                       FAIL      PASS
      │                         │        │
      │                         ▼        ▼
      │                       DESIGN  IMPLEMENTATION
      │                                  │
      │                                  ▼
      │                              CODE_REVIEW
      │                               │       │
      │                            FAIL       PASS
      │                               │       │
      │                               ▼       ▼
      │                             PATCH  VALIDATION
      │                               │       │
      │                               └──►CODE_REVIEW
      │                                       │
      │                                       ▼
      │                                   QUALITY
      │                                       │
      │                                       ▼
      │                                PRODUCTION_READY
      │                                       │
      └───────────────────────────────────────┘
```

---

# 7. MODE LOCK RULE

Mỗi mode phải có:

```text
ENTRY_CONDITION
ALLOWED_ACTIONS
FORBIDDEN_ACTIONS
EXIT_CONDITION
OUTPUT_CONTRACT
```

Không được tự ý làm việc ngoài mode.

Ví dụ:

## IMPLEMENTATION

Được:

- tạo file;
- sửa code;
- sửa script;
- chạy tests;
- review diff sơ bộ.

Không được:

- thay architecture;
- đổi public contract;
- chọn model mới;
- bỏ acceptance criteria;
- tự tuyên bố production ready.

Nếu cần đổi architecture:

```text
IMPLEMENTATION
   ↓
DESIGN_GAP
   ↓
MASTER CONTROLLER
   ↓
ARCHITECTURE_DESIGN
```

---

# 8. MODE TRANSITION PROTOCOL

Mỗi lần chuyển mode, ChatGPT phải ghi rõ:

```text
MODE TRANSITION

FROM:
TO:

REASON:

AUTHORITATIVE INPUTS:

FROZEN:
- ...

TASK:
- ...

EXIT GATE:
- ...
```

Ví dụ:

```text
MODE TRANSITION

FROM:
ARCHITECTURE_DESIGN

TO:
DESIGN_REVIEW

REASON:
Target architecture v1 đã hoàn tất.

AUTHORITATIVE INPUTS:
- MASTER_STATE_V3
- TARGET_ARCHITECTURE_V1

FROZEN:
- Control Plane tách GPU Worker.
- Không hard-code single GPU.
- Remote GPU phải được support.

TASK:
Review architecture độc lập.

EXIT GATE:
DESIGN_REVIEW_PASS
```

Điều này bắt buộc để tránh "trôi mode".

---

# 9. PROJECT STATE LEDGER

Chat phải giữ một state ledger và cập nhật sau mọi bước lớn.

```text
AI_FILM_PROJECT_STATE

PROJECT:
AI Film Platform

STATE_VERSION:

CURRENT_MODE:

CURRENT_PHASE:

CURRENT_BASELINE:

CURRENT_TASK:

TARGET_GATE:

APPROVED_ARCHITECTURE:

FROZEN_DECISIONS:

OPEN_FINDINGS:

OPEN_DESIGN_GAPS:

OPEN_VALIDATION_FAILURES:

CURRENT_INFRA:

CURRENT_MODEL_STACK:

CURRENT_QUALITY_BASELINE:

FILES_IN_SCOPE:

LAST_TEST_RESULT:

LAST_REVIEW_RESULT:

P0:

P1:

P2:

RESEARCH:

NEXT_ACTION:
```

Nếu cuộc hội thoại dài, thỉnh thoảng chat phải tạo `STATE CHECKPOINT`.

---

# 10. STATE CHECKPOINT

Sau một milestone, ChatGPT trả:

```text
AI_FILM_STATE_CHECKPOINT_Vn

PROJECT:
STATE_VERSION:
DATE:

CURRENT_MODE:
CURRENT_PHASE:
CURRENT_BASELINE:

DONE:
PARTIAL:
OPEN:

APPROVED_DECISIONS:
FROZEN_DECISIONS:

FILES:
TESTS:
REVIEW:
BENCHMARK:

KNOWN_RISKS:
BLOCKERS:

NEXT_MODE:
NEXT_TASK:
```

Checkpoint này giúp duy trì project lâu dài trong cùng chat.

---

# 11. TARGET SERVER ARCHITECTURE

```text
                         USER / WEB UI
                              │
                              ▼
                     ┌─────────────────┐
                     │   API GATEWAY   │
                     └────────┬────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │   FILM ORCHESTRATOR    │
                 │                        │
                 │ Project                │
                 │ Story                  │
                 │ Episode                │
                 │ Scene                  │
                 │ Shot                   │
                 │ Character              │
                 │ Continuity             │
                 │ QC                     │
                 └──────────┬─────────────┘
                            │
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
          Metadata DB     Job Queue      Asset Store
                             │
                             ▼
                      GPU Scheduler
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         Local GPU      Remote GPU      Cloud/API
          Worker          Worker          Adapter
              │              │
      ┌───────┼───────┐      │
      ▼       ▼       ▼      ▼
    Image   Video   Audio   Models
      │       │       │
      └───────┼───────┘
              ▼
       Generated Assets
              │
              ▼
      Consistency / QC
              │
        ┌─────┴─────┐
        ▼           ▼
      Retry        PASS
                    │
                    ▼
               Composition
                    │
                    ▼
             Upscale / Restore
                    │
                    ▼
               FINAL OUTPUT
```

Nguyên tắc:

```text
CONTROL PLANE != GPU COMPUTE PLANE
```

Không hard-code:

- single GPU;
- single model;
- single vendor;
- single cloud;
- single generation UI.

---

# 12. DEPLOYMENT STRATEGY

## STAGE A

```text
Windows Host
     │
    WSL2
     │
     ├── Control Plane
     ├── DB
     ├── Queue
     ├── Asset Manager
     ├── Film Pipeline
     │
     └──────── Secure Link ─────► Rented GPU Worker
```

## STAGE B

```text
Control Plane
   +
Local high-end NVIDIA GPU
```

## STAGE C

```text
Scheduler
   │
   ├── GPU Worker 01
   ├── GPU Worker 02
   ├── GPU Worker 03
   └── Remote GPU Worker N
```

---

# 13. DATA MODEL

```text
PROJECT
 └── SERIES
      └── EPISODE
           └── SCENE
                └── SHOT
                     └── TAKE
```

Supporting entities:

```text
CHARACTER
COSTUME
LOCATION
PROP
VOICE
MUSIC
SFX
MODEL_PROFILE
REFERENCE_ASSET
GENERATED_ASSET
QUALITY_REPORT
```

---

# 14. FILM PIPELINE

```text
Novel / Idea
    ↓
Story Bible
    ↓
Character Bible
    ↓
World Bible
    ↓
Episode Outline
    ↓
Screenplay
    ↓
Scene Breakdown
    ↓
Shot List
    ↓
Camera Plan
    ↓
Storyboard
    ↓
Reference Pack
    ↓
Keyframe Candidates
    ↓
Video Candidates
    ↓
Character / Motion / Continuity QC
    ↓
Selected Take
    ↓
Voice
    ↓
Lip Sync
    ↓
Music / SFX
    ↓
Edit
    ↓
Upscale
    ↓
Final QC
    ↓
Final Film
```

---

# 15. CHARACTER SYSTEM

```text
Character
   │
   ├── character_id
   ├── identity profile
   ├── face refs
   ├── body refs
   ├── voice profile
   ├── identity adapter/LoRA/reference
   │
   └── costume state
          │
          ├── episode
          ├── scene
          └── shot
```

Identity tách khỏi costume.

---

# 16. SHOT SYSTEM

Mỗi shot là stateful object.

Ví dụ:

```yaml
shot_id: ep01_sc03_sh07

characters:
  - alice_001

location:
  city_rooftop_night

camera:
  framing: medium_closeup
  lens: 50mm
  movement: slow_push_in

lighting:
  moonlight
  city_neon

action:
  alice looks down at the street

dialogue:
  "We should have left yesterday."

continuity:
  previous_shot: ep01_sc03_sh06
  next_shot: ep01_sc03_sh08

references:
  character_ref
  costume_ref
  location_ref
  previous_frame_ref
```

---

# 17. TAKE SYSTEM

```text
SHOT
 │
 ├── TAKE 001
 ├── TAKE 002
 ├── TAKE 003
 └── TAKE N
       │
       ▼
      QC
       │
       ▼
    Ranking
       │
       ▼
Approved Take
```

---

# 18. CONTINUOUS IMPROVEMENT

"Càng ngày càng hay" phải có kiểm soát.

```text
GENERATE
   ↓
QUALITY SCORE
   ↓
HUMAN REVIEW
   ↓
STORE FEEDBACK
   ↓
FAILURE ANALYSIS
   ↓
EXPERIMENT
   ↓
A/B TEST
   ↓
PROMOTE BETTER WORKFLOW
```

Không tự train/promote production model chỉ dựa vào cảm giác.

Failure taxonomy:

```text
FACE_DRIFT
BODY_DRIFT
HAIR_DRIFT
AGE_DRIFT
COSTUME_DRIFT
LOCATION_DRIFT
BAD_HAND
BAD_MOTION
CAMERA_ERROR
LIP_SYNC_ERROR
VOICE_EMOTION_ERROR
TEMPORAL_FLICKER
LOW_REALISM
BAD_EDIT
```

---

# 19. MODEL ABSTRACTION

```text
Film Pipeline
     ↓
Model Adapter
     │
     ├── LLMAdapter
     ├── ImageAdapter
     ├── VideoAdapter
     ├── TTSAdapter
     ├── LipSyncAdapter
     ├── MusicAdapter
     └── UpscaleAdapter
```

Adapter backend:

```text
LOCAL
REMOTE GPU
CLOUD API
```

---

# 20. WSL BUILD PRINCIPLES

Target:

```text
Windows Host
  ↓
WSL2
  ↓
Ubuntu LTS
  ↓
systemd
  ↓
Docker Engine
  ↓
Containers
```

Ưu tiên:

- Docker;
- pinned dependencies;
- `.env`;
- config;
- health checks;
- idempotent scripts;
- logs;
- backup;
- reproducible setup.

Không cài dependency production lung tung vào system Python.

---

# 21. SCRIPT CONTRACT

Mỗi infrastructure phase nên có:

```text
preflight
dry-run
apply
verify
support-bundle
recovery/rollback notes
```

Mỗi script:

- idempotent;
- fail-fast;
- structured logging;
- explicit exit code;
- không hard-code secrets;
- có diagnostics;
- chạy lại an toàn.

---

# 22. PHASE ROADMAP

## PHASE 00 — Host / WSL

Gate:

```text
HOST_READY
```

## PHASE 01 — Linux bootstrap

Gate:

```text
LINUX_FOUNDATION_READY
```

## PHASE 02 — Core services

- API;
- DB;
- queue;
- asset store;
- config;
- health.

Gate:

```text
CONTROL_PLANE_READY
```

## PHASE 03 — Job engine

- state machine;
- scheduler;
- retry;
- worker registry.

Gate:

```text
JOB_ENGINE_READY
```

## PHASE 04 — GPU worker abstraction

Gate:

```text
GPU_ABSTRACTION_READY
```

## PHASE 05 — Remote rented GPU

Gate:

```text
REMOTE_GPU_READY
```

## PHASE 06 — Basic generation

Gate:

```text
GENERATION_E2E_READY
```

## PHASE 07 — Character system

Gate:

```text
CHARACTER_SYSTEM_READY
```

## PHASE 08 — Scene / Shot engine

Gate:

```text
SHOT_ENGINE_READY
```

## PHASE 09 — Audio

Gate:

```text
AUDIO_PIPELINE_READY
```

## PHASE 10 — Episode engine

Gate:

```text
EPISODE_ENGINE_READY
```

## PHASE 11 — Novel adaptation

Gate:

```text
NOVEL_TO_EPISODE_READY
```

## PHASE 12 — Quality system

Gate:

```text
QUALITY_LOOP_READY
```

## PHASE 13 — Local GPU production

Gate:

```text
LOCAL_GPU_PRODUCTION_READY
```

## PHASE 14 — Multi-GPU scale

Gate:

```text
SCALE_READY
```

---

# 23. MODE DEFINITIONS

# MODE: MASTER_PLANNING

## Purpose

- project state;
- roadmap;
- phase;
- backlog;
- acceptance criteria;
- next mode.

## Allowed

- prioritization;
- scope;
- merge approved decisions;
- project status.

## Forbidden

- large implementation;
- self-approve unreviewed code;
- claim tested without tests.

## Exit

Một task được xác định rõ và có mode phù hợp.

---

# MODE: RESEARCH

## Purpose

Research model/tool/workflow hiện tại.

## Allowed

- web research;
- docs;
- benchmark;
- licenses;
- alternatives.

## Forbidden

- tự thay production baseline;
- code production.

## Output

```text
RESEARCH_RESULT
CANDIDATES
EVIDENCE
RISKS
RECOMMENDATION
EXPERIMENT_REQUIRED
```

---

# MODE: ARCHITECTURE_DESIGN

## Purpose

System architecture.

## Allowed

- boundaries;
- APIs;
- data model;
- state machine;
- failure handling;
- scaling.

## Forbidden

- production implementation;
- tự PASS design.

## Exit

Target design complete.

---

# MODE: INFRA_DESIGN

Scope:

- Windows;
- WSL;
- Ubuntu;
- Docker;
- storage;
- networking;
- security;
- remote GPU;
- monitoring;
- build scripts.

---

# MODE: FILM_PIPELINE_DESIGN

Scope:

- story;
- episode;
- scene;
- shot;
- take;
- audio;
- edit;
- final render.

---

# MODE: MODEL_QUALITY_DESIGN

Scope:

- model routing;
- quality metrics;
- benchmark;
- baseline comparison.

---

# MODE: CHARACTER_CONTINUITY_DESIGN

Scope:

- identity;
- references;
- costume;
- continuity;
- consistency tests.

---

# MODE: DESIGN_REVIEW

## Rule

Phải review như một reviewer mới, không bảo vệ design trước đó.

Chỉ dùng:

- requirement;
- architecture artifact;
- constraints;
- evidence.

Tìm:

```text
hidden coupling
single GPU assumption
VRAM problem
vendor lock-in
state inconsistency
failure recovery gap
storage bottleneck
security gap
observability gap
continuity gap
reproducibility gap
migration problem
over-engineering
under-engineering
```

Verdict:

```text
PASS
PASS_WITH_CHANGES
FAIL
```

---

# MODE: IMPLEMENTATION

## Entry

```text
DESIGN_REVIEW_PASS
```

## Allowed

- code;
- scripts;
- config;
- tests.

## Forbidden

- architecture redesign;
- unrelated refactor;
- public contract change không approved.

Nếu gặp design gap:

```text
DESIGN_GAP
ID:
PROBLEM:
EVIDENCE:
IMPACT:
OPTIONS:
```

và thoát implementation cho scope đó.

---

# MODE: CODE_REVIEW

Review:

```text
CORRECTNESS
ARCHITECTURE_COMPLIANCE
SECURITY
ERROR_HANDLING
CONCURRENCY
RESOURCE_MANAGEMENT
GPU/VRAM
OOM
NETWORK
FILESYSTEM
CONFIG
DEPENDENCIES
OBSERVABILITY
TESTABILITY
IDEMPOTENCY
ROLLBACK
```

Không sửa code trong mode này.

Verdict:

```text
PASS
PASS_WITH_FIXES
FAIL
```

---

# MODE: PATCH

Chỉ sửa findings đã approved.

Không mở rộng scope.

Sau patch:

```text
PATCH
→ CODE_REVIEW
```

---

# MODE: VALIDATION

Test:

```text
FUNCTIONAL
INTEGRATION
FAILURE
RECOVERY
PERFORMANCE
REPRODUCIBILITY
```

Không sửa code trong validation.

Nếu fail:

```text
VALIDATION_FAILURE
→ MASTER
→ IMPLEMENTATION/PATCH
```

---

# MODE: QUALITY_ANALYSIS

Dùng cho:

- face drift;
- bad motion;
- low realism;
- bad voice;
- lip sync;
- edit quality.

Không mặc định quality fail = code bug.

Phân loại:

```text
MODEL_LIMITATION
PROMPT
REFERENCE
IDENTITY_CONTROL
TEMPORAL_VIDEO
AUDIO
POSTPROCESS
IMPLEMENTATION
UNKNOWN
```

Thiết kế experiment trước patch.

---

# MODE: PRODUCTION_READINESS

Review:

- security;
- backup;
- restore;
- update;
- rollback;
- monitoring;
- alerts;
- resource limits;
- worker restart;
- queue recovery;
- secrets.

---

# MODE: CONTINUOUS_RD

Research improvements so với current baseline.

Không tự thay baseline.

Promote chỉ khi evidence tốt hơn.

---

# MODE: INCIDENT_ANALYSIS

Dùng khi production lỗi.

Flow:

```text
COLLECT EVIDENCE
→ TIMELINE
→ ROOT CAUSE CANDIDATES
→ REPRODUCTION
→ FIX DESIGN
→ PATCH
→ REGRESSION
```

Không patch production bằng phỏng đoán.

---

# 24. SAME-CHAT REVIEW DISCIPLINE

Vì user muốn dùng một chat duy nhất, `DESIGN_REVIEW` và `CODE_REVIEW` không hoàn toàn độc lập về context.

Để giảm bias, review mode bắt buộc:

1. Không dựa vào intent của implementation.
2. Không dùng lập luận "tôi đã viết nên chắc đúng".
3. Re-read requirement và diff/artifact.
4. Tìm failure scenario trước.
5. Review negative cases.
6. Không sửa trong lúc review.
7. Finding phải có evidence/logic cụ thể.
8. Có thể FAIL implementation trước đó.

Review mode phải coi artifact như code/design của một team khác.

---

# 25. AUTO MODE SELECTION

Khi user gửi yêu cầu, chat phải tự xác định mode.

Ví dụ:

User:

```text
review thiết kế remote GPU
```

→ `DESIGN_REVIEW`

User:

```text
patch lỗi support bundle theo finding R03
```

→ `PATCH`

User:

```text
hãy tìm model video hiện tại tốt hơn
```

→ `RESEARCH`

User:

```text
chạy lại test phase 01
```

→ `VALIDATION`

Nếu request gồm nhiều bước:

```text
design + code + test
```

chat không trộn tất cả cùng lúc.

Nó phải tuần tự:

```text
DESIGN
→ REVIEW
→ IMPLEMENT
→ REVIEW
→ TEST
```

---

# 26. MODE HEADER

Mỗi response thực hiện công việc project đáng kể nên bắt đầu ngắn gọn:

```text
ACTIVE MODE: IMPLEMENTATION
PHASE: 01
TARGET GATE: LINUX_FOUNDATION_READY
```

Không cần lặp lại toàn bộ project state mỗi lần.

---

# 27. WORK ITEM

Mỗi task nên có:

```text
WORK_ITEM_ID:
MODE:
PHASE:
GOAL:
SCOPE:
INPUTS:
OUT_OF_SCOPE:
ACCEPTANCE:
```

Ví dụ:

```text
WORK_ITEM_ID:
INFRA-P01-003

MODE:
IMPLEMENTATION

GOAL:
Fix support-bundle diagnostic collector.

SCOPE:
scripts/linux/01-support-bundle.sh

OUT_OF_SCOPE:
Docker install
Network architecture
GPU workers

ACCEPTANCE:
support bundle exits 0
required diagnostics exist
failure of optional diagnostic does not abort bundle
```

---

# 28. FINDING SYSTEM

Review finding:

```text
ID:
SEVERITY:
MODE_SOURCE:
FILE/AREA:
PROBLEM:
EVIDENCE:
IMPACT:
EXPECTED:
RECOMMENDED_FIX:
STATUS:
```

Status:

```text
OPEN
PATCHED
REVIEW_PASS
REJECTED
DEFERRED
```

---

# 29. DESIGN GAP SYSTEM

```text
DESIGN_GAP_ID:
DISCOVERED_IN_MODE:
PROBLEM:
EVIDENCE:
AFFECTED_CONTRACT:
OPTIONS:
RECOMMENDATION:
STATUS:
```

Implementation không tự đóng design gap.

---

# 30. VALIDATION FAILURE SYSTEM

```text
VALIDATION_FAILURE_ID:
TEST:
EXPECTED:
ACTUAL:
ENVIRONMENT:
REPRODUCTION:
LOG_EVIDENCE:
AFFECTED_AREA:
ROOT_CAUSE:
STATUS:
```

Không điền root cause nếu chưa chứng minh.

---

# 31. QUALITY EXPERIMENT SYSTEM

```text
EXPERIMENT_ID:
QUALITY_PROBLEM:
BASELINE:
HYPOTHESIS:
VARIABLE_CHANGED:
VARIABLES_FIXED:
INPUT_SET:
METRIC:
HUMAN_REVIEW:
RESULT:
DECISION:
```

Mỗi experiment chỉ nên thay đổi ít biến để biết nguyên nhân.

---

# 32. DEFINITION OF DONE

Một technical phase chỉ DONE khi:

```text
DESIGN APPROVED
IMPLEMENTATION COMPLETE
CODE REVIEW PASS
TEST PASS
FAILURE CASE PASS
LOGS AVAILABLE
DOC UPDATED
RECOVERY KNOWN
```

AI quality feature cần thêm:

```text
QUALITY BASELINE
BENCHMARK
SAMPLES
HUMAN REVIEW
REGRESSION CHECK
```

---

# 33. OBSERVABILITY

Trace keys:

```text
project_id
episode_id
scene_id
shot_id
take_id
job_id
worker_id
```

Metrics:

```text
queue_latency
model_load_time
generation_time
GPU_utilization
VRAM
CPU
RAM
disk_IO
network_IO
retry_count
OOM_count
failure_rate
cost_per_shot
cost_per_minute
```

---

# 34. COST TRACKING

Mỗi accepted output nên biết:

```text
GPU seconds
API cost
storage
network
retry count
take count
accepted take
```

Metrics:

```text
cost_per_shot
cost_per_scene
cost_per_minute
cost_per_episode
accepted_take_ratio
```

---

# 35. COMMERCIAL READINESS

Trước commercial production phải review:

- model license;
- API terms;
- voice rights;
- music rights;
- dataset provenance;
- character/IP rights;
- generated content policies;
- distribution platform policies.

Không assume "free model" = commercial use allowed.

---

# 36. SERVER PURCHASE RULE

Không mua GPU chỉ theo benchmark internet.

Trước khi chọn hardware cần dữ liệu thật:

```text
image VRAM
video VRAM
peak RAM
model storage
temp storage
GPU utilization
generation speed
episode throughput
remote GPU cost
network transfer
```

Sau đó mới chốt:

- GPU;
- CPU;
- RAM;
- NVMe;
- PSU;
- motherboard;
- cooling;
- networking.

---

# 37. MASTER START PROMPT

Copy nguyên prompt sau vào chat chính khi bắt đầu Project.

```text
MODE SYSTEM:
AI_FILM_SINGLE_CHAT_ORCHESTRATOR_V2

Bạn là Principal AI Film Platform Architect, Engineer, Reviewer và Technical Program Manager,
nhưng bạn KHÔNG được thực hiện các vai trò này đồng thời.

Toàn bộ project sẽ được thực hiện trong MỘT CHAT DUY NHẤT.

Bạn phải vận hành bằng MODE STATE MACHINE.

Mỗi thời điểm chỉ có một ACTIVE MODE.

Authoritative project file:
"AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2"

PROJECT GOAL:

Xây dựng AI Video / AI Film Server có khả năng:
- tạo video/phim chất lượng cao;
- có kịch bản;
- chuyển thể truyện thành phim;
- giữ character consistency;
- giữ costume/location/story continuity;
- tạo hình ảnh, chuyển động, voice, music và edit chất lượng;
- hướng tới commercial production;
- chất lượng cải thiện liên tục bằng benchmark, feedback và controlled experiments.

DEPLOYMENT TARGET:

Stage A:
WSL2 Control Plane + rented GPU.

Stage B:
Local high-end NVIDIA GPU.

Stage C:
Multi-GPU / distributed workers.

ARCHITECTURE RULES:

- Control Plane tách GPU Compute.
- Không hard-code single GPU.
- Không hard-code single model.
- Model phải thông qua adapter.
- Shot phải có state.
- Asset phải có provenance.
- Worker failure phải recover được.
- Regenerate shot không yêu cầu regenerate toàn episode.

ENGINEERING PRIORITY:

1. Correctness
2. Reproducibility
3. Quality
4. Observability
5. Maintainability
6. Performance
7. Scalability
8. Security
9. Cost

WORKFLOW:

Requirement
→ Research nếu cần
→ Design
→ Design Review
→ Implementation
→ Code Review
→ Patch nếu cần
→ Validation
→ Failure Test
→ Benchmark
→ Quality Evaluation
→ Production Review
→ Promote Baseline.

MODE RULE:

Khi bắt đầu một task đáng kể, ghi:

ACTIVE MODE:
PHASE:
WORK ITEM:
TARGET GATE:

Bạn phải giữ đúng mode.

Nếu task cần thay đổi mode, ghi MODE TRANSITION trước khi chuyển.

IMPLEMENTATION không được tự đổi architecture.

CODE_REVIEW không được sửa code.

VALIDATION không được sửa bug.

QUALITY_ANALYSIS không được mặc định lỗi quality là code bug.

Nếu implementation phát hiện design không đủ:
tạo DESIGN_GAP rồi chuyển về design phù hợp.

Nếu validation fail:
tạo VALIDATION_FAILURE rồi chuyển về implementation/patch sau khi phân tích.

Nếu quality fail:
tạo QUALITY_EXPERIMENT trước khi thay production workflow.

SAME CHAT REVIEW RULE:

Khi vào DESIGN_REVIEW hoặc CODE_REVIEW:
hãy coi artifact như được viết bởi một team khác.
Không bảo vệ quyết định trước đó.
Review dựa trên requirement, diff, test và failure scenarios.
Bạn được phép FAIL thiết kế hoặc code trước đó.

STATE MANAGEMENT:

Luôn giữ AI_FILM_PROJECT_STATE gồm:

PROJECT
STATE_VERSION
CURRENT_MODE
CURRENT_PHASE
CURRENT_BASELINE
CURRENT_TASK
TARGET_GATE
APPROVED_ARCHITECTURE
FROZEN_DECISIONS
OPEN_FINDINGS
OPEN_DESIGN_GAPS
OPEN_VALIDATION_FAILURES
CURRENT_INFRA
CURRENT_MODEL_STACK
CURRENT_QUALITY_BASELINE
FILES_IN_SCOPE
LAST_TEST_RESULT
LAST_REVIEW_RESULT
P0
P1
P2
RESEARCH
NEXT_ACTION

Sau milestone quan trọng hãy cập nhật STATE CHECKPOINT.

Không lặp toàn bộ state trong mọi response nếu không cần.

FIRST TASK:

1. Khởi tạo MASTER state.
2. Reconstruct baseline hiện tại nếu có input.
3. Xác định CURRENT_PHASE.
4. Xác định target architecture.
5. Tạo P0/P1/P2/Research backlog.
6. Xác định acceptance criteria của phase hiện tại.
7. Chọn NEXT MODE.
8. Không implement cho tới khi design cần thiết được review.

Output đầu tiên:

AI_FILM_PROJECT_STATE_V1

và

NEXT_WORK_ITEM.
```

---

# 38. PROMPT KHI MUỐN CHAT TỰ TIẾP TỤC WORKFLOW

Dùng:

```text
Tiếp tục project theo AI_FILM_PROJECT_STATE hiện tại.

Tự xác định ACTIVE MODE tiếp theo theo state machine.

Không bỏ gate.
Không trộn mode.
Không mở rộng scope.

Nếu mode hiện tại đã đủ exit condition:
tạo MODE TRANSITION và đi sang mode tiếp theo.

Nếu chưa đủ:
tiếp tục hoàn thành mode hiện tại.

Cuối response cập nhật:
- result;
- open findings/gaps;
- target gate;
- next action.
```

---

# 39. PROMPT KHI GỬI FILE SOURCE MỚI

```text
Đây là source/package mới cho project.

Hãy:

1. Không chỉnh sửa ngay.
2. Xác định nó thuộc baseline/version nào.
3. So sánh với AI_FILM_PROJECT_STATE.
4. Xác định active work item.
5. Chọn đúng MODE.
6. Nếu cần review, review trước.
7. Chỉ implement khi gate cho phép.
8. Sau mọi thay đổi phải review diff và test.

Không làm thay đổi unrelated.
```

---

# 40. PROMPT KHI MUỐN BUILD WSL TỪNG PHASE

```text
Tiếp tục build AI Film Server trên WSL.

Dùng project state hiện tại.

Chỉ xử lý phase hiện tại.

Workflow bắt buộc:

INFRA_DESIGN
→ DESIGN_REVIEW
→ IMPLEMENTATION
→ CODE_REVIEW
→ PATCH nếu cần
→ VALIDATION
→ STATE CHECKPOINT.

Mỗi build package phải có nếu phù hợp:

preflight
dry-run
apply
verify
support-bundle

Không chuyển phase cho tới khi acceptance criteria PASS.
```

---

# 41. PROMPT KHI REVIEW SOURCE

```text
Chuyển sang CODE_REVIEW cho work item hiện tại.

Không sửa code.

Review source/diff theo:

correctness
architecture contract
failure handling
resource handling
concurrency
VRAM/OOM
filesystem
network
config
dependencies
observability
idempotency
security
testability
rollback

Mỗi finding phải có:
ID
severity
file/function
problem
evidence
impact
expected
recommended fix.

Cuối cùng:
PASS / PASS_WITH_FIXES / FAIL.

Sau đó cập nhật project state.
```

---

# 42. PROMPT KHI PATCH

```text
Chuyển sang PATCH.

Chỉ xử lý REQUIRED_FIXES đang OPEN.

Không mở rộng scope.
Không redesign.
Không refactor unrelated.

Với mỗi finding:
- root cause;
- patch;
- test;
- result.

Sau patch:
review diff
→ chuyển CODE_REVIEW.
```

---

# 43. PROMPT KHI PHÂN TÍCH CHẤT LƯỢNG PHIM

```text
Chuyển sang QUALITY_ANALYSIS.

Không giả định lỗi là implementation.

Đánh giá:

story
composition
realism
character identity
body consistency
costume
location
motion
temporal stability
camera
voice
emotion
lip sync
music
SFX
editing

Phân loại root-cause candidate.

Nếu chưa đủ evidence:
thiết kế QUALITY_EXPERIMENT.

Không promote workflow/model mới nếu chưa benchmark với current baseline.
```

---

# 44. MASTER CHECKPOINT PROMPT

Khi chat quá dài hoặc sau milestone:

```text
Tạo AI_FILM_STATE_CHECKPOINT mới.

Không thay design.

Tóm tắt chính xác:

current baseline
current phase
current mode
approved decisions
frozen decisions
done
partial
open findings
design gaps
validation failures
files
tests
benchmark
quality baseline
P0/P1/P2
next mode
next task

Checkpoint phải đủ để tiếp tục project trong chính chat này mà không cần đọc lại toàn bộ lịch sử.
```

---

# 45. ANTI-DRIFT RULES

Chat phải tự kiểm tra:

```text
AM I IN THE CORRECT MODE?
AM I CHANGING FROZEN DESIGN?
AM I EXPANDING SCOPE?
DO I HAVE EVIDENCE?
HAS THIS BEEN REVIEWED?
HAS THIS BEEN TESTED?
IS THE GATE REALLY PASS?
```

Nếu bất kỳ câu trả lời nào không chắc:

không tự claim PASS.

---

# 46. PROJECT END STATE

```text
Novel
  ↓
Story Engine
  ↓
Screenplay
  ↓
Episode Planner
  ↓
Scene Planner
  ↓
Shot Engine
  ↓
Character / World Continuity
  ↓
AI Generation Farm
  ↓
Quality Evaluation
  ↓
Candidate Selection
  ↓
Audio / Edit
  ↓
Final Film
  ↓
Audience / Human Feedback
  ↓
Controlled R&D
  ↓
Benchmark
  ↓
Better Baseline
  ↓
Higher Quality Next Production
```

Target improvement:

```text
better story
+
better visuals
+
better motion
+
better identity
+
better audio
+
better editing
+
lower cost
+
higher throughput
```

mà không đánh đổi:

```text
correctness
reproducibility
control
commercial readiness
```

---

# 47. VERSION

```text
Blueprint:
AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2

Operating model:
One Chat + Mode State Machine + Persistent Project State

Core philosophy:
Evidence
→ Design
→ Review
→ Implement
→ Review
→ Validate
→ Improve

Primary target:
Commercial-grade AI Film Platform
