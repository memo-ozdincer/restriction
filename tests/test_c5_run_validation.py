import json
import tempfile
import unittest
from pathlib import Path

from scripts.project.validate_c5_reward_reject_run import training_accounting, validate


def summary(blocked: int, alternative: int, incorrect: int) -> str:
    return "[HARD_BLOCKING] " + json.dumps(
        {
            "intervention": "reject_reward",
            "blocked_correct_count": blocked,
            "blocked_correct_advantage_mean": -1.0 if blocked else None,
            "alternative_correct_count": alternative,
            "alternative_correct_advantage_mean": 1.0 if alternative else None,
            "incorrect_count": incorrect,
            "incorrect_advantage_mean": -0.5 if incorrect else None,
        }
    )


class C5RunValidationTests(unittest.TestCase):
    def test_training_accounting_tracks_buffered_steps_and_residual(self):
        log = "\n".join(
            [
                "[TRAINING] Step train batch size: 224",
                "[TRAINING] Buffer size: 224",
                "[TRAINING] Step train batch size: 480",
                "[TRAINING] Buffer size: 704",
                "[TRAINING] Update train batch size: 704",
                summary(19, 468, 217),
                "[TRAINING] Step train batch size: 192",
                "[TRAINING] Buffer size: 192",
            ]
        )

        result = training_accounting(log)

        self.assertEqual(result["step_sizes"], [224, 480, 192])
        self.assertEqual(result["update_sizes"], [704])
        self.assertEqual(result["retained_samples"], 896)
        self.assertEqual(result["optimized_samples"], 704)
        self.assertEqual(result["residual_buffer_samples"], 192)
        self.assertEqual(len(result["summaries"]), 1)

    def test_training_accounting_rejects_summary_per_data_step_assumption(self):
        log = "\n".join(
            [
                "[TRAINING] Step train batch size: 224",
                summary(8, 150, 66),
                "[TRAINING] Step train batch size: 480",
                "[TRAINING] Update train batch size: 704",
                summary(19, 468, 217),
            ]
        )

        with self.assertRaisesRegex(ValueError, "summaries for 1 optimizer updates"):
            training_accounting(log)

    def test_training_accounting_rejects_uncategorized_update_samples(self):
        log = "\n".join(
            [
                "[TRAINING] Step train batch size: 320",
                "[TRAINING] Update train batch size: 320",
                summary(8, 227, 84),
            ]
        )

        with self.assertRaisesRegex(ValueError, "categorizes 319 samples"):
            training_accounting(log)

    def test_validate_accepts_buffered_steps_and_subthreshold_residual(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            checkpoint = run_dir / "artifacts" / "actor" / "global_step_3"
            checkpoint.mkdir(parents=True)
            log = "\n".join(
                [
                    "[TRAINING] Step train batch size: 224",
                    "[TRAINING] Buffer size: 224",
                    "[TRAINING] Step train batch size: 480",
                    "[TRAINING] Buffer size: 704",
                    "[TRAINING] Update train batch size: 704",
                    summary(19, 468, 217),
                    "[TRAINING] Step train batch size: 192",
                    "[TRAINING] Buffer size: 192",
                ]
            )
            (run_dir / "run.log").write_text(log, encoding="utf-8")
            metrics = {
                "condition": "c5_reward_reject_restart",
                "classification": "exploratory_full_seed42_h100",
                "proposals": 308_960,
                "physical_proposals": 308_992,
                "excluded_padding_proposals": 32,
                "expected_registered_proposals": 308_960,
                "theorems_with_rollouts": 9_655,
                "expected_training_theorems": 9_655,
                "archive_sha256": (
                    "fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3"
                ),
                "blocked_correct": 19,
                "blocked_correct_zero_advantage": 0,
                "blocked_correct_reward_rejected": 19,
                "physical_blocked_correct": 19,
                "physical_blocked_correct_zero_advantage": 0,
                "physical_blocked_correct_reward_rejected": 19,
                "actor_checkpoint": str(checkpoint),
                "update_batch_samples": 896,
                "correct": 42,
                "correct_mode_coverage": 37,
            }
            (run_dir / "metrics.json").write_text(
                json.dumps(metrics), encoding="utf-8"
            )

            result = validate(run_dir, expected_steps=3, max_residual=255)

            self.assertEqual(result["dataloader_steps"], 3)
            self.assertEqual(result["optimizer_updates"], 1)
            self.assertEqual(result["retained_samples"], 896)
            self.assertEqual(result["optimized_samples"], 704)
            self.assertEqual(result["residual_buffer_samples"], 192)

    def test_validate_rejects_residual_at_train_batch_threshold(self):
        with tempfile.TemporaryDirectory() as temporary:
            run_dir = Path(temporary)
            checkpoint = run_dir / "artifacts" / "actor" / "global_step_2"
            checkpoint.mkdir(parents=True)
            (run_dir / "run.log").write_text(
                "\n".join(
                    [
                        "[TRAINING] Step train batch size: 320",
                        "[TRAINING] Buffer size: 320",
                        "[TRAINING] Update train batch size: 320",
                        summary(8, 227, 85),
                        "[TRAINING] Step train batch size: 256",
                        "[TRAINING] Buffer size: 256",
                    ]
                ),
                encoding="utf-8",
            )
            metrics = {
                "condition": "c5_reward_reject_restart",
                "classification": "exploratory_full_seed42_h100",
                "proposals": 308_960,
                "physical_proposals": 308_992,
                "excluded_padding_proposals": 32,
                "expected_registered_proposals": 308_960,
                "theorems_with_rollouts": 9_655,
                "expected_training_theorems": 9_655,
                "archive_sha256": (
                    "fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3"
                ),
                "blocked_correct": 1,
                "blocked_correct_zero_advantage": 0,
                "blocked_correct_reward_rejected": 1,
                "physical_blocked_correct": 1,
                "physical_blocked_correct_zero_advantage": 0,
                "physical_blocked_correct_reward_rejected": 1,
                "actor_checkpoint": str(checkpoint),
                "update_batch_samples": 576,
                "correct": 1,
                "correct_mode_coverage": 1,
            }
            (run_dir / "metrics.json").write_text(
                json.dumps(metrics), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "residual buffer 256 exceeds"):
                validate(run_dir, expected_steps=2, max_residual=255)


if __name__ == "__main__":
    unittest.main()
