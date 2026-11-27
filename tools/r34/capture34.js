// R34 납품 이미지 — 음향 점검 페이지(동작 확인 포함) · 4시대 달리는 척준경(색 보정 뒤) · 격파 수 표시
const { open, toEra } = require('./h');
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8037;
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  // ① 음향 점검 페이지: 휴대폰 폭으로 열어 버튼을 실제로 눌러 본다(루프 1 · 효과음 1 · 순서 1)
  const b0 = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const p0 = await b0.newPage({ viewport: { width: 420, height: 900 }, deviceScaleFactor: 2 });
  const errs = [];
  p0.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  p0.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  await p0.goto(`http://127.0.0.1:${PORT}/sound-check.html`);
  const nb = await p0.locator('button').count();
  await p0.locator('#amb button').first().click();
  await sleep(1900);
  await p0.locator('#smp button.new').first().click();
  await p0.locator('#seqB').click();
  await sleep(700);
  const st = await p0.evaluate(() => ({ ac: ac && ac.state, cur: cur && cur.key, gain: cur && Math.round(cur.g.gain.value * 100) / 100, loaded: Object.keys(buf).length, overflow: document.documentElement.scrollWidth > window.innerWidth }));
  await p0.screenshot({ path: `${OUT}/sound_check.png` });
  console.log('sound-check', JSON.stringify({ buttons: nb, st, errs }));
  await b0.close();
  // ② 게임: 4시대 거란 전선에서 달리는 척준경
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1000);
  await page.evaluate(() => window.__RELIC_DEV.r31autoQuiz(true));
  await toEra(page, 4);
  await sleep(2500);
  await page.evaluate(() => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 0; p.x = g.cameraX + 200; });
  await page.keyboard.down('ArrowRight');
  await sleep(520);
  await page.screenshot({ path: `${OUT}/e4_run.png` });
  await page.keyboard.up('ArrowRight');
  await sleep(500);
  await page.screenshot({ path: `${OUT}/e4_idle.png` });
  console.log('game errors', errors.length);
  await browser.close();
})().catch((e) => { console.error('CAPTURE CRASH', e); process.exit(1); });
