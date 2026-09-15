#!/usr/bin/python3
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--root',default='/home/dragon/ai-film-dev');parser.add_argument('--check',action='store_true');args=parser.parse_args();root=Path(args.root)
expected='#!/usr/bin/env bash\nset -euo pipefail\n'+f'exec /usr/bin/python3 {root}/repo/tools/run_test_workflow.py implement\n';path=root/'test.sh'
if not root.is_dir(): print('WORKSPACE_HELPER_SYNC_SKIPPED workspace unavailable');raise SystemExit(0)
if args.check:
    actual=path.read_text(encoding='utf-8') if path.is_file() else None
    if actual!=expected: print('WORKSPACE_HELPER_DRIFT test.sh');raise SystemExit(1)
    print('WORKSPACE_HELPER_CHECK_PASS');raise SystemExit(0)
path.write_text(expected,encoding='utf-8');path.chmod(0o755);print('WORKSPACE_HELPER_SYNCED',path)
