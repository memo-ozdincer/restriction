"""Frozen no-tool diagnostic; each call sees the current exact state only."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
from environment import OPTIMUM, case, unresolved, verify

SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"comparators": {"type": "array", "items": {
              "type": "array", "items": {"type": "integer"}}}},
          "required": ["comparators"]}
MODELS = ("gpt-6-luna", "gpt-6.1-terra")
CONDITIONS = ("root", "random", "known")


def prompt(n, state, condition):
    rows = "All possible binary rows (sorted rows can be ignored)." if condition == "root" else json.dumps(unresolved(n, state))
    return (
        f"Construct a sorting network continuation for {n} wires numbered 0..{n-1} "
        "left to right. A comparator [i,j] with 0<=i<j<n replaces the "
        "values on wires i,j with their minimum and maximum respectively. "
        "The SAME sequence of comparators is applied to every row. The "
        "terminal goal is that every possible row is nondecreasing left to right. "
        "Here is the set of currently possible unsorted rows (wire 0 is the leftmost "
        "digit; sorted rows are implicit and need no work). "
        f"Current rows: {rows}\n"
        f"Use at most {OPTIMUM[n]} new comparators. Return only JSON "
        '{"comparators":[[i,j],...]}. No tools.\n'
    )


def attempt(root, model, n, condition):
    state, prefix = case(n, condition)
    out = root / model / str(n) / condition
    out.mkdir(parents=True)
    query = prompt(n, state, condition)
    (out / "prompt.txt").write_text(query)
    command = ["codex", "exec", "--ignore-user-config", "--ephemeral",
               "--skip-git-repo-check", "--sandbox", "read-only", "--color", "never",
               "--json", "-m", model, "-c", 'model_reasoning_effort="low"',
               "--output-schema", str(root / "schema.json"),
               "--output-last-message", str(out / "answer.json"), "-"]
    before = time.monotonic()
    with tempfile.TemporaryDirectory() as cwd:
        with (out / "events.jsonl").open("w") as stdout, (out / "stderr.txt").open("w") as stderr:
            try:
                rc = subprocess.run(command, input=query, text=True, cwd=cwd,
                                    stdout=stdout, stderr=stderr, timeout=180).returncode
            except subprocess.TimeoutExpired:
                rc = 124
    row = dict(model=model, n=n, condition=condition, budget=OPTIMUM[n],
               reset_prefix=prefix, initial_unsorted=len(unresolved(n, state)),
               returncode=rc, seconds=time.monotonic()-before,
               prompt_sha256=hashlib.sha256(query.encode()).hexdigest())
    try:
        events = [json.loads(line) for line in (out / "events.jsonl").read_text().splitlines()]
        if rc or any(e.get("item", {}).get("type") not in
                     (None, "agent_message", "reasoning", "plan", "todo_list") for e in events):
            raise ValueError("failed CLI or tool use")
        raw = (out / "answer.json").read_bytes()
        answer = json.loads(raw)
        gates = answer["comparators"]
        row["answer_sha256"] = hashlib.sha256(raw).hexdigest()
        row["actions"] = gates
        row.update(verify(n, gates, OPTIMUM[n], state))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        row.update(reward=0, error=str(exc))
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / "schema.json").write_text(json.dumps(SCHEMA))
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(attempt, root, model, n, condition)
                   for model in MODELS for n in OPTIMUM for condition in CONDITIONS]
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            rows.append(row)
            print(row, flush=True)
            (root / "summary.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
