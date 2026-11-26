"""Measure native policy state coverage using released NICO checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import torch
from nico.checkpoint import load_checkpoint
from nico.problems.tsp import TSP
from nico.search import SearchState, advance, policy_logits, select_moves


def canonical(tour):
    tour = tuple(tour)
    i = tour.index(0)
    t = tour[i:] + tour[:i]
    return min(t, (t[0],) + t[:0:-1])


def neighbor(tour, i, j):
    i, j = sorted((i, j))
    return canonical(tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:])


@torch.no_grad()
def audit(model, cfg, n, trial):
    problem = TSP()
    instance = problem.sample_instances(1, n, "cpu")
    first = problem.random_solutions(instance)
    B = 8
    inst = {k: v.repeat_interleave(B, 0) for k, v in instance.items()}
    state = SearchState.initial(first.repeat_interleave(B, 0), cfg.search)
    visited = set()
    visits = []
    costs = []
    samples = []
    selected = []
    for step in range(5*n+1):
        tours = state.solution.tolist()
        keys = [canonical(t) for t in tours]
        visited.update(keys)
        visits.append(len(visited))
        costs.append(problem.cost(inst, state.solution).tolist())
        if step == 5*n:
            break
        logits, _ = policy_logits(model, problem, inst, state)
        probabilities = torch.softmax(logits.float(), -1)
        values = problem.move_values(inst, state.solution)
        if step in (0, n, 2*n, 5*n-1):
            for row in range(B):
                allowed = torch.isfinite(logits[row]).nonzero().flatten().tolist()
                candidates = {}
                for a in allowed:
                    i, j = divmod(a,n)
                    key = neighbor(tours[row], i,j)
                    candidates[key] = candidates.get(key,0.) + float(probabilities[row,a])
                samples.append((step,row,candidates,float(probabilities[row][values[row]>1e-8].sum())))
        moves = select_moves(logits,n,sample=True)
        selected.append(moves.tolist())
        state = advance(problem,inst,state,moves)
    results = []
    for step,row,candidates,worse in samples:
        observed = set(candidates) & visited
        results.append(dict(step=step,chain=row,neighbors=len(candidates),
                            seen=len(observed),seen_probability=sum(candidates[k] for k in observed),
                            worsening_probability=worse))
    return dict(n=n,trial=trial,coordinates=instance["coords"][0].tolist(),
                start=first[0].tolist(),unique_tours=visits,costs=costs,
                moves=selected,local_coverage=results)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    torch.set_num_threads(4)
    torch.manual_seed(42)
    checkpoint=a.repo/"checkpoints/nico_tsp.pt"
    model,cfg,data=load_checkpoint(checkpoint)
    model.eval()
    results=dict(revision=subprocess.check_output(["git","-C",str(a.repo),"rev-parse","HEAD"],text=True).strip(),
                 checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                 config=cfg.to_dict(),epoch=data["epoch"],stage=data["stage"],torch=torch.__version__,
                 seed=42,runs=[])
    t=time.monotonic()
    for n in (20,50):
        for trial in range(4):
            row=audit(model,cfg,n,trial)
            results["runs"].append(row)
            results["seconds"]=time.monotonic()-t
            a.out.write_text(json.dumps(results,indent=2))
            print(n,trial,row["unique_tours"][-1],flush=True)


if __name__=="__main__":
    main()
