"""Independently check policy hitting probabilities via the unique shortest Hanoi path."""
from pathlib import Path
import json
import math
import numpy as np
from run import ACTIONS

ROOT=Path(__file__).parent


def witness(n,src=0,dst=2,aux=1):
    if n:
        yield from witness(n-1,src,aux,dst)
        yield (src,dst)
        yield from witness(n-1,aux,dst,src)


def legal_moves(state):
    towers=[[d for d,p in enumerate(state) if p==t] for t in range(3)]
    return [(s,d) for s,d in ACTIONS if towers[s] and
            (not towers[d] or towers[s][0] < towers[d][0])]


def move(state,action):
    assert action in legal_moves(state)
    src,dst=action
    disk=next(d for d,p in enumerate(state) if p==src)
    state[disk]=dst


def policy(row,state,tabular):
    weights=np.asarray(row["weights"],dtype=np.float32)
    if tabular:
        index=sum(p*3**(len(state)-1-i) for i,p in enumerate(state))
        logits=weights[index]
    else:
        logits=weights[[3*i+p for i,p in enumerate(state)]].sum(axis=0)
    valid=legal_moves(state)
    ids=[ACTIONS.index(a) for a in valid]
    values=logits[ids].astype(float)
    p=np.exp(values-values.max());p/=p.sum()
    return valid,p


def audit(row,tabular):
    n=row["n"]
    state=[0]*n
    probability=1.
    route=list(witness(n))
    assert len(route)==2**n-1
    for a in route:
        valid,p=policy(row,state,tabular)
        probability*=p[valid.index(a)]
        move(state,a)
    assert state==[2]*n
    # Float32 training evaluation versus float64 independent product.
    assert math.isclose(probability,row["final_root_probability"],rel_tol=5e-5,abs_tol=1e-100)
    rng=np.random.default_rng(20261128)
    wins=0
    if probability>=.1:
        for _ in range(512):
            state=[0]*n
            for step in range(2**n-1):
                actions,p=policy(row,state,tabular)
                move(state,actions[rng.choice(len(actions),p=p)])
                if state==[2]*n:
                    assert step+1==2**n-1
                    wins+=1;break
    return dict(n=n,mode=row["mode"],seed=row["seed"],tabular=tabular,
                independent_probability=probability,
                fresh_trials=512 if probability>=.1 else 0,fresh_wins=wins)


if __name__=="__main__":
    items=[]
    for name,tabular in [("results.json",False),("tabular_results.json",True)]:
        data=json.loads((ROOT/name).read_text())
        for row in data:items.append(audit(row,tabular))
    (ROOT/"audit.json").write_text(json.dumps(items,indent=2))
    print("audited",len(items),"policies",sum(r["fresh_wins"] for r in items),
          "wins /",sum(r["fresh_trials"] for r in items))
