// R29 시작 화면: 켠 직후(가림막) · 조기 Enter(예약) · 자동 시작 · 콘솔 에러
const { open } = require('./h');
const OUT = process.argv[2];
(async () => {
  const t0 = Date.now();
  const { browser, page, errors } = await open('http://127.0.0.1:8030/index.html', { w: 1280, h: 720, dsf: 1 });
  const g0 = await page.evaluate(() => window.__RELIC_DEV.titleGate());
  console.log('at load', Date.now() - t0, 'ms', JSON.stringify({ open: g0.open, p: g0.p, info: g0.info, label: g0.label }));
  await page.screenshot({ path: OUT + '/r29_t0_curtain.png' });
  const lab = await page.evaluate(() => [...document.querySelectorAll('button')].map((b) => b.textContent).filter((t) => /START|불러오는|곧 시작/.test(t)));
  console.log('labels', JSON.stringify(lab));
  await page.keyboard.press('Enter');
  await page.waitForTimeout(120);
  const g1 = await page.evaluate(() => ({ gate: window.__RELIC_DEV.titleGate(), st: window.__RELIC_DEV.assets.status(1) }));
  console.log('after early Enter', JSON.stringify({ pending: g1.gate.pending, open: g1.gate.open, label: g1.gate.label, st: g1.st }));
  await page.screenshot({ path: OUT + '/r29_t1_pending.png' });
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  console.log('ready at', Date.now() - t0, 'ms');
  await page.waitForTimeout(700);
  const g2 = await page.evaluate(() => ({ gate: window.__RELIC_DEV.titleGate(), playing: !!(window.__RELIC && window.__RELIC.player && window.__RELIC.player.x), tick: window.__RELIC.tick }));
  console.log('after ready', JSON.stringify(g2));
  await page.screenshot({ path: OUT + '/r29_t2_started.png' });
  console.log('errors', errors.length, JSON.stringify(errors.slice(0, 5)));
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
