#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]

def executable(path,body):
    path.write_text(body); os.chmod(path,0o755)

def prepare(base):
    tool=base/'tool'; tool.mkdir(); root=base/'evidence'; root.mkdir(); inbox=base/'inbox'; inbox.mkdir()
    interop=base/'private-windows-interop.sh'
    script=(SOURCE/'pre-v03-authority-stage.sh').read_text()
    script=script.replace('ROOT=/home/dragon/ai-film-dev/run-evidence/validation/v02-authority-dev22',f'ROOT={root}')
    script=script.replace('INBOX=/mnt/c/Users/Admin/AppData/Local/AI-FILM/LAB/authority-approved/dev22',f'INBOX={inbox}')
    script=script.replace('/home/dragon/ai-film-dev/root-ops/private-windows-interop.sh',str(interop))
    stage=tool/'pre-v03-authority-stage.sh'; stage.write_text(script); os.chmod(stage,0o755)
    return tool,root,interop

def run(stage): return subprocess.run([str(stage)],text=True,capture_output=True)

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); tool,root,interop=prepare(base); stage=tool/'pre-v03-authority-stage.sh'
        policy=root/'native-policy.candidate.json'

        executable(tool/'v02-authority-intake.py',"#!/usr/bin/env bash\necho '{\"status\":\"BLOCKED\"}'\nexit 12\n")
        executable(tool/'verify-lab-artifact-seal.py',"#!/usr/bin/env bash\necho seal\n")
        executable(tool/'materialize-v02-native-policy.py',"#!/usr/bin/env bash\nexit 99\n")
        executable(interop,"#!/usr/bin/env bash\necho 'AI-FILM-P00-LAB Stopped 2'\n")
        policy.write_text('stale\n'); p=run(stage)
        assert p.returncode==12 and not policy.exists() and 'BLOCKED_AUTHORITY' in p.stdout
        print('PASS blocked_authority_removes_stale_policy')

        executable(tool/'v02-authority-intake.py',"#!/usr/bin/env bash\necho '{\"status\":\"READY_TO_ADVANCE\"}'\nexit 0\n")
        executable(tool/'verify-lab-artifact-seal.py',"#!/usr/bin/env bash\nexit 1\n")
        policy.write_text('stale\n'); p=run(stage)
        assert p.returncode!=0 and not policy.exists()
        print('PASS seal_failure_removes_stale_policy')

        executable(tool/'verify-lab-artifact-seal.py',"#!/usr/bin/env bash\necho seal\n")
        executable(tool/'materialize-v02-native-policy.py',f"#!/usr/bin/env bash\necho candidate > {policy}\necho blocked\nexit 12\n")
        p=run(stage)
        assert p.returncode==12 and not policy.exists() and 'BLOCKED_POLICY' in p.stdout
        print('PASS materializer_failure_removes_partial_policy')

        executable(tool/'materialize-v02-native-policy.py',f"#!/usr/bin/env bash\necho candidate > {policy}\necho ready\nexit 0\n")
        executable(interop,"#!/usr/bin/env bash\necho 'AI-FILM-P00-LAB Running 2'\n")
        p=run(stage)
        assert p.returncode==12 and not policy.exists() and 'LAB_NOT_STOPPED' in p.stdout
        print('PASS lab_running_removes_policy')

        executable(interop,"#!/usr/bin/env bash\necho 'AI-FILM-P00-LAB Stopped 2'\n")
        p=run(stage)
        assert p.returncode==0 and policy.is_file() and 'READY_FOR_LOCAL_NATIVE_POLICY_REVIEW' in p.stdout
        print('PASS success_preserves_current_policy')
    print('V02_PRE_V03_FAILCLOSED_TEST_PASS 5 cases')

if __name__=='__main__': main()
