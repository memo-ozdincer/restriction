"""CPU tests of actual step accounting and final weight completeness."""
import ast
import copy
import json
import math
import os
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts.project import execution_training_telemetry as telemetry
from verl.lean.telemetry import telemetry_identity

ROOT = Path(__file__).resolve().parents[1]


def actor_events(rank, applied=(True, False)):
    common = {"schema_version": 1, "role": "actor", "rank": rank,
              "hostname": "node", "pid": 100 + rank, "update_index": 1}
    rows = [{"event": "actor_update_begin", "rows": 64, "ppo_epochs": 2,
             "mini_batch_size": 64, "response_tokens": 128},
            *[{"event": "optimizer_attempt", "ppo_epoch": epoch, "mini_batch_index": 0,
               "response_tokens": 128, "applied": value} for epoch, value in enumerate(applied)],
            {"event": "actor_update_end", "optimizer_attempts": 2,
             "optimizer_steps_applied": sum(applied), "optimizer_steps_skipped": 2 - sum(applied)}]
    return [{**common, **row, "sequence": index} for index, row in enumerate(rows, 1)]


class AccountingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        resolved_config = {"trainer": {"total_training_steps": 64}}
        environment = {"git_commit": "pinned"}
        config_hash, environment_hash = telemetry_identity(
            json.dumps(resolved_config, sort_keys=True, separators=(",", ":")), environment)
        driver = [{"event": "runtime_config", "resolved_config": resolved_config,
                   "environment": environment, "config_hash": config_hash, "environment_hash": environment_hash},
                  {"event": "rollout_batch", "groups": 16, "samples_per_group": 32,
                   "admitted_groups": 8, "skipped_groups": 8},
                  {"event": "actor_dispatch_complete", "rows": 256},
                  {"event": "checkpoint_saved", "checkpoint": "/run/actor/global_step_1"}]
        self.driver = [{"schema_version": 1, "role": "driver", "rank": -1, "hostname": "node",
                        "pid": 99, "sequence": i, "step": 1, **row} for i, row in enumerate(driver, 1)]
        self.write("driver", self.driver)
        for rank in range(4):
            self.write(f"rank{rank}", actor_events(rank))

    def write(self, name, rows):
        (self.root / (name + ".jsonl")).write_text("".join(json.dumps(row) + "\n" for row in rows))

    def summarize(self):
        return telemetry.summarize_telemetry(self.root, expected_steps=1)

    def test_applied_updates_are_not_scheduler_calls_or_summed_gpu_counts(self):
        result = self.summarize()
        self.assertEqual(result["actor_update_calls"], 1)
        self.assertEqual(result["optimizer_attempts"], 2)
        self.assertEqual(result["actual_optimizer_steps"], 1)
        self.assertEqual(result["skipped_optimizer_steps"], 1)
        self.assertEqual(result["optimized_response_tokens"], 512)
        self.assertEqual(result["response_token_exposures_with_ppo_epochs"], 1024)
        self.assertEqual(result["admitted_groups"], 8)
        self.assertEqual(result["skipped_groups"], 8)
        self.assertEqual(result["residual_buffer_rows"], 0)

    def test_missing_rank_incomplete_update_and_rank_disagreement_fail(self):
        (self.root / "rank3.jsonl").unlink()
        with self.assertRaisesRegex(ValueError, "actor ranks"):
            self.summarize()
        self.write("rank3", actor_events(3)[:-1])
        with self.assertRaisesRegex(ValueError, "incomplete actor update"):
            self.summarize()
        self.write("rank3", actor_events(3, (True, True)))
        with self.assertRaisesRegex(ValueError, "rank optimizer"):
            self.summarize()

    def test_no_actual_updates_or_final_checkpoint_never_passes(self):
        for rank in range(4):
            self.write(f"rank{rank}", actor_events(rank, (False, False)))
        with self.assertRaisesRegex(ValueError, "no actual optimizer"):
            self.summarize()
        for rank in range(4):
            self.write(f"rank{rank}", actor_events(rank))
        self.write("driver", self.driver[:-1])
        with self.assertRaisesRegex(ValueError, "final checkpoint"):
            self.summarize()

    def test_changed_token_counts_and_missing_batches_fail(self):
        rows = actor_events(0)
        rows[1]["response_tokens"] += 1
        self.write("rank0", rows)
        with self.assertRaisesRegex(ValueError, "token exposure"):
            self.summarize()
        self.write("rank0", actor_events(0))
        self.write("driver", [row for row in self.driver if row["event"] != "rollout_batch"])
        with self.assertRaisesRegex(ValueError, "rollout steps"):
            self.summarize()

    def test_runtime_config_is_required_once_with_matching_proof_telemetry_hashes(self):
        result = self.summarize()
        self.assertEqual(result["config_hash"], self.driver[0]["config_hash"])
        self.assertEqual(result["environment_hash"], self.driver[0]["environment_hash"])
        bad = copy.deepcopy(self.driver)
        bad[0]["environment"]["git_commit"] = "changed"
        self.write("driver", bad)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.summarize()
        self.write("driver", self.driver[1:])
        with self.assertRaisesRegex(ValueError, "runtime configuration"):
            self.summarize()

    def test_emitter_is_disabled_without_environment_and_fsyncs_when_enabled(self):
        with patch.dict(os.environ, {}, clear=True):
            telemetry.emit_event("test", role="driver")
        with patch.dict(os.environ, {"EXECUTION_TRAINING_TELEMETRY": str(self.root)}), patch.object(os, "fsync") as fsync:
            telemetry.emit_event("test", role="driver")
            fsync.assert_called_once()


class RealOptimizerDecisionTests(unittest.TestCase):
    """Execute the actual source method without importing GPU-only packages."""
    def method(self, norm, enabled):
        tree = ast.parse((ROOT / "verl/workers/actor/dp_actor.py").read_text())
        actor = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DataParallelPPOActor")
        method = next(node for node in actor.body if isinstance(node, ast.FunctionDef) and node.name == "_optimizer_step")
        events = []
        fake_torch = SimpleNamespace(isfinite=math.isfinite,
            nn=SimpleNamespace(utils=SimpleNamespace(clip_grad_norm_=lambda *args, **kwargs: norm)))
        namespace = {"torch": fake_torch, "FSDP": type("FSDP", (), {}),
                     "telemetry_enabled": lambda: enabled,
                     "emit_event": lambda *args, **kwargs: events.append((args, kwargs))}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "actual_optimizer_step", "exec"), namespace)
        config = SimpleNamespace(grad_clip=1.0, get=lambda key, default: 20.0)
        state = SimpleNamespace(config=config, actor_module=SimpleNamespace(parameters=lambda: []),
            actor_optimizer=SimpleNamespace(step=Mock()), _execution_optimizer_attempts=0,
            _execution_optimizer_applied=0, _execution_optimized_tokens=0,
            _execution_update_index=1, _execution_attempt_context={"response_tokens": 9, "ppo_epoch": 0, "mini_batch_index": 0})
        value = namespace["_optimizer_step"](state)
        return state, events, value

    def test_unchanged_gradient_boundary_and_actual_call_counts(self):
        for norm, applied in ((1.0, True), (19.99, True), (20.0, False), (float("inf"), False), (float("nan"), False)):
            for enabled in (False, True):
                with self.subTest(norm=norm, enabled=enabled):
                    state, events, value = self.method(norm, enabled)
                    self.assertEqual(state.actor_optimizer.step.call_count, int(applied))
                    self.assertEqual(len(events), int(enabled))
                    if enabled:
                        self.assertEqual(state._execution_optimizer_applied, int(applied))
                        self.assertEqual(state._execution_optimized_tokens, 9 * int(applied))
                        self.assertEqual(events[0][1]["applied"], applied)


def write_weights(root, *, shape=(2,), dtype="F32", values=b"\0" * 8):
    spec = {"weight": {"dtype": dtype, "shape": list(shape), "data_offsets": [0, len(values)]}}
    header = json.dumps(spec).encode()
    (root / "model.safetensors").write_bytes(struct.pack("<Q", len(header)) + header + values)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / "base"
        self.actor = self.root / "global_step_64"
        for directory in (self.base, self.actor):
            directory.mkdir()
            write_weights(directory)
            (directory / "config.json").write_text(json.dumps({"model_type": "test", "eos_token_id": 1}))
            (directory / "tokenizer.json").write_text('{"model": {"type": "test"}}')
            (directory / "tokenizer_config.json").write_text('{"eos_token": "EOS"}')
            (directory / "special_tokens_map.json").write_text('{"eos_token": "EOS"}')
        self.expected_tokenizer = {filename: json.loads((self.base / filename).read_text()) for filename in
                                   ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json")}
        normalization = patch.object(telemetry, "normalized_tokenizer_files", return_value=self.expected_tokenizer)
        normalization.start()
        self.addCleanup(normalization.stop)

    def test_complete_checkpoint_has_hashes_and_explicit_no_resume_claim(self):
        result = telemetry.validate_actor_checkpoint(self.actor, self.base)
        self.assertTrue(result["complete"])
        self.assertEqual(result["tensor_count"], 1)
        self.assertFalse(result["exact_resume_supported"])
        self.assertIn("model.safetensors", result["files"])

    def test_truncated_weights_shape_changes_and_missing_tokenizer_fail(self):
        file = self.actor / "model.safetensors"
        file.write_bytes(file.read_bytes()[:-1])
        with self.assertRaisesRegex(ValueError, "payload"):
            telemetry.validate_actor_checkpoint(self.actor, self.base)
        write_weights(self.actor, shape=(1, 2))
        with self.assertRaisesRegex(ValueError, "shapes differ"):
            telemetry.validate_actor_checkpoint(self.actor, self.base)
        write_weights(self.actor)
        (self.actor / "tokenizer.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing checkpoint file"):
            telemetry.validate_actor_checkpoint(self.actor, self.base)

    def test_sharded_checkpoint_requires_every_indexed_tensor_and_exact_size(self):
        shard = self.actor / "model-00001-of-00001.safetensors"
        (self.actor / "model.safetensors").rename(shard)
        index = {"metadata": {"total_size": 8}, "weight_map": {"weight": shard.name}}
        path = self.actor / "model.safetensors.index.json"
        path.write_text(json.dumps(index))
        self.assertTrue(telemetry.validate_actor_checkpoint(self.actor, self.base)["complete"])
        index["weight_map"]["missing"] = shard.name
        path.write_text(json.dumps(index))
        with self.assertRaisesRegex(ValueError, "incomplete checkpoint"):
            telemetry.validate_actor_checkpoint(self.actor, self.base)

    def test_tokenizer_semantics_and_complete_special_tokens_are_authenticated(self):
        (self.actor / "tokenizer.json").write_text('{"model": {"type": "changed"}}')
        with self.assertRaisesRegex(ValueError, "tokenizer differs"):
            telemetry.validate_actor_checkpoint(self.actor, self.base)
        (self.actor / "tokenizer.json").write_text(json.dumps(self.expected_tokenizer["tokenizer.json"], indent=3))
        self.assertTrue(telemetry.validate_actor_checkpoint(self.actor, self.base)["complete"])
        (self.actor / "special_tokens_map.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing checkpoint file"):
            telemetry.validate_actor_checkpoint(self.actor, self.base)


if __name__ == "__main__":
    unittest.main()
