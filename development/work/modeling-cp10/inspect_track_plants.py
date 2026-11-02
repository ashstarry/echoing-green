exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
r=json.loads((OUT/'station-bend-world-check.json').read_text());names=sorted({n for c in r['car_mesh_checks']for x in c['contacts']for n in x['objects']});rows=[]
for n in names:
 o=bpy.data.objects[n];p=o.matrix_world.translation;rows.append({'name':n,'rbz':[p.dot(RIGHT),p.dot(BACK),p.z],'scale':list(o.scale),'parent':o.parent.name if o.parent else None})
print(json.dumps(rows,indent=2));(WORK/'track-plant-positions.json').write_text(json.dumps(rows,indent=2))
