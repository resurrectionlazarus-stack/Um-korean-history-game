// R35 실제 조작 재현 — 공격 도중 방향 전환 · 왼쪽으로 걷기/공격을 실제 키 입력으로 하고 연속 촬영
//  node tools/r35/turn_check.js <out-dir> [port] [era=4]
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8038;
const ERA = +(process.argv[4] || 4);
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(800);
  await page.evaluate(() => window.__RELIC_DEV.r31autoQuiz(true));
  await toEra(page, ERA);
  await sleep(2200);
  await page.evaluate(() => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 1e9; p.x = g.cameraX + 480; p.z = 450; });
  const geo = await page.evaluate(() => { const c = [...document.querySelectorAll('canvas')].sort((a, b) => b.width * b.height - a.width * a.height)[0]; const r = c.getBoundingClientRect(); return { left: r.left, top: r.top, w: r.width, h: r.height }; });
  const snap = async (tag, n, gap) => {
    for (let i = 0; i < n; i++) {
      const st = await page.evaluate(() => { const g = window.__RELIC, p = g.player; return { x: p.x - g.cameraX, z: p.z, f: p.facing, at: p.attackTimer, st: p.state, fr: p._assetFrame, cs: p.comboStep }; });
      const sc = geo.w / 960;
      const cx = Math.round(geo.left + st.x * sc), cy = Math.round(geo.top + st.z * sc);
      const clip = { x: Math.max(0, Math.min(1280 - 380, cx - 190)), y: Math.max(0, cy - 290), width: 380, height: 340 };
      await page.screenshot({ path: `${OUT}/${tag}_${String(i).padStart(2, '0')}.png`, clip });
      fs.appendFileSync(`${OUT}/log.txt`, `${tag}_${i} ${JSON.stringify(st)}\n`);
      if (gap) await sleep(gap);
    }
  };
  // ① 오른쪽 보고 공격 3연타 → 공격 도중 왼쪽 키
  await page.keyboard.press('ArrowRight'); await sleep(200);
  await page.keyboard.down('j'); await sleep(60); await page.keyboard.up('j');
  await sleep(120);
  await page.keyboard.down('ArrowLeft');
  await snap('turnMidAtk', 8, 0);
  await page.keyboard.up('ArrowLeft');
  await sleep(500);
  // ② 왼쪽 보고 제자리 공격 4연타
  for (let k = 0; k < 4; k++) { await page.keyboard.down('j'); await sleep(50); await page.keyboard.up('j'); await snap('atkL' + k, 4, 0); await sleep(120); }
  await sleep(600);
  // ③ 왼쪽으로 걷기
  await page.keyboard.down('ArrowLeft'); await sleep(200); await snap('walkL', 8, 30); await page.keyboard.up('ArrowLeft');
  await sleep(300);
  // ④ 좌우 연타(방향만 빠르게 전환)
  for (let k = 0; k < 3; k++) { await page.keyboard.down('ArrowRight'); await sleep(70); await page.keyboard.up('ArrowRight'); await snap('flipR' + k, 1, 0); await page.keyboard.down('ArrowLeft'); await sleep(70); await page.keyboard.up('ArrowLeft'); await snap('flipL' + k, 1, 0); }
  console.log('errors', errors.length, errors.slice(0, 3));
  await browser.close();
})().catch((e) => { console.error('CRASH', e); process.exit(1); });
