exec(compile((__import__('pathlib').Path(__file__).parent/'common.py').read_text(),__file__,'exec'))
erase(bpy.data.objects['CP09 sakura branch.009']);rec=json.loads((OUT/'revision-record.json').read_text());rec['last_clearance_repairs']['pruned_branch']='CP09 sakura branch.009';(OUT/'revision-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2))
