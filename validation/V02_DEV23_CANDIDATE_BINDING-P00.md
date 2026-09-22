# Phase00 dev23 — candidate binding preparation

```yaml
BINDING_ID: V02-DEV23-CANDIDATE-BINDING-P00-001
RUN_ID: RUN-P00-VALIDATION-002
STATUS: PROPOSED_PENDING_CROSS_MODEL_REVIEW
CANDIDATE_ID: acf18da3-4969-451c-8a4b-a7e46ad89c98
CANDIDATE_BINDING_SHA256: ed7823332afa96c3335f3353518ca0330b9e3c687b0022926c776319611c1890
SOURCE_COMMIT: 2f7da39984a7a582c7cf2a84f743299fc7fe735f
SOURCE_TREE: 4bcd0cd81b9f90d6f48d811229a52bb152415ef0
PACKAGE_SHA256: d60433b2b559c975dd93378db7c3c8481ba80896deb539d8227b28b169a83dbf
WHEEL_SHA256: 55853acf55374db3e8da6159ae6fe26dcad2d0a6b7f022aef79b2009c40253df
BUILD_DIGEST: d07c053704f58f18647b9e3d0eca778d930d9af9e8595d3c4e6e13462511bb6d
TEST_SET_DIGEST: c859758b4bbe8e467c0495238c28cededf261aa89a639044a59833bf51859864
CONTRACT_DIGEST: f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee
IMPLEMENTATION_VERSION: 0.1.0.dev23
AUTHORITY_MODEL: LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN
NATIVE_EXECUTION_AUTHORIZED: false
AUTHORITY_SIGNING_AUTHORIZED: false
```

The candidate ID is a fresh opaque UUID allocated once for this reviewed dev23 identity. Deterministic authority binding is the SHA256 of the exact canonical JSON bytes in `validation/tooling/dev23-candidate-binding.json`, including its final newline, matching the dev22 binding convention. The UUID is not claimed to be derived from source bytes.

The binding uses the exact reviewed source/package/wheel/source-content/test/contract identities. Its functional test authority is TEST_REVIEW 007; package/version identity is additionally covered by TEST_REVIEW 008, CODE_REVIEW dev23 and the package-identity review on canonical main. No dev22 package, build digest, test digest, wheel hash, candidate ID or binding hash is reused as dev23 proof.

This record creates no authority envelope, signature, HKLM policy or native permission.
