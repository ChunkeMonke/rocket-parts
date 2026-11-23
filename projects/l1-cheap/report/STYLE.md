# Report style guide — l1-cheap Engineering Design Report

Owner request 2026-11-23: "make the report look like a professional engineering report that cost a lot of money to make,
at least 10k dollars. It should be professional, easy to read, and organized."

The PDF is built by `tools/report_pdf.sh l1-cheap` (pandoc markdown -> HTML template `tools/report_template.html`
+ `tools/report.css` -> Chromium PDF, two passes for TOC page numbers). The cover page, document-control page and
table of contents are generated from the YAML metadata block. Do NOT write them by hand.

## 1. File format (pandoc markdown, not GFM)

Start the file with a YAML metadata block:

```yaml
---
title: "Pepto B. #2"
subtitle: "Level 1 Minimum-Diameter Rocket — Engineering Design Report"
docnumber: "L1C-EDR-001"
revision: "D"            # bump one letter per owner-visible release
date: "2026-11-23"
status: "Released for build — open items listed in §10"
prepared_for: "Project owner (Tripoli Level 1 certification flight)"
prepared_by: "l1-cheap design team (rocket-parts)"
revisions:               # newest first, max ~8 rows
  - {rev: "D", date: "2026-11-23", description: "Professional restructure; owner SolidWorks design basis; slicer masses; corrected CG"}
---
```

- Do not write a level-1 title heading. Top-level sections are `#` headings, numbered automatically. Never type numbers into headings.
- Executive summary: `# Executive Summary {.unnumbered}`.
- Appendices: `# Appendix A — Title {.unnumbered .appendix}`, with subsections `## A.1 Title {.unnumbered}`.
- Use `{#sec-id}` anchors on major sections and cross-reference them as `[§4](#sec-aero)`.

## 2. Structure (main body ≤ ~45 pages, history goes to the appendices)

1. Executive Summary (≤ 2 pages):
   - purpose;
   - configuration in one paragraph;
   - **Key Results** table;
   - **Findings**;
   - **Recommendations** (numbered, actionable);
   - **Open items** (top 5).
2. Introduction: scope, mission, requirements (table with a compliance column), conventions (units, reference diameter, coordinate origin = nose tip).
3. Vehicle Configuration: overview figure, layout table, component descriptions, mass-properties table.
4. Propulsion: motor data, thrust curve, retention, delay selection.
5. Aerodynamics: method overview; CP by method (Barrowman / OpenRocket / CFD) in one comparison table; drag; CFD results (a few key figures, the rest in the appendix); the owner-vs-rev 9 question with its uncertainty.
6. Structures: load cases, FEA method and calibration, results table, margins.
7. Stability & Flight Performance: mass budget, static margin (all bases in one table), ballast, flight simulation, delay.
8. Recovery: scheme, chute, descent, shock cord, ejection, pack position (WARNING).
9. Manufacturing & Assembly: print settings, the validated thread, assembly sequence, deliverables (drawings, guides).
10. Verification, Risks & Open Items: verification matrix (requirement → method → status), risk register (likelihood × severity), open-items table.
11. Conclusions & Recommendations.

Appendices:

- **A** Design history (fin can revs 2–9, nose, superseded analyses: keep the content, condensed).
- **B** CFD figure gallery.
- **C** FEA detail and ANSYS calibration.
- **D** OpenRocket model review and owner OR files.
- **E** Decision log.
- **F** References.
- **G** Data sources & traceability (file paths).
- **H** Analysis tools.

## 3. Writing

- Write like a consulting engineering report: short declarative sentences, one idea per paragraph. Never write "main session", "agent", "owner said in chat" or similar; say "the design team" or "the project owner".
- Lead each section with a 1–3 sentence **summary** in a `::: summary` box.
- Every number carries units and its basis. Status words appear as small tags: `[ESTIMATE]{.tag}`, `[PROVISIONAL]{.tag}`, `[UNCONFIRMED]{.tag}`, `[NOMINAL]{.tag}`, `[VALIDATED]{.tag .ok}`.
- Callouts (fenced divs). The first line is the bold title.

  ```
  ::: warning
  **Recovery pack position**
  Text…
  :::
  ```

  Classes: `summary`, `note`, `warning`, `decision`, `result`.
- Sources: no file paths or long code spans in body text. Cite as `[R3]`, `[D2]` (references / data sources in Appendices F and G). Code spans only for parameter names, sparingly.

## 4. Figures and tables

- Figure: an image alone in its own paragraph, with the caption as alt text, e.g.
  `![Owner fin can — CFD surface pressure at 100 m/s, α = 4°.](figures/cfd/owner/gallery/06_fincan_Cp_iso_windward.png){width=85%}`
  Captions are numbered automatically. Do not type "Figure N".
- Main body: ≤ ~30 figures, only the ones that carry a conclusion. Everything else goes in Appendix B.
- Tables: pipe tables, ≤ 6 columns, short cells. Put the caption line `Table: Caption text.` directly **below** the table (pandoc syntax). Numbered automatically.
- Bold sparingly: key result values only.
