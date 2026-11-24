// SVG → PNG (dsf 2 렌더 후 PIL로 512 축소는 별도) — 사용: node render_svg.js IN_DIR OUT_DIR [size]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [inDir, outDir, sizeArg] = process.argv.slice(2);
  const size = +(sizeArg || 512);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: size, height: size }, deviceScaleFactor: 2 });
  const files = fs.readdirSync(inDir).filter((f) => f.endsWith('.svg')).sort();
  for (const f of files) {
    const svg = fs.readFileSync(path.join(inDir, f), 'utf8');
    await page.setContent(`<!doctype html><html><head><style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body>${svg}</body></html>`);
    await page.screenshot({ path: path.join(outDir, f.replace(/\.svg$/, '@2x.png')), omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
  }
  await browser.close();
  console.log('rendered', files.length);
})();
