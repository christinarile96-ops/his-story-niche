"""Location builder: a warm living-room corner from Poly Haven assets (CC0)."""
import bpy, os, math
from mathutils import Vector

PH = os.environ.get("PH_DIR")


def _tex_mat(name, base, scale=2.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    def img(suffix, cs):
        p = f"{PH}/tex/{base}_{suffix}.jpg"
        if not os.path.exists(p):
            return None
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(p)
        n.image.colorspace_settings.name = cs
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n
    d = img("Diffuse", "sRGB")
    if d:
        nt.links.new(d.outputs["Color"], bsdf.inputs["Base Color"])
    r = img("Rough", "Non-Color")
    if r:
        nt.links.new(r.outputs["Color"], bsdf.inputs["Roughness"])
    n = img("nor_gl", "Non-Color")
    if n:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(n.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def _plane(name, size, loc, rot, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project(cube_size=1.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    o.data.materials.append(mat)
    return o


def _gltf(name, loc, rot_z=0.0, scale=1.0):
    p = f"{PH}/{name}/{name}.gltf"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=p)
    new = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in new if o.parent is None]
    for r in roots:
        r.location = Vector(loc)
        r.rotation_euler = (0, 0, rot_z)
        r.scale = (scale, scale, scale)
    return roots


def build_room():
    floor = _tex_mat("floor", "laminate_floor_02", 3.0)
    wall = _tex_mat("wall", "beige_wall_001", 1.5)
    _plane("Floor", (8, 8), (0, 0, 0), (0, 0, 0), floor)
    _plane("WallBack", (8, 3.2), (0, 2.2, 1.6), (math.radians(90), 0, 0), wall)
    _plane("WallLeft", (8, 3.2), (-2.6, 0, 1.6), (math.radians(90), 0, math.radians(90)), wall)
    _plane("WallRight", (8, 3.2), (4.2, 0, 1.6), (math.radians(90), 0, math.radians(-90)), wall)
    ceil = bpy.data.materials.new("ceiling"); ceil.use_nodes = True
    ceil.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.78, 0.74, 1)
    _plane("Ceiling", (8, 8), (0, 0, 2.7), (math.radians(180), 0, 0), ceil)
    # warm practical lamp glow near the sofa
    bpy.ops.object.light_add(type='POINT', location=(-1.4, 1.7, 1.5))
    l = bpy.context.object; l.name = "Practical"; l.data.energy = 60; l.data.color = (1.0, 0.7, 0.4); l.data.shadow_soft_size = 0.3
    _gltf("Sofa_01", (-0.3, 1.6, 0), math.radians(0))
    _gltf("CoffeeTable_01", (-0.3, 0.75, 0))
    _gltf("Rockingchair_01", (-1.9, 0.9, 0), math.radians(60))
    _gltf("potted_plant_01", (-2.2, 1.9, 0))
    _gltf("Lantern_01", (0.0, 0.75, 0.45), 0, 1.0)
    _gltf("book_encyclopedia_set_01", (-0.6, 0.7, 0.45), math.radians(20))
    _gltf("WoodenTable_01", (1.6, 1.7, 0), math.radians(90))


def build_world(hdri="st_fagans_interior", strength=0.6):
    w = bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(f"{PH}/hdri/{hdri}_2k.hdr")
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = strength
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])


def key_lights():
    # warm window key from camera-left, cool rim from behind-right, soft fill
    def area(name, loc, rot, size, power, color):
        bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
        l = bpy.context.object
        l.name = name
        l.data.size = size
        l.data.energy = power
        l.data.color = color
        return l
    area("Key", (-1.6, -1.4, 2.4), (math.radians(55), 0, math.radians(-40)), 1.6, 380, (1.0, 0.86, 0.7))
    area("Rim", (1.4, 1.6, 2.2), (math.radians(-60), 0, math.radians(150)), 0.8, 260, (0.7, 0.8, 1.0))
    area("Fill", (1.8, -2.2, 1.4), (math.radians(75), 0, math.radians(40)), 2.5, 90, (1.0, 0.95, 0.9))
