import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EvaluationLauncherTests(unittest.TestCase):
    def test_sample_only_evaluation_resolves_grpo_worker_path(self):
        launcher = (ROOT / "scripts/project/launch_lean_evaluation.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("+trainer.sample_only=True", launcher)
        self.assertEqual(launcher.count("algorithm.adv_estimator=grpo"), 1)


if __name__ == "__main__":
    unittest.main()
