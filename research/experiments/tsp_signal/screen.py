"""Frozen independent rollouts on the first suboptimal warmup trajectory."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
from experiment import ROOT,N,D,HORIZON,cost,move,group_metrics

SCHEMA = {"type":"object","additionalProperties":False,
          "properties":{"moves":{"type":"array","items":{"type":"object",
                  "additionalProperties":False,
                  "properties":{"i":{"type":"integer"},"j":{"type":"integer"}},
                  "required":["i","j"]}}},
          "required":["moves"]}


def query(state):
    return (
        "Solve this symmetric 10-city traveling salesman problem. The current ordered "
        "tour visits every city once and closes back to its first city. You may change "
        "the tour using up to three 2-opt operations. In a move {i,j}, i and j are "
        "zero-indexed POSITIONS in the current tour, 0<=i<j<10, j>=i+2, excluding "
        "i=0,j=9. Reverse the inclusive segment from position i+1 through j. "
        "Subsequent positions refer to the resulting tour. Minimize the final closed "
        "tour's total integer length; doing no moves is allowed if best. Return "
        "only JSON with moves in execution order. Use no tools. The symmetric "
        "distance matrix D is indexed by city IDs 0..9.\n"
        +json.dumps({"D":D,"current":state,"move_budget":HORIZON})
    )


def attempt(model,variant,index,state,output,schema):
    directory=output/model/variant/str(index)
    directory.mkdir(parents=True)
    prompt=query(state)
    (directory/"prompt.txt").write_text(prompt)
    command=["codex","exec","--ignore-user-config","--ephemeral","--skip-git-repo-check",
             "--sandbox","read-only","--color","never","--json","-m",model,
             "-c",'model_reasoning_effort="low"',"--output-schema",str(schema),
             "--output-last-message",str(directory/"answer.json"),"-"]
    start=time.monotonic()
    with tempfile.TemporaryDirectory() as cwd:
        with (directory/"events.jsonl").open("w") as stdout, (directory/"stderr.txt").open("w") as stderr:
            try: rc=subprocess.run(command,input=prompt,text=True,cwd=cwd,
                                   stdout=stdout,stderr=stderr,timeout=180).returncode
            except subprocess.TimeoutExpired: rc=124
    row=dict(model=model,variant=variant,index=index,returncode=rc,seconds=time.monotonic()-start,
             prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
    try:
        events=[json.loads(x) for x in (directory/"events.jsonl").read_text().splitlines()]
        if rc or any(e.get("item",{}).get("type") not in
                     (None,"agent_message","reasoning","plan","todo_list") for e in events):
            raise ValueError("CLI error or tool use")
        answer=json.loads((directory/"answer.json").read_text())
        actions=answer["moves"]
        if len(actions)>HORIZON: raise ValueError("too many moves")
        costs=[cost(state)]
        for a in actions:
            if type(a["i"]) is not int or type(a["j"]) is not int: raise ValueError("invalid move type")
            state=move(state,(a["i"],a["j"]))
            costs.append(cost(state))
        row.update(valid=True,moves=actions,costs=costs)
    except (ValueError,TypeError,KeyError,OSError) as exc:
        row.update(valid=False,error=str(exc))
    return row


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--models",nargs="+",default=["gpt-6-luna","gpt-6.1-terra"])
    args=parser.parse_args()
    output=args.out.resolve()
    output.mkdir(parents=True,exist_ok=False)
    schema=output/"schema.json"
    schema.write_text(json.dumps(SCHEMA))
    local=json.loads((ROOT/"local_results.json").read_text())
    optimum=local["optimum"]
    trace=next((t for t in local["traces"] if t["costs"][-1]>optimum),local["traces"][0])
    states={k:tuple(v) for k,v in [("mid",trace["tour_states"][(len(trace["tour_states"])-1)//2]),
                                  ("plateau",trace["tour_states"][-1])]}
    rows=[]
    groups=[]
    for model in args.models:
        for variant,state in states.items():
            with ThreadPoolExecutor(max_workers=4) as pool:
                futures=[pool.submit(attempt,model,variant,i,state,output,schema) for i in range(4)]
                group=[f.result() for f in futures]
            rows.extend(group)
            paths=[r["costs"] if r["valid"] else [cost(state)] for r in group]
            metrics=group_metrics(paths,optimum)
            # Invalids carry zero in both metrics and cannot be credited at goal.
            metrics["terminal_successes"]=sum(r["valid"] and r["costs"][-1]==optimum for r in group)
            metrics["mixed_terminal_group"]=int(0<metrics["terminal_successes"]<len(group))
            entry=dict(model=model,variant=variant,reference_cost=cost(state),
                       valid=sum(r["valid"] for r in group),**metrics)
            groups.append(entry)
            print(entry,flush=True)
            (output/"summary.json").write_text(json.dumps(dict(trial=trace["trial"],states=states,
                 optimum=optimum,groups=groups,rows=rows),indent=2))


if __name__=="__main__":
    main()
