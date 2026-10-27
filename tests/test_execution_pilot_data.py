import importlib.util
import json
from collections import Counter
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/project/prepare_execution_pilot.py"
spec = importlib.util.spec_from_file_location("execution_pilot_data", SCRIPT)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class PrefixBoundaryTests(unittest.TestCase):
    def test_nested_proof_and_comments_are_kept_as_exact_slice(self):
        proof = ("  -- initial comment\n  intro h\n"
                 "  have h' : True := by\n    /- nested /- note -/ comment -/\n    trivial\n"
                 "  simp only [h'] at h\n  exact h\n```")
        choices = pilot.prefix_boundaries(proof)
        self.assertEqual([c[1] for c in choices], [1, 2])
        self.assertEqual(choices[0][0], "  -- initial comment\n  intro h\n")
        self.assertTrue(choices[1][0].endswith("    trivial\n"))
        self.assertEqual(choices[1][2], 2)
        self.assertEqual(choices[1][3], "intro")
        for prefix, *_ in choices:
            self.assertEqual(prefix, proof[:len(prefix)])

    def test_multiline_expression_is_not_cut_at_same_indent(self):
        proof = "  simp only [\n  Nat.add_comm]\n  intro h\n  exact h\n```"
        choices = pilot.prefix_boundaries(proof)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0][0], "  simp only [\n  Nat.add_comm]\n")

    def test_comments_strings_and_unclosed_syntax_do_not_create_steps(self):
        proof = '  trace "sorry [ -- fake"\n  intro h\n  exact h\n```'
        self.assertEqual(len(pilot.prefix_boundaries(proof)), 1)
        for invalid in (
            "  intro h\n  sorry\n  exact h\n```",
            "  intro h\n  admit\n  exact h\n```",
            "  intro h\n  /- unterminated\n  exact h\n```",
            "  simp [foo\n  intro h\n  exact h\n```",
            "  intro h\n  exact h\n```",  # fewer than two suffix steps
        ):
            self.assertEqual(pilot.prefix_boundaries(invalid), [], invalid)

    def test_two_bullets_stay_with_their_constructor(self):
        proof = ("  constructor\n  · intro h\n    exact h\n"
                 "  · intro h\n    exact h\n  skip\n  done\n```")
        choices = pilot.prefix_boundaries(proof)
        self.assertEqual(len(choices), 1)
        self.assertIn("  · intro h\n    exact h\n", choices[0][0])
        self.assertEqual(choices[0][2], 2)

    def test_all_token_budgets_are_applied_to_exact_concatenation(self):
        proof = "  intro h\n  simp [a_long_lemma_name] at h\n  exact h\n```"
        count = len  # deterministic token-count stand-in to test boundaries
        candidates = pilot.eligible_prefixes(proof, "p", count)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["witness_proof"], proof)
        self.assertEqual(candidates[0]["witness_sha256"], pilot.text_hash(proof))
        self.assertEqual(pilot.eligible_prefixes(proof, "p" * 510, count), [])
        self.assertEqual(pilot.eligible_prefixes(proof, "p", count, max_prefix_tokens=2), [])
        self.assertEqual(pilot.eligible_prefixes(proof, "p", count, max_fraction=0.01), [])


class SourceIntegrityTests(unittest.TestCase):
    def make_sources(self, directory):
        rows = {"A": {"theorem_statement": "theorem A := by\n",
                      "informal_statement": "", "src_context": "import Mathlib\n"}}
        records = [dict(theorem_name="A", theorem_statement=rows["A"]["theorem_statement"],
                        informal_statement="", context="import Mathlib\n", proof=str(i),
                        correct=i != 0) for i in range(3)]
        path = Path(directory) / "log.jsonl"
        path.write_text("".join(json.dumps(row) + "\n" for row in records))
        return rows, records, [{"local_path": str(path), "sha256": pilot.sha256(path)}]

    def test_first_group_padding_and_correctness_are_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            rows, records, specs = self.make_sources(directory)
            counts = Counter()
            selected = list(pilot.iter_registered_records(specs, rows, 2, counts))
            self.assertEqual([row[0]["proof"] for row in selected], ["1"])
            self.assertEqual(selected[0][1]["source_line"], 2)
            self.assertEqual(selected[0][1]["source_proposal_index"], 1)
            self.assertEqual(counts, {"raw_proposals": 3, "padding_excluded": 1,
                                      "registered_proposals": 2, "registered_correct": 1})

    def test_corruption_and_nontraining_theorem_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            rows, records, specs = self.make_sources(directory)
            with self.assertRaisesRegex(ValueError, "outside registered training"):
                list(pilot.iter_registered_records(specs, {}, 2, Counter()))
            rows["A"]["theorem_statement"] = "different"
            with self.assertRaisesRegex(ValueError, "metadata mismatch"):
                list(pilot.iter_registered_records(specs, rows, 2, Counter()))
            Path(specs[0]["local_path"]).write_text("changed")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                list(pilot.iter_registered_records(specs, rows, 2, Counter()))


class SelectionTests(unittest.TestCase):
    def test_route_selection_distinct_heads_and_order_independence(self):
        choices = {"A": {prefix: {"initial_tactic_head": head, "proof_prefix": prefix}
                         for prefix, head in (("intro h", "intro"), ("intro j", "intro"),
                                              ("have h", "have"), ("rw h", "rw"))}}
        selected = pilot.choose_routes(choices, 42)
        reversed_choices = {"A": dict(reversed(list(choices["A"].items())))}
        self.assertEqual(selected, pilot.choose_routes(reversed_choices, 42))
        self.assertEqual(len({c["initial_tactic_head"] for c in selected["A"]}), 2)

    def test_stratification_and_shortage_are_deterministic(self):
        routes = {str(i): [{"initial_tactic_head": "intro" if i < 10 else "have"}]
                  for i in range(20)}
        selected = pilot.stratified_selection(routes, 8, 42)
        self.assertEqual(selected, pilot.stratified_selection(dict(reversed(list(routes.items()))), 8, 42))
        self.assertEqual(Counter(routes[name][0]["initial_tactic_head"] for name in selected),
                         {"intro": 4, "have": 4})
        with self.assertRaisesRegex(ValueError, "criteria unchanged"):
            pilot.stratified_selection(routes, 21, 42)

    def test_root_control_matches_mixed_budget_and_mixed_is_half_roots(self):
        bank = []
        for theorem, count in (("A", 2), ("B", 1)):
            bank.append({"theorem_full_name": theorem, "condition": "root", "pilot_row_id": theorem})
            for i in range(count):
                bank.append({"theorem_full_name": theorem, "condition": "prefix",
                             "pilot_row_id": f"{theorem}:{i}", "prefix_sha256": str(i)})
        panels = pilot.make_panels(bank)
        self.assertEqual(len(panels["root"]), len(panels["mixed"]))
        self.assertEqual(len(panels["prefix"]), 3)
        self.assertEqual(Counter(row["condition"] for row in panels["mixed"]), {"root": 3, "prefix": 3})
        for panel in panels.values():
            self.assertEqual(len({row["pilot_row_id"] for row in panel}), len(panel))
        self.assertEqual(Counter(row["theorem_full_name"] for row in panels["root"]),
                         Counter(row["theorem_full_name"] for row in panels["mixed"]))


if __name__ == "__main__":
    unittest.main()
