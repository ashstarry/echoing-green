exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
dg=bpy.context.evaluated_depsgraph_get()
for name,focus,scale,w,h,pts in [('balcony',bpy.data.objects['west_home'].matrix_world@Vector((0,-1.4,1.7)),5.8,1400,1100,[(452,792),(600,740),(500,700)]),('boat',bpy.data.objects['pond_boat'].matrix_world.translation+Vector((0,0,.10)),4.2,1400,1000,[(934,688),(742,750),(975,730)])]:
 for x,y in pts:
  p=focus-FWD*30+RIGHT*((x/w-.5)*scale)+UP*((.5-y/h)*scale/(w/h));hit,loc,no,fi,o,ma=s.ray_cast(dg,p,FWD,distance=60)
  print('PIXEL',name,x,y,'OBJECT',o.name if o else None,'FACE',fi,'NORMAL',list(no),'POS',list(loc),flush=True)
  if o:
   print('MATERIALS',[(m.name,tuple(m.diffuse_color)) for m in o.data.materials if m],'MODIFIERS',[(m.name,m.type) for m in o.modifiers],flush=True)
# CPU reference closeup, same exact balcony camera.
d=bpy.data.cameras.new('CPU surface check');d.type='ORTHO';d.ortho_scale=5.8;c=bpy.data.objects.new('CPU surface check',d);s.collection.objects.link(c);c.rotation_euler=cam.rotation_euler;c.location=bpy.data.objects['west_home'].matrix_world@Vector((0,-1.4,1.7))-FWD*30;s.camera=c;s.render.resolution_x=700;s.render.resolution_y=550;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6;s.render.filepath=str(WORK/'cpu-balcony.png');bpy.ops.render.render(write_still=True)
