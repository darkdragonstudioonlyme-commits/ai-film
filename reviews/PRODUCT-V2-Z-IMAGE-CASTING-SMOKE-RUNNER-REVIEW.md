# PRODUCT V2 — Z-Image formal casting smoke runner review

VERDICT: READY FOR MERGE CANDIDATE; NO INFERENCE IN THIS COMMIT

Scope:
- fixed Z-Image 1024×1024 four-job face_front population: An/Linh × photoreal/stylized_3d
- exact revision 04cc4abb7c5069926f75c9bfde9ef43d49423021
- BF16 FULL_GPU, 50 steps, guidance 4.0, cfg_normalization=false
- canonical per-job negative_prompt applied natively

Safety boundaries:
- profile execution_authorized_by_profile=false
- plan execution_permitted_by_plan=false
- runner independently validates live A40 runtime, active USD 60 authority, current cost ledger and 512 qualification gate
- current Z-Image worker admission_ready must remain false before formal evidence
- smoke manifests carry production_acceptance=false, selection_authorized=false, publish_authority=false
- no model winner selection, no publication, no new resource creation

The execution commit must not promote Z-Image admission until all four 1024 jobs PASS and measured peak VRAM/cost evidence is ingested.
