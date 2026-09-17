#!/usr/bin/env python3
"""Adversarial regression tests for the learning lifecycle checker."""
from pathlib import Path
import json,os,re,shutil,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
CHECKER=Path('tools/check_learning_lifecycle.py')

def execute(dst,role=None):
    env=os.environ.copy()
    if role: env['AIFILM_DOCSYS_ROLE']=role
    return subprocess.run(['python3',str(CHECKER)],cwd=dst,text=True,capture_output=True,env=env)
def run_case(name,mutate,expected,role=None):
    with tempfile.TemporaryDirectory(prefix='r9-learning-check-') as td:
        dst=Path(td)/'repo'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
        mutate(dst); proc=execute(dst,role); output=proc.stdout+proc.stderr
        if proc.returncode==0 or expected not in output:
            raise AssertionError(f'{name}: expected fail containing {expected!r}; rc={proc.returncode}; output={output}')
        print(f'PASS {name}: {expected}')
def run_pass_case(name,mutate,role=None):
    with tempfile.TemporaryDirectory(prefix='r9-learning-check-') as td:
        dst=Path(td)/'repo'; shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
        mutate(dst); proc=execute(dst,role); output=proc.stdout+proc.stderr
        if proc.returncode!=0:
            raise AssertionError(f'{name}: expected pass; rc={proc.returncode}; output={output}')
        print(f'PASS {name}: accepted role={role or "GENERIC"}')
def reg(dst):
    p=dst/'learning/LEARNING_STATE.json'; return p,json.loads(p.read_text(encoding='utf-8'))
def write_reg(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def state_field(dst,name):
    text=(dst/'PROJECT_STATE.md').read_text(encoding='utf-8'); m=re.search(rf'^\s*{re.escape(name)}:\s*(.*?)\s*$',text,re.M)
    if not m: raise AssertionError(f'missing state field {name}')
    v=m.group(1).strip(); return v[1:-1] if len(v)>=2 and v[0]==v[-1]=='"' else v
def promotion_contract(dst):
    return {'release':state_field(dst,'DOCUMENTATION_SYSTEM'),'review_id':state_field(dst,'FINAL_REVIEW_ID'),
            'review_record':state_field(dst,'FINAL_REVIEW_RECORD'),'audit_id':state_field(dst,'FINAL_AUDIT_ID'),
            'audit_record':state_field(dst,'FINAL_AUDIT_RECORD')}
def clear_promotion_verdicts(dst):
    c=promotion_contract(dst)
    for key in ('review_record','audit_record'):
        p=dst/c[key]
        if p.exists(): p.unlink()
    return c
def verdict_text(kind,target,c):
    if kind=='review':
        return f"REVIEW_ID: {c['review_id']}\nTARGET_RELEASE: {c['release']}\nTARGET_DESIGN_COMMIT: {target}\nVERDICT: PASS\n"
    return f"AUDIT_ID: {c['audit_id']}\nTARGET_RELEASE: {c['release']}\nTARGET_DESIGN_COMMIT: {target}\nREQUIRED_REVIEW_ID: {c['review_id']}\nVERDICT: PASS\n"
def stale_activation(dst):
    p,d=reg(dst); release=promotion_contract(dst)['release']
    k,r=next((k,v) for k,v in d['records'].items() if v.get('activation_target')==release and v.get('activation_status') in {'ACTIVE','ACTIVE_ON_PROMOTION'})
    r['review_status']='PASS'; r['activation_status']='PENDING_ACTIVATION'; r['activation_blocker']=None; write_reg(p,d)
def ineffective_without_successor(dst):
    p,d=reg(dst); d['records']['LEARNING-DOCSYS-ACTIVATION-001']['successor']=None; write_reg(p,d)
def aggregate_drift(dst):
    p=dst/'PROJECT_STATE.md'; s=p.read_text(); p.write_text(s.replace('LEARNED_BUT_NOT_ACTIVE_BACKLOG: 0','LEARNED_BUT_NOT_ACTIVE_BACKLOG: 9'))
def effective_without_evidence(dst):
    p,d=reg(dst); d['records']['LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004']['effectiveness_evidence']=[]; write_reg(p,d)
def effective_without_receipt(dst):
    p,d=reg(dst); d['records']['LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004']['effectiveness_receipt']=None; write_reg(p,d)
def success_metric_drift(dst):
    p,d=reg(dst); d['records']['LEARNING-WORKFLOW-CONTINUITY-001']['success_metric']='weakened metric'; write_reg(p,d)
def receipt_metric_hash_mismatch(dst):
    _,d=reg(dst); rp=dst/d['records']['LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004']['effectiveness_receipt']
    s=rp.read_text(); rp.write_text(re.sub(r'(?m)^SUCCESS_METRIC_SHA256: .*$', 'SUCCESS_METRIC_SHA256: '+'0'*64,s))
def unrelated_effectiveness_evidence(dst):
    p,d=reg(dst); d['records']['LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004']['effectiveness_evidence']=['README.md']; write_reg(p,d)
def active_without_activation_evidence(dst):
    p,d=reg(dst); d['records']['LEARNING-SOURCE-VISIBILITY-001']['activation_evidence']=[]; write_reg(p,d)
def overdue_measurement_drift(dst):
    rp,d=reg(dst); sp=dst/'PROJECT_STATE.md'; s=sp.read_text(); current=int(re.search(r'^STATE_VERSION: (\d+)$',s,re.M).group(1))
    r=d['records']['LEARNING-ADVERSARIAL-STATE-INDEPENDENCE-004']; r['effectiveness_status']='PENDING_MEASUREMENT'; r['effectiveness_evidence']=[]; r['effectiveness_receipt']=None; r['measurement_gate']={'kind':'STATE_VERSION_AT_LEAST','value':current}; write_reg(rp,d)
    pending=sum(1 for x in d['records'].values() if x.get('effectiveness_status')=='PENDING_MEASUREMENT')
    s=re.sub(r'^\s*PENDING_EFFECTIVENESS_MEASUREMENT:\s*\d+\s*$',f'  PENDING_EFFECTIVENESS_MEASUREMENT: {pending}',s,flags=re.M)
    s=re.sub(r'^\s*OVERDUE_EFFECTIVENESS_MEASUREMENT:\s*\d+\s*$','  OVERDUE_EFFECTIVENESS_MEASUREMENT: 0',s,flags=re.M); sp.write_text(s)
def release_drift(dst):
    p,d=reg(dst); d['candidate_documentation_release']='DOCSYS-V2-R999'; write_reg(p,d)
def partial_promotion_verdict(dst):
    c=clear_promotion_verdicts(dst); p=dst/c['review_record']; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(verdict_text('review','a'*40,c))
def mismatched_promotion_target(dst):
    c=clear_promotion_verdicts(dst); rp=dst/c['review_record']; ap=dst/c['audit_record']; rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(verdict_text('review','a'*40,c)); ap.write_text(verdict_text('audit','b'*40,c))
def design_stage(dst): clear_promotion_verdicts(dst)
def review_stage(dst):
    c=clear_promotion_verdicts(dst); p=dst/c['review_record']; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(verdict_text('review','a'*40,c))
def audit_stage(dst):
    c=clear_promotion_verdicts(dst); rp=dst/c['review_record']; ap=dst/c['audit_record']; rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(verdict_text('review','a'*40,c)); ap.write_text(verdict_text('audit','a'*40,c))

def main():
    cases=[
      ('stale_activation',stale_activation,'stale-current-release-activation',None),
      ('ineffective_without_successor',ineffective_without_successor,'ineffective-without-successor',None),
      ('aggregate_drift',aggregate_drift,'learning-backlog-drift',None),
      ('effective_without_evidence',effective_without_evidence,'effective-without-evidence',None),
      ('effective_without_receipt',effective_without_receipt,'effective-without-receipt',None),
      ('success_metric_drift',success_metric_drift,'success-metric-drift',None),
      ('receipt_metric_hash_mismatch',receipt_metric_hash_mismatch,'receipt-metric-hash',None),
      ('unrelated_effectiveness_evidence',unrelated_effectiveness_evidence,'receipt-evidence-binding',None),
      ('active_without_activation_evidence',active_without_activation_evidence,'active-without-activation-evidence',None),
      ('overdue_measurement_drift',overdue_measurement_drift,'learning-overdue-measurement-drift',None),
      ('release_drift',release_drift,'register-documentation-release-drift',None),
      ('partial_promotion_verdict',partial_promotion_verdict,'partial-promotion-verdict-set',None),
      ('mismatched_promotion_target',mismatched_promotion_target,'promotion-target-design-mismatch',None),
    ]
    for name,mutate,expected,role in cases: run_case(name,mutate,expected,role)
    run_pass_case('design_stage_predeclared_verdicts',design_stage,'DESIGN')
    run_pass_case('review_stage_review_only',review_stage,'REVIEW')
    run_pass_case('audit_stage_full_verdict_set',audit_stage,'AUDIT')
    print('ADVERSARIAL_LEARNING_LIFECYCLE_TEST_PASS',len(cases)+3,'cases')
if __name__=='__main__': main()
