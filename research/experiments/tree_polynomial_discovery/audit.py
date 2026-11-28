"""Exact offline historical-output and local-neighborhood audit."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import heapq
import json
import math
from pathlib import Path
import random
import re
import time
import urllib.request

COMMIT = "79ef336cce13b2b6bcd68fce2f4f6fa12a8b69a5"
URL = "https://raw.githubusercontent.com/ericgramos/TreeUnimodalityPatternBoost/" + COMMIT + "/60_vertex_output/"
FILES = ("search_output_1.txt", "search_output_11.txt", "transformer-output-decoded.txt",
         "distribution.txt", "training_distribution.txt", "README.md")


def decode(code, n=None):
    """Independent zero-based Prüfer decoder."""
    n = len(code) + 2 if n is None else n
    if len(code) != n - 2 or any(v < 0 or v >= n for v in code):
        raise ValueError("invalid Prüfer sequence")
    degree = [1] * n
    for v in code:
        degree[v] += 1
    leaves = [v for v in range(n) if degree[v] == 1]
    heapq.heapify(leaves)
    edges = []
    for v in code:
        u = heapq.heappop(leaves)
        edges.append((u, v))
        degree[v] -= 1
        if degree[v] == 1:
            heapq.heappush(leaves, v)
    edges.append(tuple(leaves))
    return edges


def encode(n, edges):
    adj = adjacency(n, edges)
    leaves = [i for i in range(n) if len(adj[i]) == 1]
    heapq.heapify(leaves)
    out = []
    for _ in range(n - 2):
        u = heapq.heappop(leaves)
        v = adj[u].pop()
        adj[v].remove(u)
        out.append(v)
        if len(adj[v]) == 1:
            heapq.heappush(leaves, v)
    return out


def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    if len(edges) != n - 1:
        raise ValueError("wrong edge count")
    for u, v in edges:
        if not (0 <= u < n and 0 <= v < n) or u == v or v in adj[u]:
            raise ValueError("invalid edge")
        adj[u].add(v)
        adj[v].add(u)
    visited = {0}
    todo = [0]
    while todo:
        for v in adj[todo.pop()]:
            if v not in visited:
                visited.add(v)
                todo.append(v)
    if len(visited) != n:
        raise ValueError("disconnected tree")
    return adj


def mul(a, b):
    if len(a) > len(b):
        a, b = b, a
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def add(a, b):
    a, b = (a, b) if len(a) >= len(b) else (b, a)
    out = a.copy()
    for j, y in enumerate(b):
        out[j] += y
    return out


def coefficients(adj):
    """Independent deletion/contraction-style rooted independent-set DP."""
    def rooted(u, p):
        excluded, included = [1], [0, 1]
        for v in adj[u]:
            if v != p:
                x, y = rooted(v, u)
                excluded = mul(excluded, add(x, y))
                included = mul(included, x)
        return excluded, included
    a, b = rooted(0, -1)
    c = add(a, b)
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return c + [0] * (len(adj) + 1 - len(c)), len(c) - 1


def canonical(adj):
    """AHU canonical unrooted form via leaf stripping; no hash collisions."""
    degrees = [len(v) for v in adj]
    layer = [i for i, d in enumerate(degrees) if d <= 1]
    remaining = len(adj)
    while remaining > 2:
        remaining -= len(layer)
        new = []
        for v in layer:
            degrees[v] = 0
            for w in adj[v]:
                if degrees[w]:
                    degrees[w] -= 1
                    if degrees[w] == 1:
                        new.append(w)
        layer = new
    def root(u, p):
        return "(" + "".join(sorted(root(v, u) for v in adj[u] if v != p)) + ")"
    if len(layer) == 1:
        return root(layer[0], -1)
    return "(" + "".join(sorted((root(layer[0], layer[1]), root(layer[1], layer[0])))) + ")"


def measures(c, i):
    lhs, rhs = c[i - 1] * c[i + 1], c[i] ** 2
    # Out of support remains invalid; denominator zero given no positive midpoint.
    return lhs - rhs, Fraction(lhs-rhs, lhs+rhs) if lhs+rhs else None


def descr(values):
    if not values:
        return {}
    values = sorted(values)
    return {k: float(values[min(len(values)-1, int((len(values)-1)*q))])
            for k, q in [('min', 0), ('p10', .1), ('median', .5), ('p90', .9), ('max', 1)]}


def galvin(m=5, t=5):
    edges = []
    next_v = 1
    for _ in range(m):
        v = next_v
        next_v += 1
        edges.append((0, v))
        for _ in range(t):
            u, w = next_v, next_v + 1
            next_v += 2
            edges.extend(((v, u), (u, w)))
    return next_v, edges


def edge_neighbors(n, edges):
    adj = adjacency(n, edges)
    for u, v in edges:
        component = {u}
        todo = [u]
        while todo:
            w = todo.pop()
            for x in adj[w]:
                if (w == u and x == v) or (w == v and x == u):
                    continue
                if x not in component:
                    component.add(x)
                    todo.append(x)
        other = set(range(n)) - component
        remaining = list(edges)
        remaining.remove((u, v))
        for a in sorted(component):
            for b in sorted(other):
                if a != u or b != v:
                    yield remaining + [(a, b)]


def prufer_neighbors(n, edges):
    code = encode(n, edges)
    for i, old in enumerate(code):
        for new in range(n):
            if old != new:
                modified = code.copy()
                modified[i] = new
                yield decode(modified)


def neighborhood(name, n, edges, moves, indices):
    c, alpha = coefficients(adjacency(n, edges))
    parent = {i: measures(c, i) for i in indices}
    rows = {i: {"raw": [], "norm": [], "raw_better": 0, "norm_better": 0,
                "hits": 0, "outside_support": 0} for i in indices}
    ids = set()
    count = 0
    for e in moves(n, edges):
        a = adjacency(n, e)
        ids.add(canonical(a))
        p, _ = coefficients(a)
        count += 1
        for i in indices:
            raw, norm = measures(p, i)
            r = rows[i]
            r["raw"].append(raw)
            r["raw_better"] += raw > parent[i][0]
            r["hits"] += raw > 0
            if norm is None:
                r["outside_support"] += 1
            else:
                r["norm"].append(norm)
                r["norm_better"] += parent[i][1] is not None and norm > parent[i][1]
    for i in indices:
        r = rows[i]
        r["parent_raw"] = parent[i][0]
        r["parent_norm"] = float(parent[i][1]) if parent[i][1] is not None else None
        r["best_raw_exact"] = max(r["raw"])
        r["raw_distribution"] = descr(r.pop("raw"))
        r["normalized_distribution"] = descr(r.pop("norm"))
    return {"anchor": name, "n": n, "alpha": alpha, "moves": moves.__name__,
            "labeled_neighbors": count, "unlabeled_neighbor_classes": len(ids), "indices": rows}


def get_files(cache):
    cache.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name in FILES:
        p = cache / name
        if not p.exists():
            with urllib.request.urlopen(URL + name, timeout=120) as src:
                p.write_bytes(src.read())
        b = p.read_bytes()
        manifest[name] = {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b), "url": URL + name}
    return manifest


def source_codes(path):
    with path.open() as f:
        for line in f:
            try:
                parsed = json.loads(line)
                if not isinstance(parsed, list) or any(not isinstance(x, int) for x in parsed):
                    yield None
                else:
                    yield [x - 1 for x in parsed]
            except (ValueError, TypeError):
                yield None


def aggregate(codes, n, indices):
    count = invalid = 0
    structural = Counter()
    hits = {i: set() for i in indices}
    positive = Counter()
    dist = {i: {"raw": [], "normalized": []} for i in indices}
    maxes = {i: None for i in indices}
    alpha_counts, leaf_counts = Counter(), Counter()
    violation_counts = Counter()
    for code in codes:
        count += 1
        if code is None or len(code) != n - 2 or any(v < 0 or v >= n for v in code):
            invalid += 1
            continue
        a = adjacency(n, decode(code, n))
        c, alpha = coefficients(a)
        ident = canonical(a)
        structural[ident] += 1
        alpha_counts[alpha] += 1
        leaf_counts[sum(len(x) == 1 for x in a)] += 1
        violation_counts[sum(measures(c, i)[0] > 0 for i in range(1, n))] += 1
        for i in indices:
            raw, norm = measures(c, i)
            dist[i]["raw"].append(raw)
            if norm is not None:
                dist[i]["normalized"].append(norm)
            if raw > 0:
                positive[i] += 1
                hits[i].add(ident)
            if maxes[i] is None or raw > maxes[i]["score"]:
                maxes[i] = {"score": raw, "coefficients": c[i-1:i+2], "prufer_zero_based": code}
    rows = {}
    for i in indices:
        rows[i] = {"positive": positive[i], "distinct_positive": len(hits[i]), "best": maxes[i],
                   "raw_dist": descr(dist[i]["raw"]), "normalized_dist": descr(dist[i]["normalized"])}
    path = canonical(adjacency(n, [(i,i+1) for i in range(n-1)]))
    return {"total": count, "invalid": invalid, "unique_unlabeled": len(structural),
            "most_common_unlabeled_counts": [v for _, v in structural.most_common(8)],
            "path_count": structural[path], "alpha_counts": dict(sorted(alpha_counts.items())),
            "leaf_counts": dict(sorted(leaf_counts.items())), "violation_counts": dict(sorted(violation_counts.items())),
            "indices": rows}


def compare_shared():
    """Cross-check generic independent implementation against shared verifier."""
    import environment as env
    rng = random.Random(15)
    for n in range(2, 13):
        for _ in range(20):
            code = [rng.randrange(n) for _ in range(n-2)]
            e = decode(code, n)
            c, _ = coefficients(adjacency(n,e))
            assert c == list(env.independence_polynomial(n,e))
            # Independently enumerate all subsets for small test cases.
            brute = [0]*(n+1)
            emasks = [(1<<u)|(1<<v) for u,v in e]
            for bits in range(1<<n):
                if all(bits&m != m for m in emasks):
                    brute[bits.bit_count()] += 1
            assert c == brute
            labels = list(range(n))
            rng.shuffle(labels)
            newe = [(labels[u],labels[v]) for u,v in e]
            assert canonical(adjacency(n,e)) == canonical(adjacency(n,newe))
            assert env.tree_id(n,e) == env.tree_id(n,newe)
    return 220


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", type=Path, default=Path("/tmp/tree_polynomial_patternboost_79ef336"))
    p.add_argument("--out", type=Path, default=Path(__file__).with_name("audit.json"))
    p.add_argument("--no-data", action="store_true")
    p.add_argument("--split-only", action="store_true", help="Audit verified old elite prefix vs fresh suffix; append to existing result")
    p.add_argument("--limit", type=int, default=0, help="Smoke only, cap each corpus")
    args = p.parse_args()
    t0 = time.monotonic()
    if args.split_only:
        from itertools import islice
        prior = args.cache / "search_output_10.txt"
        if not prior.exists():
            with urllib.request.urlopen(URL+prior.name,timeout=120) as src:
                prior.write_bytes(src.read())
        loop = args.cache / "fc_loop.py"
        loop_url = URL.replace("60_vertex_output/","PatternBoost/fc_loop.py")
        if not loop.exists():
            with urllib.request.urlopen(loop_url,timeout=120) as src:
                loop.write_bytes(src.read())
        prior_codes = list(source_codes(prior))
        mixed_codes = source_codes(args.cache / "transformer-output-decoded.txt")
        prefix_codes = list(islice(mixed_codes,len(prior_codes)))
        assert len(prior_codes) == 50000 and prefix_codes == prior_codes
        result = json.loads(args.out.read_text())
        result["source_files"][prior.name] = {"sha256":hashlib.sha256(prior.read_bytes()).hexdigest(),"url":URL+prior.name,"bytes":prior.stat().st_size}
        result["source_files"][loop.name] = {"sha256":hashlib.sha256(loop.read_bytes()).hexdigest(),"url":loop_url,"bytes":loop.stat().st_size}
        result["mixed_prefix_matches_prior_elite"] = True
        result["old_elite_prefix"] = aggregate(prior_codes,60,[29,30])
        print("previous elite",result["old_elite_prefix"]["indices"][30]["positive"],flush=True)
        result["fresh_transformer_suffix"] = aggregate(mixed_codes,60,[29,30])
        print("fresh transformer",result["fresh_transformer_suffix"]["total"],result["fresh_transformer_suffix"]["indices"][30]["positive"],flush=True)
        result["split_elapsed_seconds"] = time.monotonic()-t0
        args.out.write_text(json.dumps(result,indent=2)+"\n")
        return
    result = {"source_commit": COMMIT, "neighborhoods": [],
              "crosscheck_count": compare_shared()}
    n, e = galvin()
    c, alpha = coefficients(adjacency(n,e))
    assert n == 56 and alpha == 30 and measures(c,27)[0] == 332324762280
    anchors = [("path", 56, [(i,i+1) for i in range(55)]), ("Galvin_T5_5",n,e)]
    for name,n,e in anchors:
        for moves in (edge_neighbors,prufer_neighbors):
            row = neighborhood(name,n,e,moves,[27,28])
            result["neighborhoods"].append(row)
            print("neighborhood",name,moves.__name__,row["labeled_neighbors"],flush=True)
    if not args.no_data:
        from itertools import islice
        result["source_files"] = get_files(args.cache)
        result["historical"] = {}
        for name in FILES[:3]:
            codes = source_codes(args.cache / name)
            if args.limit:
                codes = islice(codes,args.limit)
            row = aggregate(codes,60,[29,30])
            result["historical"][name] = row
            print(name, row["total"], row["indices"][30]["positive"],row["unique_unlabeled"],flush=True)
        rng = random.Random(20261127)
        result["random60"] = aggregate(([rng.randrange(60) for _ in range(58)]
                                        for _ in range(args.limit or 10000)),60,[29,30])
        for f in ("distribution.txt","training_distribution.txt"):
            total = positive = parse_errors = 0
            for line in (args.cache/f).read_text().splitlines():
                m = re.fullmatch(r"Score: (.*), Count: (\d+)",line.strip())
                if m is None:
                    parse_errors += 1
                    continue
                score, count = float(m.group(1)), int(m.group(2))
                total += count
                positive += count if score > 0 else 0
            result[f] = {"reported_total": total, "reported_positive": positive,
                         "parse_errors": parse_errors}
    result["elapsed_seconds"] = time.monotonic()-t0
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print("finished",args.out,result["elapsed_seconds"],flush=True)


if __name__ == "__main__":
    main()
