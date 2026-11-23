// node tools/report_print.js HTML PDF RANGES HEADERFOOTER(0|1) HEADER_LEFT HEADER_RIGHT FOOTER_LEFT FOOTER_RIGHT
const { chromium } = require("playwright");
const [html, pdf, ranges, hf, hl, hr, fl, fr] = process.argv.slice(2);
const st = "font-family:Inter,Arial,sans-serif;font-size:7.5px;color:#5e6873;width:100%;padding:0 18mm;display:flex;justify-content:space-between;";
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + html, { waitUntil: "load" });
  const opt = { path: pdf, format: "Letter", printBackground: true, preferCSSPageSize: true };
  if (ranges) opt.pageRanges = ranges;
  if (hf === "1") {
    opt.displayHeaderFooter = true;
    opt.headerTemplate = `<div style="${st}border:0;"><span style="color:#0e2742;font-weight:600">${hl}</span><span>${hr}</span></div>`;
    opt.footerTemplate = `<div style="${st}"><span>${fl}</span><span style="color:#0e2742;font-weight:600">Page <span class="pageNumber"></span> of <span class="totalPages"></span></span><span>${fr}</span></div>`;
  } else {
    opt.displayHeaderFooter = false;
  }
  await p.pdf(opt);
  await b.close();
})();
