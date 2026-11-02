import bpy,hashlib,json,array
def scene_signature(scene):
 rows={};mesh_cache={}
 for o in scene.objects:
  if o.type in ['LIGHT','CAMERA']:continue
  row={'type':o.type,'matrix':[round(v,7)for r in o.matrix_world for v in r],'hide_render':o.hide_render,'parent':o.parent.name if o.parent else None,'entity_id':o.get('decision_entity_id'),'part_id':o.get('decision_part_id'),'owner':o.get('decision_owner')}
  if o.type=='MESH':
   key=o.data.as_pointer()
   if key not in mesh_cache:
    h=hashlib.sha256();a=array.array('f',[0.0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());h.update(str([(p.loop_start,p.loop_total)for p in o.data.polygons]).encode());mesh_cache[key]=h.hexdigest()
   row['geometry']=mesh_cache[key];row['modifiers']=[(m.name,m.type,m.show_render)for m in o.modifiers]
  elif o.type=='CURVE':
   row['geometry']=[{'type':sp.type,'points':[list(p.co)for p in sp.points],'bezier':[list(p.co)for p in sp.bezier_points]}for sp in o.data.splines];row['bevel_depth']=o.data.bevel_depth;row['bevel_resolution']=o.data.bevel_resolution
  rows[o.name]=row
 cam=scene.camera;camera={'matrix':[round(v,7)for r in cam.matrix_world for v in r],'type':cam.data.type,'scale':cam.data.ortho_scale,'lens':cam.data.lens,'shift':[cam.data.shift_x,cam.data.shift_y]}
 return {'objects':rows,'camera':camera,'collections':{c.name:{'hide_render':c.hide_render,'hide_viewport':c.hide_viewport}for c in bpy.data.collections},'digest':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
