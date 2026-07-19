import tempfile
import unittest
from pathlib import Path

import torch

from verl.lean.hard_blocking import (
    apply_hard_exclusion,
    assert_pristine_restart,
    should_skip_prompt,
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
    def test_blocked_correct_advantages_are_zero_only_for_blocked_rollouts(self):
        upstream = torch.tensor([1.25, -0.75, 0.50])
        result = zero_blocked_advantages(upstream, [False, True, False])
        self.assertTrue(torch.equal(result, torch.tensor([1.25, 0.0, 0.50])))
        self.assertEqual(result[0].item(), upstream[0].item())  # incorrect treatment unchanged

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
