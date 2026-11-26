"""Frozen three-wire exact-distance screen with local causal LM checkpoints."""
import argparse
import json
import random
import subprocess
from pathlib import Path

from environment import distances, identity, verify


def panel():
    rng = random.Random(20261127)
    goal = rng.choice(sorted(p for p, d in distances(3).items() if d == 8))
    depth = distances(3, goal)
    for condition, ds in [("root", [8]*4), ("uniform", [None]*4), ("near", [1, 2, 3, 4])]:
        for i, d in enumerate(ds):
            start = identity(3) if condition == "root" else rng.choice(sorted(p for p, v in depth.items() if d is None or d == v))
            yield dict(condition=condition, index=i, current=start, target=goal,
                       exact_distance=depth[start], budget=8)


def prompt(row):
    return ("Three binary wires 0,1,2, numbered least significant bit first. The current permutation maps each input integer 0..7 to its current output integer. Apply generalized Toffoli gates to CURRENT output values. A gate {\"target\":t,\"controls\":[c,...]} flips bit t exactly when all listed control bits are 1 (empty controls always flip). Controls must be distinct and exclude target. Each gate costs one. Find at most 8 gates that transform the current permutation to the target permutation. Every entry must match. Return only JSON {\"actions\":[...]} in execution order.\n" + json.dumps({k: row[k] for k in ("current", "target", "budget")}))


def score(row, answer):
    try:
        obj = json.loads(answer.strip())
        if not isinstance(obj, dict) or set(obj) != {"actions"} or not isinstance(obj["actions"], list):
            raise ValueError("invalid action container")
        actions = []
        for g in obj["actions"]:
            if not isinstance(g, dict) or set(g) != {"target", "controls"} or type(g["target"]) is not int or not isinstance(g["controls"], list) or any(type(c) is not int for c in g["controls"]):
                raise ValueError("invalid gate")
            actions.append((g["target"], tuple(g["controls"])))
        return verify(3, row["target"], actions, row["budget"], row["current"])
    except (ValueError, TypeError, KeyError) as exc:
        return dict(reward=0, correct=False, error=str(exc))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--preview", action="store_true")
    args = p.parse_args()
    rows = list(panel())
    if args.preview:
        print(json.dumps(rows, indent=2)); return
    if args.model is None or args.out is None:
        p.error("--model and --out are required for execution")
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("Exactly one allocated CUDA GPU is required")
    tok = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, torch_dtype=torch.bfloat16).to("cuda").eval()
    args.out.mkdir(parents=True, exist_ok=False)
    meta = dict(model=str(args.model), torch=torch.__version__, transformers=transformers.__version__, cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(), commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), dirty=subprocess.check_output(["git", "status", "--porcelain"], text=True), seed=20261127, max_new_tokens=1024, temperature=0.7, top_p=0.95, panel=rows)
    (args.out / "manifest.json").write_text(json.dumps(meta, indent=2))
    for i, row in enumerate(rows):
        torch.manual_seed(20261127+i)
        query = prompt(row)
        rendered = tok.apply_chat_template([{"role":"user", "content":query}], tokenize=False, add_generation_prompt=True)
        inputs = tok(rendered, return_tensors="pt").to("cuda")
        with torch.inference_mode():
            generated = model.generate(**inputs, max_new_tokens=1024, do_sample=True, temperature=0.7, top_p=0.95, pad_token_id=tok.eos_token_id)
        answer = tok.decode(generated[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)
        result = dict(row, prompt=query, answer=answer, **score(row, answer))
        with (args.out / "results.jsonl").open("a") as f:
            f.write(json.dumps(result)+"\n")
        print(row["condition"], row["index"], result["reward"], flush=True)
    (args.out / "complete").touch()


if __name__ == "__main__":
    main()
