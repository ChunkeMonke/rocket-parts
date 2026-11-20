# Project: l1-cheap — Phase 2 Recovery

**Status:** Phase 2 draft, 2026-11-20. The total mass, length, apogee and delay are still
unknown because other agents are working in parallel. All mass-dependent results are
given over a **placeholder descent mass range of 450–700 g**, a range the main session set.
It is not a sim value.
Calc script: `/tmp/claude-0/-home-user/c895d01b-a099-5773-be20-859042f2dc61/scratchpad/rec.py`
(scratch only; the formulas are written out below).

## 1. Deployment scheme

**Proposal: single deploy on the H182R-14A's own ejection charge.** The owner must confirm.
- `inventory.yaml` lists no electronics. An altimeter would cost money the $95 budget doesn't have.
- feasibility.md §5 already plans on motor ejection and rates the project difficulty 3/5 on that basis.
- Risks:
  - The charge size is unpublished (motor.md), and a DMS charge can't be ground tested on its own.
  - The 38.735 mm × up to 34" (864 mm) tube has a large free volume: π/4 × 3.8735² cm² = **117.8 cm³ per 100 mm** of empty tube.
  - Mitigations:
    - Keep the volume between the motor and the nose shoulder short. This depends on where stability and payload put things.
    - Use a nose friction fit that is *just* firm enough to hold in flight. The nosecone agent owns that fit.

## 2. Parachute sizing

Steady descent: D = √(8 m g / (π ρ Cd v²)).
- ρ = 1.225 kg/m³, ISA sea level. Palm Bay is near sea level.
- g = 9.80665 m/s².
- Circular canopy area assumed. Estes canopies are polygons, so their real area may be smaller (unverified).

**Cd.** Sources disagree on the Cd of a flat sheet:
- **0.75** (design value, conservative): [Instructables parachute calc](https://www.instructables.com/Calculating-the-Performance-of-a-Parachute), [NASA GRC](https://www.grc.nasa.gov/WWW/k-12/VirtualAero/BottleRocket/airplane/rktvrecv.html), and Van Milligan as cited there.
- **1.5** (optimistic bound): [Nakka App. K](https://nakka-rocketry.net/Appendix-K.htm).

All accessed 2026-11-20.

**Required diameter (in)**

| Descent rate | Cd | 450 g | 575 g | 700 g |
|---|---|---|---|---|
| 4.5 m/s (14.8 ft/s) | 0.75 | 30.6 | 34.6 | 38.2 |
| 5.5 m/s (18.0 ft/s) | 0.75 | 25.0 | 28.3 | 31.2 |
| 6.5 m/s (21.3 ft/s) | 0.75 | 21.2 | 23.9 | 26.4 |
| 4.5 m/s | 1.5 | 21.6 | 24.5 | 27.0 |
| 5.5 m/s | 1.5 | 17.7 | 20.0 | 22.1 |
| 6.5 m/s | 1.5 | 15.0 | 16.9 | 18.7 |

D scales with √m. Doubling the mass needs 1.41× the diameter.

**Descent rate of the cheap chutes (m/s)**

| Chute | Cd | 450 g | 575 g | 700 g |
|---|---|---|---|---|
| 24" | 0.75 | 5.74 | 6.49 | 7.16 |
| 24" | 1.5 | 4.06 | 4.59 | 5.06 |
| 30" | 0.75 | 4.59 | 5.19 | 5.72 |
| 30" | 1.5 | 3.25 | 3.67 | 4.05 |

**Prices (2026-11-20)**
- 24":
  - Estes rip-stop, $10.25 ([feasibility.md](https://edu.estesrockets.com/products/rip-stop-parachute-24-inch))
  - Estes Pro Series II, $14.99 ([Estes](https://estesrockets.com/products/pro-series-ii-24-inch-nylon-parachute)), or $12.95 ([Arizona Hobbies](https://arizonahobbies.com/products/pro-series-ii%E2%84%A2-24-inch-nylon-parachute))
- 30" Estes Pro Series II, $19.99 ([Estes](https://estesrockets.com/products/pro-series-ii%e2%84%a2-30-inch-nylon-parachute)), or $16.95 ([Arizona Hobbies](https://arizonahobbies.com/products/pro-series-ii%e2%84%a2-30-inch-nylon-parachute))
- Shipping is TBD.

**Reading the tables.** On the conservative Cd:
- A 24" chute is only fine at ≥ 6.5 m/s up to about 575 g, or at ≤ 5.74 m/s if the rocket is about 450 g.
- A 30" chute stays at or below 5.7 m/s across the whole range.

The pick waits on the owner's target rate and stability's mass.

Field reports of about 16–17 ft/s (about 5 m/s) design targets are anecdotal. I found no Tripoli L1 rule on descent rate.

## 3. Shock cord

- **Length: 3× rocket length.** Rocket length means `stability.total_length_mm`, which is TBD. This is a rule of thumb, with 2–3× body tube and 3–5× also quoted. Sources: [Purdue 4-H](https://www.extension.purdue.edu/county/boone/4-H-Youth-Development/rocketry2011.pdf), [TRF](https://www.rocketryforum.com/threads/why-4x-the-length-of-rocket-for-shock-cord.129201/), [Stanford SSI wiki](https://ssi-wiki.stanford.edu/Special:MobileDiff/1557), accessed 2026-11-20.
  - Floor: if the full 34" tube is used, 3 × 864 mm = **2.6 m minimum** before the nose and fin can are added.
- **Layout:**
  - Aft anchor → long Kevlar run → chute loop at about ⅓ of the cord length from the nose end → nose eye.
  - With the chute loop off-centre, the nose and body hang at different heights and can't swing into each other. This is common practice; I have no source for the ⅓ figure.
  - Use a Z-fold with masking-tape bundles, so the cord pays out instead of snapping taut all at once.
- **Strength (estimate).**
  - Opening load: F = ½ρv²·Cd·A·Cx, with Cx = 1.6 from Knacke 1992, cited in [this paper](https://www.redalyc.org/journal/3094/309456744012/html). For a 24" chute at Cd 0.75:

    | v at deploy | 5 m/s | 10 | 20 | 30 | 40 |
    |---|---|---|---|---|---|
    | F (N) | 5 | 21 | 86 | 193 | 343 |

  - Design case 40 m/s (late or early deploy) × safety factor 3 gives **≥ 1030 N rated, after knot losses**. The SF of 3 is my proposal; the owner sets it. Knots reduce cord strength substantially ([MIT wiki](https://wikis.mit.edu/confluence/x/ckP_Bg)), so use the rating *after* knots, or sewn or spliced loops.
  - Separation snatch is not computed. It is F = v_rel·√(k·μ), with μ = m_nose·m_body / (m_nose + m_body) and k = EA/L of the cord. v_rel and the cord's EA are both unknown.
  - Compare against the rating once the owner gives the cord spec. The opening-load estimate stands until then.

## 4. Attachment points

General check for any printed anchor: σ = F·SF / A_net ≤ 15 MPa interlayer shear. That is A_net ≥ F·SF / 15:

| F | 50 N | 100 N | 200 N | 400 N |
|---|---|---|---|---|
| A_net (mm²), SF 3 | 10 | 20 | 40 | 80 |

For F = 343 N, A_net ≥ 69 mm².

**Aft anchor (fin can).**
- motor.md prints the can axis-vertical. The cord pulls the anchor **forward, along Z**, so it pulls the layers apart (interlayer tension). That is the weak direction.
- A bar across the bore is **not allowed**: it would sit in the ejection gas path. Instead:
  - Run two axial holes through the annular web forward of the motor, off-axis, and pass the Kevlar loop around a printed bridge between them.
  - The bridge is printed in-layer (XY) and loaded in bending and shear within the layers.
  - The reaction then runs through the can wall to the shoulder joint in Z tension.
- Check: the solid section on the weakest layer plane must have A_net ≥ 69 mm².
  - Example only: a 38.6 mm OD wall ring with 2.6 mm of solid walls is about 294 mm², about 3.5 MPa at SF 3. These are not the real dimensions.
- **Lower-risk alternative:** epoxy a Kevlar leader along the paper tube ID for about 100 mm (length TBD) forward of the can. No PETG layers are then in the load path. The owner's epoxy is already owned.

**Nose eye.**
- The cord pulls the nose **aft along Z**, assuming a tip-up print, which the nosecone agent decides. The shoulder wall is in interlayer tension. Same A_net check.
- Use a cross-bar or eye at the shoulder base, printed in-layer.
- Load: the same 343 N design case.

## 5. Ejection protection

- **Proposal: Estes recovery wadding, 75 sheets, $5.43–$5.99.** Sources: [School Specialty](https://www.schoolspecialty.com/estes-model-rocket-recovery-wadding-1006149), [STEMfinity](https://stemfinity.com/collections/estes-rockets/products/estes-recovery-wadding), [Rainbow Resource](https://rainbowresource.com/product/000597/Recovery-Wadding-for-rockets.html), 2026-11-20. Load it between the motor and the chute; the amount is set on the bench.
- Alternative: a reusable Nomex 6"×6" protector for 1–2" tubes, $5.00, from a forum vendor listing that may be stale ([TRF](https://www.rocketryforum.com/threads/a-cornucopia-of-nomex-parachute-and-shock-cord-protectors.169577/)), plus shipping TBD.
- A Kevlar blanket at $11.50 ([Giant Leap](https://giantleaprocketry.com/products/kevlar-chute-protector-up-to-2-6-airframe)) is over budget.
- The Kevlar leader in the gas path doesn't need protection.

## 6. Timing, packing, drift

- **Delay.** Delay = t_apogee − t_burnout. The motor's delay timer starts at burnout.
  - Ask stability for vertical and total speed and altitude at ejection for each candidate delay from 14 s downward.
  - **Flag if speed at ejection > 10 m/s.** This threshold is my proposal: at 10 m/s the opening load is only about 21 N on a 24" chute, against 86 N at 20 m/s.
- **Packing.** The packed chute + cord + wadding volume is TBD. Do a pack test with the actual chute, then set the bay length: tube free volume is 117.8 cm³ per 100 mm, and the pack must not be hard.
- **Drift.** Drift ≈ wind × apogee / v_descent. Apogee and the field's wind are TBD.
  - Per 100 m of apogee at 5.5 m/s descent, the rocket is under canopy for 18.2 s.
  - At 2.2, 4.5 and 6.7 m/s of wind (5, 10 and 15 mph), that is 40, 82 and 122 m of drift.
