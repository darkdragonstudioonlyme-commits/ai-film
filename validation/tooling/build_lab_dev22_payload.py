#!/usr/bin/env python3
"""Build a deterministic exact-app payload for the disposable dev22 LAB.

This tool packages only the immutable application tree from an already-audited
prodlike dev22 release. It never copies a host venv and never executes native
cases.
"""
import argparse,hashlib,json,os,subprocess,sys,tarfile
from pathlib import Path

EXPECTED={
    "release_name":"dev22",
    "implementation_version":"0.1.0.dev22",
    "source_commit":"86bb64938a136e3f8d6cfd0266685a01cb832b77",
    "source_digest":"69fdc1840472a96bce8f8841e4d780543827e3cefdd3fe3bc8445f8a1fb4a0d6",
    "test_digest":"47d4ae767b26b05ef16d6809ea9377ef4e1b21bfbc4c44093dbd1cc158b75698",
    "contract_digest":"f259656c48ed24c15bd48da2bb040950ed94d8edcf1473cf6456b96578c933ee",
    "package_sha256":"c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae",
    "wheel_sha256":"e5a7ae51c73e5e9bea1e9d62c2220d2f39133a2bd74f73ccf97c38d75019147f",
    "app_file_count":284,
}
EXPECTED_APP_MANIFEST_SHA256="8f31bb6359387257f00388e12f05e2cb6014867ebb90295d1684d3b6fab00471"

def sha_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def safe_rel(name):
    p=Path(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts and "\\" not in name

def parse_manifest(path):
    rows={}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        digest,name=line.split(None,1); name=name.strip().lstrip("*")
        if not safe_rel(name) or name in rows: raise RuntimeError("app-manifest-path")
        if len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest): raise RuntimeError("app-manifest-digest")
        rows[name]=digest
    return rows

def build_tar(app,rows,out):
    app=Path(app);out=Path(out)
    with tarfile.open(out,"w",format=tarfile.GNU_FORMAT) as tf:
        for name in sorted(rows):
            p=app/name
            if not p.is_file() or p.is_symlink(): raise RuntimeError("app-member:"+name)
            raw=p.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=rows[name]: raise RuntimeError("app-byte-drift:"+name)
            ti=tarfile.TarInfo(name)
            ti.size=len(raw);ti.mode=0o444;ti.uid=0;ti.gid=0;ti.uname="root";ti.gname="root";ti.mtime=0
            import io
            tf.addfile(ti,io.BytesIO(raw))
    return sha_file(out)

def verify_tar(path,rows):
    with tarfile.open(path,"r") as tf:
        members=tf.getmembers()
        if len(members)!=len(rows) or {m.name for m in members}!=set(rows): raise RuntimeError("tar-member-set")
        for m in members:
            if not m.isfile() or m.mode!=0o444 or m.uid!=0 or m.gid!=0 or m.mtime!=0: raise RuntimeError("tar-metadata:"+m.name)
            f=tf.extractfile(m)
            raw=f.read() if f else b""
            if hashlib.sha256(raw).hexdigest()!=rows[m.name]: raise RuntimeError("tar-byte-drift:"+m.name)
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--release-root",required=True);ap.add_argument("--output",required=True)
    a=ap.parse_args();root=Path(a.release_root);out=Path(a.output)
    if out.exists(): raise RuntimeError("output-exists")
    manifest=json.loads((root/"runtime-manifest.json").read_text(encoding="utf-8"))
    for key,want in EXPECTED.items():
        if manifest.get(key)!=want: raise RuntimeError("runtime-manifest:"+key)
    if manifest.get("native_lab_authority") is not False or manifest.get("native_execution_started") is not False:
        raise RuntimeError("native-boundary")
    app_manifest=root/"app-manifest.sha256"
    if sha_file(app_manifest)!=EXPECTED_APP_MANIFEST_SHA256: raise RuntimeError("app-manifest-identity")
    rows=parse_manifest(app_manifest)
    if len(rows)!=EXPECTED["app_file_count"]: raise RuntimeError("app-file-count")
    app=root/"app"
    if {p.relative_to(app).as_posix() for p in app.rglob("*") if p.is_file()}!=set(rows): raise RuntimeError("app-member-set")
    p=subprocess.run([str(root/"bin/verify-runtime")],text=True,capture_output=True)
    if p.returncode or "PRODLIKE_RUNTIME_VERIFY_PASS 284 86 NOT_RUN release=dev22" not in p.stdout:
        raise RuntimeError("source-release-verify")
    out.mkdir(mode=0o700)
    tar=out/"AI-FILM-P00-DEV22_APP.tar"
    tar_sha=build_tar(app,rows,tar);verify_tar(tar,rows)
    target_manifest=out/"AI-FILM-P00-DEV22_APP.sha256"
    target_manifest.write_bytes(app_manifest.read_bytes())
    meta={
        "schema_version":1,"kind":"P00_LAB_DEV22_APP_PAYLOAD","candidate_id":"6f895394-e0b4-5434-bebc-79ee4e576282",
        "candidate_binding_sha256":"4aaf09ec2ef8618a5680e147cd2eeac695f940d45ae5cb0446c7b7e5c2483384",
        **EXPECTED,"app_manifest_sha256":sha_file(target_manifest),"app_tar_sha256":tar_sha,"app_tar_bytes":tar.stat().st_size,
        "target_root":"/opt/ai-film-lab/runtime/dev22","native_execution_started":False,
    }
    mp=out/"LAB_DEV22_PAYLOAD_MANIFEST.json";mp.write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    for pth in (tar,target_manifest,mp): os.chmod(pth,0o444)
    print(json.dumps({"kind":"P00_LAB_DEV22_PAYLOAD_BUILD","status":"PASS","app_files":len(rows),
        "app_tar_sha256":tar_sha,"app_manifest_sha256":meta["app_manifest_sha256"],"native_execution_started":False},
        sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    try: main()
    except Exception as e:
        print("P00_LAB_DEV22_PAYLOAD_BUILD_FAIL "+str(e),file=sys.stderr);raise SystemExit(1)
