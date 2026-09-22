import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
TOOL=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('up',TOOL/'update-v03-native-policy.py');up=importlib.util.module_from_spec(spec);spec.loader.exec_module(up)
def can(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
class PolicyTests(unittest.TestCase):
 def setUp(self):
  self.td=tempfile.TemporaryDirectory();self.r=Path(self.td.name);obj={'role':'base','x':1};raw=can(obj);ref=hashlib.sha256(raw).hexdigest()
  self.parent={'schema_version':1,'host_id':'h','operator_sids':['S'],'role_pins':{'base':[ref]},'blobs':{ref:raw.decode()},'withdrawn_refs':[],'generation':1}
  self.pr=self.r/'parent.json';self.pr.write_bytes(can(self.parent));self.cur=self.r/'current.json';self.cur.write_bytes(self.pr.read_bytes())
  self.add=[{'role':'lab_authority_lineage','schema_version':1,'x':2}]
  self.e={'suite_ref':'1'*64,'case_id':'T','stage_index':1,'slot_ref':'2'*64,'immutable_partition_digest':'3'*64,'lineage_ref':'4'*64,'plan_ref':'5'*64}
  self.j=self.r/'j.jsonl';self.g=self.r/'guard';self.sha=hashlib.sha256(self.pr.read_bytes()).hexdigest()
 def tearDown(self):self.td.cleanup()
 def test_publish_and_idempotent_recovery(self):
  a=up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g);self.assertTrue(a['rewrote_policy']);self.assertEqual(a['new_generation'],2)
  b=up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g);self.assertFalse(b['rewrote_policy']);self.assertTrue(b['publication_event_reused'])
 def test_after_write_fault_does_not_rewrite(self):
  with self.assertRaisesRegex(Exception,'FAULT_AFTER_WRITE'):up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g,fault='AFTER_WRITE_BEFORE_READBACK')
  self.assertFalse(up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g)['rewrote_policy'])
 def test_unknown_current_blocks(self):
  self.cur.write_bytes(b'{}')
  with self.assertRaisesRegex(Exception,'UNKNOWN_CURRENT_POLICY'):up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g)
 def test_same_key_conflict_blocks(self):
  up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g);rows=up.read_events(self.j);rows[0]['plan_ref']='6'*64;self.j.write_bytes(can(rows[0])+b'\n')
  with self.assertRaisesRegex(Exception,'PUBLICATION_EVENT_CONFLICT'):up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g)
 def test_all_publication_fault_boundaries_reconcile(self):
  for fault in ['BEFORE_WRITE','AFTER_READBACK_BEFORE_EVENT','AFTER_EVENT']:
   self.cur.write_bytes(self.pr.read_bytes());self.j.unlink(missing_ok=True)
   with self.assertRaises(Exception):up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g,fault=fault)
   r=up.publish(self.pr,self.cur,self.sha,self.add,self.e,self.j,self.g);self.assertTrue(r['guard_released_before_request_entry']);self.assertEqual(r['new_generation'],2)
if __name__=='__main__':unittest.main()
