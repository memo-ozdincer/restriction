#!/usr/bin/env python3
"""Track exact and one-line scaffold recovery of frozen near misses."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re


def lines(proof):
    return tuple(proof.splitlines(keepends=True))


def edits(body):
    for i, line in enumerate(body):
        if line.strip():
            yield i, body[:i]+body[i+1:]


def meaningful(line):
    s = line.strip()
    return bool(s and not s.startswith(('\x60\x60\x60', '--', '/-', '-/')) and s != 'by')


def head(line):
    m = re.match(r"\s*([A-Za-z_][\w'.]*)", line)
    return m.group(1) if m else ''


def category(old, new):
    if old is None:
        return 'missing_line'
    if new is None:
        return 'extra_line'
    if old.strip() == new.strip() or not (meaningful(old) and meaningful(new)):
        return 'format_or_comment'
    if (head(old) in ('induction', "induction'", 'cases', "cases'") or
        head(new) in ('induction', "induction'", 'cases', "cases'")):
        return 'scope_or_case_edit'
    if head(old) and head(old) == head(new):
        return 'same_head_argument_edit'
    if head(old) and head(new):
        return 'different_tactic_head'
    return 'other'


class Bank:
    def __init__(self, rows):
        self.good = defaultdict(list)
        self.bad = defaultdict(list)
        self.unresolved = defaultdict(list)
        for r in rows:
            target = self.good if r['correct'] else self.bad if r['failure_class']=='lean_rejected' else self.unresolved
            target[lines(r['proof'])].append(r['proposal_id'])
        self.index = defaultdict(set)
        for body in self.good:
            for i, scaffold in edits(body):
                self.index[(i, scaffold)].add(body)

    def siblings(self, b):
        found = set()
        for i, skeleton in edits(b):
            if skeleton in self.good:
                found.add((skeleton, i, skeleton, b[i], None))
            for a in self.index.get((i, skeleton), ()):
                if a != b:
                    found.add((a, i, skeleton, b[i], a[i]))
        for i in range(len(b)+1):
            for a in self.index.get((i,b), ()):
                found.add((a,i,b,None,a[i]))
        return sorted(found, key=repr)

    def families(self, skeletons, candidates):
        # A scaffold is an exact retained sequence at a specified edit position.
        return {b for b in candidates if any((i,s) in skeletons for i,s in edits(b))
                or any((i,b) in skeletons for i in range(len(b)+1))}


def status(good,bad):
    return 'both' if good and bad else 'corrected_only' if good else 'failure_only' if bad else 'unobserved'


def load(root):
    inventory = json.loads(Path('research/recovery/2026-11-18/evidence-inventory.json').read_text())['files']
    hashes = {Path(x['archive_path']).parts[-4]:x['sha256'] for x in inventory
              if '/eval128-' in x['archive_path'] and '/artifacts/proofs/' in x['archive_path']}
    result = {}
    for p in sorted(root.rglob('eval128-*/artifacts/proofs/*.jsonl')):
        name=p.parents[2].name
        assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==hashes[name]
        groups=defaultdict(list)
        with p.open() as f:
            for l in f:
                r=json.loads(l); groups[r['theorem_name']].append(r)
        assert len(groups)==467 and sum(map(len,groups.values()))==59904
        selected={}
        for k, rows in groups.items():
            assert len(rows)>=128
            rs=rows[:128]
            assert {r['candidate_index'] for r in rs}==set(range(128))
            keys={(r['theorem_statement'],r['context']) for r in rs}
            assert len(keys)==1
            selected[(k,*keys.pop())]=rs
        result[name.split('-')[1]]=selected
    assert set(result)=={'c0','c1','c2','c3'}
    assert all(set(x)==set(result['c0']) for x in result.values())
    return result


def analyze(data, half=False, discovery_n=None, observation_n=None):
    counts=defaultdict(Counter)
    records=[]
    for key, rows in sorted(data['c0'].items()):
        n = discovery_n if discovery_n is not None else (64 if half else len(rows))
        budget = observation_n if observation_n is not None else (64 if half else len(rows))
        base=Bank(rows[:n])
        observations={c:Bank(rs[key][:budget]) for c,rs in data.items() if c!='c0'}
        if n < len(rows):
            observations['c0_holdout']=Bank(rows[n:n+budget])
        # Index every observed body once per condition.
        indexes={}
        for c, obs in observations.items():
            ix={}
            for label, bodies in [('good',obs.good),('bad',obs.bad)]:
                m=defaultdict(set)
                for b in bodies:
                    for i,s in edits(b):
                        m[(i,s)].add(b)
                    for i in range(len(b)+1):
                        m[(i,b)].add(b)
                ix[label]=m
            indexes[c]=ix
        for b in sorted(base.bad):
            if b in base.good:
                continue
            siblings=base.siblings(b)
            if not siblings:
                continue
            a_set={a for a,*_ in siblings}
            cats={category(old,new) for a,i,s,old,new in siblings}
            cat=next(iter(cats)) if len(cats)==1 else 'ambiguous'
            skeletons={(i,s) for a,i,s,old,new in siblings if sum(map(meaningful,s))>=2}
            rec=dict(theorem=key[0],statement=key[1],failed=''.join(b),failed_ids=base.bad[b],
                     category=cat,strict=bool(skeletons),
                     siblings=[dict(proof=''.join(a),ids=base.good[a],edit_index=i,
                                    old=old,new=new,retained_lines=sum(map(meaningful,s)),
                                    category=category(old,new)) for a,i,s,old,new in siblings],
                     outcomes={})
            for c, obs in observations.items():
                g=a_set & obs.good.keys()
                f=b in obs.bad
                exact=status(g,f)
                out=dict(exact=exact,accepted_ids=[j for a in sorted(g) for j in obs.good[a]],
                         failed_ids=obs.bad.get(b,[]),unresolved_ids=obs.unresolved.get(b,[]))
                for stratum in ('all',cat,'strict' if skeletons else 'short'):
                    counts[(c,'exact',stratum)][exact]+=1
                if skeletons:
                    fg=set().union(*(indexes[c]['good'].get(s,set()) for s in skeletons))
                    fb=set().union(*(indexes[c]['bad'].get(s,set()) for s in skeletons))
                    fam=status(fg,fb)
                    out.update(family=fam,family_correct_bodies=len(fg),family_failed_bodies=len(fb),
                               family_accepted_ids=[j for a in sorted(fg) for j in obs.good[a]],
                               family_rejected_ids=[j for a in sorted(fb) for j in obs.bad[a]])
                    for stratum in ('strict',cat):
                        counts[(c,'family',stratum)][fam]+=1
                rec['outcomes'][c]=out
            records.append(rec)
    return dict(records=records,counts={'/'.join(k):dict(v) for k,v in sorted(counts.items())})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args()
    data=load(args.root)
    result={'full':analyze(data,False),'split':analyze(data,True)}
    with args.output.open('x') as f: json.dump(result,f,ensure_ascii=False,indent=2)
    for k,v in result.items():
        print(k,len(v['records']))
        for x,y in v['counts'].items():
            if x.endswith(('/all','/strict')): print(x,y)
