# PHASE00_IMPLEMENTATION_STATUS_V1

## Kết quả

**PARTIAL — IMPL-P00-001 chưa đạt exit condition AUTHOR_COMPLETE.** Đây không phải chỉ thiếu Windows test evidence: một số Windows/native implementations thực sự chưa được viết và nối vào interfaces. Vì vậy không chuyển toàn work item sang CODE_REVIEW.

| Contract interface | Phần source có | Phần còn thiếu |
|---|---|---|
| preflight | Workspace metadata CLI; profile/resource validators; passive planning không gọi WSL | Actual Windows principal/host/runtime/registry/storage/config collectors; C1 discovery; protected output/admission integration |
| dry-run | Bounded JSON, input/path syntax validation, deterministic semantic hash, operation scope, detached approval reference, explicit expected state/budgets | Native observation-to-plan binder, đủ typed group facts và stage applicability; cannot label APPLICABLE from untrusted JSON |
| apply | Authorization core, operation orchestrator, admission/fence ports, command-vector compiler | Windows actuator/supervisor, actual observed postconditions, OOBE/reboot/resume, payload verification handles, create/adopt/export/import integration |
| verify | Pure predicates cho resources, affected-resource health, restore envelope, final epoch/time/source checks | Actual native assertion runners, sentinel/perms/content, source/clone lifecycle, network, boot witnesses và automatic invalidation events |
| support-bundle | Record envelope, allowlisted redaction, in-memory ZIP/member hashes, completeness/outcome core | Actual protected record catalog and access verification, full conditional subfield schema, bounded live collectors, native atomic output publisher/exit18 and trusted scanner integration |
| recovery/rollback notes | Runbook giữ dữ liệu và các stop conditions | Executable native recovery/reconciliation path với exact original plan/actor context; no blind retry |

## Module inventory

`codec.py`: JSON caps, duplicate-key/NaN rejection, canonical UTF-8, timestamps, identifiers và lexical Windows paths. Lexical path validation **không thay** actual NTFS/reparse/ACL/volume checks.

`plans.py`: permitted purpose/action mapping, bounded allocations, semantic digest. Detached `approval_ref` nằm ngoài `semantic`; original signed/approved scope vẫn phải khớp plan digest. `expected_after/profile/before` hiện là object slots, chưa phải full field-level native schema.

`authority.py`: checks role-pinned document bytes, matching build/test/profile/receipt/lab/actor and validity windows. Native out-of-band pins acquisition, original-document normalization, withdrawal verification và live timing/identity acquisition còn pending. Đây không phải signature verifier và không có quyền tự phát hành receipt.

`policy.py`: D00-01/02/04/08/10/12/13 predicates. Input proof booleans là typed model của trusted evidence adapter tương lai, không đủ để tin một JSON caller tự viết. Group-specific content manifests/measurement validation chưa hoàn tất.

`admission.py`: one admission protocol, write-ahead fence, event ordering, unresolved state và explicit terminal reconciliation. Đây là protocol implementation phụ thuộc ports; chưa có Windows host-global primitive/root implementation.

`journal_files.py`: actual atomic writes/fsync, hash-chain events, terminal archive retention trên POSIX workspace. Windows constructor chặn; không dùng POSIX test thay cross-session/SID native proof.

`engine.py`: fixture-executable orchestration. Native port chưa có; full operation-specific prerequisites/postconditions, per-step renewed authority và original-plan reconciliation/resume còn phải hoàn thiện. Không coi dependency injection tự nó là native backend.

`evidence.py`: safe projection and byte assembly, strict unknown-field rejection, scanner failure blocks publication, protected raw excluded, no E17 self-reference. Return `component_eligible` chỉ là pure core calculation trên facts được cung cấp, không phải authenticated gate assessment. Complete group-specific stage/conditional semantics chưa implement.

`windows_commands.py`: argv compiler giữ explicit target/location và no-restart intents. Chưa kiểm syntax/behavior với locked Windows WSL CLI; chưa có process execution hoặc native completion evidence.

## Tests và lịch sử authoring

Actual author run đầu lỗi parse trong `tests/test_core.py` do Windows path raw string kết thúc bằng backslash. Đã sửa fixture, không thay acceptance. Logs `workspace_test_first.txt` đến `workspace_test_fourth.txt` giữ history; final exact-source run nằm trong `WORKSPACE_TEST_REPORT.json`/`WORKSPACE_TEST_LOG.txt`.

185 workspace tests cuối PASS, gồm JSON/paths, plan hash/permissions, synthetic qualification negatives, resource boundaries, protection/restore/freshness, memory admission/fences, POSIX journal persistence, safe bundle/caps/privacy, literal argv, fixture orchestration và CLI native refusal. Không có test coverage percentage claim. 86 native/acceptance IDs/subcases chưa chạy; workspace results không đóng AC00-01…08.

## Decisions và mode

Không thay Blueprint, FD-01…08, D00-01…14 hoặc four normative V2 documents. Những thiếu sót hiện tại là implementation omissions; chưa có bằng chứng contract không khả thi để mở DESIGN_GAP. Nếu native implementation cần thay approved behavior hoặc thêm prerequisite không nằm trong scope thì phải tạo DESIGN_GAP trước thay đổi.

Code review chưa thực hiện. Sáu DR findings vẫn REVIEW_PASS ở design-only scope; không dùng các closure đó để chứng nhận source này. Phase 00 vẫn chưa DONE.
