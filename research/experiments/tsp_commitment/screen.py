"""Frozen one-shot TSP screen; same prompt within groups."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from environment import ROOT, verify

SCHEMA = {"type":"object", "additionalProperties":False,
          "properties":{"tour":{"type":"array","items":{"type":"integer"}}},
          "required":["tour"]}
MODELS = ("gpt-6-luna", "gpt-6.1-terra")
CONDITIONS = ("root","locked","released")
GATES = {"root":1,"locked":5,"released":4}


def prompt(case, mode):
    matrix = "\n".join(f"{i}: " + " ".join(map(str, row))
                        for i,row in enumerate(case["matrix"]))
    policy = {
        "root": "Only the first city, 0, is fixed. Choose every remaining visit yourself.",
        "locked": f"A greedy policy has committed to the prefix {case['greedy'][:5]}. "
                  "These five cities, in this exact order, must begin your tour. Choose the remaining visits.",
        "released": f"A greedy policy has committed to the prefix {case['greedy'][:5]}. "
                    "You may reconsider its final decision: only the first four cities "
                    f"{case['greedy'][:4]} must begin your tour. The fifth city may be visited later. "
                    "Choose the remaining visits."
    }[mode]
    return ("Solve this symmetric traveling salesman problem. Cities are numbered 0..11. "
            "The distance matrix below has rows and columns numbered 0..11; distances are integers. "
            f"The goal is a closed tour of length at most {case['threshold']}. It must start at 0, "
            "visit every city exactly once and return implicitly to 0. Do not repeat 0 at the end. "
            "Return only JSON containing the entire ordered tour, including the fixed prefix if any. "
            "Use no tools, external code, files, or solver calls.\n"
            + policy + "\nDistance matrix:\n" + matrix + "\n")


def run(root, case, model, mode, attempt):
    dest = root/model/mode/str(attempt)
    dest.mkdir(parents=True)
    query = prompt(case, mode)
    (dest/"prompt.txt").write_text(query)
    command = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
               "--sandbox","read-only","--color","never","--json","-m",model,
               "-c",'model_reasoning_effort="low"',
               "--output-schema",str(root/"schema.json"), "--output-last-message",str(dest/"answer.json"),"-"]
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="tsp-commitment-") as cwd:
        with (dest/"events.jsonl").open("w") as stdout, (dest/"stderr.txt").open("w") as stderr:
            try:
                rc = subprocess.run(command, input=query,text=True,cwd=cwd,stdout=stdout,
                                    stderr=stderr,timeout=180).returncode
            except subprocess.TimeoutExpired:
                rc = 124
    row = dict(model=model, condition=mode, attempt=attempt, returncode=rc,
               seconds=time.monotonic()-start,
               prompt_sha256=hashlib.sha256(query.encode()).hexdigest())
    try:
        events = [json.loads(line) for line in (dest/"events.jsonl").read_text().splitlines()]
        tools = [e.get("item", {}).get("type") for e in events if e.get("item", {}).get("type")
                 not in (None,"agent_message","reasoning","plan","todo_list")]
        row["usage"] = [e.get("usage") for e in events if e.get("type")=="turn.completed"]
        if rc or tools:
            raise ValueError(f"CLI failure or tool use: {tools}")
        answer = json.loads((dest/"answer.json").read_text())
        row["tour"] = answer["tour"]
        row.update(verify(case, row["tour"], case["greedy"][:GATES[mode]]))
    except (ValueError,TypeError,OSError,KeyError) as exc:
        row.update(reward=0,error=str(exc))
    print(row,flush=True)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--attempts",type=int,default=4)
    ap.add_argument("--workers",type=int,default=4)
    args=ap.parse_args()
    root=args.out.resolve()
    root.mkdir(parents=True,exist_ok=False)
    case=json.loads((ROOT/"case.json").read_text())
    (root/"schema.json").write_text(json.dumps(SCHEMA))
    jobs=[(root,case,m,c,a) for a in range(args.attempts) for m in MODELS for c in CONDITIONS]
    rows=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(lambda payload:run(*payload),jobs):
            rows.append(row)
            (root/"summary.json").write_text(json.dumps(rows,indent=2))
    groups=[]
    for m in MODELS:
        for c in CONDITIONS:
            group=[r for r in rows if r["model"]==m and r["condition"]==c]
            wins=sum(r["reward"] for r in group)
            groups.append(dict(model=m,condition=c,wins=wins,total=len(group),
                               mixed=0<wins<len(group),
                               best=min((r["length"] for r in group if r.get("prefix_valid")),default=None)))
    print(groups)
    (root/"groups.json").write_text(json.dumps(groups,indent=2))


if __name__=="__main__": main()
