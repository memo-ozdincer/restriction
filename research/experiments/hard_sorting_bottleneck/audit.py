"""Independent replay and analytic zero-reward baseline waiting-time audit."""
import json, math
from pathlib import Path
import numpy as np
from run import graph,exact_root

ROOT=Path(__file__).parent

def scalar_verify(n,gates,actions):
    for value in range(1<<n):
        row=[(value>>(n-1-i))&1 for i in range(n)]
        for a in actions:
            i,j=gates[a]
            row[i],row[j]=min(row[i],row[j]),max(row[i],row[j])
        if row!=sorted(row):return False
    return True

def audit():
    env=graph(8)
    trans,feat,target,depth,states,gates=env
    h=int(depth[0]);A=len(gates)
    paths=[0]*len(states);paths[target]=1
    for d in range(1,h+1):
        for i in np.flatnonzero(depth==d):
            paths[i]=sum(paths[j] for j in trans[i] if depth[j]==d-1)
    uniform=paths[0]/A**h
    initial=[]
    for seed in range(42,50):
        w=np.random.default_rng(seed).normal(0,.02,(feat.shape[1],A)).astype(np.float32)
        p=exact_root(w,env,h)
        initial.append(dict(seed=seed,p=p,mean_episodes_to_first=1/p,
                            probability_first_within_60000_updates=-math.expm1(60000*64*math.log1p(-p)),
                            probability_first_within_1000000_updates=-math.expm1(1000000*64*math.log1p(-p))))
    out=dict(optimal_root_sequences=paths[0],total_length_h_sequences=A**h,
             uniform_root_probability=uniform,initial=initial)
    if (ROOT/"results.json").exists():
        rows=json.loads((ROOT/"results.json").read_text());verified=0
        for row in rows:
            w=np.array(row["weights"],np.float32)
            assert math.isclose(exact_root(w,env,h),row["root_exact"],rel_tol=1e-12,abs_tol=1e-15)
            assert sum(x["count"] for x in row["paths"])==row["fresh_hits"]
            for x in row["paths"]:
                assert len(x["actions"])==h and scalar_verify(8,gates,x["actions"])
                verified+=x["count"]
            if row["radius"]==0 and row["records"][-1]["train_hits"]==0:
                original=np.random.default_rng(row["seed"]).normal(0,.02,w.shape).astype(np.float32)
                assert np.array_equal(w,original)
        out.update(runs=len(rows),independently_replayed_wins=verified)
    (ROOT/"audit.json").write_text(json.dumps(out,indent=2))
    print(out)

if __name__=="__main__":audit()
