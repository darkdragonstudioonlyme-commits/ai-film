"""Author tests for the native acceptance controller; never native validation."""
import inspect,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch

from aifilm_p00.codec import digest,sha256
from aifilm_p00.errors import P00Error
from aifilm_p00.native.harness_cases import (
    PROCEDURES,case_ids,procedure,validate_inventory,
)
from aifilm_p00.native.harness_controller import validate_stage
from aifilm_p00.native.request_entry import prepare_execution

ROOT=Path(__file__).resolve().parents[1]
H='a'*64


class Store:
    def __init__(self,items):self.items=items
    def get(self,role,ref):
        value=self.items[(role,ref)]
        self.last=(role,ref)
        return value


def collector():
    return {'withdrawn':False,'review_verdict':'PASS'}


class HarnessCatalogTests(unittest.TestCase):
    def test_exact_inventory_coverage_and_digests(self):
        inventory=json.loads((ROOT/'config/required-native-test-inventory.json').read_text())
        ids=[row['case_id'] for row in inventory['cases']]
        self.assertEqual(len(ids),86);self.assertTrue(validate_inventory(ids))
        self.assertEqual(set(ids),set(case_ids()))
        for row in inventory['cases']:
            self.assertEqual(row['procedure_digest'],procedure(row['case_id']).procedure_digest)
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
        proc=self.run_tool('--execute-stage','--suite-ref',H,'--case-id','T05-A','--stage','0')
        self.assertEqual(proc.returncode,11,proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['reason'],'WINDOWS_X64_REQUIRED')


class StageOracleTests(unittest.TestCase):
    def test_native_stage_process_exit_without_journal_or_entry_oracle_is_rejected(self):
        proc=procedure('T05-A');stage_ref='b'*64;oracle_ref='c'*64;raw_ref='d'*64;collector_ref='e'*64
        actual={'epoch_changed':True}
        subject=digest({'case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
                        'stage_index':0,'oracle':'LIFECYCLE_EPOCH','host_id':'lab-host'})
        oracle={'role':'lab_case_oracle','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'stage_index':0,'oracle':'LIFECYCLE_EPOCH','status':'OBSERVED','actual':actual,
            'raw_artifact_ref':raw_ref,'collector_ref':collector_ref,'timestamp_utc':'2026-09-15T00:00:00Z'}
        stage={'role':'lab_case_stage','schema_version':1,'withdrawn':False,'source_kind':'LAB',
            'host_id':'lab-host','case_id':proc.case_id,'procedure_digest':proc.procedure_digest,
            'stage_index':0,'route':proc.routes[0],'plan_digest':H,'normalized_exit':0,'state':'COMPLETE',
            'journal_digest':None,'fence_digest':None,'oracle_refs':[oracle_ref],'evidence_ids':['E00-09'],
            'timestamp_utc':'2026-09-15T00:00:00Z','native_execution_observed':True,
            'parent_case_executed':False}
        raw={'schema_version':1,'withdrawn':False,'actual_digest':digest(actual),'subject_digest':subject}
        store=Store({('lab_case_stage',stage_ref):stage,('lab_case_oracle',oracle_ref):oracle,
                     ('collector_release',collector_ref):collector(),('lab_case_artifact',raw_ref):raw})
        with self.assertRaises(P00Error) as caught:validate_stage(store,stage_ref,proc,0,'lab-host')
        self.assertEqual(caught.exception.reason,'LAB_STAGE_PROCESS_EXIT_ONLY')


if __name__=='__main__':unittest.main()
