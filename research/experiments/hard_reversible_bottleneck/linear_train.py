"""Terminal-only restricted CNOT matrix task; no shortest path oracle in training."""
import argparse,json,time,sys
from pathlib import Path
import numpy as np
from linear_certificate import N,ACTIONS,ROOT,HORIZON
HERE=Path(__file__).resolve().parent
ROOT=np.asarray(ROOT,dtype=np.uint8)
GOAL=np.asarray(json.loads((HERE/"linear_task.json").read_text())["target"],dtype=np.uint8)
HOT=np.eye(1<<N,dtype=np.float32)
IDX=np.array(ACTIONS,dtype=int);A=len(ACTIONS);BATCH=64;STEPS=6000
ARMS=[("root",None),("goal4",None),("goal4",1000)]


def move_batch(s,choices):
    nxt=s.copy()
    i,j=IDX[choices].T
    k=np.arange(len(s))
    nxt[k,i]^=s[k,j]
    return nxt


def starts(mode,size,rng):
    states=np.tile(ROOT if mode=="root" else GOAL,(size,1))
    if mode=="root":return states,0
    lengths=rng.integers(1,5,size=size)
    for j in range(4):states=np.where((j<lengths)[:,None],move_batch(states,rng.integers(A,size=size)),states)
    solved=(states==GOAL).all(1);cost=int(lengths.sum())
    if solved.any():
        states[solved],extra=starts(mode,int(solved.sum()),rng);cost+=extra
    return states,cost


def probabilities(s,w):
    x=HOT[s].reshape(len(s),-1)
    z=x@w;z-=z.max(1,keepdims=True)
    p=np.exp(z);p/=p.sum(1,keepdims=True)
    return x,p


def rollout(w,s,rng,gradient=False):
    s=s.copy();alive=(s!=GOAL).any(1);history=[];actions=0
    for _ in range(HORIZON):
        x,p=probabilities(s,w);choice=np.minimum((rng.random(len(s))[:,None]>np.cumsum(p,axis=1)).sum(1),A-1)
        if gradient:history.append((x,p,choice,alive.copy()))
        actions+=int(alive.sum())
        s=np.where(alive[:,None],move_batch(s,choice),s)
        alive&=(s!=GOAL).any(1)
    r=(~alive).astype(np.float32);wins=int(r.sum())
    if not gradient:return wins,actions
    adv=r-r.mean();grad=np.zeros_like(w)
    if np.any(adv):
        for x,p,choice,mask in history:
            score=-p;score[np.arange(len(s)),choice]+=1;score*=(adv*mask)[:,None]
            grad+=x.T@score/len(s)
    return wins,actions,grad


def train(mode,switch,seed):
    w=np.random.default_rng(seed).normal(0,.02,(N*(1<<N),A)).astype(np.float32);m=np.zeros_like(w);v=np.zeros_like(w)
    rr=np.random.default_rng(seed+30000);tr=np.random.default_rng(seed+20000);er=np.random.default_rng(seed+10000)
    wins=rootwins=actions=reset=0;first=None;records=[];t=time.monotonic()
    for step in range(STEPS+1):
        if step%250==0:
            hit,_=rollout(w,np.tile(ROOT,(512,1)),er)
            records.append(dict(step=step,root_hits=hit,root_trials=512,train_wins=wins,root_wins=rootwins,active_actions=actions,reset_actions=reset))
        if step==STEPS:break
        active="root" if switch is not None and step>=switch else mode
        s,cost=starts(active,BATCH,rr)
        hit,n,grad=rollout(w,s,tr,True)
        wins+=hit;actions+=n;reset+=cost
        if active=="root":
            rootwins+=hit
            if hit and first is None:first=step+1
        m=.9*m+.1*grad;v=.999*v+.001*grad*grad
        w+=.01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(mode=mode,switch=switch,seed=seed,first_root_win_batch=first,records=records,weights=w.tolist(),seconds=time.monotonic()-t,
                policy_slots=STEPS*BATCH*HORIZON)


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--mode",required=True);parser.add_argument("--switch",type=int);parser.add_argument("--seed",type=int,required=True)
    a=parser.parse_args();result=train(a.mode,a.switch,a.seed)
    out=HERE/"linear_runs";out.mkdir(exist_ok=True)
    (out/f"{a.mode}-{a.switch}-{a.seed}.json").write_text(json.dumps(result,separators=(",",":")))
    print(a.mode,a.switch,a.seed,result["records"][-1],result["seconds"],flush=True)
