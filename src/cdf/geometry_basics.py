"""
Geometry basics -- reusable Rhino.Geometry functions for Grasshopper.

Adding a new function with Copilot
-----------------------------------
1. Open this file and select this chat model, then ask Copilot something like:
   "Add a function here, all in Rhino geometry, that builds a <your shape/idea>.
   Follow the same style as create_cone / create_fractal_tree (defaults for
   optional inputs, a docstring listing params, return a Rhino.Geometry object)."
2. Once the function is added, ask Copilot:
   "Give me the Python code to use this function in a Grasshopper GHPython 3
   component, importing it from computational_design_and_fabrication."
3. Copy the snippet Copilot gives you into a GHPython component, wire up the
   inputs as sliders/panels, and set the output variable (e.g. `a`).
"""

import math
import Rhino.Geometry as rg

def create_cone(base_point=None, height=10.0, radius=5.0, cap_bottom=True):
    """
    Build a cone as a Brep.

    base_point : Rhino.Geometry.Point3d -- center of the cone's base circle
    height     : float -- cone height along the base plane's normal (Z by default)
    radius     : float -- base circle radius
    cap_bottom : bool  -- whether to cap the base circle (closed vs open cone)

    Returns a Rhino.Geometry.Brep.
    """
    if base_point is None:
        base_point = rg.Point3d(0, 0, 0)

    plane = rg.Plane(base_point, rg.Vector3d.ZAxis)
    cone = rg.Cone(plane, height, radius)
    return cone.ToBrep(cap_bottom)

def create_sphere():
    pass  # TODO: Implement this function to create a sphere using Rhino.Geometry

def boolean_difference(brep_a, brep_b):
    """
    Perform a boolean difference operation between two Breps.

    brep_a : Rhino.Geometry.Brep -- the first Brep
    brep_b : Rhino.Geometry.Brep -- the second Brep to subtract from the first

    Returns a list of Rhino.Geometry.Brep resulting from the difference.
    """
    if brep_a is None or brep_b is None:
        raise ValueError("Both brep_a and brep_b must be provided.")

    result = rg.Brep.CreateBooleanDifference(brep_a, brep_b, 0.001)
    return result


def copy_brep_along_z(brep, distance, copy_count):
    """
    Create copies of a Brep, each offset in the +Z direction.

    brep : Rhino.Geometry.Brep -- the Brep to copy
    distance : float -- the Z spacing between consecutive copies
    copy_count : int -- the number of copies to create

    Returns a list of Rhino.Geometry.Brep copies; copy i is moved by distance * (i + 1).
    """
    if brep is None:
        raise ValueError("brep must be provided.")
    if copy_count < 0:
        raise ValueError("copy_count must not be negative.")

    copies = []
    for i in range(1, int(copy_count) + 1):
        copy = brep.DuplicateBrep()
        copy.Transform(rg.Transform.Translation(rg.Vector3d(0, 0, distance * i)))
        copies.append(copy)
    return copies

def create_cloud_city(building_count=9, density=.85, building_size=1, height_jitter=4, seed=12, island_depth=1.15, orb_size=1, dome_height=1, levels=5, spread=2, twist=-16, model_scale=1):
    """Build the floating city. Return geometry, colors and named connection pairs.

    The twelve controls are documented in parameters/controls.json.
    Counts include three core towers and optional satellite districts.
    """
    """CLOUD CITY LAB / Twelve Controls. CDF Assignment 01.
    Inputs: levels 3..6 controls crown elevation; spread 0..8 controls east bridge span;
    twist -20..25 rotates the roof pavilion. Same code generates all three presets.
    RhinoCommon Breps only; composition study inspired by Monument Valley.
    """
    import math
    import Rhino.Geometry as rg
    from System.Drawing import Color
    levels=max(3,min(6,int(round(float(levels)))))
    spread=max(0,min(8,float(spread)))
    twist=max(-20,min(25,float(twist)))
    # Independent exposed controls; the seed makes the same settings reproducible.
    import random
    building_count=max(3,min(15,int(round(float(building_count)))))
    density=max(.35,min(1.0,float(density)))
    building_size=max(.65,min(1.5,float(building_size)))
    height_jitter=max(0,min(6,float(height_jitter)))
    seed=max(0,min(99,int(round(float(seed)))))
    island_depth=max(.6,min(1.6,float(island_depth)))
    orb_size=max(.6,min(1.5,float(orb_size)))
    dome_height=max(.6,min(1.5,float(dome_height)))
    model_scale=max(.5,min(2,float(model_scale)))
    rng=random.Random(seed)
    geometry,colors,connections=[],[],[]
    rock_parts={}
    boolean_count=[0]
    P=[Color.FromArgb(197,76,63),Color.FromArgb(225,174,58),Color.FromArgb(52,94,153),Color.FromArgb(53,64,74),Color.FromArgb(235,226,205)]
    H=12+2*levels
    X=8+.32*spread
    
    def box(x,y,z,w,d,h):
        return rg.Box(rg.Plane(rg.Point3d(x,y,z),rg.Vector3d.ZAxis),rg.Interval(0,w),rg.Interval(0,d),rg.Interval(0,h)).ToBrep()
    def cyl(x,y,z,r,h,axis=rg.Vector3d.ZAxis):
        return rg.Cylinder(rg.Circle(rg.Plane(rg.Point3d(x,y,z),axis),r),h).ToBrep(True,True)
    def add(b,c,angle=0,pivot=None):
        if angle:b.Transform(rg.Transform.Rotation(math.radians(angle),rg.Vector3d.ZAxis,pivot or rg.Point3d.Origin))
        if not b or not b.IsValid or not b.IsSolid:raise ValueError('Open or invalid solid')
        geometry.append(b);colors.append(P[c]);return b
    def cut(a,b):
        r=rg.Brep.CreateBooleanDifference(a,b,.001)
        if not r or len(r)!=1:raise ValueError('Boolean cut failed')
        boolean_count[0]+=1;return r[0]
    def join(parts):
        r=rg.Brep.CreateBooleanUnion(parts,.001)
        if not r or len(r)!=1:raise ValueError('Terrace union failed')
        return r[0]
    def portal(body,x,y,z,w,h,depth):
        r=w/2
        body=cut(body,box(x-r,y,z-.2,w,depth,h-r+.2))
        return cut(body,cyl(x,y,z+h-r,r,depth,rg.Vector3d.YAxis))
    def strut(a,b,r=.12,c=3):
        a,b=rg.Point3d(*a),rg.Point3d(*b)
        axis=b-a
        return add(rg.Cylinder(rg.Circle(rg.Plane(a,axis),r),axis.Length).ToBrep(True,True),c)
    def stair_y(x,y,z,w,run,rise,n,c=1):
        for k in range(n):
            add(box(x,y+k*run/n,z+rise*k/n-.16,w,run/n+.025,rise/n+.16),c)
        for offset in [.22,w-.22]:strut((x+offset,y,z-.2),(x+offset,y+run,z+rise-.2))
    def stair_x(x,y,z,w,run,rise,n,c=1):
        for k in range(n):
            add(box(x+k*run/n,y,z+rise*k/n-.16,run/n+.025,w,rise/n+.16),c)
        for offset in [.22,w-.22]:strut((x,y+offset,z-.2),(x+run,y+offset,z+rise-.2))
    # Independent island caps leave real voids beneath the paths and between the towers.
    def island(cx,cy,z,rx,ry,depth,c=3,shift=0):
        depth*=island_depth
        coords=[(-1,-.65),(-.82,-1),(.82,-1),(1,-.65),(1,.65),(.82,1),(-.82,1),(-1,.65)]
        def ring(height,factor,offset=0):
            pts=[rg.Point3d(cx+rx*x*factor+offset,cy+ry*y*factor,height) for x,y in coords]
            pts.append(pts[0]);return rg.PolylineCurve(pts)
        loop=ring(z-.5,1)
        cap=add(rg.Extrusion.Create(loop,.6,True).ToBrep(),4)
        sections=[ring(z-.5,.98),ring(z-depth*.4,.70,shift*.3),ring(z-depth,.075,shift)]
        rock=rg.Brep.CreateFromLoft(sections,rg.Point3d.Unset,rg.Point3d.Unset,rg.LoftType.Straight,False)
        if not rock or len(rock)!=1:raise ValueError('Island loft failed')
        rock_parts[(cx,cy)]=add(rock[0].CapPlanarHoles(.001),c)
        return cap
    west_island=island(-8,3,0,4.4,4.2,6.4,0,-.5)
    main_island=island(4,6,0,4.7,4.5,9+levels*.4,2,.8)
    east_island=island(X+2.25,.25,0,3.5,3.7,5.6,3,.5)
    front_island=island(X/2+.05,-5.45,0,(X+9.1)/2+.85,2.05,4.3,0,-.7)
    arrival_island=island(-9.5,-9.6,0,2.3,1.7,3.3,3,.4)
    # West gate / first destination at level 10.
    west=portal(box(-11,0,0,6,6,9.85),-8,-.5,0,3,6.8,7)
    west=add(west,0)
    west_deck=add(box(-11.4,-.25,9.75,6.8,6.6,.5),4)
    connections.extend([('West tower / terrace',west,west_deck),('West tower / island',west,west_island)])
    stair_y(-11,-10,0,3,10.05,10.25,22)
    # Main arch tower; the upper oculus is a genuine through-hole.
    main=portal(box(1,3,0,6,6,H-.15),4,2.5,0,3.2,7.6,7)
    main=cut(main,cyl(4,2.5,H-3.4,1.2,7,rg.Vector3d.YAxis))
    main=cut(main,rg.Sphere(rg.Point3d(4,2.75,.55*H),2.15).ToBrep())
    main=add(main,4)
    main_deck=add(box(.65,2.65,H-.25,6.7,6.7,.55),0)
    connections.extend([('Main tower / crown',main,main_deck),('Main tower / island',main,main_island)])
    # East gate: a narrower tower establishes a lower counterpoint.
    east=portal(box(X,-2.5,0,4.5,5.5,9.85),X+2.25,-3,0,2.4,6.6,6.5)
    east=add(east,2)
    east_deck=add(box(X-.35,-2.85,9.75,7.3,6.2,.5),4)
    connections.extend([('East tower / terrace',east,east_deck),('East tower / island',east,east_island)])
    # An L-shaped continuous bridge ties all three gates around the open court.
    bridge=add(join([box(-5.25,4,9.75,X+7.55,2.1,.5),box(X,2.65,9.75,2.3,3.45,.5),box(-5.3,6.05,9.75,6.6,2.65,.5)]),2)
    connections.extend([('Bridge / west terrace',bridge,west_deck),('Bridge / main tower',bridge,main),('Bridge / east terrace',bridge,east_deck)])
    # A second flight turns ninety degrees, climbing from the gate to the crown.
    stair_x(-5,6.1,10.25,2.45,6.05,H+.3-10.25,18)
    # Front arcade and its walkable roof reconnect the lower composition.
    arcade=box(-4.5,-7,0,X+9.1,3.1,4.7)
    for j in range(4):
        x=-2.5+j*(X+5.5)/3
        arcade=portal(arcade,x,-7.5,0,2.35,3.9,4.1)
    arcade=add(arcade,0)
    front=add(box(-4.75,-7.25,4.6,X+11.65,4.9,.4),4)
    connections.extend([('Arcade / island',arcade,front_island),('Arcade / front terrace',arcade,front),('Front terrace / east tower',front,east)])
    stair_y(X+4.6,-4.5,5,2.15,7.7,5.25,16)
    # Low parapets frame the routes without masking the stair profiles.
    add(box(-4.75,-7.25,5,X+9,.22,.6),2)
    add(box(-11.4,5.9,10.25,5.6,.22,.55),0)
    add(box(X+6.6,-2.75,10.25,.22,5.8,.55),0)
    add(box(-5.1,4,10.25,5.9,.2,.45),2)
    # Roof belvedere: a hollow gate with a small stepped canopy, rotated parametrically.
    pivot=rg.Point3d(4,6,H+.3)
    pav=portal(box(2.2,4.7,H+.3,3.6,2.9,4.7),4,4.2,H+.3,2,3.8,3.9)
    add(pav,4,twist,pivot)
    def dome(cx,cy,z,r,sx,sy,sz,c):
        b=rg.Sphere(rg.Point3d(cx,cy,z),r).ToBrep()
        # Convert analytic sphere surfaces/edges to deformable NURBS before affine scaling.
        # This keeps the elliptical cut edge coincident with the scaled sphere surface.
        b.MakeDeformable()
        b.Transform(rg.Transform.Scale(rg.Plane(rg.Point3d(cx,cy,z),rg.Vector3d.ZAxis),sx,sy,sz))
        b=cut(b,box(cx-2*r,cy-2*r,z-2*r,4*r,4*r,2*r-.12))
        return add(b,c)
    main_dome=dome(4,6,H+5,2.8,1,.87,.67*dome_height,2)
    connections.append(('Main pavilion / dome',pav,main_dome))
    add(rg.Sphere(rg.Point3d(4,6,H+5+2.8*.67*dome_height+.17*orb_size),.37*orb_size).ToBrep(),1)
    # A small red gate on the west roof makes the route's first pause legible.
    small=portal(box(-10.7,2.8,10.25,4.7,2.1,4.2),-8.35,2.4,10.25,2.1,3.45,2.9)
    add(small,4)
    west_dome=dome(-8.35,3.85,14.45,2.9,1,.66,.58*dome_height,0)
    connections.append(('West pavilion / dome',small,west_dome))
    # Circular disc and repeated blocks retain Bauhaus geometry within the new spatial language.
    sphere_base=add(cyl(X+2.25,.5,10.2,.85,.7),3)
    east_sphere=add(rg.Sphere(rg.Point3d(X+2.25,.5,10.35+1.9*orb_size),1.9*orb_size).ToBrep(),1)
    connections.extend([('East sphere / pedestal',east_sphere,sphere_base),('Pedestal / east terrace',sphere_base,east_deck)])
    # One small unbridged island keeps the surrounding void legible.
    island(1,-11,-3,1.5,1.3,2.4,3,.25)
    add(rg.Sphere(rg.Point3d(1,-11,-2.95+.8*orb_size),.8*orb_size).ToBrep(),2)
    # A suspended orb under the deepest island is an abstract levitation motif.
    orb_z=-(9+levels*.4)*island_depth-3.5
    add(rg.Sphere(rg.Point3d(4.8,6,orb_z),1.15*orb_size).ToBrep(),1)
    add(rg.Torus(rg.Plane(rg.Point3d(4.8,6,orb_z),rg.Vector3d(.25,.4,1)),1.9*orb_size,.11*orb_size).ToBrep(),2)
    # True circular arcs form an extruded crescent deck across the court.
    def crescent(left,right,y,z,width,height,c):
        radius=(right-left)/2
        plane=rg.Plane(rg.Point3d((left+right)/2,y,z),rg.Vector3d(-1,0,0),rg.Vector3d(0,-1,0))
        outer=rg.Arc(plane,radius+width/2,math.pi).ToNurbsCurve()
        inner=rg.Arc(plane,radius-width/2,math.pi).ToNurbsCurve()
        inner.Reverse()
        edges=[outer,rg.LineCurve(outer.PointAtEnd,inner.PointAtStart),inner,rg.LineCurve(inner.PointAtEnd,outer.PointAtStart)]
        loop=rg.Curve.JoinCurves(edges,.001)[0]
        return add(rg.Extrusion.Create(loop,height,True).ToBrep(),c)
    curved_bridge=crescent(-5.6,X+1.1,3.2,9.9,1.35,.4,2)
    connections.extend([('Curved bridge / west terrace',curved_bridge,west_deck),('Curved bridge / east terrace',curved_bridge,east_deck)])
    # A thin barrel shell contrasts with the solid stair masses below.
    vault=cyl(-3.7,-5,7.2,2.25,6.6,rg.Vector3d.XAxis)
    vault=cut(vault,cyl(-3.8,-5,7.2,1.96,6.8,rg.Vector3d.XAxis))
    vault=cut(vault,box(-4,-8,2,7.2,6,5.15))
    vault=add(vault,4)
    for px in [-3.4,2.6]:
        for py in [-7.12,-2.88]:
            post=add(cyl(px,py,4.95,.16,2.4),2)
            connections.extend([('Canopy post / front terrace',post,front),('Vault / canopy post',vault,post)])
    # Count, packing density, footprint and elevation affect complete satellite districts.
    # Each roof bridge is generated from the resulting elevations, rather than moved afterward.
    def roof_bridge(start,end,width=1.05):
        ax,ay,az=start;bx,by,bz=end
        dx,dy=bx-ax,by-ay
        length=math.sqrt(dx*dx+dy*dy)
        nx,ny=-dy/length*width/2,dx/length*width/2
        pts=[rg.Point3d(ax+nx,ay+ny,az-.3),rg.Point3d(ax-nx,ay-ny,az-.3),rg.Point3d(bx-nx,by-ny,bz-.3),rg.Point3d(bx+nx,by+ny,bz-.3),rg.Point3d(ax+nx,ay+ny,az),rg.Point3d(ax-nx,ay-ny,az),rg.Point3d(bx-nx,by-ny,bz),rg.Point3d(bx+nx,by+ny,bz)]
        return add(rg.Brep.CreateFromBox(pts),4)
    angles=[180,0,-125,125,-55,55,-155,155,-25,25,-90,90]
    extra=building_count-3
    radius_x=max(19.5,extra*3.7*building_size/math.pi)/math.sqrt(density)
    radius_y=radius_x*.77
    satellite_centers=[]
    for j in range(extra):
        a=math.radians(angles[j])
        cx=1.5+radius_x*math.cos(a)
        cy=radius_y*math.sin(a)
        base_z=3.5+height_jitter*rng.uniform(-1,1)
        s=building_size
        w=3.1*s;d=(2.7+.25*rng.random())*s
        h=(5.6+.8*rng.random())*s
        cap=island(cx,cy,base_z,2.3*s,2.35*s,(4.5+.5*rng.random())*s,j%3,.25*s)
        body=portal(box(cx-w/2,cy-d/2,base_z,w,d,h),cx,cy-d/2-.3,base_z,1.5*s,min(h-.6*s,4.2*s),d+.6)
        body=add(body,4 if j%2==0 else 2)
        roof_z=base_z+h-.1*s
        roof=add(box(cx-w/2-.35*s,cy-d/2-.35*s,roof_z,w+.7*s,d+.7*s,.45*s),2 if j%2==0 else 4)
        connections.extend([('District %d / island'%j,body,cap),('District %d / roof'%j,body,roof)])
        if j%3==0:
            crown=dome(cx,cy,roof_z+.45*s,1.5*s,1,.9,.58*dome_height,0)
            connections.append(('District %d / dome'%j,roof,crown))
        else:
            r=.5*s*orb_size
            pedestal=add(cyl(cx,cy,roof_z+.4*s,.3*s,.35*s),3)
            orb=add(rg.Sphere(rg.Point3d(cx,cy,roof_z+.62*s+r),r).ToBrep(),1)
            connections.extend([('District %d / finial base'%j,roof,pedestal),('District %d / finial'%j,pedestal,orb)])
        if math.cos(a)<-.4:
            anchor=west_deck;start=(-8,3,10.18)
        elif math.cos(a)>.4:
            anchor=east_deck;start=(X+3,.25,10.18)
        elif cy>0:
            anchor=main_deck;start=(4,6,H+.23)
        else:
            anchor=front;start=(3,-5.4,4.93)
        vx,vy=cx-start[0],cy-start[1]
        distance=math.sqrt(vx*vx+vy*vy)
        end=(cx-vx/distance*1.5*s,cy-vy/distance*1.5*s,roof_z+.38*s)
        link=roof_bridge(start,end,max(.65,1.05*s))
        connections.extend([('District %d / lane'%j,roof,link),('District %d / main anchor'%j,anchor,link)])
        satellite_centers.append((cx,cy,base_z))
    # Root-like curved tendrils remain beneath the island, clear of the walkways.
    for dx,dy in [(-1.5,-.8),(1.5,.9),(.2,-1.5)]:
        pts=[rg.Point3d(4+dx,6+dy,-4.8*island_depth),rg.Point3d(4+dx*1.6,6+dy*1.3,-7*island_depth),rg.Point3d(4.8+dx*.8,6+dy*.6,-(9+levels*.4)*island_depth+.3),rg.Point3d(4.8+dx*.3,6+dy*.2,orb_z+.6)]
        rail=rg.Curve.CreateInterpolatedCurve(pts,3)
        pipes=rg.Brep.CreatePipe(rail,.15,False,rg.PipeCapMode.Round,True,.001,.1)
        if not pipes:raise ValueError('Root pipe failed')
        for pipe in pipes:add(pipe,3)
    # A thin circular rim picks out the main island's upper terrace.
    add(rg.Torus(rg.Plane(rg.Point3d(4,6,-.25),rg.Vector3d.ZAxis),5.25,.11).ToBrep(),1)
    for j in range(4):
        t=math.radians(45+90*j)
        strut((4+3.5*math.cos(t),6+3.5*math.sin(t),-1),(4+5.25*math.cos(t),6+5.25*math.sin(t),-.25),.1,3)
    # Uniform final scaling changes the entire composition while retaining all joints.
    if abs(model_scale-1)>1e-10:
        transform=rg.Transform.Scale(rg.Point3d.Origin,model_scale)
        for geo in geometry:geo.Transform(transform)
    return {"geometry": geometry, "colors": colors, "connections": connections}

# ---------------------------------------------------------------------------
# CLOUD CITY v2 - one grammar, three hollow styles, seeded satellites + bridges
# ---------------------------------------------------------------------------

def create_cloud_city_v2(style=0, levels=6, void_ratio=.45,
                         satellite_count=6, ring_radius=22, satellite_size=.7,
                         height_variation=.5, seed=12, bridge_width=1.0,
                         island_depth=1.0, detail=2, model_scale=1.0):
    """Bauhaus floating city: one central tower, ring gallery, seeded satellites.

    style 0 = arch / Rundbogen, 1 = oculus / Okulus, 2 = split / Riss.
    Height drives the opening rhythm through t = (bay+0.5)/levels.
    Returns geometry, per-brep colors, named connection pairs and a text report.
    """
    import math
    import random
    import Rhino.Geometry as rg
    from System.Drawing import Color

    style = int(round(float(style))) % 3
    levels = max(3, min(9, int(round(float(levels)))))
    void_ratio = max(.20, min(.70, float(void_ratio)))
    satellite_count = max(0, min(8, int(round(float(satellite_count)))))
    ring_radius = max(13.0, min(32.0, float(ring_radius)))
    satellite_size = max(.40, min(1.0, float(satellite_size)))
    height_variation = max(0.0, min(1.0, float(height_variation)))
    seed = max(0, min(999, int(round(float(seed)))))
    bridge_width = max(.5, min(1.6, float(bridge_width)))
    island_depth = max(.6, min(1.6, float(island_depth)))
    detail = max(0, min(2, int(round(float(detail)))))
    model_scale = max(.5, min(2.0, float(model_scale)))

    rng = random.Random(seed)
    P = [Color.FromArgb(197, 76, 63), Color.FromArgb(225, 174, 58),
         Color.FromArgb(52, 94, 153), Color.FromArgb(53, 64, 74),
         Color.FromArgb(235, 226, 205)]
    RED, GOLD, BLUE, CHAR, CREAM = 0, 1, 2, 3, 4

    geometry, colors, connections = [], [], []
    report_lines = []

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    def box(x, y, z, w, d, h):
        return rg.Box(rg.Plane(rg.Point3d(x, y, z), rg.Vector3d.ZAxis),
                      rg.Interval(0, w), rg.Interval(0, d), rg.Interval(0, h)).ToBrep()

    def boxc(cx, cy, z, w, d, h):
        return box(cx - w / 2, cy - d / 2, z, w, d, h)

    def cyl(x, y, z, r, h, axis=rg.Vector3d.ZAxis):
        return rg.Cylinder(rg.Circle(rg.Plane(rg.Point3d(x, y, z), axis), r), h).ToBrep(True, True)

    def add(b, c):
        if b is None or not b.IsValid or not b.IsSolid:
            raise ValueError('Invalid or open solid in cloud city v2')
        geometry.append(b)
        colors.append(P[c])
        return b

    def cut(a, b):
        r = rg.Brep.CreateBooleanDifference(a, b, .001)
        if not r or len(r) != 1:
            raise ValueError('Boolean cut failed (%s part)' % (len(r) if r else 0))
        return r[0]

    def arch_cut(body, cx, cy, z0, w, h, depth, along_y=True):
        r = w / 2.0
        if along_y:
            c1 = box(cx - r, cy - depth / 2, z0 - .2, w, depth, h - r + .2)
        else:
            c1 = box(cx - depth / 2, cy - r, z0 - .2, depth, w, h - r + .2)
        body = cut(body, c1)
        if along_y:
            c2 = cyl(cx, cy - depth / 2, z0 + h - r, r, depth, rg.Vector3d.YAxis)
        else:
            c2 = cyl(cx - depth / 2, cy, z0 + h - r, r, depth, rg.Vector3d.XAxis)
        return cut(body, c2)

    def oculus_cut(body, cx, cy, z, r, depth, along_y=True):
        if along_y:
            c = cyl(cx, cy - depth / 2, z, r, depth, rg.Vector3d.YAxis)
        else:
            c = cyl(cx - depth / 2, cy, z, r, depth, rg.Vector3d.XAxis)
        return cut(body, c)

    def niche(body, cx, cy, z0, w, h, tw, side, depth=.35):
        """Shallow arched recess on a solid face (blind arch)."""
        r = w / 2.0
        d = max(.12, depth)
        if side in ('E', 'W'):
            sx = 1 if side == 'E' else -1
            x0 = cx + sx * tw / 2 - d
            c1 = box(x0, cy - r, z0 - .2, d + .10, w, h - r + .2)
            body = cut(body, c1)
            c2 = cyl(x0, cy, z0 + h - r, r, d + .10, rg.Vector3d.XAxis)
            body = cut(body, c2)
        else:
            sy = 1 if side == 'N' else -1
            y0 = cy + sy * tw / 2 - d
            c1 = box(cx - r, y0, z0 - .2, w, d + .10, h - r + .2)
            body = cut(body, c1)
            c2 = cyl(cx, y0, z0 + h - r, r, d + .10, rg.Vector3d.YAxis)
            body = cut(body, c2)
        return body

    def island(cx, cy, top_z, rx, ry, depth, c=CHAR, shift=0.0):
        coords = [(-1, -.65), (-.82, -1), (.82, -1), (1, -.65),
                  (1, .65), (.82, 1), (-.82, 1), (-1, .65)]

        def ring(height, factor, offset=0.0):
            pts = [rg.Point3d(cx + rx * x * factor + offset, cy + ry * y * factor, height) for x, y in coords]
            pts.append(pts[0])
            return rg.PolylineCurve(pts)

        cap = add(rg.Extrusion.Create(ring(top_z - .7, 1.0), .7, True).ToBrep(), CREAM)
        sections = [ring(top_z - .7, .98), ring(top_z - .7 - depth * .38, .72, shift * .3),
                    ring(top_z - .7 - depth, .07, shift)]
        rock = rg.Brep.CreateFromLoft(sections, rg.Point3d.Unset, rg.Point3d.Unset,
                                      rg.LoftType.Straight, False)
        if not rock or len(rock) != 1:
            raise ValueError('Island loft failed')
        rock = rock[0].CapPlanarHoles(.001)
        add(rock, c)
        return cap

    phase = rng.uniform(0, 1)
    bay_h = 3.0
    step = bay_h + .10
    width = 7.4
    base_z = .7
    main_H = levels * step
    ring_z = base_z + max(1.8, .42 * main_H)
    ring_deck = ring_z + .4
    half = width / 2.0

    # ---------------- main island ----------------
    island(0, 0, 0.0, 10.4, 9.6, 9.6 * island_depth, CHAR, .55)
    # low rim / terrace lip
    add(rg.Torus(rg.Plane(rg.Point3d(0, 0, -.06), rg.Vector3d.ZAxis), 9.9, .10).ToBrep(), BLUE)

    # south stair from the island terrace to the main terrace
    for k in range(6):
        add(box(-1.6, -4.2 - (k + 1) * .30, 0, 3.2, .30, .12 + k * .112), CREAM)
    # ---------------- tower grammar ----------------
    def tower(cx, cy, tbase, tw, tbay, n, tstyle, is_main=False, crown_scale=1.0):
        tstep = tbay + .12
        add(boxc(cx, cy, tbase - .28, tw + .7, tw + .7, .28), CREAM)  # plinth
        top = tbase
        for i in range(n):
            z0 = tbase + i * tstep
            top = z0 + tbay + .12
            t = (i + .5) / n
            prof = .70 + .30 * math.sin(2 * math.pi * (t * .9 + phase))
            tpr = 1.0 - .35 * (i / max(1, n - 1))
            twi = tw * tpr
            hwi = twi / 2.0
            if tstyle == 2:
                gap = twi * .36
                sw = (twi - gap) / 2.0
                left = box(cx - hwi, cy - hwi, z0, sw, twi, tbay - .03)
                right = box(cx + gap / 2, cy - hwi, z0, sw, twi, tbay - .03)
                if i == 0:
                    left = arch_cut(left, cx - hwi + sw / 2, cy, z0, min(sw * .62, 1.5), tbay - .55, twi + .8, False)
                    right = arch_cut(right, cx + gap / 2 + sw / 2, cy, z0, min(sw * .62, 1.5), tbay - .55, twi + .8, False)
                if i % 2 == 0:
                    slot_h = min(tbay - 1.0, 2.4 * tpr)
                    lslot = box(cx - hwi - .2, cy - .38, z0 + (tbay - slot_h) / 2, sw + .4, .76, slot_h)
                    rslot = box(cx + gap / 2 - .2, cy - .38, z0 + (tbay - slot_h) / 2, sw + .4, .76, slot_h)
                    left = cut(left, lslot)
                    right = cut(right, rslot)
                add(left, CREAM)
                add(right, CREAM)
                add(box(cx - hwi - .12, cy - hwi - .12, z0 + tbay, sw + .24, twi + .24, .10), CREAM)
                add(box(cx + gap / 2 - .12, cy - hwi - .12, z0 + tbay, sw + .24, twi + .24, .10), CREAM)
                if i % 3 == 0:
                    add(box(cx - hwi - .18, cy - hwi - .18, z0 + tbay + .10, twi + .36, twi + .36, .12), RED)
                if i in (max(1, n // 3), max(2, (2 * n) // 3)):
                    add(boxc(cx, cy, z0 + tbay - .35, twi, .5, .22), CHAR)
            else:
                gate = is_main and i == 0
                if gate:
                    pw = min(1.55, twi * .23)
                    for sx in (-1, 1):
                        for sy in (-1, 1):
                            px = cx + sx * (hwi - pw / 2) - pw / 2
                            py = cy + sy * (hwi - pw / 2) - pw / 2
                            add(box(px, py, z0, pw, pw, tbay - .03), CREAM)
                    for sx in (-1, 1):
                        add(box(cx + sx * (hwi - .35) - .35, cy - hwi, z0 + tbay - .55,
                                .70, 2 * hwi, .52), CREAM)
                else:
                    b = box(cx - hwi, cy - hwi, z0, twi, twi, tbay - .03)
                    along_y = (i % 2 == 0)
                    if tstyle == 0:
                        ow = min(twi * .78, max(twi * .52, 6.4 * (void_ratio / .45) * prof))
                        oh = min(tbay - .30, max(1.6, 2.45 * prof + .22))
                        ow = min(ow, 2 * (oh - .22))
                        b = arch_cut(b, cx, cy, z0, ow, oh, twi + 1.2, along_y)
                        nd = min(.35, twi * .08)
                        if along_y:
                            b = niche(b, cx, cy, z0, ow * .92, oh, twi, 'E', nd)
                            b = niche(b, cx, cy, z0, ow * .92, oh, twi, 'W', nd)
                        else:
                            b = niche(b, cx, cy, z0, ow * .92, oh, twi, 'N', nd)
                            b = niche(b, cx, cy, z0, ow * .92, oh, twi, 'S', nd)
                        add(b, CREAM)
                    else:
                        r = min(twi * .30, max(.42, 2.05 * (void_ratio / .45) * prof), tbay * .40)
                        zc = z0 + tbay * .50
                        b = oculus_cut(b, cx, cy, zc, r, twi + 1.2, along_y)
                        add(b, CREAM)
                add(box(cx - hwi - .10, cy - hwi - .10, z0 + tbay, twi + .20, twi + .20, .08), CREAM)
                if i % 3 == 0:
                    add(box(cx - hwi - .16, cy - hwi - .16, z0 + tbay + .08, twi + .32, twi + .32, .14), RED)
        return top

    # ---------------- crown grammar ----------------
    def crown(cx, cy, z, w, cstyle, scale=1.0):
        if cstyle == 0:
            add(boxc(cx, cy, z, w * .70, w * .70, .85), CREAM)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    add(box(cx + sx * w * .28 - .35, cy + sy * w * .28 - .35, z + .85, .70, .70, 1.75), CREAM)
            add(boxc(cx, cy, z + 2.60, w * .86, w * .86, .28), RED)
            dr = w * .34
            dz = z + 2.88
            dome = rg.Sphere(rg.Point3d(cx, cy, dz), dr).ToBrep()
            dome.MakeDeformable()
            dome.Transform(rg.Transform.Scale(rg.Plane(rg.Point3d(cx, cy, dz), rg.Vector3d.ZAxis), 1, 1, .72))
            dome = cut(dome, box(cx - 2 * dr, cy - 2 * dr, dz - 2 * dr, 4 * dr, 4 * dr, 2 * dr - .15))
            add(dome, BLUE)
            add(rg.Sphere(rg.Point3d(cx, cy, dz + dr * .72 + .18), .19 * scale).ToBrep(), GOLD)
        elif cstyle == 1:
            drum = cyl(cx, cy, z, w * .34, 1.80)
            drum = oculus_cut(drum, cx, cy, z + .90, min(w * .16, .55), w * .9, True)
            add(drum, CREAM)
            add(rg.Torus(rg.Plane(rg.Point3d(cx, cy, z + 1.85), rg.Vector3d.ZAxis), w * .40, .11).ToBrep(), BLUE)
            add(rg.Sphere(rg.Point3d(cx, cy, z + 2.32), w * .17).ToBrep(), GOLD)
        else:
            add(box(cx - w * .50, cy - w * .50, z, w * .46, w, .28), RED)
            add(box(cx + w * .04, cy - w * .50, z + .82, w * .46, w, .28), CREAM)
            add(boxc(cx, cy, z + .18, .12, w * .82, 1.45), CHAR)

    # ---------------- satellite placement (before ring gaps) ----------------
    R_eff = max(ring_radius, 12.5 + satellite_count * .9)
    sats = []
    for i in range(satellite_count):
        a = (i * 137.5 + rng.uniform(-13, 13)) % 360.0
        rad = R_eff + rng.uniform(-2.0, 2.0)
        s = min(1.15, max(.35, satellite_size * rng.uniform(.78, 1.15)))
        for q in sats:
            if math.hypot(rad * math.cos(math.radians(a)) - q['rad'] * math.cos(math.radians(q['a'])),
                          rad * math.sin(math.radians(a)) - q['rad'] * math.sin(math.radians(q['a']))) < 5.2 * max(s, q['s']):
                rad += 2.2
        roof = ring_deck + rng.uniform(-1, 1) * 4.2 * height_variation
        roof = clamp(roof, ring_deck - 4.0, ring_deck + 4.0)
        pav = (i % 3 == 2)
        if pav:
            ns = 1
            bh = 2.55 * s
        else:
            hs = main_H * rng.uniform(.18, .32) * (.70 + .50 * satellite_size)
            ns = max(2, int(round(hs / (2.5 * s))))
            bh = hs / ns
        tw = (4.8 if pav else 4.0) * s
        sats.append({'i': i, 'a': a, 'rad': rad, 's': s, 'roof': roof, 'pav': pav,
                     'ns': ns, 'bh': bh, 'tw': tw, 'x': rad * math.cos(math.radians(a)),
                     'y': rad * math.sin(math.radians(a))})

    # ---------------- main tower + ring ----------------
    add(boxc(0, 0, 0, 9.8, 9.2, .35), CREAM)
    add(boxc(0, 0, .35, 8.8, 8.4, .35), CREAM)
    # low parapet around the lower terrace, with a stair gap on the south
    add(box(-4.9, 4.4, .35, 9.8, .22, .20), CREAM)
    add(box(1.7, -4.6, .35, 3.2, .22, .20), CREAM)
    add(box(-4.9, -4.6, .35, 3.2, .22, .20), CREAM)
    add(box(-4.9, -4.6, .35, .22, 9.2, .20), CREAM)
    add(box(4.68, -4.6, .35, .22, 9.2, .20), CREAM)
    main_top = tower(0, 0, base_z, width, bay_h, levels, style, is_main=True)
    main_w = width * (.65 if levels > 1 else 1.0)
    add(boxc(0, 0, main_top, main_w + .30, main_w + .30, .30), RED)
    crown(0, 0, main_top + .30, main_w, style, 1.0)

    ring = cut(cyl(0, 0, ring_z, 6.25, .55), cyl(0, 0, ring_z - .10, 4.35, .75))
    add(ring, CREAM)
    for a in (0, 90, 180, 270):
        br = box(-.45, 3.05, ring_z - .10, .90, 1.35, .55)
        br.Transform(rg.Transform.Rotation(math.radians(a), rg.Vector3d.ZAxis, rg.Point3d.Origin))
        add(br, CHAR)
    for a in (0, 90, 180, 270):
        t = math.radians(a)
        p0 = rg.Point3d(3.05 * math.cos(t), 3.05 * math.sin(t), ring_z - 2.0)
        p1 = rg.Point3d(4.35 * math.cos(t), 4.35 * math.sin(t), ring_z - .15)
        axis = p1 - p0
        add(rg.Cylinder(rg.Circle(rg.Plane(p0, axis), .16), axis.Length).ToBrep(True, True), CHAR)
    # circular parapet with a low sill, then gaps at bridge angles
    par = cut(cyl(0, 0, ring_deck, 6.26, .55), cyl(0, 0, ring_deck - .12, 6.08, .75))
    for q in sats:
        w = clamp(1.5 * q['s'] * bridge_width, .8, 1.9)
        gap = box(-(w + .55) / 2, 5.60, ring_deck + .10, w + .55, 1.15, .75)
        gap.Transform(rg.Transform.Rotation(math.radians(q['a']), rg.Vector3d.ZAxis, rg.Point3d.Origin))
        par = cut(par, gap)
    add(par, BLUE)

    # ---------------- satellites ----------------
    for q in sats:
        cx, cy, s = q['x'], q['y'], q['s']
        top_island = q['roof'] - q['ns'] * (q['bh'] + .12) - .70
        q['z0'] = top_island
        q['topw'] = q['tw'] * (.65 if q['ns'] > 1 else 1.0)
        island(cx, cy, top_island, max(4.2 * s, q['tw'] * .62), max(4.2 * s, q['tw'] * .62), 4.6 * s * island_depth, CHAR, .40 * s)
        add(boxc(cx, cy, top_island, q['tw'] + .8, q['tw'] + .8, .35), CREAM)
        top_t = tower(cx, cy, top_island + .35, q['tw'], q['bh'], q['ns'], style, is_main=False, crown_scale=s)
        add(boxc(cx, cy, top_t, q['topw'] + .75, q['topw'] + .75, .35), CREAM)
        crown(cx, cy, top_t + .35, q['topw'], style, s)
        # landing deck toward the main tower
        ux, uy = math.cos(math.radians(q['a'])), math.sin(math.radians(q['a']))
        land_d = 1.45
        lc = (cx - ux * (q['topw'] / 2 + land_d / 2), cy - uy * (q['topw'] / 2 + land_d / 2))
        add(boxc(lc[0], lc[1], q['roof'] - .30, q['topw'] * .78 + .6, land_d, .30), CREAM)
        # side rails on the landing (short, keep the bridge mouth open)
        for sign in (-1, 1):
            nx, ny = -uy * sign, ux * sign
            add(boxc(lc[0] + nx * (q['topw'] * .39 + .3), lc[1] + ny * (q['topw'] * .39 + .3),
                     q['roof'], .10, land_d, .38), CREAM)
        if detail >= 1:
            add(rg.Sphere(rg.Point3d(cx, cy, top_island - 3.4 * s), .55 * s).ToBrep(), GOLD)
        if detail >= 1 and not q['pav']:
            sgn = 1 if q['i'] % 2 == 0 else -1
            tx, ty = -uy * sgn, ux * sgn
            ax, ay = cx + tx * (q['tw'] * .95), cy + ty * (q['tw'] * .95)
            ah = q['bh'] * 1.15
            aw = q['tw'] * .62
            for sx in (-1, 1):
                for sy in (-1, 1):
                    add(box(ax + sx * (aw / 2 - .18) - .18, ay + sy * (aw / 2 - .18) - .18,
                            top_island + .35, .36, .36, ah), CREAM)
            add(boxc(ax, ay, top_island + .35 + ah, aw + .25, aw + .25, .22), RED)
            add(rg.Sphere(rg.Point3d(ax, ay, top_island + .35 + ah + .38), .28 * s).ToBrep(), GOLD)

    # ---------------- bridges ----------------
    spans, slopes = [], []
    for q in sats:
        a = math.radians(q['a'])
        ux, uy = math.cos(a), math.sin(a)
        A = rg.Point3d(ux * 7.62, uy * 7.62, ring_deck)
        B = rg.Point3d(q['x'] - ux * (q['topw'] / 2 + 1.45),
                       q['y'] - uy * (q['topw'] / 2 + 1.45), q['roof'])
        span = math.hypot(B.X - A.X, B.Y - A.Y)
        if span < 1.5:
            continue
        spans.append(span)
        slopes.append(math.degrees(math.atan2(abs(B.Z - A.Z), span)))
        w = clamp(1.5 * q['s'] * bridge_width, .8, 1.9)
        deck = None
        dx, dy = B.X - A.X, B.Y - A.Y
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        t = .28

        def quad(p, side, zoff):
            return rg.Point3d(p.X + nx * side * w / 2, p.Y + ny * side * w / 2, p.Z + zoff)

        if style == 2:
            # twin decks with a central slot
            for side in (-1, 1):
                off = side * (w / 4 + .05)
                pts = [rg.Point3d(A.X + nx * (off - w / 4 + .05), A.Y + ny * (off - w / 4 + .05), A.Z - t),
                       rg.Point3d(A.X + nx * (off + w / 4 - .05), A.Y + ny * (off + w / 4 - .05), A.Z - t),
                       rg.Point3d(B.X + nx * (off + w / 4 - .05), B.Y + ny * (off + w / 4 - .05), B.Z - t),
                       rg.Point3d(B.X + nx * (off - w / 4 + .05), B.Y + ny * (off - w / 4 + .05), B.Z - t),
                       rg.Point3d(A.X + nx * (off - w / 4 + .05), A.Y + ny * (off - w / 4 + .05), A.Z),
                       rg.Point3d(A.X + nx * (off + w / 4 - .05), A.Y + ny * (off + w / 4 - .05), A.Z),
                       rg.Point3d(B.X + nx * (off + w / 4 - .05), B.Y + ny * (off + w / 4 - .05), B.Z),
                       rg.Point3d(B.X + nx * (off - w / 4 + .05), B.Y + ny * (off - w / 4 + .05), B.Z)]
                d0 = add(rg.Brep.CreateFromBox(pts), CREAM)
                if deck is None:
                    deck = d0
                # outer parapet
                side2 = 1 if off > 0 else -1
                edge = off + side2 * (w / 4 - .05)
                pp = [rg.Point3d(A.X + nx * (edge - .06), A.Y + ny * (edge - .06), A.Z),
                      rg.Point3d(A.X + nx * (edge + .06), A.Y + ny * (edge + .06), A.Z),
                      rg.Point3d(B.X + nx * (edge + .06), B.Y + ny * (edge + .06), B.Z),
                      rg.Point3d(B.X + nx * (edge - .06), B.Y + ny * (edge - .06), B.Z),
                      rg.Point3d(A.X + nx * (edge - .06), A.Y + ny * (edge - .06), A.Z + .55),
                      rg.Point3d(A.X + nx * (edge + .06), A.Y + ny * (edge + .06), A.Z + .55),
                      rg.Point3d(B.X + nx * (edge + .06), B.Y + ny * (edge + .06), B.Z + .55),
                      rg.Point3d(B.X + nx * (edge - .06), B.Y + ny * (edge - .06), B.Z + .55)]
                add(rg.Brep.CreateFromBox(pp), CREAM)
            for p in (A, B):
                add(boxc(p.X, p.Y, p.Z - .34, w, .35, .34), CHAR)
        else:
            pts = [quad(A, -1, -t), quad(A, 1, -t), quad(B, 1, -t), quad(B, -1, -t),
                   quad(A, -1, 0), quad(A, 1, 0), quad(B, 1, 0), quad(B, -1, 0)]
            deck = add(rg.Brep.CreateFromBox(pts), CREAM)
            for side in (-1, 1):
                pp = [quad(A, side, 0), quad(A, side + .0, 0), quad(B, side, 0), quad(B, side, 0),
                      quad(A, side, .55), quad(A, side, .55), quad(B, side, .55), quad(B, side, .55)]
                # build a proper thin parapet from two offset planes
                e0 = side * (w / 2 - .06)
                e1 = side * (w / 2 + .06)
                pp = [rg.Point3d(A.X + nx * e0, A.Y + ny * e0, A.Z),
                      rg.Point3d(A.X + nx * e1, A.Y + ny * e1, A.Z),
                      rg.Point3d(B.X + nx * e1, B.Y + ny * e1, B.Z),
                      rg.Point3d(B.X + nx * e0, B.Y + ny * e0, B.Z),
                      rg.Point3d(A.X + nx * e0, A.Y + ny * e0, A.Z + .55),
                      rg.Point3d(A.X + nx * e1, A.Y + ny * e1, A.Z + .55),
                      rg.Point3d(B.X + nx * e1, B.Y + ny * e1, B.Z + .55),
                      rg.Point3d(B.X + nx * e0, B.Y + ny * e0, B.Z + .55)]
                if style == 0:
                    add(rg.Brep.CreateFromBox(pp), CREAM)
                    rail = [rg.Point3d(A.X + nx * e0, A.Y + ny * e0, A.Z + .54),
                            rg.Point3d(A.X + nx * e1, A.Y + ny * e1, A.Z + .54),
                            rg.Point3d(B.X + nx * e1, B.Y + ny * e1, B.Z + .54),
                            rg.Point3d(B.X + nx * e0, B.Y + ny * e0, B.Z + .54),
                            rg.Point3d(A.X + nx * e0, A.Y + ny * e0, A.Z + .64),
                            rg.Point3d(A.X + nx * e1, A.Y + ny * e1, A.Z + .64),
                            rg.Point3d(B.X + nx * e1, B.Y + ny * e1, B.Z + .64),
                            rg.Point3d(B.X + nx * e0, B.Y + ny * e0, B.Z + .64)]
                    add(rg.Brep.CreateFromBox(rail), BLUE)
                else:
                    # oculus style: open balustrade (posts + top rail)
                    for k in range(6):
                        f = (k + .5) / 6.0
                        px = A.X + (B.X - A.X) * f + nx * side * (w / 2 - .06)
                        py = A.Y + (B.Y - A.Y) * f + ny * side * (w / 2 - .06)
                        pz = A.Z + (B.Z - A.Z) * f
                        add(boxc(px, py, pz, .10, .10, .42), CREAM)
                    rail = [rg.Point3d(A.X + nx * e0, A.Y + ny * e0, A.Z + .48),
                            rg.Point3d(A.X + nx * e1, A.Y + ny * e1, A.Z + .48),
                            rg.Point3d(B.X + nx * e1, B.Y + ny * e1, B.Z + .48),
                            rg.Point3d(B.X + nx * e0, B.Y + ny * e0, B.Z + .48),
                            rg.Point3d(A.X + nx * e0, A.Y + ny * e0, A.Z + .56),
                            rg.Point3d(A.X + nx * e1, A.Y + ny * e1, A.Z + .56),
                            rg.Point3d(B.X + nx * e1, B.Y + ny * e1, B.Z + .56),
                            rg.Point3d(B.X + nx * e0, B.Y + ny * e0, B.Z + .56)]
                    add(rg.Brep.CreateFromBox(rail), BLUE)
            if style == 0:
                # shallow arch rib + hangers
                mid = rg.Point3d((A.X + B.X) / 2, (A.Y + B.Y) / 2, (A.Z + B.Z) / 2 - 1.35)
                curve = rg.Curve.CreateInterpolatedCurve(
                    [rg.Point3d(A.X, A.Y, A.Z - .35), mid, rg.Point3d(B.X, B.Y, B.Z - .35)], 3)
                pipes = rg.Brep.CreatePipe(curve, .11, False, rg.PipeCapMode.Round, True, .001, .1)
                if pipes:
                    for pipe in pipes:
                        add(pipe, CHAR)
                for k in range(1, 5):
                    f = k / 5.0
                    px = A.X + (B.X - A.X) * f
                    py = A.Y + (B.Y - A.Y) * f
                    pz = A.Z + (B.Z - A.Z) * f
                    za = pz - .35 - 1.0 * 4 * f * (1 - f)
                    h = pz - za
                    if h > .05:
                        add(cyl(px, py, za, .055, h), CHAR)
        if deck is not None:
            connections.append(('bridge %d / main ring' % q['i'], deck, ring))
            connections.append(('bridge %d / satellite' % q['i'], deck, None))

    # ---------------- suspended orb under the main island ----------------
    if detail >= 1:
        oz = -9.6 * island_depth - 2.6
        add(rg.Sphere(rg.Point3d(0, 0, oz), 1.05).ToBrep(), GOLD)
        add(rg.Torus(rg.Plane(rg.Point3d(0, 0, oz), rg.Vector3d(.2, .35, 1)), 1.75, .10).ToBrep(), BLUE)
    if detail >= 2:
        for k, (dx, dy, dz) in enumerate([(11.5, -9.0, -4.2), (-12.0, 8.0, -6.0)]):
            if satellite_count and any(math.hypot(dx - q['x'], dy - q['y']) < 4.0 for q in sats):
                continue
            island(dx, dy, dz, 1.5, 1.4, 2.2, CHAR, .2)
            add(rg.Sphere(rg.Point3d(dx, dy, dz + .65), .55).ToBrep(), GOLD)

    # ---------------- uniform scale ----------------
    if abs(model_scale - 1) > 1e-9:
        tr = rg.Transform.Scale(rg.Point3d.Origin, model_scale)
        for g in geometry:
            g.Transform(tr)

    report_lines.append('CLOUD CITY v2')
    report_lines.append('style %d / levels %d / H %.1f / ring z %.1f' % (style, levels, main_H, ring_z))
    report_lines.append('satellites %d / main breps %d' % (satellite_count, len(geometry)))
    if spans:
        report_lines.append('bridge span %.1f-%.1f / max slope %.0f deg' % (min(spans), max(spans), max(slopes)))
    report_lines.append('seed %d / scale %.2f' % (seed, model_scale))
    return {'geometry': geometry, 'colors': colors, 'connections': connections,
            'report': '\n'.join(report_lines), 'sats': sats, 'ring_z': ring_z}

# ---------------------------------------------------------------------------
# SKY CITY v3 - continuous fantasy grammar
# form 0..1 morphs arch -> oculus -> lattice -> bloom
# ---------------------------------------------------------------------------

def create_sky_city(form=.50, levels=6, void_ratio=.45,
                    satellite_count=6, ring_radius=22, satellite_size=.80,
                    height_variation=.50, seed=12, bridge_width=1.0,
                    island_depth=1.0, detail=2, model_scale=1.0):
    import math
    import random
    import Rhino.Geometry as rg
    from System.Drawing import Color

    form = max(0.0, min(1.0, float(form)))
    levels = max(3, min(9, int(round(float(levels)))))
    void_ratio = max(.20, min(.70, float(void_ratio)))
    satellite_count = max(0, min(8, int(round(float(satellite_count)))))
    ring_radius = max(13.0, min(32.0, float(ring_radius)))
    satellite_size = max(.40, min(1.0, float(satellite_size)))
    height_variation = max(0.0, min(1.0, float(height_variation)))
    seed = max(0, min(999, int(round(float(seed)))))
    bridge_width = max(.5, min(1.6, float(bridge_width)))
    island_depth = max(.6, min(1.6, float(island_depth)))
    detail = max(0, min(2, int(round(float(detail)))))
    model_scale = max(.5, min(2.0, float(model_scale)))

    rng = random.Random(seed)
    STONE = Color.FromArgb(228, 220, 205)
    STONE2 = Color.FromArgb(205, 196, 180)
    CHAR = Color.FromArgb(64, 72, 80)
    TEAL = Color.FromArgb(52, 102, 120)
    BLUE = Color.FromArgb(52, 94, 153)
    TERRA = Color.FromArgb(190, 96, 74)
    GOLD = Color.FromArgb(225, 174, 58)
    LIGHT = Color.FromArgb(150, 200, 220)
    GREEN = Color.FromArgb(90, 120, 80)

    geometry, colors, connections = [], [], []
    report = []

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    def interp(f, vals):
        a = [0.0, .33, .66, 1.0]
        f = clamp(f, 0, 1)
        for i in range(3):
            if f <= a[i + 1]:
                t = (f - a[i]) / (a[i + 1] - a[i])
                return vals[i] * (1 - t) + vals[i + 1] * t
        return vals[-1]

    def add(b, c):
        if b is None:
            return None
        if not b.IsValid or not b.IsSolid:
            try:
                b2 = b.CapPlanarHoles(.001)
                if b2 and b2.IsValid and b2.IsSolid:
                    b = b2
            except Exception:
                pass
        if b is None or not b.IsValid or not b.IsSolid:
            return None
        try:
            bb = b.GetBoundingBox(True)
            ds = [bb.Max.X - bb.Min.X, bb.Max.Y - bb.Min.Y, bb.Max.Z - bb.Min.Z]
            if min(ds) < .025 and max(ds) > .40:
                return None
        except Exception:
            pass
        geometry.append(b); colors.append(c); return b

    def cut_one(a, b):
        r = rg.Brep.CreateBooleanDifference(a, b, .001)
        if not r or len(r) != 1:
            raise ValueError('One-part cut failed (%d)' % (len(r) if r else 0))
        return r[0]

    def cut_all(a, b):
        r = rg.Brep.CreateBooleanDifference(a, b, .001)
        if not r:
            raise ValueError('Cut failed')
        out = [x for x in r if x and x.IsValid and x.IsSolid]
        if not out:
            raise ValueError('Cut produced no solid')
        return out

    def box(x, y, z, w, d, h):
        return rg.Box(rg.Plane(rg.Point3d(x, y, z), rg.Vector3d.ZAxis),
                      rg.Interval(0, w), rg.Interval(0, d), rg.Interval(0, h)).ToBrep()

    def boxc(cx, cy, z, w, d, h):
        return box(cx - w / 2, cy - d / 2, z, w, d, h)

    def cyl(x, y, z, r, h, axis=rg.Vector3d.ZAxis):
        return rg.Cylinder(rg.Circle(rg.Plane(rg.Point3d(x, y, z), axis), r), h).ToBrep(True, True)

    def plan_curve(cx, cy, z, hx, hy, n, rot, seg=28):
        pts = []
        ca, sa = math.cos(rot), math.sin(rot)
        for k in range(seg):
            th = 2 * math.pi * k / seg
            c, s = math.cos(th), math.sin(th)
            x = hx * math.copysign(abs(c) ** (2.0 / n), c)
            y = hy * math.copysign(abs(s) ** (2.0 / n), s)
            pts.append(rg.Point3d(cx + x * ca - y * sa, cy + x * sa + y * ca, z))
        pts.append(pts[0])
        return rg.PolylineCurve(pts)

    def rounded_plan(cx, cy, z, hx, hy, r, rot, seg=6):
        r = clamp(r, 0.0, min(hx, hy) * .98)
        ca, sa = math.cos(rot), math.sin(rot)
        pts = []
        corners = [(hx - r, hy - r, 0), (-hx + r, hy - r, 90), (-hx + r, -hy + r, 180), (hx - r, -hy + r, 270)]
        for ccx, ccy, a0 in corners:
            for k in range(seg + 1):
                a = math.radians(a0 + 90.0 * k / seg)
                x, y = ccx + r * math.cos(a), ccy + r * math.sin(a)
                pts.append(rg.Point3d(cx + x * ca - y * sa, cy + x * sa + y * ca, z))
        out = []
        for p in pts:
            if not out or p.DistanceTo(out[-1]) > 1e-6:
                out.append(p)
        if out[0].DistanceTo(out[-1]) > 1e-6:
            out.append(out[0])
        else:
            out[-1] = out[0]
        return rg.PolylineCurve(out)

    def prism(cx, cy, z, hx, hy, n, rot, h, c):
        return add(rg.Extrusion.Create(plan_curve(cx, cy, z, hx, hy, n, rot), h, True).ToBrep(), c)

    def plan_ring(cx, cy, z, rout, rin, nout, nin, rot, h, c):
        outer = rg.Extrusion.Create(plan_curve(cx, cy, z, rout, rout, nout, rot, 40), h, True).ToBrep()
        inner = rg.Extrusion.Create(plan_curve(cx, cy, z - .1, rin, rin, nin, rot, 40), h + .2, True).ToBrep()
        return add(cut_one(outer, inner), c)

    # ---- continuous form parameters -------------------------------------
    aspect = interp(form, [1.50, 1.00, 1.50, .80])
    top_n = interp(form, [2.40, 2.00, 3.00, 1.20])
    bot_n = interp(form, [12.0, 2.00, 8.00, 2.50])
    lobe_amp = interp(form, [0.00, 0.00, 0.06, 0.26])
    plan_n = 2.0
    plan_round = interp(form, [0.05, 0.30, 0.55, 0.85])
    twist_total = interp(form, [0.0, 18.0, 38.0, 58.0])
    lean_amt = interp(form, [0.0, 0.60, 1.50, 2.60])
    slot_factor = interp(form, [0.0, 0.02, 0.22, 0.45])
    crown_flare = interp(form, [0.20, 0.60, 1.20, 1.80])
    crown_h = interp(form, [2.0, 3.2, 4.5, 5.5])
    crown_tw = interp(form, [0.0, 15.0, 30.0, 45.0])
    bow_scale = interp(form, [0.55, 0.75, 1.00, 1.25])
    arch_scale = interp(form, [0.55, 0.75, 1.00, 1.25])
    lean_dir = rng.uniform(0, 2 * math.pi)
    taper = interp(form, [.30, .42, .50, .62])
    phase = rng.uniform(0, 2 * math.pi)
    bay_h = 3.4
    step = bay_h + .10
    width = 7.4
    base_z = 1.25

    # ---- opening profile ------------------------------------------------
    def profile_curve(a, b):
        pts = []
        seg = 48
        for k in range(seg):
            th = 2 * math.pi * k / seg
            c, s = math.cos(th), math.sin(th)
            n = top_n if s >= 0 else bot_n
            x = a * math.copysign(abs(c) ** (2.0 / n), c)
            y = b * math.copysign(abs(s) ** (2.0 / n), s)
            if lobe_amp > 1e-5:
                ang = math.atan2(y / b, x / a)
                r = 1 + lobe_amp * math.cos(5 * ang)
                x *= r; y *= r
            pts.append(rg.Point3d(x, y, 0))
        pts.append(pts[0])
        return rg.PolylineCurve(pts)

    def opening_cut(body, cx, cy, z0, a, b, along_y, rot, depth):
        crv = profile_curve(a, b)
        c = rg.Extrusion.Create(crv, depth, True).ToBrep()
        c.Transform(rg.Transform.Rotation(math.pi / 2, rg.Vector3d.XAxis, rg.Point3d.Origin))
        if along_y:
            c.Transform(rg.Transform.Rotation(math.radians(rot), rg.Vector3d.ZAxis, rg.Point3d.Origin))
            c.Transform(rg.Transform.Translation(cx, cy + depth / 2, z0 + b - .30))
        else:
            c.Transform(rg.Transform.Rotation(math.radians(90 + rot), rg.Vector3d.ZAxis, rg.Point3d.Origin))
            c.Transform(rg.Transform.Translation(cx - depth / 2, cy, z0 + b - .30))
        return cut_one(body, c)

    def cut_parts(parts, cutter):
        flat = []
        for p in parts:
            if isinstance(p, list):
                flat.extend(p)
            else:
                flat.append(p)
        out = []
        for p in flat:
            r = rg.Brep.CreateBooleanDifference(p, cutter, .001)
            if not r:
                out.append(p)
                continue
            out.extend([x for x in r if x and x.IsValid and x.IsSolid])
        if not out:
            return flat
        return out

    def opening_solid(cx, cy, z0, a, b, along_y, rot, depth):
        crv = profile_curve(a, b)
        c = rg.Extrusion.Create(crv, depth, True).ToBrep()
        c.Transform(rg.Transform.Rotation(math.pi / 2, rg.Vector3d.XAxis, rg.Point3d.Origin))
        if along_y:
            c.Transform(rg.Transform.Rotation(math.radians(rot), rg.Vector3d.ZAxis, rg.Point3d.Origin))
            c.Transform(rg.Transform.Translation(cx, cy + depth / 2, z0 + b - .30))
        else:
            c.Transform(rg.Transform.Rotation(math.radians(90 + rot), rg.Vector3d.ZAxis, rg.Point3d.Origin))
            c.Transform(rg.Transform.Translation(cx - depth / 2, cy, z0 + b - .30))
        return c

    def slot_solid(cx, cy, z0, tw, sw, rot, h):
        c = box(-sw / 2, -(tw / 2 + 1.2), z0 - .3, sw, tw + 2.4, h + .6)
        c.Transform(rg.Transform.Rotation(rot, rg.Vector3d.ZAxis, rg.Point3d.Origin))
        c.Transform(rg.Transform.Translation(cx, cy, 0))
        return c

    # ---- tower ----------------------------------------------------------
    def tower(cx, cy, tbase, tw, n, is_main=False, twist_deg=None, lean=None, scale=1.0, bays_h=None):
        twist_d = twist_total if twist_deg is None else twist_deg
        lean_a = lean_amt if lean is None else lean
        bh_local = 3.4 if bays_h is None else bays_h
        step_local = bh_local - .02
        top = tbase
        for i in range(n):
            z0 = tbase + i * step_local
            u = i / max(1, n - 1)
            twi = tw * (1 - taper * u)
            rotd = twist_d * u
            dx = lean_a * (u ** 1.4) * math.cos(lean_dir)
            dy = lean_a * (u ** 1.4) * math.sin(lean_dir)
            bx, by = cx + dx, cy + dy
            b = rg.Extrusion.Create(rounded_plan(bx, by, z0, twi / 2, twi / 2, twi / 2 * plan_round, rotd), bh_local + .08, True).ToBrep()
            a = min(twi * (.07 + .32 * (void_ratio / .70)), twi * .34)
            bhalf = min(a * aspect, (bh_local - .65) / 2)
            a = min(a, bhalf / max(.4, aspect))
            along_y = (i % 2 == 0)
            opened = True
            try:
                cutter = opening_solid(bx, by, z0, a, bhalf, along_y, rotd, twi + 1.8)
                try:
                    b = cut_one(b, cutter)
                except ValueError:
                    b = cut_parts([b], cutter)
            except Exception:
                opened = False
            if opened and a > .55 and bhalf > .45:
                mw, mh = .16, 2 * bhalf - .45
                md = twi * .72
                if along_y:
                    add(boxc(bx, by, z0 + .22, mw, md, mh), CHAR)
                else:
                    add(boxc(bx, by, z0 + .22, md, mw, mh), CHAR)
            sw = twi * slot_factor * (1.0 if is_main else .35)
            if sw > .07 and i < n - 2:
                parts_b = b if isinstance(b, list) else [b]
                b = cut_parts(parts_b, slot_solid(bx, by, z0, twi, sw, rotd, bh_local))
            for part in (b if isinstance(b, list) else [b]):
                add(part, STONE)
            # light stone cornice + occasional teal accent, no dark eaves
            corn = rg.Extrusion.Create(rounded_plan(bx, by, z0 + bh_local, twi / 2 + .09, twi / 2 + .09, (twi / 2 + .09) * plan_round, rotd), .06, True).ToBrep()
            if sw > .07 and i < n - 2:
                corn = cut_parts([corn], slot_solid(bx, by, z0 + bh_local, twi, sw, rotd, .06))
            for part in (corn if isinstance(corn, list) else [corn]):
                add(part, STONE2)
            if i % 3 == 0:
                ring = rg.Extrusion.Create(rounded_plan(bx, by, z0 + bh_local + .06, twi / 2 + .10, twi / 2 + .10, (twi / 2 + .10) * plan_round, rotd), .025, True).ToBrep()
                add(ring, TEAL)
            top = z0 + bh_local + .08
        top_w = tw * (1 - taper)
        top_cx = cx + lean_a * math.cos(lean_dir)
        top_cy = cy + lean_a * math.sin(lean_dir)
        return top, top_w, top_cx, top_cy, twist_d

    # ---- crown ----------------------------------------------------------
    def crown(cx, cy, z, w, rot, s=1.0):
        # tapered cap + neck: no spikes, no fins
        cap = rg.Brep.CreateFromLoft([rounded_plan(cx, cy, z - .01, w * .55, w * .55, w * .28, math.radians(rot)),
                                      rounded_plan(cx, cy, z + 1.10, w * .38, w * .38, w * .19, math.radians(rot))],
                                     rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
        if cap and len(cap) == 1:
            add(cap[0].CapPlanarHoles(.001), STONE)
        nb = rounded_plan(cx, cy, z + 1.10, w * .38, w * .38, w * .19, math.radians(rot))
        nt = rounded_plan(cx, cy, z + 1.65, w * .30, w * .30, w * .15, math.radians(rot))
        neck = rg.Brep.CreateFromLoft([nb, nt], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
        if neck and len(neck) == 1:
            add(neck[0].CapPlanarHoles(.001), STONE2)
        zc = z + 1.65
        if s < .95:
            # satellite / side tower: flat faceted cap + orb
            d0 = rounded_plan(cx, cy, zc, w * .36, w * .36, w * .18, math.radians(rot))
            d1 = rounded_plan(cx, cy, zc + .16, w * .30, w * .30, w * .15, math.radians(rot))
            slab = rg.Brep.CreateFromLoft([d0, d1], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
            if slab and len(slab) == 1:
                add(slab[0].CapPlanarHoles(.001), TEAL if s > .55 else STONE2)
            add(rg.Sphere(rg.Point3d(cx, cy, zc + .30), w * .09).ToBrep(), GOLD)
            return
        # main tower: flat crystal eave + floating halo orb, no upward spikes
        d0 = rounded_plan(cx, cy, zc, w * .44, w * .44, w * .22, math.radians(rot))
        d1 = rounded_plan(cx, cy, zc + .16, w * .38, w * .38, w * .19, math.radians(rot))
        slab = rg.Brep.CreateFromLoft([d0, d1], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
        if slab and len(slab) == 1:
            add(slab[0].CapPlanarHoles(.001), STONE2)
        halo_z = zc + .95 + .45 * form
        add(rg.Torus(rg.Plane(rg.Point3d(cx, cy, halo_z), rg.Vector3d.ZAxis), w * .30, .045).ToBrep(), BLUE)
        add(rg.Sphere(rg.Point3d(cx, cy, halo_z), w * .11).ToBrep(), GOLD)

    # ---- island ---------------------------------------------------------
    def jagged_ring(cx, cy, z, rx, ry, n, f=1.0, phase0=0.0, jitter=0.08):
        pts = []
        for k in range(n):
            th = 2 * math.pi * k / n + phase0
            rr = 1 + jitter * math.sin(5 * th + phase0) + jitter * .4 * rng.uniform(-1, 1)
            pts.append(rg.Point3d(cx + rx * f * rr * math.cos(th), cy + ry * f * rr * math.sin(th), z))
        pts.append(pts[0])
        return rg.PolylineCurve(pts)

    def island(cx, cy, top_z, rx, ry, depth, waterfall=False, shards=True, water_angle=None):
        cap = rg.Extrusion.Create(jagged_ring(cx, cy, top_z - .65, rx, ry, 12, 1.0, phase, .07), .65, True).ToBrep()
        add(cap, STONE)
        r0 = jagged_ring(cx, cy, top_z - .65, rx, ry, 12, .98, phase, .07)
        r1 = jagged_ring(cx, cy, top_z - .65 - depth * .36, rx, ry, 12, .70, phase + .2, .10)
        r2 = jagged_ring(cx, cy, top_z - .65 - depth, rx, ry, 12, .10, phase + .4, .05)
        rock = rg.Brep.CreateFromLoft([r0, r1, r2], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)
        if not rock or len(rock) != 1:
            raise ValueError('Island loft failed')
        add(rock[0].CapPlanarHoles(.001), CHAR)
        if shards:
            for k in range(5):
                th = rng.uniform(0, 2 * math.pi)
                rr = rng.uniform(.25, .72) * rx
                bz = top_z - .65 - depth * rng.uniform(.25, .7)
                bx, by = cx + rr * math.cos(th), cy + rr * math.sin(th)
                ln = depth * rng.uniform(.14, .30)
                ax = rg.Vector3d(rng.uniform(-.15, .15), rng.uniform(-.15, .15), -1)
                add(rg.Cone(rg.Plane(rg.Point3d(bx, by, bz), ax), ln, rng.uniform(.25, .55)).ToBrep(True), CHAR)
        if detail >= 1:
            for k in range(3):
                th = rng.uniform(0, 2 * math.pi)
                rr = rng.uniform(.2, .55) * rx
                bx, by = cx + rr * math.cos(th), cy + rr * math.sin(th)
                zz = top_z - .65 - depth * rng.uniform(.35, .75)
                pts = [rg.Point3d(bx, by, zz),
                       rg.Point3d(bx + rng.uniform(-.6, .6), by + rng.uniform(-.6, .6), zz - depth * .20),
                       rg.Point3d(bx + rng.uniform(-.8, .8), by + rng.uniform(-.8, .8), zz - depth * .38)]
                crv = rg.Curve.CreateInterpolatedCurve(pts, 3)
                pipes = rg.Brep.CreatePipe(crv, .045, False, rg.PipeCapMode.Round, True, .001, .1)
                if pipes:
                    for p in pipes: add(p, GREEN)
                add(rg.Sphere(rg.Point3d(pts[-1].X, pts[-1].Y, pts[-1].Z - .06), .10).ToBrep(), GOLD)
        if waterfall and detail >= 2:
            th = water_angle if water_angle is not None else rng.uniform(0, 2 * math.pi)
            wx, wy = cx + rx * .92 * math.cos(th), cy + ry * .92 * math.sin(th)
            for k in range(9):
                zz = top_z - .15 - k * .55
                xx = wx + math.sin(k * .55 + phase) * .18
                add(boxc(xx, wy, zz - .5, 1.05, .07, .58), LIGHT)
            for k in range(5):
                add(rg.Sphere(rg.Point3d(wx + rng.uniform(-.4, .4), wy + rng.uniform(-.4, .4), top_z - 5.4 + rng.uniform(-.4, .4)), rng.uniform(.10, .18)).ToBrep(), LIGHT)

    # ---- terrace / stairs ----------------------------------------------
    def stairs_south():
        for k in range(7):
            add(box(-1.8, -6.2 - (k + 1) * .32, 0, 3.6, .32, .10 + k * .16), STONE2)

    # ---- main island ----------------------------------------------------
    island(0, 0, 0.0, 9.8, 9.2, 9.6 * island_depth, waterfall=True, shards=True, water_angle=math.radians(225))
    prism(0, 0, 0, 7.8, 7.4, 6.0, 0.0, .40, STONE)
    prism(0, 0, .40, 6.6, 6.2, 6.0, math.radians(9), .42, STONE2)
    prism(0, 0, .82, 5.4, 5.0, 5.0, math.radians(-7), .40, STONE)
    stairs_south()
    # ---- main tower -----------------------------------------------------
    main_top, main_w, main_cx, main_cy, main_rot = tower(0, 0, base_z, width, levels, is_main=True)
    crown(main_cx, main_cy, main_top, main_w, main_rot, 1.0)
    # ---- ring -----------------------------------------------------------
    H = levels * step
    u_r = (base_z + .42 * H - base_z) / H
    ring_z = base_z + .42 * H
    ring_rot = twist_total * u_r
    ring_cx = lean_amt * (u_r ** 1.4) * math.cos(lean_dir)
    ring_cy = lean_amt * (u_r ** 1.4) * math.sin(lean_dir)
    tw_r = width * (1 - taper * u_r)
    tin, tout = tw_r * .5 + .55, tw_r * .5 + 2.35
    ring_deck = ring_z + .45
    ring = rg.Extrusion.Create(jagged_ring(ring_cx, ring_cy, ring_z, tout, tout, 32, 1.0, phase, .04), .45, True).ToBrep()
    hole = rg.Extrusion.Create(plan_curve(ring_cx, ring_cy, ring_z - .1, tin, tin, 2.0, ring_rot, 40), .65, True).ToBrep()
    add(cut_one(ring, hole), STONE)
    # balustrade posts + thin handrail, open and light
    for k in range(28):
        th = 2 * math.pi * k / 28 + ring_rot
        rr = tout * (1 + .04 * math.sin(5 * th + phase))
        add(boxc(ring_cx + rr * math.cos(th), ring_cy + rr * math.sin(th), ring_deck, .10, .10, .48), CHAR)
    # brackets
    for k in range(4):
        th = math.pi / 2 * k + ring_rot
        p0 = rg.Point3d(ring_cx + (tin - .3) * math.cos(th), ring_cy + (tin - .3) * math.sin(th), ring_z - 1.9)
        p1 = rg.Point3d(ring_cx + (tin + .15) * math.cos(th), ring_cy + (tin + .15) * math.sin(th), ring_z - .1)
        ax = p1 - p0
        add(rg.Cylinder(rg.Circle(rg.Plane(p0, ax), .13), ax.Length).ToBrep(True, True), CHAR)
    # hanging vines from ring
    for k in range(4):
        th = rng.uniform(0, 2 * math.pi)
        bx = ring_cx + (tout - .2) * math.cos(th); by = ring_cy + (tout - .2) * math.sin(th)
        pts = [rg.Point3d(bx, by, ring_deck), rg.Point3d(bx + .2, by - .2, ring_deck - 1.1), rg.Point3d(bx - .1, by - .3, ring_deck - 2.2)]
        pipes = rg.Brep.CreatePipe(rg.Curve.CreateInterpolatedCurve(pts, 3), .035, False, rg.PipeCapMode.Round, True, .001, .1)
        if pipes:
            for p in pipes: add(p, GREEN)
        add(rg.Sphere(rg.Point3d(pts[-1].X, pts[-1].Y, pts[-1].Z - .05), .08).ToBrep(), GOLD)

    for q in sats if False else []:
        pass

    # ---- satellites -----------------------------------------------------
    R_eff = max(ring_radius, 12.5 + satellite_count * .9)
    sats = []
    for i in range(satellite_count):
        a = (i * 137.5 + ring_rot + rng.uniform(-12, 12)) % 360
        rad = R_eff + rng.uniform(-2.2, 2.2)
        s = min(1.15, max(.35, satellite_size * rng.uniform(.78, 1.14)))
        for q in sats:
            if math.hypot(rad * math.cos(math.radians(a)) - q['rad'] * math.cos(math.radians(q['a'])),
                          rad * math.sin(math.radians(a)) - q['rad'] * math.sin(math.radians(q['a']))) < 5.0 * max(s, q['s']):
                rad += 2.2
        roof = ring_deck + rng.uniform(-1, 1) * 4.2 * height_variation
        roof = clamp(roof, ring_deck - 4.0, ring_deck + 4.0)
        typ = 'pavilion' if (i + seed) % 3 == 0 else 'tower'
        sats.append({'i': i, 'a': a, 'rad': rad, 's': s, 'roof': roof, 'typ': typ,
                     'x': rad * math.cos(math.radians(a)), 'y': rad * math.sin(math.radians(a))})

    for q in sats:
        cx, cy, s = q['x'], q['y'], q['s']
        ux, uy = math.cos(math.radians(q['a'])), math.sin(math.radians(q['a']))
        if q['typ'] == 'spire':
            hsp = 7.0 * s
            z0 = q['roof'] - hsp - .7
            q['z0'] = z0
            island(cx, cy, z0, 3.4 * s, 3.4 * s, 4.0 * s * island_depth, waterfall=(q['i'] % 3 == 0))
            # twisted spire
            base = plan_curve(cx, cy, z0, 1.5 * s, 1.5 * s, 5.0, math.radians(q['a']), 20)
            mid = plan_curve(cx, cy + .15 * s, z0 + hsp * .55, .85 * s, .85 * s, 5.0, math.radians(q['a'] + 25), 20)
            topc = plan_curve(cx, cy + .25 * s, z0 + hsp, .10 * s, .10 * s, 5.0, math.radians(q['a'] + 45), 20)
            sp = rg.Brep.CreateFromLoft([base, mid, topc], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
            if sp and len(sp) == 1:
                add(sp[0].CapPlanarHoles(.001), TEAL if q['i'] % 2 else STONE)
            add(rg.Sphere(rg.Point3d(cx, cy + .25 * s, z0 + hsp + .35 * s), .32 * s).ToBrep(), GOLD)
            # balcony for the bridge
            bz = q['roof'] - .35
            plan_ring(cx, cy, bz, 1.95 * s, 1.15 * s, 8, 2, math.radians(q['a']), .28, STONE2)
            q['link_z'] = bz + .28
            q['link_r'] = 1.95 * s
        else:
            pav = q['typ'] == 'pavilion'
            n = 1 if pav else max(2, int(round(levels * rng.uniform(.28, .42) * (.65 + .5 * s) / 2.6)))
            tws = (4.8 if pav else 3.7) * s
            bh = (2.6 if pav else 2.5) * s
            z0 = q['roof'] - n * (bh + .10) - .75
            q['z0'] = z0
            island(cx, cy, z0, 3.6 * s, 3.6 * s, 4.2 * s * island_depth, waterfall=(q['i'] % 3 == 0))
            prism(cx, cy, z0, 2.9 * s, 2.9 * s, 6, 0, .30, STONE)
            top_t, top_w, top_cx, top_cy, top_rot = tower(cx, cy, z0 + .30, tws, n,
                                                          twist_deg=twist_total * .65,
                                                          lean=lean_amt * .45,
                                                          scale=s, bays_h=bh)
            crown(top_cx, top_cy, top_t, top_w, top_rot, s)
            q['link_z'] = top_t
            q['link_r'] = top_w * .5
        # landing / pad toward main
        ux, uy = math.cos(math.radians(q['a'])), math.sin(math.radians(q['a']))
        lz = q['link_z']
        lx = cx - ux * (q['link_r'] + .7)
        ly = cy - uy * (q['link_r'] + .7)
        prism(lx, ly, lz - .28, 1.15 * s + .35, .80 * s + .30, 8, math.radians(q['a']), .28, STONE2)
        connections.append(('satellite %d' % q['i'], None, None))

    # ring pads at each bridge angle
    for q in sats:
        a = math.radians(q['a'])
        ux, uy = math.cos(a), math.sin(a)
        prism(ring_cx + ux * (tout + .55), ring_cy + uy * (tout + .55), ring_deck - .26,
              1.10, .85, 8, a, .26, STONE2)

    # ---- curved bridges -------------------------------------------------
    spans = []; slopes = []
    for q in sats:
        a = math.radians(q['a'])
        ux, uy = math.cos(a), math.sin(a)
        A = rg.Point3d(ring_cx + ux * (tout + 1.62), ring_cy + uy * (tout + 1.62), ring_deck)
        B = rg.Point3d(q['x'] - ux * (q['link_r'] + .7 + 1.15 * q['s'] + .35), q['y'] - uy * (q['link_r'] + .7 + 1.15 * q['s'] + .35), q['link_z'])
        L = math.hypot(B.X - A.X, B.Y - A.Y)
        if L < 2.0:
            continue
        spans.append(L); slopes.append(math.degrees(math.atan2(abs(B.Z - A.Z), L)))
        w = clamp(1.5 * q['s'] * bridge_width, .8, 1.9)
        nx, ny = -uy, ux
        bow = min(3.0, L * .10) * bow_scale
        p1x, p1y = (A.X + B.X) / 2 + nx * bow, (A.Y + B.Y) / 2 + ny * bow
        N = 12
        pts = []
        for k in range(N + 1):
            t = k / float(N)
            xx = (1 - t) ** 2 * A.X + 2 * (1 - t) * t * p1x + t ** 2 * B.X
            yy = (1 - t) ** 2 * A.Y + 2 * (1 - t) * t * p1y + t ** 2 * B.Y
            zz = (1 - t) * A.Z + t * B.Z + .55 * arch_scale * math.sin(math.pi * t)
            pts.append(rg.Point3d(xx, yy, zz))
        # deck segments
        for k in range(N):
            p0, p1 = pts[k], pts[k + 1]
            dx, dy = p1.X - p0.X, p1.Y - p0.Y
            ll = math.hypot(dx, dy) or 1
            nnx, nny = -dy / ll, dx / ll
            ww = w * (1 - .10 * math.sin(math.pi * (k + .5) / N))
            d = [rg.Point3d(p0.X + nnx * ww / 2, p0.Y + nny * ww / 2, p0.Z - .22),
                 rg.Point3d(p0.X - nnx * ww / 2, p0.Y - nny * ww / 2, p0.Z - .22),
                 rg.Point3d(p1.X - nnx * ww / 2, p1.Y - nny * ww / 2, p1.Z - .22),
                 rg.Point3d(p1.X + nnx * ww / 2, p1.Y + nny * ww / 2, p1.Z - .22),
                 rg.Point3d(p0.X + nnx * ww / 2, p0.Y + nny * ww / 2, p0.Z),
                 rg.Point3d(p0.X - nnx * ww / 2, p0.Y - nny * ww / 2, p0.Z),
                 rg.Point3d(p1.X - nnx * ww / 2, p1.Y - nny * ww / 2, p1.Z),
                 rg.Point3d(p1.X + nnx * ww / 2, p1.Y + nny * ww / 2, p1.Z)]
            add(rg.Brep.CreateFromBox(d), STONE)
        # railings as interpolated pipes on both sides
        for side in (-1, 1):
            rp = []
            for k in range(N + 1):
                t = k / float(N)
                p = pts[k]
                d = math.hypot(B.X - A.X, B.Y - A.Y) or 1
                # use a slowly varying normal; sufficient for a gentle bow
                rp.append(rg.Point3d(p.X + nx * side * (w / 2 - .04),
                                     p.Y + ny * side * (w / 2 - .04), p.Z + .46))
            pipes = rg.Brep.CreatePipe(rg.Curve.CreateInterpolatedCurve(rp, 3), .045, False, rg.PipeCapMode.Round, True, .001, .1)
            if pipes:
                for p in pipes: add(p, BLUE)
        # slender arch spine + hangers
        sp = []
        for k in range(N + 1):
            t = k / float(N)
            p = pts[k]
            sp.append(rg.Point3d(p.X, p.Y, p.Z - .35 - 1.1 * arch_scale * math.sin(math.pi * t)))
        pipes = rg.Brep.CreatePipe(rg.Curve.CreateInterpolatedCurve(sp, 3), .075, False, rg.PipeCapMode.Round, True, .001, .1)
        if pipes:
            for p in pipes: add(p, CHAR)
        for k in range(2, N, 2):
            p = pts[k]
            zsp = p.Z - .35 - 1.1 * arch_scale * math.sin(math.pi * (k / float(N)))
            add(cyl(p.X, p.Y, zsp, .028, p.Z - zsp), CHAR)
        # derived bridge screen: same opening profile as the tower, scaled
        if detail >= 1:
            mid = pts[N // 2]
            tang = math.atan2(pts[N // 2 + 1].Y - pts[N // 2 - 1].Y,
                              pts[N // 2 + 1].X - pts[N // 2 - 1].X)
            ap = .36 + .42 * void_ratio
            bp = .22 + .30 * void_ratio
            plen, ph = 2.20, 1.00
            for side in (-1, 1):
                pcx = mid.X + nx * side * (w / 2 + .06)
                pcy = mid.Y + ny * side * (w / 2 + .06)
                pcz = mid.Z + .48
                panel = box(-plen / 2, -.05, -ph / 2, plen, .10, ph)
                panel.Transform(rg.Transform.Rotation(tang, rg.Vector3d.ZAxis, rg.Point3d.Origin))
                panel.Transform(rg.Transform.Translation(pcx, pcy, pcz))
                cutter = rg.Extrusion.Create(profile_curve(ap, bp), .32, True).ToBrep()
                cutter.Transform(rg.Transform.Rotation(math.pi / 2, rg.Vector3d.XAxis, rg.Point3d.Origin))
                cutter.Transform(rg.Transform.Rotation(tang, rg.Vector3d.ZAxis, rg.Point3d.Origin))
                cutter.Transform(rg.Transform.Translation(pcx + nx * .16, pcy + ny * .16, pcz))
                for part in cut_parts([panel], cutter):
                    add(part, STONE2)
        # end pads
        add(cyl(A.X, A.Y, A.Z - .24, w * .62, .24), STONE2)
        add(cyl(B.X, B.Y, B.Z - .24, w * .62, .24), STONE2)

    # ---- side towers on the main island --------------------------------
    side_specs = [(38.0, 8.0, 3, 3.6, .58), (205.0, 7.4, 4, 3.0, .48)]
    for sa_deg, rad, nn, wt, sc in side_specs:
        side_a = math.radians(sa_deg)
        sx, sy = rad * math.cos(side_a), rad * math.sin(side_a)
        sbase = .40
        prism(sx, sy, sbase, wt * .70, wt * .64, 6, side_a, .30, STONE2)
        stop, sw, scx, scy, srot = tower(sx, sy, sbase + .30, wt, nn,
                                         twist_deg=twist_total * .55, lean=lean_amt * .40,
                                         scale=sc, bays_h=2.8)
        crown(scx, scy, stop, sw, srot, sc)
        prism(ring_cx + math.cos(side_a) * (tout + .55), ring_cy + math.sin(side_a) * (tout + .55),
              ring_deck - .26, 1.05, .80, 8, side_a, .26, STONE2)
        A2 = rg.Point3d(ring_cx + math.cos(side_a) * (tout + 1.55), ring_cy + math.sin(side_a) * (tout + 1.55), ring_deck)
        B2 = rg.Point3d(sx - math.cos(side_a) * (sw * .5 + .35), sy - math.sin(side_a) * (sw * .5 + .35), stop)
        L2 = math.hypot(B2.X - A2.X, B2.Y - A2.Y)
        if L2 > 1.0:
            w2 = 1.15
            nx2, ny2 = -math.sin(side_a), math.cos(side_a)
            p1x, p1y = (A2.X + B2.X) / 2 + nx2 * .35, (A2.Y + B2.Y) / 2 + ny2 * .35
            pts = []
            for k in range(7):
                t = k / 6.0
                pts.append(rg.Point3d((1 - t) ** 2 * A2.X + 2 * (1 - t) * t * p1x + t ** 2 * B2.X,
                                      (1 - t) ** 2 * A2.Y + 2 * (1 - t) * t * p1y + t ** 2 * B2.Y,
                                      (1 - t) * A2.Z + t * B2.Z + .25 * math.sin(math.pi * t)))
            for k in range(6):
                p0, p1 = pts[k], pts[k + 1]
                d = [rg.Point3d(p0.X + nx2 * w2 / 2, p0.Y + ny2 * w2 / 2, p0.Z - .18),
                     rg.Point3d(p0.X - nx2 * w2 / 2, p0.Y - ny2 * w2 / 2, p0.Z - .18),
                     rg.Point3d(p1.X - nx2 * w2 / 2, p1.Y - ny2 * w2 / 2, p1.Z - .18),
                     rg.Point3d(p1.X + nx2 * w2 / 2, p1.Y + ny2 * w2 / 2, p1.Z - .18),
                     rg.Point3d(p0.X + nx2 * w2 / 2, p0.Y + ny2 * w2 / 2, p0.Z),
                     rg.Point3d(p0.X - nx2 * w2 / 2, p0.Y - ny2 * w2 / 2, p0.Z),
                     rg.Point3d(p1.X - nx2 * w2 / 2, p1.Y - ny2 * w2 / 2, p1.Z),
                     rg.Point3d(p1.X + nx2 * w2 / 2, p1.Y + ny2 * w2 / 2, p1.Z)]
                add(rg.Brep.CreateFromBox(d), STONE)
            for side in (-1, 1):
                rp = [rg.Point3d(p.X + nx2 * side * (w2 / 2 - .04), p.Y + ny2 * side * (w2 / 2 - .04), p.Z + .38) for p in pts]
                pipes = rg.Brep.CreatePipe(rg.Curve.CreateInterpolatedCurve(rp, 3), .04, False, rg.PipeCapMode.Round, True, .001, .1)
                if pipes:
                    for p in pipes: add(p, BLUE)

    # ---- suspended orb + debris ----------------------------------------
    if detail >= 1:
        oz = -9.8 * island_depth - 2.8
        add(rg.Sphere(rg.Point3d(0, 0, oz), 1.05).ToBrep(), GOLD)
        add(rg.Torus(rg.Plane(rg.Point3d(0, 0, oz), rg.Vector3d(.2, .35, 1)), 1.75, .10).ToBrep(), BLUE)
    # remove stray solids from failed booleans before framing the model
    if geometry:
        kg, kc = [], []
        for g, c in zip(geometry, colors):
            b = g.GetBoundingBox(True)
            if b.Diagonal.Length > 120:
                continue
            if b.Center.DistanceTo(rg.Point3d.Origin) > 80:
                continue
            kg.append(g); kc.append(c)
        geometry, colors = kg, kc

    # ---- scale ----------------------------------------------------------
    if abs(model_scale - 1) > 1e-9:
        tr = rg.Transform.Scale(rg.Point3d.Origin, model_scale)
        for g in geometry: g.Transform(tr)

    report.append('SKY CITY v3')
    report.append('form %.2f / levels %d / H %.1f / ring z %.1f' % (form, levels, H, ring_z))
    report.append('satellites %d / breps %d' % (satellite_count, len(geometry)))
    if spans:
        report.append('bridge span %.1f-%.1f / max slope %.0f deg' % (min(spans), max(spans), max(slopes)))
    report.append('seed %d / scale %.2f' % (seed, model_scale))
    return {'geometry': geometry, 'colors': colors, 'connections': connections,
            'report': '\n'.join(report), 'sats': sats, 'ring_z': ring_z}
