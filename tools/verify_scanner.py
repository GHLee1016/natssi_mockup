"""머리 윗면 스캐너 치수 확인: 렌즈 지름 12mm, 커버 두께 1.2mm, LED·렌즈가 커버 밑면보다 낮은지."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "natssi_mockup.py")
src = open(SCRIPT).read().replace("RENDER = bool(bpy.app.background)", "RENDER = False")
g = {"__file__": SCRIPT, "__name__": "__main__"}
exec(compile(src, "natssi_mockup.py", "exec"), g)
import bpy

dg = bpy.context.evaluated_depsgraph_get()
root = bpy.data.objects["Device"]
inv = root.matrix_world.inverted()


def zrange(name):
    """디바이스 로컬 좌표에서 (모디파이어 적용 후) 최저·최고 z(mm)."""
    o = bpy.data.objects[name].evaluated_get(dg)
    m = inv @ o.matrix_world
    zs = [(m @ v.co).z for v in o.to_mesh().vertices]
    o.to_mesh_clear()
    return min(zs) * 1000, max(zs) * 1000


def dims(name):
    return [round(v * 1000, 2) for v in bpy.data.objects[name].dimensions]


ok = True
def check(label, cond):
    global ok
    ok &= cond
    print(("  OK  " if cond else "  FAIL") + " " + label)


lens = dims("Device_scan_lens"); cover = dims("Device_cover_glass")
print("스캔 렌즈 크기(mm):", lens)
print("커버 유리 크기(mm):", cover)
print("센서 베이스 크기(mm):", dims("Device_sensor_base"))
cz = zrange("Device_cover_glass"); lz = zrange("Device_scan_lens"); rz = zrange("Device_LED")
dz = max(zrange(f"Device_LEDdot{i}")[1] for i in range(12)); bz = zrange("Device_sensor_base")
print("커버 z: %.2f ~ %.2f mm" % cz)
print("렌즈 z: %.2f ~ %.2f / LED 링 윗면 %.2f / 도트 윗면 %.2f / 베이스 윗면 %.2f mm" % (*lz, rz[1], dz, bz[1]))
check("렌즈 지름 12.0mm", abs(lens[0] - 12) < 0.05 and abs(lens[1] - 12) < 0.05)
check("커버 두께 1.2mm", abs(cover[2] - 1.2) < 0.02)
check("렌즈가 커버 밑면보다 낮음", lz[1] < cz[0])
check("LED 링·도트가 커버 밑면보다 낮음", rz[1] < cz[0] and dz < cz[0])
check("렌즈·LED가 베이스 위에 놓임", abs(lz[0] - bz[1]) < 0.05 and abs(rz[0] - bz[1]) < 0.05)
mat = bpy.data.objects["Device_cover_glass"].active_material.node_tree.nodes["Glass BSDF"]
check("커버 IOR 1.5 / Roughness 0.01", abs(mat.inputs["IOR"].default_value - 1.5) < 1e-6
      and abs(mat.inputs["Roughness"].default_value - 0.01) < 1e-6)
print("결과:", "통과" if ok else "실패")
