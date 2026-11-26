"""Frozen permutation synthesis screen. No feedback or solver access."""
import argparse
import json
from pathlib import Path
import random
import subprocess
import tempfile
import time
from environment import execute, identity, gate_library, random_start, load_benchmark, verify

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[3] / "circuit-tools/reversible-benchmarks"
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"actions": {"type": "array", "items": {
              "type": "object", "additionalProperties": False,
              "properties": {"target": {"type": "integer"},
                             "controls": {"type": "array", "items": {"type": "integer"}}},
              "required": ["target", "controls"]}}}, "required": ["actions"]}


def cases(condition):
    n = 4
    goal = load_benchmark(SOURCE, 1)["target"]
    rng = random.Random(20261127)
    gates = gate_library(n)
    for index in range(4):
        if condition == "root":
            start = identity(n)
        elif condition == "uniform":
            start = random_start(n, rng)
        else:
            # Certified upper bound of 1..4 moves to goal. No exact-distance claim.
            walk = [rng.choice(gates) for _ in range(index + 1)]
            start = execute(n, walk, goal)
            assert execute(n, reversed(walk), start) == goal
        yield index, start, goal


def prompt(start, goal):
    return (
        "There are four binary wires 0,1,2,3, numbered least significant bit first. "
        "The current permutation maps each input integer 0..15 to the current output "
        "integer. Apply generalized Toffoli gates to the CURRENT output values. "
        "A gate {target:t,controls:[c,...]} flips bit t exactly when all listed "
        "control bits are 1 (empty controls always flip). Controls must be distinct "
        "and exclude target. All gates cost one. Find at most 15 gates that transform "
        "the current permutation to the target permutation. Every entry must match. "
        "Return only JSON actions in execution order. Use no tools.\n"
        + json.dumps({"current": start, "target": goal, "budget": 15})
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--condition", choices=["root", "uniform", "near"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / "schema.json").write_text(json.dumps(SCHEMA))
    rows = []
    for index, start, goal in cases(args.condition):
        out = root / str(index)
        out.mkdir()
        query = prompt(start, goal)
        (out / "prompt.txt").write_text(query)
        command = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
                   "--sandbox", "read-only", "--color", "never", "--json",
                   "-m", args.model, "-c", 'model_reasoning_effort="low"',
                   "--output-schema", str(root / "schema.json"),
                   "--output-last-message", str(out / "answer.json"), "-"]
        now = time.monotonic()
        with tempfile.TemporaryDirectory() as cwd:
            with (out / "events.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
                try:
                    rc = subprocess.run(command, input=query, text=True, cwd=cwd,
                                        stdout=stdout, stderr=stderr, timeout=180).returncode
                except subprocess.TimeoutExpired:
                    rc = 124
        row = dict(index=index, condition=args.condition, model=args.model,
                   returncode=rc, seconds=time.monotonic()-now)
        try:
            events = [json.loads(line) for line in (out / "events.jsonl").read_text().splitlines()]
            if rc or any(e.get("item", {}).get("type") not in
                         (None, "agent_message", "reasoning", "plan", "todo_list") for e in events):
                raise ValueError("failed CLI or tool use")
            answer = json.loads((out / "answer.json").read_text())
            actions = [(g["target"], tuple(g["controls"])) for g in answer["actions"]]
            row.update(verify(4, goal, actions, 15, start))
        except (ValueError, TypeError, OSError, KeyError) as exc:
            row.update(reward=0, error=str(exc))
        rows.append(row)
        (root / "summary.json").write_text(json.dumps(rows, indent=2))
        print(row, flush=True)


if __name__ == "__main__":
    main()
