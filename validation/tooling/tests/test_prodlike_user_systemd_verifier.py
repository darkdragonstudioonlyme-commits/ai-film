#!/usr/bin/env python3
import hashlib,json,subprocess,sys,tarfile,tempfile
from pathlib import Path
TOOL=Path(__file__).resolve().parents[1]/'verify_prodlike_user_systemd.py'

def h(b): return hashlib.sha256(b).hexdigest()
def build(root, mutate_archive=False):
    files={
      'systemd/aifilm-p00-a.service':b'[Service]\nType=oneshot\nExecStart=/bin/true\n',
      'systemd/aifilm-p00-a.timer':b'[Timer]\nOnBootSec=1m\n',
      'systemd/dropins/aifilm-p00-a.service/resources.conf':b'[Service]\nMemoryMax=1G\n',
    }
    manifest={'files':{k:{'sha256':h(v),'size':len(v)} for k,v in files.items()}}
    arc=root/'control.tar.gz'
    with tarfile.open(arc,'w:gz') as tf:
        data=json.dumps(manifest).encode(); ti=tarfile.TarInfo('backup-manifest.json');ti.size=len(data);tf.addfile(ti,io(data))
        for k,v in files.items():
            actual=(b'X'+v[1:]) if mutate_archive and k.endswith('.timer') else v
            ti=tarfile.TarInfo(k);ti.size=len(actual);tf.addfile(ti,io(actual))
    u=root/'user'; u.mkdir()
    for k,v in files.items():
        parts=Path(k).parts
        if parts[1]=='dropins': p=u/(parts[2]+'.d')/Path(*parts[3:])
        else: p=u/Path(*parts[1:])
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
    return arc,u,files

def io(b): import io as _io; return _io.BytesIO(b)
def run(arc,u): return subprocess.run([sys.executable,str(TOOL),'--backup-archive',str(arc),'--unit-dir',str(u)],text=True,capture_output=True)
def expect(name,mut,rc,reason=None, archive_mut=False):
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);arc,u,files=build(root,archive_mut);mut(u,files);r=run(arc,u)
        assert r.returncode==rc,(name,r.returncode,r.stdout,r.stderr)
        x=json.loads(r.stdout);assert x['status']==('PASS' if rc==0 else 'FAIL')
        if reason: assert x['reason']==reason,(name,x)
        print('PASS',name)
expect('valid',lambda u,f:None,0)
expect('missing',lambda u,f:(u/'aifilm-p00-a.service').unlink(),1,'DEPLOYED_SYSTEMD_DRIFT')
expect('content-drift',lambda u,f:(u/'aifilm-p00-a.timer').write_text('drift\n'),1,'DEPLOYED_SYSTEMD_DRIFT')
expect('dropin-missing',lambda u,f:(u/'aifilm-p00-a.service.d/resources.conf').unlink(),1,'DEPLOYED_SYSTEMD_DRIFT')
expect('archive-drift',lambda u,f:None,1,'ARCHIVE_MEMBER_DRIFT:systemd/aifilm-p00-a.timer',archive_mut=True)
print('PRODLIKE_USER_SYSTEMD_VERIFIER_TEST_PASS 5 cases')
