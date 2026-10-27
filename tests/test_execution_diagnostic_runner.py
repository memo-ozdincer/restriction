"""Fail-closed final-checkpoint evaluation tests; no GPU or Lean launches."""
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.project import execution_training_telemetry as weights
from scripts.project import run_execution_diagnostic as runner
from scripts.project import run_execution_screen as screen
from tests.test_execution_pilot_analysis import bank_rows, records_for
from tests.test_execution_training import write, write_lines
from tests.test_execution_training_telemetry import write_weights
from verl.lean.telemetry import telemetry_identity


class DiagnosticCompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "evaluation"
        self.panel = self.root / "panel"
        self.model = self.root / "training/artifacts/actor/global_step_64"
        self.commit = "a" * 40
        self.verifier = self.root / "verifier"
        rows = [r for r in bank_rows(0, 64, two_prefixes=True)
                if not (r["pilot_row_id"].endswith(":2") and int(r["theorem_full_name"].split("_")[1]) >= 40)]
        self.bank = {r["pilot_row_id"]: r for r in rows}
        self.assertEqual(len(rows), 168)
        self.run.mkdir()
        self.panel.mkdir()
        (self.panel / "diagnostic.parquet").write_bytes(b"frozen diagnostic fixture")
        (self.run / "train.parquet").write_bytes((self.panel / "diagnostic.parquet").read_bytes())
        write(self.panel / "manifest.json", {"frozen": "panel fixture"})
        write(self.run / "command.json", screen.command_for_panel(self.run, self.model, 32))
        (self.run / "run.log").write_text("[TRAINING] Training finished\nException: Stop\n")
        self.status = {"timed_out": False, "returncode": 1, "expected_steps": 11,
                       "registered_rows": 168, "registered_proposals": 5376, "elapsed_evaluation_seconds": 500}
        write(self.run / "process_status.json", self.status)
        self.certificate = {"arm": "practice", "checkpoint": str(self.model)}
        config = runner.expected_runtime_config(self.run, self.model)
        environment = {"git_commit": self.commit, "model_revision": screen.MODEL_REVISION,
                       "verifier_root": str(self.verifier), "verifier_memory_limit_gb": "32"}
        config_hash, environment_hash = telemetry_identity(
            json.dumps(config, sort_keys=True, separators=(",", ":")), environment)
        self.events = [{"event": "runtime_config", "resolved_config": config, "environment": environment,
                        "config_hash": config_hash, "environment_hash": environment_hash}]
        self.events += [{"event": "rollout_batch", "step": step, "groups": 16 if step < 11 else 8,
                         "samples_per_group": 32, "admitted_groups": 16 if step < 11 else 8,
                         "skipped_groups": 0} for step in range(1, 12)]
        self.events = [{**r, "schema_version": 1, "role": "driver", "hostname": "node",
                        "pid": 3, "rank": -1, "sequence": i} for i, r in enumerate(self.events, 1)]
        write_lines(self.run / "telemetry/driver.jsonl", self.events)
        self.records = records_for(rows)
        slots = {row["pilot_row_id"]: i for i, row in enumerate(rows)}
        for record in self.records:
            slot = slots[record["pilot_row_id"]]
            record.update(config_hash=config_hash, environment_hash=environment_hash,
                          batch_id=f"evaluation:step-{slot // 16 + 1}", theorem_index_in_batch=slot % 16)
        self.proof = self.run / "artifacts/proofs/global_step_11.jsonl"
        write_lines(self.proof, self.records)

    def certify(self):
        return runner.certify_evaluation(self.run, self.bank, self.certificate, self.panel,
                                         self.commit, self.verifier, self.status)

    def test_complete_exact_diagnostic_outputs_have_separate_runtime_attestation(self):
        summary, telemetry = self.certify()
        self.assertEqual(summary["registered"]["proposals"], 5376)
        self.assertEqual(summary["panels"]["diagnostic_root"]["tasks"], 64)
        self.assertEqual(summary["panels"]["diagnostic_prefix"]["tasks"], 104)
        self.assertEqual(telemetry["actor_updates"], 0)
        self.assertEqual(telemetry["trained_samples"], 0)
        self.assertNotIn("gate", summary)
        self.assertIn("separate evaluation_complete.json required", summary["provenance"]["runtime_attestation"])

    def test_sample_command_preserves_base_screen_settings_and_disables_updates(self):
        command = screen.command_for_panel(self.run, self.model, 32)
        baseline = screen.command_for_panel(self.run, Path("/base"), 32)
        self.assertEqual([x for x in command if not x.startswith("actor_rollout_ref.model.path=")],
                         [x for x in baseline if not x.startswith("actor_rollout_ref.model.path=")])
        for setting in ("+trainer.sample_only=True", "trainer.save_freq=0", "lean.max_workers=32",
                        "lean.hard_blocking.enabled=False", "lean.advantage_threshold=False", "lean.num_samples=32"):
            self.assertIn(setting, command)
        config = runner.expected_runtime_config(self.run, self.model)
        self.assertTrue(config["trainer"]["sample_only"])
        self.assertEqual(config["actor_rollout_ref"]["actor"]["optim"]["total_training_steps"], 11)

    def test_incomplete_duplicate_or_training_proposals_fail(self):
        cases = [self.records[:-1], self.records + [self.records[0]], deepcopy(self.records)]
        cases[-1][0]["pilot_split"] = "train"
        for records in cases:
            with self.subTest(count=len(records)):
                write_lines(self.proof, records)
                with self.assertRaises(ValueError):
                    self.certify()

    def test_samples_cannot_mask_runtime_model_or_optimizer_changes(self):
        for mutate in (
            lambda rows: rows[0]["resolved_config"]["actor_rollout_ref"]["model"].update(path="/different/actor"),
            lambda rows: rows[0]["resolved_config"]["trainer"].update(sample_only=False),
            lambda rows: rows[-1].update(event="actor_dispatch_complete"),
            lambda rows: rows[-1].update(groups=16),
            lambda rows: rows[0].update(environment_hash="bad"),
        ):
            changed = deepcopy(self.events)
            mutate(changed)
            write_lines(self.run / "telemetry/driver.jsonl", changed)
            with self.assertRaises(ValueError):
                self.certify()
        write_lines(self.run / "telemetry/driver.jsonl", self.events)
        write_lines(self.run / "telemetry/actor.jsonl", [{"event": "optimizer_attempt"}])
        with self.assertRaisesRegex(ValueError, "no actor updates"):
            self.certify()

    def test_proposals_require_runtime_identity_and_no_padding(self):
        for field, value in (("config_hash", "wrong"), ("environment_hash", "wrong"),
                             ("pilot_padding", True), ("blocked_correct", True), ("batch_id", "other:step-1")):
            records = deepcopy(self.records)
            records[0][field] = value
            write_lines(self.proof, records)
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.certify()

    def test_final_proof_and_finish_marker_required_and_timeout_cannot_pass(self):
        self.proof.rename(self.proof.with_name("global_step_10.jsonl"))
        with self.assertRaisesRegex(ValueError, "final diagnostic proof"):
            self.certify()
        self.proof.with_name("global_step_10.jsonl").rename(self.proof)
        (self.run / "run.log").write_text("partial\n")
        with self.assertRaisesRegex(ValueError, "did not complete"):
            self.certify()
        (self.run / "run.log").write_text("[TRAINING] Training finished\nException: Stop\n")
        self.status["timed_out"] = True
        with self.assertRaisesRegex(ValueError, "did not complete"):
            self.certify()


class DiagnosticCheckpointTests(unittest.TestCase):
    def test_partial_training_certificate_is_refused_before_recertification(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            saved = {"schema_version": 1, "evaluation_eligible": True,
                     "status": "complete_eligible_for_diagnostic_evaluation", "global_steps": 63,
                     "arm": "root", "source_commit": "a" * 40, "training_manifest_sha256": "b" * 64}
            write(run / "training_complete.json", saved)
            with patch.object(runner.training, "certify_completion") as recertify:
                with self.assertRaisesRegex(ValueError, "partial"):
                    runner.authenticate_training(run, run, "b" * 64, run, "root", "a" * 40, {}, [])
            recertify.assert_not_called()

    def test_actual_checkpoint_bytes_must_match_training_certificate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base, actor = root / "base", root / "global_step_64"
            tokenizer = {"tokenizer.json": {"model": "test"}, "tokenizer_config.json": {"eos": 1},
                         "special_tokens_map.json": {"eos": 1}}
            for path in (base, actor):
                path.mkdir()
                write_weights(path)
                write(path / "config.json", {"model_type": "test", "eos_token_id": 1})
                for name, value in tokenizer.items():
                    write(path / name, value)
            with patch.object(weights, "normalized_tokenizer_files", return_value=tokenizer):
                certificate = {"checkpoint": str(actor), "checkpoint_manifest": weights.validate_actor_checkpoint(actor, base)}
                self.assertEqual(runner.authenticate_checkpoint(certificate, base), certificate["checkpoint_manifest"])
                path = actor / "model.safetensors"
                original = path.read_bytes()
                path.write_bytes(original[:-1])
                with self.assertRaisesRegex(ValueError, "payload"):
                    runner.authenticate_checkpoint(certificate, base)
                path.write_bytes(original[:-1] + b"x")
                with self.assertRaisesRegex(ValueError, "checkpoint bytes changed"):
                    runner.authenticate_checkpoint(certificate, base)


class DiagnosticAllocationTests(unittest.TestCase):
    def args(self, root):
        return SimpleNamespace(bundle=root, output=root / "runs/new-evaluation", training_run=root / "training",
                               training_panel=root / "panel", training_sha256="b" * 64,
                               arm="root", commit="a" * 40, job_id=1176227)

    def test_pending_or_short_allocation_cannot_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            args = self.args(Path(directory))
            with patch.object(runner.subprocess, "check_output", side_effect=[
                    "JobId=1176227 Account=def-zhijing JobState=PENDING NodeList=node", "node\n"]), \
                    patch.object(screen, "run_bounded") as launch:
                with self.assertRaisesRegex(ValueError, "not running"):
                    runner.run(args)
            launch.assert_not_called()
            self.assertFalse(args.output.exists())
            with self.assertRaisesRegex(ValueError, "remaining allocation"):
                runner.training.require_remaining_allocation("EndTime=" + datetime.fromtimestamp(11000).isoformat(),
                                                             runner.MAXIMUM_SECONDS, now=0)

    def test_existing_output_and_shared_training_lock_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = self.args(root)
            args.output.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "existing diagnostic output"):
                runner.run(args)
            args.output.rmdir()
            preflight = root / "repository/scripts/project/preflight.sh"
            preflight.parent.mkdir(parents=True)
            preflight.write_text("fixture")
            lock = root / "runs/.execution-training-1176227.active.json"
            lock.write_text("existing training owner")
            with patch.object(runner.subprocess, "check_output", side_effect=["NodeList=node", "node\n"]), \
                    patch.object(screen, "validate_allocation"), \
                    patch.object(runner.training, "require_remaining_allocation", return_value=20000), \
                    patch.object(screen, "validate_snapshot", return_value={"scripts/project/preflight.sh": screen.sha256(preflight)}), \
                    patch.object(screen, "run_bounded") as launch:
                with self.assertRaises(FileExistsError):
                    runner.run(args)
            launch.assert_not_called()
            self.assertEqual(lock.read_text(), "existing training owner")
            self.assertFalse(args.output.exists())


if __name__ == "__main__":
    unittest.main()
