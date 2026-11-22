# nose_cone_rev1 — spec sheet

**Generated:** 2026-11-22 · `python make.py nose_cone --rev 1`
**Status:** FAILED VERIFY

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=49139.3 mm3, bodies=1 |
| 2 | mass | FAIL | target 52.7 g (±5 %); reachable 61.2 g (0 %) – 62.4 g (100 %); infill to hit target = -716.6 % |
| 3 | mating interference | PASS | tube_wall: 0.000 mm3, bottom_cap: 0.000 mm3, ballast_plug: 0.000 mm3 |
| 4 | renders | PASS | written: nose_cone_rev1_iso.png, nose_cone_rev1_front.png, nose_cone_rev1_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 41.3 / Y 41.3 / Z 203.3 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 48.20 cm³ · infill region 0.94 cm³ · mesh volume 49.14 cm³
- Mass at 0 % / 100 % infill: 61.2 g / 62.4 g · target 52.7 g · infill needed: -716.6 %

## Print orientation
TIP UP, shoulder's aft face on the bed. No supports: the ballast bulkhead's underside is a 45° cone, the thread ring top is an up-facing ledge, thread flanks are 45°.

## Loads vs. layers
- Recovery snatch: the Kevlar pulls the cap aft (-Z); the cap thread shears the ring across layers (about pi x 30 x 15 x 0.5 = 700 mm2 x 15 MPa = ~10 kN), then the shoulder wall carries it forward in Z tension across layers (251 mm2, 15 MPa reference -> 3.77 kN, nosecone.md section 4). Wall is the weak link.
- Ballast at landing/deploy: pushes the plug forward... no: inertia pushes ballast AFT onto the bulkhead (+plug) in compression/bending within layers; the bulkhead's 45° cone carries it to the wall.

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
| `target_mass_g` | 52.7 | derived/shop |  |
