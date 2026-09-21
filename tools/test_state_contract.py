#!/usr/bin/env python3
"""Adversarial tests for canonical selection and honest continuity-check scope.
All Git remotes are disposable local repositories; no native/runtime action occurs.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from check_state_contract import StateContractError, load_selected_state

ROOT = Path(__file__).resolve().parents[1]


class StateContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='aifilm-state-contract-')
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        (self.root / 'PROJECT_STATE.md').write_text('STATE_VERSION: 1\n')
        (self.root / 'AI_FILM_PROJECT_STATE_V1.json').write_text('{"state_version":1,"active_run":null}')

    def tearDown(self):
        self.tmp.cleanup()

    def test_selected_not_largest(self):
        (self.root / 'AI_FILM_PROJECT_STATE_V99999.json').write_text('{"state_version":99999}')
        self.assertEqual(load_selected_state(self.root)[0], 1)

    def test_missing_selector(self):
        (self.root / 'PROJECT_STATE.md').write_text('No state pointer\n')
        with self.assertRaisesRegex(StateContractError, 'state-selector-count:0'):
            load_selected_state(self.root)

    def test_duplicate_selector(self):
        (self.root / 'PROJECT_STATE.md').write_text('STATE_VERSION: 1\nSTATE_VERSION: 2\n')
        with self.assertRaisesRegex(StateContractError, 'state-selector-count:2'):
            load_selected_state(self.root)

    def test_malformed_selector(self):
        (self.root / 'PROJECT_STATE.md').write_text('STATE_VERSION: latest\n')
        with self.assertRaisesRegex(StateContractError, 'state-selector-invalid'):
            load_selected_state(self.root)

    def test_missing_selected_snapshot(self):
        (self.root / 'AI_FILM_PROJECT_STATE_V1.json').unlink()
        with self.assertRaisesRegex(StateContractError, 'selected-state-missing'):
            load_selected_state(self.root)

    def test_version_parity(self):
        (self.root / 'AI_FILM_PROJECT_STATE_V1.json').write_text('{"state_version":2}')
        with self.assertRaisesRegex(StateContractError, 'version-mismatch'):
            load_selected_state(self.root)

    def test_boolean_version_not_integer(self):
        (self.root / 'AI_FILM_PROJECT_STATE_V1.json').write_text('{"state_version":true}')
        with self.assertRaisesRegex(StateContractError, 'version-mismatch'):
            load_selected_state(self.root)

    def test_duplicate_json_key(self):
        (self.root / 'AI_FILM_PROJECT_STATE_V1.json').write_text('{"state_version":1,"active_run":{},"active_run":null}')
        with self.assertRaisesRegex(StateContractError, 'duplicate-json-key'):
            load_selected_state(self.root)

    def test_nonobject_snapshot(self):
        (self.root / 'AI_FILM_PROJECT_STATE_V1.json').write_text('[]')
        with self.assertRaisesRegex(StateContractError, 'not-object'):
            load_selected_state(self.root)

    def test_symlink_snapshot(self):
        target = self.root / 'outside.json'
        target.write_text('{"state_version":1}')
        selected = self.root / 'AI_FILM_PROJECT_STATE_V1.json'
        selected.unlink(); selected.symlink_to(target)
        with self.assertRaisesRegex(StateContractError, 'symlink'):
            load_selected_state(self.root)

    def prepare_checker(self):
        tools = self.root / 'tools'; tools.mkdir(exist_ok=True)
        for name in ('check_state_contract.py','check_workflow_continuity.py','check_continuity_measurements.py'):
            shutil.copy2(ROOT / 'tools' / name, tools / name)
        active = {'run_id':'RUN-TEST-001','workflow_id':'WF-TEST-CONTINUITY',
                  'owner_lane':'TEST','run_record':'lane/test:workflow-runs/RUN-TEST-001.md',
                  'status':'RUNNING','current_step':'D01_STEP','canonical_base':'a'*40,
                  'local_worktree':None}
        (self.root / 'AI_FILM_PROJECT_STATE_V1.json').write_text(json.dumps({'state_version':1,'active_run':active}))

    def run_checker(self, *args, repo=None, script='check_workflow_continuity.py'):
        env = dict(os.environ, AIFILM_CONTROL_REPO=str(repo or (self.root / 'absent')),
                   AIFILM_WORKSPACE_ROOT=str(self.root / 'workspace-absent'))
        return subprocess.run([sys.executable,str(self.root/'tools'/script),*args],
                              env=env,text=True,capture_output=True,timeout=15)

    def test_schema_only_not_pass(self):
        self.prepare_checker(); p=self.run_checker('--schema-only')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertIn('WORKFLOW_CONTINUITY_SCHEMA_ONLY',p.stdout)
        self.assertIn('NOT_HANDOFF_EVIDENCE',p.stdout)
        self.assertNotIn('CHECK_PASS',p.stdout)

    def test_absent_workspace_default_discloses_scope(self):
        self.prepare_checker(); p=self.run_checker()
        self.assertEqual(p.returncode,0)
        self.assertIn('remote=NOT_EVALUATED',p.stdout)

    def test_required_remote_fails_closed(self):
        self.prepare_checker(); p=self.run_checker('--require-remote')
        self.assertNotEqual(p.returncode,0)
        self.assertIn('remote-reconciliation-unavailable',p.stdout)

    def test_shadow_does_not_disable_active_run(self):
        self.prepare_checker()
        (self.root/'AI_FILM_PROJECT_STATE_V99999.json').write_text('{"state_version":99999,"active_run":null}')
        p=self.run_checker('--require-remote')
        self.assertNotEqual(p.returncode,0)
        self.assertNotIn('no-active-run',p.stdout)

    def test_both_consumers_reject_duplicate_pointer(self):
        self.prepare_checker()
        (self.root/'PROJECT_STATE.md').write_text('STATE_VERSION: 1\nSTATE_VERSION: 1\n')
        for script in ('check_workflow_continuity.py','check_continuity_measurements.py'):
            p=self.run_checker(script=script)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('state-selector-count:2',p.stdout)

    def git(self, path, *args):
        return subprocess.check_output(['git','-C',str(path),*args],text=True,stderr=subprocess.DEVNULL).strip()

    def prepare_remote(self, output=None, duplicate=False, local=False):
        self.prepare_checker()
        producer=Path(self.tmp.name)/'producer';producer.mkdir()
        upstream=Path(self.tmp.name)/'upstream.git';upstream.mkdir()
        self.git(upstream,'init','--bare')
        self.git(producer,'init');self.git(producer,'config','user.name','Fixture')
        self.git(producer,'config','user.email','fixture@example.invalid')
        self.git(producer,'checkout','-b','lane/test')
        run_dir=producer/'workflow-runs';run_dir.mkdir()
        inp={'fixture':'local-only'}
        key=hashlib.sha256(json.dumps({'step_id':'D01_STEP','input_identity':inp},sort_keys=True,separators=(',',':')).encode()).hexdigest()
        record=f'''RUN_ID: RUN-TEST-001
WORKFLOW_ID: WF-TEST-CONTINUITY
BASE_IDENTITY: {'a'*40}
WORKTREE_REL: NONE
STATUS: RUNNING
CURRENT_STEP: D01_STEP
STEP_ID: D01_STEP
STATE: COMPLETE
INPUT_IDENTITY: {{"fixture":"local-only"}}
IDEMPOTENCY_KEY: {key}
DONE_WHEN: {{"observed":true}}
OUTPUT_IDENTITY: {json.dumps({'artifact':'verified'} if output is None else output)}
REPLAY_POLICY: VERIFY_AND_REUSE
'''
        if local:
            record=record.replace('WORKTREE_REL: NONE','WORKTREE_REL: worktree-test')+'OBSERVED_LOCAL_HEAD: '+('b'*40)+'\n'
            path=self.root/'AI_FILM_PROJECT_STATE_V1.json';data=json.loads(path.read_text())
            data['active_run'].update(local_worktree='worktree-test',observed_local_head='b'*40)
            path.write_text(json.dumps(data))
        (run_dir/'RUN-TEST-001.md').write_text(record)
        if duplicate:
            (run_dir/'RUN-TEST-002.md').write_text(record.replace('RUN-TEST-001','RUN-TEST-002'))
        (producer/'LANE_STATE.md').write_text('RUN-TEST-001\nworkflow-runs/RUN-TEST-001.md\nD01_STEP\n')
        self.git(producer,'add','.');self.git(producer,'commit','-m','fixture')
        self.git(producer,'remote','add','origin',str(upstream));self.git(producer,'push','origin','lane/test')
        self.git(self.root,'init');self.git(self.root,'remote','add','origin',str(upstream))
        return self.git(producer,'rev-parse','HEAD')

    def test_full_remote_check_resolves_immutable_head(self):
        sha=self.prepare_remote();p=self.run_checker('--require-remote',repo=self.root)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertIn('scope=REMOTE_LEDGER',p.stdout)
        self.assertIn('lane_head='+sha,p.stdout)
        self.assertIn('native=NOT_EVALUATED',p.stdout)

    def test_empty_complete_output_rejected(self):
        self.prepare_remote(output={});p=self.run_checker('--require-remote',repo=self.root)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('current-step-complete-output-missing',p.stdout)

    def test_duplicate_run_rejected(self):
        self.prepare_remote(duplicate=True);p=self.run_checker('--require-remote',repo=self.root)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('duplicate-or-mismatched-active-run',p.stdout)

    def test_malformed_or_missing_active_run_not_no_run(self):
        self.prepare_checker()
        for data in ({'state_version':1},{'state_version':1,'active_run':[]},{'state_version':1,'active_run':False}):
            (self.root/'AI_FILM_PROJECT_STATE_V1.json').write_text(json.dumps(data))
            p=self.run_checker('--schema-only')
            self.assertNotEqual(p.returncode,0)
            self.assertIn('active-run-schema',p.stdout)

    def test_remote_run_status_parity(self):
        self.prepare_remote()
        selected=self.root/'AI_FILM_PROJECT_STATE_V1.json';data=json.loads(selected.read_text())
        data['active_run']['status']='BLOCKED';selected.write_text(json.dumps(data))
        p=self.run_checker('--require-remote',repo=self.root)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('lane-run-field:STATUS',p.stdout)

    def test_remote_scope_does_not_pretend_local_worktree_verified(self):
        self.prepare_remote(local=True)
        remote=self.run_checker('--require-remote',repo=self.root)
        self.assertEqual(remote.returncode,0,remote.stdout+remote.stderr)
        self.assertIn('local=NOT_EVALUATED',remote.stdout)
        strict=self.run_checker('--require-local',repo=self.root)
        self.assertNotEqual(strict.returncode,0)
        self.assertIn('active-run-worktree-missing',strict.stdout)

    def test_required_remote_fetch_failure_is_not_schema_pass(self):
        self.prepare_checker();self.git(self.root,'init')
        self.git(self.root,'remote','add','origin',str(self.root/'no-such-repository'))
        p=self.run_checker('--require-remote',repo=self.root)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('remote-lane-fetch',p.stdout)

    def test_measurements_ignore_unselected_shadow(self):
        self.prepare_checker()
        shutil.copy2(ROOT/'PROJECT_STATE.md',self.root/'PROJECT_STATE.md')
        _,selected,_=load_selected_state(ROOT)
        shutil.copy2(selected,self.root/selected.name)
        shutil.copytree(ROOT/'learning',self.root/'learning')
        shutil.copytree(ROOT/'workflow-runs',self.root/'workflow-runs')
        (self.root/'AI_FILM_PROJECT_STATE_V99999.json').write_text('{"state_version":99999}')
        p=self.run_checker(script='check_continuity_measurements.py')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertIn('scope=STRUCTURAL_EVENT_COUNT',p.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
