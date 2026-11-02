exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
rec=json.loads((OUT/'revision-record.json').read_text())
# The rider follows a real bicycle root; keep the stall approach unobstructed.
bike=bpy.data.objects['street_bicycle'];bike.location=xy((987,440));bpy.context.view_layer.update();rider=bpy.data.objects['cyclist'];rider.location=bike.matrix_world@Vector((-.12,0,.29));rider.rotation_euler.z=bike.rotation_euler.z+PI/2;bpy.context.view_layer.update();world=rider.matrix_world.copy();rider.parent=bike;rider.matrix_world=world
# Lower the annex consistently with its parent neighborhood's revised roof hierarchy.
bpy.data.objects['small_wood_home'].scale.z*=.88

# The seated residents retain actual seats after the station/plaza rebalancing.
COL=cols['01_Plaza']
for name,actorname in [('listener_seat','listener'),('station_seat_A','waiting_passenger'),('station_seat_B','waiting_passenger_2')]:
 actor=bpy.data.objects[actorname];root=asset(name,actor.location,actor.rotation_euler.z);root['entity_kind']='seat';root['movable']=True;root['occupied_by']=actorname
 with under(root):
  box('CP08 activity seat top',(0,.03,.44),(.58,.36,.065),woodlight)
  for x in [-.22,.22]:
   for y in [-.10,.16]:box('CP08 activity seat leg',(x,y,.22),(.055,.055,.44),wood)
  if actorname!='listener':
   for x in [-.24,.24]:box('CP08 seat back upright',(x,.20,.64),(.04,.04,.48),wood)
   for h in [.66,.83]:box('CP08 seat back slat',(0,.20,h),(.58,.045,.10),woodlight)

# Open the pond's center and front water, with plants concentrated along its banks.
pond=bpy.data.objects['CP02 pond'];pond.scale.y*=1.16;pond.scale.x*=1.035;pc=pond.matrix_world.translation.copy();removed=[]
for name in [o.name for o in s.objects if o.get('entity_id') and o.name.startswith(('CP07 garden cluster','garden_planter_'))]:
 root=bpy.data.objects.get(name)
 if root is None:continue
 p=root.matrix_world.translation-pc;rho=(p.dot(RIGHT)/3.2)**2+(p.dot(BACK)/2.55)**2
 if rho<.85:removed.append(root.name);erase(root)
for o in list(s.objects):
 if o.parent or not any(c.name=='07_Paper_Foliage' for c in o.users_collection) or o.type!='MESH':continue
 if not o.name.startswith(('CP02 restrained flower bed','CP02 edge planting')):continue
 p=o.matrix_world.translation-pc
 if (p.dot(RIGHT)/3.2)**2+(p.dot(BACK)/2.55)**2<.88:erase(o)
for o in bpy.data.objects['pond_willow_canopy'].children:
 if o.name.startswith('CP08 willow hanging leaf'):o.scale.x*=1.8
bpy.data.objects['CP08 warm tree canopy bounce'].data.energy=78
bpy.data.objects['Warm lantern tree pool'].data.energy=75
rec['activity_space_fixes']={'cyclist_moved_to_pixel':[987,440],'cyclist_parent':'street_bicycle','new_real_seats':['listener_seat','station_seat_A','station_seat_B'],'pond_area_scale_xy':[1.035,1.16],'plants_removed_from_open_water':removed,'annex_height_factor':.88}
rec['baseline_asset_transforms']={n:[list(v) for v in bpy.data.objects[n].matrix_world] for n in rec['cp07_core_transforms']};bpy.context.view_layer.update()
(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
bpy.context.view_layer.update()
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
 for d in pref.devices:d.use=d.type=='METAL'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.cycles.samples=64;s.render.filepath=str(WORK/'activity-space.png');bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'activity-space.blend'));bpy.ops.render.render(write_still=True);print('CP08_ACTIVITY_SPACE_READY',flush=True)
