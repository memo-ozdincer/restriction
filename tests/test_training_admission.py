import unittest
from collections import Counter

from scripts.project.analyze_training_admission import classify, summarize
from verl.lean.mode_archive import ModeArchive


class TrainingAdmissionTests(unittest.TestCase):
    def test_all_possible_count_pairs_obey_admission_identities(self):
        for correct in range(33):
            for blocked in range(correct + 1):
                row = classify(correct, blocked)
                self.assertEqual(row["reward_reject_admitted"] and not row["zero_advantage_admitted"],
                                 correct == 32 and 0 < blocked < 32)
                self.assertEqual(row["soft_admitted"] and not row["reward_reject_admitted"],
                                 0 < correct < 32 and blocked == correct)
                self.assertFalse(row["zero_advantage_admitted"] and not row["reward_reject_admitted"])

    def test_invalid_counts_rejected(self):
        for correct, blocked in ((-1, 0), (33, 0), (2, 3), (2, -1), (2.0, 1), (True, 0)):
            with self.subTest(correct=correct, blocked=blocked):
                with self.assertRaises(ValueError):
                    classify(correct, blocked)

    def test_summary_separates_archive_eligibility_and_admission(self):
        archive = ModeArchive({"x": {"a": 3, "b": 1}, "z": {"a": 4}})
        data = {
            "x": {"correct": 32, "blocked": 20, "modes": Counter(a=20, b=12), "step": 1},
            "y": {"correct": 32, "blocked": 0, "modes": Counter(a=32), "step": 1},
            "z": {"correct": 2, "blocked": 2, "modes": Counter(a=2), "step": 1},
        }
        result = summarize(data, archive, check_blocked=True)
        self.assertEqual(result["panels"]["archive_eligible"]["groups"], 2)
        self.assertEqual(result["panels"]["all"]["admission"],
                         {"soft_admitted": 1, "zero_advantage_admitted": 0, "reward_reject_admitted": 1})
        self.assertEqual(result["newly_admitted_vs_zero_advantage"][0]["theorem"], "x")
        self.assertEqual(result["lost_vs_soft"], ["z"])

    def test_telemetry_or_mode_count_mismatch_rejected(self):
        archive = ModeArchive({"x": {"a": 4}})
        row = {"correct": 2, "blocked": 0, "modes": Counter(a=2), "step": 1}
        with self.assertRaisesRegex(ValueError, "telemetry"):
            summarize({"x": row}, archive, check_blocked=True)
        with self.assertRaisesRegex(ValueError, "mode/correct"):
            summarize({"x": {**row, "correct": 3}}, archive)


if __name__ == "__main__":
    unittest.main()
