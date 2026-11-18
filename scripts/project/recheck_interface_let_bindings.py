#!/usr/bin/env python3
"""Recheck unchanged producer samples after the prospective parser bug amendment.

Refuses to replace selections once any consumer phase has started. Preserves
all original records and selected artifacts. No generation is performed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace",type=Path,required=True)
    p.add_argument("--bundle",type=Path,required=True)
    args=p.parse_args()
    run=args.workspace/"experiment"
    root=Path(__file__).resolve().parents[2]
    source=root/"scripts/project/interface_discovery_pilot.py"
    out=run/"producer-recheck"
    out.mkdir(exist_ok=False)
    shutil.copyfile(source,out/"pilot-corrected.py")
    env=os.environ.copy()
    env.update(ELAN_HOME=str(args.bundle/"lean/elan"),OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
    records={"reason":"Legitimate local let/have bindings contain :=; reject declarations, not assignment-token count.",
             "new_generation":False,"started_unix":time.time(),"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
             "verification_commands":[],"input_sha256":{}}
    for label in ("base","grpo"):
        inp=run/(label+"-producer.jsonl")
        shutil.copyfile(inp,out/inp.name)
        records["input_sha256"][inp.name]=hashlib.sha256(inp.read_bytes()).hexdigest()
        command=[sys.executable,str(out/"pilot-corrected.py"),"verify","--input",str(out/inp.name),
            "--output",str(out/(label+"-producer-verified.jsonl")),"--verifier",str(args.bundle/"verifier/DeepSeek-Prover-V1.5"),
            "--lake",str(args.bundle/"lean/elan/bin/lake")]
        records["verification_commands"].append(command)
        subprocess.run(command,env=env,check=True)
    subprocess.run([sys.executable,str(out/"pilot-corrected.py"),"select","--run",str(out),
                    "--output",str(out/"selected-artifacts.json")],check=True,env=env)
    status=json.loads((run/"status.json").read_text())
    if any("consumer" in x["name"] for x in status["phases"]):
        raise RuntimeError("Consumer already started: preserve recheck but do not replace its inputs")
    if status["state"] != "running":raise RuntimeError("Pilot is not running")
    original=run/"selected-artifacts.json"
    shutil.copyfile(original,out/"selected-artifacts-original.json")
    records["previous_selection_sha256"]=hashlib.sha256(original.read_bytes()).hexdigest()
    corrected=(out/"selected-artifacts.json").read_bytes()
    records["corrected_selection_sha256"]=hashlib.sha256(corrected).hexdigest()
    records["phase_at_replacement"]=status["current_phase"]
    records["ended_unix"]=time.time()
    (out/"amendment.json").write_text(json.dumps(records,indent=2)+"\n")
    temporary=run/"selected-artifacts-corrected.tmp"
    temporary.write_bytes(corrected)
    temporary.replace(original)
    print(json.dumps({"selected_artifacts":len(json.loads(corrected)),"phase":status["current_phase"]}),flush=True)


if __name__=="__main__":main()
