"""Independent exact-answer checks; never visible to candidate models."""
from fractions import Fraction
from functools import lru_cache
from itertools import permutations, combinations
from math import gcd, isqrt
import json


def markov():
    # c is a quadratic root; iterate a,b and use exact discriminant.
    found=set()
    for a in range(1,1001):
        for b in range(a,1001):
            s=3*a*b; D=s*s-4*(a*a+b*b)
            if D<0:continue
            r=isqrt(D)
            if r*r!=D:continue
            for x in (s-r,s+r):
                if x%2==0 and b<=x//2<=1000:found.add((a,b,x//2))
    return len(found)


def race():
    a,b='HHTHT','THHHT'
    states=sorted({''}|{p[:i] for p in (a,b) for i in range(1,len(p))})
    n=len(states)
    M=[[Fraction(int(i==j)) for j in range(n)]+[Fraction(0)] for i in range(n)]
    for i,s in enumerate(states):
        for ch in 'HT':
            w=s+ch
            if w.endswith(a):M[i][-1]+=Fraction(1,2)
            elif not w.endswith(b):
                t=max((x for x in states if w.endswith(x)),key=len)
                M[i][states.index(t)]-=Fraction(1,2)
    for i in range(n):
        row=next(j for j in range(i,n) if M[j][i])
        M[i],M[row]=M[row],M[i]
        a=M[i][i];M[i]=[x/a for x in M[i]]
        for j in range(n):
            if j!=i:
                a=M[j][i];M[j]=[x-a*y for x,y in zip(M[j],M[i])]
    return M[states.index('')][-1]


def cyclic():
    ans=0
    for ones in combinations(range(20),8):
        s=['0']*20
        for i in ones:s[i]='1'
        s=''.join(s);t=s+s[:2]
        ans+= '000' not in t and '111' not in t
    return ans


def records():
    ans=0
    for p in permutations(range(1,10)):
        if any(v==i for i,v in enumerate(p,1)):continue
        mx=k=0
        for v in p:
            if v>mx:mx=v;k+=1
        ans+=k==3
    return ans


def trees():
    verts=[(i,j) for i in range(3) for j in range(5)]
    m=[]
    for u in verts[:-1]:
        row=[]
        for v in verts[:-1]:
            row.append(sum(abs(u[0]-w[0])+abs(u[1]-w[1])==1 for w in verts) if u==v
                       else -int(abs(u[0]-v[0])+abs(u[1]-v[1])==1))
        m.append(list(map(Fraction,row)))
    det=Fraction(1)
    for i in range(len(m)):
        j=next(j for j in range(i,len(m)) if m[j][i])
        if i!=j:det=-det;m[i],m[j]=m[j],m[i]
        k=m[i][i];det*=k
        for j in range(i+1,len(m)):
            c=m[j][i]/k
            m[j]=[x-c*y for x,y in zip(m[j],m[i])]
    assert det.denominator==1
    return int(det)


def paths():
    @lru_cache(None)
    def f(x,y):
        if x<0 or y<0 or y<x or (x,y) in {(3,6),(8,10)}:return 0
        if x==0 and y==0:return 1
        return f(x-1,y)+f(x,y-1)
    return f(12,12)


def primitive():
    return sum(gcd(gcd(a,b),60-a-b)==1 and (a+2*b+3*(60-a-b))%7==0
               for a in range(61) for b in range(61-a))


def matrices():
    @lru_cache(None)
    def f(cols):
        if not any(cols):return 1
        return sum(f(tuple(c-int(i in (a,b)) for i,c in enumerate(cols)))
                   for a,b in combinations(range(5),2) if cols[a]>0 and cols[b]>0)
    return f((2,)*5)


if __name__=='__main__':
    answers=dict(markov=markov(),pattern_race=race(),cyclic_words=cyclic(),
                 record_derangements=records(),grid_trees=trees(),ballot_paths=paths(),
                 primitive_triples=primitive(),regular_bipartite=matrices())
    print(json.dumps({k:str(v) for k,v in answers.items()},indent=2))
