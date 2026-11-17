"""Internal Blender scene builder; invoked by render.py."""
import argparse
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--out',required=True);p.add_argument('--frames',type=int,required=True);p.add_argument('--fps',type=int,required=True);p.add_argument('--width',type=int,required=True);p.add_argument('--height',type=int,required=True);p.add_argument('--model');p.add_argument('--primitive')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.out)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
if a.model:
    if Path(a.model).suffix.lower() in ('.glb','.gltf'):
        bpy.ops.import_scene.gltf(filepath=a.model)
    else:
        bpy.ops.wm.obj_import(filepath=a.model)
else:
    bpy.ops.mesh.primitive_cube_add()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
if not meshes:
    raise RuntimeError('The model contains no mesh objects')
bpy.context.view_layer.update()
points=[o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
center=(lo+hi)/2
size=max(hi-lo)
if size<=0:
    raise RuntimeError('The model has zero size')
root=bpy.data.objects.new('Turntable',None);bpy.context.scene.collection.objects.link(root)
for obj in [o for o in bpy.context.scene.objects if o!=root and o.parent is None]:
    matrix=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=matrix
factor=2/size;root.scale=(factor,)*3;root.location=-center*factor
root.rotation_euler.z=0;root.keyframe_insert(data_path='rotation_euler',frame=1)
root.rotation_euler.z=2*math.pi;root.keyframe_insert(data_path='rotation_euler',frame=a.frames+1)
if root.animation_data and root.animation_data.action:
    action=root.animation_data.action
    if hasattr(action,'fcurves'):
        for curve in action.fcurves:
            for key in curve.keyframe_points:key.interpolation='LINEAR'
bpy.ops.object.camera_add(location=(4,-6,3))
camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=3.7
scene=bpy.context.scene;scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(2,-4,5));light=bpy.context.object;light.data.energy=900;light.data.shape='DISK';light.data.size=5
scene.world.color=(0.12,0.12,0.12)
try:
    scene.render.engine='BLENDER_EEVEE_NEXT'
except TypeError:
    scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=a.width;scene.render.resolution_y=a.height;scene.render.resolution_percentage=100;scene.render.fps=a.fps;scene.frame_start=1;scene.frame_end=a.frames
scene.render.image_settings.file_format='PNG';(out/'frames').mkdir();scene.render.filepath=str(out/'frames'/'frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
bpy.ops.render.render(animation=True)
