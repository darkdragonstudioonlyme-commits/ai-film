# CPU TTS feasibility — slice01

VieNeu v3 Turbo 3.8.3 was tested on WSL CPU using the pinned ONNX model revision and built-in preset voices only. No real-person voice cloning was used.

The first load exposed a Hugging Face snapshot-symlink issue with ONNX external-data path validation. Materializing the exact cached snapshot symlink targets as regular files resolved the loader without altering model bytes.

Measured EN/VI samples all fit their current dialogue cue budgets. Mean real-time factor was below 1, so generation was faster than audio duration on this machine for the four smoke lines.

This is a timing/previsualization result, not final voice-quality approval. Mandarin is not routed through VieNeu in this project; VoxCPM2 remains the multilingual EN/ZH/VI model-eval candidate.
