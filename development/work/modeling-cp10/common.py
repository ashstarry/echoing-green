import bpy,math,json,ast,random
from pathlib import Path
from mathutils import Vector,Matrix
from contextlib import contextmanager
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-10';WORK=ROOT/'work/modeling-cp10';s=bpy.context.scene;cam=s.camera;PI=math.pi;Z=.61;R=random.Random(80825);PARENT=None;assets=[]
cols={c.name:c for c in bpy.data.collections};COL=cols['01_Plaza'];templates={k:bpy.data.meshes['Shared '+k] for k in ['cube','sphere','ico','cyl']}
src=ast.parse((ROOT/'work/modeling-cp02/refine_and_present.py').read_text());node=next(n for n in src.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='aliases' for t in n.targets));exec(compile(ast.Module(body=[node],type_ignores=[]),'<aliases>','exec'))
for k,n in aliases.items():globals()[k]=bpy.data.materials[n]
src=ast.parse((ROOT/'work/modeling-cp01/build_town.py').read_text());allow={'setmat','mesh','unit','primitive','box','cyl','ellipsoid','ico','beam','taper','path','ring','asset','under','window','lantern','leaf','roof','ellipse_solid','person'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<helpers>','exec'))
leafmesh=bpy.data.meshes['Shared folded leaf'];flower_mesh=bpy.data.meshes['CP07 shared five-petal paper flower | 106 triangles'];coatmats=[bpy.data.materials['Resident coat '+str(i)] for i in range(6)];terr=[bpy.data.materials['Paper land layer '+str(i)] for i in range(5)]
Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));UP=Q@Vector((0,1,0))
def rb(r,b,z=Z):
 p=RIGHT*r+BACK*b;p.z=z;return p
def xy(pixel,z=Z):
 p=cam.location+RIGHT*((pixel[0]/1672-.5)*cam.data.ortho_scale)+UP*((.5-pixel[1]/941)*cam.data.ortho_scale/(1672/941));return p+FWD*((z-p.z)/FWD.z)
def pixel(p):
 v=world_to_camera_view(s,cam,p);return [v.x*1672,(1-v.y)*941]
def erase(o):
 names=[c.name for c in o.children_recursive]+[o.name]
 for n in names:
  x=bpy.data.objects.get(n)
  if x:bpy.data.objects.remove(x,do_unlink=True)
def variant(base,name,c):
 m=base.copy();m.name=name;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.diffuse_color=(*c,1);return m
def bloom(name,p,scale,mat,parent=None):
 o=bpy.data.objects.new(name,flower_mesh);COL.objects.link(o);o.location=p;o.scale=(scale,scale,scale);o.rotation_euler=(.15,R.uniform(-.2,.2),R.random()*2*PI);o.parent=parent or PARENT;o.material_slots[0].link='OBJECT';o.material_slots[0].material=mat;return o
