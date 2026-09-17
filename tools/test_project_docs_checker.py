#!/usr/bin/env python3
"""Adversarial regression cases for current documentation-authority semantics."""
from pathlib import Path
import json,re,shutil,subprocess,sys,tempfile

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


def run_case(mutator=None):
    with tempfile.TemporaryDirectory(prefix='aifilm-docs-check-') as td:
        dst=Path(td)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__'))
        if mutator: mutator(dst)
        return subprocess.run(
            [sys.executable,str(dst/'tools/check_project_docs.py')],
            cwd=dst,text=True,capture_output=True
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

print('ADVERSARIAL_PROJECT_DOCS_TEST_PASS 4 cases')
