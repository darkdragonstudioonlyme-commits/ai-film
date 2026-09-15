# NEXT_WORK_ITEM — tiếp tục cùng implementation task

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV1
TARGET_GATE: CODE_REVIEW_PASS
ENTRY_GATE: DESIGN_REVIEW_PASS
ENTRY_GATE_STATUS: SATISFIED_EXACT_V2
GOAL: "Hoàn thiện các native adapters và interfaces còn thiếu theo REM-01…08, không thay approved design."
INPUTS:
  - AI_FILM_PROJECT_STATE_V6
  - Exact_approved_V2_contracts
  - IMPL-P00-001_IMPLEMENTATION_PACKAGE_V1
  - docs/REMAINING_IMPLEMENTATION.md
  - evidence/WORKSPACE_TEST_REPORT.json
SCOPE:
  - "Native identity/trust/guard/fence trước actuator integration."
  - "Provisioning/resume/restore/live assertions/evidence pipeline."
  - "Executable native harness, full traceability và workspace regression."
FORBIDDEN:
  - "Thay FD/D00/public contracts hoặc hạ acceptance."
  - "Cài/chạy native Windows/WSL trên host hoặc lab trong authoring task."
  - "Biến synthetic fixtures thành approvals/qualification/observations."
  - "Tự CODE_REVIEW_PASS hoặc HOST_READY."
DESIGN_GAP_RULE: "Nếu implementation yêu cầu đổi reviewed behavior, tạo DESIGN_GAP rồi chuyển design cho affected scope."
EXIT_CONDITION: "Full author-complete candidate; REM-01…08 giải quyết hoặc blocker được quản lý đúng, không hidden stub."
NEXT_MODE_AFTER_EXIT: CODE_REVIEW
NEXT_REVIEW_WORK_ITEM: CODE-REVIEW-P00-001
MODE_TRANSITION_NOW: NONE
```
