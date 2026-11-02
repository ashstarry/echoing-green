import bpy,json
from pathlib import Path
p=bpy.ops.export_scene.gltf.get_rna_type().properties
a={x.identifier:{"type":x.type,"default":str(getattr(x,"default",None)),"enums":[e.identifier for e in x.enum_items] if x.type=="ENUM" else []} for x in p}
Path("work/modeling-cp07/gltf-options.json").write_text(json.dumps(a,indent=2))
print(json.dumps({k:v for k,v in a.items() if any(x in k for x in ["color","draco","export_lights","export_materials","export_cameras"])}))
