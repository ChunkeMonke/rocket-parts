# l1-cheap — Fin Can Design Proposal (one-piece PETG)

**Status:** concept + parameter signature, awaiting owner review. No geometry written yet.

## What it does (one part, five jobs)
1. **Fin can:** 3 integral fins with a selectable airfoil section and root fillets.
2. **Motor mount / inner tube:** a 29 mm bore that supports the full motor length.
3. **Centering rings:** webs/rings that join the inner tube to the outer shoulder wall.
4. **Thrust stop + retainer:** the aft face takes the motor's thrust ring; 2× M3 heat-set inserts with screws and washers clamp the ring.
5. **Airframe joint:** a shoulder epoxied into the BT-1.52, with the exposed OD flush to the tube OD so there's no step in the airflow.

## Section (axis vertical, as printed: aft face on the bed)

```
                 ┌──┐        ┌──┐   ← shoulder top (fwd end), inside the BT-1.52
  shoulder ──▶   │  │ ░░░░░░ │  │      Kevlar anchor loop, off-axis (out of the ejection gas path)
  (in tube)      │  │ ░bore░ │  │   ← centering ring / webs (fwd)
                 │  │ ░░░░░░ │  │
 ════tube════════╡  │ ░░░░░░ │  ╞═══════tube══════  ← flush butt joint: exposed OD = tube OD
                 │  │ ░░░░░░ │  │╲
  exposed ──▶    │  │ ░░░░░░ │  │ ╲  fin (airfoil section in each layer)
  (fin root)     │  │ ░░░░░░ │  │  ╲ root fillet blends the fin into the body
                 │  └─┐░░░░┌─┘  │   │
                 └────┘ ░░ └────┘───┘ ← aft face = thrust face; M3 inserts around the bore
                        motor thrust ring bears here
```

## Proposed parameter signature (`parts/fin_can.py: build(**params)`)

Every value comes from `design.yaml`, shop constants, or the owner; none are written into the code. ❓ marks values the owner hasn't given yet.

| Group | Parameter | Unit | Value / source |
|---|---|---|---|
| Airframe | `body_od_mm` | mm | ❓ measured tube OD (nominal 41.275 until measured) |
| | `shoulder_od_mm` | mm | ❓ fit choice from `fits_in_tube`: press 38.615 or slip 38.555 (epoxy gap) |
| | `shoulder_length_mm` | mm | ❓ stability assumed 103 (= motor 203 − exposed 100) |
| | `shoulder_wall_mm` | mm | ❓ |
| | `exposed_length_mm` | mm | 100 = fin root chord (aero) |
| Motor mount | `motor_od_mm` | mm | ❓ **unmeasured** |
| | `bore_clearance_mm` | mm, diametral | ❓ |
| | `inner_wall_mm` | mm | ❓ |
| | `thrust_ring_od_mm`, `thrust_ring_thk_mm` | mm | ❓ **unmeasured**; sets the aft-face counterbore |
| | `centering`: `rings` or `webs`, count, thickness | –, mm | ❓ |
| Retention | `insert_hole_d_mm`, `insert_depth_mm` | mm | 4.0 / 5.7 (motor.md, cited) |
| | `insert_count`, `insert_radius_mm` | –, mm | 2 / ❓ outside the thrust ring |
| Fins | `fin_count`, `root_chord_mm`, `tip_chord_mm`, `span_mm`, `sweep_mm` | –, mm | 3 / 100 / 40 / 40 / 60 (aero) |
| | `airfoil` | – | ❓ `flat_rounded` or `naca00xx` |
| | `fin_thickness_mm` or `t_over_c` | mm or – | ❓ constant thickness (5 mm) vs constant t/c |
| | `root_fillet_r_mm` | mm | ❓ |
| Aft | `boattail_length_mm`, `boattail_aft_od_mm` | mm | ❓ (0 = no boattail) |
| Recovery | `anchor`: `printed_loop` or `kevlar_leader`; `cord_d_mm` | –, mm | ❓ / 2.3 (owner Kevlar) |
| | `anchor_min_net_area_mm2` | mm² | 48 at ≤20 m/s deploy (sim: 7.2 m/s at 12 s delay) |
| Mass | `target_mass_g` | g | 197.3 (stability; ESTIMATE) |

Print: aft face down, height = exposed + shoulder ≈ 203 mm ≤ 256. Fin outlines get smaller going up, so there are no overhangs and no supports. Fin root bending runs within the layers.

## Outputs for ANSYS
`make.py fin_can` also writes:
- `fin_airfoil.dat`: Selig-format section coordinates (root and tip), loadable in Fluent, XFOIL, or SpaceClaim/DesignModeler as a curve.
- `fin_can_fin_only.step`: one fin with its fillet, for a 3D fin study.

## Risks to resolve
- **Motor fit:** the bore and thrust-face counterbore need the real motor dimensions. The motor is planned as a launch-day field purchase, so it won't be in hand before printing.
- **Heat:** the ejection charge fires about 12 s after burnout, while the case is hot. The PETG around the bore and inserts softens near ~80 °C (glass transition). A paper liner or a thicker inner wall would help. To check: the DMS case temperature.
- **Flutter:** PETG shear modulus G is still TBD (aero).
- **verify.py doesn't exist yet.** It must be built before this part can be called good (owner rule).
