"""Frozen one-shot row-operation synthesis diagnostic."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import time
from environment import starts, TARGET, BUDGET, verify

SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"actions": {"type": "array", "items": {
              "type": "object", "additionalProperties": False,
              "properties": {"dest": {"type": "integer"},
                             "src": {"type": "integer"},
                             "k": {"type": "integer"}},
              "required": ["dest", "src", "k"]}}}, "required": ["actions"]}


def matrix(state):
    return [list(state[i:i+3]) for i in (0, 3, 6)]


def prompt(start):
    return (
        "All matrix entries are integers modulo 3. Rows are numbered 0,1,2. "
        "Transform the CURRENT matrix into the target matrix in at most 7 elementary "
        "row operations. Each operation has the form {dest:i,src:j,k:c}. "
        "If i and j differ, replace row i by row i + c * row j modulo 3, "
        "where c is 1 or 2 (2 means subtraction). If i=j, the only legal c is 2; "
        "it replaces row i by 2 * row i modulo 3 (negation). "
        "Only these operations are legal. All other rows remain unchanged. "
        "Use no tools. Return JSON with actions in execution order.\n"
        + json.dumps({"current": matrix(start), "target": matrix(TARGET), "budget": BUDGET}))


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
    for mode, index, start, distance in starts():
        if mode != args.condition:
            continue
        out = root / str(index)
        out.mkdir()
        query = prompt(start)
        (out / "prompt.txt").write_text(query)
        command = ["codex", "exec", "--ignore-user-config", "--ephemeral",
                   "--skip-git-repo-check", "--sandbox", "read-only", "--color",
                   "never", "--json", "-m", args.model, "-c",
                   'model_reasoning_effort="low"', "--output-schema",
                   str(root / "schema.json"), "--output-last-message",
                   str(out / "answer.json"), "-"]
        now = time.monotonic()
        with tempfile.TemporaryDirectory() as cwd:
            with (out / "events.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
                try:
                    rc = subprocess.run(command, input=query, text=True, cwd=cwd,
                                        stdout=stdout, stderr=stderr, timeout=180).returncode
                except subprocess.TimeoutExpired:
                    rc = 124
        row = dict(index=index, condition=mode, model=args.model, start=start,
                   distance=distance, returncode=rc, seconds=time.monotonic()-now)
        try:
            events = [json.loads(line) for line in (out / "events.jsonl").read_text().splitlines()]
            if rc or any(e.get("item", {}).get("type") not in
                         (None, "agent_message", "reasoning", "plan", "todo_list") for e in events):
                raise ValueError("failed CLI or tool use")
            answer = json.loads((out / "answer.json").read_text())
            acts = [(g["dest"], g["src"], g["k"]) for g in answer["actions"]]
            row.update(verify(start, acts))
            row["submitted_actions"] = acts
        except (ValueError, TypeError, OSError, KeyError) as exc:
            row.update(reward=0, error=str(exc))
        rows.append(row)
        (root / "summary.json").write_text(json.dumps(rows, indent=2))
        print(row, flush=True)


if __name__ == "__main__":
    main()
