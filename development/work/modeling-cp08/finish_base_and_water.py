exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
rec=json.loads((OUT/'revision-record.json').read_text());pond=bpy.data.objects['CP02 pond'];pond.data=pond.data.copy();bpy.context.view_layer.update();inv=pond.matrix_world.inverted();center=pond.matrix_world.translation.copy()
# Clip the enlarged water footprint to a protected inner bank curve; rails remain dry.
def inside(p):return (p.dot(RIGHT)/11.30)**2+((p.dot(BACK)+.52)/5.70)**2<=1
clipped=0
for v in pond.data.vertices:
 p=pond.matrix_world@v.co
 if inside(p):continue
 z=p.z;a=Vector((center.x,center.y,z));b=p.copy()
 for _ in range(28):
  m=(a+b)/2
  if inside(m):a=m
  else:b=m
 v.co=inv@a;clipped+=1
# Flat layered stone caps articulate the broad bare paper rim without another flower ring.
COL=cols['00_Terrain'];new=[]
for i in range(25):
 a=PI+PI*(i+.18)/25;p=rb(12.55*math.cos(a),-.78+7.15*math.sin(a),Z-.01);w=R.uniform(.55,1.04);d=R.uniform(.28,.48);verts=[]
 for j in range(6):
  t=j*PI/3;v=p+RIGHT*(w*math.cos(t)*math.cos(a)-d*math.sin(t)*math.sin(a))+BACK*(w*math.cos(t)*math.sin(a)+d*math.sin(t)*math.cos(a));v.z+=R.uniform(-.055,.018);verts.append(tuple(v))
 verts.append(tuple(p+Vector((0,0,.025))));o=mesh('CP08 layered rim cap',verts,[(6,j,(j+1)%6) for j in range(6)],R.choice([terr[3],terr[4],bpy.data.materials['CP08 plaza | dusty rose']]));new.append(o.name)
rec['final_water_bank']={'clipped_boundary_vertices':clipped,'protected_inner_ellipse':[11.30,5.70],'water_kept_inside_track_bank':True,'scope':'Water polygon clipping to authored bank envelope; not hydrodynamics'};rec['rim_caps']=new
for me in bpy.data.meshes:
 if not me.users or not me.polygons or me.uv_layers:continue
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(poly.normal[i]))]
  for li in poly.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*2,p[axes[1]]*2)
bpy.context.view_layer.update();rec['baseline_asset_transforms']={n:[list(v) for v in bpy.data.objects[n].matrix_world] for n in rec['cp07_core_transforms']};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'borrowed-wind-town-cp08.blend'));print('FINAL_BANK_READY',clipped,flush=True)
