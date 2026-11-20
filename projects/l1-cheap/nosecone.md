# Project: l1-cheap — Phase 2 Nose cone

**Status:** Phase 2 proposal, 2026-11-20. Owner review pending. `parts/nose_cone.py` is **not** written
yet; its signature is the owner's Step 4 review.
Estimate script (scratch, not a part module):
`/tmp/claude-0/-home-user/c895d01b-a099-5773-be20-859042f2dc61/scratchpad/nose_est.py`. It reads every
constant through `parts/shop.py`. CadQuery volume 43 690 mm³ against 43 686 mm³ from the numeric
integration, a 0.01 % difference.

## 1. Shape and length

| Item | Value | Source / reason |
|---|---|---|
| Shape | **Tangent ogive** | See below |
| Base OD | 41.275 mm | Tube OD **nominal**. `od_measured_mm` is TBD; measure it and re-set the base OD so the step is flush |
| Exposed length L | **165 mm** | Design choice: fineness 165 / 41.275 = **4.0** |
| Tip | Solid for the first 9.2 mm, half-angle 14.3° | Calculated |

Why this shape and length:
- **Speed.** This is a light rocket on a 29 mm H, so I expect it to stay subsonic. `aero.max_velocity_m_s` is still TBD, so aero should confirm.
  - Below about Mach 0.8, ogive, von Kármán and elliptical noses all have very little pressure drag at fineness ≥ 3. Skin friction dominates, so a longer nose mostly adds friction and mass.
  - Von Kármán only pays off transonic. Its tip is blunt (dy/dx → ∞ at x = 0), which prints poorly tip-up.
- **Printability.** The ogive's tip is sharp and the wall is tangent at the base, so the cone prints tip-up with no supports.
- **Why fineness 4.**
  - It is the middle of the usual 3–5 range.
  - Nose plus shoulder comes to 205 mm, which leaves 51 mm of Z margin.
  - A 5:1 nose (206 + 40 = 246 mm) would still fit if aero asks for one.

## 2. Shoulder

| Item | Value | Source |
|---|---|---|
| OD | **38.555 mm** | id_measured 38.735 − 2 × snug_slip 0.09 (`fits_in_tube`) |
| Length | **40 mm** | Design choice of about 1 tube caliber. This is the common "shoulder ≥ 1 diameter" rule of thumb, not a cited source; owner to accept |
| Wall | 2.2 mm (ID 34.155 mm) | Same as the cone |
| Shoulder-to-cone junction | 45° inner chamfer from ID 34.16 to 36.88 mm | The shoulder and cone walls overlap by only 0.84 mm radially, so the chamfer gives the load a continuous path |
| Interference with tube ID | **0** by construction (0.09 mm per side clearance) | verify check 3 in Step 6 |

## 3. Wall thickness and mass (walls + infill model)

The crust is 0.42 mm (outer wall) + 5 × 0.45 mm (inner walls) = **2.67 mm per perimeter**.
- In a tip-up print, every layer of the cone is a ring with two perimeters: the outside and the hole.
- Any section narrower than 2 × 2.67 = **5.34 mm** is therefore all wall lines, so **infill has no effect there**.
- The cone's horizontal wall thickness is at most 2.26 mm, the junction about 3.6 mm and the solid tip under 2.3 mm in radius. **All of these are solid.**

I chose a **2.2 mm** wall: 2 outer lines (0.42) + 3 inner lines (0.45) = 2.19 mm, which avoids gap fill.

The only place infill matters is the core of the **5 mm aft bulkhead**:
- Thickness: 5 − 0.6 bottom shell − 1.0 top shell = 3.4 mm.
- Radius: 19.28 − 2.67 = 16.6 mm.
- Volume: 2.95 cm³.

| Infill in bulkhead core | Mass (ESTIMATE) | CG from tip |
|---|---|---|
| 0 % | 51.7 g | 118.4 mm |
| 25 % (profile default) | **52.7 g** | **119.9 mm** |
| 100 % | 55.5 g | 124.1 mm |

The method:
1. Revolve the ogive profile and its 2.2 mm normal offset.
2. Add the shoulder, the chamfer and the bulkhead.
3. Mass = (solid volume + core volume × infill) × 1.27 g/cm³.

The cord holes and fill port are not subtracted, so the mass reads slightly high.

## 4. Shock-cord attachment

**Concept.** An **integral aft bulkhead**, 5 mm thick, closes the shoulder end and is printed first, on the bed.
- Two holes through it form a strap; the Kevlar passes up one hole, over the web and down the other.
- A third hole is a ballast fill port, plugged after filling.
- Hole sizes are **TBD** until the Kevlar diameter is known.

**Load path, printed tip-up.** The snatch load pulls the strap aft, along −Z.
1. **Web.** The web bends in-plane, so the fibre stress runs along the layers. The transverse shear puts some shear on the interlayer planes.
2. **Bulkhead to wall.** The load passes through a vertical cylindrical interface of π × 34.16 × 5 = 537 mm². That is within-layer fused material.
3. **Shoulder wall (the weak link).** The load runs forward through the wall to the nose mass in **Z tension across the layers**. The annulus is 251 mm², so 15 MPa is reached at **3.77 kN**.
   - 15 MPa is the shop's interlayer *shear* figure. The shop constants have no interlayer tension value, so it is used here only as a reference.

**Load: TBD.** Recovery's *estimate* is 343 N opening load, and it proposes a 1030 N cord rating.
- At 343 N the wall stress is 1.4 MPa; at 1030 N it is 4.1 MPa.
- Neither is a verified load; recovery has to size the snatch load before the check is final.

**Alternative.** Anchor the cord near the forward end, so the wall behind the anchor is pushed in compression. It is harder to thread and print, and it conflicts with the ballast cavity, so I am not proposing it unless the load turns out high.

## 5. Ballast cavity (if stability asks)

The cavity is the interior forward of the shoulder, filled tip-down through the bulkhead port.

| Filled from tip to | Volume | CG of fill from tip |
|---|---|---|
| 60 mm | 6.0 cm³ | 46.5 mm |
| 80 mm | 14.6 cm³ | 60.8 mm |
| 100 mm | 27.2 cm³ | 74.6 mm |
| 120 mm | 43.6 cm³ | 88.0 mm |
| 165 mm (whole cone) | 89.1 cm³ | 116.2 mm |

Ballast mass = volume × the packed density of the chosen material. The material and its packing are **TBD**; owner to choose.

## 6. Print orientation and build volume

- **Orientation:** tip up, with the aft bulkhead on the bed.
  - The tip needs no support, and the bulkhead prints as the first layers.
  - The only overhang is the 1.36 mm flat ledge where the shoulder steps out to the base OD. It is unsupported; I expect it to print acceptably (judgement, not tested).
- **Bounding box:** 41.3 × 41.3 × 205 mm, inside 256 × 256 × 256. **No split needed.**
- **Elephant-foot compensation** (0.15 mm) applies to the aft end of the shoulder.

## 7. Open questions for the owner
1. Measure the tube OD. The base OD should match it, not the nominal value.
2. Accept the 40 mm shoulder, the 4.0 fineness and the 2.2 mm wall?
3. What is the Kevlar diameter? It sets the strap-hole size.
4. If ballast is needed, what material and form?

## 8. Hand-offs
- **Stability:** nose mass 52.7 g (estimate), CG 119.9 mm from the tip, length 165 mm plus a 40 mm shoulder inside the tube. The ballast table is in §5.
- **Aerodynamics:** tangent ogive, L = 165 mm, base OD 41.275 mm. Confirm the flight is subsonic.
- **Recovery:** send the snatch load and Kevlar diameter. The wall reaches 15 MPa at 3.77 kN.
