import json
import unittest

from scripts.project.validate_c5_reward_reject_run import training_accounting


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


if __name__ == "__main__":
    unittest.main()
