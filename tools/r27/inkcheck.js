// 수묵 호흡 오버레이 확인: 4타 피니시 직후 화면 1장(정지 없이) + 먹물 항목이 그려지며 사라지는지
const { open, start, toEra } = require('./h');
const fs = require('fs');
(async () => {
  const { browser, page, errors } = await open('http://127.0.0.1:8027/index.html', { w: 1280, h: 720, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await toEra(page, 2);
  await page.waitForTimeout(1200);
  await page.evaluate(() => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2500);
  await page.evaluate(() => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; p.invincibleTimer = 99999; p.facing = 1; [100, 170, 230].forEach((dx) => { D.spawnUnit('GOJO_PIKE', p.x + dx, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }); });
  await page.waitForTimeout(300);
  const wait = page.evaluate(() => new Promise((res) => { const g = window.__RELIC; const t0 = performance.now(); const L = () => { const B = g.breathFx || []; if (B.some((e) => e.k === 'inkarc') && performance.now() - Math.max(...B.map((e) => e.t0)) > 70) { const t = performance.now(); performance.now = () => t; res('ink'); } else if (performance.now() - t0 > 5000) res('timeout'); else requestAnimationFrame(L); }; requestAnimationFrame(L); }));
  for (let i = 0; i < 8; i++) { await page.keyboard.press('j'); await page.waitForTimeout(190); }
  console.log('wait', await wait);
  await page.waitForTimeout(250);
  fs.writeFileSync(__dirname + '/../ink_overlay.png', await page.screenshot());
  const n0 = await page.evaluate(() => (window.__RELIC.breathFx || []).length);
  await page.waitForTimeout(1500);
  const n1 = await page.evaluate(() => (window.__RELIC.breathFx || []).length);
  console.log('breathFx entries', n0, '->', n1, 'errors', errors.length);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
