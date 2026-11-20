"""Matched rewards and response-only proximal/replay objectives."""
import math


def reward_vectors(rows, trace_by_id):
    if len(rows) != 16 or not all(r['reward_eligible'] for r in rows):
        raise ValueError('Need sixteen fully resolved candidates')
    local = [float(r['local_accepted']) for r in rows]
    cross = [r['cross_reward'] for r in rows]
    if any(not math.isfinite(r) or not 0 <= r <= 1 for r in cross):
        raise ValueError('Invalid cross reward')
    if any(c and not l for l,c in zip(local,cross)): raise ValueError('Incorrect source received credit')
    eligible = [i for i,l in enumerate(local) if l]
    order = sorted(eligible, key=lambda i:(len(trace_by_id[rows[i]['id']]['response_token_ids']),
                                         trace_by_id[rows[i]['id']]['sample_index']))
    length = [0.] * len(rows)
    for index, reward in zip(order, sorted((cross[i] for i in eligible), reverse=True)):
        length[index] = reward
    return dict(local=local, cross=cross, length=length, replay=local)


def advantages(rewards):
    mean = sum(rewards)/len(rewards)
    std = (sum((r-mean)**2 for r in rewards)/len(rewards))**.5
    return [(r-mean)/(std+1e-6) for r in rewards]


def response_log_probs(model, prompt_ids, response_ids, device):
    import torch
    if not prompt_ids or not response_ids: raise ValueError('Empty prompt/response tokens')
    ids = torch.tensor([prompt_ids + response_ids], dtype=torch.long, device=device)
    logits = model(input_ids=ids[:,:-1], use_cache=False).logits[0, len(prompt_ids)-1:, :].float()
    target = ids[0, len(prompt_ids):]
    return logits.log_softmax(-1).gather(-1, target[:,None]).squeeze(-1)


def loss_terms(logp, old, reference, advantage, reward, arm, clip=.2, beta=.02):
    import torch
    if logp.shape != old.shape or logp.shape != reference.shape or logp.numel() == 0:
        raise ValueError('Token log-probability shape mismatch')
    if arm not in ('local', 'cross', 'length', 'replay'): raise ValueError('Unknown arm')
    ratio = (logp-old).exp()
    if arm == 'replay': actor = -reward*logp.mean()
    else: actor = -torch.minimum(ratio*advantage, ratio.clamp(1-clip,1+clip)*advantage).mean()
    difference = reference-logp
    penalty = (difference.exp()-difference-1).mean()
    total = actor+beta*penalty
    if not torch.isfinite(total): raise FloatingPointError('Nonfinite objective')
    return total, actor, penalty, ((ratio < 1-clip) | (ratio > 1+clip)).float().mean()
