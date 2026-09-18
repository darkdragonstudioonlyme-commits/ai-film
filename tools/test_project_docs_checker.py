#!/usr/bin/env python3
"""Adversarial regression cases for current documentation-authority semantics."""
from pathlib import Path
import json,re,shutil,subprocess,sys,tempfile,os

ROOT=Path(__file__).resolve().parents[1]
STATE=(ROOT/'PROJECT_STATE.md').read_text(encoding='utf-8')

def state_field(name):
    m=re.search(rf'^\s*{re.escape(name)}:\s*(.*?)\s*$',STATE,re.M)
    if not m: raise RuntimeError(f'missing state field {name}')
    value=m.group(1).strip()
    if len(value)>=2 and value[0]==value[-1]=='"': value=value[1:-1]
    return value

def ordinal(value):
    m=re.search(r'-(\d+)$',value)
    if not m: raise RuntimeError(f'no ordinal in {value}')
    return int(m.group(1))

state_version=int(re.search(r'^STATE_VERSION: (\d+)$',STATE,re.M).group(1))
review_id=state_field('FINAL_REVIEW_ID')
audit_id=state_field('FINAL_AUDIT_ID')
review_n=ordinal(review_id); audit_n=ordinal(audit_id)
stale_review=max(1,review_n-1) if review_n>1 else review_n+1
stale_audit=max(1,audit_n-1) if audit_n>1 else audit_n+1
stale_pair=f'R{stale_review}/A{stale_audit}'
checkpoint=f'AI_FILM_STATE_CHECKPOINT_V{state_version}.md'


def run_case(mutator=None,role='PROMOTED'):
    with tempfile.TemporaryDirectory(prefix='aifilm-docs-check-') as td:
        dst=Path(td)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__'))
        if mutator: mutator(dst)
        env=os.environ.copy(); env['AIFILM_DOCSYS_ROLE']=role
        return subprocess.run(
            [sys.executable,str(dst/'tools/check_project_docs.py')],
            cwd=dst,text=True,capture_output=True,env=env
        )

def require(name,proc,should_pass,needle=None):
    ok=(proc.returncode==0)
    output=(proc.stdout or '')+(proc.stderr or '')
    if ok!=should_pass or (needle and needle not in output):
        print(f'FAIL {name}')
        print(output)
        raise SystemExit(1)
    print(f'PASS {name}')

require('baseline',run_case(),True,'DOCS_CHECK_PASS')

def stale_live(dst):
    p=dst/checkpoint
    p.write_text(p.read_text(encoding='utf-8')+f'\nCurrent review/audit authority: {stale_pair}.\n',encoding='utf-8')
require('stale_live_authority',run_case(stale_live),False,'stale-verdict-authority')

def explicit_history(dst):
    p=dst/checkpoint
    p.write_text(p.read_text(encoding='utf-8')+f'\nHistorical {stale_pair} evidence remains prior and is not promotion authority.\n',encoding='utf-8')
require('explicit_historical_authority',run_case(explicit_history),True,'DOCS_CHECK_PASS')

def governance_parity_drift(dst):
    p=dst/'PROJECT_STATE.md'
    text=p.read_text(encoding='utf-8')
    text=text.replace(f'FINAL_REVIEW_ID: {review_id}',f'FINAL_REVIEW_ID: {review_id}-DRIFT',1)
    p.write_text(text,encoding='utf-8')
require('governance_parity_drift',run_case(governance_parity_drift),False,'governance-parity:FINAL_REVIEW_ID')



def promoted_candidate_state(dst):
    p=dst/'PROJECT_STATE.md'; text=p.read_text(encoding='utf-8')
    text=re.sub(r'(?m)^(\s*PROMOTION_STATE:)\s*\S+',r'\1 CANDIDATE_REVIEW_REQUIRED',text,count=1)
    p.write_text(text,encoding='utf-8')
    jp=dst/f'AI_FILM_PROJECT_STATE_V{state_version}.json'; data=json.loads(jp.read_text(encoding='utf-8'))
    data['documentation_governance']['promotion_state']='CANDIDATE_REVIEW_REQUIRED'
    jp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
require('promoted_candidate_state',run_case(promoted_candidate_state),False,'promoted-promotion-state-stale')

def prospective_current_pair(dst):
    p=dst/checkpoint
    p.write_text(p.read_text(encoding='utf-8')+f'\nCurrent tree still requires prospective R{review_n}/A{audit_n} review/audit before promotion.\n',encoding='utf-8')
require('promoted_current_pair_prospective',run_case(prospective_current_pair),False,'promoted-current-verdict-stage-drift')
require('design_current_pair_prospective',run_case(prospective_current_pair,role='DESIGN'),True,'DOCS_CHECK_PASS')

def subject_to_current_pair_review(dst):
    p=dst/checkpoint
    p.write_text(p.read_text(encoding='utf-8')+f'\nLearning state is EFFECTIVE candidate, subject to R{review_n}/A{audit_n} semantic review before it is final.\n',encoding='utf-8')
require('promoted_current_pair_subject_to_review',run_case(subject_to_current_pair_review),False,'promoted-current-verdict-stage-drift')
require('design_current_pair_subject_to_review',run_case(subject_to_current_pair_review,role='DESIGN'),True,'DOCS_CHECK_PASS')

def mixed_line_historical_mask(dst):
    p=dst/checkpoint
    older_review=max(1,review_n-2) if review_n>2 else review_n+2
    older_audit=max(1,audit_n-2) if audit_n>2 else audit_n+2
    older=f'R{older_review}/A{older_audit}'
    p.write_text(p.read_text(encoding='utf-8')+f'\nHistorical {older} evidence remains prior. Current review/audit authority: {stale_pair}.\n',encoding='utf-8')
require('mixed_line_historical_does_not_mask_live_stale',run_case(mixed_line_historical_mask),False,'stale-verdict-authority')

def mixed_line_historical_current_stage(dst):
    p=dst/checkpoint
    older_review=max(1,review_n-1) if review_n>1 else review_n+1
    older_audit=max(1,audit_n-1) if audit_n>1 else audit_n+1
    older=f'R{older_review}/A{older_audit}'
    current=f'R{review_n}/A{audit_n}'
    p.write_text(p.read_text(encoding='utf-8')+f'\nHistorical {older} evidence remains prior. Current {current} is still prospective before promotion.\n',encoding='utf-8')
require('mixed_line_historical_does_not_mask_current_stage',run_case(mixed_line_historical_current_stage),False,'promoted-current-verdict-stage-drift')

def source_visibility_parity_drift(dst):
    p=dst/'PROJECT_STATE.md'
    text=p.read_text(encoding='utf-8').replace('FULL_SOURCE_GIT_MIRROR: true','FULL_SOURCE_GIT_MIRROR: false',1)
    p.write_text(text,encoding='utf-8')
require('source_visibility_parity_drift',run_case(source_visibility_parity_drift),False,'source-visibility-parity:FULL_SOURCE_GIT_MIRROR')

def full_git_tree_missing_ref(dst):
    p=dst/'PROJECT_STATE.md'
    text=p.read_text(encoding='utf-8').replace('REMOTE_SOURCE_REF: source/p00-dev21-exact','REMOTE_SOURCE_REF: null',1)
    p.write_text(text,encoding='utf-8')
    jp=dst/f'AI_FILM_PROJECT_STATE_V{state_version}.json'
    data=json.loads(jp.read_text(encoding='utf-8'))
    data['source_visibility']['remote_source_ref']=None
    jp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
require('full_git_tree_missing_ref',run_case(full_git_tree_missing_ref),False,'source-visibility-full-tree-contract')

print('ADVERSARIAL_PROJECT_DOCS_TEST_PASS 13 cases')
