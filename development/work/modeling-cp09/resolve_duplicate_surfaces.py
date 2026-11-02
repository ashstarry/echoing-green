exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
rec=json.loads((OUT/'revision-record.json').read_text());seen={};removed=[]
for o in sorted([o for o in s.objects if o.type=='MESH' and o.name.startswith('CP07 district fence post')],key=lambda o:o.name):
 key=tuple(sorted(tuple(round(v,5)for v in o.matrix_world@p.co)for p in o.data.vertices))
 if key in seen:removed.append({'removed':o.name,'retained':seen[key]});erase(o)
 else:seen[key]=o.name
a=bpy.data.objects['CP05 residence side walk'];b=bpy.data.objects['CP05 landing to residence link']
for o in [a,b]:
 o.data=o.data.copy();inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if abs(p.z-1.243)<.005:p.z=1.243
  if abs(p.z-1.173)<.005:p.z=1.173
  v.co=inv@p
 o.data.update()
bpy.ops.object.select_all(action='DESELECT');a.select_set(True);bpy.context.view_layer.objects.active=a;mod=a.modifiers.new('CP09 union overlapping floor plates','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=b;bpy.ops.object.modifier_apply(modifier=mod.name);erase(b)
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('CP05 residence walkway bracket'):
  o.data=o.data.copy();inv=o.matrix_world.inverted()
  for v in o.data.vertices:
   p=o.matrix_world@v.co
   if p.z>1.171:p.z=1.171
   v.co=inv@p
  o.data.update()
rec['duplicate_surface_cleanup']={'duplicate_fence_posts':removed,'deck':'Exact union of overlapping residence side-walk and landing-link volumes; one exterior top surface at Z=1.243','brackets':'Trimmed to below the floor underside','cause_note':'Not all dark patches were renderer-only artifacts; duplicate/copanar source geometry was found and repaired.'};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print('DUPLICATE_REPAIRS',json.dumps(rec['duplicate_surface_cleanup']),flush=True)
