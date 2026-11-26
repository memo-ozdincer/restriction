"""Isolated real Lean proof generation and conditional idea/local-claim handoff."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
from verify import verify,ROOT,HEADER

SCHEMA={"type":"object","properties":{k:{"type":"string"} for k in
          ['idea','proof','insight_statement','insight_proof']},
        "required":['idea','proof','insight_statement','insight_proof'],"additionalProperties":False}
PROMPT="""Complete the exact Lean 4 theorem below. Use only your own mathematical reasoning and knowledge of Lean; do not run tools, commands, files, browsing, or consult other agents.
Return JSON with:
- idea: a concise mathematical strategy in plain language (one or two sentences, no Lean proof code).
- proof: Lean tactic body AFTER the given ':= by', without Markdown fences, no sorry/admit/axioms or new declarations. The exact imports are shown; do not change them.
- insight_statement and insight_proof: if your strategy actually uses one useful nontrivial root-context mathematical claim that is NOT the original target, give its Lean proposition (not a declaration) and its separate Lean tactic proof body in the original hypotheses. Otherwise return empty strings. Do not rely on h_help unless explicitly provided.
"""
def run(row,arm,model,effort,hint=None,local_fact=None):
    out=ROOT/'rollouts'/arm/row['id'];out.mkdir(parents=True,exist_ok=False)
    prompt=PROMPT+'\n'+HEADER+'\n'+row['statement']
    if hint is not None:
        prompt+='\nA separate model suggested only this informal mathematical idea. You may use or ignore it; provide the complete executable Lean proof yourself.\n'+hint+'\n'
    if local_fact is not None:
        prompt+='\nA Lean-verified local hypothesis named h_help is already available in the proof state, with type:\n'+local_fact[0]+'\nProvide the continuation after that hypothesis. You may use or ignore it.\n'
    (out/'prompt.txt').write_text(prompt);(out/'schema.json').write_text(json.dumps(SCHEMA,indent=2))
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--color','never','--json','-m',model,'-c',f'model_reasoning_effort="{effort}"','--output-schema',str(out/'schema.json'),'--output-last-message',str(out/'answer.json'),'-']
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='lean-spec-isolated-') as cwd:
        with (out/'events.jsonl').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
            try:code=subprocess.run(cmd,input=prompt,text=True,cwd=cwd,stdout=stdout,stderr=stderr,timeout=360).returncode
            except subprocess.TimeoutExpired:code=124
    elapsed=time.monotonic()-start
    events=[]
    for l in (out/'events.jsonl').read_text().splitlines():
        try:events.append(json.loads(l))
        except json.JSONDecodeError:pass
    tool_items=[e['item']['type'] for e in events if isinstance(e.get('item'),dict) and e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
    try:
        answer=json.loads((out/'answer.json').read_text())
    except Exception:answer=None
    valid=code==0 and answer is not None and not tool_items
    result=verify(row['statement'],row['id'],answer['proof'],out,local_fact) if valid else dict(accepted=False,reason='invalid_cli_or_tool_use')
    meta=dict(task=row['id'],arm=arm,model=model,effort=effort,cli_returncode=code,tool_items=tool_items,valid=valid,generated_seconds=elapsed,
              prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),usage=[e.get('usage') for e in events if e.get('type')=='turn.completed'],verification=result,
              cli_version=subprocess.check_output(['codex','--version'],text=True).strip())
    (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(arm,row['id'],result['accepted'],result['reason'],f'{elapsed:.1f}s',flush=True)
    return meta

def main():
    p=argparse.ArgumentParser();p.add_argument('arm');p.add_argument('model');p.add_argument('effort')
    p.add_argument('--ideas',type=Path);p.add_argument('--facts',type=Path);p.add_argument('--workers',type=int,default=4)
    a=p.parse_args()
    rows=json.loads((ROOT/'panel.json').read_text())
    ideas=json.loads(a.ideas.read_text()) if a.ideas else None
    facts=json.loads(a.facts.read_text()) if a.facts else None
    if ideas is not None:rows=[r for r in rows if r['id'] in ideas]
    if facts is not None:rows=[r for r in rows if r['id'] in facts]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        fut=[ex.submit(run,r,a.arm,a.model,a.effort,None if ideas is None else ideas[r['id']],None if facts is None else facts[r['id']]) for r in rows]
        for f in concurrent.futures.as_completed(fut):f.result()
if __name__=='__main__':main()
