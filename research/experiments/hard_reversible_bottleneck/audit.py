"""Independent exact root path probability and simulator replay."""
import argparse
import json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"reversible_initial"))
from environment import gate_library, gate_permutation, verify, execute

N=4
WIDTH=16
LIB=gate_library(N)
DAG=json.loads((HERE/"dag.json").read_text())
TASK=json.loads((HERE/"task.json").read_text())
GOAL=tuple(TASK["target"])
ROOT=tuple(range(WIDTH))
HORIZON=TASK["horizon"]
HOT=np.eye(WIDTH,dtype=np.float32)


def paths():
    records=[(ROOT,[])]
    for layer in DAG:
        links={tuple(row["state"]):row["links"] for row in layer}
        records=[(tuple(dst),actions+[a]) for s,actions in records for a,dst in links[s]]
    assert len(records)==TASK["verified_shortest_count"]
    assert all(s==GOAL and verify(N,GOAL,[LIB[a] for a in actions],HORIZON)["reward"] for s,actions in records)
    return [actions for _,actions in records]


def probs(w):
    result={ROOT:1.}
    for layer in DAG:
        following=defaultdict(float)
        for row in layer:
            s=tuple(row["state"])
            logits=(HOT[list(s)].reshape(-1)@w).astype(np.float64)
            p=np.exp(logits-logits.max());p/=p.sum()
            for a,dst in row["links"]:
                assert execute(N,[LIB[a]],s)==tuple(dst)
                following[tuple(dst)]+=result[s]*float(p[a])
        result=following
    assert list(result)==[GOAL]
    return result[GOAL]


def scalar_replay(w,seed,trials=512):
    rng=np.random.default_rng(seed)
    successes=[]
    for _ in range(trials):
        s=ROOT;actions=[]
        for _ in range(HORIZON):
            logits=HOT[list(s)].reshape(-1)@w
            p=np.exp(logits-logits.max());p/=p.sum()
            a=min(int((rng.random()>np.cumsum(p)).sum()),len(LIB)-1)
            actions.append(LIB[a])
            s=execute(N,[LIB[a]],s)
            if s==GOAL:break
        if verify(N,GOAL,actions,HORIZON)["reward"]:
            successes.append(actions)
    return successes


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--runs",type=Path,default=HERE/"runs")
    p.add_argument("--out",type=Path,default=HERE/"audit.json")
    p.add_argument("--scalar-threshold",type=float,default=0.01)
    a=p.parse_args()
    all_paths=paths()
    print("verified shortest paths",len(all_paths),"uniform",probs(np.zeros((256,32),dtype=np.float32)))
    rows=[]
    for file in sorted(a.runs.glob("*.json")):
        r=json.loads(file.read_text())
        w=np.array(r["weights"],dtype=np.float32)
        initial=np.random.default_rng(r["seed"]).normal(0,.02,(256,32)).astype(np.float32)
        start=probs(initial);final=probs(w)
        s=dict(mode=r["mode"],switch=r["switch"],seed=r["seed"],steps=r["steps"],
               initial_exact_probability=start,final_exact_probability=final,
               first_root_win_batch=r["first_root_win_batch"],final=r["records"][-1],
               weights_unchanged=bool(np.array_equal(initial,w)))
        if final>=a.scalar_threshold:
            successes=scalar_replay(w,99000+r["seed"])
            s["scalar_wins"]=len(successes)
            s["scalar_trials"]=512
            s["verified_example"]=successes[0] if successes else None
        rows.append(s)
        print(file.name,start,final,"root wins",s["final"]["root_train_wins"],flush=True)
    a.out.write_text(json.dumps(rows,indent=2))

if __name__=="__main__":main()
