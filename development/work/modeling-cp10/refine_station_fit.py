exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
st=bpy.data.objects['station_main'];actor=bpy.data.objects['station_traveler'];p=st.matrix_world.inverted()@actor.matrix_world.translation;p.x=1.8;move(actor,st.matrix_world@p-actor.matrix_world.translation)
wing=bpy.data.objects['CP08 station wing -2.85'];frame=wing.matrix_world.copy();original={};all_y=[]
for o in wing.children_recursive:
 if o.type!='MESH':continue
 o.data=o.data.copy();coords=[frame.inverted()@o.matrix_world@v.co for v in o.data.vertices];original[o.name]=coords;all_y.extend(p.y for p in coords)
ymin,ymax=min(all_y),max(all_y);postman=bpy.data.objects['postman'];shoes=[o for o in postman.children_recursive if o.name.startswith('Shoe')];trials=[]
def visible(root,o):
 p=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices);hit,loc,n,i,obj,ma=s.ray_cast(bpy.context.evaluated_depsgraph_get(),p-FWD*30,FWD,distance=30.01)
 while obj:
  if obj==root:return True
  obj=obj.parent
 return False
for back_edge in [.8,.7,.6,.5,.4,.3,.2,.1,0]:
 for name,coords in original.items():
  o=bpy.data.objects[name];inv=o.matrix_world.inverted()@frame
  for v,p0 in zip(o.data.vertices,coords):
   p=p0.copy();p.y=ymin+(p.y-ymin)*(back_edge-ymin)/(ymax-ymin);v.co=inv@p
  o.data.update()
 bpy.context.view_layer.update();ok=all(visible(postman,o)for o in shoes);trials.append({'back_edge':back_edge,'postman_feet_visible':ok})
 if ok:break
assert ok,'Cannot retain postman foot visibility'
for o in st.children:
 if o.name.startswith('CP08 station open column'):
  p=st.matrix_world.inverted()@o.matrix_world.translation
  if p.x<-1.55 and p.y>1.0:move(o,BACK*((.90+back_edge-.10)-p.y))
bpy.context.view_layer.update();r=json.loads((OUT/'revision-record.json').read_text());r['station_rail_repair']['traveler_station_local_x']=1.8;r['station_rail_repair']['left_canopy_depth_fit']={'old_y_bounds':[ymin,ymax],'new_back_edge':back_edge,'trials':trials,'purpose':'Preserve postman feet visibility while keeping station headroom and train clearance'};(OUT/'revision-record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'station-final.blend'));print('STATION_FINAL_FIT',trials,flush=True)
