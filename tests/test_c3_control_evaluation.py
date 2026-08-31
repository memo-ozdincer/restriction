import unittest

from scripts.project.analyze_c3_control_evaluation import mcnemar_exact


class C3ControlEvaluationTests(unittest.TestCase):
    def test_exact_mcnemar_uses_only_discordant_pairs(self):
        result = mcnemar_exact(
            [True, True, False, False, True],
            [True, False, True, False, False],
        )
        self.assertEqual(result["control_only"], 2)
        self.assertEqual(result["c3_only"], 1)
        self.assertEqual(result["exact_p"], 1.0)

    def test_exact_mcnemar_all_agreement(self):
        result = mcnemar_exact([True, False], [True, False])
        self.assertEqual(result, {"control_only": 0, "c3_only": 0, "exact_p": 1.0})


if __name__ == "__main__":
    unittest.main()
