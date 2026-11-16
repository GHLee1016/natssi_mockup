import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "natssi_mockup.py")
src = open(SCRIPT).read().replace("RENDER = bool(bpy.app.background)", "RENDER = False")
g = {"__file__": SCRIPT, "__name__": "__main__"}
exec(compile(src, "natssi_mockup.py", "exec"), g)
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
DEV = g["DEV"]; sc = bpy.context.scene; bpy.context.view_layer.update()
pts = {"머리뒤":(0.04,0.036,0.012),"머리앞":(0.04,-0.036,0.012),"손잡이끝":(-0.105,0,0.012),"LED바": (-0.0145, -0.052, 0.0055), "머리중심": (0.04, 0, 0.0104), "손잡이중심": (-0.045, 0, 0.0104),
       "거치대앞좌": (-0.125, -0.052, 0.012), "거치대앞우": (0.096, -0.052, 0.012), "거치대뒤우": (0.096, 0.052, 0.012)}
for name, cam in g["cams"].items():
    if name not in ("dock", "dock_empty"): continue
    sc.camera = cam
    print(name, {k: tuple(round(c, 2) for c in world_to_camera_view(sc, cam, DEV.matrix_world @ Vector(v))[:2]) for k, v in pts.items()})
