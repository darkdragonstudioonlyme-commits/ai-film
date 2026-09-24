# Slice01 model evaluation harness

Purpose: prepare a reproducible benchmark before any GPU rental or hardware purchase.

Safety state:
- all model entries start with execution_ready=false;
- license_hint is not production approval;
- exact checkpoint/version, code/weights/dataset rights, runner environment and bounded spend must be reviewed before flipping execution_ready;
- dry-run is the default behavior;
- actual runner invocation requires --execute, --runner and --max-jobs.

Useful commands:

  PYTHONPATH=. python3 tools/run_model_benchmark.py --profile smoke --run-id local-smoke

  PYTHONPATH=. python3 tools/run_model_benchmark.py --profile keyframe_core --run-id keyframe-plan

Video profiles expose reference_image as a blocker until keyframe references exist. Provide a reference index with --reference-index using reference_index.example.json as the shape.

A GPU runner receives job.json and output_dir. See RUNNER_CONTRACT.md. After execution the harness emits timing, optional nvidia-smi peak memory, artifact SHA-256 hashes, a public blind-review list, a private model map and a score CSV.

Do not commit generated benchmark outputs under benchmarks/. Preserve selected run receipts separately once real MODEL-EVAL begins.
