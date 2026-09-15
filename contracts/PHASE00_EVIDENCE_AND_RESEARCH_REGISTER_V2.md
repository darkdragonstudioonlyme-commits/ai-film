# PHASE00_EVIDENCE_AND_RESEARCH_REGISTER_V2

**Work item:** INFRA-P00-002 — INFRA_DESIGN  
**Date:** 2026-09-14 — Asia/Ho_Chi_Minh  
**Status:** REVIEW_CANDIDATE_V2; no real host/lab evidence collected.  
**Roles:** authoritative inputs / inherited documentary support / targeted source checks / proposed contracts / missing execution evidence.

## 1. Input authority và provenance

Blueprint V2 SHA-256 `adc4a1fcd77fe8e70ad8beb6e6a53e218399c22a397ab6bfeb04c589cf910a14` giữ nguyên. Design package V1, review package V1 (verdict FAIL), state V3 và RC-01…06 là nguồn revision. Actual input path/byte/hash inventory và manifests từ hai ZIP ở evidence/INPUT_IDENTITY_AUDIT.json và hai *_INPUT_MANIFEST.json. Không overwrite/extract lên source. Không coi prior chat prose là source thay bytes package.

Blueprint §§4–10,20–24,28–32,40 là workflow/state/WSL/script/DoD basis. V2 không tự chốt phase gate, model, hardware, Docker hoặc architectural contracts phase sau. D00-01…06 kế thừa proposals V1, D00-07…14 là proposed revisions cần review. Hash/input packaging checks không phải host/software validation và không phải independent design review.

## 2. Documentary evidence và limits

R-01A status giữ DOCUMENTARY_RESEARCH_COMPLETE từ V1, không host compatibility test. Profile Windows11 x64 supported margin, Ubuntu24.04 và WSL2.7.14 candidate được **kế thừa**, không chọn phiên bản mới trong INFRA-P00-002; không claim đó là latest/current best. Payload hash/trust proof thực, compatibility và installation behavior vẫn phải bind/test trước execution.

Trong revision này chỉ đối chiếu hẹp ba primary sources đã thuộc register: Microsoft WSL configuration, basic commands và networking. Đây là factual support cho RC-02/04/05, không một work item nghiên cứu lựa chọn công nghệ mới. Các nguồn khác trong bảng được ghi **INHERITED_R01A_NOT_RECHECKED_THIS_REVISION**, không tự đổi ngày kiểm chứng R-01A thành validation V2.

| Check ID | Source | Điểm được tài liệu hỗ trợ | Không được suy ra |
|---|---|---|---|
| V2-X01 | MS-CONFIG; đọc 2026-09-14 | Config global/per-distro có activation behavior; automount/interop là configuration surfaces cần xét | Site config đã có hiệu lực, clone đã isolated hoặc guest config là enforcement chống guest |
| V2-X02 | MS-COMMANDS; đọc 2026-09-14 | Có documented explicit distro operations, no-launch/install options và export/import; unregister destructive | Exact runtime/payload CLI đã được project contract-test; export có application-consistency |
| V2-X03 | MS-NETWORK; đọc 2026-09-14 | Host/guest connectivity phải xét networking context | Site VPN/proxy/routes ổn, Windows PASS đủ cho guest hoặc một networking mode phải bị sửa |

Mọi serialization/fence/protection/qualification/isolation/bundle policy ở V2 là **đề xuất thiết kế**, không tuyên bố Microsoft/Canonical yêu cầu chúng. Cửa sổ qualification30ngày, terminal30phút, gate seal15phút là project policy mới trong scope RC; các ngưỡng resource/timeouts/90-day support margin từ V1 giữ nguyên. Không có benchmark chứng minh sizing production.

## 3. Source register kế thừa

Giữ stable source IDs để đối chiếu các đoạn D00-01…06; URLs là source references, không endpoint đã được site kiểm. Không copy toàn bộ nội dung tài liệu ngoài vào package.

| ID | Nguồn / URL | Phạm vi sử dụng |
|---|---|---|
| MS-INSTALL | Microsoft — Install WSL: https://learn.microsoft.com/en-us/windows/wsl/install | Install prerequisites, runtime/distro stages, offline package direction |
| MS-COMMANDS | Microsoft — Basic commands: https://learn.microsoft.com/en-us/windows/wsl/basic-commands | Explicit distro targeting, terminate vs shutdown, export/import và cảnh báo unregister |
| MS-CONFIG | Microsoft — Advanced settings: https://learn.microsoft.com/en-us/windows/wsl/wsl-config | Shared `.wslconfig`, per-distro `wsl.conf`, resource configuration scope |
| MS-SYSTEMD | Microsoft — Use systemd: https://learn.microsoft.com/en-us/windows/wsl/systemd | Systemd capability và việc cần quan sát actual init state |
| MS-NETWORK | Microsoft — Networking: https://learn.microsoft.com/en-us/windows/wsl/networking | NAT/mirrored và khác biệt host/guest connectivity |
| MS-FILES | Microsoft — Working across filesystems: https://learn.microsoft.com/en-us/windows/wsl/filesystems | Linux workspace placement recommendation |
| MS-LIFE-HOME | Microsoft — Windows 11 Home/Pro lifecycle: https://learn.microsoft.com/en-us/lifecycle/products/windows-11-home-and-pro | Support eligibility theo release/edition |
| MS-LIFE-ENT | Microsoft — Windows 11 Enterprise/Education lifecycle: https://learn.microsoft.com/en-us/lifecycle/products/windows-11-enterprise-and-education | Support eligibility theo release/edition |
| MS-RELEASE | Microsoft WSL release 2.7.14: https://github.com/microsoft/WSL/releases/tag/2.7.14 | Version-specific official candidate, chưa được project test |
| UB-INSTALL | Canonical — Install Ubuntu on WSL2: https://ubuntu.com/wsl/docs/latest/howto/install-ubuntu-wsl2/ | Ubuntu versioned install, official `.wsl` source và WSL floor 2.4.10 |
| UB-LIFECYCLE | Canonical — Ubuntu release cycle: https://ubuntu.com/about/release-cycle | 24.04/26.04 và maintenance windows; không chọn alias latest |
| UB-RELEASE | Canonical — Noble archive: https://releases.ubuntu.com/noble/ | Nguồn discover payload/checksum metadata; chưa bind image hash hoặc trust proof |

## 4. Evidence catalog và record addressing (normative, RC-06)
<a id="evidence-catalog"></a>

Tất cả paths dưới đây là **contract của output implementation tương lai**, không phải file host đã tạo. Root protected evidence bound theo owner/ACL; mỗi run immutable sealed snapshot và manifest. `evidence_id` định nghĩa nhóm; `record_id` phân biệt context/step/stage, không ghi đè cùng ID bằng sample mới. Mỗi record fields theo Design D00-14; record hash xác định bytes, `actual` không được infer từ expected. Các scoped observation files có thể chứa arrays theo record_id nhưng index phải trỏ exact entry và hash snapshot.

| ID | Protected record path logical | Safe representation bắt buộc theo scope | Semantics |
|---|---|---|---|
| E00-01 | observations/host.json | summaries/host.json | Host alias, OS/profile eligibility, owner/execution match; raw SID/path chỉ protected |
| E00-02 | observations/runtime.json | summaries/runtime.json | Features/virtualization/WSL/kernel/version/capabilities/pending reboot |
| E00-03 | observations/distros.json | summaries/distros.json | Own-principal target/default/list aliases; cross-owner coverage ref khi C3 |
| E00-04 | observations/guest.json | summaries/guest.json | Guest OS/user/home/init/startup-class assertions hoặc stage status NOT_YET_CREATED/REQUIRES_ACTIVE_PROBE |
| E00-05 | observations/resources.json | summaries/resources.json | Host/guest CPU/RAM, timestamps/context |
| E00-06 | observations/storage.json | summaries/storage.json | Volume aliases/free/budgets/path-validation/ACL outcomes, no raw private paths |
| E00-07 | observations/config.json | summaries/config.json | Relevant config hashes/allowlisted values/default transitions, source/disk vs observed behavior |
| E00-08 | observations/network.json | summaries/network.json | Context/endpoint aliases/DNS/TCP/TLS/HTTPS/response outcomes; sanitized URLs/errors |
| E00-09 | recovery/source_manifest.json | summaries/source_manifest.json | Class/critical-list identity/quiesce/checkpoint scope/retention; no user file contents |
| E00-10 | governance/execution_binding.json | summaries/execution_binding.json | Design/code/contract/build/plan/trust refs, approved stage/purpose, class/actor/approval |
| E00-11 | execution/admission_journal.json + protected durable fence | summaries/admission.json | Admission/fence/budget/event refs; unresolved vs terminal, no arbitrary command lines |
| E00-12 | recovery/c3_protection.json | summaries/c3_protection.json | Impact rows/owners alias, CPK-PRE-C3 and pre/post actual assertions, empty-impact reasons |
| E00-13 | qualification/release_receipt.json + linked test records | summaries/qualification.json | Qualified digests/profile/purposes/issued-expiry/withdrawal/actual T/F aggregate with detail refs |
| E00-14 | verification/terminal.json + assertions | summaries/terminal.json | Source epoch/witnesses/start-end/as-of/actual final conditions/invalidation |
| E00-15 | recovery/restore_session.json + controller proofs | summaries/restore.json | Source class/checkpoint hash, destination/session/envelope preboot, actual restore/observer results |
| E00-16 | support/collection_report.json + member_manifest.json | support/collection_report.json + member_manifest.json | Scope/completeness/outcome/scan/collector list; own manifest/outer hash rules below |
| E00-17 | governance/gate_assessment.json | Separate gate_assessment.safe.json, **ngoài support bundle** | Proposal/accepted status by ledger, as-of, E14/E16 digests và unresolved blocker summary |

Protected refs format logical: `run_id/relative_path#record_id`; index lưu relative path, JSON pointer/record_id khi cần, media_type, bytes, SHA-256, sensitivity, source role và availability/access-verification. Safe index thay run/path bằng opaque artifact alias nếu chứa thông tin người dùng; alias map giữ local. Gate evaluator đọc/hash/access-check protected refs qua owner-approved environment; public summary không tự chứng thực actual.

Record source_kind DOCUMENT chỉ cho reviewer/contract/receipt metadata, không thay SOURCE_SITE actual measurements. Lab fixture expected/results phải tách actual; lab test source host và site host khác nhau hợp lệ theo qualified-profile relation. Không fake values cho host IDs, machine boot ID, signer/hash, capacity hoặc benchmark. Source restore/destination liên kết qua checkpoint hash, không reuse destination identity như source.

## 5. Stage requiredness (normative)
<a id="stage-requiredness"></a>

Ký hiệu: **R** = required actual record/subset cho stage; **C** = conditional với exact applicability rule; **S** = record status bắt buộc nhưng future actual được NOT_YET_CREATED/REQUIRES_ACTIVE_PROBE; **—** = chưa được required cho stage (không fake PASS). R không có nghĩa mọi trường guest phải tồn tại trước CREATE. `MISSING` ở một record R → stage BLOCKED/incomplete; chỉ S cho phép absence được định nghĩa.

| Evidence | Passive C0 inventory | SITE active DISCOVERY entry | Distro apply entry CREATE/ADOPT | C3 native entry | Terminal/GATE_HANDOFF |
|---|---|---|---|---|---|
| E01 host/principal | R | R | R | R | R |
| E02 runtime/feature | R, ABSENT hợp lệ khi engine chưa có | R cho bounded probe capability | R supported runtime | R before-profile và expected after | R actual final |
| E03 distro/default | R own context, cross-owner scope status | R exact named source authority | R target uniqueness/ownership | R complete impacted coverage | R actual preserved/expected-after |
| E04 guest | S | S trước first probe, R sau probe nếu guest có | S CREATE; R ADOPT eligibility | C existing target stopped baseline; S khi chưa có target | R final actual |
| E05 resources | R host subset; S guest | R host+declared probe budget | R host, S guest CREATE/R ADOPT | R host+operation budget, C guest existing prior observations | R actual host+guest |
| E06 storage | R relevant output/volume observations | R budget/path/ACL | R physical capacity/ownership/trust bound | R all impacted checkpoint/recovery allocation | R actual incl retained clones |
| E07 config | R host config/status; S guest | R host; S guest until authorized read | R protected relevant state; S future guest CREATE | R pre config/default; no boot source after quiesce merely to collect | R final config + effective assertion refs |
| E08 network | S | C if probe/network purpose | C required download context; offline payload may record not-needed-for-step, not waive AC04 later | C operation-required connectivity; offline payload bound | R full route endpoint matrix actual final |
| E09 source/critical manifest | S planned source class | R owner startup/source authority for existing launch | R source authority/class/consistency plan; S future checkpoint CREATE | R for data-bearing resources, C no-data disposition proofs | R actual source/checkpoint scope |
| E10 execution binding | R request/collector identity; review/approval may S for planning only | R design/code/trust/plan/approval/purpose | R | R | R |
| E11 admission/journal | C if persistent output | R before active step and event results after | R | R | R closed or accounted; no unresolved writer |
| E12 C3 protection | — | —; discovery may collect to prepare it | C if operation actually includes C3 (prefer separate engine plan) | R all impact rows, no blank waiver | R pre/post any C3 incl planned host restart |
| E13 qualification | — (C0 trusted collector still required for real use) | R SITE; LAB follows class rule | R SITE; LAB registration/test plan instead | R SITE; LAB class proof | R package actual qualification |
| E14 terminal | — | — | — | — | R after all source-affecting plan steps |
| E15 restore session/envelope | — | C when discovery purpose enters restore env | C for RESTORE_IMPORT, R before first boot | R ISO-EXTERNAL independent recovery proof cho existing target/data rows; C empty no-target row | R actual post-apply restore plus pre-C3 refs |
| E16 bundle | — | — | — | — | R GATE_HANDOFF, mandatory complete |
| E17 gate assessment | — | — | — | — | R **after** bundle, not prerequisite for generating E16 |

LAB rows use authenticated registration/fixture/isolation/approval before controlled operations; no qualification receipt prerequisite của chính tests đang tạo nó. Test fixtures cố tình thiếu precondition chỉ authorize negative test expected rejection, không authorize unsafe actual mutation. C0 `COMPLETE_FOR_STAGE` không đủ mở SITE active action. Discovery-stage gate không cần future checkpoint nhưng cần known ownership/data authority/startup permission; không bypass D00-02 eligibility để ADOPT.

## 6. Bundle requiredness và exact outcome mapping (normative)
<a id="bundle-requiredness"></a>

Caller chọn scope explicit; không tự đổi scope sau failure. Mọi bundle có safe root index, declared scope, member manifest, collector report, sanitizer/schema/scan version+result, contract/build/run/source aliases, record availabilities và fixed-code errors. Payloads chỉ allowlisted schemas, không arbitrary nested stderr.

| Scope | Mandatory semantic content | Conditional | Optional diagnostics |
|---|---|---|---|
| INVENTORY | Common skeleton; safe E01/02/03 host-context, E05 host subset/E06 output-volume/E07 host subset, E10 request/collector; E04/08/09 status entries đúng stage | E11 nếu operation đã ghi persistent output; relevant guest facts nếu authorized probe thực sự diễn ra | Extra bounded timing/hardware labels đã allowlist, không dùng cho thresholds/gate |
| FAILED_RUN | Common skeleton + failing interface/stage/reason/actual normalized-native outcome, available relevant E10 and E11 intent nếu đã có mutation, before/after/uncertainty status; known missing required-next-stage được liệt kê | E12 nếu C3 attempted/blocked và pack hiện có; safe E15 nếu restore attempted; E01…09 subsets needed to explain actual failure | Additional safe diagnostics không quyết định assertion |
| GATE_HANDOFF | Common skeleton + required final safe E01…15 (conditional subfields theo stage matrix), exact passed assertion summaries/detail refs, valid qualification/review/docs/recovery refs và E16 | Non-target health N/A chỉ observed empty-impact rows; SITE unused route records N/A có evidence; protected raw excluded by design | Non-load-bearing collector timings/optional labels only |

Đối với FAILED_RUN, unavailable initial identity do **chính prerequisite đang fail** có thể ghi typed `UNKNOWN/UNAVAILABLE` kèm safe failure reason; không đòi impossible successful future measurements để tạo diagnostic bundle. Nếu **collector được phép phải đọc một existing required journal mà timeout/missing** thì vẫn22, không dùng typed unknown để che mất evidence. GATE_HANDOFF đòi actual required assertions; một marker `NOT_RUN` không hoàn thành nội dung dù JSON hợp schema.

Conditional record luôn có applicability decision + reason/evidence hash. Optional diagnostics phải được định danh trước run; không đổi required field thành optional sau khi collector lỗi. Protected raw data không được include public chỉ để “đủ” mandatory. Safe schema/hash/ref là phép thay đã định nghĩa trong §4; actual records vẫn phải local access/hash-check được.

| Condition | outcome / exit | inventory_complete | bundle_mandatory_complete | bundle_component_eligible |
|---|---|---|---|---|
| Required semantic content đủ, optional đủ, trusted hashes + scan PASS | COMPLETE /0 | Theo stage thật | true | true chỉ GATE_HANDOFF + protected access/refs valid |
| Chỉ optional missing/timeout/truncated | PARTIAL_OPTIONAL /2 | Theo stage thật | true | Như trên; optional failure không block gate |
| Required missing/unavailable/timeout/truncated/cap prevents full semantic record | INCOMPLETE_MANDATORY /22 | false nếu ảnh hưởng inventory stage | false | false |
| Unredacted nested/URL/path canary hoặc sanitize/scan chưa chứng minh | BLOCKED_REDACTION /23 | Không thay observations trước đó | false/not_publishable | false |
| Manifest/record bytes/trust sai | FAILED_INTEGRITY /15 | Không suy lại từ corrupt record | false | false |
| Output I/O/publish thất bại | FAILED_OUTPUT /18 | Inventory có thể đã có nhưng output incomplete | false | false |

Collection report actual `inventory_complete` và `bundle_mandatory_complete` là booleans kèm scope/stage/reasons; not-publishable report giữ safe local codes, không raw output. E00-16 completeness chỉ own component, không actual phase gate. Policy precedence/30s/10MiB/100MiB và EOF rules là D00-14; T08/F13 exact cases bao gồm mandatory cap và privacy cùng mandatory failure.

E00-16 member manifest không hash chính nó; outer archive hash do subsequent gate assessment ghi. E00-17 không nằm trong bundle nó tham chiếu. Gate assessment references E14 sealed snapshot and E16 digests; immutable evidence index/file hashes tránh circular content digest. One final archive có manifest không là authenticity signature của reviewer/owner.

## 7. Missing evidence và decision dependencies

**E00-01…17 đều MISSING dưới vai trò execution/site tương ứng.** V2 documents mô tả catalog, không chứa generated site records ở những paths logical trên. Input-document integrity audit chỉ DOCUMENT, không lấp E00-01…17.

| Group | Missing execution material | Blocked action |
|---|---|---|
| E01…08 | Windows/SID/WSL/guest/resources/config/network observations và epochs | Host eligibility, site bindings và acceptance |
| E09/12 | Owner classification/critical scope, full C3 impact coverage, quiesce/backup/proof/independent recovery access và owner postchecks | Source launch/mutation theo class, C3 và later phase gate |
| E10/11 | V2 reviewer PASS, implementation/build/code review/real operation plans/guard namespace mapping and journal | Implementation entry trước review; later target apply |
| E13 | Registered disposable lab, actor approval, actual T/F results/qualified matrix/receipt | SITE active operations, không design review |
| E14 | Actual final live assertions/witnesses/seal after planned boundaries | HOST_READY |
| E15 | Pre-first-boot controller proof, source class, exact checkpoint and actual destination restore | Restore/import/launch và C3 khi recovery phụ thuộc proof |
| E16/17 | Actual scoped sanitized evidence bundle và downstream assessment | Gate acceptance; not satisfied by this design ZIP |

Không coi exact machine IDs/path/hash/user rights chưa có hôm nay là design freedom. Behavior khi thiếu đã được quy định; thực tế có đáp ứng được không cần implementation/lab/site evidence, reviewer vẫn được quyền FAIL nếu contract thiếu nhất quán/khả thi.

## 8. Research backlog và residual limitations

RD00-01 image/runtime payload hash/signature/trust metadata: future binding before apply, không điền sample. RD00-02 host outside supported profile hoặc cần change global configuration: RESEARCH/INFRA_DESIGN extension riêng. RD00-03 enterprise VPN/proxy/CA/firewall remediation ngoài P00 plan: change scope/review riêng. R-01B Linux/systemd/Docker; R02…R06 GPU/models/quality/rights/workload unchanged NOT_STARTED.

Không thêm nhà cung cấp lab/hypervisor hay model. ISO-EXTERNAL là execution profile với enforceable assertions; chưa có environment đáp ứng được xác minh. Nếu tool/host không thể chứng minh no-auto-launch, cross-SID guard, envelope hoặc recovery path, execution BLOCKED và design gap quay về design nếu contract không implementable. Không tăng permission/sửa security tự động để vừa profile.

Guard chỉ cooperative package, không malicious-admin security boundary; source class/provenance/owner authority vẫn thiết yếu. Documentation supports platform behavior, không đảm bảo correctness của parsers/CLI/ACL/native process lifecycle/signature verification/capacity estimates. Những điều đó còn code review và actual lab/site testing. Six DR-P00 findings giữ OPEN, responses REVISED_PENDING_REVIEW, không self-approve.
