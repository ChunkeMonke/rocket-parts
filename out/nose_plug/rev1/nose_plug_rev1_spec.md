# nose_plug_rev1 — spec sheet

**Generated:** 2026-11-22 · `python make.py nose_plug --rev 1`
**Status:** AUTO CHECKS PASS — pending visual review

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=2894.9 mm3, bodies=1 |
| 2 | mass | PASS | target 3.0 g (±5 %); reachable 2.1 g (0 %) – 3.6 g (100 %); infill to hit target = 58.0 % |
| 3 | mating interference | PASS | nose_cone: 0.000 mm3 |
| 4 | renders | PASS | written: nose_plug_rev1_iso.png, nose_plug_rev1_front.png, nose_plug_rev1_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 23.0 / Y 23.0 / Z 8.5 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 1.66 cm³ · infill region 1.21 cm³ · mesh volume 2.89 cm³
- Mass at 0 % / 100 % infill: 2.1 g / 3.6 g · target 3.0 g · infill needed: 58.0 %

## Print orientation
Head on the bed (screwdriver slot down), threaded shank up. No supports.

## Loads vs. layers
- Ballast inertia pushes aft on the plug; the thread carries it to the bulkhead.

## Parameters
| Parameter | Value | Status | Source / note |
|---|---|---|---|
| `length_mm` | 165 | derived/shop |  |
| `base_od_mm` | 41.275 | derived/shop |  |
| `shoulder_length_mm` | 40 | derived/shop |  |
| `shoulder_od_mm` | 38.555 | derived/shop |  |
| `wall_thickness_mm` | 2.2 | derived/shop |  |
| `ballast_bulkhead_from_tip_mm` | 100 | derived/shop |  |
| `ballast_bulkhead_thickness_mm` | 6 | derived/shop |  |
| `plug_bore_d_mm` | 20 | derived/shop |  |
| `plug_head_d_mm` | 23 | derived/shop |  |
| `plug_head_thickness_mm` | 3 | derived/shop |  |
| `plug_slot_width_mm` | 2 | derived/shop |  |
| `plug_slot_depth_mm` | 1.5 | derived/shop |  |
| `cap_bore_d_mm` | 30 | derived/shop |  |
| `cap_ring_height_mm` | 15 | derived/shop |  |
| `cap_flange_thickness_mm` | 3 | derived/shop |  |
| `cap_shank_length_mm` | 12 | derived/shop |  |
| `cap_wall_mm` | 3 | derived/shop |  |
| `kevlar_hole_d_mm` | 5 | derived/shop |  |
| `kevlar_hole_spacing_mm` | 12 | derived/shop |  |
| `thread_pitch_mm` | 2.5 | derived/shop |  |
| `thread_depth_mm` | 1 | derived/shop |  |
| `thread_clearance_mm` | 0.2 | derived/shop |  |
| `ogive_points` | 60 | derived/shop |  |
| `tip_flat_r_mm` | 0.42 | derived/shop |  |
| `target_mass_g` | 3 | derived/shop |  |
