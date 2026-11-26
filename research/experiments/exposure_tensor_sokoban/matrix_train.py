"""CPU-ready grouped terminal-reward search, no imported solution states."""
import argparse
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import json
import time

import numpy as np
from matrix_flip import ROOT, TARGET, legal_neighbors, scalar_verify, tensor_value

# Max candidates before de-duplication: ordered p,q,3 axes plus all possible
# dependency relations, with up to 9 pivots per relation and 3 axes.
MAX_SLOTS = 9*8*3 + 3*9*(2**9-1)
ARMS = ('ordinary','extra','switch')


@lru_cache(maxsize=2048)
def candidate_array(state):
    states=legal_neighbors(state) or (state,)
    # Width fixed to cap9; zero is padding, not a rank-one term.
    arr=np.zeros((len(states),9),dtype=np.int32)
    keep=np.zeros(len(states),dtype=bool)
    for i,dest in enumerate(states):
        arr[i,:len(dest)]=dest
        keep[i]=len(dest)<=8
    return states,arr,keep


def episode(w,cap,rng,horizon,grad):
    state=ROOT
    score=np.zeros(4096,dtype=float) if grad else None
    path=[state]
    candidates=active=0
    for _ in range(horizon):
        states,arr,keep=candidate_array(state)
        candidates+=len(states)
        active+=1
        logits=w[arr].sum(axis=1)
        mask=keep if cap==8 else np.ones(len(states),dtype=bool)
        if not mask.any():
            path.append(state)
            continue
        logits[~mask]=-np.inf
        probs=np.exp(logits-logits.max())
        probs/=probs.sum()
        chosen=int(rng.choice(len(states),p=probs))
        if grad:
            score+=np.bincount(arr[chosen],minlength=4096)
            score-=np.bincount(arr.ravel(),weights=np.repeat(probs,9),minlength=4096)
        state=states[chosen]
        path.append(state)
        if len(state)<=7:
            assert scalar_verify(state)
            break
    if grad:
        score[0]=0
    return len(state)<=7,score,path,candidates,active


def verify_path(path,cap):
    assert path[0]==ROOT
    for src,dst in zip(path,path[1:]):
        assert len(dst)<=cap and tensor_value(dst)==TARGET
        assert dst in legal_neighbors(src) or (dst==src and not any(len(x)<=cap for x in legal_neighbors(src)))
    return len(path[-1])<=7 and scalar_verify(path[-1])


def run(args):
    config,arm,seed=args
    start=time.monotonic()
    rng=np.random.default_rng(seed)
    eval_rng=np.random.default_rng(seed+1000000)
    w=np.zeros(4096);m=w.copy();v=w.copy()
    history=[];witnesses=[]
    for t in range(config['updates']):
        cap=9 if arm=='extra' or (arm=='switch' and t<max(1,int(.3*config['updates']))) else 8
        gradient=np.zeros(4096);hits=mixed=candidates=active=0
        for _ in range(config['groups']):
            batch=[episode(w,cap,rng,config['horizon'],True) for _ in range(config['group_size'])]
            reward=np.array([e[0] for e in batch],dtype=float)
            hits+=int(reward.sum());mixed+=int(0<reward.sum()<len(reward))
            centered=reward-reward.mean()
            gradient+=sum(c*e[1] for c,e in zip(centered,batch))/len(batch)
            candidates+=sum(e[3] for e in batch);active+=sum(e[4] for e in batch)
        gradient/=config['groups']
        m=.9*m+.1*gradient;v=.999*v+.001*gradient**2
        w+=.003*(m/(1-.9**(t+1)))/(np.sqrt(v/(1-.999**(t+1)))+1e-8)
        history.append(dict(step=t+1,cap=cap,hits=hits,mixed_groups=mixed,
                            candidate_scores=candidates,active_actions=active,
                            allocated_max_slots=MAX_SLOTS*config['horizon']*config['groups']*config['group_size']))
    successes=0
    for _ in range(config['eval_count']):
        hit,_,path,_,_=episode(w,8,eval_rng,config['horizon'],False)
        assert verify_path(path,8)==hit
        successes+=int(hit)
        if hit and len(witnesses)<3:
            witnesses.append(path)
    return dict(arm=arm,seed=seed,history=history,evaluation_hits=successes,
                evaluation_count=config['eval_count'],witnesses=witnesses,
                candidate_cache=str(candidate_array.cache_info()),seconds=time.monotonic()-start)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--updates',type=int,default=120)
    p.add_argument('--groups',type=int,default=2)
    p.add_argument('--group-size',type=int,default=8)
    p.add_argument('--horizon',type=int,default=32)
    p.add_argument('--eval-count',type=int,default=128)
    p.add_argument('--seeds',nargs='+',type=int,default=[42,43,44,45])
    p.add_argument('--workers',type=int,default=1)
    a=p.parse_args();config=vars(a).copy();del config['out']
    jobs=[(config,arm,seed) for arm in ARMS for seed in a.seeds]
    if a.workers==1:
        results=list(map(run,jobs))
    else:
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            results=list(pool.map(run,jobs))
    a.out.write_text(json.dumps(dict(config=config,results=results),indent=2))
    print([(r['arm'],r['seed'],r['evaluation_hits']) for r in results])

if __name__=='__main__':
    main()
