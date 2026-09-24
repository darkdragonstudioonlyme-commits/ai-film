#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, time
from pathlib import Path
from deployment_transaction_common import (
    SubprocessRunner, UnknownCommandCompletion, append_event, assert_input_hashes,
    atomic_json, atomic_symlink, begin_transaction, copy_file_exact, load_authorization,
    load_json, minimal_subprocess_env, req, require_within, run_checked, set_receipt,
    sha_file, validated_user_bus_env,
)

SYSTEMCTL="/usr/bin/systemctl"
TX_KIND="PRODLIKE_RECONCILIATION_V1"
OLD_TX="PRODLIKE-DEV23-CORRECTED-96F4EA3-005"
DEV22="/home/dragon/ai-film-runtime/dev22"
DEV23="/home/dragon/ai-film-runtime/dev23"
DEV23_CORRECTED="/home/dragon/ai-film-runtime/dev23-corrected"
CURRENT="/home/dragon/ai-film-runtime/current"
VERIFY_CURRENT="/home/dragon/ai-film-runtime/bin/verify-current"

def service_for_timer(timer:str)->str:
    req(timer.endswith(".timer"),"TIMER_NAME")
    return timer[:-6]+".service"

def decode(cp):
    raw=cp.stdout if isinstance(cp.stdout,(bytes,bytearray)) else str(cp.stdout).encode()
    return raw.decode("utf-8",errors="replace").strip()

def decode_err(cp):
    raw=cp.stderr if isinstance(cp.stderr,(bytes,bytearray)) else str(cp.stderr).encode()
    return raw.decode("utf-8",errors="replace").strip()

def timer_state_live(runner,timers,authorized):
    out={}
    internal=[[SYSTEMCTL,"--user"]]
    for timer in timers:
        en=run_checked(runner,[SYSTEMCTL,"--user","is-enabled",timer],
            internal_prefixes=internal,authorized_prefixes=authorized,allowed_returncodes=(0,1,3,4))
        ac=run_checked(runner,[SYSTEMCTL,"--user","is-active",timer],
            internal_prefixes=internal,authorized_prefixes=authorized,allowed_returncodes=(0,1,3,4))
        er,ar=decode(en),decode(ac); ee,ae=decode_err(en),decode_err(ac)
        req(not ee and not ae,"TIMER_QUERY_STDERR")
        req(er=="enabled" and en.returncode==0,"TIMER_NOT_ENABLED:"+timer+":"+er)
        req(ar=="active" and ac.returncode==0,"TIMER_NOT_ACTIVE:"+timer+":"+ar)
        out[timer]={"enabled":True,"active":True,"enabled_raw":er,"active_raw":ar}
    return out

def tree_snapshot(root):
    root=Path(root)
    req(root.is_dir() and not root.is_symlink(),"TREE_ROOT_UNSAFE:"+str(root))
    rows={}
    for p in sorted(root.rglob("*")):
        rel=p.relative_to(root).as_posix()
        if p.is_symlink():
            rows[rel]={"type":"symlink","target":os.readlink(p)}
        elif p.is_file():
            st=p.stat(); rows[rel]={"type":"file","sha256":sha_file(p),"bytes":st.st_size,"mode":format(st.st_mode&0o777,"o")}
        elif p.is_dir():
            rows[rel]={"type":"dir","mode":format(p.stat().st_mode&0o777,"o")}
        else:
            req(False,"TREE_ENTRY_UNSUPPORTED:"+str(p))
    return rows

def snapshot_digest(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def command_prefixes(timers):
    rows=[]
    for timer in timers:
        rows += [
            [SYSTEMCTL,"--user","stop",timer],
            [SYSTEMCTL,"--user","stop",service_for_timer(timer)],
            [SYSTEMCTL,"--user","enable",timer],
            [SYSTEMCTL,"--user","start",timer],
            [SYSTEMCTL,"--user","is-enabled",timer],
            [SYSTEMCTL,"--user","is-active",timer],
        ]
    rows += [[SYSTEMCTL,"--user","daemon-reload"],[VERIFY_CURRENT]]
    return rows

def validate_inputs(args):
    receipt=load_json(args.transaction_receipt)
    req(receipt.get("transaction_id")==OLD_TX,"SOURCE_RECEIPT_ID")
    req(receipt.get("state")=="RECONCILE_REQUIRED" and receipt.get("unknown_completion") is True
        and receipt.get("mutation_started") is True and receipt.get("rollback_attempted") is False,
        "SOURCE_RECEIPT_STATE")
    witness=load_json(args.host_witness)
    req(witness.get("current_target")==DEV23_CORRECTED, "HOST_WITNESS_CURRENT")
    req(witness.get("all_live_timers_enabled_active") is True and witness.get("deployment_receipt_exists") is False,
        "HOST_WITNESS_STATE")
    req(isinstance(witness.get("broken_dev23_runtime_manifest_sha256"),str) and
        isinstance(witness.get("corrected_runtime_manifest_sha256"),str), "HOST_WITNESS_FAILED_TREES")
    plan=load_json(args.rollback_plan)
    timers=plan.get("timers")
    req(plan.get("old_current_target")==DEV22 and type(timers) is list and len(timers)==11 and len(set(timers))==11,
        "ROLLBACK_PLAN")
    state=load_json(args.rollback_timer_state)
    req(set(state)==set(timers),"ROLLBACK_TIMER_SET")
    req(all(row=={"enabled":True,"active":True,"enabled_raw":"enabled","active_raw":"active"} for row in state.values()),
        "ROLLBACK_TIMER_STATE")
    meta=load_json(args.rollback_control_meta)
    req(type(meta) is list and len(meta)==64,"ROLLBACK_CONTROL_COUNT")
    for row in meta:
        req(type(row) is dict and isinstance(row.get("path"),str),"ROLLBACK_CONTROL_SCHEMA")
        if row.get("present"):
            bp=Path(row["backup"])
            req(bp.is_file() and not bp.is_symlink(),"ROLLBACK_BACKUP_MISSING:"+str(bp))
            req(sha_file(bp)==row["sha256"],"ROLLBACK_BACKUP_HASH:"+str(bp))
            req(format(bp.stat().st_mode & 0o777,"o")==row["mode"],"ROLLBACK_BACKUP_MODE:"+str(bp))
    dev22=load_json(args.dev22_runtime_manifest)
    req(dev22.get("implementation_version")=="0.1.0.dev22" and
        dev22.get("source_commit")=="86bb64938a136e3f8d6cfd0266685a01cb832b77",
        "DEV22_MANIFEST")
    req(dev22.get("verify_runtime_sha256")==sha_file(args.dev22_verify_runtime),"DEV22_VERIFY_RUNTIME")
    return receipt,witness,plan,state,meta,timers

def build_plan(args):
    receipt,witness,rollback_plan,timer_state,meta,timers=validate_inputs(args)
    return {
        "schema_version":1,
        "kind":"AIFILM_P00_PRODLIKE_RECONCILIATION_PLAN_V1",
        "status":"PLAN_ONLY",
        "source_transaction_id":OLD_TX,
        "source_transaction_receipt_sha256":sha_file(args.transaction_receipt),
        "observed_current_target":witness["current_target"],
        "reconciliation_target":DEV22,
        "staged_dev23_disposition":"PRESERVE_UNMODIFIED_AS_FAILED_EVIDENCE",
        "staged_dev23_corrected_disposition":"PRESERVE_UNMODIFIED_AS_FAILED_EVIDENCE",
        "control_entry_count":len(meta),
        "timer_count":len(timers),
        "timers":timers,
        "required_steps":[
            "QUIESCE_REVIEWED_11_TIMER_SERVICE_SET",
            "RESTORE_EXACT_64_CAPTURED_CONTROL_ENTRIES",
            "ATOMIC_SWITCH_CURRENT_TO_DEV22",
            "SYSTEMD_USER_DAEMON_RELOAD",
            "RESTORE_CAPTURED_11_TIMER_ENABLED_ACTIVE_STATE",
            "VERIFY_CURRENT_PASS",
            "VERIFY_ALL_11_TIMERS_ENABLED_ACTIVE",
            "PERSIST_RECONCILIATION_RECEIPT",
            "REQUIRE_SEPARATE_CANONICAL_DEV22_LIVE_VERIFICATION",
        ],
        "allowed_command_prefixes":command_prefixes(timers),
        "mutation_roots":[
            "/home/dragon/ai-film-runtime",
            "/home/dragon/.config/systemd/user",
            str(Path(args.receipt).parent),
        ],
        "native_execution_started":False,
        "signing_performed":False,
        "hklm_touched":False,
        "site_entered":False,
        "qualification_issued":False,
        "host_ready":False,
    }

def restore_controls(meta,roots):
    for row in meta:
        dst=Path(row["path"]); require_within(dst,roots)
        if row["present"]:
            copy_file_exact(row["backup"],dst,int(row["mode"],8))
        else:
            if dst.exists() or dst.is_symlink():
                req(dst.is_file() and not dst.is_symlink(),"ROLLBACK_CONTROL_UNSAFE:"+str(dst))
                dst.unlink()

def execute(args):
    receipt0,witness,plan0,timer_state,meta,timers=validate_inputs(args)
    auth,auth_sha=load_authorization(
        args.authorization,args.authorization_sha256,TX_KIND,
        candidate_id=args.candidate_id,binding_sha256=args.candidate_binding_sha256,
        main_commit=args.main_commit,validation_commit=args.validation_commit,
        executor_commit=args.executor_commit,executor_tree=args.executor_tree,
    )
    assert_input_hashes(auth,{
        "reconciliation_script":Path(__file__),
        "transaction_common":Path(__file__).with_name("deployment_transaction_common.py"),
        "transaction004_receipt":args.transaction_receipt,
        "host_witness":args.host_witness,
        "rollback_plan":args.rollback_plan,
        "rollback_timer_state":args.rollback_timer_state,
        "rollback_control_meta":args.rollback_control_meta,
        "dev22_runtime_manifest":args.dev22_runtime_manifest,
        "dev22_verify_runtime":args.dev22_verify_runtime,
    })
    roots=auth["mutation_roots"]
    for p in [CURRENT,*[row["path"] for row in meta],Path(args.receipt).parent]:
        require_within(p,roots)
    req(auth["allowed_command_prefixes"]==command_prefixes(timers),"AUTHORIZATION_COMMAND_SET")
    rec,fresh=begin_transaction(
        args.receipt,transaction_id=auth["transaction_id"],transaction_kind=TX_KIND,
        authorization_sha256=auth_sha,candidate_id=args.candidate_id,
        candidate_binding_sha256=args.candidate_binding_sha256,
    )
    if not fresh:
        return rec
    current=Path(CURRENT)
    req(current.is_symlink() and os.readlink(current)==DEV23_CORRECTED,"LIVE_CURRENT_PRECONDITION")
    req(sha_file(Path(DEV23)/"runtime-manifest.json")==witness["broken_dev23_runtime_manifest_sha256"],"DEV23_RUNTIME_DRIFT")
    req(sha_file(Path(DEV23_CORRECTED)/"runtime-manifest.json")==witness["corrected_runtime_manifest_sha256"],"DEV23_CORRECTED_RUNTIME_DRIFT")
    dev23_before=tree_snapshot(Path(DEV23)); dev23_corrected_before=tree_snapshot(Path(DEV23_CORRECTED))
    dev23_before_digest=snapshot_digest(dev23_before); dev23_corrected_before_digest=snapshot_digest(dev23_corrected_before)
    runner=SubprocessRunner(env={**minimal_subprocess_env(),**validated_user_bus_env()})
    authorized=auth["allowed_command_prefixes"]
    mutation=False
    try:
        atomic_json(Path(args.receipt).parent/"plan.json",build_plan(args))
        set_receipt(args.receipt,state="RUNNING",phase="PREMUTATION_VERIFIED")
        mutation=True
        set_receipt(args.receipt,mutation_started=True,phase="QUIESCE")
        internal=[[SYSTEMCTL,"--user"]]
        for timer in timers:
            run_checked(runner,[SYSTEMCTL,"--user","stop",timer],
                internal_prefixes=internal,authorized_prefixes=authorized)
            run_checked(runner,[SYSTEMCTL,"--user","stop",service_for_timer(timer)],
                internal_prefixes=internal,authorized_prefixes=authorized,allowed_returncodes=(0,5))
        append_event(args.receipt,"USER_SYSTEMD_QUIESCED",timer_count=len(timers))
        set_receipt(args.receipt,phase="RESTORE_CONTROL")
        restore_controls(meta,roots)
        append_event(args.receipt,"CONTROL_RESTORED",control_entries=len(meta))
        set_receipt(args.receipt,phase="SWITCH_CURRENT_DEV22")
        atomic_symlink(DEV22,CURRENT)
        req(os.readlink(CURRENT)==DEV22,"CURRENT_DEV22_READBACK")
        append_event(args.receipt,"CURRENT_RESTORED",target=DEV22)
        run_checked(runner,[SYSTEMCTL,"--user","daemon-reload"],
            internal_prefixes=internal,authorized_prefixes=authorized)
        set_receipt(args.receipt,phase="RESTORE_TIMERS")
        for timer in timers:
            run_checked(runner,[SYSTEMCTL,"--user","enable",timer],
                internal_prefixes=internal,authorized_prefixes=authorized)
            run_checked(runner,[SYSTEMCTL,"--user","start",timer],
                internal_prefixes=internal,authorized_prefixes=authorized)
        live=timer_state_live(runner,timers,authorized)
        set_receipt(args.receipt,phase="VERIFY_CURRENT")
        run_checked(runner,[VERIFY_CURRENT],
            internal_prefixes=[[VERIFY_CURRENT]],authorized_prefixes=authorized)
        req(Path(DEV23).is_dir() and Path(DEV23_CORRECTED).is_dir(),"FAILED_TREES_MUST_BE_PRESERVED")
        dev23_after=tree_snapshot(Path(DEV23)); dev23_corrected_after=tree_snapshot(Path(DEV23_CORRECTED))
        req(dev23_after==dev23_before,"STAGED_DEV23_DRIFT")
        req(dev23_corrected_after==dev23_corrected_before,"STAGED_DEV23_CORRECTED_DRIFT")
        rec=set_receipt(
            args.receipt,state="RECONCILED_PENDING_INDEPENDENT_VERIFY",phase="INTERNAL_VERIFY_PASS",
            current_target=DEV22,timer_state_after=live,rollback_attempted=True,rollback_verified=True,
            staged_dev23_preserved=True,staged_dev23_snapshot_sha256=dev23_before_digest,
            staged_dev23_corrected_preserved=True,staged_dev23_corrected_snapshot_sha256=dev23_corrected_before_digest,
            internal_verify_pass=True,independent_live_verification_required=True,
            independent_live_verification_status="PENDING",
            native_execution_started=False,signing_performed=False,
            hklm_touched=False,site_entered=False,qualification_issued=False,host_ready=False,
        )
        append_event(args.receipt,"RECONCILIATION_INTERNAL_PASS")
        return load_json(args.receipt)
    except Exception as exc:
        unknown=isinstance(exc,UnknownCommandCompletion)
        if mutation:
            return set_receipt(args.receipt,state="RECONCILE_REQUIRED",phase="RECONCILIATION_UNCERTAIN",
                unknown_completion=unknown,failure=type(exc).__name__+":"+str(exc),rollback_verified=False)
        return set_receipt(args.receipt,state="FAILED_PREMUTATION",phase="FAILED",
            failure=type(exc).__name__+":"+str(exc))

def main():
    ap=argparse.ArgumentParser()
    for name in ["transaction-receipt","host-witness","rollback-plan","rollback-timer-state",
                 "rollback-control-meta","dev22-runtime-manifest","dev22-verify-runtime","receipt"]:
        ap.add_argument("--"+name,required=True)
    ap.add_argument("--authorization");ap.add_argument("--authorization-sha256")
    ap.add_argument("--main-commit");ap.add_argument("--validation-commit")
    ap.add_argument("--executor-commit");ap.add_argument("--executor-tree")
    ap.add_argument("--candidate-id");ap.add_argument("--candidate-binding-sha256")
    ap.add_argument("--execute",action="store_true")
    a=ap.parse_args()
    if not a.execute:
        print(json.dumps(build_plan(a),sort_keys=True,separators=(",",":")));return 0
    for field in ("authorization","authorization_sha256","main_commit","validation_commit",
                  "executor_commit","executor_tree","candidate_id","candidate_binding_sha256"):
        req(getattr(a,field) is not None,"EXECUTION_ARG_REQUIRED:"+field)
    out=execute(a);print(json.dumps(out,sort_keys=True,separators=(",",":")))
    return 0 if out.get("state")=="RECONCILED_PENDING_INDEPENDENT_VERIFY" else 2
if __name__=="__main__": raise SystemExit(main())
