# kevlar_bulkhead_rev2 — spec sheet

**Generated:** 2026-11-24 · `python make.py kevlar_bulkhead --rev 2`
**Status:** AUTO CHECKS PASS — pending visual review

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=12037.1 mm3, bodies=1 |
| 2 | mass | PASS | target 15.0 g (±5 %); reachable 13.2 g (0 %) – 15.3 g (100 %); infill to hit target = 87.0 % |
| 3 | mating interference | PASS | body_tube: 0.000 mm3 |
| 4 | renders | PASS | written: kevlar_bulkhead_rev2_iso.png, kevlar_bulkhead_rev2_front.png, kevlar_bulkhead_rev2_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 38.6 / Y 38.5 / Z 24.0 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 10.37 cm³ · infill region 1.65 cm³ · mesh volume 12.04 cm³
- Mass at 0 % / 100 % infill: 13.2 g / 15.3 g · target 15.0 g · infill needed: 87.0 %

## Print orientation
Aft face (z = 0) on the bed, axis vertical, NO supports: the eye tunnel has a 45° diamond roof and there is no enclosed cavity. 0.20 mm layers, 6 walls.

## Loads vs. layers
- Kevlar snatch load (axial, forward): ≤ 686 N at 20 m/s separation (recovery analysis); 343 N at 10 m/s.
- Eye bar: 6 mm span, 6 mm deep above the apex, 12 mm long; bending ≈ 14 MPa at 686 N, within layers.
- Eye posts: 2 × 5 × 12 mm = 120 mm² in tension ACROSS layers: 5.7 MPa at 686 N (PETG interlayer ≈ 15–20 MPa).
- Plate: 6 mm, in-plane bending ≈ 10 MPa at 686 N. Bond: epoxy shear on ≈ 2900 mm² ≈ 2.9 kN at 1 MPa.

## Parameters
| Parameter | Value | Status | Source / note |
|---|---|---|---|
| `od_mm` | 38.555 | derived/shop |  |
| `wall_mm` | 2 | derived/shop |  |
| `length_mm` | 24 | derived/shop |  |
| `plate_mm` | 6 | derived/shop |  |
| `eye_tunnel_w_mm` | 6 | derived/shop |  |
| `eye_tunnel_h_mm` | 6 | derived/shop |  |
| `eye_bar_mm` | 6 | derived/shop |  |
| `eye_post_mm` | 5 | derived/shop |  |
| `eye_length_mm` | 12 | derived/shop |  |
| `install_fwd_face_from_tip_mm` | 340 | derived/shop |  |
| `tube_id_mm` | 38.735 | derived/shop |  |
| `tube_od_mm` | 41.275 | derived/shop |  |
| `vent_d_mm` | 6.5 | derived/shop |  |
| `vent_r_mm` | 12.25 | derived/shop |  |
| `groove_w_mm` | 1.5 | derived/shop |  |
| `groove_depth_mm` | 0.5 | derived/shop |  |
| `chamfer_mm` | 0.8 | derived/shop |  |
| `edge_break_mm` | 1 | derived/shop |  |
| `target_mass_g` | 15 | derived/shop |  |
