"""Rerun only normalized-PG groups after D-170 equal-objective guard."""
import json
import pathlib
import panel
import concurrent.futures as cf
import os

if __name__ == "__main__":
    # The original runner writes relative results/ in an isolated snapshot.
    root=pathlib.Path("results");root.mkdir(exist_ok=False)
    specs=[(k,a) for k,a in panel.specs() if "-pg-normalized-" in k]
    assert len(specs)==33
    (root/"registered_specs.json").write_text(json.dumps(specs,indent=2))
    completed=[];failed=[]
    with cf.ThreadPoolExecutor(max_workers=min(len(specs),int(os.environ.get("SLURM_CPUS_PER_TASK","2")))) as ex:
        fs={ex.submit(panel.run,s):s[0] for s in specs}
        for f in cf.as_completed(fs):
            try:
                r=f.result()
                assert r["counters"]["updates"]<=r["counters"]["nonconstant_score_groups"]
                completed.append(r);print(r["key"],r["train"]["successes"],flush=True)
            except Exception as e:
                failed.append({"key":fs[f],"error":repr(e)});print("FAILED",fs[f],repr(e),flush=True)
            tmp=root/"summary.tmp";tmp.write_text(json.dumps({"runs":completed,"failed":failed},indent=2));tmp.replace(root/"summary.json")
    if failed:raise SystemExit(1)
