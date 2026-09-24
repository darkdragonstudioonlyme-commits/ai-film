# BÀN GIAO — REVIEW TOÀN DIỆN DỰ ÁN AI-FILM (24/09/2026)

> Dành cho chat/agent tiếp theo. Đọc hết file trước khi làm bất cứ việc gì.
> Reviewer: Claude (Opus 5.5), truy cập máy DESKTOP-LCISMET (WSL, user `dragon`) qua Desktop Commander, chế độ chỉ đọc — không sửa repo, worktree hay state của dự án.
> Số liệu đo trực tiếp ngày 24/09/2026, trừ chỗ ghi "chưa xác minh".
> Cập nhật lượt 2: đã chạy lại test độc lập (766/766 PASS, digest khớp); đã kiểm `file/script`; đã xác nhận giới hạn cứng của bridge Claude.
> Cập nhật lượt 3: thêm mục 11 — đánh giá cơ chế "Tiếp tục" và thiết kế v2 để tăng tiến độ mỗi lượt.
> Cập nhật lượt 4: ghi quyết định chủ dự án (24/09), phát hiện máy không có GPU rời, shortlist model mở kèm license (mục 12).
> Cập nhật lượt 5: chủ dự án chọn thuê GPU vài ngày để benchmark rồi mới mua — kế hoạch ở mục 12.10.
> Cập nhật lượt 6: đẩy lên GitHub — branch `handover/review-2026-09-24`, file `handoffs/HANDOVER_REVIEW_2026-09-24.md` (không đụng `main`).
> Cập nhật lượt 7 (ChatGPT, 24/09/2026): đối chiếu GitHub xác nhận `main` vẫn ở `15f27a0`; nhánh handoff tách từ đúng commit đó và so với `main` chỉ thay đổi đường dẫn `handoffs/HANDOVER_REVIEW_2026-09-24.md` (các commit tiếp theo trên nhánh này chỉ hiệu đính chính handoff); `NEXT_WORK_ITEM.md` trên `main` vẫn trỏ TEST_DESIGN R2 / BLOCK 057. Bổ sung freeze + phân loại thẩm quyền để tránh agent sau tự biến khuyến nghị review thành lệnh thực thi.
> Cập nhật lượt 8 (ChatGPT, 24/09/2026): chủ dự án gỡ freeze và cho phép triển khai nếu review đúng. Product-v2 vertical slice đã được test/review, GitHub Actions PASS và merge vào `main` tại `1c3e0b65ad728095e6200ee8c4250bbaedd49a29`; P00 baseline được giữ ở ref `archive/p00-governance-2026-09-24` = `15f27a0`.
> Cập nhật lượt 9 (ChatGPT, 24/09/2026): tái audit toàn bộ handoff bằng archive Git, runtime queue, local WSL/Windows, rerun P00 tests/static và upstream model/license. Sửa các số sai/stale; xác nhận §3.3; phát hiện 11 P00 user timers vẫn chạy và đã freeze reversible (`disable --now`), receipt local `/home/dragon/ai-film-dev/run-evidence/P00_TIMER_FREEZE_20260924.json`.

## Trạng thái hiện tại và thẩm quyền của handoff

**REVIEW_FREEZE: CLOSED. PRODUCT_V2: ACTIVE.** Freeze trước đây đã được chủ dự án gỡ. Pivot đã được triển khai và merge sau test/review.

- Canonical `main`: `1c3e0b65ad728095e6200ee8c4250bbaedd49a29`.
- Active state: `PRODUCT_V2_001`, phase `Vertical Slice 01`, mode `PRODUCT_BUILD`.
- Active work: `T-008..T-009` — GPU benchmark harness/scoring + ffmpeg/animatic preparation.
- P00 historical baseline: ref `archive/p00-governance-2026-09-24` = `15f27a0`.
- P00 legacy worktrees/evidence remain intact; normal `Tiếp tục.` no longer routes to P00.
- 11 scheduled `aifilm-p00-*.timer` found during this re-audit were disabled and stopped; no scheduled P00 automation should continue producing evidence/state in the background.

File này giờ có hai vai trò: **forensic snapshot của P00 cũ** và **record giải thích vì sao PRODUCT_V2 được chọn**. Nó không thay thế `PROJECT_STATE.md`, `RESUME.md`, `BACKLOG.yaml`, `MILESTONES.md` hay `CONTINUE_PROTOCOL.md` trên `main`.

Từ lượt tái audit này, mọi claim được hiểu theo bốn nhãn:
- **CONFIRMED:** tái kiểm chứng bằng Git/runtime/test/host hoặc upstream chính thức.
- **STALE/SUPERSEDED:** đúng tại snapshot P00 nhưng không còn là trạng thái hiện tại.
- **PARTIALLY CONFIRMED:** lõi factual đúng nhưng có số/biên/phần diễn giải cần sửa.
- **ANALYSIS / ESTIMATE / RECOMMENDATION:** đánh giá hoặc thiết kế đề xuất; không thể biến thành “fact” chỉ bằng audit.

Các hành động chi tiền, publish, xóa dữ liệu hoặc quyền nhạy cảm vẫn cần bounded authority tại thời điểm thực hiện; pivot không cấp quyền chi tiêu vô hạn.

## 0. Tóm tắt 60 giây — sau tái audit

- **Finding lịch sử cốt lõi: CONFIRMED.** Trước pivot, P00/governance chiếm gần như toàn bộ hoạt động; archive có 529 commit, 486 Markdown, 130 state V12→V144 và không có film implementation ngoài một planning backlog.
- **P00 code quality: CONFIRMED.** Rerun mới trong lượt tái audit: 766/766 workspace tests PASS, source/test digest khớp; `tools/check_source.py` 101/101 PASS.
- **§3.3 MD/self-learning/dual-AI: CONFIRMED với vài correction số liệu.** 18 learning = 10 EFFECTIVE / 6 INEFFECTIVE / 2 PENDING; continuity receipts 0/3. Runtime queue có 322 task, 74 fail (~22,98%), 72 budget-cap + 2 turn-cap, $70.822, 172 PASS, 75 FINDINGS, 195 findings, 248 RESULT_UNREVIEWED. Tổng `duration_api_ms` trực tiếp = ~1,76 giờ, không phải 1,96 giờ.
- **Role inversion: CONFIRMED.** 322/322 queue tasks là Claude `TEXT_REVIEW` + role `REVIEW`, author_actor = ChatGPT, không file-write scope; 248 completed reviews đều `STATIC_ONLY`.
- **Historical “no film output”: vẫn đúng.** Hiện nay đã có screenplay/casting/continuity/film core/8 benchmark shots, nhưng vẫn chưa có ảnh/video/voice render thực tế.
- **Pivot: IMPLEMENTED.** Main đã chuyển sang PRODUCT_V2; M0/M1 hoàn thành; v2 active control set ~4,1 KB (core) / ~5,9 KB nếu tính state+next, thay vì legacy minimum ~155,7 KiB trước lane/contract-specific context.
- **P00 background automation gap: FOUND + FIXED.** 11 P00 timers còn hoạt động sau pivot; đã disable+stop reversible trong re-audit.
- **Current blocker:** máy không có discrete NVIDIA GPU; ffmpeg/Docker/PyTorch chưa cài. Việc tiếp theo là T-008/T-009, chưa phải quay lại dev23/prodlike.
- **GPU strategy:** thuê/benchmark trước mua vẫn hợp lý; “32 GB là minimum tuyệt đối” không được coi là fact. 32 GB và 96 GB là benchmark tiers; fit thật phụ thuộc model/precision/offload/workflow.
- **Progress ≈2% / P00≈65%** trong bản review gốc là **reviewer estimate**, không phải metric tái chứng minh. PRODUCT_V2 dùng milestone/product metrics thay cho phần trăm đó.

## 1. Bản đồ nguồn — historical vs current

| Hạng mục | Tái audit | Trạng thái |
|---|---|---|
| Canonical current | `origin/main = 1c3e0b65...` | PRODUCT_V2 active |
| Frozen P00 | `archive/p00-governance-2026-09-24 = 15f27a0...` | historical evidence |
| Local clone | `/home/dragon/ai-film-dev/repo` | đã fast-forward và đồng bộ main sau merge |
| Blueprint | `origin/source/p00-dev22-local-authority-exact:contracts/AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2.md` | 2.371 dòng, CONFIRMED |
| P00 contracts | 7 file trong `contracts/` | 3.369 dòng / 172.350 byte, CONFIRMED |
| P00 source | `origin/source/p00-dev22-local-authority-exact = 86bb649...` | 8.130 src lines + 4.069 test lines; 12.775 Python lines total |
| Validation lane | `origin/lane/validation-p00 = 4850b4d...` | 478 file; 7.628 Python lines; 913.119 Markdown bytes |
| Legacy state | archive `PROJECT_STATE.md` V144 | P00 TEST_DESIGN / BLOCK 057, SUPERSEDED |
| Current state | main `PROJECT_STATE.md` | PRODUCT_V2_001 / Vertical Slice 01 / T-008..T-009 |
| Historical film design | archive `docs/FILM_PIPELINE_DESIGN_BACKLOG.md` | F01–F07 only; no film code |
| Current film implementation | main `film/`, `projects/slice01/`, `tests/film/` | film core + 7 design contracts + screenplay/casting/continuity + 8 benchmark shots; no rendered media yet |
| Legacy dual-AI | archive docs + `tools/dual_ai_text_bridge.py`; runtime queue 322 tasks | TEXT_REVIEW-only behavior CONFIRMED |
| Current Claude role intent | main `CLAUDE.md` | implement/debug/test role declared, but implementation-capable headless runtime **chưa được xây/qualified** |
| Legacy learning | archive `learning/LEARNING_STATE.json` | 18 records, process-oriented |
| Current product learning | main `FILM_LEARNINGS.md` | structure exists; chưa có measured film lesson |
| Handoff | branch `handover/review-2026-09-24` + local `/home/dragon/ai-film-dev/handoffs/HANDOVER_REVIEW_2026-09-24.md` | forensic/re-audit document, không phải active router |

## 2. Số liệu then chốt — tái kiểm chứng

| Chỉ số | Kết quả tái audit |
|---|---|
| Archive P00 main | 529 commit; daily counts 15→24/09 = 119·107·89·112·18·24·26·34 — CONFIRMED |
| Commit prefixes | docs(r9) 178 · state 111 · docs 35 · audit(r9) 24 · review(r9) 24 · docs(r8) 14 · review 13 · learning(r9) 12 — CONFIRMED |
| State | 130 JSON state, V12→V144 — CONFIRMED |
| Archive tree | 723 file; 486 MD; 212 JSON — CONFIRMED |
| docs/ | 110 file: **38 `DOCUMENTATION_SYSTEM*` + 68 review/audit/criteria + 2 dual-AI + 1 Phase00 + 1 film**. Bản cũ ghi “~106 DOCUMENTATION_SYSTEM_*” là wording sai |
| Reviews / health / test governance | 108 paths dưới `reviews/`; 42 `HEALTH_REVIEW*.md` (46 workflow-health MD total); 22 paths dưới `test-governance/` — cách đếm cũ “108/44/22” cần ngữ cảnh |
| P00 tests | **766 PASS / 0 fail/error/skip**; digest source `69fdc184…`, test `47d4ae76…` — rerun mới CONFIRMED |
| P00 static | **101/101 PASS** — rerun mới CONFIRMED; bản cũ “chưa chạy lại 101” đã stale |
| Legacy native validation | 86 case NOT_RUN; LAB/SITE NOT_RUN; qualification NOT_ISSUED; HOST_READY NOT_EVALUATED — historical snapshot CONFIRMED |
| Legacy Claude queue | 322 task · $70.8221716 · **~1,76 giờ API** theo tổng `duration_api_ms` · 74 failed = 22,98% · 72 budget cap · 2 turn cap · 172 PASS · 75 FINDINGS · 195 findings · 248 RESULT_UNREVIEWED |
| Legacy task shape | 322/322 role REVIEW; 322/322 TEXT_REVIEW; 322/322 author_actor ChatGPT; 248/248 completed review `STATIC_ONLY` |
| Self-learning | 18 = 10 EFFECTIVE / 6 INEFFECTIVE / 2 PENDING; continuity event receipts 0/3 — CONFIRMED |
| Historical film code | 0 implementation paths; chỉ `docs/FILM_PIPELINE_DESIGN_BACKLOG.md` match film path; `file/script/env` = 12 byte, mode 0600, không mở content |
| Current film code/data | 29 files under `film/`, `projects/`, `tests/film/` sau pivot; 7/7 film tests PASS; 8 benchmark shots compile |
| Hardware current | Windows: Ryzen 9 9950X 16C/32T, ~61,6 GiB RAM, chỉ AMD Radeon iGPU. WSL: CPU capped 24 logical, ~47 GiB RAM, root 1007G còn ~925G |
| Tools current | Python 3.12.3; `nvidia-smi`, ffmpeg, Docker absent; PyTorch not installed |
| P00 timers | 11 scheduled P00 timers found after pivot; re-audit disabled+stopped all 11. Stale dev21 timer entry is not found/inactive |

## 3. Đánh giá chi tiết

### 3.1 Thiết kế có tạo được phim thương mại chất lượng?

**Historical verdict: CONFIRMED. Current status: PARTIALLY REMEDIATED.**

Ở archive P00, kết luận “chưa” là đúng: chỉ có Blueprint + F01–F07 planning backlog, không có film implementation hay media output. Sau pivot, main đã có screenplay gốc, casting spec, continuity ledger, deterministic shot compiler, provenance manifest, 7 design contracts và 8-shot benchmark. Tuy nhiên chưa có GPU output, TTS/lip-sync/edit/QC thực tế, nên **chưa thể đánh giá chất lượng phim thương mại**.

| Tiêu chí | Historical finding | Current PRODUCT_V2 |
|---|---|---|
| Script/story | thiếu executable script engine | screenplay slice01 + SCRIPT_ENGINE contract có, quality loop chưa chạy trên audience/media |
| Continuity | thiếu ledger/validator | ledger + `state_at` + tests có; media QC chưa có |
| Costume/injury/prop | thiếu story-time state | đã có event model và regression test; vision QC chưa có |
| Visual/casting | chưa chọn model/look | casting spec có; chưa có generated refs/face embedding |
| Voice | chưa có voice casting/TTS path | VOICE_BIBLE contract có; audio chưa generate |
| Quality learning | chưa có eval set/takes | FILM_LEARNINGS + QUALITY_LOOP structure có; chưa có measured lesson |
| Commercial readiness | checklist khái niệm | rights metadata scaffold có; platform/publish checks vẫn phải làm tại publication time |

### 3.2 Source có bám thiết kế?

**Historical factual basis: CONFIRMED. “Over-engineering” là reviewer analysis, nhưng evidence hỗ trợ mạnh.**

- P00 accepted source identity `86bb649...`, traceability/test governance và 766+101 checks đều được tái chứng minh.
- Blueprint phần host yêu cầu WSL/systemd/Docker/preflight-style bootstrap; implementation/governance thực tế mở rộng tới authority envelope, trust anchor, LAB/SITE, prodlike systemd supervision, DR/off-host, credential isolation.
- Archive có 11 P00 timers từng được schedule; sau pivot chúng vẫn còn chạy cho tới re-audit này và đã được freeze.
- Archive có đúng **một** film-related path theo path scan: planning backlog; không có story/image/video/audio implementation.
- Do đó factual statement “effort concentrated on P00/governance rather than film pipeline” là CONFIRMED. Câu “lệch tinh thần Blueprint/over-engineered” vẫn là đánh giá kiến trúc, không phải binary test result.
- Current main đã sửa hướng: Product V2 ưu tiên vertical slice và giữ legacy P00 ở archive ref.

### 3.3 Hệ MD, self-learning, phối hợp ChatGPT–Claude

**Re-audit verdict: các vấn đề chính 1–5 đều được xác nhận; wording/số liệu được chuẩn hóa như dưới đây.**

Nên giữ — **CONFIRMED useful properties**:
- Git/exact commit làm durable memory và evidence identity.
- Fail-closed semantics; NOT_RUN / NOT_PROVEN thay cho PASS giả.
- SHA-256 provenance/idempotency patterns.
- F01–F07, film failure taxonomy, experiment template, rights/publication checklist.

Vấn đề:

1. **Hệ MD thành sản phẩm — CONFIRMED.**
   - Archive: 529 commit, 486 MD, 130 state snapshots.
   - `docs/`: 110 file, trong đó **106/110 thuộc family documentation/governance/criteria** = 38 `DOCUMENTATION_SYSTEM*` + 68 review/audit/criteria; wording cũ “~106 DOCUMENTATION_SYSTEM_*” là không chính xác theo tên file.
   - V70 tự ghi: V61→V69 có 25 commit / 8 state transitions, accepted product source không đổi.
   - Current remediation: v2 active control set chỉ ~4,1 KB; ~5,9 KB khi cộng PROJECT_STATE+NEXT. Historical files vẫn ở main/archive để giữ evidence nhưng không còn nằm trong cold-start router.

2. **Self-learning học sai đối tượng — CONFIRMED.**
   - `LEARNING_STATE.json`: 18 = 10 EFFECTIVE / 6 INEFFECTIVE / 2 PENDING.
   - Không record nào là measured film-quality experiment; continuity receipts thực tế 0/3.
   - `SELF_LEARNING.md` tự phân biệt process correction với film-quality improvement và nói process register không chứng minh phim đang tốt lên.
   - Current remediation: `FILM_LEARNINGS.md` riêng đã tạo, nhưng **chưa có measured film lesson** vì chưa có media output.

3. **MD tự sửa nhưng chưa chứng minh tự tốt lên — CONFIRMED historical.**
   - V70 verdict: PARTIAL_CONFORMANCE / END-TO-END EFFECTIVENESS NOT PROVEN.
   - V70 ghi trực tiếp: JavaScript/backtick parsing lỗi lặp; unsafe workspace recreation/branch-exists attempts; TEST_CHANGE 005 lọt feasibility gap rồi gây rework.
   - Search toàn archive policy không tìm thấy explicit complexity/document budget hay add-one/remove-one rule.
   - Current remediation: active docs giảm mạnh, product KPI/milestones có; nhưng retro 10-turn và measured complexity-effectiveness chưa đủ sample.

4. **Phân vai bị đảo — FULLY CONFIRMED historical; remediation chưa hoàn tất.**
   - Bridge code: `--safe-mode --restricted`, `--tools ''`, model sonnet, effort low, `TEXT_REVIEW`, `max_turns=2`, `STATIC_ONLY`.
   - Runtime corpus: 322/322 Claude tasks = role REVIEW + profile TEXT_REVIEW + author_actor ChatGPT; 322/322 không có writable output files; 248 completed reviews đều STATIC_ONLY.
   - Task samples dùng cap $0,25 / 2 turns.
   - Current `CLAUDE.md` đã định nghĩa Claude là code/debug/test worker, **nhưng implementation-capable Claude runtime/headless profile vẫn chưa được xây và qualified**. Vì vậy finding này chưa được đóng hoàn toàn.

5. **Phối hợp nặng nghi thức — CONFIRMED factual core.**
   - 322 task; 74 failed = 22,98%; 72 budget cap, 2 turn cap; $70.822; 248 RESULT_UNREVIEWED.
   - Task/work-item strings có 52 AUTHORIZATION, 62 ATTEMPT, 77 RECONCILIATION occurrences; đây không phải quality metric nhưng chứng minh workflow bị phân mảnh nhiều vòng.
   - Policy thật sự nói tối đa hai correction rounds cùng premise rồi **chủ động route một WORKFLOW_REVIEW**. Vì vậy wording cũ “thoát luật bằng thêm WORKFLOW_REVIEW” là reviewer interpretation; fact chính xác là policy thiết kế WORKFLOW_REVIEW như meta-correction sau hai vòng, và thực tế V63 đã dùng route này.
   - Current remediation: Continue v2 batch routing đã active; L2/background runner và Claude implement engine chưa active.

### 3.4 Chất lượng code và tiến độ

**Code-quality finding: CONFIRMED. Progress percentages: ESTIMATE only.**

- P00 source rerun: 766/766 PASS + 101/101 static PASS; exact digests match.
- Bridge reusable implementation patterns confirmed: `atomic_json`, file+dir `fsync`, strict duplicate-key JSON parser, durable idempotency receipts.
- Block 057 factual sequence is preserved in archive: 13/13 targeted TV014 tests passed; predecessor fixture gap caused 22 regression failures and forced TEST_DESIGN R2 rather than weakening producer contract.
- Vì vậy “code locally careful but scope/governance disproportionate” has strong evidence; “disproportionate” remains architectural judgment.
- Bảng phase weighting và “≈2% total / P00≈65%” của reviewer là **heuristic estimate**, không có canonical denominator; không dùng làm current KPI.
- Current PRODUCT_V2 uses milestones instead: M0/M1 completed, M2 next; no generated media yet.

## 4. Nguyên nhân gốc — trạng thái xác minh

Các mục dưới đây là **causal analysis**, không phải fact có thể PASS/FAIL độc lập. Re-audit xác nhận evidence nền:
1. Router cũ tuần tự/mode-gated và có nhiều pre-execution guards — CONFIRMED.
2. Same-project review independence bị giới hạn; thêm nhiều review/audit layers — CONFIRMED as structure; causal claim “vì thế sinh đệ quy” là analysis.
3. P00 có LAB/SITE/authority/prodlike/DR/offhost scope lớn cho một workstation — CONFIRMED.
4. Legacy system không có measured film-output KPI — CONFIRMED.
5. Scope/oracle strictness làm thay đổi fixture nhỏ có thể quay lại TEST_DESIGN — CONFIRMED qua block 057.
6. Claude implementation role bị bridge TEXT_REVIEW-only vô hiệu hóa — CONFIRMED.

Do đó hướng product-first pivot vẫn được giữ. Không cần coi thứ tự 1→6 là ranking nguyên nhân đã chứng minh.

## 5. Khuyến nghị của reviewer — trạng thái triển khai sau re-audit

| Khuyến nghị | Trạng thái |
|---|---|
| Freeze/archive P00 | **DONE:** archive ref = `15f27a0`; legacy evidence/worktrees giữ nguyên |
| HOST_READY_PRACTICAL | **DONE/PASS:** 8 practical checks PASS |
| Dừng P00 prodlike/authority/LAB routing | **DONE:** main routes PRODUCT_V2 |
| Dừng P00 background timers | **DONE trong re-audit:** 11 timers disabled+inactive |
| Di chuyển physical old docs/state vào thư mục archive | **NOT DONE BY DESIGN:** không cần đổi hàng trăm paths; archive ref giữ immutable snapshot, active cold-start bỏ qua legacy files |
| North-star product metrics | **DECLARED, chưa có media sample** |
| Vertical slice | **IN PROGRESS:** M0/M1 done, no rendered media |
| 7 film design docs | **DONE initial contracts**; advanced media QC/casting/voice implementation còn thiếu |
| Claude implement runtime | **NOT DONE:** role intent changed, runtime still legacy TEXT_REVIEW-only |
| Continue v2 L1 | **ACTIVE** |
| L2 background runner | **NOT ENABLED** |
| Measured film learning | **NOT YET:** FILM_LEARNINGS empty of experiments |
| GPU rental benchmark | **NOT YET:** T-008 prepares harness |
| ffmpeg/animatic | **NOT YET:** T-009 |
| First film | **NOT YET** |

### P0 — Dừng chảy máu (historical recommendation)
- Tag hiện trạng `archive/p00-governance-2026-09-24`. Không xóa gì.
- Tuyên bố `HOST_READY_PRACTICAL`: checklist ≤ 1 trang + script < 5 phút (WSL, distro, user, disk, DNS/HTTPS, systemd, Python, git, GPU/driver nếu có).
- Dừng dev23/prodlike/authority/LAB; tạm dừng hàng đợi dual-ai cho P00.
- Chuyển DOCUMENTATION_SYSTEM_* và state snapshot cũ vào `archive/` (vẫn trong git).

### P0 — Đổi thước đo (North Star)
Theo dõi các chỉ số:
- time-to-first-clip;
- số giây phim hoàn chỉnh/tuần;
- chi phí/giây phim;
- % take dùng được;
- điểm người chấm (1–5) theo rubric;
- sau khi đăng: retention/completion.

### P1 — Vertical slice 2 tuần

Output:
- slice01: 60–90 giây, 1–2 scene (sau đó mở rộng tới ≤ 3 phút);
- 2–3 nhân vật khác biệt rõ, 10–15 shot;
- thoại 3 ngôn ngữ EN/ZH/VI (ưu tiên phát hành EN/ZH), nhạc + SFX, phụ đề từng ngôn ngữ;
- master 9:16, có đường xuất 16:9 (mục 12.6).

Chuỗi xử lý: premise → story bible → screenplay → shot list YAML (Blueprint §16) → continuity ledger → casting (ngoại hình + giọng) → keyframe (3–4 take/shot) → image-to-video → TTS theo nhân vật → lip-sync cho cận cảnh có thoại → nhạc/SFX → dựng (ffmpeg) → QC → xuất.

Hạ tầng tối thiểu:
- Python package trong WSL;
- thư mục project + SQLite + manifest JSON mỗi asset (provenance §3.4);
- chưa cần Docker/queue/DB server; model mở chạy trên GPU cục bộ (mục 12.3).

Trước khi build: MODEL-EVAL 3–5 ngày trên GPU thuê (mục 12.10) theo shortlist mục 12.4 (video, ảnh, TTS EN/ZH/VI, lip-sync, nhạc) với 5–10 shot cố định, thử cả tả thực và 3D. Model thay đổi nhanh nên phải benchmark mới tại thời điểm làm.

### P1 — Thiết kế phim cần viết (mỗi tài liệu ≤ 2 trang, có schema + ví dụ)
1. **SCRIPT_ENGINE:** hook, xung đột, cao trào, twist; beat sheet; scene card; format screenplay. Writers' room 2 model (A viết, B phê bình theo rubric, người chọn). Table read bằng TTS để kiểm nhịp thoại.
2. **CONTINUITY_LEDGER:** mô hình sự kiện theo thời gian truyện (ví dụ bên dưới).
3. **CASTING_AND_LOOK:** character sheet (turnaround, biểu cảm), art bible. Kiểm tra khác biệt giữa nhân vật và nhất quán trong nhân vật bằng face embedding.
4. **VOICE_BIBLE:** mỗi nhân vật có giới tính, tuổi, âm sắc, tốc độ, vùng miền, dải cảm xúc. Kèm từ điển phát âm tên riêng, tag cảm xúc từng câu, kiểm tra khác biệt giọng (speaker embedding), đồng thuận/bản quyền giọng clone, chuẩn loudness theo nền tảng.
5. **SHOT_COMPILER:** shot spec + ledger + casting → prompt + references theo từng model; lưu cả spec lẫn prompt đầy đủ.
6. **QC_AND_RATING:** auto-check (identity similarity, costume/injury so với ledger bằng vision model, flicker) + form chấm người theo taxonomy §18.
7. **QUALITY_LOOP:** lưu mọi take (spec, prompt, refs, model/version, seed, cost, điểm, failure tag); báo cáo sau mỗi phim; champion/challenger trên eval set 20–30 shot; promote khi tốt hơn mà không vượt ngưỡng chi phí.

```yaml
characters:
  an:
    identity: {face_ref: refs/an/face_v1.png, voice_id: vi_male_28_bac_01}
    baseline: {hair: "tóc ngắn đen", build: "gầy, cao"}
timeline:
  - t: D1_sang
    scene: sc01
    events:
      - {char: an, type: costume, value: "áo sơ mi trắng, quần tây xám"}
  - t: D1_chieu
    scene: sc03
    events:
      - {char: an, type: injury_add, part: "cẳng tay trái", desc: "vết chém, băng gạc trắng", severity: medium}
      - {char: an, type: costume_damage, part: "tay áo trái", desc: "rách, dính máu"}
  - t: D3_toi
    scene: sc07
    events:
      - {char: an, type: injury_update, part: "cẳng tay trái", desc: "băng nhỏ, đang lành"}
# state_at(char, t) = gộp mọi event ≤ t. Mỗi shot khai báo t → compiler chèn trạng thái vào prompt/reference; QC so khung hình với state_at.
```

### P1 — Tái phân vai (giả thuyết, xác nhận bằng A/B thực tế)

| Việc | Chính | Review |
|---|---|---|
| Ưu tiên, kế hoạch, tiêu chí nghiệm thu | ChatGPT + chủ dự án | Claude phản biện khả thi |
| Code, test, debug trong repo | Claude Code (Read/Edit/Bash trong worktree; không secrets, không push main) | ChatGPT review diff |
| Kịch bản, thoại, shot list | Cả hai theo writers' room; người chọn | Model còn lại phê bình theo rubric |
| Chấm take | Auto-QC + người | Model gắn failure tag |
| Merge / publish / chi tiền | Chủ dự án | — |

Budget Claude theo quy mô task (vd 1–5 USD, 20–50 lượt) thay vì 0,25 USD/2 lượt; bỏ `--tools ''` cho task implement.

### P2 — Quy trình nhẹ
- Root chỉ còn: README, PROJECT_STATE (≤ 1 trang), NEXT, DECISIONS (ADR ngắn), FILM_LEARNINGS, CLAUDE.md.
- Gate nặng chỉ cho: chi tiền vượt ngưỡng, xóa dữ liệu, publish, đổi schema dữ liệu phim. Còn lại: branch → test → review chéo 1 vòng → merge.
- Task > 1 ngày không có delta sản phẩm → dừng, báo chủ dự án.
- Tranh luận 2 vòng cùng premise → chủ dự án quyết, không mở thêm review.
- Bài học phải có số liệu trước/sau; không đổi được hành vi trong 2 tuần → xóa.

## 6. Việc tiếp theo — CURRENT, không còn là resume proposal

Freeze đã đóng và pivot đã merge. Không chạy lại các bước archive/scaffold đã hoàn tất.

Canonical next batch trên `main`:
1. **T-008:** xây rental-GPU benchmark harness + model matrix + blind scoring rubric; chưa launch paid GPU nếu chưa có bounded budget.
2. **T-009:** cài/chuẩn bị ffmpeg + animatic path + EN/ZH/VI timing assets trên CPU.
3. Sau đó mới chạy MODEL-EVAL trên GPU thuê, chọn stack theo chất lượng/VRAM/throughput/license.
4. Tiếp M2 casting refs → M3 keyframes → M4 motion → M5 voice/lip-sync → M6 first film → M7 measured quality loop.

Cold start đúng hiện tại: `RESUME.md` → `BACKLOG.yaml` → `MILESTONES.md` → `CONTINUE_PROTOCOL.md` → `PROJECT_STATE.md` / `NEXT_WORK_ITEM.md`. Handoff này chỉ dùng để hiểu lịch sử và các finding đã dẫn tới pivot.

## 7. Không làm
- Không tiếp tục TEST_DESIGN 014 R2, prodlike attempt, authority/LAB/HKLM, native signing.
- Không xóa branch/worktree/evidence; chỉ tag + archive.
- Không mua GPU trước khi có kết quả benchmark trên GPU thuê (mục 12.10); không mua GPU thứ 2 trở đi trước khi có số đo sản xuất từ slice01 (Blueprint §36).
- Không dựng queue/distributed/Docker trước phim đầu tiên.
- Không thêm tài liệu quy trình mới trước khi có output phim.

## 8. Quyết định của chủ dự án — current interpretation

Đã chốt: short trước, 9:16 với đường 16:9, EN/ZH/VI, photoreal + 3D benchmark candidates, tự viết + chuyển thể, generation stack local/open-weight candidate, thuê GPU benchmark trước mua, thời lượng mục tiêu ≤3 phút.

Ba policy detail vẫn chưa có quyết định riêng biệt rõ ràng:
1. Human-in-the-loop chính xác bao nhiêu approval gates.
2. LLM viết kịch bản có bắt buộc local hay tiếp tục dùng ChatGPT/Claude.
3. Slice01 production style cuối cùng; hiện benchmark phải thử cả photoreal và 3D.

Việc chủ dự án cho phép “nếu handoff đúng thì triển khai không cần đợi” đã authorize pivot/product-v2 work, **không tự động đồng nghĩa với quyền publish, mua hardware hoặc chi GPU/API không giới hạn**.

## 9. Giới hạn của re-audit

- Re-audit này tái chứng minh các claim định lượng/cốt lõi bằng exact archive ref, runtime queue, local host và tests; **không đọc semantic từng dòng của toàn bộ 486 Markdown / 108 review**.
- 766 workspace tests và 101 static checks đã được rerun; lane validation full test suite không được rerun toàn bộ.
- `file/script/env` chỉ kiểm metadata 12 byte / 0600; content không mở.
- Chất lượng phim vẫn NOT_EVALUATED vì chưa có rendered media.
- Số “22.678 Desktop Commander commands / 59 sessions / 11 days” là reviewer-observed telemetry cũ; không re-verified và không dùng làm canonical productivity metric.
- Progress ≈2% và phase weighting là reviewer estimate.
- Model/license review đã đối chiếu lại nhiều upstream chính thức; exact checkpoint/dependency/dataset rights vẫn phải recheck khi MODEL-EVAL/publish.
- Handoff branch là historical review branch; canonical execution state nằm trên `main`.

## 10. Lệnh tái kiểm chứng

```bash
cd /home/dragon/ai-film-dev/repo
git fetch --all --prune
git rev-parse origin/main
git rev-parse archive/p00-governance-2026-09-24
sed -n '1,60p' PROJECT_STATE.md
sed -n '1,120p' RESUME.md
python3 tools/check_product_v2.py
PYTHONPATH=. python3 -m unittest discover -s tests/film -v

# P00 frozen baseline:
rm -rf /tmp/p00 && mkdir /tmp/p00
git archive origin/source/p00-dev22-local-authority-exact | tar -x -C /tmp/p00
cd /tmp/p00
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests /home/dragon/ai-film-dev/.venv/bin/python tools/run_workspace_tests.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests /home/dragon/ai-film-dev/.venv/bin/python tools/check_source.py

# Verify no scheduled P00 timer remains active:
systemctl --user list-timers --all --no-pager | grep aifilm-p00 || true
```

## 11. Cơ chế "Tiếp tục" — đánh giá và thiết kế v2

### 11.1 Legacy MD có biết trạng thái và việc tiếp theo không?

**Historical answer: Có về kỹ thuật, nhưng route tới process cursor thay vì product goal — CONFIRMED.**

Normalized 130 state JSON (hỗ trợ cả schema uppercase V12–V17 và lowercase sau đó):
- 130/130 phase = `00 — Host / WSL`.
- Mode counts: IMPLEMENTATION 43 · VALIDATION 33 · CODE_REVIEW 32 · TEST_REVIEW 9 · TEST_DESIGN 8 · DESIGN_REVIEW 2 · WORKFLOW_REVIEW 1 · DESIGN 1 · DOC_REVIEW 1.
- **70** unique normalized current tasks (bản cũ ghi 71).
- Task substring: PRODLIKE 52 · REVIEW 44 · RECON 17 · FILM 0.
- Dev23 task xuất hiện từ V76; **dev23 prodlike** xuất hiện từ V92 (23/09 11:54). Bản cũ gộp hai khái niệm này.
- Legacy router là bounded/single-mode và không có background execution nếu runtime riêng chưa deploy.

**Current answer:** PRODUCT_V2 đã thay route này; normal `Tiếp tục` đọc product backlog/milestones, không V144 current_work.

### 11.2 Vì sao legacy workflow nhiều lượt mà ít product delta

| Chỉ số | Re-audit |
|---|---|
| Desktop Commander 22.678 / 59 sessions / 11 days | REVIEWER_OBSERVED, **không re-verified** |
| dev22 accepted | V55, 18/09 12:46:11 +07 — CONFIRMED |
| dev23 | current task từ V76; dev23 prodlike từ V92 — corrected |
| V92→V144 | 52 state-version steps, prodlike cycle chưa accepted successor — CONFIRMED framing |
| 130-state modes | counts ở 11.1 — CONFIRMED |
| Legacy cold-start listed set | ~159.427 byte ≈155,7 KiB minimum; còn lane/contract-specific reads có thể tăng thêm. Bản cũ “170–210KB” không tái tạo được từ listed set |
| Current v2 cold-start core | ~4.074 byte; ~5.925 byte nếu cộng PROJECT_STATE+NEXT |
| Continuity productivity events | 0/3 persisted receipts in legacy — CONFIRMED |

Evidence hỗ trợ nguyên nhân workflow: single-mode routing, guard precedence, 111 state commits, fragmented authorization/attempt/reconciliation corpus, no film KPI và Claude bridge TEXT_REVIEW-only. Causal wording vẫn là analysis, không phải proof về một biến duy nhất.

### 11.3 Thiết kế "Tiếp tục v2" — lượt theo lô

**Implementation status:** L1 routing/control files đã được triển khai và merge. `turn_start.sh` + `turn_end.sh` đã smoke-test. Cold-start target đạt. Claude Code headless IMPLEMENT engine, paid wrapper và L2 background runner **chưa triển khai**; các đoạn dưới mô tả target design cho phần còn lại.

Nguyên tắc: mỗi lệnh "Tiếp tục" phải tạo **delta sản phẩm**. Chat điều phối và review; Claude Code headless là động cơ chạy dài; quy trình chỉ nặng ở chỗ rủi ro thật.

Thuật toán mỗi lượt:
1. `tools/turn_start.sh` (1 lệnh): `git fetch` + status, in RESUME.md, 5 task READY đầu BACKLOG, kết quả lô trước, ngân sách còn lại.
2. Có lô chưa review → review diff + log test (tối đa 1 vòng) → merge, hoặc tạo task sửa.
3. Chọn N task READY theo ưu tiên, vừa ngân sách lượt.
4. Thực thi: task code/asset → Claude Code headless (có tool, worktree riêng); task thiết kế/kịch bản → chat tự làm. Hai task độc lập chạy song song.
5. Task bị chặn → ghi `BLOCKED` + lý do + câu hỏi, chuyển task kế. Không mở vòng design mới cho thay đổi phạm vi nhỏ; ghi vào báo cáo lô.
6. Dừng khi: hết ngân sách lượt · cần chủ dự án quyết · mọi task còn lại bị chặn · chạm guard (chi tiền vượt trần, xóa dữ liệu, publish, sửa main).
7. `tools/turn_end.sh` (1 lệnh): cập nhật BACKLOG + RESUME + 1 dòng PROGRESS_LOG → 1 commit.
8. Báo cáo ≤ 6 dòng: đã xong, delta sản phẩm, test, chi phí, % milestone, việc kế, câu hỏi cho chủ dự án (0–3).

Bộ trạng thái v2 — target cold-start ≤10 KB; **đo hiện tại**: RESUME+BACKLOG+MILESTONES+CONTINUE_PROTOCOL ≈4.074 byte, hoặc ≈5.925 byte khi cộng PROJECT_STATE+NEXT. Ví dụ dưới đây vẫn là số liệu minh họa, không phải current state:

```markdown
# RESUME  (≤ 2 KB, ghi đè mỗi lượt)
GOAL: phim ngắn slice01 60–90s
MILESTONE: M3 Keyframe — 55% (11/20 shot đạt identity check)
LAST_TURN: #14 2026-09-25 — xong T-031, T-032; T-033 BLOCKED (chờ chọn giọng)
NEXT: T-034, T-035, T-036
CẦN CHỦ DỰ ÁN: chọn giọng cho Lan (3 mẫu trong projects/slice01/voice/casting/)
NGÂN SÁCH: tháng 120/300 USD · lượt ≤ 5 USD
KPI 10 LƯỢT: 3,2 task/lượt · 0 lượt không delta · 0,9 USD/task
```

```yaml
# BACKLOG.yaml — nguồn việc duy nhất
- id: T-034
  milestone: M3
  goal: "Keyframe sc02_sh03, 3 take, ref nhân vật An, state_at(D1_chieu)"
  accept:
    - "3 take trong projects/slice01/takes/sc02_sh03/"
    - "face similarity ≥ ngưỡng casting"
    - "manifest đủ trường provenance §3.4"
  owner: executor      # executor | coordinator | human
  status: READY        # READY | RUNNING | REVIEW | DONE | BLOCKED
  est_usd: 0.6
```

```json
{"turn":14,"ts":"2026-09-25T10:02+07:00","actor":"chatgpt+claude_code","done":["T-031","T-032"],"blocked":["T-033"],"delta":["projects/slice01/takes/sc01_*"],"tests":"42 pass","usd":3.1,"tool_calls":38,"minutes":24,"milestone":"M3 40→55%"}
```

MILESTONES.md: M0 host thực dụng · M1 kịch bản + shot list · M2 casting + continuity ledger · M3 keyframe đạt identity · M4 video clip · M5 giọng + lip-sync · M6 dựng + xuất phim đầu tiên · M7 vòng chất lượng A/B. Mỗi milestone là checklist; % = mục đã tick / tổng, in ra mỗi lượt.

Động cơ thực thi — Claude Code headless:
- Dùng lại khung `tools/dual_ai_text_bridge.py` (receipt, idempotency, trần budget), thêm profile IMPLEMENT: bật tool đọc/sửa/chạy lệnh trong worktree riêng, effort cao hơn, 30–60 lượt, budget theo task (vd 1–5 USD).
- Guardrail: chỉ ghi trong worktree `film/wip-*`; không push main; không đọc secrets; mọi API trả phí đi qua một wrapper có trần chi phí và ghi log; file `AUTOPILOT_STOP` là công tắc dừng.

Hai mức tự động:
- **L1: ACTIVE.** Mỗi "Tiếp tục" chạy một bounded product batch theo CONTINUE_PROTOCOL; turn scripts đã smoke-test.
- **L2: NOT ENABLED.** Nếu sau này cần runner nền, phải tạo dedicated Product-V2 timer + daily budget/stop guard riêng. Không tái sử dụng P00 timers; 11 scheduled P00 timers đã được disable+stop trong re-audit.

Tự cải thiện có đo (thay self-learning quy trình hiện tại):
- Mỗi 10 lượt: retro tự tính KPI (task/lượt, lượt không delta, USD/task, top lý do chặn) → đề xuất tối đa 3 thay đổi, mỗi thay đổi có KPI mục tiêu; 10 lượt sau không cải thiện → hoàn tác.
- Ngân sách độ phức tạp: tài liệu quy trình đang hiệu lực ≤ 30 KB; thêm 1 luật phải bỏ hoặc gộp 1 luật.
- Báo động: một task nằm ở "việc kế tiếp" 3 lượt liền → tự tách nhỏ hoặc hỏi chủ dự án.
- Bài học phim ghi vào FILM_LEARNINGS.md kèm số liệu trước/sau (vd "thêm ảnh tham chiếu trang phục: COSTUME_DRIFT 40% → 10% trên 20 shot").

Mục tiêu năng suất:
- ≥ 3 task hoàn thành mỗi lượt; không quá 1 lượt liên tiếp không có delta sản phẩm; mỗi 3–5 lượt qua một milestone.
- Cold-start ≤ 10 KB và ≤ 3 lệnh công cụ trước khi bắt đầu làm việc.

### 11.4 Chuyển đổi — trạng thái thực tế

1. Archive ref P00: **DONE**.
2. RESUME/BACKLOG/MILESTONES/PROGRESS_LOG/CONTINUE_PROTOCOL + turn scripts: **DONE**.
3. README/CLAUDE/WORKFLOW_ROUTER chuyển sang PRODUCT_V2: **DONE**.
4. Initial backlog + first product batch: **DONE**; M0/M1 complete.
5. Physical move legacy docs/state vào `archive/`: **không làm**, thay bằng immutable archive ref và active read-set nhỏ để tránh phá path/evidence.
6. P00 systemd timers: **11 timers found still scheduled during re-audit; now disabled+inactive**.
7. Claude implementation runtime: **PENDING**.
8. L2 autonomous timer runner: **NOT ENABLED**.

## 12. Quyết định chủ dự án (24/09/2026) và hệ quả kỹ thuật

### 12.1 Quyết định đã chốt

| Hạng mục | Quyết định | Hệ quả chính |
|---|---|---|
| Ngân sách API/GPU | Tạm thời không đặt trần chiến lược cho bài toán lựa chọn cấu hình | **Không phải quyền tự chi tiền.** Mọi thuê GPU, mua phần cứng hoặc API trả phí vẫn cần trần chi phí/phê duyệt cụ thể trước khi chạy; vẫn ghi điện, khấu hao, giờ GPU, token để tính giá/phút phim |
| Định dạng | 9:16 trước; làm hoặc chuyển sang 16:9 dễ dàng | Tỉ lệ khung là tham số render, không nằm trong kịch bản; timeline trung lập tỉ lệ (12.6) |
| Phong cách | Tả thực và 3D | Hai preset trong art bible; MODEL-EVAL thử cả hai |
| Ngôn ngữ | Đa ngôn ngữ; 3 ngôn ngữ đầu EN/ZH/VI; doanh thu kỳ vọng chủ yếu từ EN/ZH | Kịch bản master + bản địa hóa thoại; giọng nhân vật nhất quán xuyên ngôn ngữ; lip-sync theo từng ngôn ngữ (12.5) |
| Nguồn truyện | Tự viết (chủ dự án chỉ viết đại khái) và chuyển thể | SCRIPT_ENGINE 2 chế độ; chuyển thể có cổng bản quyền (12.7) |
| Model | Cục bộ (open weights) | Cần GPU — máy hiện không có (12.2); chỉ dùng model có license thương mại phù hợp (12.4) |
| Thời lượng | ≤ 3 phút, làm short trước | slice01 60–90s rồi mở rộng; phim 3 phút ≈ 36–60 shot |
| GPU | Thuê vài ngày để benchmark rồi mới mua | Chạy bộ benchmark trên các cấu hình ứng viên; sản xuất vẫn chạy cục bộ trên máy mua (12.10) |

Điểm còn mở — mặc định đề xuất, chờ xác nhận:
1. **Human-in-the-loop:** 3 điểm duyệt — (a) logline + kịch bản; (b) casting ngoại hình + giọng + khung hình phong cách; (c) bản dựng cuối từng ngôn ngữ. Mọi bước khác tự động, có auto-QC.
2. **"Cục bộ" cho LLM viết kịch bản?** Đề xuất: model tạo hình/video/giọng/nhạc chạy cục bộ; viết kịch bản và điều phối vẫn dùng ChatGPT/Claude như hiện tại.
3. **Phong cách slice01:** chọn sau MODEL-EVAL (cùng 5–10 shot, thử cả tả thực và 3D).
4. **Đường mua GPU — ĐÃ CHỐT (24/09):** thuê GPU 3–5 ngày để benchmark rồi mới mua (12.10).

### 12.2 Phần cứng hiện tại — tái đo 24/09

- Windows CPU: AMD Ryzen 9 9950X, 16 cores / 32 logical processors. WSL hiện được cap 24 logical processors.
- RAM host: ~61,6 GiB; WSL thấy ~47 GiB.
- GPU: Windows chỉ thấy `AMD Radeon(TM) Graphics`; WSL không có `nvidia-smi`. **Không có discrete NVIDIA GPU — CONFIRMED.**
- WSL root: 1007G, hiện còn khoảng **925G**; con số cũ “403GB free” đã stale.
- C: ~1,999 TB, còn ~1,162 TB decimal (~1,1 TiB class).
- Python 3.12.3.
- ffmpeg absent; Docker absent; PyTorch absent.
- Kết luận giữ nguyên: control/script/data work chạy được; local image/video generation chưa có practical NVIDIA path.

### 12.3 Kế hoạch GPU cục bộ — recommendation, không phải minimum đã chứng minh

Blueprint §36 “measure before purchase” vẫn hợp lý và đã được giữ.

- **Benchmark tier A:** 32 GB class, ví dụ RTX 5090 32GB. Đây là practical candidate để xem stack có fit với quantization/offload hay không, **không phải minimum tuyệt đối cho mọi model**.
- HunyuanVideo 1.5 upstream nêu khoảng 14 GB minimum với offload; Wan/LTX fit phụ thuộc exact checkpoint, precision, offload, resolution và runtime. Phải benchmark thay vì hard-code threshold.
- **Benchmark tier B:** 96 GB workstation class, ví dụ RTX PRO 6000 Blackwell 96GB, để đo lợi ích của ít offload/model concurrency.
- Separate native-Linux GPU worker, RAM ≥128GB và NVMe ≥4TB là architecture/capacity hypothesis, chưa phải purchase requirement.
- Nếu gắn GPU vào PC hiện tại: kiểm PSU/case/slot/thermal; RTX 5090 class có power envelope rất cao, nên sizing phải theo exact card.
- Chọn NVIDIA/CUDA là recommendation do ecosystem compatibility; mẫu cuối chỉ chốt sau benchmark.

### 12.4 Shortlist model mở cho MODEL-EVAL — upstream rechecked 24/09/2026

Các dòng dưới là **candidate shortlist, không phải production approval**. Apache/MIT/community license của upstream chính đã được tái đối chiếu cho các ứng viên chính; exact weights/dependencies/dataset/territory phải check lại lúc benchmark/publish.

| Nhóm | Ứng viên | License | Ghi chú |
|---|---|---|---|
| Video | Wan 2.2 (T2V-14B, I2V-14B, TI2V-5B) | Apache 2.0 | Weights/open license confirmed; VRAM fit không hard-code, đo theo precision/offload/workflow |
| Video | Wan-Animate-2 (Base/Distillation, 08/2026) | Apache 2.0 | Repo chính thức phát hành inference scripts + weights ngày 07/08/2026; hoạt họa nhân vật từ video tham chiếu. Kiểm exact checkpoint trước benchmark |
| Video | LTX-2.x (2.3/2.5) | LTX-2 Community; entity ≥10M USD annual revenue cần paid commercial license theo upstream terms | Audio + video; kiểm exact version/threshold terms tại benchmark |
| Video | HunyuanVideo 1.5 (8,3B) | Tencent Hunyuan Community: không áp dụng tại EU/UK/Hàn Quốc | Rủi ro khi phát hành toàn cầu → chỉ dùng sau review pháp lý |
| Ảnh/keyframe | Qwen-Image (bản đến 12/2025, gồm Edit), Z-Image, FLUX.2 klein-4B | Apache 2.0 | Tránh FLUX.2 dev/klein-9B (cần license thương mại) |
| Giọng | VoxCPM2 (2B, 30 ngôn ngữ gồm EN/ZH/VI, clone + voice design, 48 kHz) | Apache 2.0 | Ứng viên chính cho giọng xuyên ngôn ngữ |
| Giọng VI | VieNeu-TTS-v2 (0.3B, VI/EN) + v2-Turbo/GGUF cho CPU | Apache 2.0 | Model card chính thức ghi Apache-2.0; biến thể Turbo/GGUF được tối ưu CPU. Vẫn kiểm exact weights/dependencies trước dùng thương mại |
| Lip-sync | LatentSync (Apache 2.0), MuseTalk (MIT), InfiniteTalk (Apache 2.0) | như cột trước | Tránh Wav2Lip (cấm thương mại) |
| Nhạc | ACE-Step 1.5 (02/2026; Base/SFT/Turbo; exact checkpoint cần chốt khi benchmark) | MIT | Repo và model card chính thức ghi MIT; vẫn kiểm lại license của đúng weights/dependency được tải |

Luật license: kiểm đủ 3 lớp (code, weights, dataset huấn luyện); ghi license + phiên bản weights vào manifest mỗi asset; model không rõ license thì không dùng cho sản phẩm.
Runtime đề xuất: ComfyUI chế độ API trên GPU worker, bọc sau adapter của pipeline (Blueprint §19) để đổi model mà không đổi dữ liệu phim.

### 12.5 Pipeline đa ngôn ngữ
- Chủ dự án viết ý tưởng bằng ngôn ngữ nào cũng được; kịch bản master bằng EN; thoại được bản địa hóa (không dịch sát chữ) sang ZH (mặc định Quan thoại, chữ giản thể) và VI; độ dài câu giữa các ngôn ngữ lệch ≤ ~15% để giữ nhịp dựng.
- Hình là master chung; audio, phụ đề và lip-sync tách theo từng ngôn ngữ.
- Mỗi nhân vật một voice identity: kiểm nhất quán âm sắc xuyên ngôn ngữ và khác biệt giữa các nhân vật (speaker embedding).
- Chỉ lip-sync shot thấy rõ miệng đang nói; ưu tiên bố cục giảm nhu cầu lip-sync (qua vai, toàn cảnh, lời dẫn ngoài hình).
- Audio sinh kèm của LTX-2.x chỉ dùng cho SFX/ambience; thoại luôn là track riêng để đổi ngôn ngữ.
- Phụ đề: burn-in cho bản short, file phụ đề riêng cho YouTube; gắn nhãn nội dung AI theo quy định từng nền tảng/quốc gia khi đăng.

### 12.6 9:16 trước, 16:9 dễ dàng
- Tỉ lệ khung là tham số render; kịch bản, shot list, continuity ledger và timeline không phụ thuộc tỉ lệ.
- Mỗi shot có `framing_9x16` và `reframe_16x9` (gợi ý bố cục, vùng an toàn cho chữ/UI nền tảng).
- Bản 16:9: (a) chất lượng — render lại từ cùng spec/ref/seed; (b) nhanh — outpaint nền hoặc pillarbox mờ. Audio và timeline dùng lại toàn bộ.
- Master sinh ở độ phân giải dọc model hỗ trợ tốt (vd 720×1280) rồi upscale lên 1080×1920; chốt sau MODEL-EVAL.

### 12.7 Hai chế độ nguồn truyện
- **Tự viết:** vài dòng ý tưởng → 3 logline → chủ dự án chọn → story bible → beat sheet → kịch bản ≤ 3 phút (móc câu 3 giây đầu) → vòng phê bình/viết lại → shot list. Phần "sáng tạo thêm" được liệt kê riêng để chủ dự án duyệt nhanh.
- **Chuyển thể:** nhập chương truyện → phân tích nhân vật/sự kiện → chia tập ≤ 3 phút có móc cuối tập → kịch bản từng tập; story bible và continuity ledger dùng chung cả series.
- **Cổng bản quyền:** tác phẩm còn bản quyền phải có giấy phép bằng văn bản trước khi đăng; ghi quyền vào metadata project; thiếu quyền thì chặn publish.

### 12.8 Ước lượng tải GPU (công thức — thay bằng số đo thật)
GPU-giờ/phim ≈ số shot × số take × phút/take ÷ 60. Ví dụ giả định: 45 shot × 3 take × 8 phút ≈ 18 GPU-giờ cho một phim 3 phút, chưa tính lip-sync, upscale và 16:9. Đo thật ở slice01 để quyết định thêm GPU.

### 12.9 Việc chưa GPU — trạng thái hiện tại

**Đã làm:** PRODUCT_V2/L1, `film/` core, provenance manifest, continuity ledger, shot compiler, casting spec, 7 design contracts, original slice01 screenplay, 8-shot benchmark set, EN/ZH/VI dialogue fields, tests.

**Chưa làm / next:** 
- T-008 benchmark harness/model matrix/scoring.
- T-009 ffmpeg install/animatic/subtitle-timing path.
- CPU TTS experiment.
- actual image/video/keyframe/TTS/lip-sync outputs.
- exact MODEL-EVAL environment and paid rental execution.

Vì vậy current work có product delta thật nhưng vẫn chưa có first clip/media quality measurement.

### 12.10 Kế hoạch thuê GPU để benchmark (chiến lược đã chốt; **chưa thuê/chưa chi tiền**)

Current gate: T-008 phải tạo reproducible harness + fixed benchmark + scoring trước; sau đó mới chọn provider/config và bounded budget.

Mục tiêu: trong 3–5 ngày thuê, trả lời ba câu hỏi — (1) stack model nào cho slice01; (2) mua cấu hình GPU nào; (3) một phim 3 phút tốn bao nhiêu GPU-giờ.

Cấu hình thuê thử (tùy chợ GPU có sẵn, vd RunPod, Vast.ai, Lambda):

| Mức | Ví dụ GPU | Câu hỏi cần trả lời |
|---|---|---|
| A — 32 GB | RTX 5090 | Stack chính có chạy ổn (không OOM, tốc độ chấp nhận được) không? Nếu có → phương án gắn vào PC hiện tại |
| B — 96 GB | RTX PRO 6000 Blackwell | Nhanh và ổn định hơn bao nhiêu khi không phải offload? Chạy song song nhiều model được không? |
| Tham chiếu (tùy chọn) | GPU 48 GB hoặc 80 GB đang có trên chợ | Điểm giữa để nội suy chi phí/hiệu năng |

Chuẩn bị trước khi thuê (làm trên máy hiện tại, không tốn GPU):
- Bộ benchmark cố định: 5–10 shot từ kịch bản slice01, mỗi shot có spec + prompt + ảnh tham chiếu (nếu có); cả tả thực và 3D; 9:16 ở độ phân giải mục tiêu, thêm 1–2 shot 16:9.
- Câu thoại mẫu của từng nhân vật bằng EN/ZH/VI để thử giọng và lip-sync.
- `setup_gpu_worker.sh`: PyTorch → ComfyUI (chế độ API) → tải weights theo danh sách có ghi phiên bản + SHA-256. Dùng lại nguyên trạng khi mua máy.
- `run_benchmark.py`: chạy tự động model × shot × seed cố định; ghi thời gian, VRAM đỉnh, lỗi/OOM; lưu output + manifest.

Chạy (mỗi cấu hình 1–2 ngày):
1. Video: Wan 2.2 (TI2V-5B, I2V-14B), LTX-2.x; HunyuanVideo 1.5 chỉ chạy nếu review pháp lý cho phép.
2. Ảnh/keyframe + casting sheet: Qwen-Image, Z-Image, FLUX.2 klein-4B.
3. Giọng: VoxCPM2 (EN/ZH/VI, clone xuyên ngôn ngữ), VieNeu-TTS-v2 (VI).
4. Lip-sync: LatentSync, MuseTalk, InfiniteTalk trên cùng clip với audio 3 ngôn ngữ.
5. Nhạc: ACE-Step 1.5, 2–3 đoạn nền 30–60 giây.

Đo và chấm:
- Máy: giây/clip theo độ phân giải và độ dài, VRAM đỉnh, tỉ lệ lỗi/OOM, thời gian nạp model, chi phí thuê thực tế.
- Chất lượng: chủ dự án chấm 1–5 theo rubric (identity, chuyển động, độ tả thực/phong cách 3D, bám prompt, giọng, lip-sync) trên bản xem mù (ẩn tên model); ghi failure tag theo taxonomy §18.
- Đa ngôn ngữ: độ giống âm sắc của cùng nhân vật giữa EN/ZH/VI; độ khác biệt giữa các nhân vật.

Quyết định sau benchmark (ghi vào DECISIONS):
- Stack slice01: model tốt nhất mỗi khâu có license hợp lệ.
- Cấu hình mua: mức rẻ nhất chạy stack đã chọn ở độ phân giải mục tiêu mà không OOM và đạt thông lượng mục tiêu. Số GPU ≈ GPU-giờ/phim (12.8, số đo thật) × số phim mỗi tuần ÷ số giờ máy chạy mỗi tuần.
- Nghiệm thu máy mua: chạy lại `setup_gpu_worker.sh` và một phần bộ benchmark; kết quả phải khớp số đo lúc thuê.

Vệ sinh và rủi ro:
- Chỉ đưa lên máy thuê dữ liệu benchmark; không đưa truyện chưa có quyền hay secret không cần thiết; dùng SSH key riêng; xóa ổ khi trả máy.
- Tải toàn bộ output + log về `/home/dragon/ai-film-dev/benchmarks/<ngày>/` trước khi trả máy.
- License model áp dụng như nhau trên GPU thuê và GPU mua.
- Đây là ngoại lệ tạm thời chỉ để đo; sản xuất vẫn chạy cục bộ.

## 13. Ma trận tái audit toàn handoff — kết luận cuối

| Hạng mục | Verdict | Current disposition |
|---|---|---|
| P00 test/code identity | **CONFIRMED** | archived, reusable patterns kept |
| P00 native/HOST_READY formal gate incomplete | **CONFIRMED historical** | replaced by HOST_READY_PRACTICAL for Product V2; formal P00 not resumed |
| “MD became product” | **CONFIRMED factual basis** | active control plane reduced; legacy retained as evidence |
| Self-learning process-only / no film proof | **CONFIRMED** | FILM_LEARNINGS separated; no measured lesson yet |
| Repeated parser/workspace/feasibility gaps | **CONFIRMED from V70** | v2 simpler; effectiveness still needs future measurements |
| Claude role inversion | **FULLY CONFIRMED historical** | role intent corrected, implementation runtime still pending |
| 23% Claude task failure / ritualized workflow | **CONFIRMED** | L1 batching active; legacy bridge not used as product implementer |
| 1,96h Claude API duration | **CORRECTED** | direct provider sum ~1,76h |
| ~106 DOCUMENTATION_SYSTEM files | **CORRECTED** | 38 literal DOCUMENTATION_SYSTEM + 68 related criteria = 106 governance-family docs |
| 71 tasks / REVIEW 40 | **CORRECTED** | 70 unique normalized tasks; REVIEW substring 44 |
| dev23 begins V92 | **CORRECTED** | dev23 task starts V76; dev23 prodlike starts V92 |
| cold start 170–210KB | **CORRECTED** | listed legacy minimum ~155,7KiB; v2 core ~4,1KB |
| P00 systemd supervision still running | **NEW GAP FOUND + CLOSED** | 11 scheduled P00 timers disabled+inactive |
| Historical no film code/output | **CONFIRMED at archive** | code/data now exist; media output still none |
| 7 proposed film design docs | **IMPLEMENTED initial versions** | advanced media QC/casting/voice still pending |
| Continue v2 L1 | **IMPLEMENTED** | active router |
| Continue v2 L2 | **NOT IMPLEMENTED** | keep off unless explicitly needed |
| Claude headless IMPLEMENT profile | **NOT IMPLEMENTED** | one of remaining system gaps |
| Hardware: no NVIDIA GPU | **CONFIRMED** | GPU MODEL-EVAL blocked pending rental |
| 32GB “minimum” | **NOT CONFIRMED as universal minimum** | treat as benchmark tier |
| Model shortlist/license | **PARTIALLY/mostly CONFIRMED upstream** | exact checkpoint/dependency/territory review at MODEL-EVAL |
| ≈2% project / P00≈65% | **ESTIMATE ONLY** | do not use as current KPI |
| Root-cause ordering | **ANALYSIS supported by evidence** | not a mathematically proven causal ranking |
| Product-first pivot | **SUPPORTED + IMPLEMENTED** | main PRODUCT_V2_001, M0/M1 done |
| First commercial-quality film | **NOT YET PROVEN** | current work T-008/T-009 → M2 onward |

### 13.1 Sẵn sàng quay lại công việc?

**YES, với phạm vi chính xác:** handoff hiện đủ tin cậy để làm forensic context; canonical execution phải tiếp tục từ PRODUCT_V2 `RESUME/BACKLOG/MILESTONES/NEXT`, không từ P00 V144. Không còn blocker governance nào yêu cầu quay lại TEST_DESIGN 014 R2.

Những gap còn lại là product work thật: benchmark harness, ffmpeg/animatic, GPU MODEL-EVAL, casting refs, generation, audio/lip-sync, edit/QC và measured FILM_LEARNINGS. Claude implementation runtime là system-efficiency gap riêng; nó không được phép chặn T-008/T-009 nếu ChatGPT/available tools có thể hoàn thành an toàn.

## Phụ lục A — Yêu cầu Blueprint cần mang sang thiết kế phim

- **Ưu tiên chất lượng (§3.1):** Story → Visual → Character consistency → Motion → Audio → Dialogue → Editing → Continuity → Reproducibility → Performance/cost.
- **Nhân vật (§3.2):** identity ổn định (face, body, age, hair, proportions). Được đổi có chủ đích: costume, makeup, hairstyle, emotion, injuries, lighting, aging theo truyện. IDENTITY ≠ COSTUME ≠ EXPRESSION ≠ LIGHTING.
- **Continuity (§3.3):** character, costume, location, prop, story, time, lighting, camera, dialogue.
- **Provenance mỗi asset (§3.4):** model, model version/hash, prompt, negative prompt, seed, references, workflow version, config, worker, GPU, generation time, parent asset.
- **Shot (§16):** shot_id, characters, location, camera (framing, lens, movement), lighting, action, dialogue, continuity (previous/next shot), references (character, costume, location, previous frame).
- **Take (§17):** N take/shot → QC → ranking → approved take.
- **Failure taxonomy (§18):** FACE_DRIFT, BODY_DRIFT, HAIR_DRIFT, AGE_DRIFT, COSTUME_DRIFT, LOCATION_DRIFT, BAD_HAND, BAD_MOTION, CAMERA_ERROR, LIP_SYNC_ERROR, VOICE_EMOTION_ERROR, TEMPORAL_FLICKER, LOW_REALISM, BAD_EDIT.
- **Nguyên nhân lỗi chất lượng (mode QUALITY_ANALYSIS):** MODEL_LIMITATION, PROMPT, REFERENCE, IDENTITY_CONTROL, TEMPORAL_VIDEO, AUDIO, POSTPROCESS, IMPLEMENTATION, UNKNOWN.
- **Mẫu thí nghiệm (§31):** EXPERIMENT_ID, QUALITY_PROBLEM, BASELINE, HYPOTHESIS, VARIABLE_CHANGED, VARIABLES_FIXED, INPUT_SET, METRIC, HUMAN_REVIEW, RESULT, DECISION.
- **Chi phí (§34):** cost_per_shot, cost_per_scene, cost_per_minute, cost_per_episode, accepted_take_ratio.
- **Thương mại (§35):** model license, API terms, voice rights, music rights, dataset provenance, character/IP rights, generated content policies, distribution platform policies.
- **Mua phần cứng (§36):** chỉ sau khi có số đo thật (VRAM, RAM, storage, throughput, chi phí GPU thuê).

## Phụ lục B — Backlog F01–F07: giữ gì cho vertical slice

| Mục | Nội dung | Cho slice |
|---|---|---|
| F01 | State machine tách project/episode/scene/shot/take, job/attempt, asset, release | Chỉ giữ shot/take + selection revision bất biến |
| F02 | Retry, idempotency, UNKNOWN_OUTCOME sau timeout, ngân sách | Giữ generation key + trần chi phí/project; không retry mù khi gọi API trả tiền |
| F03 | Asset graph, invalidation có chọn lọc | Manifest có parent refs; đổi thoại → chỉ làm lại voice/lip-sync |
| F04 | Trạng thái nhân vật/thế giới + prompt compiler | Cốt lõi (CONTINUITY_LEDGER + SHOT_COMPILER) |
| F05 | Queue, bộ nhớ GPU, chi phí | Hoãn đến khi có số đo |
| F06 | Học chất lượng phim (champion/challenger, eval set) | Bật ngay sau phim đầu tiên |
| F07 | Bảo mật, bản quyền, publication | Checklist rights trước khi đăng |
