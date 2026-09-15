# PHASE00_FAILURE_RECOVERY_PLAN_V2

**Work item:** INFRA-P00-002 — INFRA_DESIGN  
**Status:** REVIEW_CANDIDATE_V2, NOT_IMPLEMENTED, NOT_VALIDATED  
**Inputs:** Recovery V1/F00-01…16; RC-01…06; Design V2 D00-07…14.  
**Scope:** Phase 00 only. Những failure dưới đây là scenarios/specifications, không phải sự cố đã xảy ra trên máy người dùng.

## 1. Safety và applicability

Giữ dữ liệu/resource hiện có; không unregister/overwrite/format/repair/convert/in-place upgrade để thử recovery. Không tự gán source sạch, usable, disposable hoặc current runtime version. C1/C2/C3 cần proper actor/plan/guard; C3 thêm protection, SITE active thêm qualification. Negative destructive fixtures chỉ registered disposable LAB; site chỉ approved normal lifecycle và assertions. Failure test đúng expected rejection là test PASS, không phải phase PASS.

P00 restore chỉ CLEAN_P00/ADOPT_NONSENSITIVE_QUIESCED/SYNTHETIC_LAB như D00-13. Sensitive/unknown target source không được phép; owner-controlled non-target protection attestations ở C3 không authorize P00 import hoặc launch sensitive data. Full Windows DR, vendor recovery changes và source-host policy repair không tự phát sinh từ runbook này.

## 2. Failure test matrix — giữ F00-01…16

Các subcase exact expected ở Acceptance V2 được reference, không thay bằng prose mơ hồ. Native exit lưu riêng. Mỗi single-fault case có code cụ thể; multi-fault tuân entry order D00-11 và bundle precedence D00-14.

| ID | Scenario / safe test location | Expected behavior và evidence | Recovery/retest |
|---|---|---|---|
| F00-01 | Virtualization/prerequisite bị policy chặn; mock inventory/disposable Windows |11, nêu stage/prerequisite; no BIOS/boot policy change | Owner xử lý riêng/design extension; fresh inventory T02/11/13 |
| F00-02 | Wrong SID/alternate account, missing elevation/approval, SITE giả LAB |12 trước target action; lab flag không thay controller-attested identity | Correct actor/approval/rebind; T14-E/F; không log passwords |
| F00-03 | Existing name/path khác ownership, junction/symlink escape, shell-control input |10 input hoặc16 collision/path drift; no mutation/secret file read | Chọn target mới hoặc owner evidence; không delete; T06/10/14 |
| F00-04 | Unsupported Windows margin/WSL preview/guest profile; eligible profile nhưng không qualified matrix row |11 unsupported prerequisite;16 exact qualification profile mismatch, không tự fallback | Research/design extension hoặc lab qualification phù hợp; giữ source; T02/12/14 |
| F00-05 | Below resource floor; backup volume thiếu; other run để retained allocation khiến run sau thiếu |13 trước write; run concurrent chưa được admit trả21 trước capacity claim; no disk-fill test ở site | Re-budget từ actual free dưới guard; owner storage action riêng; T03/07-D |
| F00-06 | DNS/TCP/TLS/portal/proxy mismatch; network PASS trước reboot nhưng FAIL sau |14 underlying probe, final verify assertion19; old evidence invalid; no security weakening | Re-diagnose hoặc design môi trường; after fix terminal rerun T04/05 |
| F00-07 | Payload/receipt byte hash hoặc trust anchor sai, self-declared PASS, unknown native integrity |15/trust, no install/import. Trusted nhưng actual receipt FAIL/missing →11 theo T14-A/B, không coi code-review thay lab | Fresh trusted refs; qualifier/reviewer xử lý, no receipt fabrication; T14 |
| F00-08 | Stale plan>24h, external config/runtime/default/target drift; stale receipt>30d; activation thay behavior không đổi hash |16 material plan/profile drift;11 receipt expired; effective evidence invalidation cần terminal recollect, không mượn old PASS | Replan/approval hoặc requalify; T05-B…F/T14; planned explicit transition không bị đánh nhầm |
| F00-09 | Cross-scope C3/C2/C1/export/verify/C0-output, cross-SID và native action timeout/crash |21 cho competing admission;17/UNCERTAIN cho native timeout, durable fence giữ. OS-lock abandonment không là authorization mới | R1 + R6; observed native termination/completion trước release; T07-A…J |
| F00-10 | Native install/network timeout, reboot required, OOBE pending |17 hoặc20 theo actual; expected post-state chưa đủ thì no APPLIED/full success; approval expired không bypass resume | Reconcile/checkpoint/owner action; T11/13/14-I |
| F00-11 | C3 thiếu pre-protection; intentional lab runtime crash với source WSL unavailable; non-target health fail |Missing/inaccessible protection→11 trước mutation; malformed archive→15; actual postcheck fail→19. Failure recovery dùng material sealed **trước** C3, không backup sau lỗi rồi gọi “pre” | R3; independent env restore proof, owner-controlled health; T10/13-B…G |
| F00-12 | Corrupt/truncated checkpoint, boot/content fail, missing pre-boot isolation, source class prohibited |15 checkpoint integrity,19 boot/content assertions,11 source/envelope unsupported/missing,12 thiếu data/controller permission; không launch khi envelope chưa đủ | R2 + restore procedure; original protected; T09-B…J |
| F00-13 | Optional/mandatory missing/timeout/cap; nested error/URL/path canaries; bundle I/O/integrity |Optional→2; mandatory→22; unproven redaction→23/no archive; integrity→15; output failure→18. Scope rules và precedence exact như D00-14/T08 | R5; recollect under same declared scope; tests T08-A…N; no arbitrary raw upload |
| F00-14 | C0 preflight/dry-run gặp stopped guest/custom startup/unknown guest facts |No launch. Record REQUIRES_ACTIVE_PROBE; inventory partial/not-ready không trở thành full acceptance | Qualified authorized C1 DISCOVERY hoặc stop; T06/14-G |
| F00-15 | Non-target distro/custom global config/VPN; planned restart effects; restore envelope drift/same-host dirty clone |C1/C2 preserve; C3 impact gate. Unapproved drift→16; dirty/unknown same-host source→11; missing owner postcheck→20/blocked | R4/R7; T05/09/10; không thêm source-host firewall/network exception |
| F00-16 | Journal/evidence I/O fail, unrecognized native code, cleanup ownership not proven |18/internal hoặc16 ownership; no next mutation/no wildcard delete. Journal failure giữ unresolved fence, sanitized diagnostic only | Restore evidence access theo owner authority; reconcile before resume; T07-J/08-J/14 |

Không tạo F00-17 để né bộ 16 mandatory IDs cũ; các RC thêm subcases dưới existing IDs. Khi actual có nhiều lý do, record từng reason thay vì chọn một code và giấu condition khác.

## 3. Checkpoints và protection order
<a id="checkpoints"></a>

| Checkpoint | Thời điểm/phạm vi | Không được nhầm với |
|---|---|---|
| CPK-0 | Inventory/identity/version/config/default/ownership/critical list, plan/quyền/budgets trước mutation | Không phải backup |
| CPK-PRE-C3 | Protection pack E00-12: every impact row classified, owner quiesce/no-write boundary, immutable recovery material + successful independent restore proof, approved postchecks; sealed trước C3 intent | Không thay bằng metadata, maintenance consent, hoặc CPK-1 tương lai |
| CPK-1 | Post-apply source target consistent checkpoint, source manifest và T09 functional restore proof cho state được bàn giao | Không tự chứng minh Windows/runtime rollback |
| CPK-TERMINAL | E00-14 final live behavior/sentinel/resources/config after last source-affecting plan operations, sealed as-of | Không production uptime/SLA, không full Windows snapshot |

**Existing source quiesce:** owner xác định writers/apps/sessions; stop writers, commit/sync dữ liệu trong scope, stop explicit target có approval. Không assume export tự làm application-consistent. Không launch source lại để thu “fresh guest facts” giữa checkpoint và C3; preconditions dùng stopped-state witnesses + previously collected immutable facts, identity/config/OS observations không cần boot. Nếu writer/guest khởi động lại sau checkpoint và có thể thay covered state, invalidate consistency boundary và tạo checkpoint/proof mới.

Export/proof path outside target/runtime; Windows user data/external mounted volumes/shared WSL/OS không tự nằm trong distro export. Missing coverage resource trở thành missing protection, không được lén bỏ vào exclusions mà vẫn nói protected. Backup-of-record được bảo vệ ngoài lab writable surfaces; offline working copy có hash bind; recovery access/independent environment phải sẵn có trước C3. Backup cùng physical disk có giới hạn logical recovery, không disk-loss protection; ghi rõ trong handoff. Retention/permissions do owner bind; không gửi raw archive lên chat.

Đối với non-target managed/sensitive workloads, P00 chỉ nhận owner-controlled protected proof refs/attestations theo D00-10. Permission không đủ, proof không thể kiểm hoặc coverage UNKNOWN → chặn C3. Không tạo/mở backup có secrets bằng một generic recovery script. Windows writers bị host reboot tác động có owner saved/closed/recoverable confirmation; đây không phải full Windows DR claim.

Independent restore pre-C3 có thể cần operator giữ source stopped lâu hơn; không estimate thời gian hoặc bỏ proof để tiện. Host chưa có target dùng CLEAN_HOST_ABSENT row; sau CREATE khi target đã có, planned restart vẫn cần target CPK-PRE-C3. Pre-C3 proof và post-apply T09 phục vụ hai state khác nhau; không circular prerequisite. SAME_HOST_CLEAN chỉ có thể đáp ứng post-apply functional T09; pre-C3 target proof phải trên ISO-EXTERNAL đã sẵn có để không phụ thuộc source runtime đang thay.

## 4. Recovery runbooks

### R1 — Target apply gián đoạn / UNCERTAIN

Ngừng admit mutation khác, giữ durable fence. Native process identity/start witness và observed target registration/path được đối chiếu dưới host guard bởi owner phù hợp. Timeout/process disappearance không tự chứng minh action không chạy; check actual terminal postcondition và outstanding service action. Khi vẫn unknown, giữ UNCERTAIN/20 cho operator và21 cho competing operation. Không force unlock theo tuổi lock, không tạo target lần hai.

Nếu action đã xong đúng expected state, ghi result/reservations rồi resume từ next authorized step; approval/design/build còn valid. Nếu registration có nhưng chưa marker, identity phải nối durable intent + native result + canonical path, không infer ownership từ tên. Lỗi payload cache chỉ sửa project cache theo exact trusted bytes; không lấy latest. Không xóa directory/registration dư mặc định.

Safe diagnostics khi fence unresolved: original owner/controller được acquire guard trong **RECONCILIATION_ONLY** để đọc và ghi diagnostics vào budget/output đã duyệt của run cũ; không clear fence hoặc execute queued mutations. Support bundle trên evidence snapshot có thể tạo trong môi trường công cụ khác được data owner cho phép; không dùng điều này để chạy target action từ host khác.

### R2 — Existing target không boot / checkpoint restore

Không unregister, overwrite VHD, fsck/repair hay tự đổi source config. Kiểm E00-09/12/15 và source class trước mọi export/import. Restore eligible checkpoint trong ISO-EXTERNAL hoặc clean exception đủ điều kiện; sensitive/unknown nguồn đi owner recovery/INCIDENT_ANALYSIS riêng, không mở rộng ADOPT.

Nếu không có usable checkpoint hoặc môi trường/proof, giữ BLOCKED; sự thiếu đó không cấp quyền cài mới trên source. Bản clone hỏng giữ lại investigation theo retention; previous backup/original không bị xóa. Selected critical assertions phải định nghĩa trước export, không đổi danh sách sau khi thấy lỗi. Restore actual boot/content/perms PASS mới tạo proof. Hash đúng nhưng boot sai là fail.

### R3 — C3 runtime/feature/host restart lỗi

CPK-PRE-C3 đã có trước intent phải đọc được khi source WSL unavailable. Ghi Windows/runtime/native state và từng affected resource. P00 không auto disable feature/uninstall/downgrade; không hứa runtime rollback bằng export. Owner dùng independent recovery path đã bind để khôi phục **copy ở destination mới**, hoặc route host/native recovery sang work item có scope/approval riêng. Source data được preserve.

Nếu C3 native thành công nhưng resource-owner health check fail, stage vẫn failed19; target mới boot được không override resource fail. Missing postcheck approval/evidence → AWAITING_OWNER_VERIFICATION20, no HOST_READY. Clean-host N/A chỉ non-target content checks với empty coverage evidence, không bỏ runtime/boot checks.

Trong disposable lab, controller snapshot restore có thể reset lab ngoài package theo test plan đã duyệt; snapshot mechanism không là claim site có tương đương. Lab thử source-runtime unavailable phải chứng minh recovery material/independent env đã sẵn có, không tạo chúng sau lỗi. Quiesce/protection failure thì không thực hiện C3 để “xem có sao không”.

### R4 — Network/resource failure

Giữ nguyên DNS/VPN/proxy/firewall/memory/volume policy. Authorized diagnostic có bounded retry; false PASS do pre-restart evidence được ngăn bằng terminal revalidation. External writer ăn disk không được giải bằng xóa backup/distro; dừng next write/reconcile ongoing native action. Owner chọn resource remediation/design riêng; sau change rebind plan và rerun affected site assertions. Environment failure không mặc định code bug.

### R5 — Bundle incomplete / privacy risk

Tách collector status khỏi interface/gate status. Mandatory thiếu/timeout/truncated→22; optional-only→2; scan/redaction unavailable/residual secret→23, không published archive. Keep raw necessary evidence protected; error/status output chỉ fixed-code/allowlisted metadata. Không in secret vào error khi giải thích việc redaction fail. Không auto đổi GATE_HANDOFF thành FAILED_RUN để “thành công”. Diagnostic scope có thể tạo riêng với tên/scope rõ, không thay handoff proof.

Collector code sửa chỉ ở implementation/patch sau routing/review; trong validation chỉ record expected/actual. Data owner không bị yêu cầu upload `.env`, backup tar, credentials hay full home. Không giữ raw unnecessary capture chỉ để tiện debug. Final bundle hashes và protected refs phải verify được; unavailable gate refs giữ gate false.

### R6 — Admission/fence và capacity reconciliation

All P00 side-effect operations cùng host guard dù khác SID/target/path/version. Người reconcile giữ guard, kiểm old/new boot identity, native/process witnesses, path ownership và all retained/pending allocations; không giải phóng reservation theo wall-clock. Chỉ known terminal hoặc safe cancellation đã chứng minh no pending writer mới commit fence release. Nếu new actor không có quyền resource cũ, chỉ có thể báo21/12 và route owner; không hijack guard để nhận distro.

After release, run sau đo free space lại, không dùng approval capacity cũ hoặc semantic plan làm số đo thật. Planned reboot giữ pending fence qua restart; operator resume không thực thi queued install trước khi reconcile. Coordination root corrupt/ACL unknown chặn side effect; không tạo root “V2 mới” để bypass fence V1/cooperating other build. P00 guard không kiểm soát external admin/WSL tools; maintenance scope và drift checks là giới hạn rõ.

### R7 — Restore envelope / terminal freshness failure

Pre-boot envelope thiếu, policy/device changed hoặc source class không phù hợp → stop **trước import có thể launch**. Không boot clone để thử xem isolation có đủ không. Môi trường ready ở management plane, native no-auto-launch capability qualified trước action. V2 không sửa source host global networking để tạo sandbox.

Post-boot fixture cho thấy egress/write không đúng allowlist → lab failure, isolate/quarantine evidence theo controller plan; không tạo site qualification. Source remains unchanged. Terminal report stale/mixed epoch → recollect final sweep sau completion/quiesce approved operations; không sửa timestamps hoặc đưa config về đẹp bằng code trong verify. Historical PASS vẫn historical, không đổi thành current HOST_READY.

## 5. Restore drill — explicit actor/action chain
<a id="restore-chain"></a>

| Step | Actor/class/authority | Preconditions và evidence |
|---|---|---|
| RD-1 | Source owner C1 quiesce, package apply RESTORE_EXPORT (C1/C0 protected-output) | Qualified SITE purpose hoặc registered LAB; host guard/budget, source class/critical manifest, no-write boundary; checkpoint bytes/hash refs |
| RD-2 | Lab controller/physical owner, ngoài restored guest | ISO-EXTERNAL session ready, no uplinks/production writable shares/credential forwarding; media working copy verify; E00-15 pre-boot proof. SAME_HOST_CLEAN có provenance/consent exception, không gọi isolated |
| RD-3 | Package apply RESTORE_IMPORT C2 | New exact path/name/owner, destination guard/capacity, no implicit launch tested; source checkpoint trusted/hash exact; no conflicting fence |
| RD-4 | Package verify C1 | No import/repair; launch exact clone, OS/user/home/sentinel/perms/critical assertions; lab negative observer/canary only approved fixtures |
| RD-5 | Owner/package verify C1 stop clone | Stop/retain; no unregister. Record timing, final allocations; source metadata/state preserved, backup-of-record unchanged |
| RD-6 | Source terminal verification after source-affecting steps | D00-12 epoch/witnesses + T02/03/04/10/sentinel; E00-14; handoff bundle/assessment as-of |

Không giữ host guards hai máy cùng lúc. Source export seal trước transfer/import; dữ liệu source thay sau checkpoint không sửa identity checkpoint cũ nhưng làm nó không phải proof cho state mới. Cleanup default không xóa clone; mọi disposal ngoài default cần exact ownership/approval và không phá protected checkpoint. Clone retained được budget trước tạo, không trông chờ sau test tự xóa để đủ disk.

## 6. RPO/RTO, coverage limits và failure routing

Giữ mục tiêu V1: sentinel/checkpoint state đã commit trong test; không zero data loss cho ứng dụng, power loss hay physical disk. Cold-start diagnostic budget180giây, timings thực báo rõ, chưa production SLA. No hardware stress/low-disk fill/crash simulation trên target host. Imported distro rollback không là Windows recovery.

VALIDATION actual khác expected → VALIDATION_FAILURE(TEST/EXPECTED/ACTUAL/ENVIRONMENT/REPRODUCTION/LOG_EVIDENCE/AFFECTED_AREA/ROOT_CAUSE=UNKNOWN/STATUS=OPEN), collect/analyze trước PATCH/IMPLEMENTATION. Thiếu contract trong implementation → DESIGN_GAP và về design, không tự fix architecture. INCIDENT_ANALYSIS cho existing incident khi scope cần; quality taxonomy không dùng thay lỗi hạ tầng.

Tài liệu này không chạy restore, không đã chứng minh host có backups và không tự đóng DR-P00. Tất cả actual/result hiện NOT_RUN; six reviewer findings OPEN/response pending re-review.
