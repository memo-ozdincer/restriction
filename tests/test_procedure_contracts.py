"""Instrument gates plus optional readback of actual local Lean-run evidence."""

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts.project import check_procedure_contracts as checker


class ContractGateTests(unittest.TestCase):
    def test_parser_does_not_recover_binders_from_pretty_printed_goals(self):
        self.assertEqual(checker.parse_records("a b : ℤ\n⊢ a = b\n"), [])
        self.assertEqual(checker.parse_records('info: CONTRACT_JSON:{"kind":"x"}\n'),
                         [{"kind": "x"}])

    def test_partial_success_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            checker.validate_records([])

    def test_existing_run_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileExistsError):
                checker.run_checks(Path(folder), Path("unused"), 1)


@unittest.skipUnless(os.environ.get("PROCEDURE_CONTRACT_RUN"),
                     "set PROCEDURE_CONTRACT_RUN to an actual checker output directory")
class RealLeanEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_dir = Path(os.environ["PROCEDURE_CONTRACT_RUN"])
        cls.report = json.loads((cls.run_dir / "report.json").read_text())
        cls.records = checker.parse_records((cls.run_dir / "AtomicShear.stdout.log").read_text())

    def test_actual_compilation_and_negative_results(self):
        self.assertTrue(self.report["complete"])
        config = json.loads((self.run_dir / "config.json").read_text())
        for filename, digest in config["fixture_hashes"].items():
            self.assertEqual(checker.sha256(checker.FIXTURES / filename), digest)
        cases = {r["case"]: r for r in self.report["cases"]}
        self.assertEqual(set(cases), set(checker.CASES))
        self.assertEqual(cases["AtomicShear"]["exit_code"], 0)
        self.assertEqual(checker.sha256(self.run_dir / "AtomicShear.olean"),
                         cases["AtomicShear"]["olean_sha256"])
        for name, expected in checker.CASES.items():
            case = cases[name]
            self.assertFalse(case["timed_out"])
            self.assertEqual(checker.sha256(self.run_dir / f"{name}.lean"), case["source_sha256"])
            if expected:
                self.assertNotEqual(case["exit_code"], 0)
                self.assertIn(expected, (self.run_dir / f"{name}.stdout.log").read_text())

    def test_actual_alpha_invariance_type_value_changes_and_premise_use(self):
        checked = checker.validate_records(deepcopy(self.records))
        certificates = checked["certificates"]
        self.assertEqual(certificates["atomic_shear"]["alpha_interface_sha256"],
                         certificates["atomic_shear_renamed"]["alpha_interface_sha256"])
        self.assertNotEqual(certificates["atomic_shear"]["alpha_interface_sha256"],
                            certificates["atomic_shear_rational"]["alpha_interface_sha256"])
        self.assertNotEqual(certificates["atomic_shear_value_one"]["alpha_interface_sha256"],
                            certificates["atomic_shear_value_two"]["alpha_interface_sha256"])

    def test_untrusted_axiom_record_is_fail_closed(self):
        tampered = deepcopy(self.records)
        next(r for r in tampered if r["kind"] == "closed_certificate")["axioms"].append("sorryAx")
        with self.assertRaisesRegex(ValueError, "untrusted axiom"):
            checker.validate_records(tampered)

    def test_missing_premise_use_record_is_fail_closed(self):
        tampered = deepcopy(self.records)
        adapter = next(r for r in tampered if r.get("name") == "shear_adapter")
        adapter["proof_binder_usage"][6]["used_in_body"] = False
        with self.assertRaisesRegex(ValueError, "both recorded input facts"):
            checker.validate_records(tampered)


if __name__ == "__main__":
    unittest.main()
