import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-08';s=bpy.context.scene;cam=s.camera;dg=bpy.context.evaluated_depsgraph_get();Q=cam.rotation_euler.to_quaternion();RIGHT=Q@Vector((1,0,0));BACK=Vector((-RIGHT.y,RIGHT.x,0));FWD=Q@Vector((0,0,-1));label=sys.argv[sys.argv.index('--')+1] if '--'in sys.argv else 'CP08'
def chain(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
verts=[];tris=[];owners=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 ancestors=chain(o)
 if any(any(c.name in ['08_Residents_SCALE_PROXIES','09_Animals_SCALE_PROXIES'] for c in x.users_collection) for x in ancestors):continue
 if any(x.name in ['street_bicycle','tram_car_front','tram_car_rear','pond_boat','pond_fish_0','pond_fish_1'] for x in ancestors):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(verts);verts.extend(ev.matrix_world@v.co for v in me.vertices)
 for t in me.loop_triangles:tris.append(tuple(off+i for i in t.vertices));owners.append(o.name)
 ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,tris,all_triangles=True);center=bpy.data.objects['plaza_ground'].matrix_world.translation.copy();grid=[];step=.35
for j in range(-14,15):
 for i in range(-14,15):
  if i*i+j*j>14*14 or i*i+j*j<4*4:continue
  p=center+RIGHT*(i*step)+BACK*(j*step);p.z=.68;hit,n,idx,d=bvh.ray_cast(p+Vector((0,0,1.5)),Vector((0,0,-1)),2.0)
  supported=hit is not None and .57<=hit.z<=.70
  row={'foot':[p.x,p.y,hit.z if hit else .61],'supported_ground':supported,'body_clear':False,'visible_samples':0}
  if supported:
   p.z=hit.z;clear=True
   for h in [.25,.65,1.05,1.25]:
    q,normal,idx,dist=bvh.find_nearest(p+Vector((0,0,h)))
    if q is not None and dist<.218:clear=False;break
   row['body_clear']=clear
   if clear:
    for h in [.35,.75,1.10]:
     target=p+Vector((0,0,h));q,n,idx,d=bvh.ray_cast(target-FWD*40,FWD,39.97)
     if q is None:row['visible_samples']+=1
  grid.append(row)
# Probe actual musician component centers; self occlusion is allowed, other objects are named.
actor=bpy.data.objects['musician'];probe=[]
for o in actor.children_recursive:
 if o.type!='MESH' or not o.name.startswith(('Head.','CP07 guitar paper body','Hand.','CP08 musician hand','Seated shin.','Shoe.')):continue
 p=o.matrix_world@(sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices));hit,loc,n,fi,obj,ma=s.ray_cast(dg,p-FWD*40,FWD,distance=40.1);visible=obj is not None and actor in chain(obj);probe.append({'component':o.name,'visible':visible,'first_hit':obj.name if obj else None})
record={'checkpoint':label,'method':'Same .35-unit grid in a radius 4.9 central region, excluding radius 1.4 around tree. Down-ray support between .57 and .70; four radius-.22 body sphere probes; camera probes at .35/.75/1.10. People, animals and moving vehicles excluded as temporary occupants. Not navmesh, animated clearance or total world area.','grid_samples':len(grid),'clear_ground_samples':sum(x['body_clear'] for x in grid),'clear_and_partly_visible_samples':sum(x['body_clear'] and x['visible_samples']>0 for x in grid),'clear_and_three_probes_visible_samples':sum(x['body_clear'] and x['visible_samples']==3 for x in grid),'sample_cell_area':step*step,'musician_component_visibility':probe,'samples':grid}
(OUT/(label.lower()+'-activity-area.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in record.items() if k not in ['samples','method']},ensure_ascii=False,indent=2))
