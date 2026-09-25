# Batch 008 contracts

T-026 launch gate:
- rate snapshot is hash-bound to observed provider pricing;
- authorization receipt is hash-bound to the rental proposal and rate snapshot;
- repository placeholder is explicitly NOT_AUTHORIZED;
- tests may construct synthetic authorization receipts only inside test scope;
- no resource launch implementation exists in this batch.

T-027 synthetic casting fixtures:
- deterministic tiny PPM files exercise output-manifest, provenance ingestion, blind asset binding and score completeness;
- every fixture is marked SYNTHETIC_PPM_NOT_PRODUCTION_ASSET;
- ingestion never fills accepted casting slots or promotes a production reference.

T-028 decision templates:
- image/video/voice templates define expected model populations and required metrics;
- cost rows normalize into the generic decision ledger;
- incomplete populations stay INSUFFICIENT_EVIDENCE;
- no report sets selected_winner or selection_authorized.
