"""240 equal hexagons, random orientations, nested fills and longest open path.

layout 1..8 reproduces the eight presentation arrangements.
layout 0 creates independent seeded 0/60-degree rotations for every tile.
"""
from math import cos, pi, sin, sqrt
import Rhino.Geometry as rg
from System import Random
from System.Drawing import Color

NEIGHBORS = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
CELLS = [[-3, 0], [-3, 1], [-3, 2], [-3, 3], [-3, 4], [-3, 5], [-3, 6], [-3, 7], [-3, 8], [-3, 9], [-3, 10], [-2, -1], [-2, 0], [-2, 1], [-2, 2], [-2, 3], [-2, 4], [-2, 5], [-2, 6], [-2, 7], [-2, 8], [-2, 9], [-2, 10], [-1, -2], [-1, -1], [-1, 0], [-1, 1], [-1, 2], [-1, 3], [-1, 4], [-1, 5], [-1, 6], [-1, 7], [-1, 8], [-1, 9], [-1, 10], [0, -3], [0, -2], [0, -1], [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [0, 10], [1, -3], [1, -2], [1, -1], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9], [1, 10], [2, -4], [2, -3], [2, -2], [2, -1], [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9], [3, -4], [3, -3], [3, -2], [3, -1], [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [3, 5], [3, 6], [3, 7], [3, 8], [3, 9], [4, -5], [4, -4], [4, -3], [4, -2], [4, -1], [4, 0], [4, 1], [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [4, 8], [5, -5], [5, -4], [5, -3], [5, -2], [5, -1], [5, 0], [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8], [6, -6], [6, -5], [6, -4], [6, -3], [6, -2], [6, -1], [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7], [7, -6], [7, -5], [7, -4], [7, -3], [7, -2], [7, -1], [7, 0], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6], [7, 7], [8, -7], [8, -6], [8, -5], [8, -4], [8, -3], [8, -2], [8, -1], [8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [9, -7], [9, -6], [9, -5], [9, -4], [9, -3], [9, -2], [9, -1], [9, 0], [9, 1], [9, 2], [9, 3], [9, 4], [9, 5], [9, 6], [10, -8], [10, -7], [10, -6], [10, -5], [10, -4], [10, -3], [10, -2], [10, -1], [10, 0], [10, 1], [10, 2], [10, 3], [10, 4], [10, 5], [11, -8], [11, -7], [11, -6], [11, -5], [11, -4], [11, -3], [11, -2], [11, -1], [11, 0], [11, 1], [11, 2], [11, 3], [11, 4], [11, 5], [12, -8], [12, -7], [12, -6], [12, -5], [12, -4], [12, -3], [12, -2], [12, -1], [12, 0], [12, 1], [12, 2], [12, 3], [12, 4], [13, -8], [13, -7], [13, -6], [13, -5], [13, -4], [13, -3], [13, -2], [13, -1], [13, 0], [13, 1], [13, 2], [13, 3], [14, -8], [14, -7], [14, -6], [14, -5], [14, -4], [14, -3], [14, -2], [14, -1], [14, 0], [14, 1], [14, 2]]
PRESETS = ['010111110010110100010101100100001110010111000001111101110000010011011100110011001001000000111011010000010101011000000001010110000101010100100111101010100100000011001011000001011101111000011000101011011110010000111011001000111111111111011001', '011011001101101001011000100110111101111000101100011010110111010100111000000110001001111101100010111111101011011111010010010111001111001011110111000110111101110011101111110010101000001101000010101010111110111110011110000010100000011011011111', '101110000010110011111011101001001000000010000011100010110010010100110010110110011011010010010000110001101001110000110110010000001001001100110101110000111011011110010001000111100010010000000001011101011010011001101101110101100100100110011010', '011001111011011111011001110000001000101100000101000111000010110111100100101101010100010110101110100101110101011001010011001010001001110010010101100111010011000101111111000001101111110110011110000100111110101110001101010010010101011111101101', '100100000001000011110011011001111001101101001101001000110000101001010000111010101001101101101101101111010011001111100100110010000011101000001111101001101011111010100101000110101111101101110010101011110011011000011100110110000001011011111100', '101000010100001101100010101000110101110011100011010110111011101111011100001101100100110111000101011010011111010011110000001101111111001010100011010011110011011110100100101001101010110101011011000111011000110000110001001011101101001110000110', '100000010111100011011001000101110111010101101000101000011110011111100101000101010001100001101001011100110000110011111111001100100000101010001000010000001001001011110110010110111010111010001001000001000101100001011110001010010011010100001001', '001011110011011010110100111011000001111110001100010111000011001101000111000100111101111111000011010001110010101100101100001001111111000101111111101011100011111001101010111101001011001111011011101011001100101101100110000010001001000101001000']


def polar(x, y, z, radius, angle):
    return rg.Point3d(x + radius * cos(angle), y + radius * sin(angle), z)


def make_tile(x, y, side):
    points = [polar(x, y, 0, side, i * pi / 3) for i in range(6)]
    profile = rg.PolylineCurve(points + points[:1])
    return rg.Extrusion.Create(profile, 0.045, True).ToBrep()


def make_arc(x, y, side, edge, height):
    angle = (edge + 1) * pi / 3
    center = polar(x, y, height, side, angle)
    points = [polar(center.X, center.Y, height, side / 2, angle + i * pi / 3)
              for i in (2, 3, 4)]
    return rg.ArcCurve(rg.Arc(*points))


def make_band(x, y, side, edge, width, height):
    angle = (edge + 1) * pi / 3
    center = polar(x, y, height, side, angle)
    angles = [angle + i * pi / 3 for i in (2, 3, 4)]
    outer = [polar(center.X, center.Y, height, (side + width) / 2, a) for a in angles]
    inner = [polar(center.X, center.Y, height, (side - width) / 2, a) for a in angles]
    boundary = rg.PolyCurve()
    boundary.Append(rg.ArcCurve(rg.Arc(*outer)))
    boundary.Append(rg.LineCurve(outer[-1], inner[-1]))
    boundary.Append(rg.ArcCurve(rg.Arc(*reversed(inner))))
    boundary.Append(rg.LineCurve(inner[0], outer[0]))
    return rg.Brep.CreatePlanarBreps(boundary, 0.000001)[0]


def join_paths(rotations, arcs, tolerance):
    """Each arc joins exactly one arc across each internal tile edge."""
    remaining = set(arcs)
    paths = []
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        component = {first}
        pending = [first]
        while pending:
            q, r, edge = pending.pop()
            for port in (edge, (edge + 1) % 6):
                dq, dr = NEIGHBORS[port]
                neighbor = q + dq, r + dr
                if neighbor not in rotations:
                    continue
                incoming = (port + 3) % 6
                start = (incoming - (incoming - rotations[neighbor]) % 2) % 6
                connected = neighbor[0], neighbor[1], start
                if connected in remaining:
                    remaining.remove(connected)
                    component.add(connected)
                    pending.append(connected)
        joined = rg.Curve.JoinCurves([arcs[key] for key in sorted(component)], tolerance)
        if len(joined) != 1:
            raise ValueError('A connected arc group failed to join.')
        paths.append((joined[0], component))
    return paths


def nesting_depths(loops, plane, tolerance):
    """Count containing loops, with no limit on nesting depth."""
    return [sum(rg.Curve.PlanarClosedCurveRelationship(a, b, plane, tolerance)
                == rg.RegionContainment.AInsideB for j, b in enumerate(loops) if i != j)
            for i, a in enumerate(loops)]


def build_floor(layout=6, seed=23, side=0.42, fill=True, trace=True):
    index = int(layout)
    side = float(side)
    if not 0 <= index <= 8 or side <= 0:
        raise ValueError('layout must be 0..8 and side must be positive.')
    rng = Random(int(seed))
    rotations = {tuple(cell): (rng.Next(2) if index == 0 else int(PRESETS[index - 1][i]))
                 for i, cell in enumerate(CELLS)}
    tolerance = side * 1e-6
    geometry, colors, arcs, bands = [], [], {}, {}
    ceramic = Color.FromArgb(230, 219, 193)
    navy = Color.FromArgb(32, 69, 82)
    orange = Color.FromArgb(163, 74, 50)
    height = 0.0452

    for (q, r), turn in rotations.items():
        x = 1.5 * side * q
        y = sqrt(3) * side * (r + q / 2.0)
        geometry.append(make_tile(x, y, side))
        colors.append(ceramic)
        for i in range(3):
            edge = (2 * i + turn) % 6
            key = q, r, edge
            arcs[key] = make_arc(x, y, side, edge, height)
            bands[key] = make_band(x, y, side, edge, 0.19 * side, height + 0.0002)

    paths = join_paths(rotations, arcs, tolerance)
    loops = [curve for curve, _ in paths if curve.IsClosed]
    open_paths = [(curve, keys) for curve, keys in paths if not curve.IsClosed]
    longest = max(open_paths, key=lambda pair: pair[0].GetLength(), default=None)
    plane = rg.Plane(rg.Point3d(0, 0, height), rg.Vector3d.ZAxis)
    depths = nesting_depths(loops, plane, tolerance)

    if fill and loops:
        # Planar Breps interpret nested closed boundaries as alternating
        # outer loops and holes, so this works at every nesting depth.
        filled = list(rg.Brep.CreatePlanarBreps(loops, tolerance) or [])
        expected_area = sum((-1)**depth * rg.AreaMassProperties.Compute(curve).Area
                            for curve, depth in zip(loops, depths))
        actual_area = sum(rg.AreaMassProperties.Compute(brep).Area for brep in filled)
        if abs(actual_area - expected_area) > max(1e-7, expected_area * 1e-5):
            raise ValueError('Nested-loop fill area failed the parity check.')
        geometry.extend(filled)
        colors.extend([navy] * len(filled))

    orange_keys = longest[1] if trace and longest else set()
    for key in sorted(bands):
        geometry.append(bands[key])
        colors.append(orange if key in orange_keys else navy)
    info = {
        'tiles': len(rotations),
        'closed': len(loops),
        'open': len(open_paths),
        'max_depth': max(depths, default=-1) + 1,
        'longest_arcs': len(longest[1]) if longest else 0,
        'longest_length': longest[0].GetLength() if longest else 0,
        'orange_bands': len(orange_keys),
    }
    return geometry, colors, [curve for curve, _ in paths], info


if all(name in globals() for name in ('layout', 'seed', 'side', 'fill', 'trace')):
    geometry, colors, paths, metrics = build_floor(int(layout), int(seed), side, bool(fill), bool(trace))
    print('240 equal hexagons; layout {}'.format(int(layout)))
    print('{} closed loops, {} open paths, {} nested levels'.format(
        metrics['closed'], metrics['open'], metrics['max_depth']))
    print('Longest open path: {} arcs, {:.2f} m'.format(
        metrics['longest_arcs'], metrics['longest_length']))
