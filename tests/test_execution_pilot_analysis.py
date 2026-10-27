"""Scientific accounting checks for the continuation availability gate."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.project.analyze_execution_pilot import (
    analyze, conditioning_id, load_manifest, screen_samples, sha256,
    summarize, text_hash, validate_bank,
)


def bank_rows(train_count=48, diagnostic_count=1, two_prefixes=False):
    rows = []
    heads = ["intro", "have", "apply", "rw"]
    for split, count in (("train", train_count), ("diagnostic", diagnostic_count)):
        for i in range(count):
            name = f"{split}_{i}"
            statement = f"theorem {name} : True := by\n"
            shared = dict(theorem_full_name=name, theorem_statement=statement,
                          informal_statement="", src_context="import Mathlib\n", pilot_split=split)
            for j in range(3 if two_prefixes else 2):
                head = "root" if j == 0 else heads[(i + j - 1) % 4]
                prefix = "" if j == 0 else f"  {head} h\n"
                witness = prefix + "  exact True.intro\n```"
                rows.append(dict(
                    **shared, pilot_row_id=f"{name}:{j}", condition="prefix" if prefix else "root",
                    proof_prefix=prefix, prefix_sha256=text_hash(prefix),
                    conditioning_id=conditioning_id(statement, shared["src_context"], prefix),
                    prefix_token_count=3 if prefix else 0, prompt_token_count=20 if prefix else 17,
                    initial_tactic_head=head, witness_proof=witness, witness_sha256=text_hash(witness),
                ))
    return rows


def records_for(bank, successes=4, diagnostic_successes=32):
    records = []
    for row in bank:
        n = screen_samples(row)
        correct_count = diagnostic_successes if row["pilot_split"] == "diagnostic" else successes
        for candidate in range(n):
            suffix = "  exact True.intro\n```" if candidate < correct_count else "  broken\n```"
            proof = row["proof_prefix"] + suffix
            record = dict(
                pilot_row_id=row["pilot_row_id"], pilot_split=row["pilot_split"], pilot_padding=False,
                theorem_name=row["theorem_full_name"], theorem_statement=row["theorem_statement"],
                context=row["src_context"], proof=proof, proof_hash=text_hash(proof),
                proposal_id=f"{row['pilot_row_id']}:{candidate}", candidate_index=candidate,
                batch_id="batch", theorem_index_in_batch=0, token_count=5,
                correct=candidate < correct_count, verdict=candidate < correct_count,
                lean_complete=candidate < correct_count, timed_out=False, verifier_error=None,
                parse_time=0.1, queue_wait_time=0.2, verification_time=0.3,
                failure_class=None if candidate < correct_count else "lean_error",
            )
            if row["proof_prefix"]:
                record.update(proof_prefix=row["proof_prefix"], proof_prefix_sha256=row["prefix_sha256"],
                              generated_suffix=suffix, conditioning_id=row["conditioning_id"],
                              prompt_token_count=row["prompt_token_count"])
            records.append(record)
    return records


def minimal_manifest(bank):
    ids = {split: sorted({row["theorem_full_name"] for row in bank if row["pilot_split"] == split})
           for split in ("train", "diagnostic")}
    return dict(
        schema_version=1, model_revision="fixture", files={},
        selection={"train_theorem_ids": ids["train"], "diagnostic_theorem_ids": ids["diagnostic"],
                   "train_theorems": len(ids["train"]), "diagnostic_theorems": len(ids["diagnostic"])},
        tasks=[dict(pilot_row_id=row["pilot_row_id"], conditioning_id=row["conditioning_id"],
                    screen_samples=screen_samples(row)) for row in bank],
    )


class ExecutionPilotAnalysisTests(unittest.TestCase):
    def test_gate_boundary_and_diagnostics_never_change_selection(self):
        for count, advance in ((47, False), (48, True)):
            bank = bank_rows(count)
            by_id = validate_bank(bank, minimal_manifest(bank))
            with self.subTest(count=count):
                result = summarize(by_id, records_for(bank))
                self.assertEqual(result["gate"]["advance"], advance)
                self.assertEqual(len(result["gate"]["qualifying_heads"]), 4)
                changed = summarize(by_id, records_for(bank, diagnostic_successes=0))
                self.assertEqual(result["gate"], changed["gate"])
                self.assertNotEqual(result["panels"]["diagnostic_root"], changed["panels"]["diagnostic_root"])

    def test_gate_inclusive_success_boundary_and_first_head_requirement(self):
        bank = bank_rows()
        for successes, advance in ((0, False), (1, True), (8, True), (9, False), (16, False)):
            with self.subTest(successes=successes):
                result = summarize({r["pilot_row_id"]: r for r in bank}, records_for(bank, successes))
                self.assertEqual(result["gate"]["advance"], advance)
        for row in bank:
            if row["condition"] == "prefix":
                row["initial_tactic_head"] = "intro"
        result = summarize({r["pilot_row_id"]: r for r in bank}, records_for(bank))
        self.assertEqual(len(result["gate"]["eligible_theorems"]), 48)
        self.assertFalse(result["gate"]["advance"])

    def test_multiple_prefixes_do_not_double_count_theorem_identities(self):
        bank = bank_rows(24, two_prefixes=True)
        result = summarize({r["pilot_row_id"]: r for r in bank}, records_for(bank))
        self.assertEqual(len(result["gate"]["eligible_prefix_rows"]), 48)
        self.assertEqual(len(result["gate"]["eligible_theorems"]), 24)
        self.assertFalse(result["gate"]["advance"])

    def test_root_missing_prefix_fields_is_distinct_from_conditional_task(self):
        bank = bank_rows(1)
        records = records_for(bank)
        result = summarize({r["pilot_row_id"]: r for r in bank}, records)
        self.assertEqual(result["registered"]["proposals"], 16 + 32 + 32)
        self.assertEqual(result["panels"]["diagnostic_root"]["proposals"], 32)
        self.assertEqual(result["panels"]["diagnostic_prefix"]["proposals"], 32)
        self.assertEqual(result["physical"]["generated_tokens"], 80 * 5)
        self.assertEqual(result["physical"]["supplied_prefix_tokens"], 48 * 3)

    def test_theorem_balancing_prevents_two_prefix_theorems_double_weight(self):
        bank = bank_rows(1, 2, two_prefixes=True)
        bank = [r for r in bank if r["pilot_row_id"] != "diagnostic_1:2"]
        records = records_for(bank)
        for record in records:
            if record["theorem_name"] == "diagnostic_0":
                record.update(correct=False, verdict=False, lean_complete=False)
        result = summarize({r["pilot_row_id"]: r for r in bank}, records)
        self.assertEqual(result["panels"]["diagnostic_prefix"]["theorem_balanced_correctness"], 0.5)

    def test_missing_extra_duplicate_and_nonboolean_records_rejected(self):
        bank = bank_rows(1)
        records = records_for(bank)
        by_id = {r["pilot_row_id"]: r for r in bank}
        bad_cases = [records[:-1], records + [deepcopy(records[0])]]
        extra = deepcopy(records[0])
        extra["proposal_id"] = "unmarked-extra"
        bad_cases.append(records + [extra])
        for key, value in (("correct", 1), ("pilot_padding", None), ("proof_prefix", "wrong"),
                           ("generated_suffix", "wrong"), ("candidate_index", 16),
                           ("verdict", True), ("verification_time", float("nan"))):
            changed = deepcopy(records)
            changed[4][key] = value
            bad_cases.append(changed)
        for i, changed in enumerate(bad_cases):
            with self.subTest(case=i), self.assertRaises(ValueError):
                summarize(by_id, changed)

    def test_only_explicit_complete_bounded_padding_is_excluded_and_charged(self):
        bank = bank_rows(1)
        records = records_for(bank)
        by_id = {r["pilot_row_id"]: r for r in bank}
        original = summarize(by_id, records)
        padding = []
        for index in range(4):
            for record in records[:16]:
                copy = deepcopy(record)
                copy.update(pilot_padding=True, theorem_index_in_batch=index,
                            proposal_id=f"padding-{index}-{copy['candidate_index']}")
                padding.append(copy)
        padded = summarize(by_id, records + padding[:48])
        self.assertEqual(original["gate"], padded["gate"])
        self.assertEqual(original["registered"], padded["registered"])
        self.assertEqual(padded["explicit_padding"]["proposals"], 48)
        self.assertEqual(padded["physical"]["generated_tokens"], original["physical"]["generated_tokens"] + 240)
        for bad in (padding[:47], padding):
            with self.assertRaises(ValueError):
                summarize(by_id, records + bad)

    def test_bank_rejects_leakage_and_manifest_task_count_drift(self):
        bank = bank_rows(1)
        manifest = minimal_manifest(bank)
        validate_bank(bank, manifest)
        changed = deepcopy(manifest)
        changed["tasks"][1]["screen_samples"] = 32
        with self.assertRaisesRegex(ValueError, "screen sample"):
            validate_bank(bank, changed)
        changed_bank = deepcopy(bank)
        changed_bank[-1]["pilot_split"] = "train"
        with self.assertRaisesRegex(ValueError, "leakage"):
            validate_bank(changed_bank, manifest)

    def write_fixture(self, directory):
        bank = bank_rows(1)
        source = directory / "source.jsonl"
        witnesses = []
        for row in bank:
            if row["condition"] == "prefix":
                witnesses.append(dict(theorem_name=row["theorem_full_name"],
                                      theorem_statement=row["theorem_statement"],
                                      informal_statement=row["informal_statement"], context=row["src_context"],
                                      proof=row["witness_proof"], correct=True))
                row.update(source_log=str(source), source_line=len(witnesses))
        source.write_text("".join(json.dumps(r) + "\n" for r in witnesses))
        for row in bank:
            if row["condition"] == "prefix":
                row["source_log_sha256"] = sha256(source)
        bank_path = directory / "selection_bank.jsonl"
        bank_path.write_text("".join(json.dumps(r) + "\n" for r in bank))
        manifest = minimal_manifest(bank)
        manifest["files"] = {bank_path.name: sha256(bank_path)}
        manifest["source_logs"] = [{"path": str(source), "local_path": str(source), "sha256": sha256(source)}]
        for key in ("source_dataset", "c0_validation"):
            path = directory / (key + ".json")
            path.write_text('{}\n')
            manifest[key] = dict(path=str(path), sha256=sha256(path))
        path = directory / "manifest.json"
        path.write_text(json.dumps(manifest))
        records = records_for(bank)
        logs = []
        for split in ("train", "diagnostic"):
            log = directory / f"{split}.jsonl"
            log.write_text("".join(json.dumps(r) + "\n" for r in records if r["pilot_split"] == split))
            logs.append(log)
        return path, logs

    def test_full_file_analysis_authenticates_sources_and_source_witnesses(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            path, logs = self.write_fixture(directory)
            result = analyze(path, *logs)
            self.assertEqual(result["registered"]["proposals"], 80)
            self.assertEqual(result["provenance"]["manifest_sha256"], sha256(path))
            source = directory / "source.jsonl"
            source.write_text(source.read_text().replace('"correct": true', '"correct": false'))
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_manifest(path)

    def test_self_consistent_rehashed_bank_still_cannot_fabricate_witness(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            path, _ = self.write_fixture(directory)
            manifest = json.loads(path.read_text())
            bank_path = directory / "selection_bank.jsonl"
            bank = [json.loads(line) for line in bank_path.read_text().splitlines()]
            bank[1]["witness_proof"] += "\n-- fabricated"
            bank[1]["witness_sha256"] = text_hash(bank[1]["witness_proof"])
            bank_path.write_text("".join(json.dumps(row) + "\n" for row in bank))
            manifest["files"][bank_path.name] = sha256(bank_path)
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "witness source mismatch"):
                load_manifest(path)


if __name__ == "__main__":
    unittest.main()
