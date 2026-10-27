#!/usr/bin/env python3
"""Freeze statement-only dependent-composition tasks; never run a model/train.

The witnesses are authored feasibility checks, not model results. Model-visible
tasks and hidden witnesses are separate artifacts. This is a small synthetic
instrument, not a natural-theorem OOD benchmark. See the dated design note.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PARAMETERS = ((2, 3), (3, 2), (2, 5), (5, 2))
HEADER = "import Mathlib\nimport Aesop\nset_option maxHeartbeats 800000\n\n"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def invariant(fn: str, m: str = "m") -> str:
    z = f"({fn} {m} a b c d)"
    return f"{z}.1*{z}.2.2.2 - {z}.2.1*{z}.2.2.1 = a*d-b*c"


def invariant_proof(fn: str) -> str:
    return f"""  have inv : ∀ (m : Nat) (a b c d : Int),
      {invariant(fn)} := by
    intro m
    induction m with
    | zero => intros; rfl
    | succ m ih =>
      intros
      simp only [{fn}]
      rw [ih]
      ring
"""


def records():
    index = 0
    for target in ("invariant", "nonzero", "bezout"):
        for variant, (k, ell) in enumerate(PARAMETERS):
            name, fn = f"pt_{index:02d}", f"op_{index:02d}"
            # Upper then lower row shear: the second update depends on the first.
            # Reversing the order changes the state, although determinant survives.
            declarations = f"""def {fn} : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => {fn} n (a+{k}*c) (b+{k}*d) (c+{ell}*(a+{k}*c)) (d+{ell}*(b+{k}*d))

"""
            z = f"({fn} n a b c d)"
            if target == "invariant":
                statement = f"theorem {name} (n : Nat) (a b c d : Int) :\n    {invariant(fn, 'n')} := by\n"
                suffix = "  exact inv n a b c d\n"
                graph = ["local_polynomial_identity", "generalized_induction"]
            elif target == "nonzero":
                statement = f"theorem {name} (n : Nat) (a b c d : Int) (h : a*d-b*c ≠ 0) :\n    {z}.1 ≠ 0 ∨ {z}.2.1 ≠ 0 := by\n"
                suffix = """  by_contra hh
  push_neg at hh
  have hi := inv n a b c d
  rw [hh.1, hh.2] at hi
  simp only [zero_mul, sub_self] at hi
  exact h hi.symm
"""
                graph = ["local_polynomial_identity", "generalized_induction", "invariant_to_nonzero"]
            else:
                statement = f"theorem {name} (n : Nat) (a b c d : Int) (h : a*d-b*c = 1) :\n    ∃ u v : Int, u*{z}.1 + v*{z}.2.1 = 1 := by\n"
                suffix = f"""  refine ⟨{z}.2.2.2, -{z}.2.2.1, ?_⟩
  calc
    _ = {z}.1*{z}.2.2.2 - {z}.2.1*{z}.2.2.1 := by ring
    _ = a*d-b*c := inv n a b c d
    _ = 1 := h
"""
                graph = ["local_polynomial_identity", "generalized_induction", "invariant_to_bezout_witness"]
            yield make_record(name, "integer_updates", target, variant, graph,
                              declarations + statement, invariant_proof(fn) + suffix)
            index += 1

    for variant, k in enumerate((2, 3, 5, 7)):
        name, fn = f"pt_{index:02d}", f"op_{index:02d}"
        statement = f"""noncomputable def {fn} : Nat → Real → Real
  | 0, x => x
  | n+1, x => {fn} n (x/(1+{k}*x))

theorem {name} (n : Nat) (x : Real) (hx : 0 ≤ x) :
    {fn} n x = x/(1+{k}*(n:Real)*x) := by
"""
        proof = f"""  induction n generalizing x with
  | zero => simp [{fn}]
  | succ n ih =>
    have hd : 0 < 1+{k}*x := by positivity
    have hy : 0 ≤ x/(1+{k}*x) := div_nonneg hx (le_of_lt hd)
    rw [{fn}, ih _ hy]
    push_cast
    have hn : 0 ≤ (n:Real) := Nat.cast_nonneg n
    have he : 0 < 1+{k}*(n:Real)*(x/(1+{k}*x)) := by positivity
    have hf : 0 < 1+{k}*((n:Real)+1)*x := by positivity
    field_simp [ne_of_gt hd, ne_of_gt he, ne_of_gt hf]
    <;> ring <;> simp
"""
        yield make_record(name, "rational_updates", "closed_form", variant,
                          ["positive_denominator", "invariant_domain", "generalized_induction", "rational_identity"],
                          statement, proof)
        index += 1


def make_record(name, family, target, variant, graph, statement, proof):
    return {
        "task_id": name,
        "family": family,
        "target_schema": target,
        "variant": variant,
        "dependency_graph": graph,
        "theorem_statement": statement,
        "src_context": "",
        "proof_prefix": "",
        "statement_sha256": digest(statement),
        "witness": proof,
        "witness_sha256": digest(proof),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Never overwrite a frozen panel, even with identical text.
    args.output.mkdir(parents=True, exist_ok=False)
    rows = list(records())
    tasks, witnesses, lean = [], [], [HEADER]
    for row in rows:
        tasks.append({k: v for k, v in row.items() if k not in {"witness", "witness_sha256"}})
        witnesses.append({k: row[k] for k in ("task_id", "witness", "witness_sha256", "statement_sha256")})
        lean.append(row["theorem_statement"] + row["witness"] + "\n")
    files = {
        "tasks.jsonl": "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in tasks),
        "witnesses.jsonl": "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in witnesses),
        "witnesses.lean": "".join(lean),
    }
    for name, content in files.items():
        (args.output / name).write_text(content)
    manifest = {
        "status": "frozen-authored-tasks-awaiting-Lean-and-token-audit",
        "training_allowed": False,
        "model_inference_performed": False,
        "task_count": len(rows),
        "independent_domains": 2,
        "target_schemas": 4,
        "variants_per_schema": 4,
        "selection": "fixed hand-authored schemas and parameter tuples, no model-score filtering",
        "source_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "files": {name: digest(content) for name, content in files.items()},
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
