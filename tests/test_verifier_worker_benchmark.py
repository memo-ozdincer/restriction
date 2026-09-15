import unittest
from scripts.project.benchmark_verifier_workers import compare


class WorkerBenchmarkTests(unittest.TestCase):
    def test_separates_verdict_and_failure_class_changes(self):
        a = [{'verdict': True, 'failure_class': None}, {'verdict': False, 'failure_class': 'timeout'}]
        b = [{'verdict': False, 'failure_class': 'timeout'}, {'verdict': False, 'failure_class': 'lean_rejected'}]
        self.assertEqual(compare(a, b), {'verdict_disagreements': 1, 'failure_class_disagreements': 2})

    def test_rejects_unaligned_results(self):
        with self.assertRaises(ValueError):
            compare([], [{'verdict': True, 'failure_class': None}])
