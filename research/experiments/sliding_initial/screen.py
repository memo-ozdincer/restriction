"""Frozen one-shot baseline and distance-shell diagnostic."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import tempfile
import time
from environment import GOAL, distances, verify

ROOT = Path(__file__).resolve().parent
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"actions": {"type": "array", "items": {
              "type": "string", "enum": ["U", "D", "L", "R"]}}},
          "required": ["actions"]}
BUDGET = 29


def panel():
    depth = distances()
    rng = random.Random(20261127)
    cases = []
    for d in (29, 1, 3, 5):
        candidates = sorted(s for s, k in depth.items() if k == d)
        board = rng.choice(candidates)
        cases.append(dict(name=f"depth-{d}", distance=d, start=list(board),
                          shell_size=len(candidates)))
    return cases


def prompt(board):
    return (
        "Solve this 3x3 sliding tile puzzle. The board is in row-major order. "
        "0 is the blank. Each action moves the BLANK up (U), down (D), left (L), "
        "or right (R) by swapping it with the adjacent tile. A move must remain "
        "inside the board. Make the board exactly equal to the goal in at most "
        "29 moves. Return only a JSON object with actions as a list of move "
        "letters in execution order. Do not use tools.\n" +
        json.dumps({"current": board, "goal": GOAL, "budget": BUDGET})
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / "schema.json").write_text(json.dumps(SCHEMA))
    cases = json.loads((ROOT / "panel.json").read_text())
    rows = []
    for case in cases:
        out = root / case["name"]
        out.mkdir()
        query = prompt(case["start"])
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
                                        stdout=stdout, stderr=stderr, timeout=100).returncode
                except subprocess.TimeoutExpired:
                    rc = 124
        row = dict(case, model=args.model, returncode=rc, seconds=time.monotonic()-now)
        row["prompt_sha256"] = hashlib.sha256((out / "prompt.txt").read_bytes()).hexdigest()
        try:
            events = [json.loads(line) for line in (out / "events.jsonl").read_text().splitlines()]
            if rc or any(e.get("item", {}).get("type") not in
                         (None, "agent_message", "reasoning", "plan", "todo_list") for e in events):
                raise ValueError("failed CLI or tool use")
            row["answer_sha256"] = hashlib.sha256((out / "answer.json").read_bytes()).hexdigest()
            answer = json.loads((out / "answer.json").read_text())
            row["actions"] = answer["actions"]
            row.update(verify(case["start"], answer["actions"], BUDGET))
        except (ValueError, TypeError, OSError, KeyError) as exc:
            row.update(reward=0, error=str(exc))
        rows.append(row)
        (root / "summary.json").write_text(json.dumps(rows, indent=2))
        print(row, flush=True)


if __name__ == "__main__":
    main()
