#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def must_replace(path, old, new, count=1):
    p=ROOT/path; s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'missing expected text in {path}: {old[:100]}')
    p.write_text(s.replace(old,new,count),encoding='utf-8')

# PROJECT_STATE.md
p=ROOT/'PROJECT_STATE.md'; s=p.read_text(encoding='utf-8')
repls={
'REVISION: R11_V41_AUTHORITY_REFERENCE_CONSISTENCY':'REVISION: R12_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION',
'DESIGN_BRANCH: lane/docs-v2-r9-v41-authority-reference-design':'DESIGN_BRANCH: lane/docs-v2-r9-v41-v02-auth-design',
'REVIEW_BRANCH: lane/docs-v2-r9-v41-authority-reference-review':'REVIEW_BRANCH: lane/docs-v2-r9-v41-v02-auth-review',
'AUDIT_BRANCH: lane/docs-v2-r9-v41-authority-reference-audit':'AUDIT_BRANCH: lane/docs-v2-r9-v41-v02-auth-audit',
'DESIGN_RECORD: docs/DOCUMENTATION_SYSTEM_R9_V41_FORENSIC_HARDENING.md':'DESIGN_RECORD: docs/DOCUMENTATION_SYSTEM_R9_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION.md',
'FINAL_REVIEW_ID: DOC-V2-R9-REVIEW-012':'FINAL_REVIEW_ID: DOC-V2-R9-REVIEW-013',
'FINAL_REVIEW_RECORD: reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R12_PASS.md':'FINAL_REVIEW_RECORD: reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R13_PASS.md',
'FINAL_AUDIT_ID: DOC-V2-R9-AUDIT-012':'FINAL_AUDIT_ID: DOC-V2-R9-AUDIT-013',
'FINAL_AUDIT_RECORD: reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R12_PASS.md':'FINAL_AUDIT_RECORD: reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R13_PASS.md',
'ACTIVATION_CONDITION: "Exact V41 authority-reference-consistency tree requires R12 review PASS and A12 audit PASS bound to the same design commit."':'ACTIVATION_CONDITION: "Exact V41 external-authenticity reconciliation tree requires R13 review PASS and A13 audit PASS bound to the same design commit."',
'PROMOTION_RULE: "After audit, main may add only R12/A12 immutable verdict records to the exact audited V41 authority-reference-consistency tree; post-promotion CI is mandatory."':'PROMOTION_RULE: "After audit, main may add only R13/A13 immutable verdict records to the exact audited V41 external-authenticity reconciliation tree; post-promotion CI is mandatory."',
'  VALIDATION_EVIDENCE_HEAD: 8024990809364168f7bd04cde44ccf7b30c60b66':'  VALIDATION_EVIDENCE_HEAD: 9a3854d80b7e4c35c5d2ec933709280ce0baa7fa',
'  PENDING_EFFECTIVENESS_MEASUREMENT: 4':'  PENDING_EFFECTIVENESS_MEASUREMENT: 5',
'  CURRENT_PENDING_MEASUREMENTS: "LEARNING-SOURCE-VISIBILITY-001@NEXT_FORMAL_SOURCE_HANDOFF; LEARNING-WORKFLOW-CONTINUITY-001@3_INTERRUPTED_RESUME_EVENTS; LEARNING-EVIDENCE-SEMANTICS-007@V42; LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008@NEXT_DOCUMENTATION_PROMOTION_OR_AUTHORITY_REFERENCE_REGRESSION"':'  CURRENT_PENDING_MEASUREMENTS: "LEARNING-SOURCE-VISIBILITY-001@NEXT_FORMAL_SOURCE_HANDOFF; LEARNING-WORKFLOW-CONTINUITY-001@3_INTERRUPTED_RESUME_EVENTS; LEARNING-EVIDENCE-SEMANTICS-007@V42; LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008@NEXT_DOCUMENTATION_PROMOTION_OR_AUTHORITY_REFERENCE_REGRESSION; LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009@NEXT_EXTERNAL_KEY_ACTIVATION_OR_SIGNED_APPROVAL"',
'  REASON: "Recovery-state effectiveness is reconciled, but V02 remains blocked until independently verified protected external LAB authority exists."':'  REASON: "V02 authenticity hardening is deployed, but authority remains blocked until independently established external Ed25519 key provenance is reviewed/activated and a signed exact approval envelope plus protected object graph verify successfully."',
'NEXT_ACTION: "Resume unchanged RUN-P00-VALIDATION-001 at V02. Only independently verified external LAB authority may advance V02 to V03."':'NEXT_ACTION: "Resume unchanged RUN-P00-VALIDATION-001 at V02. First obtain independently established external Ed25519 public-key provenance for separate reviewed trust-anchor activation; only a subsequently signed exact approval envelope plus protected authority graph may advance V02 to V03."'
}
for a,b in repls.items():
    if a not in s: raise SystemExit('PROJECT_STATE missing '+a[:80])
    s=s.replace(a,b,1)
s=s.replace(
'  AUTHORITY_REFERENCE_EVIDENCE: workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015.md\n  NOTE: "R11/A11 remain immutable authority for their prior exact SHA only. This correction removes live-authority prose that still named superseded R10/A10 and adds machine checks that derive the current verdict pair from canonical governance state. Native V02 remains unchanged."',
'  AUTHORITY_REFERENCE_EVIDENCE: workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015.md\n  V02_EXTERNAL_AUTHENTICITY_EVIDENCE: workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-V02-AUTHENTICITY-016.md\n  NOTE: "Historical R12/A12 authorized the prior authority-reference tree. This revision reconciles the independently reviewed/deployed V02 external-authenticity boundary from validation lane head 9a3854d8... while preserving all native NOT_RUN and qualification/SITE/HOST_READY boundaries."',1)
needle='  APPROVAL_ENVELOPE_MAPPING: validation/LAB_APPROVAL_ENVELOPE_MAPPING-P00-DEV21.md\n'
insert='''  APPROVAL_ENVELOPE_MAPPING: validation/LAB_APPROVAL_ENVELOPE_MAPPING-P00-DEV21.md
  EXTERNAL_AUTHENTICITY_HARDENING: validation/V02_EXTERNAL_AUTHENTICITY_HARDENING-P00-DEV21.md
  EXTERNAL_AUTHENTICITY_DEPLOYMENT: validation/V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT-P00-DEV21.md
  EXTERNAL_AUTHENTICITY_DEPLOYMENT_REVIEW: reviews/VALIDATION-V02-AUTHENTICITY-DEPLOYMENT-REVIEW-001_PASS.md
  EXTERNAL_AUTHENTICITY_STATUS: DEPLOYED_PENDING_EXTERNAL_KEY
  EXTERNAL_TRUST_ALGORITHM: ED25519
  EXTERNAL_TRUST_CONFIG_STATUS: PENDING_EXTERNAL_KEY
  APPROVAL_ENVELOPE_STATUS: MISSING
  V02_READY_TO_ADVANCE: false
'''
if needle not in s: raise SystemExit('PROJECT_STATE validation insertion anchor missing')
s=s.replace(needle,insert,1)
s=s.replace('    EXTERNAL_AUTHORITY_ATTESTED: false\n    APPROVED: false','    EXTERNAL_AUTHORITY_ATTESTED: false\n    EXTERNAL_AUTHORITY_SIGNATURE_VERIFIED: false\n    EXTERNAL_KEY_PROVENANCE_VERIFIED: false\n    APPROVED: false',1)
s=s.replace('  GUARDED_SELF_OPTIMIZATION: ACTIVE\n','  GUARDED_SELF_OPTIMIZATION: ACTIVE\n  EXTERNAL_AUTHENTICITY_LEARNING: LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009\n',1)
old='V41 authority-reference correction is valid only if the exact correction tree passes executable checks and independent R12/A12 review confirms that current authority prose derives from canonical governance, historical verdict references are explicitly historical, the CONTROL-001 effectiveness receipt is semantically valid, learning 008 is only conditionally activated, and product/native authority remains unchanged.'
new='V41 external-authenticity reconciliation is valid only if the exact design tree passes executable checks and independent R13/A13 review confirms the promoted validation head, external-key/signature boundary, learning lifecycle and native NOT_RUN/qualification/SITE/HOST_READY non-drift. Historical R12/A12 remains evidence for the prior exact documentation tree only.'
if old not in s: raise SystemExit('PROJECT_STATE bottom paragraph missing')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# NEXT_WORK_ITEM.md
p=ROOT/'NEXT_WORK_ITEM.md'; s=p.read_text(encoding='utf-8')
s=s.replace('STATUS: BLOCKED_EXTERNAL_AUTHORITY_ONLY','STATUS: BLOCKED_EXTERNAL_AUTHENTICITY_AND_AUTHORITY',1)
s=s.replace('  VALIDATION_LANE: lane/validation-p00\n','  VALIDATION_LANE: lane/validation-p00\n  VALIDATION_EVIDENCE_HEAD: 9a3854d80b7e4c35c5d2ec933709280ce0baa7fa\n',1)
needle='  LAB_EXTERNAL_APPROVAL_HANDOFF: validation/LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md\n'
if needle not in s: raise SystemExit('NEXT_WORK_ITEM handoff anchor missing')
s=s.replace(needle,needle+'''  V02_EXTERNAL_AUTHENTICITY_HARDENING: validation/V02_EXTERNAL_AUTHENTICITY_HARDENING-P00-DEV21.md
  V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT: validation/V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT-P00-DEV21.md
  V02_DEPLOYMENT_REVIEW: reviews/VALIDATION-V02-AUTHENTICITY-DEPLOYMENT-REVIEW-001_PASS.md
  EXTERNAL_TRUST_ALGORITHM: ED25519
  EXTERNAL_TRUST_CONFIG_STATUS: PENDING_EXTERNAL_KEY
  APPROVAL_ENVELOPE_STATUS: MISSING
  READY_TO_ADVANCE: false
''',1)
s=s.replace('GOAL: "Close V02 only with independently approved protected registration/owner-controller attestation and approved exact dev21 fixture/plan/suite authority for the already-prepared AI-FILM-P00-LAB candidate; then execute the mandatory 86-case reviewed LAB inventory and produce qualification evidence before any SITE active operation."','GOAL: "Close V02 only after independently established external Ed25519 public-key provenance is separately reviewed/activated and the external authority signs the exact approval envelope binding the protected registration/attestation/fixture/plan/suite graph for the prepared LAB; then execute the mandatory 86-case reviewed LAB inventory before qualification or SITE activity."',1)
s=s.replace('  - V02_LAB_EXECUTION_AUTHORITY: BLOCKED_EXTERNAL_AUTHORITY_ONLY','  - V02_LAB_EXECUTION_AUTHORITY: BLOCKED_EXTERNAL_AUTHENTICITY_AND_AUTHORITY',1)
s=s.replace('SUCCESS_OUTPUT: "Verified protected LAB registration/owner-controller attestation plus protected fixture/plan refs and approved <=24h exact-dev21 lab_acceptance_suite bound to candidate 336b12af-cada-4968-8083-8a5b41e479a2."','SUCCESS_OUTPUT: "Verified independently rooted external Ed25519 signature over the exact approval envelope plus protected LAB registration/owner-controller attestation, fixture/plan refs and approved <=24h exact-dev21 lab_acceptance_suite bound to candidate 336b12af-cada-4968-8083-8a5b41e479a2."',1)
s=s.replace('EXIT_CONDITION: "V02 authority prerequisites are independently established for the prepared LAB candidate; no native stage has run before this condition."','EXIT_CONDITION: "External key provenance is independently verified and separately activated; the exact signed authority graph passes V02 intake; no native stage has run before this condition."',1)
s=s.replace('REASON: "Technical disposable LAB infrastructure and the sealed pending authority bundle are complete. Remaining V02 requirement is an independent external authority decision that turns the protected pending candidate into approved registration/attestation, fixture/plan and <=24h suite records."','REASON: "Technical LAB infrastructure and V02 authenticity enforcement are complete. Remaining V02 requirements are independently established external Ed25519 public-key provenance, separate reviewed trust-anchor activation, then an externally signed exact approval envelope and protected authority graph."',1)
s=s.replace('Do **not** create another LAB and do not start the stopped LAB for native execution. The external owner/controller must review the protected bundle identified by `fa38540df...` and return the immutable protected refs specified by `LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md`. Credentials and raw SID/MachineGuid stay out of GitHub. Only after those records independently verify may this same run advance V02 → V03.','''Do **not** create another LAB and do not start the stopped LAB for native execution. The next external action is **not** to write an `APPROVE` file into the local inbox. The external owner/controller must first establish an Ed25519 public-key identity and protected/out-of-band provenance. That public key is then activated only through a separate reviewed trust-anchor transaction; the private key never belongs on this host or in GitHub.

After activation, the external authority reviews the sealed bundle `fa38540df...`, returns the protected refs required by `LAB_EXTERNAL_APPROVAL_HANDOFF-P00-DEV21.md`, and signs the **exact raw bytes** of `approval-envelope.json`. Only a signature under the activated external key plus the fully verified hash-addressed authority graph may advance this same run V02 → V03. Credentials, raw SID/MachineGuid and private signing material stay out of GitHub.''',1)
p.write_text(s,encoding='utf-8')

# AI_FILM_PROJECT_STATE_V41.json
p=ROOT/'AI_FILM_PROJECT_STATE_V41.json'; o=json.loads(p.read_text(encoding='utf-8'))
g=o['documentation_governance']
g.update({'revision':'R12_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION','design_branch':'lane/docs-v2-r9-v41-v02-auth-design','review_branch':'lane/docs-v2-r9-v41-v02-auth-review','audit_branch':'lane/docs-v2-r9-v41-v02-auth-audit','design_record':'docs/DOCUMENTATION_SYSTEM_R9_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION.md','final_review_id':'DOC-V2-R9-REVIEW-013','final_review_record':'reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R13_PASS.md','final_audit_id':'DOC-V2-R9-AUDIT-013','final_audit_record':'reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R13_PASS.md','v02_external_authenticity_evidence':'workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-V02-AUTHENTICITY-016.md'})
v=o['validation']; v['validation_evidence_head']='9a3854d80b7e4c35c5d2ec933709280ce0baa7fa'
v['external_authenticity']={'status':'DEPLOYED_PENDING_EXTERNAL_KEY','algorithm':'ED25519','trust_config_status':'PENDING_EXTERNAL_KEY','approval_envelope_status':'MISSING','ready_to_advance':False,'external_key_provenance_verified':False,'external_signature_verified':False,'deployment_record':'validation/V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT-P00-DEV21.md','deployment_review':'reviews/VALIDATION-V02-AUTHENTICITY-DEPLOYMENT-REVIEW-001_PASS.md'}
la=o['learning_activation']; la['pending_effectiveness_measurement']=5
la['current_pending_measurements'].append({'learning_id':'LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009','gate':'NEXT_EXTERNAL_KEY_ACTIVATION_OR_SIGNED_APPROVAL'})
la['external_authenticity_learning']='LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009'
p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

# AI_FILM_STATE_CHECKPOINT_V41.md
p=ROOT/'AI_FILM_STATE_CHECKPOINT_V41.md'; s=p.read_text(encoding='utf-8')
s=s.replace('The new correction must be reviewed by R12 and audited by A12 on one exact design SHA. Historical R10/A10 and R11/A11 references remain available when explicitly labeled as prior/superseded evidence; they are not live authority for the new tree.','The historical R12/A12 correction was reviewed/audited on its exact prior design SHA. Historical R10/A10, R11/A11 and R12/A12 references remain evidence only and are not live authority for the new tree.',1)
s=s.replace('candidate receipt `learning/measurements/MEASUREMENT-LEARNING-CONTROL-001-001.md` marks it EFFECTIVE only subject to independent R12/A12 semantic verification.','candidate receipt `learning/measurements/MEASUREMENT-LEARNING-CONTROL-001-001.md` was later confirmed by historical R12/A12 semantic review.',1)
s=s.replace('Canonical next action remains `RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY`; documentation-governance repair cannot substitute for protected external LAB authority.','''## V02 external-authenticity reconciliation

Validation lane head `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa` records a forensic trust-boundary correction without native execution. The approved local inbox was confirmed writable by the constrained Windows operator, so ACL protection plus content hashes could prove local integrity but not independent external authorship. Reviewed/audited tooling now requires an Ed25519 signature over the exact raw approval-envelope bytes under a hash-pinned external trust config.

Runtime deployment is verified fail-closed: trust config remains `PENDING_EXTERNAL_KEY`, `approval-envelope.json` is missing, READY and native-policy candidates are absent, HKLM native trust is absent, the V02 watcher is enabled/active, and `AI-FILM-P00-LAB` remains Stopped. All 86 native procedures remain `NOT_RUN`; qualification, SITE and HOST_READY remain unchanged.

New `LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009` captures the reusable rule: local ACL ownership and content-addressing are not independent authority when the constrained operator can write the store. External authority must be cryptographically rooted outside that operator boundary, and key activation itself is a separate reviewed transaction.

The exact reconciliation tree must be independently reviewed by R13 and audited by A13. Historical R12/A12 remains authority only for its prior exact documentation tree.

Canonical next action remains `RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY`: obtain external Ed25519 public-key provenance, review/activate only that public key, then require a genuinely externally signed exact approval envelope before V03.''',1)
p.write_text(s,encoding='utf-8')

# Learning lifecycle
p=ROOT/'learning/LEARNING_STATE.json'; reg=json.loads(p.read_text(encoding='utf-8'))
r8=reg['records']['LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008']
r8['review_status']='PASS'; r8['activation_status']='ACTIVE'; r8['activated_in']='DOCSYS-V2-R9'; r8['review_record']='reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R12_PASS.md'
reg['records']['LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009']={'record':'learning/LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009.md','score':10,'activation_target':'DOCSYS-V2-R9','review_status':'PASS_ON_FINAL_REVIEW','review_record':'reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R13_PASS.md','activation_status':'ACTIVE_ON_PROMOTION','activated_in':'DOCSYS-V2-R9','activation_evidence':['reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R13_PASS.md','reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R13_PASS.md'],'activation_blocker':None,'effectiveness_status':'PENDING_MEASUREMENT','effectiveness_evidence':[],'effectiveness_receipt':None,'success_metric':'Future external-authority activation/approval workflows reject operator-authored, unsigned, wrong-key or trust-anchor-drifted authority; only independently provenance-rooted signatures can authorize the exact envelope, and no native stage advances while the external anchor is pending.','measurement_trigger':'external authority key activation or signed approval attempt','measurement_gate':{'kind':'NEXT_QUALIFYING_EVENT','event_kind':'EXTERNAL_AUTHORITY_KEY_ACTIVATION_OR_SIGNED_APPROVAL'},'successor':None}
p.write_text(json.dumps(reg,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

# PROJECT_MEMORY
p=ROOT/'PROJECT_MEMORY.md'; s=p.read_text(encoding='utf-8')
marker='| MEM-20260917-001 | GOVERNANCE | Live review/audit authority in prose must derive from canonical final verdict IDs; older verdict pairs are valid only when explicitly historical/superseded context is stated. | `tools/check_project_docs.py`, `tools/test_project_docs_checker.py` |\n'
if marker not in s: raise SystemExit('memory marker missing')
s=s.replace(marker,marker+'| MEM-20260918-001 | SECURITY | External authority is not established by operator-writable ACL protection or content hashes alone; root authenticity in independently established cryptographic provenance outside the constrained operator boundary. | V02 authority tooling/contract, `NEXT_WORK_ITEM.md` |\n',1)
p.write_text(s,encoding='utf-8')

# New records
(ROOT/'learning/LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009.md').write_text('''# LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009 — External authority requires provenance outside the constrained operator boundary

```yaml
LEARNING_ID: LEARNING-EXTERNAL-AUTHORITY-AUTHENTICITY-009
DISCOVERED_IN: RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY
CLASS: SECURITY
OBSERVATION: "The protected LAB approved inbox had inheritance disabled and content-addressed objects, but the constrained Windows operator still had FullControl. Those controls proved local integrity and limited ambient writers; they did not prove that an external owner/controller authored the approval package."
ROOT_CAUSE: "The workflow conflated filesystem protection plus content integrity with independent authority provenance. A principal able to author the trusted store could satisfy structural assertions without proving an external decision."
EVIDENCE: "lane/validation-p00@9a3854d80b7e4c35c5d2ec933709280ce0baa7fa: workflow-health/HEALTH_REVIEW-WF-P00-V02-AUTHENTICITY-003.md; validation/V02_EXTERNAL_AUTHENTICITY_DEPLOYMENT-P00-DEV21.md; reviews/VALIDATION-V02-AUTHENTICITY-REVIEW-001_PASS.md; reviews/VALIDATION-V02-AUTHENTICITY-AUDIT-001_PASS.md; reviews/VALIDATION-V02-AUTHENTICITY-DEPLOYMENT-REVIEW-001_PASS.md"
REUSABLE_RULE: "When a workflow claims authority is external to the operator it constrains, authenticity must root in a credential/provenance boundary the operator cannot self-issue. Local ACLs and hashes remain integrity controls; require a separately reviewed external trust anchor and cryptographic signature, fail closed while the anchor is pending, and never generate the external private key inside the constrained environment."
SCORE: 10
CURRENT_ACTION: "Keep V02 trust config PENDING_EXTERNAL_KEY; obtain external Ed25519 public-key provenance; review activation separately; require exact-envelope signature before any protected object graph can authorize V03."
POLICY_OR_TOOL_PROMOTION: "validation V02 tooling/contract; PROJECT_STATE.md; NEXT_WORK_ITEM.md; PROJECT_MEMORY.md"
SUCCESS_METRIC: "Future external-authority activation/approval workflows reject operator-authored, unsigned, wrong-key or trust-anchor-drifted authority; only independently provenance-rooted signatures can authorize the exact envelope, and no native stage advances while the external anchor is pending."
STATUS: CANDIDATE_PENDING_R13_A13
```

This learning does not claim effectiveness yet. The current deployment proves only that the pending-anchor path fails closed. Effectiveness requires a future qualifying external-key activation or signed-approval attempt and independently reviewed evidence against the immutable metric.
''',encoding='utf-8')

(ROOT/'workflow-health/HEALTH_REVIEW-DOCSYS-R9-V41-V02-AUTHENTICITY-016.md').write_text('''# HEALTH_REVIEW-DOCSYS-R9-V41-V02-AUTHENTICITY-016

```yaml
HEALTH_REVIEW_ID: HEALTH-DOCSYS-R9-V41-V02-AUTHENTICITY-016
STATE_VERSION: 41
DOCUMENTATION_RELEASE: DOCSYS-V2-R9
TRIGGER: VALIDATION_LANE_EXTERNAL_AUTHENTICITY_PROMOTION
VALIDATION_HEAD: 9a3854d80b7e4c35c5d2ec933709280ce0baa7fa
STATUS: RECONCILIATION_CANDIDATE
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
V02_ADVANCED: false
V03_STARTED: false
```

## Reconciled facts

Validation lane independently reviewed, audited, deployed and deployment-reviewed a V02 trust-boundary hardening. The prior approved inbox was writable by the same Windows operator V02 intended to constrain; ACL isolation and SHA-addressed objects therefore provided local integrity but not independent external provenance.

Exact validation head `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa` requires Ed25519 authentication of the exact raw approval-envelope bytes under a separately activated external public-key anchor. The deployed anchor intentionally remains `PENDING_EXTERNAL_KEY`; no private key is stored/generated locally. Real-inbox checks remain `APPROVAL_ENVELOPE_MISSING`, READY/native-policy/HKLM trust are absent and LAB remains Stopped.

## Canonical reconciliation

This documentation revision changes only control-plane truth/routing: validation evidence head, V02 exit predicate, external action wording and reusable learning. Exact dev21 source/package/test/contract identity is unchanged. All 86 native cases remain NOT_RUN; qualification, SITE and HOST_READY remain unchanged.

Learning 008 is finalized ACTIVE using its completed historical R12/A12 activation evidence so it does not depend on the new promotion verdict fields. New learning 009 is conditional on R13/A13 activation and remains PENDING_MEASUREMENT.

## Review boundary

R13/A13 must verify exact validation-head provenance, external authenticity semantics, Markdown/JSON parity, current R13/A13 authority references, learning aggregates and product/native non-drift. The documentation layer must not claim an external key exists, that V02 is satisfied, or that V03 may start.
''',encoding='utf-8')

(ROOT/'docs/DOCUMENTATION_SYSTEM_R9_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION.md').write_text('''# DOCSYS-V2-R9 V41 — external-authenticity reconciliation

## Purpose

Revision `R12_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION` reconciles canonical documentation with exact validation lane head `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa`. It does not advance native validation. Its purpose is to prevent the canonical router from treating operator-writable protected files as sufficient evidence of an external decision.

## Validation fact change

The LAB candidate, dev21 identities and 86-case inventory are unchanged. What changed is the **trust model** for V02. Validation forensic review established that the approved inbox ACL and SHA-addressed object graph provide integrity, but the current operator has write authority to that local store. Therefore those controls cannot independently prove external authorship.

Reviewed/audited validation tooling now requires:

1. an independently established Ed25519 public-key identity/provenance;
2. a separate reviewed activation transaction for that public trust anchor;
3. a detached Ed25519 signature over the exact raw `approval-envelope.json` bytes;
4. unchanged SHA-addressed protected refs/role pins/suite/fixture/plan semantic checks;
5. fail-closed behavior while the external trust config is `PENDING_EXTERNAL_KEY`.

The external private key must never be generated or stored in the constrained host/operator environment.

## Canonical truth after reconciliation

- validation evidence head: `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa`;
- V02 hardening: `DEPLOYED_PENDING_EXTERNAL_KEY`;
- real approval envelope: MISSING;
- V02 ready-to-advance: false;
- LAB: Stopped / native NOT_RUN;
- qualification: NOT_ISSUED;
- SITE: NOT_RUN;
- HOST_READY: NOT_EVALUATED.

## Learning lifecycle

Historical R12/A12 completed activation evidence for learning 008, so this revision finalizes 008 from `ACTIVE_ON_PROMOTION` to `ACTIVE` without coupling it to R13/A13. New learning 009 captures the external-authenticity boundary and is `ACTIVE_ON_PROMOTION` only after R13/A13; effectiveness remains pending a future external-key activation or signed-approval event.

## Promotion boundary

This tree predeclares new final verdicts `DOC-V2-R9-REVIEW-013` and `DOC-V2-R9-AUDIT-013`. Historical R12/A12 remains immutable evidence for the prior exact documentation tree only. R13/A13 must bind one exact final design SHA; promotion may add only those two verdict records and requires post-promotion main CI.

## Non-claims

No external key is activated by documentation. No approval package exists. No native trust is installed. No LAB case is executed. No product code changes. No qualification, SITE evidence or HOST_READY is produced.
''',encoding='utf-8')

(ROOT/'docs/DOCUMENTATION_R9_V41_EXTERNAL_AUTH_REVIEW_CRITERIA.md').write_text('''# DOCSYS-V2-R9 V41 External Authenticity — R13 Detailed Review Criteria

R13 may PASS only if one exact `R12_V41_EXTERNAL_AUTHENTICITY_RECONCILIATION` design SHA satisfies all conditions below.

1. State remains V41/VALIDATION and exact dev21 source/package/test/contract identities are unchanged.
2. Validation evidence head is exactly `9a3854d80b7e4c35c5d2ec933709280ce0baa7fa` and R13 verifies that remote branch currently resolves to that commit.
3. Canonical V02 routing explicitly requires independently established Ed25519 public-key provenance, separate reviewed trust-anchor activation, and an externally signed exact approval envelope before V03.
4. Documentation does not claim an ACTIVE external key, approval envelope, READY flag, native trust, native execution, qualification, SITE evidence or HOST_READY.
5. `PROJECT_STATE.md`, JSON V41 and NEXT_WORK_ITEM agree on `DEPLOYED_PENDING_EXTERNAL_KEY`, `PENDING_EXTERNAL_KEY`, missing envelope and not-ready state.
6. R13/A13 identities, branch roles and active design record are predeclared; historical R12/A12 is not reused for the changed tree.
7. Learning 008 is finalized ACTIVE only from completed historical R12/A12 evidence; it remains PENDING_MEASUREMENT unless separately measured.
8. Learning 009 immutable metric matches the lifecycle register, is conditional `ACTIVE_ON_PROMOTION`, and remains PENDING_MEASUREMENT.
9. Derived learning aggregates equal the register: zero activation backlog, zero unresolved ineffective, five pending effectiveness measurements, zero overdue, three semantically verified EFFECTIVE and four historical INEFFECTIVE.
10. Current-authority prose passes stale-verdict detector using R13/A13 as the live pair; older verdict pairs are line-locally historical/superseded only.
11. Existing lifecycle, 16 adversarial lifecycle cases, documentation governance, active-doc + 4 adversarial active-doc cases, workflow continuity and holistic audit all PASS on the exact design target.
12. Platform main protection remains explicit external debt; no repository-enforcement claim is invented.

Any native/product advancement, local-key self-issuance, unsigned-approval allowance, stale validation head, stale live verdict pair or lifecycle mismatch requires R13 FAIL.
''',encoding='utf-8')

(ROOT/'docs/DOCUMENTATION_R9_V41_EXTERNAL_AUTH_AUDIT_CRITERIA.md').write_text('''# DOCSYS-V2-R9 V41 External Authenticity — A13 Holistic Audit Criteria

A13 may PASS only after R13 PASS exists for the same exact design SHA and the review-bearing commit itself passes REVIEW-stage CI.

1. Exact-tree chain is design → one R13 review record → one A13 audit record; no state/policy/checker edit occurs after the reviewed design SHA.
2. Validation head provenance is exact and the documentation faithfully represents deployed pending-anchor behavior rather than merely copying intended design.
3. The external-authority model distinguishes integrity (ACL/hash) from authenticity (external cryptographic provenance) and never lets the constrained operator self-issue the external trust root.
4. The private external key is explicitly out of scope for the host/repository; current trust config remains pending.
5. V02 remains BLOCKED; V03/native/qualification/SITE/HOST_READY boundaries remain unchanged.
6. Learning lifecycle retains failure provenance, finalizes old activation without current-verdict coupling and adds learning 009 without claiming effectiveness.
7. Markdown/JSON/checkpoint/NEXT routing are mutually consistent and current R13/A13 authority is machine-checkable.
8. CI covers all standing governance checks and the exact review-bearing commit.
9. GitHub main protection/ruleset enforcement is not falsely claimed.
10. Post-promotion main CI is mandatory; any edit after A13 reopens review/audit.

Any false closure of V02, external-key self-generation, unsigned authority path, stale truth, erased finding or native/product drift requires A13 FAIL.
''',encoding='utf-8')

print('AUTHORING_READY')
