"""Matched-bounded local optimization comparison on historical fresh proposals.

No model training; tests proposal distribution quality independent of
autonomous success. Same primitive candidate evaluation budget per start.
The sample is drawn uniformly from valid fresh suffix rows; previous
accepted elite prefix is excluded. This imports the shared local optimizer
rather than implementing a second subtly different search.
"""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import random
import time
import numpy as np
from audit import source_codes, COMMIT, URL, decode, adjacency, coefficients, measures, canonical


def prepare(cache, sample_path, draws=1000):
    path=cache/"transformer-output-decoded.txt"
    prior=cache/"search_output_10.txt"
    old=list(source_codes(prior))
    data=list(source_codes(path))
    assert len(old)==50000 and old==data[:len(old)]
    new=data[len(old):]
    valid=[(j,c) for j,c in enumerate(new)
           if c is not None and len(c)==58 and all(0<=x<60 for x in c)]
    sample=random.Random(202611271).sample(valid,draws)
    rng=random.Random(202611272)
    random_codes=[[rng.randrange(60) for _ in range(58)] for _ in range(draws)]
    rec={"source_commit":COMMIT,
         "source_files":{p.name:{"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                                 "url":URL+p.name} for p in (path,prior)},
         "source_fresh_rows":len(new),"source_valid_fresh_rows":len(valid),
         "selection_seed":202611271,"uniform_seed":202611272,"prefix_rows_excluded":len(old),
         "fresh_source_indices_zero_based_suffix":[i for i,_ in sample],
         "fresh":[c for _,c in sample],"uniform":random_codes}
    sample_path.write_text(json.dumps(rec,separators=(",",":"))+"\n")
    print("sample written",sample_path,"sha256",hashlib.sha256(sample_path.read_bytes()).hexdigest())


def one(job):
    from local_search import optimize
    from train import Evaluator
    group,i,code,cap,path_reset,max_swaps=job
    raw_code=np.asarray(code,dtype=np.int64)
    args=argparse.Namespace(n=60,family="independence",index=30,required=1,score="raw")
    # Report true initial score; this independent diagnostic evaluation is
    # counted separately, not part of search call budget.
    initial=Evaluator(args).evaluate(raw_code)
    reset=path_reset and len(set(code))==len(code)
    start=np.zeros(58,dtype=np.int64) if reset else raw_code
    ev=Evaluator(args)
    out=optimize(start,ev,np.random.default_rng(202611280+i),max_swaps=max_swaps,
                 strategy="cycle",order="random",budget=cap,stop_on_hit=False,ties="random")
    final=out["record"]
    return {"group":group,"row":i,"initial_score":initial[0],"initial_alpha":initial[4],
            "initial_hit":initial[1],"reset_path":reset,"final_score":final[0],
            "final_hit":final[1],"final_id":final[2],"final_alpha":final[4],
            "calls":out["calls"],"swaps":out["swaps"],"attempts":out["attempts"],
            "any_searched_hit":bool(ev.successes),"witnesses":ev.witnesses,
            "final_code":list(map(int,out["code"])) if final[1] else None}


def summarize(rows):
    out={}
    for group in ("fresh","uniform"):
        rr=[r for r in rows if r["group"]==group]
        out[group]={"N":len(rr),"calls":sum(r["calls"] for r in rr),
                    "initial_hits":sum(r["initial_hit"] for r in rr),
                    "final_hits":sum(r["final_hit"] for r in rr),
                    "any_hit_starts":sum(r["any_searched_hit"] for r in rr),
                    "path_resets":sum(r["reset_path"] for r in rr),
                    "actual_swaps":sum(r["swaps"] for r in rr),
                    "insertion_attempts":sum(r["attempts"] for r in rr),
                    "unique_final_trees":len({r["final_id"] for r in rr}),
                    "unique_final_hits":len({r["final_id"] for r in rr if r["final_hit"]}),
                    "initial_median_score":float(np.median([r["initial_score"] for r in rr],)),
                    "final_median_score":float(np.median([r["final_score"] for r in rr])),
                    "initial_alpha_hist":dict(Counter(r["initial_alpha"] for r in rr)),
                    "final_alpha_hist":dict(Counter(r["final_alpha"] for r in rr))}
    return out


def replay(rows):
    counts=Counter()
    unique=set()
    for row in rows:
        if row["final_hit"]:
            c,_=coefficients(adjacency(60,decode(row["final_code"])))
            assert measures(c,30)[0]==row["final_score"]>0
            counts["final_confirmed"]+=1
        for w in row["witnesses"]:
            a=adjacency(60,decode(w["code"]))
            c,_=coefficients(a)
            vs=[i for i in range(1,60) if measures(c,i)[0]>0]
            assert vs==w["violations"]
            assert {str(i):str(measures(c,i)[0]) for i in vs}==w["defects"]
            counts["witness_records_confirmed"]+=1
            unique.add(canonical(a))
    return {**counts,"unique_unlabeled_witness_records":len(unique)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cache",type=Path,default=Path("/tmp/tree_polynomial_patternboost_79ef336"))
    p.add_argument("--sample",type=Path,default=Path("/tmp/tree_polynomial_patternboost_79ef336/sample-1000.json"))
    p.add_argument("--prepare",action="store_true")
    p.add_argument("--limit",type=int,default=100)
    p.add_argument("--budget",type=int,default=500)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--max-swaps",type=int,default=10)
    p.add_argument("--path-reset",action="store_true")
    p.add_argument("--out",type=Path,default=Path(__file__).with_name("audit_local_search.json"))
    a=p.parse_args()
    if a.prepare:
        prepare(a.cache,a.sample)
        return
    t=time.monotonic()
    sample=json.loads(a.sample.read_text())
    assert 0<a.limit<=len(sample["fresh"])==len(sample["uniform"])
    jobs=[(group,i,code,a.budget,a.path_reset,a.max_swaps)
          for i in range(a.limit) for group in ("fresh","uniform")
          for code in (sample[group][i],)]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        rows=list(pool.map(one,jobs,chunksize=1))
    result={"sample_sha256":hashlib.sha256(a.sample.read_bytes()).hexdigest(),
            "source_files":sample["source_files"],"source_commit":sample["source_commit"],
            "limit":a.limit,"budget_per_start":a.budget,"max_swaps":a.max_swaps,"path_reset":a.path_reset,
            "source_fresh_indices_zero_based_suffix":sample["fresh_source_indices_zero_based_suffix"][:a.limit],
            "outside_search_diagnostic_calls":len(jobs),"summary":summarize(rows),
            "rows":rows,"independent_replay":replay(rows),"elapsed_seconds":time.monotonic()-t}
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result["summary"],indent=2),flush=True)


if __name__=="__main__":
    main()
