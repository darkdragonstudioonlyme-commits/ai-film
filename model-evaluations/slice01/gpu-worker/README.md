# GPU worker base runtime

This is a pinned dry-run bootstrap baseline, not a claim that all selected models already run together.

The base Python package versions are snapshotted for reproducibility. CUDA/driver/torch-wheel compatibility must be probed on the actual rented GPU host before installation. Model-specific packages or source checkouts are added by the relevant backend adapter/runtime after that probe.

The setup_gpu_worker tool deliberately has no enabled apply mode. It emits the exact preflight/setup plan and lock hashes so infrastructure preparation can be reviewed without renting or mutating a GPU host.
