"""Build the professional engineering report PDF.

  .venv/bin/python tools/report_build.py [project] [--md FILE] [--out FILE]

pandoc markdown + YAML metadata (see projects/<p>/report/STYLE.md) -> HTML (tools/report_template.html,
tools/report_pro.css) -> Chromium PDF in two passes (pass 1 finds the page of every section, pass 2 writes the
page numbers into the contents). The cover is printed without header/footer and merged in front.
"""
import argparse
import html as H
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent.parent


def pandoc(md: Path, out: Path, resdir: Path):
    subprocess.run(["pandoc", str(md), "-f", "markdown-tex_math_dollars+tex_math_single_backslash", "-t", "html5",
                    "--template", str(ROOT / "tools/report_template.html"), "--toc", "--toc-depth=2",
                    "--number-sections", "--mathml", "--css", str(ROOT / "tools/report_pro.css"),
                    "--embed-resources", "--resource-path", str(resdir), "-o", str(out)], check=True)


def prep(html: str):
    """Add page markers to h1/h2 in the body; restructure TOC links; return html and the id order."""
    ids = []
    head, sep, body = html.partition('<main class="body">')

    def mark(m):
        ids.append(m.group(2))
        return f'{m.group(1)}<span class="mk">QZ{len(ids) - 1:03d}ZQ</span>'
    body = re.sub(r'(<h[12][^>]*\bid="([^"]+)"[^>]*>)', mark, body)

    def toc(m):
        inner = m.group(3)
        num = re.search(r'<span class="toc-section-number">.*?</span>', inner)
        num_s = num.group(0) if num else ""
        txt = inner.replace(num_s, "").strip()
        return f'<a href="#{m.group(1)}"{m.group(2)}><span class="tt">{num_s}{txt}</span><span class="pg" data-id="{m.group(1)}"></span></a>'
    head = re.sub(r'<a href="#([^"]+)"([^>]*)>(.*?)</a>', toc, head, flags=re.S)
    return head + sep + body, ids


def print_pdf(html: Path, pdf: Path, ranges: str, hf: bool, meta: dict):
    hl = H.escape(f'{meta.get("title", "")} — Engineering Design Report')
    hr = H.escape(f'{meta.get("docnumber", "")} · Rev {meta.get("revision", "")}')
    fl = H.escape(str(meta.get("date", "")))
    fr = H.escape(str(meta.get("footer_right", "Released for build")))
    subprocess.run(["node", str(ROOT / "tools/report_print.js"), str(html), str(pdf), ranges, "1" if hf else "0",
                    hl, hr, fl, fr], check=True, cwd=ROOT)


def pages_of(pdf: Path, n: int):
    txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout.split("\f")
    found = {}
    for pi, t in enumerate(txt):
        for k in re.findall(r"QZ(\d{3})ZQ", t.replace(" ", "")):
            found.setdefault(int(k), pi + 1)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default="l1-cheap")
    ap.add_argument("--md"); ap.add_argument("--out")
    a = ap.parse_args()
    rd = ROOT / "projects" / a.project / "report"
    md = Path(a.md) if a.md else rd / "report.md"
    out = Path(a.out) if a.out else rd / "report.pdf"
    meta = yaml.safe_load(md.read_text().split("---", 2)[1])
    meta["footer_right"] = str(meta.get("status", "")).split("—")[0].strip()
    tmp = Path(tempfile.mkdtemp())
    raw = tmp / "raw.html"
    pandoc(md, raw, rd)
    html, ids = prep(raw.read_text())
    h1 = rd / "report.html"
    h1.write_text(html)
    p1 = tmp / "pass1.pdf"
    print_pdf(h1, p1, "", True, meta)
    pg = pages_of(p1, len(ids))
    idpage = {ids[k]: v for k, v in pg.items()}
    html2 = re.sub(r'<span class="pg" data-id="([^"]+)"></span>',
                   lambda m: f'<span class="pg">{idpage.get(m.group(1), "")}</span>', html)
    h1.write_text(html2)
    n = len(PdfReader(str(p1)).pages)
    cov, body = tmp / "cover.pdf", tmp / "body.pdf"
    print_pdf(h1, cov, "1", False, meta)
    print_pdf(h1, body, f"2-{n}", True, meta)
    w = PdfWriter()
    for f in (cov, body):
        for p in PdfReader(str(f)).pages:
            w.add_page(p)
    w.add_metadata({"/Title": f'{meta.get("title")} — {meta.get("subtitle")}', "/Subject": str(meta.get("docnumber"))})
    with open(out, "wb") as fh:
        w.write(fh)
    missing = [i for k, i in enumerate(ids) if k not in pg]
    print(out, f"{n} pages; sections found {len(pg)}/{len(ids)}", "missing: " + ", ".join(missing[:5]) if missing else "")


if __name__ == "__main__":
    main()
