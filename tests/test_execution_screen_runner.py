"""Validate execution-screen gates without Slurm, GPUs, or actual Lean calls."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts.project import run_execution_screen as runner


def candidate(correct, failure=None):
    return {"verdict": correct, "lean_complete": correct,
            "failure_class": failure, "timed_out": False, "verifier_error": None}


class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bank = self.root / "bank.jsonl"
        self.output = self.root / "checks.json"
        self.verifier = ModuleType("verl.lean.verifier")
        self.mock = Mock(side_effect=lambda proofs, statements, contexts, **kwargs: [
            {"candidate_results": [candidate(True), candidate(False, "lean_rejected")]}
            for _ in statements])
        self.verifier.verify_with_deepseek_verifier = self.mock

    def rows(self, count=1):
        prefix = "  have h : True := True.intro\n"
        proof = prefix + "  exact h\n```"
        return [{"pilot_row_id": f"row{i}", "proof_prefix": prefix,
                 "witness_proof": proof,
                 "witness_sha256": hashlib.sha256(proof.encode()).hexdigest(),
                 "theorem_statement": f"theorem t{i} : True := by\n",
                 "src_context": "import Mathlib\n"} for i in range(count)]

    def invoke(self, rows):
        self.bank.write_text("".join(json.dumps(row) + "\n" for row in rows))
        with patch.dict(sys.modules, {"verl.lean.verifier": self.verifier}):
            runner.verify_witnesses(self.bank, self.output)

    def test_witness_and_prefix_are_two_candidates_per_task_across_batches(self):
        rows = self.rows(33)
        self.invoke([{"proof_prefix": ""}] + rows)
        self.assertEqual(self.mock.call_count, 2)
        first = self.mock.call_args_list[0]
        proofs, statements, contexts = first.args
        self.assertEqual(len(proofs), 64)
        self.assertEqual(len(statements), 32)
        self.assertEqual(len(contexts), 32)
        self.assertEqual(proofs[:2], [rows[0]["witness_proof"], rows[0]["proof_prefix"] + "\n```\n"])
        self.assertEqual(first.kwargs, {"max_workers": 32, "penalize_extra_text": True})
        result = json.loads(self.output.read_text())
        self.assertTrue(result["complete"])
        self.assertEqual(result["physical_lean_calls"], 66)
        self.assertEqual(result["invalid_tasks"], [])

    def test_solved_prefix_or_invalid_witness_stops_the_gate(self):
        for outputs in ([candidate(True), candidate(True)],
                        [candidate(False, "lean_rejected"), candidate(False, "lean_rejected")]):
            with self.subTest(outputs=outputs):
                self.mock.side_effect = lambda *args, **kwargs: [{"candidate_results": outputs}]
                with self.assertRaisesRegex(ValueError, "no generation launched"):
                    self.invoke(self.rows())
                result = json.loads(self.output.read_text())
                self.assertEqual(result["invalid_tasks"], ["row0"])

    def test_infrastructure_failures_do_not_prove_nonterminal_prefix(self):
        for failure in ("timeout", "verifier_exception", "proof_parse_failure", "extra_text_penalty"):
            with self.subTest(failure=failure):
                self.mock.side_effect = lambda *args, **kwargs: [{"candidate_results": [
                    candidate(True), candidate(False, failure)]}]
                with self.assertRaisesRegex(ValueError, "no generation launched"):
                    self.invoke(self.rows())
        corrupt = candidate(False, "lean_rejected") | {"timed_out": True}
        self.mock.side_effect = lambda *args, **kwargs: [{"candidate_results": [candidate(True), corrupt]}]
        with self.assertRaises(ValueError):
            self.invoke(self.rows())

    def test_wrong_verifier_shapes_and_corrupt_witness_fail_closed(self):
        self.mock.side_effect = lambda *args, **kwargs: []
        with self.assertRaisesRegex(ValueError, "batch length"):
            self.invoke(self.rows())
        self.mock.side_effect = lambda *args, **kwargs: [{"candidate_results": [candidate(True)]}]
        with self.assertRaisesRegex(ValueError, "candidate count"):
            self.invoke(self.rows())
        self.mock.reset_mock()
        rows = self.rows()
        rows[0]["witness_proof"] += "changed"
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.invoke(rows)
        self.mock.assert_not_called()

    def test_failed_later_batch_preserves_checked_evidence_and_unknown_cost(self):
        good = [{"candidate_results": [candidate(True), candidate(False, "lean_rejected")]}] * 32
        self.mock.side_effect = [good, RuntimeError("worker disappeared")]
        with self.assertRaisesRegex(RuntimeError, "worker disappeared"):
            self.invoke(self.rows(33))
        result = json.loads(self.output.read_text())
        self.assertFalse(result["complete"])
        self.assertEqual(len(result["checked"]), 32)
        self.assertEqual(result["submitted_candidates"], 66)
        self.assertIsNone(result["physical_lean_calls"])
        self.assertEqual(result["physical_lean_calls_lower_bound"], 64)


class AllocationAndProcessTests(unittest.TestCase):
    def test_allocated_host_account_state_and_exact_job_cgroup_are_required(self):
        info = "JobId=1234 Account=def-zhijing JobState=RUNNING NodeList=trig0012"
        args = (1234, info, "trig0012.cluster", "0::/slurm/uid_123/job_1234/step_extern", ["trig0012"])
        self.assertEqual(runner.validate_allocation(*args)["Account"], "def-zhijing")
        bad = [
            (1234, info.replace("def-zhijing", "rrg-zhijing"), *args[2:]),
            (1234, info.replace("RUNNING", "PENDING"), *args[2:]),
            (1234, info, "login01", args[3], args[4]),
            (1234, info, args[2], "0::/slurm/job_12345/step_extern", args[4]),
            (1234, info.replace("JobId=1234", "JobId=5678"), *args[2:]),
        ]
        for attempt in bad:
            with self.subTest(attempt=attempt), self.assertRaises(ValueError):
                runner.validate_allocation(*attempt)

    def test_sample_command_explicitly_disables_updates_and_fixes_sampling(self):
        command = runner.command_for_panel(Path("/fresh/run"), Path("/bundle/models/base"), 16)
        for setting in ("+trainer.sample_only=True", "+trainer.resume=False", "trainer.save_freq=0",
                        "lean.hard_blocking.enabled=False", "lean.advantage_threshold=False",
                        "actor_rollout_ref.model.path=/bundle/models/base", "data.max_prompt_length=512",
                        "actor_rollout_ref.rollout.response_length=512",
                        "actor_rollout_ref.rollout.temperature=1.0", "actor_rollout_ref.rollout.top_p=1.0",
                        "actor_rollout_ref.rollout.top_k=-1", "lean.num_samples=16"):
            self.assertIn(setting, command)

    def test_process_timeout_terminates_then_kills_entire_group(self):
        with tempfile.TemporaryDirectory() as directory:
            child = Mock(pid=8123)
            child.wait.side_effect = [subprocess.TimeoutExpired("run", 4),
                                      subprocess.TimeoutExpired("run", 30), -9]
            with patch.object(runner.subprocess, "Popen", return_value=child) as launch, \
                    patch.object(runner.os, "killpg") as kill:
                result = runner.run_bounded(["fake"], Path(directory) / "run.log",
                                            cwd=directory, env={}, seconds=4)
            self.assertTrue(result["timed_out"])
            self.assertEqual(result["returncode"], -9)
            self.assertEqual(kill.call_args_list[0].args, (8123, signal.SIGTERM))
            self.assertEqual(kill.call_args_list[1].args, (8123, signal.SIGKILL))
            self.assertTrue(launch.call_args.kwargs["start_new_session"])

    def test_wrong_allocation_fails_before_any_output_or_gpu_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = SimpleNamespace(bundle=root, panel=root / "panel", output=root / "output",
                                   commit="a" * 40, job_id=1234, panel_sha256="b" * 64)
            with patch.object(runner, "validate_snapshot", return_value={}), \
                    patch.object(runner.subprocess, "check_output", side_effect=[
                        "JobId=1234 Account=def-zhijing JobState=PENDING NodeList=trig0012", "trig0012\n"]), \
                    patch.object(runner.subprocess, "Popen") as launch:
                with self.assertRaisesRegex(ValueError, "not running"):
                    runner.run(args)
            self.assertFalse(args.output.exists())
            launch.assert_not_called()


class ImmutableInputsTests(unittest.TestCase):
    def test_model_weight_bytes_must_match_the_pinned_shards(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory)
            (model / "one.safetensors").write_bytes(b"base weights one")
            (model / "two.safetensors").write_bytes(b"base weights two")
            expected = {name: runner.sha256(model / name) for name in ("one.safetensors", "two.safetensors")}
            self.assertEqual(runner.validate_model_weights(model, expected), expected)
            (model / "two.safetensors").write_bytes(b"another checkpoint")
            with self.assertRaisesRegex(ValueError, "weight checksum mismatch"):
                runner.validate_model_weights(model, expected)

    def test_snapshot_rejects_missing_changed_or_injected_source(self):
        with tempfile.TemporaryDirectory() as directory:
            live = Path(directory) / "live"
            snapshot = Path(directory) / "snapshot"
            live.mkdir()
            subprocess.run(["git", "init", "-q", str(live)], check=True)
            (live / "program.py").write_text("print('pinned')\n")
            (live / "operational.patch").write_text("pinned operational patch\n")
            subprocess.run(["git", "-C", str(live), "add", "."], check=True)
            subprocess.run(["git", "-C", str(live), "-c", "user.name=Fixture", "-c",
                            "user.email=fixture@example.invalid", "commit", "-qm", "fixture"], check=True)
            commit = subprocess.check_output(["git", "-C", str(live), "rev-parse", "HEAD"], text=True).strip()
            snapshot.mkdir()
            for name in ("program.py", "operational.patch"):
                shutil.copyfile(live / name, snapshot / name)
            self.assertEqual(len(runner.validate_snapshot(snapshot, live, commit)), 2)
            (snapshot / "operational.patch").unlink()
            with self.assertRaisesRegex(ValueError, "missing"):
                runner.validate_snapshot(snapshot, live, commit)
            shutil.copyfile(live / "operational.patch", snapshot / "operational.patch")
            (snapshot / "program.py").write_text("print('changed')\n")
            with self.assertRaisesRegex(ValueError, "differs"):
                runner.validate_snapshot(snapshot, live, commit)
            shutil.copyfile(live / "program.py", snapshot / "program.py")
            (snapshot / "injected.py").write_text("pass\n")
            with self.assertRaisesRegex(ValueError, "untracked"):
                runner.validate_snapshot(snapshot, live, commit)
            with self.assertRaisesRegex(ValueError, "separate immutable"):
                runner.validate_snapshot(live, live, commit)

    def test_panel_digests_and_base_configuration_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            panel = bundle / "panel"
            model = bundle / "models/base"
            panel.mkdir()
            model.mkdir(parents=True)
            (model / "config.json").write_text('{"model":"base"}\n')
            files = {}
            for name in ("selection_bank.jsonl", "train_prefix.parquet", "diagnostic.parquet"):
                (panel / name).write_text(name)
                files[name] = runner.sha256(panel / name)
            manifest = {"schema_version": 1, "model_revision": runner.MODEL_REVISION,
                        "model_path": str(model), "files": files,
                        "gpu_workspace": {"job_id": 1234, "account": "def-zhijing"},
                        "model_configuration_and_tokenizer_sha256": {"config.json": runner.sha256(model / "config.json")}}
            path = panel / "manifest.json"
            path.write_text(json.dumps(manifest))
            digest = runner.sha256(path)
            self.assertEqual(runner.validate_panel(panel, digest, bundle)["gpu_workspace"]["job_id"], 1234)
            (model / "config.json").write_text("changed")
            with self.assertRaisesRegex(ValueError, "model configuration"):
                runner.validate_panel(panel, digest, bundle)
            (model / "config.json").write_text('{"model":"base"}\n')
            (panel / "diagnostic.parquet").write_text("changed")
            with self.assertRaisesRegex(ValueError, "panel checksum"):
                runner.validate_panel(panel, digest, bundle)
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                runner.validate_panel(panel, "f" * 64, bundle)


if __name__ == "__main__":
    unittest.main()
