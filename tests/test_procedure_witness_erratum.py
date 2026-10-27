"""A witness repair must not change the frozen test or broaden its proof edit."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.project.check_procedure_transfer_witnesses import apply_witness_overrides, digest


class WitnessErratumTests(unittest.TestCase):
    def setUp(self):
        self.tasks = [{"task_id": f"pt_{i:02d}", "statement_sha256": digest(f"statement-{i}")}
                      for i in range(16)]
        self.original = "  field_simp [ne_of_gt hd, ne_of_gt he, ne_of_gt hf]\n"
        self.proofs = [self.original + "\n```\n"] * 16
        self.rows = [{"task_id": self.tasks[i]["task_id"],
                      "statement_sha256": self.tasks[i]["statement_sha256"],
                      "original_witness_sha256": digest(self.original),
                      "witness": self.original.replace("ne_of_gt", "_root_.ne_of_gt"),
                      "witness_sha256": digest(self.original.replace("ne_of_gt", "_root_.ne_of_gt"))}
                     for i in range(12, 16)]

    def apply(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "overlay.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            return apply_witness_overrides(self.tasks, self.proofs, path)

    def test_only_four_witnesses_change_and_original_inputs_survive(self):
        original_tasks, original_proofs = deepcopy(self.tasks), list(self.proofs)
        repaired = self.apply(self.rows)
        self.assertEqual(repaired[:12], self.proofs[:12])
        self.assertTrue(all(proof.count("_root_.ne_of_gt") == 3 for proof in repaired[12:]))
        self.assertEqual(self.tasks, original_tasks)
        self.assertEqual(self.proofs, original_proofs)

    def test_statement_or_original_proof_substitution_rejected(self):
        for key in ("statement_sha256", "original_witness_sha256", "witness_sha256"):
            rows = deepcopy(self.rows)
            rows[0][key] = "0" * 64
            with self.assertRaisesRegex(ValueError, "checksum"):
                self.apply(rows)

    def test_broader_proof_edit_rejected_even_with_valid_checksum(self):
        rows = deepcopy(self.rows)
        rows[0]["witness"] += "  sorry\n"
        rows[0]["witness_sha256"] = digest(rows[0]["witness"])
        with self.assertRaisesRegex(ValueError, "more than"):
            self.apply(rows)

    def test_missing_duplicate_or_wrong_task_rejected(self):
        cases = [self.rows[:-1], self.rows + self.rows[:1],
                 [self.rows[0], self.rows[0], *self.rows[2:]]]
        wrong = deepcopy(self.rows)
        wrong[0]["task_id"] = "pt_00"
        for rows in [*cases, wrong]:
            with self.assertRaisesRegex(ValueError, "exactly"):
                self.apply(rows)


if __name__ == "__main__":
    unittest.main()
