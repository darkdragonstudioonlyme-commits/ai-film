# Batch 016 — source ingestion, reusable scaffold and portable spec package

T-050 source/adaptation ingestion:
- source text is always inert data; it cannot grant tool, execution or publication authority;
- embedded instruction/tool/secret-looking text may be flagged for review but is never executed;
- ORIGINAL_PROJECT, LICENSED_ADAPTATION and PUBLIC_DOMAIN each require compatible commercial-use rights state;
- rights/source evidence is bound by SHA-256 at ingestion.

T-051 project scaffold:
- creates only empty draft spec/state files needed to begin a new film project;
- does not copy runtime/, compiled/, delivery/, artifacts, run-evidence, secrets, credentials or generated media;
- generated media is EMPTY, runtime is NOT_INITIALIZED and publication remains NOT_EVALUATED.

T-052 portable production-spec package:
- deterministic manifest of 15 curated story/continuity/casting/shot/timing/localization/framing/lipsync/audio/QC/publication-policy inputs;
- every entry is relative, SHA-256/size bound and self-verifiable;
- generated/binary media, runtime receipts, secrets and unsafe paths are rejected;
- package grants neither execution nor publication authority.
