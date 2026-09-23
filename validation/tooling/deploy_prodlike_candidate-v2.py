#!/usr/bin/env python3
"""Review-gated prodlike deployment transaction. Default is plan-only."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from deployment_transaction_common import (
    Runner, SubprocessRunner, TxnError, UnknownCommandCompletion, append_event,
    assert_input_hashes, atomic_json, atomic_symlink, begin_transaction,
    copy_file_exact, load_authorization, load_json, req, require_within,
    run_checked, set_receipt, sha_file,
)
from v02_candidate_profile import ProfileError, load_profile

TOOL = Path(__file__).resolve().parent
SYSTEMCTL = "/usr/bin/systemctl"

def _load_tool(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, TOOL / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

CONTROL_VERIFY = _load_tool("verify_prodlike_control_bundle-v2.py", "prodlike_control_verify_v2")

class DeployError(TxnError):
    pass

def tree_snapshot(root: str | Path) -> dict[str, dict[str, Any]]:
    root = Path(root)
    req(root.is_dir() and not root.is_symlink(), "TREE_ROOT_UNSAFE:" + str(root))
    rows = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        req(not p.is_symlink(), "TREE_MEMBER_UNSAFE:" + rel)
        if p.is_dir():
            continue
        req(p.is_file(), "TREE_MEMBER_UNSAFE:" + rel)
        rows[rel] = {
            "sha256": sha_file(p),
            "bytes": p.stat().st_size,
            "mode": format(p.stat().st_mode & 0o777, "o"),
        }
    return rows

def verify_release_copy(source: Path, target: Path) -> dict:
    before = tree_snapshot(source)
    after = tree_snapshot(target)
    req(before == after, "RELEASE_TREE_DRIFT")
    runtime = load_json(target / "runtime-manifest.json")
    req(runtime.get("native_execution_started") is False and
        runtime.get("native_lab_authority") is False, "RUNTIME_NATIVE_BOUNDARY")
    inv = load_json(target / "evidence/native-inventory.json")
    req(inv.get("case_count") == 86 and inv.get("actual_status") == "NOT_RUN" and
        inv.get("parent_cases_executed") == 0 and
        inv.get("qualification_issued") is False and
        inv.get("host_ready") is False, "RUNTIME_INVENTORY_BOUNDARY")
    return {"tree": before, "runtime": runtime, "inventory": inv}

def timer_names(bundle: Path) -> list[str]:
    manifest = load_json(bundle / "CONTROL_BUNDLE_MANIFEST.json")
    names = sorted(Path(x).name for x in manifest["files"]
                   if x.startswith("systemd/") and x.endswith(".timer"))
    req(len(names) == 11 and len(set(names)) == 11, "TIMER_POPULATION")
    return names

def service_for_timer(timer: str) -> str:
    req(timer.endswith(".timer"), "TIMER_NAME")
    return timer[:-6] + ".service"

def _decode(cp: subprocess.CompletedProcess) -> str:
    raw = cp.stdout if isinstance(cp.stdout, (bytes, bytearray)) else str(cp.stdout).encode()
    return raw.decode("utf-8", errors="replace").strip()

def capture_timer_state(runner: Runner, timers: list[str], authorized: list[list[str]]) -> dict:
    internal = [[SYSTEMCTL, "--user"]]
    out = {}
    for timer in timers:
        en = run_checked(runner, [SYSTEMCTL, "--user", "is-enabled", timer],
                         internal_prefixes=internal, authorized_prefixes=authorized,
                         allowed_returncodes=(0, 1, 3, 4))
        ac = run_checked(runner, [SYSTEMCTL, "--user", "is-active", timer],
                         internal_prefixes=internal, authorized_prefixes=authorized,
                         allowed_returncodes=(0, 1, 3, 4))
        out[timer] = {
            "enabled": en.returncode == 0 and _decode(en) == "enabled",
            "active": ac.returncode == 0 and _decode(ac) == "active",
            "enabled_raw": _decode(en), "active_raw": _decode(ac),
        }
    return out

def quiesce(runner: Runner, timers: list[str], authorized: list[list[str]]) -> None:
    internal = [[SYSTEMCTL, "--user"]]
    for timer in timers:
        run_checked(runner, [SYSTEMCTL, "--user", "stop", timer],
                    internal_prefixes=internal, authorized_prefixes=authorized)
        run_checked(runner, [SYSTEMCTL, "--user", "stop", service_for_timer(timer)],
                    internal_prefixes=internal, authorized_prefixes=authorized,
                    allowed_returncodes=(0, 5))

def restore_timer_state(runner: Runner, state: dict, authorized: list[list[str]]) -> None:
    internal = [[SYSTEMCTL, "--user"]]
    for timer, row in sorted(state.items()):
        cmd = "enable" if row["enabled"] else "disable"
        run_checked(runner, [SYSTEMCTL, "--user", cmd, timer],
                    internal_prefixes=internal, authorized_prefixes=authorized)
        cmd = "start" if row["active"] else "stop"
        run_checked(runner, [SYSTEMCTL, "--user", cmd, timer],
                    internal_prefixes=internal, authorized_prefixes=authorized)

def _deploy_targets(bundle: Path, bin_root: Path, unit_root: Path, config_path: Path) -> list[tuple[Path, Path, int]]:
    manifest = load_json(bundle / "CONTROL_BUNDLE_MANIFEST.json")
    rows = []
    for rel, rec in sorted(manifest["files"].items()):
        src = bundle / rel
        req(src.is_file() and not src.is_symlink(), "CONTROL_SOURCE_UNSAFE:" + rel)
        mode = int(rec["deploy_mode"], 8)
        if rel == "release-control.json":
            dst = config_path
        elif rel.startswith("scripts/"):
            dst = bin_root / rel.removeprefix("scripts/")
        elif rel.startswith("systemd/"):
            dst = unit_root / rel.removeprefix("systemd/")
        else:
            raise DeployError("CONTROL_MEMBER_PATH:" + rel)
        rows.append((src, dst, mode))
    req(len(rows) == 64, "CONTROL_FILE_COUNT")
    return rows

def capture_control_backup(rows, rollback_root: Path) -> list[dict]:
    backup_root = rollback_root / "control"
    meta = []
    for index, (_, dst, _) in enumerate(rows):
        if dst.exists() or dst.is_symlink():
            req(dst.is_file() and not dst.is_symlink(), "DEPLOYED_CONTROL_UNSAFE:" + str(dst))
            bp = backup_root / f"{index:03d}.bin"
            copy_file_exact(dst, bp, dst.stat().st_mode & 0o777)
            meta.append({"path": str(dst), "present": True, "backup": str(bp),
                         "sha256": sha_file(dst), "mode": format(dst.stat().st_mode & 0o777, "o")})
        else:
            meta.append({"path": str(dst), "present": False, "backup": None,
                         "sha256": None, "mode": None})
    atomic_json(rollback_root / "control-meta.json", meta)
    return meta

def restore_control_backup(meta: list[dict]) -> None:
    for row in meta:
        dst = Path(row["path"])
        if row["present"]:
            copy_file_exact(row["backup"], dst, int(row["mode"], 8))
        else:
            if dst.exists() or dst.is_symlink():
                req(dst.is_file() and not dst.is_symlink(), "ROLLBACK_CONTROL_UNSAFE:" + str(dst))
                dst.unlink()

def _verify_deployed(bundle, binding, binding_sha, release_target, bin_root, unit_root, config_path):
    return CONTROL_VERIFY.verify(binding, binding_sha, bundle,
                                 release_target / "runtime-manifest.json",
                                 bin_root, unit_root, config_path, release_target)

def build_plan(*, binding, binding_sha256, release_source, control_bundle,
               current_link, current_deployment_receipt, current_runtime_manifest,
               release_target, bin_root, unit_root, config_path, rollback_root) -> dict:
    profile, profile_sha = load_profile(binding, binding_sha256)
    release_source = Path(release_source); bundle = Path(control_bundle)
    release = verify_release_copy(release_source, release_source)
    req(release["runtime"].get("candidate_id") == profile["candidate_id"] and
        release["runtime"].get("candidate_binding_sha256") == profile_sha and
        release["runtime"].get("source_commit") == profile["source_commit"],
        "RELEASE_CANDIDATE_SCOPE")
    CONTROL_VERIFY.verify(binding, binding_sha256, bundle,
                          release_source / "runtime-manifest.json")
    current = Path(current_link)
    req(current.is_symlink(), "CURRENT_LINK_REQUIRED")
    old_target = os.readlink(current)
    req(Path(old_target).name == "dev22" or "dev22" in Path(old_target).name,
        "CURRENT_NOT_DEV22")
    prior = load_json(current_deployment_receipt)
    req(prior.get("kind") == "AIFILM_P00_PRODLIKE_DEV22_MIGRATION_DEPLOYMENT" and
        prior.get("status") == "PASS" and prior.get("current_release") == old_target and
        prior.get("production_like_status") == "READY_NON_NATIVE_PRODLIKE_OPERATIONS" and
        prior.get("native_inventory_status") == "86_NOT_RUN" and
        prior.get("native_execution_started") is False, "DEV22_DEPLOYMENT_BASELINE")
    req(prior.get("source_commit") != profile["source_commit"] and
        prior.get("package_sha256") != profile["package_sha256"], "DEV22_BASELINE_NOT_DISTINCT")
    crm = Path(current_runtime_manifest)
    req(crm.is_file() and not crm.is_symlink(), "CURRENT_RUNTIME_MANIFEST_UNSAFE")
    current_runtime = load_json(crm)
    req(sha_file(crm) == prior.get("runtime_manifest_sha256"), "DEV22_RUNTIME_RECEIPT_DRIFT")
    req(current_runtime.get("implementation_version") == "0.1.0.dev22" and
        current_runtime.get("source_commit") == prior.get("source_commit") and
        current_runtime.get("package_sha256") == prior.get("package_sha256") and
        current_runtime.get("native_execution_started") is False, "DEV22_RUNTIME_BASELINE")
    req(current.resolve(strict=False) == crm.parent.resolve(strict=False), "CURRENT_RUNTIME_PATH_DRIFT")
    timers = timer_names(bundle)
    return {
        "schema_version": 1,
        "kind": "AIFILM_P00_PRODLIKE_DEPLOYMENT_PLAN_V2",
        "status": "PLAN_ONLY",
        "candidate_id": profile["candidate_id"],
        "candidate_binding_sha256": profile_sha,
        "source_commit": profile["source_commit"],
        "old_current_target": old_target,
        "current_deployment_receipt_sha256": sha_file(current_deployment_receipt),
        "current_runtime_manifest_sha256": sha_file(current_runtime_manifest),
        "release_source": str(release_source),
        "release_target": str(release_target),
        "bin_root": str(bin_root), "unit_root": str(unit_root),
        "config_path": str(config_path), "rollback_root": str(rollback_root),
        "timers": timers,
        "mutation_started": False, "native_execution_started": False,
        "signing_performed": False, "hklm_touched": False,
    }

def execute_transaction(*, binding, binding_sha256, release_source, control_bundle,
                        current_link, current_deployment_receipt, current_runtime_manifest,
                        release_target, bin_root, unit_root, config_path, rollback_root,
                        authorization, authorization_sha256, main_commit, validation_commit,
                        executor_commit, executor_tree, receipt_path, deployment_receipt,
                        runner: Runner) -> dict:
    profile, profile_sha = load_profile(binding, binding_sha256)
    auth, auth_sha = load_authorization(
        authorization, authorization_sha256, "PRODLIKE_DEPLOYMENT_V2",
        candidate_id=profile["candidate_id"], binding_sha256=profile_sha,
        main_commit=main_commit, validation_commit=validation_commit,
        executor_commit=executor_commit, executor_tree=executor_tree,
    )
    roots = auth["mutation_roots"]
    for p in (release_target, Path(current_link).parent, bin_root, unit_root,
              Path(config_path).parent, rollback_root, Path(receipt_path).parent):
        require_within(p, roots)
    assert_input_hashes(auth, {
        "binding": binding,
        "current_deployment_receipt": current_deployment_receipt,
        "current_runtime_manifest": current_runtime_manifest,
        "release_runtime_manifest": Path(release_source) / "runtime-manifest.json",
        "control_bundle_manifest": Path(control_bundle) / "CONTROL_BUNDLE_MANIFEST.json",
    })
    receipt, fresh = begin_transaction(
        receipt_path, transaction_id=auth["transaction_id"],
        transaction_kind="PRODLIKE_DEPLOYMENT_V2",
        authorization_sha256=auth_sha, candidate_id=profile["candidate_id"],
        candidate_binding_sha256=profile_sha,
    )
    if not fresh:
        return receipt
    plan = build_plan(binding=binding, binding_sha256=binding_sha256,
                      release_source=release_source, control_bundle=control_bundle,
                      current_link=current_link, current_deployment_receipt=current_deployment_receipt,
                      current_runtime_manifest=current_runtime_manifest, release_target=release_target,
                      bin_root=bin_root, unit_root=unit_root,
                      config_path=config_path, rollback_root=rollback_root)
    authorized = auth["allowed_command_prefixes"]
    bundle = Path(control_bundle); release_source = Path(release_source)
    release_target = Path(release_target); current_link = Path(current_link)
    bin_root = Path(bin_root); unit_root = Path(unit_root); config_path = Path(config_path)
    rollback_root = Path(rollback_root)
    rows = _deploy_targets(bundle, bin_root, unit_root, config_path)
    old_target = plan["old_current_target"]
    timers = plan["timers"]
    timer_state = None
    backup_meta = None
    release_created = False
    mutation_started = False
    evidence_commit_started = False
    try:
        rollback_root.mkdir(parents=True, exist_ok=False)
        atomic_json(rollback_root / "plan.json", plan)
        timer_state = capture_timer_state(runner, timers, authorized)
        atomic_json(rollback_root / "timer-state.json", timer_state)
        backup_meta = capture_control_backup(rows, rollback_root)
        append_event(receipt_path, "ROLLBACK_CAPTURED",
                     old_current_target=old_target,
                     timer_count=len(timers),
                     control_entries=len(backup_meta))
        set_receipt(receipt_path, state="RUNNING", phase="ROLLBACK_CAPTURED")
        mutation_started = True
        set_receipt(receipt_path, mutation_started=True, phase="STAGE_RELEASE")
        if release_target.exists():
            req(release_target.is_dir() and not release_target.is_symlink(), "RELEASE_TARGET_UNSAFE")
            req(tree_snapshot(release_target) == tree_snapshot(release_source),
                "EXISTING_RELEASE_TARGET_DRIFT")
        else:
            shutil.copytree(release_source, release_target, copy_function=shutil.copy2)
            release_created = True
        verify_release_copy(release_source, release_target)
        append_event(receipt_path, "RELEASE_STAGED", target=str(release_target))

        set_receipt(receipt_path, phase="QUIESCE_USER_SYSTEMD")
        quiesce(runner, timers, authorized)
        append_event(receipt_path, "USER_SYSTEMD_QUIESCED", timer_count=len(timers))

        set_receipt(receipt_path, phase="DEPLOY_CONTROL")
        for src, dst, mode in rows:
            copy_file_exact(src, dst, mode)
        run_checked(runner, [SYSTEMCTL, "--user", "daemon-reload"],
                    internal_prefixes=[[SYSTEMCTL, "--user"]],
                    authorized_prefixes=authorized)
        _verify_deployed(bundle, binding, binding_sha256, release_target,
                         bin_root, unit_root, config_path)
        append_event(receipt_path, "CONTROL_DEPLOYED_VERIFIED")

        set_receipt(receipt_path, phase="SWITCH_CURRENT")
        atomic_symlink(str(release_target), current_link)
        req(os.readlink(current_link) == str(release_target), "CURRENT_SWITCH_READBACK")
        append_event(receipt_path, "CURRENT_SWITCHED", target=str(release_target))

        set_receipt(receipt_path, phase="START_TIMERS")
        for timer in timers:
            run_checked(runner, [SYSTEMCTL, "--user", "enable", "--now", timer],
                        internal_prefixes=[[SYSTEMCTL, "--user"]],
                        authorized_prefixes=authorized)
        live = capture_timer_state(runner, timers, authorized)
        req(all(v["enabled"] and v["active"] for v in live.values()), "LIVE_TIMER_STATE")

        verify_current = str(bin_root / "verify-current")
        runtime_health = str(bin_root / "runtime-health.py")
        run_checked(runner, [verify_current],
                    internal_prefixes=[[verify_current]],
                    authorized_prefixes=authorized)
        # Runtime health is intentionally last and cannot self-certify earlier gates.
        run_checked(runner, [runtime_health],
                    internal_prefixes=[[runtime_health]],
                    authorized_prefixes=authorized)
        deployed = _verify_deployed(bundle, binding, binding_sha256,
                                    release_target, bin_root, unit_root, config_path)
        evidence_commit_started = True
        set_receipt(receipt_path, phase="FINAL_EVIDENCE_COMMIT")
        final = {
            "schema_version": 1, "kind": "P00_PRODLIKE_CANDIDATE_DEPLOYMENT_V2", "status": "PASS",
            "candidate_id": profile["candidate_id"], "candidate_binding_sha256": profile_sha,
            "source_commit": profile["source_commit"], "implementation_version": profile["implementation_version"],
            "package_sha256": profile["package_sha256"], "wheel_sha256": profile["wheel_sha256"],
            "prior_current_target": old_target, "current_release": str(release_target),
            "prior_deployment_receipt_sha256": sha_file(current_deployment_receipt),
            "prior_runtime_manifest_sha256": sha_file(current_runtime_manifest),
            "runtime_manifest_sha256": sha_file(release_target / "runtime-manifest.json"),
            "control_bundle_manifest_sha256": sha_file(bundle / "CONTROL_BUNDLE_MANIFEST.json"),
            "timer_count": 11, "user_timer_state_checked": True,
            "rollback_evidence_path": str(rollback_root),
            "rollback_plan_sha256": sha_file(rollback_root / "plan.json"),
            "rollback_timer_state_sha256": sha_file(rollback_root / "timer-state.json"),
            "rollback_control_meta_sha256": sha_file(rollback_root / "control-meta.json"),
            "native_execution_started": False, "signing_performed": False,
            "hklm_touched": False, "site_entered": False,
            "qualification_issued": False, "host_ready": False,
        }
        atomic_json(deployment_receipt, final, 0o400)
        receipt = set_receipt(
            receipt_path, state="PASS", phase="COMMITTED",
            current_target=str(release_target),
            prior_current_target=old_target,
            deployed_verify=deployed,
            timer_state_after=live, deployment_receipt_sha256=sha_file(deployment_receipt),
            rollback_attempted=False, rollback_verified=False,
            native_execution_started=False, signing_performed=False,
            hklm_touched=False, site_entered=False,
            qualification_issued=False, host_ready=False,
        )
        append_event(receipt_path, "TRANSACTION_COMMITTED")
        return load_json(receipt_path)
    except Exception as exc:
        unknown = isinstance(exc, UnknownCommandCompletion)
        set_receipt(receipt_path, unknown_completion=unknown, failure=type(exc).__name__ + ":" + str(exc))
        if not mutation_started:
            return set_receipt(receipt_path, state="FAILED_PREMUTATION", phase="FAILED")
        if unknown:
            return set_receipt(receipt_path, state="RECONCILE_REQUIRED",
                               phase="UNKNOWN_COMPLETION", rollback_verified=False)
        if evidence_commit_started:
            return set_receipt(receipt_path, state="RECONCILE_REQUIRED",
                               phase="EVIDENCE_COMMIT_UNCERTAIN", rollback_verified=False)
        try:
            set_receipt(receipt_path, rollback_attempted=True, phase="ROLLBACK")
            # Quiesce best-effort through the same fail-closed runner.
            quiesce(runner, timers, authorized)
            if backup_meta is not None:
                restore_control_backup(backup_meta)
            atomic_symlink(old_target, current_link)
            run_checked(runner, [SYSTEMCTL, "--user", "daemon-reload"],
                        internal_prefixes=[[SYSTEMCTL, "--user"]],
                        authorized_prefixes=authorized)
            if timer_state is not None:
                restore_timer_state(runner, timer_state, authorized)
            if release_created and release_target.exists():
                shutil.rmtree(release_target)
            req(current_link.is_symlink() and os.readlink(current_link) == old_target,
                "ROLLBACK_CURRENT_VERIFY")
            if backup_meta is not None:
                for row in backup_meta:
                    dst = Path(row["path"])
                    if row["present"]:
                        req(dst.is_file() and sha_file(dst) == row["sha256"] and
                            format(dst.stat().st_mode & 0o777, "o") == row["mode"],
                            "ROLLBACK_CONTROL_VERIFY:" + str(dst))
                    else:
                        req(not dst.exists(), "ROLLBACK_ABSENT_VERIFY:" + str(dst))
            return set_receipt(receipt_path, state="FAILED_ROLLED_BACK",
                               phase="ROLLED_BACK", rollback_verified=True)
        except Exception as rollback_exc:
            return set_receipt(
                receipt_path, state="RECONCILE_REQUIRED", phase="ROLLBACK_UNCERTAIN",
                rollback_verified=False,
                rollback_failure=type(rollback_exc).__name__ + ":" + str(rollback_exc),
            )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--binding", required=True); ap.add_argument("--binding-sha256", required=True)
    ap.add_argument("--release-source", required=True); ap.add_argument("--control-bundle", required=True)
    ap.add_argument("--current-link", required=True); ap.add_argument("--current-deployment-receipt", required=True)
    ap.add_argument("--current-runtime-manifest", required=True); ap.add_argument("--release-target", required=True)
    ap.add_argument("--bin-root", required=True); ap.add_argument("--unit-root", required=True)
    ap.add_argument("--config-path", required=True); ap.add_argument("--rollback-root", required=True)
    ap.add_argument("--authorization"); ap.add_argument("--authorization-sha256")
    ap.add_argument("--main-commit"); ap.add_argument("--validation-commit")
    ap.add_argument("--executor-commit"); ap.add_argument("--executor-tree"); ap.add_argument("--receipt")
    ap.add_argument("--deployment-receipt")
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    try:
        if not a.execute:
            out = build_plan(binding=a.binding, binding_sha256=a.binding_sha256,
                             release_source=a.release_source, control_bundle=a.control_bundle,
                             current_link=a.current_link, current_deployment_receipt=a.current_deployment_receipt,
                             current_runtime_manifest=a.current_runtime_manifest, release_target=a.release_target,
                             bin_root=a.bin_root, unit_root=a.unit_root,
                             config_path=a.config_path, rollback_root=a.rollback_root)
            print(json.dumps(out, sort_keys=True, separators=(",", ":")))
            return 0
        req(all((a.authorization, a.authorization_sha256, a.main_commit, a.validation_commit,
                     a.executor_commit, a.executor_tree, a.receipt, a.deployment_receipt)), "EXECUTION_AUTHORIZATION_REQUIRED")
        out = execute_transaction(
            binding=a.binding, binding_sha256=a.binding_sha256,
            release_source=a.release_source, control_bundle=a.control_bundle,
            current_link=a.current_link, current_deployment_receipt=a.current_deployment_receipt,
            current_runtime_manifest=a.current_runtime_manifest, release_target=a.release_target,
            bin_root=a.bin_root, unit_root=a.unit_root,
            config_path=a.config_path, rollback_root=a.rollback_root,
            authorization=a.authorization, authorization_sha256=a.authorization_sha256,
            main_commit=a.main_commit, validation_commit=a.validation_commit,
            executor_commit=a.executor_commit, executor_tree=a.executor_tree, receipt_path=a.receipt,
            deployment_receipt=a.deployment_receipt, runner=SubprocessRunner(),
        )
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
        return 0 if out["state"] == "PASS" else 3
    except (ProfileError, TxnError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"kind": "AIFILM_P00_PRODLIKE_DEPLOYMENT_V2", "status": "FAIL",
                          "reason": str(exc), "deployment_started": False,
                          "native_execution_started": False, "signing_performed": False},
                         sort_keys=True, separators=(",", ":")))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
