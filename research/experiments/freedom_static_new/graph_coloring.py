"""Product policy over whole graph colorings; exact terminal rewards only."""
import argparse
import json
from pathlib import Path
import time

import numpy as np

N=15
MAX_COLORS=5
BATCH=256
STEPS=500
SWITCH=150
SEEDS=range(42,50)


def make_graph():
    rng=np.random.default_rng(20261127)
    planted=rng.permutation(np.repeat(np.arange(3),N//3))
    pairs=np.array([(i,j) for i in range(N) for j in range(i+1,N)
                    if planted[i]!=planted[j]],dtype=int)
    return pairs[rng.random(len(pairs))<.65]


def count_colorings(edges,k):
    order=sorted(range(N),key=lambda v:-sum(v in edge for edge in edges))
    adjacency=[set() for _ in range(N)]
    for i,j in edges:
        adjacency[i].add(j); adjacency[j].add(i)
    colors=[-1]*N
    def rec(depth):
        if depth==N:
            return 1
        v=order[depth]
        forbidden={colors[u] for u in adjacency[v]}
        total=0
        for c in range(k):
            if c not in forbidden:
                colors[v]=c
                total+=rec(depth+1)
        colors[v]=-1
        return total
    return rec(0)


def settings(mode,step):
    switch = 300 if mode.endswith("switch300") else 400 if mode.endswith("switch400") else SWITCH
    if mode=="ordinary" or ("-switch" in mode and step>=switch):
        return 3,1.,False
    if mode=="mask35-anneal300":
        return 3,min(1.,.35+.65*step/300),False
    if mode.startswith("mask35") or mode.startswith("expected35") or mode.startswith("shared35"):
        return 3,.35,False
    if mode.startswith("mask45") or mode.startswith("expected45") or mode.startswith("shared45"):
        return 3,.45,False
    if mode=="mask55-anneal":
        return 3,min(1.,.55+.45*step/SWITCH),False
    if mode.startswith("mask55"):
        return 3,.55,False
    if mode.startswith("mask75"):
        return 3,.75,False
    if mode.startswith("fixed55"):
        return 3,.55,True
    if mode.startswith("colors4"):
        return 4,1.,False
    if mode.startswith("colors5"):
        return 5,1.,False
    if mode.startswith("combined"):
        return 4,.75,False
    raise ValueError(mode)


def sample(weights,colors,rng,batch):
    logits=weights[:,:colors].copy()
    logits-=logits.max(axis=1,keepdims=True)
    probs=np.exp(logits)
    probs/=probs.sum(axis=1,keepdims=True)
    choice=(rng.random((batch,N,1))>np.cumsum(probs,axis=1)[None,:,:]).sum(axis=2)
    return probs,np.minimum(choice,colors-1)


def exact_reward(labels,edges,mask=None):
    conflicts=labels[:,edges[:,0]]==labels[:,edges[:,1]]
    if mask is not None:
        conflicts &= mask
    return ~conflicts.any(axis=1)


def train(edges,mode,seed):
    rng=np.random.default_rng(seed)
    eval_rng=np.random.default_rng(seed+100000)
    weights=rng.normal(0,.02,(N,MAX_COLORS)).astype(np.float32)
    # Use independent random stream for relaxation, avoiding coupling to policy samples.
    relaxation_rng=np.random.default_rng(seed+1000000)
    fixed_mask=relaxation_rng.random(len(edges))<.55
    m=np.zeros_like(weights); v=np.zeros_like(weights)
    train_hits=0
    full_train_hits=0
    checks=0
    records=[]
    switch_hits=0
    for step in range(STEPS+1):
        if step%50==0:
            _,labels=sample(weights,3,eval_rng,1024)
            hits=int(exact_reward(labels,edges).sum())
            # First successful assignment certificate only.
            certificate=labels[np.flatnonzero(exact_reward(labels,edges))[0]].tolist() if hits else None
            records.append(dict(step=step,root_hits=hits,root_trials=1024,
                                train_hits=train_hits,full_train_hits=full_train_hits,
                                constraint_checks=checks,certificate=certificate))
        if step==STEPS:
            break
        colors,keep,fixed=settings(mode,step)
        probs,labels=sample(weights,colors,rng,BATCH)
        shared=mode.startswith("shared") and keep<1.
        expected=mode.startswith("expected") and keep<1.
        mask=None if keep==1. or expected else fixed_mask if fixed else relaxation_rng.random(len(edges) if shared else (BATCH,len(edges)))<keep
        if expected:
            m_violations=(labels[:,edges[:,0]]==labels[:,edges[:,1]]).sum(axis=1)
            reward=((1-keep)**m_violations).astype(np.float32)
        else:
            reward=exact_reward(labels,edges,mask).astype(np.float32)
        train_hits+=float(reward.sum()) if mode.startswith("expected") else int(reward.sum())
        full_train_hits+=int((exact_reward(labels,edges)&(labels<3).all(axis=1)).sum())
        checks+=BATCH*len(edges) if mask is None else int(mask.sum())*(BATCH if fixed or shared else 1)
        advantage=reward-reward.mean()
        grad=np.zeros_like(weights)
        for c in range(colors):
            grad[:,c]=advantage @ ((labels==c).astype(np.float32)-probs[None,:,c])/BATCH
        m=.9*m+.1*grad; v=.999*v+.001*grad*grad
        weights+=.03*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(mode=mode,seed=seed,records=records,final_logits=weights.tolist())


MODES=["ordinary","mask55","mask55-switch","mask75","mask75-switch","fixed55","fixed55-switch",
       "colors4","colors4-switch","colors5","colors5-switch","combined","combined-switch","mask55-anneal"]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--followup",action="store_true")
    parser.add_argument("--controls",action="store_true")
    args=parser.parse_args()
    edges=make_graph()
    counts={str(k):count_colorings(edges,k) for k in (2,3)}
    assert counts["2"]==0 and counts["3"]>0
    print("graph",len(edges),counts,"uniform p",counts["3"]/3**N,flush=True)
    modes=["mask55-switch300","mask55-switch400","mask35","mask35-switch","mask45","mask45-switch","mask35-anneal300"] if args.followup else MODES
    if args.controls:
        modes=["expected45","shared45","expected35-switch","shared35-switch"]
    out=dict(edges=edges.tolist(),counts=counts,config=dict(steps=STEPS,batch=BATCH,switch=SWITCH,
             seeds=list(SEEDS),modes=modes),runs=[])
    for mode in modes:
        start=time.monotonic()
        for seed in SEEDS:
            result=train(edges,mode,seed)
            out["runs"].append(result)
        values=[r["records"][-1]["root_hits"] for r in out["runs"] if r["mode"]==mode]
        print(mode,values,"seconds",round(time.monotonic()-start,2),flush=True)
        args.out.write_text(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
