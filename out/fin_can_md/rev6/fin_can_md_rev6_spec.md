# fin_can_md_rev6 — spec sheet

**Generated:** 2026-11-21 · `python make.py fin_can_md --rev 6`
**Status:** DRAFT — NOT PRINT-READY (placeholders/open items below)

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=80276.6 mm3, bodies=1 |
| 2 | mass | PASS | target 84.8 g (±5 %); reachable 87.0 g (0 %) – 101.9 g (100 %); infill to hit target = -14.6 % |
| 3 | mating interference | PASS | tube_wall: 0.000 mm3, motor_case: 0.000 mm3, motor_thrust_ring: 0.000 mm3 |
| 4 | renders | PASS | written: fin_can_md_rev6_iso.png, fin_can_md_rev6_front.png, fin_can_md_rev6_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 102.6 / Y 118.4 / Z 120.0 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 68.51 cm³ · infill region 11.76 cm³ · mesh volume 80.28 cm³
- Mass at 0 % / 100 % infill: 87.0 g / 101.9 g · target 84.83 g · infill needed: -14.6 %

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
| `motor_case_od_mm` | 38.1 | PLACEHOLDER | 1.500 in nominal from AeroTech I500T (different 38 mm DMS) page, via motor agent; MEASURE the H100W |
| `lip_bore_d_mm` | 38.28 | derived/shop |  |
| `motor_length_mm` | 155 | CITED | motor agent 2026-11-21 (38 x 155 mm; ThrustCurve snippet said 153) — measure |
| `thrust_ring_od_mm` | 41 | PLACEHOLDER | not published yet (motor agent researching); must be > lip bore to bear |
| `thrust_ring_thk_mm` | 3 | PLACEHOLDER | not published; mating check only |
| `fin_count` | 3 | derived/shop |  |
| `root_chord_mm` | 50 | derived/shop |  |
| `tip_chord_mm` | 30 | derived/shop |  |
| `span_mm` | 43.18 | derived/shop |  |
| `sweep_mm` | 20.32 | derived/shop |  |
| `fin_thickness_mm` | 12 | derived/shop |  |
| `fin_tip_thickness_mm` | 6 | derived/shop |  |
| `te_thickness_mm` | 0.84 | derived/shop |  |
| `root_fillet_r_mm` | 6 | PROPOSED | rev 6: 4 -> 6 mm at the ANSYS failure site (root fillet); larger collides with the sleeve bore geometry |
| `te_root_thickness_mm` | 2 | PROPOSED | rev 6: blunt TE at the root (aft end = ANSYS crack origin), tapering to 2 outer lines (0.84) at the tip |
| `root_fillet_sections` | 6 | PROPOSED |  |
| `airfoil_points` | 41 | PROPOSED |  |
| `insert_hole_d_mm` | 4 | CITED | accu-components chart (motor.md) |
| `insert_depth_mm` | 5.7 | CITED | Prusa/CNC Kitchen M3 x 5.7 (motor.md) |
| `boss_wall_mm` | 2.67 | derived/shop |  |
| `insert_radius_mm` | 25.398 | derived/shop |  |
| `boss_fairing_length_mm` | 20 | PROPOSED |  |
| `target_mass_g` | 84.83 | OWNER | owner 2026-11-21: Bambu Studio slicer 84.83 g for rev 6 at 25 % GYROID infill (88.43 g at 25 % grid/50 %; rev 5 was 80 g) |
| `washer_min_od_mm` | 13.795 | derived/shop |  |

## Not print-ready until resolved
- `motor_case_od_mm`: 1.500 in nominal from AeroTech I500T (different 38 mm DMS) page, via motor agent; MEASURE the H100W
- `thrust_ring_od_mm`: not published yet (motor agent researching); must be > lip bore to bear
- `thrust_ring_thk_mm`: not published; mating check only
- `tube_od_mm`: BT-1.52 OD nominal; MEASURE — sets the sleeve bore

## Extra outputs
- `fin_can_md_rev6_airfoil_root.dat`
- `fin_can_md_rev6_airfoil_tip.dat`
- `fin_can_md_rev6_fin_only.step`
