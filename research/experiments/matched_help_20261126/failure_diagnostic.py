from run import *

def history(r,p,i):
    d=ROOT/'rollouts'/p/r['id']/str(i)/'actor'
    m=json.loads((d/'metadata.json').read_text())
    assert m['valid'] and m['answer']['action']=='proof' and not m['verification']['accepted']
    diagnostic=(d/'lean-output.txt').read_text() if (d/'lean-output.txt').exists() else m['verification']['reason']
    return 'Your previous proof attempt:\n'+m['answer']['message']+'\n\nLean verifier output:\n'+diagnostic+'\n\n'

def request(r,p,i):
    return call(r,p,i,'diagnostic-request',PAIRS[p][0],base(r)+history(r,p,i)+'Choose any question or message to send to a partner model that you think will help you solve the original theorem. You can ask for anything, including a full solution, or state your reasoning. Return your exact message in response.','partner')
def reply(r,p,i,q):
    return call(r,p,i,'diagnostic-partner',PAIRS[p][1],base(r)+'Another model working on this theorem sent the following message. Reply freely in response, including full proof if useful.\n\n'+q['answer']['response'],'partner')
def final(r,p,i,q,stage,other_q=None,h=None):
    prompt=base(r)+history(r,p,i)+'You sent this question to a partner model:\n'+q['answer']['response']+'\n\n'
    if h is not None: prompt+='Here is a conversation about the same theorem:\nQuestion:\n'+other_q['answer']['response']+'\nResponse:\n'+h['answer']['response']+'\n\n'
    else: prompt+='No partner response is available.\n\n'
    prompt+='Now complete the original theorem. You may abandon any previous reasoning or use any available information. Return the complete tactic body after := by in proof, without Markdown fences.'
    return call(r,p,i,'diagnostic-'+stage,PAIRS[p][0],prompt,'final')

def main():
    units=[(r,p,i) for p in PAIRS for r in ROWS for i in range(2)]
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        requests=list(ex.map(lambda x:request(*x),units)); qbank={(q['pair'],q['task'],q['trial']):q for q in requests if q['valid']}
        jobs=[(r,p,i,qbank[p,r['id'],i]) for r,p,i in units if (p,r['id'],i) in qbank]
        replies=list(ex.map(lambda x:reply(*x),jobs)); hbank={(h['pair'],h['task'],h['trial']):h for h in replies if h['valid']}
        finals=[]
        for r,p,i,q in jobs:
            k=(p,r['id'],i); other=(p,r['id'],1-i)
            finals.append((r,p,i,q,'control'))
            if k in hbank: finals.append((r,p,i,q,'matched',q,hbank[k]))
            if k in hbank and other in hbank: finals.append((r,p,i,q,'swapped',qbank[other],hbank[other]))
        list(ex.map(lambda x:final(*x),finals))
    dump(ROOT/'diagnostic-summary.json',[json.loads(p.read_text()) for p in sorted((ROOT/'rollouts').glob('*/*/*/diagnostic-*/metadata.json'))])
if __name__=='__main__':main()
