# fin_can_rev2 — spec sheet

**Generated:** 2026-11-20 · `python make.py fin_can --rev 2`
**Status:** DRAFT — NOT PRINT-READY (placeholders/open items below)

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=137055.7 mm3, bodies=1 |
| 2 | mass | PASS | target 171.1 g (±5 %); reachable 171.0 g (0 %) – 174.1 g (100 %); infill to hit target = 2.3 % |
| 3 | mating interference | PASS | tube_wall: 0.000 mm3, liner_and_motor: 0.000 mm3, motor_thrust_ring: 0.000 mm3 |
| 4 | renders | PASS | written: fin_can_rev2_iso.png, fin_can_rev2_front.png, fin_can_rev2_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 93.2 / Y 107.6 / Z 203.0 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 134.67 cm³ · infill region 2.39 cm³ · mesh volume 137.06 cm³
- Mass at 0 % / 100 % infill: 171.0 g / 174.1 g · target 171.1 g · infill needed: 2.3 %

## Print orientation
Aft face DOWN on the bed, axis vertical (+Z = forward). No supports: fin outlines shrink going up (TE square at the bed, LE swept back).

## Loads vs. layers
- Motor thrust: the thrust ring pushes UP (+Z) on the aft face, so the layers are pressed together (compression across layers). Good direction.
- Fin root bending (aero side load): bending stress runs radially/tangentially, WITHIN the layers.
- Kevlar anchor (deploy): the cord pulls +Z on a groove epoxied under the tube. The bond is loaded in shear on vertical faces, so the PETG layers are sheared in-plane, not peeled apart.
- Ejection kick on the motor (aft): thrust ring pulls the screws/washers aft (-Z); each insert is pulled out of its boss along Z, which loads the boss across the layers (the weak direction). Capacity estimate in motor.md (SF ~2.6 for 2 inserts; rev 2 has one per fin).

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
| `target_mass_g` | 171.1 | FROM_STABILITY | stability budget 2026-11-20 uses the rev 1 model mass (25 % infill) |
| `retention` | insert_bosses_at_fin_roots | OWNER | owner 2026-11-20 rev 2: Option A, one M3 heat-set insert per fin in a faired boss at the fin root, aft end (supersedes friction fit) |
| `insert_hole_d_mm` | 4 | CITED | M3 heat-set hole for 3D prints, accu-components chart (motor.md) |
| `insert_depth_mm` | 5.7 | CITED | M3 x 5.7 standard insert length, Prusa/CNC Kitchen listing (motor.md) |
| `boss_wall_mm` | 2.67 | PROPOSED |  |
| `insert_radius_mm` | 20.01 | derived/shop |  |
| `boss_fairing_length_mm` | 20 | PROPOSED | length over which the boss tapers into the fin, forward of the insert |
| `washer_min_overlap_mm` | 2 | FROM_MOTOR | motor.md overlap rule: washer OD/2 - (insert radius - ring OD/2) >= 2 mm |
| `washer_min_od_mm` | 11.02 | derived/shop |  |

## Not print-ready until resolved
- `body_od_mm`: tube OD nominal; measure the BT-1.52 with calipers
- `liner_od_mm`: not published; measure the liner
- `thrust_ring_od_mm`: not published; measure the motor (mating check only)
- `thrust_ring_thk_mm`: not published; measure the motor (mating check only)

## Extra outputs
- `fin_can_rev2_airfoil_root.dat`
- `fin_can_rev2_airfoil_tip.dat`
- `fin_can_rev2_fin_only.step`
