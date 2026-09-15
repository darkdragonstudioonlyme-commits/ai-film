# Native integration boundary — dev2

This document describes implementation wiring, not a change to D00/public contracts.

## Entry and authority

`native.entry._entry` loads native ABI only after platform gating, obtains a read-only HKLM64 policy snapshot with protected owner/writer checks, reads actual principal/host observations, checks exact reviewed build/test identity and registered principal/context. The store never writes the anchor or manufactures approvals. A fresh `read_anchor` call is required before each active step; full active-loop wiring is pending.

`Policy` is a bounded JSON string at the fixed HKLM path described in `native/trust.py`. Its syntax schema is not an enrollment procedure. Role pins and raw blob digests must come from independently authenticated operator/controller material. No working SITE/LAB authority fixture is supplied. A privileged malicious administrator remains outside the protection guarantee; a global mutex cannot control unrelated administrative tools.

## Admission and durable state

The OS namespace and ProgramData directory are fixed, not derived from the caller's current path/version/SID. Metadata initialization is create-only. A rerun validates existing ACLs, root identity and journal genesis before NOOP; pending fence, torn/corrupt log, unknown existing directory or replaced root blocks. The source does not repair or truncate an existing journal.

Native supervisor ordering is suspended creation → job assignment → durable PID/start witness → resume. On uncertain resumed process/tree state it does not kill the mutation. The Coordinator can retain the native mutex until controller exit; the durable fence remains for the next controller. A job/process witness alone cannot prove completion of WSL/MSI/DISM service work. That native after-state reconciliation remains open.

## Components not standalone commands

The actuator requires a checked plan/admission/current intent, pinned payload/trust references and a caller-managed guard. It still needs the missing route driver to enforce target identity/ownership, capacity, quiesce, C3 protection, restore isolation, authority freshness and route postconditions at the correct step. Do not call it directly as a substitute for `apply`.

The snapshot reader requires an authenticated exact index and approved protected root; the publisher requires a support-bundle intent. The full producer of that index and all E00 field-level evidence are not implemented. A private record or input flag is not transformed into an actual observation merely because it parses.

## Fixed collector scripts

`host-observe.ps1` accepts only HOST, FEATURES or AUTHENTICODE requests and writes bounded output under the supervisor contract; no arbitrary expression, no execution-policy bypass, no profile. The source was not parsed or run with PowerShell here.

`guest-observe.sh` is fixed source passed through stdin to an explicit target/user command. It reads a small inventory and emits framed base64 data. It does not install tools, configure networking or systemd, or generate approvals. Syntax was checked, but it was not executed. No administrative capability is inferred merely from group membership.

## Foundation harness

`run_native_foundation_tests.py` has NF-IDENTITY, NF-JOURNAL-APPEND, NF-PATH-ROUNDTRIP, NF-HARDLINK-REJECT and NF-GUARD-CONTENDER. Native entry requires a registered disposable LAB and an external approved lab plan matching code/test identities. The runner does not issue qualification. Its scratch data is retained, not auto-deleted. Contender testing requires a separately authorized holder/controller. None of the five was executed on Windows in this authoring task.

This is not the complete T/F failure harness. In particular, no restore isolation proof, cross-user multi-process regression, global C3 race, WSL lifecycle, interrupted native service or production-network proof is supplied.
