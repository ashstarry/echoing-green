import json,struct,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/modeling-checkpoint-07';p=OUT/'borrowed-wind-town-cp07-web.glb';d=p.read_bytes();magic,version,total=struct.unpack_from('<4sII',d);assert magic==b'glTF' and version==2 and total==len(d)
chunks=[];off=12
while off<len(d):
 n,t=struct.unpack_from('<II',d,off);chunks.append((t,d[off+8:off+8+n]));off+=8+n
g=json.loads(chunks[0][1]);bin_data=next(v for t,v in chunks if t==0x004e4942);assert len(bin_data)>=g['buffers'][0]['byteLength']
prims=[p for m in g['meshes'] for p in m['primitives']];accessors=g['accessors'];used=set();tris=0;verts=0;issues=[]
for prim in prims:
 assert all(k in prim['attributes'] for k in ['POSITION','NORMAL','TEXCOORD_0','COLOR_0']);assert 'KHR_draco_mesh_compression' in prim['extensions'];assert prim.get('mode',4)==4
 tris+=accessors[prim['indices']]['count']//3;verts+=accessors[prim['attributes']['POSITION']]['count'];used.add(prim['indices']);used.update(prim['attributes'].values());assert prim['material']<len(g['materials'])
 for bound in ['min','max']:assert all(math.isfinite(v) for v in accessors[prim['attributes']['POSITION']][bound])
for v in g['bufferViews']:assert v.get('byteOffset',0)+v['byteLength']<=len(bin_data)
images=[]
for im in g['images']:
 b=g['bufferViews'][im['bufferView']];png=bin_data[b.get('byteOffset',0):b.get('byteOffset',0)+b['byteLength']];assert png[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack_from('>II',png,16);images.append({'name':im['name'],'width':w,'height':h,'encoded_bytes':len(png)});assert w==h==1024
sizes={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4};components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
decoded=sum(accessors[i]['count']*sizes[accessors[i]['componentType']]*components[accessors[i]['type']] for i in used)
entity_nodes=[n for n in g['nodes'] if n.get('extras',{}).get('entity_id')];entity_names=[n['extras']['entity_id'] for n in entity_nodes]
expected=['postman','elder','porch_resident','vendor_bread','vendor_lamp','customer_one','customer_two','courier','musician','listener','child_listener','kite_child','child_parent','gardener','water_visitor','station_attendant','station_traveler','waiting_passenger','quiet_reader','returning_resident','tram_car_front','tram_car_rear','pond_boat','lantern_tree','hill_windwheel'];assert all(n in entity_names for n in expected)
baseline=json.loads((ROOT/'work/modeling-cp07/baseline-audit.json').read_text());audit=json.loads((OUT/'resource-audit.json').read_text())
record={'passed':True,'file_bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'mesh_batches':len(g['meshes']),'material_primitives':len(prims),'materials':len(g['materials']),'images':images,'triangles':tris,'summed_primitive_vertices':verts,'decoded_accessor_storage_bytes':decoded,'texture_rgba8_bytes_without_mips':sum(x['width']*x['height']*4 for x in images),'texture_rgba8_bytes_with_full_mips_estimate':round(sum(x['width']*x['height']*4 for x in images)*4/3),'entity_nodes':len(entity_nodes),'entity_ids':entity_names,'source_master_triangles':audit['render_triangles'],'cp06_triangles':baseline['render_triangles'],'triangle_reduction_fraction':1-audit['render_triangles']/baseline['render_triangles'],'embedded_images':True,'required_extensions':g.get('extensionsRequired',[]),'external_uris':[b.get('uri') for b in g.get('buffers',[]) if 'uri' in b],'browser_fps_measured':False,'actual_draw_calls_measured':False,'gpu_memory_measured':False,'limits':'Counts and storage calculation only; primitives are not measured draw calls. Shadows, post effects, canvas resolution, runtime overhead and device behavior are unmeasured. No runtime lighting is included.'}
(OUT/'web-asset-validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
