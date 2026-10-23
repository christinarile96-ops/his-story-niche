import bpy, math, mathutils, sys
from mathutils import Matrix, Vector, Quaternion
G="/home/user/threejs-models/examples/models/gltf/"
A="/home/user/his-story-niche/assets/01-grandpas-whistle/"
OUT=sys.argv[sys.argv.index('--')+1]
FR=150
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc.render.fps=30; sc.frame_start=1; sc.frame_end=FR

def imp(p):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=p); return [o for o in bpy.data.objects if o not in before]
tgt_objs=imp(G+"readyplayer.me.glb"); tgt=[o for o in tgt_objs if o.type=='ARMATURE'][0]
src_objs=imp(G+"Xbot.glb"); src=[o for o in src_objs if o.type=='ARMATURE'][0]
for o in src_objs:
    if o.type=='MESH': o.hide_render=True; o.hide_viewport=True
src.animation_data.action=bpy.data.actions['walk']
act=bpy.data.actions['walk']; L=int(act.frame_range[1]); print('walk len',L)

# ---- retarget: match each target bone's armature-space rotation delta to the source
def amap(n): return 'mixamorig:'+n
pairs=[(b.name,amap(b.name)) for b in tgt.data.bones if amap(b.name) in src.data.bones]
print('mapped bones',len(pairs))
src_rest={n:(src.matrix_world@src.data.bones[n].matrix_local).to_quaternion() for _,n in pairs}
tgt_rest={n:(tgt.matrix_world@tgt.data.bones[n].matrix_local).to_quaternion() for n,_ in pairs}
hip_src0=None
src_h=(src.matrix_world@src.data.bones['mixamorig:Head'].head_local).z; tgt_h=(tgt.matrix_world@tgt.data.bones['Head'].head_local).z
scale=tgt_h/src_h
order=[b.name for b in tgt.data.bones]  # parents before children
for f in range(1,FR+1):
    sf=(f-1)%L+1; sc.frame_set(sf); bpy.context.view_layer.update()
    world_rot={}
    for tn,sn in pairs:
        sw=(src.matrix_world@src.pose.bones[sn].matrix).to_quaternion()
        world_rot[tn]=sw@src_rest[sn].inverted()@tgt_rest[tn]
    sc.frame_set(f)
    for tn in order:
        if tn not in world_rot: continue
        pb=tgt.pose.bones[tn]
        m=tgt.matrix_world.inverted().to_quaternion()@world_rot[tn]
        loc=pb.matrix.to_translation()
        pb.matrix=Matrix.Translation(loc)@m.to_matrix().to_4x4()
        bpy.context.view_layer.update()
        pb.keyframe_insert('rotation_quaternion',frame=f)
    # hips bob (vertical only, in place) scaled
    sc.frame_set(sf); hs=(src.matrix_world@src.pose.bones['mixamorig:Hips'].matrix).to_translation()
    if hip_src0 is None: hip_src0=hs.copy()
    sc.frame_set(f)
    hp=tgt.pose.bones['Hips']; hp.location=(0,0,0); bpy.context.view_layer.update()
    w=tgt.matrix_world@hp.matrix
    w.translation.z+= (hs.z-hip_src0.z)*scale
    hp.matrix=tgt.matrix_world.inverted()@w; hp.keyframe_insert('location',frame=f)

# walk toward camera (-Y) at ~1.1 m/s
speed=1.1/30
tgt.rotation_euler=(0,0,math.radians(180)) if False else tgt.rotation_euler
tgt.location=(0,4.5,0); tgt.keyframe_insert('location',frame=1)
tgt.location=(0,4.5-speed*FR*1.0,0); tgt.keyframe_insert('location',frame=FR)
for fc in tgt.animation_data.action.fcurves if hasattr(tgt.animation_data.action,'fcurves') else []:
    pass
# face: smile
for o in tgt_objs:
    if o.type=='MESH' and o.data.shape_keys and 'mouthSmile' in o.data.shape_keys.key_blocks:
        o.data.shape_keys.key_blocks['mouthSmile'].value=0.6

# ---- environment
def mat(name,col,rough=0.8):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=col+(1,); b.inputs['Roughness'].default_value=rough; return m
bpy.ops.mesh.primitive_plane_add(size=60,location=(0,10,0)); g=bpy.context.object
gm=mat('grass',(0.12,0.22,0.05)); g.data.materials.append(gm)
# grass noise
nt=gm.node_tree; n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=40
cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.06,0.13,0.03,1); cr.color_ramp.elements[1].color=(0.25,0.35,0.08,1)
nt.links.new(n.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
# stone path slabs
import random; random.seed(2)
sm=mat('stone',(0.45,0.42,0.38),0.9)
y=-3
while y<16:
    bpy.ops.mesh.primitive_cylinder_add(vertices=9,radius=random.uniform(0.32,0.42),depth=0.06,location=(random.uniform(-0.15,0.15),y,0.02))
    s=bpy.context.object; s.scale=(1.1,0.8,1); s.rotation_euler.z=random.random(); s.data.materials.append(sm)
    bev=s.modifiers.new('b','BEVEL'); bev.width=0.03; bev.segments=2
    y+=random.uniform(0.75,0.95)
# picket fences both sides
fm=mat('fence',(0.9,0.88,0.82),0.6)
for side in (-1,1):
    for k in range(40):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(side*2.6,-2+k*0.45,0.45)); p=bpy.context.object; p.scale=(0.05,0.09,0.9); p.data.materials.append(fm)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(side*2.6,7,0.6)); r=bpy.context.object; r.scale=(0.04,18,0.06); r.data.materials.append(fm)
# backdrop: our Nano Banana porch plate far behind
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,30,20),rotation=(math.radians(90),0,0)); bd=bpy.context.object; bd.scale=(36,64.5,1)
bm=bpy.data.materials.new('bd'); bm.use_nodes=True; nt=bm.node_tree; nt.nodes.clear()
ti=nt.nodes.new('ShaderNodeTexImage'); ti.image=bpy.data.images.load(A+'bg_porch.png'); em=nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value=1.0
out=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(ti.outputs['Color'],em.inputs['Color']); nt.links.new(em.outputs['Emission'],out.inputs['Surface']); bd.data.materials.append(bm)
# trees (simple stylised blobs) for parallax
tm=mat('leaf',(0.18,0.28,0.06)); trm=mat('trunk',(0.25,0.16,0.08))
for (x,yy,s) in [(-4.5,6,1.6),(4.8,9,2.0),(-5.5,13,2.2),(5.2,3,1.3)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15*s,depth=3*s,location=(x,yy,1.5*s)); bpy.context.object.data.materials.append(trm)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1.4*s,location=(x,yy,3.2*s)); o=bpy.context.object; o.data.materials.append(tm); o.modifiers.new('s','SUBSURF').levels=2; bpy.ops.object.shade_smooth()
    d=o.modifiers.new('d','DISPLACE'); d.strength=0.35; tx=bpy.data.textures.new('t','CLOUDS'); tx.noise_scale=0.6; d.texture=tx
# lights: golden-hour sun from behind-left + warm sky
sun=bpy.data.lights.new('sun','SUN'); sun.energy=4.5; sun.color=(1,0.78,0.5); sun.angle=math.radians(3)
so=bpy.data.objects.new('sun',sun); sc.collection.objects.link(so); so.rotation_euler=(math.radians(70),0,math.radians(150))
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.75,0.6,0.5,1); bg.inputs[1].default_value=0.9
fill=bpy.data.lights.new('fill','AREA'); fill.energy=250; fill.size=3; fill.color=(0.9,0.95,1)
fo=bpy.data.objects.new('fill',fill); sc.collection.objects.link(fo); fo.location=(2.5,-2,2.2); fo.rotation_euler=(math.radians(70),0,math.radians(35))
# ---- camera: low fisheye-ish tracking shot moving backward in front of him, handheld wobble
cd=bpy.data.cameras.new('cam'); cd.lens=18; cd.dof.use_dof=True; cd.dof.aperture_fstop=2.2
co=bpy.data.objects.new('cam',cd); sc.collection.objects.link(co); sc.camera=co
foc=bpy.data.objects.new('focus',None); sc.collection.objects.link(foc); foc.parent=tgt; foc.location=(0,0,1.4); cd.dof.focus_object=foc
for f in range(1,FR+1):
    u=(f-1)/(FR-1); e=u*u*(3-2*u)
    cy=4.5-speed*f-1.6-0.8*e     # stay ahead, pull away slightly
    co.location=(0.25*math.sin(f/23)+0.6*(1-e), cy, 0.55+0.4*e+0.03*math.sin(f/7))
    look=Vector((0, 4.5-speed*f, 1.35))
    d=(look-co.location); co.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    co.rotation_euler.y+=math.radians(2*math.sin(f/17))
    co.keyframe_insert('location',frame=f); co.keyframe_insert('rotation_euler',frame=f)
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.cycles.use_denoising=True; sc.cycles.device='CPU'
sc.render.use_motion_blur=True; sc.render.motion_blur_shutter=0.5
sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Medium High Contrast'
sc.render.resolution_x,sc.render.resolution_y=720,1280
sc.render.image_settings.file_format='PNG'
sc.render.filepath=OUT+'/f_'
if '--still' in sys.argv:
    sc.frame_start=sc.frame_end=75
bpy.ops.render.render(animation=True)
