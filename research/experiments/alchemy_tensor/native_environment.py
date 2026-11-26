"""Exact finite environments for two neutral-exposure mechanism pilots."""
from collections import deque
from itertools import combinations, product
from dataclasses import dataclass

import numpy as np


@dataclass
class Environment:
    name: str
    states: list
    features: np.ndarray
    transitions: np.ndarray  # -1 is padding, self-loop is legal
    terminal: np.ndarray
    distances: np.ndarray  # offline diagnostics/reset construction only
    root: int
    horizon: int
    metadata: dict
    ranks: np.ndarray | None = None


# All nonzero rank-one terms over F2^2 x F2^2 x F2^2.
TERMS = tuple(product(range(1, 4), repeat=3))
TERM_IDS = {term: i for i, term in enumerate(TERMS)}
TENSOR_BITS = tuple(
    sum(((a >> i & 1) * (b >> j & 1) * (c >> k & 1)) << (4*i + 2*j + k)
        for i, j, k in product(range(2), repeat=3))
    for a, b, c in TERMS
)


def tensor_value(state):
    result = 0
    for i in state:
        result ^= TENSOR_BITS[i]
    return result


def tensor_toggle(state, remove, add):
    """Canonical set over F2: a duplicated summand cancels."""
    result = set(state) - set(remove)
    for term in add:
        if 0 in term:
            continue
        result.symmetric_difference_update({TERM_IDS[tuple(term)]})
    return tuple(sorted(result))


def tensor_neighbors(state, cap):
    """Native flip/plus transformations; same types at all caps."""
    destinations = set()
    for p, q in product(state, repeat=2):
        if p == q:
            continue
        a, b = TERMS[p], TERMS[q]
        for axis in range(3):
            if a[axis] == b[axis]:
                # Shared-factor flip: in the two other axes do
                # (x,y)+(z,w) -> (x,y+w)+(z+x,w).
                other = [i for i in range(3) if i != axis]
                u, v = other
                c, d = list(a), list(b)
                c[v] ^= b[v]
                d[u] ^= a[u]
                dest = tensor_toggle(state, (p, q), (c, d))
            else:
                # Plus: replace q by two terms using pivot factor from p.
                c, d = list(b), list(b)
                c[axis] ^= a[axis]
                d[axis] = a[axis]
                dest = tensor_toggle(state, (q,), (c, d))
            if len(dest) <= cap and dest != state:
                destinations.add(dest)
    return sorted(destinations)


