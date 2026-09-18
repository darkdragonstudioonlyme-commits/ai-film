#!/usr/bin/env python3
import hashlib,importlib.util,json,stat,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("lab_payload",ROOT/"build_lab_dev22_payload.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);app=td/"app";app.mkdir()
        rows={}
        for i in range(7):
            p=app/f"d{i%3}/f{i:02d}.txt";p.parent.mkdir(parents=True,exist_ok=True)
            raw=(f"payload-{i}\n").encode();p.write_bytes(raw);rows[p.relative_to(app).as_posix()]=hashlib.sha256(raw).hexdigest()
        a=td/"a.tar";b=td/"b.tar"
        m.build_tar(app,rows,a);m.build_tar(app,rows,b)
        assert h(a)==h(b)
        assert m.verify_tar(a,rows)
        with tarfile.open(a) as tf:
            assert [x.name for x in tf.getmembers()]==sorted(rows)
            assert all(x.mode==0o444 and x.uid==0 and x.gid==0 and x.mtime==0 for x in tf.getmembers())
        # Byte drift must fail before packaging.
        victim=app/sorted(rows)[0];victim.write_bytes(b"drift")
        try:m.build_tar(app,rows,td/"bad.tar")
        except RuntimeError as e: assert str(e).startswith("app-byte-drift:")
        else: raise AssertionError("drift accepted")
        for bad in ("../x","/abs","a\\b"):
            assert not m.safe_rel(bad)
    print("LAB_DEV22_PAYLOAD_BUILDER_TEST_PASS")
if __name__=="__main__": main()
