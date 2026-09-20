import unittest
from scripts.project.analyze_base_overlap import summarize


class BaseOverlapTests(unittest.TestCase):
    def test_weighting_can_reverse_direction(self):
        result = summarize({
            "a": {"c1": (1, 1), "c2": (9, 10), "c3": (1, 1)},
            "b": {"c1": (1, 1), "c2": (0, 1), "c3": (1, 10)},
        })
        c2, c3 = (result["conditions"][key] for key in ("c2", "c3"))
        self.assertGreater(c2["pooled_all_solved"], c3["pooled_all_solved"])
        self.assertLess(c2["macro_common"], c3["macro_common"])
        self.assertAlmostEqual(result["paired"]["c3_minus_c2"]["mean_difference"], .1)

    def test_common_panel_excludes_undefined_but_keeps_zero_overlap(self):
        result = summarize({
            "a": {"c1": (0, 0), "c2": (1, 1), "c3": (1, 1)},
            "b": {"c1": (0, 1), "c2": (0, 1), "c3": (0, 1)},
        })
        self.assertEqual(result["common_solved_theorems"], 1)
        self.assertEqual(result["conditions"]["c1"]["excluded_unsolved_theorems"], 1)
        self.assertEqual(result["conditions"]["c2"]["macro_common"], 0)
        self.assertEqual(result["paired"]["c3_minus_c2"]["tied"], 1)

    def test_empty_common_panel_is_not_zero(self):
        result = summarize({"a": {"c1": (0, 0), "c2": (1, 1), "c3": (1, 1)}})
        self.assertIsNone(result["conditions"]["c2"]["macro_common"])
        self.assertIsNone(result["paired"]["c3_minus_c2"]["mean_difference"])
