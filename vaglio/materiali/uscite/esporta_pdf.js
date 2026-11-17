// Esporta i PDF scaricabili dalle pagine web di Vaglio.
// Uso, da vaglio/materiali/uscite/:   node esporta_pdf.js
// Richiede Node e Playwright (con Chromium). Scrive in ./pdf/.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const HERE = __dirname;
const OUT = path.join(HERE, "pdf");
const DATE = "17 nov 2026";

// larghezza della finestra = area stampabile A4 (210 mm meno i margini) + i 32 px di margine laterale della pagina,
// cosi' i grafici, disegnati alla larghezza reale, entrano esattamente nella pagina
const mmToPx = (mm) => Math.round((mm / 25.4) * 96);
const JOBS = [
  { src: "rapporto/index.html", hash: "#it", out: "Vaglio_rapporto_IT.pdf", margin: 15, label: `Vaglio · Rapporto · ${DATE}` },
  { src: "rapporto/index.html", hash: "#en", out: "Vaglio_report_EN.pdf", margin: 15, label: `Vaglio · Report · 17 Nov 2026` },
  { src: "pubblico/index.html", hash: "", out: "Sotto_la_foresta.pdf", margin: 14, label: "Sotto la foresta · Vaglio · Mirko Tornani" },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  for (const job of JOBS) {
    const width = mmToPx(210 - 2 * job.margin) + 32;
    const page = await browser.newPage({ viewport: { width, height: 1100 }, colorScheme: "light", deviceScaleFactor: 2, locale: "it-IT" });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("file://" + path.join(HERE, job.src) + job.hash, { waitUntil: "networkidle" });
    await page.evaluate(async () => {
      document.querySelectorAll('img[loading="lazy"]').forEach((i) => { i.loading = "eager"; });
      await Promise.all([...document.images].map((i) => (i.complete ? null : new Promise((r) => { i.onload = i.onerror = r; }))));
      await document.fonts.ready;
    });
    const footer = `<div style="width:100%;padding:0 ${job.margin}mm;font:7pt Helvetica,Arial,sans-serif;color:#66726c;display:flex;justify-content:space-between;">`
      + `<span>${job.label}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
    const file = path.join(OUT, job.out);
    await page.pdf({
      path: file, format: "A4", printBackground: true, displayHeaderFooter: true,
      headerTemplate: "<div></div>", footerTemplate: footer,
      margin: { top: `${job.margin}mm`, bottom: `${job.margin + 4}mm`, left: `${job.margin}mm`, right: `${job.margin}mm` },
    });
    console.log(job.out, Math.round(fs.statSync(file).size / 1024) + " KB", errors.length ? errors : "");
    await page.close();
  }
  await browser.close();
})();
