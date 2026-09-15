#!/usr/bin/env python3
from pathlib import Path
import re,sys,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
active=['README.md','PROJECT_STATE.md','NEXT_WORK_ITEM.md','PROJECT_ROADMAP.md','WORKFLOW_ROUTER.md',
'EXECUTION_LANES.md','DOCUMENTATION_MAP.md','PROJECT_MEMORY.md','SELF_LEARNING.md','TEST_STRATEGY.md',
'WORKFLOW_HEALTH.md','POLICY_REGISTRY.md','SERVER_ENVIRONMENT.md','MODEL_EVALUATION.md','RECOVERY_PLAYBOOK.md',
'OPERATING_ARCHITECTURE.md','GIT_WORKFLOW.md','WORKSPACE_WSL.md','CHAT_HANDOFF.md']
errors=[]
texts={p:(ROOT/p).read_text(encoding='utf-8') for p in active if (ROOT/p).is_file()}
# Active protocol docs must be version agnostic except state/task/workspace/environment/roadmap/memory.
allow_version={'PROJECT_STATE.md','NEXT_WORK_ITEM.md','SERVER_ENVIRONMENT.md','PROJECT_ROADMAP.md','PROJECT_MEMORY.md'}
for p,t in texts.items():
    if p not in allow_version and re.search(r'0\.1\.0\.dev\d+',t): errors.append('stale-version-risk:'+p)
# Workspace map must not duplicate mutable source candidate identities.
workspace=texts.get('WORKSPACE_WSL.md','')
if re.search(r'0\.1\.0\.dev\d+',workspace): errors.append('workspace-mutable-version')
if re.search(r'\b[0-9a-f]{40}\b',workspace): errors.append('workspace-source-commit-pin')
if re.search(r'\b\d+ PASS\b',workspace): errors.append('workspace-test-count-pin')
if re.search(r'active .*V2 (design|review|audit)',workspace,re.I): errors.append('workspace-transient-workflow-activity')
# Checkers cannot hard-code a delivery file/hash.
for p in ['tools/check_project_docs.py','tools/check_runtime_state.py','tools/audit_documentation_v2.py']:
    t=(ROOT/p).read_text(encoding='utf-8')
    if re.search(r'IMPLEMENTATION_PACKAGE_V\d+',t): errors.append('checker-hardcoded-package:'+p)
# Business-first tests / policy retirement / learning effects.
if 'code is the subject under test' not in texts.get('TEST_STRATEGY.md',''): errors.append('test-code-authority-risk')
if 'SUPERSEDED' not in texts.get('POLICY_REGISTRY.md','') or 'RETIRED' not in texts.get('POLICY_REGISTRY.md',''): errors.append('policy-lifecycle-incomplete')
if 'SUCCESS_METRIC' not in texts.get('SELF_LEARNING.md',''): errors.append('learning-no-measurement')
if 'DOC-AUDIT-V2' not in texts.get('EXECUTION_LANES.md',''): errors.append('missing-holistic-audit-lane')
if 'environments/' not in texts.get('SERVER_ENVIRONMENT.md','') or 'SNAPSHOT_DIGEST' not in texts.get('SERVER_ENVIRONMENT.md',''): errors.append('environment-record-contract-incomplete')
if 'Owner' not in texts.get('POLICY_REGISTRY.md','') or 'Review trigger' not in texts.get('POLICY_REGISTRY.md',''): errors.append('policy-accountability-incomplete')
for path in ['environments/README.md','model-evaluations/README.md','learning/README.md']:
    if not (ROOT/path).is_file(): errors.append('missing-record-domain:'+path)
env_record=ROOT/'environments/ENV-DEV-WSL-20260915.md'
if env_record.is_file():
    et=env_record.read_text(encoding='utf-8')
    if 'DIGEST_INPUT: exact UTF-8 bytes of CANONICAL_JSON_PAYLOAD' not in et or 'Canonical JSON payload' not in et:
        errors.append('environment-digest-ambiguous')
    m_payload=re.search(r'```json\n(.+?)\n```',et,re.S)
    m_digest=re.search(r'SNAPSHOT_DIGEST: ([0-9a-f]{64})',et)
    if not m_payload or not m_digest:
        errors.append('environment-digest-record-missing')
    else:
        try:
            obj=json.loads(m_payload.group(1))
            canonical=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
            if hashlib.sha256(canonical).hexdigest()!=m_digest.group(1):
                errors.append('environment-digest-mismatch')
        except (ValueError,TypeError):
            errors.append('environment-canonical-json-invalid')
# Bootstrap docs must point to canonical router/state, not own current versions.
for p in ['README.md','CHAT_HANDOFF.md']:
    t=texts.get(p,'')
    if 'PROJECT_STATE.md' not in t or 'WORKFLOW_ROUTER.md' not in t: errors.append('bootstrap-routing:'+p)
# Active docs should not call historical V1 governance current.
for p,t in texts.items():
    if p!='PROJECT_STATE.md' and 'SYSTEM_VERSION: V1' in t: errors.append('historical-leak:'+p)
if errors:
    print('DOC_AUDIT_FAIL');print('\n'.join(errors));sys.exit(1)
print('DOC_AUDIT_PASS',len(texts),'active docs')
