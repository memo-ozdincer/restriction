"""Offline exact ordinary symmetry-quotient geometry and tiny random audit."""
import argparse
import json
from pathlib import Path
from collections import Counter
import time

import numpy as np
from matrix_flip import ROOT, TARGET, symmetry_map, orbit_key, cap_neighbors, scalar_verify, certify


def ordinary_geometry(horizons=(8,16,32,64), limit=3000):
    maps=symmetry_map()
    states=[ROOT]
    index={orbit_key(ROOT,maps):0}
    edges=[]
    for state in states:
        if len(state)<=7:
            edges.append({index[orbit_key(state,maps)]:1})
            continue
        row=Counter()
        for nxt in cap_neighbors(state,8):
            key=orbit_key(nxt,maps)
            if key not in index:
                index[key]=len(states)
                states.append(nxt)
                if len(states)>limit:
                    raise RuntimeError("ordinary quotient exceeded audit limit")
            row[index[key]]+=1
        edges.append(dict(row))
    terminal=np.array([len(s)<=7 for s in states])
    assert terminal.sum() and all(scalar_verify(s) for s in states if len(s)<=7)
    probability=terminal.astype(float)
    out={}
    for t in range(1,max(horizons)+1):
        probability=np.array([sum(count*probability[j] for j,count in row.items())/sum(row.values())
                              for row in edges])
        if t in horizons:
            out[str(t)]=float(probability[0])
    return dict(orbits=len(states),goal_orbits=int(terminal.sum()),
                mixture_hit=out,quotient="GL(2,F2)^3; no axis permutations",
                ordinary_root_degree=len(cap_neighbors(ROOT,8)),
                extra_root_degree=len(cap_neighbors(ROOT,9)))


def uniform_samples(cap, episodes=32,horizon=32,seed=42):
    rng=np.random.default_rng(seed)
    hits=0
    total_candidates=active=0
    unique={ROOT}
    for _ in range(episodes):
        state=ROOT
        for step in range(horizon):
            choices=cap_neighbors(state,cap)
            total_candidates+=len(choices)
            active+=1
            state=choices[int(rng.integers(len(choices)))]
            unique.add(state)
            if len(state)<=7:
                assert scalar_verify(state)
                hits+=1
                break
    return dict(cap=cap,hits=hits,episodes=episodes,horizon=horizon,
                candidates=total_candidates,active_actions=active,unique_labeled_states=len(unique))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    start=time.monotonic()
    certificate=certify()
    assert certificate["found"]
    result=dict(root=list(ROOT),target=TARGET,certificate=certificate,
                ordinary=ordinary_geometry(),random_samples=[uniform_samples(c) for c in (8,9)],
                seconds=time.monotonic()-start)
    a.out.write_text(json.dumps(result,indent=2))
    print(result)


if __name__=="__main__":
    main()
