#!/usr/bin/env python3
"""Shared-workflow pure guards. No model launch, lifecycle mutation or runtime claim."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from check_state_contract import load_selected_state
from check_current_work import scalar

ACTORS = {'CHATGPT', 'CLAUDE_CODE'}
HEX64 = re.compile(r'[0-9a-f]{64}')

class SharedError(ValueError):
    pass

def require(ok, reason):
    if not ok:
        raise SharedError(reason)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')

def sha(value):
    return hashlib.sha256(value).hexdigest()

def strings(value):
    return (type(value) is list and all(type(x) is str and x for x in value)
            and len(value) == len(set(value)))

def knowledge_view(register, invalidated_ids=()):
    """Derived eligibility only; semantic truth/relevance is not inferred."""
    require(type(register) is dict and type(register.get('records')) is dict,
            'REGISTER_SCHEMA')
    records = register['records']
    require(all(type(k) is str and k and type(v) is dict for k,v in records.items()),
            'RECORD_SCHEMA')
    require(type(invalidated_ids) in (tuple, list) and all(type(x) is str for x in invalidated_ids), 'INVALIDATION_SCHEMA')
    invalidated = set(invalidated_ids)
    require(invalidated <= set(records), 'UNKNOWN_INVALIDATION')
    for key, row in records.items():
        nxt = row.get('successor')
        require(nxt is None or type(nxt) is str and nxt in records, 'SUCCESSOR_MISSING')
    for key in records:
        seen = set(); cursor = key
        while cursor is not None:
            require(cursor not in seen, 'SUCCESSOR_CYCLE')
            seen.add(cursor); cursor = records[cursor].get('successor')
    operative = {}; warnings = {}; blocked = []
    for key, row in sorted(records.items()):
        eff = row.get('effectiveness_status')
        require(eff in {'EFFECTIVE', 'INEFFECTIVE', 'PENDING_MEASUREMENT', 'NOT_MEASURED'},
                'EFFECTIVENESS_STATE')
        if key in invalidated:
            warnings[key] = 'QUARANTINED'; blocked.append(key)
        elif row.get('successor') is not None:
            terminal = row['successor']
            while records[terminal].get('successor') is not None:
                terminal = records[terminal]['successor']
            final = records[terminal]
            usable = (terminal not in invalidated and final.get('activation_status') == 'ACTIVE'
                      and final.get('review_status') == 'PASS'
                      and final.get('effectiveness_status') in {'EFFECTIVE', 'PENDING_MEASUREMENT', 'NOT_MEASURED'})
            warnings[key] = 'HISTORICAL_WARNING' if usable else 'REVALIDATION_REQUIRED'
            if not usable:
                blocked.append(key)
        elif row.get('activation_status') != 'ACTIVE' or row.get('review_status') != 'PASS':
            warnings[key] = 'NOT_ACTIVE_REVIEWED'
        elif eff == 'INEFFECTIVE':
            warnings[key] = 'REVALIDATION_REQUIRED'; blocked.append(key)
        else:
            operative[key] = 'METRIC_EFFECTIVE' if eff == 'EFFECTIVE' else 'UNMEASURED'
    return {'operative': operative, 'warnings': warnings, 'blocked': blocked}

def validate_selection(register, selected_ids, read_ids, applied_ids, context_sha, current_sha, *, invalidated_ids=()):
    """Host must independently verify hashes/bytes and supply current invalidations."""
    require(type(context_sha) is str and HEX64.fullmatch(context_sha)
            and type(current_sha) is str and HEX64.fullmatch(current_sha), 'CONTEXT_HASH')
    require(context_sha == current_sha, 'STALE_CONTEXT')
    require(all(strings(v) for v in (selected_ids, read_ids, applied_ids)), 'KNOWLEDGE_IDS')
    view = knowledge_view(register, invalidated_ids)
    require(set(selected_ids) <= set(view['operative']), 'NONOPERATIVE_SELECTION')
    require(set(selected_ids) <= set(read_ids), 'MISSING_CONTEXT_ACK')
    require(set(applied_ids) <= set(selected_ids), 'UNSELECTED_APPLICATION')
    return True

def check_actor_projection(state, md, nxt):
    w = state.get('current_work', {})
    require(type(w) is dict, 'CURRENT_WORK')
    for key, mdkey, nwkey in (('assignee','CURRENT_ASSIGNEE','ASSIGNEE'),
                              ('author_actor','CURRENT_AUTHOR_ACTOR','AUTHOR_ACTOR')):
        require(type(w.get(key)) is str and w[key] in ACTORS, 'ACTOR_SCHEMA')
        require(w[key] == scalar(md, mdkey) == scalar(nxt,nwkey), 'ACTOR_PROJECTION')
    role = w.get('role')
    require(type(role) is str and role in {'AUTHOR','REVIEW','AUDIT'}, 'ROLE_SCHEMA')
    modes={'AUTHOR':{'DOC_DESIGN','DESIGN','IMPLEMENTATION','PATCH','TEST_DESIGN','WORKFLOW_REVIEW'},
           'REVIEW':{'DOC_REVIEW','DESIGN_REVIEW','CODE_REVIEW','TEST_REVIEW'},
           'AUDIT':{'DOC_AUDIT'}}
    require(type(w.get('mode')) is str and w['mode'] in modes[role], 'MODE_ROLE_CONFLICT')
    require(w.get('profile') in {'TEXT_REVIEW','WSL_IMPLEMENT','CONTROL_PLANE_AUTHOR'},
            'PROFILE_SCHEMA')
    if role in {'REVIEW','AUDIT'}:
        require(w['assignee'] != w['author_actor'], 'SELF_ACCEPTANCE')
        require(w['profile'] == 'TEXT_REVIEW', 'REVIEW_PROFILE')
    else:
        require(w['assignee'] == w['author_actor'], 'AUTHOR_IDENTITY')
        require(w['profile'] in {'WSL_IMPLEMENT','CONTROL_PLANE_AUTHOR'}, 'AUTHOR_PROFILE')
    require(type(w.get('return_to')) is str and bool(w['return_to'])
            and w['return_to'] == scalar(nxt,'RETURN_TO'), 'RETURN_CURSOR')
    require(type(w.get('next_on_success')) is str and bool(w['next_on_success'])
            and w['next_on_success'] == scalar(nxt,'ON_SUCCESS'), 'NEXT_CURSOR')
    return True

def check_governance_runtime_scope(state, md=None):
    g=state.get('documentation_governance', {});c=state.get('collaboration', {})
    require(type(g) is dict and type(c) is dict, 'ACCEPTANCE_SCOPE_SCHEMA')
    require(type(c.get('cross_model_acceptance')) is str and c['cross_model_acceptance'] in {'NOT_RUN','PASS','FAIL'}, 'CROSS_MODEL_STATE')
    if g.get('promotion_state') == 'PROMOTED':
        require(g.get('projection_semantics') == 'INTENDED_CANONICAL_CONTENT_NOT_PUBLICATION_PROOF'
                and g.get('acceptance_rule') == 'MATCHED_POLICY_VERDICTS_NOT_LOCAL_MARKER'
                and c.get('acceptance_scope') == 'EXECUTOR_RUNTIME_PROFILE', 'POLICY_RUNTIME_ACCEPTANCE_CONFLATION')
    if md is not None:
        for key, name in [('projection_semantics','PROJECTION_SEMANTICS'),('acceptance_rule','ACCEPTANCE_RULE')]:
            values=re.findall(r'^  '+name+r':[ \t]*(.*)$', md, re.M)
            require(len(values)==1 and values[0].strip()==g.get(key), 'GOVERNANCE_SCOPE_PROJECTION')
    return True

FACT_KEYS = {'identities_match','permission_denied','design_hold','knowledge_invalidated',
             'context_current','transport','work_complete','output_verified','profile_ready','prerequisites_satisfied'}

def next_action(facts):
    """Deterministic planning reference; caller facts are NOT authenticated here."""
    require(type(facts) is dict and set(facts) == FACT_KEYS, 'ROUTE_FACT_SCHEMA')
    require(all(type(v) is bool for k,v in facts.items() if k != 'transport'), 'ROUTE_BOOL')
    require(facts['transport'] in {'IDLE','RUNNING','RECONCILE_REQUIRED',
                                  'RESULT_UNREVIEWED','CONSUMED'}, 'TRANSPORT_STATE')
    if not facts['identities_match']:
        return 'RECONCILE_IDENTITIES'
    if facts['permission_denied']:
        return 'BLOCKED_PERMISSION'
    if facts['design_hold'] or facts['knowledge_invalidated']:
        return 'APPLICABILITY_HOLD'
    if facts['transport'] in {'RUNNING','RECONCILE_REQUIRED'}:
        return 'RECONCILE_EXISTING_ATTEMPT'
    if not facts['context_current']:
        return 'RECONCILE_STALE_CONTEXT'
    if facts['transport'] == 'RESULT_UNREVIEWED':
        return 'VERIFY_EXISTING_RESULT'
    if facts['work_complete']:
        return 'SELECT_DECLARED_NEXT' if facts['output_verified'] else 'BLOCKED_MISSING_OUTPUT'
    if not facts['prerequisites_satisfied']:
        return 'BLOCKED_PREREQUISITES'
    return 'EXECUTE_ASSIGNED_STEP' if facts['profile_ready'] else 'BLOCKED_CAPABILITY'

def seal_static_review(task_digest, context_digest, actor, body, acceptance_ids):
    """Host hashes a complete body; model never hashes its future output envelope."""
    for h in (task_digest, context_digest):
        require(type(h) is str and HEX64.fullmatch(h), 'REPORT_CONTEXT')
    require(type(actor) is str and actor in ACTORS, 'REPORT_ACTOR')
    require(strings(acceptance_ids) and bool(acceptance_ids), 'ACCEPTANCE_IDS')
    required = {'assessment','covered','not_evaluated','findings','execution_scope','executed_commands'}
    require(type(body) is dict and set(body) == required, 'REPORT_SCHEMA')
    require(body['assessment'] in {'PASS','FINDINGS','BLOCKED','NOT_EVALUATED'}, 'REPORT_ASSESSMENT')
    require(body['execution_scope']=='STATIC_ONLY' and body['executed_commands']==[],
            'STATIC_EXECUTION_OVERCLAIM')
    require(strings(body['covered']) and strings(body['not_evaluated']), 'REPORT_COVERAGE')
    covered=set(body['covered']); missing=set(body['not_evaluated'])
    require(not (covered & missing) and covered | missing == set(acceptance_ids), 'COVERAGE_PARTITION')
    require(type(body['findings']) is list, 'FINDINGS_SCHEMA')
    ids=set(); blocking=False
    for f in body['findings']:
        require(type(f) is dict and set(f)=={'id','severity','status','evidence'}, 'FINDING_SCHEMA')
        require(type(f['id']) is str and f['id'] and f['id'] not in ids, 'FINDING_ID')
        ids.add(f['id'])
        require(f['severity'] in {'BLOCKER','HIGH','MEDIUM','LOW'}
                and f['status'] in {'OPEN','FIX_PENDING_REVIEW','VERIFIED_CLOSED'}, 'FINDING_STATE')
        require(type(f['evidence']) is str and bool(f['evidence'].strip()), 'FINDING_EVIDENCE')
        blocking |= f['status'] != 'VERIFIED_CLOSED' and f['severity'] in {'BLOCKER','HIGH'}
    require(body['assessment'] != 'PASS' or not missing and not blocking, 'UNSUPPORTED_PASS')
    raw=canonical(body)
    return raw, {'task_digest':task_digest,'context_digest':context_digest,
                 'actor':actor,'report_sha256':sha(raw),'transport_status':'RESULT_UNREVIEWED'}

def verify_report_bytes(raw, envelope, task_digest, current_context, expected_actor, acceptance_ids):
    require(type(raw) is bytes and type(envelope) is dict, 'REPORT_BYTES')
    require(envelope.get('report_sha256')==sha(raw), 'REPORT_HASH_MISMATCH')
    require(envelope.get('task_digest')==task_digest and envelope.get('context_digest')==current_context
            and envelope.get('actor')==expected_actor, 'REPORT_IDENTITY_MISMATCH')
    require(envelope.get('transport_status')=='RESULT_UNREVIEWED', 'REPORT_SELF_PROMOTION')
    def unique_pairs(pairs):
        obj={}
        for k,v in pairs:
            require(k not in obj, 'REPORT_DUPLICATE_KEY');obj[k]=v
        return obj
    def reject_constant(value):
        raise SharedError('REPORT_NONFINITE_NUMBER')
    try:
        body=json.loads(raw.decode('utf-8'),object_pairs_hook=unique_pairs,parse_constant=reject_constant)
    except (UnicodeError,json.JSONDecodeError) as exc:
        raise SharedError('REPORT_INVALID_JSON') from exc
    normalized,_=seal_static_review(task_digest,current_context,expected_actor,body,acceptance_ids)
    require(raw==normalized, 'REPORT_NOT_CANONICAL')
    return True

CAPABILITY_GATES = ('context_loading','cross_model_acceptance','dispatcher_qualification',
                    'permission_tests','recovery_tests','data_budget_authorization')

def check_capabilities(c):
    require(type(c) is dict and type(c.get('runtime_enabled')) is bool, 'RUNTIME_SCHEMA')
    gates=c.get('operational_gates')
    require(type(gates) is dict and set(gates)==set(CAPABILITY_GATES), 'CAPABILITY_GATES')
    require(all(v in {'PASS','NOT_VERIFIED','NOT_RUN','NOT_IMPLEMENTED'} for v in gates.values()),
            'CAPABILITY_STATE')
    if c['runtime_enabled']:
        require(all(v=='PASS' for v in gates.values()), 'AUTOMATION_NOT_QUALIFIED')
        require(c.get('capability_status')=='READY' and c.get('deployment_verified') is True,
                'RUNTIME_DEPLOYMENT')
    require(c.get('learning_effectiveness') in {'IMPROVEMENT_NOT_PROVEN','MEASURED_SCOPE_ONLY'}, 'EFFECTIVENESS_CLAIM')
    if c['learning_effectiveness']=='MEASURED_SCOPE_ONLY':
        m=c.get('effectiveness_receipt')
        require(type(m) is dict and type(m.get('path')) is str and type(m.get('sha256')) is str and HEX64.fullmatch(m['sha256']), 'MEASUREMENT_REQUIRED')
    return True

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--knowledge',action='store_true'); args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    _,_,state=load_selected_state(root)
    register=json.loads((root/'learning/LEARNING_STATE.json').read_text())
    view=knowledge_view(register)
    if args.knowledge:
        print(json.dumps(view,indent=2,sort_keys=True)); return 0
    check_actor_projection(state,(root/'PROJECT_STATE.md').read_text(),(root/'NEXT_WORK_ITEM.md').read_text())
    c=state.get('collaboration',{}); check_capabilities(c)
    check_governance_runtime_scope(state,(root/'PROJECT_STATE.md').read_text())
    require(scalar((root/'PROJECT_STATE.md').read_text(),'CROSS_MODEL_ACCEPTANCE_SCOPE') == c.get('acceptance_scope'), 'ACCEPTANCE_SCOPE_PROJECTION')
    from check_dual_ai_contract import relative_path
    ev=c.get('setup_observation')
    require(type(ev) is dict and set(ev)=={'path','sha256'}, 'SETUP_EVIDENCE')
    relative_path(ev['path']); p=root/ev['path']
    require(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==ev['sha256'], 'SETUP_HASH')
    receipt=json.loads(p.read_text())
    require(receipt.get('scope')=='SETUP_AND_BOUNDED_TEXT_CALLS_ONLY'
            and receipt.get('connectivity')=='PASS_REAL_INVOCATION', 'SETUP_SCOPE')
    require(c.get('capability_status') != 'BLOCKED_CLAUDE_NOT_FOUND', 'STALE_SETUP_STATE')
    if c['learning_effectiveness']=='MEASURED_SCOPE_ONLY':
        m=c['effectiveness_receipt']; relative_path(m['path']); mp=root/m['path']
        require(mp.is_file() and not mp.is_symlink() and sha(mp.read_bytes())==m['sha256'], 'MEASUREMENT_HASH')
    print('SHARED_WORKFLOW_CHECK_PASS scope=DECLARATIONS_AND_PURE_MODEL operative='+str(len(view['operative']))
          +' warnings='+str(len(view['warnings']))+' runtime=NOT_EVALUATED cross_model=NOT_EVALUATED effectiveness=SEMANTIC_REVIEW_REQUIRED')
    return 0

if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (SharedError,ValueError,OSError,TypeError,KeyError) as exc:
        print('SHARED_WORKFLOW_CHECK_FAIL',str(exc)); raise SystemExit(1)
