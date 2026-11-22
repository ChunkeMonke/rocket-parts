# fin_can_md_rev8 — spec sheet

**Generated:** 2026-11-22 · `python make.py fin_can_md --rev 8`
**Status:** DRAFT — NOT PRINT-READY (placeholders/open items below)

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=96215.1 mm3, bodies=1 |
| 2 | mass | FAIL | target 90.0 g (±5 %); reachable 98.4 g (0 %) – 122.3 g (100 %); infill to hit target = -35.3 % |
| 3 | mating interference | PASS | tube_wall: 0.000 mm3, motor_case: 0.000 mm3, motor_thrust_ring: 0.000 mm3, tail_cone: 0.000 mm3 |
| 4 | renders | PASS | written: fin_can_md_rev8_iso.png, fin_can_md_rev8_front.png, fin_can_md_rev8_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 102.6 / Y 118.4 / Z 138.5 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 77.50 cm³ · infill region 18.78 cm³ · mesh volume 96.22 cm³
- Mass at 0 % / 100 % infill: 98.4 g / 122.3 g · target 90.0 g · infill needed: -35.3 %

## Print orientation
Aft face (lip) DOWN on the bed, axis vertical. No supports: lip and sleeve are vertical walls, fins shrink going up, the forward fairing narrows going up. REV 8 (tail_cone): the collar is on the bed and the fins' blunt trailing edges (1-8 mm wide) hang 12 mm above it: add small supports under the three fin TEs only (paint-on / tree, build plate only).

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
| `thrust_ring_thk_mm` | 9.525 | PLACEHOLDER | 3/8 in: Rocketry Forum estimate for 38 mm DMS thrust rings (no official AeroTech drawing found, 2026-11-22); owner photo agrees (long black aft band). Nozzle reported flush with the ring bottom. MEASURE |
| `fin_count` | 3 | derived/shop |  |
| `root_chord_mm` | 50 | derived/shop |  |
| `tip_chord_mm` | 30 | derived/shop |  |
| `span_mm` | 43.18 | derived/shop |  |
| `sweep_mm` | 20.32 | derived/shop |  |
| `fin_thickness_mm` | 12 | derived/shop |  |
| `fin_tip_thickness_mm` | 6 | derived/shop |  |
| `te_thickness_mm` | 0.84 | derived/shop |  |
| `root_fillet_r_mm` | 6 | PROPOSED | rev 6: 4 -> 6 mm at the ANSYS failure site (root fillet); larger collides with the sleeve bore geometry |
| `te_root_thickness_mm` | 8 | PROPOSED | rev 7: blunt TE 8 mm at the root (was 2.0 in rev 6) so the aft root envelops the insert boss; both FEA peaks sat in the boss outer wall near the TE (fea_results.md). Tapers to 0.84 at the tip |
| `root_fillet_sections` | 6 | PROPOSED |  |
| `airfoil_points` | 41 | PROPOSED |  |
| `insert_hole_d_mm` | 4 | CITED | accu-components chart (motor.md) |
| `insert_depth_mm` | 5.7 | CITED | Prusa/CNC Kitchen M3 x 5.7 (motor.md) |
| `boss_wall_mm` | 2.67 | derived/shop |  |
| `boss_extra_wall_mm` | 1 | PROPOSED | rev 7: +1 mm around the insert boss (wall 2.67 -> 3.67 mm) where the in-house FEA peaks sit |
| `insert_radius_mm` | 25.398 | derived/shop |  |
| `boss_fairing_length_mm` | 20 | PROPOSED |  |
| `target_mass_g` | 90 | OWNER | owner 2026-11-21: Bambu Studio slicer 90 g for REV 7 at 25 % GYROID infill (rev 6 was 84.83 g; rev 5 80 g) |
| `tail_cone` | True | OWNER | rev 8: threaded collar behind the aft face + separate tail cone (parts/tail_cone.py) |
| `collar_length_mm` | 18.5 | PROPOSED | rev 8 (updated 2026-11-22): 9.5 mm thrust ring + 6.5 mm thread + 2.5 mm run-out. Was 12 (3 mm ring assumption) -> no thread left with a 9.5 mm ring |
| `collar_bore_d_mm` | 41.6 | PROPOSED | rev 8: clears the 41.0 mm thrust ring (PLACEHOLDER) by 0.3/side; thread minor dia; wall behind the groove 1.6 mm |
| `boattail_length_mm` | 20 | OWNER | owner 2026-11-22: 20 mm taper aft of the collar |
| `boattail_end_od_mm` | 43 | PROPOSED | 46.8 -> 43.0 over 20 mm = 5.4 deg half-angle (attached-flow boattail range 5-10 deg) |
| `tail_cone_bore_d_mm` | 38.6 | PROPOSED | clears the 38.10 case/nozzle; shank face bears on the thrust ring annulus 38.6-41.0 |
| `thread_pitch_mm` | 2.5 | PROPOSED | printed 45-deg trapezoid thread, same as the nose cone cap |
| `thread_depth_mm` | 1 | PROPOSED |  |
| `thread_clearance_mm` | 0.2 | PROPOSED | same as the nose cap (owner to test-fit) |
| `te_gusset_mm` | 4 | PROPOSED | rev 8: 45-deg wedge under each fin root TE onto the collar; removes the 90-deg corner where rev 8 FEA peaked (FI 0.46 at r 22.8, z 0) |
| `washer_min_od_mm` | 13.795 | derived/shop |  |

## Not print-ready until resolved
- `motor_case_od_mm`: 1.500 in nominal from AeroTech I500T (different 38 mm DMS) page, via motor agent; MEASURE the H100W
- `thrust_ring_od_mm`: not published yet (motor agent researching); must be > lip bore to bear
- `thrust_ring_thk_mm`: 3/8 in: Rocketry Forum estimate for 38 mm DMS thrust rings (no official AeroTech drawing found, 2026-11-22); owner photo agrees (long black aft band). Nozzle reported flush with the ring bottom. MEASURE
- `tube_od_mm`: BT-1.52 OD nominal; MEASURE — sets the sleeve bore

## Extra outputs
- `fin_can_md_rev8_airfoil_root.dat`
- `fin_can_md_rev8_airfoil_tip.dat`
- `fin_can_md_rev8_fin_only.step`
