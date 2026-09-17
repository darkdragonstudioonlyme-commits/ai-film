# Phase00 V02 validation tooling source

This directory preserves the exact source for host-side V02 validation tooling. Runtime copies live under `/home/dragon/ai-film-dev/validation-ops/`; a runtime copy is trusted only when its SHA-256 matches the independently reviewed source recorded by the validation lane.

The tooling is candidate-scoped to exact dev21 and may contain safe pseudonymous digests/host scope required for admission. It contains no passwords, private signing keys, raw MachineGuid or raw external-authority secrets.

`external-authority-trust-anchor.json` is intentionally committed as `PENDING_EXTERNAL_KEY`. Do not replace it with an operator-generated key. An ACTIVE update requires independently established external public-key provenance and review, and the verifier's pinned config hash must change in the same reviewed transaction.

Tests under `validation/tooling/tests/` use only synthetic keys and staging directories. They grant no LAB authority.
