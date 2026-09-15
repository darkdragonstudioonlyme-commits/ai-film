# OPEN_IMPLEMENTATION_ITEMS_V1

Đây là danh sách phần **chưa hoàn tất**, không phải findings do CODE_REVIEW tạo, không phải design waivers hoặc acceptance bị loại bỏ. Tất cả thuộc IMPL-P00-001 và giữ code-review handoff ở NOT_READY.

| ID | Phần phải hoàn thiện | Contract/acceptance | Điều kiện để bỏ khỏi danh sách pending |
|---|---|---|---|
| IMPL-REM-01 | Windows native observation/identity/storage/path/ACL adapters; reviewed passive collector và qualified C1 guest discovery | D00-01…06, T02/03/04/06/10 | Actual source adapters + typed facts; no passive launch; Windows/WSL integration harness prepared, chưa phải test PASS trước code review |
| IMPL-REM-02 | Fixed host-global native guard, metadata initialization authority, cross-SID permissions, Windows durable fence store và process witnesses | D00-07, T07-A…J | Không caller-chosen namespace/root; one admission across entrypoints; interrupted native action vẫn có enforceable fence; no fake MemoryGuard on host |
| IMPL-REM-03 | Trusted raw document/payload/owner/qualification adapters, role pins protected outside request; exact original review normalization | D00-08/11, T14 | Không tin self-declared PASS JSON, no auto-issued receipt; native runtime dependency binding không tự cài software ngoài scope |
| IMPL-REM-04 | Full ENGINE/CREATE/ADOPT/EXPORT/IMPORT executors, payload handles, explicit target/ownership, bounded native process supervision | D00-02/03/08/09, T11/12/13, F03/10/16 | Actual native source, no arbitrary shell, no implicit fallback/reboot/unregister; observed after-state và final capacity, nonzero/native timeout correctly normalized |
| IMPL-REM-05 | Renewed authority/drift before each step, paused-run/original-plan reconciliation, restart/OOBE resume, multi-step ownership and C3 postcheck integration | D00-07/08/10/11 | Resume uses original intent + newly valid consent; no semantic purpose/hash contradiction or repeated mutation; actor/plan state tests include real admission path |
| IMPL-REM-06 | Live network, sentinel/perms/content, guest/WSL/host epochs, pre-C3 checkpoint proof, destination import/boot/stop and terminal sweep | D00-10/12/13, T04/05/09/10 | Native collectors/runners and lab canary/controller integration authored; actual measurements required later, no booleans supplied as observations |
| IMPL-REM-07 | Full E00-01…17 field catalogs/conditional requiredness, protected record access/hash verification, safe snapshot reader/publisher, scanner, output I/O outcome18 | D00-14, E register §§4–6, T08 | Full six-interface wiring; safe diagnostic output for missing caps; no group-wide PASS placeholder; E17 separate, MASTER authority external |
| IMPL-REM-08 | Native test harness/fixtures for complete supported routes and failure cases, additional core schema/route/property tests, full requirement-to-source mapping | AC00-01…08, T00-01…14, F00-01…16 | Harness is executable source, not just test inventory; limitations explicit; actual native execution still waits code review and lab authorization |

## Known integration boundaries, không che bằng “chỉ chưa test”

`Coordinator` currently exercises reconciliation with a pre-authorized model; the concrete binder relating a new reconciliation-only authorization to the original immutable plan and paused fence is missing. It must not be implemented by manually editing a plan hash or changing a CREATE plan into a different purpose under the same approval.

`OperationEngine` currently exercises a single atomic fixture operation and selected negative entry paths. It does not yet prove all route-specific source authority, target collision, full poststate semantics, post-C3 owner assertions, remaining-allocation recalculation, planned default transition or renewal checks inside a real multi-step execution. Those are part of REM-04/05, not obligations silently delegated to an operator.

`PinnedStore` and pure protection/isolation validators currently assume the trusted adapter has authenticated the provided model. That adapter is absent. Hand-authoring a JSON with true/PASS values is not a supported replacement.

`assemble` does not implement native collector execution, native publisher or all per-field stage conditions; the CLI deliberately refuses instead of using the memory assembler as an end-to-end site support bundle.

## Continuation order

Hoàn thiện REM-01/02/03 trước nối các actuator; sau đó REM-04/05/06; cuối cùng REM-07/08 và rerun workspace tests. Bất kỳ architecture/public-contract change nào phải dừng scope đó bằng DESIGN_GAP. Không cần review lại design chỉ vì source chưa viết xong, trừ khi phát hiện gap thật.
