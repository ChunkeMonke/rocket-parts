# fin_can_rev1 — spec sheet

**Generated:** 2026-11-20 · `python make.py fin_can --rev 1`
**Status:** DRAFT — NOT PRINT-READY (placeholders/open items below)

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=136196.5 mm3, bodies=1 |
| 2 | mass | FAIL | target 197.3 g (±5 %); reachable 170.5 g (0 %) – 173.0 g (100 %); infill to hit target = 1072.6 % |
| 3 | mating interference | PASS | tube_wall: 0.000 mm3, liner_and_motor: 0.000 mm3, motor_thrust_ring: 0.000 mm3 |
| 4 | renders | PASS | written: fin_can_rev1_iso.png, fin_can_rev1_front.png, fin_can_rev1_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 93.2 / Y 107.6 / Z 203.0 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 134.23 cm³ · infill region 1.97 cm³ · mesh volume 136.20 cm³
- Mass at 0 % / 100 % infill: 170.5 g / 173.0 g · target 197.3 g · infill needed: 1072.6 %

## Print orientation
Aft face DOWN on the bed, axis vertical (+Z = forward). No supports: fin outlines shrink going up (TE square at the bed, LE swept back).

## Loads vs. layers
- Motor thrust: the thrust ring pushes UP (+Z) on the aft face, so the layers are pressed together (compression across layers). Good direction.
- Fin root bending (aero side load): bending stress runs radially/tangentially, WITHIN the layers.
- Kevlar anchor (deploy): the cord pulls +Z on a groove epoxied under the tube. The bond is loaded in shear on vertical faces, so the PETG layers are sheared in-plane, not peeled apart.
- Ejection kick on the motor (aft): taken by the motor retention, which is NOT in rev 1 (OPEN).

## Parameters
| Parameter | Value | Status | Source / note |
|---|---|---|---|
| `body_od_mm` | 41.275 | PLACEHOLDER | tube OD nominal; measure the BT-1.52 with calipers |
| `tube_id_mm` | 38.735 | derived/shop |  |
| `shoulder_od_mm` | 38.555 | derived/shop |  |
| `exposed_length_mm` | 100 | FROM_AERO | = fin root chord, TE flush with aft face |
| `shoulder_length_mm` | 103 | FROM_STABILITY | motor 203 - exposed 100: bore supports full motor |
| `liner_od_mm` | 30.5 | PLACEHOLDER | not published; measure the liner |
| `liner_id_mm` | 28.956 | CITED | 1.140 in, OpenRocket catalogue via github.com/nrdptel/fusionspace-eridanus/issues/280 (third-party) |
| `liner_length_mm` | 203 | FROM_MOTOR | = motor length |
| `bore_d_mm` | 30.68 | derived/shop |  |
| `fin_count` | 3 | derived/shop |  |
| `root_chord_mm` | 100 | derived/shop |  |
| `tip_chord_mm` | 40 | derived/shop |  |
| `span_mm` | 40 | derived/shop |  |
| `sweep_mm` | 60 | derived/shop |  |
| `fin_thickness_mm` | 5 | derived/shop |  |
| `te_thickness_mm` | 0.84 | derived/shop |  |
| `root_fillet_r_mm` | 4 | PROPOSED | owner suggested range 3-5 not yet confirmed |
| `root_fillet_sections` | 6 | PROPOSED | loft stations approximating the circular fillet |
| `airfoil_points` | 41 | PROPOSED | cosine-spaced chord stations per side |
| `anchor_groove_width_mm` | 3 | PROPOSED | Kevlar 2.3 mm + clearance |
| `anchor_groove_depth_mm` | 2.6 | PROPOSED |  |
| `anchor_angle_deg` | 60 | PROPOSED | between fins |
| `thrust_ring_od_mm` | 33 | PLACEHOLDER | not published; measure the motor (mating check only) |
| `thrust_ring_thk_mm` | 3 | PLACEHOLDER | not published; measure the motor (mating check only) |
| `target_mass_g` | 197.3 | FROM_STABILITY | stability ESTIMATE; update stability with the real model mass |

## Not print-ready until resolved
- `body_od_mm`: tube OD nominal; measure the BT-1.52 with calipers
- `liner_od_mm`: not published; measure the liner
- `retention`: axial M3 inserts need ~3 mm walls around a 4 mm hole; only ~5 mm between bore and OD. Needs thrust-ring OD to choose a scheme
- `thrust_ring_od_mm`: not published; measure the motor (mating check only)
- `thrust_ring_thk_mm`: not published; measure the motor (mating check only)

## Extra outputs
- `fin_can_rev1_airfoil_root.dat`
- `fin_can_rev1_airfoil_tip.dat`
- `fin_can_rev1_fin_only.step`
