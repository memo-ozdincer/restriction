"""Offline capacity and gradient diagnostics for existing Hanoi policies."""
from pathlib import Path
import sys
import json
import numpy as np
from scipy.optimize import linprog

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hanoi_bottleneck"))
from run import environment, ACTIONS, probabilities, exact_probability
from audit import witness


def route(env,n):
    transitions,legal,features,root,goal,depth=env
    state=root
    seq=[]
    for move in witness(n):
        a=ACTIONS.index(move);assert legal[state,a]
        seq.append((state,a))
        state=transitions[state,a]
    assert state==goal and len(seq)==2**n-1
    return seq


def capacity(env,n):
    transitions,legal,features,root,goal,depth=env
    M=[]
    for state,a in route(env,n):
        x=features[state].astype(float)
        for b in np.flatnonzero(legal[state]):
            if a==b:continue
            v=np.zeros((3*n,6));v[:,a]=x;v[:,b]=-x;M.append(v.ravel())
    A=np.array(M)
    result=linprog(np.zeros(3*n*6),A_ub=-A,b_ub=-np.ones(len(A)),
                   bounds=[(None,None)]*(3*n*6),method="highs")
    if result.success:
        # Verify the actual certificate, not just solver status.
        margins=A@result.x
        assert margins.min()>=1-1e-7
        W=result.x.reshape(3*n,6)
        p=probabilities(30*W,features,legal)
        root_p,_=exact_probability(p,env,2**n-1)
        assert root_p>.999999
        return dict(feasible=True,min_margin=float(margins.min()),
                    root_probability=root_p,certificate_weights=W.tolist())
    return dict(feasible=False,solver_status=int(result.status))


def reset_distributions(env):
    transitions,legal,features,root,goal,depth=env
    n=len(depth)
    def point(i):
        p=np.zeros(n);p[i]=1;return p
    random=legal/legal.sum(axis=1,keepdims=True)
    def walk(center):
        p=point(center);out=np.zeros(n)
        for _ in range(12):
            p=np.bincount(transitions.ravel(),weights=(p[:,None]*random).ravel(),minlength=n)
            out+=p/12
        out[goal]=0;return out/out.sum()
    u=np.full(n,1/n);u[goal]=0;u/=u.sum()
    return dict(root=point(root),uniform=u,goalwalk=walk(goal),rootwalk=walk(root))


def value_gradient(p,env,start,horizon,tabular):
    transitions,legal,features,root,goal,depth=env
    V=[np.zeros(len(depth))]
    V[0][goal]=1.
    for _ in range(horizon):
        v=(p*V[-1][transitions]).sum(axis=1);v[goal]=1.;V.append(v)
    d=start.copy();d[goal]=0
    score=np.zeros_like(p,dtype=float)
    for t in range(horizon,0,-1):
        q=V[t-1][transitions]
        score += d[:,None]*p*(q-V[t][:,None])
        d=np.bincount(transitions.ravel(),weights=(d[:,None]*p).ravel(),minlength=len(d))
        d[goal]=0
    return float(start@V[-1]),score if tabular else features.T@score


def diagnose(row,env,tabular,weights):
    transitions,legal,features,root,goal,depth=env
    logits=weights if tabular else features@weights
    logits=np.where(legal,logits,-1e100)
    logits-=logits.max(axis=1,keepdims=True)
    p=np.exp(logits);p/=p.sum(axis=1,keepdims=True)
    root_grad=np.zeros_like(p)
    logprob=0
    probs=[]
    for state,a in route(env,row["n"]):
        root_grad[state]-=p[state];root_grad[state,a]+=1
        logprob+=float(np.log(p[state,a]));probs.append(float(p[state,a]))
    if not tabular:root_grad=features.T@root_grad
    info={}
    for name,start in reset_distributions(env).items():
        j,g=value_gradient(p,env,start,2**row["n"]-1,tabular)
        dot=float(np.sum(g*root_grad));denom=np.linalg.norm(g)*np.linalg.norm(root_grad)
        info[name]=dict(success=j,gradient_norm=float(np.linalg.norm(g)),
                        root_logprob_directional_derivative=dot,
                        cosine=float(dot/denom) if denom else None)
    return dict(n=row["n"],mode=row["mode"],seed=row["seed"],tabular=tabular,
                root_log_probability=logprob,root_path_move_probabilities=probs,distributions=info)


def main():
    data={}
    for n in (5,6):
        env=environment(n)
        data[str(n)]=capacity(env,n)
    rows=[]
    for file,tabular in [("results.json",False),("tabular_results.json",True)]:
        original=json.loads((ROOT/"hanoi_bottleneck"/file).read_text())
        for row in original:
            env=environment(row["n"])
            record=diagnose(row,env,tabular,np.array(row["weights"],dtype=float))
            assert np.isclose(np.exp(record["root_log_probability"]),row["final_root_probability"],
                              rtol=1e-4,atol=1e-100)
            initial=np.random.default_rng(row["seed"]).normal(0,.02,(3*row["n"],6)).astype(np.float32)
            w=env[2]@initial if tabular else initial
            beginning=diagnose(row,env,tabular,w.astype(float))
            rows.append(dict(final=record,initial=beginning))
    output=dict(capacity=data,rows=rows)
    Path(__file__).with_name("results.json").write_text(json.dumps(output,indent=2))
    print("capacity",[(n,v["root_probability"]) for n,v in data.items()])
    for n in (5,6):
        for tabular in (False,True):
            for mode in ("root","uniform","goalwalk","uniform-switch","goalwalk-switch"):
                rr=[x for x in rows if x["final"]["n"]==n and x["final"]["tabular"]==tabular
                    and x["final"]["mode"]==mode]
                if not rr:continue
                d=mode.split("-")[0]
                print(n,tabular,mode,
                      "initial cos",np.mean([x["initial"]["distributions"][d]["cosine"] for x in rr]),
                      "final cos",np.mean([x["final"]["distributions"][d]["cosine"] for x in rr]),
                      "root log change",np.mean([x["final"]["root_log_probability"]-x["initial"]["root_log_probability"] for x in rr]))
if __name__=="__main__":main()
