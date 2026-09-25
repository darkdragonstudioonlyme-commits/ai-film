# HANDOFF — Tự động hóa phối hợp ChatGPT ↔ Claude (25/09/2026)

> Dành cho chat ChatGPT điều phối dự án AI-FILM. Đọc hết rồi triển khai theo mục 10.
> Ràng buộc của chủ dự án: **chỉ thao tác trên ChatGPT**. Claude (Claude Code trên máy WSL) phải **tự động** nhận việc, làm, tự kiểm và trả kết quả; ChatGPT review, merge và báo cáo.
> Số liệu đo trên DESKTOP-LCISMET ngày 25/09/2026 ~17:30 (+07). Tài liệu liên quan: `handoffs/HANDOVER_REVIEW_2026-09-24.md` (mục 11–12).

## 0. Tóm tắt

- Hiện trạng: từ lúc pivot Product v2 (24/09 21:41), Claude **không được gọi lần nào** (bridge 0 task, 0 phiên Claude Code). Một chat tự làm và tự kiểm toàn bộ ~10,6 nghìn dòng code + 165 test.
- Trước pivot: 322 task Claude (22–24/09, 70,82 USD), nhưng chỉ là soát văn bản không tool, tối đa 2 lượt, ~0,25 USD/task; 74 task (23%) chết vì chạm trần.
- Thiết kế mới: ChatGPT đưa task vào **hàng đợi file**; **worker nền** (systemd user) chạy **Claude Code headless có tool** trong **worktree riêng**; kết quả trả về theo **schema JSON**; mỗi lệnh "Tiếp tục" tự đọc kết quả → review chéo có chạy test → merge → giao task tiếp.
- Review hai chiều: code của Claude do ChatGPT review; thay đổi của ChatGPT do Claude review (có chạy test). Kịch bản: ChatGPT viết, Claude chấm rubric và đề xuất viết lại, chủ dự án chọn.
- Chủ dự án chỉ cần trả lời 1 câu (qua ChatGPT): trần sử dụng Claude mỗi ngày.

## 1. Hiện trạng kỹ thuật (đo 25/09)

| Hạng mục | Giá trị |
|---|---|
| Claude Code CLI | `/home/dragon/.local/bin/claude`, bản 2.1.267 |
| Xác thực | Không có `ANTHROPIC_API_KEY`; có `~/.claude/.credentials.json` → đăng nhập bằng tài khoản. Cần xác nhận gói thuê bao hay API; nếu thuê bao, giới hạn thật là hạn mức của gói |
| Cờ headless có sẵn | `-p`, `--output-format`, `--json-schema`, `--max-budget-usd`, `--model`, `--effort`, `--tools`, `--allowedTools`/`--disallowedTools`, `--permission-mode`, `--append-system-prompt`, `--add-dir`, `--resume`/`--session-id`, `--settings`, `--no-session-persistence` (kiểm lại bằng `claude --help` trước khi dùng) |
| systemd user | Chạy được; shell của Desktop Commander phải đặt `XDG_RUNTIME_DIR=/run/user/$(id -u)`, nếu không sẽ báo "Failed to connect to bus" |
| GitHub | Push qua SSH key `~/.ssh/id_ed25519` hoạt động (URL `git@github.com:darkdragonstudioonlyme-commits/ai-film.git`); remote `origin` là HTTPS và không có credential |
| Bridge cũ | `tools/dual_ai_text_bridge.py` (profile TEXT_REVIEW, `--tools ''`, effort low, max_turns = 2); queue `/home/dragon/ai-film-dev/dual-ai-queue`. Giữ làm lịch sử, không dùng cho vai implement |
| Product v2 | `main` d6af95b; 48 task DONE, 3 READY, 4 BLOCKED (T-019 chờ duyệt chi tiền GPU); BACKLOG `owner`: executor 48, coordinator 7 |
| Hook lượt | `tools/turn_start.sh` (fetch, in RESUME/READY/MILESTONES/status), `tools/turn_end.sh` (ghi PROGRESS_LOG) |
| CLAUDE.md | Đã viết cho v2 (worker entry) nhưng chưa được dùng |

## 2. Nguyên tắc

1. Chủ dự án chỉ nói chuyện với ChatGPT. Claude không hỏi trực tiếp chủ dự án; câu hỏi của Claude nằm trong `result.questions`, ChatGPT gom lại và hỏi tối đa 1 câu mỗi lượt.
2. Claude chạy tự động theo hai cách: trong lượt ChatGPT (dispatch, thu kết quả ở lượt sau hoặc chờ ngắn) và giữa các lượt bằng worker nền.
3. Không ai tự duyệt việc của mình: code Claude → ChatGPT review; thay đổi của ChatGPT → Claude review. Review nào cũng phải chạy test.
4. Mỗi task có hợp đồng rõ (mục 5): mục tiêu, tiêu chí chấp nhận, đường dẫn được sửa, lệnh test, branch, trần.
5. Bất đồng giải bằng bằng chứng (test, số đo). Tối đa 1 vòng sửa; sau đó ChatGPT quyết phần kỹ thuật, chủ dự án quyết phần sáng tạo và chi tiền.
6. Chỉ ChatGPT tạo task. Claude đề xuất trong `next_suggestions`, ChatGPT quyết → không có vòng tự sinh việc.
7. Worker không được: chi tiền GPU/API trả phí, publish, xóa lịch sử, đọc secret, push hoặc merge `main`. Merge `main` là việc của ChatGPT sau review; chi tiền và publish cần chủ dự án duyệt.
8. Mọi task gắn milestone; không giao Claude việc hạ tầng không gỡ chặn milestone sớm nhất.

## 3. Phân vai mặc định (chỉnh theo KPI sau 10 lượt)

| Việc | Làm chính | Kiểm |
|---|---|---|
| Giao tiếp chủ dự án, ưu tiên, chia task, tiêu chí nghiệm thu | ChatGPT | Claude phản biện khả thi khi nhận task |
| Code, test, debug, refactor trong repo | Claude (worker) | ChatGPT review diff + chạy lại test |
| Thay đổi ChatGPT tự làm (dữ liệu phim, thiết kế, script nhỏ) | ChatGPT | Claude review có chạy test |
| Kịch bản thương mại | ChatGPT viết nháp | Claude chấm rubric + đề xuất viết lại → ChatGPT gộp tối đa 2 phương án → chủ dự án chọn |
| QC dữ liệu phim (continuity, localization, timing, phụ đề) | Claude chạy validator + soát | ChatGPT quyết |
| Merge `main`, cập nhật RESUME/BACKLOG/MILESTONES/PROGRESS_LOG | ChatGPT | — |
| Chi tiền, publish, thao tác phá hủy | Chủ dự án duyệt (qua ChatGPT) | ChatGPT thực thi |

## 4. Kiến trúc

```text
Chủ dự án ──"Tiếp tục"──▶ ChatGPT (Desktop Commander)
                              │ turn_start: đọc kết quả Claude, review, merge
                              │ enqueue task mới
                              ▼
        /home/dragon/ai-film-dev/claude-queue/inbox/<task_id>.json
                              │
        aifilm-claude-worker.service (systemd user, vòng lặp)
          ├─ kiểm STOP, trần ngày, hạn mức
          ├─ git fetch; worktree mới claude/<task_id> từ origin/main
          ├─ claude -p … (có tool, trong worktree)
          ├─ chạy lại test_command độc lập
          └─ push branch claude/<task_id>; ghi done/<task_id>/result.json
                              │
ChatGPT lượt sau ◀────────────┘  review → approve (merge) / changes_requested (1 vòng)
```

- Hàng đợi nằm ngoài git để không tạo commit tranh chấp với `main`. `BACKLOG.yaml` vẫn là nguồn sự thật về task; ChatGPT đồng bộ trạng thái ở `turn_end`.
- Thư mục `claude-queue/`: `inbox/`, `running/`, `done/`, `failed/`, `STOP` (có file = dừng), `budget.json` (chi phí theo ngày), `STATUS.md` (worker ghi trạng thái cho ChatGPT đọc), `worker.log`.

## 5. Hợp đồng dữ liệu

### 5.1 Gói task (ChatGPT → Claude)

```json
{
  "task_id": "T-060",
  "type": "implement",
  "size": "M",
  "milestone": "M2",
  "goal": "Mô tả việc cần làm, 1–3 câu",
  "acceptance": ["Tiêu chí kiểm được 1", "Tiêu chí kiểm được 2"],
  "context_files": ["RESUME.md", "CLAUDE.md", "film/casting_jobs.py"],
  "allowed_paths": ["film/", "tests/film/", "tools/"],
  "test_command": "PYTHONPATH=. python3 -m unittest discover -s tests/film -t tests/film -p 'test_*.py'",
  "base_ref": "origin/main",
  "branch": "claude/T-060",
  "review_target": null,
  "created_by": "chatgpt",
  "created_at": "2026-09-25T18:00:00+07:00"
}
```

- `type`: `implement` | `fix` | `review` | `script_critique` | `qc`.
- `size` (S/M/L) quyết định trần (mục 6.3).
- Với `review`: `review_target` là branch/commit của ChatGPT; Claude không sửa code, chỉ chạy test và trả `findings`.

### 5.2 Kết quả (Claude → ChatGPT), ép bằng `--json-schema`

```json
{
  "task_id": "T-060",
  "status": "DONE",
  "summary": "Đã làm gì, 2–4 câu",
  "branch": "claude/T-060",
  "commits": ["abc1234"],
  "changed_files": ["film/x.py", "tests/film/test_x.py"],
  "tests": {"command": "...", "passed": 172, "failed": 0},
  "acceptance": [{"item": "Tiêu chí 1", "met": true, "evidence": "tests/film/test_x.py::test_y"}],
  "findings": [{"severity": "MAJOR", "file": "film/y.py", "issue": "...", "suggestion": "..."}],
  "questions": [],
  "next_suggestions": [],
  "cost_usd": 1.4,
  "turns": 23,
  "duration_s": 610,
  "session_id": "..."
}
```

- `status`: `DONE` | `PARTIAL` | `BLOCKED` | `FAILED`.
- `severity`: `BLOCKER` | `MAJOR` | `MINOR`.

### 5.3 Vòng review

- ChatGPT đọc `result.json` + `git diff origin/main...claude/<task_id>` + chạy lại test, rồi chọn:
  - `approve`: merge vào `main`, cập nhật BACKLOG;
  - `changes_requested`: tạo task `fix` trên cùng branch kèm danh sách điểm cụ thể; worker dùng `--resume <session_id>`.
- Tối đa 1 vòng `fix`. Vẫn chưa đạt → ChatGPT tự sửa hoặc tách task, ghi lý do vào PROGRESS_LOG.
- Khi Claude review ChatGPT: `BLOCKER`/`MAJOR` phải xử lý trước khi merge. ChatGPT được bác finding nếu có bằng chứng (test, số đo) và phải ghi lý do.

### 5.4 Chấm kịch bản (`script_critique`)

Rubric 0–5 cho từng mục:
- móc câu 3 giây đầu;
- động cơ và cái giá của nhân vật;
- xung đột, twist;
- dễ theo dõi trong ≤ 3 phút;
- thoại tự nhiên ở từng ngôn ngữ (EN/ZH/VI);
- khả thi khi render bằng AI;
- tải continuity;
- khớp thời lượng.

Claude trả điểm + 2 hướng viết lại cụ thể; ChatGPT gộp thành tối đa 2 phương án để chủ dự án chọn.

## 6. Worker nền

### 6.1 Thành phần (ChatGPT dựng khung; có thể giao Claude viết phần code)

- `tools/claude_worker.py`: vòng lặp xử lý hàng đợi; tái dùng pattern đã kiểm của bridge cũ (ghi file nguyên tử, receipt, idempotency, khóa process).
- `tools/claude_queue.py`: `enqueue` · `status` · `review --approve|--changes` · `stop` · `start`.
- `tools/claude_task.schema.json`, `tools/claude_result.schema.json`, `tools/claude_prompt_template.md`.
- `~/.config/systemd/user/aifilm-claude-worker.service`.
- Test cho worker dùng một CLI giả (script trả JSON mẫu) để chạy không tốn hạn mức.

### 6.2 Vòng lặp của worker

1. Có file `STOP` → nghỉ. Chạm trần ngày → ghi `STATUS.md`, nghỉ đến hôm sau.
2. Lấy task ưu tiên cao nhất trong `inbox/` → chuyển sang `running/` (lease + heartbeat).
3. `git fetch origin`; `git worktree add -b claude/<task_id> <worktree> origin/main`.
4. Gọi Claude theo 6.3. Xử lý lỗi:
   - lỗi xác thực → trạng thái `WAITING_AUTH`; ChatGPT báo chủ dự án chạy `claude` để đăng nhập lại một lần;
   - chạm hạn mức gói → `WAITING_QUOTA`, thử lại sau.
5. Kiểm kết quả:
   - JSON hợp schema;
   - không có file nào ngoài `allowed_paths`;
   - chạy lại `test_command` độc lập (không tin số test Claude tự báo).
6. Rebase lên `origin/main` mới nhất và chạy lại test. Push branch bằng URL SSH ở mục 1. Chuyển task sang `done/` hoặc `failed/`; cập nhật `budget.json`, `STATUS.md`.
7. Mỗi lần chỉ 1 job. Chỉ tăng lên 2 sau khi đo hạn mức trong 10 lượt.

### 6.3 Lệnh gọi Claude (xác nhận cú pháp bằng `claude --help` của bản 2.1.267)

```bash
cd "$WT" && claude -p "$(cat "$PROMPT_FILE")" \
  --output-format json \
  --json-schema "$(cat tools/claude_result.schema.json)" \
  --model "$MODEL" --effort "$EFFORT" \
  --max-budget-usd "$BUDGET" \
  --permission-mode acceptEdits \
  --allowedTools "Read" "Edit" "Write" "Glob" "Grep" "Bash(python3:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git add:*)" "Bash(git commit:*)" \
  --append-system-prompt "$(cat CLAUDE.md)"
```

| Cỡ | Trần/task | Thời gian | Effort | Model |
|---|---|---|---|---|
| S | 1 USD | 15 phút | medium | sonnet |
| M | 3 USD | 30 phút | high | sonnet |
| L | 6 USD | 60 phút | high | model mạnh nhất tài khoản có |

- Trần ngày mặc định 60 USD (theo chi phí CLI báo); chủ dự án đổi được.
- Không dùng `--dangerously-skip-permissions`.
- Không cho `git push` trong `allowedTools`; worker tự push sau khi đã kiểm.

### 6.4 Service

```ini
[Unit]
Description=AI-FILM Claude worker

[Service]
WorkingDirectory=/home/dragon/ai-film-dev
Environment=PATH=/home/dragon/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 /home/dragon/ai-film-dev/claude-runtime/claude_worker.py --queue /home/dragon/ai-film-dev/claude-queue --loop --poll 60
Restart=on-failure
RestartSec=30

[Install]
WantedBy=default.target
```

- Worker chạy từ bản cài cố định `claude-runtime/` (copy từ `main` mỗi khi ChatGPT merge thay đổi của worker), không chạy thẳng từ worktree đang thay đổi.
- Từ shell Desktop Commander: `export XDG_RUNTIME_DIR=/run/user/$(id -u)` rồi `systemctl --user daemon-reload && systemctl --user enable --now aifilm-claude-worker`.

## 7. Tích hợp vào "Tiếp tục"

Sửa `tools/turn_start.sh`, `tools/turn_end.sh` và `CONTINUE_PROTOCOL.md`:

1. `turn_start` in thêm mục CLAUDE:
   - worker có đang chạy không;
   - số task inbox / running / done chưa review / failed;
   - chi phí hôm nay so với trần;
   - các kết quả chờ review (task, status, test, branch).
2. Việc đầu tiên mỗi lượt: review mọi kết quả Claude (mục 5.3).
3. Giữ hàng đợi Claude luôn có 2–5 task READY đúng milestone, để Claude làm cả giữa các lượt.
4. Mọi thay đổi ChatGPT tự làm → đẩy lên branch `chatgpt/<task_id>` + enqueue `review` cho Claude; merge ở lượt sau khi review pass. Việc nhỏ khẩn cấp được merge trước, review hậu kiểm, ghi rõ.
5. `turn_end` ghi thêm vào PROGRESS_LOG: `claude: {dispatched, done, merged, failed, fix_rounds, findings_valid, cost_usd}`. BACKLOG dùng `owner: claude | chatgpt | owner`.
6. Báo cáo cho chủ dự án thêm 1 dòng: "Claude: … xong, … đã merge, … đang chạy, chi phí hôm nay …".

## 8. KPI phối hợp

| KPI | Mục tiêu | Mốc trước |
|---|---|---|
| Task Claude DONE / dispatched | ≥ 80% | 0 task sau pivot |
| Task chết vì trần/timeout | < 10% | 23% (22–24/09) |
| Merge lần đầu không cần `fix` | ≥ 60% | — |
| Thời gian dispatch → merge (trung vị) | ≤ 1 lượt | — |
| Lỗi thật bắt được nhờ review chéo (mỗi bên) | ghi nhận mỗi lượt | 0 (không có review chéo) |
| Claude rảnh khi còn task READY | ≈ 0 | rảnh toàn thời gian |
| Lượt không có tiến độ milestone | ≤ 1 lượt liên tiếp | nhiều lượt "no media" |

Retro mỗi 10 lượt: chỉnh cỡ task, trần, phân vai; thay đổi nào không cải thiện KPI thì hoàn tác.

## 9. Chống lặp lại lỗi cũ

- Trần quá thấp → trần theo cỡ task, cho phép `--resume`.
- Review không có tool → review nào cũng chạy test.
- Ping-pong → tối đa 1 vòng `fix`.
- Xây hạ tầng khi bị chặn:
  - không enqueue việc không gỡ chặn milestone sớm nhất;
  - milestone bị chặn vì chờ chủ dự án quyết quá 2 lượt → ChatGPT hỏi đúng 1 câu ở đầu báo cáo.
- Hai bên sửa cùng file → dùng `allowed_paths`; ChatGPT không sửa file của task đang RUNNING.
- Lệch nền → fetch trước mỗi task; rebase và chạy lại test trước khi trả kết quả.
- Chi tiền, publish, secret, `main` → cấm với worker.

## 10. Kế hoạch triển khai (2–3 lượt ChatGPT)

**Lượt A — dựng khung**
1. Hỏi chủ dự án 1 câu: trần Claude mỗi ngày (mặc định 60 USD theo chi phí CLI báo, 1 job/lần), đồng thời xác nhận tài khoản Claude là gói thuê bao hay API.
2. Tạo `claude-queue/`, schema, prompt template, `claude_worker.py`, `claude_queue.py`, test bằng CLI giả; chạy test.
3. Cài service, bật, kiểm `STATUS.md`; thử `STOP`.

**Lượt B — chạy thử thật**
4. Enqueue 3 task nhỏ:
   - (a) `review` batch016 của ChatGPT, có chạy test;
   - (b) `implement` cỡ S gỡ chặn M2 mà không tốn GPU;
   - (c) `script_critique` cho "Last Train Signal" theo rubric 5.4.
5. Review kết quả, merge. Sửa `turn_start`, `turn_end`, `CONTINUE_PROTOCOL.md`, `CLAUDE.md` theo mục 7.

**Lượt C — chuyển hẳn**
6. Đổi `owner` trong BACKLOG: code/test → `claude`; điều phối → `chatgpt`; quyết định → `owner`.
7. Ghi KPI từ lượt này; retro sau 10 lượt.

**Hoàn thành khi:**
- Chủ dự án chỉ gõ "Tiếp tục" trên ChatGPT, và trong 1–2 lượt có task Claude được tạo, chạy nền, review và merge mà không ai phải mở Claude.
- Worker tự dừng khi có `STOP` hoặc chạm trần; không đụng `main`.
- Có ít nhất 1 review Claude → ChatGPT và 1 review ChatGPT → Claude, đều có chạy test.
- PROGRESS_LOG có trường `claude` ở mỗi lượt.

## 11. Lệnh kiểm nhanh

```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
systemctl --user status aifilm-claude-worker --no-pager | head -5
cat /home/dragon/ai-film-dev/claude-queue/STATUS.md
ls /home/dragon/ai-film-dev/claude-queue/{inbox,running,done,failed}
tail -20 /home/dragon/ai-film-dev/claude-queue/worker.log
touch /home/dragon/ai-film-dev/claude-queue/STOP    # dừng khẩn
```

## 12. Prompt khởi động cho ChatGPT

```text
Đọc handoffs/CHATGPT_CLAUDE_AUTOMATION_HANDOFF_2026-09-25.md (GitHub branch handover/review-2026-09-24, hoặc /home/dragon/ai-film-dev/handoffs/).
Mục tiêu: Claude chạy tự động qua worker nền và làm việc cùng bạn theo mục 2–7; tôi chỉ thao tác trên ChatGPT.
Bắt đầu Lượt A (mục 10). Nếu cần, hỏi tôi đúng 1 câu về trần Claude mỗi ngày.
```
