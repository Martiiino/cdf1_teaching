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
