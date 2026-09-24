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

## Trạng thái freeze và thẩm quyền của handoff

**REVIEW_FREEZE: ACTIVE.** Ở lượt này chỉ đọc, đối chiếu và chỉnh file handoff trên nhánh riêng. Không sửa `main`, `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md`, source, validation lane, queue/runtime hay máy local.

File này là **snapshot review + bàn giao**, không phải execution authority. Khi đọc, phân loại mọi nội dung theo ba mức:
- **VERIFIED_GITHUB_SNAPSHOT:** sự kiện/trạng thái đã đối chiếu trực tiếp trên GitHub tại mốc 24/09/2026; có thể dùng làm mốc lịch sử nhưng phải `git fetch` và kiểm lại trước khi resume.
- **REVIEWER_OBSERVED:** số đo/quan sát trên máy hoặc runtime do reviewer trước ghi nhận; ChatGPT hiện tại chưa tái đo local thì không được tự nâng thành fact mới.
- **ESTIMATE / RECOMMENDATION / PROPOSED DESIGN:** phần trăm tiến độ, nguyên nhân gốc, pivot, kiến trúc v2, shortlist/hardware và các bước ở mục 5–6/11–12 là đề xuất để chủ dự án quyết, không tự động được thi hành.

Trong lúc freeze, **không chạy lệnh `Tiếp tục.` để thực thi workflow**. Với `main` hiện hành, lệnh đó vẫn sẽ route tới `REVISE-TEST-DESIGN-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014-R2`; handoff này chưa thay router hay state. Chỉ resume sau khi chủ dự án nói rõ hướng cần tiếp tục.

Các quyết định đã ghi ở mục 12.1 vẫn là ràng buộc thiết kế đã được chủ dự án nêu, nhưng **không tự cấp quyền chi tiền, merge, publish, xóa dữ liệu, bật runner nền hay thay `main`**. Mọi hành động loại đó cần lệnh/phê duyệt cụ thể tại thời điểm thực hiện.

## 0. Tóm tắt 60 giây

- Mục tiêu (Blueprint): AI Film Production Server chất lượng thương mại (YouTube/TikTok/Facebook, short/long-form, chuyển thể truyện).
- Thực trạng: CHƯA có output phim nào (không ảnh, không video, không giọng). Công sức ~10 ngày dồn vào Phase 00 "Host/WSL" và hệ quản trị tài liệu.
- Phase 00 chưa qua HOST_READY: 86 case native NOT_RUN, LAB/SITE NOT_RUN, qualification NOT_ISSUED.
- Thực tế máy đã đủ dùng: WSL có systemd user (46 unit, 11 timer đang chạy), Python 3.12 venv, git ↔ GitHub, Claude CLI đã chạy 322 task, đã qua Windows update + reboot.
- Code P00 đúng như công bố: chạy lại độc lập 766 test, 0 fail/error/skip, digest khớp. Vấn đề nằm ở mục tiêu và phạm vi, không phải tay nghề.
- Tiến độ ước tính: làm phim 0% · toàn dự án ≈ 2% · Phase 00 ≈ 65% (theo gate của nó).
- Đề xuất của reviewer (chưa phải lệnh thực thi): freeze Phase 00 → vertical slice phim 60–90s trong 2 tuần → quy trình nhẹ → Claude Code implement có tool.
- TRẠNG THÁI MAIN: nếu dùng "Tiếp tục." với state hiện hành, router vẫn trỏ tới `REVISE-TEST-DESIGN-P00-DEV23-PRODLIKE-RELEASE-CONTROL-014-R2` (tiếp vòng Phase 00). Trong REVIEW_FREEZE không dùng lệnh này.
- "Tiếp tục" hiện chỉ chạy 1 bước quy trình mỗi lượt và không đo năng suất; thiết kế v2 (mục 11) chuyển sang lượt theo lô có backlog sản phẩm, KPI mỗi lượt và Claude Code headless làm động cơ chạy dài.
- Chủ dự án đã chốt (24/09): 9:16 trước (dễ ra 16:9), ≤ 3 phút, tả thực + 3D, 3 ngôn ngữ EN/ZH/VI (doanh thu chủ yếu EN/ZH), tự viết + chuyển thể, model cục bộ; chưa đặt trần chiến lược cho lựa chọn GPU/API nhưng mọi khoản chi cụ thể vẫn cần phê duyệt/trần chi phí — xem mục 12.
- Máy hiện tại KHÔNG có GPU rời (chỉ iGPU AMD). Đã chốt: thuê GPU 3–5 ngày để benchmark model mở rồi mới mua cấu hình phù hợp (mục 12.10); trong lúc chuẩn bị vẫn làm được kịch bản, ledger, dựng, TTS tiếng Việt trên CPU (mục 12.9).

## 1. Bản đồ nguồn (đã xác minh)

| Hạng mục | Vị trí | Ghi chú |
|---|---|---|
| Repo | github.com/darkdragonstudioonlyme-commits/ai-film | `origin/main` = `15f27a0` (2026-09-24 18:23 +07) |
| Clone local | /home/dragon/ai-film-dev/repo | main local = `fa0891f` (V72), behind 71 commit → dùng `origin/main` sau `git fetch` |
| Blueprint gốc | package-dev22/source/contracts/AI_VIDEO_SERVER_SINGLE_CHAT_WORKFLOW_BLUEPRINT_V2.md | 2.371 dòng; phần sản phẩm: mục 1–3, 11–19, 31–36, 46 |
| Thiết kế Phase 00 | contracts/PHASE00_INFRA_DESIGN_V2.md + ACCEPTANCE_MATRIX, FAILURE_RECOVERY_PLAN, EVIDENCE_REGISTER | 7 file contracts = 3.369 dòng / 172 KB |
| Source sản phẩm | branch `origin/source/p00-dev22-local-authority-exact` (86bb649…) | `aifilm_p00`: src 8.130 dòng, tests 4.069 dòng; cả branch 12.775 dòng .py |
| Lane validation | `origin/lane/validation-p00` (4850b4d, 24/09 18:05) | 478 file; 7.628 dòng Python; ~913 KB MD |
| State hiện hành | origin/main: PROJECT_STATE.md (V144), NEXT_WORK_ITEM.md | PHASE "00 — Host / WSL", MODE TEST_DESIGN, BLOCK 057 |
| Thiết kế phim duy nhất | origin/main: docs/FILM_PIPELINE_DESIGN_BACKLOG.md | 73 dòng, F01–F07, PLANNING_BACKLOG_NOT_IMPLEMENTATION_AUTHORITY |
| Dual-AI | docs/DUAL_AI_COLLABORATION.md, docs/DUAL_AI_AUTOMATIC_HANDOFF.md, CLAUDE.md, tools/dual_ai_text_bridge.py | runtime: /home/dragon/ai-film-dev/dual-ai-queue (322 task) |
| Self-learning | SELF_LEARNING.md, learning/LEARNING_STATE.json, learning/measurements/ | 18 bài học |
| Tự audit gần nhất | docs/DOCUMENTATION_SYSTEM_R9_V70_EFFECTIVENESS_AUDIT.md | IMPROVEMENT_NOT_PROVEN |
| Workspace | /home/dragon/ai-film-dev | 38 worktree ẩn `.wt-*` + hàng chục thư mục docs-*/validation-*/package-dev*/source-dev*; ~364 remote branch |
| File bàn giao này | Máy: /home/dragon/ai-film-dev/handoffs/HANDOVER_REVIEW_2026-09-24.md · GitHub: branch `handover/review-2026-09-24`, file `handoffs/HANDOVER_REVIEW_2026-09-24.md` | Bản máy nằm ngoài git repo; bản GitHub ở branch riêng, không đụng `main` |

## 2. Số liệu then chốt

| Chỉ số | Giá trị |
|---|---|
| Thời gian | Thiết kế P00 từ 14/09; repo từ 15/09 07:40 → 24/09 |
| Commit trên main | 529 (theo ngày 15→24/09: 119·107·89·112·18·24·26·34) |
| Loại commit | docs(r9) 178 · state 111 · docs 35 · review(r9) 24 · audit(r9) 24 · docs(r8) 14 · review 13 · learning(r9) 12 … |
| Phiên bản state | V12 → V144 |
| Control plane (main) | 723 file; 486 MD = 1,18 MB; 212 JSON = 3,47 MB |
| docs/ | 110 file: ~106 DOCUMENTATION_SYSTEM_*/tiêu chí review-audit, 2 dual-AI, 1 Phase00, 1 phim |
| Review / health / test-governance | 108 / 44 / 22 hồ sơ |
| Package P00 | dev1 → dev22 (accepted), dev23 đang làm |
| Test P00 | 766 PASS / 0 fail / 0 error / 0 skip — chạy lại độc lập 24/09 trên bản archive sạch; digest source `69fdc184…`, test `47d4ae76…` khớp PROJECT_STATE. Static check (101) chưa chạy lại |
| Native validation | 86 case NOT_RUN; LAB/SITE NOT_RUN; HOST_READY NOT_EVALUATED |
| Claude bridge (22/09 17:10 → 24/09 18:01) | 322 task · 70,82 USD · 1,96 giờ API · 74 FAILED (72 chạm trần budget, 2 hết lượt) · 172 PASS / 75 FINDINGS · 195 finding · 248 receipt ở RESULT_UNREVIEWED (bridge không tự promote) |
| Bài học tự học | 18 (10 EFFECTIVE, 6 INEFFECTIVE, 2 PENDING) — 0 bài về phim; continuity 0/3 |
| Code làm phim | 0 dòng trong các nhánh đã kiểm; `file/script` chỉ có 1 file `env` 12 byte, quyền 600 (không mở) |

## 3. Đánh giá chi tiết

### 3.1 Thiết kế có tạo được phim thương mại chất lượng?

Kết luận: **Chưa.** Đúng hướng ở tầm nhìn, trống ở mọi phần quyết định chất lượng.

| Tiêu chí | Blueprint/Backlog có gì | Thiếu gì | Đã code? |
|---|---|---|---|
| Kịch bản tốt | "Story quality" ưu tiên #1; Story Bible → Screenplay | Cấu trúc truyện, beat sheet, hook, arc nhân vật, vòng critique, rubric chấm, format theo nền tảng | Không |
| Giữ tình tiết/tình huống | Continuity list; F04 story-time, flashback | Schema continuity ledger, validator | Không |
| Áo quần, vết thương, đạo cụ | IDENTITY ≠ COSTUME; injuries là thay đổi có chủ đích; F04 theo dõi injury/prop | Mô hình sự kiện theo thời gian truyện, QC so khung hình với ledger | Không |
| Hình ảnh đẹp | Quality priorities; upscale/restore; LOW_REALISM | Art/style bible, chọn model, workflow keyframe → video | Không |
| Đa dạng diễn viên | face/body refs, LoRA/reference | Casting đảm bảo nhân vật khác nhau rõ; kiểm tra face embedding | Không |
| Voice chất lượng, đa dạng | voice profile, TTSAdapter, VOICE_EMOTION_ERROR, LIP_SYNC_ERROR; F04 pronunciation | Casting giọng, từ điển phát âm tiếng Việt, tag cảm xúc từng câu, kiểm tra khác biệt giọng, mix/loudness | Không |
| Càng làm càng hay | §18 loop + failure taxonomy; §31 experiment; F06 champion/challenger | Eval set, lưu điểm take, A/B chạy thật | Không |
| Thương mại | §35 rights checklist; §34 cost; F07 publication | Chính sách gắn nhãn nội dung AI của nền tảng (kiểm lại lúc đăng), đo retention, mục tiêu cost/phút | Không |

Phần mô tả phim chiếm khoảng 1/5 Blueprint; còn lại là mode/state machine/prompt vận hành.

### 3.2 Source có bám thiết kế?

- **Phase 00: có.** Có TRACEABILITY.md/json, code review PASS, test governance; test chạy lại độc lập đều pass. Chưa đối chiếu độc lập từng yêu cầu.
- **Tinh thần Blueprint: lệch.** §20–21 chỉ cần WSL2 → Ubuntu → systemd → Docker với script preflight/dry-run/apply/verify/support-bundle. Thực tế đã thêm:
  - host admission guard, durable fence;
  - authority envelope có chữ ký, trust anchor;
  - LAB/SITE qualification, 86 case native;
  - prodlike deployment (11 timer/46 unit systemd user);
  - DR rehearsal, off-host export, CI credential isolation.
- Mâu thuẫn với chính dự án: mode DESIGN_REVIEW (§23) coi over-engineering là lỗi; backlog phim ghi "use the simplest deployment that satisfies the measured load".
- **Toàn Blueprint (15 phase): 0% phần làm phim.** Không có module story/screenplay/shot/character/image/video/TTS/lipsync/edit/QC.

### 3.3 Hệ MD, self-learning, phối hợp ChatGPT–Claude

Nên giữ:
- Git là bộ nhớ; cold-start rõ.
- Cấm PASS giả; nhãn NOT_RUN/NOT_PROVEN.
- Provenance SHA-256.
- Backlog F01–F07, taxonomy lỗi phim §18, mẫu QUALITY_EXPERIMENT §31, checklist thương mại §35 (tóm tắt ở Phụ lục A, B).

Vấn đề:
1. **Hệ MD thành sản phẩm.** ~106 file thiết kế/tiêu chí của chính hệ tài liệu. Mỗi sửa đổi đi DOC-DESIGN → DOC-REVIEW → DOC-AUDIT với branch riêng; 144 state trong 10 ngày. V70 tự đếm: V61→V69 có 25 commit, 8 lần đổi state, source sản phẩm không đổi.
2. **Self-learning học sai đối tượng.** 18 bài học đều về quy trình (activation, lifecycle, CI credential, key parity, prodlike supervision…). 6/18 INEFFECTIVE theo chính metric; continuity 0/3. SELF_LEARNING.md tự thừa nhận register quy trình không chứng minh phim tốt lên.
3. **MD có tự sửa nhưng không tự tốt lên.** Chỉ có chiều thêm (luật, gate, checker, criteria); không có ngân sách độ phức tạp, cơ chế xóa/gộp, metric sản phẩm. V70 ghi nhận:
   - lỗi lặp khi parse JavaScript/backtick;
   - tạo lại workspace không an toàn;
   - gap khả thi lọt qua review (TEST_CHANGE 005).
4. **Phân vai bị đảo.**
   - Thiết kế: ChatGPT điều phối/kiến trúc/review; Claude implement/debug/test.
   - Thực tế (`tools/dual_ai_text_bridge.py`): `--tools ''`, `--effort low`, `--model sonnet`, `--safe-mode --restricted`; task bắt buộc profile TEXT_REVIEW, role REVIEW/AUDIT; `max_turns != 2` bị từ chối (`TEXT_REVIEW_LIMITS`); task mẫu budget 0,25 USD; execution_scope STATIC_ONLY.
   - Claude chỉ soát tĩnh diff/biên nhận Phase 00; thiết kế, code, state do ChatGPT viết.
5. **Phối hợp nặng nghi thức.**
   - 23% task Claude thất bại (tiền mất, không kết quả).
   - Nhiều vòng cho từng "authorization 002/003", "attempt 004/005", "reconciliation 002 corrected".
   - Luật "tối đa 2 vòng cùng premise" lại thoát ra bằng thêm một WORKFLOW_REVIEW.

### 3.4 Chất lượng code và tiến độ

Code:
- Điểm tốt: cục bộ cẩn thận (ghi nguyên tử + fsync, JSON strict chặn key trùng, ràng buộc SHA-256, idempotency receipt). Chạy lại độc lập: 766/766 test pass, digest khớp. Có thể tái dùng pattern cho asset manifest phim (xem `atomic_json`, `strict_json_bytes` trong `tools/dual_ai_text_bridge.py`).
- Điểm yếu: độ phức tạp không tương xứng mục tiêu, khóa chặt vào artifact governance.
- Ví dụ block 057: thêm `package_name/wheel_name/app_file_count` làm 22 test cũ hỏng; file fixture ngoài allowlist → quay lại TEST_DESIGN R2.

Tiến độ (trọng số là ước lượng của reviewer):

| Phase | Trọng số | Hoàn thành | Đóng góp |
|---|---|---|---|
| 00 Host/WSL | 3% | ~65% (author + code review xong, native NOT_RUN) | ~2,0% |
| 01 Linux bootstrap | 3% | 0% chính thức (thực tế đã có systemd, venv) | 0 |
| 02 Core services | 8% | 0 | 0 |
| 03 Job engine | 7% | 0 | 0 |
| 04 GPU abstraction | 4% | 0 | 0 |
| 05 Remote GPU | 5% | 0 | 0 |
| 06 Basic generation | 10% | 0 | 0 |
| 07 Character | 10% | 0 | 0 |
| 08 Scene/Shot | 10% | 0 | 0 |
| 09 Audio | 8% | 0 | 0 |
| 10 Episode | 8% | 0 | 0 |
| 11 Novel adaptation | 8% | 0 | 0 |
| 12 Quality loop | 8% | 0 | 0 |
| 13 Local GPU | 4% | 0 | 0 |
| 14 Multi-GPU | 4% | 0 | 0 |
| **Tổng** | 100% | | **≈ 2%** (tối đa +1% nếu tính thiết kế sơ bộ) |

## 4. Nguyên nhân gốc

1. Blueprint đặt quy trình trước sản phẩm: mọi việc, kể cả nhỏ, phải đi DESIGN → REVIEW → IMPLEMENT → REVIEW → VALIDATE.
2. Mô hình "một chat tự review như team khác" thiếu độc lập → bù bằng thêm tầng review/audit → đệ quy.
3. Phase 00 được định nghĩa như hạ tầng doanh nghiệp (LAB/SITE, authority, qualification) cho một máy cá nhân.
4. Không có metric sản phẩm → hệ thống tối ưu thứ đo được (gate PASS, số record).
5. "Không nới strictness" + "mọi đổi phạm vi phải qua TEST_DESIGN" → mỗi bước nhỏ sinh một vòng.
6. Claude bị khóa tool → vai implementer bỏ trống, ChatGPT gánh hết.

## 5. Khuyến nghị của reviewer (theo ưu tiên — chưa phải execution authority)

### P0 — Dừng chảy máu (1 ngày)
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

## 6. Việc chat tiếp theo nên làm sau khi chủ dự án gỡ freeze / chọn hướng

**Trong REVIEW_FREEZE hiện tại: không thực hiện các bước dưới đây.** Đây là resume plan đề xuất, không phải continuation tự động.

1. `git -C /home/dragon/ai-film-dev/repo fetch`; đọc file này + PROJECT_STATE.md trên origin/main. Không `git pull` đè WIP; kiểm `git status` các worktree trước.
2. Đọc quyết định đã chốt (mục 12.1); xác nhận 3 điểm còn mở (mục 8).
3. Tạo tag archive (xin xác nhận trước khi push).
4. Viết + chạy script `HOST_READY_PRACTICAL`; lưu kết quả.
5. Tạo branch `film/vertical-slice-01`; scaffold package `film/` + `projects/slice01/`.
6. Viết kịch bản slice01 (SCRIPT_ENGINE bản đầu) và chọn 5–10 shot làm bộ benchmark → trình cấu hình thuê + trần chi phí để chủ dự án duyệt → thuê GPU theo mục 12.10 → chốt stack model + cấu hình GPU mua → trình cấu hình/giá để chủ dự án duyệt → mua, cài đặt, chạy lại bộ benchmark để nghiệm thu. Trong lúc chuẩn bị, làm các việc ở mục 12.9 đã được phê duyệt.
7. Viết 7 tài liệu thiết kế phim ngắn → build: script → ledger → casting → keyframe → video → voice → edit → QC.
8. Ra phim đầu tiên; chấm điểm; ghi FILM_LEARNINGS đầu tiên có số liệu.

Chỉ nếu chủ dự án phê duyệt pivot + giao thức v2: làm mục 11.4 cùng lúc với bước 3–4 để mọi lượt sau đều có KPI. Nếu chưa có phê duyệt đó, giữ nguyên router/state hiện hành.

File này **đã** nằm trên GitHub ở branch riêng `handover/review-2026-09-24`. Mọi hiệu đính handoff tiếp theo tiếp tục ở branch này; không merge/commit vào `main` trong REVIEW_FREEZE.

**Resume prompt mẫu — chỉ dùng sau khi chủ dự án phê duyệt pivot:**

```text
Đọc /home/dragon/ai-film-dev/handoffs/HANDOVER_REVIEW_2026-09-24.md (hoặc GitHub branch handover/review-2026-09-24, file handoffs/HANDOVER_REVIEW_2026-09-24.md; ưu tiên phần freeze, mục 0, 11, 12). Không tiếp tục vòng P00 dev23/prodlike.
Mục tiêu: phim ngắn ≤ 3 phút, master 9:16, EN/ZH/VI, model cục bộ. Bắt đầu: xác nhận 3 điểm mở (mục 8), làm 11.4 và 12.9, chuẩn bị benchmark GPU thuê (mục 12.10).
```

## 7. Không làm
- Không tiếp tục TEST_DESIGN 014 R2, prodlike attempt, authority/LAB/HKLM, native signing.
- Không xóa branch/worktree/evidence; chỉ tag + archive.
- Không mua GPU trước khi có kết quả benchmark trên GPU thuê (mục 12.10); không mua GPU thứ 2 trở đi trước khi có số đo sản xuất từ slice01 (Blueprint §36).
- Không dựng queue/distributed/Docker trước phim đầu tiên.
- Không thêm tài liệu quy trình mới trước khi có output phim.

## 8. Quyết định của chủ dự án

Đã chốt ngày 24/09/2026 — chi tiết và hệ quả ở mục 12.1. Còn mở 3 điểm (mặc định đề xuất ở 12.1):
1. Human-in-the-loop (mặc định: 3 điểm duyệt).
2. "Cục bộ" có áp dụng cho LLM viết kịch bản không (mặc định: không — kịch bản và điều phối vẫn dùng ChatGPT/Claude).
3. Phong cách cho slice01: tả thực hay 3D (mặc định: chọn theo kết quả MODEL-EVAL).

Đã chốt thêm (24/09): thuê GPU vài ngày để benchmark rồi mới mua (mục 12.10).

## 9. Giới hạn của review
- Reviewer ban đầu không sửa working tree, `main`, lane hay state của dự án; đã ghi bản handoff local ngoài repo, các thư mục tạm dưới đây và branch `handover/review-2026-09-24`. ChatGPT lượt 7 chỉ hiệu đính **cùng file handoff trên branch đó**. So sánh branch với `main` có đúng một changed path: `handoffs/HANDOVER_REVIEW_2026-09-24.md`; base/merge-base vẫn là `15f27a0`.
- Thư mục tạm có thể xóa: /tmp/aifilm-review-main, /tmp/aifilm-review-val, /tmp/aifilm-review-src, log /tmp/aifilm-review-tests.log.
- Đã xác minh độc lập: 766 test workspace. Chưa chạy lại: static check 101, test của lane validation, test trong tools/ trên main.
- Chưa đọc hết 486 MD và 108 review, chưa đọc từng dòng code, chưa kiểm các worktree ẩn (có thể chứa WIP — không được xóa).
- Không mở `file/script/env` (quyền 600, có thể là secret).
- Không đánh giá được chất lượng phim vì chưa có output.
- Không có lịch sử chat ChatGPT; nhận định về vai trò dựa trên repo, bridge và queue.
- Shortlist model/license ở mục 12.4 dựa trên tra cứu web ngày 24/09/2026 (có nguồn bên thứ ba); phải đọc license gốc trước khi dùng thương mại.

## 10. Lệnh tái kiểm chứng
```bash
cd /home/dragon/ai-film-dev/repo && git fetch
git log origin/main --oneline | wc -l
git log origin/main --format='%s' | awk '{print $1}' | sort | uniq -c | sort -rn | head
git show origin/main:PROJECT_STATE.md | sed -n '1,40p'
git show origin/main:learning/LEARNING_STATE.json | python3 -m json.tool | less
ls /home/dragon/ai-film-dev/dual-ai-queue | wc -l
# Chạy lại test P00 trên bản sạch (không đụng worktree):
rm -rf /tmp/p00 && mkdir /tmp/p00 && git archive origin/source/p00-dev22-local-authority-exact | tar -x -C /tmp/p00
cd /tmp/p00 && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests /home/dragon/ai-film-dev/.venv/bin/python tools/run_workspace_tests.py | tail -3
```

## 11. Cơ chế "Tiếp tục" — đánh giá và thiết kế v2

### 11.1 MD hiện tại có biết trạng thái và việc tiếp theo không?

**Có, về mặt kỹ thuật.**
- `PROJECT_STATE.md`, `NEXT_WORK_ITEM.md` và `current_work` trong JSON V144 nêu chính xác run, bước, người làm, lộ trình khi thành công/thất bại/bị chặn và điểm quay lại.
- `WORKFLOW_ROUTER.md` có thuật toán "Continue" 10 luật; README khai báo "Tiếp tục." là lệnh tối thiểu; V70 đã thêm checker chống lệch CURRENT_TASK.

**Nhưng nó chỉ biết bước quy trình kế tiếp, không biết đích sản phẩm.**
- 130/130 bản state JSON đọc được đều ở Phase "00 — Host / WSL"; 71 task khác nhau, từ khóa nhiều nhất PRODLIKE (52), REVIEW (40), RECON (17); không task nào về phim.
- Mỗi lượt là "bounded turn", "route exactly one active mode", chạy tuần tự; router ghi rõ không có hoạt động nào khi không có lệnh gọi hoặc runtime triển khai riêng.
- Clone local đang chậm 71 commit; chat nào quên `git fetch` sẽ đọc state cũ.

### 11.2 Vì sao nhiều lượt mà ít tiến độ

| Chỉ số | Giá trị |
|---|---|
| Lệnh công cụ Desktop Commander trên máy | 22.678 lệnh / 59 phiên / 11 ngày (~2.000 lệnh/ngày; tổng mọi chat dùng connector, phần review này chỉ vài chục) |
| Bản sản phẩm được chấp nhận gần nhất | dev22 ở V55 (18/09 12:46). Đến V144 (24/09 18:23): 89 phiên bản state, hơn 120 commit main, chưa có bản mới được chấp nhận |
| dev23 | xuất hiện từ V92 (23/09 11:54); sau 52 phiên bản state vẫn chưa được chấp nhận |
| Mode của 130 bản state | IMPLEMENTATION 43 · VALIDATION 33 · CODE_REVIEW 32 · TEST_REVIEW 9 · TEST_DESIGN 8 · khác 5 |
| Chi phí khởi động mỗi phiên | CORE + profile Resume + JSON V144 (38 KB) + learning + dual-actor ≈ 170–210 KB phải đọc trước khi làm việc (theo DOCUMENTATION_MAP) |
| Đo năng suất theo lượt | không có: `workflow-runs/continuity-events/` chỉ có README (0 sự kiện) |

Nguyên nhân:
1. **Một lượt = một bước**, theo thiết kế: một mode, một task, tuần tự.
2. **Guard trước, việc sau.** 5 luật đầu của router (recovery, workflow review, excursion, block, continuity recovery) đứng trước thực thi; gap nào cũng thành BLOCKED rồi mở vòng design/test-design mới (vd block 057).
3. **Overhead mỗi bước:** đọc ~170–210 KB; ghi state JSON + checkpoint + hồ sơ review/audit; 111/529 commit main là `state:`.
4. **Việc bị băm quá nhỏ:** mỗi lần triển khai thử đi prepare → review → authorize → attempt → receipt → reconcile (authorization 002/003, attempt 004/005…).
5. **Không có thước đo sản phẩm**, nên không có áp lực ra kết quả.
6. **Không có động cơ chạy dài:** chat không hoạt động giữa các lượt; Claude bị khóa ở vai soát văn bản 2 lượt.

### 11.3 Thiết kế "Tiếp tục v2" — lượt theo lô

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

Bộ trạng thái mới — cold-start ≤ 10 KB thay vì ~170–210 KB. Ví dụ (số liệu minh họa):

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

Hai mức tự động (đề xuất, chưa bật):
- **L1 (mặc định sau khi v2 được phê duyệt):** mỗi "Tiếp tục" chạy một lô rồi báo cáo.
- **L2 (chỉ khi chủ dự án bật rõ ràng):** runner nền bằng systemd user timer (máy đã chạy 11 timer) xử lý backlog theo lịch, trần USD/ngày; "Tiếp tục" chỉ để review, duyệt merge và gỡ chặn.

Tự cải thiện có đo (thay self-learning quy trình hiện tại):
- Mỗi 10 lượt: retro tự tính KPI (task/lượt, lượt không delta, USD/task, top lý do chặn) → đề xuất tối đa 3 thay đổi, mỗi thay đổi có KPI mục tiêu; 10 lượt sau không cải thiện → hoàn tác.
- Ngân sách độ phức tạp: tài liệu quy trình đang hiệu lực ≤ 30 KB; thêm 1 luật phải bỏ hoặc gộp 1 luật.
- Báo động: một task nằm ở "việc kế tiếp" 3 lượt liền → tự tách nhỏ hoặc hỏi chủ dự án.
- Bài học phim ghi vào FILM_LEARNINGS.md kèm số liệu trước/sau (vd "thêm ảnh tham chiếu trang phục: COSTUME_DRIFT 40% → 10% trên 20 shot").

Mục tiêu năng suất:
- ≥ 3 task hoàn thành mỗi lượt; không quá 1 lượt liên tiếp không có delta sản phẩm; mỗi 3–5 lượt qua một milestone.
- Cold-start ≤ 10 KB và ≤ 3 lệnh công cụ trước khi bắt đầu làm việc.

### 11.4 Đề xuất chuyển đổi (chưa thực hiện; cần chủ dự án phê duyệt)
1. Tag archive; chuyển tài liệu quy trình cũ vào `archive/` (vẫn trong git).
2. Tạo RESUME.md, BACKLOG.yaml, MILESTONES.md, PROGRESS_LOG.jsonl, CONTINUE_PROTOCOL.md (≤ 3 KB, chứa thuật toán 11.3), `tools/turn_start.sh`, `tools/turn_end.sh`.
3. Sửa README.md và CLAUDE.md trỏ sang giao thức v2; từ đây "Tiếp tục." chạy thuật toán 11.3.
4. Nạp backlog đầu từ mục 5–6 (slice01); chạy lượt đầu, ghi dòng PROGRESS_LOG đầu tiên làm mốc so sánh.

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

### 12.2 Phần cứng hiện tại (đo 24/09)
- CPU AMD Ryzen 9 9950X (WSL thấy 24 luồng); RAM host 61,6 GB (WSL thấy 47 GB).
- **Không có GPU rời:** Windows chỉ báo "AMD Radeon(TM) Graphics" (iGPU); WSL không có `nvidia-smi`; không có driver NVIDIA.
- Ổ: WSL root 1 TB (còn 403 GB); C: 1,9 TB (còn 1,1 TB).
- Chưa cài ffmpeg, Docker, PyTorch.
- Kết luận: máy này làm được control plane, kịch bản, dựng/ghép (sau khi cài ffmpeg) và TTS nhỏ chạy CPU; không sinh được ảnh/video cục bộ ở tốc độ dùng được.

### 12.3 Kế hoạch GPU cục bộ
- Blueprint §36 (đo trước khi mua) được giữ nguyên: chủ dự án chọn thuê GPU 3–5 ngày để benchmark rồi mới mua (12.10). Các mức dưới đây là cấu hình ứng viên để thuê thử.
- Tối thiểu: 1 GPU NVIDIA 32 GB (vd RTX 5090). LTX-2.x có đường FP8 cho GPU 32 GB; HunyuanVideo 1.5 cần khoảng 14 GB; Wan 2.2 14B cần fp8/offload trên GPU 32 GB.
- Ứng viên benchmark cấu hình lớn (không phải quyết định mua): 1 GPU 96 GB lớp workstation (vd RTX PRO 6000 Blackwell) trong **máy Linux riêng** (Ubuntu native) làm GPU worker; PC hiện tại giữ vai control plane + dựng (đúng Stage B của Blueprint). Mốc RAM ≥ 128 GB, NVMe ≥ 4 TB là giả thuyết cấu hình để đo, chỉ chốt sau benchmark và báo giá.
- Nếu gắn GPU thẳng vào PC hiện tại: kiểm PSU/case/khe PCIe cho GPU lớp ~600 W, nâng RAM, dùng CUDA trên WSL.
- Chọn NVIDIA (CUDA) vì hệ sinh thái model/ComfyUI ưu tiên CUDA. Chọn mẫu cụ thể lúc mua; thêm GPU thứ 2 chỉ sau khi đo throughput slice01.

### 12.4 Shortlist model mở cho MODEL-EVAL (ứng viên benchmark, không phải model đã duyệt; license theo tra cứu 24/09/2026 — đọc lại license gốc trước khi dùng)

| Nhóm | Ứng viên | License | Ghi chú |
|---|---|---|---|
| Video | Wan 2.2 (T2V-14B, I2V-14B, TI2V-5B) | Apache 2.0 | Các checkpoint này có weights mở; không suy diễn trạng thái license/weights của các phiên bản Wan mới hơn — kiểm lại tại thời điểm MODEL-EVAL |
| Video | Wan-Animate-2 (Base/Distillation, 08/2026) | Apache 2.0 | Repo chính thức phát hành inference scripts + weights ngày 07/08/2026; hoạt họa nhân vật từ video tham chiếu. Kiểm exact checkpoint trước benchmark |
| Video | LTX-2.x (2.3/2.5) | LTX-2 Community: miễn phí thương mại khi doanh thu năm < 10 triệu USD | Audio + video một lượt, IC-LoRA điều khiển; kiểm lại khi doanh thu tăng |
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

### 12.9 Việc có thể làm khi chưa có GPU (sau khi gỡ REVIEW_FREEZE và duyệt phạm vi)
- Nếu chủ dự án phê duyệt "Tiếp tục v2": thực hiện mục 11.4; sau đó scaffold package `film/` và schema shot/ledger/manifest.
- SCRIPT_ENGINE hai chế độ; kịch bản slice01 bản EN + bản địa hóa ZH/VI.
- Continuity ledger, shot compiler (xuất prompt), casting spec (ngoại hình), voice bible.
- Cài ffmpeg; dựng animatic (thẻ chữ/placeholder + TTS) để kiểm nhịp và thời lượng; pipeline phụ đề và xuất 9:16/16:9.
- Thử VieNeu-TTS-v2 trên CPU cho bản VI.
- Chuẩn bị bộ benchmark cho GPU thuê: 5–10 shot từ kịch bản slice01, câu thoại mẫu EN/ZH/VI, script cài đặt và script chạy benchmark (12.10).

### 12.10 Kế hoạch thuê GPU để benchmark (chiến lược đã chốt 24/09; cấu hình/nhà cung cấp/trần chi phí từng lần vẫn cần duyệt)

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
