import argparse
import json
from pathlib import Path
import tempfile
import unittest

from scripts.project import interface_discovery_pilot as pilot


class InterfaceDiscoveryTests(unittest.TestCase):
    def test_producers_do_not_receive_targets_or_oracle(self):
        for w in pilot.worlds():
            self.assertNotIn(w["oracle"], w["producer_prompt"])
            for target in w["targets"]:
                self.assertNotIn(target["statement"], w["producer_prompt"])
                self.assertNotIn(target["oracle_suffix"], w["producer_prompt"])
            self.assertTrue(w["producer_prompt"].endswith("theorem reusable_fact (n : Nat) :\n"))

    def test_single_theorem_gate_rejects_admissions_and_declarations(self):
        for body in ["True := by sorry\n```", "True := by trivial\naxiom bad : False\n```",
                     "True := by run_tac pure ()\n```", "True := by trivial\n```extra"]:
            self.assertIsNone(pilot.completion_code(body, True)[0])
        self.assertIsNotNone(pilot.completion_code("n = n := by\n  rfl\n```", True)[0])
        self.assertIsNone(pilot.completion_code("n = n := by rfl", True)[0])

    def test_local_bindings_are_not_extra_theorem_declarations(self):
        self.assertIsNotNone(pilot.completion_code(
            "let s := orbit n; s = s := by rfl\n```", True)[0])
        self.assertIsNotNone(pilot.completion_code(
            "n = n := by\n  have h : n = n := by rfl\n  exact h\n```", True)[0])

    def test_selection_uses_validity_and_index_not_target_scores(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            for label in ("base", "grpo"):
                rs = [{"id": f"{label}/{i}", "sample_index": i, "world": "quadratic2",
                       "text": "n = n := by rfl\n```", "downstream_score": i} for i in reversed(range(7))]
                vs = [{"id": r["id"], "accepted": r["sample_index"] != 0, "code_sha256": "fixture"} for r in rs]
                (run / f"{label}-producer.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rs))
                (run / f"{label}-producer-verified.jsonl").write_text("".join(json.dumps(r)+"\n" for r in vs))
            output = run / "selected.json"
            pilot.select(argparse.Namespace(run=run, output=output))
            selected = json.loads(output.read_text())
            self.assertEqual([r["proposal_id"] for r in selected],
                             [f"{label}/{i}" for label in ("base", "grpo") for i in range(1,5)])

    def test_preregistered_counts_and_empty_bare_helpers(self):
        with tempfile.TemporaryDirectory() as directory:
            panel = Path(directory) / "panel"
            pilot.prepare(panel)
            bare = pilot.generation_requests(argparse.Namespace(panel=panel, phase="bare", artifacts=None))
            self.assertEqual(sum(r["samples"] for r in bare), 512)
            self.assertLessEqual(max(r["samples"] for r in bare), pilot.MAX_CONCURRENT_SEQUENCES)
            self.assertTrue(all("reusable_fact" not in r["prompt"] for r in bare))
            producer = pilot.generation_requests(argparse.Namespace(panel=panel, phase="producer"))
            self.assertEqual(sum(r["samples"] for r in producer), 32)
            with self.assertRaises(FileExistsError): pilot.prepare(panel)


if __name__ == "__main__":
    unittest.main()
