# Phase00 local-operator LAB authority change — dev22

CHANGE_ID: P00-LOCAL-OPERATOR-LAB-AUTHORITY-001
BASE_SOURCE_COMMIT: 934659f535d81d9a4a07389531acc2b9c304fa6d
TARGET_CANDIDATE: IMPL-P00-001-DEV22
OWNER_DECISION: LOCAL_ONLY_WSL_EXECUTION
CONTRACT_DIGEST_CHANGED: false
NATIVE_VALIDATION_STATUS: NOT_RUN

## Requirement

The owner explicitly selects a lower-assurance local authority model so Phase00 LAB validation can be prepared and authorized entirely within the same WSL/Windows trust domain. `controller_external=false` is therefore a valid LAB controller mode. It must never be represented as independent/external authority.

External-controller LABs remain valid with `controller_external=true`. In both modes, registration and fixture containment remain mandatory: `disposable=true`, `no_real_credentials=true`, and `no_production_mappings=true`. Fixture authority mode must match the registration mode for the same LAB execution.

The local model changes authorship/provenance assurance only. It does not relax exact source/build/test/contract binding, approved plan/suite coverage, <=24h authority windows, host/operator scope, role pins, content-addressed object integrity, native evidence requirements, qualification semantics, SITE requirements, or HOST_READY assessment.

A local cryptographic signing key may be used as an integrity/tamper boundary inside WSL after reviewed activation, but its signature proves only possession of the local key and must not be described as independent external approval.
