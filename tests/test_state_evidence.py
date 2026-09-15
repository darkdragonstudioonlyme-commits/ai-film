import unittest
import tempfile
import subprocess
import sys
from pathlib import Path
from dataclasses import replace
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
from aifilm_p00.errors import P00Error
from aifilm_p00.codec import canonical,sha256,loads
from aifilm_p00.authority import authorize,Admission
from aifilm_p00.admission import Coordinator
from aifilm_p00.evidence import *
from aifilm_p00.journal_files import FileJournal
from aifilm_p00.windows_commands import *
from helpers import *
from test_core import Checks

class AdmissionTests(Checks):
    def setup_admission(self):
        i,p,ctx,store=authority_case(); return authorize(i,p,ctx,store)
    def setup_coord(self):
        g=MemoryGuard(); st=MemoryStorage(); a=self.setup_admission(); c=Coordinator(g,st); c.acquire(a); return c,st,g,a
    def intent(self,c):
        c.intent('INSTALL_DISTRO',[{'volume_id':'v','reserve':5*GIB}],{'host_boot':'boot','controller_pid':1,'controller_start':'start','build_digest':B,'step_id':'s1'})
    def proof(self,c): return {'action':c.fence['action'],'no_pending_writer':True,'terminal_observed':True,'postconditions_observed':True,'evidence_digest':CP,'native_witness':c.fence['native']}
    def test_busy_no_other_fence(self):
        c,st,g,a=self.setup_coord(); other=Coordinator(g,st); self.reject(21,other.acquire,a); c.close()
    def test_timeout_fence_survives_os_lock_release(self):
        c,st,g,a=self.setup_coord(); self.intent(c); c.native_started({'pid':2,'start':'s','action_id':'native'}); c.uncertain(); c.close()
        self.assertFalse(g.busy); self.assertEqual(st.fence['state'],'UNCERTAIN'); self.reject(21,Coordinator(g,st).acquire,a)
    def test_no_age_based_unlock(self):
        c,st,g,a=self.setup_coord(); self.intent(c); st.fence['ancient_time']='2000-01-01'; c.close(); self.reject(21,Coordinator(g,st).acquire,a)
    def test_other_owner_cannot_reconcile(self):
        c,st,g,a=self.setup_coord(); self.intent(c); c.close(); wrong=replace(a,owner_sid='S-1-5-99',purpose='RECONCILIATION_ONLY'); self.reject(12,Coordinator(g,st).acquire,wrong,reconciliation=True)
    def test_reconcile_still_needs_terminal_observation(self):
        c,st,g,a=self.setup_coord(); self.intent(c); c.close(); a=replace(a,purpose='RECONCILIATION_ONLY'); rec=Coordinator(g,st).acquire(a,reconciliation=True)
        proof=self.proof(rec); proof['no_pending_writer']=False; self.reject(21,rec.reconcile,proof); self.assertIsNotNone(st.fence); rec.close()
    def test_explicit_reconciliation_clears_after_journal(self):
        c,st,g,a=self.setup_coord(); self.intent(c); c.close(); rec=Coordinator(g,st).acquire(replace(a,purpose='RECONCILIATION_ONLY'),reconciliation=True)
        rec.reconcile(self.proof(rec)); self.assertIsNone(st.fence); self.assertEqual(st.events[-1]['kind'],'TERMINAL'); rec.close()
    def test_journal_failure_preserves_fence(self):
        c,st,g,a=self.setup_coord(); st.fail_append=True; self.reject(18,self.intent,c); self.assertIsNotNone(st.fence); c.close()
    def test_terminal_append_failure_does_not_clear(self):
        c,st,g,a=self.setup_coord(); self.intent(c); st.fail_append=True; self.reject(18,c.terminal,self.proof(c)); self.assertIsNotNone(st.fence); c.close()
    def test_no_same_run_nested_acquire(self):
        c,st,g,a=self.setup_coord(); self.reject(21,c.acquire,a); self.assertTrue(g.busy); c.close()
    def test_native_witness_required(self):
        c,st,g,a=self.setup_coord(); self.intent(c); self.reject(11,c.native_started,{'pid':2}); c.close()
    def test_awaiting_reboot_fence_retained(self):
        c,st,g,a=self.setup_coord(); self.intent(c); c.awaiting('AWAITING_REBOOT'); c.close(); self.assertEqual(st.fence['state'],'AWAITING_REBOOT')
    def test_wrong_native_witness_not_terminal(self):
        c,st,g,a=self.setup_coord(); self.intent(c); proof=self.proof(c); proof['native_witness']={'pid':123}; self.reject(19,c.terminal,proof); c.close()

class JournalTests(Checks):
    def test_persist_reload_fence(self):
        with tempfile.TemporaryDirectory() as d:
            st=FileJournal(Path(d)); st.write_fence({'state':'UNCERTAIN','action':'synthetic'}); self.assertEqual(FileJournal(Path(d)).load_fence()['state'],'UNCERTAIN')
    def test_hash_chain_reload(self):
        with tempfile.TemporaryDirectory() as d:
            st=FileJournal(Path(d)); st.append_event({'a':1}); st.append_event({'a':2}); self.assertEqual(len(FileJournal(Path(d)).read_events()),2)
    def test_truncated_journal_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            st=FileJournal(Path(d)); st.append_event({'a':1}); p=Path(d)/'events.jsonl'; p.write_bytes(p.read_bytes()[:-1]); self.reject(15,st.read_events)
    def test_fence_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            st=FileJournal(Path(d)); st.write_fence({'state':'UNCERTAIN'}); p=Path(d)/'fence.json'; p.write_bytes(p.read_bytes().replace(b'UNCERTAIN',b'TERMINAL')); self.reject(15,st.load_fence)
    def test_cannot_clear_uncertain(self):
        with tempfile.TemporaryDirectory() as d:
            st=FileJournal(Path(d)); st.write_fence({'state':'UNCERTAIN'}); self.reject(21,st.clear_fence)
    def test_terminal_archive_retained(self):
        with tempfile.TemporaryDirectory() as d:
            st=FileJournal(Path(d)); st.write_fence({'state':'TERMINAL'}); st.clear_fence(); self.assertIsNone(st.load_fence()); self.assertEqual(len(list(Path(d).glob('terminal-*'))),1)
    def test_symlink_fence_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'secret').write_text('CANARY'); (root/'fence.json').symlink_to(root/'secret'); st=FileJournal(root); self.reject(16,st.load_fence)

class EvidenceTests(Checks):
    def inventory(self,scope='INVENTORY'):
        records=[]
        for eid in sorted(requiredness(scope)):
            c=collected(eid)
            if scope=='GATE_HANDOFF':
                rec=deepcopy(c.record); rec['source_kind']='LAB' if eid=='E00-13' else 'SITE'
                c=replace(c,record=rec,expected_bytes_digest=sha256(canonical(rec)),bytes_seen=len(canonical(rec)))
            records.append(c)
        return records
    def bundle(self,records=None,scope='INVENTORY',**kw):
        return assemble(scope,self.inventory(scope) if records is None else records,Sanitizer(b'workspace-salt-not-host-1234'),context={},scanner=lambda b:b'CANARY_SECRET' not in b,**kw)
    def test_complete_inventory_not_gate(self):
        result=self.bundle(); self.assertEqual(result.exit,0); self.assertFalse(result.component_eligible); self.assertFalse(result.report['host_ready']); bundle_integrity(result.archive)
    def test_document_records_cannot_be_site_gate(self):
        records=[collected(eid) for eid in requiredness('GATE_HANDOFF')]; self.assertEqual(self.bundle(records,'GATE_HANDOFF').exit,22)
    def test_gate_component_only_not_host_ready(self):
        r=self.bundle(scope='GATE_HANDOFF'); self.assertEqual(r.exit,0); self.assertTrue(r.component_eligible); self.assertFalse(r.report['host_ready'])
    def test_optional_missing(self): self.assertEqual(self.bundle(optional_ids=frozenset({'E00-15'})).exit,2)
    def test_mandatory_missing(self): self.assertEqual(self.bundle(self.inventory()[:-1]).exit,22)
    def test_mandatory_timeout(self):
        r=self.inventory(); r[0]=replace(r[0],duration_ms=30001); self.assertEqual(self.bundle(r).exit,22)
    def test_optional_timeout(self):
        r=self.inventory()+[collected('E00-15',duration_ms=30001)]; self.assertEqual(self.bundle(r,optional_ids=frozenset({'E00-15'})).exit,2)
    def test_at_collector_cap_with_eof(self):
        r=self.inventory(); r[0]=replace(r[0],bytes_seen=COLLECTOR_CAP,eof=True); self.assertEqual(self.bundle(r).exit,0)
    def test_at_collector_cap_without_eof(self):
        r=self.inventory(); r[0]=replace(r[0],bytes_seen=COLLECTOR_CAP,eof=False); self.assertEqual(self.bundle(r).exit,22)
    def test_eof_missing_even_below_cap(self):
        r=self.inventory(); r[0]=replace(r[0],eof=False); self.assertEqual(self.bundle(r).exit,22)
    def test_mandatory_over_cap(self):
        r=self.inventory(); r[0]=replace(r[0],bytes_seen=COLLECTOR_CAP+1); self.assertEqual(self.bundle(r).exit,22)
    def test_aggregate_cap(self): self.assertEqual(self.bundle(bundle_cap=1024).exit,22)
    def test_protected_access_unavailable(self):
        r=self.inventory(); r[0]=replace(r[0],protected_access=False); self.assertEqual(self.bundle(r).exit,22)
    def test_known_nested_raw_redacted(self):
        summary={'errors':[{'message':'CANARY_SECRET','details':{'url':'https://u:CANARY_SECRET@example.invalid/?token=CANARY_SECRET','path':r'C:\CANARY_SECRET\x','password':'CANARY_SECRET'}}]}
        r=self.inventory(); r[0]=collected('E00-01',summary=summary); result=self.bundle(r); self.assertEqual(result.exit,0)
        with ZipFile(BytesIO(result.archive)) as z:
            for name in z.namelist(): self.assertNotIn(b'CANARY_SECRET',z.read(name))
    def test_unknown_nested_key_blocks_all_publication(self):
        r=self.inventory(); r[0]=collected('E00-01',summary={'errors':[{'unallowlisted':'CANARY_SECRET'}]}); result=self.bundle(r); self.assertEqual(result.exit,23); self.assertIsNone(result.archive)
    def test_scanner_unavailable_blocks(self):
        result=assemble('INVENTORY',self.inventory(),Sanitizer(b'x'*16),context={},scanner=None); self.assertEqual(result.exit,23)
    def test_privacy_beats_missing_and_optional(self):
        r=self.inventory()[1:]; r[0]=collected(r[0].evidence_id,summary={'oops':'CANARY_SECRET'}); self.assertEqual(self.bundle(r,optional_ids=frozenset({'E00-15'})).exit,23)
    def test_hash_mismatch(self):
        r=self.inventory(); r[0]=replace(r[0],expected_bytes_digest=B); self.assertEqual(self.bundle(r).exit,15)
    def test_no_required_to_optional(self): self.reject(10,self.bundle,optional_ids=frozenset({'E00-01'}))
    def test_no_auto_scope_change(self):
        r=self.bundle(self.inventory()[:-1]); self.assertEqual(r.report['scope'],'INVENTORY')
    def test_future_guest_inventory_only(self):
        r=self.inventory(); idx=[c.evidence_id for c in r].index('E00-04'); r[idx]=collected('E00-04',status='NOT_YET_CREATED'); self.assertEqual(self.bundle(r).exit,0)
    def test_gate_no_e17_recursion(self):
        r=self.bundle(scope='GATE_HANDOFF'); result=bundle_integrity(r.archive); self.assertTrue(result['integrity'])
        with ZipFile(BytesIO(r.archive)) as z: self.assertFalse(any('gate_assessment' in name for name in z.namelist()))
    def test_member_hash_tamper(self):
        r=self.bundle(); out=BytesIO()
        with ZipFile(BytesIO(r.archive)) as src,ZipFile(out,'w',ZIP_DEFLATED) as dst:
            for name in src.namelist(): dst.writestr(name,src.read(name)+b' ' if name=='summaries/host.json' else src.read(name))
        self.reject(15,bundle_integrity,out.getvalue())

class CommandTests(Checks):
    def test_create_literals_unicode_spaces(self):
        args=compile_wsl('INSTALL_DISTRO',system_directory=r'C:\Windows\System32',target='AI Film Việt',payload=r'D:\Tải về\Ubuntu.wsl',base_path=r'D:\Phim Việt\Target')
        self.assertEqual(args[-1],'--no-launch'); self.assertIn('AI Film Việt',args); self.assertIn(r'D:\Tải về\Ubuntu.wsl',args)
    def test_import_explicit_v2(self):
        args=compile_wsl('IMPORT_NEW_CLONE',system_directory=r'C:\Windows\System32',target='clone',payload=r'D:\backup.tar',base_path=r'D:\clone'); self.assertEqual(args[-2:],['--version','2'])
    def test_no_unregister_compiler(self): self.reject(10,compile_wsl,'UNREGISTER',system_directory=r'C:\Windows\System32',target='x')
    def test_target_control_rejected(self): self.reject(10,compile_wsl,'STOP_TARGET',system_directory=r'C:\Windows\System32',target='x;evil')
    def test_feature_no_restart(self): self.assertIn('/NoRestart',compile_feature('VirtualMachinePlatform',r'C:\Windows\System32'))
    def test_feature_allowlist(self): self.reject(10,compile_feature,'DisableFirewall',r'C:\Windows\System32')
    def test_runtime_no_restart(self): self.assertIn('/norestart',compile_runtime(r'D:\wsl.msi',r'C:\Windows\System32'))

class CLITests(Checks):
    def runcli(self,*args):
        return subprocess.run([sys.executable,'-m','aifilm_p00',*args],capture_output=True,timeout=10)
    def test_workspace_preflight_not_host(self):
        p=self.runcli('preflight','--workspace-only'); self.assertEqual(p.returncode,0); self.assertEqual(loads(p.stdout)['observed_windows_host'],'NOT_COLLECTED')
    def test_recovery_notes_no_mutation(self):
        p=self.runcli('recovery-notes'); self.assertEqual(p.returncode,0); self.assertFalse(loads(p.stdout)['native_execution'])
for interface in ('preflight','apply','verify','support-bundle'):
    def test(self,interface=interface):
        p=self.runcli(interface)
        expected=11 if interface=='preflight' else 10
        reason='WINDOWS_X64_REQUIRED' if interface=='preflight' else 'NATIVE_PLAN_REFERENCE_REQUIRED'
        self.assertEqual(p.returncode,expected); self.assertEqual(loads(p.stdout)['reason'],reason)
    setattr(CLITests,'test_native_'+interface.replace('-','_')+'_blocked_on_workspace',test)
