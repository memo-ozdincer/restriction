"""Frozen pilot: one instance, three states, terminal verification."""
import argparse, json, random, subprocess, tempfile, time
from pathlib import Path
from environment import find_instance,cost,moves,apply
ROOT=Path(__file__).parent
SCHEMA={"type":"object","additionalProperties":False,"properties":{"actions":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{"i":{"type":"integer"},"j":{"type":"integer"}},"required":["i","j"]}}},"required":["actions"]}
HORIZON=3

def audit(matrix,tour,threshold):
    counts=[]; frontier=[tour]
    for _ in range(HORIZON):
        frontier=[apply(t,m) for t in frontier for m in moves(len(tour))]
        counts.append(sum(cost(matrix,t)<=threshold for t in frontier))
    return counts

def build():
    task=find_instance(); root=tuple(task["plateau"]); task['plateau_cost']=cost(task['matrix'],root)
    kick_moves=random.Random(42).sample(moves(len(root)),2)
    states=[('plateau',root,None), *[(f'kick{i}',apply(root,m),m) for i,m in enumerate(kick_moves)]]
    task['states']=[dict(id=name,tour=t,kick=m,cost=cost(task['matrix'],t),successful_sequences_by_length=audit(task['matrix'],t,task['threshold'])) for name,t,m in states]
    return task

def prompt(task,state):
    public={k:task[k] for k in ('matrix','threshold')}
    public.update(current_tour=state['tour'],max_actions=HORIZON)
    return ('Solve this symmetric traveling salesman local-search task. Distance matrix rows and columns are city IDs 0 through 10. A tour visits all cities exactly once and returns to its first city. The tour is anchored at position 0 (city 0). An action {i,j} reverses positions i through j inclusive in the CURRENT tour, using zero-based positions, with 1<=i<j<=10 and (i,j)!=(1,10). Apply up to three such actions. Intermediate lengths may increase. Win only if final tour length is at most threshold. Return only JSON actions in execution order. Use no tools.\n'+json.dumps(public))

def verify(task,state,answer):
    tour=tuple(state['tour']); actions=answer['actions']; lengths=[cost(task['matrix'],tour)]
    for a in actions:
        tour=apply(tour,(a['i'],a['j'])); lengths.append(cost(task['matrix'],tour))
    return dict(valid=True,actions=len(actions),lengths=lengths,final_cost=lengths[-1],reward=int(len(actions)<=HORIZON and lengths[-1]<=task['threshold']))

def run(model,state,task,out):
    out.mkdir(parents=True,exist_ok=False); query=prompt(task,state); (out/'prompt.txt').write_text(query); (out/'schema.json').write_text(json.dumps(SCHEMA))
    command=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--color','never','--json','-m',model,'-c','model_reasoning_effort="low"','--output-schema',str(out/'schema.json'),'--output-last-message',str(out/'answer.json'),'-']
    start=time.monotonic()
    with tempfile.TemporaryDirectory() as cwd:
        with (out/'events.jsonl').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
            try:rc=subprocess.run(command,input=query,text=True,cwd=cwd,stdout=stdout,stderr=stderr,timeout=180).returncode
            except subprocess.TimeoutExpired: rc=124
    row=dict(state=state['id'],model=model,returncode=rc,seconds=time.monotonic()-start)
    try:
        events=[json.loads(line) for line in (out/'events.jsonl').read_text().splitlines()]
        if rc or any(e.get('item',{}).get('type') not in (None,'agent_message','reasoning','plan','todo_list') for e in events):raise ValueError('failed CLI or tool use')
        answer=json.loads((out/'answer.json').read_text());row.update(verify(task,state,answer));row['response']=answer
    except (ValueError,TypeError,OSError,KeyError) as exc: row.update(valid=False,reward=0,error=str(exc))
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--state',choices=['plateau','kick0','kick1'],required=True);p.add_argument('--samples',type=int,default=4);a=p.parse_args();root=a.out.resolve();root.mkdir(parents=True,exist_ok=False)
    task=json.loads((ROOT/'instance.json').read_text());state=next(s for s in task['states'] if s['id']==a.state);rows=[]
    for i in range(a.samples):
        row=run(a.model,state,task,root/str(i));rows.append(row);(root/'summary.json').write_text(json.dumps(rows,indent=2));print(row,flush=True)

if __name__=='__main__':main()
