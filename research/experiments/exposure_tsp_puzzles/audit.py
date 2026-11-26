"""Frozen starting-policy audit; no learning or outcome-conditioned sampling."""
import json
import math
from pathlib import Path
import numpy as np
from run import TSP, TSP_REFERENCE, Flip, DIST, ROOT, GOAL, MASKS

tsp=TSP()
rng=np.random.default_rng(20261127)
gaps=[]
for _ in range(64):
    start,_=tsp.starts("root",rng,8)
    _,d,_,tours=start
    gaps.append(float(tsp.cost(d,tours)[0])/TSP_REFERENCE-1)
values={"warmup_gaps":gaps,"initial_groups":{}}
for bias in (0.,10.):
    w=np.random.default_rng(42).normal(0,.02,tsp.dim).astype(np.float32)
    w[12]+=bias
    for mode in ("root","subset"):
        rr=np.random.default_rng(20261128)
        pr=np.random.default_rng(20261129)
        groups=[]
        for i in range(64):
            start,_=tsp.starts(mode,rr,16)
            r=tsp.rollout(w,start,pr,True)
            groups.append(dict(cities=len(start[0]),informative=r["informative"],scores=r["score"]))
        values["initial_groups"][f"{bias}-{mode}"]=groups
# Exact finite horizon probability under uniform actions.
hit=np.zeros(512)
hit[GOAL]=1
for _ in range(Flip.horizon):
    hit=hit[np.arange(512)[:,None]^MASKS].mean(1)
    hit[GOAL]=1
assert math.isclose(hit[ROOT],math.factorial(9)/9**9)
uniform=np.zeros(512)
uniform[list(DIST)]=1
uniform[GOAL]=0
uniform/=uniform.sum()
mass=np.zeros(512)
mass[GOAL]=1
near=np.zeros_like(mass)
for _ in range(4):
    mass=np.bincount((np.arange(512)[:,None]^MASKS).ravel(),weights=np.repeat(mass/9,9),minlength=512)
    near+=mass/4
near[GOAL]=0
near/=near.sum()
values["flip"]={"root":ROOT,"goal":GOAL,"horizon":Flip.horizon,
                "distance_histogram":dict(zip(*[x.tolist() for x in np.unique(list(DIST.values()),return_counts=True)])),
                "uniform_action_root":float(hit[ROOT]),"uniform_action_uniform":float(hit@uniform),
                "uniform_action_near":float(hit@near)}
Path(__file__).with_name("initial_audit.json").write_text(json.dumps(values,indent=2))
for key,groups in values["initial_groups"].items():
    print(key,sum(g["informative"] for g in groups),sum(x>0 for g in groups for x in g["scores"]))
print(values["flip"])
