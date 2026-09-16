#!/usr/bin/env python3
"""Adversarial regression tests for the learning lifecycle checker."""
from pathlib import Path
import json,re,shutil,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
CHECKER=Path('tools/check_learning_lifecycle.py')


def run_case(name, mutate, expected):
    with tempfile.TemporaryDirectory(prefix='r9-learning-check-') as td:
        dst=Path(td)/'repo'
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
        mutate(dst)
        proc=subprocess.run(['python3',str(CHECKER)],cwd=dst,text=True,capture_output=True)
        output=proc.stdout+proc.stderr
        if proc.returncode==0 or expected not in output:
            raise AssertionError(f'{name}: expected fail containing {expected!r}; rc={proc.returncode}; output={output}')
        print(f'PASS {name}: {expected}')


def reg(dst):
    p=dst/'learning/LEARNING_STATE.json'
    return p,json.loads(p.read_text(encoding='utf-8'))


def write_reg(p,d):
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def state_field(dst,name):
    text=(dst/'PROJECT_STATE.md').read_text(encoding='utf-8')
    m=re.search(rf'^\s*{re.escape(name)}:\s*(\S+)\s*$',text,re.M)
    if not m: raise AssertionError(f'missing state field {name}')
    return m.group(1)


def promotion_contract(dst):
    return {
        'release':state_field(dst,'DOCUMENTATION_SYSTEM'),
        'review_id':state_field(dst,'FINAL_REVIEW_ID'),
        'review_record':state_field(dst,'FINAL_REVIEW_RECORD'),
        'audit_id':state_field(dst,'FINAL_AUDIT_ID'),
        'audit_record':state_field(dst,'FINAL_AUDIT_RECORD'),
    }


def clear_promotion_verdicts(dst):
    c=promotion_contract(dst)
    for key in ('review_record','audit_record'):
        p=dst/c[key]
        if p.exists(): p.unlink()
    return c


def stale_activation(dst):
    p,d=reg(dst); release=promotion_contract(dst)['release']
    eligible=[(k,v) for k,v in d['records'].items()
              if v.get('activation_target')==release and v.get('activation_status') in {'ACTIVE','ACTIVE_ON_PROMOTION'}]
    if not eligible: raise AssertionError('no current-release active learning fixture')
    current,r=eligible[0]
    r['review_status']='PASS'; r['activation_status']='PENDING_ACTIVATION'; r['activation_blocker']=None
    write_reg(p,d)


def ineffective_without_successor(dst):
    p,d=reg(dst); d['records']['LEARNING-DOCSYS-ACTIVATION-001']['successor']=None; write_reg(p,d)


def aggregate_drift(dst):
    p=dst/'PROJECT_STATE.md'; s=p.read_text(encoding='utf-8')
    p.write_text(s.replace('LEARNED_BUT_NOT_ACTIVE_BACKLOG: 0','LEARNED_BUT_NOT_ACTIVE_BACKLOG: 9'),encoding='utf-8')


def effective_without_evidence(dst):
    p,d=reg(dst); d['records']['LEARNING-CONTROL-001']['effectiveness_evidence']=[]; write_reg(p,d)


def active_without_activation_evidence(dst):
    p,d=reg(dst); d['records']['LEARNING-SOURCE-VISIBILITY-001']['activation_evidence']=[]; write_reg(p,d)


def overdue_measurement_drift(dst):
    """Construct a due pending measurement even when the live register has none."""
    rp,d=reg(dst)
    sp=dst/'PROJECT_STATE.md'; s=sp.read_text(encoding='utf-8')
    m=re.search(r'^STATE_VERSION: (\d+)$',s,re.M); assert m
    current=int(m.group(1))
    release=promotion_contract(dst)['release']
    eligible=[r for r in d['records'].values()
              if r.get('activation_target')==release and r.get('activation_status') in {'ACTIVE','ACTIVE_ON_PROMOTION'}]
    if not eligible: raise AssertionError('no active learning for pending-measurement fixture')
    r=eligible[0]
    r['effectiveness_status']='PENDING_MEASUREMENT'
    r['effectiveness_evidence']=[]
    r['measurement_gate']={'kind':'STATE_VERSION_AT_LEAST','value':current}
    write_reg(rp,d)
    pending=sum(1 for row in d['records'].values() if row.get('effectiveness_status')=='PENDING_MEASUREMENT')
    s=re.sub(r'^\s*PENDING_EFFECTIVENESS_MEASUREMENT:\s*\d+\s*$',
             f'  PENDING_EFFECTIVENESS_MEASUREMENT: {pending}',s,flags=re.M)
    s=re.sub(r'^\s*OVERDUE_EFFECTIVENESS_MEASUREMENT:\s*\d+\s*$',
             '  OVERDUE_EFFECTIVENESS_MEASUREMENT: 0',s,flags=re.M)
    sp.write_text(s,encoding='utf-8')


def release_drift(dst):
    p,d=reg(dst); d['candidate_documentation_release']='DOCSYS-V2-R999'; write_reg(p,d)


def verdict_text(kind,target,c):
    if kind=='review':
        return (f"REVIEW_ID: {c['review_id']}\nTARGET_RELEASE: {c['release']}\n"
                f'TARGET_DESIGN_COMMIT: {target}\nVERDICT: PASS\n')
    return (f"AUDIT_ID: {c['audit_id']}\nTARGET_RELEASE: {c['release']}\n"
            f"TARGET_DESIGN_COMMIT: {target}\nREQUIRED_REVIEW_ID: {c['review_id']}\nVERDICT: PASS\n")


def partial_promotion_verdict(dst):
    c=clear_promotion_verdicts(dst)
    p=dst/c['review_record']; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(verdict_text('review','a'*40,c),encoding='utf-8')


def mismatched_promotion_target(dst):
    c=clear_promotion_verdicts(dst)
    rp=dst/c['review_record']; ap=dst/c['audit_record']; rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(verdict_text('review','a'*40,c),encoding='utf-8')
    ap.write_text(verdict_text('audit','b'*40,c),encoding='utf-8')


def main():
    cases=[
        ('stale_activation',stale_activation,'stale-current-release-activation'),
        ('ineffective_without_successor',ineffective_without_successor,'ineffective-without-successor'),
        ('aggregate_drift',aggregate_drift,'learning-backlog-drift'),
        ('effective_without_evidence',effective_without_evidence,'effective-without-evidence'),
        ('active_without_activation_evidence',active_without_activation_evidence,'active-without-activation-evidence'),
        ('overdue_measurement_drift',overdue_measurement_drift,'learning-overdue-measurement-drift'),
        ('release_drift',release_drift,'register-documentation-release-drift'),
        ('partial_promotion_verdict',partial_promotion_verdict,'partial-promotion-verdict-set'),
        ('mismatched_promotion_target',mismatched_promotion_target,'promotion-target-design-mismatch'),
    ]
    for name,mutate,expected in cases: run_case(name,mutate,expected)
    print('ADVERSARIAL_LEARNING_LIFECYCLE_TEST_PASS',len(cases),'cases')


if __name__=='__main__': main()
