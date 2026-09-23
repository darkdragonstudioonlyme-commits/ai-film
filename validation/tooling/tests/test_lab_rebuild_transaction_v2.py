import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL))
from deployment_transaction_common import UnknownCommandCompletion, canonical, sha_file

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, TOOL / filename)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

lab = load("lab_txn", "rebuild_lab_candidate-v2.py")

class FakeLabRunner:
    def __init__(self, version, exports, fail_argv=None):
        self.version = version
        self.exports = exports
        self.fail_argv = tuple(fail_argv) if fail_argv else None
        self.calls = []
        self.states = {lab.PRIMARY: "STOPPED"}

    def run(self, argv, *, input_bytes=None, input_path=None):
        argv = list(argv); self.calls.append(argv)
        if self.fail_argv is not None and tuple(argv) == self.fail_argv:
            raise UnknownCommandCompletion("INJECTED_UNKNOWN")

        if argv == [lab.WSL, "--list", "--verbose"]:
            lines = ["  NAME                   STATE           VERSION"]
            for name, state in sorted(self.states.items()):
                lines.append(f"  {name}    {state.title()}         2")
            return subprocess.CompletedProcess(argv, 0, ("\n".join(lines) + "\n").encode(), b"")

        if argv[:2] == [lab.WSL, "--export"]:
            distro, winpath = argv[2], argv[3]
            out = self.exports[winpath]
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(("EXPORT:" + distro + ":" + winpath).encode())
            return subprocess.CompletedProcess(argv, 0, b"", b"")

        if argv[:2] == [lab.WSL, "--terminate"]:
            name = argv[2]
            if name in self.states: self.states[name] = "STOPPED"
            return subprocess.CompletedProcess(argv, 0, b"", b"")

        if argv[:2] == [lab.WSL, "--unregister"]:
            self.states.pop(argv[2], None)
            return subprocess.CompletedProcess(argv, 0, b"", b"")

        if argv[:2] == [lab.WSL, "--import"]:
            self.states[argv[2]] = "STOPPED"
            return subprocess.CompletedProcess(argv, 0, b"", b"")

        if len(argv) > 4 and argv[:2] == [lab.WSL, "--distribution"]:
            distro = argv[2]
            self.states[distro] = "RUNNING"
            try:
                ix = argv.index("--exec")
            except ValueError:
                return subprocess.CompletedProcess(argv, 9, b"", b"no exec")
            cmd = argv[ix + 1:]
            if cmd[-3:] == ["-m", "aifilm_p00", "--version"]:
                return subprocess.CompletedProcess(argv, 0, (self.version + "\n").encode(), b"")
            if len(cmd) >= 2 and cmd[-1] == "--list" and "run_native_acceptance_tests.py" in cmd[-2]:
                payload = {
                    "case_count": 86, "actual_status": "NOT_RUN",
                    "parent_cases_executed": 0, "qualification_issued": False,
                    "host_ready": False,
                }
                return subprocess.CompletedProcess(argv, 0, json.dumps(payload).encode(), b"")
            if cmd[:2] == ["/usr/bin/cat", "/etc/wsl.conf"]:
                return subprocess.CompletedProcess(argv, 0, b"[automount]\nenabled=false\n", b"")
            if cmd[:2] == ["/usr/bin/findmnt", "/mnt/c"]:
                return subprocess.CompletedProcess(argv, 1, b"", b"")
            if cmd and cmd[0] == "/usr/bin/find":
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            return subprocess.CompletedProcess(argv, 0, b"", b"")

        return subprocess.CompletedProcess(argv, 7, b"", b"unexpected")

class LabTxnTests(unittest.TestCase):
    MAIN = "1" * 40
    VALIDATION = "2" * 40
    EXECUTOR = "3" * 40
    TREE = "4" * 40

    def setUp(self):
        self.td = tempfile.TemporaryDirectory(prefix="lab-txn-")
        self.r = Path(self.td.name)
        self.payload_tar = self.r / "candidate-app.tar"
        self.payload_tar.write_bytes(b"candidate-app")
        self.app_manifest = self.r / "candidate-app.sha256"
        self.app_manifest.write_text("abc  x.py\n")
        self.wheel = self.r / "candidate.whl"
        self.wheel.write_bytes(b"wheel")
        self.profile = {
            "authority_model": "LOCAL_OPERATOR_SAME_WSL_TRUST_DOMAIN",
            "build_digest": "1" * 64,
            "candidate_id": "11111111-2222-4333-8444-555555555555",
            "code_review_record": "reviews/code.md",
            "contract_digest": "2" * 64,
            "implementation_version": "0.1.0.dev23",
            "package_sha256": "3" * 64,
            "schema_version": 1,
            "source_commit": "a" * 40,
            "status": "CANDIDATE_BOUND",
            "test_review_record": "test-governance/review.md",
            "test_set_digest": "4" * 64,
            "wheel_sha256": sha_file(self.wheel),
        }
        self.binding = self.r / "binding.json"
        self.binding.write_bytes(canonical(self.profile) + b"\n")
        self.bsha = sha_file(self.binding)

        self.payload_manifest = self.r / "payload.json"
        self.payload_manifest.write_text(json.dumps({
            "kind": "P00_LAB_CANDIDATE_APP_PAYLOAD",
            "candidate_id": self.profile["candidate_id"],
            "candidate_binding_sha256": self.bsha,
            "source_commit": self.profile["source_commit"],
            "implementation_version": self.profile["implementation_version"],
            "contract_digest": self.profile["contract_digest"],
            "package_sha256": self.profile["package_sha256"],
            "wheel_sha256": self.profile["wheel_sha256"],
            "app_tar_sha256": sha_file(self.payload_tar),
            "app_manifest_sha256": sha_file(self.app_manifest),
            "native_execution_started": False,
        }, sort_keys=True))

        self.seal_root = self.r / "seal"
        self.seal_root.mkdir()
        self.facts = self.seal_root / "LAB_TECHNICAL_FACTS.json"
        self.facts.write_text(json.dumps({"candidate": "dev22"}, sort_keys=True))
        self.seal = self.seal_root / "LAB_ARTIFACT_SEAL_V1.json"
        self.seal.write_text(json.dumps({"candidate_id": "old", "pristine_restore_probe": "PASS"}, sort_keys=True))
        self.prev = self.r / "previous-lab.json"
        self.prev.write_text(json.dumps({
            "status": "PASS", "lab_state": "STOPPED", "restore_probe": "PASS",
            "candidate_id": "old-candidate", "candidate_binding_sha256": "8" * 64,
            "source_commit": "b" * 40,
            "pre_migration_export_sha256": "9" * 64,
            "pristine_raw_sha256": "a" * 64,
            "pristine_sealed_sha256": "b" * 64,
            "technical_facts_sha256": sha_file(self.facts),
            "artifact_seal_sha256": sha_file(self.seal),
            "native_execution_started": False,
        }, sort_keys=True))

        self.plan = self.r / "plan.json"
        self.plan.write_text(json.dumps({
            "schema_version": 1, "kind": "P00_LAB_CANDIDATE_REBUILD_PLAN_V2",
            "status": "READY_FOR_SEPARATE_DEPLOYMENT_REVIEW",
            "target": {
                "candidate_id": self.profile["candidate_id"],
                "candidate_binding_sha256": self.bsha,
                "source_commit": self.profile["source_commit"],
                "implementation_version": self.profile["implementation_version"],
                "package_sha256": self.profile["package_sha256"],
                "wheel_sha256": self.profile["wheel_sha256"],
                "app_tar_sha256": sha_file(self.payload_tar),
                "app_manifest_sha256": sha_file(self.app_manifest),
            },
            "rollback": {"source_commit": "b" * 40},
            "payload_manifest_sha256": sha_file(self.payload_manifest),
            "previous_receipt_sha256": sha_file(self.prev),
            "execution_authorized": False, "lab_mutation_started": False,
        }, sort_keys=True))

        self.prodlike = self.r / "prodlike.json"
        self.prodlike.write_text(json.dumps({
            "kind": "P00_PRODLIKE_CANDIDATE_DEPLOYMENT_V2", "status": "PASS",
            "candidate_id": self.profile["candidate_id"],
            "candidate_binding_sha256": self.bsha,
            "source_commit": self.profile["source_commit"],
            "implementation_version": self.profile["implementation_version"],
            "package_sha256": self.profile["package_sha256"],
            "wheel_sha256": self.profile["wheel_sha256"],
            "native_execution_started": False,
        }, sort_keys=True))

        self.registration = self.r / "registration.json"
        self.registration.write_text(json.dumps({
            "schema_version": 1, "distro": lab.PRIMARY, "observed_state": "STOPPED",
            "wsl_version": 2, "install_location_windows": r"C:\AI-FILM\LAB",
            "observation_source": "HOST_WSL_LIST",
        }, sort_keys=True))

        self.history = self.r / "history"
        self.evidence = self.r / "evidence"
        self.rollback = self.seal_root / "rollback-dev22.tar"
        self.pristine = self.seal_root / "pristine-dev23.tar"
        self.sealed = self.seal_root / "pristine-dev23.tar.gz"
        self.rollback_win = r"C:\AI-FILM\evidence\rollback-dev22.tar"
        self.pristine_win = r"C:\AI-FILM\evidence\pristine-dev23.tar"
        self.probe_install_win = r"C:\AI-FILM\probe"
        self.deployment = self.evidence / "lab-deployment.json"
        self.txn = self.evidence / "transaction.json"
        self.auth = self.r / "authorization.json"

    def tearDown(self):
        self.td.cleanup()

    @property
    def target(self):
        return f"/opt/ai-film-lab/runtime/{self.profile['implementation_version']}"

    @property
    def probe(self):
        return "AI-FILM-P00-LAB-RP-" + hashlib.sha256(b"LAB-TXN-001").hexdigest()[:8]

    def guest_verify_commands(self, distro):
        return [
            lab._guest(distro, f"{self.target}/venv/bin/python", "-m", "aifilm_p00", "--version"),
            lab._guest(distro, f"{self.target}/venv/bin/python",
                       f"{self.target}/app/tools/run_native_acceptance_tests.py", "--list"),
            lab._guest(distro, "/usr/bin/sha256sum", "-c",
                       f"{self.target}/app-manifest.sha256", cd=f"{self.target}/app"),
            lab._guest(distro, "/usr/bin/find", f"{self.target}/app",
                       "-type", "f", "-perm", "/222", "-print"),
            lab._guest(distro, "/usr/bin/cat", "/etc/wsl.conf"),
            lab._guest(distro, "/usr/bin/findmnt", "/mnt/c"),
        ]

    def commands(self):
        rows = []
        def add(x):
            if x not in rows: rows.append(x)
        add([lab.WSL, "--list", "--verbose"])
        add([lab.WSL, "--export", lab.PRIMARY, self.rollback_win, "--format", "tar"])
        for x in [
            lab._guest(lab.PRIMARY, "/usr/bin/install", "-d", "-m", "0755", self.target),
            lab._guest(lab.PRIMARY, "/usr/bin/install", "-d", "-m", "0755", f"{self.target}/app"),
            lab._guest(lab.PRIMARY, "/usr/bin/tar", "-xf", "-", "-C", f"{self.target}/app"),
            lab._guest(lab.PRIMARY, "/usr/bin/dd", f"of={self.target}/app-manifest.sha256", "status=none"),
            lab._guest(lab.PRIMARY, "/usr/bin/python3", "-m", "venv", f"{self.target}/venv"),
            lab._guest(lab.PRIMARY, "/usr/bin/dd", f"of={self.target}/candidate.whl", "status=none"),
            lab._guest(lab.PRIMARY, f"{self.target}/venv/bin/python", "-m", "pip", "install",
                       "--no-index", "--no-deps", f"{self.target}/candidate.whl"),
            lab._guest(lab.PRIMARY, "/usr/bin/chmod", "-R", "a-w", f"{self.target}/app"),
            lab._guest(lab.PRIMARY, "/usr/bin/chmod", "0444",
                       f"{self.target}/app-manifest.sha256", f"{self.target}/candidate.whl"),
        ]: add(x)
        for x in self.guest_verify_commands(lab.PRIMARY): add(x)
        add([lab.WSL, "--terminate", lab.PRIMARY])
        add([lab.WSL, "--export", lab.PRIMARY, self.pristine_win, "--format", "tar"])
        add([lab.WSL, "--import", self.probe, self.probe_install_win,
             self.pristine_win, "--version", "2"])
        for x in self.guest_verify_commands(self.probe): add(x)
        add([lab.WSL, "--terminate", self.probe])
        add([lab.WSL, "--unregister", self.probe])
        # Deterministic rollback commands.
        add([lab.WSL, "--unregister", lab.PRIMARY])
        add([lab.WSL, "--import", lab.PRIMARY, r"C:\AI-FILM\LAB",
             self.rollback_win, "--version", "2"])
        return rows

    def write_auth(self, **overrides):
        inputs = {
            "binding": sha_file(self.binding), "plan": sha_file(self.plan),
            "payload_manifest": sha_file(self.payload_manifest),
            "payload_tar": sha_file(self.payload_tar),
            "payload_app_manifest": sha_file(self.app_manifest),
            "wheel": sha_file(self.wheel), "prodlike_receipt": sha_file(self.prodlike),
            "previous_lab_receipt": sha_file(self.prev),
            "registration_snapshot": sha_file(self.registration),
            "current_technical_facts": sha_file(self.facts),
            "current_artifact_seal": sha_file(self.seal),
        }
        value = {
            "schema_version": 1, "kind": "AIFILM_P00_TRANSACTION_AUTHORIZATION_V1",
            "status": "AUTHORIZED", "transaction_id": "LAB-TXN-001",
            "transaction_kind": "LAB_REBUILD_V2",
            "main_commit": self.MAIN, "validation_commit": self.VALIDATION,
            "executor_commit": self.EXECUTOR, "executor_tree": self.TREE,
            "candidate_id": self.profile["candidate_id"],
            "candidate_binding_sha256": self.bsha,
            "input_sha256": inputs, "mutation_roots": [str(self.r)],
            "allowed_command_prefixes": self.commands(),
            "attempt": 1, "authorized": True, "expires_at": 4102444800,
            "native_execution_authorized": False, "signing_authorized": False,
            "hklm_authorized": False, "site_authorized": False,
            "qualification_authorized": False, "host_ready_authorized": False,
        }
        value.update(overrides)
        self.auth.write_text(json.dumps(value, sort_keys=True))
        return sha_file(self.auth)

    def runner(self, fail=None):
        return FakeLabRunner(self.profile["implementation_version"], {
            self.rollback_win: self.rollback, self.pristine_win: self.pristine,
        }, fail_argv=fail)

    def kwargs(self, runner, auth_sha=None):
        if auth_sha is None: auth_sha = self.write_auth()
        return dict(
            binding=self.binding, binding_sha256=self.bsha, plan_path=self.plan,
            payload_manifest=self.payload_manifest, payload_tar=self.payload_tar,
            payload_app_manifest=self.app_manifest, wheel=self.wheel,
            prodlike_receipt=self.prodlike, previous_lab_receipt=self.prev,
            registration_snapshot=self.registration, seal_root=self.seal_root,
            history_root=self.history, evidence_root=self.evidence,
            rollback_export=self.rollback, rollback_export_windows=self.rollback_win,
            pristine_raw=self.pristine, pristine_raw_windows=self.pristine_win,
            pristine_sealed=self.sealed, probe_install_windows=self.probe_install_win,
            facts_path=self.facts, seal_path=self.seal,
            deployment_receipt=self.deployment, authorization=self.auth,
            authorization_sha256=auth_sha, main_commit=self.MAIN,
            validation_commit=self.VALIDATION, executor_commit=self.EXECUTOR,
            executor_tree=self.TREE, transaction_receipt=self.txn, runner=runner,
        )

    def test_plan_only_has_no_mutation(self):
        out = lab.build_plan(
            binding=self.binding, binding_sha256=self.bsha, plan=self.plan,
            payload_manifest=self.payload_manifest, payload_tar=self.payload_tar,
            payload_app_manifest=self.app_manifest, wheel=self.wheel,
            prodlike_receipt=self.prodlike, previous_lab_receipt=self.prev,
            registration_snapshot=self.registration, seal_root=self.seal_root,
            history_root=self.history, evidence_root=self.evidence)
        self.assertEqual(out["status"], "PLAN_ONLY")
        self.assertFalse(out["lab_mutation_started"])
        self.assertFalse(self.rollback.exists())

    def test_happy_rebuild_probe_seal_and_receipt(self):
        runner = self.runner()
        out = lab.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "PASS")
        self.assertEqual(runner.states[lab.PRIMARY], "STOPPED")
        self.assertNotIn(self.probe, runner.states)
        self.assertTrue(self.rollback.is_file())
        self.assertTrue(self.pristine.is_file())
        self.assertTrue(self.sealed.is_file())
        self.assertTrue(self.deployment.is_file())
        final = json.loads(self.deployment.read_text())
        self.assertEqual(final["inventory_status"], "NOT_RUN")
        self.assertFalse(final["native_execution_started"])
        self.assertTrue(any(self.history.iterdir()))
        seal = json.loads(self.seal.read_text())
        self.assertEqual(seal["candidate_id"], self.profile["candidate_id"])
        self.assertEqual(seal["pristine_restore_probe"], "PASS")

    def test_existing_receipt_never_touches_wsl_again(self):
        runner = self.runner()
        first = lab.execute_transaction(**self.kwargs(runner))
        calls = len(runner.calls)
        second = lab.execute_transaction(**self.kwargs(runner, sha_file(self.auth)))
        self.assertEqual(first["state"], "PASS")
        self.assertEqual(second["state"], "PASS")
        self.assertEqual(len(runner.calls), calls)

    def test_wrong_executor_tree_rejected_before_receipt_or_wsl(self):
        runner = self.runner()
        auth_sha = self.write_auth(executor_tree="9" * 40)
        with self.assertRaisesRegex(Exception, "AUTHORIZATION_EXECUTOR_TREE_DRIFT"):
            lab.execute_transaction(**self.kwargs(runner, auth_sha))
        self.assertEqual(runner.calls, [])
        self.assertFalse(self.txn.exists())

    def test_stale_dev22_facts_fails_premutation(self):
        runner = self.runner()
        auth_sha = self.write_auth()
        self.facts.write_text(self.facts.read_text() + "\n")
        out = lab.execute_transaction(**self.kwargs(runner, auth_sha))
        self.assertEqual(out["state"], "FAILED_PREMUTATION")
        self.assertFalse(out["mutation_started"])
        self.assertEqual(runner.calls, [])

    def test_unknown_install_completion_requires_reconcile_no_retry(self):
        fail = lab._guest(lab.PRIMARY, "/usr/bin/tar", "-xf", "-", "-C", f"{self.target}/app")
        runner = self.runner(fail)
        out = lab.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "RECONCILE_REQUIRED")
        self.assertEqual(out["phase"], "UNKNOWN_COMPLETION")
        idx = runner.calls.index(fail)
        self.assertEqual(len(runner.calls), idx + 1)
        self.assertTrue(self.rollback.exists())

    def test_unknown_completion_boundary_matrix(self):
        cases = ["rollback_export", "pristine_export", "probe_import", "probe_unregister"]
        for index, name in enumerate(cases):
            with self.subTest(boundary=name):
                if index:
                    self.tearDown(); self.setUp()
                if name == "rollback_export": fail=[lab.WSL, "--export", lab.PRIMARY, self.rollback_win, "--format", "tar"]
                elif name == "pristine_export": fail=[lab.WSL, "--export", lab.PRIMARY, self.pristine_win, "--format", "tar"]
                elif name == "probe_import": fail=[lab.WSL, "--import", self.probe, self.probe_install_win, self.pristine_win, "--version", "2"]
                else: fail=[lab.WSL, "--unregister", self.probe]
                runner=self.runner(fail);out=lab.execute_transaction(**self.kwargs(runner))
                if name == "rollback_export":
                    self.assertEqual(out["state"], "FAILED_PREMUTATION")
                else:
                    self.assertEqual(out["state"], "RECONCILE_REQUIRED")
                    self.assertEqual(out["phase"], "UNKNOWN_COMPLETION")
                    if name in ("probe_import","probe_unregister"):
                        self.assertTrue(out["probe_may_be_registered"])
                idx=runner.calls.index(fail);self.assertEqual(len(runner.calls),idx+1)

    def test_deterministic_primary_verify_failure_rolls_back(self):
        runner = self.runner()
        with mock.patch.object(lab, "_guest_verify", side_effect=lab.LabError("INJECTED_VERIFY")):
            out = lab.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "FAILED_ROLLED_BACK")
        self.assertTrue(out["rollback_verified"])
        self.assertEqual(runner.states[lab.PRIMARY], "STOPPED")
        self.assertTrue(self.rollback.exists())

    def test_probe_failure_cleans_probe_then_rolls_back(self):
        runner = self.runner()
        original = lab._guest_verify
        calls = {"n": 0}
        def fail_second(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 2:
                raise lab.LabError("INJECTED_PROBE_VERIFY")
            return original(*args, **kwargs)
        with mock.patch.object(lab, "_guest_verify", side_effect=fail_second):
            out = lab.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "FAILED_ROLLED_BACK")
        self.assertNotIn(self.probe, runner.states)
        self.assertEqual(runner.states[lab.PRIMARY], "STOPPED")

    def test_evidence_commit_failure_requires_reconcile_not_destructive_retry(self):
        runner = self.runner()
        with mock.patch.object(lab, "_make_final_evidence", side_effect=lab.LabError("INJECTED_EVIDENCE")):
            out = lab.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "RECONCILE_REQUIRED")
        self.assertEqual(out["phase"], "EVIDENCE_COMMIT_UNCERTAIN")
        self.assertEqual(runner.states[lab.PRIMARY], "STOPPED")
        # No primary unregister occurs after evidence commit begins.
        self.assertNotIn([lab.WSL, "--unregister", lab.PRIMARY], runner.calls)

    def test_lab_must_be_stopped_before_rollback_export(self):
        runner = self.runner()
        runner.states[lab.PRIMARY] = "RUNNING"
        out = lab.execute_transaction(**self.kwargs(runner))
        self.assertEqual(out["state"], "FAILED_PREMUTATION")
        self.assertFalse(self.rollback.exists())

if __name__ == "__main__":
    unittest.main(verbosity=2)
