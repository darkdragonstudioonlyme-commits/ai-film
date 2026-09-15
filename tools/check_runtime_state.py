#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]; WS=Path('/home/dragon/ai-film-dev'); REPO=WS/'repo'; errors=[]
def run(*args,strip=True):
    value=subprocess.check_output(args,text=True); return value.strip() if strip else value
if not REPO.is_dir() or not (WS/'implement').is_dir() or not (WS/'review').is_dir():
    print('RUNTIME_STATE_CHECK_SKIPPED prepared WSL workspace unavailable'); raise SystemExit(0)
subprocess.check_call(['git','-C',str(REPO),'fetch','origin','main','lane/implement-p00','lane/review-p00'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
state=(ROOT/'PROJECT_STATE.md').read_text(encoding='utf-8')
m=re.search(r'^STATE_VERSION: (\d+)$',state,re.M)
if not m:
    print('CHECKER_DRIFT\nstate-version-missing'); raise SystemExit(2)
sv=int(m.group(1)); jp=ROOT/f'AI_FILM_PROJECT_STATE_V{sv}.json'
if not jp.is_file():
    print('CHECKER_DRIFT\nstate-json-missing:'+jp.name); raise SystemExit(2)
try: doc=json.loads(jp.read_text(encoding='utf-8'))
except (ValueError,TypeError):
    print('CHECKER_DRIFT\nstate-json-invalid'); raise SystemExit(2)
rr=doc.get('runtime_reconciliation')
allowed={'WIP','HANDED_OFF','REVIEWED_FAIL','REVIEWED_CLEAN_RESIDUAL_AUDIT','FINAL_AUTHOR_CANDIDATE','FORMAL_CODE_REVIEW','VALIDATION'}
if type(rr) is not dict or rr.get('schema_version')!=1 or rr.get('state_kind') not in allowed:
    print('CHECKER_DRIFT\nruntime-reconciliation-schema-or-kind'); raise SystemExit(2)
impl_head=run('git','-C',str(WS/'implement'),'rev-parse','HEAD'); review_head=run('git','-C',str(WS/'review'),'rev-parse','HEAD')
if impl_head!=rr['implement_head']: errors.append(f'implement-head:{impl_head}!={rr["implement_head"]}')
if review_head!=rr['review_head']: errors.append(f'review-head:{review_head}!={rr["review_head"]}')
porcelain=run('git','-C',str(WS/'implement'),'status','--porcelain',strip=False).splitlines()
actual_dirty={line[3:] for line in porcelain if len(line)>=4}; expected_dirty=set(rr['implement_dirty_files'])
if actual_dirty!=expected_dirty: errors.append(f'dirty-set:{sorted(actual_dirty)}!={sorted(expected_dirty)}')
impl_lane=run('git','-C',str(REPO),'show','origin/lane/implement-p00:LANE_STATE.md'); review_lane=run('git','-C',str(REPO),'show','origin/lane/review-p00:LANE_STATE.md')
for token in rr.get('implement_lane_required_tokens',[]):
    if token not in impl_lane: errors.append('implement-lane-token:'+token)
for token in rr.get('review_lane_required_tokens',[]):
    if token not in review_lane: errors.append('review-lane-token:'+token)
pkg=rr.get('package') or {}
if pkg.get('required'):
    path=Path(pkg.get('path','')); sha=pkg.get('sha256','')
    if not path.is_file(): errors.append('package-missing:'+str(path))
    elif hashlib.sha256(path.read_bytes()).hexdigest()!=sha: errors.append('package-hash-drift')
if errors:
    print('STATE_DRIFT');print('\n'.join(errors));raise SystemExit(1)
print('RUNTIME_STATE_CHECK_PASS','state_version='+str(sv),'state_kind='+rr['state_kind'],'implement='+impl_head,'review='+review_head,'dirty='+str(len(actual_dirty)))
