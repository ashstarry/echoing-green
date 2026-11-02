exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
src=ast.parse((WORK/'enrich_paper_town.py').read_text());allow={'slug','tag','foliage_node','leaf_card'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in allow],type_ignores=[]),'<landscape helpers>','exec'))
import re
broad=bpy.data.meshes['CP09 shared broad folded leaf'];blue=bpy.data.materials['CP09 broad foliage | deep teal'];sage2=bpy.data.materials['CP09 broad foliage | sage'];ivleaf=bpy.data.materials['CP09 broad foliage | pale sage'];rec=json.loads((OUT/'revision-record.json').read_text())
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
COL=cols['07_Paper_Foliage']
def sprigs(root,count=3):
 fol=foliage_node(root)
 with under(fol):
  for k in range(count):
   x=-.40+k*.35+R.uniform(-.06,.06);y=.10+R.uniform(0,.06);h=R.uniform(.50,.78);beam('CP09 upright border stem',(x,y,.03),(x+.06,y,h),.010,sage2)
   for j in range(5):
    z=.16+j*h/6;sign=(-1)**j;leaf_card('CP09 upright border leaflet',(x+sign*.10,y,z),(.34,.46,.5),R.choice([blue,blueleaf,sage2,ivleaf]),(.72,sign*.25,PI/2+sign*.40))
for name in rec['art_revision']['outer_groups_rebuilt']:sprigs(bpy.data.objects[name])
# Additional foliage-only clumps fill the largest foreground gaps without another flower garland.
angles=[]
for name in rec['art_revision']['outer_groups_rebuilt']:
 p=bpy.data.objects[name].matrix_world.translation;a=math.atan2((p.dot(BACK)+1.15)/7.35,p.dot(RIGHT)/12.98)%(2*PI)
 if PI<a<2*PI:angles.append(a)
angles=sorted(angles);gaps=sorted([(b-a,(a+b)/2) for a,b in zip(angles,angles[1:])],reverse=True)[:6];added=[]
land=bpy.data.objects['Island paper layer 4'];inv=land.matrix_world.inverted()
for i,(_,a) in enumerate(gaps):
 p=rb(12.98*math.cos(a),-1.15+7.35*math.sin(a));hit,lo,n,fi=land.ray_cast(inv@Vector((p.x,p.y,3)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
 if not hit:continue
 p.z=(land.matrix_world@lo).z+.003;root=asset('outer_foliage_patch_'+str(i),p,a-PI/2);tag(root,'plant',['sway','settle','bloom_state']);fol=foliage_node(root)
 with under(fol):
  for j in range(8):leaf_card('CP09 low border infill',(R.uniform(-.42,.42),R.uniform(-.01,.13),R.uniform(.13,.25)),(.62,.75,.8),R.choice([blue,blueleaf,sage2]),(.70,.1,PI/2+R.uniform(-.2,.2)))
 sprigs(root,2);added.append(root.name)
# Keep blossoms on the left of the windwheel, with a lower shrub behind its base.
for name in ['terrace_sakura_0','terrace_sakura_1']:
 o=bpy.data.objects[name];o.scale=(.90,.90,.85)
bpy.data.objects['terrace_sakura_2'].scale=(.68,.68,.48)
for o in s.objects:
 if o.name.startswith('terrace_garden_lantern_') and o.type=='EMPTY':move(o,(0,0,-.028))
# Keep the merchants outside the menu boards and visible at their true working positions.
tea=bpy.data.objects['tea_house']
for name in ['vendor_bread','vendor_lamp','vendor_flower']:move(bpy.data.objects[name],tea.matrix_world.to_3x3()@Vector((0,-.19,0)))
rec['art_revision']['foliage_only_infill']=added;rec['art_revision']['pink_canopy_rebalanced']=True
bpy.context.view_layer.update();(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'final-art-base.blend'));print('CP09_ART_BALANCED',added,flush=True)
