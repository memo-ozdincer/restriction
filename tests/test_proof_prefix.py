"""Run the production continuation path with a fake actor and verifier.

These tests cover token attribution and task reconstruction, not Lean prefix
validity or learning quality. No Ray workers or GPUs are started.
"""

import ast
from collections import defaultdict
from contextlib import nullcontext, redirect_stdout
import io
import json
from pathlib import Path
from types import SimpleNamespace
from typing import List
import unittest

import numpy as np
import torch

from verl import DataProto
from verl.protocol import pad_dataproto_to_divisor
import verl.lean.utils as lean_utils
from verl.lean.hard_blocking import ZERO_ADVANTAGE
from verl.lean.prompts import prompt_fn_deepseek
from verl.lean.proof_prefix import assemble_proofs, conditioning_id, pilot_record, prefix_record, proof_prefixes
from verl.lean.telemetry import build_proposal_telemetry
from verl.utils.model import compute_position_id_with_mask
import verl.utils.torch_functional as verl_F


SOURCE = Path(__file__).resolve().parents[1] / "verl/trainer/ppo/ray_lean_trainer.py"


class CharacterTokenizer:
    pad_token_id = 0

    def __call__(self, text, **kwargs):
        ids = torch.tensor([[ord(char) + 1 for char in text]], dtype=torch.long)
        return {"input_ids": ids, "attention_mask": torch.ones_like(ids)}

    def decode(self, ids, **kwargs):
        return "".join(chr(int(token) - 1) for token in ids if token)


class PrefixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(SOURCE.read_text())
        trainer = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                       and node.name == "RayLeanTrainer")
        names = {"_generate_and_verify_full_proofs", "_format_model_input", "_compute_advantages", "_pad_problem_batch"}
        methods = [node for node in trainer.body if isinstance(node, ast.FunctionDef) and node.name in names]
        cls.namespace = dict(
            torch=torch, np=np, json=json, os=SimpleNamespace(), List=List,
            DataProto=DataProto, defaultdict=defaultdict, lean_utils=lean_utils,
            proof_prefixes=proof_prefixes, assemble_proofs=assemble_proofs,
            conditioning_id=conditioning_id, prefix_record=prefix_record,
            pilot_record=pilot_record, pad_dataproto_to_divisor=pad_dataproto_to_divisor,
            build_proposal_telemetry=build_proposal_telemetry, ZERO_ADVANTAGE=ZERO_ADVANTAGE,
            verl_F=verl_F, compute_position_id_with_mask=compute_position_id_with_mask,
            masked_mean=verl_F.masked_mean, _timer=lambda *args, **kwargs: nullcontext(),
        )
        exec(compile(ast.Module(body=methods, type_ignores=[]), str(SOURCE), "exec"), cls.namespace)

    def run_path(self, prefixes=None, *, max_prompt_length=1024, pilot=False):
        suffixes = ["  exact True.intro\n```", "  invalid\n```"] * 2
        tokenizer = CharacterTokenizer()
        lean = SimpleNamespace(
            prompt_key="deepseek-prover", max_workers=1, rejection_sampling=False,
            advantage_threshold=True, max_samples=32, get=lambda key, default=None: default,
        )
        trainer = SimpleNamespace(
            config=SimpleNamespace(lean=lean, data=SimpleNamespace(max_prompt_length=max_prompt_length),
                                   trainer=SimpleNamespace(experiment_name="prefix-unit")),
            tokenizer=tokenizer, prompt_fn=prompt_fn_deepseek, terminal_token="```",
            _proof_telemetry_identity=("config", "environment"), global_steps=1,
            mode_archive=None, hard_blocking_intervention=ZERO_ADVANTAGE, lean_proofs=[],
        )
        observed = {}

        def generate(batch):
            observed["prompts"] = [tokenizer.decode(row) for row in batch.batch["input_ids"]]
            width = max(map(len, suffixes))
            response_ids = torch.tensor([[ord(c) + 1 for c in text] + [0] * (width - len(text))
                                         for text in suffixes])
            response_mask = response_ids.ne(0).long()
            observed["response_ids"] = response_ids.clone()
            return DataProto.from_dict({
                "responses": response_ids,
                "input_ids": torch.cat([batch.batch["input_ids"], response_ids], dim=1),
                "attention_mask": torch.cat([batch.batch["attention_mask"], response_mask], dim=1),
            })

        def verify(proofs, statements, contexts, **kwargs):
            observed["verified"] = proofs
            observed["contexts"] = contexts.tolist()
            return [dict(success_indices=[0], num_success=1, num_errors=1, msg="synthetic",
                         candidate_results=[{"verdict": True, "lean_complete": True},
                                            {"verdict": False, "lean_complete": False}]) for _ in statements]

        self.namespace["verify_with_deepseek_verifier"] = verify
        trainer.actor_rollout_wg = SimpleNamespace(generate_sequences=generate)
        trainer._format_model_input = lambda *args, **kwargs: self.namespace["_format_model_input"](
            trainer, *args, **kwargs)
        metadata = {
            "theorem_statement": np.array(["theorem same : True := by\n"] * 2, dtype=object),
            "theorem_full_name": np.array(["same"] * 2, dtype=object),
            "src_context": np.array(["import Mathlib\n"] * 2, dtype=object),
            "uid": np.array(["same-parent-id"] * 2, dtype=object),
        }
        if prefixes is not None:
            metadata["proof_prefix"] = np.array(prefixes, dtype=object)
        if pilot:
            metadata.update(
                pilot_row_id=np.array(["row1", "row2"], dtype=object),
                pilot_split=np.array(["diagnostic", "diagnostic"], dtype=object),
                pilot_padding=np.array([False, True], dtype=np.bool_),
            )
        problem = DataProto.from_single_dict({"dummy": torch.zeros((2, 1)), **metadata})
        with redirect_stdout(io.StringIO()):
            batch, metrics = self.namespace["_generate_and_verify_full_proofs"](trainer, problem, 2)
        return trainer, batch, observed, metrics

    def test_prefix_is_context_but_full_proof_is_verified_and_logged(self):
        prefixes = ["  have h : True := True.intro\n", "  constructor\n"]
        trainer, batch, observed, _ = self.run_path(prefixes)
        self.assertTrue(torch.equal(batch.batch["responses"], observed["response_ids"]))
        for i, record in enumerate(trainer.lean_proofs):
            prefix = prefixes[i // 2]
            suffix = record["generated_suffix"]
            self.assertEqual(observed["verified"][i], prefix + suffix)
            self.assertEqual(record["proof"], prefix + suffix)
            self.assertEqual(record["context"], "import Mathlib\n")
            self.assertEqual(record["token_count"], len(suffix))
            self.assertEqual(record["prompt_token_count"], len(observed["prompts"][i]))
            self.assertTrue(observed["prompts"][i].endswith(prefix))
        self.assertEqual(batch.non_tensor_batch["full_proofs"].tolist(), observed["verified"])
        self.assertNotEqual(batch.non_tensor_batch["uid"][0], batch.non_tensor_batch["uid"][2])
        self.assertEqual(batch.non_tensor_batch["uid"][0], batch.non_tensor_batch["uid"][1])
        batch.batch["old_log_probs"] = torch.zeros_like(batch.batch["responses"], dtype=torch.float32)
        batch = self.namespace["_compute_advantages"](trainer, batch)
        self.assertEqual(batch.batch["advantages"].shape, batch.batch["responses"].shape)
        self.assertTrue(torch.all(batch.batch["advantages"][batch.batch["responses"] == 0] == 0))

    def test_empty_prefix_matches_absent_path_exactly(self):
        absent, absent_batch, absent_seen, absent_metrics = self.run_path()
        empty, empty_batch, empty_seen, empty_metrics = self.run_path(["", ""])
        self.assertEqual(absent.lean_proofs, empty.lean_proofs)
        self.assertEqual(absent_seen["prompts"], empty_seen["prompts"])
        self.assertEqual(absent_seen["verified"], empty_seen["verified"])
        for key in absent_batch.batch.keys():
            self.assertTrue(torch.equal(absent_batch.batch[key], empty_batch.batch[key]), key)
        for key in absent_metrics:
            self.assertEqual(absent_metrics[key], empty_metrics[key])

    def test_prefix_prompt_cannot_be_silently_truncated(self):
        with self.assertRaisesRegex(NotImplementedError, "larger than"):
            self.run_path(["  have h : True := True.intro\n", ""], max_prompt_length=8)
        # The historical path still uses its previous left-truncation behavior.
        self.run_path(max_prompt_length=8)

    def test_prefix_validation_rejects_missing_values_or_unsupported_prompt(self):
        for values in ([None, ""], [1, ""], ["```", ""], [""]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                proof_prefixes({"proof_prefix": values}, 2, "deepseek-prover")
        with self.assertRaises(ValueError):
            proof_prefixes({"proof_prefix": ["  intro h\n"]}, 1, "internlm2-step-prover")

    def test_pilot_identity_and_padding_are_logged_for_root_rows(self):
        trainer, _, observed, metrics = self.run_path(pilot=True)
        self.assertEqual([p["pilot_row_id"] for p in trainer.lean_proofs], ["row1", "row1", "row2", "row2"])
        self.assertEqual([p["pilot_padding"] for p in trainer.lean_proofs], [False, False, True, True])
        self.assertTrue(all(p["pilot_split"] == "diagnostic" for p in trainer.lean_proofs))
        self.assertEqual(metrics["num_physical_proposals"], 4)
        self.assertEqual(metrics["num_pilot_padding_proposals"], 2)
        for i, record in enumerate(trainer.lean_proofs):
            self.assertEqual(record["prompt_token_count"], len(observed["prompts"][i]))

    def test_only_sample_only_pilot_can_duplicate_rows_and_marks_them(self):
        problem = DataProto.from_single_dict({
            "dummy": torch.zeros((3, 1)),
            "pilot_row_id": np.array(["row1", "row2", "row3"], dtype=object),
        })
        trainer = SimpleNamespace(actor_rollout_wg=SimpleNamespace(world_size=4),
                                  config=SimpleNamespace(trainer={"sample_only": False}))
        with self.assertRaisesRegex(ValueError, "refusing duplicate"):
            self.namespace["_pad_problem_batch"](trainer, problem)
        trainer.config.trainer["sample_only"] = True
        padded = self.namespace["_pad_problem_batch"](trainer, problem)
        self.assertEqual(padded.non_tensor_batch["pilot_row_id"].tolist(), ["row1", "row2", "row3", "row1"])
        self.assertEqual(padded.non_tensor_batch["pilot_padding"].tolist(), [False, False, False, True])

    def test_advantage_normalization_cannot_mix_conditioned_tasks(self):
        trainer, batch, _, _ = self.run_path(["  constructor\n", "  have h : True := True.intro\n"])
        batch.batch["rewards"] = torch.tensor([1., 0., 1., 1.])
        batch.batch["old_log_probs"] = torch.zeros_like(batch.batch["responses"], dtype=torch.float32)
        batch = self.namespace["_compute_advantages"](trainer, batch)
        self.assertGreater(batch.batch["advantages"][0, 0], 0)
        self.assertLess(batch.batch["advantages"][1, 0], 0)
        self.assertTrue(torch.all(batch.batch["advantages"][2:] == 0))


if __name__ == "__main__":
    unittest.main()
