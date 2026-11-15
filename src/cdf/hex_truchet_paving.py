"""Assignment 2.2. Equal hexagons with a single rotating three-arc motif."""
from math import cos, pi, sin, sqrt

import Rhino.Geometry as rg
from System import Random
from System.Drawing import Color


NEIGHBORS = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))


def trace_motifs(rotations, columns):
    """Return the best connected chain and whether it runs left to right."""
    remaining = {(q, r, (2 * i + turn) % 6)
                 for (q, r), turn in rotations.items() for i in range(3)}
    best = set()
    score = (-1, -1, -1)
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        pending = [first]
        component = {first}
        open_left = open_right = False
        while pending:
            q, r, edge = pending.pop()
            for port in (edge, (edge + 1) % 6):
                dq, dr = NEIGHBORS[port]
                neighbor = (q + dq, r + dr)
                if neighbor not in rotations:
                    open_left |= q == 0 and dq == -1
                    open_right |= q == columns - 1 and dq == 1
                    continue
                incoming = (port + 3) % 6
                paired_start = (incoming - (incoming - rotations[neighbor]) % 2) % 6
                segment = (neighbor[0], neighbor[1], paired_start)
                if segment in remaining:
                    remaining.remove(segment)
                    component.add(segment)
                    pending.append(segment)
        span = max(s[0] for s in component) - min(s[0] for s in component)
        rank = (int(open_left and open_right), span, len(component))
        if rank > score:
            score, best = rank, component
    return best, bool(score[0])


def choose_layout(columns, rows, seed):
    """Compare 48 seeded arrangements and prefer a long crossing of the field."""
    rng = Random(seed)
    cells = [(q, row - q // 2) for q in range(columns) for row in range(rows)]
    best = (-1, -1, -1)
    for _ in range(48):
        rotations = {cell: rng.Next(2) for cell in cells}
        path, crosses = trace_motifs(rotations, columns)
        span = max(s[0] for s in path) - min(s[0] for s in path)
        score = (int(crosses), span, len(path))
        if score > best:
            best, result = score, (rotations, path, crosses)
    return result


def polar(x, y, z, radius, angle):
    return rg.Point3d(x + radius * cos(angle), y + radius * sin(angle), z)


def make_tile(x, y, side, thickness):
    vertices = [polar(x, y, 0, side, i * pi / 3) for i in range(6)]
    outline = rg.PolylineCurve(vertices + vertices[:1])
    return rg.Extrusion.Create(outline, thickness, True).ToBrep()


def make_ribbon(x, y, side, z, edge, width):
    """Make one 120-degree band tangent to the same band on the next tile."""
    corner_angle = (edge + 1) * pi / 3
    vertex = polar(x, y, z, side, corner_angle)
    angles = [corner_angle + i * pi / 3 for i in (2, 3, 4)]
    outer = [polar(vertex.X, vertex.Y, z, (side + width) / 2, a) for a in angles]
    inner = [polar(vertex.X, vertex.Y, z, (side - width) / 2, a) for a in angles]
    boundary = rg.PolyCurve()
    boundary.Append(rg.ArcCurve(rg.Arc(*outer)))
    boundary.Append(rg.LineCurve(outer[-1], inner[-1]))
    boundary.Append(rg.ArcCurve(rg.Arc(*reversed(inner))))
    boundary.Append(rg.LineCurve(inner[0], outer[0]))
    return rg.Brep.CreatePlanarBreps(boundary, 0.00001)[0]


def make_module(x, y, side, turn, stripe):
    thickness = 0.045
    tile = make_tile(x, y, side, thickness)
    marks = [make_ribbon(x, y, side, thickness + 0.0002, (2 * i + turn) % 6, stripe)
             for i in range(3)]
    return tile, marks


def build_floor(columns, rows, side, seed, trace):
    rotations, path, crosses = choose_layout(columns, rows, seed)
    geometry, colors = [], []
    ceramic = Color.FromArgb(230, 219, 193)
    navy = Color.FromArgb(32, 69, 82)
    fog = Color.FromArgb(179, 181, 168)
    red = Color.FromArgb(187, 69, 44)
    for (q, r), turn in rotations.items():
        x = 1.5 * side * q
        y = sqrt(3.0) * side * (r + q / 2.0)
        tile, marks = make_module(x, y, side, turn, 0.19 * side)
        geometry.extend([tile] + marks)
        colors.append(ceramic)
        for i in range(3):
            key = (q, r, (2 * i + turn) % 6)
            colors.append((red if key in path else fog) if trace else navy)
    return geometry, colors, (len(rotations), len(path), len({s[:2] for s in path}), crosses)


if all(name in globals() for name in ('columns', 'rows', 'side', 'seed', 'trace')):
    geometry, colors, metrics = build_floor(int(columns), int(rows), float(side), int(seed), bool(trace))
    count, arcs, tiles, crossing = metrics
    print('{} equal tiles, {} matching motifs'.format(count, count))
    print('Selected route: {} arcs across {} distinct tiles'.format(arcs, tiles))
    print('Crosses left to right: {}'.format('yes' if crossing else 'no'))
