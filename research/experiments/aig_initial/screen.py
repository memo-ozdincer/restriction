"""Frozen one-shot Luna screen; no verifier feedback or reference circuits."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
import time
from aig import panel, verify

MODEL = "gpt-6-luna"
SCHEMA = {"type": "object", "additionalProperties": False,
          "properties": {"gates": {"type": "array", "items": {
              "type": "array", "items": {"type": "integer"}}},
                         "outputs": {"type": "array", "items": {"type": "integer"}}},
          "required": ["gates", "outputs"]}


def prompt(task, named=False):
    public = {k: task[k] for k in ("inputs", "target", "budget")}
    description = ""
    if named:
        name = task["name"]
        if name.startswith(("xor", "parity")):
            description = "The output is XOR of all input variables.\n"
        elif name == "majority3":
            description = "The output is true when at least two inputs are true.\n"
        elif name.startswith("add"):
            description = "Add the two unsigned input words (first half, second half), each least significant bit first. Outputs are sum bits least significant first, including carry.\n"
    return ("Construct an AND-inverter graph matching all target truth tables. "
            "Literal 2*i is node i, 2*i+1 its complement. Node 0 is false, "
            "nodes 1 through inputs are variables. Each gate is a pair of "
            "previous literals; its node index is inputs + 1 + its zero-based "
            "gate index. Outputs are literals in target order. Integer truth "
            "tables use bit r for assignment r, variable i (1-based) is bit "
            "i-1 of r. At most budget AND gates. Return JSON gates and outputs. "
            "Use no tools.\n" + description + json.dumps(public))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--named", action="store_true")
    parser.add_argument("--panel", type=Path, help="Optional external benchmark JSON")
    parser.add_argument("--calibration", type=Path, help="Optional certified minima JSON")
    args = parser.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    (root / "schema.json").write_text(json.dumps(SCHEMA))
    tasks = json.loads(args.panel.read_text()) if args.panel else panel()
    (root / "panel.json").write_text(json.dumps(tasks, indent=2))
    calibration_path = args.calibration or (None if args.panel else Path(__file__).with_name("optimality.json"))
    calibration = json.loads(calibration_path.read_text()) if calibration_path else {}
    rows = []
    for task in tasks:
        if args.named and task["name"].startswith("random"):
            continue
        optimum = calibration.get(task["name"], {}).get("optimum")
        if optimum is not None:
            task = dict(task, budget=optimum)
        for attempt in range(args.attempts):
            directory = root / task["name"] / str(attempt)
            directory.mkdir(parents=True)
            query = prompt(task, args.named)
            (directory / "prompt.txt").write_text(query)
            start = time.monotonic()
            command = ["codex", "exec", "--ignore-user-config", "--ephemeral",
                       "--skip-git-repo-check", "--sandbox", "read-only",
                       "--color", "never", "--json", "-m", MODEL,
                       "-c", 'model_reasoning_effort="low"',
                       "--output-schema", str(root / "schema.json"),
                       "--output-last-message", str(directory / "answer.json"), "-"]
            with tempfile.TemporaryDirectory() as cwd:
                with (directory / "events.jsonl").open("w") as stdout, (directory / "stderr.txt").open("w") as stderr:
                    try:
                        rc = subprocess.run(command, input=query, text=True, cwd=cwd,
                                            stdout=stdout, stderr=stderr, timeout=180).returncode
                    except subprocess.TimeoutExpired:
                        rc = 124
            row = {"task": task["name"], "attempt": attempt, "returncode": rc,
                   "seconds": time.monotonic() - start}
            try:
                events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
                tool_use = any(e.get("item", {}).get("type") not in
                               (None, "agent_message", "reasoning", "plan", "todo_list")
                               for e in events)
                if rc or tool_use:
                    raise ValueError("failed CLI or tool use")
                row.update(verify(task, **json.loads((directory / "answer.json").read_text())))
                row["optimum"] = optimum
                if row["correct"] and optimum is not None:
                    row["continuous_reward"] = 1.0 if row["gates"] == 0 else optimum / row["gates"]
                elif not row["correct"]:
                    row["continuous_reward"] = 0.0
            except (ValueError, TypeError, OSError) as exc:
                row.update(reward=0, error=str(exc))
            rows.append(row)
            (root / "summary.json").write_text(json.dumps(rows, indent=2))
            print(row, flush=True)


if __name__ == "__main__":
    main()
