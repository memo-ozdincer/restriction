#!/usr/bin/env python3
"""Small, target-blind lemma discovery and frozen-consumer crossover.

Separate preparation, CPU verification and GPU generation processes. No training.
See research/INTERFACE_DISCOVERY_PILOT_2026-11-18.md for prospective claims/costs.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HEADER = "import Mathlib\nimport Aesop\n\nset_option maxHeartbeats 0\n\nopen BigOperators Real Nat Topology Rat\n\n"
PREFIX = "Complete the following Lean 4 code:\n\n```lean4\n"
SEED = 20261118
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
# This is an explicitly limited single-theorem instrument, not a Lean sandbox.
FORBIDDEN = re.compile(r"\b(?:sorry|admit|axiom|constant|opaque|unsafe|run_tac|run_cmd|elab|macro|syntax|import|namespace|section|end|theorem|lemma|example|def|abbrev|instance|attribute|set_option|initialize|native_decide)\b|#")


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def worlds():
    result = []
    for label, d, a, b in [("quadratic2", 2, 3, 2), ("quadratic3", 3, 2, 1)]:
        name = "orbit"
        definition = f"""def {name} : Nat → Int × Int
  | 0 => (1, 0)
  | n+1 => let s := {name} n; ({a}*s.1 + {d*b}*s.2, {b}*s.1 + {a}*s.2)

"""
        oracle = f"""theorem reusable_fact (n : Nat) :
    (orbit n).1 ^ 2 - {d} * (orbit n).2 ^ 2 = 1 := by
  induction n with
  | zero => norm_num [orbit]
  | succ n ih =>
    change ({a}*(orbit n).1 + {d*b}*(orbit n).2)^2 -
      {d}*({b}*(orbit n).1 + {a}*(orbit n).2)^2 = 1
    nlinarith [ih]

"""
        targets = [
            {"id": label + "_nonzero", "statement": "theorem target (n : Nat) : (orbit n).1 ≠ 0 := by\n",
             "oracle_suffix": "  have h := reusable_fact n\n  intro hz\n  rw [hz] at h\n  nlinarith [sq_nonneg ((orbit n).2)]\n"},
            {"id": label + "_bezout", "statement": "theorem target (n : Nat) : ∃ u v : Int, u*(orbit n).1 + v*(orbit n).2 = 1 := by\n",
             "oracle_suffix": f"  refine ⟨(orbit n).1, -{d}*(orbit n).2, ?_⟩\n  nlinarith [reusable_fact n]\n"},
        ]
        # No target statement, authored invariant, or witness enters this prompt.
        producer = PREFIX + HEADER + definition + (
            "/-- Discover and prove a useful algebraic equality about this state "
            "after an arbitrary number of iterations. State the equality yourself. "
            "Prefer an informative relation to a tautology. -/\n"
            "theorem reusable_fact (n : Nat) :\n")
        result.append({"id": label, "definition": definition, "producer_prompt": producer,
                       "oracle": oracle, "targets": targets})
    return result


def prepare(output):
    output.mkdir(parents=True, exist_ok=False)
    ws = worlds()
    write(output / "worlds.json", ws)
    # Keep model-visible producer inputs separate from target/witness records.
    write(output / "producer_inputs.json", [{"id": w["id"], "prompt": w["producer_prompt"]} for w in ws])
    for w in ws:
        for t in w["targets"]:
            (output / (t["id"] + ".lean")).write_text(HEADER + w["definition"] + w["oracle"] + t["statement"] + t["oracle_suffix"])
    write(output / "manifest.json", {"seed": SEED, "training": False,
        "source_sha256": sha(Path(__file__).read_bytes()),
        "files": {p.name: sha(p.read_bytes()) for p in sorted(output.iterdir())},
        "producer_samples_per_world_and_model": 16, "selected_artifacts_per_world_and_producer": 4,
        "selection": "first four kernel-valid by sample index; no target-outcome selection",
        "bare_samples_per_target_and_consumer": 128, "artifact_samples_per_target_and_consumer": 16,
        "oracle_and_irrelevant_samples_per_target_and_consumer": 32,
        "maximum_model_proposals": 2624, "consumer_max_tokens": 512, "producer_max_tokens": 768,
        "max_prompt_tokens": 1536, "temperature": 1.0, "top_p": 1.0,
        "verifier_timeout_seconds": 60, "verifier_workers": 8,
        "scope": "Two related synthetic recurrences; inference discovery feasibility, not trained generalization or novel mathematics."})


def completion_code(text, producer=False):
    if "```" not in text:
        return None, "missing_closing_fence"
    body, after = text.split("```", 1)
    if after.strip() or FORBIDDEN.search(body):
        return None, "unsupported_or_extra_code"
    # Local `let`/`have` bindings legitimately contain additional `:=` tokens.
    # Extra top-level declarations are rejected by FORBIDDEN, then Lean and
    # the axiom audit check the actual closed theorem.
    if producer and not re.search(r":=\s*by\b", body):
        return None, "expected_tactic_proof"
    return body, None


def verify_one(job):
    # Identical upstream Lean completeness predicate; explicit paths and a
    # prospectively shorter timeout. No correctness-source modifications.
    sys.path.insert(0, job["verifier"])
    from prover.lean.verifier import verify_lean4_file
    result = verify_lean4_file(job["code"], lake_path=job["lake"],
        lean_workspace=str(Path(job["verifier"]) / "mathlib4"), timeout=60)
    infos = [x.get("data", "") for x in result.get("infos", [])]
    axioms = set()
    found = False
    for info in infos:
        if "depends on axioms:" in info:
            match = re.search(r"depends on axioms:\s*\[([^]]*)\]", info)
            if match:
                found = True
                axioms.update(x.strip() for x in match[1].split(",") if x.strip())
        elif "does not depend on any axioms" in info:
            found = True
    accepted = bool(result.get("complete")) and found and axioms <= ALLOWED_AXIOMS
    return {"id": job["id"], "accepted": accepted, "lean_complete": result.get("complete", False),
            "axiom_audit_found": found, "axioms": sorted(axioms),
            "errors": result.get("errors", []), "system_errors": result.get("system_errors"),
            "seconds": result.get("verify_time"), "code_sha256": sha(job["code"])}


def verify_jobs(jobs, output, workers=8):
    results = []
    with output.open("x", buffering=1) as stream:
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn")) as pool:
            for result in pool.map(verify_one, jobs, chunksize=1):
                results.append(result)
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
    return results


def verify_generated(args):
    generated = rows(args.input)
    jobs, rejected = [], []
    for r in generated:
        body, error = completion_code(r["text"], r["kind"] == "producer")
        if error:
            rejected.append({"id": r["id"], "accepted": False, "parse_error": error})
            continue
        # Model prefix excludes the formatting instruction/fence, not definitions.
        code = r["prompt"].removeprefix(PREFIX) + body
        theorem = "reusable_fact" if r["kind"] == "producer" else "target"
        code += "\n#print axioms " + theorem + "\n"
        jobs.append({"id": r["id"], "code": code, "verifier": str(args.verifier), "lake": str(args.lake)})
    results = verify_jobs(jobs, args.output)
    with args.output.open("a") as f:
        for result in rejected:
            f.write(json.dumps(result) + "\n")
    write(args.output.with_suffix(".summary.json"), {"proposals": len(generated),
        "physical_lean_calls": len(jobs), "parse_rejections": len(rejected),
        "accepted": sum(r["accepted"] for r in results)})


def validate_panel(args):
    ws = json.loads((args.panel / "worlds.json").read_text())
    jobs = []
    for w in ws:
        for t in w["targets"]:
            jobs.append({"id": t["id"], "code": HEADER + w["definition"] + w["oracle"] +
                t["statement"] + t["oracle_suffix"] + "\n#print axioms target\n"})
        jobs.append({"id": w["id"] + "_oracle", "code": HEADER + w["definition"] +
            w["oracle"] + "\n#print axioms reusable_fact\n"})
    jobs.extend([
        {"id": "negative_sorry", "code": HEADER + "theorem target : False := by sorry\n#print axioms target\n"},
        {"id": "negative_fresh_axiom", "code": HEADER + "axiom untrusted : False\ntheorem target : False := untrusted\n#print axioms target\n"},
    ])
    for j in jobs:
        j.update(verifier=str(args.verifier), lake=str(args.lake))
    results = verify_jobs(jobs, args.output, workers=2)
    valid = all(r["accepted"] == (not r["id"].startswith("negative_")) for r in results)
    write(args.output.with_suffix(".summary.json"), {"passed": valid, "physical_lean_calls": len(jobs)})
    if not valid:
        raise SystemExit("Authored panel/negative control failed; no model execution allowed")


def generation_requests(args):
    if args.phase == "producer":
        return [{"id": r["id"], "world": r["id"], "kind": "producer", "condition": "producer",
                 "prompt": r["prompt"], "samples": 16, "max_tokens": 768}
                for r in json.loads((args.panel / "producer_inputs.json").read_text())]
    requests = []
    artifacts = json.loads(args.artifacts.read_text()) if args.artifacts else []
    for w in json.loads((args.panel / "worlds.json").read_text()):
        conditions = [("bare", "", 128)] if args.phase == "bare" else [
            ("oracle", w["oracle"], 32),
            ("irrelevant", "theorem reusable_fact (n : Nat) : n = n := by\n  rfl\n\n", 32)]
        if args.phase == "consumer":
            conditions += [(a["id"], a["code"], 16) for a in artifacts if a["world"] == w["id"]]
        for condition, helper, count in conditions:
            for target in w["targets"]:
                requests.append({"id": target["id"] + "/" + condition, "world": w["id"],
                    "target": target["id"], "kind": "consumer", "condition": condition,
                    "prompt": PREFIX + HEADER + w["definition"] + helper + target["statement"],
                    "samples": count, "max_tokens": 512})
    return requests


def generate(args):
    import torch
    from vllm import LLM, SamplingParams
    requests = generation_requests(args)
    model = LLM(model=str(args.model), tokenizer=str(args.tokenizer), dtype="bfloat16",
                tensor_parallel_size=1, seed=SEED, max_model_len=2304,
                gpu_memory_utilization=0.70, enforce_eager=True, disable_log_stats=True,
                max_num_seqs=64, swap_space=0)
    tokenizer = model.get_tokenizer()
    started = time.monotonic()
    with args.output.open("x", buffering=1) as stream:
        for request in requests:
            prompt_length = len(tokenizer.encode(request["prompt"]))
            if prompt_length > 1536:
                raise ValueError(f"Prompt limit exceeded: {request['id']}")
            params = SamplingParams(n=request["samples"], temperature=1.0, top_p=1.0,
                top_k=-1, max_tokens=request["max_tokens"], stop=["```"], include_stop_str_in_output=True,
                seed=SEED + int(sha(request["id"])[:6], 16))
            responses = model.generate([request["prompt"]], params, use_tqdm=False)[0]
            for index, response in enumerate(responses.outputs):
                row = {**request, "id": args.model_label + "/" + request["id"] + "/" + str(index),
                       "sample_index": index, "model": args.model_label, "text": response.text,
                       "prompt_tokens": prompt_length, "generated_tokens": len(response.token_ids),
                       "finish_reason": response.finish_reason}
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(json.dumps({"generated": request["id"], "samples": request["samples"]}), flush=True)
    write(args.output.with_suffix(".generation.json"), {"elapsed_seconds": time.monotonic()-started,
        "model": str(args.model), "torch": torch.__version__, "gpu": torch.cuda.get_device_name(0),
        "seed": SEED, "phase": args.phase})


def select(args):
    artifacts = []
    for label in ("base", "grpo"):
        records = rows(args.run / (label + "-producer.jsonl"))
        verdicts = {x["id"]: x for x in rows(args.run / (label + "-producer-verified.jsonl"))}
        for world in ("quadratic2", "quadratic3"):
            eligible = [r for r in records if r["world"] == world and verdicts[r["id"]]["accepted"]]
            for r in sorted(eligible, key=lambda x:x["sample_index"])[:4]:
                body, error = completion_code(r["text"], True)
                assert not error
                artifacts.append({"id": label + "_artifact_" + world + "_" + str(r["sample_index"]),
                    "world": world, "producer": label, "proposal_id": r["id"],
                    "code": "theorem reusable_fact (n : Nat) :\n" + body + "\n\n",
                    "code_sha256": verdicts[r["id"]]["code_sha256"]})
    write(args.output, artifacts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["prepare", "generate", "verify", "select", "validate"])
    for name in ("output", "input", "panel", "run", "model", "tokenizer", "verifier", "lake", "artifacts"):
        p.add_argument("--"+name, type=Path)
    p.add_argument("--phase", choices=["producer", "bare", "consumer"])
    p.add_argument("--model-label", choices=["base", "grpo"])
    args = p.parse_args()
    if args.mode == "prepare": prepare(args.output)
    elif args.mode == "generate": generate(args)
    elif args.mode == "verify": verify_generated(args)
    elif args.mode == "validate": validate_panel(args)
    else: select(args)


if __name__ == "__main__":
    main()
