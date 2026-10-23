"""Retarget a CMU BVH (MotionBuilder skeleton) onto an MPFB cmu_mb rig.

Method: put the target into the source's rest pose by aligning bone directions
(once), store per-bone world-space rotation offsets, then for each frame set
target_world_rot = source_world_rot @ offset.  Hips translation is scaled by
the leg-length ratio.  Result is keyed onto the target rig.
"""
import bpy
from mathutils import Matrix, Vector


def _hier(arm):
    out = []
    def walk(b):
        out.append(b.name)
        for c in b.children:
            walk(c)
    for b in arm.data.bones:
        if b.parent is None:
            walk(b)
    return out


def _world_rot(arm, pb):
    return (arm.matrix_world @ pb.matrix).to_3x3().normalized()


def _set_world_rot(arm, pb, wrot):
    head = (arm.matrix_world @ pb.matrix).translation
    m = wrot.to_4x4()
    m.translation = head
    pb.matrix = arm.matrix_world.inverted() @ m


def retarget(src, tgt, frame_start, frame_end, step, out_start=1, loc_scale=None,
             root_motion=True, bones=None, z_offset=0.0):
    scene = bpy.context.scene
    vl = bpy.context.view_layer
    names = [n for n in _hier(tgt) if n in src.pose.bones and (bones is None or n in bones)]

    # 1) source at rest
    src_action = src.animation_data.action
    src.animation_data.action = None
    for pb in src.pose.bones:
        pb.matrix_basis = Matrix()
    for pb in tgt.pose.bones:
        pb.matrix_basis = Matrix()
    vl.update()

    # 2) align target bone directions to source rest directions
    for n in names:
        spb, tpb = src.pose.bones[n], tgt.pose.bones[n]
        s_dir = (src.matrix_world.to_3x3() @ (spb.tail - spb.head))
        t_dir = (tgt.matrix_world.to_3x3() @ (tpb.tail - tpb.head))
        if s_dir.length < 1e-6 or t_dir.length < 1e-6:
            continue
        q = t_dir.normalized().rotation_difference(s_dir.normalized())
        w = _world_rot(tgt, tpb)
        _set_world_rot(tgt, tpb, q.to_matrix() @ w)
        vl.update()

    offsets = {}
    for n in names:
        offsets[n] = _world_rot(src, src.pose.bones[n]).inverted() @ _world_rot(tgt, tgt.pose.bones[n])

    src_hip_rest = (src.matrix_world @ src.pose.bones['Hips'].head).copy()
    tgt_hip_rest = (tgt.matrix_world @ tgt.pose.bones['Hips'].head).copy()
    if loc_scale is None:
        def leglen(a):
            return sum((a.pose.bones[b].tail - a.pose.bones[b].head).length * a.matrix_world.to_scale()[0]
                       for b in ('LeftUpLeg', 'LeftLeg'))
        loc_scale = leglen(tgt) / max(leglen(src), 1e-6)

    for pb in tgt.pose.bones:
        pb.matrix_basis = Matrix()
    src.animation_data.action = src_action
    vl.update()

    if tgt.animation_data is None:
        tgt.animation_data_create()
    act = bpy.data.actions.new(tgt.name + "_retarget")
    tgt.animation_data.action = act

    f_out = out_start
    f = frame_start
    first_src_hip = None
    while f <= frame_end:
        scene.frame_set(int(f))
        vl.update()
        src_hip = src.matrix_world @ src.pose.bones['Hips'].head
        if first_src_hip is None:
            first_src_hip = src_hip.copy()
        for n in names:
            tpb = tgt.pose.bones[n]
            wrot = _world_rot(src, src.pose.bones[n]) @ offsets[n]
            if n == 'Hips':
                d = (src_hip - first_src_hip) * loc_scale
                if not root_motion:
                    d.x = d.y = 0.0
                head = tgt_hip_rest + d
                head.z = tgt_hip_rest.z + (src_hip.z - first_src_hip.z) * loc_scale + z_offset
                m = wrot.to_4x4()
                m.translation = head
                tpb.matrix = tgt.matrix_world.inverted() @ m
            else:
                _set_world_rot(tgt, tpb, wrot)
            vl.update()
        for n in names:
            tpb = tgt.pose.bones[n]
            tpb.keyframe_insert('rotation_quaternion' if tpb.rotation_mode == 'QUATERNION' else 'rotation_euler', frame=f_out)
            if n == 'Hips':
                tpb.keyframe_insert('location', frame=f_out)
        f += step
        f_out += 1
    return act, f_out - out_start
