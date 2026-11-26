"""Independent exact verifier and static candidate diagnostics."""
from collections import Counter
import json
from pathlib import Path
import numpy as np
from graph_coloring import make_graph, count_colorings, N, train

ROOT=Path(__file__).parent

def scalar_valid(labels,edges):
    return len(labels)==N and all(0<=c<3 for c in labels) and all(
        labels[i]!=labels[j] for i,j in edges)

def audit_file(path):
    data=json.loads(path.read_text())
    edges=data["edges"]
    totals={}
    for row in data["runs"]:
        for record in row["records"]:
            assert (record["certificate"] is not None)==(record["root_hits"]>0)
            if record["certificate"] is not None:
                assert scalar_valid(record["certificate"],edges)
        weights=np.array(row["final_logits"])[:,:3]
        probabilities=np.exp(weights-weights.max(axis=1,keepdims=True))
        probabilities/=probabilities.sum(axis=1,keepdims=True)
        rng=np.random.default_rng(20261127)
        labels=(rng.random((2048,N,1))>np.cumsum(probabilities,axis=1)[None]).sum(axis=2)
        hits=sum(scalar_valid(candidate,edges) for candidate in labels)
        key=row["mode"]
        totals.setdefault(key,[]).append(hits)
    return totals

def conflict_histogram(edges):
    histogram=np.zeros(len(edges)+1,dtype=np.int64)
    powers=3**np.arange(N)
    for start in range(0,3**N,100000):
        numbers=np.arange(start,min(start+100000,3**N))
        labels=(numbers[:,None]//powers[None])%3
        conflicts=(labels[:,edges[:,0]]==labels[:,edges[:,1]]).sum(axis=1)
        histogram+=np.bincount(conflicts,minlength=len(histogram))
    assert histogram.sum()==3**N
    return histogram

def main():
    edges=make_graph()
    histogram=conflict_histogram(edges)
    assert histogram[0]==count_colorings(edges,3)==6
    powers=np.arange(len(histogram))
    random_prob={str(keep):float(np.sum(histogram*(1-keep)**powers)/3**N)
                 for keep in (1.,.75,.55,.45,.35)}
    fixed_prob={}
    for seed in range(42,50):
        mask=np.random.default_rng(seed+1000000).random(len(edges))<.55
        fixed_prob[str(seed)]=count_colorings(edges[mask],3)/3**N
    outputs=dict(conflict_histogram=histogram.tolist(),random_mask_success=random_prob,
                 fixed_mask_success=fixed_prob,runs={})
    for name in ("coloring_results.json","coloring_followup.json","coloring_controls.json"):
        outputs["runs"][name]=audit_file(ROOT/name)
    # Exact reproduction of successful switched trajectory seed 42.
    archived=json.loads((ROOT/"coloring_followup.json").read_text())
    expected=next(r for r in archived["runs"] if r["mode"]=="mask35-switch" and r["seed"]==42)
    assert train(edges,"mask35-switch",42)==expected
    (ROOT/"audit.json").write_text(json.dumps(outputs,indent=2))
    print("exact uniform p by mask",random_prob)
    print("fixed mask initial p",fixed_prob)
    for name,runs in outputs["runs"].items():
        for mode,counts in runs.items():
            print(mode,counts,sum(c>=205 for c in counts),round(np.mean(counts)/2048,3))

if __name__=="__main__":
    main()
