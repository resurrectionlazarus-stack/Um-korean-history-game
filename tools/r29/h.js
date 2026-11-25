// shared Playwright harness (test-only: routes cdnjs React to local npm copies)
const { chromium } = require('playwright');
const path = require('path');
const NPM = path.join(__dirname, '..', 'npm');
async function open(url, { w = 1280, h = 720, dsf = 1 } = {}) {
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dsf });
  await ctx.route('https://cdnjs.cloudflare.com/**', (r) => {
    const u = r.request().url();
    const f = u.includes('react-dom') ? 'react-dom-18.3.1/umd/react-dom.production.min.js' : 'react-18.3.1/umd/react.production.min.js';
    r.fulfill({ path: path.join(NPM, f), contentType: 'application/javascript' });
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__RELIC && window.__RELIC_DEV, null, { timeout: 30000 });
  return { browser, page, errors };
}
async function start(page) {
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC && window.__RELIC.player && window.__RELIC.stats && window.__RELIC.tick > 30, null, { timeout: 20000 });
}
async function toEra(page, era) {
  for (let i = 0; i < 8; i++) {
    const cur = await page.evaluate(() => window.__RELIC.era);
    if (cur >= era) break;
    await page.evaluate(() => window.__RELIC_DEV.advance());
    await page.waitForTimeout(400);
  }
  // wait assets ready
  await page.waitForFunction((e) => { const D = window.__RELIC_DEV; return D.assets.status(e) === 'ready' || D.assets.status(e) === 'none' || D.assets.status(e) === 'failed'; }, era, { timeout: 60000 });
}
module.exports = { open, start, toEra };
