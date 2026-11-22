# nose_cap_rev1 — spec sheet

**Generated:** 2026-11-22 · `python make.py nose_cap --rev 1`
**Status:** FAILED VERIFY

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=6663.7 mm3, bodies=1 |
| 2 | mass | FAIL | target 10.0 g (±5 %); reachable 6.9 g (0 %) – 8.5 g (100 %); infill to hit target = 198.6 % |
| 3 | mating interference | PASS | nose_cone: 0.000 mm3 |
| 4 | renders | PASS | written: nose_cap_rev1_iso.png, nose_cap_rev1_front.png, nose_cap_rev1_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 38.6 / Y 38.5 / Z 15.0 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 5.44 cm³ · infill region 1.23 cm³ · mesh volume 6.66 cm³
- Mass at 0 % / 100 % infill: 6.9 g / 8.5 g · target 10.0 g · infill needed: 198.6 %

## Print orientation
Flange on the bed, threaded shank up. No supports (45° thread flanks).

## Loads vs. layers
- Snatch: Kevlar pulls the floor web aft; the floor bends within its layers; the thread carries it to the nose ring.

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
| `target_mass_g` | 10 | derived/shop |  |
