"""Terminal-only fixed four-wire synthesis, no verifier hints or oracle in training."""
import argparse
import json
import time
import sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"reversible_initial"))
from environment import gate_library,gate_permutation

N=4
WIDTH=16
GATES=gate_library(N)
ACTIONS=len(GATES)
HORIZON=10
BATCH=64
STEPS=10000
SEEDS=range(42,46)
ROOT=np.arange(WIDTH,dtype=np.uint8)
TABLE=np.array([gate_permutation(N,g) for g in GATES],dtype=np.uint8)
GOAL=np.array(json.loads((HERE/"task.json").read_text())["target"],dtype=np.uint8)
ONE_HOT=np.eye(WIDTH,dtype=np.float32)
ARMS=[("root",False)]+[(mode,sw) for mode in ("root4","goal4","goal8","mix4") for sw in (False,True)]


def starts(mode,size,rng):
    state=np.tile(ROOT,(size,1))
    if mode=="root":
        return state,0
    depth=int(mode[-1])
    if mode.startswith("goal"):
        state[:]=GOAL
    elif mode.startswith("mix"):
        state[rng.random(size)<.5]=GOAL
    lens=rng.integers(1,depth+1,size=size)
    for i in range(depth):
        chosen=rng.integers(ACTIONS,size=size)
        nxt=TABLE[chosen[:,None],state]
        state=np.where((i<lens)[:,None],nxt,state)
    cost=int(lens.sum())
    solved=(state==GOAL).all(axis=1)
    if solved.any():
        state[solved],extra=starts(mode,int(solved.sum()),rng)
        cost+=extra
    return state,cost


def probabilities(x,w):
    logits=x@w
    logits-=logits.max(axis=1,keepdims=True)
    p=np.exp(logits);p/=p.sum(axis=1,keepdims=True)
    return p


def rollout(weights,start,rng,gradient=False):
    state=start.copy()
    alive=(state!=GOAL).any(axis=1)
    histories=[]
    count=0
    size=len(state)
    for _ in range(HORIZON):
        x=ONE_HOT[state].reshape(size,-1)
        prob=probabilities(x,weights)
        choice=np.minimum((rng.random(size)[:,None]>np.cumsum(prob,axis=1)).sum(axis=1),ACTIONS-1)
        if gradient: histories.append((x,prob,choice,alive.copy()))
        count+=int(alive.sum())
        state=np.where(alive[:,None],TABLE[choice[:,None],state],state)
        alive&=(state!=GOAL).any(axis=1)
    reward=(~alive).astype(np.float32)
    wins=int(reward.sum())
    if not gradient:
        return wins,count
    grad=np.zeros_like(weights)
    advantage=reward-reward.mean()
    if np.any(advantage):
        for x,prob,choice,mask in histories:
            score=-prob
            score[np.arange(size),choice]+=1
            score*=(advantage*mask)[:,None]
            grad+=x.T@score/size
    return wins,count,grad


def train(mode,sw,seed,steps=STEPS):
    w=np.random.default_rng(seed).normal(0,.02,(WIDTH*WIDTH,ACTIONS)).astype(np.float32)
    m=np.zeros_like(w);v=np.zeros_like(w)
    rr=np.random.default_rng(seed+30000)
    tr=np.random.default_rng(seed+20000)
    er=np.random.default_rng(seed+10000)
    first=None
    records=[]
    wins=real=reset=0
    root_wins=0
    t=time.monotonic()
    for step in range(steps+1):
        if step%250==0 or step==steps:
            hit,_=rollout(w,np.tile(ROOT,(512,1)),er)
            records.append(dict(step=step,root_hits=hit,root_trials=512,train_wins=wins,
                                root_train_wins=root_wins,active_actions=real,reset_actions=reset))
        if step==steps:break
        active="root" if sw and step>=round(steps*.6) else mode
        s,extra=starts(active,BATCH,rr)
        hit,actions,grad=rollout(w,s,tr,True)
        wins+=hit;real+=actions;reset+=extra
        if active=="root":
            root_wins+=hit
            if hit and first is None:first=step+1
        m=.9*m+.1*grad
        v=.999*v+.001*grad*grad
        w+=.01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(mode=mode,switch=sw,seed=seed,steps=steps,first_root_win_batch=first,
                policy_slots=steps*BATCH*HORIZON,records=records,weights=w.tolist(),
                seconds=time.monotonic()-t)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=[x for x,_ in ARMS])
    parser.add_argument("--switch",action="store_true")
    parser.add_argument("--seed",type=int)
    parser.add_argument("--steps",type=int,default=STEPS)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    arms=[(args.mode,args.switch)] if args.mode else ARMS
    seeds=[args.seed] if args.seed is not None else SEEDS
    for mode,sw in arms:
        for seed in seeds:
            r=train(mode,sw,seed,args.steps)
            dest=args.out/f"{mode}-{int(sw)}-{seed}.json"
            dest.write_text(json.dumps(r,separators=(',',':')))
            print(mode,sw,seed,r["records"][-1],"seconds",r["seconds"],flush=True)


if __name__=="__main__":main()
