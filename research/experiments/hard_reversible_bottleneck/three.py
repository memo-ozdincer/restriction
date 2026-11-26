"""Mechanically selected three-wire rare-optimal-path target."""
import argparse,json,time,sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"freedom_reversible_new"))
from run import make_environment,build_distributions,probabilities,rollout,hitting_probability,WIDTH,ACTIONS

STEPS=10000;H=8;BATCH=128;SEEDS=range(42,46)
ARMS=[("root",None),("goal_walk4",None),("goal_walk4",180),("goal_walk4",1000),("goal_walk4",6000),("root_walk4",None),("root_walk4",180),("both_walks",180),("balanced_shell",180)]


def rare_environment():
    transitions,features,root,_,_=make_environment()
    depth=np.full(len(transitions),-1)
    depth[root]=0
    count=np.zeros(len(transitions),np.int64)
    count[root]=1
    frontier=np.array([root])
    for d in range(1,H+1):
        candidates=transitions[frontier].ravel()
        next_layer=np.unique(candidates[depth[candidates]<0])
        depth[next_layer]=d
        selected=depth[candidates]==d
        np.add.at(count,candidates[selected],np.repeat(count[frontier],ACTIONS)[selected])
        frontier=next_layer
    assert np.all(depth>=0)
    goal=min(frontier,key=lambda s:(count[s],s))
    target=features[goal].reshape(WIDTH,WIDTH).argmax(1)
    return (transitions,features,root,goal,target),int(count[goal])


def train(env,distributions,mode,switch,seed):
    transitions,features,root,goal,_=env
    w=np.random.default_rng(seed).normal(0,.02,(WIDTH*WIDTH,ACTIONS)).astype(np.float32)
    rr=np.random.default_rng(seed+30000);tr=np.random.default_rng(seed+20000);er=np.random.default_rng(seed+10000)
    cdf=np.cumsum(distributions[mode])
    m=np.zeros_like(w);v=np.zeros_like(w)
    wins=rootwins=active=0;first=None;records=[]
    t=time.monotonic()
    for step in range(STEPS+1):
        if step in (0,25,100,180,300,600,1000,2000,4000,6000,8000,10000):
            exact=hitting_probability(probabilities(features,w),transitions,goal,H)[root]
            hit,_=rollout(w,np.full(512,root),transitions,features,goal,er,H)
            records.append(dict(step=step,root_trials=512,root_hits=hit,root_probability=float(exact),train_wins=wins,root_wins=rootwins,active_actions=active))
        if step==STEPS:break
        is_root=mode=="root" or (switch is not None and step>=switch)
        starts=(np.full(BATCH,root,dtype=np.int32) if is_root else np.searchsorted(cdf,rr.random(BATCH),side="right").astype(np.int32))
        assert np.all(starts!=goal)
        hit,actions,grad=rollout(w,starts,transitions,features,goal,tr,H,gradient=True)
        wins+=hit;active+=actions
        if is_root:
            rootwins+=hit
            if first is None and hit:first=step+1
        m=.9*m+.1*grad;v=.999*v+.001*grad*grad
        w+=.01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(mode=mode,switch=switch,seed=seed,records=records,first_root_win_batch=first,policy_slots=STEPS*BATCH*H,weights=w.tolist(),seconds=time.monotonic()-t)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,default=HERE/"three_runs");p.add_argument("--mode");p.add_argument("--switch",type=int);p.add_argument("--seed",type=int)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    env,count=rare_environment(); t,x,root,goal,target=env
    dist,gd,rd=build_distributions(t,root,goal)
    baseline=hitting_probability(np.full((len(t),ACTIONS),1/ACTIONS),t,goal,H)
    (HERE/"three_task.json").write_text(json.dumps(dict(target=target.tolist(),optimum=H,shortest_count=count,uniform_root_probability=count/ACTIONS**H,reset_random_reward={key:float(value@baseline) for key,value in dist.items()}),indent=2))
    arms=ARMS if a.mode is None else [(a.mode,a.switch)]
    seeds=SEEDS if a.seed is None else [a.seed]
    for mode,switch in arms:
        for seed in seeds:
            r=train(env,dist,mode,switch,seed)
            (a.out/f"{mode}-{switch}-{seed}.json").write_text(json.dumps(r,separators=(",",":")))
            print(mode,switch,seed,r["records"][-1],r["seconds"],flush=True)
