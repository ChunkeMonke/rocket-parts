# rocket-parts — working notes for Claude

- Shop rules and constants: `skills/SKILL.md`. Project workflow: `skills/build-planner/SKILL.md`.
- Python: always `.venv/bin/python` (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`).
- Parts: `python make.py <part> --rev N`. Never call a part good unless every verify check passes
  and the renders have been opened and looked at.
- **Living report:** after every phase completion or rocket-agent result, run the `rocket-docs`
  agent to update `projects/<project>/report/report.md` before replying to the owner (owner request 2026-11-20).
  It returns the text between `=== BEGIN/END report.md ===` markers; save it verbatim, then run
  `tools/report_pdf.sh <project>` and look at the PDF pages before sharing.
- Commit and push after each meaningful change.
