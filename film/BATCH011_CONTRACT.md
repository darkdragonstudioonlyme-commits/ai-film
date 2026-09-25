# Batch 011 — render compiler, technical QC, delivery manifest

T-035:
- render compiler consumes a READY edit plan plus a storage asset catalog;
- creative selection remains asset-id/manifest based; storage paths stay outside selection state;
- edit plan digest and catalog hashes/manifests are checked before command compilation;
- output is argv/filter specification only and execution_permitted=false;
- blocked edit plans cannot yield render commands.

T-036:
- technical QC consumes structured ffprobe data;
- checks duration tolerance, exact dimensions/aspect, frame rate, audio presence and sample rate;
- optional media binding computes immutable file SHA-256/byte size;
- no visual-quality PASS is inferred from technical metadata.

T-037:
- delivery package expects six variants: 9:16/16:9 × EN/ZH/VI;
- every variant binds media hash+manifest, subtitle hash and technical QC identity;
- a package can be complete while publication is blocked;
- even AUTHORIZED_TO_PUBLISH produces PACKAGE_AUTHORIZED_NOT_PUBLISHED; no publish action is performed.
