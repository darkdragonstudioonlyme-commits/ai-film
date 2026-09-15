"""Document/workspace commands and digest-bound native interface dispatch.

No backend/port flags. Native paths require the ACL-anchored role/digest graph,
exact reviewed code, registered class, actual observations and per-step rights.
Merely possessing this source package is not authority to call native operations.
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime,timezone
from . import __version__,CONTRACT_DIGEST
from .codec import read_json,canonical,hash_value
from .plans import make_plan
from .errors import P00Error,require


def main(argv=None):
    parser=argparse.ArgumentParser(description='Phase00 source: native execution requires later authorized review/validation gates')
    parser.add_argument('--version',action='version',version=__version__)
    sub=parser.add_subparsers(dest='interface',required=True)
    for name in ('preflight','dry-run','apply','verify','support-bundle','recovery-notes'):
        p=sub.add_parser(name)
        if name=='dry-run':
            group=p.add_mutually_exclusive_group(required=True)
            group.add_argument('--binding',type=Path,help='offline document analysis only')
            group.add_argument('--selection-ref',help='pinned binding_selection digest')
            p.add_argument('--capture-digest',help='protected native C0 capture digest; required with --selection-ref')
        if name=='preflight':
            group=p.add_mutually_exclusive_group()
            group.add_argument('--workspace-only',action='store_true')
            group.add_argument('--initialize-metadata',action='store_true')
            group.add_argument('--plan-ref',help='pinned PASSIVE or DISCOVERY execution_plan digest')
        if name in ('apply','verify','support-bundle'):
            p.add_argument('--plan-ref',help='pinned execution_plan digest; no observation or backend override')
    try:
        args=parser.parse_args(argv);root=Path(__file__).resolve().parents[2]
        if args.interface=='dry-run' and args.binding is not None:
            require(args.capture_digest is None,10,'OFFLINE_BINDING_CAPTURE_SCOPE')
            plan=make_plan(read_json(args.binding),datetime.now(timezone.utc).isoformat())
            result={'source_kind':'DOCUMENT','analysis_only':True,'native_eligibility_proven':False,
                    'plan':plan,'host_ready':False}
        elif args.interface=='dry-run':
            hash_value(args.selection_ref);hash_value(args.capture_digest)
            from .native.request_entry import draft
            result=draft(root,args.selection_ref,args.capture_digest)
        elif args.interface=='preflight' and args.workspace_only:
            result={'source_kind':'DOCUMENT','interface':'preflight','package_version':__version__,
                    'contract_digest':CONTRACT_DIGEST,'observed_windows_host':'NOT_COLLECTED',
                    'guest_status':'REQUIRES_ACTIVE_PROBE','host_ready':False}
        elif args.interface=='preflight' and not args.plan_ref:
            from .native.entry import passive_preflight,initialize_metadata
            result=initialize_metadata(root) if args.initialize_metadata else passive_preflight(root)
        elif args.interface=='recovery-notes':
            result={'source_kind':'DOCUMENT','runbook':'docs/RECOVERY.md','native_execution':False,
                    'rules':['PRESERVE_UNRESOLVED_FENCE','NO_BLIND_RETRY','NO_UNREGISTER',
                             'NO_AUTOMATIC_REBOOT','NO_SECRET_UPLOAD'],'host_ready':False}
        else:
            require(args.plan_ref is not None,10,'NATIVE_PLAN_REFERENCE_REQUIRED')
            hash_value(args.plan_ref)
            from .native.request_entry import execute
            result=execute(root,args.interface,args.plan_ref)
        code=result.get('exit',0)
        require(type(code) is int and 0<=code<=255,18,'INTERFACE_EXIT_SCHEMA')
        sys.stdout.buffer.write(canonical(result)+b'\n');return code
    except P00Error as error:
        sys.stdout.buffer.write(canonical(error.safe())+b'\n');return int(error.code)
    except (OSError,ValueError,TypeError,KeyError):
        sys.stdout.buffer.write(canonical({'exit':18,'reason':'INTERNAL_ERROR','host_ready':False})+b'\n');return 18

if __name__=='__main__':raise SystemExit(main())
