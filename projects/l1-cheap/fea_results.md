# l1-cheap — In-house FEA (CalculiX), 2026-11-21

**Tool:** `tools/fea_ccx.py`, gmsh 4.15.2 + CalculiX 2.21, run in the project container by the main session.
The setup mirrors the owner's ANSYS runs (`ansys_results.md`):
- support: fixed sleeve bore;
- load: force spread over the +X fin's tip face;
- material: CONSERVATIVE orthotropic PETG (E 1472/1472/1087 MPa, ν 0.38, G 533/394/394 MPa);
- failure index FI = σ_Z / 19 MPa, read in the fin-root zone (load-face spike excluded).

Element type C3D10. Mesh 2.5 mm globally, **0.7 mm in a box around the +X fin root**. Direct solver (SPOOLES).
Run directories: `out/fea/rev<N>/<case>/result.json` and the renders (`fi_overview.png`, `fi_root_zoom.png`).

## 1. Validation against the owner's ANSYS (rev 5)
| Case | Owner ANSYS | CalculiX (0.7 mm root mesh) | Difference |
|---|---|---|---|
| 50 N Y: root σ_Z | 10.85 MPa (FI 0.571) | 8.85 MPa (FI 0.466) | −18 % |
| 50 N Y: root σ_Z (uniform 2.0 mm mesh) | 10.85 MPa | 10.25 MPa (FI 0.540) | −5.5 % |
| 50 N Y: tip deflection | 2.51 mm | 2.84 mm | +13 % |
| 400 N Z: root σ_Z | 9.88 MPa | 9.52 MPa (FI 0.501) | **−3.6 %** |

**Mesh dependence:** the 50 N Y peak sits on a sharp concave edge (top of the insert boss cap, near
(29.8, −1.5, 8.3) mm). The peak there changes with mesh (7.5–10.3 MPa across the meshes tried), as
expected at a sharp corner, in ANSYS too. So **rev-to-rev comparisons use identical settings**, and the
absolute values are scaled to the owner's ANSYS calibration.

## 2. Rev 6 vs rev 5 (identical settings)
| Case | Rev 5 FI | Rev 6 FI | Ratio | Rev 6 peak location (mm) |
|---|---|---|---|---|
| 50 N Y (sideways) | 0.466 | **0.162** | 0.348 (**2.87× stronger**) | (29.4, −2.5, 6.8): boss/fillet |
| 400 N Z (axial) | 0.501 | **0.422** | 0.843 (1.19× stronger) | (29.9, 1.1, 0.8): aft face, root corner |
| Max deflection, 50 N Y | 2.84 mm | 0.90 mm | 3.2× stiffer | tip |

## 3. Rev 6 capacities (FI = 1)
| Load | Raw CalculiX | Scaled to the owner's ANSYS rev 5 calibration |
|---|---|---|
| **Sideways (Y)** | **~308 N** | **~252 N** |
| **Axial (Z)** | ~947 N | ~913 N |

- **Realistic sideways landing hit, ~200 N (ESTIMATE): FI 0.65 (raw) to 0.80 (ANSYS-scaled), so it survives with a 1.25–1.5× margin.**
- Rev 5 at the same 200 N: FI 1.86–2.28 (fails).
- The pre-build prediction for rev 6 (~350–400 N, FI 0.50–0.57 at 200 N) was **optimistic**. The actual gain is 2.9×, not the 4× from pure thickness² scaling, because the peak sits at the boss/fillet corner rather than in plain fin bending.
- The axial capacity barely changed, because the axial peak is at the **aft-face root corner**, which the thickness taper doesn't reinforce.

## 4. Combined loads (rev 6)
Pending: `combined_Y200_Z770` (the owner's rev 5 ANSYS case: FI 3.28) and `combined_200N_at45` (a 200 N
resultant at 45°). The rev 6 Y and Z peaks are at **different** locations, so simple superposition is not valid; the combined runs give the real number.

## 5. Suggested geometric improvements (for the part library; not built)
1. Fillet the **top edge of the insert-boss cap** (the sharp concave edge that carries the sideways peak).
2. Add a small fillet or chamfer where the **fin root meets the aft face** (the axial peak).
