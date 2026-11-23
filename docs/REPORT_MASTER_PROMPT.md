# Master prompt — Engineering Design Report (same format as Ms. Piggy, L1C-EDR-001)

Copy everything between the two lines into the other chat. Fill in the `<…>` fields first.

---

Write a professional Engineering Design Report for my rocket **"<ROCKET NAME>"**. It must be in exactly the same
format as the Ms. Piggy report (document L1C-EDR-001), which is built by the tooling in the GitHub repo
**ChunkeMonke/rocket-parts** (branch main).

**If you can access the repo (Claude Code):**

1. Clone it and set up Python: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Needs pandoc and Playwright Chromium.
2. Read these files and follow them exactly:
   - `projects/l1-cheap/report/STYLE.md` (format rules)
   - `tools/report_template.html` and `tools/report_pro.css` (do not change them)
   - `projects/l1-cheap/report/report.md` (the reference report: copy its structure, tone and density)
3. Create `projects/<project-slug>/report/report.md` and `projects/<project-slug>/report/figures/`.
   Build with `tools/report_pdf.sh <project-slug>`.
4. Make a cover render from my CAD with `tools/render_cover.py`, adapted for the new STL path. Save it to `figures/cover_rocket.png`: transparent background, cropped tight.
5. Make an A3 drawing set from my STEP files in the style of `tools/drawing_owner.py`:
   - general arrangement with stations, CG/CP symbols, parts list with masses and notes;
   - aft-end assembly section;
   - one sheet per printed part.
   Use the title block from `tools/drawing.py` `new_sheet(...)`. Insert each sheet with `{.drawing}` so it gets its own landscape page.
6. Open the PDF and look at every page before sending it: no blank or overflow pages, all tables captioned, equations rendered.

**If you cannot access the repo,** produce the same document by these rules:

- **Front matter** (in this order):
  - Cover:
    - "ENGINEERING DESIGN REPORT", the rocket name in large bold, a subtitle and a greyscale render of the rocket.
    - A ruled info box: Document No., Revision, Date, Status, Purpose.
    - A double-line border around the page.
  - Document Control: metadata table, revision history (Rev, Date, Description), approval block (Prepared, Checked, Approved, each with Name, Signature, Date), status-tag legend.
  - Table of Contents with dot leaders and page numbers.
  - List of Figures, then List of Tables.
- **Numbering:**
  - Main sections are numbered "1.0 TITLE" in uppercase; subsections "1.1 Title", then "1.1.1".
  - Executive Summary is unnumbered. Appendices are "APPENDIX A — TITLE".
  - Captions are "Figure 3-2." and "Table 3-1." (section-figure). Table captions go above the table, centred and bold. Figure captions go below.
- **Look:**
  - Black and white only.
  - Body text: Times-style serif, about 11 pt, justified.
  - Headings, tables and captions: Arial-style sans.
  - Tables: thin black grid with light-grey header row.
  - Callouts: plain bordered boxes:
    - a grey-filled SUMMARY box at the top of every section;
    - NOTE;
    - WARNING (heavy border, ⚠);
    - DECISION ("Required before flight").
  - Status tags: small outlined uppercase labels. VALIDATED is the one shown black-filled.
    - VALIDATED: test
    - NOMINAL: published, not measured
    - ESTIMATE
    - PROVISIONAL
    - UNCONFIRMED
  - Images are greyscale, except data plots whose colour encodes values (CFD/FEA contours).
  - Header: "<Rocket> — Engineering Design Report" on the left, "<Doc No> · Rev X" on the right. Footer: date, "Page N of M", status.
- **Structure:**
  - Executive Summary (≤ 2 pages):
    - purpose and configuration paragraphs;
    - an 8-tile key-results grid (value + label + basis);
    - Key Findings (numbered, bold lead-in);
    - Recommendations in a DECISION box.
  - 1.0 Introduction: scope, mission, requirements table with a compliance column, conventions.
  - 2.0 Vehicle Configuration: general-arrangement drawing first, layout, components, mass properties.
  - 3.0 Propulsion.
  - 4.0 Aerodynamics: CP by method in one table, drag, CFD if any.
  - 5.0 Structures.
  - 6.0 Stability & Flight Performance: all margin bases in one table, ballast, simulation, delay.
  - 7.0 Recovery.
  - 8.0 Manufacturing & Assembly: print settings, drawing register, drawings.
  - 9.0 Verification, Risks & Open Items: verification matrix, risk register (likelihood × severity), open-items table, decisions needed.
  - 10.0 Conclusions & Recommendations.
  - Appendices:
    - A design history
    - B figure gallery
    - C analysis detail
    - D simulation-model review
    - E decision log
    - F references [R#]
    - G data sources & traceability [D#]
    - H analysis tools
- **Voice:**
  - Impersonal technical voice, passive or noun phrases.
  - No "owner", "you", "we", "for the client"; avoid pronouns (if unavoidable, "I").
  - Short declarative sentences. Every number has units and its basis.
  - Never invent numbers; mark gaps TBD and list them in 9.0.
  - Cite sources as [R#] / [D#]; no file paths in body text.

**Inputs for this rocket** (I will attach or paste them):

- Rocket name; document number (e.g. `<PREFIX>-EDR-001`, Rev A); date; purpose / flight (event, site, date).
- Motor (designation, delay, how it's retained); body tube (make/size, OD/ID, length); nose cone (shape, length, mass); fins (count, root/tip chord, span, sweep, thickness, material).
- OpenRocket file or its PDF export: mass, CG, CP, stability, apogee, max velocity, optimum delay, landing speed, part list with masses.
- Weighed or slicer masses of the printed parts, and print settings.
- STEP files of the printed parts (for the drawings and cover render).
- Recovery: chute size and material, shock cord, attachment, deployment method.
- Any analysis already done (CFD, FEA, test prints, ground tests), with results.
- Budget and target stability margin.

---
