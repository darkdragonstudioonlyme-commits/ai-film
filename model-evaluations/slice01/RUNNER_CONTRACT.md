# External Benchmark Runner Contract

The backend-neutral harness invokes an external runner as:

  runner-command job.json output_dir

Contract:
- read job.json and do not mutate it;
- write one or more generated artifacts under output_dir;
- exit 0 only when the requested generation completed;
- write diagnostics to stdout/stderr;
- never publish or spend outside its own already-authorized model runtime;
- the harness records wall time, exit status, optional nvidia-smi peak memory, and SHA-256/size for every artifact.

Dry-run creates planned job manifests without invoking a runner. Actual execution requires both --execute and --runner, reducing accidental paid execution risk.
