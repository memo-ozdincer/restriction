"""Independent exact single-move star landscape diagnostic."""
from __future__ import annotations
from collections import Counter
from math import comb
from pathlib import Path
import json
import time

from audit import (adjacency, coefficients, canonical, edge_neighbors,
                   prufer_neighbors, measures)
from environment import independence_polynomial

N = 56
INDICES = (27, 28)


def binomial(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def analytic_star(n):
    # Star: choose any subset of leaves, or the center alone.
    return [binomial(n-1, k) + int(k == 1) for k in range(n+1)]


def analytic_near_star(n):
    # Center excluded: one edge on two of the leaves, n-3 free leaves.
    # Center included: the outermost leaf may be chosen, other leaves
    # and the intermediate degree-two vertex cannot be selected.
    return [binomial(n-3, k) + 2*binomial(n-3, k-1)
            + int(k in (1, 2)) for k in range(n+1)]


def encoded_measure(c, i):
    raw, norm = measures(c, i)
    return {"coefficient_triplet": c[i-1:i+2], "raw": raw,
            "normalized_exact": str(norm), "normalized": float(norm)}


def inspect_neighbors(n, edges, moves, parent):
    expected = analytic_near_star(n)
    ids = set()
    labeled = set()
    rows = {i: {"raw": Counter(), "normalized": Counter(), "hits": 0}
            for i in INDICES}
    count = 0
    for e in moves(n, edges):
        a = adjacency(n, e)
        c, _ = coefficients(a)
        assert c == expected == independence_polynomial(n, e)
        ids.add(canonical(a))
        edge_id = tuple(sorted(tuple(sorted(edge)) for edge in e))
        assert edge_id not in labeled, "duplicate labeled neighbor"
        labeled.add(edge_id)
        count += 1
        for i in INDICES:
            raw, norm = measures(c, i)
            p_raw, p_norm = parent[i]
            assert norm is not None and p_norm is not None
            for field, a_value, b_value in (("raw", raw, p_raw),
                                          ("normalized", norm, p_norm)):
                key = "better" if a_value > b_value else "worse" if a_value < b_value else "equal"
                rows[i][field][key] += 1
            rows[i]["hits"] += raw > 0
    assert count == (n-1)*(n-2) if moves is edge_neighbors else count == (n-2)*(n-1)
    assert len(ids) == 1
    return {"moves": moves.__name__, "labeled_neighbors": count,
            "unlabeled_neighbor_classes": len(ids), "indices": rows}


def main():
    start = time.monotonic()
    star = [(0, v) for v in range(1, N)]
    star_c, _ = coefficients(adjacency(N, star))
    assert star_c == analytic_star(N) == independence_polynomial(N, star)
    parent = {i: measures(star_c, i) for i in INDICES}
    near_c = analytic_near_star(N)
    result = {"n": N, "anchor": "star", "indices": {
        i: {"star": encoded_measure(star_c, i),
            "near_star": encoded_measure(near_c, i)} for i in INDICES},
        "neighborhoods": [inspect_neighbors(N, star, moves, parent)
                          for moves in (edge_neighbors, prufer_neighbors)]}
    result["elapsed_seconds"] = time.monotonic() - start
    path = Path(__file__).with_name("star_audit.json")
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
