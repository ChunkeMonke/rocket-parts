"""ParaView script: opens the rocket CFD case and builds ready-made views + screenshots.

Windows ParaView GUI:  View -> Python Shell -> Run Script -> pick this file
  (browse to \\\\wsl.localhost\\Ubuntu\\home\\<you>\\rocket-parts\\tools\\paraview_views.py)
Command line (Linux/WSL with ParaView installed):  pvbatch tools/paraview_views.py [case_name]

Finds out/cfd/of_<case>/ next to this script (default a4), creates case.foam if missing, and builds:
  1. rocket surface coloured by pressure (full rocket: half model reflected)
  2. side slice (y = 0) coloured by speed
  3. cross-section 10 mm behind the base coloured by axial speed
  4. streamlines around the fin can
Screenshots -> out/cfd/of_<case>/figures/paraview_*.png. In the GUI the pipeline stays open to explore
(eye icons in the Pipeline Browser show/hide each item).
"""
import json
import os
import sys

from paraview.simple import (Calculator, ColorBy, CreateView, Delete, ExtractBlock, GetActiveViewOrCreate,  # noqa: F401
                             GetColorTransferFunction, GetDisplayProperties, Hide, OpenFOAMReader, Reflect,
                             Render, SaveScreenshot, SetActiveView, Show, Slice, StreamTracer, Tube,
                             UpdatePipeline)

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
NAME = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "a4"
CASE = os.path.normpath(os.path.join(HERE, "..", "out", "cfd", "of_" + NAME))
FOAM = os.path.join(CASE, "case.foam")
FIGS = os.path.join(CASE, "figures")
if not os.path.exists(FOAM):
    open(FOAM, "w").close()
os.makedirs(FIGS, exist_ok=True)
info = json.load(open(os.path.join(CASE, "case.json")))
L, V = info["L"], info["speed"]

src = OpenFOAMReader(registrationName="rocket CFD", FileName=FOAM)
src.CaseType = "Decomposed Case"
src.MeshRegions = ["internalMesh", "patch/rocket"]
src.CellArrays = ["p", "U"]
src.UpdatePipelineInformation()
t_last = max(src.TimestepValues) if src.TimestepValues else 0
UpdatePipeline(time=t_last, proxy=src)

view = GetActiveViewOrCreate("RenderView")
view.ViewTime = t_last
view.ViewSize = [1600, 800]
view.Background = [1, 1, 1]
try:
    view.UseColorPaletteForBackground = 0
except AttributeError:
    pass
view.OrientationAxesVisibility = 1


def full(proxy, label):
    """Mirror the half model about y = 0."""
    r = Reflect(registrationName=label, Input=proxy)
    r.Plane = "Y Min"
    r.CopyInput = 1
    return r


def shoot(name, cam_pos, focal, up, scale=None):
    view.CameraPosition, view.CameraFocalPoint, view.CameraViewUp = cam_pos, focal, up
    if scale:
        view.CameraParallelProjection = 1
        view.CameraParallelScale = scale
    Render(view)
    SaveScreenshot(os.path.join(FIGS, name), view, ImageResolution=[1600, 800])
    print("saved", name)


# 1. rocket surface pressure
body = ExtractBlock(registrationName="rocket surface", Input=src)
try:
    body.Selectors = ["/Root/boundary/rocket"]
except AttributeError:
    body.BlockIndices = [2]
bodyF = full(body, "rocket surface (full)")
d = Show(bodyF, view)
ColorBy(d, ("POINTS", "p"))
lut = GetColorTransferFunction("p")
lut.ApplyPreset("Cool to Warm", True)
q = 0.5 * V * V
lut.RescaleTransferFunction(-0.5 * q, 0.5 * q)
d.SetScalarBarVisibility(view, True)
shoot("paraview_surface_pressure_below.png", [0.6, -0.9, -1.4], [0.75, 0, 0], [0, 0, 1])
shoot("paraview_fins_pressure.png", [1.25, -0.25, -0.2], [1.0, 0, 0], [0, 0, 1])

# 2. side slice coloured by speed
sl = Slice(registrationName="side slice y=0", Input=src)
sl.SliceType = "Plane"
sl.SliceType.Origin = [L / 2, 0.0005, 0]
sl.SliceType.Normal = [0, 1, 0]
sd = Show(sl, view)
ColorBy(sd, ("POINTS", "U", "Magnitude"))
lu = GetColorTransferFunction("U")
lu.ApplyPreset("Viridis (matplotlib)", True)
lu.RescaleTransferFunction(0, 1.15 * V)
sd.SetScalarBarVisibility(view, True)
Hide(bodyF, view)
shoot("paraview_side_speed.png", [L * 0.9, -2.0, 0], [L * 0.9, 0, 0], [0, 0, 1], scale=0.12)
shoot("paraview_side_speed_fins.png", [1.03, -2.0, 0], [1.03, 0, 0], [0, 0, 1], scale=0.07)

# 3. cross-section behind the base
xs = Slice(registrationName="cross-section 10 mm behind base", Input=src)
xs.SliceType = "Plane"
xs.SliceType.Origin = [L + 0.01, 0, 0]
xs.SliceType.Normal = [1, 0, 0]
xsF = full(xs, "cross-section (full)")
xd = Show(xsF, view)
ColorBy(xd, ("POINTS", "U", "X"))
Hide(sl, view)
shoot("paraview_cross_section_wake.png", [L - 1.0, 0, 0], [L + 0.01, 0, 0], [0, 0, 1], scale=0.09)

# 4. streamlines around the fin can (seed line upstream, in the pitch plane and off it)
st = StreamTracer(registrationName="streamlines", Input=src, SeedType="Line")
st.Vectors = ["POINTS", "U"]
st.SeedType.Point1 = [L - 0.12, 0.03, -0.08]
st.SeedType.Point2 = [L - 0.12, 0.03, 0.08]
st.SeedType.Resolution = 60
st.MaximumStreamlineLength = 1.2
stF = full(st, "streamlines (full)")
td = Show(stF, view)
ColorBy(td, ("POINTS", "U", "Magnitude"))
Hide(xsF, view)
Show(bodyF, view)
ColorBy(GetDisplayProperties(bodyF, view), None)
view.CameraParallelProjection = 0
shoot("paraview_streamlines.png", [1.0, -0.55, 0.25], [1.08, 0, 0], [0, 0, 1])

# leave a sensible view in the GUI: rocket by pressure + streamlines
ColorBy(GetDisplayProperties(bodyF, view), ("POINTS", "p"))
Render(view)
print("ParaView views done; screenshots in", FIGS)
