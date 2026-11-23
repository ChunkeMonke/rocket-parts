"""Cover / overview renders of the owner OML (pvbatch). pvbatch tools/render_cover.py OUT_DIR"""
import sys
from paraview.simple import (STLReader, Show, GetActiveViewOrCreate, Render, SaveScreenshot, ResetCamera, Transform,
                             GenerateSurfaceNormals)
out = sys.argv[1]
r = STLReader(FileNames=["out/cfd/rocket_oml_owner.stl"])
n = GenerateSurfaceNormals(Input=r); n.FeatureAngle = 35
v = GetActiveViewOrCreate("RenderView")
v.ViewSize = [3200, 1100]; v.OrientationAxesVisibility = 0
v.Background = [1, 1, 1]
try:
    v.BackgroundColorMode = "Single Color"; v.UseColorPaletteForBackground = 0
except Exception:
    pass
d = Show(n, v); d.DiffuseColor = [0.80, 0.82, 0.86]; d.Specular = 0.55; d.SpecularPower = 40; d.Ambient = 0.12
d.Interpolation = "Gouraud"
try:
    v.EnableRenderOnInteraction = 0
except Exception:
    pass
# rocket axis = z (aft face at 0, tip at +z). Camera: 3/4 view from the side, slightly below, nose to the right
v.CameraFocalPoint = [0, 0, 520]; v.CameraPosition = [-1400, -900, 380]; v.CameraViewUp = [0, 0, 1]
Render(v)
v.CameraFocalPoint = [0, 0, 520]; v.CameraPosition = [-1150, -760, 430]; v.CameraViewUp = [1, -1.2, 0]
v.CameraViewAngle = 30
Render(v)
SaveScreenshot(out + "/cover_rocket.png", v, ImageResolution=[3200, 1100], TransparentBackground=1)
v.ViewSize = [1800, 1200]
v.CameraFocalPoint = [0, 0, 60]; v.CameraPosition = [-260, -230, 140]; v.CameraViewUp = [0, 0, 1]
Render(v)
SaveScreenshot(out + "/cover_fincan.png", v, ImageResolution=[1800, 1200], TransparentBackground=1)
