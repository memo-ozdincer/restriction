#!/usr/bin/env python3
"""Freeze exact model inputs for the synthetic transfer TEST; no inference.

Run with the bundle Python and repository on PYTHONPATH. Witness files are
deliberately never opened. This script cannot overwrite an exported panel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()
    import pandas as pd
    from transformers import AutoTokenizer
    import verl.lean.prompts as prompts

    manifest = json.loads((args.panel / "manifest.json").read_text())
    assert manifest["training_allowed"] is False
    assert sha(args.panel / "tasks.jsonl") == manifest["files"]["tasks.jsonl"]
    paths = [args.panel / name for name in
             ("model_inputs.jsonl", "root_eval.parquet", "materialization.json")]
    if any(path.exists() for path in paths):
        parser.error("refusing to overwrite any materialized test artifact")
    tokenizer = AutoTokenizer.from_pretrained(str(args.model), local_files_only=True)
    rows, inputs, counts = [], [], []
    for index, line in enumerate((args.panel / "tasks.jsonl").read_text().splitlines()):
        task = json.loads(line)
        assert not task["proof_prefix"] and not task["src_context"]
        assert not any("witness" in key for key in task)
        statement = task["theorem_statement"]
        assert hashlib.sha256(statement.encode()).hexdigest() == task["statement_sha256"]
        prompt = prompts.prompt_fn_deepseek(statement, "", task["task_id"], "")
        count = len(tokenizer.encode(prompt, add_special_tokens=False))
        if count > 512:
            raise ValueError(f"prompt overflow: {task['task_id']} ({count})")
        inputs.append({"task_id": task["task_id"], "prompt": prompt,
                       "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()})
        counts.append({"task_id": task["task_id"], "prompt_tokens": count})
        # Match the upstream dataset shape, with an explicit evaluation split.
        # No semantic labels, graph IDs, explanations or proof text enter rows.
        rows.append({
            "data_source": "lean", "prompt": [{"role": "user", "content": ""}],
            "ability": "formal_math", "split": "test", "informal_statement": "",
            "theorem_statement": statement, "theorem_full_name": task["task_id"],
            "src_context": "", "proof_prefix": "", "condition": "root",
            "extra_info": {"index": index}, "pilot_split": "transfer_test",
            "pilot_row_id": task["task_id"] + ":root", "pilot_padding": False,
        })
    assert len(rows) == manifest["task_count"] == 16
    paths[0].write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in inputs))
    pd.DataFrame(rows).to_parquet(paths[1], index=False)
    restored = pd.read_parquet(paths[1])
    assert len(restored) == 16 and restored.theorem_full_name.is_unique
    assert set(restored.split) == {"test"}
    assert set(restored.proof_prefix) == {""}
    assert not any("witness" in col or "graph" in col for col in restored.columns)
    for row, model_input in zip(restored.to_dict("records"), inputs):
        assert prompts.prompt_fn_deepseek(row["theorem_statement"], row["informal_statement"],
                                        row["theorem_full_name"], "") == model_input["prompt"]
    result = {
        "training_allowed": False, "model_inference_performed": False,
        "prompt_limit": 512, "generation_limit": 512, "samples_per_task": 32,
        "proposals_per_policy": 512, "token_counts": counts,
        "model_path": str(args.model.resolve()),
        "prompt_source_sha256": sha(prompts.__file__),
        "materializer_sha256": sha(__file__),
        "files": {p.name: sha(p) for p in paths[:2]},
        "witness_input_audit": "pass: witness files never read; exported rows contain only explicit input fields",
    }
    paths[2].write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
