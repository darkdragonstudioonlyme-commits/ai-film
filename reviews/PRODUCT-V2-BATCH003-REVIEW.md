# PRODUCT V2 BATCH003 REVIEW — model pins, CPU TTS, rental proposal

VERDICT: PASS FOR MERGE CANDIDATE
SCOPE: T-010, T-011, T-012.
REVIEWER: ChatGPT self-review plus executable local regression; GitHub CI still required before merge.

Findings closed:
1. Qwen-Image-2.1 upstream license is research/non-commercial without a separate commercial license. It is pinned but disabled from the commercial benchmark shortlist.
2. Pinning reduced the enabled image population from three models to two. Benchmark regression expectations were corrected rather than re-enabling Qwen for test convenience.
3. VieNeu v3 Turbo ONNX initially failed because Hugging Face snapshot symlinks caused ONNX external-data paths to resolve outside the allowed model directory. Exact snapshot bytes were materialized as regular local cache files; repo-native smoke then PASSed.
4. VieNeu is scoped to EN/VI CPU timing/previsualization. ZH remains routed to VoxCPM2 MODEL-EVAL; no unsupported-language success is claimed.
5. GPU rental numbers are a proposal only. Compute ceiling is USD 99 and hard proposed all-in cap is USD 150, with launch_authorized=false and spend_authorized=false.
6. Apache-2.0 on an upstream model does not clear dependency/dataset/publication rights. Model records now separate upstream model-license permission from the still-pending production gate.

Acceptance evidence:
- product checker PASS
- 28/28 film/product tests PASS before cursor update
- repo-native CPU TTS smoke PASS, 4/4 samples fit cue budget, mean RTF <1
- no WAV/model binary is committed
- no GPU/API rental/resource was launched
