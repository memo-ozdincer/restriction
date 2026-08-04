from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class ConsolidateC0Tests(unittest.TestCase):
    def test_disjoint_snapshots_and_padding_are_accounted_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / "dataset.parquet"
            pd.DataFrame({
                "theorem_full_name": ["A", "B", "held_out"],
                "split": ["train", "train", "valid"],
            }).to_parquet(dataset, index=False)
            dataset_hash = hashlib.sha256(dataset.read_bytes()).hexdigest()

            first = root / "first.jsonl"
            second = root / "second.jsonl"
            first.write_text("".join(json.dumps(record) + "\n" for record in [
                {"theorem_name": "A", "proof": "  simp\n```", "correct": True},
                {"theorem_name": "A", "proof": "  exact h\n```", "correct": False},
            ]), encoding="utf-8")
            second.write_text("".join(json.dumps(record) + "\n" for record in [
                {"theorem_name": "B", "proof": "  ring\n```", "correct": True},
                {"theorem_name": "B", "proof": "  nlinarith\n```", "correct": True},
                # One complete padding group. These records count as physical
                # compute but must not affect the registered C0 sample.
                {"theorem_name": "B", "proof": "  aesop\n```", "correct": True},
                {"theorem_name": "B", "proof": "  omega\n```", "correct": False},
            ]), encoding="utf-8")
            output = root / "complete"
            subprocess.run([
                sys.executable, str(ROOT / "scripts/project/consolidate_c0.py"),
                "--proofs", str(first), "--proofs", str(second),
                "--dataset", str(dataset), "--dataset-sha256", dataset_hash,
                "--output-dir", str(output), "--model-revision", "revision",
                "--seed", "42", "--samples-per-theorem", "2",
                "--expected-padding-proposals", "2",
            ], cwd=ROOT, check=True, capture_output=True, text=True)

            metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
            validation = json.loads((output / "validation.json").read_text(encoding="utf-8"))
            archive = json.loads((output / "mode_archive.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["raw_proposals"], 6)
            self.assertEqual(metrics["proposals"], 4)
            self.assertEqual(metrics["raw_correct"], 4)
            self.assertEqual(metrics["correct"], 3)
            self.assertEqual(validation["padding_proposals_excluded_from_scientific_sample"], 2)
            self.assertEqual(sum(sum(modes.values()) for modes in archive["counts"].values()), 3)


if __name__ == "__main__":
    unittest.main()
