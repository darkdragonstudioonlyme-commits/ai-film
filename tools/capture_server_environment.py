#!/usr/bin/python3
from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,hashlib,os

def cmd(args):
    try:return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:return None

def which(name):return cmd(['sh','-lc','command -v '+name+' || true']) or None
cpu=cmd(['sh','-lc',"lscpu | awk -F: '/^CPU\\(s\\)/{gsub(/^ +/,\"\",$2);print $2;exit}'"])
model=cmd(['sh','-lc',"lscpu | awk -F: '/^Model name/{gsub(/^ +/,\"\",$2);print $2;exit}'"])
mem=cmd(['sh','-lc',"free -b | awk '/^Mem:/{print $2}'"])
disk=cmd(['sh','-lc',"df -B1 /home/dragon | awk 'NR==2{print $2\" \"$4}'"])
gpu=cmd(['sh','-lc','nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader 2>/dev/null || true'])
dxg=Path('/dev/dxg').exists()
env={'kernel':cmd(['uname','-r']),'architecture':cmd(['uname','-m']),'distro':cmd(['sh','-lc','. /etc/os-release; echo "$PRETTY_NAME"']),'cpu_visible':int(cpu) if cpu and cpu.isdigit() else None,'cpu_model':model,'memory_total_bytes':int(mem) if mem and mem.isdigit() else None,'filesystem_home_total_bytes':int(disk.split()[0]) if disk else None,'filesystem_home_free_bytes':int(disk.split()[1]) if disk else None,'dxg_present':dxg,'nvidia_smi_observation':gpu or None,'system_python':cmd(['/usr/bin/python3','--version']),'project_venv_python':cmd(['/home/dragon/ai-film-dev/.venv/bin/python','--version']),'project_venv_pip_present':Path('/home/dragon/ai-film-dev/.venv/bin/pip').exists(),'git':cmd(['git','--version']),'tools':{x:which(x) for x in ['ffmpeg','docker','podman','git-lfs','uv','cmake','gcc','pip3']}}
identity={k:v for k,v in env.items() if k!='filesystem_home_free_bytes'}
raw=json.dumps(identity,sort_keys=True,separators=(',',':')).encode()
out={'schema_version':1,'observed_at':datetime.now(timezone.utc).isoformat(),'environment_class':'WSL_DEVELOPMENT_AUTHORING','environment':env,'fingerprint_basis':'stable_observed_fields_excluding_dynamic_free_capacity','environment_fingerprint_sha256':hashlib.sha256(raw).hexdigest(),'gpu_observed':bool(gpu),'model_evaluation_ready':False}
path=Path(__file__).resolve().parents[1]/'evidence'/'SERVER_ENVIRONMENT_SNAPSHOT.json';path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(path);print(out['environment_fingerprint_sha256'])
