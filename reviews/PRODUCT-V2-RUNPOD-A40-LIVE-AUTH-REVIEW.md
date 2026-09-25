# PRODUCT V2 — RunPod A40 live authorization review

VERDICT: READY FOR T-019 STAGE-A RUNTIME QUALIFICATION

Evidence:
- existing owner-created RunPod Pod 0h1twwxqw6yx0k is RUNNING in EU-SE-1
- NVIDIA A40, 46068 MiB measured VRAM, driver 580.159.03
- Python 3.12.3, Torch 2.8.0+cu128, torch CUDA 12.8, CUDA available
- cgroup limits: 7.65 CPU cores, 49,999,998,976 bytes RAM
- 250 GB root/container disk; /workspace is not a separate mount
- public repo cloned at exact main fc2cb236...
- project owner explicitly authorized a maximum total project spend of USD 60
- RunPod live Pod rate observed through MCP: USD 0.49/h
- provider accrued billing total is not exposed by the MCP; bootstrap runtime is recorded as an evidence-based estimate

Safety:
- historical NOT_AUTHORIZED placeholder remains unchanged for fail-closed tests
- active receipt is separate and binds original proposal, actual A40 execution plan, live rate snapshot and USD 60 cap
- no new resource creation is authorized
- model-specific resource profiles remain UNMEASURED/admission_ready=false until real measurements
- DAG readiness may expose casting/voice as READY, but generic execution_permitted remains false and per-model admission still gates work

Review finding closed:
- live A40 worker exposed a real admission bug: unmeasured canonical profiles use vram_reserve_gb=null, but evaluate_admission attempted float(None) before returning fail-closed reasons. The admission code now treats a null reserve as 0 only for evaluation arithmetic while still rejecting the profile for PROFILE_NOT_ADMISSION_READY / VRAM_REQUIREMENT_UNMEASURED / VRAM_REQUIREMENT_MISSING.

Verification:
- active A40 launch gate PASS at exactly USD 60
- USD 60.01 request correctly rejected
- historical NOT_AUTHORIZED placeholder still rejected
- live host evidence / worker / rate / execution-plan / receipt bindings PASS
- product checker PASS
- 185/185 film/product tests PASS
- no model-specific profile marked admission-ready and no model inference executed by this authorization commit
