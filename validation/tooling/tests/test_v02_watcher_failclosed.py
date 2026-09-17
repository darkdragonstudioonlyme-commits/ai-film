#!/usr/bin/env python3
import hashlib, os, shutil, subprocess, tempfile
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]

def prepare(base):
    tool=base/'tool'; tool.mkdir(); out=base/'out'; inbox=base/'inbox'; inbox.mkdir()
    script=(SOURCE/'watch-v02-authority.sh').read_text()
    script=script.replace('OUT=/home/dragon/ai-film-dev/run-evidence/validation/v02-authority',f'OUT={out}')
    script=script.replace('INBOX=/mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev21',f'INBOX={inbox}')
    (tool/'watch-v02-authority.sh').write_text(script); os.chmod(tool/'watch-v02-authority.sh',0o755)
    return tool,out

def validator(tool,body,rc):
    p=tool/'v02-authority-intake.py'
    p.write_text('#!/usr/bin/env bash\n'+f"printf '%s\\n' '{body}'\nexit {rc}\n");os.chmod(p,0o755)

def run(tool): return subprocess.run([str(tool/'watch-v02-authority.sh')],text=True,capture_output=True)

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td);tool,out=prepare(base);flag=out/'READY_TO_ADVANCE.flag';out.mkdir()
        flag.write_text('stale\n'); validator(tool,'not-json',1); p=run(tool)
        assert p.returncode==1 and not flag.exists() and 'status=UNREADABLE' in p.stderr
        print('PASS crash_or_nonjson_removes_stale_ready')

        flag.write_text('stale\n');validator(tool,'{"status":"BLOCKED"}',12);p=run(tool)
        assert p.returncode==0 and not flag.exists() and 'V02_AUTHORITY_WATCH_BLOCKED' in p.stdout
        print('PASS blocked_removes_stale_ready')

        validator(tool,'{"status":"READY_TO_ADVANCE"}',0);p=run(tool)
        assert p.returncode==0 and flag.is_file() and 'V02_AUTHORITY_WATCH_READY_OPERATOR_ACTION_REQUIRED' in p.stdout
        want=hashlib.sha256((out/'latest.json').read_bytes()).hexdigest();assert flag.read_text().strip()==want
        print('PASS ready_recreates_current_evidence_bound_flag')
    print('V02_WATCHER_FAILCLOSED_TEST_PASS 3 cases')

if __name__=='__main__': main()
