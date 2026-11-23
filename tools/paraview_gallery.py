"""ParaView gallery of the rocket CFD: many ready-made views + a state file to explore them in the GUI.

Windows ParaView GUI:  View -> Python Shell -> Run Script -> tools/paraview_gallery.py
  (\\\\wsl.localhost\\Ubuntu\\home\\<you>\\rocket-parts\\tools\\paraview_gallery.py)
Linux/WSL:  pvbatch tools/paraview_gallery.py [case_name]      (headless: xvfb-run -a pvbatch ...)

Reads out/cfd/of_<case>/ (default a4, decomposed). Writes out/cfd/of_<case>/figures/gallery/NN_<name>.png and
gallery.pvsm (File -> Load State in the GUI restores every filter; toggle the eye icons).
Each view is independent: if one fails it is reported and the rest continue.
Frame: x aft from the nose tip (m), z = pitch plane through fin 0 (up), half model y >= 0 (reflected for display).
"""
import json
import os
import sys
import traceback

from paraview.simple import (Calculator, Clip, ColorBy, Contour, ExtractBlock, GetActiveViewOrCreate,  # noqa: F401
                             GetColorTransferFunction, GetDisplayProperties, GetSources, Glyph, Hide,
                             OpenFOAMReader, Reflect, Render, SaveScreenshot, SaveState, Show, Slice,
                             StreamTracer, Text, Tube)
import paraview.simple as pvs

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
NAME = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "a4"
CASE = os.path.normpath(os.path.join(HERE, "..", "out", "cfd", "of_" + NAME))
FOAM = os.path.join(CASE, "case.foam")
OUT = os.path.join(CASE, "figures", "gallery")
os.makedirs(OUT, exist_ok=True)
if not os.path.exists(FOAM):
    open(FOAM, "w").close()
info = json.load(open(os.path.join(CASE, "case.json")))
L, V = info["L"], info["speed"]
COMP = bool(info.get("compressible"))
Q = 0.5 * V * V                      # kinematic dynamic pressure (p is p/rho) for incompressible runs
CP_EXPR = (f"(p-{info['p_inf']})/{0.5 * info['rho_inf'] * V * V}" if COMP else f"p/{Q}")
RES = [1600, 900]

src = OpenFOAMReader(registrationName="rocket CFD (case.foam)", FileName=FOAM)
src.CaseType = "Decomposed Case"
src.MeshRegions = ["internalMesh", "patch/rocket"]
src.CellArrays = ["p", "U", "k", "omega", "nut"] + (["T"] if COMP else [])
src.UpdatePipelineInformation()
T = max(src.TimestepValues) if src.TimestepValues else 0

view = GetActiveViewOrCreate("RenderView")
view.ViewTime = T
view.ViewSize = RES
view.Background = [1, 1, 1]
for attr, val in (("UseColorPaletteForBackground", 0), ("OrientationAxesVisibility", 1)):
    try:
        setattr(view, attr, val)
    except AttributeError:
        pass
shown = []
n = [0]


def reflect(proxy, label):
    r = Reflect(registrationName=label, Input=proxy)
    r.Plane = "Y Min"
    r.CopyInput = 1
    return r


def bars_off():
    for arr in ("p", "Cp", "U", "u_over_Uinf", "dUz", "k", "Mach"):
        try:
            pvs.GetScalarBar(GetColorTransferFunction(arr), view).Visibility = 0
        except Exception:
            pass


def color(disp, arr, comp=None, lo=None, hi=None, preset="Cool to Warm", bar=True):
    bars_off()
    ColorBy(disp, ("POINTS", arr, comp) if comp else ("POINTS", arr))
    lut = GetColorTransferFunction(arr)
    lut.ApplyPreset(preset, True)
    if comp:
        lut.VectorMode = "Component" if comp != "Magnitude" else "Magnitude"
        lut.VectorComponent = {"X": 0, "Y": 1, "Z": 2}.get(comp, 0)
    if lo is not None:
        lut.RescaleTransferFunction(lo, hi)
        try:
            lut.AutomaticRescaleRangeMode = "Never"
        except AttributeError:
            pass
    disp.SetScalarBarVisibility(view, bar)
    return lut


def only(*proxies):
    bars_off()
    for s in shown:
        Hide(s, view)
    shown.clear()
    out = []
    for p in proxies:
        out.append(Show(p, view))
        shown.append(p)
    return out


def cam(pos, focal, up=(0, 0, 1), parallel=None, fit=False):
    Render(view)                      # first render may auto-reset the camera; do it before placing ours
    view.CameraPosition, view.CameraFocalPoint, view.CameraViewUp = list(pos), list(focal), list(up)
    view.CameraParallelProjection = 1 if (parallel or fit) else 0
    if fit:
        view.ResetCamera(False)
        view.CameraParallelScale = view.CameraParallelScale * 0.55
    elif parallel:
        view.CameraParallelScale = parallel


caption = Text(registrationName="caption")
cap_disp = None


def shot(name, text=""):
    global cap_disp
    caption.Text = text or name.replace("_", " ")
    cap_disp = Show(caption, view)
    try:
        cap_disp.WindowLocation = "Upper Left Corner"
    except Exception:
        cap_disp.WindowLocation = "UpperLeftCorner"
    cap_disp.FontSize = 22
    cap_disp.Color = [0.1, 0.1, 0.1]
    n[0] += 1
    f = os.path.join(OUT, f"{n[0]:02d}_{name}.png")
    Render(view)
    SaveScreenshot(f, view, ImageResolution=RES)
    print("saved", os.path.basename(f))


def section(title, fn):
    try:
        fn()
    except Exception:  # keep going: one failed view must not stop the gallery
        print(f"FAILED {title}:\n{traceback.format_exc(limit=2)}")


# ---------------------------------------------------------------- building blocks
body = ExtractBlock(registrationName="rocket surface (half)", Input=src)
try:
    body.Selectors = ["/Root/boundary/rocket"]
except AttributeError:
    body.BlockIndices = [2]
bodyF = reflect(body, "rocket surface")
fluid = ExtractBlock(registrationName="air (half)", Input=src)
try:
    fluid.Selectors = ["/Root/internalMesh"]
except AttributeError:
    fluid.BlockIndices = [1]
cp = Calculator(registrationName="Cp field", Input=fluid)
cp.ResultArrayName = "Cp"
cp.Function = CP_EXPR
spd = Calculator(registrationName="speed ratio", Input=cp)
spd.ResultArrayName = "u_over_Uinf"
spd.Function = f"mag(U)/{V}"
if COMP:
    spd = Calculator(registrationName="local Mach", Input=spd)
    spd.ResultArrayName = "Mach"
    spd.Function = "mag(U)/sqrt(1.4*287.05*T)"
upw = Calculator(registrationName="upwash (Uz - freestream)", Input=spd)
upw.ResultArrayName = "dUz"
upw.Function = f"U_Z-{info['U'][2]}"
bcp = Calculator(registrationName="rocket Cp", Input=bodyF)
bcp.ResultArrayName = "Cp"
bcp.Function = CP_EXPR


def surface_views():
    (d,) = only(bcp)
    color(d, "Cp", lo=-0.6, hi=0.6)
    for name, pos, up, txt in (("surface_Cp_side", (0.515, -3, 0), (0, 0, 1), "Surface Cp, side (fin 0 up)"),
                               ("surface_Cp_below", (0.515, 0, -3), (0, 1, 0), "Surface Cp from below (windward)"),
                               ("surface_Cp_above", (0.515, 0, 3), (0, 1, 0), "Surface Cp from above (leeward)")):
        cam(pos, (0.515, 0, 0), up, parallel=0.31)
        shot(name, txt)
    views = [
             ("surface_Cp_iso", (0.2, -0.7, -0.45), (0.6, 0, 0), None, None),
             ("nose_Cp_closeup", (0.05, -0.25, -0.12), (0.1, 0, 0), None, None),
             ("fincan_Cp_iso_windward", (0.85, -0.18, -0.16), (1.0, 0, 0), None, None),
             ("fincan_Cp_iso_leeward", (0.85, -0.18, 0.2), (1.0, 0, 0), None, None),
             ("fins_from_behind", (1.45, 0, 0), (1.0, 0, 0), None, 0.08),
             ("fins_from_front", (0.55, -0.02, 0.02), (1.0, 0, 0), None, 0.08)]
    for name, pos, foc, up, par in views:
        cam(pos, foc, up or (0, 0, 1), par)
        shot(name, "Surface Cp (red = pressure, blue = suction): " + name.replace("_", " "))


def side_slices():
    s = Slice(registrationName="side slice (y=0)", Input=upw)
    s.SliceType = "Plane"
    s.SliceType.Origin = [L / 2, 0.0003, 0]
    s.SliceType.Normal = [0, 1, 0]
    d, b = only(s, bodyF)
    b.DiffuseColor = [0.35, 0.35, 0.35]
    ColorBy(b, None)
    framings = [("whole", (0.62 * L, -2, 0), (0.62 * L, 0, 0), 0.36),
                ("nose", (0.12, -2, 0), (0.12, 0, 0), 0.07),
                ("fins", (1.03, -2, 0), (1.03, 0, 0), 0.07),
                ("wake", (1.25, -2, 0), (1.25, 0, 0), 0.15)]
    for arr, comp, lo, hi, preset, tag in (("u_over_Uinf", None, 0, 1.15, "Viridis (matplotlib)", "speed"),
                                           ("Cp", None, -0.6, 0.6, "Cool to Warm", "Cp"),
                                           ("U", "Z", info["U"][2] - 12, info["U"][2] + 12, "Cool to Warm", "upwash_Uz"),
                                           ("k", None, 0, 150, "Inferno (matplotlib)", "turbulence_k")) + ((("Mach", None, 0, 1.2, "Jet", "Mach"),) if COMP else ()):
        color(d, arr, comp, lo, hi, preset)
        for fname, pos, foc, par in framings:
            if tag in ("upwash_Uz", "turbulence_k") and fname == "nose":
                continue
            cam(pos, foc, (0, 0, 1), par)
            what = {"speed": "speed / U∞", "Cp": "pressure Cp", "upwash_Uz": "vertical velocity Uz (m/s; white = freestream)",
                    "turbulence_k": "turbulence energy k (m²/s²)",
                    "Mach": "local Mach number (red > 1 = supersonic pocket)"}[tag]
            shot(f"side_{tag}_{fname}", f"Side slice through fin 0: {what}, {fname}")


def top_slice():
    s = Slice(registrationName="top slice (z=0)", Input=spd)
    s.SliceType = "Plane"
    s.SliceType.Origin = [L / 2, 0, 0.0]
    s.SliceType.Normal = [0, 0, 1]
    sF = reflect(s, "top slice (full)")
    d, b = only(sF, bodyF)
    ColorBy(b, None)
    color(d, "u_over_Uinf", None, 0, 1.15, "Viridis (matplotlib)")
    cam((1.05, 0, 2), (1.05, 0, 0), (0, 1, 0), 0.12)
    shot("top_speed_fins_wake", "Top slice z = 0: speed / U∞ around the fins and wake")


def cross_sections():
    xle, xte = info.get("x_fin_le", L - 0.05), info.get("x_fin_te", L)   # fin span region from the OML (cfd_rocket setup)
    stations = [(0.08, "nose"), (0.5, "mid_tube"), (xle - 0.07, "fairing"), ((xle + xte) / 2, "mid_fin"),
                (L + 0.01, "base_plus10mm"), (L + 0.08, "wake_80mm"), (L + 0.25, "wake_250mm")]
    for x, tag in stations:
        s = Slice(registrationName=f"cross-section {tag}", Input=spd)
        s.SliceType = "Plane"
        s.SliceType.Origin = [x, 0, 0]
        s.SliceType.Normal = [1, 0, 0]
        sF = reflect(s, f"cross-section {tag} (full)")
        (d,) = only(sF)
        color(d, "u_over_Uinf", None, 0, 1.15, "Viridis (matplotlib)")
        cam((x - 1.0, 0, 0), (x, 0, 0), (0, 0, 1), 0.09)
        shot(f"xsec_speed_{tag}", f"Cross-section looking forward, {tag.replace('_', ' ')}: speed / U∞")
        if tag in ("mid_fin", "base_plus10mm"):
            color(d, "Cp", None, -0.6, 0.6, "Cool to Warm")
            shot(f"xsec_Cp_{tag}", f"Cross-section, {tag.replace('_', ' ')}: pressure Cp")


def streamlines():
    st = StreamTracer(registrationName="streamlines (fin can)", Input=spd, SeedType="Line")
    st.Vectors = ["POINTS", "U"]
    st.SeedType.Point1 = [L - 0.12, 0.004, -0.09]
    st.SeedType.Point2 = [L - 0.12, 0.004, 0.09]
    st.SeedType.Resolution = 80
    st.MaximumStreamlineLength = 1.2
    st2 = StreamTracer(registrationName="streamlines (off-plane)", Input=spd, SeedType="Line")
    st2.Vectors = ["POINTS", "U"]
    st2.SeedType.Point1 = [L - 0.12, 0.0, 0.028]
    st2.SeedType.Point2 = [L - 0.12, 0.08, -0.02]
    st2.SeedType.Resolution = 60
    st2.MaximumStreamlineLength = 1.2
    wk = StreamTracer(registrationName="streamlines (base wake)", Input=spd, SeedType="Line")
    wk.Vectors = ["POINTS", "U"]
    wk.SeedType.Point1 = [L + 0.004, 0.002, -0.02]
    wk.SeedType.Point2 = [L + 0.004, 0.002, 0.02]
    wk.SeedType.Resolution = 30
    wk.MaximumStreamlineLength = 0.6
    a, b, c, bd = only(reflect(st, "streamlines fin can (full)"), reflect(st2, "streamlines off-plane (full)"),
                       wk, bodyF)
    for d in (a, b, c):
        color(d, "u_over_Uinf", None, 0, 1.15, "Plasma (matplotlib)")
    ColorBy(bd, None)
    cam((1.03, -2, 0), (1.06, 0, 0), (0, 0, 1), 0.12); shot("streamlines_side")
    cam((1.06, 0, 2), (1.06, 0, 0), (0, 1, 0), 0.12); shot("streamlines_top")
    cam((0.85, -0.35, 0.22), (1.06, 0, 0)); shot("streamlines_iso")
    cam((1.03, -2, 0), (1.06, 0, 0), (0, 0, 1), 0.05); shot("streamlines_base_recirculation")
    tb = Tube(registrationName="streamline tubes", Input=st2)
    tb.Radius = 0.0012
    t, bd = only(reflect(tb, "streamline tubes (full)"), bodyF)
    color(t, "u_over_Uinf", None, 0, 1.15, "Plasma (matplotlib)")
    ColorBy(bd, None)
    cam((0.88, -0.22, 0.12), (1.04, 0, 0)); shot("streamline_tubes_iso")


def arrows():
    s = Slice(registrationName="arrows slice", Input=spd)
    s.SliceType = "Plane"
    s.SliceType.Origin = [L / 2, 0.0003, 0]
    s.SliceType.Normal = [0, 1, 0]
    g = Glyph(registrationName="velocity arrows", Input=s, GlyphType="Arrow")
    g.OrientationArray = ["POINTS", "U"]
    g.ScaleArray = ["POINTS", "No scale array"]
    g.ScaleFactor = 0.0025
    try:
        g.GlyphMode = "Every Nth Point"     # the mesh is finest near the rocket, so arrows cluster there
        g.Stride = 3
    except Exception:
        pass
    d, bd = only(g, bodyF)
    color(d, "u_over_Uinf", None, 0, 1.15, "Viridis (matplotlib)")
    ColorBy(bd, None)
    cam((1.04, -2, 0), (1.04, 0, 0), (0, 0, 1), 0.06); shot("velocity_arrows_fins", "Velocity arrows in the side slice around the fins")


def isosurfaces():
    c = Contour(registrationName="slow-air wake (u < 60 % U)", Input=spd)
    c.ContourBy = ["POINTS", "u_over_Uinf"]
    c.Isosurfaces = [0.6]
    cF = reflect(c, "wake surface (full)")
    d, bd = only(cF, bcp)
    d.DiffuseColor = [0.2, 0.5, 0.9]
    d.Opacity = 0.6
    ColorBy(d, None)
    color(bd, "Cp", None, -0.6, 0.6)
    cam((0.85, -0.35, 0.2), (1.08, 0, 0)); shot("wake_isosurface_iso", "Blue surface: air slower than 60 % of flight speed (the wake)")
    c2 = Contour(registrationName="suction bubble (Cp = -0.3)", Input=cp)
    c2.ContourBy = ["POINTS", "Cp"]
    c2.Isosurfaces = [-0.3]
    c2F = reflect(c2, "suction surface (full)")
    d2, bd2 = only(c2F, bodyF)
    d2.DiffuseColor = [0.15, 0.35, 0.95]
    d2.Opacity = 0.7
    ColorBy(d2, None)
    ColorBy(bd2, None)
    cam((0.9, -0.25, 0.15), (1.0, 0, 0)); shot("suction_isosurface_fins", "Blue surface: suction region Cp = -0.3 (lift on the fins)")
    c3 = Contour(registrationName="high pressure (Cp = +0.3)", Input=cp)
    c3.ContourBy = ["POINTS", "Cp"]
    c3.Isosurfaces = [0.3]
    c3F = reflect(c3, "pressure surface (full)")
    d3, bd3 = only(c3F, bodyF)
    d3.DiffuseColor = [0.9, 0.2, 0.15]
    ColorBy(d3, None)
    ColorBy(bd3, None)
    cam((0.9, -0.25, -0.15), (1.0, 0, 0)); shot("pressure_isosurface_fin_leading_edges", "Red surface: high pressure Cp = +0.3 at the leading edges")


def sonic():
    if not COMP:
        return
    c = Contour(registrationName="sonic surface (Mach = 1)", Input=spd)
    c.ContourBy = ["POINTS", "Mach"]
    c.Isosurfaces = [1.0]
    cF = reflect(c, "sonic surface (full)")
    d, bd = only(cF, bcp)
    d.DiffuseColor = [1.0, 0.55, 0.0]
    ColorBy(d, None)
    color(bd, "Cp", None, -0.6, 0.6)
    for nm, pos, foc in (("sonic_surface_fins", (0.88, -0.25, 0.15), (1.0, 0, 0)),
                         ("sonic_surface_nose", (0.0, -0.3, 0.12), (0.15, 0, 0))):
        cam(pos, foc)
        shot(nm, "Orange: where the air reaches Mach 1 (supersonic inside); nothing orange = subsonic everywhere")


for title, fn in (("sonic", sonic), ("surface", surface_views), ("side slices", side_slices), ("top slice", top_slice),
                  ("cross-sections", cross_sections), ("streamlines", streamlines), ("arrows", arrows),
                  ("isosurfaces", isosurfaces)):
    section(title, fn)

# leave a nice view in the GUI and save the state
only(bcp)
cam((0.85, -0.18, -0.16), (1.0, 0, 0))
Render(view)
try:
    SaveState(os.path.join(OUT, "gallery.pvsm"))
    print("state saved: gallery.pvsm (File -> Load State)")
except Exception:
    print("state not saved:", traceback.format_exc(limit=1))
print(f"{n[0]} views in {OUT}")
