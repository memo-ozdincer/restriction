"""Run isolated Codex CLI math rollouts, preserving raw event logs."""
import argparse
import concurrent.futures
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parent
SCHEMA={
    "type":"object","properties":{
        "answer":{"type":"string"},
        "solution":{"type":"string"},
        "insight":{"type":"string"},
        "insight_justification":{"type":"string"}
    },"required":["answer","solution","insight","insight_justification"],"additionalProperties":False
}
BASE="""Solve the following math problem independently, with mathematical reasoning only. Do not use any tools, shell commands, files, code execution, web, external resources, or other agents. Give the exact answer as an integer or reduced fraction string, with concise but convincing mathematical derivation. Also state one concise, non-answer mathematical fact or relationship that is particularly useful in your reasoning (not the complete solution), and justify that fact separately. Return only JSON matching the schema.
Problem:
{question}
"""
def run_one(row,model,effort,arm,hint=None):
    out=ROOT/'rollouts'/arm/row['id']
    out.mkdir(parents=True,exist_ok=False)
    prompt=BASE.format(question=row['question'])
    if hint is not None:
        prompt+=f"Additional mathematical information (you may use or ignore it):\n{hint}\n"
    (out/'prompt.txt').write_text(prompt)
    (out/'schema.json').write_text(json.dumps(SCHEMA,indent=2))
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
         '--sandbox','read-only','--color','never','--json','-m',model,
         '-c',f'model_reasoning_effort="{effort}"','--output-schema',str(out/'schema.json'),
         '--output-last-message',str(out/'answer.json'),'-']
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='math-spec-isolated-') as cwd:
        with (out/'events.jsonl').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
            try:
                p=subprocess.run(cmd,input=prompt,text=True,cwd=cwd,stdout=stdout,stderr=stderr,timeout=360)
                code=p.returncode
            except subprocess.TimeoutExpired:
                code=124
    elapsed=time.monotonic()-start
    events=[]
    for l in (out/'events.jsonl').read_text().splitlines():
        try:events.append(json.loads(l))
        except json.JSONDecodeError:pass
    tool_items=[e['item']['type'] for e in events if isinstance(e.get('item'),dict) and
                e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
    answer=None;parse_error=None
    try:answer=json.loads((out/'answer.json').read_text())
    except Exception as e:parse_error=str(e)
    truth=json.loads((ROOT/'answers.json').read_text())[row['id']]
    valid=code==0 and answer is not None and not tool_items
    correct=False
    try:correct=valid and Fraction(answer['answer'].replace(',','').strip())==Fraction(truth)
    except Exception: pass
    info=dict(task=row['id'],arm=arm,model=model,effort=effort,returncode=code,elapsed_seconds=elapsed,
              tool_items=tool_items,valid=valid,correct=correct,parse_error=parse_error,
              usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'],
              prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),reference_answer=truth,
              cli_version=subprocess.check_output(['codex','--version'],text=True).strip(),
              command=cmd[:-1]+['<prompt via stdin>'])
    (out/'metadata.json').write_text(json.dumps(info,indent=2)+'\n')
    print(f"{arm}/{row['id']}: code={code} valid={valid} correct={correct} elapsed={elapsed:.1f}s",flush=True)
    return info


def main():
    p=argparse.ArgumentParser();p.add_argument('arm');p.add_argument('model');p.add_argument('effort')
    p.add_argument('--tasks',nargs='+');p.add_argument('--hints',type=Path);p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    panel=json.loads((ROOT/'panel.json').read_text())
    hints=json.loads(args.hints.read_text()) if args.hints else None
    if args.tasks:panel=[r for r in panel if r['id'] in args.tasks]
    if hints is not None:panel=[r for r in panel if r['id'] in hints]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        fut=[ex.submit(run_one,r,args.model,args.effort,args.arm,None if hints is None else hints[r['id']]) for r in panel]
        for f in concurrent.futures.as_completed(fut):f.result()

if __name__=='__main__':main()
