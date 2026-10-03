import json
from pathlib import Path
import tempfile
import unittest

from scripts.project.evaluate_c5_actorloaded_feasibility import evaluate


class C5ActorLoadedFeasibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        self.run.mkdir()
        self.baseline = self.root / "baseline.log"
        self.write_log(self.baseline, 90)
        self.write_log(self.run / "run.log", 70)
        (self.run / "stop_status.json").write_text(json.dumps({
            "classification": "operational_prefix_only_not_scientific_result",
            "stop_reason": "completed_step_boundary", "last_completed_step": 20,
        }))
        (self.run / "memory.tsv").write_text(
            "timestamp\tmem_available_kib\tgpu_memory_used_mib\trepl_processes\n"
            "2026-10-02T20:00:00-04:00\t314572800\t40000;39000;40000;39000\t64\n"
        )

    @staticmethod
    def write_log(path, verify_seconds, blocked=8, count=20):
        lines = []
        for step in range(1, count + 1):
            lines.append(
                f"step:{step} - num_accepted:320.000 - num_rejected:192.000 "
                f"- num_blocked:{blocked}.000 - num_reward_rejected:8.000 "
                f"- num_trained:320.000 - timing/verify_full_proof:{verify_seconds}.000 "
                "- timing/step:120.000\n"
            )
        path.write_text("".join(lines))

    def test_complete_prefix_passes_integrity_and_runtime_screen(self):
        result = evaluate(self.run, self.baseline)
        self.assertTrue(result["operational_integrity_pass"])
        self.assertTrue(result["throughput_gate_1_19x_and_22h"])
        self.assertEqual(result["last_completed_step"], 20)
        self.assertEqual(result["memory"]["peak_repl_processes"], 64)

    def test_accounting_mismatch_fails_integrity(self):
        self.write_log(self.run / "run.log", 70, blocked=7)
        result = evaluate(self.run, self.baseline)
        self.assertFalse(result["operational_integrity_pass"])
        self.assertIn("step 1 blocked/reward-rejected counts differ", result["errors"])

    def test_short_or_timed_out_prefix_fails_integrity(self):
        self.write_log(self.run / "run.log", 70, count=19)
        status = json.loads((self.run / "stop_status.json").read_text())
        status["stop_reason"] = "time_cap"
        status["last_completed_step"] = 19
        (self.run / "stop_status.json").write_text(json.dumps(status))
        result = evaluate(self.run, self.baseline)
        self.assertFalse(result["operational_integrity_pass"])
        self.assertEqual(result["last_completed_step"], 19)


if __name__ == "__main__":
    unittest.main()
