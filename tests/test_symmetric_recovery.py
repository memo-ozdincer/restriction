import unittest

from scripts.project.analyze_symmetric_recovery import partition_recovery


class SymmetricRecoveryTests(unittest.TestCase):
    def test_partition_and_frequency_floor(self):
        base = {"t": {"a": 4, "b": 4, "c": 4, "d": 4, "e": 1, "f": 8}}
        grpo = {"t": {"f": 1}}
        soft = {"t": {"a": 1, "c": 2}}
        blocking = {"t": {"b": 1, "c": 3}}
        result = partition_recovery(base, grpo, soft, blocking, 4)
        self.assertEqual(result["missing_c1_patterns"], 4)
        for bucket in result["buckets"].values():
            self.assertEqual(bucket["patterns"], 1)
            self.assertEqual(bucket["theorems"], 1)
        self.assertEqual(result["buckets"]["both"]["entries"][0]["pattern"], "c")

    def test_theorem_specific_identity(self):
        base = {"a": {"mode": 4}, "b": {"mode": 4}}
        empty = {"a": {}, "b": {}}
        result = partition_recovery(base, empty, base, empty, 4)
        self.assertEqual(result["buckets"]["c2_only"]["patterns"], 2)

    def test_reject_mismatched_panel(self):
        with self.assertRaises(ValueError):
            partition_recovery({"t": {}}, {}, {}, {}, 1)

    def test_reject_nonpositive_floor(self):
        with self.assertRaises(ValueError):
            partition_recovery({}, {}, {}, {}, 0)
