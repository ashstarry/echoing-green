exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
from mathutils.bvhtree import BVHTree
def chain(o):
 a=[]
 while o:a.append(o);o=o.parent
 return a
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
def place(o,p):move(o,Vector(p)-o.matrix_world.translation);bpy.context.view_layer.update()
rec=json.loads((OUT/'revision-record.json').read_text());normalized=[]
# Earlier building transforms had stretched several residents in depth. Restore body proportions.
for root in [o for o in s.objects if o.get('decision_kind')=='resident']:
 if max(root.scale)-min(root.scale)>.015:
  old=list(root.scale);v=root.scale.z;root.scale=(v,v,v);normalized.append({'actor':root.name,'before':old,'after':v})
tea=bpy.data.objects['tea_house']
for o in tea.children_recursive:
 if o.name.startswith(('CP07 ceramic serving bowl','CP07 dish content')):move(o,tea.matrix_world.to_3x3()@Vector((0,-.12,0)))
duck=bpy.data.objects['duck_0'];duck_delta=RIGHT*.36+BACK*.32;move(duck,duck_delta)
for o in s.objects:
 if o.name.startswith('CP08 duck wake duck_0'):move(o,duck_delta)

# Old lily fragments are replaced by coherent pads in verified free patches of water.
for name in [o.name for o in s.objects if o.type in ['MESH','CURVE'] and 'lily' in o.name.lower()]:
 o=bpy.data.objects.get(name)
 if o:erase(o)
bpy.context.view_layer.update();cat=bpy.data.objects['doorstep_cat'];dg=bpy.context.evaluated_depsgraph_get();worldv=[];worldf=[];worldnames=[];floorv=[];floorf=[];catv=[];catf=[]
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render or any(c.hide_render or c.name.startswith('12_') for c in o.users_collection):continue
 if o.name=='CP02 pond' or any(k in o.name.lower() for k in ['visible paper rain','paper water glint','duck wake','water ripple','rain ripple']):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();v=[ev.matrix_world@p.co for p in me.vertices];f=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear()
 if cat in chain(o):
  off=len(catv);catv.extend(v);catf.extend(tuple(off+i for i in t) for t in f);continue
 off=len(worldv);worldv.extend(v);worldf.extend(tuple(off+i for i in t) for t in f);worldnames.extend([o.name]*len(f))
 n=o.name.lower()
 if not any(k in n for k in ['roof','shingle','seat','bench','table']) and any(k in n for k in ['floor','paving','platform','deck','tread','landing','step','island paper layer','stone ring']):
  off=len(floorv);floorv.extend(v);floorf.extend(tuple(off+i for i in t) for t in f)
world=BVHTree.FromPolygons(worldv,worldf,all_triangles=True);floor=BVHTree.FromPolygons(floorv,floorf,all_triangles=True);old=cat.matrix_world.translation.copy();low=min(p.z for p in catv)-old.z;candidates=[]
for xx in [280,290,300,314,325,338]:
 for yy in [485,500,512,524]:
  p=xy((xx,yy));hit,n,i,d=floor.ray_cast(p+Vector((0,0,.6)),Vector((0,0,-1)),1.2)
  if hit is None:continue
  p.z=hit.z-low+.003;delta=p-old;bv=BVHTree.FromPolygons([v+delta for v in catv],catf,all_triangles=True);pairs=bv.overlap(world);candidates.append({'position':list(p),'pixel':[xx,yy],'pairs':len(pairs),'score':len(pairs)*100000+(xx-290)**2+(yy-485)**2,'obstacles':sorted(set(worldnames[b] for a,b in pairs))})
best=min(candidates,key=lambda q:q['score']);place(cat,Vector(best['position']))

# Clearance-sampled lily locations use actual boat, duck, fish, bridge and bank geometry.
pond=bpy.data.objects['CP02 pond'];ps=[pond.matrix_world@v.co for v in pond.data.vertices];top=max(p.z for p in ps);outline=[p for p in ps if abs(p.z-top)<1e-5]
def inside(p):
 yes=False
 for a,b in zip(outline,outline[1:]+outline[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:yes=not yes
 return yes
free=[]
for i in range(17):
 for j in range(12):
  p=rb(4.7+i*.34,-4.8+j*.32,top+.025)
  if not inside(p):continue
  q,n,idx,d=world.find_nearest(p+Vector((0,0,.025)))
  if q is not None and d>.24:free.append(p)
targets=[(5.2,-4.0),(6.1,-4.6),(7.0,-4.6),(9.6,-3.7),(10,-2.8),(9.6,-2.0),(5.5,-2.8),(7.5,-2.0)];selected=[];COL=cols['05_Water_Garden'];new=[]
for i,target in enumerate(targets):
 available=[p for p in free if all((p-q).length>.46 for q in selected)]
 if not available:continue
 p=min(available,key=lambda q:(q-rb(*target,top+.025)).length);selected.append(p);root=asset('water_lily_'+str(i),p);root['decision_entity_id']='plant.water_lily_'+str(i);root['decision_kind']='plant';root['decision_actions']=json.dumps(['float','sway','bloom_state']);root['decision_status']='authoring_only_runtime_unimplemented';root['medium']='water';root['movable']=True
 with under(root):
  # A notched, folded pad with a shallow edge, rather than a cylinder.
  vs=[(0,0,.008)]+[(.18*math.cos(a),.18*math.sin(a),0) for a in [j*2*PI/15 for j in range(15)]];fs=[(0,j+1,(j+1)%15+1) for j in range(1,15)];mesh('CP09 floating paper lily pad',vs,fs,sage)
  if i%2==0:bloom('CP09 water blossom',(0,0,.025),.25,pinklight,root)
 new.append(root.name)
rec['final_contact_adjustments']={'normalized_body_depth':normalized,'serving_ware_forward_shift':.12,'duck_separation':list(duck_delta),'cat_clear_location':best,'lily_clearance_radius':.24,'new_water_lilies':new};bpy.context.view_layer.update();(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'final-contact-candidate.blend'));print('FINAL_CONTACT_CANDIDATE',json.dumps(best),'LILIES',len(new),flush=True)
