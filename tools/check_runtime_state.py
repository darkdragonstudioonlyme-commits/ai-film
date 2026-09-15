#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
WS=Path('/home/dragon/ai-film-dev'); REPO=WS/'repo'; errors=[]

def run(*args,strip=True):
    value=subprocess.check_output(args,text=True)
    return value.strip() if strip else value

def latest_state_json():
    rows=[]
    for p in ROOT.glob('AI_FILM_PROJECT_STATE_V*.json'):
        m=re.fullmatch(r'AI_FILM_PROJECT_STATE_V(\d+)\.json',p.name)
        if m: rows.append((int(m.group(1)),p))
    if not rows: raise SystemExit('RUNTIME_STATE_CHECK_NO_STATE_JSON')
    version,path=max(rows)
    return version,path,json.loads(path.read_text(encoding='utf-8'))

if not REPO.is_dir() or not (WS/'implement').is_dir() or not (WS/'review').is_dir():
    print('RUNTIME_STATE_CHECK_SKIPPED prepared WSL workspace unavailable'); raise SystemExit(0)
subprocess.check_call(['git','-C',str(REPO),'fetch','origin','main','lane/implement-p00','lane/review-p00'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
version,state_path,state=latest_state_json(); md=(ROOT/'PROJECT_STATE.md').read_text(encoding='utf-8')
if state.get('project')!='AI-FILM-SERVER': errors.append('state-project')
if state.get('current_mode')!='IMPLEMENTATION': errors.append('state-mode')
if state.get('state_version')!=version: errors.append(f'state-json-version:{state.get("state_version")}!={version}')
mm=re.search(r'STATE_VERSION:\s*(\d+)',md)
if not mm or int(mm.group(1))!=version: errors.append('state-markdown-version-drift')
docsys=state.get('documentation_system')
if isinstance(docsys,dict): docsys=docsys.get('release_id') or docsys.get('version')
if docsys not in ('DOCSYS-V2-R6','V2'): errors.append('documentation-system-v2')

def commit_from(obj,*keys):
    if not isinstance(obj,dict): return None
    for k in keys:
        v=obj.get(k)
        if isinstance(v,str) and re.fullmatch(r'[0-9a-f]{40}',v): return v
    return None
wip=state.get('implementation_wip') or {}
last=state.get('last_reviewed_candidate') or state.get('last_durable_implementation') or {}
current=state.get('current_review_candidate') or {}
impl_expected=commit_from(wip,'base_commit') or commit_from(current,'source_commit') or commit_from(last,'source_commit')
review_expected=commit_from(current,'source_commit') or commit_from(last,'source_commit') or impl_expected
if not impl_expected:
    m=re.search(r'INPUT_COMMIT:\s*([0-9a-f]{40})',md); impl_expected=m.group(1) if m else None
if not review_expected: review_expected=impl_expected
if not impl_expected: errors.append('state-source-identity-missing')

impl_head=run('git','-C',str(WS/'implement'),'rev-parse','HEAD')
review_head=run('git','-C',str(WS/'review'),'rev-parse','HEAD')
if impl_expected and impl_head!=impl_expected: errors.append(f'implement-head:{impl_head}!={impl_expected}')
if review_expected and review_head!=review_expected: errors.append(f'review-head:{review_head}!={review_expected}')

porcelain=run('git','-C',str(WS/'implement'),'status','--porcelain',strip=False).splitlines()
actual_dirty={line[3:] for line in porcelain if len(line)>=4}
block=re.search(r'DIRTY_FILES:\n((?:\s+- .+\n)+)',md)
if block:
    expected_dirty={line.strip()[2:] for line in block.group(1).splitlines()}
    if actual_dirty!=expected_dirty: errors.append(f'dirty-set:{sorted(actual_dirty)}!={sorted(expected_dirty)}')
else:
    if actual_dirty: errors.append(f'undocumented-dirty-set:{sorted(actual_dirty)}')

impl_lane=run('git','-C',str(REPO),'show','origin/lane/implement-p00:LANE_STATE.md')
review_lane=run('git','-C',str(REPO),'show','origin/lane/review-p00:LANE_STATE.md')
if impl_expected and impl_expected not in impl_lane: errors.append('implement-lane-source-drift')
if review_expected and review_expected not in review_lane: errors.append('review-lane-source-drift')

version_name=last.get('version') if isinstance(last,dict) else None
package_hash=last.get('package_sha256') if isinstance(last,dict) else None
if version_name and package_hash and re.fullmatch(r'0\.1\.0\.dev(\d+)',version_name):
    n=re.fullmatch(r'0\.1\.0\.dev(\d+)',version_name).group(1)
    pkg=WS/'artifacts'/f'IMPL-P00-001_IMPLEMENTATION_PACKAGE_V{n}.zip'
    if pkg.is_file():
        if hashlib.sha256(pkg.read_bytes()).hexdigest()!=package_hash: errors.append('durable-package-drift')
    elif 'LOCAL_WSL_PACKAGE_VERIFIED: true' in md or 'local_wsl_package_verified' in json.dumps(state).lower():
        errors.append('durable-package-missing')

if errors:
    print('STATE_DRIFT'); print('\n'.join(errors)); raise SystemExit(1)
print('RUNTIME_STATE_CHECK_PASS',f'state=V{version}',f'impl={impl_expected}',f'review={review_expected}',f'dirty={len(actual_dirty)}')
