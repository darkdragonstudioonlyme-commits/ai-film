# Traceability V2 — implementation contributions, not acceptance PASS

Eight ACs remain NOT_EVALUATED. All 14 T, 16 F and 56 expanded entries (86 total) remain NOT_RUN. Workspace tests exercise components with fakes/synthetic data/POSIX I/O; native-source links do not prove full test-case coverage.

The JSON companion contains exact actual test IDs, source links and expanded-case→parent links. An expanded row only inherits a component reference, not an executable full native case.

| Requirement | Source contributions | Actual workspace tests linked | Native / acceptance |
|---|---|---:|---|
| T00-01 | `src/aifilm_p00/authority.py`, `src/aifilm_p00/content.py`, `src/aifilm_p00/native/entry.py`, `src/aifilm_p00/native/trust.py`, `src/aifilm_p00/plans.py` | 42 | NOT_RUN / NOT_EVALUATED |
| T00-02 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/codec.py`, `src/aifilm_p00/content.py`, `src/aifilm_p00/native/entry.py`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/security.py`, `src/aifilm_p00/native/trust.py`, `src/aifilm_p00/policy.py` | 24 | NOT_RUN / NOT_EVALUATED |
| T00-03 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/admission.py`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/security.py`, `src/aifilm_p00/policy.py` | 33 | NOT_RUN / NOT_EVALUATED |
| T00-04 | `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/network_probe.py`, `src/aifilm_p00/policy.py` | 14 | NOT_RUN / NOT_EVALUATED |
| T00-05 | `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/resume.py` | 22 | NOT_RUN / NOT_EVALUATED |
| T00-06 | `src/aifilm_p00/__main__.py`, `src/aifilm_p00/codec.py`, `src/aifilm_p00/content.py`, `src/aifilm_p00/native/coordination.py`, `src/aifilm_p00/native/entry.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/native/trust.py`, `src/aifilm_p00/plans.py`, `src/aifilm_p00/resume.py` | 62 | NOT_RUN / NOT_EVALUATED |
| T00-07 | `src/aifilm_p00/admission.py`, `src/aifilm_p00/engine.py`, `src/aifilm_p00/journal_files.py`, `src/aifilm_p00/native/coordination.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/resume.py` | 61 | NOT_RUN / NOT_EVALUATED |
| T00-08 | `src/aifilm_p00/evidence.py`, `src/aifilm_p00/native/snapshot.py` | 54 | NOT_RUN / NOT_EVALUATED |
| T00-09 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/native/security.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/resume.py`, `src/aifilm_p00/windows_commands.py` | 29 | NOT_RUN / NOT_EVALUATED |
| T00-10 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/native/security.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/resume.py` | 24 | NOT_RUN / NOT_EVALUATED |
| T00-11 | `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/plans.py`, `src/aifilm_p00/resume.py`, `src/aifilm_p00/windows_commands.py` | 15 | NOT_RUN / NOT_EVALUATED |
| T00-12 | `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/plans.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/resume.py` | 13 | NOT_RUN / NOT_EVALUATED |
| T00-13 | `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/coordination.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/resume.py`, `src/aifilm_p00/windows_commands.py` | 49 | NOT_RUN / NOT_EVALUATED |
| T00-14 | `src/aifilm_p00/authority.py`, `src/aifilm_p00/codec.py`, `src/aifilm_p00/content.py`, `src/aifilm_p00/engine.py`, `src/aifilm_p00/native/entry.py`, `src/aifilm_p00/native/trust.py` | 32 | NOT_RUN / NOT_EVALUATED |
| F00-01 | `src/aifilm_p00/codec.py`, `src/aifilm_p00/content.py`, `src/aifilm_p00/native/entry.py`, `src/aifilm_p00/native/trust.py`, `src/aifilm_p00/policy.py` | 15 | NOT_RUN / NOT_EVALUATED |
| F00-02 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/authority.py`, `src/aifilm_p00/codec.py`, `src/aifilm_p00/engine.py`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/security.py` | 32 | NOT_RUN / NOT_EVALUATED |
| F00-03 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/__main__.py`, `src/aifilm_p00/codec.py`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/security.py`, `src/aifilm_p00/plans.py` | 22 | NOT_RUN / NOT_EVALUATED |
| F00-04 | `src/aifilm_p00/codec.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/network_probe.py`, `src/aifilm_p00/policy.py` | 19 | NOT_RUN / NOT_EVALUATED |
| F00-05 | `src/aifilm_p00/admission.py`, `src/aifilm_p00/content.py`, `src/aifilm_p00/native/entry.py`, `src/aifilm_p00/native/trust.py`, `src/aifilm_p00/policy.py` | 33 | NOT_RUN / NOT_EVALUATED |
| F00-06 | `src/aifilm_p00/content.py`, `src/aifilm_p00/native/entry.py`, `src/aifilm_p00/native/trust.py`, `src/aifilm_p00/policy.py` | 10 | NOT_RUN / NOT_EVALUATED |
| F00-07 | `src/aifilm_p00/authority.py`, `src/aifilm_p00/codec.py`, `src/aifilm_p00/engine.py`, `src/aifilm_p00/native/coordination.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/resume.py` | 63 | NOT_RUN / NOT_EVALUATED |
| F00-08 | `src/aifilm_p00/native/coordination.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/resume.py` | 49 | NOT_RUN / NOT_EVALUATED |
| F00-09 | `src/aifilm_p00/admission.py`, `src/aifilm_p00/engine.py`, `src/aifilm_p00/journal_files.py`, `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/coordination.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/resume.py` | 61 | NOT_RUN / NOT_EVALUATED |
| F00-10 | `src/aifilm_p00/admission.py`, `src/aifilm_p00/engine.py`, `src/aifilm_p00/journal_files.py`, `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/resume.py` | 34 | NOT_RUN / NOT_EVALUATED |
| F00-11 | `src/aifilm_p00/native/actuator.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/resume.py`, `src/aifilm_p00/windows_commands.py` | 22 | NOT_RUN / NOT_EVALUATED |
| F00-12 | `src/aifilm_p00/native/snapshot.py`, `src/aifilm_p00/policy.py`, `src/aifilm_p00/windows_commands.py` | 36 | NOT_RUN / NOT_EVALUATED |
| F00-13 | `src/aifilm_p00/evidence.py`, `src/aifilm_p00/native/snapshot.py` | 54 | NOT_RUN / NOT_EVALUATED |
| F00-14 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/__main__.py`, `src/aifilm_p00/codec.py`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/security.py`, `src/aifilm_p00/plans.py` | 22 | NOT_RUN / NOT_EVALUATED |
| F00-15 | `native/guest-observe.sh`, `native/host-observe.ps1`, `src/aifilm_p00/native/filesystem.py`, `src/aifilm_p00/native/inventory.py`, `src/aifilm_p00/native/probes.py`, `src/aifilm_p00/native/security.py`, `src/aifilm_p00/policy.py` | 11 | NOT_RUN / NOT_EVALUATED |
| F00-16 | `src/aifilm_p00/admission.py`, `src/aifilm_p00/engine.py`, `src/aifilm_p00/journal_files.py`, `src/aifilm_p00/native/coordination.py`, `src/aifilm_p00/native/process.py`, `src/aifilm_p00/resume.py` | 61 | NOT_RUN / NOT_EVALUATED |

Five NF-* foundation paths are documented in `NATIVE_INTEGRATION_BOUNDARY.md`. They do not close a parent T/F case. Exact remaining integration is in `REMAINING_IMPLEMENTATION.md`.
