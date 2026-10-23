"""Pilot: Milo walks into Grandpa's living room (wide), cut to close-up: 'Grandpa... I'm not a dog.'"""
import bpy, sys, math, os
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)

import milo, retarget, scene as room

def all_fcurves(action):
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    out = []
    for layer in action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                out += list(cb.fcurves)
    return out


FPS = 30
SHOT_A = (1, 84)      # wide walk
SHOT_B = (85, 234)    # close-up acting
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, SHOT_B[1]

room.build_room()
room.build_world(strength=0.5)
room.key_lights()

body, parts = milo.build()
rig = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for pb in rig.pose.bones:
    pb.rotation_mode = 'QUATERNION'

# ---------------- walk (shot A) ----------------
bpy.ops.import_anim.bvh(filepath=os.environ["BVH"], global_scale=0.056, rotate_mode='NATIVE',
                        axis_forward='-Z', axis_up='Y', update_scene_fps=False, update_scene_duration=False)
src = bpy.context.object
fr = src.animation_data.action.frame_range
start = int(fr[0]) + 8
end = min(int(fr[1]), start + (SHOT_A[1] - 1) * 4)
act, n = retarget.retarget(src, rig, start, end, 4, out_start=1)
if n < SHOT_A[1]:
    sc.frame_set(n)
    for pb in rig.pose.bones:
        pb.keyframe_insert('rotation_quaternion', frame=SHOT_A[1]); pb.keyframe_insert('location', frame=SHOT_A[1])
bpy.data.objects.remove(src)
walk_end = n

# Walk path: rig local -Y  ->  world -X (right to left across the room, in front of the sofa)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "CONSTANT"
rig.location = (2.3, -0.15, 0)
rig.rotation_euler = (0, 0, math.radians(-90))
rig.keyframe_insert("location", frame=1)
rig.keyframe_insert("rotation_euler", frame=1)

# hold the last walk pose until the cut
sc.frame_set(walk_end)
hips_end_world = rig.matrix_world @ rig.pose.bones["Hips"].head

# ---------------- standing acting pose (shot B) ----------------
B0 = SHOT_B[0]
# place rig so Milo stands where the walk ended, now facing camera (-Y)
rig.location = (hips_end_world.x, hips_end_world.y, 0)
rig.rotation_euler = (0, 0, math.radians(22))
rig.keyframe_insert("location", frame=B0)
rig.keyframe_insert("rotation_euler", frame=B0)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "BEZIER"

vl = bpy.context.view_layer
sc.frame_set(B0)
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix()
vl.update()


def aim(bone, world_dir):
    pb = rig.pose.bones[bone]
    cur = (rig.matrix_world.to_3x3() @ (pb.tail - pb.head)).normalized()
    q = cur.rotation_difference(Vector(world_dir).normalized())
    w = (rig.matrix_world @ pb.matrix).to_3x3()
    head = (rig.matrix_world @ pb.matrix).translation
    m = (q.to_matrix() @ w).to_4x4()
    m.translation = head
    pb.matrix = rig.matrix_world.inverted() @ m
    vl.update()


def key_all(frame, bones=None):
    for pb in rig.pose.bones:
        if bones and pb.name not in bones:
            continue
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("location", frame=frame)


rz = rig.matrix_world.to_3x3()
side = rz @ Vector((1, 0, 0))
fwd = rz @ Vector((0, -1, 0))
# arms relaxed down, slight forward, elbows soft
aim("LeftArm", side * 0.18 + fwd * 0.05 + Vector((0, 0, -1)))
aim("RightArm", -side * 0.18 + fwd * 0.05 + Vector((0, 0, -1)))
aim("LeftForeArm", side * 0.05 + fwd * 0.25 + Vector((0, 0, -1)))
aim("RightForeArm", -side * 0.05 + fwd * 0.25 + Vector((0, 0, -1)))
base_pose = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}


def pose_at(frame, head_pitch=0.0, head_yaw=0.0, chest=0.0, shoulders=0.0):
    for pb in rig.pose.bones:
        pb.matrix_basis = base_pose[pb.name].copy()
    def rot(bone, x=0, y=0, z=0):
        pb = rig.pose.bones[bone]
        pb.rotation_quaternion = pb.rotation_quaternion @ Euler((x, y, z)).to_quaternion()
    rot("Head", math.radians(head_pitch), math.radians(head_yaw), 0)
    rot("Neck", math.radians(head_pitch * 0.4), math.radians(head_yaw * 0.3), 0)
    rot("Spine1", math.radians(chest), 0, 0)
    rot("LeftShoulder", 0, 0, math.radians(shoulders))
    rot("RightShoulder", 0, 0, math.radians(-shoulders))
    key_all(frame)


# acting beats (head down -> looks up, annoyed -> says line -> regret)
beats = [
    (B0, dict(head_pitch=14, head_yaw=-6, chest=4, shoulders=3)),
    (B0 + 18, dict(head_pitch=12, head_yaw=-4, chest=4.5, shoulders=3)),
    (B0 + 30, dict(head_pitch=-3, head_yaw=4, chest=1, shoulders=-2)),
    (B0 + 55, dict(head_pitch=-5, head_yaw=7, chest=0, shoulders=-4)),
    (B0 + 85, dict(head_pitch=-2, head_yaw=2, chest=1, shoulders=-2)),
    (B0 + 110, dict(head_pitch=10, head_yaw=-5, chest=4, shoulders=4)),
    (SHOT_B[1], dict(head_pitch=16, head_yaw=-8, chest=6, shoulders=6)),
]
for f, kw in beats:
    pose_at(f, **kw)

# hold walk pose through shot A: key the last walk frame at SHOT_A end
sc.frame_set(walk_end)

# constant interpolation for the object transform cut
for fc in all_fcurves(rig.animation_data.action):
    if fc.data_path in ("location", "rotation_euler"):
        for k in fc.keyframe_points:
            k.interpolation = 'CONSTANT'

# ---------------- face ----------------
kb = {k.name: k for k in body.data.shape_keys.key_blocks}


def face(frame, **vals):
    for name, v in vals.items():
        for k in kb:
            if k.lower() == name.lower():
                kb[k].value = v
                kb[k].keyframe_insert("value", frame=frame)


ALL = ["eyeBlinkLeft", "eyeBlinkRight", "browDownLeft", "browDownRight", "browInnerUp",
       "mouthFrownLeft", "mouthFrownRight", "jawOpen", "mouthFunnel", "mouthClose",
       "mouthPucker", "eyeLookDownLeft", "eyeLookDownRight", "mouthPressLeft", "mouthPressRight",
       "mouthSmileLeft", "mouthSmileRight", "eyeSquintLeft", "eyeSquintRight", "mouthShrugLower"]
face(1, **{n: 0.0 for n in ALL})
# shot A: neutral with a blink
for f, v in ((40, 0), (43, 1), (46, 0)):
    face(f, eyeBlinkLeft=v, eyeBlinkRight=v)

S = B0
sad = dict(browInnerUp=0.55, mouthFrownLeft=0.35, mouthFrownRight=0.35, eyeLookDownLeft=0.5, eyeLookDownRight=0.5)
face(S, **{**{n: 0.0 for n in ALL}, **sad})
face(S + 20, **sad)
# looks up, annoyed
annoyed = dict(browInnerUp=0.0, browDownLeft=0.7, browDownRight=0.7, mouthFrownLeft=0.3, mouthFrownRight=0.3,
               eyeLookDownLeft=0.0, eyeLookDownRight=0.0, eyeSquintLeft=0.35, eyeSquintRight=0.35,
               mouthPressLeft=0.4, mouthPressRight=0.4)
face(S + 30, **annoyed)
for f, v in ((S + 33, 0), (S + 35, 1), (S + 38, 0)):
    face(f, eyeBlinkLeft=v, eyeBlinkRight=v)

# "Grandpa... I'm not a dog."  (syllable-level mouth shapes)
T = S + 42
seq = [  # (offset frames, jawOpen, funnel, close, pucker)
    (0, 0.05, 0, 0.0, 0), (3, 0.30, 0, 0, 0), (7, 0.12, 0, 0, 0), (10, 0.38, 0, 0, 0),  # Gran-
    (14, 0.0, 0, 0.6, 0), (16, 0.35, 0, 0, 0), (21, 0.05, 0, 0, 0),                      # -pa
    (30, 0.05, 0, 0, 0), (33, 0.28, 0, 0, 0), (36, 0.0, 0, 0.6, 0),                      # I'm
    (39, 0.18, 0, 0, 0), (42, 0.32, 0, 0, 0), (45, 0.08, 0, 0, 0),                       # not
    (48, 0.22, 0, 0, 0), (51, 0.10, 0, 0, 0),                                             # a
    (54, 0.20, 0.3, 0, 0.2), (57, 0.35, 0.55, 0, 0.3), (61, 0.15, 0.2, 0, 0), (64, 0.02, 0, 0, 0),  # dog
]
for off, jaw, fun, clo, puk in seq:
    face(T + off, jawOpen=jaw, mouthFunnel=fun, mouthClose=clo, mouthPucker=puk)
face(T + 20, browDownLeft=0.75, browDownRight=0.75)
face(T + 64, browDownLeft=0.8, browDownRight=0.8, mouthPressLeft=0.5, mouthPressRight=0.5)

# beat of regret
R = T + 80
face(R, browDownLeft=0.2, browDownRight=0.2, browInnerUp=0.3, eyeSquintLeft=0.1, eyeSquintRight=0.1,
     mouthPressLeft=0.2, mouthPressRight=0.2)
for f, v in ((R + 6, 0), (R + 8, 1), (R + 12, 0)):
    face(f, eyeBlinkLeft=v, eyeBlinkRight=v)
face(R + 40, browDownLeft=0.0, browDownRight=0.0, browInnerUp=0.75, mouthFrownLeft=0.5, mouthFrownRight=0.5,
     eyeLookDownLeft=0.55, eyeLookDownRight=0.55, mouthShrugLower=0.3, mouthPressLeft=0.0, mouthPressRight=0.0)
face(SHOT_B[1], browInnerUp=0.8, mouthFrownLeft=0.55, mouthFrownRight=0.55, eyeLookDownLeft=0.6, eyeLookDownRight=0.6)

# ---------------- cameras ----------------
def cam(name, lens):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.data.lens = lens
    c.data.sensor_width = 36
    return c


def look(c, target):
    d = Vector(target) - c.location
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# Shot A: wide, low "hero" angle, slow push-in + pan following Milo
camA = cam("CamA", 26)
for f, loc in ((1, (1.6, -3.4, 0.62)), (SHOT_A[1], (0.7, -3.0, 0.72))):
    camA.location = loc
    camA.keyframe_insert("location", frame=f)
tc = camA.constraints.new('TRACK_TO')
tc.target = rig
tc.subtarget = "Spine1"
tc.track_axis = 'TRACK_NEGATIVE_Z'
tc.up_axis = 'UP_Y'
tc.influence = 0.85

# Shot B: medium close-up at face height, slow push-in, handheld drift, shallow DOF
sc.frame_set(B0)
head_w = rig.matrix_world @ rig.pose.bones["Head"].head
eye_h = head_w.z + 0.07
camB = cam("CamB", 50)
camB.data.dof.use_dof = True
camB.data.dof.aperture_fstop = 2.0
focus = bpy.data.objects.new("Focus", None)
sc.collection.objects.link(focus)
focus.location = (head_w.x, head_w.y, eye_h)
camB.data.dof.focus_object = focus
for f, dist, dz in ((B0, 1.25, -0.05), (SHOT_B[1], 0.85, -0.03)):
    camB.location = (head_w.x + 0.55 * dist, head_w.y - 0.85 * dist, eye_h + dz)
    look(camB, (head_w.x + 0.04, head_w.y, eye_h - 0.04))
    camB.keyframe_insert("location", frame=f)
    camB.keyframe_insert("rotation_euler", frame=f)
try:
    for fc in all_fcurves(camB.animation_data.action):
        if fc.data_path == "rotation_euler":
            mod = fc.modifiers.new('NOISE')
            mod.scale = 40
            mod.strength = 0.006
except Exception as e:
    print("noise skipped", e)

mA = sc.timeline_markers.new("A", frame=1)
mA.camera = camA
mB = sc.timeline_markers.new("B", frame=B0)
mB.camera = camB
sc.camera = camA

# ---------------- render settings ----------------
r = sc.render
r.resolution_x, r.resolution_y = int(os.environ.get("RX", 540)), int(os.environ.get("RY", 960))
r.engine = 'CYCLES'
sc.cycles.samples = int(os.environ.get("SAMPLES", 16))
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
r.use_motion_blur = True
r.motion_blur_shutter = 0.35
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
r.image_settings.file_format = 'PNG'
r.filepath = os.path.join(HERE, "frames", "f_")
r.use_persistent_data = True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "pilot.blend"))
print("BUILT walk_end", walk_end, "B0", B0)
