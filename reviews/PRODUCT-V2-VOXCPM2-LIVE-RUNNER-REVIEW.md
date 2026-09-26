# PRODUCT V2 — VoxCPM2 live qualification runner review

VERDICT: READY FOR ONE-SAMPLE RUNTIME QUALIFICATION AFTER MERGE

Contract:
- exact openbmb/VoxCPM2 revision 32279effe8c19989596f05d353d1447f51d9e915
- exact voxcpm==2.0.3 package pin
- existing RunPod A40 only; no new resource creation
- active USD 60 project cap enforced before execution
- Voice Design only
- prompt_wav_path=None, reference_wav_path=None, cloning/reference audio disabled
- load_denoiser=false for the qualification path; no extra denoiser model is pulled
- optimize=false for first baseline measurement
- canonical request remains execution_permitted=false; authority is supplied separately by the active receipt

Execution boundary:
- first run is one fixed EN request only;
- runtime PASS means model loaded/generated and produced a hash-bound WAV;
- cue_fit is recorded independently and may fail without invalidating the runtime measurement;
- no quality score, speaker-identity approval, model selection, or production acceptance is implied;
- full 12-sample packet is not executed until one-sample runtime/VRAM/cost evidence is reviewed.
