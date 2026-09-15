# PHASE00_ACCEPTANCE_MATRIX_V2

**Work item:** INFRA-P00-002 — INFRA_DESIGN  
**Phase/gate:** 00 — Host / WSL / HOST_READY  
**Status:** REVIEW_CANDIDATE_V2; không test nào trong tài liệu này đã chạy.  
**Normative references:** Design V2 D00-01…14; Recovery V2; Evidence Register V2.  
**Input:** AC00-01…08/T00-01…14/F00-01…16 của V1; RC-01…06. IDs và acceptance intent giữ nguyên, subcases được bổ sung.

## 1. Evaluation contract

Blueprint §§21/32 yêu cầu script contract, approved design, implementation, code-review PASS, actual tests/failure cases, logs/docs/recovery. V2 không thay những điều kiện đó bằng documentary checks. D00-* và các test dưới đây là proposed design, không gán thành nguyên văn Blueprint.

Mỗi executed test record có `test_id/subcase_id`, AC/RC refs, source_kind LAB/SITE/DOCUMENT, reviewed contract/build/test-set hashes, qualified profile/fixture/payload digest, host/target alias, actor/approval, expected, actual, start/end UTC, native/normalized exit, lifecycle/epoch refs, protected/safe evidence refs và status. Expected trong specification không được copy làm actual. N/A phải có applicability rule + evidence; fixture thiếu không phải N/A.

Statuses: PASS / FAIL / BLOCKED / NOT_RUN / N/A. Negative test PASS khi reject/stop đúng contract và no-unapproved-mutation được chứng minh; không phải khi command return 0. Missing permission/environment là BLOCKED. Unexpected actual tạo VALIDATION_FAILURE với root cause UNKNOWN; không tự sửa code trong VALIDATION.

## 2. Acceptance matrix — giữ AC00-01…08

| AC | Điều kiện PASS cụ thể của V2 | Tests | Evidence bắt buộc |
|---|---|---|---|
| AC00-01 | Exact design review PASS, required changes closed by reviewer; plan/trust/permission bound; SITE active entry kiểm E00-13 trước side effect và C3 protection trước shared change | T00-01/13/14 | E00-10/12/13; review refs, design/build/plan hashes, authorization |
| AC00-02 | Đúng Windows principal/host/target/profile; WSL2/Ubuntu/non-root/home/admin readiness; preservation + affected-resource postconditions sau C3; effective final facts | T00-02/10/11/12 | E00-01…04/07/12/14; không dựa default hoặc lab host thay site |
| AC00-03 | Toàn bộ floors D00-04 giữ nguyên; capacity theo physical volume cộng allocation/retained objects, một host admission, ACL/path đúng và terminal headroom đạt | T00-03/07 | E00-05/06/11/14; before-step/final measurements và ledger allocation |
| AC00-04 | Endpoint matrix Windows/guest theo route PASS DNS/TCP/TLS/HTTPS trong final epoch; no security exception và không captive portal | T00-04/05 | E00-08/14; endpoint/context/freshness/response evidence |
| AC00-05 | Sentinel/content/perms qua target stop/start và một owner-planned host restart; pre-C3 recoverability; post-apply checkpoint thực sự restore trên approved source/destination class | T00-05/09/10/13 | E00-09/12/14/15, CPK-PRE-C3 và CPK-1, content assertions |
| AC00-06 | Sáu interface đúng semantics, no passive boot, bound apply/NOOP, host-wide fence/budget, exact outcomes, privacy và stage/scope completeness | T00-06/07/08/13/14 | E00-10/11/16; contract/journal/bundle records |
| AC00-07 | Implementation complete, CODE_REVIEW_PASS exact build; mandatory package T/F PASS; all advertised route/purpose profiles được qualify, không gate blocker | T00-01…14 + F00-01…16 | E00-13; detailed actual lab records, fixtures/isolation, findings disposition |
| AC00-08 | Docs/runbook/handoff đủ; mandatory protected evidence truy vết được; GATE_HANDOFF sanitized và complete mandatory; terminal as-of rõ, E00-17 không circular bundle | T00-01/08/09 + terminal sweep | E00-10…17 và safe refs E00-01…09; manifests/hashes/actor permissions |

**Trạng thái hiện tại:** AC00-01…08 = NOT_EVALUATED; T/F toàn bộ = NOT_RUN. V1 review = FAIL; V2 review = NOT_PERFORMED.

## 3. Test specifications

### T00-01 — Requirements, exact revision và review chain

Review độc lập Blueprint/FD-01…08 + full V2 affected contracts và diffs; kiểm source hashes, RC response, no reduction of acceptance. Chỉ reviewer đánh dấu design PASS/REVIEW_PASS finding. Sau implementation kiểm code review đúng executable/test/config content digest; không thay implementation digest bằng docs-only hash. Trước gate kiểm withdrawal/blocking finding và exact qualification. Đây là documentary check, không suy thành T00-02…14 đã test.

### T00-02 — Host/principal/profile và terminal guest facts

Site collection: Windows version/edition/x64/channel/support margin, owner/execution SID, runtime/kernel/capabilities, exact target name/path/registration, Ubuntu 24.04 amd64/WSL2, user UID !=0, home writable và admin readiness qua authorized procedure không log password. PID1/systemd được ghi, không enable ở P00. Lab fixtures cover matching/mismatching fields; site terminal repeat sau last activation theo D00-12. Missing witness → BLOCKED, wrong assertion → 19, input profile unsupported →11 hoặc qualified-row mismatch→16 tại entry stage tương ứng.

### T00-03 — Resource/capacity và boundary cases

Giữ floors: host installed RAM ≥8 GiB, host logical CPU ≥4, host available RAM ≥2 GiB, guest CPU ≥2, MemTotal ≥3 GiB/MemAvailable ≥1 GiB, guest free ≥20 GiB. Windows volume reserve 20 GiB OS/distro hoặc 5 GiB evidence/backup-only; per-volume peak gồm payload/staging/export/clone/retained evidence/swap tăng thêm. Bounded scratch ≤64 MiB; sentinel 1 MiB. Fixtures ngay dưới/đúng/trên thresholds; thiếu riêng backup volume phải 13 dù distro volume đủ. No real disk-fill/stress at site.

Shared-volume case: A và B different targets đều đủ riêng lẻ trước A; A giữ guard và budget. B trả21, không commit allocation. A terminal release, B recompute from actual free; nếu không đủ tổng reserve/retained allocations thì B trả13. Khác physical volumes vẫn serialize P00 (policy), không tự chạy song song. External writer fixture tiêu thụ available bytes: trước next native write phải reject13/reconcile; không claim lock ngăn writer ngoài package. Site final measure tính cả stopped retained clone.

### T00-04 — Endpoint/context và final network assertions

Probe matrix từ Windows và guest; DNS/TCP443/TLS hostname-chain/HTTPS bounded valid response, official redirect allowlist. Timeout 10 giây/attempt, tối đa3, backoff2/5 giây. Invalid TLS/portal/proxy context →14, không đổi DNS/firewall/VPN/CA. Site replay applicable endpoints trong terminal epoch, kể cả Windows download-source endpoint của route đã dùng; không dùng cached payload để bỏ final network requirement. Failure fixture chỉ lab; preserve separate actual/native errors.

### T00-05 — Lifecycle, staged config và terminal freshness (RC-04)
<a id="t00-05"></a>

Normal site: create sentinel/content/UID/GID/mode baseline → owner quiesce → exact target stop/start → assert content → D00-10 protection cho host restart → owner restart → boot witness đổi như expected → sentinel/content/affected-resource checks. Không auto-start service người khác; no reboot automation. Chỉ có guest stop/start không đủ host-restart requirement.

| Subcase | Setup/action | Expected oracle |
|---|---|---|
| T05-A | Standard site/lab lifecycle | Sentinel/perms preserved; new boot/activation witnessed; later terminal assertions actual PASS |
| T05-B | LAB: config được staged trước initial inventory nhưng chưa hiệu lực; T04 ban đầu PASS, host restart kích hoạt behavior không đạt | Config disk hash có thể không đổi, nhưng old T04 phải invalidated; terminal network FAIL19/underlying14; HOST_READY false |
| T05-C | LAB: transport/environment fixture làm connectivity đổi qua restart dù no config hash change | Invalidation dựa boundary/observed behavior, không chỉ diff file; phải probe lại và không false PASS |
| T05-D | LAB: planned old→new runtime/default ABSENT→new target được exact plan cho phép | Rebind sau engine; planned transition không bị đánh nhầm external drift; unexpected default khác thì16 |
| T05-E | LAB: guest/WSL restart hoặc missed continuity witness trong terminal sweep | Reject terminal report, recollect; không ghép assertions hai epochs |
| T05-F | LAB clock/metadata fixture: sweep >30 phút hoặc gate assessment >15 phút sau sweep | Terminal evidence ineligible cho fresh seal; không đổi timestamp để qua; historical report không ghi thành current |

T05-B phải có actual activation-capable lab case cho một runtime/profile được hỗ trợ, không chỉ stub. T05-C là additional controlled fixture, không substitute toàn bộ real lifecycle test. Không stage cấu hình lỗi trên site. Rerun terminal sau T09/clone operations để không dùng T05 thành terminal proof trước khi còn side effects.

### T00-06 — Passive contract và deterministic plan

Preflight C0 với stopped/custom-startup target không launch và không gán unknown thành absent; `REQUIRES_ACTIVE_PROBE` là expected discovery result. C0 output phải giữ guard/budget khi ghi; nếu root chưa hợp lệ có bounded stdout inventory, không chọn alternate guard. Dry-run cùng semantic inputs có cùng digest, timestamps là report fields; approval expiry kiểm riêng. Không download/install/dependency/guest scratch. Qualified approved C1 discovery mới thu guest facts, không tự ADOPT unknown guest.

### T00-07 — Cross-scope concurrency, interruption và NOOP (RC-01)
<a id="t00-07"></a>

Run thực ở disposable Windows/WSL lab cho lock/principal/lifecycle; unit fault injection cho crash boundaries bổ trợ. Quan sát native start/stop times, shared guard/fence, allocation table và before/after target/config. Site chỉ normal apply/NOOP + authorized diagnostics, không crash injection.

| Subcase | Interleaving | Expected |
|---|---|---|
| T07-A | Hai apply same target | Exactly one active admission, run hai exit21 trước native mutation; rerun sau completion là NOOP khi postconditions đúng |
| T07-B | C3 trước/sau C2 đang chạy; lặp C3-vs-C1 startup/stop | Cùng host guard loại trừ cả hai hướng, không runtime replacement trong native import/probe |
| T07-C | Export-vs-apply, active verify-vs-apply, C0 output-vs-large write | Same exclusive admission; no duplicate reservation; readonly in-memory C0 observation được đánh overlap, không authorize stale snapshot |
| T07-D | Different targets shared volume; different targets separate volumes | B vẫn21; sau release remeasure retained bytes, thiếu→13; không reservation “ảo” từ snapshot cũ |
| T07-E | Separate sessions và different legitimate owner SIDs, different package directories/versions | Cùng logical guard, run hai21; mỗi target thao tác đúng owner SID; caller đổi namespace/path không được chấp nhận |
| T07-F | Timeout nhưng native import còn chạy |17/UNCERTAIN, fence giữ; new apply21; không kill/force unlock rồi chạy duplicate |
| T07-G | Process crash, OS lock abandoned, native outcome unknown | New holder chỉ authorized reconcile; durable fence còn; chỉ explicit observed terminal + journal commit mới release |
| T07-H | Crash sau registration trước ownership marker; restart qua pending checkpoint | Không adopt theo tên; use intent/observed identity; unresolved→20/21 theo actor, không repeat install |
| T07-I | Cùng run gọi step con và source→destination restore | Child shares admission, không deadlock re-lock; không giữ guards hai host; checkpoint immutable link |
| T07-J | Sau mutation completion journal không ghi được | Dừng next step18, protect unresolved fence; support diagnostics dưới original authorized reconciliation, không ignore failure |

Event trace phải chứng minh **không overlap native critical sections**, không chỉ thấy exit21 ở client. Lab expected fences across host reboot được kiểm với pre-C3 protection/fixture snapshot; stale age không là lý do unlock.

### T00-08 — Requiredness, caps và privacy outcomes (RC-06)
<a id="t00-08"></a>

Bind bundle_scope explicit và Evidence Register §6 requiredness. Lab synthetic data/canaries; site chỉ actual allowlisted evidence. Case nào missing input/proof giữ actual MISSING, không sinh giả record để tạo bundle PASS.

| Subcase | Condition sau input/quyền hợp lệ | Exact expected interface outcome |
|---|---|---|
| T08-A | Mandatory + optional complete, hashes valid, scan PASS | COMPLETE/0; manifest đúng bytes; gate component chỉ eligible nếu GATE_HANDOFF |
| T08-B | Optional collector missing hoặc >30s | PARTIAL_OPTIONAL/2, mandatory complete, optional reason+duration, other safe collectors tiếp tục |
| T08-C | Mandatory missing, unavailable, timeout hoặc required protected ref inaccessible | INCOMPLETE_MANDATORY/22; safe diagnostic output NOT_GATE; chưa đủ gate |
| T08-D | Optional output cap/truncated |2, listed TRUNCATED; không drop error khỏi manifest |
| T08-E | Mandatory output cap hoặc aggregate cap gây mất mandatory field |22, không cắt rồi claim complete; exactly-at-cap chỉ0 khi verified EOF + complete semantic record |
| T08-F | Synthetic secrets ở nested error array, URL userinfo/query/encoding và path; known fields redact hoàn toàn | Không canary/raw identifier trong bundle; 0 nếu complete, alias mapping chỉ protected |
| T08-G | Residual canary, unallowlisted raw field hoặc sanitizer/scan không chạy được | BLOCKED_REDACTION/23, không published archive/content; fixed-code status không leak secret |
| T08-H | Optional failure + mandatory missing + residual secret đồng thời |23 có precedence privacy; collector reasons chỉ safe; không publish partial content |
| T08-I | Manifest/member hash sai |15, không GATE_HANDOFF accepted |
| T08-J | Output write/atomic publish thất bại sau safe collection |18; không in raw collected output để thay file |
| T08-K | INVENTORY trước CREATE: guest NOT_YET_CREATED hợp lệ | Bundle INVENTORY complete-for-scope có thể0, nhưng GATE false; GATE_HANDOFF với cùng data→22 |
| T08-L | FAILED_RUN sau entry rejection có blocker report nhưng không có apply result | Complete cho failure scope nếu evidence rules đủ; không auto đổi scope thành GATE_HANDOFF, gate false |
| T08-M | Arbitrary path/symlink/escape request |10 hoặc16 tại input/path stage; không đọc secret file rồi mới redact |
| T08-N | Gate record E17 reference E16 manifest/outer hash, E16 không tự chứa E17 | Verify no self-hash prerequisite; missing E17 chặn MASTER gate, không phá bundle creation |

Mandatory raw evidence không cần public: protected digest/access proof + schema-defined safe assertions/ref là hợp lệ. Một dòng `missing=true` không thay mandatory actual evidence trong scope cần nó. Tests scanner dùng nested/encoded cases và known-field allowlist; không claim detect mọi unknown secret.

### T00-09 — Restore, source classification và pre-boot isolation (RC-05)
<a id="t00-09"></a>

Trước export bind critical list/hash/UID/GID/mode/symlink semantics/OS/user home; quiesce/stop source đúng scope. Apply RESTORE_EXPORT/IMPORT tách verify assertions. Pre-C3 target proof dùng ISO-EXTERNAL; SAME_HOST_CLEAN chỉ là post-apply functional exception. Full checkpoint bytes, source identity và destination linked qua E00-15; hash backup đúng nhưng boot/content sai phải FAIL, không PASS chỉ vì archive có.

| Subcase | Setup/action | Expected |
|---|---|---|
| T09-A | CLEAN_P00 provenance đầy đủ, source/sentinel checkpoint, new destination name/path | Restore actual boot/OS/user/home/perms/critical files PASS; source retained, measurements/export/import/boot timing lưu |
| T09-B | Eligible ADOPT_NONSENSITIVE | Chỉ ISO-EXTERNAL; same-host request reject11; no sensitive adoption exception |
| T09-C | ISO-EXTERNAL thiếu pre-boot device/share/identity proof, envelope có uplink hoặc writable backup mapping | Reject11/12 trước import/launch; không dựa post-boot test để sửa consent |
| T09-D | SYNTHETIC_LAB startup cố egress qua Linux và Windows-interop; writes ngoài allowed surfaces | External observer không egress vượt boundary; synthetic read-only canary unchanged; allowed scratch write succeeded; no real endpoints/credentials |
| T09-E | ISO-EXTERNAL profile đổi NIC/share sau attestation trước import | Drift16, attestation invalid; không launch |
| T09-F | SAME_HOST_CLEAN yêu cầu provenance thiếu/custom startup/undeclared credential changes |11, phải use external profile nếu class vẫn eligible hoặc block; clean exception không sandbox |
| T09-G | Sensitive/unknown/nonconsented source |11/12 trước export/import; isolation không override source policy |
| T09-H | Trusted checkpoint đổi byte, import failure/no-auto-launch capability thiếu, wrong sentinel/perms sau boot |15 (integrity), 11 (missing proven capability) hoặc19 (assertion); original/previous backup không bị xóa |
| T09-I | Clone stopped/retained, no cleanup permission; retained bytes làm thiếu reserve |No unregister; block creation13 nếu dự toán đã biết, final assert13/19 nếu actual thiếu; không xóa để ép PASS |
| T09-J | verify request ngầm export/import |10/PURPOSE_NOT_ALLOWED hoặc12 nếu thiếu approval; không mutate; explicit apply restore plan mới được phép |

T09-D là lab canary test trong isolated disposable environment, không boot fixture nguy hiểm trên site. Same-host branch chỉ actual clean source, ghi NOT_ISOLATION_SANDBOX; package vẫn phải test external isolation branch. Source host final terminal sau restore-related source lifecycle; destination results không dùng thay source live assertions.

### T00-10 — Coexistence và affected-resource health (RC-02)
<a id="t00-10"></a>

Before/after registry/default/.wslconfig/selected wsl.conf/ownership checks giữ từ V1. C1/C2 target-only không stop/mutate non-target. C3 có declared affected rows và từng owner authorization; sau C3 actual health/content assertions của mỗi affected resource phải có, không chỉ config hash giữ nguyên.

Lab cases: non-target distro basic launch/state fail dù target mới PASS → C3 postcheck19, stage/gate fail; owner denies non-target launch → BLOCKED/20 awaiting verification, không auto-admin launch; empty observed/attested impact set → non-target **content** check N/A, OS/runtime checks vẫn bắt buộc. Planned host restart không bị đánh thành violation của rule target-only, nhưng launch non-target ngoài approval vẫn lỗi. Non-target sensitive health evidence do owner cung cấp safe attestation refs; unknown coverage không N/A.

### T00-11 — CREATE_NEW

Disposable Windows/WSL lab từ locked trusted payload; đúng name/location, no target before state, no guest-prerequisite vòng tròn. Guest fields NOT_YET_CREATED trước create và actual verify sau OOBE. ENGINE riêng nếu thiếu runtime, fresh inventory/plan sau engine. Collision reject16; input dangerous10; first default transition ABSENT→bound target chỉ khi approved+tested. Site chạy chỉ route đã chọn; no convert/upgrade.

### T00-12 — ADOPT_EXISTING

Eligible Ubuntu 24.04/WSL2 + owner/user/startup/source-class/permissions; không sửa system/user config để ép đạt. Incompatible/WSL1/data-sensitive/unknown/quiesce không được reject11/12 theo failure condition; preserve original. No in-place conversion. History seed UNKNOWN được ghi, new checkpoint establishes known provenance, không bịa old seed. Source restore chỉ ADOPT_NONSENSITIVE ISO-EXTERNAL; unrelated sensitive workloads được owner bảo vệ qua D00-10, không adopt chúng.

### T00-13 — ENGINE/C3 pre-protection và recovery (RC-02)
<a id="t00-13"></a>

| Subcase | Condition/action | Expected |
|---|---|---|
| T13-A | Clean-host evidence đầy đủ, qualified engine build, valid permissions | Allowed engine stages; no future guest prerequisite; reboot-required/OOBE→20 với journal, owner action |
| T13-B | Maintenance approved nhưng affected data-bearing distro thiếu checkpoint/restore proof |11/PROTECTION_INCOMPLETE trước native C3, zero engine mutation |
| T13-C | Backup/proof nằm trong chính WSL sẽ sửa hoặc recovery env chưa usable |11/RECOVERY_DEPENDS_ON_SOURCE_RUNTIME, không apply rồi mới chuẩn bị backup |
| T13-D | Source writer chạy lại sau pre-C3 checkpoint/proof |16/CONSISTENCY_BOUNDARY_DRIFT, phải fresh proof; không timestamp-only waiver |
| T13-E | C3 failure/crash tại lab với protection pack đã seal trước intent | Recovery dùng exact pre-existing material, independent env hoạt động khi source WSL unavailable; no automatic uninstall/downgrade/repair |
| T13-F | Impact set có resource unknown/không quyền kiểm health hoặc real sensitive data owner chưa cung cấp proof |11/12 trước C3; missing postcheck→20/blocked, không PASS target rồi bỏ resource khác |
| T13-G | Normal host-restart T05 với existing target, target còn sạch | Still requires pre-C3 checkpoint/proof; CLEAN_NON_TARGET exception không bỏ target AC05 |

Global destructive failure injection chỉ disposable lab có qualified isolation và management recovery; actual site chỉ normal branch. Lab snapshots/native recovery mechanisms có thể bảo vệ lab environment, nhưng không giả định source site có snapshot hoặc coi snapshot metadata thay actual restore proof. Recovery time đo, không đặt SLA mới.

### T00-14 — Trust, authorization, qualification và lab/site distinction (RC-03)
<a id="t00-14"></a>

Giữ V1 tests valid/sai payload/trust anchor/signature/hash, preview, stale plan>24h, different build/SID/target, Unicode/spaces và shell-control input. Bad schema→10; quyền/SID→12; trust/integrity→15; unexpected target/config→16. Không eval input hay chuyển negative native code thành generic0.

| Subcase | Setup single fault | Expected trước SITE active side effect |
|---|---|---|
| T14-A | CODE_REVIEW_PASS + lab receipt missing |11/QUALIFICATION_MISSING; apply/active-preflight/active-verify/recovery đều chặn |
| T14-B | Receipt FAIL/withdrawn/new gate-blocking finding/>30day expiry |11; không target mutation |
| T14-C | Receipt design/build/test-set/profile/payload exact match sai |16/QUALIFICATION_MISMATCH; không chấp nhận “gần giống” |
| T14-D | Receipt hash/trust artifact forged hoặc unsupported actor |15 hoặc12 theo first violated entry predicate; không tin self-declared PASS JSON |
| T14-E | Registered disposable LAB with approved design/code/test plan, no prior regression PASS | Lab test run allowed to create evidence; no circular prerequisite |
| T14-F | SITE đổi CLI flag thành LAB nhưng không controller registration đúng identity |12; site policy không bị bypass |
| T14-G | SITE DISCOVERY row match C0 facts, guest còn unknown | Chỉ bounded qualified discovery probes; sau đo mismatch→block CREATE/ADOPT, không auto-promote eligibility |
| T14-H | ENGINE preprofile WSL ABSENT đã qualify và expected after pinned | Branch entry không đòi absent runtime version; after install verify exact postprofile |
| T14-I | Valid approval hết hạn khi resume sau reboot | Không repeat mutation;20/AWAITING_APPROVAL hoặc12 nếu cố apply không approval; new consent bind same expected poststate |

Qualification negative suite phải có actual gate check trên mọi active entrypoint, không chỉ unit test hàm chung. Fake receipt data chỉ là lab negative fixture; không xuất như site evidence. Test set đủ 14 T IDs và 16 F IDs; supported route nào thiếu coverage thì không cấp full release receipt.

## 4. Execution dependency graph và environment coverage

Document design review PASS → implementation → code review PASS → registered LAB tests/negative fixtures → VALIDATION receipt + ledger qualification → C0 site inventory (có thể thu sớm hơn bằng reviewed passive collector) → qualified active discovery → route/protection binding → site apply/lifecycle/recovery → terminal sweep → evidence/bundle/gate assessment.

Pre-C3 protection steps được chạy dưới approved discovery/protection purpose để tạo E00-12; không cần E00-12 trước chính mọi read/export trong quy trình tạo nó. Nhưng native C3 đợi pack hoàn chỉnh. Guest chưa tạo không đòi restore; first post-create host-restart với target đã có thì có. CPK-1 post-apply khác CPK-PRE-C3. D00-12 yêu cầu final sweep sau post-apply T09; không terminal verify trước khi còn source-affecting operations.

**Package regression:** toàn bộ supported CREATE/ADOPT/ENGINE/restore purpose profiles, T/F required subcases. Fixture-only/mocked validation có nhãn; native interop/locking/restore/startup cases cần real disposable Windows/WSL. **Site:** T01/02/03/04/05/06 passive/07 normal-noop/08 actual/09 actual/10/14 actual, cộng T11 hoặc T12 và T13 nếu engine route. Host-restart protection T13-G áp dụng ngay cả site không ENGINE. Fault injection trên site OUT_OF_SCOPE; actual site reject trước gate vẫn lưu evidence.

N/A hợp lệ cho site ENGINE nếu observed runtime đã phù hợp; cho site CREATE vs ADOPT là route không chọn; cho non-target content rows chỉ khi empty impact set có evidence. Không N/A vì thiếu lab, thiếu maintenance/backup/qualification hoặc missing owner postcheck. T00-13 và mọi supported branch vẫn bắt buộc LAB.

## 5. Terminal seal và HOST_READY formula
<a id="gate-formula"></a>

`HOST_READY(as_of sealed_terminal_time)` chỉ được MASTER chấp nhận khi:

- Exact design review PASS + implementation complete + exact code review PASS; all DR gate-blocking findings resolved by reviewer.
- E00-13 valid tại SITE operation admission và assessment; mandatory package T/F PASS, tested profile relation phù hợp.
- Applicable site tests actual PASS; pre/post-C3 proof đầy đủ nếu có C3; lifecycle sentinel và exact post-apply checkpoint restore PASS.
- E00-14 terminal sweep đúng source host/target/epoch, after all source-affecting plan operations; required effective assertions PASS, timing/witnesses hợp lệ.
- E00-01…15 mandatory protected records còn access/integrity đúng; E00-16 GATE_HANDOFF outcome0/2, mandatory complete, scan PASS, docs/recovery refs đủ.
- E00-17 assessment references sealed snapshot/receipt/bundle hashes, as-of scope rõ, no unresolved blocking unknown/finding.

Không có HOST_READY trong package này. E00-17 có thể proposal=false khi tập evidence thiếu; assessment schema không tự có quyền MASTER approve. Gate historical không cam kết uptime sau seal; config/restart/new incident làm cần fresh terminal validation cho trạng thái hiện hành. Lab/destination/source hosts khác nhau là đúng role; source assertions không được trộn host/epoch tùy ý.

## 6. RC coverage và preserved intent

| RC | AC giữ nguyên được làm rõ | Added/expanded specifications |
|---|---|---|
| RC-01 | AC03/05/06/07 | T03 concurrent budget; T07-A…J; F09 |
| RC-02 | AC01/02/05/07/08 | T10 affected health; T13-A…G; F11 |
| RC-03 | AC01/06/07 | T14-A…I + active entry tests; F04/07/08 expanded trong Recovery V2 |
| RC-04 | AC02/03/04/05/08 | T05-A…F + terminal rechecks; F08/15 |
| RC-05 | AC05/06/07/08 | T09-A…J; F12/15 |
| RC-06 | AC06/08 | T08-A…N; F13 |

Không xóa 16 F cases, không đổi required→optional để đóng finding. Current result cho từng subcase vẫn NOT_RUN; design response không thay actual test evidence.
