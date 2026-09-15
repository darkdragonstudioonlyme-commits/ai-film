# REQUIREMENT → SOURCE → TEST TRACEABILITY V1

**No official T/F or AC is marked PASS by this mapping.** Workspace tests are actual source tests, but they cover selected predicates/ports only. Exact test IDs and code paths are in TRACEABILITY.json.

| Requirement | Source modules | Linked workspace tests | Native/acceptance | Limitation |
|---|---|---:|---|---|
| T00-01 | plans.py, authority.py | 33 | NOT_RUN / NOT_EVALUATED | Exact source/design byte identity exists; code review remains NOT_PERFORMED. |
| T00-02 | policy.py, codec.py | 6 | NOT_RUN / NOT_EVALUATED | Native Windows/guest/principal collectors absent; only selected profile predicates tested. |
| T00-03 | policy.py, admission.py | 24 | NOT_RUN / NOT_EVALUATED | No actual host capacity measurement or Windows physical-volume mapping. |
| T00-04 | policy.py | 1 | NOT_RUN / NOT_EVALUATED | Network aggregation negative only; DNS/TCP/TLS/HTTPS native collectors NOT_IMPLEMENTED. |
| T00-05 | policy.py | 9 | NOT_RUN / NOT_EVALUATED | No actual sentinel/lifecycle/host restart; epoch/time predicates only. |
| T00-06 | codec.py, plans.py, __main__.py | 13 | NOT_RUN / NOT_EVALUATED | Workspace metadata and deterministic plan only; native passive collector absent. |
| T00-07 | admission.py, journal_files.py, engine.py | 21 | NOT_RUN / NOT_EVALUATED | Memory concurrency and POSIX durability; no Windows global/cross-SID proof. |
| T00-08 | evidence.py | 25 | NOT_RUN / NOT_EVALUATED | In-memory snapshots/synthetic data; native safe reader/publisher/field catalogs incomplete. |
| T00-09 | policy.py, windows_commands.py | 7 | NOT_RUN / NOT_EVALUATED | Envelope predicates and argv only; actual export/import/boot/content/observer not implemented. |
| T00-10 | policy.py | 2 | NOT_RUN / NOT_EVALUATED | Owner-health aggregation predicates only; no actual affected-resource checks. |
| T00-11 | plans.py, windows_commands.py | 2 | NOT_RUN / NOT_EVALUATED | New-target planning and argv only; native create/OOBE/workspace absent. |
| T00-12 | policy.py, plans.py | 0 | NOT_RUN / NOT_EVALUATED | Guest eligibility predicate source exists; actual ADOPT source and native harness pending. |
| T00-13 | policy.py, windows_commands.py | 9 | NOT_RUN / NOT_EVALUATED | Protection predicates/feature argv only; no ENGINE/C3 execution or recovery drill. |
| T00-14 | authority.py, codec.py, engine.py | 23 | NOT_RUN / NOT_EVALUATED | Synthetic trusted models only; native trust/normalization/renewal/registration adapters pending. |
| F00-01 | policy.py, codec.py | 6 | NOT_RUN / NOT_EVALUATED | Native Windows/guest/principal collectors absent; only selected profile predicates tested. |
| F00-02 | authority.py, codec.py, engine.py | 23 | NOT_RUN / NOT_EVALUATED | Synthetic trusted models only; native trust/normalization/renewal/registration adapters pending. |
| F00-03 | codec.py, plans.py, __main__.py | 13 | NOT_RUN / NOT_EVALUATED | Workspace metadata and deterministic plan only; native passive collector absent. |
| F00-04 | policy.py, codec.py | 6 | NOT_RUN / NOT_EVALUATED | Native Windows/guest/principal collectors absent; only selected profile predicates tested. |
| F00-05 | policy.py, admission.py | 24 | NOT_RUN / NOT_EVALUATED | No actual host capacity measurement or Windows physical-volume mapping. |
| F00-06 | policy.py | 1 | NOT_RUN / NOT_EVALUATED | Network aggregation negative only; DNS/TCP/TLS/HTTPS native collectors NOT_IMPLEMENTED. |
| F00-07 | authority.py, codec.py, engine.py | 23 | NOT_RUN / NOT_EVALUATED | Synthetic trusted models only; native trust/normalization/renewal/registration adapters pending. |
| F00-08 | policy.py | 9 | NOT_RUN / NOT_EVALUATED | No actual sentinel/lifecycle/host restart; epoch/time predicates only. |
| F00-09 | admission.py, journal_files.py, engine.py | 21 | NOT_RUN / NOT_EVALUATED | Memory concurrency and POSIX durability; no Windows global/cross-SID proof. |
| F00-10 | admission.py, journal_files.py, engine.py | 21 | NOT_RUN / NOT_EVALUATED | Memory concurrency and POSIX durability; no Windows global/cross-SID proof. |
| F00-11 | policy.py, windows_commands.py | 9 | NOT_RUN / NOT_EVALUATED | Protection predicates/feature argv only; no ENGINE/C3 execution or recovery drill. |
| F00-12 | policy.py, windows_commands.py | 7 | NOT_RUN / NOT_EVALUATED | Envelope predicates and argv only; actual export/import/boot/content/observer not implemented. |
| F00-13 | evidence.py | 25 | NOT_RUN / NOT_EVALUATED | In-memory snapshots/synthetic data; native safe reader/publisher/field catalogs incomplete. |
| F00-14 | codec.py, plans.py, __main__.py | 13 | NOT_RUN / NOT_EVALUATED | Workspace metadata and deterministic plan only; native passive collector absent. |
| F00-15 | policy.py | 2 | NOT_RUN / NOT_EVALUATED | Owner-health aggregation predicates only; no actual affected-resource checks. |
| F00-16 | admission.py, journal_files.py, engine.py | 21 | NOT_RUN / NOT_EVALUATED | Memory concurrency and POSIX durability; no Windows global/cross-SID proof. |

## AC00 giữ nguyên

| AC | Related test specs | Current result |
|---|---|---|
| AC00-01 | T01/13/14 | Design-review subcondition available; full execution binding missing. |
| AC00-02 | T02/10/11/12 | NOT_EVALUATED; native facts absent. |
| AC00-03 | T03/07 | NOT_EVALUATED; core thresholds tested only. |
| AC00-04 | T04/05 | NOT_EVALUATED; live endpoint collectors absent. |
| AC00-05 | T05/09/10/13 | NOT_EVALUATED; no actual lifecycle or restore. |
| AC00-06 | T06/07/08/13/14 | NOT_EVALUATED; six native interfaces not complete. |
| AC00-07 | All T/F | NOT_EVALUATED; code review absent, native test harness/results absent. |
| AC00-08 | T01/08/09 + terminal | NOT_EVALUATED; native evidence/handoff incomplete. |

Native inventory preserves 14 T IDs + 16 F IDs + 56 expanded subcases = 86 entries. None is N/A merely because the implementation or lab is missing.
