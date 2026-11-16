import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "natssi_mockup.py")
src = open(SCRIPT).read().replace("RENDER = bool(bpy.app.background)", "RENDER = False")
g = {"__file__": SCRIPT, "__name__": "__main__"}
exec(compile(src, "natssi_mockup.py", "exec"), g)
import bpy
from mathutils import Vector
dg = bpy.context.evaluated_depsgraph_get()
root = bpy.data.objects["Device"]
rot = root.rotation_euler.to_matrix(); org = root.location
def loc2w(v): return org + rot @ Vector(v)
dock = bpy.data.objects["Device_dock"]
def dock_z(x, y):
    """거치대만 대상으로 위에서 레이를 쏜 높이(m)."""
    o = loc2w((x, y, 0.2)); d = rot @ Vector((0, 0, -1))
    inv = dock.matrix_world.inverted()
    hit, loc, n, idx = dock.ray_cast(inv @ o, inv.to_3x3() @ d)
    return (dock.matrix_world @ loc).z if hit else None
print("거치대 윗면(가장자리 근처):", round(dock_z(0.085, 0.045)*1000, 2), "mm")
print("머리 홈 바닥(중심):", round(dock_z(0.04, 0)*1000, 2), "mm")
print("손잡이 홈 바닥(중심선):", round(dock_z(-0.045, 0)*1000, 2), "mm")
print("손잡이 홈 옆 (y=+9mm):", round(dock_z(-0.045, 0.009)*1000, 2), "mm")
print("홈 깊이(머리):", round((dock_z(0.085,0.045)-dock_z(0.04,0))*1000,2), "mm / (손잡이):", round((dock_z(0.085,0.045)-dock_z(-0.045,0))*1000,2), "mm")
bar = bpy.data.objects["Device_dock_LED"]
print("LED 바 크기(mm):", [round(v*1000,2) for v in bar.dimensions])
print("거치대 크기(mm):", [round(v*1000,1) for v in dock.dimensions])
print("디바이스 바닥 z(mm):", round((0.012-0.002+0.0004)*1000,2))
print("홈 영역 정점수:", len(dock.data.vertices))
