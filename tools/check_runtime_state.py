#!/usr/bin/env python3
from pathlib import Path
import subprocess, re, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
WS=Path('/home/dragon/ai-film-dev')
REPO=WS/'repo'
errors=[]

def run(*args,strip=True):
    value=subprocess.check_output(args,text=True)
    return value.strip() if strip else value

if not REPO.is_dir() or not (WS/'implement').is_dir() or not (WS/'review').is_dir():
    print('RUNTIME_STATE_CHECK_SKIPPED prepared WSL workspace unavailable')
    raise SystemExit(0)
subprocess.check_call(['git','-C',str(REPO),'fetch','origin','main','lane/implement-p00','lane/review-p00'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
state=(ROOT/'PROJECT_STATE.md').read_text(encoding='utf-8')

def grab(pattern):
    m=re.search(pattern,state)
    if not m: errors.append('state-pattern:'+pattern);return None
    return m.group(1)
base=grab(r'BASE_COMMIT: ([0-9a-f]{40})')
review_target=grab(r'TARGET_COMMIT: ([0-9a-f]{40})')
planned=grab(r'PLANNED_VERSION: (0\.1\.0\.dev\d+)')
pkg_path=grab(r'PACKAGE_PATH: (.+)')
pkg_hash=grab(r'PACKAGE_SHA256: ([0-9a-f]{64})')
impl_head=run('git','-C',str(WS/'implement'),'rev-parse','HEAD')
review_head=run('git','-C',str(WS/'review'),'rev-parse','HEAD')
if base and impl_head!=base: errors.append(f'implement-head:{impl_head}!={base}')
if review_target and review_head!=review_target: errors.append(f'review-head:{review_head}!={review_target}')
porcelain=run('git','-C',str(WS/'implement'),'status','--porcelain',strip=False).splitlines()
actual_dirty={line[3:] for line in porcelain if len(line)>=4}
block=re.search(r'DIRTY_FILES:\n((?:\s+- .+\n)+)',state)
expected_dirty={line.strip()[2:] for line in block.group(1).splitlines()} if block else set()
if actual_dirty!=expected_dirty: errors.append(f'dirty-set:{sorted(actual_dirty)}!={sorted(expected_dirty)}')
impl_lane=run('git','-C',str(REPO),'show','origin/lane/implement-p00:LANE_STATE.md')
review_lane=run('git','-C',str(REPO),'show','origin/lane/review-p00:LANE_STATE.md')
if base and base not in impl_lane: errors.append('implement-lane-base-drift')
if planned and planned not in impl_lane: errors.append('implement-lane-version-drift')
if review_target and review_target not in review_lane: errors.append('review-lane-target-drift')
if pkg_path and pkg_hash:
    pkg=Path(pkg_path)
    if not pkg.is_file() or hashlib.sha256(pkg.read_bytes()).hexdigest()!=pkg_hash:
        errors.append('durable-package-drift')
if errors:
    print('STATE_DRIFT')
    print('\n'.join(errors))
    raise SystemExit(1)
print('RUNTIME_STATE_CHECK_PASS', 'base='+str(base), 'planned='+str(planned), 'review='+str(review_target), 'dirty='+str(len(actual_dirty)))
