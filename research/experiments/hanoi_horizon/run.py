import argparse, json, multiprocessing as mp, sys, time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'hanoi_mechanism'))
from analyze import environment, reset_distributions, route, value_gradient
from run import rollout as linear_rollout, probabilities, starts, BATCH, STEPS
from tabular import rollout as tabular_rollout, probs


def train(job):
    n,mode,seed,mult,tab=job
    env=environment(n); t,l,f,root,goal,depth=env; H=2**n-1; horizon=H*mult
    rng=np.random.default_rng(seed+100); reset_rng=np.random.default_rng(seed+200)
    initial=np.random.default_rng(seed).normal(0,.02,(3*n,6)).astype(np.float32)
    w=f@initial if tab else initial
    m=np.zeros_like(w); v=np.zeros_like(w); wins=actions=reset_actions=0
    records=[]; begin=time.monotonic(); distributions=reset_distributions(env)
    rr=np.array(route(env,n)); ss,aa=rr.T
    def policy(): return probs(w,l) if tab else probabilities(w,f,l)
    def checkpoint(step):
        p=policy().astype(float); p/=p.sum(1,keepdims=True)
        lg=float(np.log(p[ss,aa]).sum()); gd=np.zeros_like(p); gd[ss]=-p[ss];gd[ss,aa]+=1
        if not tab:gd=f.T@gd
        hit=np.zeros(len(depth));hit[goal]=1; curves={}
        for j in range(1,16*H+1):
            hit=(p*hit[t]).sum(1);hit[goal]=1
            if j in (H,2*H,4*H,16*H):curves[str(j//H)]=float(hit[root])
            if j==horizon:uniform=float(distributions['uniform']@hit)
        _,g=value_gradient(p,env,distributions['uniform'],horizon,tab)
        norm=np.linalg.norm(g)*np.linalg.norm(gd)
        records.append(dict(step=step,root_log=lg,root_curves=curves,uniform=uniform,train_wins=wins,actions=actions,reset_actions=reset_actions,uniform_cosine=float(np.sum(g*gd)/norm) if norm else None))
    for step in range(STEPS+1):
        if step%100==0 or step==STEPS:checkpoint(step)
        if step==STEPS:break
        dist=mode.split('-')[0]
        if mode.endswith('-switch') and step>=int(.6*STEPS):dist='root'
        states,cost=starts(dist,reset_rng,env,BATCH);reset_actions+=cost
        hit,count,g=(tabular_rollout if tab else linear_rollout)(w,states,env,horizon,rng,True)
        wins+=hit;actions+=count
        m=.9*m+.1*g;v=.999*v+.001*g*g
        delta=.01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
        if step%100==0:
            p=policy().astype(float);p/=p.sum(1,keepdims=True)
            gd=np.zeros_like(p);gd[ss]=-p[ss];gd[ss,aa]+=1
            if not tab:gd=f.T@gd
            records[-1]["adam_root_log_direction"]=float(np.sum(gd*delta))
            records[-1]["batch_wins"]=hit
        w+=delta
        if step%100==0:
            p=policy().astype(float);p/=p.sum(1,keepdims=True)
            records[-1]["actual_root_log_step"]=float(np.log(p[ss,aa]).sum()-records[-1]["root_log"])
    return dict(n=n,mode=mode,seed=seed,mult=mult,tab=tab,records=records,weights=w.tolist(),slots=STEPS*BATCH*horizon,seconds=time.monotonic()-begin)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--workers',type=int,default=1);args=ap.parse_args()
    jobs=[(n,mode,seed,mult,tab) for n in (5,6) for mode in ('root','uniform','uniform-switch') for seed in (42,43) for mult in (1,2) for tab in (False,True)]
    rows=[]
    with mp.Pool(args.workers) as pool:
        for row in pool.imap_unordered(train,jobs):
            rows.append(row);args.out.write_text(json.dumps(rows));print(row['n'],row['mode'],row['seed'],row['mult'],row['tab'],row['records'][-1]['root_curves'],flush=True)
