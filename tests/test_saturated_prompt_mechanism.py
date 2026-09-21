"""Exercise production selection/advantage code without Ray or GPU startup.

AST extraction deliberately executes the source statements rather than a
second implementation of the admission rule. Generation, Lean correctness and
archive membership are supplied as synthetic inputs, not tested here.
"""

import ast
from collections import defaultdict
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import torch

from verl.lean.hard_blocking import (
    REJECT_REWARD, ZERO_ADVANTAGE, advantage_summary, apply_hard_exclusion,
    effective_binary_rewards, effective_success_indices, should_skip_prompt,
)
from verl.utils.torch_functional import masked_mean


SOURCE = Path(__file__).resolve().parents[1] / "verl/trainer/ppo/ray_lean_trainer.py"


class SaturatedPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(SOURCE.read_text())
        trainer = next(node for node in tree.body
                       if isinstance(node, ast.ClassDef) and node.name == "RayLeanTrainer")
        methods = {node.name: node for node in trainer.body if isinstance(node, ast.FunctionDef)}
        body = methods["_generate_and_verify_full_proofs"].body

        def assigns(node, name):
            return isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == name for target in node.targets)

        start = next(i for i, node in enumerate(body) if assigns(node, "selected_idxs"))
        end = next(i for i in range(start + 1, len(body)) if assigns(body[i], "gen_tensors"))
        cls.selection = compile(ast.Module(body=body[start:end], type_ignores=[]), str(SOURCE), "exec")
        namespace = dict(
            torch=torch, defaultdict=defaultdict, json=json, masked_mean=masked_mean,
            ZERO_ADVANTAGE=ZERO_ADVANTAGE, apply_hard_exclusion=apply_hard_exclusion,
            advantage_summary=advantage_summary,
        )
        exec(compile(ast.Module(body=[methods["_compute_advantages"]], type_ignores=[]),
                     str(SOURCE), "exec"), namespace)
        cls.compute = staticmethod(namespace["_compute_advantages"])

    def run_group(self, condition, proofs, successes, *, threshold=True):
        blocking = condition in ("C3", "C5")
        intervention = REJECT_REWARD if condition == "C5" else ZERO_ADVANTAGE
        lean = SimpleNamespace(
            hard_blocking=SimpleNamespace(threshold=0.5, min_verified=1),
            rejection_sampling=False, advantage_threshold=threshold, max_samples=10000,
            get=lambda key, default: (0.25 if condition == "C2" else 0.0)
            if key == "rank_penalty" else default,
        )
        archive = SimpleNamespace(is_blocked=lambda theorem, mode, *_: mode == "blocked")
        trainer = SimpleNamespace(config=SimpleNamespace(lean=lean),
                                  mode_archive=archive if blocking else None,
                                  hard_blocking_intervention=intervention)
        context = dict(
            self=trainer, num_samples=len(proofs), proofs=proofs,
            outputs=[{"success_indices": successes}], theorem_full_names=["synthetic"],
            problem_batch=[SimpleNamespace(non_tensor_batch={"uid": "synthetic"})],
            defaultdict=defaultdict, mode_id=lambda proof: proof,
            effective_success_indices=effective_success_indices,
            effective_binary_rewards=effective_binary_rewards,
            should_skip_prompt=should_skip_prompt,
        )
        exec(self.selection, context)
        indices = context["selected_idxs"]
        advantages = []
        if indices:
            count = len(indices)
            batch = SimpleNamespace(
                batch={"rewards": torch.tensor(context["rewards"], dtype=torch.float32),
                       "old_log_probs": -torch.arange(1, count + 1, dtype=torch.float32)[:, None],
                       "responses": torch.zeros((count, 1), dtype=torch.long),
                       "attention_mask": torch.ones((count, 1))},
                non_tensor_batch={"uid": context["metadata"]["uid"]},
            )
            if blocking:
                batch.non_tensor_batch["blocked_correct"] = context["blocked_correct"]
            with redirect_stdout(io.StringIO()):
                self.compute(trainer, batch)
            advantages = batch.batch["advantages"][:, 0].tolist()
        return indices, advantages, context["skipped_all_blocked_prompts"]

    def test_all_correct_mixed_modes_are_admitted_only_by_rejection(self):
        proofs = ["blocked", "blocked", "alternative", "alternative"]
        for condition in ("C1", "C2", "C3"):
            with self.subTest(condition=condition):
                self.assertEqual(self.run_group(condition, proofs, range(4)), ([], [], 0))
        indices, advantages, skipped = self.run_group("C5", proofs, range(4))
        self.assertEqual(indices, list(range(4)))
        self.assertEqual(skipped, 0)
        self.assertTrue(all(value < 0 for value in advantages[:2]))
        self.assertTrue(all(value > 0 for value in advantages[2:]))

    def test_all_blocked_and_no_alternative_is_skipped(self):
        for condition in ("C3", "C5"):
            for proofs, successes in ((["blocked"] * 4, range(4)),
                                      (["blocked", "incorrect"], [0])):
                with self.subTest(condition=condition, proofs=proofs):
                    self.assertEqual(self.run_group(condition, proofs, successes), ([], [], 1))

    def test_no_blocked_modes_preserves_all_correct_filter(self):
        for condition in ("C1", "C2", "C3", "C5"):
            with self.subTest(condition=condition):
                self.assertEqual(self.run_group(condition, ["alternative"] * 4, range(4)), ([], [], 0))

    def test_c2_can_learn_from_all_correct_when_admission_filter_is_disabled(self):
        indices, advantages, skipped = self.run_group(
            "C2", ["alternative"] * 4, range(4), threshold=False)
        self.assertEqual(indices, list(range(4)))
        self.assertEqual(skipped, 0)
        self.assertLess(advantages[0], 0)  # most likely proof
        self.assertGreater(advantages[-1], 0)  # least likely proof

    def test_mixed_correctness_distinguishes_zeroing_from_rejection(self):
        proofs = ["blocked", "alternative", "incorrect", "incorrect"]
        for condition in ("C3", "C5"):
            indices, advantages, skipped = self.run_group(condition, proofs, [0, 1])
            self.assertEqual(indices, list(range(4)))
            self.assertEqual(skipped, 0)
            if condition == "C3":
                self.assertEqual(advantages[0], 0)
            else:
                self.assertLess(advantages[0], 0)
            self.assertGreater(advantages[1], 0)
            self.assertTrue(all(value < 0 for value in advantages[2:]))


if __name__ == "__main__":
    unittest.main()
