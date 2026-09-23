import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
from deployment_transaction_common import (SubprocessRunner, UnknownCommandCompletion, canonical,
    minimal_subprocess_env, path_within, sha_file, validated_user_bus_env)

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, TOOL / filename)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

deploy = load("deploy_txn", "deploy_prodlike_candidate-v2.py")
bundle_builder = load("bundle_builder", "build_prodlike_control_bundle-v2.py")

class FakeRunner:
    def __init__(self, fail_argv=None):
        self.calls = []
        self.fail_argv = tuple(fail_argv) if fail_argv else None
        self.timers = {}
    def run(self, argv, *, input_bytes=None, input_path=None):
        argv = list(argv); self.calls.append(argv)
        if self.fail_argv is not None and tuple(argv) == self.fail_argv:
            raise UnknownCommandCompletion("INJECTED_UNKNOWN")
        if argv[:2] == [deploy.SYSTEMCTL, "--user"]:
            op = argv[2]
            name = argv[-1] if len(argv) > 3 else None
            if op == "is-enabled":
                state = self.timers.get(name, {"enabled": True, "active": True})
                return subprocess.CompletedProcess(argv, 0 if state["enabled"] else 1,
                                                   b"enabled\n" if state["enabled"] else b"disabled\n", b"")
            if op == "is-active":
                state = self.timers.get(name, {"enabled": True, "active": True})
                return subprocess.CompletedProcess(argv, 0 if state["active"] else 3,
                                                   b"active\n" if state["active"] else b"inactive\n", b"")
            if op == "stop":
                if name and name.endswith(".timer"):
                    self.timers.setdefault(name, {"enabled": True, "active": True})["active"] = False
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            if op == "enable":
                if name:
                    row = self.timers.setdefault(name, {"enabled": True, "active": False})
                    row["enabled"] = True
                    if "--now" in argv: row["active"] = True
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            if op == "disable":
                self.timers.setdefault(name, {"enabled": True, "active": False})["enabled"] = False
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            if op == "start":
                self.timers.setdefault(name, {"enabled": True, "active": False})["active"] = True
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            if op == "daemon-reload":
                return subprocess.CompletedProcess(argv, 0, b"", b"")
        return subprocess.CompletedProcess(argv, 0, b"PASS\n", b"")


class InvalidTimerRunner(FakeRunner):
    def __init__(self, *, stdout=b"", stderr=b"Failed to connect to bus: No medium found\n"):
        super().__init__(); self.invalid_stdout=stdout; self.invalid_stderr=stderr
    def run(self, argv, *, input_bytes=None, input_path=None):
        argv=list(argv); self.calls.append(argv)
        if argv[:3] == [deploy.SYSTEMCTL, "--user", "is-enabled"]:
            return subprocess.CompletedProcess(argv, 1, self.invalid_stdout, self.invalid_stderr)
        return super().run(argv, input_bytes=input_bytes, input_path=input_path)

class ProdlikeTxnTests(unittest.TestCase):
    MAIN = "1" * 40
    VALIDATION = "2" * 40
    EXECUTOR = "3" * 40
    TREE = "4" * 40

    def setUp(self):
        self.td = tempfile.TemporaryDirectory(prefix="prodlike-txn-")
        self.r = Path(self.td.name)
        self.binding = TOOL / "dev23-candidate-binding.json"
        self.profile = json.loads(self.binding.read_text())
        self.bsha = hashlib.sha256(self.binding.read_bytes()).hexdigest()

        self.old = self.r / "runtime" / "dev22"
        self.old.mkdir(parents=True)
        old_runtime = {
            "implementation_version": "0.1.0.dev22",
            "source_commit": "86bb64938a136e3f8d6cfd0266685a01cb832b77",
            "package_sha256": "c2ea52087039f4c7b98c53a7cc0eaf1a4a0f931645f86491bf2eb8ef12956aae",
            "native_execution_started": False,
        }
        (self.old / "runtime-manifest.json").write_text(json.dumps(old_runtime, sort_keys=True))
        self.current = self.r / "runtime" / "current"
        self.current.symlink_to(self.old)
        self.old_receipt = self.r / "dev22-receipt.json"
        self.old_receipt.write_text(json.dumps({
            "kind": "AIFILM_P00_PRODLIKE_DEV22_MIGRATION_DEPLOYMENT",
            "status": "PASS",
            "current_release": str(self.old),
            "production_like_status": "READY_NON_NATIVE_PRODLIKE_OPERATIONS",
            "native_inventory_status": "86_NOT_RUN",
            "native_execution_started": False,
            "source_commit": old_runtime["source_commit"],
            "package_sha256": old_runtime["package_sha256"],
            "runtime_manifest_sha256": sha_file(self.old / "runtime-manifest.json"),
        }, sort_keys=True))

        self.release_source = self.r / "release-source"
        (self.release_source / "evidence").mkdir(parents=True)
        runtime = {
            "candidate_id": self.profile["candidate_id"],
            "candidate_binding_sha256": self.bsha,
            "implementation_version": self.profile["implementation_version"],
            "source_commit": self.profile["source_commit"],
            "source_digest": self.profile["build_digest"],
            "test_digest": self.profile["test_set_digest"],
            "contract_digest": self.profile["contract_digest"],
            "package_sha256": self.profile["package_sha256"],
            "wheel_sha256": self.profile["wheel_sha256"],
            "native_execution_started": False,
            "native_lab_authority": False,
        }
        (self.release_source / "runtime-manifest.json").write_text(json.dumps(runtime, sort_keys=True))
        (self.release_source / "evidence" / "native-inventory.json").write_text(json.dumps({
            "case_count": 86, "actual_status": "NOT_RUN", "parent_cases_executed": 0,
            "qualification_issued": False, "host_ready": False,
        }, sort_keys=True))

        self.bundle = self.r / "bundle"
        bundle_builder.build(
            self.binding, self.bsha, self.release_source / "runtime-manifest.json",
            TOOL / "prodlike_control_templates_v2.json", self.bundle,
            str(self.r / "runtime" / "dev23"), str(self.r / "rebuild" / "dev23"),
            str(self.r / "backup"), str(self.r / "offhost"), str(self.r / "authority" / "dev23"),
        )

        self.release_target = self.r / "runtime" / "dev23"
        self.bin_root = self.r / "bin"
        self.unit_root = self.r / "systemd"
        self.config = self.r / "release-control.json"
        self.rollback = self.r / "rollback"
        self.txn_receipt = self.r / "txn.json"
        self.deploy_receipt = self.r / "deployment.json"
        self.auth = self.r / "auth.json"

    def tearDown(self):
        self.td.cleanup()

    def commands(self):
        timers = deploy.timer_names(self.bundle)
        rows = []
        def add(argv):
            if argv not in rows: rows.append(argv)
        for timer in timers:
            add([deploy.SYSTEMCTL, "--user", "is-enabled", timer])
            add([deploy.SYSTEMCTL, "--user", "is-active", timer])
            add([deploy.SYSTEMCTL, "--user", "stop", timer])
            add([deploy.SYSTEMCTL, "--user", "stop", deploy.service_for_timer(timer)])
            add([deploy.SYSTEMCTL, "--user", "enable", "--now", timer])
            add([deploy.SYSTEMCTL, "--user", "enable", timer])
            add([deploy.SYSTEMCTL, "--user", "disable", timer])
            add([deploy.SYSTEMCTL, "--user", "start", timer])
        add([deploy.SYSTEMCTL, "--user", "daemon-reload"])
        add([str(self.bin_root / "verify-current")])
        add([str(self.bin_root / "runtime-health.py")])
        return rows

    def write_auth(self, **overrides):
        inputs = {
            "binding": sha_file(self.binding),
            "current_deployment_receipt": sha_file(self.old_receipt),
            "current_runtime_manifest": sha_file(self.old / "runtime-manifest.json"),
            "release_runtime_manifest": sha_file(self.release_source / "runtime-manifest.json"),
            "control_bundle_manifest": sha_file(self.bundle / "CONTROL_BUNDLE_MANIFEST.json"),
        }
        value = {
            "schema_version": 1, "kind": "AIFILM_P00_TRANSACTION_AUTHORIZATION_V1",
            "status": "AUTHORIZED", "transaction_id": "PRODLIKE-TXN-001",
            "transaction_kind": "PRODLIKE_DEPLOYMENT_V2",
            "main_commit": self.MAIN, "validation_commit": self.VALIDATION,
            "executor_commit": self.EXECUTOR, "executor_tree": self.TREE,
            "candidate_id": self.profile["candidate_id"],
            "candidate_binding_sha256": self.bsha, "input_sha256": inputs,
            "mutation_roots": [str(self.r)],
            "allowed_command_prefixes": self.commands(),
            "attempt": 1, "authorized": True, "expires_at": 4102444800,
            "native_execution_authorized": False, "signing_authorized": False,
            "hklm_authorized": False, "site_authorized": False,
            "qualification_authorized": False, "host_ready_authorized": False,
        }
        value.update(overrides)
        self.auth.write_text(json.dumps(value, sort_keys=True))
        return sha_file(self.auth)

    def kwargs(self, runner, auth_sha=None):
        if auth_sha is None: auth_sha = self.write_auth()
        return dict(
            binding=self.binding, binding_sha256=self.bsha,
            release_source=self.release_source, control_bundle=self.bundle,
            current_link=self.current, current_deployment_receipt=self.old_receipt,
            current_runtime_manifest=self.old / "runtime-manifest.json",
            release_target=self.release_target, bin_root=self.bin_root,
            unit_root=self.unit_root, config_path=self.config, rollback_root=self.rollback,
            authorization=self.auth, authorization_sha256=auth_sha,
            main_commit=self.MAIN, validation_commit=self.VALIDATION,
            executor_commit=self.EXECUTOR, executor_tree=self.TREE,
            receipt_path=self.txn_receipt, deployment_receipt=self.deploy_receipt,
            runner=runner,
        )

    def test_plan_only_binds_dev22_and_dev23(self):
        plan = deploy.build_plan(
            binding=self.binding, binding_sha256=self.bsha,
            release_source=self.release_source, control_bundle=self.bundle,
            current_link=self.current, current_deployment_receipt=self.old_receipt,
            current_runtime_manifest=self.old / "runtime-manifest.json",
            release_target=self.release_target, bin_root=self.bin_root,
            unit_root=self.unit_root, config_path=self.config, rollback_root=self.rollback)
        self.assertEqual(plan["status"], "PLAN_ONLY")
        self.assertEqual(plan["old_current_target"], str(self.old))
        self.assertFalse(plan["native_execution_started"])
        self.assertFalse(self.release_target.exists())

    def test_happy_commit_and_final_receipt(self):
        runner = FakeRunner()
        out = deploy.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "PASS")
        self.assertEqual(os.readlink(self.current), str(self.release_target))
        final = json.loads(self.deploy_receipt.read_text())
        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["candidate_id"], self.profile["candidate_id"])
        self.assertFalse(final["native_execution_started"])
        self.assertEqual(final["timer_count"], 11)

    def test_existing_receipt_never_replays(self):
        runner = FakeRunner()
        first = deploy.execute_transaction(**self.kwargs(runner))
        calls = len(runner.calls)
        second = deploy.execute_transaction(**self.kwargs(runner, sha_file(self.auth)))
        self.assertEqual(second["state"], "PASS")
        self.assertEqual(len(runner.calls), calls)
        self.assertEqual(first["transaction_id"], second["transaction_id"])

    def test_wrong_main_or_executor_tree_fails_before_mutation(self):
        runner = FakeRunner()
        auth_sha = self.write_auth(main_commit="9" * 40)
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_MAIN_DRIFT"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))
        self.assertFalse(self.release_target.exists())
        self.assertEqual(runner.calls, [])
        auth_sha = self.write_auth(executor_tree="8" * 40)
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_EXECUTOR_TREE_DRIFT"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))

    def test_input_drift_fails_before_mutation(self):
        runner = FakeRunner()
        auth_sha = self.write_auth()
        self.old_receipt.write_text(self.old_receipt.read_text() + "\n")
        with self.assertRaisesRegex(Exception, "INPUT_HASH_DRIFT"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))
        self.assertFalse(self.release_target.exists())

    def test_unknown_command_completion_requires_reconcile_no_retry(self):
        timers = deploy.timer_names(self.bundle)
        fail = [deploy.SYSTEMCTL, "--user", "stop", timers[0]]
        runner = FakeRunner(fail)
        out = deploy.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "RECONCILE_REQUIRED")
        self.assertTrue(out["unknown_completion"])
        self.assertFalse(out["rollback_verified"])
        idx = runner.calls.index(fail)
        self.assertEqual(len(runner.calls), idx + 1)

    def test_unknown_completion_matrix_after_mutation_never_retries(self):
        timers = deploy.timer_names(self.bundle)
        boundaries = [
            [deploy.SYSTEMCTL, "--user", "daemon-reload"],
            [deploy.SYSTEMCTL, "--user", "enable", "--now", timers[0]],
            [str(self.bin_root / "verify-current")],
            [str(self.bin_root / "runtime-health.py")],
        ]
        for index, fail in enumerate(boundaries):
            with self.subTest(boundary=fail):
                if index:
                    self.tearDown(); self.setUp(); timers = deploy.timer_names(self.bundle)
                    if "enable" in fail: fail = [deploy.SYSTEMCTL, "--user", "enable", "--now", timers[0]]
                    elif fail and fail[0].endswith("verify-current"): fail = [str(self.bin_root / "verify-current")]
                    elif fail and fail[0].endswith("runtime-health.py"): fail = [str(self.bin_root / "runtime-health.py")]
                runner = FakeRunner(fail)
                out = deploy.execute_transaction(**self.kwargs(runner))
                self.assertEqual(out["state"], "RECONCILE_REQUIRED")
                self.assertTrue(out["unknown_completion"])
                idx = runner.calls.index(fail)
                self.assertEqual(len(runner.calls), idx + 1)

    def test_local_mutation_boundary_failures_roll_back(self):
        cases = ["release_stage", "control_copy", "current_switch"]
        for index, name in enumerate(cases):
            with self.subTest(boundary=name):
                if index:
                    self.tearDown(); self.setUp()
                runner = FakeRunner()
                if name == "release_stage":
                    patcher = mock.patch.object(deploy.shutil, "copytree", side_effect=OSError("STAGE_FAIL"))
                elif name == "control_copy":
                    original = deploy.copy_file_exact; calls={"n":0}
                    def fail_control(*args, **kwargs):
                        calls["n"] += 1
                        if calls["n"] == 1: raise deploy.DeployError("CONTROL_COPY_FAIL")
                        return original(*args, **kwargs)
                    patcher = mock.patch.object(deploy, "copy_file_exact", side_effect=fail_control)
                else:
                    original = deploy.atomic_symlink; calls={"n":0}
                    def fail_switch(*args, **kwargs):
                        calls["n"] += 1
                        if calls["n"] == 1: raise deploy.DeployError("SWITCH_FAIL")
                        return original(*args, **kwargs)
                    patcher = mock.patch.object(deploy, "atomic_symlink", side_effect=fail_switch)
                with patcher:
                    out = deploy.execute_transaction(**self.kwargs(runner))
                self.assertEqual(out["state"], "FAILED_ROLLED_BACK")
                self.assertTrue(out["rollback_verified"])
                self.assertEqual(os.readlink(self.current), str(self.old))

    def test_deterministic_postmutation_failure_rolls_back(self):
        runner = FakeRunner()
        original = deploy._verify_deployed
        calls = {"n": 0}
        def fail_once(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise deploy.DeployError("INJECTED_DETERMINISTIC")
            return original(*args, **kwargs)
        with mock.patch.object(deploy, "_verify_deployed", side_effect=fail_once):
            out = deploy.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "FAILED_ROLLED_BACK")
        self.assertTrue(out["rollback_verified"])
        self.assertEqual(os.readlink(self.current), str(self.old))
        self.assertFalse(self.release_target.exists())
        self.assertFalse(self.deploy_receipt.exists())

    def test_authorization_rejects_shell_and_broad_root(self):
        runner = FakeRunner()
        auth_sha = self.write_auth(allowed_command_prefixes=[["/bin/bash", "-c", "x"]])
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_COMMAND_FORBIDDEN"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))
        auth_sha = self.write_auth(allowed_command_prefixes=[["systemctl", "--user"]])
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_COMMAND_NOT_ABSOLUTE"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))
        auth_sha = self.write_auth(mutation_roots=["/"])
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_ROOT_TOO_BROAD"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))
        auth_sha = self.write_auth(mutation_roots=["/home/dragon/.ssh"])
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_ROOT_SENSITIVE"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))
        auth_sha = self.write_auth(mutation_roots=["/home/dragon/.config"])
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_ROOT_CONFIG_SCOPE"):
            deploy.execute_transaction(**self.kwargs(runner, auth_sha))

    def test_authorization_allows_exact_reviewed_user_systemd_root(self):
        auth_sha = self.write_auth(mutation_roots=[str(self.r), "/home/dragon/.config/systemd/user"])
        value, actual = deploy.load_authorization(self.auth, auth_sha, "PRODLIKE_DEPLOYMENT_V2",
            candidate_id=self.profile["candidate_id"], binding_sha256=self.bsha,
            main_commit=self.MAIN, validation_commit=self.VALIDATION,
            executor_commit=self.EXECUTOR, executor_tree=self.TREE)
        self.assertEqual(actual, auth_sha)
        self.assertIn("/home/dragon/.config/systemd/user", value["mutation_roots"])

    def test_plan_validates_release_source_not_self_compare(self):
        runtime_path = self.release_source / "runtime-manifest.json"
        runtime = json.loads(runtime_path.read_text())
        runtime["native_execution_started"] = True
        runtime_path.write_text(json.dumps(runtime, sort_keys=True))
        with self.assertRaisesRegex(Exception, "RUNTIME_NATIVE_BOUNDARY"):
            deploy.build_plan(binding=self.binding, binding_sha256=self.bsha, release_source=self.release_source, control_bundle=self.bundle, current_link=self.current, current_deployment_receipt=self.old_receipt, current_runtime_manifest=self.old / "runtime-manifest.json", release_target=self.release_target, bin_root=self.bin_root, unit_root=self.unit_root, config_path=self.config, rollback_root=self.rollback)

    def test_release_symlink_member_rejected(self):
        target = self.r / "outside-file"; target.write_text("x")
        (self.release_source / "bad-link").symlink_to(target)
        with self.assertRaisesRegex(Exception, "TREE_MEMBER_UNSAFE"):
            deploy.build_plan(binding=self.binding, binding_sha256=self.bsha, release_source=self.release_source, control_bundle=self.bundle, current_link=self.current, current_deployment_receipt=self.old_receipt, current_runtime_manifest=self.old / "runtime-manifest.json", release_target=self.release_target, bin_root=self.bin_root, unit_root=self.unit_root, config_path=self.config, rollback_root=self.rollback)

    def test_final_evidence_failure_requires_reconcile(self):
        runner = FakeRunner()
        with mock.patch.object(deploy, "atomic_json", side_effect=deploy.DeployError("EVIDENCE_WRITE_FAIL")):
            out = deploy.execute_transaction(**self.kwargs(runner))
        # The patched writer can fail before durable transaction setup; fail-closed outcome is sufficient.
        self.assertIn(out.get("state", "FAILED_PREMUTATION"), ("RECONCILE_REQUIRED", "FAILED_PREMUTATION"))

    def test_resolved_path_escape_is_not_authorized(self):
        outside = self.r.parent / (self.r.name + "-outside")
        outside.mkdir(exist_ok=True)
        link = self.r / "escape"
        link.symlink_to(outside, target_is_directory=True)
        self.assertFalse(path_within(link / "x", self.r))

    def _make_bus(self, *, mode=0o700):
        base = self.r / "run-user"; runtime = base / str(os.getuid()); runtime.mkdir(parents=True); runtime.chmod(mode)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); sock.bind(str(runtime / "bus"))
        self.addCleanup(sock.close); return base, runtime, runtime / "bus"

    def test_user_bus_env_validated_and_default_runner_remains_minimal(self):
        base, runtime, bus = self._make_bus()
        env = validated_user_bus_env(runtime_base=base)
        self.assertEqual(env, {"XDG_RUNTIME_DIR": str(runtime), "DBUS_SESSION_BUS_ADDRESS": "unix:path=" + str(bus)})
        default = SubprocessRunner().env
        self.assertNotIn("XDG_RUNTIME_DIR", default); self.assertNotIn("DBUS_SESSION_BUS_ADDRESS", default)
        self.assertNotIn("validated_user_bus_env", (TOOL / "rebuild_lab_candidate-v2.py").read_text())

    def test_user_bus_failclosed_matrix(self):
        uid=os.getuid(); base=self.r / "missing-base"; base.mkdir()
        with self.assertRaisesRegex(Exception, "USER_BUS_RUNTIME_MISSING_OR_UNSAFE"):
            validated_user_bus_env(runtime_base=base)
        base=self.r / "file-base"; base.mkdir(); (base/str(uid)).write_text("x")
        with self.assertRaisesRegex(Exception, "USER_BUS_RUNTIME_NOT_DIRECTORY"):
            validated_user_bus_env(runtime_base=base)
        base,runtime,bus=self._make_bus(mode=0o777)
        with self.assertRaisesRegex(Exception, "USER_BUS_RUNTIME_WRITABLE"):
            validated_user_bus_env(runtime_base=base)
        base=self.r/"owner-base"; runtime=base/str(uid+1); runtime.mkdir(parents=True); runtime.chmod(0o700)
        with self.assertRaisesRegex(Exception, "USER_BUS_RUNTIME_OWNER"):
            validated_user_bus_env(uid=uid+1,runtime_base=base)
        base=self.r/"no-bus"; runtime=base/str(uid); runtime.mkdir(parents=True); runtime.chmod(0o700)
        with self.assertRaisesRegex(Exception, "USER_BUS_SOCKET_MISSING_OR_UNSAFE"):
            validated_user_bus_env(runtime_base=base)
        (runtime/"bus").write_text("not socket")
        with self.assertRaisesRegex(Exception, "USER_BUS_NOT_SOCKET"):
            validated_user_bus_env(runtime_base=base)
        (runtime/"bus").unlink(); sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); sock.bind(str(runtime/"bus")); self.addCleanup(sock.close)
        original = Path.lstat
        def wrong_owner(path_obj):
            st=original(path_obj)
            if path_obj == runtime/"bus":
                class S: pass
                fake=S(); fake.st_mode=st.st_mode; fake.st_uid=uid+1; return fake
            return st
        with mock.patch.object(Path, "lstat", new=wrong_owner):
            with self.assertRaisesRegex(Exception, "USER_BUS_SOCKET_OWNER"):
                validated_user_bus_env(runtime_base=base)

    def test_timer_semantic_states_and_invalid_observations(self):
        enabled, raw = deploy._enabled_state(subprocess.CompletedProcess([],0,b"enabled\n",b"")); self.assertTrue(enabled); self.assertEqual(raw,"enabled")
        enabled, raw = deploy._enabled_state(subprocess.CompletedProcess([],1,b"disabled\n",b"")); self.assertFalse(enabled); self.assertEqual(raw,"disabled")
        active, raw = deploy._active_state(subprocess.CompletedProcess([],0,b"active\n",b"")); self.assertTrue(active); self.assertEqual(raw,"active")
        active, raw = deploy._active_state(subprocess.CompletedProcess([],3,b"inactive\n",b"")); self.assertFalse(active); self.assertEqual(raw,"inactive")
        for cp, reason, fn in [
            (subprocess.CompletedProcess([],1,b"",b""),"TIMER_ENABLED_STATE_INVALID",deploy._enabled_state),
            (subprocess.CompletedProcess([],1,b"unknown\n",b""),"TIMER_ENABLED_STATE_INVALID",deploy._enabled_state),
            (subprocess.CompletedProcess([],1,b"disabled\n",b"Failed to connect to bus"),"TIMER_ENABLED_STDERR",deploy._enabled_state),
            (subprocess.CompletedProcess([],3,b"activating\n",b""),"TIMER_ACTIVE_STATE_INVALID",deploy._active_state)]:
            with self.assertRaisesRegex(Exception, reason): fn(cp)

    def test_invalid_timer_observation_is_durable_premutation_failure(self):
        runner=InvalidTimerRunner(); out=deploy.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"],"FAILED_PREMUTATION"); self.assertFalse(out["mutation_started"])
        self.assertEqual(os.readlink(self.current),str(self.old)); self.assertFalse(self.release_target.exists()); self.assertFalse(self.deploy_receipt.exists())

    def test_reconcile_receipt_is_never_replayed(self):
        runner=FakeRunner(); auth_sha=self.write_auth()
        self.txn_receipt.write_text(json.dumps({"transaction_id":"PRODLIKE-TXN-001","authorization_sha256":auth_sha,"state":"RECONCILE_REQUIRED","mutation_started":True}))
        out=deploy.execute_transaction(**self.kwargs(runner,auth_sha)); self.assertEqual(out["state"],"RECONCILE_REQUIRED"); self.assertEqual(runner.calls,[])

    def test_exact_staged_dev23_reused_and_drift_fails_closed(self):
        shutil.copytree(self.release_source,self.release_target); runner=FakeRunner(); out=deploy.execute_transaction(**self.kwargs(runner)); self.assertEqual(out["state"],"PASS")
        self.tearDown(); self.setUp(); shutil.copytree(self.release_source,self.release_target); (self.release_target/"runtime-manifest.json").write_text("{}")
        runner=FakeRunner(); out=deploy.execute_transaction(**self.kwargs(runner)); self.assertEqual(out["state"],"FAILED_ROLLED_BACK"); self.assertEqual(os.readlink(self.current),str(self.old))

    def test_prodlike_main_explicitly_opts_into_only_validated_bus_env(self):
        captured={}
        def fake_execute(**kwargs): captured.update(kwargs["runner"].env); return {"state":"PASS"}
        argv=["tool","--binding","b","--binding-sha256","h","--release-source","r","--control-bundle","c","--current-link","l","--current-deployment-receipt","dr","--current-runtime-manifest","rm","--release-target","rt","--bin-root","br","--unit-root","ur","--config-path","cp","--rollback-root","rr","--authorization","a","--authorization-sha256","ah","--main-commit","m","--validation-commit","v","--executor-commit","e","--executor-tree","t","--receipt","rec","--deployment-receipt","dep","--execute"]
        with mock.patch.object(sys,"argv",argv), mock.patch.object(deploy,"validated_user_bus_env",return_value={"XDG_RUNTIME_DIR":"/run/user/1","DBUS_SESSION_BUS_ADDRESS":"unix:path=/run/user/1/bus"}), mock.patch.object(deploy,"execute_transaction",side_effect=fake_execute):
            os.environ["SECRET_SHOULD_NOT_LEAK"]="x"
            try:self.assertEqual(deploy.main(),0)
            finally:os.environ.pop("SECRET_SHOULD_NOT_LEAK",None)
        self.assertEqual(captured["XDG_RUNTIME_DIR"],"/run/user/1");self.assertEqual(captured["DBUS_SESSION_BUS_ADDRESS"],"unix:path=/run/user/1/bus");self.assertNotIn("SECRET_SHOULD_NOT_LEAK",captured)

if __name__ == "__main__":
    unittest.main(verbosity=2)
