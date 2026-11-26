"""Lazy flip/plus/reduction graph for exact 2x2 matrix multiplication over F2."""
from functools import lru_cache
from itertools import product, combinations

import numpy as np

# Term IDs store the three nonzero row-major 2x2 factor bitmasks.
def pack(a,b,c):
    return a | (b<<4) | (c<<8)


def unpack(term):
    return term&15, (term>>4)&15, (term>>8)&15


TERMS=tuple(pack(*t) for t in product(range(1,16),repeat=3))
ROOT=tuple(sorted(pack(1<<(2*i+j),1<<(2*j+k),1<<(2*i+k))
                  for i,j,k in product(range(2),repeat=3)))


def outer2(a,b):
    return sum(1<<(4*i+j) for i,j in product(range(4),repeat=2)
               if (a>>i)&(b>>j)&1)


def outer3(a,b,c):
    return sum(1<<(16*i+4*j+k) for i,j,k in product(range(4),repeat=3)
               if (a>>i)&(b>>j)&(c>>k)&1)


TENSOR_BITS={s:outer3(*unpack(s)) for s in TERMS}


def tensor_value(state):
    value=0
    for term in state:
        value ^= TENSOR_BITS[term]
    return value


TARGET=tensor_value(ROOT)


def tensor_value_scalar(state):
    entries=[0]*64
    for term in state:
        a,b,c=unpack(term)
        for i,j,k in product(range(4),repeat=3):
            entries[16*i+4*j+k]^=((a>>i)&(b>>j)&(c>>k)&1)
    return sum(v<<i for i,v in enumerate(entries))


def scalar_verify(state):
    """Independent arithmetic check on all 256 pairs of binary matrices."""
    if len(set(state))!=len(state) or any(t not in TENSOR_BITS for t in state):
        return False
    triples=[unpack(t) for t in state]
    for x,y in product(range(16),repeat=2):
        expected=0
        for i,k in product(range(2),repeat=2):
            value=0
            for j in range(2):
                value^=(x>>(2*i+j))&(y>>(2*j+k))&1
            expected |= value<<(2*i+k)
        actual=0
        for a,b,c in triples:
            if (a&x).bit_count()%2 and (b&y).bit_count()%2:
                actual ^= c
        if actual!=expected:
            return False
    return True


def toggle(state, remove, add):
    out=set(state)-set(remove)
    for t in add:
        if 0 not in unpack(t):
            out.symmetric_difference_update({t})
    return tuple(sorted(out))


def null_relations(vectors):
    """All nonzero GF2 dependency vectors, via a Gaussian-elimination basis."""
    basis={}
    deps=[]
    for i,v in enumerate(vectors):
        relation=1<<i
        while v:
            bit=v.bit_length()-1
            if bit not in basis:
                basis[bit]=(v,relation)
                break
            u,r=basis[bit]
            v ^= u
            relation ^= r
        if v==0:
            deps.append(relation)
    relations=[0]
    for relation in deps:
        relations += [v^relation for v in relations]
    return relations[1:]


def reduce_neighbors(state, values):
    destinations=set()
    for axis in range(3):
        other=[i for i in range(3) if i!=axis]
        pair_tensors=[outer2(t[other[0]],t[other[1]]) for t in values]
        for relation in null_relations(pair_tensors):
            subset=[i for i in range(len(state)) if relation>>i&1]
            for pivot in subset:
                replacements=[]
                for i in subset:
                    if i != pivot:
                        factors=list(values[i])
                        factors[axis] ^= values[pivot][axis]
                        replacements.append(pack(*factors))
                destinations.add(toggle(state,[state[i] for i in subset],replacements))
    return destinations


@lru_cache(maxsize=8192)
def legal_neighbors(state):
    """Full cap9 vocabulary. Cap8 masks rank-increasing destinations."""
    if len(state)<=7:
        return (state,)
    destination=set()
    values=tuple(map(unpack,state))
    for p,q in product(range(len(state)),repeat=2):
        if p==q:
            continue
        a,b=values[p],values[q]
        for axis in range(3):
            if a[axis]==b[axis]:
                u,v=[i for i in range(3) if i!=axis]
                c,d=list(a),list(b)
                c[v]^=b[v]
                d[u]^=a[u]
                nxt=toggle(state,(state[p],state[q]),(pack(*c),pack(*d)))
            else:
                c,d=list(b),list(b)
                c[axis]^=a[axis]
                d[axis]=a[axis]
                nxt=toggle(state,(state[q],),(pack(*c),pack(*d)))
            if nxt!=state and len(nxt)<=9:
                destination.add(nxt)
    destination.update(reduce_neighbors(state,values))
    for dest in destination:
        # Every generated state is checked, not just successful endpoints.
        assert len(dest)<=9 and tensor_value(dest)==TARGET
    return tuple(sorted(destination))


def cap_neighbors(state, cap):
    assert cap in (8,9)
    valid=tuple(s for s in legal_neighbors(state) if len(s)<=cap)
    return valid or (state,)


# Standard 2x2 matrix multiplication symmetry. Used solely for certificate
# search bookkeeping; training uses the labeled graph.
def matrix_transpose(a):
    return ((a&1) | ((a&2)<<1) | ((a&4)>>1) | (a&8))


def matrix_multiply(a,b):
    result=0
    for i,k in product(range(2),repeat=2):
        bit=0
        for j in range(2):
            bit^=(a>>(2*i+j))&(b>>(2*j+k))&1
        result|=bit<<(2*i+k)
    return result


IDENTITY=9
GL=tuple(a for a in range(1,16) if next((b for b in range(1,16)
    if matrix_multiply(a,b)==IDENTITY and matrix_multiply(b,a)==IDENTITY),None) is not None)
INVERSE={a:next(b for b in GL if matrix_multiply(a,b)==IDENTITY) for a in GL}


def symmetry_map():
    """T -> P^T A Q^-T, Q^T B R^-T, P^-1 C R."""
    maps=[]
    for p,q,r in product(GL,repeat=3):
        amap={a:matrix_multiply(matrix_multiply(matrix_transpose(p),a),
                               matrix_transpose(INVERSE[q])) for a in range(1,16)}
        bmap={b:matrix_multiply(matrix_multiply(matrix_transpose(q),b),
                               matrix_transpose(INVERSE[r])) for b in range(1,16)}
        cmap={c:matrix_multiply(matrix_multiply(INVERSE[p],c),r) for c in range(1,16)}
        mapping=np.zeros(4096,dtype=np.uint16)
        for term in TERMS:
            a,b,c=unpack(term)
            mapping[term]=pack(amap[a],bmap[b],cmap[c])
        assert tensor_value(tuple(sorted(int(mapping[t]) for t in ROOT)))==TARGET
        maps.append(mapping)
    return np.array(maps)


def orbit_key(state,maps):
    shifted=np.sort(maps[:,list(state)],axis=1)
    best=np.lexsort(shifted[:,::-1].T)[0]
    return tuple(int(x) for x in shifted[best])


def certify(max_nodes=3000):
    """BFS over verified symmetry quotient, store labeled solution path."""
    maps=symmetry_map()
    root_key=orbit_key(ROOT,maps)
    queue=[ROOT]
    labels=[None]
    seen={root_key}
    expanded=0
    for index,state in enumerate(queue):
        if len(state)<=7:
            path=[]
            cursor=index
            while cursor is not None:
                path.append(queue[cursor])
                cursor=labels[cursor]
            path.reverse()
            for a,b in zip(path,path[1:]):
                assert b in cap_neighbors(a,8)
            assert scalar_verify(path[-1])
            return dict(found=True,expanded=expanded,orbits=len(seen),path=path)
        if expanded>=max_nodes:
            break
        expanded+=1
        for nxt in cap_neighbors(state,8):
            k=orbit_key(nxt,maps)
            if k not in seen:
                seen.add(k)
                labels.append(index)
                queue.append(nxt)
    return dict(found=False,expanded=expanded,orbits=len(seen))
