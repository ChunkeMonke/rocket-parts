#!/usr/bin/env bash
# Render a project's living report to PDF:  tools/report_pdf.sh [project]   (default l1-cheap)
# Markdown -> standalone HTML (pandoc, MathML equations) -> PDF (headless Chromium via Playwright).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${1:-l1-cheap}"
DIR="$ROOT/projects/$PROJECT/report"
MD="$DIR/report.md"
HTML="$DIR/report.html"
PDF="$DIR/report.pdf"
[ -f "$MD" ] || { echo "no report at $MD" >&2; exit 1; }

pandoc "$MD" -f gfm+tex_math_dollars -t html5 --standalone --mathml \
  --metadata title="$(head -1 "$MD" | sed 's/^# //')" \
  --css "$ROOT/tools/report.css" --embed-resources \
  --resource-path="$DIR" -o "$HTML"

node -e '
const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + process.argv[1], { waitUntil: "load" });
  await p.pdf({ path: process.argv[2], format: "Letter", printBackground: true,
    margin: { top: "16mm", bottom: "18mm", left: "16mm", right: "16mm" },
    displayHeaderFooter: true, headerTemplate: "<span></span>",
    footerTemplate: "<div style=\"font-size:8px;width:100%;text-align:center;color:#666\">" +
      process.argv[3] + " — page <span class=pageNumber></span> / <span class=totalPages></span></div>" });
  await b.close();
})();' "$HTML" "$PDF" "$PROJECT design & research report"
echo "$PDF"
