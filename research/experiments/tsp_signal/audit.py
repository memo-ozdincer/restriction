"""Exact action probabilities and independent optimum check for the observed diagnostic."""
from itertools import permutations
from collections import defaultdict
import json
import math
from experiment import ROOT,N,D,MOVES,HORIZON,GROUP,cost,move,delta,exact_optimum


def exact_policy_event(start,optimum):
    mass = {start: 1.0}
    # The same fixed horizon as the local stochastic screen.
    for step in range(HORIZON):
        result = defaultdict(float)
        for state,p in mass.items():
            changes = [delta(state,a) for a in MOVES]
            smallest = min(changes)
            tau = .03*cost(state)
            w = [math.exp(-(v-smallest)/tau) for v in changes]
            total = sum(w)
            for action,weight in zip(MOVES,w):
                s = move(state,action)
                result[s] += p*weight/total
        mass = result
    assert abs(sum(mass.values())-1)<1e-8
    p = sum(m for state,m in mass.items() if cost(state)==optimum)
    return p


def brute_optimum():
    # Independent direct scalar evaluation, start/end at city zero.
    return min(D[0][p[0]]+sum(D[a][b] for a,b in zip(p,p[1:]))+D[p[-1]][0]
               for p in permutations(range(1,N)))


def main():
    data=json.loads((ROOT/"local_results.json").read_text())
    optimum=data["optimum"]
    assert optimum==exact_optimum()==brute_optimum()
    records=[]
    for trace in data["traces"]:
        if trace["costs"][-1]==optimum: continue
        for kind,tour in [("mid",trace["tour_states"][(len(trace["tour_states"])-1)//2]),
                          ("plateau",trace["tour_states"][-1])]:
            state=tuple(tour)
            for action in MOVES:
                assert cost(move(state,action))-cost(state)==delta(state,action)
            p=exact_policy_event(state,optimum)
            records.append(dict(trial=trace["trial"],variant=kind,reference=cost(state),
                                improving_one_step=sum(delta(state,a)<0 for a in MOVES),
                                terminal_probability=p,
                                expected_mixed_groups=1-p**GROUP-(1-p)**GROUP))
    (ROOT/"exact_audit.json").write_text(json.dumps(dict(optimum=optimum,records=records),indent=2))
    for kind in ("mid","plateau"):
        rows=[r for r in records if r["variant"]==kind]
        print(kind,"exact average p",sum(r["terminal_probability"] for r in rows)/len(rows),
              "exact mean mixed",sum(r["expected_mixed_groups"] for r in rows)/len(rows))
    print("optimum independently verified via 9! permutations",optimum)

if __name__=="__main__":
    main()
