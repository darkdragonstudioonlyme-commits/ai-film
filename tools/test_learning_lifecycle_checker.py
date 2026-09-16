#!/usr/bin/env python3
"""Adversarial regression tests for the learning lifecycle checker."""
from pathlib import Path
import json,shutil,subprocess,tempfile

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


def stale_activation(dst):
    p,d=reg(dst); r=d['records']['LEARNING-LIFECYCLE-CONSISTENCY-002']
    r['review_status']='PASS'; r['activation_status']='PENDING_ACTIVATION'
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
    p=dst/'PROJECT_STATE.md'; s=p.read_text(encoding='utf-8')
    p.write_text(s.replace('STATE_VERSION: 33','STATE_VERSION: 36'),encoding='utf-8')


def release_drift(dst):
    p,d=reg(dst); d['candidate_documentation_release']='DOCSYS-V2-R999'; write_reg(p,d)


def main():
    cases=[
        ('stale_activation',stale_activation,'stale-current-release-activation'),
        ('ineffective_without_successor',ineffective_without_successor,'ineffective-without-successor'),
        ('aggregate_drift',aggregate_drift,'learning-backlog-drift'),
        ('effective_without_evidence',effective_without_evidence,'effective-without-evidence'),
        ('active_without_activation_evidence',active_without_activation_evidence,'active-without-activation-evidence'),
        ('overdue_measurement_drift',overdue_measurement_drift,'learning-overdue-measurement-drift'),
        ('release_drift',release_drift,'register-documentation-release-drift'),
    ]
    for name,mutate,expected in cases: run_case(name,mutate,expected)
    print('ADVERSARIAL_LEARNING_LIFECYCLE_TEST_PASS',len(cases),'cases')


if __name__=='__main__': main()
