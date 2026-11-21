# l1-cheap — Design & Research Report
_Last updated: 2026-11-21 · b0dd66b_

> Living document, maintained by the `rocket-docs` agent. Every number is copied from a project source and cited inline. Labels ESTIMATE / PLACEHOLDER / PROPOSED / TBD are carried over from the sources.
>
> **2026-11-21: the motor changed to the H100W (38 mm, minimum-diameter).** All flight numbers (stability, mass budget, apogee, Mach, delay) are still from the 2026-11-20 run of `sims/l1_cheap.py --allow-tbd` for the **H182R and fin can rev 2**. They are marked **"H182R basis — superseded, re-sim pending"** and must not be used for the H100W rocket. Where sources disagree, both values are shown and the conflict is listed in §11.

---

## Briefing

**Goal:** Tripoli Level 1 certification flight, as cheaply as possible: **$100 cap including the motor**. Launch at **Palm Bay, FL, on 2026-12-14** (goal.md).

**Rocket at a glance**

| | |
|---|---|
| Motor | AeroTech **H100W-14A DMS, 38 mm**, owner 2026-11-21: 226.8 N·s, 97.7 N avg, 2.32 s, 261 g, **$54.99, HAZMAT** (design.yaml `motor`) |
| Layout | **Minimum-diameter.** The motor sits directly in the LOC BT-1.52 (ID 38.735 mm measured). The MMT-1.14 liner is dropped (motor.md) |
| Airframe | BT-1.52, 863 mm uncut; OD 41.275 mm nominal, **PLACEHOLDER** until measured |
| Nose | 165 mm tangent ogive in PETG, 52.7 g ESTIMATE. Ballast is **TBD** pending re-sim (90.5 g was the H182R figure) |
| Fin can | **Rev 3 DRAFT**: printed sleeve over the tube, OD 46.8 mm, 97.6–98.3 g. Verify **4 / 5** (check 2 FAIL: no target mass) |
| Recovery | Single deploy on motor ejection (PROPOSED), with the owned 40 in chute and 750 lb Kevlar. Owner drills the delay (UDDT); the setting is TBD |
| Payload | None |

**Key performance: H182R basis — superseded, re-sim pending.** The last sim (H182R, fin can rev 2) gave 1.80 cal at liftoff, a 1284 m apogee, M 0.829 and a 12 s delay (§6). **None of these apply to the H100W.** The H100W thrust curve (.eng) has not been uploaded yet.

**Phase status**

| 0 Goal | 1 Feasibility | 2 Design | 3 BOM | 4 Budget | 5 Schedule | 6 Parts | 7 Build | 8 Flight |
|---|---|---|---|---|---|---|---|---|
| done | done, Cond. GO | **reopened 2026-11-21 (motor change)** | needs update (motor, liner) | not started | — | fin can rev 3 DRAFT; nose not generated | — | — |

**Top risks**
1. **No H100W sim.** Without the .eng file, the ballast, margin, delay, apogee and rail-exit speed are all unknown.
2. **Min-diameter fit is unmeasured.** The case OD and thrust ring are unpublished; the 38.10 mm nominal leaves 0.64 mm clearance. The factory-glued ring carries all 137.8 N of thrust (AT 2014 advisory).
3. **Low thrust.** The 93.4–100 N average clears the forum's > 80 N L1 rule by only 13–20 N. Thrust-to-weight thresholds are TBD.

**Next steps**
- Owner: upload the ThrustCurve H100W_DMS file. Stability then re-sims and sets the ballast, delay and fin can target mass.
- Measure the tube OD and the motor (case OD ×3, ring OD and thickness, length). Then regenerate fin can rev 3.
- Owner: decide on the forward backup stop. Then design the aft Kevlar anchor (missing in rev 3).
- Update recovery, aero CP (sleeve) and the BOM, then start the Phase 4 budget.

---

## 1. Requirements & Constraints

### 1.1 Mission and owner constraints (goal.md, design.yaml `owner`, `motor`)

| Item | Value | Source |
|---|---|---|
| Certification | Tripoli L1 (member, uncertified); age 18+ confirmed | goal.md, feasibility.md §7 |
| Motor | Goal said "cheapest 29 mm H". **Owner changed this on 2026-11-21 to the AeroTech H100W-14A DMS, 38 mm** | goal.md; design.yaml `motor.designation` |
| Airframe | 38 mm class tube (LOC BT-1.52). **Minimum-diameter since 2026-11-21** | goal.md, feasibility.md §7, motor.md status |
| Printed parts | Fin can and nose cone, PETG, Bambu P1S | goal.md |
| Stability | Target 1.8 cal, band ±0.2 cal, **gated at liftoff only** | design.yaml `owner.stability_*` |
| Budget | $100 total incl. motor; 5 % contingency held back ($95 spendable) | design.yaml `owner`, feasibility.md §4 |
| Filament | $13/kg PETG | goal.md |
| Launch / deadline | Palm Bay, FL, 2026-12-14 (24 days from 2026-11-20); club/prefecture name TBD | goal.md |

- The owner wrote the stability band as "±2". It is read as ±0.2 cal (design.yaml `owner.stability_band_cal`; skills/build-planner/SKILL.md marks it "CONFIRM").
- design.yaml `owner.motor_class` still reads "29mm H", and goal.md and feasibility.md still say "not min-diameter" (§11).

### 1.2 Certification rules (feasibility.md §1, secondary sources; check tripoli.org/Level1 before buying)

| Requirement | H100W status (motor.md §B) |
|---|---|
| Single certified H or I motor, 160.01–640 N·s | 223.9–234 N·s, depending on source: pass |
| Average thrust > 80 N (forum claim only) | 93.4–100 N: pass, **but with only a 13–20 N margin** |
| Rocket built by the flyer | plan |
| Witnesses: 2× L1 or 1× L2/L3; form to the prefect before the flight | arrange at launch |
| Safe recovery; rocket flyable again | design for it |

### 1.3 Shop and printer constants (skills/SKILL.md)

| Constant | Value |
|---|---|
| BT-1.52 ID (measured = nominal) / OD nominal | 38.735 mm / 41.275 mm; `od_measured_mm` **TBD** |
| Fits in tube, per side | press 0.06 mm, snug-slip 0.09 mm |
| PETG density / interlayer shear | 1.27 g/cm³ / 15 MPa (approximate, weak direction) |
| Printer limit (P1S) | 256 × 256 × 256 mm, hard limit |
| Print profile | 0.2 mm layers; 6 wall loops (0.42 outer / 0.45 inner); 5 top / 3 bottom layers; elephant-foot comp. 0.15 mm |
| Verify mass tolerance | ±5 % (provisional) |
| Rail size | **TBD** (1010 or 1515, set by the club) |

---

## 2. Propulsion

### 2.1 Motor data: AeroTech H100W-14A DMS, 38 mm single-use, AT part 081014 (motor.md §A, design.yaml `motor`)

Every value was read through WebSearch on 2026-11-21, because direct fetches return 403. No manufacturer cert sheet could be read.

| Item | Design value | Other sources | Source / basis |
|---|---|---|---|
| Total impulse | 226.8 N·s | 234 (QA, manufacturer listing); 223.9 (RR) | ThrustCurve "calculated" = Wildman |
| Average thrust | 97.7 N | 100 (QA); 93.4 (RR) | Wildman label. Check: 226.8 / 2.32 = 97.8 |
| Max thrust | **137.8 N** (structural) | 131 (QA); 130.2 (RR) | Wildman labels 137.75 as the max |
| ThrustCurve "116.1 N" | **unresolved** | — | The value has no label; check it when the file arrives |
| Burn time | 2.32 s | 2.3 (TC, QA); 2.40 (RR) | Wildman |
| Loaded / propellant / burnout mass | 261 / 121 / 140 g | all agree on 261 / 121 | 140 g is derived (261 − 121) and ignores delay and ejection mass |
| Length | 155 mm | 153 (TC); 157.5 (RR) | AT/QA product name "38mm x 155mm". The RSE file will govern the sim |
| Delay | 14 s max; owner drills it shorter with the **UDDT** (not included) | "6, 8, 10 s" attributed to TC (unverified) | QA |
| Case OD | **TBD** (1.500 in = 38.10 mm nominal, from the I500T DMS page) | — | motor.md §C |
| Thrust ring | present, factory-glued; OD and thickness **TBD** | "usually 3/8 in long" (forum, informal) | AT DMS data sheet |
| HAZMAT / price | yes / **$54.99** | eRockets $54.99, out of stock | QA; Wildman; AT catalog 03.26.25 |
| MESS failure reports | 3 (details not seen) | — | ThrustCurve, quoting motorcato.org |

TC = ThrustCurve, QA = Quest Aerospace, RR = RocketReviews. The design values are the ones in design.yaml `motor`.

**Thrust curve: TBD.** `projects/l1-cheap/motor/H100W.eng` is not present. The sim stops on the missing file on purpose, so no curve is guessed (motor.md §A). There is no H100W thrust-curve figure yet.

### 2.2 Case OD and thrust ring: critical for minimum diameter (motor.md §C)
- **Case OD.** No measurement is published, and forum threads asking for it got no answer. If the 38.10 mm nominal holds, the case has **0.64 mm diametral clearance** in the 38.735 mm tube. Labels and glue can take up that gap.
- **Ring.** Factory-glued; AeroTech's DMS thrust-ring advisory (04/2014) says to check it. In this layout **the glue joint carries all of the thrust (137.8 N)**.
  - A tape ring forward of the factory ring won't fit inside the tube.
  - A CA fillet on the forward face would spoil the flat bearing face.
- **PROPOSED:** a forward backup stop inside the tube (a printed or plywood ring epoxied at motor length). Owner decision.
- **Heat.** The paper tube now touches the case directly, and the case and nozzle are hot when the ejection charge fires (motor.md §D).

### 2.3 Selection rationale
- **2026-11-20:** owner confirmed the H182R-14A (29 mm DMS, $42.29–56.40, no case to buy), chosen over 29 mm RMS reloads that need a $108.79–$152.99 case (feasibility.md §2–3).
- **2026-11-21:** owner switched to the **H100W-14A (38 mm DMS)** and chose **minimum-diameter**, over a larger airframe or keeping a 29 mm motor (design.yaml `motor`; git c717e50, 7544078).
  - The owner's reasons are not recorded in the project files (§11).
  - Cost: $54.99 is $12.70 more than the H182R's low price (motor.md §A).
- HAZMAT applies to both motors. The earlier plan was to buy from the club's launch-day vendor; the H100W vendor plan is TBD.

### 2.4 Delay
- Delay = t_apogee − t_burnout, because the delay timer starts at burnout (recovery.md §6).
- **TBD for the H100W.** It will be set from the stability re-sim's coast to apogee, then drilled by the owner with the UDDT. The UDDT step sizes are TBD (motor.md §F).
- The 12 s recommendation (stability.md §3) was for the H182R and is superseded.

### 2.5 H182R-14A (29 mm): SUPERSEDED 2026-11-21, kept for history (motor.md, lower part)

| Item | Spec sheet | RSE / .eng | Design value then |
|---|---|---|---|
| Impulse / avg / peak thrust | 218 N·s / 182 N (derived) / 192 N stated, ~205 N plotted | 216.1 N·s / 175.0 N / 200.8 N | sim used the .eng file; 205 N structural |
| Burn / loaded / burnout / length | 1.2 s / 207 g / 92 g / 203 mm | 1.235 s | — |

![H182R thrust curve (superseded)](figures/h182r_thrust.png)

*Figure 1. SUPERSEDED motor. H182R-14A thrust vs time, plotted from `projects/l1-cheap/motor/H182R.eng` (owner's ThrustCurve RSE file, AT DMS data May 2014): 216.1 N·s, 175.0 N average, 200.8 N peak at 1.144 s. Generated 2026-11-20.*

---

## 3. Aerodynamics

> aero.md has **not** been re-run for the H100W or the sleeve fin can. The CP, drag-vs-Mach and Vmax values below are on the H182R / rev 2 basis.

### 3.1 Fins (aero.md §1, design.yaml `aero`, `fin_can_md`)

| Item | Value | Status |
|---|---|---|
| Count | 3 | aero proposal |
| Root / tip chord | 100 / 40 mm (λ = 0.4) | aero proposal |
| Span | 40 mm (tuning range 30–50) | aero |
| LE sweep | 60 mm; TE square and flush with the aft face | aero |
| Thickness | 5 mm | **provisional**, pending flutter |
| Section | NACA 4-digit symmetric, constant thickness, TE 0.84 mm (2 outer lines) | PROPOSED |
| Root fillet | r = 4 mm | PROPOSED (owner's 3–5 mm range not confirmed) |
| **Fin root diameter (rev 3)** | on the sleeve, OD 46.795 mm, not on the 41.275 mm tube | fin_can_md rev 3 spec |

### 3.2 Barrowman centre of pressure (aero.md §2)

Reference point: the nose tip. All lengths in mm.

Symbols:
- Ln: nose length.
- Lb: body length, from the nose base to the aft end.
- d: body diameter (41.275 mm); r = d/2.
- N: fin count.
- s: fin span.
- Cr / Ct: root / tip chord.
- xs: LE sweep.

**Nose:** CNα,n = 2 and X_n = k·Ln, with k = 0.466 for a tangent ogive, 0.5 for Haack/VK/parabolic, 0.666 for a cone.

**Fins:**
- CNα,f = K_fb · 4N(s/d)² / [1 + √(1 + (2 l_m/(Cr + Ct))²)]
- K_fb = 1 + r/(s + r)
- l_m = √(s² + (xs + Ct/2 − Cr/2)²)
- For s = 40: l_m = 50.0 mm, K_fb = 1.340, **CNα,f = 6.777**.

**Fin CP from the root LE:** ΔX_f = xs(Cr + 2Ct)/(3(Cr + Ct)) + (1/6)[(Cr + Ct) − Cr·Ct/(Cr + Ct)] = **44.3 mm**.

**Total:** **CP = (2·X_n + CNα,f·X_f) / (2 + CNα,f)**, where X_f = Ln + Lb − 55.7 mm.

| Case | CP from nose tip | Source |
|---|---|---|
| aero.md headline (Lb 863, fin can length not included) | 768.3 mm | design.yaml `aero.cp_from_nose_tip_mm` |
| H182R / rev 2 geometry (Lb 963) | 845.5 mm (RocketPy 845.4 at M 0) | design.yaml `stability.cp_from_nose_mm`, **superseded** |
| RocketPy at M ≥ 0.8 (H182R / rev 2) | 856.6 mm | sim 2026-11-20, **superseded** |

For rev 3 the CP has to be recomputed. Three things changed:
- The sleeve slides over the tube, so the body length changes.
- The fins now root on a 46.795 mm sleeve, not the 41.275 mm tube.
- There is a 20 mm forward fairing.

K_fb and r both depend on the body radius at the fins (§11).

### 3.3 Drag and Mach (aero.md §3)

Cd is an **ESTIMATE** from an OpenRocket-method component buildup:
- skin friction at 60 µm roughness;
- base drag 0.12 + 0.13M²;
- fin LE/TE pressure drag.

Rail buttons, nose wave drag and the transonic drag rise are not included. The sleeve step and fairing aren't included either.

| M | 0.1 | 0.5 | 0.7 |
|---|---|---|---|
| Cd | 0.70 | 0.76 | 0.83 |

- Above M 0.7 the sim holds Cd at 0.83 (ASSUMPTION, design.yaml `stability.assumptions.cd_vs_mach`).
- **H182R basis, superseded:** Vmax 281.4 m/s, M 0.829, max q 47.7 kPa. aero.md's older 286–369 m/s (M 0.84–1.09) range assumed 300–500 g structures. **The H100W Mach is TBD until the re-sim.**

### 3.4 Flutter: TBD (aero.md §4)

Method: NACA TN 4197, via Apogee *Peak of Flight* #291.

V_f = a · √( G / [ 1.337·AR³·P·(λ + 1) / (2(AR + 2)(t/Cr)³) ] ), with AR = s²/A_fin

Symbols: V_f flutter speed (m/s), a speed of sound (m/s), G shear modulus (Pa), P pressure (Pa), λ taper ratio, t thickness, Cr root chord, A_fin fin area.

PETG G is not in the shop constants, so aero.md inverts the formula to find the G that each fin size would need. Conditions: Vmax 369 m/s (old worst case), a = 339.3 m/s, P = 98.6 kPa. The 1.5× margin is aero's choice.

| s / t | G for V_f = Vmax | G for V_f = 1.5·Vmax |
|---|---|---|
| 40 / 4 mm | 124 MPa | 279 MPa |
| **40 / 5 mm** | **63 MPa** | **143 MPa** |
| 35 / 5 mm | 44 MPa | 98 MPa |
| 30 / 5 mm | 28 MPa | 64 MPa |

### 3.5 CFD domain tool (new 2026-11-21): `tools/fluent_domain.py`
- **What it does:** writes Fluent-ready 2D C-domains around the fin root (100 mm) and tip (40 mm) sections into `out/cfd/`:
  - `*_domain.step` with named edges;
  - airfoil `.csv` point files;
  - check PNGs;
  - `fluent_setup.md`.
- **Geometry:** it uses the same NACA section, thickness and TE as the printed fin (parts/fin_can.py, which rev 3 imports). The domain size defaults to 20 chords.
- **Setup sheet** (out/cfd/fluent_setup.md):
  - density-based solver, ideal gas, Sutherland viscosity, k-ω SST;
  - pressure far-field; AoA 0, 2, 4 and 6°;
  - first-cell height for y+ ≈ 1 (ESTIMATE, flat-plate Cf).
- **Caveat:** the setup sheet's speeds (rail exit 28.4 m/s, Vmax 283.1 m/s, "Mach 0.83") are on the H182R basis. It also points to the rev 2 fin-only STEP. Both are stale (§11).
- No CFD results exist yet.

---

## 4. Structures & Manufacturing

### 4.1 Fin can rev 3: min-diameter sleeve (DRAFT, NOT PRINT-READY)

New part `parts/fin_can_md.py` (`make.py fin_can_md --rev 3`, 2026-11-21) is a printed PETG sleeve that slides **over** the BT-1.52's aft end. It has:
- 3 fins;
- a 20 mm forward fairing down to the tube OD;
- an **aft lip** under the tube end, which acts as the **thrust stop**;
- M3 heat-set insert bosses at the fin roots.

The motor sits directly in the tube (part docstring; out/fin_can_md/rev3/fin_can_md_rev3_spec.md).

| Parameter | Value | Status |
|---|---|---|
| Tube OD (sets the sleeve bore) | 41.275 mm | **PLACEHOLDER**: measure |
| Sleeve bore / wall / OD | 41.455 / 2.67 / **46.795 mm** | derived (snug-slip PROPOSED) / PROPOSED / derived |
| Sleeve length / fairing | 100 mm (= root chord) / 20 mm | FROM_AERO / PROPOSED |
| Lip thickness / lip bore | 2.67 mm / 38.18 mm (case OD + 2 × snug-slip) | PROPOSED / derived |
| Motor case OD | **38 in the rev 3 model**; design.yaml now 38.10 | **PLACEHOLDER** (§11) |
| Motor length | **153 in the rev 3 model**; design.yaml now 155 | CITED (§11) |
| Thrust ring OD × thickness | 41.0 × 3.0 mm | **PLACEHOLDER** (must be > lip bore to bear) |
| Retention | Option A carried over: one M3 insert per fin (Ø4.0 × 5.7 mm hole), in a faired boss at the fin root | OWNER (design.yaml `fin_can_md.retention`) |
| Insert radius / washer min. OD | 25.398 mm / 13.795 mm (from the placeholder ring) | derived |
| Kevlar anchor | **not in rev 3**; rev 2 used a shoulder groove, and rev 3 has no shoulder | open (§11) |
| Extents / print | 97.4 × 112.4 × 120.0 mm; lip down, axis vertical, no supports | verify check 5; spec |
| Target mass | **TBD** (null), to be set by stability after the H100W re-sim | design.yaml `fin_can_md.target_mass_g` |

![Fin can rev 3, iso](figures/fin_can_md_rev3_iso.png)

*Figure 2. Fin can rev 3 (min-diameter sleeve), iso view in print orientation (aft lip on the bed, Z up). It shows the sleeve with 3 fins, the root bosses at the aft end and the forward fairing (Z 100–120 mm). Source: `out/fin_can_md/rev3/fin_can_md_rev3_iso.png`, `make.py fin_can_md --rev 3`, 2026-11-21. Built with the placeholder tube OD, a 38 mm case and 153 mm motor length.*

![Fin can rev 3, section](figures/fin_can_md_rev3_section.png)

*Figure 3. Fin can rev 3, axial section through a fin (y = 0).*
- *Left: the 2.67 mm sleeve wall, with the lip turning inward at Z = 0.*
- *Right: the fin root, with the M3 insert hole entering from the aft face.*
- *The sleeve tapers in the fairing from Z = 100 to 120 mm.*

*Source: `out/fin_can_md/rev3/fin_can_md_rev3_section.png`, 2026-11-21.*

**Verify results (out/fin_can_md/rev3/fin_can_md_rev3_verify.json): 4 / 5 PASS, so the part is not good.**

| # | Check | Result |
|---|---|---|
| 1 | Mesh integrity | PASS: watertight, 1 body, 77 396.1 mm³ |
| 2 | Mass | **FAIL: no target mass declared.** Model gives 97.6 g (0 %) to 98.3 g (100 %) |
| 3 | Mating interference | PASS: 0 mm³ with the tube wall, motor case and thrust ring (**all from placeholders**, and the case and length predate the design.yaml update) |
| 4 | Renders | PASS: iso, front and section written. Iso and section reviewed for this report |
| 5 | Build volume | PASS: 97.4 / 112.4 / 120.0 mm vs 256 |

**Loads vs. layers (rev 3, printed axis-vertical, lip down).** Sources: spec sheet rev 3, motor.md §D–E.

| Load | Direction vs layers | Bond loading |
|---|---|---|
| Motor thrust: ring pushes +Z on the lip underside; the lip pushes the tube end forward | across layers | **compression** (good); the tube butts on the lip, so there is no PETG interlayer shear |
| Fin root bending | within layers (radial/tangential) | in-plane |
| Sleeve-to-tube epoxy joint (fin loads, drag) | shear on vertical cylindrical faces | in-plane shear of the PETG |
| Ejection kick on the motor (−Z): the ring pulls the screws aft, out of the boss inserts | across layers | **pull-out: shear + tension (weak direction)** |

### 4.2 Structural checks (rev 3, H100W)

**Thrust bearing on the lip** (motor.md §D): σ = F / A, with A = π/4 · (ring OD² − lip ID²).
- σ is the bearing stress (MPa), F the force (N) and A the bearing area (mm²).
- F = 137.8 N. A is TBD until the ring is measured.
- The 15 MPa reference is reached at A = 9.2 mm².
- Example only: ring 41 mm, lip ID 39 mm gives A = 125.7 mm², so σ = 1.1 MPa.
- 15 MPa is the interlayer *shear* figure, used as a conservative reference because the shop has no PETG compressive allowable.

**Retention pull-out** (motor.md §E, PROPOSAL)
- **Design load (ESTIMATE):** 15 psi (0.1034 MPa) × 1178.4 mm² = **122 N**. The area is the tube-ID face, an upper bound for the case. ×3 margin gives **366 N** (design.yaml `motor.retention_design_load_n`). With the 38 mm class diameter instead: 117 / 352 N.
- **Capacity per insert, plug shear:** τ·π·D·L = 15 × π × 4.0 × 5.7 = 1074 N.
  - Symbols: τ interlayer shear (MPa), D hole diameter (mm), L insert length (mm).
  - SPIROL's installation knock-down to 25 % gives 269 N per insert.
- **Three inserts:** 807 N, so **SF 2.2**.
- A commercial 38 mm retainer won't fit, because there is no motor tube to mount it on. Screw and washer lengths are TBD.

**Fin root bending** (aero.md §5; H182R-era load case: α = 5° at max q 81.8 kPa)
- F = q·S_ref·CNα·α = 47 N, with a spanwise centroid of 17.1 mm, so M = 0.805 N·m.
- σ = M/Z, with Z = Cr·t²/6 = 417 mm³, so **σ = 1.93 MPa**. τ = 1.5F/(Cr·t) = 0.14 MPa.
- That is a factor of 7.8 below 15 MPa. Not re-run for the H100W.

**Interlayer net-area check for printed anchors** (recovery.md §4): σ = F·SF / A_net ≤ 15 MPa, so A_net ≥ F·SF / 15.
- **191 mm²** for a 40 m/s deploy on the 40 in chute (953 N × 3 / 15).
- **48 mm²** for a deploy at ≤ 20 m/s.
- Rev 3 has no aft anchor to check yet.

### 4.3 Mass model (walls + infill): skills/SKILL.md, verify check 2

m = ρ · (V_shell + f · V_interior)

Symbols:
- ρ = 1.27 g/cm³ (PETG).
- V_shell: walls (2.67 mm band) plus top/bottom skins (cm³).
- V_interior: infill region (cm³).
- f: infill fraction.

| Rev | V_shell (cm³) | V_interior (cm³) | m at f = 0 / f = 1 |
|---|---|---|---|
| rev 2 | 134.67 | 2.39 | 171.0 / 174.1 g |
| **rev 3** | **76.84** | **0.54** | **97.6 / 98.3 g** (essentially solid) |

### 4.4 Fin can revision history

| Rev | Part / layout | Change | Mass (0–100 % infill) | Verify | Status |
|---|---|---|---|---|---|
| rev 1 | `fin_can.py`, 29 mm mount + MMT-1.14 liner, shoulder in tube | First geometry; no motor retention | 170.5–173.0 g | 5/5 (target 171.1 g) | superseded |
| rev 2 | `fin_can.py`, 29 mm | Option A M3 insert bosses at the 3 fin roots | 171.0–174.1 g | 5/5 (target 171.1 g, 2.3 % infill) | **SUPERSEDED 2026-11-21** (29 mm motor dropped) |
| **rev 3** | **`fin_can_md.py`, min-diameter sleeve** | Sleeve over the tube, aft-lip thrust stop, forward fairing, root bosses | 97.6–98.3 g | **4/5** (check 2 FAIL) | **DRAFT** |

**Rev 2, for the record** (out/fin_can/rev2/fin_can_rev2_spec.md):
- One PETG part with a 103 mm shoulder inside the tube, a 30.68 mm bore for the MMT-1.14 liner, and the thrust ring on the aft face.
- Kevlar anchored in an epoxied 3.0 × 2.6 mm shoulder groove.
- Extents 93.2 × 107.6 × 203.0 mm.
- The H182R sim used it at 171.8 g, with the CG 79.8 mm forward of the aft face.

![Fin can rev 2, iso (superseded)](figures/fin_can_rev2_iso.png)

*Figure 4. SUPERSEDED. Fin can rev 2 (29 mm mount), iso view in print orientation. Source: `out/fin_can/rev2/fin_can_rev2_iso.png`, `make.py fin_can --rev 2`, 2026-11-20.*

![Fin can rev 2, section (superseded)](figures/fin_can_rev2_section.png)

*Figure 5. SUPERSEDED. Fin can rev 2, axial section through a fin (y = 0): the bore wall, the fin root with the M3 insert hole, and the shoulder step at Z = 100 mm. Source: `out/fin_can/rev2/fin_can_rev2_section.png`, 2026-11-20.*

### 4.5 Nose cone: PROPOSED, part module not written (nosecone.md)

| Item | Value | Status |
|---|---|---|
| Shape / length | Tangent ogive, 165 mm, fineness 4.0 | PROPOSED |
| Base OD | 41.275 mm | nominal; reset to the measured tube OD |
| Shoulder | OD 38.555 mm, 40 mm long | PROPOSED |
| Wall | 2.2 mm (fully solid, < 2 × 2.67 mm) | PROPOSED |
| Aft bulkhead | 5 mm, integral; Kevlar strap holes and a ballast fill port (sizes TBD) | PROPOSED |
| Mass / CG | **52.7 g ESTIMATE** (51.7–55.5 g over 0–100 %), CG 119.9 mm from the tip | ESTIMATE |
| Ballast cavity | 27.2 cm³ from the tip to 100 mm; fill CG 74.6 mm | nosecone.md §5 |
| Print | Tip up, bulkhead on the bed, 41.3 × 41.3 × 205 mm, no supports | |

**Loads vs. layers (nose, printed tip-up)**, nosecone.md §4. The snatch load pulls the strap aft (−Z).
- The web bends in-plane.
- The bulkhead-to-wall interface is within the layers.
- The shoulder wall carries the load in **Z tension across the layers**, which makes it the weak link.
- Its annulus is 251 mm², which reaches 15 MPa at 3.77 kN.

`parts/nose_cone.py` does not exist, so the nose has no verify run.

---

## 5. Recovery

> recovery.md has not been re-run for the H100W. design.yaml `recovery.deployment` still names the H182R-14A charge.

### 5.1 Scheme (recovery.md §1, design.yaml `recovery`)
- **Single deploy on the motor's own ejection charge** (now the H100W-14A). PROPOSED; no electronics are flown.
- The charge size is unpublished, and a DMS charge can't be ground-tested on its own.
- The tube has 117.8 cm³ of free volume per 100 mm. The recovery pack is about 120 mm long (ESTIMATE; pack test pending).
- **Aft anchor:** rev 2's shoulder groove no longer exists, and rev 3 has no anchor feature. The method is TBD (§11).
- **Heat:** the paper tube touches the motor case directly (motor.md §D).

### 5.2 Parachute: owned 40 in (recovery.md §7)

Descent rate, flat canopy: **v = √( 2·m·g / (ρ·Cd·A) )**

Symbols:
- v: descent rate (m/s).
- m: descent mass (kg).
- g = 9.80665 m/s².
- ρ = 1.225 kg/m³.
- Cd: canopy drag coefficient (0.75 design, 1.5 optimistic).
- A = πD²/4: canopy area (m²).

| 40 in chute | 450 g | 575 g | 700 g |
|---|---|---|---|
| Cd 0.75 | 3.44 m/s | 3.89 m/s | 4.29 m/s |
| Cd 1.5 | 2.43 m/s | 2.75 m/s | 3.04 m/s |
| Reefed to ~30 in, Cd 0.75 | 4.59 m/s | 5.19 m/s | 5.72 m/s |

- The 450–700 g mass range is the main session's **PLACEHOLDER**. The H182R-basis burnout mass of 600.3 g is superseded; the H100W burnout mass is TBD.
- Recommendation: reef the chute to cut drift, and fly it full size in light wind. Chute mass ≤ 57 g (ESTIMATE); weigh it. Descent-rate target TBD (owner).

### 5.3 Opening load (recovery.md §3, §7)

**F = ½ · ρ · v² · Cd · A · Cx**, where Cx = 1.6 is the opening-shock factor (Knacke 1992), F is in N and v is the deploy speed (m/s).

| v at deploy (40 in, Cd 0.75) | 10 m/s | 20 | 30 | 40 |
|---|---|---|---|---|
| F | 60 N | 238 N | 536 N | 953 N |

Design case: 953 N × SF 3 (proposed) = **2860 N**. The H100W deploy speed is TBD until the re-sim and the drilled delay.

### 5.4 Shock cord
- **9KM DWLIFE Kevlar, 750 lb (3336 N), 2.3 mm, 2.91 g/m; 16 m owned.**
- Cut length rule: 3 × rocket length + 300 mm. That gave 3.68 m for the 1128 mm H182R rocket; the new length is TBD.
- Knotted at 40 % efficiency, the cord holds 1334 N, which passes only up to a ~27 m/s deploy. **Splice or sew the loops.**
- Layout: aft anchor, long run, chute loop about ⅓ from the nose end, then the nose eye. Z-fold the cord.

### 5.5 Ejection protection
Estes recovery wadding is PROPOSED ($5.43–5.99). A Nomex 6×6 (~$5) is the reusable alternative (recovery.md §5).

---

## 6. Stability & Flight Simulation

> **H182R basis — superseded, re-sim pending.** Everything in §6 is for the H182R-14A in fin can rev 2 (29 mm mount, liner, 90.5 g ballast).
> - The H100W changes the motor mass (261 vs 207 g), length (155 vs 203 mm), thrust curve and position.
> - It also changes the fin can (98 g vs 171.8 g) and the fin root diameter.
>
> The re-sim is blocked on the H100W .eng file (design.yaml `motor.thrust_curve_source`). The H100W ballast, balance point, apogee, Mach and delay are all **TBD**.

**Tool:** RocketPy 1.13.0, `sims/l1_cheap.py`. The sim takes each value in this order (sim docstring):
1. the owner value, if it is a number;
2. otherwise the `stability.assumptions` value;
3. otherwise the item is left out and the run is stamped PROVISIONAL.

Conditions: standard atmosphere, vertical rail, no wind.

### 6.1 Static margin (method unchanged)
**SM = (CP − CG) / d**

Symbols: SM static margin (calibers); CP and CG measured from the nose tip (mm); d = 41.275 mm body diameter.

H182R basis: (845.5 − 771.2) / 41.275 = 1.80 cal at liftoff. **Superseded.**

### 6.2 Mass budget: H182R basis, SUPERSEDED (x from the nose tip)

| Item | g | x (mm) | Basis | H100W status |
|---|---|---|---|---|
| Nose cone | 52.7 | 119.9 | ESTIMATE | unchanged |
| Ballast | 90.5 | 74.6 | solved for 1.8 cal | **re-solve** |
| BT-1.52 tube, 863 mm | 93.6 | 596.5 | ESTIMATE 0.1085 g/mm | position changes |
| Fin can rev 2 | 171.8 | 1048.2 | model, 25 % infill | **now rev 3, 97.6–98.3 g** |
| Liner MMT-1.14 | 10.0 | 1026.5 | ESTIMATE | **dropped** |
| Parachute / Kevlar / wadding | 57.0 / 10.7 / 2.0 | 865 / 865 / 915 | ESTIMATES | cord length changes |
| Epoxy / rail buttons / retention | 10.0 / 5.0 / 5.0 | 976.5 / 828 / 1126 | ESTIMATES | re-place |
| **Structure** | **508.3** | 667.2 | | TBD |
| Motor loaded / burnout | 207 / 92 | 1026.5 | H182R | **261 / 140 (H100W)** |
| **Liftoff / burnout** | **715.3 / 600.3** | CG 771.2 / 722.3 | | TBD |

### 6.3 Margin vs time: H182R basis, SUPERSEDED

![Static margin vs time (H182R basis, superseded)](figures/l1_cheap_margin_vs_time.png)

*Figure 6. SUPERSEDED (H182R, fin can rev 2, 90.5 g ballast). Static margin CP(Mach) − CG(t) from liftoff to apogee, on a 1.83 m rail, with 0 / 5 / 10 g of delay and ejection mass loss. The shaded band is the owner's 1.8 ± 0.2. Source: `out/sims/l1_cheap_margin_vs_time.png`, regenerated 2026-11-20. Not valid for the H100W.*

Method (stability.md §3a; will be reused):
- CP(M) comes from RocketPy's Mach-dependent Barrowman.
- Propellant m(t) is impulse-proportional.
- The propellant CG is at the motor midpoint.

| Event (H182R basis) | t (s) | Mach | CP (mm) | CG (mm) | Mass (g) | SM (cal) |
|---|---|---|---|---|---|---|
| Liftoff | 0.000 | 0.000 | 845.4 | 771.2 | 715.3 | 1.80 (min) |
| Rail exit (1.83 m) | 0.142 | 0.083 | 845.5 | 767.1 | 704.1 | 1.90 |
| Max q = Vmax | 1.199 | 0.829 | 856.6 | 722.5 | 600.6 | 3.25 |
| Burnout | 1.235 | 0.821 | 856.6 | 722.3 | 600.3 | 3.25 |
| Apogee | 13.891 | 0.000 | 845.4 | 722.3 | 600.3 | 2.98 |

### 6.4 Flight summary: H182R basis, SUPERSEDED

| Quantity | H182R value (superseded) | H100W |
|---|---|---|
| Apogee | 1284 m (4212 ft) at 13.89 s | TBD |
| Burnout / coast to apogee | 1.235 s / 12.66 s | burn 2.32 s (motor); coast TBD |
| Vmax / Mach / max q | 281.4 m/s / 0.829 / 47.7 kPa | TBD |
| Rail exit 1.5 m / 1.83 m | 25.5 / 28.3 m/s | TBD (thresholds TBD, motor.md §F) |

### 6.5 Delay table: H182R basis, SUPERSEDED

| Delay (s) | 14 | 13 | 12 | 11 | 10 | 9 | 8 |
|---|---|---|---|---|---|---|---|
| Speed at deploy (m/s) | 12.7 ↓ | 3.4 ↓ | 6.4 ↑ | 16.3 ↑ | 26.5 ↑ | 37.2 | 48.5 |

The 12 s recommendation was for the H182R. The H100W table will come from the re-sim; recovery prefers ≤ 20 m/s and sets the limit at ≤ 27 m/s.

### 6.6 Sensitivity (method notes that carry over; values are H182R basis)
- Nose mass: ballast absorbs nose error at −0.93 g per +1 g. Set the final ballast from the weighed nose (stability.md §5).
- Ballast vs CG: about 1 g of nose ballast per 1 mm of CG shift (design.yaml `stability.ballast_g`).
- Liftoff aim 1.8 cal, accept 1.6–2.0 (stability.md §3b, PROPOSED).
- Cd ×0.85–1.3 spanned an apogee of ~1413–1096 m for the H182R.

---

## 7. Bill of Materials & Budget

### 7.1 BOM (bom.csv, Phase 3; **not yet updated for the H100W**)

| Tag | Item | Qty | Mass (g) | Unit price (USD) | H100W change |
|---|---|---|---|---|---|
| buy | Motor: bom.csv lists the H182R-14A | 1 | 207 | 42.29–56.40 | **H100W-14A DMS, 261 g, $54.99, HAZMAT** (motor.md §A) |
| buy | LOC BT-1.52 tube, 34 in | 1 | 93.6 ESTIMATE | 9.30 | — |
| buy | Estes recovery wadding | 1 pack | 2 ESTIMATE | 5.43–5.99 | — |
| buy | M3 brass heat-set inserts | 2 (pack of 100) | ~1 ESTIMATE | 10.99 / 100 | rev 3 uses 3 |
| TBD | M3 screws + washers | 2 + 2 | ~3 ESTIMATE | TBD | 3 + 3; washer min. OD 13.795 mm (placeholder ring) |
| print | Nose cone | 1 | 52.7 | 0.69 | — |
| print | Fin can | 1 | 197.3 (stale) | 2.56 | rev 3 model 97.6–98.3 g |
| have | Ballast, 40 in chute, Kevlar, epoxy, PETG, glue stick, calipers, scale | — | — | 0 | ballast mass TBD |
| borrow | AeroTech delay tool; pad, rail, controller | — | — | 0 | **UDDT** (not included with the motor); source TBD |
| owner-handled | Rail buttons, igniter, soldering iron | — | — | excluded | — |
| — | MMT-1.14 liner | — | — | — | **dropped** (min-diameter) |
| PROPOSED | Forward backup motor stop (printed or plywood ring) | — | — | — | owner decision (motor.md §C) |

### 7.2 Budget: Phase 4 not started
- Cap $100 incl. motor; 5 % contingency leaves **$95 spendable** (feasibility.md §4).
- The motor is now $54.99, $12.70 more than the H182R's low price (motor.md §A).
- Excluded from this budget:
  - the altimeter, which is outside the budget (git 392a135);
  - the owner-handled items (bom.csv).
- No total is given yet: screws, washers, UDDT access and shipping or vendor terms are unpriced.

---

## 8. Schedule

Phase 5 has not started, and there is no `schedule.md`.
- Deadline: launch on 2026-12-14, 24 days from 2026-11-20 (goal.md).
- **New ordering constraints (2026-11-21):**
  - the H100W .eng file comes before the re-sim, which comes before the ballast, delay and fin can target mass;
  - motor measurements (case OD, ring) come before the fin can rev 3 print.
- The motor is HAZMAT. If it is bought at the field, its dimensions may not be in hand before printing (fin_can_design.md, Risks).
- Project difficulty is 3 / 5 (feasibility.md §5).

---

## 9. Verification & Test Plan

### 9.1 verify.py (skills/SKILL.md)

| # | Check | Pass condition | Fin can rev 3 | Nose cone |
|---|---|---|---|---|
| 1 | Mesh integrity | watertight, manifold, one body | PASS | not generated |
| 2 | Mass | within ±5 % of target | **FAIL** (no target) | — |
| 3 | Mating interference | 0 mm³ with each mating solid | PASS (vs placeholders: case 38, length 153) | — |
| 4 | Renders | written and looked at | PASS (reviewed for this report) | — |
| 5 | Build volume | ≤ 256 mm on each axis | PASS | — |

A part is not "good" until every check passes and its renders have been reviewed (CLAUDE.md). Rev 2 passed 5/5 but is superseded.

### 9.2 Measurements and fit tests before printing
- **Tube OD** (calipers): sets the sleeve bore and the nose base OD.
- **Motor, in hand** (motor.md §C):
  1. Case OD at the label, in 3 places.
  2. Ring OD.
  3. Ring axial thickness.
  4. Ring-to-nozzle-exit offset.
  5. Overall length.
- **Thrust ring glue:** inspect the joint per the AT 2014 advisory.
- **Fit test:** slide the motor into the BT-1.52 to check the min-diameter clearance.

### 9.3 Weigh-and-balance
- Weigh the nose, tube, chute and Kevlar, then re-run the sim with the H100W and as-built masses.
- Set the ballast from the weighed nose.
- The ready-to-fly balance point (771 ± 8 mm) is **H182R basis, superseded**. The new value comes from the re-sim.
- A swing test checks CP qualitatively.

### 9.4 Recovery and pre-flight
- Pack-test the chute, cord and wadding (recovery.md §6). Splice or sew the Kevlar loops. Reef the chute if the wind is up.
- **Drill the H100W delay with the UDDT** to the re-sim setting (TBD).
- Arrange witnesses and give the cert form to the prefect (feasibility.md §1).

### 9.5 Analysis tools
- `sims/l1_cheap.py`: RocketPy flight and stability (§6).
- `tools/fluent_domain.py`: 2D fin-section CFD domains for Fluent (§3.5). No results yet.

---

## 10. Decision Log

| Date | Decision | By | Rationale / source |
|---|---|---|---|
| 2026-11-20 | Goal: Tripoli L1, $100 incl. motor, 29 mm H, 38 mm tube, printed PETG fin can and nose, 1.8 cal | owner | goal.md |
| 2026-11-20 | Owner is 18+; launch at Palm Bay, FL, on 2026-12-14 | owner | feasibility.md §7 |
| 2026-11-20 | Airframe: buy a LOC BT-1.52 34 in ($9.30) | owner | feasibility.md §7 |
| 2026-11-20 | Motor: AeroTech H182R-14A. **Superseded 2026-11-21** | owner | git f1494d0 |
| 2026-11-20 | Recovery: owned 40 in chute and 750 lb Kevlar | owner | recovery.md §7 |
| 2026-11-20 | No payload in this rocket; Quasar-LR kept for later; altimeter cost outside the budget | owner | payload.md; git b0bd19e, 392a135 |
| 2026-11-20 | Rail buttons, igniter and soldering iron owner-handled; owner has ballast, calipers and scale | owner | bom.csv |
| 2026-11-20 | Stability band gates **liftoff only** | owner | design.yaml `owner.stability_band_applies` |
| 2026-11-20 | Liftoff aim 1.8 cal, accept 1.6–2.0 | stability (PROPOSED) | stability.md §3b |
| 2026-11-20 | Motor liner LOC MMT-1.14. **Dropped 2026-11-21** | owner | design.yaml `fin_can.liner` |
| 2026-11-20 | Retention: **Option A**, one M3 insert per fin in a root boss | owner | design.yaml `fin_can.retention` |
| 2026-11-20 | Ballast 90.5 g and delay 12 s (H182R). **Superseded** | stability (PROPOSED) | stability.md §3 |
| 2026-11-20 | Single deploy on motor ejection | recovery (PROPOSED) | design.yaml `recovery.deployment` |
| **2026-11-21** | **Motor: AeroTech H100W-14A DMS (38 mm)**; owner drills the delay with the UDDT | owner | design.yaml `motor.designation`; git c717e50, 7544078. Reason not recorded |
| **2026-11-21** | **Minimum-diameter**: motor directly in the BT-1.52, liner dropped. Chosen over a larger airframe or keeping a 29 mm motor | owner | motor.md status; design.yaml `fin_can_md`. Reason not recorded |
| 2026-11-21 | Fin can becomes a sleeve over the tube with an aft-lip thrust stop (rev 3, `fin_can_md.py`); Option A retention carried over | main session / owner | design.yaml `fin_can_md`; git cfd68fc |
| 2026-11-21 | Forward backup motor stop inside the tube | motor (PROPOSED) | motor.md §C; owner decision pending |

---

## 11. Open Items & Placeholders

### 11.1 Blocks the H100W re-sim
- **`motor/H100W.eng` is not present.** The owner needs to upload the ThrustCurve H100W_DMS RSE or ENG file.
- Until then, these are all TBD: ballast, liftoff margin, balance point, apogee, Vmax/Mach, rail exit, delay, deploy speed, burnout mass, total length, Kevlar length and `fin_can_md.target_mass_g` (verify check 2).

### 11.2 Placeholders that block printing (fin can rev 3 spec)
- `tube_od_mm` 41.275: measure the tube.
- `motor_case_od_mm`: 38 in the rev 3 model, 38.10 in design.yaml. Measure.
- `thrust_ring_od_mm` 41.0 and `thrust_ring_thk_mm` 3.0: measure.
- No aft Kevlar anchor in rev 3.
- Nose cone: `parts/nose_cone.py` not written.

### 11.3 Stale or conflicting source entries
1. **Rev 3 outputs vs design.yaml:** the rev 3 spec, verify and renders (01:15) were built with case OD 38 and motor length 153. design.yaml was updated at 01:17 (b0dd66b) to 38.10 and 155. **Regenerate rev 3.**
2. **H100W data disagree between sources:**
   - impulse 226.8 / 234 / 223.9 N·s;
   - average thrust 97.7 / 100 / 93.4 N, plus the unlabelled TC 116.1 N;
   - maximum thrust 137.8 / 131 / 130.2 N;
   - burn time 2.32 / 2.3 / 2.40 s;
   - length 155 / 153 / 157.5 mm.
3. **design.yaml `owner.motor_class` "29mm H"**, goal.md ("29 mm motor … not minimum-diameter") and feasibility.md ("Not min-diameter") all conflict with the owner's 2026-11-21 change.
4. **design.yaml `recovery.deployment`** names the H182R-14A charge. recovery.md has not been re-run.
5. **All `stability` results**, stability.md, `stability.target_mass_g.fin_can` 171.1 and the balance point 771 mm are on the H182R / rev 2 basis.
6. **aero.md CP** does not include the 46.795 mm sleeve, the fairing or the new body length. Vmax and Mach are H182R / older-basis values.
7. **out/cfd/fluent_setup.md** uses H182R-basis speeds (28.4, 283.1 m/s, M 0.83) and refers to `fin_can_rev2_fin_only.step`. Rev 3 writes `fin_can_md_rev3_fin_only.step`.
8. **design.yaml `motor.retention`** says "sleeve geometry TBD", but rev 3 now defines it (insert radius 25.398 mm).
9. **bom.csv:** the motor row is still the H182R; inserts and screws are qty 2 (rev 3 needs 3); fin can 197.3 g; the delay-tool row is for the AeroTech tool, not the UDDT.
10. **fin_can_design.md** describes the 29 mm design (2 inserts, 197.3 g). It is superseded by rev 3.
11. **payload.md** has two contradictory banners. The latest owner decision is no payload.
12. **Ballast packing density** is ≥ 3.27 g/cm³ (stability.md, design.yaml) vs ≥ 3.54 g/cm³ (bom.csv). Both are H182R basis.
13. **Flutter and fin root bending** use the old worst case (369 m/s, 81.8 kPa).

### 11.4 Owner inputs still TBD
- **Upload the H100W .eng/RSE file.** Measure the motor (5 items, §9.2) and the tube OD.
- **Approve or reject the forward backup stop.** Choose how the Kevlar is anchored at the aft end.
- **UDDT:** do you own one, or who has one? What are its step sizes?
- Minimum thrust-to-weight and rail-exit-speed thresholds.
- Reasons for the H100W switch and for min-diameter (for the Decision Log). Where will you buy the motor (HAZMAT)?
- Heat protection for the paper tube around the case?
- Carried over:
  - PETG shear modulus G and the flutter margin;
  - club rail size and length, club name, waiver altitude;
  - descent-rate target; chute brand and mass; cord SF; fillet radius;
  - confirm the ±0.2 cal reading and single deploy on motor ejection;
  - epoxy type; ballast material; whether M3 screws and washers are owned;
  - check the Tripoli L1 rules on tripoli.org (especially the > 80 N average-thrust claim).

---

## 12. References

Accessed 2026-11-20 unless noted (as recorded in the project files).

**Motor: H100W (searched 2026-11-21)**
- ThrustCurve H100W_DMS — https://www.thrustcurve.org/motors/AeroTech/H100W_DMS
- Wildman H100W — https://wildmanrocketry.com/products/h100w
- Quest Aerospace H100W — https://questaerospace.com/products/product_f89c2d4d-4c3c-9a99-bfd8-b2d0b1dcef8a
- AeroTech catalog 03.26.25 — https://cdn.shopify.com/s/files/1/0615/7592/1878/files/Model_and_HP_03.26.25.pdf
- eRockets H100W — https://www.erockets.biz/aerotech-38mm-composite-model-rocket-motor-dms-h100w-14a-1pk-aer-081014-required-to-pay-for-ups-ground-shipping-requires-level-1-certification/
- RocketReviews H100W — https://www.pirate.rocketreviews.com/h100w.html
- AeroTech generic DMS data sheet — https://cdn.shopify.com/s/files/1/0615/7592/1878/files/genericdms_1648304178571.pdf
- AeroTech I500T DMS page (1.500 in nominal; URL not recorded in motor.md)
- NAR notices (AT DMS thrust-ring advisory) — https://nar.org/?p=16459
- MESS failure reports — motorcato.org (not seen)
- Rocketry Forum: 38 mm DMS OD — https://www.rocketryforum.com/threads/can-someone-measure-the-od-of-a-38mm-dms-motor-for-me.145958/ ; ring — https://www.rocketryforum.com/threads/38mm-aerotech-dms-thrust-ring-dimensions.146365/ ; drawings — https://www.rocketryforum.com/threads/aerotech-dms-dimensional-drawings.181755/

**Motor: H182R and options (superseded) & certification**
- AeroTech DMS H182R-14A spec sheet (owner-supplied); ThrustCurve RSE `motor/AeroTech_HP-H182R.rse` (owner)
- ThrustCurve HP-H182R — https://www.thrustcurve.org/motors/AeroTech/HP-H182R
- AeroTech H182R — https://aerotech-rocketry.com/products/product_907feaa5-d1fd-0d12-e28f-37e0cfa3bb8f
- AeroTech H128W — https://aerotech-rocketry.com/products/product_2df7f4ec-4f83-4bb0-01ce-b9a1932c0541
- AeroTech H13ST — https://aerotech-rocketry.com/products/product_b7697119-7d82-3db0-694e-7de6ea74dd90
- AeroTech RMS-29 hardware — https://aerotech-rocketry.com/collections/a-rms-29-hardware
- RouseTech RMS-29 — https://rousetech.net/collections/hardware/rms-29-mm/
- Sirius Rocketry H182R — https://www.siriusrocketry.biz/ishop/aerotech-high-power-h182r-14a-29mm-dms-hazmat-1509.html
- Apogee H182R — https://www.apogeerockets.com/Rocket_Motors/AeroTech_Motors/29mm_Motors_Single_Use/Aerotech_29mm_Motor_H182R-14A_SU
- rocket.supplies H182R — https://rocket.supplies/proddetail.php?prod=A081814
- Wildman H128W — https://wildmanrocketry.com/products/h128w
- TRA Certification Rules 2009 — https://laulima.hawaii.edu/access/content/group/7f13b953-c1b5-4532-00fe-072e1311e8a4/uslipub/USLI%20KFC%20Editor/DOCUMENTS/ROCKETRY%20RELATED/TRA_Certification_Rules_2009.pdf
- BYU Rocketry L1 — https://rocketry.byu.edu/join-us/level-1-cert
- Rocketry Forum (L1 avg thrust) — https://www.rocketryforum.com/goto/post?id=1926841
- NAR motor shipping — https://thisistheoldsite.nar.org/wp-content/uploads/2014/05/Shipping-Rocket-Motors.pdf

**Retention & inserts**
- Ejection charge calc — https://tonuonu.github.io/MyLevel1Peregrine/calculations/ejection-charges
- NAU capstone ejection/parachute — https://ceias.nau.edu/capstone/projects/ME/2026/F25toSp26_Rocket/files/AislinnJoyGacayan-ME476C-001-EjectionChargeandParachuteAnalysis.pdf
- 3D People inserts white paper — https://felix-manley-n4jm.squarespace.com/s/Threaded-Inserts-White-Paper-V1.pdf
- Sculpteo insert pull-out — https://www.sculpteo.com/en/3d-learning-hub/design-guidelines/pull-out-resistance-of-threaded-inserts-testing-and-results/
- SPIROL inserts in plastic — https://www.spirol.com/resources/white-papers/performance-expectations-for-threaded-inserts-in-plastic-assemblies/
- McMaster inserts — https://www.mcmaster.com/products/threaded-inserts/performance~any-orientation/ ; https://www.mcmaster.com/product/94459A769/
- accu-components hole chart — https://accu-components.com/p/488-threaded-insert-hole-size-charts-for-3d-printing-pla-petg-resin
- Prusa / CNC Kitchen M3 inserts — https://www.prusa3d.com/en/product/heat-set-inserts-m3-standard-100-pcs/
- Zoro 94459A130 — https://zoro.com/bsc-preferred-heat-set-inserts-for-plastic-brass-m3-x-05-mm-43-mm-installed-length-50pk-94459a130/i/G111638281
- MMT-1.14 ID, OpenRocket catalogue (third-party) — github.com/nrdptel/fusionspace-eridanus/issues/280

**Aerodynamics, CFD & stability**
- Barrowman CP method; OpenRocket technical documentation (drag buildup) — aero.md
- NACA TN 4197 flutter, via Apogee *Peak of Flight* #291 — aero.md
- RocketPy 1.13.0 — sims/l1_cheap.py
- Fluent domain sizing (20 chords, "common external-aero CFD practice") and flat-plate Cf = 0.026 Re^-1/7 — tools/fluent_domain.py, out/cfd/fluent_setup.md
- RocketReviews, over-stability — https://rocketreviews.com/over-stability-230702231653.html
- MIT Rocket Team wiki (stability) — https://wikis.mit.edu/confluence/x/JGf_Bg
- NASA SL "Rocketry by the Numbers" (2023) — https://www.nasa.gov/wp-content/uploads/2023/09/nasa-sl-2024-arw-rocketry-by-the-numbers-508.pdf
- OpenRocket cardboard density — https://www.rocketryforum.com/goto/post?id=2317962 ; https://hub.wsu.edu/aerospace/wp-content/uploads/sites/204/2015/02/OpenRocket-Model.pdf

**Airframe**
- LOC BT-1.52 — https://wildmanrocketry.com/products/bt-1-52 ; https://www.csrocketry.com/building-supplies/loc-precision/cardboard-airframes/1.52-loc-airframe-38mm.html ; https://locprecision.com/products/cardboard-airframes

**Recovery**
- Instructables parachute calc — https://www.instructables.com/Calculating-the-Performance-of-a-Parachute
- NASA GRC recovery — https://www.grc.nasa.gov/WWW/k-12/VirtualAero/BottleRocket/airplane/rktvrecv.html
- Nakka App. K — https://nakka-rocketry.net/Appendix-K.htm
- Knacke 1992 opening factor, cited in — https://www.redalyc.org/journal/3094/309456744012/html
- Estes 24 in rip-stop — https://edu.estesrockets.com/products/rip-stop-parachute-24-inch
- Estes Pro Series II 24 / 30 in — https://estesrockets.com/products/pro-series-ii-24-inch-nylon-parachute ; https://estesrockets.com/products/pro-series-ii%e2%84%a2-30-inch-nylon-parachute
- Arizona Hobbies 24 / 30 in — https://arizonahobbies.com/products/pro-series-ii%E2%84%A2-24-inch-nylon-parachute ; https://arizonahobbies.com/products/pro-series-ii%e2%84%a2-30-inch-nylon-parachute
- 42 in chute mass — https://the-rocketman.com/?p=3121
- Shock-cord length — https://www.extension.purdue.edu/county/boone/4-H-Youth-Development/rocketry2011.pdf ; https://www.rocketryforum.com/threads/why-4x-the-length-of-rocket-for-shock-cord.129201/ ; https://ssi-wiki.stanford.edu/Special:MobileDiff/1557
- Knot strength — https://wikis.mit.edu/confluence/x/ckP_Bg ; https://link.springer.com/article/10.1007%2Fs40870-015-0015-5 ; https://www.cmcpro.com/?p=121806
- Wadding — https://www.schoolspecialty.com/estes-model-rocket-recovery-wadding-1006149 ; https://stemfinity.com/collections/estes-rockets/products/estes-recovery-wadding ; https://rainbowresource.com/product/000597/Recovery-Wadding-for-rockets.html ; https://store.hobbyetc.com/parts/view/123056
- Nomex protector — https://www.rocketryforum.com/threads/a-cornucopia-of-nomex-parachute-and-shock-cord-protectors.169577/
- Kevlar chute protector — https://giantleaprocketry.com/products/kevlar-chute-protector-up-to-2-6-airframe

**Payload (scoping only; not flown)**
- Eggtimer Quasar FAQ — https://eggtimerrocketry.com/quasar/
- Quasar User's Guide 1.02S — https://eggtimerrocketry.com/wp-content/uploads/2024/02/Eggtimer-Quasar-1_02s.pdf
- Quasar forum thread — https://www.rocketryforum.com/threads/the-eggtimer-quasar-a-wifi-enabled-gps-altimeter.175766/
- Eggtimer Apogee — https://www.rocketryforum.com/goto/post?id=2051607 ; https://contrailrockets.com/product/eggtimer-apogee-altimeter
- Estes Altimeter 2246 — https://estesrockets.com/product/002246-estes-altimeter/ ; https://edu.estesrockets.com/products/altimeter
- Jolly Logic AltimeterOne — https://locprecision.com/products/jolly-logic-altimeterone ; https://aeroconsystems.com/product/altimeter-one-by-jolly-logic
- Lucid RB02 beeper — https://lucidtechnologies.info/rb02_11.htm

---

## Changelog

- **2026-11-21 (b0dd66b)**: motor change to the H100W, minimum-diameter (rocket-docs).
  - Briefing rewritten: at-a-glance table for the H100W and rev 3; performance marked H182R basis, superseded; Phase 2 reopened; new top risks.
  - §1: motor and airframe rows; cert check for the H100W.
  - §2: new H100W data, case and ring, delay (UDDT). The H182R material was moved to §2.5 as superseded.
  - §3: sleeve flagged for the CP; new §3.5 on the CFD domain tool.
  - §4: fin can rev 3 (`fin_can_md`) with figures, verify 4/5, loads vs layers, lip bearing and retention. Rev 2 moved to the revision history.
  - §5–§9: marked stale where they depend on the motor; BOM change column; new measurement list.
  - §10: Date column added, plus 2026-11-21 decisions. §11 rebuilt; §12 gains the H100W sources.
  - Figures added: `fin_can_md_rev3_iso.png` and `fin_can_md_rev3_section.png`.
- **2026-11-20 (5741954)**: first full build of this report (rocket-docs). Figures: H182R thrust curve, fin can rev 2 iso and section, margin vs time.

Project history (git log):
- 2026-11-20:
  - 6d16bdd → 095784c: repo skeleton, shop rules, Phase 0 goal, Phase 1 feasibility.
  - 44c87a1 → 8437b9b: subagents, design.yaml, RocketPy; Phase 2 motor (H182R), nosecone, aero.
  - f1494d0, 9c72e0a: owner confirms the H182R, Kevlar and 40 in chute.
  - 7f29410 → b0bd19e: payload scoped, then no payload.
  - 415a24e, c7feb6c: retention sizing; stability sim.
  - b789686 → aa449c0: Phase 3 BOM.
  - 5465fab → 7e1d2cd: fin can design, verify.py and make.py, rev 1, rev 2 (Option A); 90.5 g ballast.
  - 5741954, a8eaef5, eee4948, 51644a5: rocket-docs agent; report PDF tooling; first report build.
- 2026-11-21:
  - a5b9da7: `tools/fluent_domain.py`, Fluent 2D C-domains for the fin root and tip.
  - c717e50: owner switches the motor to the H100W-14A DMS (38 mm); dependent data flagged stale.
  - cfd68fc: fin can rev 3, min-diameter sleeve (`parts/fin_can_md.py`); draft, target mass TBD.
  - 7544078: motor agent sources the H100W data, L1 check, case and ring TBD, lip bearing, retention proposal.
  - b0dd66b: `fin_can_md` case OD 38.10 nominal and motor length 155, from the motor agent.
