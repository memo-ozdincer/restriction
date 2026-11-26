"""Terminal-only learning on a fixed classical Tower of Hanoi task."""
import argparse
from collections import deque
import itertools
import json
import multiprocessing as mp
from pathlib import Path
import time
import numpy as np

BATCH=128
STEPS=3000
MODES=("root","uniform","uniform-switch","goalwalk","goalwalk-switch","rootwalk","rootwalk-switch")
ACTIONS=list(itertools.permutations(range(3),2))


def environment(n):
    states=list(itertools.product(range(3),repeat=n))
    index={s:i for i,s in enumerate(states)}
    transitions=np.empty((len(states),6),dtype=np.int32)
    legal=np.zeros_like(transitions,dtype=bool)
    for i,s in enumerate(states):
        top=[next((d for d,p in enumerate(s) if p==t),n) for t in range(3)]
        for a,(src,dst) in enumerate(ACTIONS):
            d=top[src]
            valid=d<top[dst]
            legal[i,a]=valid
            if valid:
                q=list(s);q[d]=dst
                transitions[i,a]=index[tuple(q)]
            else:transitions[i,a]=i
    root=index[(0,)*n];goal=index[(2,)*n]
    depth=np.full(len(states),-1,dtype=int);depth[goal]=0
    queue=deque([goal])
    while queue:
        i=queue.popleft()
        for j in transitions[i,legal[i]]:
            if depth[j]<0:depth[j]=depth[i]+1;queue.append(int(j))
    assert depth[root]==2**n-1 and np.all(depth>=0)
    features=np.eye(3,dtype=np.float32)[np.array(states)].reshape(-1,3*n)
    return transitions,legal,features,root,goal,depth


def probabilities(weights,features,legal):
    logits=features@weights
    logits=np.where(legal,logits,-1e9)
    logits-=logits.max(axis=1,keepdims=True)
    p=np.exp(logits)
    return p/p.sum(axis=1,keepdims=True)


def exact_probability(p,env,horizon):
    transitions,legal,features,root,goal,depth=env
    hit=np.zeros(len(depth));hit[goal]=1
    for _ in range(horizon):
        hit=(hit[transitions]*p).sum(axis=1);hit[goal]=1
    return float(hit[root]),[float(hit[depth==d].mean()) for d in range(depth.max()+1)]


def choices(p,rng):
    return np.minimum((rng.random(len(p))[:,None]>np.cumsum(p,axis=1)).sum(axis=1),5)


def starts(mode,rng,env,size):
    transitions,legal,features,root,goal,depth=env
    if mode=="root":return np.full(size,root,dtype=np.int32),0
    if mode=="uniform":
        states=rng.integers(0,len(depth)-1,size=size,dtype=np.int32)
        states+=states>=goal
        return states,0
    center=goal if mode=="goalwalk" else root
    states=np.full(size,center,dtype=np.int32)
    length=rng.integers(1,13,size=size)
    for k in range(12):
        p=legal[states]/legal[states].sum(axis=1,keepdims=True)
        states=np.where(k<length,transitions[states,choices(p,rng)],states)
    cost=int(length.sum())
    invalid=states==goal
    if invalid.any():
        repl,extra=starts(mode,rng,env,int(invalid.sum()))
        states[invalid]=repl;cost+=extra
    return states,cost


def rollout(weights,initial,env,horizon,rng,gradient=False):
    transitions,legal,features,root,goal,depth=env
    state=initial.copy();alive=state!=goal
    history=[];actions=0
    for _ in range(horizon):
        x=features[state]; p=probabilities(weights,x,legal[state])
        a=choices(p,rng)
        if gradient:history.append((x,p,a,alive.copy()))
        actions+=int(alive.sum())
        state=np.where(alive,transitions[state,a],state)
        alive &= state!=goal
    r=(~alive).astype(np.float32)
    if not gradient:return int(r.sum()),actions
    adv=r-r.mean();g=np.zeros_like(weights)
    for x,p,a,active in history:
        score=-p;score[np.arange(len(a)),a]+=1
        g+=x.T@(score*(adv*active)[:,None])/len(r)
    return int(r.sum()),actions,g


def train(job):
    n,mode,seed,steps=job
    env=environment(n);transitions,legal,features,root,goal,depth=env
    horizon=2**n-1
    rng=np.random.default_rng(seed+100);reset_rng=np.random.default_rng(seed+200)
    eval_rng=np.random.default_rng(seed+300)
    weights=np.random.default_rng(seed).normal(0,.02,(3*n,6)).astype(np.float32)
    m=np.zeros_like(weights);v=np.zeros_like(weights)
    wins=actions=reset_actions=0;first=None;records=[]
    begin=time.monotonic()
    for step in range(steps+1):
        if step%100==0 or step==steps:
            hits,_=rollout(weights,np.full(256,root),env,horizon,eval_rng)
            exact,_=exact_probability(probabilities(weights,features,legal),env,horizon)
            records.append(dict(step=step,root_hits=hits,root_trials=256,exact_probability=exact,
                                train_wins=wins,actions=actions,reset_actions=reset_actions))
        if step==steps:break
        distribution=mode.split("-")[0]
        if mode.endswith("-switch") and step>=int(.6*steps):distribution="root"
        initial,cost=starts(distribution,reset_rng,env,BATCH);reset_actions+=cost
        hit,count,grad=rollout(weights,initial,env,horizon,rng,True)
        wins+=hit;actions+=count
        if hit and first is None:first=step
        m=.9*m+.1*grad;v=.999*v+.001*grad*grad
        weights+=.01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    p=probabilities(weights,features,legal);exact,shell=exact_probability(p,env,horizon)
    return dict(n=n,mode=mode,seed=seed,steps=steps,first_training_reward=first,
                final_root_probability=exact,final_shell_probability=shell,
                records=records,weights=weights.tolist(),
                policy_slots=steps*BATCH*horizon,seconds=time.monotonic()-begin)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--steps",type=int,default=STEPS)
    parser.add_argument("--workers",type=int,default=1)
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args()
    jobs=[(n,mode,seed,args.steps) for n in (5,6) for mode in MODES for seed in range(42,50)]
    if args.smoke:jobs=[(5,"root",42,20),(5,"uniform-switch",42,20)]
    for n in (5,6):
        env=environment(n);legal=env[1]
        print("random root",n,exact_probability(legal/legal.sum(axis=1,keepdims=True),env,2**n-1)[0])
    rows=[]
    with mp.Pool(args.workers) as pool:
        for row in pool.imap_unordered(train,jobs):
            rows.append(row);args.out.write_text(json.dumps(rows))
            print(row["n"],row["mode"],row["seed"],row["final_root_probability"],flush=True)
