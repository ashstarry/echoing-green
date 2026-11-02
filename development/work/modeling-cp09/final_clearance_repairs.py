exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
def move(o,d):
 f=o.parent.matrix_world@o.matrix_parent_inverse if o.parent else Matrix.Identity(4);o.location+=f.to_3x3().inverted()@Vector(d)
st=bpy.data.objects['station_main'];move(bpy.data.objects['station_entry_door'],st.matrix_world.to_3x3()@Vector((0,-.03,.014)))
wind=bpy.data.objects['hill_windwheel'];move(bpy.data.objects['hill_windwheel__rotor'],wind.matrix_world.to_3x3()@Vector((0,-.008,0)))
for name in ['CP09 rear pink blossom.047','CP09 rear pink blossom.049','CP09 rear pink blossom.063']:erase(bpy.data.objects[name])
COL=cols['04_Station_Tram'];bike=bpy.data.objects['street_bicycle']
for name in [o.name for o in bike.children if o.name.startswith('CP09 cycle main tube')]:erase(bpy.data.objects[name])
with under(bike):
 for a,b in [((-.1,0,.70),(.04,0,.30)),((-.1,0,.70),(.27,0,.70)),((.27,0,.70),(.04,0,.30)),((.27,0,.70),(.30,0,.91))]:beam('CP09 cycle main tube',a,b,.018,navy)
rec=json.loads((OUT/'revision-record.json').read_text());rec['last_clearance_repairs']={'door':'Bottom .004 above platform, panel moved .03 forward to clear window moulding during slide','wind_rotor':'Moved .008 forward to avoid nominal tangent contact with mast','bicycle':'Front down tube rerouted outside tyre envelope','low_blossoms_pruned':3};(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'final-repaired.blend'))
