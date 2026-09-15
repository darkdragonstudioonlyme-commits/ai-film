# PHASE00_INFRA_DESIGN_V2

**Project:** AI-FILM-SERVER  
**Work item:** INFRA-P00-002  
**Mode:** INFRA_DESIGN  
**Phase / gate:** 00 — Host / WSL / HOST_READY  
**Ngày:** 2026-09-14, Asia/Ho_Chi_Minh  
**Trạng thái:** REVIEW_CANDIDATE — NOT_APPROVED — NOT_IMPLEMENTED — NOT_VALIDATED

## 1. Căn cứ và giới hạn

Nguồn yêu cầu authoritative là “AI VIDEO SERVER — SINGLE CHAT WORKFLOW BLUEPRINT V2”, đặc biệt các mục 4–10, 11–12, 20–24, 28–32 và 40. SHA-256 của attachment: `adc4a1fcd77fe8e70ad8beb6e6a53e218399c22a397ab6bfeb04c589cf910a14`. State đầu vào là AI_FILM_PROJECT_STATE_V3; design V1 và REVIEW-P00-001/REQUIRED_CHANGES_V1 là baseline revision. FD-01…FD-08 được giữ nguyên. V1 có verdict FAIL; V2 chưa được review.

**FACT — từ project:** Stage A dùng Windows/WSL2 cho Control Plane, GPU compute tách riêng. Blueprint yêu cầu Ubuntu LTS, hướng tới systemd → Docker Engine → containers; infrastructure có preflight/dry-run/apply/verify/support-bundle/recovery, idempotency, logs và gate. Blueprint không chốt phiên bản, cấu hình tài nguyên, layout ổ đĩa hoặc test matrix Phase 00.

**FACT — đã quan sát trong chat:** đã có blueprint, design V1, review V1 và state V3 dưới dạng tài liệu. Không có inventory host, source implementation, kết quả host test, backup hoặc baseline đã promote. Việc tạo các tài liệu này diễn ra trong môi trường công cụ của chat, không trên Windows/WSL của người dùng.

**EXTERNAL EVIDENCE:** R-01A kiểm chứng tài liệu Microsoft/Canonical. Source register và giới hạn của research nằm trong PHASE00_EVIDENCE_AND_RESEARCH_REGISTER_V2.md. Research không phải host validation.

**PROPOSED DESIGN:** D00-01…06 và các ngưỡng cũ được giữ; D00-07…14 là revision đề xuất để xử lý RC-01…06, không phải trích nguyên yêu cầu của Blueprint. Chưa quyết định nào trong nhóm này được thêm vào FROZEN_DECISIONS.

**REVISION AUTHORITY:** Bốn tài liệu normative V2 là design, acceptance, recovery và evidence register. Chúng thay thế V1 cho lần review mới, không hồi tố verdict V1. Changelog/diffs chỉ để truy vết; nếu bốn tài liệu mâu thuẫn thì review phải block, không cho implementation chọn đoạn thuận tiện. Bảng mapping và trạng thái finding nằm ở FINDING_RESPONSE_MATRIX_V1.

**ASSUMPTIONS TO VERIFY:** người vận hành có quyền sở hữu/ủy quyền đối với host và distro; có thể sắp xếp maintenance; có nơi bảo vệ evidence/backup và môi trường test tách biệt khi cần. Không chứng minh được điều kiện liên quan thì nhánh thao tác bị BLOCKED, không mặc định đúng.

## 2. Ranh giới Phase 00 / 01

| Phase 00 sở hữu | Bàn giao, không triển khai tại Phase 00 |
|---|---|
| Inventory Windows, virtualization, WSL runtime, distro và tài nguyên | Windows OS upgrade, sửa BIOS/UEFI, chuyển kiến trúc host |
| Chuẩn bị WSL runtime khi thật sự thiếu/không tương thích, bằng change plan có phạm vi host | Cấu hình global tuning WSL hoặc network/security remediation ngoài profile |
| Tạo Ubuntu đã định danh hoặc tiếp nhận distro tương thích; hoàn thành first-login tối thiểu | Upgrade distro tại chỗ; chuyển WSL1 sang WSL2 trên dữ liệu hiện có |
| Xác minh non-root user, home writable và quyền quản trị Linux theo owner-approved procedure | Linux hardening, service users, SSH, package bootstrap, production dependencies |
| Ghi nhận PID 1/systemd và prerequisite khả dụng | Bật/sửa systemd và service policy nếu cần ở Phase 01 |
| Kiểm tra storage, DNS/HTTPS, stop/start, restart host có kế hoạch và recovery | Docker Engine, containers, API/DB/queue, remote GPU, CUDA, model |
| Evidence, support bundle, checkpoint, bàn giao rõ blocker Phase 01 | Production availability, workload benchmark hoặc quality baseline |

Systemd chưa chạy không tự làm FAIL HOST_READY nếu distro/WSL nằm trong profile và thông tin được bàn giao đầy đủ. Nó vẫn là yêu cầu trước khi đóng phần Linux foundation liên quan ở Phase 01. Không sửa `/etc/wsl.conf` chỉ để bật systemd trong Phase 00. [MS-SYSTEMD]

## 3. Quyết định thiết kế đề xuất

### D00-01 — Profile hỗ trợ và pinning

Profile đầu tiên là **Windows 11 x64, bản phát hành ổn định**, edition Home/Pro/Enterprise/Education, không Insider. Tại thời điểm bind execution plan, phiên bản/edition phải còn ít nhất **90 ngày** trong vòng hỗ trợ chính thức. Đây là biên an toàn vận hành do project đề xuất, không phải minimum của Microsoft. OS khác hoặc profile hết biên này phải dừng để có thiết kế bổ sung; script không tự nâng Windows. [MS-LIFE-HOME, MS-LIFE-ENT]

Guest là **Ubuntu 24.04 LTS amd64, WSL2**. Canonical vẫn liệt kê standard maintenance đến tháng 5/2029. Việc chọn 24.04 không tuyên bố đây là LTS mới nhất hoặc tốt hơn 26.04 qua benchmark. [UB-LIFECYCLE]

WSL dùng bản packaged, non-preview, version được quan sát và khóa trong execution manifest. Với distro mới theo định dạng `.wsl`, floor là **2.4.10**. Candidate cho host cần cài runtime mới là **WSL 2.7.14**, release chính thức được quan sát trong R-01A. Candidate chưa được test; không tự nâng/downgrade runtime hiện có để khớp candidate. Distro/runtime đã có được giữ nếu đáp ứng floor, channel, capability, trust và test của profile. [UB-INSTALL, MS-RELEASE]

Không dùng alias `latest`, tên `Ubuntu` không version, hoặc update tự động trong apply. Trước mutation phải bind: Windows edition/build; WSL version/channel; package identity; kernel quan sát; distro release/architecture; tên đăng ký; payload filename/source/version/size/SHA-256/trust evidence; package implementation hash. Với distro tiếp nhận không có seed lịch sử, ghi `historical_seed=UNKNOWN`; export/checkpoint mới là mốc reproducibility từ lúc tiếp nhận, không suy diễn provenance cũ.

Payload hash, SID và drive path chưa có hôm nay là **execution bindings**, không phải lựa chọn hành vi để implementation tự quyết. Nếu chưa bind/kiểm chứng thì không có APPLICABLE plan. Hash lấy từ chính file tải về chỉ chứng minh định danh byte; trust còn cần publisher/signature hoặc authenticated release metadata với trust anchor đã duyệt. Trusted metadata/key reference phải được đóng trong payload manifest trước apply. Không phát hành manifest với placeholder rồi xem là được phép chạy.

### D00-02 — Tiếp nhận an toàn và định danh target

Mỗi thao tác chỉ định rõ Windows principal, distro name và canonical base path; không dựa vào default distro. Tên gợi ý cho bản mới là `AI-Film-Control`, nhưng operator bind tên thật trước dry-run. Không được suy ra distro là project-owned chỉ từ tên. Input được parse/validate theo schema và truyền bằng argument boundaries; không eval chuỗi config hoặc ghép input thành shell expression. Path có Unicode/spaces phải được test; ký tự điều khiển hoặc input có thể đổi command scope bị từ chối.

| Hiện trạng | Nhánh |
|---|---|
| Không có WSL runtime phù hợp | ENGINE_BOOTSTRAP riêng, được chấp thuận ở cấp host; sau reboot/inventory mới mới lập distro plan |
| Runtime phù hợp, chưa có target | CREATE_NEW từ payload chính thức đã khóa; target name/path phải chưa tồn tại |
| Có distro Ubuntu 24.04/WSL2 phù hợp và owner chọn rõ | ADOPT_EXISTING; không đổi cấu hình hệ thống/user hiện có để làm nó phù hợp |
| Có Ubuntu cũ, WSL1 hoặc distro không khớp | Giữ nguyên; tạo distro song song khi được duyệt hoặc quay về design; không convert/upgrade |
| Có tên/path đích nhưng không chứng minh ownership, hoặc distro lỗi | BLOCKED; không ghi đè, unregister, sửa disk hoặc tự tiếp quản |

ADOPT_EXISTING là tiếp nhận nguyên trạng đủ điều kiện, không phải cam kết hỗ trợ mọi distro tùy biến. Nếu thiếu non-root account/quyền cần thiết, startup behavior không rõ, có dữ liệu nhạy cảm hoặc workload không thể quiesce, nhánh này bị BLOCKED. Nhánh nhận dữ liệu nhạy cảm/unknown không được mở lại bằng restore isolation; D00-13 chỉ nhận các source classes được phép. Tạo bản sạch song song không làm cho shared WSL runtime trở thành độc lập.

WSL commands của implementation phải được contract-test trên runtime đã khóa cho explicit target, location, launch behavior và native exit codes. Route mới ưu tiên local official `.wsl` với explicit name/location, không cài default distro bằng lệnh tổng quát. Thiếu capability thì fail trước mutation; không tự chọn route khác. First-user/OOBE là checkpoint tương tác được owner thực hiện, không thu mật khẩu qua config/log. [UB-INSTALL, MS-INSTALL]

### D00-03 — Phạm vi tác động và quyền

| Class | Phạm vi | Quy tắc |
|---|---|---|
| C0 | Đọc metadata host; ghi evidence vào output root được chấp thuận | Không khởi động distro ngầm; không cài tool, download payload hoặc sửa setting |
| C1 | Probe guest, network, scratch test, stop/start target | Cần chấp thuận rõ vì launch có thể chạy startup services; chỉ workspace kiểm tra thuộc project |
| C2 | Tạo target mới, OOBE, marker/workspace, import clone mới theo restore plan riêng | Plan-bound; không ghi lên resource có trước hoặc không chứng minh ownership; verify không được ngầm import |
| C3 | Enable prerequisite feature, install/update WSL runtime, reboot host | Host-wide approval + protection gate D00-10 trước bước đầu; postconditions sau C3; không reboot tự động |
| CX | Unregister distro cũ, disk format/resize/repair, in-place convert/upgrade, tắt firewall/AV | Bị cấm trong work item này |

`.wslconfig` là cấu hình shared WSL; giữ nguyên byte/hash, không đặt memory/swap/network tuning ở đây. Không chạy shutdown toàn cục như một bước mặc định. Dùng target stop/start có chấp thuận; cần thao tác global thì dừng ở C3. [MS-CONFIG, MS-COMMANDS]

Registry distro/evidence có thể thuộc user context; inventory của một user không được coi là đã thấy mọi workload của host. Bind owner SID và execution SID; elevation phải giữ đúng account. Alternate-account run-as bị chặn. Global mutation cần owner xác nhận phạm vi cross-user; thiếu quyền quan sát được ghi UNKNOWN. Không dùng quyền admin để suy ra được phép sửa mọi distro.

### D00-04 — Tài nguyên tối thiểu của gate này

Các số dưới đây là **ngưỡng thiết kế P00**, chưa phải sizing production và không lấy từ benchmark AI.

| Chỉ tiêu | Ngưỡng |
|---|---|
| Physical RAM lắp trên host | ≥8 GiB, đọc dung lượng lắp đặt, không nhầm với RAM khả dụng sau hardware reserve |
| Host logical CPU | ≥4 |
| Host available RAM tại kiểm tra | ≥2 GiB |
| Guest visible logical CPU | ≥2 |
| Guest MemTotal / MemAvailable tại kiểm tra | ≥3 GiB / ≥1 GiB |
| Guest filesystem available sau các thao tác | ≥20 GiB |
| Probe scratch | ≤64 MiB/run; sentinel persistence 1 MiB |

Đo lại ngay trước apply, trước bước ghi lớn và sau verify. Không stress RAM/CPU trên host để chứng minh floor. VM memory là shared budget, không phải reservation riêng của distro. Không đạt floor thì BLOCKED; không tự sửa `.wslconfig` hoặc khuyên mua GPU từ kết quả này. [MS-CONFIG]

**Capacity budget theo từng volume vật lý:**

`required_free(volume) = reserve(volume) + peak_additional_bytes_of_approved_plan(volume)`

Reserve là **20 GiB** với volume OS hoặc chứa distro, **5 GiB** với volume chỉ chứa evidence/backup. Các vai trò chung volume chỉ dùng reserve lớn nhất nhưng cộng mọi allocation đồng thời. `peak_additional_bytes` bao gồm payload, staging/extraction, distro mới, export, restore clone, logs và phần swap tăng thêm dự kiến; không tính lại byte đã chiếm sẵn. Guest `df` không thay cho Windows volume free space.

Bản mới đặt upper budget 20 GiB cho một distro chưa có workload; payload và expanded contents phải chứng minh nằm trong budget. Export/restore reserve thêm riêng, không coi là miễn phí. Bản tiếp nhận dùng upper bound từ logical file sizes/archive metadata và allocated VHD; không dựa riêng vào compressed download size. Không tính được bound đáng tin cậy thì chặn bước export/restore, không dùng giá trị 0. Không thử low-disk bằng cách lấp ổ thật. Quy tắc cộng budget, admission và giữ reservation xuyên native action tại D00-07 áp dụng cho tất cả target/owner, kể cả output evidence và clone giữ lại.

### D00-05 — Storage và bảo vệ dữ liệu

Distro mới đặt trên volume local NTFS do owner chọn, directory chưa tồn tại, không nằm trong thư mục cloud-sync, network share, removable media hoặc reparse/junction path. Existing distro chỉ tiếp nhận khi path/storage đáp ứng profile; không di chuyển nó. File-level compression/encryption flags và policy được kiểm kê; không tự tắt encryption hay thay BitLocker.

Workspace Linux dự kiến nằm dưới `/home/<bound-user>/ai-film-server`; Linux service data layout thuộc phase sau. Không lấy `/mnt/c` làm mặc định workspace Linux; Microsoft khuyến nghị dùng filesystem Linux cho công việc Linux. Windows evidence/cache/backup root được bind riêng và có ACL hạn chế. Không sửa VHD trực tiếp qua Explorer hoặc copy VHD đang chạy làm backup. [MS-FILES]

Trước mutation phải kiểm tra canonical path, volume identity, ownership, quyền ghi và free-space bằng phép thử trong thư mục scratch đã duyệt. Output path có sẵn chỉ dùng khi có project ownership record đúng; symlink/junction hướng ra ngoài phạm vi bị chặn. Marker/ledger phục vụ tránh thao tác nhầm, không được quảng cáo là security boundary chống administrator.

### D00-06 — Network và security tối thiểu

Giữ networking mode, DNS, VPN/proxy và firewall hiện có. Không hard-code WSL IP, không sửa resolver, không thêm listener/port-forward/inbound rule, không cài SSH/VPN agent. NAT/mirrored chỉ là observed configuration; khả năng cần cho P00 là kết nối outbound của đúng context. [MS-NETWORK]

Endpoint matrix được khóa trong plan:

| Context | Kiểm tra bắt buộc |
|---|---|
| Windows | Official Microsoft WSL payload endpoint khi cần ENGINE_BOOTSTRAP; official Ubuntu release endpoint cho CREATE_NEW |
| Guest target | Ubuntu archive `noble/InRelease` và security archive `noble-security/InRelease`, hoặc mirror tương đương có trong plan được duyệt |
| Cả hai khi liên quan | DNS, TCP 443, TLS chain/hostname, HTTPS response phù hợp và timestamp kiểm tra |

Nguồn mặc định: `https://archive.ubuntu.com/ubuntu/dists/noble/InRelease`, `https://security.ubuntu.com/ubuntu/dists/noble-security/InRelease`, `https://releases.ubuntu.com/noble/SHA256SUMS`. URL payload Microsoft và redirect/CDN chính thức phải bind theo artifact thực, không cho redirect tùy ý. Probe HEAD không đủ khi endpoint từ chối HEAD; có thể GET giới hạn kích thước để chứng minh response không phải captive portal. Timeout mỗi attempt 10 giây, tối đa 3 attempts với backoff 2/5 giây. Không dùng ping làm tiêu chí duy nhất, không bỏ TLS verification.

Proxy/VPN/trust-store đặc biệt không được tự chữa bằng nới security. Nếu phải đổi setting, tạo design change phù hợp; ghi rõ BLOCKED_ENVIRONMENT thay vì phỏng đoán code bug.

## 4. Inventory / execution binding bắt buộc

E00-01…10 giữ nghĩa cũ; E00-11…17 bổ sung ở D00-14. Tất cả host values vẫn MISSING. Một record có status UNKNOWN không thỏa precondition bắt buộc chỉ vì file JSON tồn tại.

Mọi record có host ID, collection context, thời gian UTC, timezone hiển thị, collector/package version, status và evidence reference. UNKNOWN, UNAVAILABLE, NOT_APPLICABLE khác false/absent.

| ID | Dữ liệu |
|---|---|
| E00-01 | Host alias/ID; Windows edition/build/architecture/channel; lifecycle evidence/date; owner SID, execution SID, elevation và quyền được phép |
| E00-02 | CPU virtualization/hypervisor capability, prerequisite feature state, pending reboot; WSL package/version/channel/kernel và CLI capabilities |
| E00-03 | Distro registry trong user context; running/stopped, WSL1/2, default distro; cross-user/global-impact attestation khi có C3 |
| E00-04 | Explicit target name/base path/registration identity; os-release/architecture; bound user UID/GID/home/sudo readiness; PID1/systemd, startup behavior |
| E00-05 | Host physical/available RAM, CPU; guest memory/CPU; measurement timestamps và load context |
| E00-06 | Physical volume mapping, filesystem/free space; VHD path/allocated size; proposed allocations; output ACL; sync/reparse/encryption flags |
| E00-07 | `.wslconfig` và target `wsl.conf` tồn tại/hash, parsed allowlisted settings; baseline default distro, project-owned paths và ngoại lệ cần owner xác nhận |
| E00-08 | DNS/TCP/TLS/HTTPS evidence theo endpoint/context; VPN/proxy presence không có credential; clock và network mode quan sát |
| E00-09 | Data owner/classification, critical-file manifest, quiesce procedure, backup location/hash, consistency boundary, restore environment/permission và retention; liên kết E00-12/15 |
| E00-10 | Design/code review references, implementation hash, payload/trust lock, route, plan hash, approvals, maintenance window, execution_class; liên kết qualification E00-13 trước SITE C1/C2/C3 |

Preflight C0 không mở distro đang stopped để lấp E00-04…08. Nó ghi `REQUIRES_ACTIVE_PROBE`. Operator-approved C1 inventory mới được launch target. Probe đọc không thể cam kết zero-write toàn OS do logs/startup services; cam kết là không thay config/user data và chỉ thêm file kiểm tra đã khai báo.


## 5. Contract của package tương lai

Đây là specification; không có script production trong package. Tên operation là semantic contract, không phải lệnh đã chạy. Mọi side effect phải nằm trong operation plan và action class; không có quyền ngầm phát sinh từ chữ “verify”, “recovery” hoặc “lab”.

| Interface | Inputs/output và entry | Side effects |
|---|---|---|
| preflight | C0 inventory mặc định; C1 guest discovery chỉ sau D00-11. Xuất inventory và completeness theo stage | C0 không launch, scratch guest, stop, download hay cài dependency. Project metadata/output phải theo D00-07. |
| dry-run | Observations + requested transition + trust metadata; plan, semantic diff, budgets, approvals và protection requirements | Không đổi Windows/WSL/config; không import/boot/stop để lấp unknown. Plan có thể NON_APPLICABLE. |
| apply | Exact plan/build/review refs, approvals, payload trust; admission D00-07, protection D00-10 khi C3, qualification D00-11 khi SITE | Chỉ operation plan: ENGINE, CREATE, ADOPT workspace hoặc RESTORE_EXPORT/RESTORE_IMPORT. Không thêm interface bypass gate. |
| verify | Bound test plan và observations; active probes/lifecycle dùng cùng admission và authorization như apply | Chỉ assertions/scratch đã khai báo. Export/import/provisioning là apply hoặc operator runbook riêng; verify không repair/install/update. |
| support-bundle | Immutable allowlisted evidence snapshot; scope INVENTORY / FAILED_RUN / GATE_HANDOFF; result D00-14 | Chỉ đọc protected input + ghi safe output. Không live guest collection ngầm, không upload. |
| recovery/rollback notes | Journal, checkpoint và actor-specific plan | Runbook chỉ dẫn evidence/decision boundary. Khi cần thực thi mutation vẫn phải có plan, class/quyền tương ứng; không bypass D00-07/10/11. |

### D00-07 — Một host admission guard, shared capacity và durable fence (RC-01)
<a id="d00-07"></a>

**Quyết định V2:** serialize các operation package có side effect bằng **một host-global guard**, độc lập Windows session, owner SID, target name, checkout, package version và lab/site flag. Không dùng hai lock target/host không liên hệ với nhau. Một host chỉ có một mutation reservation hoạt động. Đây là hạn chế throughput có chủ đích của P00, không phải scheduler architecture của các phase sau.

Guard contract gồm một primitive interprocess-exclusive của host và một **durable fence/journal** trong coordination root được host owner quản lý. Namespace logic cố định `AI-FILM-P00-HOST-ADMISSION`; không có caller-supplied namespace/lock-path để bypass. Implementation phải chứng minh mapping cùng host/cross-session/cross-SID ở code review và lab. Không cần service/daemon, distributed lock hoặc lock per model/GPU.

Coordination root là project metadata ngoài distro, ACL host-admin/SYSTEM và các operator đã được host owner chỉ định; không world-writable. Tạo root lần đầu cần metadata-initialization approval, đúng principal, trusted build, atomic guard acquisition và directory/path/ACL validation; chỉ tạo metadata C0, không WSL/OS feature change. Chưa có quyền tạo/đọc guard thì C0 có thể báo inventory metadata qua bounded stdout, nhưng không ghi output ngoài scope hay chạy active action. Root tồn tại nhưng không chứng minh ownership/ACL thì reject 12/16; không nhận root khác để tiếp tục. Guard không thay quyền sửa distro: owner/execution SID vẫn phải khớp cho từng target.

| Operation A / B | C0 chỉ đọc, không persistent output | C0 publish metadata/output | C1 active guest/network/lifecycle | C2 create/adopt/import | C3 runtime/host restart |
|---|---|---|---|---|---|
| C0 chỉ đọc | Có thể cùng chạy; snapshot không chứng minh freshness nếu có concurrent mutation | Có thể cùng chạy | Có thể cùng chạy, đánh dấu overlapping observation | Có thể cùng chạy, không dùng snapshot thiếu consistency để authorize | Có thể cùng chạy, không cho rằng host stable |
| C0 publish / C1 / C2 / C3 | Như trên | EXCLUSIVE | EXCLUSIVE | EXCLUSIVE | EXCLUSIVE |

RESTORE_EXPORT/import, verify active, bounded scratch và operator-run P00 lifecycle đều vào nhóm exclusive trên **host thực thi chúng**. Support bundle chỉ đọc snapshot có thể chuẩn bị trong memory; persistent output phải được serialize và budget. Một run đã giữ guard gọi step con dùng cùng run/admission identity, không tự lấy guard lần hai. Không giữ hai host guards đồng thời: export source → seal release → transfer → acquire destination → import; destination không được đòi live source lock khi đã có immutable verified checkpoint.

**Admission order bắt buộc:** authorize requested scope (không mutation) → thử acquire host guard một lần → inspect unresolved fence/native state → refresh identities/drift/resources → reserve toàn bộ remaining peak allocations theo physical volume → ghi durable intent → thực thi step → reconcile observed completion → ghi postconditions/budget → kết thúc hoặc checkpoint. Guard đang bận trả `21/LOCK_BUSY`, không queue/retry tự động. Quyền sai trả 12 trước truy cập target. Không phát sinh target lock độc lập để đảo order.

**Budget khi serialize:** đo actual free cho từng volume sau guard acquisition; yêu cầu `free >= reserve + remaining_peak_additional`. Remaining peak là **tổng các allocation đồng thời của toàn plan đang giữ reservation**, bao gồm backup/clone/output và staging chưa xóa; không lấy max từng step hay chỉ target hiện tại. Volume dùng chung lấy một reserve lớn nhất, không double-count bytes đã tồn tại. Run B dù khác target/owner/volume vẫn bị chặn khi A giữ reservation; sau A kết thúc B phải đo lại vì A có thể đã để lại distro/clone/backup. Evidence writes cũng phải được tính, không có unlimited C0 writers cạnh tranh budget ngoài guard. Không preallocate toàn bộ disk chỉ để “reserve”.

**Timeout/crash:** OS guard có thể mất khi process chết; durable fence **không** được giải phóng theo TTL. Fence lưu run/host boot identity, owner/execution SID aliases, PID/process-start witness, native action identity, intent/result, plan/build hashes và volume reservations. Process sống vẫn giữ guard khi native action chưa rõ; crash rồi run mới acquire guard chỉ để reconcile, không được dùng abandoned OS lock làm bằng chứng mutation đã dừng. Native action chưa xác định terminal → giữ `UNCERTAIN`, reject new operation 21; authorized reconciliation chỉ quan sát, không retry mutation. Safe diagnostics khi fence unresolved chỉ trong RECONCILIATION_ONLY của original authorized run, dưới guard và budget/output đã duyệt; không clear fence hay chạy queued mutation. Pending reboot/OOBE giữ fence ở AWAITING_ACTION; resume bởi actor đúng, bound approval mới nếu hết hạn, trước khi giải phóng.

Chỉ release reservation/fence sau khi ghi durable terminal observation hoặc safe pause chứng minh không còn native writer và đã thu hồi các pending operations. Timeout không thỏa điều này. Hủy run phải có reconciliation record, không chỉ xóa lock file. Lỗi ghi journal chặn mutation tiếp theo; unknown state không được tự biến thành rollback.

**Ngoài package:** guard không ngăn Windows Update, admin/user thao tác bằng công cụ khác, non-project workload hoặc lỗi ổ đĩa. Maintenance agreement hạn chế những tác động đó; kiểm drift/free space trước bước và cuối native action. Khi có external consumption/change, dừng bước kế tiếp, giữ artifact/fence cần reconcile, không kill dịch vụ hoặc suy đoán rollback. Không cam kết OS-level disk reservation hay toàn bộ host bị cô lập. Old/uncooperative package không được chạy trong maintenance scope; không chứng minh được coordination/visibility thì active operation BLOCKED.

### D00-08 — Plan binding, staged transition và run state
<a id="d00-08"></a>

Plan có schema/version, work item, execution_class (SITE/LAB), registered host identity, principal, target/route, design-contract digest và implementation digest, immutable payload/trust refs, operations/action classes, expected before/after, profile-match key, budgets, guard/fence identity, protection và qualification refs, approval/scope, maintenance window, lifecycle boundaries, recovery actor và evidence requiredness stage. Plan digest lấy canonical semantic fields; report timestamp không làm đổi semantics, nhưng approval expiry là field phải kiểm riêng. Không dùng toàn bộ package ZIP hash tự chứa plan/test result để tạo vòng self-reference.

Safety preconditions (ownership, quyền, trust, capacity, applicable qualification/protection) phải biết trước mutation. `ENGINE_BOOTSTRAP` không đòi guest tồn tại. `CREATE_NEW` dùng `NOT_YET_CREATED` cho future guest fields và chuyển thành postconditions; không coi chúng PASS trước boot. `SITE_DISCOVERY` chỉ được phép probe để thu unknown guest facts sau qualification discovery tương ứng, không mặc định guest đã eligible để ADOPT.

Approval hết hiệu lực sau 24 giờ hoặc ngay khi scope/material inputs khác. Material drift: owner/host/target identity/path, relevant config hash, unexpected default change, Windows/WSL/payload/implementation mismatch, quyền/maintenance hoặc qualification bị rút. RAM/free-space phải remeasure, không đòi equal-bytes; IP thay đổi không đổi target identity. C3 engine plan và distro plan riêng: sau engine/reboot phải re-inventory, bind plan/approval mới trước CREATE/ADOPT.

Planned runtime transition có explicit old/new values và expected evidence; không tự coi chính expected change là drift. First ever distro registration có thể làm default từ ABSENT thành exact new target **chỉ khi plan đã cho phép và lab chứng minh**. Existing default luôn giữ nguyên; không dựa CLI default hay miễn kiểm default nói chung. Thay đổi khác expected là 16 và replan. Guest/user-init changes chỉ nằm trong CREATE/OOBE allowlist; không áp dụng để sửa ADOPT.

Run state: OBSERVED → PLAN_BOUND → AUTHORIZED → APPLYING → APPLIED → VERIFIED; nhánh BLOCKED, AWAITING_REBOOT, AWAITING_USER_INIT, FAILED, UNCERTAIN. Durable intent trước mutation và observed-result sau mutation. Rerun chỉ NOOP khi postconditions thực đúng; không dựa marker để tạo lại user/distro, đổi version hoặc ghi đè. APPROVED plan ≠ APPLIED ≠ VERIFIED ≠ HOST_READY. Code review, lab validation, site validation và MASTER gate record là các evidence khác nhau.

### D00-09 — Normalized outcomes
<a id="d00-09"></a>

| Exit | Semantics |
|---|---|
| 0 | Interface hoàn thành scope; không phải phase PASS |
| 2 | Chỉ support-bundle: PARTIAL_OPTIONAL, toàn bộ mandatory safe evidence đủ |
| 10 | Invalid schema/input/path/purpose |
| 11 | Missing/unknown/unsupported prerequisite, gồm missing/stale/failed qualification hoặc missing protection |
| 12 | Permission/approval/actor attestation thiếu hoặc sai |
| 13 | Resource/capacity không đạt |
| 14 | Network/TLS/endpoint failure |
| 15 | Byte integrity/trust/checkpoint proof invalid |
| 16 | Ownership/collision/material drift/config hoặc exact-build/profile mismatch |
| 17 | Native/probe timeout; mutation có thể UNCERTAIN |
| 18 | Internal/output/journal I/O failure; không được publish thành success |
| 19 | Verify assertion actual khác expected |
| 20 | Operator action: reboot, OOBE hoặc approved recovery checkpoint |
| 21 | Host guard busy hoặc unresolved durable fence chặn run khác |
| 22 | Support-bundle INCOMPLETE_MANDATORY: thiếu/timeout/truncated mandatory evidence |
| 23 | Support-bundle BLOCKED_REDACTION: scan/redaction không chứng minh an toàn; không publish |

Native code lưu riêng với normalized exit và error category; collector timeout không tự trở thành interface 17 (D00-14 định nghĩa 2 hoặc 22). Single-fault fixtures có exact code. Multiple blockers: thu tất cả reason IDs nếu an toàn nhưng không mutation; theo entry order D00-11. Riêng publishing áp dụng precedence D00-14. Không gán root cause chỉ từ normalized exit.

### D00-10 — Pre-C3 protection gate và affected-resource postconditions (RC-02)
<a id="d00-10"></a>

Áp dụng cho **mọi C3**, kể cả planned host restart trong T00-05 và engine restart. Không cần dựng full Windows DR nhưng không được chạy C3 trên data-bearing host chỉ với metadata hoặc maintenance approval.

**Impact set (E00-12):** host identity + C3 operation/old-new state; mọi WSL distro/runtime integration thuộc các account bị tác động; mounts/external data dependencies, và Windows apps/writers mà host restart sẽ gián đoạn. Host owner xác nhận coverage, từng resource owner xác nhận data/permissions. Inventory một SID không thay cross-user attestation; unknown resource/owner/coverage chặn C3. Không yêu cầu P00 đọc secrets hoặc lục home account khác để đạt completeness.

Mỗi row gồm `resource_id/owner`, source class, precondition baseline, critical state, planned interruption, quiesce actor, backup/recovery method, proof refs, consistency boundary/exclusions, recovery environment readiness, post-C3 expected assertions/actor, authorization và retention. Resource không bị tác động cần explanation riêng; không bỏ khỏi inventory để tránh bảo vệ.

| Resource disposition | Evidence **trước C3** | Post-C3 bắt buộc |
|---|---|---|
| CLEAN_HOST_ABSENT | Current inventory + host-owner coverage attestation chứng minh không có distro/data-bearing WSL; owner xác nhận host restart không bỏ dở writers quan trọng | OS/runtime prerequisites/boot/profile; non-target distro content test N/A chỉ khi empty impact rows có evidence |
| CLEAN_REPRODUCIBLE_NON_TARGET | Chỉ fixture hoặc distro sạch chứng minh từ trusted seed + bounded allowed changes, không user/application state; exact seed/trust và recreation/recovery proof sẵn có; owner phân loại | Authorized boot/basic identity/user/storage checks, same frozen configs; không xóa/recreate tại chỗ để “kiểm” |
| DATA_BEARING_NONSENSITIVE | Consistent pre-change checkpoint ngoài distro/runtime; hash/content manifest; successful restore proof của exact checkpoint trong independent already-ready environment; no further writes từ checkpoint đến C3 | Owner-approved launch/smoke + critical-state checks theo predeclared assertions; raw evidence giữ local, safe summary vào E00-12 |
| NON_TARGET_SENSITIVE_OR_MANAGED | Existing owner-controlled backup/recovery control có proof content/access/restore và no-write boundary cho affected data, supplied dưới dạng attestation/hash refs; P00 không tự backup/boot workload này | Resource owner thực hiện exact predeclared health/state checks; thiếu permission hoặc proof → BLOCKED, không tự launch bằng admin |
| UNKNOWN / FAILED / UNPROTECTED | Không có waiver bằng approval chung | Reject 11 trước C3; quay về owner recovery/design scope phù hợp |

**Target đã tồn tại** luôn cần consistent checkpoint + restore proof, kể cả target P00 còn sạch; không dùng CLEAN_REPRODUCIBLE_NON_TARGET để bỏ AC00-05. Pre-C3 restore proof của target phục vụ recoverability; T00-09 vẫn phải kiểm post-apply checkpoint đúng version/state bàn giao. Non-target sensitive row không cho phép ADOPT sensitive hoặc P00 restore credentials; không đủ owner proof thì BLOCKED. Existing Windows apps/writers cần owner xác nhận saved/closed/recoverable qua cơ chế sẵn có; không tuyên bố export distro bao phủ Windows apps.

Trình tự: inventory/owner baseline và independent recovery readiness → quiesce writers trong authorized window → consistent checkpoint + content manifest → restore proof trước C3 → seal CPK-PRE-C3 + owner attestation → recheck source không write/drift, impact set/capacity/approval → C3. Nếu restore proof đã có nhưng source lại ghi sau boundary, proof không còn đủ: phải checkpoint/proof lại. Với managed backups, provider/owner phải chứng minh backup/replay tới đúng checkpoint; không thay bằng file timestamp. Nếu pre-C3 restore khiến source lifecycle thay đổi, recollect affected facts và re-quiesce; không invalidate proof của immutable checkpoint khi checkpoint content không đổi.

Checkpoint, instructions, access rights và independent restore capacity phải đọc/khôi phục được **khi WSL trên source không boot**. Chúng không nằm trong target, không phụ thuộc cài lab bằng chính runtime đang sửa; recovery media/bản copy sẵn có và proof precede C3. SAME_HOST_CLEAN functional proof không tự chứng minh independent recovery khi shared source runtime lỗi: pre-C3 target recovery proof dùng ISO-EXTERNAL đã sẵn có. Ngoại lệ clean clone cùng host chỉ áp dụng post-apply functional T00-09, không bỏ pre-C3 independent proof. Không cần auto downgrade/uninstall Windows runtime. Không thể đạt precondition → chặn C3, không tự ngừng các AC.

Sau C3: bắt buộc resource-owner postconditions (khác metadata-only), exact expected runtime/profile, preserved relevant config/default và data checks. Không được báo stage hoàn thành khi resource chưa được phép kiểm; ghi AWAITING_OWNER_VERIFICATION/20 hoặc FAILED/19. Host-wide restart có thể dừng non-target theo scope đã duyệt; C1/C2 target-only không được dừng chúng. Không auto restart mọi service người khác. Raw application health do owner giữ; P00 nhận safe assertion/ref đủ audit. Postcondition FAIL giữ evidence, không rollback mù và không bỏ lỗi vì target mới vẫn boot được.

### D00-11 — LAB qualification trước SITE operations, không circular prerequisite (RC-03)
<a id="d00-11"></a>

**Implementation entry** vẫn DESIGN_REVIEW_PASS cho exact contract/scope. **SITE C1/C2/C3 entry**, dù qua preflight, apply, verify hay recovery runbook, thêm qualified build evidence E00-13 trước operation đầu. C0 passive discovery chưa cần package-regression PASS vì không active WSL/system change; vẫn cần trusted/reviewed collector trước vận hành trên site. C0 metadata initialization không được smuggle probe hoặc software install.

Hai execution classes không chỉ là CLI flag:

| Class | Binding/authorization | Regression prerequisite |
|---|---|---|
| LAB | Registered disposable Windows/WSL environment ID + machine identity + fixture/snapshot refs + owner/controller attestation từ ngoài guest. Không chứa site/production/real credentials; no live production storage/network mapping. Code-review PASS/trusted exact build và approved lab test plan. | Được chạy để **tạo** regression evidence; không yêu cầu PASS của chính lần test. Test negatives chỉ trong lab. |
| SITE | Registered real-host ID + SID/target + approved plan and maintenance/protection refs | Valid qualification receipt cho exact release/profile/capabilities + active test purpose. Host tự nhận LAB nhưng không có independent registration/approval → reject 12. |

Môi trường chưa phân loại/không xác minh được → BLOCKED, không tự dùng LAB. Chuyển SITE sang LAB đòi lifecycle decommission và approval ngoài scope này; package không có `--force-lab` để bỏ bảo vệ. Attestation/hash là evidence integrity/authorization, không chống malicious host administrator tuyệt đối.

**Qualification receipt (E00-13)** do VALIDATION lập từ actual regression records và được MASTER ledger ghi nhận, không phải build tự viết `PASS`. Bind: reviewed contract-set digest và scope, implementation-content digest, code-review PASS reference, profile matrix/fixture/payload/trust digests, test-list digest, all mandatory T00-01…14/F00-01…16 results, closure/disposition of gate findings, lab identity/actor, issued_at UTC và withdrawal record. Code/build digest chỉ gồm executable/config/test assets cần kiểm, không tự hash receipt chứa digest đó. Verification dùng trusted review/ledger artifact và hashes đối chiếu independent refs, không tin unchecked input JSON.

Full release regression vẫn phải cover CREATE_NEW, ADOPT_EXISTING, ENGINE_BOOTSTRAP cùng recovery; không gỡ một route để né RC. Matrix có operation-purpose rows cho DISCOVERY, ENGINE, CREATE, ADOPT, SITE_VERIFY và RESTORE. `DISCOVERY` cho phép guest eligibility UNKNOWN, nhưng chỉ bộ non-invasive probes đã qualify; không cho ADOPT/mutation thêm cho guest chưa rõ.

**Matching rules:** exact contract/build/test-set hashes; Windows x64 version/edition/build và WSL package/kernel/capability profile đã test; payload digest theo route; networking/storage/startup source class thuộc tested profile row. Host/SID/path/serial/IP/lượng free space không cần giống lab; là site bindings đo thật. Với ENGINE match pre-profile ABSENT/observed và expected post-profile; không yêu cầu WSL chưa cài phải báo version. Unknown effective network/startup trong DISCOVERY chỉ được thu facts trong bounded purpose; mismatch sau probe chặn CREATE/ADOPT, không được dùng discovery qualification cho chấp nhận host. Không có matching row → 16/PROFILE_NOT_QUALIFIED, đưa lab bổ sung, không “gần giống” tự duyệt.

Receipt validity đề xuất **30 ngày** kể từ issued_at, cùng contract/build/profile/test hashes và không có failure mới/revocation/gate blocker. Đây là policy mới cho RC-03, không phải vòng hỗ trợ Microsoft. Signature/trust policy và supported OS margin vẫn kiểm tại execution. Missing/stale/FAIL/withdrawn receipt → 11; byte integrity/trust sai → 15; exact build/profile mismatch → 16; thiếu actor/approval → 12. Review PASS nhưng missing lab → **không SITE C1/C2/C3**.

Entry checks có thứ tự: input/schema → host/principal/class/actor approval → trusted design/code/build/payload refs → valid qualification (SITE) / registered test fixture (LAB) → exact purpose/profile match → host guard/fence → refreshed stage preconditions/resources → C3 protection nếu áp dụng → durable intent. Missing E00-12 không cấm chạy approved owner protection steps để **tạo** E00-12; chúng vẫn cần qualification/guard và source data authority, không phải C3. External operator/native recovery khi source không hoạt động là work item riêng; P00 không giả rằng mọi incident đều có thể chạy build đã qualify trên host hỏng.

### D00-12 — Effective state, activation epochs và terminal gate (RC-04)
<a id="d00-12"></a>

Hash config-on-disk không chứng minh settings đang có hiệu lực. Microsoft mô tả settings được áp dụng khi subsystem restart/start; tài liệu đó là rationale, không phải evidence của site. [MS-CONFIG] V2 yêu cầu **quan sát behavior sau lifecycle**, không sửa config chỉ để test.

Evidence record phân biệt LAB (package correctness) với SITE (current target assertions). SITE có `host_id`, host boot witness, runtime/contract/build digests, target registration identity, guest kernel/init-session witnesses, observed lifecycle sequence, config snapshot và `activation_epoch`. Epoch là identifier của khoảng observation có witnesses xác minh được, không chỉ string tự gán. Package ghi bắt đầu/kết thúc, native lifecycle journal, guest/init witnesses; không chứng minh được continuity/boundary thì mark UNVERIFIABLE và recollect, không ghép PASS.

| Evidence/assertion | Invalidation | Hành động |
|---|---|---|
| Requirement/design/code review + lab receipt | Contract/build/profile/test change, new blocker/revocation, receipt expiry | Re-review/requalify phù hợp; site reboot riêng không invalidate lab trên host khác |
| Disk config/hash/identity | Actual change; first-target default transition chỉ hợp lệ nếu expected | Planned post-state phải match; unexpected → 16, replan |
| Guest user/home, effective CPU/RAM/PID1/network, live health | Guest activation, WSL VM restart, host reboot, external settings/network event; không cần hash file thay đổi | Rerun affected assertions sau boundary |
| Free-space/RAM headroom | Allocation/release/other writer, lifecycle hoặc thời điểm trước ghi | Remeasure trước bước và terminal sweep; không dùng snapshot dự toán |
| Sentinel/lifecycle proof | Critical content/user/perms thay ngoài plan, provenance mất | New consistent sentinel boundary và rerun relevant lifecycle tests |
| Immutable checkpoint/restore proof | Checkpoint bytes/content scope changed hoặc restore/source identity không khớp | Proof của old checkpoint chỉ còn historical; không thay proof mới |
| Terminal report | Boundary/material drift trong/ sau sweep, thiếu start/end witness, expired collection window | Không eligible cho fresh gate; recollect terminal, không xóa kết quả cũ |

**Order/dependency site:** C0 inventory → qualified C1 discovery → protection gate nếu ENGINE → engine + planned resume/reinventory → fresh distro plan → CREATE/ADOPT/OOBE → basic assertions → target stop/start + sentinel → pre-C3 protection cho planned host restart → owner host restart + resume/affected-resource checks → post-apply checkpoint/export + T00-09 restore tại destination được duyệt → stop/retain clone, account retained bytes → **TERMINAL sweep** T00-02/03/04/10 + sentinel/content check và E00-14 → seal snapshot → sanitized GATE_HANDOFF bundle → gate assessment record. Pre-C3 restore có thể cần diễn ra sớm hơn như dependency D00-10; không thay post-apply T00-09. Không vòng tròn đòi post-apply proof trước CREATE.

Terminal sweep chạy sau **mọi lifecycle/restore step thuộc handoff plan có thể ảnh hưởng source**, dưới source host guard; nếu có startup bắt đầu sweep thì activation đó precedes first assertions. Ghi start/end witnesses, không reboot/terminate giữa assertions. Default final state: source target running sau verified launch, restore clone stopped/retained. Không tự stop target sau sweep rồi gọi behavior trước stop là current. Nếu owner chọn final state khác, cần plan có final revalidation phù hợp trước gate.

Terminal sweep phải kết thúc trong **30 phút**; gate local evidence assessment seal trong **15 phút** sau sweep, có final config/epoch/resource observations. Đây là validity windows đề xuất P00, không phải SLA. Nếu collection/assembly dài hơn, recollect sweep; không đòi reviewer tương tác xong trong 15 phút: MASTER sau này có thể ghi nhận historical HOST_READY **as_of thời điểm seal**, với evidence hash và không claim host đang khỏe vô thời hạn. Muốn current HOST_READY sau thay đổi/khởi động khác phải terminal verify lại. Lỗi privacy/missing evidence về sau giữ gate chưa được chấp nhận dù snapshot đã seal.

Package evidence LAB không phải cùng host với SITE; chỉ phải cùng reviewed contract/build và qualified profile relation. Site terminal assertions phải cùng source host/target và compatible final epoch. Restore destination có host ID riêng, liên kết bằng immutable checkpoint digest và source manifest, không thay thế nguồn. Không ghép Windows network PASS của lab với guest network PASS của site để đạt AC00-04.

### D00-13 — Restore source classes, isolation envelope và actor contract (RC-05)
<a id="d00-13"></a>

Không mở rộng ADOPT sensitive/unknown. Trước export xác định source class và critical contents; sau export hash identity bind vào restore plan. Không scan một vài secrets rồi mặc định sạch.

| Source class | Điều kiện chứng minh | Destination được phép |
|---|---|---|
| CLEAN_P00 | Trusted seed + full P00 provenance; chỉ OOBE, named project files, sentinel và baseline OS-generated changes; startup/packages/mounts/credential changes đều nằm trong explicit allowlist của trusted fixture; không custom workload, synced home, tokens/keys hoặc undeclared file/import | ISO-EXTERNAL; SAME_HOST_CLEAN có ngoại lệ bên dưới |
| ADOPT_NONSENSITIVE_QUIESCED | D00-02 eligible; owner classification + startup/package/mount inventory; no real credentials, quiesce được; exact checkpoint/contents được phép đưa vào restore environment | Chỉ ISO-EXTERNAL, dù không có secrets |
| SYNTHETIC_LAB | Controlled fixture/digest; canaries giả và deliberate startup probes, không site data/credentials | Chỉ ISO-EXTERNAL registered lab; không boot adversarial fixture ở site |
| SENSITIVE / UNKNOWN / NONCONSENTED | Không đủ điều kiện P00 restore | BLOCKED 11/12; không bypass bằng chọn “isolated” |

**ISO-EXTERNAL minimum envelope:** disposable Windows/WSL machine/VM độc lập source, đã chứng minh WSL2 capability trước nhận checkpoint; controller/physical-owner quản lý isolation **ngoài restored distro và ngoài quyền của cloned startup**. Exact method có thể là detachable virtual devices của VM hoặc dedicated disconnected host, nhưng inspection/proof phải thỏa cùng assertions dưới đây; không dựa file config trong clone. Không yêu cầu chọn/mua hypervisor trong P00; environment không đáp ứng profile → BLOCKED.

Pre-first-boot attestation E00-15 phải gắn destination identity, session/snapshot, checkpoint hash và timestamp trước cả import có thể auto-launch. Nó liệt kê/kiểm: (1) không network path/uplink tới production/Internet, mọi vNIC/physical radio có thể egress đã disconnected/disabled ở management/physical boundary; (2) không production disk/network share/backup-of-record mounted writable; (3) không shared folder, clipboard/file/drive redirection, USB/storage passthrough hay credential/SSH-agent forwarding ngoài allowlist; (4) lab Windows identity không domain/production sign-in, không real secrets; (5) các vùng ghi cho phép chỉ disposable lab OS/distro/scratch/evidence, không source/backup-of-record; (6) observer/immutable source proof không writable bởi clone; (7) transport staging là offline working copy hash-verified, original backup-of-record vẫn protected ngoài envelope. Không lấy guest lời báo “network disabled” làm enforcement proof.

Restore host's own disposable Windows volume có thể được guest truy cập nếu thuộc lab writable allowlist; đó không phải production containment escape. WSL có automount/interop documented [MS-CONFIG], nên cấm mapping từ lab này ra dữ liệu thật và dùng external read-only/absent boundaries cho vùng không cho ghi. Không yêu cầu sửa `.wslconfig`, firewall hay DNS của **source** để tạo lab isolation. Management-plane isolation lifecycle do lab controller thực hiện trong lab plan, không bị lẫn với C3 trên source.

**Proof trước boot + negative test:** controller record/device attachment inventory và lab prequalification chứng minh envelope cho exact session; invalidate khi NIC/share/credential/device policy đổi. T00-09 fixture startup cố kết nối qua Linux và Windows-interoperability path, ghi vào synthetic read-only/absent out-of-envelope paths và canary backup copy. External observer ghi egress không vượt boundary, canary không đổi; allowed scratch write thành công để tránh false negative do fixture không chạy. Không dùng endpoint hay credentials production. Before-boot assertions thất bại/không quan sát được → block import/launch. Post-boot denied probes bổ sung, không thay pre-boot enforcement.

**SAME_HOST_CLEAN exception (post-apply functional T00-09, không thay independent pre-C3 proof):** chỉ CLEAN_P00 có complete provenance và exact allowlisted changes. Nó là trusted clean clone functional restore test, **không phải isolation sandbox**. Owner cho phép ordinary baseline startup/runtime/network access và xác nhận không có application credential/workload/autoconnect; mount/startup/input bất kỳ không được phân loại thì dùng ISO-EXTERNAL hoặc block. Không chạy synthetic dangerous startup ở đây. Cần bound source/destination names/paths, current source config preserved, new path unused, source data authority, no writable mapping bổ sung, guard/budget và approval C1/C2. Baseline host exposure được ghi thẳng trong E00-15; không báo network-isolated. External isolation branch vẫn phải PASS package regression, không N/A vì site chọn clean clone.

**Ai thực thi gì:** source owner quiesce (C1); package `apply` với `RESTORE_EXPORT` ghi approved archive (C1 guest lifecycle + C0 protected output, exclusive); lab controller chuẩn bị envelope bên ngoài package/guest và xác thực attestation; package `apply` với `RESTORE_IMPORT` chỉ tạo exact NEW clone (C2), no implicit launch; `verify` launch/assert/stop clone (C1); owner chủ động reboot nếu plan cần (C3). Các operation phải dùng qualified build/purpose trên SITE, registered lab test plan trên LAB, cùng guard trên host tương ứng. Không biến verify thành import. CLI capability no-auto-launch cần actual lab proof; thiếu thì reject trước import, không dựa tên command.

Default cleanup là **stop và retain clone/checkpoint**, charge retained bytes vào final capacity. Không unregister tự động, không wildcard. Destroy disposable lab sau khi evidence được seal cần controller disposal approval riêng; xóa clean clone cùng site cần separately authorized exact-resource disposal runbook ngoài default P00 flow, không làm mất original/backups. Absence of cleanup permission không tự cho xóa; thiếu capacity để retain làm BLOCKED trước tạo. Import/boot cùng host có thể đổi shared lifecycle; D00-12 terminal sweep luôn diễn ra sau phần này.

### D00-14 — Evidence catalog, completeness và support-bundle semantics (RC-06)
<a id="d00-14"></a>

E00-01…10 giữ inventory semantics. Catalog thêm: E00-11 admission/journal/budgets; E00-12 pre/post-C3 protection; E00-13 lab qualification; E00-14 terminal report; E00-15 isolation/checkpoint/restore report; E00-16 support-bundle outcome; E00-17 gate assessment. Bảng file/record/requiredness cụ thể ở Evidence Register V2 §§4–7 là normative cùng section này.

Record tối thiểu: schema_version, evidence_id/record_id, status, source_kind LAB/SITE/DOCUMENT, work_item/run/step/operation, host/target aliases, collector/build/contract hashes, timestamp_utc, stage/route, expected/actual refs, native/normalized exits, lifecycle/epoch refs khi applicable, protected_ref/digest, safe_summary_ref/digest và sensitivity label. `NOT_YET_CREATED`, `UNKNOWN`, `UNAVAILABLE`, `NOT_APPLICABLE` không đồng nghĩa PASS. Alias↔SID/path map chỉ protected local. Không gán media trace IDs chưa có.

**Ba completeness khác nhau:** INVENTORY có đủ observations/declared unavailable theo stage; BUNDLE có đủ safe evidence cho declared scope; GATE có actual mandatory assertions PASS + review/qualification/protection/restore/terminal proof. Một inventory với guest NOT_YET_CREATED có thể complete-for-stage nhưng gate chưa đủ. Không có record/file placeholder nào được coi là actual test.

Raw cần thiết giữ local ACL owner/admin, không transcript chứa mật khẩu. Capture field allowlist ngay từ collector; không toàn environment/home/repo, history, arbitrary argv, `.env`, SSH keys, tokens, browser data hay backup tar. Nested unknown errors không đưa nguyên stderr vào safe output; giữ allowlisted error code/category và redact field-by-field trước serialization. Không public raw SID/path/query credential; recursive handling cả nested objects/arrays, URL userinfo/query, encoded values và error paths. Alias maps/protected evidence không nằm trong bundle. Capability “sanitized” là theo schema/scan proof, không cam kết detect mọi secret chưa biết.

Mỗi collector timeout 30 giây, cap 10 MiB; bundle cap 100 MiB. Exactly-at-cap chỉ complete khi có verified EOF + tất cả semantic mandatory fields; cap hit không có proof EOF hoặc mất field bắt buộc là TRUNCATED. Không âm thầm cắt mandatory evidence để vừa cap. Mandatory safe summaries/hash refs có thể thay raw content khi schema quy định, không dùng tùy ý để giấu missing assertions. File nguyên gốc và quyền đọc/verify thuộc gate evaluator, không public bundle.

| Outcome | Exit | Published output | Gate component eligible? |
|---|---:|---|---|
| COMPLETE | 0 | Safe bundle + manifest/collection report | Chỉ scope GATE_HANDOFF, required records/hash/access valid; chưa là HOST_READY |
| PARTIAL_OPTIONAL | 2 | Safe bundle + mandatory complete; optional errors/truncations listed | Có cùng điều kiện COMPLETE; optional không bị nâng thành blocker |
| INCOMPLETE_MANDATORY | 22 | Chỉ safe diagnostic `.incomplete` bundle/report; marked NOT_GATE | Không, dù marker về missing evidence đã có |
| BLOCKED_REDACTION | 23 | Không archive/public output chứa collected content; chỉ fixed-code local status cho operator | Không |
| FAILED_OUTPUT | 18 | Không claim publish thành công; partial temp giữ protected | Không |
| FAILED_INTEGRITY | 15 | Không gate bundle; fixed-code report/local diagnostics | Không |

Precollection schema/quyền failure dùng 10/12, không masquerade bundle outcome. Postcollection priority: redaction/scan unavailable/unsafe → 23 và cấm publish; integrity mismatch → 15; safe assembly/output I/O → 18; mandatory missing/timeout/truncated → 22; optional missing/timeout/truncated → 2; otherwise 0. Persist failure không được in collected data ra stdout để “cứu” report. Recorded per-collector reason giữ lại; interface exit chỉ normalized summary.

Mandatory missing cho FAILED_RUN scope khác mandatory missing cho GATE_HANDOFF; scope không tự đổi để return 0. Caller chọn scope explicit; gate chỉ đọc GATE_HANDOFF. Diagnostic failure không làm các optional collector an toàn khác dừng vô lý; privacy failure vẫn chặn publish toàn bộ. GATE_HANDOFF không đòi E00-17 trong chính bundle, vì gate record reference E00-16 được lập sau bundle; tránh self-hash cycle. E00-16 collection manifest liệt kê member file hashes, loại trừ chính manifest khỏi member hash; outer bundle hash được E00-17 ghi sau, không tự chứng thực.

Retention giữ evidence/checkpoints ít nhất đến khi gate/incident liên quan đóng, backup theo owner-bound retention trước thao tác; không auto purge failed runs. Manifest/trust proof không biến hash tự tính thành chữ ký. Source/workload backup và raw secrets không được đưa vào chat.

## 6. Recovery boundary và Definition of Done

Chi tiết tại PHASE00_FAILURE_RECOVERY_PLAN_V2.md. CPK-0 là metadata; **CPK-PRE-C3** là protection gate trước shared change, không thay bằng post-apply **CPK-1**. Exact checkpoint restore test là nội dung bắt buộc của AC00-05. Không overwrite/unregister existing distro, không disk repair/convert để thử recovery, không promise distro export rollback Windows/runtime.

Mục tiêu chỉ giữ sentinel/committed P00 checkpoint theo tests; không production zero-data-loss/RPO/RTO/SLA. Ghi thời gian restore, cold-start probe budget 180 giây như V1; timeout không chứng minh mất dữ liệu. Global/destructive failure injection chỉ disposable lab. Host thật chỉ approved normal paths/lifecycle và safe observations.

HOST_READY chỉ xét theo Acceptance V2: exact design/code PASS, implementation complete, qualification, mandatory package/failure tests, applicable site lifecycle/restore + terminal assertions, protected evidence + sanitized bundle, docs/recovery, no gate-blocking finding. NOT_RUN/BLOCKED/MISSING không PASS. N/A chỉ route thực sự không áp dụng với evidence và rule; package regression supported branches không N/A. Expected rejection của negative fixture có thể test PASS; actual khác expected mới tạo VALIDATION_FAILURE, root cause UNKNOWN cho tới khi có evidence.

## 7. Handoff, decision status và exit

Bàn giao target/observed profiles, PID1/systemd, resources/storage/network/config preservation, E00-12/13/14/15/16/17, recovery limitations, immutable manifest và Phase 01 blockers. Không chọn Docker/GPU/model hoặc thay FD-01…08.

D00-01…06 giữ đề xuất V1; D00-07…09 được thay bằng contract V2; D00-10…14 bổ sung RC. Tất cả **PROPOSED_NOT_APPROVED**. Author response cho DR-P00-001…006 là REVISED_PENDING_REVIEW; finding status vẫn OPEN. Package chỉ đạt author milestone REVIEW_CANDIDATE_V2, không tự đóng finding hay mở implementation. REVIEW-P00-002 quyết định độc lập.
