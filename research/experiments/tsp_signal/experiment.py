"""One fixed geometric TSP; audit reference quality and reward group variance."""
from functools import cache
import json
import math
from pathlib import Path
import random
import statistics

ROOT = Path(__file__).resolve().parent
N = 10
HORIZON = 3
GROUP = 8
REPEATS = 128
SEED = 20261127
MOVES = tuple((i,j) for i in range(N) for j in range(i+2,N)
              if (i,j) != (0,N-1))


def problem():
    rng = random.Random(SEED)
    points = tuple((rng.randrange(101),rng.randrange(101)) for _ in range(N))
    assert len(set(points)) == N
    return points, tuple(tuple(round(100*math.dist(a,b)) for b in points) for a in points)

POINTS, D = problem()


@cache
def cost(tour):
    return sum(D[a][b] for a,b in zip(tour, tour[1:]+tour[:1]))


def move(tour, action):
    i,j = action
    if (i,j) not in MOVES:
        raise ValueError(f"illegal 2-opt move: {action}")
    return tour[:i+1]+tour[i+1:j+1][::-1]+tour[j+1:]


def delta(tour, action):
    i,j = action
    a,b,c,d = tour[i],tour[i+1],tour[j],tour[(j+1)%N]
    return D[a][c]+D[b][d]-D[a][b]-D[c][d]


def exact_optimum():
    # dp[mask,last] is shortest path from 0 to last visiting mask of others.
    dp = {}
    for i in range(1,N):
        dp[1<<i,i] = D[0][i]
    for mask in range(2, 1<<N, 2):
        if mask.bit_count() <= 1:
            continue
        for i in range(1,N):
            if mask & (1<<i):
                prev = mask ^ (1<<i)
                dp[mask,i] = min(dp[prev,j]+D[j][i] for j in range(1,N) if prev&(1<<j))
    full = (1<<N)-2
    return min(dp[full,i]+D[i][0] for i in range(1,N))


def warmup(start):
    states = [start]
    while True:
        best = min(MOVES,key=lambda a:delta(states[-1],a))
        if delta(states[-1],best)>=0:
            return states
        states.append(move(states[-1],best))


def sample_action(tour,rng):
    # Temperature is only a policy setting; no oracle action labels.
    values = [delta(tour,a) for a in MOVES]
    baseline = min(values)
    tau = .03*cost(tour)
    weights = [math.exp(-(v-baseline)/tau) for v in values]
    return rng.choices(MOVES,weights=weights,k=1)[0]


def run_rollout(start,rng):
    state = start
    costs = [cost(state)]
    for _ in range(HORIZON):
        state = move(state,sample_action(state,rng))
        costs.append(cost(state))
    return costs


def exact_neighborhood(start):
    seen = {start}
    frontier = {start}
    for _ in range(HORIZON):
        new = {move(s,a) for s in frontier for a in MOVES} - seen
        seen |= new
        frontier = new
    return min(map(cost,seen)),len(seen)


def group_metrics(paths,optimum):
    ref = paths[0][0]
    best = min(min(p) for p in paths)
    cutoff = min(i for p in paths for i,v in enumerate(p) if v == best)
    rewards = [max(ref-min(p[:cutoff+1]),0)/ref for p in paths]
    terminals = [p[-1] == optimum for p in paths]
    return dict(nonzero_group=int(max(rewards)>min(rewards)),
                all_zero=int(not any(rewards)),
                positive_rollouts=sum(r>0 for r in rewards),
                terminal_successes=sum(terminals),
                mixed_terminal_group=int(any(terminals) and not all(terminals)),
                best_cost=best)


def run():
    opt = exact_optimum()
    rng = random.Random(SEED+1)
    rows = []
    traces = []
    for trial in range(16):
        start = (0,)+tuple(rng.sample(range(1,N),N-1))
        trajectory = warmup(start)
        traces.append({"trial":trial,"tour_states":trajectory,"costs":list(map(cost,trajectory))})
        for variant, state in [("mid",trajectory[(len(trajectory)-1)//2]),("plateau",trajectory[-1])]:
            metrics = []
            for group in range(REPEATS):
                local = random.Random(SEED+1000+trial*REPEATS+group)
                metrics.append(group_metrics([run_rollout(state,local) for _ in range(GROUP)],opt))
            reachable,count = exact_neighborhood(state)
            rows.append(dict(trial=trial,variant=variant,reference_cost=cost(state),
                             terminal_warmup_cost=cost(trajectory[-1]),minimum_reachable=reachable,
                             reachable_within_horizon= count,
                             groups=REPEATS,rollouts=REPEATS*GROUP,
                             nonzero_groups=sum(m["nonzero_group"] for m in metrics),
                             all_zero_groups=sum(m["all_zero"] for m in metrics),
                             positive_rollouts=sum(m["positive_rollouts"] for m in metrics),
                             terminal_successes=sum(m["terminal_successes"] for m in metrics),
                             mixed_terminal_groups=sum(m["mixed_terminal_group"] for m in metrics),
                             best_observed_cost=min(m["best_cost"] for m in metrics)))
    result = dict(points=POINTS,distance_matrix=D,optimum=opt,seed=SEED,horizon=HORIZON,group=GROUP,
                  traces=traces,rows=rows)
    (ROOT/"local_results.json").write_text(json.dumps(result,indent=2))
    for subset,predicate in [("all",lambda r:True),("suboptimal_plateaus",lambda r:r["terminal_warmup_cost"]>opt)]:
        for variant in ("mid","plateau"):
            chosen = [r for r in rows if r["variant"]==variant and predicate(r)]
            print(subset,variant,len(chosen), "groups",sum(r["groups"] for r in chosen),
                  "nonzero",sum(r["nonzero_groups"] for r in chosen),
                  "all_zero",sum(r["all_zero_groups"] for r in chosen),
                  "terminal_success",sum(r["terminal_successes"] for r in chosen),
                  "mixed_terminal",sum(r["mixed_terminal_groups"] for r in chosen),
                  "optimal_reachable_states",sum(r["minimum_reachable"]==opt for r in chosen))
    print("optimum", opt, "warmup terminals",[t["costs"][-1] for t in traces])


if __name__ == "__main__":
    run()
