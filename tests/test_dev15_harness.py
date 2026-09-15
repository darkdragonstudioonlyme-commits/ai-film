"""Author tests for the native acceptance controller; never native validation."""
import inspect,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch

from aifilm_p00 import CONTRACT_DIGEST
from aifilm_p00.codec import digest,sha256,instant
from aifilm_p00.errors import P00Error
from aifilm_p00.native.harness_cases import (
    PROCEDURES,case_ids,procedure,validate_inventory,controller_stage_indices,
)
from aifilm_p00.native.harness_controller import (validate_stage,validate_fixture_result,_validate_journal,
    _validate_preparation_action,_validate_preparation_witness,_validate_evidence,_validate_controller_step,
    _validate_controller_windows,_collector)
from aifilm_p00.native.request_entry import prepare_execution

ROOT=Path(__file__).resolve().parents[1]
H='a'*64
BUILD='b'*64


class Store:
    def __init__(self,items):self.items=items
    def get(self,role,ref):
        value=self.items[(role,ref)]
        self.last=(role,ref)
        return value


def collector():
    return {'withdrawn':False,'review_verdict':'PASS','build_digest':BUILD,'contract_digest':CONTRACT_DIGEST}


class HarnessCatalogTests(unittest.TestCase):
    def test_exact_inventory_coverage_and_digests(self):
        inventory=json.loads((ROOT/'config/required-native-test-inventory.json').read_text())
        ids=[row['case_id'] for row in inventory['cases']]
        self.assertEqual(len(ids),86);self.assertTrue(validate_inventory(ids))
        self.assertEqual(set(ids),set(case_ids()))
        for row in inventory['cases']:
            proc=procedure(row['case_id'])
            self.assertEqual(row['procedure_digest'],proc.procedure_digest)
            self.assertEqual(row['controller_stage_indices'],proc.document()['controller_stage_indices'])
            covered={i for step in proc.controller_steps for i in controller_stage_indices(proc.routes,step)}
            self.assertEqual(covered,set(range(len(proc.routes))))
            self.assertEqual(row['status'],'NOT_RUN')
            self.assertFalse(row['acceptance_closed'])

    def test_destructive_procedures_are_lab_only(self):
        for value in PROCEDURES.values():
            if value.destructive:self.assertEqual(value.environment,'LAB')

    def test_document_case_never_requires_native_stage(self):
        value=procedure('T00-01')
        self.assertEqual(value.environment,'DOCUMENT')
        self.assertFalse(value.actual_native_required)

    def test_production_prepare_seam_has_no_backend_argument(self):
        self.assertEqual(tuple(inspect.signature(prepare_execution).parameters),
                         ('root','interface','ref'))


class HarnessCliTests(unittest.TestCase):
    def run_tool(self,*args):
        return subprocess.run([sys.executable,str(ROOT/'tools/run_native_acceptance_tests.py'),*args],
                              capture_output=True,timeout=10)

    def test_list_is_metadata_only(self):
        proc=self.run_tool('--list');self.assertEqual(proc.returncode,0,proc.stderr)
        value=json.loads(proc.stdout)
        self.assertEqual(value['case_count'],86)
        self.assertEqual(value['parent_cases_executed'],0)
        self.assertTrue(all(row['actual_status']=='NOT_RUN' for row in value['cases']))

    def test_describe_is_metadata_only(self):
        proc=self.run_tool('--describe','T13-E');self.assertEqual(proc.returncode,0,proc.stderr)
        value=json.loads(proc.stdout)
        self.assertEqual(value['case_id'],'T13-E')
        self.assertEqual(value['actual_status'],'NOT_RUN')
        self.assertFalse(value['parent_case_executed'])

    def test_execute_stage_is_blocked_on_posix(self):
        proc=self.run_tool('--execute-stage','--suite-ref',H,'--fixture-result-ref','f'*64,'--case-id','T05-A','--stage','0')
        self.assertEqual(proc.returncode,11,proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['reason'],'WINDOWS_X64_REQUIRED')


class StageOracleTests(unittest.TestCase):
    suite_ref='1'*64;fixture_result_ref='2'*64;owner='S-1-5-21-1'
    suite={'execution_id':'exec-1','issued_at':'2026-09-15T00:00:00Z','expires_at':'2026-09-15T23:59:59Z',
           'build_digest':BUILD,'contract_digest':CONTRACT_DIGEST}

    def oracle_store(self,proc):
        stage_ref='3'*64;oracle_ref='4'*64;raw_ref='5'*64;collector_ref='6'*64
        witness_ref='7'*64;wraw='8'*64;action_ref='9'*64
        actual={'epoch_changed':True};run_id='run-1'
        subject=digest({'execution_id':'exec-1','suite_ref':self.suite_ref,'case_id':proc.case_id,
            'procedure_digest':proc.procedure_digest,'fixture_result_ref':self.fixture_result_ref,
            'stage_index':0,'plan_digest':H,'run_id':run_id,'oracle':'LIFECYCLE_EPOCH','host_id':'lab-host'})
        oracle={'role':'lab_case_oracle','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'execution_id':'exec-1','suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,
            'stage_index':0,'plan_digest':H,'run_id':run_id,'oracle':'LIFECYCLE_EPOCH','status':'OBSERVED',
            'actual':actual,'raw_artifact_ref':raw_ref,'collector_ref':collector_ref,'timestamp_utc':'2026-09-15T01:00:00Z'}
        stage={'role':'lab_case_stage','schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':'lab-host',
            'owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,'execution_id':'exec-1',
            'suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,'stage_index':0,'route':proc.routes[0],
            'plan_digest':H,'run_id':run_id,'normalized_exit':0,'state':'COMPLETE','journal_ref':None,'fence_digest':None,
            'oracle_refs':[oracle_ref],'evidence_refs':[],'preparation_witness_refs':[witness_ref],
            'started_at':'2026-09-15T01:30:00Z','ended_at':'2026-09-15T02:00:00Z',
            'native_execution_observed':True,'parent_case_executed':False}
        raw={'schema_version':1,'withdrawn':False,'actual_digest':digest(actual),'subject_digest':subject}
        wactual={'condition_active':True}
        wsubject=digest({'execution_id':'exec-1','suite_ref':self.suite_ref,'case_id':proc.case_id,
            'procedure_digest':proc.procedure_digest,'fixture_result_ref':self.fixture_result_ref,
            'preparation_action_ref':action_ref,'preparation_index':0,'preparation':proc.preparations[0],
            'stage_index':0,'plan_digest':H,'run_id':run_id,'host_id':'lab-host'})
        witness={'role':'lab_case_preparation_witness','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'execution_id':'exec-1','suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,
            'preparation_action_ref':action_ref,'preparation_index':0,'preparation':proc.preparations[0],
            'mode':'ARRANGE','stage_index':0,'plan_digest':H,'run_id':run_id,'status':'OBSERVED','actual':wactual,
            'raw_artifact_ref':wraw,'collector_ref':collector_ref,'observed_at':'2026-09-15T01:20:00Z',
            'valid_through':'2026-09-15T02:10:00Z'}
        wrawdoc={'schema_version':1,'withdrawn':False,'actual_digest':digest(wactual),'subject_digest':wsubject}
        store=Store({('lab_case_stage',stage_ref):stage,('lab_case_oracle',oracle_ref):oracle,
                     ('lab_case_preparation_witness',witness_ref):witness,
                     ('collector_release',collector_ref):collector(),('lab_case_artifact',raw_ref):raw,
                     ('lab_case_artifact',wraw):wrawdoc})
        return store,stage_ref,action_ref

    def test_native_stage_process_exit_without_journal_or_entry_oracle_is_rejected(self):
        proc=procedure('T05-A');store,stage_ref,action_ref=self.oracle_store(proc)
        with self.assertRaises(P00Error) as caught:
            validate_stage(store,stage_ref,proc,0,'lab-host',self.owner,self.suite_ref,self.suite,self.fixture_result_ref,[action_ref])
        self.assertEqual(caught.exception.reason,'LAB_STAGE_PROCESS_EXIT_ONLY')

    def test_stage_cannot_replay_under_another_suite(self):
        proc=procedure('T05-A');store,stage_ref,action_ref=self.oracle_store(proc)
        with self.assertRaises(P00Error) as caught:
            validate_stage(store,stage_ref,proc,0,'lab-host',self.owner,'f'*64,self.suite,self.fixture_result_ref,[action_ref])
        self.assertEqual(caught.exception.reason,'LAB_STAGE_SCHEMA')

    def test_stale_fixture_result_is_rejected(self):
        proc=procedure('T14-E');ref='8'*64;spec='9'*64
        value={'role':'lab_case_fixture_result','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'execution_id':'exec-1','suite_ref':self.suite_ref,'fixture_spec_ref':spec,
            'preparation_action_refs':['b'*64],'measurement_refs':['a'*64],'timestamp_utc':'2020-01-01T00:00:00Z'}
        with self.assertRaises(P00Error) as caught:
            validate_fixture_result(Store({('lab_case_fixture_result',ref):value}),ref,spec,proc,
                                    self.suite_ref,self.suite,'lab-host',self.owner)
        self.assertEqual(caught.exception.reason,'LAB_FIXTURE_TIME')

    def test_fabricated_journal_hash_without_matching_raw_artifact_is_rejected(self):
        proc=procedure('T05-A');ref='b'*64;rawref='c'*64;cref='d'*64;run='run-1'
        value={'role':'lab_case_journal','schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':'lab-host',
            'owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,'execution_id':'exec-1',
            'suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,'stage_index':0,'plan_digest':H,
            'run_id':run,'journal_digest':'e'*64,'raw_artifact_ref':rawref,'collector_ref':cref,
            'timestamp_utc':'2026-09-15T01:00:00Z'}
        badraw={'schema_version':1,'withdrawn':False,'actual_digest':'f'*64,'subject_digest':'0'*64}
        store=Store({('lab_case_journal',ref):value,('collector_release',cref):collector(),('lab_case_artifact',rawref):badraw})
        with self.assertRaises(P00Error) as caught:
            _validate_journal(store,ref,proc,0,'lab-host',self.owner,self.suite_ref,self.suite,
                              self.fixture_result_ref,H,run)
        self.assertEqual(caught.exception.reason,'LAB_JOURNAL_RAW_BINDING')


class CausalTraceTests(unittest.TestCase):
    suite_ref='1'*64;fixture_result_ref='2'*64;owner='S-1-5-21-1'
    suite={'execution_id':'exec-1','issued_at':'2026-09-15T00:00:00Z','expires_at':'2026-09-15T23:59:59Z',
           'build_digest':BUILD,'contract_digest':CONTRACT_DIGEST}

    def test_arranged_preparation_requires_causal_before_after_change(self):
        proc=procedure('T07-A');ref='3'*64;raw='4'*64;collector_ref='5'*64;spec='6'*64
        value={'role':'lab_case_preparation_action','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'execution_id':'exec-1','suite_ref':self.suite_ref,'fixture_spec_ref':spec,'preparation_index':0,
            'preparation':proc.preparations[0],'mode':'ARRANGE','status':'OBSERVED','before_digest':H,
            'after_digest':H,'actual':{'causal_effect_observed':True},'raw_artifact_ref':raw,
            'collector_ref':collector_ref,'started_at':'2026-09-15T01:00:00Z','ended_at':'2026-09-15T01:01:00Z'}
        store=Store({('lab_case_preparation_action',ref):value})
        with self.assertRaises(P00Error) as caught:
            _validate_preparation_action(store,ref,proc,0,self.suite_ref,self.suite,spec,'lab-host',self.owner)
        self.assertEqual(caught.exception.reason,'LAB_PREPARATION_CAUSALITY')

    def test_controller_step_must_match_exact_procedure_sequence(self):
        proc=procedure('T07-A');ref='7'*64
        value={'role':'lab_case_controller_step','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'execution_id':'exec-1','suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,
            'step_index':0,'controller_step':'RUN_SUPPORT_BUNDLE','status':'OBSERVED','actual':{'ran':True},
            'raw_artifact_ref':'8'*64,'collector_ref':'9'*64,'started_at':'2026-09-15T01:00:00Z',
            'ended_at':'2026-09-15T01:01:00Z'}
        with self.assertRaises(P00Error) as caught:
            _validate_controller_step(Store({('lab_case_controller_step',ref):value}),ref,proc,0,'lab-host',self.owner,
                                      self.suite_ref,self.suite,self.fixture_result_ref)
        self.assertEqual(caught.exception.reason,'LAB_CONTROLLER_STEP')

    def test_evidence_name_without_exact_protected_record_binding_is_rejected(self):
        proc=procedure('T05-A');ref='a'*64;raw='b'*64;collector_ref='c'*64;run='run-1'
        value={'role':'lab_case_evidence','schema_version':1,'withdrawn':False,'source_kind':'LAB','host_id':'lab-host',
            'owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,'execution_id':'exec-1',
            'suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,'stage_index':0,'plan_digest':H,
            'run_id':run,'evidence_id':'E00-14','protected_ref':'run/x#id','protected_digest':'d'*64,
            'record_digest':'e'*64,'raw_artifact_ref':raw,'collector_ref':collector_ref,
            'timestamp_utc':'2026-09-15T01:00:00Z'}
        badraw={'schema_version':1,'withdrawn':False,'actual_digest':'f'*64,'subject_digest':'0'*64}
        store=Store({('lab_case_evidence',ref):value,('collector_release',collector_ref):collector(),
                     ('lab_case_artifact',raw):badraw})
        with self.assertRaises(P00Error) as caught:
            _validate_evidence(store,ref,proc,0,'lab-host',self.owner,self.suite_ref,self.suite,
                               self.fixture_result_ref,H,run)
        self.assertEqual(caught.exception.reason,'LAB_EVIDENCE_RAW_BINDING')


class ReviewContinuityTests(unittest.TestCase):
    suite_ref='1'*64;fixture_result_ref='2'*64;owner='S-1-5-21-1'
    suite={'execution_id':'exec-1','issued_at':'2026-09-15T00:00:00Z','expires_at':'2026-09-15T23:59:59Z',
           'build_digest':BUILD,'contract_digest':CONTRACT_DIGEST}

    def test_wrong_build_or_contract_collector_is_rejected(self):
        ref='3'*64
        store=Store({('collector_release',ref):{'withdrawn':False,'review_verdict':'PASS',
            'build_digest':'0'*64,'contract_digest':CONTRACT_DIGEST}})
        with self.assertRaises(P00Error) as caught:_collector(store,ref,self.suite,'LAB_TEST_COLLECTOR')
        self.assertEqual(caught.exception.reason,'LAB_TEST_COLLECTOR')

    def test_arranged_condition_must_remain_valid_through_stage_end(self):
        proc=procedure('T07-A');ref='4'*64;action='5'*64;raw='6'*64;cref='7'*64;run='run-1'
        actual={'condition_active':True}
        subject=digest({'execution_id':'exec-1','suite_ref':self.suite_ref,'case_id':proc.case_id,
            'procedure_digest':proc.procedure_digest,'fixture_result_ref':self.fixture_result_ref,
            'preparation_action_ref':action,'preparation_index':0,'preparation':proc.preparations[0],
            'stage_index':0,'plan_digest':H,'run_id':run,'host_id':'lab-host'})
        value={'role':'lab_case_preparation_witness','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'execution_id':'exec-1','suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,
            'preparation_action_ref':action,'preparation_index':0,'preparation':proc.preparations[0],
            'mode':'ARRANGE','stage_index':0,'plan_digest':H,'run_id':run,'status':'OBSERVED','actual':actual,
            'raw_artifact_ref':raw,'collector_ref':cref,'observed_at':'2026-09-15T01:00:00Z',
            'valid_through':'2026-09-15T01:05:00Z'}
        store=Store({('lab_case_preparation_witness',ref):value,('collector_release',cref):collector(),
                     ('lab_case_artifact',raw):{'schema_version':1,'withdrawn':False,
                     'actual_digest':digest(actual),'subject_digest':subject}})
        with self.assertRaises(P00Error) as caught:
            _validate_preparation_witness(store,ref,proc,0,0,'lab-host',self.owner,self.suite_ref,self.suite,
                self.fixture_result_ref,action,instant('2026-09-15T01:04:00Z'),instant('2026-09-15T01:10:00Z'),H,run)
        self.assertEqual(caught.exception.reason,'LAB_PREPARATION_CONTINUITY')

    def test_controller_step_must_cover_and_overlap_bound_stage_window(self):
        proc=procedure('T07-A')
        steps=[{'record':{'relation':'OVERLAP','stage_indices':[0]},
                'start':instant('2026-09-15T03:00:00Z'),'end':instant('2026-09-15T03:05:00Z')}]
        stages=[{'start':instant('2026-09-15T01:00:00Z'),'timestamp':instant('2026-09-15T02:00:00Z')}]
        with self.assertRaises(P00Error) as caught:_validate_controller_windows(steps,stages,proc)
        self.assertEqual(caught.exception.reason,'LAB_CONTROLLER_STEP_WINDOW')

    def test_controller_step_cannot_rebind_action_to_wrong_route(self):
        proc=procedure('T05-F');ref='8'*64;raw='9'*64;cref='a'*64
        actual={'controller_observed':True}
        value={'role':'lab_case_controller_step','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','owner_sid':self.owner,'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'execution_id':'exec-1','suite_ref':self.suite_ref,'fixture_result_ref':self.fixture_result_ref,
            'step_index':0,'controller_step':'RUN_TERMINAL_SWEEP','relation':'OVERLAP','stage_indices':[1],
            'status':'OBSERVED','actual':actual,'raw_artifact_ref':raw,'collector_ref':cref,
            'started_at':'2026-09-15T01:00:00Z','ended_at':'2026-09-15T02:00:00Z'}
        store=Store({('lab_case_controller_step',ref):value,('collector_release',cref):collector()})
        with self.assertRaises(P00Error) as caught:
            _validate_controller_step(store,ref,proc,0,'lab-host',self.owner,self.suite_ref,self.suite,self.fixture_result_ref)
        self.assertEqual(caught.exception.reason,'LAB_CONTROLLER_STEP')


if __name__=='__main__':unittest.main()
