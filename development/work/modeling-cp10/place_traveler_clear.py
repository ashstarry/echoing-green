exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
exec(compile((WORK/'rail_helpers.py').read_text(),'<rail helpers>','exec'))
root=bpy.data.objects['station_traveler'];station=bpy.data.objects['station_main'];dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[];owners=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection)or root in list(ancestry(o)):continue
 if 'visible paper rain'in o.name:continue
 v,f=geometry(o,dg);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in t)for t in f);owners.extend([o.name]*len(f))
door=bpy.data.objects['station_entry_door'];saved=door.matrix_basis.copy()
for delta in [.185,.37,.555,.74]:
 door.matrix_basis=saved@Matrix.Translation((delta,0,0));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for o in door.children_recursive:
  if o.type not in ['MESH','CURVE']:continue
  v,f=geometry(o,dg);off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in t)for t in f);owners.extend([o.name+' open sample']*len(f))
door.matrix_basis=saved;bpy.context.view_layer.update();world=BVHTree.FromPolygons(vv,ff,all_triangles=True);inv=root.matrix_world.inverted();v=[];f=[];soles=[]
for o in root.children_recursive:
 if o.type!='MESH':continue
 ps,ts=geometry(o,bpy.context.evaluated_depsgraph_get());off=len(v);v.extend(inv@p for p in ps);f.extend(tuple(off+i for i in t)for t in ts)
 if o.name.startswith('Shoe'):
  low=min(p.z for p in ps);soles.extend(inv@p for p in ps if p.z<low+.001)
platform=bpy.data.objects['CP10 curved station platform'];pv,pf=geometry(platform,bpy.context.evaluated_depsgraph_get());floor=BVHTree.FromPolygons(pv,pf,all_triangles=True);basis=root.matrix_world.copy();basis.translation=Vector();candidates=[]
for x in [-2.1,-1.95,-1.8,-1.65,-1.5,-1.35,-1.2,-1.05,-.9,-.75,-.6,-.45,-.3,-.15,0,.15,.3,.45,.6,.75,.9,1.05,1.2,1.35,1.5,1.65,1.8,1.95,2.1,2.25,2.4,2.55,2.7,2.85,3,3.15,3.3,3.45]:
 for y in [-.92,-.84,-.76,-.68,-.60,-.52,-.44,-.36,-.28,-.2,-.1,0,.1,.2,.3]:
  p=station.matrix_world@Vector((x,y,0));p.z=root.matrix_world.translation.z;m=Matrix.Translation(p)@basis;supported=True
  for local in soles:
   q=m@local;hit,n,i,d=floor.ray_cast(q+Vector((0,0,.02)),Vector((0,0,-1)),.3)
   if hit is None or not -.001<=q.z-hit.z<=.012:supported=False;break
  if not supported:continue
  bv=BVHTree.FromPolygons([m@q for q in v],f,all_triangles=True)
  if bv.overlap(world):continue
  head=m@Vector((0,0,1.08));hit,n,i,d=world.ray_cast(head-FWD*30,FWD,29.84)
  if hit is not None:continue
  candidates.append({'x':x,'y':y,'score':(x+.62)**2+(y+.76)**2,'position':list(p)})
assert candidates,'No valid waiting position found';best=min(candidates,key=lambda x:x['score']);root.location=best['position'];bpy.context.view_layer.update();r=json.loads((OUT/'revision-record.json').read_text());r['station_rail_repair']['traveler_validated_placement']={'chosen':best,'valid_candidates':len(candidates),'checks':'Complete body against scene plus sampled open-door poses; all actual shoe sole corners supported; head sightline clear'};(OUT/'revision-record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'station-ready.blend'));print('TRAVELER_POSITION',best,'VALID',len(candidates),flush=True)
