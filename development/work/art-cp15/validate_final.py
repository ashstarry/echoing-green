import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/art-checkpoint-15';s=bpy.context.scene;exec(compile((ROOT/'work/art-cp14/scene_signature.py').read_text(),'<signature>','exec'));current=json.loads(json.dumps(scene_signature(s)));old=json.loads((ROOT/'outputs/art-checkpoint-14/scene-signature.json').read_text());rec=json.loads((OUT/'revision-record.json').read_text());reg=json.loads((OUT/'decision-entities.json').read_text());oldreg=json.loads((ROOT/'outputs/art-checkpoint-14/decision-entities.json').read_text());modified=set(rec['modified']);unexpected=[n for n in old['objects']if n not in modified and old['objects'][n]!=current['objects'].get(n)];assert all(n.startswith('Awning')for n in modified),modified;assert set(old['objects'])<=set(current['objects'])
ids={o['decision_entity_id']for o in s.objects if o.get('decision_entity_id')};parts={(o['decision_owner'],o['decision_part_id'])for o in s.objects if o.get('decision_part_id')};assert ids=={e['id']for e in reg['entities']}and len(ids)==199;assert len(parts)==91;assert {e['id']for e in oldreg['entities']}<=ids
for i in range(2):
 e=next(e for e in reg['entities']if e['id']=='resident.upper_diner_'+str(i));assert [a['id']for a in e['actions']]==['retreat_behind_curtain','come_out_to_dine'];assert [a['id']for a in e['anchors']]==['dining_seat','behind_noren']
# Old lights and global lighting/color/post settings must remain unchanged.
oldrig=json.loads((ROOT/'outputs/art-checkpoint-14/lighting-rig.json').read_text());lights=[]
for o in s.objects:
 if o.type=='LIGHT':lights.append({'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'matrix_world':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'decision_owner':o.get('decision_owner'),'role':o.get('lighting_role','inherited art lighting'),'active':o.data.energy>0,'size':o.data.size if o.data.type=='AREA'else o.data.shadow_soft_size})
oldlights={x['name']:x for x in oldrig['lights']};newlights={x['name']:x for x in lights};assert oldlights==newlights
proof=[]
for e in reg['entities']:
 if e['id']not in rec['new_entities']:continue
 for pr in e['parts']:
  p=bpy.data.objects[pr['blender_object']];objs=[o for o in p.children_recursive if o.type=='MESH'];points=[(o,v.index,o.matrix_world@v.co)for o in objs for v in o.data.vertices];obj,idx,point=max(points,key=lambda x:(x[2]-p.matrix_world.translation).length);saved=p.matrix_basis.copy();p.matrix_basis=saved@Matrix.Rotation(math.radians(3),4,'X');bpy.context.view_layer.update();moved=obj.matrix_world@obj.data.vertices[idx].co;p.matrix_basis=saved;bpy.context.view_layer.update();restored=obj.matrix_world@obj.data.vertices[idx].co;proof.append({'entity':e['id'],'part':pr['id'],'movement':(moved-point).length,'restore_error':(restored-point).length,'passed':(moved-point).length>.005 and(restored-point).length<1e-5})
assert all(p['passed']for p in proof);(OUT/'decoration-control-check.json').write_text(json.dumps({'passed':True,'parts_checked':len(proof),'checks':proof,'scope':'Actual 3-degree pivot transform and restore; not a sway animation, cloth opening or swept-collision guarantee.'},indent=2))
# Check that the two hidden endpoint volumes lie in real static occlusion, without duplicating actors.
dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];names=[]
def resident(o):
 while o:
  if o.get('decision_kind')=='resident':return True
  o=o.parent
 return False
for o in s.objects:
 if o.type not in ['MESH','CURVE']or o.hide_render or resident(o)or any(c.hide_render or c.name.startswith('12_')for c in o.users_collection):continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);names.extend([o.name]*len(me.loop_triangles));ev.to_mesh_clear()
world=BVHTree.FromPolygons(vs,fs,all_triangles=True);FWD=s.camera.rotation_euler.to_quaternion()@Vector((0,0,-1));RIGHT=s.camera.rotation_euler.to_quaternion()@Vector((1,0,0));endpoint=[]
for e in reg['entities']:
 if not e['id'].startswith('resident.upper_diner_'):continue
 p=Vector(next(a['position']for a in e['anchors']if a['id']=='behind_noren'));rows=[]
 for dx in [-.12,.12]:
  for z in [.3,.75,1.15]:
   target=p+RIGHT*dx+Vector((0,0,z));hit,no,idx,d=world.ray_cast(target-FWD*40,FWD,39.97);rows.append({'height':z,'lateral':dx,'occluded':hit is not None,'blocker':names[idx]if hit is not None else None})
 endpoint.append({'entity':e['id'],'samples':rows,'all_samples_occluded':all(r['occluded']for r in rows)})
(OUT/'diner-endpoint-check.json').write_text(json.dumps({'passed':all(e['all_samples_occluded']for e in endpoint),'endpoints':endpoint,'scope':'Six static view probes per hidden endpoint, excluding resident geometry. Not complete body/transition verification and no rendered actor visibility switching implemented.'},indent=2));assert all(e['all_samples_occluded']for e in endpoint)
prior={}
for i in range(1,15):
 folder=('modeling-checkpoint-'if i<=10 else'lighting-checkpoint-'if i<=12 else'art-checkpoint-')+('%02d'%i);p=ROOT/'outputs'/folder;name='borrowed-wind-town-cp%02d.blend'%i;m=json.loads((p/'file-manifest.json').read_text());prior['CP%02d'%i]=hashlib.sha256((p/name).read_bytes()).hexdigest()==m[name]['sha256']
record={'passed':not unexpected and current['camera']==old['camera']and current['collections']==old['collections']and all(prior.values()),'unexpected_old_changes':unexpected,'old_geometry_changes_only_awning_translations':sorted(modified),'camera_and_collection_states_unchanged':current['camera']==old['camera']and current['collections']==old['collections'],'existing_lights_unchanged':True,'active_light_count':sum(l['active']for l in lights),'entities':len(ids),'parts':len(parts),'previous_models_unchanged':prior,'source_model_sha256':hashlib.sha256((OUT/'borrowed-wind-town-cp15.blend').read_bytes()).hexdigest(),'diner_decision_contract':'Two semantic endpoints only for these two residents','runtime_implemented':False,'browser_fps_measured':False};(OUT/'validation.json').write_text(json.dumps(record,indent=2));(OUT/'scene-signature.json').write_text(json.dumps(current,sort_keys=True));print(json.dumps(record,indent=2));assert record['passed']
rig=dict(oldrig);rig['checkpoint']='CP15';rig['lights']=lights;rig['note']='CP14 light configuration retained exactly; added noren and two non-luminous ornaments. No browser lighting implementation.';(OUT/'lighting-rig.json').write_text(json.dumps(rig,indent=2))
