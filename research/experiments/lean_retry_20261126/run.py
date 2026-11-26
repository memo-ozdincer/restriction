import concurrent.futures as cf, hashlib, json, pathlib, subprocess, sys, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parent
PREV=ROOT.parent/'mathematical_speculation_lean_20261126'
sys.path.insert(0,str(PREV))
from verify import verify, HEADER
MODELS={'ll':('gpt-6-luna','low'),'lm':('gpt-6-luna','medium'),'tl':('gpt-6.1-terra','low'),'tm':('gpt-6.1-terra','medium')}
ROWS=json.loads((PREV/'panel.json').read_text())[:4]
SCHEMA={'type':'object','properties':{'proof':{'type':'string'}},'required':['proof'],'additionalProperties':False}
def run(row,setting,arm,previous=None):
    out=ROOT/'rollouts'/setting/row['id']/arm
    if (out/'metadata.json').exists(): return json.loads((out/'metadata.json').read_text())
    out.mkdir(parents=True,exist_ok=True)
    prompt="Complete the exact Lean theorem below. Return only the tactic body after ':= by' in the proof field, without code fences. Do not use sorry, admit, new declarations, tools, files, or other agents. You may use any mathematical approach.\n"+HEADER+'\n'+row['statement']
    if previous is not None:
        p=out.parent/'first'; body=(p/'answer.json').read_text() if (p/'answer.json').exists() else '(no candidate)'; diag=(p/'lean-output.txt').read_text() if (p/'lean-output.txt').exists() else previous['verification']['reason']
        prompt+='\nYour previous attempt was rejected. You can revise or replace it freely. Previous response:\n'+body+'\nNative verifier output:\n'+diag
    (out/'prompt.txt').write_text(prompt); (out/'schema.json').write_text(json.dumps(SCHEMA))
    model,effort=MODELS[setting]; cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--color','never','--json','-m',model,'-c',f'model_reasoning_effort="{effort}"','--output-schema',str(out/'schema.json'),'--output-last-message',str(out/'answer.json'),'-']
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='lean-native-feedback-') as cwd,(out/'events.jsonl').open('w') as so,(out/'stderr.txt').open('w') as se:
        try: rc=subprocess.run(cmd,input=prompt,text=True,cwd=cwd,stdout=so,stderr=se,timeout=360).returncode
        except subprocess.TimeoutExpired: rc=124
    elapsed=time.monotonic()-start; events=[]
    for line in (out/'events.jsonl').read_text().splitlines():
        try: events.append(json.loads(line))
        except ValueError: pass
    tools=[e['item']['type'] for e in events if isinstance(e.get('item'),dict) and e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
    try: proof=json.loads((out/'answer.json').read_text())['proof']
    except Exception: proof=None
    valid=rc==0 and isinstance(proof,str) and not tools
    v=verify(row['statement'],row['id'],proof,out) if valid else {'accepted':False,'reason':'invalid_cli_or_tool_use'}
    m={'task':row['id'],'setting':setting,'arm':arm,'model':model,'effort':effort,'cli_returncode':rc,'valid':valid,'tool_items':tools,'generated_seconds':elapsed,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed'],'verification':v}
    (out/'metadata.json').write_text(json.dumps(m,indent=2)+'\n'); print(setting,row['id'],arm,v['accepted'],round(elapsed,1),flush=True); return m

def main():
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        first=list(ex.map(lambda p:run(*p,'first'),[(r,s) for s in MODELS for r in ROWS]))
        jobs=[(r,m['setting'],a,m if a=='feedback' else None) for m in first if not m['verification']['accepted'] and m['valid'] for r in ROWS if r['id']==m['task'] for a in ['feedback','restart']]
        list(ex.map(lambda p:run(*p),jobs))
    results=[json.loads(p.read_text()) for p in sorted((ROOT/'rollouts').glob('*/*/*/metadata.json'))]; (ROOT/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
