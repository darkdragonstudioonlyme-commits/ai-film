# AI-FILM-SERVER — Phase00 implementation, dev1

**Work item:** IMPL-P00-001 · **Mode:** IMPLEMENTATION · **Status:** IMPLEMENTATION_PARTIAL

> Đây là source drop một phần, **không phải bộ cài Windows/WSL đã hoàn tất**. Native backend chưa được implement/đăng ký. `apply`, native `preflight`, `verify` và `support-bundle` ở CLI trả **11 / NATIVE_BACKEND_NOT_IMPLEMENTED**. Không có `--force`, `--simulate-as-site` hay đường cài đặt bỏ gate.

## Đã có

Source Python không dùng dependency bên thứ ba cho bounded JSON/canonical hashes, deterministic plans, normalized exits, pinned-document policy, SITE/LAB authorization predicates, resource/profile/drift checks, pre-C3 protection, restore-envelope/terminal checks, admission/fence orchestration, journal filesystem POSIX cho workspace, safe in-memory bundle assembly, pure Windows command-vector compiler và workspace CLI. Tests chạy trong Linux workspace, không trên target của người dùng.

Kết quả actual nằm ở `evidence/WORKSPACE_TEST_REPORT.json`: 185 tests, 0 failures, 0 errors, 0 skipped tại lần chạy đã ghi. Đây là test counts của source drop, **không** phải 185 acceptance cases đã PASS trên Windows. Các mandatory T/F/subcases trong `config/required-native-test-inventory.json` vẫn NOT_RUN.

## Chưa có

Windows host collector/ACL/trust bootstrap, global native guard và durable native storage, native process supervisor/actuators, lifecycle/resume/restore execution, live network/guest/epoch collectors, đầy đủ field-level evidence integrations, protected snapshot reader và atomic native publisher. Native test harness chưa được implement; file inventory chỉ liệt kê các case phải thực hiện, không giả thành harness.

`OperationEngine` là orchestration core được exercise với injected in-memory fixture backend. `MemoryGuard`/`MemoryStorage` chỉ nằm trong `tests/helpers.py`; không phải implementations của host-global contract. `journal_files.FileJournal` chỉ được exercise trên POSIX và chặn trên Windows trước ghi. `windows_commands.py` **chỉ tạo argv**, không launch process.

## Chạy lại workspace tests

Trong một Linux workspace tách biệt có Python phù hợp đã được chuẩn bị, từ root của package:

```bash
python tools/run_workspace_tests.py
PYTHONPATH=src python -m aifilm_p00 preflight --workspace-only
PYTHONPATH=src python -m aifilm_p00 recovery-notes
```

Không có bước tự cài Python/WSL/dependency. Interpreter thực tế của lượt authoring được ghi là CPython 3.13.5 trên Linux; không coi đó là pinned Windows production runtime. `requires-python` là yêu cầu source-level, không phải compatibility certification cho mọi interpreter.

`dry-run --binding <json>` chỉ tạo document plan từ input, không inventory host, không cho phép native execution. Nó không biến caller-supplied fields thành actual observations. Template `config/host-binding.template.json` cố ý **không executable**, chứa unknown/null, không có SID/path/payload/receipt giả để chạy.

## Định danh và trust

Normative contract set: `f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee`, đã có REVIEW-P00-002 PASS. Exact inputs và companion approval được giữ trong `contracts/`; text candidate NOT_APPROVED trong tài liệu lịch sử không bị sửa.

Approval execution được tách khỏi semantic plan digest để không tạo self-hash cycle. `PinnedStore` là pure consumer nhận role/digest pins từ trusted port, **không phải production trust store loader**. Các schema receipt chuẩn hóa trong tests là synthetic inputs, không thay bản review/qualification gốc. Native adapter tương lai phải xác thực raw original artifact, provenance/actor/ACL và normalization trước khi cấp các trusted objects này.

## Tài liệu đọc tiếp

`docs/IMPLEMENTATION_STATUS.md`: interface coverage và giới hạn. `docs/REMAINING_IMPLEMENTATION.md`: phần code còn thiếu. `docs/TRACEABILITY.md`: AC/T/F → source → workspace tests → native status. `docs/RECOVERY.md`: runbook. `docs/CODE_REVIEW_HANDOFF_DRAFT.md`: handoff **NOT_READY**. State/checkpoint V6 giữ implementation IN_PROGRESS và gate CODE_REVIEW_PASS chưa đạt.

Không publish code-review approval, qualification receipt, E00-17 accepted assessment, HOST_READY hay promoted baseline trong source drop này.
