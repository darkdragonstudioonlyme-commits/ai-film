"""Workspace-only fake Win32 reads; no native scripts are run."""
from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace
import unittest

from helpers import B, SID, digest, sha256, canonical
from aifilm_p00.errors import P00Error
from aifilm_p00.native.source_pin import SourcePins
from aifilm_p00.native.guest import GuestTransport
from aifilm_p00.native.coordination import NativeJournal
from test_native_supervision import JournalPaths
from aifilm_p00.native.trust import MetadataPermit
from aifilm_p00.resume import progress_digest, completed_steps
from test_dev4_noop import NoopSessionTests

# Importing a TestCase under an alias still makes unittest rediscover it; delete
# it below after extracting a fixture, so the report contains no duplicate tests.
_setup_noop = NoopSessionTests.setup_case
del NoopSessionTests

class FakePaths:
    def __init__(self,raw):
        self.raw=raw;self.events=[];self.api=SimpleNamespace(read=lambda h,cap:self.raw)
    @contextmanager
    def pin(self,path,**kw):
        self.events.append(('pin',path))
        yield SimpleNamespace(identity={'bytes':len(self.raw)},handle=1)
        self.events.append(('unpin',path))
    @contextmanager
    def pinned_payload(self,path,hash_,size):
        self.events.append(('pin_payload',hash_,size))
        if sha256(self.raw)!=hash_ or len(self.raw)!=size:raise P00Error(15,'SOURCE_HASH')
        yield SimpleNamespace(handle=1)
        self.events.append(('unpin_payload',hash_,size))

class SourceTests(unittest.TestCase):
    def setup_case(self):
        raw=b'# synthetic code, never executed\n';rows=[{'path':'native/guest-agent.py','bytes':len(raw),'sha256':sha256(raw)}]
        identity={'source_content_digest':digest(rows),'source_members':rows}
        paths=FakePaths(raw);return SourcePins('/fixture',paths,identity,digest(rows)),paths,identity
    def test_read_exact_reviewed_member(self):
        pins,paths,_=self.setup_case();self.assertEqual(pins.read('native/guest-agent.py'),paths.raw)
        self.assertEqual(paths.events[0][0],'pin');self.assertEqual(paths.events[-1][0],'unpin')
    def test_same_size_replacement_rejected(self):
        pins,paths,_=self.setup_case();paths.raw=b'x'*len(paths.raw)
        with self.assertRaises(P00Error):pins.read('native/guest-agent.py')
    def test_changed_size_rejected(self):
        pins,paths,_=self.setup_case();paths.raw+=b'evil'
        with self.assertRaises(P00Error):pins.read('native/guest-agent.py')
    def test_no_self_trusted_current_hash(self):
        pins,paths,ident=self.setup_case();ident['source_members'][0]['sha256']='0'*64
        with self.assertRaises(P00Error):SourcePins('/fixture',paths,ident,ident['source_content_digest'])
    def test_unreviewed_source_not_opened(self):
        pins,paths,_=self.setup_case()
        with self.assertRaises(P00Error):pins.read('native/other.py')
        self.assertEqual(paths.events,[])
    def test_parent_traversal_not_opened(self):
        pins,paths,_=self.setup_case()
        with self.assertRaises(P00Error):pins.read('../other.py')
        self.assertEqual(paths.events,[])
    def test_path_handle_remains_pinned_during_caller(self):
        pins,paths,_=self.setup_case()
        with pins.path('native/guest-agent.py'):
            self.assertEqual(paths.events[-1][0],'pin_payload')
        self.assertEqual(paths.events[-1][0],'unpin_payload')
    def test_guest_transport_c0_recovery_cannot_launch(self):
        pins,paths,_=self.setup_case();called=[]
        transport=GuestTransport('/fixture',SimpleNamespace(run=lambda *a,**kw:called.append(a)),
                                 r'C:\Windows\System32',{},pins)
        c=SimpleNamespace(held=True,fence={'state':'INTENT'},admission=SimpleNamespace(purpose='RECONCILIATION_ONLY'))
        with self.assertRaises(P00Error):transport.run('target','film',{'operation':'INVENTORY','user':'film'},c)
        self.assertEqual(called,[]);self.assertEqual(paths.events,[])

class NativeJournalAdmissionTests(unittest.TestCase):
    def setup_case(self):
        paths=JournalPaths();journal=NativeJournal(paths,SimpleNamespace(held=True),'synthetic')
        journal.initialize(MetadataPermit('synthetic',SID,'a'*64,'b'*64));return journal
    def test_quiet_metadata_journal_allows_admission(self):
        journal=self.setup_case();journal.admission_check()
    def test_pending_detached_read_without_mutation_fence_blocks_new_actions(self):
        journal=self.setup_case();journal.append_event({'kind':'READ_PROBE_INTENT','read_id':'read-x'})
        self.assertIsNone(journal.load_fence())
        with self.assertRaises(P00Error):journal.admission_check()
    def test_metadata_noop_also_checks_pending_reads(self):
        journal=self.setup_case();journal.append_event({'kind':'READ_PROBE_INTENT','read_id':'read-x'})
        with self.assertRaises(P00Error):journal.initialize_or_verify(MetadataPermit('synthetic',SID,'a'*64,'b'*64))

class ProgressIdentityTests(unittest.TestCase):
    def test_integer_indices_are_serialized_without_weakening_codec(self):
        value={1:{'x':2},0:{'y':3}}
        self.assertEqual(progress_digest(value),digest({'0':{'y':3},'1':{'x':2}}))
        with self.assertRaises(P00Error):digest(value)
    def test_boolean_index_is_not_a_step(self):
        with self.assertRaises(P00Error):progress_digest({True:{}})
    def test_revalidation_cannot_hide_malformed_step_or_baseline(self):
        r,d,st,g,i,p=_setup_noop(self);r.execute(i,p)
        rows=deepcopy(st.read_events())
        # Test replay's semantic checks after the storage hash chain layer.
        altered=None
        for row in rows:
            e=row['event']
            if e['kind']=='SET_FENCE' and e['record'].get('state')=='TERMINAL' and e['record']['witness'].get('execution_phase')=='LIVE_REVALIDATION':
                altered=e['record'];altered['witness']['step_id']='step-999'
            elif e['kind']=='CLEAR_FENCE' and altered is not None:
                e['fence_digest']=digest(altered)
        with self.assertRaises(P00Error):completed_steps(rows,p)
