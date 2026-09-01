import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from verl.lean.hard_blocking import (
    REJECT_REWARD,
    ZERO_ADVANTAGE,
    apply_hard_exclusion,
    assert_pristine_restart,
    effective_binary_rewards,
    effective_success_indices,
    should_skip_prompt,
    validate_intervention,
    zero_blocked_advantages,
)
from verl.lean.mode_archive import ModeArchive
from verl.lean.proof_modes import canonicalize_proof, mode_id


class ProofModeTests(unittest.TestCase):
    def test_comments_and_whitespace_do_not_change_mode(self):
        a = "by\n  -- comment\n  intro h\n  exact h"
        b = "by\n\n intro   h\n\n exact h"
        self.assertEqual(canonicalize_proof(a), canonicalize_proof(b))
        self.assertEqual(mode_id(a), mode_id(b))

    def test_material_tactic_heads_change_mode(self):
        self.assertNotEqual(mode_id("by\n  intro h\n  exact h"), mode_id("by\n  intro h\n  assumption"))

    def test_archive_round_trip_and_dominance_boundaries(self):
        archive = ModeArchive(metadata={"source_condition": "c0_base"})
        for _ in range(4):
            archive.add("T", "a")
        for _ in range(4):
            archive.add("T", "b")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive.json"
            checksum = archive.save(path)
            loaded = ModeArchive.load(path)
            self.assertEqual(loaded.to_dict(), archive.to_dict())
            self.assertEqual(loaded.metadata, archive.metadata)
            self.assertEqual(checksum, archive.save(Path(directory) / "archive-copy.json"))
        self.assertIsNone(archive.dominant_mode("T", threshold=0.5))  # exactly at boundary
        archive.add("T", "a")
        self.assertEqual(archive.dominant_mode("T", threshold=0.5), "a")  # above boundary
        self.assertIsNone(archive.dominant_mode("T", threshold=0.6))  # below boundary


class HardBlockingTests(unittest.TestCase):
    def test_zero_advantage_keeps_lean_correct_training_successes(self):
        accepted = effective_success_indices(
            [1, 3], [False, True, False, False], intervention=ZERO_ADVANTAGE
        )
        self.assertEqual(accepted, {1, 3})

    def test_reward_rejection_removes_only_blocked_correct_successes(self):
        accepted = effective_success_indices(
            [1, 3], [False, True, False, False], intervention=REJECT_REWARD
        )
        self.assertEqual(accepted, {3})

    def test_reward_rejection_changes_only_the_blocked_correct_reward(self):
        rewards = effective_binary_rewards(
            4, [1, 3], [False, True, False, False], intervention=REJECT_REWARD
        )
        self.assertEqual(rewards, [0.0, 0.0, 0.0, 1.0])

    def test_zero_advantage_preserves_upstream_binary_rewards(self):
        rewards = effective_binary_rewards(
            4, [1, 3], [False, True, False, False], intervention=ZERO_ADVANTAGE
        )
        self.assertEqual(rewards, [0.0, 1.0, 0.0, 1.0])

    def test_reward_rejection_can_leave_no_accepted_solution(self):
        accepted = effective_success_indices(
            [1, 3], [False, True, False, True], intervention=REJECT_REWARD
        )
        self.assertEqual(accepted, set())

    def test_unknown_intervention_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported hard-block intervention"):
            validate_intervention("silently-do-something-else")

    def test_success_index_outside_metadata_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "outside blocked_correct metadata"):
            effective_success_indices([2], [False, False], intervention=REJECT_REWARD)

    def test_blocked_correct_advantages_are_zero_only_for_blocked_rollouts(self):
        upstream = torch.tensor([1.25, -0.75, 0.50])
        result = zero_blocked_advantages(upstream, [False, True, False])
        self.assertTrue(torch.equal(result, torch.tensor([1.25, 0.0, 0.50])))
        self.assertEqual(result[0].item(), upstream[0].item())  # incorrect treatment unchanged

    def test_object_array_blocked_mask_is_normalized_to_boolean(self):
        upstream = torch.tensor([1.25, -0.75, 0.50])
        blocked = np.asarray([False, True, False], dtype=object)
        result = zero_blocked_advantages(upstream, blocked)
        self.assertTrue(torch.equal(result, torch.tensor([1.25, 0.0, 0.50])))

    def test_disabled_blocking_is_bit_for_bit_equivalent(self):
        upstream = torch.tensor([0.125, -0.25, 1.0])
        disabled_path = apply_hard_exclusion(upstream, enabled=False)
        self.assertIs(disabled_path, upstream)
        self.assertTrue(torch.equal(upstream, disabled_path))

    def test_all_blocked_correct_prompt_is_skipped_but_all_incorrect_is_not(self):
        self.assertTrue(should_skip_prompt([1, 3], [False, True, False, True]))
        self.assertFalse(should_skip_prompt([1, 3], [False, True, False, False]))
        self.assertFalse(should_skip_prompt([], [False, False]))

    def test_restart_refuses_non_base_checkpoint_unless_control(self):
        kwargs = dict(
            enabled=True,
            archive_path="archive.json",
            base_model_path="/models/base",
            model_path="/models/c1-checkpoint",
            resume=False,
            resume_train_batch_buffer=None,
        )
        with self.assertRaisesRegex(ValueError, "pristine base"):
            assert_pristine_restart(**kwargs)
        assert_pristine_restart(**kwargs, is_control=True)
        with self.assertRaisesRegex(ValueError, "fresh optimizer"):
            assert_pristine_restart(**{**kwargs, "model_path": "/models/base", "resume": True})


if __name__ == "__main__":
    unittest.main()
