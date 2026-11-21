# fin_can_md_rev3 — spec sheet

**Generated:** 2026-11-21 · `python make.py fin_can_md --rev 3`
**Status:** DRAFT — NOT PRINT-READY (placeholders/open items below)

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=77396.1 mm3, bodies=1 |
| 2 | mass | FAIL | no target mass declared |
| 3 | mating interference | PASS | tube_wall: 0.000 mm3, motor_case: 0.000 mm3, motor_thrust_ring: 0.000 mm3 |
| 4 | renders | PASS | written: fin_can_md_rev3_iso.png, fin_can_md_rev3_front.png, fin_can_md_rev3_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 97.4 / Y 112.4 / Z 120.0 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 76.84 cm³ · infill region 0.54 cm³ · mesh volume 77.40 cm³
- Mass at 0 % / 100 % infill: 97.6 g / 98.3 g · target None g · infill needed: n/a

## Print orientation
Aft face (lip) DOWN on the bed, axis vertical. No supports: lip and sleeve are vertical walls, fins shrink going up, the forward fairing narrows going up.

## Loads vs. layers
- Motor thrust: the thrust ring pushes UP (+Z) on the lip's underside, and the lip pushes the tube end forward. The layers are pressed together (compression across layers). Good direction.
- Fin root bending: within the layers (radial/tangential).
- Sleeve-to-tube epoxy joint: carries fin loads and drag in shear on vertical (cylindrical) faces, so the PETG is sheared in-plane.
- Ejection kick on the motor (-Z): the ring pulls the screws aft, and the inserts pull out of their bosses along Z (across layers, the weak direction). See motor.md for capacity.

## Parameters
| Parameter | Value | Status | Source / note |
|---|---|---|---|
| `tube_od_mm` | 41.275 | PLACEHOLDER | BT-1.52 OD nominal; MEASURE — sets the sleeve bore |
| `tube_id_mm` | 38.735 | derived/shop |  |
| `sleeve_bore_d_mm` | 41.455 | derived/shop |  |
| `sleeve_wall_mm` | 2.67 | PROPOSED |  |
| `body_od_mm` | 46.795 | derived/shop |  |
| `sleeve_length_mm` | 100 | derived/shop |  |
| `fairing_length_mm` | 20 | PROPOSED | forward taper from sleeve OD down to the tube OD (no step in the flow) |
| `feather_edge_mm` | 0.84 | derived/shop |  |
| `lip_thickness_mm` | 2.67 | PROPOSED |  |
| `motor_case_od_mm` | 38 | PLACEHOLDER | 38 mm class, NOT measured; lip bore = case OD + 2 x snug slip |
| `lip_bore_d_mm` | 38.18 | derived/shop |  |
| `motor_length_mm` | 153 | CITED | ThrustCurve H100W_DMS via search (38 x 153 mm); motor agent confirming |
| `thrust_ring_od_mm` | 41 | PLACEHOLDER | not published yet (motor agent researching); must be > lip bore to bear |
| `thrust_ring_thk_mm` | 3 | PLACEHOLDER | not published; mating check only |
| `fin_count` | 3 | derived/shop |  |
| `root_chord_mm` | 100 | derived/shop |  |
| `tip_chord_mm` | 40 | derived/shop |  |
| `span_mm` | 40 | derived/shop |  |
| `sweep_mm` | 60 | derived/shop |  |
| `fin_thickness_mm` | 5 | derived/shop |  |
| `te_thickness_mm` | 0.84 | derived/shop |  |
| `root_fillet_r_mm` | 4 | PROPOSED |  |
| `root_fillet_sections` | 6 | PROPOSED |  |
| `airfoil_points` | 41 | PROPOSED |  |
| `insert_hole_d_mm` | 4 | CITED | accu-components chart (motor.md) |
| `insert_depth_mm` | 5.7 | CITED | Prusa/CNC Kitchen M3 x 5.7 (motor.md) |
| `boss_wall_mm` | 2.67 | derived/shop |  |
| `insert_radius_mm` | 25.398 | derived/shop |  |
| `boss_fairing_length_mm` | 20 | PROPOSED |  |
| `target_mass_g` | None | TBD | stability to set after re-sim with the H100W |
| `washer_min_od_mm` | 13.795 | derived/shop |  |

## Not print-ready until resolved
- `motor_case_od_mm`: 38 mm class, NOT measured; lip bore = case OD + 2 x snug slip
- `thrust_ring_od_mm`: not published yet (motor agent researching); must be > lip bore to bear
- `thrust_ring_thk_mm`: not published; mating check only
- `tube_od_mm`: BT-1.52 OD nominal; MEASURE — sets the sleeve bore

## Extra outputs
- `fin_can_md_rev3_airfoil_root.dat`
- `fin_can_md_rev3_airfoil_tip.dat`
- `fin_can_md_rev3_fin_only.step`
