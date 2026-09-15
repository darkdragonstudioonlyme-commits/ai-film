#!/usr/bin/env python3
"""Phase00 causal acceptance controller. Metadata modes never execute cases."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

from aifilm_p00.codec import canonical,hash_value,token
from aifilm_p00.errors import P00Error,require
from aifilm_p00.native.harness_cases import PROCEDURES,procedure
from aifilm_p00.native.harness_controller import execute_stage,finalize_case


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument('--list',action='store_true')
    m.add_argument('--describe')
    m.add_argument('--execute-stage',action='store_true')
    m.add_argument('--finalize',action='store_true')
    p.add_argument('--suite-ref');p.add_argument('--case-id');p.add_argument('--stage',type=int)
    a=p.parse_args(argv)
    try:
        if a.list:
            require(a.suite_ref is None and a.case_id is None and a.stage is None,
                    10,'LIST_NOT_EXECUTION')
            value={'kind':'NATIVE_CASE_PROCEDURE_INVENTORY','actual_status':'NOT_RUN',
                   'case_count':len(PROCEDURES),
                   'cases':[{'case_id':x,'procedure_digest':PROCEDURES[x].procedure_digest,
                             'actual_status':'NOT_RUN'} for x in PROCEDURES],
                   'parent_cases_executed':0,'qualification_issued':False,
                   'host_ready':False}
        elif a.describe:
            require(a.suite_ref is None and a.case_id is None and a.stage is None,
                    10,'DESCRIBE_NOT_EXECUTION')
            proc=procedure(a.describe)
            value={**proc.document(),'procedure_digest':proc.procedure_digest,
                   'actual_status':'NOT_RUN','parent_case_executed':False,
                   'qualification_issued':False,'host_ready':False}
        elif a.execute_stage:
            hash_value(a.suite_ref);token(a.case_id)
            require(type(a.stage) is int,10,'LAB_STAGE_INDEX')
            value=execute_stage(ROOT,a.suite_ref,a.case_id,a.stage)
        else:
            hash_value(a.suite_ref);token(a.case_id)
            require(a.stage is None,10,'FINALIZE_STAGE_FORBIDDEN')
            value=finalize_case(ROOT,a.suite_ref,a.case_id)
        sys.stdout.buffer.write(canonical(value)+b'\n');return 0
    except P00Error as e:
        sys.stdout.buffer.write(canonical({**e.safe(),'actual_status':'BLOCKED_OR_FAILED',
            'qualification_issued':False})+b'\n');return int(e.code)
    except (OSError,KeyError,TypeError,ValueError):
        sys.stdout.buffer.write(canonical({'exit':18,'reason':'HARNESS_IO_OR_SCHEMA',
            'actual_status':'ERROR','host_ready':False,'qualification_issued':False})+b'\n')
        return 18

if __name__=='__main__':
    raise SystemExit(main())
