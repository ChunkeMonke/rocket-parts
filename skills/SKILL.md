---
name: rocket-parts
description: Shop rules for generating, verifying and printing parametric model-rocket parts (LOC 38 mm min-diameter HPR, PETG on a Bambu P1S). Load before writing or editing anything in parts/, make.py or verify.py.
---

# Rocket Parts — Shop Rules

## How this file is used

The YAML block below is the **single source of truth** for every house constant.
`parts/shop.py` parses it at runtime, so edit the numbers here and every part
and every verify check picks up the change on the next run. Never copy a
constant into part code.

- All lengths in **mm**, masses in **g**, forces in **N**, stresses in **MPa**,
  temperatures in **°C**. Inch values are kept only as the source of truth
  they came from; code uses the mm field.
- A value of `TBD` is a constant the owner has not given yet. Code that needs a
  `TBD` value must **stop and raise**, never substitute a guess.

```yaml shop-constants
airframe:
  loc_38mm_paper:
    id_nominal_in: 1.525
    od_nominal_in: 1.625
    id_nominal_mm: 38.735      # = 1.525 in
    od_nominal_mm: 41.275      # = 1.625 in
    id_measured_mm: 38.735     # use THIS for fits
    od_measured_mm: TBD       # none yet — measure before any part that fits OVER the tube (fin jig)

fits_in_tube:                  # per side, applied to id_measured_mm
  sign_convention: clearance   # modelled part is SMALLER than tube ID; print over-size makes it press/slip
  press_mm_per_side: 0.06
  snug_slip_mm_per_side: 0.09

material:
  petg:
    density_g_cm3: 1.27
    interlayer_shear_mpa: 15   # approximate; the weak direction

print_profile_petg:
  nozzle_temp_c: [245, 250]
  bed_temp_c: 75
  bed_adhesion: glue stick
  build_plate: TBD
  part_cooling_fan_pct: [30, 40]
  layer_height_mm: 0.16
  elephant_foot_comp_mm: 0.15
  seam_position: Back
  nozzle_diameter_mm: 0.4      # P1S stock
  wall_loops: 4                # Bambu Studio Strength tab
  # infill % is NOT fixed here: verify.py solves it per part from the target mass

printer:
  bambu_p1s:
    max_z_mm: 256              # HARD constraint, checked on every part
    max_x_mm: 256              # HARD constraint
    max_y_mm: 256              # HARD constraint

motors:
  aerotech_i175ws_13a:
    diameter_class_mm: 38      # class, not a measured case OD
    case_od_mm: TBD            # needed for motor-OD interference checks; no published value found — measure the case
    case_hardware: TBD         # which RMS case you fly it in
    length_mm: 214
    loaded_mass_g: 348
    propellant_mass_g: 168
    avg_thrust_n: 175

mating:
  rail_guide:
    rail_size: TBD             # 1010 or 1515 — set by the launch club's pads; ask them
    slot_geometry: TBD

verify:
  mass_tolerance_pct: 5        # +/- around declared target mass (provisional)
  mass_basis: walls_plus_infill  # shell (walls + top/bottom) solid, interior at infill_pct
  top_layers: TBD              # Bambu Studio Strength tab -> top shell layers
  bottom_layers: TBD           # Bambu Studio Strength tab -> bottom shell layers
  # target mass per part comes from the OpenRocket design or the build planner;
  # verify reports the infill % needed to hit it and fails if it is outside 0-100 %.
```

## Hard rules

1. **Ask before assuming a dimension.** If a part needs a number that is not
   in this file or in the user's request, stop and ask. Do not "use a typical
   value".
2. **No magic numbers in geometry code.** Every part module takes explicit
   parameters, each documented with its unit in the docstring. Shop
   constants come from `parts/shop.py`, never literals.
3. **Every generated part is verified.** `make.py` always runs `verify.py`.
   A part is not "done", "good" or "ready to print" unless every check passes,
   including the renders having been opened and looked at.
4. **X, Y, Z ≤ the printer.bambu_p1s limits in the chosen print orientation.** Check
   this on every part, no exceptions. If it fails, reorient or split the part
   — never shrink it silently.
5. **State the load path through the layers.** For every structural part,
   the spec sheet says which way each primary load crosses the layer planes
   (along Z = across layers, in XY = within layers) and whether it loads
   the interlayer bond in shear, tension or compression. Interlayer shear
   ≈ `material.petg.interlayer_shear_mpa`; prefer orientations that keep the
   main load in compression or within layers.
6. **Fits are applied to the measured tube ID**, not nominal, using the
   per-side values in `fits_in_tube`.
7. **Zero interference with declared mating geometry** (tube ID, motor OD,
   rail slot). Any non-zero intersection volume is a failure.

## Verify checks (verify.py)

| # | Check | Pass condition |
|---|-------|----------------|
| 1 | Mesh integrity (trimesh) | watertight, manifold, exactly one body |
| 2 | Mass | (shell volume + interior × infill) × `material.petg.density_g_cm3` within `verify.mass_tolerance_pct` of the declared target; also reports the infill % that would hit target |
| 3 | Mating interference | boolean intersection with each declared mating solid = 0 mm³ |
| 4 | Renders | iso, front and axial-section PNGs written to `out/` and visually inspected |
| 5 | Build volume | bounding box in print orientation ≤ `printer.bambu_p1s` max X/Y/Z |

## Output layout

Each run writes to `out/<part>/rev<N>/`:
`<part>_rev<N>.step`, `.stl`, `_iso.png`, `_front.png`, `_section.png`,
`_spec.md` (params with units, mass, print orientation, load-vs-layer
statement, and the pass/fail of each verify check).

## Print setup (PETG, P1S)

Nozzle 245–250 °C · bed 75 °C + glue stick · fan 30–40 % · 0.16 mm layers ·
elephant-foot compensation 0.15 mm · seam Back. Values above in the YAML are
authoritative; this line is a human summary.
