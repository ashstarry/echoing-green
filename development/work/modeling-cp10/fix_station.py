exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
exec(compile((WORK/'rail_helpers.py').read_text(),'<rail helpers>','exec'))
rec=json.loads((ROOT/'outputs/modeling-checkpoint-09/revision-record.json').read_text());rec['checkpoint']='CP10';rec['source_checkpoint']='CP09';rec['requested_focus']='Station left corner overlaps rail: reshape platform to stay inside a conservative moving-car envelope; preserve central station, main camera and town art.'
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
station=bpy.data.objects['station_main'];frame=station.matrix_world.copy();moved=[];shift=.90
for o in list(station.children):
 if o.name=='CP08 station platform':continue
 p=frame.inverted()@o.matrix_world.translation
 if p.x<-1.55:move(o,BACK*shift);moved.append(o.name)
for name in ['station_attendant','waiting_passenger','station_seat_A']:move(bpy.data.objects[name],BACK*shift);moved.append(name)
# The platform front follows the inward envelope of complete car boxes, with a visible margin.
old=bpy.data.objects['CP08 station platform'];erase(old);COL=cols['04_Station_Tram'];margin=.25;xs=[-3.9+i*7.8/78 for i in range(79)];front_edge=[]
for x in xs:
 p=frame@Vector((x,0,0));y=max(-1.10,envelope_back_at(p.dot(RIGHT))+margin-frame.translation.dot(BACK));front_edge.append((x,y))
outline=front_edge+[(3.9,.86),(-1.50,.86),(-1.50,.86+shift),(-3.9,.86+shift)];n=len(outline);verts=[(x,y,z)for z in [0,.18]for x,y in outline];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
with under(station):platform=mesh('CP10 curved station platform',verts,faces,ivory)
import bmesh
bm=bmesh.new();bm.from_mesh(platform.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(platform.data);bm.free()
station['footprint_design']='Curved rail-facing edge and inset western waiting wing; no platform geometry in the reserved car passage';station['left_wing_inset']=shift
bpy.context.view_layer.update();rec['station_rail_repair']={'left_wing_shift':shift,'moved_objects':moved,'margin_back_axis':margin,'front_edge_local':front_edge,'complete_car_bounds_samples':COUNT*2,'sampled_parameter_interval':[T0,T1],'camera_unchanged':True,'central_ticket_house_unchanged':True,'guitarist_unchanged':True};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'station-repaired.blend'));print('CP10_STATION_REPAIRED',flush=True)
