# NEXT WORK ITEM — T-019 VoxCPM2 formal packet + blind image scoring

STATUS: READY
MILESTONE: M2

IMAGE BLIND MATERIALIZATION COMPLETE:
- 8/8 neutral-name PNG copies exist under /workspace/artifacts/blind-comparison
- every copy matches canonical asset_bytes + asset_sha256
- public neutral manifest contains no model identity
- scores.csv remains blank; selection_authorized=false

VOXCPM2 QUALIFICATION COMPLETE:
- exact model revision: 32279effe8c19989596f05d353d1447f51d9e915
- package: voxcpm==2.0.3
- exact snapshot: 7 required files / 4.620033 GiB
- one EN request PASS_RUNTIME
- peak VRAM: 5,827 MiB
- inference: 3.452767s
- audio: 3.04s at 48 kHz, cue-fit PASS against 3.5s
- estimated qualification cost: USD 0.004291
- no reference audio, no cloning, no production acceptance
- canonical execution ledger: USD 0.170799 / USD 60

NEXT:
1. Execute the remaining 11 fixed VoxCPM2 requests with the same model revision/package/seed/descriptions.
2. Do not rerun the already-qualified EN request unless a concrete runtime premise changes.
3. Aggregate 12 output manifests, cue-fit, peak VRAM, elapsed and measured execution cost.
4. Keep voice quality/identity status NOT_EVALUATED until the 12-sample packet is complete.
5. Keep image model mapping blinded until all 8 image score rows are complete.

DO NOT:
- modify voice descriptions/seeds between languages
- enable reference_audio or cloning
- select an image-model winner before complete blind scores
- treat smoke/qualification assets as production casting/audio
- create another Pod/resource
- exceed USD 60
- publish content
