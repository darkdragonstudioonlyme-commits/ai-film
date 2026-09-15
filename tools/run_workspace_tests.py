"""Run author tests and record actual results; never issue qualification receipts."""
import hashlib
import json
import os
import platform
import sys
import time
import unittest
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]

def inventory(paths):
    files=[]
    for directory in paths:
        for p in sorted((ROOT/directory).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                data=p.read_bytes(); files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    return files

def dg(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class Result(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.actual=[];self.started={}
    def startTest(self,test):self.started[test.id()]=time.monotonic();super().startTest(test)
    def record(self,test,status,reason=None):
        self.actual.append({'test_id':test.id(),'actual_status':status,'duration_seconds':round(time.monotonic()-self.started.get(test.id(),time.monotonic()),6),'reason':reason,'native_execution':False})
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'FAIL',err[0].__name__)
    def addError(self,test,err):super().addError(test,err);self.record(test,'ERROR',err[0].__name__)
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'SKIP',reason)

def main():
    if os.name!='posix':
        print('This runner currently covers isolated POSIX workspace tests, not native Windows.');return 11
    os.environ['PYTHONPATH']=str(ROOT/'src')
    source=inventory(['src','schemas','config','native']); tests=inventory(['tests','fixtures','tools'])
    start=datetime.now(timezone.utc).isoformat(); tic=time.monotonic()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    out=ROOT/'evidence';out.mkdir(exist_ok=True)
    with (out/'WORKSPACE_TEST_LOG.txt').open('w') as f:
        result=unittest.TextTestRunner(stream=f,verbosity=2,resultclass=Result).run(suite)
    report={'report_kind':'AUTHOR_WORKSPACE_TEST_REPORT','source_kind':'WORKSPACE','environment':{'os':platform.system(),'release':platform.release(),'python':platform.python_version(),'implementation':platform.python_implementation(),'machine':platform.machine()},
        'started_at':start,'ended_at':datetime.now(timezone.utc).isoformat(),'duration_seconds':round(time.monotonic()-tic,6),
        'source_content_digest':dg(source),'test_content_digest':dg(tests),'source_members':source,'test_members':tests,
        'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'successful':result.wasSuccessful(),'actual_results':result.actual,
        'windows_wsl_native':'NOT_RUN','site_tests':'NOT_RUN','code_review':'NOT_PERFORMED','qualification_issued':False,'host_ready':False}
    (out/'WORKSPACE_TEST_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['tests_run','failures','errors','skipped','successful','source_content_digest','test_content_digest']}))
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
