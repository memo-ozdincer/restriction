"""Offline global-policy feasibility and saved-policy hitting curves."""
import json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'hanoi_mechanism'))
from analyze import environment,reset_distributions,capacity,route

def global_capacity(n):
    t,l,f,root,goal,d=environment(n)
    good=l&(d[t]<d[:,None])
    assert np.all(good.sum(1)[np.arange(len(d))!=goal]==1)
    M=[]
    for s in range(len(d)):
        if s==goal:continue
        a=np.flatnonzero(good[s])[0]
        for b in np.flatnonzero(l[s]&~good[s]):
            v=np.zeros((f.shape[1],6));v[:,a]=f[s];v[:,b]=-f[s];M.append(v.ravel())
    A=np.array(M)
    result=linprog(np.zeros(A.shape[1]),A_ub=-A,b_ub=-np.ones(len(A)),bounds=[(None,None)]*A.shape[1],method='highs')
    assert result.status in (0,2)
    return dict(n=n,status=result.status,feasible=result.success,inequalities=len(A))

def evaluate(n,w,tab):
    env=environment(n);t,l,f,root,goal,d=env
    z=np.where(l,w if tab else f@w,-1e100);z-=z.max(1,keepdims=True);p=np.exp(z);p/=p.sum(1,keepdims=True)
    H=2**n-1;hit=np.zeros(len(d));hit[goal]=1;curves={}
    distributions=reset_distributions(env)
    for j in range(1,16*H+1):
        hit=(hit[t]*p).sum(1);hit[goal]=1
        if j in (H,2*H,4*H,8*H,10*H,16*H):
            curves[str(j//H)]=float(hit[root])
        if j==H:reset={s:float(x@hit) for s,x in distributions.items()}
    return dict(curves=curves,reset_success_at_H=reset)

if __name__=='__main__':
    caps=[global_capacity(n) for n in range(2,7)]
    certs={str(n):evaluate(n,30*np.array(capacity(environment(n),n)['certificate_weights']),False) for n in (5,6)}
    rows=[]
    for name,tab in [('results.json',False),('tabular_results.json',True)]:
        for r in json.loads((HERE.parent/'hanoi_bottleneck'/name).read_text()):
            ev=evaluate(r['n'],np.array(r['weights']),tab)
            assert np.isclose(ev['curves']['1'],r['final_root_probability'],rtol=1e-4,atol=1e-100)
            rows.append(dict(n=r['n'],mode=r['mode'],seed=r['seed'],tab=tab,**ev))
    (HERE/'offline_audit.json').write_text(json.dumps(dict(global_capacity=caps,root_certificates=certs,rows=rows),indent=2))
    print(caps);print(certs)
