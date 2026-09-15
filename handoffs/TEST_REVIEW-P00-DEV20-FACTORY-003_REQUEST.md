# TEST_REVIEW request — dev20 factory integration coverage

```yaml
HANDOFF_ID: HANDOFF-TEST-REVIEW-P00-DEV20-FACTORY-003
PRODUCER_WORKFLOW: WF-P00-IMPL-CR001-RESIDUAL-AUDIT
CONSUMER_WORKFLOW: TEST_REVIEW
SOURCE_COMMIT: 51c9d3f7373a2922c1ea6a3e973d817bb4e16523
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V20.zip
PACKAGE_SIZE_BYTES: 1175249
PACKAGE_SHA256: 8104985b355815d58fbc28fec3e1b9b17c72dbf9d5a9c6dc8f7eb66f77a67fff
PACKAGE_MEMBER_VERIFY: PASS
PACKAGE_GIT_BYTE_IDENTITY_VERIFY: PASS
TEST_CHANGE: TEST_CHANGE-P00-DEV20-FACTORY-003
TEST_FILE: tests/test_dev20_factory_integration.py
ORACLE_CHANGED: false
AUTHOR_TESTS: "760 PASS / 0 failure / 0 error / 0 skip"
STATIC_CHECKS: "101 PASS / 0 failed"
SOURCE_DIGEST: 1aa44211cd215b9c9691209d132a723c3b666fb5fee279b68c7f077da632d9dc
TEST_DIGEST: c645f3d9f88fcb716f78fcff9cd9b4144b320dc4f0c8c7082346a5cfbe6d9383
SOURCE_VISIBILITY_BRANCH: snapshot/dev20-source
SOURCE_VISIBILITY_SNAPSHOT: 0c7c32ff2f84442531f7df0c371229acdffc5d5d
NATIVE_WINDOWS_WSL: NOT_RUN
LAB: NOT_RUN
SITE: NOT_RUN
REQUESTED_VERDICT_ARTIFACT: test-governance/TEST_REVIEW-P00-DEV20-FACTORY-003.md
STATUS: READY_FOR_INDEPENDENT_TEST_REVIEW
```

## Review question

Verify that dev20's new production-factory integration test is an infrastructure-only coverage addition: it must prove production request/factory composition using real `prepare_execution`, `native_session`, `SessionRunner`, `NativeDriver`, and `Coordinator` while only replacing lower OS/authority construction seams. It must not change the reviewed business oracle, native acceptance criteria, error mapping, qualification rules, or HOST_READY semantics.

A PASS may only be issued by the independent TEST_REVIEW workflow against the exact identities above. IMPLEMENT does not self-close this review.
