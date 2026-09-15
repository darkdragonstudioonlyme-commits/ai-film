"""Network transport and protected I/O are simulated; no external calls."""
from copy import deepcopy
from contextlib import contextmanager
from types import SimpleNamespace
from pathlib import Path
import subprocess
import sys
import unittest
from aifilm_p00.codec import canonical,sha256
from aifilm_p00.network_probe import measure,endpoint
from aifilm_p00.errors import P00Error
from aifilm_p00.native.snapshot import strict_safe_scan,SnapshotReader,NativeBundlePublisher
from aifilm_p00.evidence import assemble,Sanitizer,Bundle
from helpers import collected

ROOT=Path(__file__).resolve().parents[1]
class Clock:
    def __init__(self):self.t=0
    def now(self):return self.t
    def sleep(self,n):self.t+=n
class Transport:
    def __init__(self,results,clock,duration=0):self.results=list(results);self.calls=[];self.clock=clock;self.duration=duration
    def attempt(self,spec,url,deadline,clock):
        self.calls.append((url,deadline));self.clock.t+=min(self.duration,deadline-self.clock.t)
        result=self.results.pop(0)
        if isinstance(result,Exception):raise result
        return result

def spec():return {'endpoint_id':'ubuntu','url':'https://example.invalid/InRelease','context':'GUEST','proxy_mode':'DIRECT',
                   'expected_status':200,'body_prefix_hex':b'PGP'.hex(),'maximum_bytes':1000,'redirect_allowlist':[]}
class NetworkTests(unittest.TestCase):
    def reject(self,code,fn,*args):
        with self.assertRaises(P00Error) as e:fn(*args)
        self.assertEqual(int(e.exception.code),code)
    def test_https_required(self):
        s=spec();s['url']='http://example.invalid';self.reject(10,endpoint,s)
    def test_no_userinfo(self):
        s=spec();s['url']='https://u:secret@example.invalid';self.reject(10,endpoint,s)
    def test_no_non443_port(self):
        s=spec();s['url']='https://example.invalid:1234';self.reject(10,endpoint,s)
    def test_query_not_echoed(self):
        s=spec();s['url']+='?credential=CANARY';c=Clock();t=Transport([{'dns':True}],c)
        r=measure(s,transport=t,clock=c.now,sleep=c.sleep);self.assertNotIn('CANARY',str(r))
    def test_proxy_not_silently_bypassed(self):
        s=spec();s['proxy_mode']='SYSTEM_PROXY';self.reject(11,endpoint,s)
    def test_invalid_port(self):
        s=spec();s['url']='https://example.invalid:evil';self.reject(10,endpoint,s)
    def test_newline_url(self):
        s=spec();s['url']='https://example.invalid/\nInjected';self.reject(10,endpoint,s)
    def test_retry_two_then_success(self):
        c=Clock();t=Transport([P00Error(14,'DNS_FAILURE'),P00Error(14,'TLS_FAILURE'),{'https':True}],c)
        r=measure(spec(),transport=t,clock=c.now,sleep=c.sleep)
        self.assertEqual(r['attempts'],3);self.assertEqual(c.t,7);self.assertEqual(r['context'],'GUEST');self.assertFalse(r['host_ready'])
    def test_collector_budget_caps_attempts(self):
        c=Clock();t=Transport([P00Error(14,'NETWORK_DEADLINE')]*3,c,10)
        r=measure(spec(),transport=t,clock=c.now,sleep=c.sleep)
        self.assertEqual(c.t,30);self.assertEqual(r['status'],'FAIL');self.assertEqual(r['duration_ms'],30000)
    def test_no_automatic_redirect(self):
        c=Clock();t=Transport([{'redirect':'https://evil.invalid'}]*3,c)
        r=measure(spec(),transport=t,clock=c.now,sleep=c.sleep)
        self.assertEqual(r['status'],'FAIL');self.assertEqual(len(t.calls),3)
    def test_exact_redirect_allowed(self):
        s=spec();s['redirect_allowlist']=['https://cdn.invalid/file'];c=Clock()
        t=Transport([{'redirect':'https://cdn.invalid/file'},{'https':True}],c)
        r=measure(s,transport=t,clock=c.now,sleep=c.sleep);self.assertEqual(r['status'],'OBSERVED');self.assertEqual(len(t.calls),2)
    def test_loop_blocked(self):
        s=spec();s['redirect_allowlist']=[s['url']];c=Clock();t=Transport([{'redirect':s['url']}]*3,c)
        self.assertEqual(measure(s,transport=t,clock=c.now,sleep=c.sleep)['status'],'FAIL')
    def test_non_network_error_not_retried(self):
        c=Clock();t=Transport([P00Error(10,'URL_SYNTAX')],c)
        with self.assertRaises(P00Error):measure(spec(),transport=t,clock=c.now,sleep=c.sleep)
        self.assertEqual(len(t.calls),1)

class ScanTests(unittest.TestCase):
    def record(self):return Sanitizer(b's'*16).record(collected('E00-10').record)
    def test_safe_structure(self):self.assertTrue(strict_safe_scan(canonical(self.record())))
    def test_raw_sid_rejected(self):
        r=self.record();r['host_alias']='S-1-5-18';self.assertFalse(strict_safe_scan(canonical(r)))
    def test_raw_url_rejected(self):
        r=self.record();r['summary']={'url':'https://user:password@example.invalid'};self.assertFalse(strict_safe_scan(canonical(r)))
    def test_unknown_field_rejected(self):
        r=self.record();r['secret']='CANARY';self.assertFalse(strict_safe_scan(canonical(r)))
    def test_nested_encoded_data_rejected(self):
        r=self.record();r['summary']={'errors':[{'message':'c2VjcmV0'}]};self.assertFalse(strict_safe_scan(canonical(r)))
    def test_redacted_message_allowed(self):
        r=self.record();r['summary']={'errors':[{'message':'[REDACTED]'}]};self.assertTrue(strict_safe_scan(canonical(r)))
    def test_unparsed_bytes_rejected(self):self.assertFalse(strict_safe_scan(b'raw CANARY'))
    def test_real_scan_bundle_component(self):
        b=assemble('FAILED_RUN',[collected('E00-10')],Sanitizer(b'x'*16),context={},scanner=strict_safe_scan)
        self.assertEqual(b.exit,0);self.assertIsNotNone(b.archive);self.assertFalse(b.component_eligible)

class PublishedPaths:
    def __init__(self,fail=None):self.writes=[];self.fail=fail;self.existing=set()
    def file_exists(self,path):return path in self.existing
    def publish_new(self,path,data,*,pending_path):
        if self.fail:raise self.fail
        self.writes.append((path,data,pending_path))
class PublisherTests(unittest.TestCase):
    def setup(self,fail=None):
        from test_session_integration import Storage
        c=SimpleNamespace(held=True,admission=SimpleNamespace(purpose='SUPPORT_BUNDLE',plan_digest=sha256(b'synthetic-plan')),
            fence={'action':'PUBLISH_SAFE_BUNDLE'},storage=Storage())
        p=PublishedPaths(fail);return p,NativeBundlePublisher(p,c)
    def publish(self,p,b,path=r'C:\Evidence\bundle.zip'):
        return p.publish(b,approved_path=path,budgets=[{'volume_id':'v','roles':['EVIDENCE'],'allocations':{'output':1000000}}],free_by_volume={'v':10*1024**3})
    def bundle(self):return assemble('FAILED_RUN',[collected('E00-10')],Sanitizer(b'x'*16),context={},scanner=strict_safe_scan)
    def test_safe_publish(self):
        paths,p=self.setup();r=self.publish(p,self.bundle());self.assertTrue(r['published']);self.assertFalse(r['host_ready']);self.assertEqual(len(paths.writes),1)
    def test_output_failure_maps18(self):
        paths,p=self.setup(P00Error(18,'OUTPUT_PUBLISH'));r=self.publish(p,self.bundle());self.assertEqual(r['exit'],18);self.assertFalse(r['published'])
    def test_privacy_does_not_write(self):
        paths,p=self.setup();b=Bundle(23,'BLOCKED_REDACTION',False,False,None,{})
        r=self.publish(p,b);self.assertEqual(r['exit'],23);self.assertEqual(paths.writes,[])
    def test_no_archive_rejects_preexisting_final_without_delete(self):
        paths,p=self.setup();path=r'C:\Evidence\bundle.zip';paths.existing.add(path)
        b=Bundle(23,'BLOCKED_REDACTION',False,False,None,{})
        with self.assertRaises(P00Error) as cm:self.publish(p,b,path)
        self.assertEqual(int(cm.exception.code),16);self.assertIn(path,paths.existing);self.assertEqual(paths.writes,[])
    def test_incomplete_suffix_required(self):
        paths,p=self.setup();b=assemble('FAILED_RUN',[],Sanitizer(b'x'*16),context={},scanner=strict_safe_scan)
        with self.assertRaises(P00Error):self.publish(p,b)
        self.assertEqual(paths.writes,[])
    def test_incomplete_marked_filename(self):
        paths,p=self.setup();b=assemble('FAILED_RUN',[],Sanitizer(b'x'*16),context={},scanner=strict_safe_scan)
        self.assertEqual(self.publish(p,b,r'C:\Evidence\bundle.incomplete.zip')['exit'],22)
    def test_wrong_authority_blocks(self):
        paths,p=self.setup();p.coordinator.admission.purpose='CREATE'
        with self.assertRaises(P00Error):self.publish(p,self.bundle())
        self.assertEqual(paths.writes,[])

class HarnessBoundaryTests(unittest.TestCase):
    def test_list_not_execution(self):
        p=subprocess.run([sys.executable,str(ROOT/'tools/run_native_foundation_tests.py'),'--list'],capture_output=True,timeout=10)
        self.assertEqual(p.returncode,0);self.assertIn(b'NOT_RUN',p.stdout);self.assertNotIn(b'"actual_status": "PASS"',p.stdout)
    def test_native_case_blocked_before_windows_api(self):
        p=subprocess.run([sys.executable,str(ROOT/'tools/run_native_foundation_tests.py'),'--case','NF-IDENTITY'],capture_output=True,timeout=10)
        self.assertEqual(p.returncode,11);self.assertIn(b'WINDOWS_X64_REQUIRED',p.stdout)
