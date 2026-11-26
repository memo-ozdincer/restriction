#!/usr/bin/env python3
"""Descriptive matched-statement screen; stream authenticated archive, no new verification."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile


def goal(statement):
    """Conservative lexical scan for colon outside parameter delimiters."""
    depth = 0
    for i, ch in enumerate(statement):
        if ch in "([{⦃":
            depth += 1
        elif ch in ")]}⦄":
            depth -= 1
        elif ch == ":" and depth == 0 and statement[i:i+2] != ":=":
            return statement[i+1:].split(":=", 1)[0].strip()
    return ""


def category(statement):
    g = goal(statement)
    if not g:
        return "unclassified"
    if g.startswith(("∃", "Exists ")):
        return "explicit_existential"
    if "∃" in g or "Exists " in g:
        return "nested_existential"
    return "other_statement"


def form(proof):
    lines = [l.strip() for l in proof.splitlines()
             if l.strip() and not l.strip().startswith(("--", "```"))]
    if not lines:
        return "empty"
    if any(re.match(r"(use|existsi)\b|(?:exact|refine'?)\s*[⟨]", l) for l in lines):
        return "explicit_candidate_syntax"
    return "other_syntax"


def run(archive, inventory):
    manifest = {r["archive_path"]: r["sha256"] for r in inventory
                if "/eval128-" in r["archive_path"] and "/artifacts/proofs/" in r["archive_path"]}
    assert len(manifest) == 4
    banks = {}
    process = subprocess.Popen(["zstd", "-dc", str(archive)], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=process.stdout, mode="r|") as tar:
        for m in tar:
            if m.name not in manifest:
                continue
            condition = Path(m.name).parts[-4].split("-")[1]
            h = hashlib.sha256()
            seen = collections.Counter()
            rows = {}
            totals = collections.Counter()
            with tar.extractfile(m) as f:
                for raw in f:
                    h.update(raw)
                    r = json.loads(raw)
                    name = r["theorem_name"]
                    seen[name] += 1
                    if seen[name] > 128:
                        continue
                    s = r["theorem_statement"]
                    root = rows.setdefault(name, {"statement": s, "context": r["context"], "category": category(s), "counts": collections.Counter(), "examples": {}})
                    assert (s, r["context"]) == (root["statement"], root["context"])
                    outcome = "accepted" if r["correct"] else "rejected" if r["failure_class"] == "lean_rejected" else "unresolved"
                    tag = outcome + "/" + form(r["proof"])
                    root["counts"][tag] += 1
                    if root["category"] != "other_statement" or name == "numbertheory_notequiv2i2jasqbsqdiv8":
                        root.setdefault("attempts", []).append({"proposal_id": r["proposal_id"], "proof": r["proof"], "outcome": outcome})
                    examples = root["examples"].setdefault(tag, [])
                    if len(examples) < 2 and all(x["proof"] != r["proof"] for x in examples):
                        examples.append({"proposal_id": r["proposal_id"], "proof": r["proof"], "failure_class": r["failure_class"]})
                    totals[outcome] += 1
            assert h.hexdigest() == manifest[m.name]
            assert len(seen) == 467 and sum(seen.values()) == 59904 and sum(totals.values()) == 59776
            banks[condition] = {"member": m.name, "sha256": h.hexdigest(), "roots": rows, "totals": totals}
            print(condition, totals, flush=True)
    assert process.wait() == 0 and set(banks) == {"c0", "c1", "c2", "c3"}
    identity = {n: (r["statement"], r["context"]) for n, r in banks["c0"]["roots"].items()}
    for bank in banks.values():
        assert {n: (r["statement"], r["context"]) for n, r in bank["roots"].items()} == identity
    return banks


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    inv = json.loads(Path("research/recovery/2026-11-18/evidence-inventory.json").read_text())["files"]
    with args.output.open("x") as f:
        json.dump(run(args.archive, inv), f, ensure_ascii=False)
