"""Exact finite tree-polynomial verifier. No learned or approximate acceptance.

Vertices are explicitly labelled 0,...,n-1; Prüfer codes encode labelled trees.
Published witness construction functions are for independent audits ONLY, never
training/reset input. All coefficients and raw defects use Python integers.
"""
from __future__ import annotations
from collections import deque
from heapq import heapify, heappop, heappush
from operator import index as integer


def prufer_to_edges(code, n=None):
    code = [integer(v) for v in code]
    if n is None:
        n = len(code) + 2
    n = integer(n)
    if n < 1 or len(code) != max(0, n - 2) or any(v < 0 or v >= n for v in code):
        raise ValueError('invalid Prüfer code')
    if n == 1:
        return []
    deg = [1] * n
    for v in code:
        deg[v] += 1
    leaves = [v for v in range(n) if deg[v] == 1]
    heapify(leaves)
    edges = []
    for v in code:
        u = heappop(leaves)
        edges.append((u, v))
        deg[v] -= 1
        if deg[v] == 1:
            heappush(leaves, v)
    edges.append(tuple(leaves))
    return edges


def adjacency(n, edges):
    """Build adjacency and reject anything except a simple, connected tree."""
    n = integer(n)
    if n < 1:
        raise ValueError('tree must have positive size')
    out = [[] for _ in range(n)]
    count = 0
    for u, v in edges:
        u, v = integer(u), integer(v)
        if not 0 <= u < n or not 0 <= v < n or u == v:
            raise ValueError('invalid tree edge')
        out[u].append(v)
        out[v].append(u)
        count += 1
    if count != n - 1:
        raise ValueError('wrong edge count')
    # With n-1 edges, connectedness also excludes repeated edges and cycles.
    seen = {0}
    stack = [0]
    while stack:
        for v in out[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    if len(seen) != n:
        raise ValueError('tree is disconnected')
    return out


def prufer_to_adj(code, n=None):
    if n is None:
        n = len(code) + 2
    return adjacency(n, prufer_to_edges(code, n))


def edges_to_prufer(n, edges):
    adj = [set(a) for a in adjacency(n, edges)]
    leaves = [v for v in range(n) if len(adj[v]) == 1]
    heapify(leaves)
    code = []
    for _ in range(max(0, n - 2)):
        u = heappop(leaves)
        v = next(iter(adj[u]))
        code.append(v)
        adj[v].remove(u)
        adj[u].clear()
        if len(adj[v]) == 1:
            heappush(leaves, v)
    return tuple(code)


def adj_to_prufer(adj):
    return edges_to_prufer(len(adj), [(u,v) for u, nbr in enumerate(adj) for v in nbr if u < v])


def _children(adj, root):
    n = len(adj)
    if not 0 <= root < n:
        raise ValueError('invalid root')
    children = [[] for _ in range(n)]
    parent = [-1] * n
    parent[root] = root
    order = [root]
    for v in order:
        for u in adj[v]:
            if parent[u] == -1:
                parent[u] = v
                order.append(u)
                children[v].append(u)
    return children, reversed(order)


def _sum(a,b):
    if len(a) < len(b):
        a,b = b,a
    out = a.copy()
    for i,v in enumerate(b):
        out[i] += v
    return out


def _sub(a,b):
    out = a.copy()
    if len(out) < len(b):
        out.extend([0] * (len(b) - len(out)))
    for i,v in enumerate(b):
        out[i] -= v
    return out


def _mul(a,b):
    if len(a) < len(b):
        a,b = b,a
    # All convolution coefficients are exact Python ints. Avoid fixed-width
    # NumPy integers: at n=101 even a single coefficient may exceed 64 bits.
    if len(b) == 1:
        return a.copy() if b[0] == 1 else [v*b[0] for v in a]
    out = [0] * (len(a) + len(b) - 1)
    for i,x in enumerate(b):
        if x:
            for j,y in enumerate(a):
                out[i+j] += x*y
    return out


def independence_polynomial(n, edges, root=0):
    """Coefficients [x^0,...,x^n], including terminal zero padding."""
    children, order = _children(adjacency(n, edges), root)
    chosen, absent = [None]*n,[None]*n
    for u in order:
        take, leave = [0,1], [1]
        for v in children[u]:
            take = _mul(take, absent[v])
            leave = _mul(leave, _sum(chosen[v], absent[v]))
        chosen[u], absent[u] = take, leave
    a = _sum(chosen[root], absent[root])
    return a + [0] * (n+1-len(a))


def domination_polynomial(n, edges, root=0):
    """Exact three-state rooted DP, A chosen, B internally dominated, C needs parent."""
    children, order = _children(adjacency(n, edges), root)
    A,B,C = [None]*n,[None]*n,[None]*n
    for u in order:
        a, ab, b_only = [0,1], [1], [1]
        for v in children[u]:
            ab_v = _sum(A[v], B[v])
            a = _mul(a, _sum(ab_v,C[v]))
            ab = _mul(ab, ab_v)
            b_only = _mul(b_only,B[v])
        A[u],B[u],C[u] = a,_sub(ab,b_only),b_only
    a = _sum(A[root],B[root])
    return a + [0] * (n+1-len(a))


def tree_id(n, edges):
    """Exact AHU unlabelled canonical string, rooted at tree center(s)."""
    adj = adjacency(n, edges)
    degree = [len(x) for x in adj]
    border = deque(v for v in range(n) if degree[v] <= 1)
    remaining = n
    while remaining > 2:
        layer = len(border)
        remaining -= layer
        for _ in range(layer):
            v = border.popleft()
            for u in adj[v]:
                degree[u] -= 1
                if degree[u] == 1:
                    border.append(u)
    centers = list(border)
    if len(centers) not in (1,2):
        raise AssertionError('center calculation failed')
    def enc(root):
        children, order = _children(adj, root)
        codes = [''] * n
        for u in order:
            codes[u] = '(' + ''.join(sorted(codes[v] for v in children[u])) + ')'
        return codes[root]
    return min(enc(v) for v in centers)


def canonical_id(adj):
    return tree_id(len(adj), [(u,v) for u,nbr in enumerate(adj) for v in nbr if u<v])


def defect(coeffs, i):
    if not 0 < i < len(coeffs)-1:
        raise ValueError('index must be interior')
    return coeffs[i-1]*coeffs[i+1] - coeffs[i]**2


def support_indices(coeffs):
    return [i for i in range(1,len(coeffs)-1) if coeffs[i-1] > 0 and coeffs[i] > 0 and coeffs[i+1] > 0]


def violations(coeffs):
    return [i for i in support_indices(coeffs) if defect(coeffs,i)>0]


def score(coeffs,index=None,required=1,mode='raw'):
    """Terminal score only. Fixed-index raw reproduces the published formula,
    including its zero-out-of-support pathology; normalized invalid -> -1.
    Multi-index uses required-th largest margin among interior support indices.
    Binary acceptance uses exact positive coefficients and integer signs.
    """
    if required < 1:
        raise ValueError('required must be positive')
    if mode not in ('raw','normalized','binary'):
        raise ValueError('unknown score mode')
    if index is not None:
        if required != 1:
            raise ValueError('cannot specify multiple required at fixed index')
        d = defect(coeffs,index)
        if mode == 'raw':
            return d
        if index not in support_indices(coeffs):
            return 0 if mode == 'binary' else -1.0
        if mode == 'binary':
            return int(d>0)
        return d/(coeffs[index-1]*coeffs[index+1]+coeffs[index]**2)
    indices = support_indices(coeffs)
    if mode == 'binary':
        return int(sum(defect(coeffs,i)>0 for i in indices) >= required)
    if len(indices) < required:
        return -1.0 if mode == 'normalized' else -1
    margins = [defect(coeffs,i) if mode == 'raw' else defect(coeffs,i)/(coeffs[i-1]*coeffs[i+1]+coeffs[i]**2) for i in indices]
    return sorted(margins,reverse=True)[required-1]


def _builder():
    edges = []
    def child(parent):
        v=len(edges)+1
        edges.append((parent,v))
        return v
    def path(parent,length):
        for _ in range(length):
            parent=child(parent)
    return edges,child,path


def path_tree(n):
    return n,[(i,i+1) for i in range(n-1)]


def galvin_tree(m,t):
    """Galvin T_(m,t,1), arxiv:2502.10654 §2."""
    edges,child,path=_builder()
    for _ in range(m):
        w=child(0)
        for _ in range(t):
            path(w,2)
    return len(edges)+1,edges


def kadrawi_26_trees():
    """Kadrawi & Levit arxiv:2305.01784, two exact 26-vertex anchors."""
    result=[]
    for lengths in [(2,2,2),(4,2,2)]:
        edges,child,path=_builder()
        w=child(0)
        for k in lengths:
            path(w,k)
        for t in ([4,4] if lengths[0]==2 else [3,4]):
            w=child(0)
            for _ in range(t):
                path(w,2)
        result.append((len(edges)+1,edges))
    return result


def bautista_ramos_tree(m,t):
    """TG_(m,t), arxiv:2511.00334 Definition 1(iv)."""
    edges,child,path=_builder()
    for _ in range(m):
        v=child(0)
        for _ in range(3):
            w=child(v)
            for _ in range(t):
                path(w,2)
    child(0)
    return len(edges)+1,edges


def domination_witness_tree(m,t):
    """W_(m,t), arxiv:2605.02193 §4: leaf extensions of TG_(m,t)."""
    edges,child,path=_builder()
    for _ in range(m):
        v=child(0)
        for _ in range(3):
            w=child(v)
            for _ in range(t):
                path(w,3)
    path(0,2)
    return len(edges)+1,edges
