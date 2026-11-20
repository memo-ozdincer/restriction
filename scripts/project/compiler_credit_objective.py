"""Off-policy masked likelihood with an explicit demonstration reference anchor."""


def loss_terms(logp, reference, mask, beta=.02):
    import torch
    if logp.ndim != 1 or logp.shape != reference.shape or logp.shape != mask.shape:
        raise ValueError('Inconsistent demonstration-token shapes')
    if not torch.all((mask == 0) | (mask == 1)) or mask.sum() == 0:
        raise ValueError('Empty or nonbinary supervision mask')
    nll = -(logp * mask).sum() / mask.sum()
    anchor = (logp - reference).square().mean()
    total = nll + beta * anchor
    if not torch.isfinite(total): raise FloatingPointError('Nonfinite objective')
    return total, nll, anchor
