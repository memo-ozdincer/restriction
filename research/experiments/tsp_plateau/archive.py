"""Replay compact evidence in a reproducible result document."""
import json
import hashlib
from pathlib import Path
from screen import ROOT,verify,prompt
import subprocess,platform

def main():
    task=json.loads((ROOT/'instance.json').read_text())
    rows=[]
    prompts={}
    for model in ['gpt-6-luna','gpt-6.1-terra']:
        for state in task['states']:
            run=Path('/tmp')/f"tsp-plateau-{model}-{state['id']}-20261127"
            records=json.loads((run/'summary.json').read_text())
            assert len(records)==4
            for i,record in enumerate(records):
                out=run/str(i);query=(out/'prompt.txt').read_text();assert query==prompt(task,state)
                key=state['id'];prompts[key]=query
                record['sample']=i;record['prompt_sha256']=hashlib.sha256(query.encode()).hexdigest()
                events=[json.loads(x) for x in (out/'events.jsonl').read_text().splitlines()]
                record['usage']=[e['usage'] for e in events if e.get('type')=='turn.completed' and 'usage' in e]
                if record['valid']:
                    answer=json.loads((out/'answer.json').read_text())
                    replay=verify(task,state,answer)
                    assert all(record[k]==v for k,v in replay.items())
                    record['answer_sha256']=hashlib.sha256((out/'answer.json').read_bytes()).hexdigest()
                rows.append(record)
    result={'instance_sha256':hashlib.sha256((ROOT/'instance.json').read_bytes()).hexdigest(),
            'cli_version':subprocess.check_output(['codex','--version'],text=True).strip(),
            'platform':platform.platform(),'raw_log_prefix':'/tmp/tsp-plateau-{model}-{state}-20261127',
            'prompts':prompts,'rows':rows}
    (ROOT/'results.json').write_text(json.dumps(result,indent=2))
    for model in ['gpt-6-luna','gpt-6.1-terra']:
        for state in task['states']:
            group=[r for r in rows if r['model']==model and r['state']==state['id']]
            count=sum(r['reward'] for r in group);print(model,state['id'],count,len(group),0<count<len(group),[r.get('final_cost') for r in group])

if __name__=='__main__':main()
