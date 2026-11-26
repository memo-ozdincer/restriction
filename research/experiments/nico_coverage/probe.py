"""Audit signal from uniformly sampled unvisited native neighbors."""
import argparse
import json
from pathlib import Path
import random
import torch
from nico.checkpoint import load_checkpoint
from nico.problems.tsp import TSP
from nico.search import SearchState, advance, policy_logits, select_moves
from nico.train_rl import group_advantages
from audit import canonical, neighbor


@torch.no_grad()
def group(model, problem, instance, state, reference, horizon=32, G=20):
    inst = {k: v.repeat_interleave(G, 0) for k,v in instance.items()}
    state = state.repeat_interleave(G)
    ref = torch.full((G,),reference)
    best = ref.clone()
    best_time = torch.full((G,),-1,dtype=torch.long)
    trace = []
    for step in range(horizon):
        logits,_ = policy_logits(model,problem,inst,state)
        state = advance(problem,inst,state,select_moves(logits,state.solution.size(1)))
        cost = problem.cost(inst,state.solution)
        improved = cost < best
        best = torch.minimum(best,cost)
        best_time[improved] = step
        trace.append(best.clone())
    adv = group_advantages(ref,torch.stack(trace),best_time,1,G)
    return dict(improving=int((best<ref).sum()),best=best.tolist(),
                nonzero=bool(adv.abs().sum()>1e-12),best_cost=float(best.min()))


@torch.no_grad()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--audit",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    torch.set_num_threads(4)
    torch.manual_seed(20261127)
    rng=random.Random(20261127)
    model,cfg,_=load_checkpoint(a.repo/"checkpoints/nico_tsp.pt")
    model.eval()
    problem=TSP()
    rows=[]
    for run in json.loads(a.audit.read_text())["runs"]:
        n=run["n"]
        if n!=20: continue
        instance=problem.from_coords(torch.tensor([run["coordinates"]]))
        B=8
        inst={k:v.repeat_interleave(B,0) for k,v in instance.items()}
        state=SearchState.initial(torch.tensor([run["start"]]).repeat_interleave(B,0),cfg.search)
        visited=set()
        saved={}
        for step in range(5*n+1):
            visited.update(canonical(t) for t in state.solution.tolist())
            if step in (2*n,5*n-1):
                saved[step]=state.index(torch.tensor([0])).clone()
            if step<5*n:
                state=advance(problem,inst,state,torch.tensor(run["moves"][step]))
        assert len(visited)==run["unique_tours"][-1]
        for step,state in saved.items():
            logits,_=policy_logits(model,problem,instance,state)
            tour=state.solution[0].tolist()
            actions={}
            for flat in torch.isfinite(logits[0]).nonzero().flatten().tolist():
                i,j=divmod(flat,n)
                key=neighbor(tour,i,j)
                if key not in visited: actions[key]=(i,j)
            picked=rng.choice(sorted(actions))
            action=actions[picked]
            alt=advance(problem,instance,state,torch.tensor([action]))
            assert canonical(alt.solution[0].tolist())==picked
            ref=float(state.progress[0,2])
            row=dict(trial=run["trial"],step=step,reference=ref,
                     root_cost=float(problem.cost(instance,state.solution)),
                     reset_cost=float(problem.cost(instance,alt.solution)),reset_move=action,
                     unseen_neighbors=len(actions),
                     ordinary=group(model,problem,instance,state,ref),
                     alternate=group(model,problem,instance,alt,ref))
            rows.append(row)
            a.out.write_text(json.dumps(rows,indent=2))
            print(run["trial"],step,row["ordinary"]["nonzero"],row["alternate"]["nonzero"],flush=True)


if __name__=="__main__":
    main()
