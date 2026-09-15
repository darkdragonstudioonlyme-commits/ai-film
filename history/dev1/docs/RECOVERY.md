# Phase00 recovery/operator notes — implementation partial

**Không phải executable host recovery tool.** Native actions chưa implement; mọi production/host instruction bên dưới là boundary để tiếp tục authoring và review, không lệnh đã được cho phép chạy.

## Native timeout hoặc crash

Giữ original plan, approval, run identity, intent, native process-start witness và reservation. Không xóa fence/lock theo tuổi, không lặp lại install/import vì client timeout. OS primitive được release không chứng minh native writer đã dừng. New run phải bị chặn đến khi original authorized reconciliation xác định terminal state và commit journal; không sửa JSON để tự tạo terminal proof.

Nếu journal commit sau mutation lỗi, giữ fence và diagnostics protected. Không thực hiện step tiếp theo. Pending reboot/OOBE phải chờ owner action đúng scope và valid renewed approval; không tự reboot. Concrete native binder/supervisor còn IMPL-REM-02/05.

## Trước C3

Không thay runtime hay restart host chỉ dựa maintenance approval. Cần impact coverage của mọi owner bị ảnh hưởng, consistent pre-change checkpoints, exact restore proof có từ trước, independent recovery environment và quyền truy cập khi source WSL không khởi động được. Existing target sạch vẫn cần independent proof; clean same-host functional clone không thay nó.

Source ghi tiếp sau consistency boundary thì checkpoint proof không đủ cho C3 hiện tại. Missing recovery material → stop; không tạo backup sau lỗi rồi gọi là pre-C3 evidence. Post-C3 health của resource khác thiếu/FAIL giữ stage chưa hoàn tất.

## Restore

Giữ original, trusted checkpoint và content manifest. Import chỉ exact NEW target/path được cho phép; no overwrite/unregister. Preboot envelope phải được controller ngoài guest xác minh trước import/launch, đặc biệt network/production writable mappings/credentials. Sensitive/unknown source không được mở lại bằng “isolation”.

Default sau test là stop/retain clone và tính retained bytes, không auto cleanup. Pre/post proof liên kết checkpoint digest; destination report không thay source terminal assertions.

## Network, resources và evidence

Không đổi DNS/VPN/firewall/AV/.wslconfig để ép PASS, không xóa backup/target để làm capacity đủ. Raw protected refs, passwords, environment, home directory, backup tar không được đưa vào public support bundle. Privacy không chứng minh được → no publication; mandatory thiếu → incomplete, không scope-switch thành complete.

Terminal evidence sau last source-affecting lifecycle/restore; không sửa timestamp hoặc lấy old network PASS ghép epoch mới. Source/kernel/user/config/actual resources/network/sentinel phải quan sát lại đúng context.

## Workspace test artifacts

POSIX temporary journals/synthetic archives do tests tạo trong temporary directories, không phải target backup. `evidence/WORKSPACE_TEST_REPORT.json` là author result, không E00-13 receipt. Có thể chạy lại tests trong riêng workspace; không dùng fixtures để ký hoặc upload như actual site facts.
