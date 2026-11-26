"""Controlled capacity diagnostic: state-specific logits, same REINFORCE."""
import argparse
import json
import multiprocessing as mp
from pathlib import Path
import time
import numpy as np
from run import environment, exact_probability, choices, starts, BATCH, STEPS


def probs(weights,legal):
    logits=np.where(legal,weights,-1e9)
    logits-=logits.max(axis=1,keepdims=True)
    p=np.exp(logits)
    return p/p.sum(axis=1,keepdims=True)


def rollout(weights,initial,env,horizon,rng,gradient=False):
    transitions,legal,features,root,goal,depth=env
    state=initial.copy();alive=state!=goal
    history=[];actions=0
    for _ in range(horizon):
        p=probs(weights[state],legal[state]);a=choices(p,rng)
        if gradient:history.append((state.copy(),p,a,alive.copy()))
        actions+=int(alive.sum())
        state=np.where(alive,transitions[state,a],state);alive &= state!=goal
    r=(~alive).astype(np.float32)
    if not gradient:return int(r.sum()),actions
    adv=r-r.mean();g=np.zeros_like(weights)
    for s,p,a,active in history:
        score=-p;score[np.arange(len(a)),a]+=1
        np.add.at(g,s,score*(adv*active)[:,None]/len(r))
    return int(r.sum()),actions,g


def train(job):
    n,mode,seed,steps=job
    env=environment(n);transitions,legal,features,root,goal,depth=env
    horizon=2**n-1
    rng=np.random.default_rng(seed+100);reset_rng=np.random.default_rng(seed+200)
    eval_rng=np.random.default_rng(seed+300)
    initial=np.random.default_rng(seed).normal(0,.02,(3*n,6)).astype(np.float32)
    weights=features@initial
    m=np.zeros_like(weights);v=np.zeros_like(weights)
    wins=actions=reset_actions=0;first=None;records=[]
    begin=time.monotonic()
    for step in range(steps+1):
        if step%100==0 or step==steps:
            hits,_=rollout(weights,np.full(256,root),env,horizon,eval_rng)
            exact,_=exact_probability(probs(weights,legal),env,horizon)
            records.append(dict(step=step,root_hits=hits,root_trials=256,
                                exact_probability=exact,train_wins=wins,
                                actions=actions,reset_actions=reset_actions))
        if step==steps:break
        distribution=mode.split("-")[0]
        if mode.endswith("-switch") and step>=int(.6*steps):distribution="root"
        initial,cost=starts(distribution,reset_rng,env,BATCH);reset_actions+=cost
        hit,count,grad=rollout(weights,initial,env,horizon,rng,True)
        wins+=hit;actions+=count
        if hit and first is None:first=step
        m=.9*m+.1*grad;v=.999*v+.001*grad*grad
        weights+=.01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    exact,shell=exact_probability(probs(weights,legal),env,horizon)
    return dict(n=n,mode=mode,seed=seed,steps=steps,first_training_reward=first,
                final_root_probability=exact,final_shell_probability=shell,
                records=records,weights=weights.tolist(),
                policy_slots=steps*BATCH*horizon,seconds=time.monotonic()-begin)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--workers",type=int,default=1)
    args=parser.parse_args()
    jobs=[(n,mode,seed,STEPS) for n in (5,6)
          for mode in ("root","uniform","uniform-switch","goalwalk","goalwalk-switch")
          for seed in range(42,50)]
    rows=[]
    with mp.Pool(args.workers) as pool:
        for row in pool.imap_unordered(train,jobs):
            rows.append(row);args.out.write_text(json.dumps(rows))
            print(row["n"],row["mode"],row["seed"],row["final_root_probability"],flush=True)
