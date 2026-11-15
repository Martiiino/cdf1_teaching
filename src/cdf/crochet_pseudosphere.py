"""Assignment 2.1. The base chain grows into three closed stitch courses."""
from math import cos, pi, sin
import Rhino.Geometry as rg
from System.Drawing import Color


def create_pseudosphere(base, first, second, third, fold):
    """Return two coloured meshes and the stitch count of each course."""
    increases = tuple(int(value) for value in (first, second, third))
    counts = [2 * int(round(float(base) / 2.0))]
    for multiplier in increases:
        counts.append(counts[-1] * multiplier)

    # One vertex per stitch, sampled on a flared annulus. The outer
    # courses carry stronger folds as stitch density increases.
    rings = []
    points = []
    for course, count in enumerate(counts):
        t = course / 3.0
        ring = []
        for index in range(count):
            angle = 2.0 * pi * index / count
            phase = angle + 0.10 * t
            wave = (6.2 * sin(6 * phase + 0.50 * sin(3 * phase))
                    + 2.5 * sin(13 * phase + 0.7)
                    + 0.75 * sin(27 * phase))
            radius = 3.0 + 22.0 * t + 2.6 * t**2 * cos(6 * phase)
            height = 10.0 * (1.0 - (1.0 - t)**2) + fold * t**2.7 * wave
            ring.append(len(points))
            points.append(rg.Point3d(radius * cos(angle), radius * sin(angle), height))
        rings.append(ring)

    # Stitch fans connect every parent to its children and close each
    # course at the seam. Keep the first half of the rim blue.
    faces = [[], []]
    for course, multiplier in enumerate(increases):
        inner, outer = rings[course:course + 2]
        for index, parent in enumerate(inner):
            start = index * multiplier
            stop = start + multiplier
            following = inner[(index + 1) % len(inner)]
            next_child = outer[stop % len(outer)]
            color = int(course == 2 and start >= len(outer) // 2)
            for j in range(start, stop - 1):
                faces[color].append((parent, outer[j], outer[j + 1]))
            faces[color].append((parent, outer[stop - 1], next_child))
            faces[color].append((parent, next_child, following))

    meshes = []
    for group in faces:
        mesh = rg.Mesh()
        indices = {}
        for face in group:
            for vertex in face:
                if vertex not in indices:
                    indices[vertex] = mesh.Vertices.Add(points[vertex])
            mesh.Faces.AddFace(*[indices[vertex] for vertex in face])
        mesh.Normals.ComputeNormals()
        mesh.Compact()
        meshes.append(mesh)
    return meshes, counts


if all(name in globals() for name in ("base", "first", "second", "third", "fold")):
    geometry, counts = create_pseudosphere(base, first, second, third, fold)
    colors = [Color.FromArgb(104, 150, 190), Color.FromArgb(42, 39, 47)]
    print("Stitches by course: {}".format(" / ".join(map(str, counts))))
    print("Outer course: {} blue / {} black".format(counts[-1] // 2, counts[-1] // 2))
