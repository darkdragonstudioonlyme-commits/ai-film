#!/usr/bin/env python3
"""Review-gated LAB rebuild/reseed transaction. Default is plan-only; tests inject fake runners."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
from typing import Any, Sequence

from deployment_transaction_common import (
    Runner, SubprocessRunner, TxnError, UnknownCommandCompletion, append_event,
    assert_input_hashes, atomic_json, begin_transaction, copy_file_exact,
    load_authorization, load_json, req, require_within, run_checked, set_receipt,
    sha_file,
)
from v02_candidate_profile import ProfileError, load_profile

TOOL = Path(__file__).resolve().parent
WSL = "/mnt/c/Windows/System32/wsl.exe"
PRIMARY = "AI-FILM-P00-LAB"

def _load_tool(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, TOOL / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

RECEIPT_VERIFY = _load_tool("verify_lab_candidate_rebuild_receipt-v2.py", "lab_receipt_verify_v2")

class LabError(TxnError):
    pass

def _decode(cp: subprocess.CompletedProcess) -> str:
    raw = cp.stdout if isinstance(cp.stdout, (bytes, bytearray)) else str(cp.stdout).encode()
    if b"\x00" in raw:
        try:
            return raw.decode("utf-16-le", errors="replace").replace("\ufeff", "").strip()
        except UnicodeError:
            pass
    return raw.decode("utf-8", errors="replace").strip()

def _exact_run(runner: Runner, argv: Sequence[str], authorized: list[list[str]],
               *, input_path: str | Path | None = None,
               allowed_returncodes: Sequence[int] = (0,)) -> subprocess.CompletedProcess:
    exact = list(argv)
    req(exact in authorized, "COMMAND_NOT_EXACTLY_AUTHORIZED:" + json.dumps(exact))
    return run_checked(runner, exact, internal_prefixes=[exact],
                       authorized_prefixes=authorized, input_path=input_path,
                       allowed_returncodes=allowed_returncodes)

def _state(runner: Runner, distro: str, authorized: list[list[str]]) -> str | None:
    argv = [WSL, "--list", "--verbose"]
    cp = _exact_run(runner, argv, authorized)
    text = _decode(cp).replace("\x00", "")
    for raw in text.splitlines():
        line = raw.strip().lstrip("*").strip()
        if not line:
            continue
        cols = line.split()
        if cols and cols[0] == distro:
            for token in cols[1:]:
                if token.lower() in ("running", "stopped"):
                    return token.upper()
    return None

def _require_state(runner: Runner, distro: str, expected: str,
                   authorized: list[list[str]]) -> None:
    req(_state(runner, distro, authorized) == expected, "WSL_STATE:" + distro + ":" + expected)

def _guest(distro: str, *args: str, cd: str | None = None) -> list[str]:
    argv = [WSL, "--distribution", distro, "--user", "root"]
    if cd is not None:
        argv += ["--cd", cd]
    return argv + ["--exec", *args]

def _gzip_deterministic(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".tmp")
    with src.open("rb") as inp, tmp.open("wb") as out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as gz:
            shutil.copyfileobj(inp, gz, 4 * 1024 * 1024)
        out.flush(); os.fsync(out.fileno())
    os.chmod(tmp, 0o400)
    os.replace(tmp, dst)

def _validate_registration_snapshot(path: str | Path) -> dict:
    x = load_json(path)
    need = {"schema_version", "distro", "observed_state", "wsl_version",
            "install_location_windows", "observation_source"}
    req(type(x) is dict and set(x) == need and x["schema_version"] == 1,
        "REGISTRATION_SNAPSHOT_SCHEMA")
    req(x["distro"] == PRIMARY and x["observed_state"] == "STOPPED" and
        x["wsl_version"] == 2 and x["observation_source"] == "HOST_WSL_LIST",
        "REGISTRATION_SNAPSHOT_STATE")
    loc = x["install_location_windows"]
    req(isinstance(loc, str) and len(loc) >= 4 and ":" in loc, "REGISTRATION_INSTALL_LOCATION")
    return x

def _validate_prodlike_receipt(path: str | Path, profile: dict, profile_sha: str) -> dict:
    x = load_json(path)
    req(x.get("kind") == "P00_PRODLIKE_CANDIDATE_DEPLOYMENT_V2" and
        x.get("status") == "PASS" and x.get("candidate_id") == profile["candidate_id"] and
        x.get("candidate_binding_sha256") == profile_sha and
        x.get("source_commit") == profile["source_commit"] and
        x.get("implementation_version") == profile["implementation_version"] and
        x.get("package_sha256") == profile["package_sha256"] and
        x.get("wheel_sha256") == profile["wheel_sha256"] and
        x.get("native_execution_started") is False, "PRODLIKE_DEV23_RECEIPT")
    return x

def _verify_plan(plan_path: str | Path, profile: dict, profile_sha: str,
                 previous_receipt: str | Path, payload_manifest: str | Path) -> dict:
    plan = load_json(plan_path)
    req(plan.get("kind") == "P00_LAB_CANDIDATE_REBUILD_PLAN_V2" and
        plan.get("status") == "READY_FOR_SEPARATE_DEPLOYMENT_REVIEW" and
        plan.get("execution_authorized") is False and
        plan.get("lab_mutation_started") is False, "LAB_PLAN_SCHEMA")
    target = plan.get("target") or {}
    expected = {
        "candidate_id": profile["candidate_id"],
        "candidate_binding_sha256": profile_sha,
        "source_commit": profile["source_commit"],
        "implementation_version": profile["implementation_version"],
        "package_sha256": profile["package_sha256"],
        "wheel_sha256": profile["wheel_sha256"],
    }
    for key, value in expected.items():
        req(target.get(key) == value, "LAB_PLAN_TARGET:" + key)
    req(plan.get("previous_receipt_sha256") == sha_file(previous_receipt),
        "LAB_PLAN_PREVIOUS_RECEIPT")
    req(plan.get("payload_manifest_sha256") == sha_file(payload_manifest),
        "LAB_PLAN_PAYLOAD_MANIFEST")
    return plan

def build_plan(*, binding, binding_sha256, plan, payload_manifest, payload_tar,
               payload_app_manifest, wheel, prodlike_receipt, previous_lab_receipt,
               registration_snapshot, seal_root, history_root, evidence_root) -> dict:
    profile, profile_sha = load_profile(binding, binding_sha256)
    rebuild = _verify_plan(plan, profile, profile_sha, previous_lab_receipt, payload_manifest)
    _validate_prodlike_receipt(prodlike_receipt, profile, profile_sha)
    reg = _validate_registration_snapshot(registration_snapshot)
    payload = load_json(payload_manifest)
    req(payload.get("candidate_id") == profile["candidate_id"] and
        payload.get("candidate_binding_sha256") == profile_sha and
        payload.get("source_commit") == profile["source_commit"] and
        payload.get("package_sha256") == profile["package_sha256"] and
        payload.get("wheel_sha256") == profile["wheel_sha256"], "LAB_PAYLOAD_IDENTITY")
    req(sha_file(payload_tar) == payload.get("app_tar_sha256"), "LAB_PAYLOAD_TAR")
    req(sha_file(payload_app_manifest) == payload.get("app_manifest_sha256"), "LAB_APP_MANIFEST")
    req(sha_file(wheel) == profile["wheel_sha256"], "LAB_WHEEL")
    previous = load_json(previous_lab_receipt)
    req(previous.get("status") == "PASS" and previous.get("lab_state") == "STOPPED" and
        previous.get("native_execution_started") is False and
        previous.get("source_commit") != profile["source_commit"], "LAB_DEV22_BASELINE")
    return {
        "schema_version": 1,
        "kind": "AIFILM_P00_LAB_REBUILD_TRANSACTION_PLAN_V2",
        "status": "PLAN_ONLY",
        "candidate_id": profile["candidate_id"],
        "candidate_binding_sha256": profile_sha,
        "source_commit": profile["source_commit"],
        "target_runtime_root": f"/opt/ai-film-lab/runtime/{profile['implementation_version']}",
        "primary_distro": PRIMARY,
        "registration_snapshot": reg,
        "seal_root": str(seal_root),
        "history_root": str(history_root),
        "evidence_root": str(evidence_root),
        "rollback_source_commit": previous["source_commit"],
        "required_final_inventory": {"case_count": 86, "status": "NOT_RUN", "parent_cases": 0},
        "lab_mutation_started": False,
        "native_execution_started": False,
        "signing_performed": False,
        "hklm_touched": False,
    }

def _guest_verify(runner: Runner, distro: str, root: str, authorized: list[list[str]],
                  expected_version: str) -> dict:
    version_cmd = _guest(distro, f"{root}/venv/bin/python", "-m", "aifilm_p00", "--version")
    v = _decode(_exact_run(runner, version_cmd, authorized))
    req(v == expected_version, "LAB_VERSION_DRIFT")
    inventory_cmd = _guest(distro, f"{root}/venv/bin/python",
                           f"{root}/app/tools/run_native_acceptance_tests.py", "--list")
    inv_text = _decode(_exact_run(runner, inventory_cmd, authorized))
    try:
        inv = json.loads(inv_text)
    except json.JSONDecodeError as exc:
        raise LabError("LAB_INVENTORY_JSON") from exc
    req(inv.get("case_count") == 86 and inv.get("actual_status") == "NOT_RUN" and
        inv.get("parent_cases_executed") == 0 and
        inv.get("qualification_issued") is False and
        inv.get("host_ready") is False, "LAB_INVENTORY_STATE")
    hash_cmd = _guest(distro, "/usr/bin/sha256sum", "-c",
                      f"{root}/app-manifest.sha256", cd=f"{root}/app")
    _exact_run(runner, hash_cmd, authorized)
    writable_cmd = _guest(distro, "/usr/bin/find", f"{root}/app",
                          "-type", "f", "-perm", "/222", "-print")
    writable = _decode(_exact_run(runner, writable_cmd, authorized))
    req(writable == "", "LAB_APP_WRITABLE")
    conf = _decode(_exact_run(runner, _guest(distro, "/usr/bin/cat", "/etc/wsl.conf"), authorized))
    low = conf.replace(" ", "").lower()
    req("[automount]" in low and "enabled=false" in low, "LAB_AUTOMOUNT_NOT_DISABLED")
    findmnt = _exact_run(runner, _guest(distro, "/usr/bin/findmnt", "/mnt/c"), authorized,
                         allowed_returncodes=(0, 1))
    req(findmnt.returncode != 0, "LAB_WINDOWS_DRIVE_MOUNTED")
    return {"version": v, "inventory": inv, "automount_disabled": True,
            "windows_drive_mounted": False}

def _install_candidate(runner: Runner, distro: str, target: str, payload_tar: Path,
                       app_manifest: Path, wheel: Path, authorized: list[list[str]]) -> None:
    commands = [
        _guest(distro, "/usr/bin/install", "-d", "-m", "0755", target),
        _guest(distro, "/usr/bin/install", "-d", "-m", "0755", f"{target}/app"),
    ]
    for argv in commands:
        _exact_run(runner, argv, authorized)
    _exact_run(runner, _guest(distro, "/usr/bin/tar", "-xf", "-", "-C", f"{target}/app"),
               authorized, input_path=payload_tar)
    _exact_run(runner, _guest(distro, "/usr/bin/dd", f"of={target}/app-manifest.sha256", "status=none"),
               authorized, input_path=app_manifest)
    _exact_run(runner, _guest(distro, "/usr/bin/python3", "-m", "venv", f"{target}/venv"),
               authorized)
    _exact_run(runner, _guest(distro, "/usr/bin/dd", f"of={target}/candidate.whl", "status=none"),
               authorized, input_path=wheel)
    _exact_run(runner, _guest(distro, f"{target}/venv/bin/python", "-m", "pip", "install",
                              "--no-index", "--no-deps", f"{target}/candidate.whl"), authorized)
    _exact_run(runner, _guest(distro, "/usr/bin/chmod", "-R", "a-w", f"{target}/app"), authorized)
    _exact_run(runner, _guest(distro, "/usr/bin/chmod", "0444",
                              f"{target}/app-manifest.sha256", f"{target}/candidate.whl"), authorized)

def _copy_history(path: Path, history_root: Path, label: str) -> str | None:
    if not path.exists():
        return None
    req(path.is_file() and not path.is_symlink(), "HISTORICAL_SOURCE_UNSAFE")
    digest = sha_file(path)
    dst = history_root / f"{label}-{digest}.json"
    if dst.exists():
        req(sha_file(dst) == digest, "HISTORICAL_COPY_CONFLICT")
    else:
        copy_file_exact(path, dst, 0o400)
    return digest

def _make_final_evidence(*, profile: dict, profile_sha: str, plan: dict,
                         payload_manifest: Path, payload_tar: Path, payload_app_manifest: Path,
                         rollback_export: Path, pristine_raw: Path, pristine_sealed: Path,
                         restore_probe_receipt: Path, facts_path: Path, seal_path: Path,
                         seal_root: Path, previous_lab_receipt: dict,
                         deployment_receipt: Path, primary_meta: dict) -> dict:
    evidence_root = restore_probe_receipt.parent
    runtime_evidence = evidence_root / "lab-runtime-manifest.json"
    inventory_evidence = evidence_root / "native-inventory.json"
    atomic_json(runtime_evidence, {
        "schema_version": 1, "kind": "P00_LAB_RUNTIME_MANIFEST_V2",
        "candidate_id": profile["candidate_id"], "candidate_binding_sha256": profile_sha,
        "source_commit": profile["source_commit"], "implementation_version": profile["implementation_version"],
        "package_sha256": profile["package_sha256"], "wheel_sha256": profile["wheel_sha256"],
        "app_tar_sha256": plan["target"]["app_tar_sha256"],
        "app_manifest_sha256": plan["target"]["app_manifest_sha256"],
        "native_execution_started": False, "host_ready": False, "qualification_issued": False,
    }, 0o400)
    atomic_json(inventory_evidence, primary_meta["inventory"], 0o400)
    facts = {
        "schema_version": 1, "kind": "P00_LAB_TECHNICAL_FACTS_V2",
        "candidate_id": profile["candidate_id"], "candidate_binding_sha256": profile_sha,
        "source_commit": profile["source_commit"], "implementation_version": profile["implementation_version"],
        "package_sha256": profile["package_sha256"], "wheel_sha256": profile["wheel_sha256"],
        "lab_state": "STOPPED", "inventory_case_count": 86, "inventory_status": "NOT_RUN",
        "parent_cases_executed": 0, "restore_probe": "PASS", "restore_probe_unregistered": True,
        "authority_envelope_created": False, "native_execution_started": False,
        "v03_started": False,
    }
    atomic_json(facts_path, facts, 0o400)
    rows = []
    for p in (payload_manifest, payload_tar, payload_app_manifest, rollback_export,
              pristine_raw, pristine_sealed, restore_probe_receipt, runtime_evidence,
              inventory_evidence, facts_path):
        req(p.is_file() and not p.is_symlink(), "SEAL_ARTIFACT_UNSAFE:" + str(p))
        dst = seal_root / p.name
        if p.resolve() != dst.resolve():
            copy_file_exact(p, dst, 0o400)
        else:
            os.chmod(dst, 0o400)
        rows.append({"name": dst.name, "bytes": dst.stat().st_size, "sha256": sha_file(dst)})
    seal = {
        "candidate_id": profile["candidate_id"],
        "candidate_binding_sha256": profile_sha,
        "source_commit": profile["source_commit"],
        "pristine_restore_probe": "PASS",
        "artifacts": rows,
    }
    atomic_json(seal_path, seal, 0o400)
    rec = {
        "schema_version": 1, "kind": "P00_LAB_CANDIDATE_REBUILD_DEPLOYMENT_V2", "status": "PASS",
        "candidate_id": profile["candidate_id"], "candidate_binding_sha256": profile_sha,
        "source_commit": profile["source_commit"], "implementation_version": profile["implementation_version"],
        "package_sha256": profile["package_sha256"], "wheel_sha256": profile["wheel_sha256"],
        "app_tar_sha256": plan["target"]["app_tar_sha256"],
        "app_manifest_sha256": plan["target"]["app_manifest_sha256"],
        "runtime_manifest_sha256": sha_file(runtime_evidence),
        "inventory_sha256": sha_file(inventory_evidence),
        "inventory_case_count": 86, "inventory_status": "NOT_RUN", "parent_cases_executed": 0,
        "qualification_issued": False, "host_ready": False, "lab_state": "STOPPED",
        "pre_rebuild_export_sha256": sha_file(rollback_export),
        "pristine_raw_sha256": sha_file(pristine_raw),
        "pristine_sealed_sha256": sha_file(pristine_sealed),
        "restore_probe": "PASS", "restore_probe_unregistered": True,
        "restore_probe_receipt_sha256": sha_file(restore_probe_receipt),
        "technical_facts_sha256": sha_file(facts_path),
        "artifact_seal_sha256": sha_file(seal_path),
        "authority_envelope_created": False, "native_execution_started": False,
        "v03_started": False,
        "rollback_source_commit": previous_lab_receipt["source_commit"],
    }
    atomic_json(deployment_receipt, rec, 0o400)
    return rec

def execute_transaction(*, binding, binding_sha256, plan_path, payload_manifest, payload_tar,
                        payload_app_manifest, wheel, prodlike_receipt, previous_lab_receipt,
                        registration_snapshot, seal_root, history_root, evidence_root,
                        rollback_export, rollback_export_windows, pristine_raw,
                        pristine_raw_windows, pristine_sealed, probe_install_windows,
                        facts_path, seal_path, deployment_receipt, authorization,
                        authorization_sha256, main_commit, validation_commit, executor_commit,
                        executor_tree, transaction_receipt, runner: Runner) -> dict:
    profile, profile_sha = load_profile(binding, binding_sha256)
    plan = _verify_plan(plan_path, profile, profile_sha, previous_lab_receipt, payload_manifest)
    _validate_prodlike_receipt(prodlike_receipt, profile, profile_sha)
    reg = _validate_registration_snapshot(registration_snapshot)
    req(PureWindowsPath(rollback_export_windows).name.lower() == Path(rollback_export).name.lower(),
        "ROLLBACK_EXPORT_PATH_ALIAS")
    req(PureWindowsPath(pristine_raw_windows).name.lower() == Path(pristine_raw).name.lower(),
        "PRISTINE_EXPORT_PATH_ALIAS")
    auth, auth_sha = load_authorization(
        authorization, authorization_sha256, "LAB_REBUILD_V2",
        candidate_id=profile["candidate_id"], binding_sha256=profile_sha,
        main_commit=main_commit, validation_commit=validation_commit,
        executor_commit=executor_commit, executor_tree=executor_tree,
    )
    roots = auth["mutation_roots"]
    for path in (seal_root, history_root, evidence_root, Path(rollback_export).parent,
                 Path(pristine_raw).parent, Path(pristine_sealed).parent,
                 Path(facts_path).parent, Path(deployment_receipt).parent,
                 Path(transaction_receipt).parent):
        require_within(path, roots)
    immutable_inputs = {
        "binding": binding, "plan": plan_path, "payload_manifest": payload_manifest,
        "payload_tar": payload_tar, "payload_app_manifest": payload_app_manifest,
        "wheel": wheel, "prodlike_receipt": prodlike_receipt,
        "previous_lab_receipt": previous_lab_receipt,
        "registration_snapshot": registration_snapshot,
    }
    assert_input_hashes(auth, immutable_inputs)
    authorized = auth["allowed_command_prefixes"]
    receipt, fresh = begin_transaction(
        transaction_receipt, transaction_id=auth["transaction_id"],
        transaction_kind="LAB_REBUILD_V2", authorization_sha256=auth_sha,
        candidate_id=profile["candidate_id"], candidate_binding_sha256=profile_sha,
    )
    if not fresh:
        return receipt
    seal_root = Path(seal_root); history_root = Path(history_root); evidence_root = Path(evidence_root)
    rollback_export = Path(rollback_export); pristine_raw = Path(pristine_raw)
    pristine_sealed = Path(pristine_sealed); facts_path = Path(facts_path)
    seal_path = Path(seal_path); deployment_receipt = Path(deployment_receipt)
    payload_manifest = Path(payload_manifest); payload_tar = Path(payload_tar)
    payload_app_manifest = Path(payload_app_manifest); wheel = Path(wheel)
    previous = load_json(previous_lab_receipt)
    history_root.mkdir(parents=True, exist_ok=True)
    evidence_root.mkdir(parents=True, exist_ok=True)
    seal_root.mkdir(parents=True, exist_ok=True)
    target = f"/opt/ai-film-lab/runtime/{profile['implementation_version']}"
    probe = "AI-FILM-P00-LAB-RP-" + hashlib.sha256(auth["transaction_id"].encode()).hexdigest()[:8]
    mutation_started = False
    probe_registered = False
    probe_import_attempted = False
    evidence_commit_started = False
    try:
        previous_baseline = load_json(previous_lab_receipt)
        req(facts_path.is_file() and sha_file(facts_path) == previous_baseline.get("technical_facts_sha256"),
            "DEV22_TECHNICAL_FACTS_DRIFT")
        req(seal_path.is_file() and sha_file(seal_path) == previous_baseline.get("artifact_seal_sha256"),
            "DEV22_ARTIFACT_SEAL_DRIFT")
        req(auth["input_sha256"].get("current_technical_facts") == sha_file(facts_path),
            "INPUT_HASH_DRIFT:current_technical_facts")
        req(auth["input_sha256"].get("current_artifact_seal") == sha_file(seal_path),
            "INPUT_HASH_DRIFT:current_artifact_seal")
        _require_state(runner, PRIMARY, "STOPPED", authorized)
        append_event(transaction_receipt, "LAB_STOPPED_PREFLIGHT")
        export_rollback = [WSL, "--export", PRIMARY, rollback_export_windows, "--format", "tar"]
        _exact_run(runner, export_rollback, authorized)
        req(rollback_export.is_file() and rollback_export.stat().st_size > 0, "ROLLBACK_EXPORT_MISSING")
        rollback_sha = sha_file(rollback_export)
        append_event(transaction_receipt, "ROLLBACK_EXPORT_CAPTURED",
                     sha256=rollback_sha, bytes=rollback_export.stat().st_size)
        set_receipt(transaction_receipt, state="RUNNING", phase="ROLLBACK_CAPTURED")

        mutation_started = True
        set_receipt(transaction_receipt, mutation_started=True, phase="INSTALL_CANDIDATE")
        _install_candidate(runner, PRIMARY, target, payload_tar, payload_app_manifest, wheel, authorized)
        primary_meta = _guest_verify(runner, PRIMARY, target, authorized, profile["implementation_version"])
        append_event(transaction_receipt, "PRIMARY_METADATA_VERIFIED",
                     version=primary_meta["version"], case_count=86)

        _exact_run(runner, [WSL, "--terminate", PRIMARY], authorized)
        _require_state(runner, PRIMARY, "STOPPED", authorized)
        set_receipt(transaction_receipt, phase="PRISTINE_EXPORT")
        _exact_run(runner, [WSL, "--export", PRIMARY, pristine_raw_windows, "--format", "tar"], authorized)
        req(pristine_raw.is_file() and pristine_raw.stat().st_size > 0, "PRISTINE_EXPORT_MISSING")
        _gzip_deterministic(pristine_raw, pristine_sealed)
        append_event(transaction_receipt, "PRISTINE_EXPORT_CAPTURED",
                     raw_sha256=sha_file(pristine_raw), sealed_sha256=sha_file(pristine_sealed))

        set_receipt(transaction_receipt, phase="RESTORE_PROBE")
        probe_import_attempted = True
        _exact_run(runner, [WSL, "--import", probe, probe_install_windows,
                            pristine_raw_windows, "--version", "2"], authorized)
        probe_registered = True
        probe_meta = _guest_verify(runner, probe, target, authorized, profile["implementation_version"])
        _exact_run(runner, [WSL, "--terminate", probe], authorized)
        _exact_run(runner, [WSL, "--unregister", probe], authorized)
        probe_registered = False
        req(_state(runner, probe, authorized) is None, "RESTORE_PROBE_STILL_REGISTERED")
        _require_state(runner, PRIMARY, "STOPPED", authorized)
        probe_receipt = evidence_root / "restore-probe-receipt.json"
        atomic_json(probe_receipt, {
            "schema_version": 1, "kind": "P00_LAB_RESTORE_PROBE_V2", "status": "PASS",
            "probe_distro": probe, "unregistered": True,
            "candidate_id": profile["candidate_id"], "candidate_binding_sha256": profile_sha,
            "source_commit": profile["source_commit"], "version": probe_meta["version"],
            "inventory_case_count": 86, "inventory_status": "NOT_RUN",
            "native_execution_started": False,
        }, 0o400)
        append_event(transaction_receipt, "RESTORE_PROBE_PASS", probe=probe)

        # Preserve prior canonical facts/seal before replacement, but only after probe PASS.
        evidence_commit_started = True
        set_receipt(transaction_receipt, phase="FINAL_EVIDENCE_COMMIT")
        old_facts_sha = _copy_history(facts_path, history_root, "technical-facts")
        old_seal_sha = _copy_history(seal_path, history_root, "artifact-seal")
        rec = _make_final_evidence(
            profile=profile, profile_sha=profile_sha, plan=plan,
            payload_manifest=payload_manifest, payload_tar=payload_tar,
            payload_app_manifest=payload_app_manifest, rollback_export=rollback_export,
            pristine_raw=pristine_raw, pristine_sealed=pristine_sealed,
            restore_probe_receipt=probe_receipt, facts_path=facts_path, seal_path=seal_path,
            seal_root=seal_root, previous_lab_receipt=previous,
            deployment_receipt=deployment_receipt, primary_meta=primary_meta,
        )
        verified = RECEIPT_VERIFY.verify(binding, binding_sha256, plan_path,
                                          deployment_receipt, seal_root)
        req(verified.get("status") == "PASS", "FINAL_RECEIPT_VERIFY")
        set_receipt(transaction_receipt, state="PASS", phase="COMMITTED",
                    rollback_export_sha256=rollback_sha,
                    pristine_raw_sha256=sha_file(pristine_raw),
                    pristine_sealed_sha256=sha_file(pristine_sealed),
                    deployment_receipt_sha256=sha_file(deployment_receipt),
                    prior_facts_sha256=old_facts_sha, prior_seal_sha256=old_seal_sha,
                    primary_state="STOPPED", restore_probe_unregistered=True,
                    native_execution_started=False, signing_performed=False,
                    hklm_touched=False, site_entered=False,
                    qualification_issued=False, host_ready=False)
        append_event(transaction_receipt, "TRANSACTION_COMMITTED")
        return load_json(transaction_receipt)
    except Exception as exc:
        unknown = isinstance(exc, UnknownCommandCompletion)
        set_receipt(transaction_receipt, unknown_completion=unknown,
                    failure=type(exc).__name__ + ":" + str(exc))
        if not mutation_started:
            return set_receipt(transaction_receipt, state="FAILED_PREMUTATION", phase="FAILED")
        if unknown:
            # Unknown command completion is never replayed or followed by another destructive guess.
            return set_receipt(transaction_receipt, state="RECONCILE_REQUIRED",
                               phase="UNKNOWN_COMPLETION", rollback_verified=False,
                               probe_may_be_registered=(probe_registered or probe_import_attempted))
        if evidence_commit_started:
            return set_receipt(transaction_receipt, state="RECONCILE_REQUIRED",
                               phase="EVIDENCE_COMMIT_UNCERTAIN", rollback_verified=False,
                               probe_may_be_registered=probe_registered)
        try:
            set_receipt(transaction_receipt, rollback_attempted=True, phase="ROLLBACK")
            if probe_registered:
                _exact_run(runner, [WSL, "--terminate", probe], authorized, allowed_returncodes=(0,))
                _exact_run(runner, [WSL, "--unregister", probe], authorized)
                probe_registered = False
                req(_state(runner, probe, authorized) is None, "ROLLBACK_PROBE_STILL_REGISTERED")
            _exact_run(runner, [WSL, "--terminate", PRIMARY], authorized,
                       allowed_returncodes=(0,))
            _exact_run(runner, [WSL, "--unregister", PRIMARY], authorized)
            _exact_run(runner, [WSL, "--import", PRIMARY, reg["install_location_windows"],
                                rollback_export_windows, "--version", "2"], authorized)
            _exact_run(runner, [WSL, "--terminate", PRIMARY], authorized)
            _require_state(runner, PRIMARY, "STOPPED", authorized)
            return set_receipt(transaction_receipt, state="FAILED_ROLLED_BACK",
                               phase="ROLLED_BACK", rollback_verified=True,
                               rollback_export_sha256=sha_file(rollback_export))
        except Exception as rollback_exc:
            return set_receipt(
                transaction_receipt, state="RECONCILE_REQUIRED",
                phase="ROLLBACK_UNCERTAIN", rollback_verified=False,
                rollback_failure=type(rollback_exc).__name__ + ":" + str(rollback_exc),
            )

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--binding", required=True); ap.add_argument("--binding-sha256", required=True)
    ap.add_argument("--plan", required=True); ap.add_argument("--payload-manifest", required=True)
    ap.add_argument("--payload-tar", required=True); ap.add_argument("--payload-app-manifest", required=True)
    ap.add_argument("--wheel", required=True); ap.add_argument("--prodlike-receipt", required=True)
    ap.add_argument("--previous-lab-receipt", required=True); ap.add_argument("--registration-snapshot", required=True)
    ap.add_argument("--seal-root", required=True); ap.add_argument("--history-root", required=True)
    ap.add_argument("--evidence-root", required=True); ap.add_argument("--rollback-export", required=True)
    ap.add_argument("--rollback-export-windows", required=True); ap.add_argument("--pristine-raw", required=True)
    ap.add_argument("--pristine-raw-windows", required=True); ap.add_argument("--pristine-sealed", required=True)
    ap.add_argument("--probe-install-windows", required=True); ap.add_argument("--facts-path", required=True)
    ap.add_argument("--seal-path", required=True); ap.add_argument("--deployment-receipt", required=True)
    ap.add_argument("--authorization"); ap.add_argument("--authorization-sha256")
    ap.add_argument("--main-commit"); ap.add_argument("--validation-commit")
    ap.add_argument("--executor-commit"); ap.add_argument("--executor-tree")
    ap.add_argument("--transaction-receipt"); ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    try:
        if not a.execute:
            out = build_plan(
                binding=a.binding, binding_sha256=a.binding_sha256, plan=a.plan,
                payload_manifest=a.payload_manifest, payload_tar=a.payload_tar,
                payload_app_manifest=a.payload_app_manifest, wheel=a.wheel,
                prodlike_receipt=a.prodlike_receipt, previous_lab_receipt=a.previous_lab_receipt,
                registration_snapshot=a.registration_snapshot, seal_root=a.seal_root,
                history_root=a.history_root, evidence_root=a.evidence_root,
            )
            print(json.dumps(out, sort_keys=True, separators=(",", ":")))
            return 0
        req(all((a.authorization, a.authorization_sha256, a.main_commit,
                 a.validation_commit, a.executor_commit, a.executor_tree,
                 a.transaction_receipt)), "EXECUTION_AUTHORIZATION_REQUIRED")
        out = execute_transaction(
            binding=a.binding, binding_sha256=a.binding_sha256, plan_path=a.plan,
            payload_manifest=a.payload_manifest, payload_tar=a.payload_tar,
            payload_app_manifest=a.payload_app_manifest, wheel=a.wheel,
            prodlike_receipt=a.prodlike_receipt, previous_lab_receipt=a.previous_lab_receipt,
            registration_snapshot=a.registration_snapshot, seal_root=a.seal_root,
            history_root=a.history_root, evidence_root=a.evidence_root,
            rollback_export=a.rollback_export, rollback_export_windows=a.rollback_export_windows,
            pristine_raw=a.pristine_raw, pristine_raw_windows=a.pristine_raw_windows,
            pristine_sealed=a.pristine_sealed, probe_install_windows=a.probe_install_windows,
            facts_path=a.facts_path, seal_path=a.seal_path,
            deployment_receipt=a.deployment_receipt,
            authorization=a.authorization, authorization_sha256=a.authorization_sha256,
            main_commit=a.main_commit, validation_commit=a.validation_commit,
            executor_commit=a.executor_commit, executor_tree=a.executor_tree,
            transaction_receipt=a.transaction_receipt, runner=SubprocessRunner(),
        )
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
        return 0 if out["state"] == "PASS" else 3
    except (ProfileError, TxnError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"kind": "AIFILM_P00_LAB_REBUILD_V2", "status": "FAIL",
                          "reason": str(exc), "lab_mutation_started": False,
                          "native_execution_started": False, "signing_performed": False},
                         sort_keys=True, separators=(",", ":")))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
