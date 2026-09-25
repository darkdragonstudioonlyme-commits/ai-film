# Batch 009 — asset graph, QC and publication rights

T-029/F03:
- immutable spec/generated asset identities;
- explicit dependency edges;
- selective descendant invalidation;
- deletion is dry-run and blocks approved/evidence/selected/referenced assets;
- invalidation never authorizes regeneration by itself.

T-030/F06:
- QC records bind exact asset + manifest identity;
- scores are 1–5 and failure taxonomy is closed;
- severe failure tags block acceptance even when scalar scores are high;
- experiment records require a fixed population, same metric set and explicit regression list;
- promotion is not authorized when regressions exist.

T-031/F07:
- rights subjects are project policy data, not hard-coded character names;
- source/voice/likeness/model-output/music rights can block publication independently;
- revoked/non-publishable assets block;
- creative/technical QC and provenance are required;
- a clean gate only becomes READY_FOR_OWNER_APPROVAL unless explicit owner approval is supplied;
- the code never performs publication.
