"""Follow-up: local completeness vs single deletion, and learned vs uniform starts."""
import concurrent.futures as cf
import gzip
import itertools
import json
import os
import pathlib
import subprocess
import sys
from panel import TASKS

def specs():
    tasks = TASKS + [("i60-30", "independence", 60, 30, 1)]
    for name, fam, n, index, required in tasks:
        # Domination evaluator is materially slower; matched budget within task.
        budget=524288 if fam=="domination" else 1048576
        for score,strategy,starts,seed in itertools.product(
            ["raw","normalized"],["cycle","single"],["uniform","cem"],[42,43]):
            key=f"{name}-{score}-{strategy}-{starts}-{seed}"
            args=["--n",str(n),"--family",fam,"--required",str(required),
                  "--score",score,"--strategy",strategy,"--starts",starts,
                  "--seed",str(seed),"--queries",str(budget),"--batch","64",
                  "--max-swaps","10","--per-start-queries","500",
                  "--eval-batch","256","--eval-every","50"]
            if index is not None:args+=["--index",str(index)]
            yield key,args,budget

def run(spec):
    key,args,budget=spec
    root=pathlib.Path("cycle_results"); path=root/(key+".json")
    with (root/(key+".log")).open("w") as log:
        subprocess.run([sys.executable,"local_search.py",*args,"--output",str(path)],
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    d=json.loads(path.read_text()); assert d["train"]["calls"]==budget
    with gzip.open(str(path)+".gz","wt",compresslevel=6) as f:json.dump(d,f,separators=(",",":"))
    path.unlink()
    return {"key":key,"config":d["config"],"train":{k:v for k,v in d["train"].items() if k!="witnesses"},
            "search":d["search"],"final":d["evaluation"]["checkpoints"][-1],
            "elapsed":d["elapsed_seconds"],"queries_per_second":d["queries_per_second"]}

if __name__=="__main__":
    root=pathlib.Path("cycle_results");root.mkdir(exist_ok=False)
    p=list(specs()); (root/"registered_specs.json").write_text(json.dumps(p,indent=2))
    runs=[];failed=[]
    with cf.ThreadPoolExecutor(max_workers=min(len(p),int(os.environ.get("SLURM_CPUS_PER_TASK","2")))) as ex:
        futures={ex.submit(run,s):s[0] for s in p}
        for f in cf.as_completed(futures):
            key=futures[f]
            try:
                r=f.result();runs.append(r);print(key,r["train"]["successes"],r["final"]["successes"],flush=True)
            except Exception as e:
                failed.append({"key":key,"error":repr(e)});print("FAILED",key,repr(e),flush=True)
            tmp=root/"summary.tmp";tmp.write_text(json.dumps({"runs":runs,"failed":failed},indent=2));tmp.replace(root/"summary.json")
    if failed:sys.exit(1)
