// SVG → PNG(각 SVG의 width · height 그대로, dsf 2) — 사용: node render2.js IN_DIR OUT_DIR
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [inDir, outDir] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 2 });
  const files = fs.readdirSync(inDir).filter((f) => f.endsWith('.svg')).sort();
  for (const f of files) {
    const svg = fs.readFileSync(path.join(inDir, f), 'utf8');
    const w = +(/width="(\d+)"/.exec(svg) || [0, 512])[1], h = +(/height="(\d+)"/.exec(svg) || [0, 512])[1];
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<!doctype html><html><head><style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body>${svg}</body></html>`);
    await page.screenshot({ path: path.join(outDir, f.replace(/\.svg$/, '@2x.png')), omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
  }
  await browser.close();
  console.log('rendered', files.length);
})();
