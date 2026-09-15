# AI-FILM-SERVER — Operating Architecture and Trust Boundaries

## Control-plane architecture

```text
Business/Reviewed Contracts
        │
        ├──> TEST AUTHORITY ──> independent tests/evidence
        │
        └──> IMPLEMENT/DESIGN producer workflows
                         │ immutable output
                         ▼
                    REVIEW consumer
                         │ findings/verdict
                         ▼
                    canonical main
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     state/router     roadmap       memory/policy
```

No workflow trusts another workflow's self-declared PASS. Consumers verify immutable identity and evidence.

## Workflow classes

- DESIGN → DESIGN_REVIEW
- IMPLEMENT/PATCH → CODE_REVIEW
- TEST-DESIGN/TEST-SCRIPT → TEST-REVIEW when oracle materially changes
- VALIDATION → validation evidence, never source patching
- DOC-DESIGN → DOC-REVIEW → DOC-AUDIT
- MODEL-EVAL → independent evaluation review
- WORKFLOW_REVIEW → governance review when process health degrades

## Separation of concerns

- state answers **where we are**;
- roadmap answers **where we are going**;
- router answers **what happens next**;
- test strategy answers **how behavior is judged**;
- policy registry answers **which operating rules are active**;
- memory answers **what reusable lessons were learned**;
- environment answers **where measurements are valid**;
- recovery answers **how to return to trusted state**.

## Trust rule

A label such as PASS, COMPLETE, REVIEWED or CURRENT has no authority without the identity/evidence contract owned by that workflow.
