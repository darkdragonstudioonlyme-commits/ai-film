"""Author static checks only: parse Python/JSON, sh -n; NEVER execute guest code."""
import ast
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = []
    for folder in ('src', 'tests', 'tools', 'native'):
        for path in sorted((ROOT / folder).rglob('*.py')):
            ast.parse(path.read_text(encoding='utf-8'), filename=path.name)
            rows.append({'path': path.relative_to(ROOT).as_posix(), 'check': 'PYTHON_AST', 'status': 'PASS'})
    for folder in ('schemas', 'config'):
        for path in sorted((ROOT / folder).glob('*.json')):
            json.loads(path.read_text(encoding='utf-8'))
            rows.append({'path': path.relative_to(ROOT).as_posix(), 'check': 'JSON_PARSE', 'status': 'PASS'})
    if os.name == 'posix':
        check = subprocess.run(['/bin/sh', '-n', str(ROOT / 'native/guest-observe.sh')],
                               capture_output=True, timeout=10, check=False)
        rows.append({'path': 'native/guest-observe.sh', 'check': 'SHELL_SYNTAX_ONLY',
                     'status': 'PASS' if check.returncode == 0 else 'FAIL', 'script_executed': False})
    else:
        rows.append({'path': 'native/guest-observe.sh', 'check': 'SHELL_SYNTAX_ONLY', 'status': 'NOT_RUN'})
    report = {'kind': 'AUTHOR_STATIC_CHECKS', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'checks': rows, 'powershell_parse': 'NOT_RUN', 'powershell_execution': 'NOT_RUN',
              'windows_native': 'NOT_RUN', 'guest_script_execution': 'NOT_RUN',
              'code_review_verdict': None, 'qualification_issued': False}
    (ROOT / 'evidence/AUTHOR_STATIC_CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'checks': len(rows), 'failed': sum(r['status'] == 'FAIL' for r in rows)}))
    return 1 if any(r['status'] == 'FAIL' for r in rows) else 0


if __name__ == '__main__':
    raise SystemExit(main())
