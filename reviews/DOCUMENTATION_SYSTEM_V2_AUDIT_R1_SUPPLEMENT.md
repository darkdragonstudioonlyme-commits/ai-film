# Documentation System V2 — Audit R1 Supplemental Finding

```yaml
AUDIT_ID: DOC-V2-AUDIT-R1-SUPPLEMENT
RELATED_TARGET: 4753de63e24977ee2229ad6c3985231ebab1dc3e
AUDIT_BRANCH: lane/docs-audit-v2
FINDING: D2A-F04
SEVERITY: HIGH
```

## D2A-F04 — governance Python resolved from an unrelated project environment

During remediation, `command -v python3` resolved to `/home/dragon/arb/.venv/bin/python3`, while the observed system interpreter is `/usr/bin/python3` and source tests intentionally use `/home/dragon/ai-film-dev/.venv/bin/python`.

V2 already states that ambient tools from unrelated environments are not project authority, but its governance scripts used `#!/usr/bin/env python3` and documented `python3 ...` commands. This allowed the control plane itself to violate its tool-provenance rule.

**Required fix:** bind governance/control-plane scripts and documented governance commands to `/usr/bin/python3`; continue using the project `.venv/bin/python` only inside the low-level source-test executor. Managed `test.sh` must call the canonical wrapper with the explicit governance interpreter. Final audit must verify these boundaries.
