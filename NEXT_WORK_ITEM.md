# NEXT WORK ITEM — Product v2 batch 003

STATUS: READY
MILESTONE: M2

BATCH:
1. T-010 — pin exact candidate checkpoint/version, upstream license source and runner requirements; keep execution_ready=false until all execution gates pass.
2. T-011 — run CPU dialogue/TTS feasibility for slice01 timing, starting without voice cloning; preserve EN/ZH/VI line identity.
3. T-012 — prepare a rental-GPU configuration/provider/budget proposal from the fixed benchmark; do not rent or spend.

CURRENT_BLOCK:
- no discrete NVIDIA GPU
- visual/video model execution is intentionally gated until exact model/license/runtime identity is pinned
- any paid GPU/API execution needs a bounded budget

SUCCESS:
- exact model candidates have source/license/checkpoint/runtime requirements recorded without overclaiming production approval
- CPU TTS path yields reproducible sample evidence or an explicit technical blocker
- rental proposal names benchmark tier, estimated duration and a hard spend cap without launching resources

DO_NOT:
- resume P00 dev23/prodlike loops
- enable legacy P00 timers
- publish content
- clone a real person's voice without explicit rights
- launch paid GPU/API work without a bounded budget
