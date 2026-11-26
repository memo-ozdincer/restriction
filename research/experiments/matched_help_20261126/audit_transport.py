"""Recover completed, unchanged responses flagged solely for transport fallback."""
from run import *
def main():
    recovered=[]
    for p in sorted((ROOT/'rollouts').glob('*/*/*/*/metadata.json')):
        m=json.loads(p.read_text())
        if m['valid'] or m['cli_returncode']!=0 or m['tool_items']!=['error'] or not isinstance(m['answer'],dict): continue
        e=[json.loads(l) for l in (p.parent/'events.jsonl').read_text().splitlines()]
        errors=[x['item'] for x in e if x.get('item',{}).get('type')=='error']
        if not errors or not all(x.get('message','').startswith('Falling back from WebSockets to HTTPS transport.') for x in errors) or not any(x.get('type')=='turn.completed' for x in e): continue
        stage=m['stage']; kind='actor' if stage=='actor' else 'partner' if stage in ('diagnostic-request','diagnostic-partner','partner') else 'final'
        ans=m['answer']; assert all(isinstance(ans[k],str) for k in SCHEMAS[kind]); dump(p.parent/'metadata-original-audit.json',m)
        m['valid']=True; m['tool_items']=[]; m['transport_fallback_audit']=errors
        if kind=='final' or kind=='actor' and ans['action']=='proof':
            row=next(r for r in ROWS if r['id']==m['task']); m['verification']=verify(row['statement'],row['id'],ans['proof'] if kind=='final' else ans['message'],p.parent)
        dump(p,m); recovered.append(str(p.relative_to(ROOT)))
    dump(ROOT/'transport-audit.json',recovered); print('Recovered unchanged:',recovered)
if __name__=='__main__':main()
