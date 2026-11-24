# kevlar_bulkhead_rev1 — spec sheet

**Generated:** 2026-11-24 · `python make.py kevlar_bulkhead --rev 1`
**Status:** AUTO CHECKS PASS — pending visual review

## Verify checks
| # | Check | Result | Detail |
|---|---|---|---|
| 1 | mesh integrity | PASS | watertight=True, winding_consistent=True, volume=11959.4 mm3, bodies=1 |
| 2 | mass | PASS | target 15.2 g (±5 %); reachable 13.7 g (0 %) – 15.2 g (100 %); infill to hit target = 101.8 % |
| 3 | mating interference | PASS | body_tube: 0.000 mm3 |
| 4 | renders | PASS | written: kevlar_bulkhead_rev1_iso.png, kevlar_bulkhead_rev1_front.png, kevlar_bulkhead_rev1_section.png — VISUAL REVIEW REQUIRED |
| 5 | build volume | PASS | extents X 38.6 / Y 38.5 / Z 26.0 mm vs limit 256/256/256 |

## Mass (walls + infill model)
- Wall band 2.67 mm · top 5 / bottom 3 layers of 0.2 mm
- Solid (walls/skins) 10.77 cm³ · infill region 1.18 cm³ · mesh volume 11.96 cm³
- Mass at 0 % / 100 % infill: 13.7 g / 15.2 g · target 15.2 g · infill needed: 101.8 %

## Print orientation
Aft face (z = 0) on the bed, axis vertical. No supports: the forward plate bridges about 13 mm between the pillar and the wall. 0.20 mm layers, 6 walls (fully solid).

## Loads vs. layers
- Kevlar snatch load (axial, forward): ≤ 686 N at 20 m/s separation (recovery analysis); 343 N at 10 m/s.
- Path: cord bears on the underside of the forward plate around the pillar; the pillar shares it with the aft plate. Plate bending is in-plane (within layers). Pillar-to-aft-plate joint is across layers (tension).
- Bond: epoxy shear on the outer surface, 3153 mm²; at 1 MPa (paper-ply limit, conservative) capacity ≈ 3.1 kN.
- Ejection pressure acts on both plates; the vents relieve it.

## Parameters
| Parameter | Value | Status | Source / note |
|---|---|---|---|
| `od_mm` | 38.555 | derived/shop |  |
| `wall_mm` | 2 | derived/shop |  |
| `length_mm` | 26 | derived/shop |  |
| `aft_plate_mm` | 3 | derived/shop |  |
| `gap_mm` | 9 | derived/shop |  |
| `fwd_plate_mm` | 5 | derived/shop |  |
| `pillar_d_mm` | 8 | derived/shop |  |
| `install_fwd_face_from_tip_mm` | 340 | derived/shop |  |
| `tube_id_mm` | 38.735 | derived/shop |  |
| `tube_od_mm` | 41.275 | derived/shop |  |
| `aft_vent_d_mm` | 7 | derived/shop |  |
| `aft_vent_r_mm` | 11.5 | derived/shop |  |
| `fwd_vent_d_mm` | 6 | derived/shop |  |
| `fwd_vent_r_mm` | 12.5 | derived/shop |  |
| `kevlar_hole_d_mm` | 5 | derived/shop |  |
| `kevlar_hole_spacing_mm` | 14 | derived/shop |  |
| `groove_w_mm` | 1.5 | derived/shop |  |
| `groove_depth_mm` | 0.5 | derived/shop |  |
| `chamfer_mm` | 0.8 | derived/shop |  |
| `target_mass_g` | 15.2 | derived/shop |  |
