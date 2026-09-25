# Visual GPU prelaunch bundle

This bundle is a deterministic staging contract for the enabled image/video candidates. It does not rent a GPU, install anything, download weights, or execute inference.

Each model row binds:
- exact upstream repo + revision;
- license/production gate;
- stage and runner profile;
- required references;
- exact planned Hugging Face download command;
- backend runner input/output identity requirements.

The generated bundle keeps execution_ready=false and provider_resource_created=false. T-019 remains the only task that may later own a paid provider launch after bounded approval.
