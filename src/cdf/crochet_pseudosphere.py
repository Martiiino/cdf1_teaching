"""Assignment 2.1: recursive curves on local spheres (Rhino 8 / Python 3).

Layer 0 is a circle of circumference a. Recursive factors are 6,5,8,5.
Split EACH previous curve into b equal arc-length parts. For each part,
use its endpoint chord as a sphere diameter, then connect those endpoints
on that sphere by a curve of length a (always the original circumference).
Default layer counts: 1,6,30,240,1200. Total lengths: a,6a,30a,240a,1200a.
Seed 23 reproduces the presentation's geometry. No external file is needed.
"""
from bisect import bisect_left
from math import sin, cos, sqrt, pi, ceil
import Rhino.Geometry as rg
import scriptcontext as sc
from System.Drawing import Color
try:
    import numpy as np
except ImportError:
    np = None

TAU = 2.0*pi
_CACHE_KEY = 'cdf_assignment21_local_spheres_v1'
PALETTE = ((8,124,141),(40,91,150),(124,80,151))


def _sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def _norm(a): return sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])
def _cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _dist(a,b): return _norm(_sub(a,b))


class _Random:
    """The same deterministic LCG used by the presentation construction."""
    def __init__(self,seed): self.state=int(seed)&0xffffffff
    def next(self):
        self.state=(1664525*self.state+1013904223)&0xffffffff
        return self.state/4294967296.0


def _stations(points,b):
    cumulative=[0.0]
    for p,q in zip(points[:-1],points[1:]):
        cumulative.append(cumulative[-1]+_dist(p,q))
    total=cumulative[-1]
    nodes=[points[0]]
    for i in range(1,b):
        station=total*i/b
        j=max(1,bisect_left(cumulative,station))
        f=(station-cumulative[j-1])/(cumulative[j]-cumulative[j-1])
        nodes.append(tuple(points[j-1][k]*(1-f)+points[j][k]*f for k in range(3)))
    nodes.append(points[-1])
    return nodes


def _replacement(P,Q,branch,rng):
    """Solve a sampled spherical spiral with fixed antipodal endpoints."""
    center=tuple((p+q)*.5 for p,q in zip(P,Q))
    diameter=_dist(P,Q)
    if diameter<1e-10: raise ValueError('A parent part has coincident endpoints.')
    radius=diameter*.5
    axis=tuple((q-p)/diameter for p,q in zip(P,Q))
    z=(0,0,1) if abs(axis[2])<.8 else (0,1,0)
    u=_cross(axis,z); mag=_norm(u); u=tuple(x/mag for x in u)
    v=_cross(axis,u)
    phase=rng.next()*TAU; p1=rng.next()*TAU; p2=rng.next()*TAU
    hand=-1 if rng.next()<.5 else 1
    n=max(512,int(ceil(12.0/radius*35)))
    # Length depends only on polar angles and differences in azimuth.
    # This avoids allocating thousands of 3D points during each bisection.
    if np is not None:
        t=np.arange(n+1,dtype=float)/n
        st=np.sin(pi*t); ct=np.cos(pi*t)
        wiggle=.4*np.sin(TAU*t+p1)+.25*np.sin(3*TAU*t+p2)
        base=np.diff(ct)**2+st[1:]**2+st[:-1]**2
        product=2*st[1:]*st[:-1]
        delta=np.diff(wiggle)
        def measure(omega):
            return float(np.sqrt(np.maximum(0,base-product*np.cos(omega/n+delta))).sum())*radius
    else:
        st=[sin(pi*j/n) for j in range(n+1)]
        ct=[cos(pi*j/n) for j in range(n+1)]
        wiggle=[.4*sin(TAU*j/n+p1)+.25*sin(3*TAU*j/n+p2) for j in range(n+1)]
        base=[(ct[j]-ct[j-1])**2+st[j]**2+st[j-1]**2 for j in range(1,n+1)]
        product=[2*st[j]*st[j-1] for j in range(1,n+1)]
        delta=[wiggle[j]-wiggle[j-1] for j in range(1,n+1)]
        def measure(omega):
            step=omega/n
            return sum(sqrt(max(0,bb-pp*cos(step+dd))) for bb,pp,dd in zip(base,product,delta))*radius
    lo=0.0; hi=max(8.0,24.0/radius)
    if measure(lo)>12: raise ValueError('The sphere cannot fit the target curve length.')
    while measure(hi)<12: hi*=2
    for _ in range(42):
        omega=(lo+hi)*.5
        if measure(omega)<12: lo=omega
        else: hi=omega
    omega=(lo+hi)*.5
    points=[]
    for j in range(n+1):
        t=j/n
        phi=phase+hand*(omega*t+.4*sin(TAU*t+p1)+.25*sin(3*TAU*t+p2))
        radial=sin(pi*t); axial=-cos(pi*t)
        cp=cos(phi); sp=sin(phi)
        points.append(tuple(center[k]+radius*(axis[k]*axial+radial*(u[k]*cp+v[k]*sp)) for k in range(3)))
    points[0]=P; points[-1]=Q
    return {'points':points,'center':center,'radius':radius,'branch':branch,'omega':omega}


def _build(first,second,third,seed):
    factors=(6,first,second,third)
    baseline=[(12.0/TAU*cos(TAU*j/4096),12.0/TAU*sin(TAU*j/4096),0.0) for j in range(4097)]
    baseline[-1]=baseline[0]
    records=[[{'points':baseline,'branch':0}]]
    rng=_Random(seed)
    for depth,b in enumerate(factors):
        current=[]
        for parent in records[-1]:
            nodes=_stations(parent['points'],b)
            for i in range(b):
                current.append(_replacement(nodes[i],nodes[i+1],i if depth==0 else parent['branch'],rng))
        records.append(current)
    pieces=[]; joined=[]
    for group in records:
        curves=[rg.PolylineCurve([rg.Point3d(*p) for p in c['points']]) for c in group]
        pieces.append(curves)
        if len(curves)==1:
            joined.append(curves[0])
        else:
            whole=rg.PolyCurve()
            for c in curves: whole.Append(c)
            joined.append(whole)
    return records,pieces,joined


def build_spherical_crochet(a=12.0,first=5,second=8,third=5,seed=23,layer=4):
    """Return selected preview, all five closed courses, and local-sphere data.

    NumPy accelerates the solver when present; a standard-Python fallback
    gives the same result. Cache is in memory only, never a file dependency.
    """
    a=float(a); first=int(first); second=int(second); third=int(third); layer=int(layer)
    if a<=0 or min(first,second,third)<2 or not 0<=layer<=4:
        raise ValueError('Use a>0, growth factors>=2, and layer 0..4.')
    key=(first,second,third,int(seed))
    cache=sc.sticky.get(_CACHE_KEY,{})
    if key not in cache:
        cache={key:_build(*key)}
        sc.sticky[_CACHE_KEY]=cache
    records,pieces,joined=cache[key]
    factor=a/12.0
    xform=rg.Transform.Scale(rg.Point3d.Origin,factor)
    def scaled(c):
        if factor==1.0: return c
        out=c.DuplicateCurve(); out.Transform(xform); return out
    geometry=[scaled(c) for c in pieces[layer]]
    colors=[Color.FromArgb(*PALETTE[c['branch']%3]) for c in records[layer]]
    courses=[scaled(c) for c in joined]
    stitches=[c.PointAtStart for c in geometry]
    counts=[len(c) for c in pieces]
    lengths=[c.GetLength() for c in courses]
    spheres=[rg.Sphere(rg.Point3d(*(factor*x for x in c['center'])),c['radius']*factor) for c in records[layer] if 'center' in c]
    return geometry,colors,courses,stitches,counts,lengths,spheres,records


if all(name in globals() for name in ('a','first','second','third','seed','layer')):
    geometry,colors,courses,stitches,counts,lengths,spheres,records=build_spherical_crochet(a,first,second,third,seed,layer)
    print('Layer 0 is the original circle. Counts: '+ ' / '.join(map(str,counts)))
    print('Lengths: '+ ' / '.join('{:.4f}'.format(x) for x in lengths))
    print('Selected layer {}: {} curves. Each new curve length = a = {}.'.format(int(layer),len(geometry),a))
    print('Each local sphere diameter is its parent part endpoint chord.')
