"""Paired, terminal-only REINFORCE pilot (no oracle observations or labels)."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from environment import make_environment, tensor_neighbors, TERMS, board_tiles, DIRECTIONS, reverse_distances

MODES = {
    "tensor": ("ordinary", "extra", "extra-switch"),
    "sokoban": ("ordinary", "solvable", "solvable-switch", "legal", "legal-switch"),
    "sokoban-medium": ("ordinary", "legal-after-prefix", "legal-after-prefix-switch"),
}


def schedule(mode, step, total):
    if mode.startswith("legal-after-prefix"):
        if step < int(total*.3):
            return "ordinary"
        if mode.endswith("-switch") and step >= int(total*.6):
            return "ordinary"
        return "legal"
    if mode.endswith("-switch"):
        return mode.split("-")[0] if step < int(total*.3) else "ordinary"
    return mode


def starts_for(env, mode, rng, groups, group_size):
    if mode == "ordinary" or env.name == "tensor":
        starts = np.full(groups, env.root, dtype=np.int32)
    else:
        available = ~env.terminal
        if mode == "solvable":
            available &= env.distances >= 0
        starts = rng.choice(np.flatnonzero(available), size=groups).astype(np.int32)
    return np.repeat(starts, group_size)


def transition_table(env, mode):
    trans = env.transitions
    if env.name == "tensor" and mode == "ordinary":
        # Same native moves, restrict intermediate rank to four.
        safe = np.maximum(trans, 0)
        trans = np.where((trans >= 0) & (env.ranks[safe] <= 4), trans, -1)
        dead = (trans < 0).all(axis=1)
        trans[dead, 0] = np.flatnonzero(dead)
    return trans


def initial_weights(env, rng, hidden=24):
    d = env.features.shape[1]
    output = d if env.name == "tensor" else env.transitions.shape[1]
    return {
        "W1": rng.normal(0, .10, (d, hidden)).astype(np.float32),
        "b1": np.zeros(hidden, dtype=np.float32),
        "W2": rng.normal(0, .10, (hidden, output)).astype(np.float32),
        "b2": np.zeros(output, dtype=np.float32),
    }


def forward(env, states, trans, weights):
    x = env.features[states]
    h = np.tanh(x @ weights["W1"] + weights["b1"])
    q = h @ weights["W2"] + weights["b2"]
    next_ids = trans[states]
    if env.name == "tensor":
        candidates = env.features[np.maximum(next_ids,0)]
        logits = np.einsum("bd,bad->ba", q, candidates, optimize=False)
    else:
        candidates = None
        logits = q
    logits = np.where(next_ids >= 0, logits, -1e30)
    logits -= logits.max(axis=1, keepdims=True)
    p = np.exp(logits)
    p /= p.sum(axis=1, keepdims=True)
    return x, h, candidates, p, next_ids


def rollout(env, weights, mode, starts, group_size, rng, gradient=False, replay=False):
    grouped_starts = starts.reshape(-1, group_size)
    assert np.all(grouped_starts == grouped_starts[:, :1])
    trans = transition_table(env, mode)
    states = starts.copy()
    alive = ~env.terminal[states]
    history = []
    active_steps = 0
    words = [[] for _ in states] if replay else None
    original = starts.copy()
    for _ in range(env.horizon):
        x,h,candidates,p,next_ids = forward(env,states,trans,weights)
        threshold = rng.random(len(states))
        # Avoid floating roundoff selecting a padded last column.
        cdf = np.cumsum(p, axis=1)
        choice = np.minimum((threshold[:,None] >= cdf).sum(axis=1), p.shape[1]-1)
        legal = next_ids[np.arange(len(states)),choice]>=0
        if not legal.all():
            last_legal = np.where(next_ids >= 0, np.arange(p.shape[1]), -1).max(axis=1)
            choice = np.where(legal, choice, last_legal)
        if gradient:
            history.append((x,h,candidates,p,choice,alive.copy()))
        if replay:
            for row in np.flatnonzero(alive):
                value = int(next_ids[row, choice[row]]) if env.name == "tensor" else int(choice[row])
                words[row].append(value)
        active_steps += int(alive.sum())
        states = np.where(alive, next_ids[np.arange(len(states)), choice], states)
        alive &= ~env.terminal[states]
    rewards = (~alive).astype(np.float32)
    groups = rewards.reshape(-1,group_size)
    mixed = int(((groups.min(axis=1)==0)&(groups.max(axis=1)==1)).sum())
    stats = dict(hits=int(rewards.sum()), mixed=mixed,
                 groups=len(groups), active_steps=active_steps,
                 slots=len(states)*env.horizon, episodes=len(states))
    if replay:
        checked = [verify_word(env, int(start), mode, word, int(end))
                   for start, word, end in zip(original, words, states)]
        assert np.array_equal(checked, rewards.astype(bool))
        stats["independent_replay_hits"] = sum(checked)
        stats["witness"] = next((word for word, ok in zip(words, checked) if ok), None)
    if not gradient:
        return stats
    advantage = (groups - groups.mean(axis=1, keepdims=True)).reshape(-1)
    grads = {k: np.zeros_like(v) for k,v in weights.items()}
    for x,h,candidates,p,choice,active in history:
        score = -p
        score[np.arange(len(states)),choice] += 1
        score *= (advantage*active/len(states))[:,None]
        dq = np.einsum("ba,bad->bd", score,candidates,optimize=False) if candidates is not None else score
        grads["W2"] += h.T@dq
        grads["b2"] += dq.sum(axis=0)
        dh = (dq@weights["W2"].T)*(1-h*h)
        grads["W1"] += x.T@dh
        grads["b1"] += dh.sum(axis=0)
    return stats,grads



def verify_word(env, start, mode, word, end):
    """Scalar replay, checking terminal semantics independently of terminal array."""
    if env.name == "tensor":
        state=env.states[start]
        cap=4 if mode=="ordinary" else 5
        for dest in word:
            nxt=env.states[dest]
            assert nxt in tensor_neighbors(state,cap) or (nxt==state and not tensor_neighbors(state,cap))
            state=nxt
            # Independent full coordinate expansion for every intermediate state.
            entries=[0]*8
            for idx in state:
                a,b,c=TERMS[idx]
                for i in range(2):
                    for j in range(2):
                        for k in range(2):
                            entries[4*i+2*j+k]^=((a>>i)&(b>>j)&(c>>k)&1)
            assert sum(v<<i for i,v in enumerate(entries))==env.metadata["target"]
        assert state==env.states[end]
        return len(state)<=env.metadata["min_rank"]
    tiles,ids,goals=board_tiles()
    boxes={tiles[i] for i in env.states[start][:2]}
    player=tiles[env.states[start][-1]]
    for action in word:
        delta=DIRECTIONS[action]
        cell=tuple(a+b for a,b in zip(player,delta))
        if cell not in ids:
            continue
        if cell in boxes:
            beyond=tuple(a+b for a,b in zip(cell,delta))
            if beyond not in ids or beyond in boxes:
                continue
            boxes.remove(cell)
            boxes.add(beyond)
        player=cell
    assert (*sorted(ids[b] for b in boxes),ids[player])==env.states[end]
    return boxes=={tiles[g] for g in goals}


def exact_hits(env, mode, weights=None):
    """Offline finite-horizon success probabilities; never used by training."""
    trans=transition_table(env,mode)
    states=np.arange(len(env.states))
    if weights is None:
        valid=(trans>=0)
        p=valid/valid.sum(axis=1,keepdims=True)
    else:
        # Evaluate in float64 to reduce accumulated numerical error.
        x=env.features.astype(np.float64)
        w={k:v.astype(np.float64) for k,v in weights.items()}
        h=np.tanh(x@w["W1"]+w["b1"])
        q=h@w["W2"]+w["b2"]
        z=np.einsum("bd,bad->ba",q,x[np.maximum(trans,0)],optimize=False) if env.name=="tensor" else q
        z=np.where(trans>=0,z,-np.inf)
        p=np.exp(z-z.max(axis=1,keepdims=True))
        p/=p.sum(axis=1,keepdims=True)
    hit=env.terminal.astype(np.float64)
    for _ in range(env.horizon):
        hit=(p*hit[np.maximum(trans,0)]).sum(axis=1)
        hit[env.terminal]=1
    return hit


def make_domain(domain):
    if domain != "sokoban-medium":
        return make_environment(domain)
    # Fixed before training: choose the first canonical configuration in a
    # moderate uniform-policy hit-probability band, not a trained-policy winner.
    env = make_environment("sokoban")
    hit = exact_hits(env, "ordinary")
    low, high = .002, .01
    eligible = np.flatnonzero((hit >= low) & (hit <= high) & ~env.terminal)
    if not len(eligible):
        raise RuntimeError("no medium root satisfies the registered probability band")
    env.root = int(eligible[0])
    env.metadata.update(root_state=env.states[env.root], root_distance=int(env.distances[env.root]),
                        root_selection="first canonical nonterminal state in uniform success band",
                        root_probability_band=[low, high], root_uniform_probability=float(hit[env.root]),
                        eligible_medium_roots=len(eligible))
    return env


def geometry(env):
    result=dict(env.metadata,horizon=env.horizon,
                distance_histogram={int(k):int(v) for k,v in zip(*np.unique(env.distances,return_counts=True))})
    for mode in (("ordinary","extra") if env.name=="tensor" else ("ordinary","solvable","legal")):
        hit=exact_hits(env,mode)
        allowed=(~env.terminal) if mode=="legal" else (~env.terminal)&(env.distances>=0)
        trans=transition_table(env,mode)
        seen={env.root}
        frontier={env.root}
        while frontier:
            nxt={int(j) for i in frontier if not env.terminal[i] for j in trans[i] if j>=0}-seen
            seen|=nxt
            frontier=nxt
        mode_distances=reverse_distances([[int(j) for j in row if j>=0] for row in trans],
                                         np.flatnonzero(env.terminal).tolist())
        root_p=float(hit[env.root])
        result[mode]=dict(random_root=root_p,random_nonterminal_mean=float(hit[allowed].mean()),
                          root_reachable=len(seen),root_reachable_dead_ends=sum(bool(mode_distances[i]<0) for i in seen),
                          root_reachable_terminal=sum(bool(env.terminal[i]) for i in seen),
                          random_root_group_mixed_probability=1-root_p**8-(1-root_p)**8,
                          random_group_mixed_probability=float(np.mean(
                              1-hit[allowed]**8-(1-hit[allowed])**8)))
    if env.name=="sokoban":
        for label,allowed in (("solvable",(env.distances>0)),("legal",~env.terminal)):
            result[label]["reset_distance_histogram"]={int(k):int(v) for k,v in zip(*np.unique(env.distances[allowed],return_counts=True))}
            result[label]["reset_mean_hit"] = float(exact_hits(env,"ordinary")[allowed].mean())
    return result

def train(env, mode, seed, updates=300, groups=32, group_size=8, eval_count=256,
          domain=None):
    rng=np.random.default_rng(seed)
    reset_rng=np.random.default_rng(seed+30000)
    eval_rng=np.random.default_rng(seed+10000)
    weights=initial_weights(env,rng)
    initial_hash=hashlib.sha256(b"".join(v.tobytes() for v in weights.values())).hexdigest()
    mom={k:np.zeros_like(v) for k,v in weights.items()}
    var={k:np.zeros_like(v) for k,v in weights.items()}
    totals={k:0 for k in ("hits","mixed","groups","active_steps","slots","episodes",
                         "mixed_group_updates","nonzero_gradient_updates",
                         "parameter_updates","zero_gradient_parameter_updates")}
    phases={}
    records=[]
    prefix_checkpoint=None
    start=time.monotonic()
    for step in range(updates+1):
        if domain=="sokoban-medium" and step==int(updates*.3):
            prefix_checkpoint=hashlib.sha256(
                b"".join(v.tobytes() for table in (weights,mom,var) for v in table.values())+
                json.dumps([rng.bit_generator.state,reset_rng.bit_generator.state],sort_keys=True).encode()
            ).hexdigest()
        if step%30==0 or step==updates or (mode.endswith("-switch") and step==int(updates*.3)) or (
                domain=="sokoban-medium" and step in (int(updates*.3),int(updates*.6))):
            stats=rollout(env,weights,"ordinary",np.full(eval_count,env.root,dtype=np.int32),
                          1,eval_rng,replay=step==updates)
            exact=exact_hits(env,"ordinary",weights)
            records.append(dict(step=step,root_hits=stats["hits"],root_trials=eval_count,
                                exact_root_probability=float(exact[env.root]),train=dict(totals),
                                **({k:stats[k] for k in ("independent_replay_hits","witness")} if step==updates else {})))
        if step==updates:
            break
        active_mode=schedule(mode,step,updates)
        starts=starts_for(env,active_mode,reset_rng,groups,group_size)
        stats,grads=rollout(env,weights,active_mode,starts,group_size,rng,True)
        stats["mixed_group_updates"]=int(stats["mixed"]>0)
        stats["nonzero_gradient_updates"]=int(any(np.any(g!=0) for g in grads.values()))
        changed=False
        # Standard Adam, identical across all arms.
        for key,g in grads.items():
            before=weights[key].copy()
            mom[key]=.9*mom[key]+.1*g
            var[key]=.999*var[key]+.001*g*g
            weights[key]+=.003*(mom[key]/(1-.9**(step+1)))/(np.sqrt(var[key]/(1-.999**(step+1)))+1e-8)
            changed=changed or bool(np.any(weights[key]!=before))
        stats["parameter_updates"]=int(changed)
        stats["zero_gradient_parameter_updates"]=int(changed and not stats["nonzero_gradient_updates"])
        phase=phases.setdefault(active_mode,{k:0 for k in totals}|{"reset_groups":0,"nonordinary_reset_groups":0})
        phase["reset_groups"]+=groups
        phase["nonordinary_reset_groups"]+=int((starts[::group_size]!=env.root).sum())
        for key in totals:
            totals[key]+=stats[key]
            phase[key]+=stats[key]
    return dict(environment=domain or env.name, mode=mode, seed=seed, updates=updates, groups=groups,
                group_size=group_size,horizon=env.horizon,eval_count=eval_count,
                common_prefix_sha256=prefix_checkpoint,root_state=env.states[env.root],
                initial_sha256=initial_hash,records=records,phases=phases,totals=totals,
                weights={k:v.tolist() for k,v in weights.items()},seconds=time.monotonic()-start)


def run_one(args):
    domain,mode,seed,updates,groups,group_size,eval_count=args
    env=make_domain(domain)
    return train(env,mode,seed,updates,groups,group_size,eval_count,domain=domain)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--domains",nargs="+",choices=list(MODES),default=["tensor","sokoban"])
    p.add_argument("--seeds",nargs="+",type=int,default=[42,43,44,45])
    p.add_argument("--updates",type=int,default=300)
    p.add_argument("--groups",type=int,default=32)
    p.add_argument("--group-size",type=int,default=8)
    p.add_argument("--eval-count",type=int,default=256)
    p.add_argument("--workers",type=int,default=1)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    environments={domain:make_domain(domain) for domain in a.domains}
    metadata={domain:geometry(env) for domain,env in environments.items()}
    (a.out/"manifest.json").write_text(json.dumps(dict(config={**vars(a),"out":str(a.out)},environments=metadata),indent=2))
    jobs=[(d,m,s,a.updates,a.groups,a.group_size,a.eval_count)
          for d in a.domains for m in MODES[d] for s in a.seeds]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        for row in pool.map(run_one,jobs):
            name=f"{row['environment']}-{row['mode']}-{row['seed']}.json"
            (a.out/name).write_text(json.dumps(row,indent=2))
            print(name,row["records"][-1]["root_hits"],row["totals"]["mixed"],flush=True)


if __name__=="__main__":
    main()
