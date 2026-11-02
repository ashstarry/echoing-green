import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
A=Path('app/runtime-cp20/public/assets');root=bpy.data.objects['cyclist'];inv=root.matrix_world.inverted();C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)));CI=C.inverted();out={}
def limb(a,b,w):
 a,b=Vector(a),Vector(b);return Matrix.Translation((a+b)*.5)@(b-a).to_track_quat('Z','Y').to_matrix().to_4x4()@Matrix.Diagonal((w,w,(b-a).length,1))
for name,key in [('CP09 cyclist thigh.001','stop_thigh'),('CP09 cyclist shin.001','stop_shin'),('CP09 cyclist shoe.001','stop_shoe')]:
 o=bpy.data.objects[name];old=inv@o.matrix_world;poses=[]
 for knee,ankle in [((.30,-.24,.20),(.29,-.05,.03)),((.42,-.24,.20),(.50,-.10,.03)),((.42,-.24,.08),(.50,-.10,-.355))]:
  target=old.copy()
  if key=='stop_thigh':target=limb((.11,.02,.46),knee,.062)
  elif key=='stop_shin':target=limb(knee,ankle,.049)
  else:target.translation=Vector(ankle)
  dm=C@(target@old.inverted())@CI;poses.append([dm[r][col]for col in range(4)for r in range(4)])
 out[key]=poses
(A/'cycle-stop-pose.json').write_text(json.dumps(out));print('STAGED_FOOT_LIFT_OUT_LOWER')
