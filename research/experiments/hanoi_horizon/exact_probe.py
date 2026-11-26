import json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'hanoi_mechanism'))
from analyze import environment,reset_distributions,value_gradient,route
from run import BATCH,STEPS
def train(tab,seed):
    n=5; e=environment(n);t,l,f,root,goal,depth=e; H=31
    d=reset_distributions(e)['uniform'];initial=np.random.default_rng(seed).normal(0,.02,(3*n,6)).astype(np.float32)
    w=(f@initial if tab else initial).astype(float);m=np.zeros_like(w);v=np.zeros_like(w);rr=np.array(route(e,n));ss,aa=rr.T
    records=[]
    for step in range(STEPS+1):
        z=np.where(l,w if tab else f@w,-1e100);z-=z.max(1,keepdims=True);p=np.exp(z);p/=p.sum(1,keepdims=True)
        j,g=value_gradient(p,e,d,H,tab)
        if step%100==0:records.append(dict(step=step,uniform=j,log_root=float(np.log(p[ss,aa]).sum())))
        if step==STEPS:break
        g*= (BATCH-1)/BATCH
        m=.9*m+.1*g;v=.999*v+.001*g*g
        w+=.01*(m/(1-.9**(step+1)))/(np.sqrt(v/(1-.999**(step+1)))+1e-8)
    return dict(tab=tab,seed=seed,records=records,weights=w.tolist())
if __name__=='__main__':
    rows=[]
    for tab in (False,True):
        for seed in (42,43):
            r=train(tab,seed);rows.append(r);print(tab,seed,r['records'][0],r['records'][-1],flush=True)
    (HERE/'exact_probe.json').write_text(json.dumps(rows,indent=2))
