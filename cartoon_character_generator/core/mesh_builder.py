import bpy
import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


def create_extruded_mesh_from_contour(contour, depth=0.5, scale=0.01, center=None):
    mesh = bpy.data.meshes.new("CartoonCharacterMesh")
    obj = bpy.data.objects.new("CartoonCharacter", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    front_verts = []
    back_verts = []

    xs = [p[0][0] for p in contour]
    ys = [p[0][1] for p in contour]

    if center is None:
        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2
    else:
        cx, cy = center

    points_2d = []

    for point in contour:
        x = (point[0][0] - cx) * scale
        z = -(point[0][1] - cy) * scale

        front_verts.append(bm.verts.new((x, -depth / 2, z)))
        back_verts.append(bm.verts.new((x, depth / 2, z)))

        points_2d.append(Vector((x, z, 0)))

    bm.verts.ensure_lookup_table()

    count = len(front_verts)

    # side faces
    for i in range(count):
        ni = (i + 1) % count

        try:
            bm.faces.new((
                front_verts[i],
                front_verts[ni],
                back_verts[ni],
                back_verts[i],
            ))
        except ValueError:
            pass

    # triangulated caps
    triangles = tessellate_polygon([points_2d])

    for tri in triangles:
        try:
            bm.faces.new((
                front_verts[tri[0]],
                front_verts[tri[1]],
                front_verts[tri[2]],
            ))
        except ValueError:
            pass

        try:
            bm.faces.new((
                back_verts[tri[2]],
                back_verts[tri[1]],
                back_verts[tri[0]],
            ))
        except ValueError:
            pass

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    for poly in obj.data.polygons:
        poly.use_smooth = False

    return obj