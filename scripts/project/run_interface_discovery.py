#!/usr/bin/env python3
"""Manually launch the frozen interface pilot inside its existing allocation."""
import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import subprocess
import sys
import time


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(8*1024**2), b""):
            h.update(data)
    return h.hexdigest()


def write(path, data):
    tmp = path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n")
    tmp.replace(path)


def records(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def analyze(run):
    groups = defaultdict(lambda: {"proposals": 0, "correct": 0, "parse_rejections": 0, "timeouts": 0,
                                  "unverified": 0, "generated_tokens": 0, "supplied_tokens": 0,
                                  "first_correct": None})
    physical = 0
    for path in sorted(run.glob("*-*.jsonl")):
        if "verified" in path.name or path.name.startswith("validation"):
            continue
        verdict_path = path.with_name(path.stem+"-verified.jsonl")
        verdicts = {r["id"]: r for r in records(verdict_path)} if verdict_path.exists() else {}
        for r in records(path):
            key = (r["model"], r["kind"], r["world"], r.get("target", ""), r["condition"])
            g = groups[key]
            g["proposals"] += 1
            g["generated_tokens"] += r["generated_tokens"]
            g["supplied_tokens"] += r["prompt_tokens"]
            v = verdicts.get(r["id"])
            if v is None:
                g["unverified"] += 1
                continue
            g["correct"] += bool(v["accepted"])
            g["parse_rejections"] += bool(v.get("parse_error"))
            g["timeouts"] += "TimeoutExpired" in str(v.get("system_errors", ""))
            physical += "lean_complete" in v
            if v["accepted"] and g["first_correct"] is None:
                g["first_correct"] = {"id": r["id"], "text": r["text"], "prompt": r["prompt"]}
    table = [{"model": k[0], "kind": k[1], "world": k[2], "target": k[3], "condition": k[4], **v}
             for k,v in sorted(groups.items())]
    strong = []
    artifacts_path = run / "selected-artifacts.json"
    if artifacts_path.exists():
        for artifact in json.loads(artifacts_path.read_text()):
            targets = [artifact["world"]+"_nonzero", artifact["world"]+"_bezout"]
            passed = True
            for target in targets:
                baseline = groups.get(("grpo", "consumer", artifact["world"], target, "bare"), {})
                assisted = groups.get(("grpo", "consumer", artifact["world"], target, artifact["id"]), {})
                irrelevant = groups.get(("grpo", "consumer", artifact["world"], target, "irrelevant"), {})
                passed &= (baseline.get("proposals") == 128 and baseline.get("correct") == 0 and
                    baseline.get("unverified") == 0 and baseline.get("timeouts") == 0 and
                    assisted.get("proposals") == 16 and assisted.get("correct",0) >= 4 and
                    assisted.get("unverified") == 0 and irrelevant.get("proposals") == 32 and
                    irrelevant.get("correct",999) <= 1 and irrelevant.get("unverified") == 0)
            if passed: strong.append(artifact["id"])
    summary = {"groups": table, "strong_artifacts": strong, "generated_proposals": sum(g["proposals"] for g in table),
               "model_verification_calls": physical, "scope": "Inference discovery only; no new model training."}
    write(run/"analysis.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--panel-sha256", required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--prior-workspace", type=Path)
    args = parser.parse_args()
    workspace, panel, bundle = args.workspace.resolve(), args.panel.resolve(), args.bundle.resolve()
    allocation = json.loads((workspace/"allocation.json").read_text())
    job = allocation["SLURM_JOB_ID"]
    if allocation["SLURM_JOB_ACCOUNT"] != "def-zhijing" or socket.gethostname() != allocation["node"]:
        raise RuntimeError("Wrong account or node")
    if "job_"+job not in Path("/proc/self/cgroup").read_text():
        raise RuntimeError("Not inside recorded allocation cgroup")
    info = subprocess.check_output(["scontrol","show","job",job,"-o"],text=True)
    if "JobState=RUNNING" not in info or "Account=def-zhijing" not in info:
        raise RuntimeError("Allocation is not running under requested account")
    end = next(x.split("=",1)[1] for x in info.split() if x.startswith("EndTime="))
    deadline = min(time.time()+3000, datetime.fromisoformat(end).timestamp()-120)
    if deadline-time.time() < 1800: raise RuntimeError("Less than 30 minutes remain; do not start")
    if digest(panel/"manifest.json") != args.panel_sha256: raise RuntimeError("Panel manifest changed")
    manifest = json.loads((panel/"manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if digest(panel/name) != expected: raise RuntimeError("Panel input changed: "+name)
    pilot = workspace/"pilot.py"
    if digest(pilot) != manifest["source_sha256"]: raise RuntimeError("Prepared pilot source changed")
    run = workspace/"experiment"
    run.mkdir(exist_ok=False)
    env = os.environ.copy()
    env.update(ELAN_HOME=str(bundle/"lean/elan"), OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", TOKENIZERS_PARALLELISM="false", VLLM_WORKER_MULTIPROC_METHOD="spawn",
               CUDA_VISIBLE_DEVICES=allocation["CUDA_VISIBLE_DEVICES"], PYTHONDONTWRITEBYTECODE="1")
    verifier = bundle/"verifier/DeepSeek-Prover-V1.5"
    lake = bundle/"lean/elan/bin/lake"
    model_paths = {"base":bundle/"models/base", "grpo":bundle/"models/c1-final"}
    started = time.time()
    status = {"state":"starting", "job_id":job, "started_unix":started, "deadline_unix":deadline,
              "panel_sha256":args.panel_sha256, "pilot_sha256":digest(pilot),
              "driver_sha256":digest(Path(__file__)), "source_commit":allocation["source_commit"],
              "initial_job":info, "automatic_training":False, "phases":[]}
    write(run/"status.json",status)
    if args.prior_workspace:
        prior=args.prior_workspace.resolve()/"experiment"
        previous=json.loads((prior/"status.json").read_text())
        prior_panel=bundle/"runs/interface-discovery-panel-20261118"
        for name in ("producer_inputs.json","worlds.json"):
            if digest(panel/name)!=digest(prior_panel/name):raise RuntimeError("Resume task input changed")
        amendment=json.loads((prior/"producer-recheck/amendment.json").read_text())
        if digest(prior/"selected-artifacts.json")!=amendment["corrected_selection_sha256"]:
            raise RuntimeError("Prior corrected selection changed")
        for label in ("base","grpo"):
            inp=prior/(label+"-producer.jsonl")
            if digest(inp)!=amendment["input_sha256"][inp.name]:raise RuntimeError("Producer outputs changed")
            shutil.copyfile(inp,run/inp.name)
            verified=prior/"producer-recheck"/(label+"-producer-verified.jsonl")
            if len(records(inp))!=32 or len(records(verified))!=32:raise RuntimeError("Incomplete producer data")
            shutil.copyfile(verified,run/verified.name)
        shutil.copyfile(prior/"selected-artifacts.json",run/"selected-artifacts.json")
        status.update(reused_producer_proposals=64,prior_workspace=str(args.prior_workspace),
                      prior_job_id=previous["job_id"])
        write(run/"resume-provenance.json",{"prior_status":previous,"producer_repair":amendment,
              "prior_model_identities_sha256":digest(prior/"model-identities.json"),
              "baseline_samples_reused":0,"producer_samples_reused":64})
        write(run/"status.json",status)

    def phase(name, command):
        remaining = deadline-time.time()
        if remaining < 90: raise TimeoutError("Bounded experiment budget exhausted")
        entry = {"name":name,"command":command,"started_unix":time.time()}
        status["state"] = "running"
        status["current_phase"] = name
        status["phases"].append(entry)
        write(run/"status.json",status)
        with (run/(name+".log")).open("x") as log:
            proc = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try: entry["returncode"] = proc.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGTERM)
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGKILL); proc.wait()
                raise TimeoutError("Phase exceeded experiment deadline: "+name)
            finally:
                # Clean up only descendants of this dedicated phase session.
                try: os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError: pass
                entry["ended_unix"] = time.time(); write(run/"status.json",status)
        if entry["returncode"]: raise RuntimeError("Phase failed: "+name)

    common = [sys.executable,"-u",str(pilot)]
    try:
        identities = {}
        for label, path in model_paths.items():
            identities[label] = {p.name:{"bytes":p.stat().st_size,"sha256":digest(p)} for p in sorted(path.iterdir())
                                 if p.suffix in (".safetensors",".json")}
        write(run/"model-identities.json",identities)
        if args.prior_workspace:
            if identities!=json.loads((args.prior_workspace/"experiment/model-identities.json").read_text()):
                raise RuntimeError("Model or tokenizer bytes changed since producer generation")
        write(run/"verifier-identity.json", {"source_sha256":digest(verifier/"prover/lean/verifier.py"),
              "lean_toolchain":(verifier/"mathlib4/lean-toolchain").read_text(),
              "lake_manifest_sha256":digest(verifier/"mathlib4/lake-manifest.json")})
        phase("validation",common+["validate","--panel",str(panel),"--verifier",str(verifier),"--lake",str(lake),
                                   "--output",str(run/"validation.jsonl")])
        for stage in (("bare","consumer") if args.prior_workspace else ("producer","bare","consumer")):
            for label,path in model_paths.items():
                name = label+"-"+stage
                output = run/(name+".jsonl")
                command=common+["generate","--phase",stage,"--panel",str(panel),"--model",str(path),
                    "--tokenizer",str(model_paths["base"]),"--model-label",label,"--output",str(output)]
                if stage=="consumer": command += ["--artifacts",str(run/"selected-artifacts.json")]
                phase(name+"-generate",command)
                phase(name+"-verify",common+["verify","--input",str(output),"--verifier",str(verifier),
                    "--lake",str(lake),"--output",str(run/(name+"-verified.jsonl"))])
            if stage=="producer":
                phase("select",common+["select","--run",str(run),"--output",str(run/"selected-artifacts.json")])
        status["state"]="complete"
    except Exception as error:
        status.update(state="incomplete",error=repr(error))
        raise
    finally:
        summary=analyze(run)
        status.update(ended_unix=time.time(),elapsed_seconds=time.time()-started,
                      generated_proposals=summary["generated_proposals"],strong_artifacts=summary["strong_artifacts"])
        write(run/"status.json",status)


if __name__=="__main__": main()
