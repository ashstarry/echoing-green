import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07/textures'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_plane_add(size=2);plane=bpy.context.object
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16
s.render.bake.use_selected_to_active=False;s.render.bake.margin=8;s.render.bake.normal_space='TANGENT'
records=[]
for key,source,dist in [('washi','washi-height-imagegen.png',.003),('cedar','cedar-height-imagegen.png',.004)]:
 mat=bpy.data.materials.new(key+' normal bake source');mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links
 p=nodes.get('Principled BSDF');height=bpy.data.images.load(str(OUT/'source'/source));height.colorspace_settings.name='Non-Color'
 tex=nodes.new('ShaderNodeTexImage');tex.image=height;tex.extension='REPEAT'
 bump=nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=dist;bump.inputs['Strength'].default_value=1;links.new(tex.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
 target=bpy.data.images.new(key+' tangent normal',1024,1024,alpha=False);target.colorspace_settings.name='Non-Color'
 node=nodes.new('ShaderNodeTexImage');node.image=target;nodes.active=node
 plane.data.materials.clear();plane.data.materials.append(mat);bpy.context.view_layer.objects.active=plane;plane.select_set(True)
 bpy.ops.object.bake(type='NORMAL')
 target.filepath_raw=str(OUT/(key+'-normal.png'));target.file_format='PNG';target.save()
 vals=list(target.pixels);xs=vals[0::4];ys=vals[1::4]
 records.append({'source':'source/'+source,'normal':key+'-normal.png','size':[1024,1024],'method':'Cycles tangent-space NORMAL bake of ImageGen height source on UV plane','distance':dist,'normal_x_range':[min(xs),max(xs)],'normal_y_range':[min(ys),max(ys)],'normal_convention':'OpenGL tangent +Y','not_scene_lighting_bake':True})
 assert max(xs)-min(xs)>.001 or max(ys)-min(ys)>.001
(OUT/'bake-provenance.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
