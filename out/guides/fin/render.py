import sys
from paraview.simple import STLReader, Show, Hide, GetActiveViewOrCreate, Render, SaveScreenshot, Plane, ColorBy
d = sys.argv[1]
v = GetActiveViewOrCreate("RenderView"); v.ViewSize = [1400, 1000]; v.Background = [1, 1, 1]
try: v.UseColorPaletteForBackground = 0
except AttributeError: pass
v.OrientationAxesVisibility = 0
ORANGE = [0.93, 0.6, 0.27]
def shot(stl, out, pos, foc, up=(0, 0, 1), planes=()):
    r = STLReader(FileNames=[d + stl]); s = Show(r, v); s.DiffuseColor = ORANGE; s.Specular = 0.25
    extra = []
    for (o, p1, p2, col) in planes:
        pl = Plane(Origin=o, Point1=p1, Point2=p2); ps = Show(pl, v); ps.DiffuseColor = col; ps.Opacity = 0.35
        extra.append(pl)
    v.CameraPosition, v.CameraFocalPoint, v.CameraViewUp = list(pos), list(foc), list(up)
    v.CameraParallelProjection = 0
    Render(v); SaveScreenshot(d + out, v, ImageResolution=[1400, 1000])
    Hide(r, v)
    for e in extra: Hide(e, v)
iso = ((120, -230, 90), (38, 0, 25))
shot("body.stl", "s01_body.png", *iso)
shot("body.stl", "s02_planes.png", (230, -120, 80), (40, 0, 25), planes=[((22.4, -14, -8), (22.4, 14, -8), (22.4, -14, 62), [0.2, 0.45, 0.9]),
                                                  ((66.6, -14, -8), (66.6, 14, -8), (66.6, -14, 62), [0.15, 0.7, 0.3])])
shot("body_one_fin_loft.stl", "s11_loft.png", *iso)
close = ((95, -75, 70), (30, 0, 22))
shot("body_one_fin_loft.stl", "s12a_noroot.png", *close)
shot("body_one_fin_fillet.stl", "s12b_rootfillet.png", *close)
under = ((60, -70, -55), (27, 0, -3))
shot("body_one_fin_fillet.stl", "s13a_noskirt.png", *under)
shot("body_one_fin_skirt.stl", "s13b_skirt.png", *under)
shot("full.stl", "s14_pattern.png", (170, -190, 140), (20, 0, 40))
shot("full.stl", "s14b_aft.png", (0, 0, -215), (0, 0, 40), up=(0, 1, 0))
