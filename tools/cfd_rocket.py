"""3D RANS CFD of the whole rocket (OpenFOAM simpleFoam, k-omega SST): normal-force slope CN_alpha, CP and drag.

  .venv/bin/python tools/cfd_rocket.py setup [--alpha 4] [--speed 100] [--name a4]   # writes out/cfd/of_<name>/
  bash out/cfd/of_<name>/Allrun                                                       # mesh + solve + VTK export
  (Ubuntu 'openfoam' or OpenFOAM.com 'openfoam2406-default'; Allrun finds either. --np N = CPU cores to use)
  .venv/bin/python tools/cfd_rocket.py post --name a4                                 # CN, CN_alpha, CP, CD

Geometry: out/cfd/rocket_oml.stl from tools/rocket_oml.py (current design.yaml: rev 7 fin can, nose ogive).
CFD frame (m): x = from the nose tip aft (flow +x), z = pitch plane through fin 0, y = 0 is a symmetry plane
(3 fins: fin 0 lies in the plane, fins 1/2 mirror). Half model; forces are doubled in post.
Incompressible at `speed` (default 100 m/s, M 0.29), sea-level air. CP = -M_y / F_z about the tip, reference
diameter 41.275 mm (owner/OR reference), area pi d^2 / 4. Wall functions, no prism layers: pressure (normal force,
CP) is the target; skin friction and drag are rough (y+ ~100-300).
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
D_REF_M = 0.041275            # reference diameter (OR / stability gate reference)
RHO, NU = 1.225, 1.5e-5        # sea-level air
P_INF, T_INF, GAMMA, R_AIR, MU = 101325.0, 288.15, 1.4, 287.05, 1.789e-5   # ISA sea level (compressible runs)
I_TURB, L_TURB = 0.005, 0.01   # freestream turbulence intensity, length scale (m)

HDR = """FoamFile {{ version 2.0; format ascii; class {cls}; object {obj}; }}
"""


def w(path: Path, cls: str, obj: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HDR.format(cls=cls, obj=obj) + body)


def write_compressible(case: Path, a, U, k, om) -> None:
    """Overwrite the incompressible files with a steady compressible (rhoSimpleFoam, transonic) set-up:
    perfect-gas air, ISA sea level, absolute pressure. Freestream far field as for the incompressible run."""
    (case / "constant/transportProperties").unlink(missing_ok=True)
    w(case / "constant/thermophysicalProperties", "dictionary", "thermophysicalProperties", f"""
thermoType {{ type hePsiThermo; mixture pureMixture; transport const; thermo hConst; equationOfState perfectGas;
  specie specie; energy sensibleInternalEnergy; }}
mixture {{ specie {{ molWeight 28.96; }} thermodynamics {{ Cp 1005; Hf 0; }} transport {{ mu {MU}; Pr 0.71; }} }}
""")
    w(case / "system/fvSchemes", "dictionary", "fvSchemes", """
ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
divSchemes { default none;
  div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,e) bounded Gauss linearUpwind default;
  div(phi,K) bounded Gauss linearUpwind default; div(phi,Ekp) bounded Gauss linearUpwind default;
  div(phiv,p) bounded Gauss linearUpwind default; div(phid,p) bounded Gauss linearUpwind default;
  div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind;
  div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear limited corrected 0.5; }
interpolationSchemes { default linear; }
snGradSchemes { default limited corrected 0.5; }
wallDist { method meshWave; }
""")
    w(case / "system/fvSolution", "dictionary", "fvSolution", f"""
solvers {{
  p {{ solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0.05; maxIter 50; }}
  "(U|e|k|omega)" {{ solver smoothSolver; smoother symGaussSeidel; tolerance 1e-9; relTol 0.1; }}
}}
// transonic/consistent off and heavy p relaxation: the impulsive M 0.8 start diverges otherwise (negative T)
SIMPLE {{ nNonOrthogonalCorrectors 1; transonic no; consistent no; pMinFactor 0.5; pMaxFactor 1.5; }}
relaxationFactors {{ equations {{ U 0.5; e 0.5; k 0.5; omega 0.5; }} fields {{ p 0.2; rho 1; }} }}
""")
    Us = f"({U[0]:.6f} {U[1]:.6f} {U[2]:.6f})"
    sym = 'symmetry { type symmetryPlane; }\n  "proc.*" { type processor; }'
    fld = {
        "U": ("volVectorField", "[0 1 -1 0 0 0 0]", f"uniform {Us}",
              f"farfield {{ type freestreamVelocity; freestreamValue uniform {Us}; }}\n  rocket {{ type noSlip; }}"),
        "p": ("volScalarField", "[1 -1 -2 0 0 0 0]", f"uniform {P_INF}",
              f"farfield {{ type freestreamPressure; freestreamValue uniform {P_INF}; supersonic false; }}\n  rocket {{ type zeroGradient; }}"),
        "T": ("volScalarField", "[0 0 0 1 0 0 0]", f"uniform {T_INF}",
              f"farfield {{ type inletOutlet; inletValue uniform {T_INF}; }}\n  rocket {{ type zeroGradient; }}"),
        "k": ("volScalarField", "[0 2 -2 0 0 0 0]", f"uniform {k:.6g}",
              f"farfield {{ type inletOutlet; inletValue uniform {k:.6g}; }}\n  rocket {{ type kqRWallFunction; value uniform {k:.6g}; }}"),
        "omega": ("volScalarField", "[0 0 -1 0 0 0 0]", f"uniform {om:.6g}",
                  f"farfield {{ type inletOutlet; inletValue uniform {om:.6g}; }}\n  rocket {{ type omegaWallFunction; value uniform {om:.6g}; }}"),
        "nut": ("volScalarField", "[0 2 -1 0 0 0 0]", "uniform 0",
                "farfield { type calculated; value uniform 0; }\n  rocket { type nutkWallFunction; value uniform 0; }"),
        "alphat": ("volScalarField", "[1 -1 -1 0 0 0 0]", "uniform 0",
                   "farfield { type calculated; value uniform 0; }\n  rocket { type compressible::alphatWallFunction; Prt 0.85; value uniform 0; }"),
    }
    for f, (cls, dim, internal, bcs) in fld.items():
        w(case / "0.orig" / f, cls, f, f"\ndimensions {dim};\ninternalField {internal};\nboundaryField {{\n  {bcs}\n  {sym}\n}}\n")


def setup(a) -> Path:
    case = ROOT / "out" / "cfd" / f"of_{a.name}"
    m = trimesh.load(ROOT / "out" / "cfd" / "rocket_oml.stl", force="mesh")
    z_tip = m.bounds[1][2]
    v = m.vertices
    m.vertices = np.column_stack([(z_tip - v[:, 2]), v[:, 1], v[:, 0]]) / 1000.0   # (X,Y,Z)->(-Z,Y,X): proper rotation
    L = float(m.bounds[1][0])
    (case / "constant" / "triSurface").mkdir(parents=True, exist_ok=True)
    m.export(case / "constant" / "triSurface" / "rocket.stl")
    comp = a.mach > 0
    if comp:
        a.speed = a.mach * math.sqrt(GAMMA * R_AIR * T_INF)
    al = math.radians(a.alpha)
    U = (a.speed * math.cos(al), 0.0, a.speed * math.sin(al))
    k = 1.5 * (a.speed * I_TURB) ** 2
    om = math.sqrt(k) / (0.09 ** 0.25 * L_TURB)
    x0, x1, y1, zr = -1.0, L + 3.0, 1.0, 1.0
    n = (int(round((x1 - x0) / 0.05)), int(round(y1 / 0.05)), int(round(2 * zr / 0.05)))
    w(case / "system/blockMeshDict", "dictionary", "blockMeshDict", f"""
convertToMeters 1;
vertices ( ({x0} 0 {-zr}) ({x1} 0 {-zr}) ({x1} {y1} {-zr}) ({x0} {y1} {-zr})
           ({x0} 0 {zr}) ({x1} 0 {zr}) ({x1} {y1} {zr}) ({x0} {y1} {zr}) );
blocks ( hex (0 1 2 3 4 5 6 7) ({n[0]} {n[1]} {n[2]}) simpleGrading (1 1 1) );
boundary (
  farfield {{ type patch; faces ( (0 4 7 3) (1 2 6 5) (3 7 6 2) (0 3 2 1) (4 5 6 7) ); }}
  symmetry {{ type symmetryPlane; faces ( (0 1 5 4) ); }}
);
""")
    w(case / "system/surfaceFeatureExtractDict", "dictionary", "surfaceFeatureExtractDict", """
rocket.stl { extractionMethod extractFromSurface; extractFromSurfaceCoeffs { includedAngle 150; } writeObj no; }
""")
    w(case / "system/snappyHexMeshDict", "dictionary", "snappyHexMeshDict", f"""
castellatedMesh true; snap true; addLayers false;
geometry {{
  rocket.stl {{ type triSurfaceMesh; name rocket; }}
  near {{ type searchableBox; min (-0.05 0 -0.16); max ({L + 0.05} 0.16 0.16); }}
  wake {{ type searchableBox; min (-0.3 0 -0.3); max ({L + 1.2} 0.3 0.3); }}
}};
castellatedMeshControls {{
  maxLocalCells 4000000; maxGlobalCells 12000000; minRefinementCells 10; maxLoadUnbalance 0.10;
  nCellsBetweenLevels 3;
  features ( {{ file "rocket.eMesh"; level 5; }} );
  refinementSurfaces {{ rocket {{ level (4 5); patchInfo {{ type wall; }} }} }}
  resolveFeatureAngle 30;
  refinementRegions {{ near {{ mode inside; levels ((1E15 3)); }} wake {{ mode inside; levels ((1E15 2)); }} }}
  locationInMesh ({L + 2.0} 0.5 0.5);
  allowFreeStandingZoneFaces true;
}}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5; nFeatureSnapIter 10;
  implicitFeatureSnap false; explicitFeatureSnap true; multiRegionFeatureSnap false; }}
addLayersControls {{ relativeSizes true; layers {{ }} expansionRatio 1.2; finalLayerThickness 0.5; minThickness 0.1;
  nGrow 0; featureAngle 60; nRelaxIter 3; nSmoothSurfaceNormals 1; nSmoothNormals 3; nSmoothThickness 10;
  maxFaceThicknessRatio 0.5; maxThicknessToMedialRatio 0.3; minMedialAxisAngle 90; nBufferCellsNoExtrude 0;
  nLayerIter 50; }}
meshQualityControls {{ maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80;
  minVol 1e-13; minTetQuality 1e-15; minArea -1; minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.05;
  minVolRatio 0.01; minTriangleTwist -1; nSmoothScale 4; errorReduction 0.75; relaxed {{ maxNonOrtho 75; }} }}
mergeTolerance 1e-6;
""")
    w(case / "system/controlDict", "dictionary", "controlDict", f"""
application {"rhoSimpleFoam" if comp else "simpleFoam"}; startFrom latestTime; startTime 0; stopAt endTime; endTime {a.iters}; deltaT 1;
writeControl timeStep; writeInterval {max(1, a.iters // 4)}; purgeWrite 0; writeFormat binary; writePrecision 8;
writeCompression off; timeFormat general; timePrecision 6; runTimeModifiable true;
// no `forces` function object: it crashes in the Debian OpenFOAM build; tools/cfd_post.py integrates the surface pressure
""")
    w(case / "system/decomposeParDict", "dictionary", "decomposeParDict", f"numberOfSubdomains {a.np};\nmethod hierarchical;\nhierarchicalCoeffs {{ n ({a.np} 1 1); order xyz; }}\n")
    w(case / "system/fvSchemes", "dictionary", "fvSchemes", """
ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U);
  div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind;
  div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear limited corrected 0.5; }
interpolationSchemes { default linear; }
snGradSchemes { default limited corrected 0.5; }
wallDist { method meshWave; }
""")
    w(case / "system/fvSolution", "dictionary", "fvSolution", """
solvers {
  p { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.05; }
  "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.1; }
}
SIMPLE { nNonOrthogonalCorrectors 1; consistent yes; }
potentialFlow { nNonOrthogonalCorrectors 5; }
relaxationFactors { equations { U 0.7; ".*" 0.5; } fields { p 0.5; } }
""")
    w(case / "constant/transportProperties", "dictionary", "transportProperties",
      f"transportModel Newtonian;\nnu {NU};\n")
    w(case / "constant/turbulenceProperties", "dictionary", "turbulenceProperties",
      "simulationType RAS;\nRAS { RASModel kOmegaSST; turbulence on; printCoeffs on; }\n")
    Us = f"({U[0]:.6f} {U[1]:.6f} {U[2]:.6f})"
    fields = {
        "U": ("volVectorField", "[0 1 -1 0 0 0 0]", f"uniform {Us}",
              f"farfield {{ type freestreamVelocity; freestreamValue uniform {Us}; }}\n  rocket {{ type noSlip; }}"),
        "p": ("volScalarField", "[0 2 -2 0 0 0 0]", "uniform 0",
              "farfield { type freestreamPressure; freestreamValue uniform 0; }\n  rocket { type zeroGradient; }"),
        "k": ("volScalarField", "[0 2 -2 0 0 0 0]", f"uniform {k:.6g}",
              f"farfield {{ type inletOutlet; inletValue uniform {k:.6g}; }}\n  rocket {{ type kqRWallFunction; value uniform {k:.6g}; }}"),
        "omega": ("volScalarField", "[0 0 -1 0 0 0 0]", f"uniform {om:.6g}",
                  f"farfield {{ type inletOutlet; inletValue uniform {om:.6g}; }}\n  rocket {{ type omegaWallFunction; value uniform {om:.6g}; }}"),
        "nut": ("volScalarField", "[0 2 -1 0 0 0 0]", "uniform 0",
                "farfield { type calculated; value uniform 0; }\n  rocket { type nutkWallFunction; value uniform 0; }"),
    }
    for f, (cls, dim, internal, bcs) in fields.items():
        w(case / "0.orig" / f, cls, f, f"""
dimensions {dim};
internalField {internal};
boundaryField {{
  {bcs}
  symmetry {{ type symmetryPlane; }}
  "proc.*" {{ type processor; }}
}}
""")
    if comp:
        write_compressible(case, a, U, k, om)
    t_last, t_prev = a.iters, a.iters - max(1, a.iters // 4)
    (case / "Allrun").write_text(f"""#!/bin/bash
# OpenFOAM environment: Debian/Ubuntu package (/usr/share/openfoam) or OpenFOAM.com package (/usr/lib/openfoam/openfoamXXXX)
cd "$(dirname "$0")"
if [ -d /usr/share/openfoam ] && command -v blockMesh >/dev/null; then
  export WM_PROJECT_DIR=/usr/share/openfoam
else
  rc=$(ls -d /usr/lib/openfoam/openfoam*/etc/bashrc 2>/dev/null | tail -1)
  [ -n "$rc" ] || {{ echo "OpenFOAM not found (install: Ubuntu 'openfoam' or OpenFOAM.com 'openfoam2406-default')"; exit 1; }}
  set +u; source "$rc"
fi
command -v blockMesh >/dev/null || {{ echo "OpenFOAM tools not on PATH"; exit 1; }}
set -e
rm -rf log.* processor* done.flag constant/polyMesh VTKL [1-9]*
export OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
MPI="mpirun --oversubscribe -np {a.np}"
blockMesh > log.blockMesh 2>&1
surfaceFeatureExtract > log.surfaceFeatureExtract 2>&1
decomposePar -force > log.decomposePar 2>&1
$MPI snappyHexMesh -overwrite -parallel > log.snappyHexMesh 2>&1
$MPI checkMesh -parallel > log.checkMesh 2>&1 || true
for d in processor*; do rm -rf $d/0; cp -r 0.orig $d/0; done
$MPI {"rhoSimpleFoam" if comp else "simpleFoam"} -parallel > log.simpleFoam 2>&1
$MPI foamToVTK -parallel -time '{t_prev},{t_last}' -no-internal -no-point-data -legacy -ascii -name VTKL > log.vtk 2>&1
$MPI foamToVTK -parallel -time '{t_last}' -no-boundary -legacy -name VTKI > log.vtki 2>&1
echo DONE > done.flag
echo "solved; now: .venv/bin/python tools/cfd_post.py --name {a.name} && .venv/bin/python tools/cfd_figures_extra.py --name {a.name}"
""")
    (case / "Allrun").chmod(0o755)
    meta = {"alpha_deg": a.alpha, "speed": a.speed, "L": L, "U": U, "t_prev": t_prev, "t_last": t_last,
            "compressible": comp, "mach": a.mach if comp else a.speed / math.sqrt(GAMMA * R_AIR * T_INF)}
    if comp:
        meta.update({"p_inf": P_INF, "T_inf": T_INF, "rho_inf": P_INF / (R_AIR * T_INF)})
    json.dump(meta, open(case / "case.json", "w"))
    print(f"case {case}  L {L:.3f} m  blocks {n}  U {Us}  k {k:.4g}  omega {om:.4g}")
    return case


def post(a) -> dict:
    case = ROOT / "out" / "cfd" / f"of_{a.name}"
    c = json.load(open(case / "case.json"))
    files = sorted(case.glob("postProcessing/forces/*/force*.dat")) + sorted(case.glob("postProcessing/forces/*/forces.dat"))
    mfiles = sorted(case.glob("postProcessing/forces/*/moment*.dat"))
    num = re.compile(r"[-+0-9.eE]+")

    def rows(f):
        out = []
        for line in Path(f).read_text().splitlines():
            if line.startswith("#") or not line.strip():
                continue
            out.append([float(x) for x in num.findall(line)])
        return np.array(out)
    F, M = rows(files[0]), rows(mfiles[0])
    n = max(1, len(F) // 10)                                  # average the last 10 % of iterations
    Ft, Mt = 2 * F[-n:, 1:4].mean(axis=0), 2 * M[-n:, 1:4].mean(axis=0)   # total (first triplet), half model x2
    Ft[1], Mt[0], Mt[2] = 0.0, 0.0, 0.0                       # symmetric: side force, roll, yaw cancel
    q = 0.5 * RHO * c["speed"] ** 2
    A = math.pi * D_REF_M ** 2 / 4
    al = math.radians(c["alpha_deg"])
    Fn = Ft[2] * math.cos(al) - Ft[0] * math.sin(al) * 0      # body-axis normal force = F_z (body frame)
    Fa = Ft[0]
    cp_x = -Mt[1] / Ft[2]
    res = {"alpha_deg": c["alpha_deg"], "speed_m_s": c["speed"], "iterations": int(F[-1, 0]),
           "CN": Fn / (q * A), "CN_alpha_per_rad": Fn / (q * A) / al, "CP_from_tip_mm": cp_x * 1000,
           "CA": Fa / (q * A), "Fz_N": Ft[2], "Fx_N": Ft[0], "My_Nm": Mt[1],
           "CP_drift_last10pct_mm": float(np.ptp(-2 * M[-n:, 2] / (2 * F[-n:, 3])) * 1000)}
    (case / "result.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["setup", "post"])
    ap.add_argument("--alpha", type=float, default=4.0)
    ap.add_argument("--speed", type=float, default=100.0)
    ap.add_argument("--mach", type=float, default=0.0, help="> 0: compressible rhoSimpleFoam at this Mach (sets speed)")
    ap.add_argument("--iters", type=int, default=800)
    ap.add_argument("--np", type=int, default=4)
    ap.add_argument("--name", default="a4")
    a = ap.parse_args()
    setup(a) if a.cmd == "setup" else post(a)
