#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

from dual_ai_text_bridge import BridgeError, provider_argv, read_task, run_task, text_review_schema, validate_admission
from check_dual_ai_contract import validate_task

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def sh(root: Path, *args: str) -> str:
    p=subprocess.run(list(args),cwd=root,text=True,capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr)
    return p.stdout.strip()

def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def make_repo(base: Path):
    root=base/'repo'; root.mkdir()
    (root/'learning').mkdir()
    (root/'PROJECT_STATE.md').write_text('''STATE_VERSION: 1\nCURRENT_ASSIGNEE: CHATGPT\nCURRENT_AUTHOR_ACTOR: CHATGPT\n''')
    (root/'NEXT_WORK_ITEM.md').write_text('''ASSIGNEE: CHATGPT\nAUTHOR_ACTOR: CHATGPT\nRETURN_TO: RUN-P00/V02B\nON_SUCCESS: NEXT_STEP\n''')
    setup_raw=b'{}\n'; setup_sha=sha(setup_raw)
    (root/'setup.json').write_bytes(setup_raw)
    state={'state_version':1,'active_run':{'run_id':'RUN-P00-VALIDATION-002'},
           'current_work':{'assignee':'CHATGPT','author_actor':'CHATGPT','role':'AUTHOR','mode':'IMPLEMENTATION',
                           'profile':'CONTROL_PLANE_AUTHOR','return_to':'RUN-P00/V02B','next_on_success':'NEXT_STEP'},
           'collaboration':{'runtime_enabled':False,'cross_model_acceptance':'NOT_RUN',
                            'operational_gates':{'context_loading':'NOT_RUN','cross_model_acceptance':'NOT_RUN',
                                'dispatcher_qualification':'NOT_IMPLEMENTED','permission_tests':'NOT_RUN',
                                'recovery_tests':'NOT_RUN','data_budget_authorization':'NOT_VERIFIED'},
                            'learning_effectiveness':'IMPROVEMENT_NOT_PROVEN',
                            'setup_observation':{'path':'setup.json','sha256':setup_sha}}}
    write_json(root/'AI_FILM_PROJECT_STATE_V1.json',state)
    (root/'SELF_LEARNING.md').write_text('policy\n')
    reg={'schema_version':1,'records':{'LEARNING-ONE':{'activation_status':'ACTIVE','review_status':'PASS',
          'effectiveness_status':'EFFECTIVE','successor':None}}}
    write_json(root/'learning/LEARNING_STATE.json',reg)
    (root/'learning/LEARNING-ONE.md').write_text('lesson one\n')
    (root/'review-target.md').write_text('target bytes\n')
    sh(root,'git','init','-q'); sh(root,'git','config','user.email','test@example.invalid'); sh(root,'git','config','user.name','Test')
    sh(root,'git','add','.'); sh(root,'git','commit','-qm','fixture')
    commit=sh(root,'git','rev-parse','HEAD')
    return root,commit

def task_for(root: Path, commit: str):
    paths=['SELF_LEARNING.md','learning/LEARNING_STATE.json','learning/LEARNING-ONE.md','review-target.md']
    files=[]
    for p in paths:
        raw=(root/p).read_bytes(); files.append({'path':p,'commit':commit,'sha256':sha(raw)})
    return {
      'schema_version':1,'task_id':'TASK-BRIDGE-001','parent_run_id':'RUN-P00-VALIDATION-002',
      'work_item':'REVIEW-BRIDGE-001','role':'REVIEW','author_actor':'CHATGPT','actor':'CLAUDE_CODE',
      'consumer_actor':'CHATGPT','profile':'TEXT_REVIEW','control_commit':commit,'source_commit':commit,
      'input_files':files,
      'knowledge':{'register_sha256':sha((root/'learning/LEARNING_STATE.json').read_bytes()),
                   'policy_sha256':sha((root/'SELF_LEARNING.md').read_bytes()),
                   'required_learning_ids':['LEARNING-ONE'],
                   'record_refs':{'LEARNING-ONE':{'path':'learning/LEARNING-ONE.md',
                       'sha256':sha((root/'learning/LEARNING-ONE.md').read_bytes())}}},
      'permissions':{'native':False,'signing':False,'publish':False,'escalate':False},
      'limits':{'max_turns':2,'max_seconds':2,'max_input_bytes':100000,'max_output_bytes':100000,'max_cost_usd':0.10},
      'return_to':'RUN-P00/V02B','acceptance':['R1'],
      'output_scope':{'worktree_rel':'unused','files_allowed':[]}}

def provider_payload(*, assessment='PASS', commands=None, reads=None, applied=None, permission=False, high=False, cost=0.001):
    review={'assessment':assessment,'covered':['R1'],'not_evaluated':[],'findings':[],
            'execution_scope':'STATIC_ONLY','executed_commands':commands or []}
    if high:
        review['findings']=[{'id':'F1','severity':'HIGH','status':'OPEN','evidence':'counterexample'}]
    result={'review':review,'knowledge_read_ids':reads or ['LEARNING-ONE'],
            'learning':{'disposition':'REUSE_EXISTING','applied_ids':applied or ['LEARNING-ONE'],
                        'proposals':[],'effectiveness_claim':'NOT_PROVEN'}}
    return {'is_error':False,'result':json.dumps(result,separators=(',',':')),'structured_output':result,
            'permission_denials':['denied'] if permission else [],
            'subagent_stats':{'spawned':0},'usage':{'server_tool_use':{'web_search_requests':0,'web_fetch_requests':0}},
            'session_id':'fake-session','modelUsage':{'sonnet':{'canonicalModel':'claude-sonnet-5'}},'total_cost_usd':cost}

def fake_provider(base: Path, payload: dict, *, sleep=0, counter: Path|None=None, exit_code=0, huge=0) -> Path:
    p=base/'fake-claude.py'
    script=['#!/usr/bin/env python3','import json,sys,time,pathlib','_ = sys.stdin.buffer.read()']
    if counter is not None:
        script += [f"p=pathlib.Path({str(counter)!r})", "n=int(p.read_text()) if p.exists() else 0", "p.write_text(str(n+1))"]
    if sleep: script += [f'time.sleep({sleep})']
    if huge:
        script += [f"sys.stdout.write('x'*{huge})", f'sys.exit({exit_code})']
    else:
        wrapper=json.dumps(payload,separators=(',',':'))
        script += [f'sys.stdout.write({wrapper!r})', f'sys.exit({exit_code})']
    p.write_text('\n'.join(script)+'\n'); p.chmod(p.stat().st_mode|stat.S_IXUSR)
    return p

def process_run(task_path, root, queue, executable, qualification, output):
    try:
        result=run_task(Path(task_path),Path(root),Path(queue),executable,Path(qualification))
    except Exception as exc:
        result={'state':'EXCEPTION','error':type(exc).__name__+':'+str(exc)}
    Path(output).write_text(json.dumps(result))

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(prefix='bridge-test-'); self.base=Path(self.td.name)
        self.root,self.commit=make_repo(self.base); self.task=task_for(self.root,self.commit)
        self.task_path=self.base/'task.json'; write_json(self.task_path,self.task)
        self.queue=self.base/'queue'
        self.q=self.base/'qualification.json'
        write_json(self.q,{'schema_version':1,'scope':'TEXT_REVIEW_QUALIFICATION_ONLY','authorized':True,
                           'control_commit':self.commit,'profile':'TEXT_REVIEW','max_cost_usd':0.25,
                           'max_input_bytes':100000,'data_scope':'REPOSITORY_CONTROL_PLANE_ONLY',
                           'setup_observation_sha256':sha((self.root/'setup.json').read_bytes()),'task_digest':validate_task(self.task)})

    def tearDown(self): self.td.cleanup()

    def fake(self, **kw): return fake_provider(self.base,provider_payload(**{k:v for k,v in kw.items() if k in {'assessment','commands','reads','applied','permission','high','cost'}}),
                                               sleep=kw.get('sleep',0),counter=kw.get('counter'),exit_code=kw.get('exit_code',0),huge=kw.get('huge',0))

    def runq(self, executable):
        q=json.loads(self.q.read_text()); q['control_commit']=self.task['control_commit']; q['task_digest']=validate_task(self.task)
        write_json(self.q,q)
        return run_task(self.task_path,self.root,self.queue,str(executable),self.q)

    def test_provider_argv_has_fixed_restrictions(self):
        a=provider_argv(self.task,'/fake/claude'); joined=' '.join(a)
        for x in ('--safe-mode','--restricted','--tools','--permission-mode','dontAsk','--no-session-persistence','--model','sonnet','--effort','low','--max-turns','2','--json-schema'): self.assertIn(x,joined)
        self.assertNotIn('--disallowedTools',a)
        self.assertNotIn('dangerously-skip-permissions',joined)

    def test_happy_path(self):
        r=self.runq(self.fake()); self.assertEqual(r['state'],'RESULT_UNREVIEWED'); self.assertFalse(r['reused'])
        result=json.loads(Path(r['result_path']).read_text()); self.assertEqual(result['assessment'],'PASS')

    def test_duplicate_dispatch_reuses_result(self):
        count=self.base/'count'; exe=self.fake(counter=count)
        a=self.runq(exe); b=self.runq(exe)
        self.assertEqual(a['state'],'RESULT_UNREVIEWED'); self.assertTrue(b['reused']); self.assertEqual(count.read_text(),'1')

    def test_timeout_never_relaunches(self):
        self.task['limits']['max_seconds']=1; write_json(self.task_path,self.task); count=self.base/'count'; exe=self.fake(sleep=3,counter=count)
        a=self.runq(exe); b=self.runq(exe)
        self.assertEqual(a['state'],'RECONCILE_REQUIRED'); self.assertEqual(b['state'],'RECONCILE_REQUIRED'); self.assertTrue(b['reused']); self.assertEqual(count.read_text(),'1')

    def test_missing_executable_is_capability_block(self):
        r=self.runq(self.base/'missing'); self.assertEqual(r['state'],'BLOCKED_CAPABILITY')

    def test_provider_permission_denial_fails_result(self):
        r=self.runq(self.fake(permission=True)); self.assertEqual(r['state'],'BLOCKED_PERMISSION'); self.assertIn('PROVIDER_PERMISSION_DENIAL',r['failure'])

    def test_tool_claim_is_rejected(self):
        r=self.runq(self.fake(commands=['git status'])); self.assertEqual(r['state'],'FAILED'); self.assertIn('STATIC_EXECUTION',r['failure'])

    def test_open_high_pass_is_rejected(self):
        r=self.runq(self.fake(high=True)); self.assertEqual(r['state'],'FAILED'); self.assertIn('UNSUPPORTED_PASS',r['failure'])

    def test_unsupplied_learning_read_is_rejected(self):
        r=self.runq(self.fake(reads=['LEARNING-ONE','LEARNING-OTHER'])); self.assertEqual(r['state'],'FAILED'); self.assertIn('UNSUPPLIED',r['failure'])

    def test_output_limit_is_enforced(self):
        self.task['limits']['max_output_bytes']=10; write_json(self.task_path,self.task)
        r=self.runq(self.fake(huge=100)); self.assertEqual(r['state'],'FAILED'); self.assertEqual(r['failure'],'OUTPUT_TOO_LARGE')

    def test_input_limit_is_enforced(self):
        self.task['limits']['max_input_bytes']=10; write_json(self.task_path,self.task)
        with self.assertRaisesRegex(BridgeError,'INPUT_TOO_LARGE'): self.runq(self.fake())

    def test_hash_mismatch_is_rejected(self):
        self.task['input_files'][-1]['sha256']='0'*64; write_json(self.task_path,self.task)
        with self.assertRaisesRegex(BridgeError,'INPUT_HASH_MISMATCH'): self.runq(self.fake())

    def test_dirty_root_is_rejected(self):
        (self.root/'review-target.md').write_text('dirty')
        with self.assertRaisesRegex(BridgeError,'CONTROL_ROOT_DIRTY'): self.runq(self.fake())

    def test_parent_run_mismatch_is_rejected(self):
        self.task['parent_run_id']='RUN-OTHER'; write_json(self.task_path,self.task)
        with self.assertRaisesRegex(BridgeError,'PARENT_RUN_MISMATCH'): self.runq(self.fake())

    def test_nonoperative_learning_is_rejected(self):
        reg=json.loads((self.root/'learning/LEARNING_STATE.json').read_text()); reg['records']['LEARNING-ONE']['effectiveness_status']='INEFFECTIVE'
        write_json(self.root/'learning/LEARNING_STATE.json',reg); sh(self.root,'git','add','.'); sh(self.root,'git','commit','-qm','bad learning')
        new=sh(self.root,'git','rev-parse','HEAD'); self.task=task_for(self.root,new); write_json(self.task_path,self.task)
        with self.assertRaisesRegex(BridgeError,'NONOPERATIVE_KNOWLEDGE'): self.runq(self.fake())

    def test_symlink_task_is_rejected(self):
        link=self.base/'link.json'; link.symlink_to(self.task_path)
        with self.assertRaisesRegex(BridgeError,'TASK_FILE_UNSAFE'): read_task(link)

    def test_text_review_requires_one_turn_and_budget(self):
        self.task['limits']['max_turns']=1; write_json(self.task_path,self.task)
        with self.assertRaisesRegex(BridgeError,'TEXT_REVIEW_LIMITS'): read_task(self.task_path)

    def test_author_task_is_rejected(self):
        self.task.update(role='AUTHOR',author_actor='CLAUDE_CODE',actor='CLAUDE_CODE',consumer_actor='CHATGPT')
        write_json(self.task_path,self.task)
        with self.assertRaises(Exception): read_task(self.task_path)

    def test_provider_error_exit_is_failed(self):
        r=self.runq(self.fake(exit_code=7)); self.assertEqual(r['state'],'FAILED'); self.assertEqual(r['failure'],'PROVIDER_EXIT')

    def test_noncanonical_model_json_is_normalized_and_validated(self):
        r=self.runq(self.fake()); raw=(Path(r['result_path']).parent/'review.json').read_bytes()
        self.assertEqual(raw.strip(),json.dumps(json.loads(raw),sort_keys=True,separators=(',',':')).encode())

    def test_task_identity_conflict_is_rejected(self):
        exe=self.fake(); self.runq(exe); self.task['acceptance']=['R2']; write_json(self.task_path,self.task)
        # New task identity is a distinct task directory; no overwrite/replay of the old task.
        r=self.runq(exe); self.assertEqual(r['state'],'FAILED')  # provider still covers R1, proving distinct execution/validation

    def test_no_qualification_receipt_blocks_before_activation(self):
        with self.assertRaisesRegex(BridgeError,'QUALIFICATION_AUTHORIZATION_REQUIRED'):
            run_task(self.task_path,self.root,self.queue,str(self.fake()))

    def test_qualification_target_mismatch_is_rejected(self):
        q=json.loads(self.q.read_text()); q['control_commit']='0'*40; write_json(self.q,q)
        with self.assertRaisesRegex(BridgeError,'QUALIFICATION_RECEIPT_TARGET'):
            run_task(self.task_path,self.root,self.queue,str(self.fake()),self.q)

    def test_tampered_review_is_not_reused(self):
        exe=self.fake(); r=self.runq(exe)
        d=Path(r['result_path']).parent; (d/'review.json').write_bytes(b'{}')
        again=self.runq(exe)
        self.assertEqual(again['state'],'RECONCILE_REQUIRED'); self.assertIn('PERSISTED_RESULT_INVALID',again['failure'])

    def active_state(self):
        current={'work_item':self.task['work_item'],'parent_run_id':self.task['parent_run_id'],
                 'assignee':self.task['actor'],'author_actor':self.task['author_actor'],
                 'role':self.task['role'],'profile':self.task['profile'],'return_to':self.task['return_to']}
        ev=self.root/'activation.json'; ev.write_text('{\"ok\":true}\n')
        return {'current_work':current,'collaboration':{'runtime_enabled':True,
                'activation_evidence':{'path':'activation.json','sha256':sha(ev.read_bytes())}}}

    def test_active_runtime_requires_current_task_match(self):
        s=self.active_state(); s['current_work']['work_item']='OTHER'
        with self.assertRaisesRegex(BridgeError,'TASK_NOT_CURRENTLY_AUTHORIZED'):
            validate_admission(None,self.task,s,self.root,validate_task(self.task))

    def test_active_runtime_checks_activation_evidence_hash(self):
        s=self.active_state(); s['collaboration']['activation_evidence']['sha256']='0'*64
        with self.assertRaisesRegex(BridgeError,'ACTIVATION_EVIDENCE_MISMATCH'):
            validate_admission(None,self.task,s,self.root,validate_task(self.task))

    def test_active_runtime_matching_task_and_evidence_passes(self):
        r=validate_admission(None,self.task,self.active_state(),self.root,validate_task(self.task))
        self.assertEqual(r['mode'],'ACTIVE_RUNTIME')

    def test_qualification_task_digest_mismatch_is_rejected(self):
        q=json.loads(self.q.read_text()); q['task_digest']='0'*64; write_json(self.q,q)
        with self.assertRaisesRegex(BridgeError,'QUALIFICATION_RECEIPT_TARGET'):
            run_task(self.task_path,self.root,self.queue,str(self.fake()),self.q)

    def test_provider_cost_over_cap_is_rejected(self):
        r=self.runq(self.fake(cost=0.11)); self.assertEqual(r['state'],'FAILED'); self.assertIn('PROVIDER_COST_LIMIT',r['failure'])

    def test_provider_missing_cost_is_rejected(self):
        payload=provider_payload(); payload.pop('total_cost_usd')
        r=self.runq(fake_provider(self.base,payload)); self.assertEqual(r['state'],'FAILED'); self.assertIn('PROVIDER_COST_LIMIT',r['failure'])

    def test_qualification_receipt_world_writable_is_rejected(self):
        self.q.chmod(0o666)
        with self.assertRaisesRegex(BridgeError,'QUALIFICATION_RECEIPT_PERMISSIONS'):
            run_task(self.task_path,self.root,self.queue,str(self.fake()),self.q)

    def test_task_file_world_writable_is_rejected(self):
        self.task_path.chmod(0o666)
        with self.assertRaisesRegex(BridgeError,'TASK_FILE_PERMISSIONS'): read_task(self.task_path)

    def test_insecure_existing_queue_is_rejected(self):
        self.queue.mkdir(); self.queue.chmod(0o777)
        with self.assertRaisesRegex(BridgeError,'QUEUE_ROOT_UNSAFE'): self.runq(self.fake())

    def test_concurrent_same_task_spawns_one_provider(self):
        count=self.base/'counter'; exe=self.fake(sleep=1,counter=count)
        # Refresh exact qualification grant before forking.
        q=json.loads(self.q.read_text()); q['task_digest']=validate_task(self.task); write_json(self.q,q)
        o1=self.base/'p1.json'; o2=self.base/'p2.json'
        p1=multiprocessing.Process(target=process_run,args=(str(self.task_path),str(self.root),str(self.queue),str(exe),str(self.q),str(o1)))
        p2=multiprocessing.Process(target=process_run,args=(str(self.task_path),str(self.root),str(self.queue),str(exe),str(self.q),str(o2)))
        p1.start(); p2.start(); p1.join(5); p2.join(5)
        self.assertFalse(p1.is_alive()); self.assertFalse(p2.is_alive()); self.assertEqual(count.read_text(),'1')
        states={json.loads(o1.read_text())['state'],json.loads(o2.read_text())['state']}
        self.assertIn('RESULT_UNREVIEWED',states)
        self.assertTrue(states <= {'RESULT_UNREVIEWED','RUNNING','RECONCILE_REQUIRED'})
        final=self.runq(exe); self.assertEqual(final['state'],'RESULT_UNREVIEWED'); self.assertTrue(final['reused']); self.assertEqual(count.read_text(),'1')

    def test_policy_identity_drift_is_rejected_by_task_contract(self):
        self.task['knowledge']['policy_sha256']='0'*64; write_json(self.task_path,self.task)
        with self.assertRaises(Exception): read_task(self.task_path)

    def test_structured_output_mismatch_is_rejected(self):
        payload=provider_payload(); payload['structured_output']={'wrong':True}
        r=self.runq(fake_provider(self.base,payload)); self.assertEqual(r['state'],'FAILED'); self.assertIn('STRUCTURED_OUTPUT_MISMATCH',r['failure'])

    def test_missing_structured_output_is_rejected(self):
        payload=provider_payload(); payload.pop('structured_output')
        r=self.runq(fake_provider(self.base,payload)); self.assertEqual(r['state'],'FAILED'); self.assertIn('STRUCTURED_OUTPUT_MISSING',r['failure'])

    def test_schema_binds_acceptance_and_lesson_ids(self):
        s=json.loads(text_review_schema(self.task))
        self.assertEqual(s['properties']['review']['properties']['covered']['items']['enum'],['R1'])
        self.assertEqual(s['properties']['review']['properties']['not_evaluated']['items']['enum'],['R1'])
        self.assertEqual(s['properties']['knowledge_read_ids']['items']['enum'],['LEARNING-ONE'])
        self.assertEqual(s['properties']['learning']['properties']['applied_ids']['items']['enum'],['LEARNING-ONE'])

    def test_missing_primary_model_is_rejected(self):
        payload=provider_payload(); payload['modelUsage']={'aux':{'canonicalModel':'claude-haiku-4-5'}}
        r=self.runq(fake_provider(self.base,payload)); self.assertEqual(r['state'],'FAILED'); self.assertIn('PROVIDER_PRIMARY_MODEL_MISSING',r['failure'])

    def test_unknown_auxiliary_model_is_rejected(self):
        payload=provider_payload(); payload['modelUsage']['mystery']={'canonicalModel':'claude-unknown-1'}
        r=self.runq(fake_provider(self.base,payload)); self.assertEqual(r['state'],'FAILED'); self.assertIn('PROVIDER_UNKNOWN_AUXILIARY_MODEL',r['failure'])

    def test_observed_haiku_auxiliary_is_allowed(self):
        payload=provider_payload(); payload['modelUsage']['aux']={'canonicalModel':'claude-haiku-4-5'}
        r=self.runq(fake_provider(self.base,payload)); self.assertEqual(r['state'],'RESULT_UNREVIEWED')

if __name__=='__main__': unittest.main(verbosity=2)
