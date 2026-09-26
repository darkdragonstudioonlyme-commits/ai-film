# HANDOFF — Review các phiên GPU thuê & cải thiện MD (26/09/2026)

> Dành cho chat ChatGPT điều phối AI-FILM. Đọc hết, rồi làm theo mục 7 theo đúng thứ tự.
> Số liệu đo ngày 26/09/2026 lúc 09:35 (+07) trên DESKTOP-LCISMET; `main` = 7963680.
> Đi kèm: `handoffs/HANDOVER_REVIEW_2026-09-24.md` (mục 11–12), `handoffs/CHATGPT_CLAUDE_AUTOMATION_HANDOFF_2026-09-25.md`.

## 0. Tóm tắt

- **Tốt:**
  - Đã chạy GPU thật. FLUX.2 klein-4B và Z-Image qua smoke 1024 (4/4 mỗi model); VoxCPM2 ra 1 mẫu giọng EN.
  - License đúng (klein-4B, Apache 2.0). Gate an toàn giữ nguyên: không tạo tài nguyên mới, không chọn model thắng khi chưa có điểm, không publish.
  - 245/245 test pass (đã chạy lại độc lập).
- **Vấn đề lớn nhất:** GPU chỉ làm việc khoảng **2%** thời gian thuê.
  - Sổ chi phí ghi 0,17 USD (thời gian model chạy), trong khi pod đã bật khoảng 15,6 giờ ≈ **7,6 USD**.
  - Trần 60 USD được so với con số 0,17 nên sẽ không bao giờ kích hoạt nếu pod bật chờ. Phê duyệt không có hạn.
- **Media kẹt trên pod.** 8 ảnh + 1 file giọng chỉ nằm trên pod, không có ổ lưu tách riêng. Chủ dự án không xem hay chấm được: `scores.csv` còn trống.
- **So sánh mù không còn mù.** `blind_map_private.json` (blind_id → model) đã commit vào repo **public**.
- **Mỗi model đi 4–5 bước riêng:** runner riêng → bài 512 → smoke 1024 → evidence → review. Kết quả: 3 model mất khoảng 15 giờ, 13 file review, 10 file evidence. Model video (quan trọng nhất cho phim) chưa thử.
- **ChatGPT–Claude:**
  - Worker tự động theo handoff 25/09 chưa được dựng.
  - Claude đang được dùng như "tay điều khiển RunPod" (12 phiên list/get/restart/billing qua RunPod MCP).
  - 2 phiên Claude review dừng khi mới đọc file, không có kết luận.
- **Ưu tiên ngay:**
  1. Pod: xếp lô chạy liên tục hoặc sync media rồi tắt.
  2. Đồng hồ chi phí theo thời gian bật.
  3. Đưa media về máy, cho chủ dự án xem và chấm ngay trong ChatGPT.
  4. Niêm phong bảng mù.
  5. Runner ma trận chạy cả bộ benchmark không cần người.
  6. Dựng worker Claude.

## 1. Diễn biến (25/09 17:30 → 26/09 09:35, giờ +07)

| Thời điểm | Sự kiện |
|---|---|
| 25/09 17:33 | Lượt 17: T-053..T-055 (spec transport, schema compat, readiness DAG) — hạ tầng, không gỡ chặn M2 |
| 17:53–17:57 | Claude (qua RunPod MCP) báo 0 pod; liệt kê loại GPU |
| 17:59 | Pod A40 được tạo (`0h1twwxqw6yx0k`, 0,49 USD/h, 46.068 MiB) |
| 18:07–18:31 | Claude đọc thông tin pod, restart pod (18:21), đọc cổng SSH |
| 18:47 | Lượt 18: phê duyệt trần 60 USD, chỉ pod hiện có, không có ngày hết hạn |
| 19:12–19:27 | Commit phê duyệt + sửa khóa phụ thuộc runtime A40 |
| 22:34 → 26/09 01:27 | Runner FLUX.2 → bài 512 (lượt 19) → smoke 1024 4/4 (lượt 20) |
| 26/09 01:37–01:38 | Claude đọc uptime pod (7,26 giờ) và billing (dữ liệu dừng ở 18:00Z do trễ) |
| 05:32–07:51 | Runner Z-Image → bài 512 (lượt 21) → smoke 1024 4/4 + gói so sánh mù 8 ảnh (lượt 22) |
| 08:27–09:13 | Runner VoxCPM2 → 1 mẫu EN (không có dòng PROGRESS_LOG) |

Khoảng trống giữa các lượt, GPU không làm gì: 18:47 → 01:12 (6,4 giờ), 01:27 → 06:03 (4,6 giờ), 07:51 → 09:13 (1,4 giờ).

| Số liệu | Giá trị |
|---|---|
| Commit `main` | 13 (7 `feat:`, 5 `evidence:`, 1 `fix:`) |
| File mới | 9 module `film/*`, 13 `reviews/PRODUCT-V2-*`, 10 `run-evidence/*` |
| Media sinh ra | 8 PNG (4 FLUX.2 + 4 Z-Image, 1024) + 1 WAV (VoxCPM2) — tất cả nằm trên pod |
| Đo tài nguyên | FLUX.2 1024×4: đỉnh 20.415 MiB, 15,4 s. Z-Image 512: đỉnh 21.913 MiB, suy luận 21,6 s; 1024 cần 26 GiB + 4 dự phòng. VoxCPM2: đỉnh 5.827 MiB, 3,04 s audio trong cue 3,5 s, runner 31,5 s |
| Chi phí | Sổ ghi 0,1708 USD; theo thời gian bật ≈ 7,6 USD (chưa gồm lưu trữ); tỉ lệ GPU làm việc ≈ 2% |
| Test | 245/245 pass (chạy lại độc lập trên `origin/main`); product checker pass |
| Desktop Commander | ~3.100 lệnh mới trong ~16 giờ (≈ 440 lệnh mỗi bước) |
| Claude Code | 14 phiên: 12 phiên sonnet-5 điều khiển RunPod MCP, 2 phiên opus-5 review tĩnh; bridge cũ 0 task; worker/queue chưa có |
| Milestone | Không đổi: M0, M1 xong; M2 đang làm |

## 2. Đánh giá các phiên GPU

### 2.1 Điểm tốt
- Có đường chạy GPU thật: khóa runtime, pin revision model (Z-Image `04cc4abb…`, FLUX.2 klein `e7b7dc27…`), đo VRAM và thời gian.
- Chọn đúng model có license thương mại; không dùng FLUX.2 dev/klein-9B.
- Gate giữ đúng: không tạo tài nguyên mới, không chọn model thắng, không publish, không vượt trần.
- Test tăng từ 165 lên 245, vẫn pass.

### 2.2 Vấn đề và cách sửa

| # | Vấn đề | Bằng chứng | Sửa |
|---|---|---|---|
| G1 | GPU rảnh gần như toàn thời gian | 0,17 USD thực thi / ~7,6 USD thời gian bật; khoảng trống 4–6 giờ giữa các lượt | Pod đang bật thì mỗi lượt phải để lại một lô chạy không cần người đủ đến lượt sau, hoặc sync media rồi tắt pod |
| G2 | Trần chi phí đo sai thứ | Trần 60 USD so với "measured execution"; phê duyệt `expires_at = None`; RESUME ghi billing "không đọc được" | Chi phí = (now − createdAt) × 0,49 + lưu trữ; trần và cảnh báo tính theo số này; phê duyệt có hạn. `get-pod` trả uptime; `list-pod-billing` có số liệu (trễ theo giờ) |
| G3 | Media chỉ nằm trên pod | `pod_path = /workspace/artifacts/...`; `workspace_separate_mount = False` | Sync về `/home/dragon/ai-film-dev/media/slice01/<lô>/` sau mỗi lô (SSH trực tiếp; cổng đổi sau restart → đọc lại qua RunPod MCP). Lần thuê sau dùng volume/network volume (kiểm tài liệu RunPod về container disk và volume) |
| G4 | Chủ dự án không chấm được | `scores.csv` 8 dòng trống; chủ dự án chỉ dùng ChatGPT | ChatGPT hiển thị ảnh/audio ngay trong chat theo blind_id, nhận điểm, ghi `scores.csv`; kèm contact sheet |
| G5 | So sánh mù bị lộ | `blind_map_private.json` (có `model_id`) trong repo public | Bảng mù để ngoài git, chỉ commit SHA-256, mở sau khi có điểm. Vòng hiện tại coi là "bán mù": chủ dự án chấm mà không mở bảng |
| G6 | Nghi thức theo từng model | 3 model → 9 module, 13 review, 10 evidence; ~15 giờ | Một runner ma trận đọc `model_matrix` (model × shot × seed), chạy cả bộ trong một lô; một evidence và một review mỗi lô |
| G7 | Chưa thử model video | Chỉ có ảnh + 1 giọng | Lô kế tiếp phải có Wan 2.2 (TI2V-5B, I2V-14B) và LTX-2.x trên 8 shot benchmark, kèm lip-sync (LatentSync/MuseTalk) và nhạc (ACE-Step 1.5) |
| G8 | Repo public chứa dữ liệu sản xuất | Bảng mù, kịch bản, kế hoạch đều public | Chủ dự án quyết: chuyển repo sang private, hoặc tách repo nội dung riêng |

## 3. Phối hợp ChatGPT–Claude

| Thiết kế (handoff 25/09) | Thực tế |
|---|---|
| Hàng đợi + worker systemd, Claude implement có tool | Chưa có `claude-queue/`, `claude-runtime/`; service `aifilm-claude-worker` inactive |
| Review hai chiều, có chạy test | 2 phiên opus review tĩnh (chỉ Read/Glob), câu cuối là "đang đọc file" → không kết luận. 13 file review mới không ghi reviewer |
| BACKLOG `owner: claude/chatgpt/owner` | Vẫn `executor` 48 / `coordinator` 7 |
| Claude làm việc giữa các lượt | Claude chỉ chạy khi ChatGPT gọi lệnh RunPod |

**Điểm tốt:** dùng Claude Code để thao tác RunPod MCP là cách hay, vì ChatGPT không có connector RunPod. Nên giữ, nhưng đưa vào hàng đợi như một loại task (`ops_runpod`):
- mặc định chỉ đọc;
- `pod-action` (start/stop/restart) chỉ được chạy khi task ghi rõ phê duyệt;
- mỗi lần đọc pod đều ghi uptime vào POD_CLOCK.

**Cần làm:**
- Triển khai Lượt A của handoff 25/09 ngay.
- Bốn task đầu giao Claude:
  - runner ma trận;
  - POD_CLOCK + tự tắt khi rảnh;
  - sync media + contact sheet;
  - review có chạy test cho lô GPU vừa rồi.
- Review nào cũng phải đủ lượt để kết luận, và ghi `Reviewer: <model> · Tests: <lệnh> → <kết quả>`.

## 4. Đánh giá hệ MD v2

**Đang chạy tốt:**
- RESUME gọn, đọc nhanh.
- PROGRESS_LOG có mỗi lượt.
- BACKLOG có trạng thái.
- Gate an toàn tiền/publish hoạt động.
- MILESTONES rõ.

**Cần sửa:**
1. RESUME không có dòng việc chủ dự án cần làm (chấm 8 ảnh) ở đầu, không có đồng hồ pod, không có trạng thái sync media.
2. CONTINUE_PROTOCOL chưa có luật GPU: bật pod, tính tiền, sync, tắt, lô chạy qua đêm.
3. Luật "không có delta 2 lượt" tính cả code/evidence, nên không phát hiện được GPU rảnh hay milestone đứng yên.
4. DECISIONS chưa ghi phê duyệt trả tiền (RunPod A40, 60 USD).
5. PROGRESS_LOG thiếu dòng cho bước VoxCPM2 (09:13).
6. M2 quá thô, không đo được tiến độ bên trong (ảnh, giọng, chốt casting).
7. Review/evidence theo từng bước nhỏ làm phình tài liệu. Mẫu cũ của P00 đang quay lại ở phần GPU.

## 5. Bản sửa MD đề xuất (ChatGPT áp dụng)

### 5.1 Thêm vào đầu `RESUME.md`
```text
OWNER_ACTION: <việc chủ dự án cần làm + cách xem/chấm ngay trong ChatGPT> (hoặc: none)
POD_CLOCK: <pod_id> <GPU> · createdAt <UTC> · uptime <giờ> · ước tính <USD>/<trần> USD (theo thời gian bật) · thực thi <USD> · GPU làm việc <%>
POD_PLAN: đang chạy lô <id> đến ~<giờ> | hàng đợi rỗng → sync + tắt sau 20 phút
MEDIA_SYNC: <n> file trên pod chưa sync / <n> đã sync về media/slice01/
```

### 5.2 Thêm vào `CONTINUE_PROTOCOL.md`
```text
11. Pod đang bật: cuối mỗi lượt phải (a) có một lô chạy không cần người đủ đến lượt sau, hoặc (b) sync media rồi tắt pod. Không để pod rảnh qua đêm.
12. Chi phí GPU = (now − createdAt) × giá/giờ + lưu trữ. Trần, cảnh báo và báo cáo dùng số này; cập nhật POD_CLOCK mỗi lượt.
13. Sync media về máy ngay sau mỗi lô. Media chỉ nằm trên pod coi như chưa có.
14. Benchmark chạy bằng một runner ma trận theo cấu hình; không viết runner riêng cho từng model. Mỗi lô: một evidence, một review.
15. Việc cần chủ dự án (chấm, duyệt) đứng đầu báo cáo, kèm cách xem ngay trong ChatGPT.
16. Bảng giải mã so sánh mù không vào git; chỉ commit SHA-256; mở sau khi có điểm.
17. Review mỗi lô do model còn lại làm, có chạy test; file review ghi reviewer và lệnh test.
18. "Có tiến độ" = milestone tiến lên hoặc có media mới đã sync/chấm. Evidence và tài liệu không tính.
```

### 5.3 Tách M2 trong `MILESTONES.md`
```text
- [ ] M2a — 2 model ảnh × 2 phong cách × 4 slot casting, chủ dự án đã chấm mù
- [ ] M2b — 12 mẫu VoxCPM2 EN/ZH/VI + mẫu VieNeu VI, đã chấm
- [ ] M2c — chốt casting ngoại hình + giọng cho An và Linh
- [ ] M4a — Wan 2.2 (TI2V-5B, I2V-14B) và LTX-2.x chạy 8 shot benchmark, có VRAM/thời gian/điểm
```

### 5.4 Thêm vào `DECISIONS.md`
```text
## D-007 — RunPod A40 benchmark (25/09)
Pod 0h1twwxqw6yx0k (A40, 0,49 USD/h), trần 60 USD, chỉ pod hiện có, không tạo tài nguyên mới. Bổ sung: có ngày hết hạn; trần tính theo thời gian bật.
## D-008 — Chi phí GPU theo thời gian bật, không theo thời gian model chạy.
## D-009 — Bảng giải mã so sánh mù để ngoài git; commit SHA-256.
## D-010 — Claude chạy tự động qua hàng đợi + worker (handoff 25/09); RunPod MCP qua Claude là task `ops_runpod`.
```

### 5.5 Task mới cho `BACKLOG.yaml` (đánh số tiếp theo)

| Task | Owner | Milestone | Mục tiêu |
|---|---|---|---|
| POD-CLOCK | claude | M2 | Tính chi phí theo thời gian bật, áp trần, tự tắt khi hàng đợi rỗng 20 phút (tắt pod cần phê duyệt trong task) |
| MEDIA-SYNC | claude | M2 | Kéo media từ pod về máy sau mỗi lô + contact sheet + manifest hash |
| OWNER-SCORING | chatgpt | M2a | Hiển thị 8 ảnh theo blind_id trong ChatGPT, nhận điểm, ghi `scores.csv` |
| BLIND-SEAL | chatgpt | M2a | Đưa bảng mù ra ngoài git, commit hash, sửa pipeline so sánh |
| MATRIX-RUNNER | claude | M2/M4 | Runner benchmark tổng quát theo `model_matrix`, chạy không cần người |
| VOICE-12 | chatgpt → pod | M2b | Chạy nốt 11 mẫu VoxCPM2 trong một lô |
| VIDEO-BENCH | chatgpt → pod | M4a | Wan 2.2 + LTX-2.x trên 8 shot |
| LIPSYNC-MUSIC-BENCH | chatgpt → pod | M5 | LatentSync/MuseTalk + ACE-Step 1.5 |
| CLAUDE-WORKER | chatgpt + claude | — | Lượt A của handoff 25/09 |

## 6. Chính sách pod mới

1. Trước khi bật pod: phải có sẵn một lô đủ việc (ma trận model × shot) để GPU chạy liên tục.
2. Lô chạy trên pod bằng `nohup`/`tmux`, ghi log và kết quả vào thư mục lô; không phụ thuộc phiên chat còn mở.
3. Mỗi lượt ChatGPT:
   - đọc POD_CLOCK;
   - kéo kết quả lô xong về máy;
   - xếp lô tiếp hoặc tắt pod.
4. Hàng đợi rỗng quá 20 phút → sync rồi tắt pod (cần phê duyệt trong task).
5. Cổng SSH trực tiếp đổi sau restart → đọc lại qua RunPod MCP trước khi sync.
6. Lần thuê sau: gắn volume để dữ liệu còn sau khi tắt; phê duyệt có ngày hết hạn.
7. Mục tiêu: GPU làm việc ≥ 60% thời gian pod bật.

## 7. Kế hoạch hành động (theo thứ tự)

1. **Ngay lượt tới — pod:**
   - Tính POD_CLOCK.
   - Nếu chưa có lô chạy được ngay: sync 8 PNG + 1 WAV về máy, rồi hỏi chủ dự án có tắt pod không.
   - Nếu có: chạy lô VOICE-12 và giữ pod.
2. **Chấm ảnh:** hiển thị 8 ảnh trong ChatGPT theo blind_id; chủ dự án chấm; ghi `scores.csv`; sau đó mới mở bảng mù.
3. **Niêm phong bảng mù** cho các vòng sau (BLIND-SEAL).
4. **Runner ma trận + lô video:** VIDEO-BENCH chạy qua đêm, có tự tắt khi xong.
5. **Worker Claude** (Lượt A handoff 25/09). Bốn task đầu cho Claude: POD-CLOCK, MEDIA-SYNC, MATRIX-RUNNER, review lô GPU có chạy test.
6. **Áp dụng bản sửa MD** ở mục 5; bổ sung dòng PROGRESS_LOG còn thiếu cho VoxCPM2.
7. **Hỏi chủ dự án** (mỗi lượt tối đa 1 câu, theo thứ tự): chấm 8 ảnh → tắt/giữ pod → repo public hay private → trần Claude mỗi ngày.

## 8. KPI theo dõi

| KPI | Mục tiêu | Hiện tại |
|---|---|---|
| GPU làm việc / thời gian pod bật | ≥ 60% | ≈ 2% |
| Chi phí theo thời gian bật / trần | hiển thị mỗi lượt | chưa hiển thị |
| Media sync về máy trong cùng lượt | 100% | 0% |
| Model benchmark mỗi ngày GPU | ≥ 6 | 3 trong ~15 giờ (chưa có video) |
| Thời gian chủ dự án chấm sau khi có media | ≤ 1 lượt | chưa có cách xem |
| Review có chạy test, có kết luận | 100% | 0/2 phiên Claude có kết luận |
| Lượt không có tiến độ milestone | ≤ 1 liên tiếp | M2 đứng yên từ 25/09 |

## 9. Giới hạn của review

- Không SSH vào pod và không gọi RunPod. Trạng thái pod suy ra từ evidence lúc 09:13 và kết quả RunPod MCP ghi trong phiên Claude lúc 01:37 (uptime 7,26 giờ). Pod có thể đang chạy lô mới vào thời điểm đọc file này.
- Chưa xem ảnh hay nghe audio: chúng nằm trên pod.
- Desktop Commander không ghi tên client; số lệnh là tổng mọi chat.
- Chi phí thời gian bật là ước tính (giá × thời gian, chưa gồm lưu trữ); số thật lấy từ billing của RunPod.

## 10. Prompt khởi động cho ChatGPT

```text
Đọc handoffs/SESSION_REVIEW_GPU_2026-09-26.md (GitHub branch handover/review-2026-09-24, hoặc /home/dragon/ai-film-dev/handoffs/).
Làm theo mục 7 đúng thứ tự: xử lý pod và POD_CLOCK trước, rồi đưa 8 ảnh cho tôi chấm ngay trong chat.
Áp dụng bản sửa MD ở mục 5. Mỗi lượt hỏi tôi tối đa 1 câu, đặt ở đầu báo cáo.
```
