# Current dev20 boundary status

Production native entry is `native.request_entry → native.session_driver.native_session → SessionRunner/NativeDriver/Coordinator`. Historical partial-boundary text below is retained for audit history and is superseded for current authoring status. Dev20 author coverage now proves the production request/factory composition with only OS/authority lower ports mocked. Native Windows/WSL/LAB/SITE execution remains NOT_RUN and belongs to VALIDATION.

---

# DEV14 Network transport boundary

Exact V2 authorizes a bounded DIRECT HTTPS probe while preserving existing networking/DNS/VPN/proxy/firewall policy. Dev14 makes special proxy context an explicit observed blocked environment, not a missing transport implementation:

```text
plan endpoint proxy_mode=DIRECT
→ observe controller/guest or Windows proxy context
→ configured proxy/auto-proxy/environment override => exit14 NETWORK_PROXY_CONTEXT
→ no policy mutation, bypass, CA install or alternate proxy adapter
→ only exact direct context proceeds to DNS/TCP/TLS/HTTPS measurement
→ parser rechecks proxy observation before accepting evidence
```

A future requirement to actually use an enterprise proxy/CA/VPN remediation adapter is RD00-03/new reviewed scope, not something IMPLEMENTATION may invent.

---

# DEV12 E16/E17 publication recovery boundary

Publication ownership is now durable before bytes are written:

```text
exact output bytes / no-archive decision
→ deterministic sibling staging identity
→ write-ahead intent(final + temp + byte identity/outcome)
→ create-only protected stage
→ write-through move without replace
→ final readback
```

Recovery never writes. For archive/assessment output: final-only exact bytes may complete; temp-only exact bytes are retained as output failure; final+temp is ambiguous; neither is missing. For an E16 no-archive decision, recovery requires the bound final output to remain absent. GATE E17 is recovered only when the recovered bundle is component-eligible and an exact assessment intent exists.

---

# DEV10 Cross-stage evidence provenance boundary

Historical facts now keep their historical provenance instead of inheriting the current snapshot source:

```text
exact current/history plan graph
→ hash-linked durable operation/pre-C3/checkpoint observation
→ host/actor/target/time/source checks
→ current trust/withdrawal revalidation for proof receipts
→ field-specific protected source_ref + original observed_at/source_kind
→ current snapshot seals the cross-stage reference without re-observing/relabeling history
```

E15 distinguishes the pre-C3 protection checkpoint/reference set from the later post-apply RESTORE_EXPORT checkpoint. No PASS envelope, filename, timestamp alone or intended digest is promoted into proof.

---

# DEV9 Durable wait / recovery authority boundary

Operator wait persistence is now a separate typed boundary:

```text
observed action result
→ safe wait projection (kind/reason/previous-state/result digest/minimal normalized reboot flags)
→ exact schema + 1024-byte cap
→ durable fence wait_observation
```

Raw stdout/stderr, owner payloads and arbitrary dictionaries are not accepted. Recovery relabel to `AWAITING_OWNER_VERIFICATION` re-authorizes after observation and before the journal write; the new wait context stores only a digest of the previous typed wait.

This is author source behavior only; native validation remains NOT_RUN.

---

# DEV8 Lifecycle / resume boundary update

A C3 child process is not sufficient lifecycle proof. Dev8 adds this control flow:

```text
C3 native process terminal
→ if native result already requests reboot: retain AWAITING_REBOOT
→ else read current Windows pending-reboot indicators
→ pending=true: retain AWAITING_REBOOT
→ operator reboot / renewed RECONCILIATION_ONLY authority
→ require host boot witness changed
→ require pending-reboot indicators cleared
→ require process/job/service and action postconditions
→ require affected-resource post-C3 owner evidence when applicable
→ only then TERMINAL + CLEAR original step
```

If postcondition evidence is not yet available, only an existing operator-wait fence may move to `AWAITING_OWNER_VERIFICATION`. The mutation is not replayed. OOBE owner-waits do not acquire a reboot requirement unless they originated from a reboot wait.

This is author source behavior, not proof that Windows service/reboot/OOBE behavior has passed native LAB/SITE tests.

---

# DEV7 Integration Boundary Update

Production child processes now have a separate executable-byte trust boundary in addition to project-source and payload trust:

```text
trusted native_binding.executable_policy_ref
→ NativeStore role/digest validation
→ host/build/contract-scoped executable policy
→ exact Windows path + size + SHA-256
→ administrator-owned/non-operator-writable pinned handle
→ CreateProcess suspended
→ durable witness including executable policy/hash/size
→ ResumeThread
```

This prevents a path-only or process-exit argument from becoming executable authority. The policy must be supplied by trusted authority; code never learns a digest from the binary it is about to execute.

The guest interpreter remains outside this Windows executable policy and must be covered by the remaining guest/rootfs provenance work; dev7 does not claim that boundary closed.

---

# Native integration boundary — dev5

The only native factory is `native.session_driver.native_session`. It constructs `WindowsPaths`, `NativeGuard`, `NativeJournal`, `NativeSupervisor`, `NativeSystemState`, `NativeDriver`, `Coordinator` and `SessionRunner`. CLI execution references cannot register alternative implementations.

## Request paths

`native.request_entry.execute` loads a pinned execution plan, checks its interface, then dispatches PASSIVE to `C0CaptureRunner`, RECONCILIATION_ONLY to original recovery, or other purposes to the native session. `draft` reads a committed C0 capture under metadata permission and guard; it writes an unapproved plan proposal, not an approval or host observation.

The root HKLM trust anchor, current principal, exact code/build/test identities, native bindings, profiles, per-step authority and SITE qualification remain enforced. A source package is not authority. In this delivery these native code paths were not executed; explicit synthetic test ports are only used in author tests.

## Original readers and guard

A detached read intent now records original actor/request and command digest. A pre-mutation interruption is reconciled through its exact original read set, without creating a fake mutation fence. PID/start/job queries prove writer termination; a missing witness requires an independent scoped native measurement chain, not a TTL or inventory flag. Pause/cancel revocation is a separate authenticated proof. Durable records are never deleted. Recovery must exit the controller if its native guard remains retained.

Journal capacity is reserved and measured before child reads. Native append checks actual byte growth, replay integrity and reserved quota. The fixed journal still stops safely at its configured source cap; the package has no automatic destructive rotation/repair path.

## Evidence and publication

Snapshot index/descriptor now include the exact stage context and digest. Bundle readers cannot infer existing target, C3, restore or guest-probe completion from an envelope status. Inventory projection preserves source flags; GATE_HANDOFF cannot upgrade APPLY/LAB/future evidence. Performed-action context is checked against durable source intents.

The publisher records intended exact output bytes before publishing; a failure keeps uncertainty. Reconciliation reads an already-existing final path, verifies bytes and ZIP members and never recreates or overwrites it. This does not yet implement all partial/temp-output and separate-assessment crash paths.

## Remaining limitations

Prior guest/pre-C3 cross-stage evidence and complete nested semantics are not finished. Non-DIRECT transport and full interpreter/executable trust remain open source tasks. Primary CLI is wired but full source-complete behavior is not claimed. The route controller has real native entry/journal oracles, not complete failure fixtures. Constructor/routing tests are not end-to-end native validation.

## Legacy explicit-port test engine

`engine.OperationEngine` and `engine.NativeUnavailable` are retained for historical contract-level tests. `NativeUnavailable` still refuses operations; it is not registered by primary CLI, native request entry or production factory. The dev5 entry change does not claim all legacy refusing symbols or outstanding supported-path gaps have disappeared.
