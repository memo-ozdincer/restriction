"""CPU-only provenance, schedule and allocation tests for conditional training."""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.project import analyze_execution_pilot as analysis
from scripts.project import prepare_execution_training as prepare
from scripts.project import run_execution_screen as screen
from scripts.project import run_execution_training as runner
from tests.test_execution_pilot_analysis import bank_rows, minimal_manifest, records_for


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n")


def write_lines(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


class TrainingScheduleTests(unittest.TestCase):
    def fixture(self, count=48):
        bank = bank_rows(count, diagnostic_count=2, two_prefixes=True)
        return {row["pilot_row_id"]: row for row in bank}, analysis.summarize(
            {row["pilot_row_id"]: row for row in bank}, records_for(bank))

    def test_matched_theorems_exact_quotas_unique_slots_and_no_padding(self):
        bank, result = self.fixture()
        arms, quotas = prepare.build_schedule(bank, result)
        self.assertEqual(len(arms["root"]), 1024)
        self.assertEqual(len(arms["practice"]), 1024)
        self.assertEqual(sum(bool(row["proof_prefix"]) for row in arms["practice"]), 512)
        self.assertFalse(any(row["proof_prefix"] for row in arms["root"]))
        for arm in arms:
            self.assertEqual(len({row["pilot_row_id"] for row in arms[arm]}), 1024)
            self.assertTrue(all(row["pilot_split"] == "train" and row["pilot_padding"] is False for row in arms[arm]))
            self.assertTrue(all(row["source_pilot_row_id"] in bank for row in arms[arm]))
        self.assertEqual([row["theorem_full_name"] for row in arms["root"]],
                         [row["theorem_full_name"] for row in arms["practice"]])
        counts = [q["prefix_rows"] for q in quotas.values()]
        self.assertEqual(max(counts) - min(counts), 1)
        for theorem, quota in quotas.items():
            routes = list(quota["prefix_routes"].values())
            self.assertLessEqual(max(routes) - min(routes), 1)
            for arm in arms:
                self.assertEqual(sum(row["theorem_full_name"] == theorem for row in arms[arm]), quota["total_rows_per_arm"])
        self.assertEqual(prepare.build_schedule(dict(reversed(list(bank.items()))), result), (arms, quotas))

    def test_diagnostic_outcomes_cannot_change_training_schedule(self):
        bank, result = self.fixture()
        changed = deepcopy(result)
        for task in changed["tasks"]:
            if task["split"] == "diagnostic":
                task["correct"] = 0
                task["correctness"] = 0
        changed["panels"] = {"diagnostic_root": {"correctness": 0}}
        self.assertEqual(prepare.build_schedule(bank, result), prepare.build_schedule(bank, changed))

    def test_gate_failure_forged_gate_and_eligible_diagnostic_are_rejected(self):
        bank, result = self.fixture()
        for mutate in (lambda r: r["gate"].update(advance=False),
                       lambda r: r["gate"].update(diagnostics_used_for_gate=True),
                       lambda r: r["gate"]["eligible_prefix_rows"].append("diagnostic_0:1"),
                       lambda r: next(t for t in r["tasks"] if t["split"] == "train").update(correct=16)):
            changed = deepcopy(result)
            mutate(changed)
            with self.assertRaises(ValueError):
                prepare.build_schedule(bank, changed)
        few_bank, few_result = self.fixture(47)
        few_result["gate"]["advance"] = True
        with self.assertRaisesRegex(ValueError, "recomputed practice gate"):
            prepare.build_schedule(few_bank, few_result)


class TrainingAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.bundle = Path(self.temp.name)
        self.panel, self.run = self.bundle / "panel", self.bundle / "screen"
        self.panel.mkdir()
        self.model = self.bundle / "models/base"
        self.model.mkdir(parents=True)
        self.verifier = self.bundle / "verifier/DeepSeek-Prover-V1.5"
        (self.verifier / "prover/lean").mkdir(parents=True)
        (self.verifier / "prover/lean/verifier.py").write_text("# pinned verifier\n")
        (self.verifier / "mathlib4").mkdir()
        (self.verifier / "mathlib4/lean-toolchain").write_text("leanprover/lean4:v4.9.0\n")
        python = self.bundle / "environment/venv/bin/python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        write(self.model / "config.json", {"model": "fixture"})
        self.source_files = {
            "scripts/project/patches/benchmark_lake_path.patch": "a" * 64,
            "scripts/project/patches/deepseek_verifier_compact_result.patch": "b" * 64,
            "scripts/project/run_execution_screen.py": "c" * 64,
        }
        self.bank = bank_rows(48, two_prefixes=True)
        source = self.bundle / "source.jsonl"
        witnesses = []
        for row in self.bank:
            if row["proof_prefix"]:
                witnesses.append(dict(theorem_name=row["theorem_full_name"], theorem_statement=row["theorem_statement"],
                                      informal_statement=row["informal_statement"], context=row["src_context"],
                                      proof=row["witness_proof"], correct=True))
                row.update(source_log=str(source), source_line=len(witnesses))
        write_lines(source, witnesses)
        for row in self.bank:
            if row["proof_prefix"]:
                row["source_log_sha256"] = screen.sha256(source)
        write_lines(self.panel / "selection_bank.jsonl", self.bank)
        import pandas as pd
        for label, rows in (("train_prefix", [r for r in self.bank if r["pilot_split"] == "train" and r["proof_prefix"]]),
                            ("diagnostic", [r for r in self.bank if r["pilot_split"] == "diagnostic"])):
            pd.DataFrame(rows).to_parquet(self.panel / (label + ".parquet"), index=False)
        manifest = minimal_manifest(self.bank)
        manifest.update(model_revision=screen.MODEL_REVISION, model_path=str(self.model),
                        model_configuration_and_tokenizer_sha256={"config.json": screen.sha256(self.model / "config.json")},
                        source_logs=[{"path": str(source), "sha256": screen.sha256(source)}])
        for key in ("source_dataset", "c0_validation"):
            path = self.bundle / (key + ".json")
            write(path, {})
            manifest[key] = {"path": str(path), "sha256": screen.sha256(path)}
        manifest["files"] = {path.name: screen.sha256(path) for path in self.panel.iterdir()}
        write(self.panel / "manifest.json", manifest)
        self.panel_digest = screen.sha256(self.panel / "manifest.json")
        self.addCleanup(patch.stopall)
        patch.object(prepare, "PANEL_SHA256", self.panel_digest).start()
        patch.object(prepare, "SOURCE_VERIFIER_SHA256", screen.sha256(self.verifier / "prover/lean/verifier.py")).start()
        patch.object(prepare, "STAGED_VERIFIER_SHA256", "d" * 64).start()
        patch.object(screen, "validate_snapshot", return_value=self.source_files).start()
        write(self.run / "provenance.json", {"source_commit": prepare.SCREEN_COMMIT,
            "source_files_sha256": self.source_files, "panel": str(self.panel), "panel_manifest_sha256": self.panel_digest,
            "model_revision": screen.MODEL_REVISION, "model_path": str(self.model),
            "model_weight_sha256": screen.BASE_MODEL_WEIGHTS, "seed": 42, "maximum_seconds": 21600,
            "hostname": "trig0012", "job_info": "JobId=1176227 Account=def-zhijing JobState=RUNNING NodeList=trig0012",
            "cgroup": "0::/slurm/job_1176227/step_extern"})
        for label in ("staging", "preflight", "witness"):
            write(self.run / (label + "_status.json"), {"returncode": 0, "timed_out": False})
        write(self.run / "verifier_provenance.json", {
            "source_verifier_sha256": screen.sha256(self.verifier / "prover/lean/verifier.py"),
            "staged_verifier_sha256": "d" * 64,
            "lake_path_patch_sha256": "a" * 64, "result_handoff_patch_sha256": "b" * 64,
            "lean_toolchain": "leanprover/lean4:v4.9.0"})
        checks = []
        for row in self.bank:
            if row["proof_prefix"]:
                checks.append({"pilot_row_id": row["pilot_row_id"],
                    "witness": {"verdict": True, "lean_complete": True, "failure_class": None, "timed_out": False},
                    "prefix_only": {"verdict": False, "lean_complete": False, "failure_class": "lean_rejected", "timed_out": False}})
        write(self.run / "witness_checks.json", {"complete": True, "checked": checks, "invalid_tasks": [],
                                                "physical_lean_calls": 2 * len(checks), "submitted_candidates": 2 * len(checks)})
        write(self.run / "generation_complete.json", {"status": "generation_complete_pending_independent_analysis",
                                                       "trained_samples": 0, "elapsed_seconds": 1000})
        records = records_for(self.bank)
        self.logs = []
        for label, split, filename, samples in (("practice", "train", "train_prefix.parquet", 16),
                                                ("diagnostic", "diagnostic", "diagnostic.parquet", 32)):
            rows = [r for r in records if r["pilot_split"] == split]
            count = len(rows) // samples
            steps = (count + 15) // 16
            destination = self.run / label
            log = destination / f"artifacts/proofs/global_step_{steps}.jsonl"
            write_lines(log, rows)
            (destination / "train.parquet").write_bytes((self.panel / filename).read_bytes())
            write(destination / "command.json", screen.command_for_panel(destination, self.model, samples))
            (destination / "run.log").write_text("[TRAINING] Training finished\nException: Stop\n")
            write(destination / "process_status.json", {"completion_candidate": True, "timed_out": False,
                "expected_steps": steps, "registered_rows": count, "registered_proposals": count * samples,
                "proof_log": str(log), "proof_log_sha256": screen.sha256(log), "returncode": 1})
            self.logs.append(log)
        write(self.run / "analysis.json", analysis.analyze(self.panel / "manifest.json", *self.logs))
        self.args = SimpleNamespace(bundle=self.bundle, panel=self.panel, screen_run=self.run,
                                    screen_source=self.bundle / "source", output=self.bundle / "training")

    def test_prepare_and_revalidate_full_synthetic_artifact(self):
        manifest = prepare.prepare(self.args)
        self.assertEqual(manifest["budget"]["proposals_per_arm"], 32768)
        digest = screen.sha256(self.args.output / "manifest.json")
        actual, arms = prepare.validate_training_panel(self.args.output, digest, self.bundle)
        self.assertEqual(manifest, actual)
        self.assertEqual(len(arms["practice"]), 1024)
        with self.assertRaisesRegex(ValueError, "existing training panel"):
            prepare.prepare(self.args)
        (self.args.output / "root/train.parquet").write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "checksum"):
            prepare.validate_training_panel(self.args.output, digest, self.bundle)

    def test_runtime_certificate_corruption_fails_before_creating_training_panel(self):
        mutations = [
            ("provenance.json", lambda r: r.update(model_weight_sha256={})),
            ("provenance.json", lambda r: r.update(source_commit="a" * 40)),
            ("witness_checks.json", lambda r: r["checked"].pop()),
            ("witness_checks.json", lambda r: r["checked"][0]["prefix_only"].update(verdict=True)),
            ("preflight_status.json", lambda r: r.update(returncode=1)),
            ("generation_complete.json", lambda r: r.update(trained_samples=1)),
            ("practice/process_status.json", lambda r: r.update(proof_log_sha256="f" * 64)),
            ("analysis.json", lambda r: r["gate"].update(advance=False)),
            ("practice/command.json", lambda r: r.append("+trainer.resume=True")),
        ]
        for filename, mutate in mutations:
            path = self.run / filename
            original = path.read_text()
            value = json.loads(original)
            mutate(value)
            write(path, value)
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                prepare.prepare(self.args)
            self.assertFalse(self.args.output.exists())
            path.write_text(original)

    def test_source_corruption_and_failed_real_gate_are_rejected(self):
        source = self.bundle / "source.jsonl"
        original = source.read_text()
        source.write_text(original + "\n")
        with self.assertRaisesRegex(ValueError, "checksum"):
            prepare.prepare(self.args)
        source.write_text(original)
        rows = list(analysis.read_jsonl(self.logs[0]))
        for row in rows:
            row.update(correct=False, verdict=False, lean_complete=False)
        write_lines(self.logs[0], rows)
        status_path = self.run / "practice/process_status.json"
        status = json.loads(status_path.read_text())
        status["proof_log_sha256"] = screen.sha256(self.logs[0])
        write(status_path, status)
        write(self.run / "analysis.json", analysis.analyze(self.panel / "manifest.json", *self.logs))
        with self.assertRaisesRegex(ValueError, "gate did not advance"):
            prepare.prepare(self.args)
        self.assertFalse(self.args.output.exists())


class TrainingRunnerTests(unittest.TestCase):
    def test_completion_can_be_reauthenticated_without_writing_and_failure_never_qualifies(self):
        with tempfile.TemporaryDirectory() as directory:
            run, model = Path(directory) / "root", Path(directory) / "base"
            proof_dir = run / "artifacts/proofs"
            proof_dir.mkdir(parents=True)
            for step in range(1, 65):
                (proof_dir / f"global_step_{step}.jsonl").write_text("fixture\n")
            (run / "run.log").write_text("[TRAINING] Training finished\nException: Stop\n")
            result = {"returncode": 1, "timed_out": False, "arm": "root", "expected_steps": 64,
                      "registered_rows": 1024, "registered_proposals": 32768, "elapsed_arm_seconds": 1000}
            write(run / "process_status.json", result)
            write(run / "command.json", runner.command_for_arm(run, model))
            provenance = {"source_commit": "a" * 40, "training_manifest_sha256": "b" * 64,
                "arm": "root", "model_weight_sha256": screen.BASE_MODEL_WEIGHTS, "model_path": str(model),
                "staged_verifier": "/fixture/verifier"}
            write(run / "provenance.json", provenance)
            telemetry = {"resolved_config": runner.expected_runtime_config(run, model), "actual_optimizer_steps": 1,
                "final_checkpoint_saved": True, "environment": {"git_commit": "a" * 40,
                "model_revision": screen.MODEL_REVISION, "verifier_root": "/fixture/verifier", "verifier_memory_limit_gb": "32"}}
            with patch("scripts.project.execution_training_telemetry.summarize_telemetry", return_value=telemetry), \
                    patch("scripts.project.execution_training_telemetry.validate_actor_checkpoint", return_value={"complete": True}), \
                    patch.object(runner, "validate_training_proofs", return_value={"proposals": 32768}):
                saved = runner.certify_completion(run, [], result, model, "root", "b" * 64, "a" * 40)
                with patch.object(runner, "write_json") as writer:
                    recertified = runner.certify_completion(run, [], result, model, "root", "b" * 64, "a" * 40, persist=False)
                    writer.assert_not_called()
                self.assertEqual(saved, recertified)
                write(run / "failure.json", {"error": "late failure"})
                with self.assertRaisesRegex(ValueError, "failure certificate"):
                    runner.certify_completion(run, [], result, model, "root", "b" * 64, "a" * 40, persist=False)

    def test_complete_fresh_proposals_and_prefix_provenance_are_required(self):
        bank = bank_rows(48, two_prefixes=True)
        by_id = {row["pilot_row_id"]: row for row in bank}
        arms, _ = prepare.build_schedule(by_id, analysis.summarize(by_id, records_for(bank)))
        rows = arms["practice"]
        # The fixture helper generates 32 candidates for diagnostic-marked rows;
        # relabel only the synthetic generator, then restore the training split.
        copied = deepcopy(rows)
        for row in copied:
            row["pilot_split"] = "diagnostic"
        records = records_for(copied)
        for index, record in enumerate(records):
            row_index = index // 32
            record.update(pilot_split="train", batch_id=f"batch-{row_index // 16}",
                          theorem_index_in_batch=row_index % 16, prompt_token_count=rows[row_index]["prompt_token_count"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proofs.jsonl"
            write_lines(path, records)
            self.assertEqual(runner.validate_training_proofs(path, rows)["proposals"], 32768)
            for field, value in (("pilot_padding", True), ("pilot_split", "diagnostic"),
                                 ("candidate_index", 32), ("proof_hash", "changed")):
                old = records[0][field]
                records[0][field] = value
                write_lines(path, records)
                with self.subTest(field=field), self.assertRaises(ValueError):
                    runner.validate_training_proofs(path, rows)
                records[0][field] = old
            write_lines(path, records[:-1])
            with self.assertRaisesRegex(ValueError, "count/index"):
                runner.validate_training_proofs(path, rows)

    def test_c2_optimizer_pristine_base_budget_and_no_automatic_resume(self):
        command = runner.command_for_arm(Path("/run/root"), Path("/bundle/models/base"))
        for option in ("actor_rollout_ref.model.path=/bundle/models/base", "actor_rollout_ref.actor.optim.lr=1e-6",
                       "actor_rollout_ref.actor.kl_loss_coef=0.10", "actor_rollout_ref.actor.ppo_epochs=2",
                       "+lean.rank_penalty=0.25", "lean.advantage_threshold=True", "lean.hard_blocking.enabled=False",
                       "trainer.save_freq=16", "trainer.save_limit=2", "trainer.save_proof_freq=1",
                       "trainer.total_training_steps=64", "lean.problem_batch_size=16", "lean.num_samples=32",
                       "+trainer.resume=False", "+trainer.sample_only=False"):
            self.assertIn(option, command)
        self.assertFalse(any("diagnostic" in option for option in command))
        resolved = runner.expected_runtime_config(Path("/run/root"), Path("/bundle/models/base"))
        self.assertEqual(resolved["actor_rollout_ref"]["actor"]["optim"]["total_training_steps"], 64)
        self.assertEqual(resolved["critic"]["optim"]["total_training_steps"], 64)
        self.assertFalse(resolved["trainer"]["resume"])
        self.assertEqual(resolved["actor_rollout_ref"]["actor"]["ppo_epochs"], 2)

    def test_allocation_budget_requires_six_hours_plus_margin(self):
        end = datetime.fromtimestamp(100000).isoformat()
        info = "EndTime=" + end
        self.assertEqual(runner.require_remaining_allocation(info, 21600, now=77500), 22500)
        with self.assertRaisesRegex(ValueError, "remaining allocation"):
            runner.require_remaining_allocation(info, 21600, now=77501)
        with self.assertRaisesRegex(ValueError, "EndTime"):
            runner.require_remaining_allocation("EndTime=Unknown", 21600)

    def test_bad_allocation_never_launches_or_creates_output(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            args = SimpleNamespace(bundle=bundle, training_panel=bundle / "panel", output=bundle / "runs/comparison",
                                   job_id=1176227, commit="a" * 40, training_sha256="b" * 64, arm="root")
            with patch.object(runner.subprocess, "check_output", side_effect=[
                    "JobId=1176227 Account=def-zhijing JobState=PENDING NodeList=trig0012", "trig0012\n"]), \
                    patch.object(screen, "run_bounded") as launch:
                with self.assertRaisesRegex(ValueError, "not running"):
                    runner.run(args)
            launch.assert_not_called()
            self.assertFalse(args.output.exists())


if __name__ == "__main__":
    unittest.main()
