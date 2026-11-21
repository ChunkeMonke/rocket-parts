# l1-cheap — ANSYS results, fin can rev 5 (owner runs, 2026-11-20/21)

**Tool:** Ansys Mechanical Enterprise 2023 R1 (owner's Workbench project "Peppa Pig Rocket Fins").
**Geometry:** `out/fin_can_md/rev5/fin_can_md_rev5.step`. Units mm; Z = rocket axis = print direction.
Screenshots are in `report/figures/ansys/`.

## Material: `3D_Printed_PETG` (orthotropic; Z = across layers)
- **Owner's entered values** (screenshot `00_material_table`): density 1270 kg/m³; Ex = Ey 1880, Ez 500 MPa; νxy 0.35, νyz 0.3, νxz 0.3; Gxy 696, Gyz 500, Gxz 500 MPa.
- **Recommended in chat 2026-11-21:**
  - *Conservative:* Exy 1472, Ez 1087, ν 0.38 (assumed), Gxy 533, Gyz = Gxz 394 MPa. In-plane and across-layer moduli are from the [JuggerBot PETG review](https://juggerbot3d.com/petg-filament-review/).
  - *Nominal:* 1939 / 1711 MPa, from the [Ultimaker PETG TDS](https://um-support-files.ultimaker.com/materials/2.85mm/tds/PETG/Ultimaker-PETG-TDS-v1.00.pdf).
  - Both sets were picked off search-result summaries, not read from the documents; confirm before relying on them.
- **The runs below used the CONSERVATIVE recommended set** (owner confirmed 2026-11-21). The material-table screenshot shows the owner's earlier values, from before the update.
- **Failure limits** used to judge results:
  - Z tensile (across layers) ~19 MPa (Ultimaker TDS, upright);
  - interlayer shear ~15 MPa (shop constant);
  - in-plane tensile ~38.5 MPa (Ultimaker TDS, flat).

## Mesh
Tetrahedral, element size 1 mm: **422,598 nodes, 244,392 elements** (`01_mesh_1mm`). An earlier default mesh had 42,442 nodes.

## Boundary condition (all static cases)
**Fixed Support on the sleeve bore** (R 20.727 mm; the epoxied joint to the tube). One support only.

## Case 1: flight side gust
Force Y = 15 N on one side of the +X fin, an ESTIMATE: 5° AoA at max q ≈ 37 kPa. Linear static.

| Result | Max | Limit | Factor |
|---|---|---|---|
| Total deformation | 0.274 mm | — | — |
| Normal Z (across layers) | +1.72 / −1.58 MPa | 19 MPa | ~11× |
| Shear XZ | 0.354 MPa | 15 MPa | ~42× |
| Shear YZ | 0.192 MPa | 15 MPa | ~78× |
| Von Mises | 3.42 MPa (fin root) | 38.5 MPa | ~11× |

## Case 2: modal (free vibration, same support)
9 modes, in groups of three (one per fin):
- **567.9 Hz** (modes 1–3) — likely 1st bending
- **1530 Hz** (modes 4–6) — torsion or 2nd bending (mode shapes not yet confirmed)
- **2677 Hz** (modes 7–9)

**Flutter estimate** (NACA TN 4197 via the main session, fins 50/30/43.18/6, sea level):
- at G = 394 MPa: Vf ≈ 1330 m/s, about **5.3×** the 250 m/s Vmax;
- at G = 620 MPa: Vf ≈ 1670 m/s, about 6.7×.

## Case 3: landing tip strike, sideways (Y)
Force Y = 50 N on the +X fin's tip face.

| Result | Max | Limit | Factor |
|---|---|---|---|
| Total deformation | 2.51 mm | — | — |
| Normal Z | 10.8 MPa (root) | 19 | 1.75× → **fails at ~88 N** |
| Shear YZ / XZ | 1.48 / 2.77 MPa | 15 | 5.4–10× |
| Von Mises | 21.4 MPa | 38.5 | 1.8× → ~90 N |

## Case 4: landing tip strike, axial (Z)
Force on the tip face in Z. The structure behaves linearly: **0.0247 MPa per N** at the fin root, aft end.

| Load | Normal Z max | Ratio to 19 MPa |
|---|---|---|
| 400 N | 9.88 MPa | 0.52 |
| 770 N | 19.0 MPa (failure index `SZ/19e6` = 1.0008, legend 0–1: **FAILURE POINT**, onset at the root fillet, aft end; `45_tipZ770_failure_point`) | 1.00 |
| 900 N | 22.2 MPa; failure index 1.1697 at the root fillet, aft end (`44_tipZ900_failure_index`) | 1.17 |
| 2000 N | failure index `SZ/19e6` max 2.5994 (49.4 MPa); legend 0–1; failed band = root fillet at the aft end (`43_tipZ2000_failure_index`) | 2.60 |

**Axial failure load ≈ 770 N.**

## Case 3b: sideways failure index
50 N Y gives failure index max **0.571** (`35_tipY50_failure_index`), which confirms the ~88 N failure load.

## Case 5: combined tip load, 200 N Y + 770 N Z
Failure index max **3.28** (`50_combined_Y200_Z770_failure_index`). This equals 2.28 (200 N Y, scaled) + 1.00 (770 N Z), so superposition holds; both peak at the root fillet.

## Landing-load context (main-session ESTIMATE, 2026-11-21)
- Landing energy: 40 in chute 3.8–4.7 J; 28 in chute 7.8–9.7 J (540–600 g, Cd 0.75).
- Impact force ≈ energy ÷ stopping distance (2–5 cm ground): 90–220 N average with the 40 in chute, peaks to ~450 N. With the 28 in chute: 180–450 N average, peaks to ~900 N.
- Realistic design value: **~200 N**.
  - Axial: fine, ~3.8× margin.
  - Sideways: **fails (~90 N capacity)**.
- **Mitigations:**
  - fly the 40 in chute unreefed;
  - drop-test the fit-test print (0.8 m for the 40 in, 1.5 m for the 28 in);
  - or a landing-tough rev 6 (needs ~2.3× root bending strength: thicker fin / bigger fillet / shorter span).

## Not yet run
- Motor thrust: +138 N on the lip underside.
- Mode-shape identification for modes 4–6.
