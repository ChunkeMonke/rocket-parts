import sys, json
from paraview.simple import STLReader, Show, Hide, GetActiveViewOrCreate, Render, SaveScreenshot, PolyLineSource, Tube
d = sys.argv[1]
meta = json.load(open(d + "meta.json"))
v = GetActiveViewOrCreate("RenderView"); v.ViewSize = [1300, 1000]; v.Background = [1, 1, 1]
try: v.UseColorPaletteForBackground = 0
except AttributeError: pass
v.OrientationAxesVisibility = 0
ORANGE, BLUE = [0.93, 0.6, 0.27], [0.45, 0.62, 0.92]
def shot(items, out, pos, foc, up=(0, 0, 1)):
    shown = []
    for kind, arg, col, op in items:
        if kind == "stl":
            r = STLReader(FileNames=[d + arg])
        else:
            pl = PolyLineSource(Points=[c for pt in meta[arg] for c in pt]); r = Tube(Input=pl, Radius=0.25)
        s = Show(r, v); s.DiffuseColor = col; s.Opacity = op; s.Specular = 0.25; shown.append(r)
    v.CameraPosition, v.CameraFocalPoint, v.CameraViewUp = list(pos), list(foc), list(up)
    Render(v); SaveScreenshot(d + out, v, ImageResolution=[1300, 1000])
    for r in shown: Hide(r, v)
cone_iso = ((95, -110, 85), (0, 0, 22))
shot([("stl", "cone_blank.stl", BLUE, 1)], "t01_blank.png", *cone_iso)
shot([("stl", "cone_blank.stl", BLUE, 0.35), ("line", "cone_helix", [0.85, 0.1, 0.1], 1)], "t03_helix.png", (70, -80, 55), (0, 0, 33))
shot([("stl", "cone_thread.stl", BLUE, 1)], "t05_thread.png", (70, -80, 55), (0, 0, 33))
shot([("stl", "cone_half.stl", BLUE, 1)], "t05b_half.png", (24, -42, 36), (21.5, 0, 34))
col_iso = ((80, -95, 45), (0, 0, -9))
shot([("stl", "collar_blank.stl", ORANGE, 0.35), ("line", "collar_helix", [0.85, 0.1, 0.1], 1)], "t07_collar_helix.png", *col_iso)
shot([("stl", "collar_half.stl", ORANGE, 1)], "t09_groove_half.png", (10, -80, -5), (0, 0, -9))
shot([("stl", "collar_half.stl", ORANGE, 1), ("stl", "cone_inst_half.stl", BLUE, 1)], "t10_assembly_half.png", (24, -40, -13), (21.3, 0, -13.5))
shot([("stl", "collar_groove.stl", ORANGE, 1)], "t11_test_ring.png", (70, -80, 35), (0, 0, -9))
