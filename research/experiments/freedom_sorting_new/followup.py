"""Preregistered targeted followup for the short/long reset contrast."""
import json
from pathlib import Path
from train import train, graph, SEEDS

env=graph()
modes=[(src,12,False,sw) for src in ("tiny","radius6","radius8","mixed")
       for sw in (False,True)]
modes += [(src,24,False,sw) for src in ("equal","short") for sw in (False,True)]
out=Path(__file__).with_name("followup.json")
runs=[]
for mode in modes:
    for seed in SEEDS:
        run=train(mode,seed,env)
        runs.append(run)
        out.write_text(json.dumps(runs,indent=2))
        print(mode,seed,run["independent_root_hits"],flush=True)
