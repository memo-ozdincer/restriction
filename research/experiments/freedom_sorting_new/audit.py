"""Independent scalar verifier for all recorded successful root paths."""
import collections
import json
from pathlib import Path

from train import N, GATES, H, graph, sample_starts
import numpy as np

HERE=Path(__file__).parent


def scalar_verify(sequence):
    if len(sequence)>H:
        return False
    for x in range(1<<N):
        row=[(x>>(N-1-i))&1 for i in range(N)]
        for a in sequence:
            i,j=GATES[a]
            row[i],row[j]=min(row[i],row[j]),max(row[i],row[j])
        if row!=sorted(row):
            return False
    return True


def summarize(runs):
    groups=collections.defaultdict(list)
    for r in runs:groups[tuple(r["mode"])].append(r)
    rows=[]
    for mode,items in groups.items():
        successes=[r["independent_root_hits"] for r in items]
        allpaths={}
        for r in items:
            n=0
            for path in r["successful_paths"]:
                assert scalar_verify(path["actions"])
                assert len(path["actions"])==H
                key=tuple(path["actions"])
                allpaths[key]=allpaths.get(key,0)+path["count"]
                n+=path["count"]
            assert n==r["independent_root_hits"]
            assert r["records"][-1]["train_action_slots"]==300*1536
        final=[r["records"][-1] for r in items]
        rows.append(dict(mode=mode,num_seeds=len(items),fresh_hits=sum(successes),
                         fresh_trials=512*len(items),per_seed_fresh=successes,
                         breakthrough_seeds=sum(x>=52 for x in successes),
                         paths=len(allpaths),
                         train_hits=sum(x["train_hits"] for x in final),
                         train_rollouts=sum(x["train_rollouts"] for x in final),
                         train_actions=sum(x["train_actions"] for x in final),
                         train_policy_calls=sum(x["train_policy_calls"] for x in final),
                         reset_actions=sum(x["reset_actions"] for x in final),
                         reset_rejected=sum(x["reset_rejected"] for x in final),
                         max_root_checkpoints=[max(c["root_hits"] for c in r["records"]) for r in items],
                         seconds=sum(r["seconds"] for r in items)))
    return rows


def extra_calibration():
    env=graph()
    trans,_,target,depth,states,equiv=env
    n=len(states);action_count=len(GATES)
    hit=np.eye(1,n,target).ravel()
    for _ in range(H):
        hit=hit[trans].mean(axis=1);hit[target]=1
    dists={}
    for maxwalk,mode in ((2,"tiny"),(4,"short"),(6,"radius6"),(8,"radius8"),(36,"wide")):
        x=np.eye(1,n,0).ravel();q=np.zeros(n)
        for _ in range(maxwalk):
            x=np.bincount(trans.ravel(),weights=np.repeat(x/action_count,action_count),minlength=n)
            q+=x/maxwalk
        q[target]=0;q/=q.sum()
        dists[mode]=q
    dists["mixed"]=(dists["short"]+dists["wide"])/2
    return {k:dict(success=float(q@hit),mean_depth=float(q@depth),
                       support=int((q>0).sum())) for k,q in dists.items()}


if __name__=="__main__":
    core=json.loads((HERE/"results.json").read_text())
    more=json.loads((HERE/"followup.json").read_text())
    result=dict(core=summarize(core["runs"]),followup=summarize(more),
                extra_calibration=extra_calibration())
    (HERE/"audit.json").write_text(json.dumps(result,indent=2))
    for group in ("core","followup"):
        print(group)
        for r in result[group]:
            print(r["mode"],r["fresh_hits"],"/",r["fresh_trials"],
                  "breakthrough",r["breakthrough_seeds"],"paths",r["paths"])
