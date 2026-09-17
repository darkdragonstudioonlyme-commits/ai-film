#!/usr/bin/env python3
import json, os, shutil, subprocess, tempfile
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); tool=base/'tool'; tool.mkdir(); inbox=base/'inbox'; inbox.mkdir()
        shutil.copy2(SOURCE/'v02-authority-preflight.py',tool/'v02-authority-preflight.py')
        payload=inbox/'payload.json'; payload.write_bytes(b'AAAA\n')
        validator=tool/'v02-authority-intake.py'
        validator.write_text("""#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--inbox')+1])
p=root/'payload.json'; st=p.stat()
p.write_bytes(b'BBBB\\n')
os.utime(p,ns=(st.st_atime_ns,st.st_mtime_ns))
print(json.dumps({'status':'BLOCKED','reason':'SYNTHETIC_MUTATION'},sort_keys=True,separators=(',',':')))
raise SystemExit(12)
""")
        os.chmod(validator,0o755)
        p=subprocess.run([str(tool/'v02-authority-preflight.py'),'--inbox',str(inbox),'--json'],
                         text=True,capture_output=True)
        data=json.loads((p.stdout.strip().splitlines() or ['{}'])[-1])
        assert p.returncode==3,(p.returncode,p.stdout,p.stderr)
        assert data.get('status')=='FAIL' and data.get('reason')=='PREFLIGHT_MUTATED_STAGING',data
        assert data.get('ready_for_intake') is False and data.get('native_execution_started') is False
        assert payload.read_bytes()==b'BBBB\n'
        print('PASS same_size_same_mtime_content_mutation_detected')
    print('V02_PREFLIGHT_CONTENT_INTEGRITY_TEST_PASS 1 case')

if __name__=='__main__': main()
