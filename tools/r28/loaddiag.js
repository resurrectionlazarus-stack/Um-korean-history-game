// [R27] 핵심 전투 장면 6초 부하 1회 — 2시대 해모수(T3 + 칼끝 궤적 + 유물 오라) + 선녀 + 톤다운 원화 몹 6 + 영웅 링 + 수묵/태양 번개 호흡 + 피니시 볼링 · Lv.5 · HD 55fps+
const { open, start, toEra } = require('./h');
(async () => {
  const port = process.argv[2] || 8027;
  const { browser, page, errors } = await open(`http://127.0.0.1:${port}/index.html`);
  await start(page);
  await toEra(page, 2);
  await page.waitForTimeout(1500);
  await page.evaluate(() => {
    const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player;
    g.enemies.length = 0; p.x = g.cameraX + 360; p.z = 430; p.facing = 1; p.invincibleTimer = 99999;
    ['GOJO_PIKE', 'GOJO_ARCHER', 'GOJO_PIKE', 'GOJO_ARCHER', 'GOJO_PIKE', 'GOJO_ARCHER'].forEach((u, i) => D.spawnUnit(u, p.x + 90 + (i % 3) * 120, 380 + (i >> 1) * 40));
    g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; }); D.setLevel(5); g.stats.relicId = 'era2_iron_sword'; g.stats.weaponTier = 3;
  });
  // 레벨업 3회(2 · 3 · 5) 배너가 끝난 뒤의 정상 전투 구간을 잰다
  await page.waitForTimeout(4000);
  const q0 = await page.evaluate(() => ({ tier: window.__RELIC.quality.tier, dpr: window.__RELIC.quality.dpr }));
  const meas = page.evaluate(() => new Promise((res) => {
    const g = window.__RELIC; const rows = []; const t0 = performance.now(); let last = t0;
    const TB = window.__RELIC_DEV.textBake;
    const loop = (t) => { const pf = g.perf || {}; rows.push([+(t - t0).toFixed(1), +(t - last).toFixed(1), +(pf.step || 0).toFixed(2), +(pf.last || 0).toFixed(2), g.particles.length, g.damagePopups.length, (g.breathFx || []).length, g.enemies.length, g.enemies.filter((e) => e.thrown).length, (g.lights || []).length, TB ? (TB.n || TB.count || 0) : -1, TB ? +(TB.ms || TB.t || 0).toFixed(1) : -1]); last = t; if (t - t0 < 6000) requestAnimationFrame(loop); else res(rows); };
    requestAnimationFrame(loop);
  }));
  const t0 = Date.now();
  while (Date.now() - t0 < 6000) { await page.keyboard.press('j'); await page.waitForTimeout(140); }
  const rows = await meas;
  const keys = ['t', 'dt', 'step', 'render', 'parts', 'popups', 'ink', 'enemies', 'thrown', 'lights', 'textN', 'textMs'];
  for (let sec = 0; sec < 6; sec++) {
    const R = rows.filter((r) => r[0] >= sec * 1000 && r[0] < (sec + 1) * 1000);
    const avg = (i) => +(R.reduce((a, r) => a + r[i], 0) / R.length).toFixed(2);
    const mx = (i) => Math.max(...R.map((r) => r[i]));
    console.log(`sec${sec}: frames ${R.length} dtMax ${mx(1)} step ${avg(2)}/${mx(2)} render ${avg(3)}/${mx(3)} parts ${avg(4)}/${mx(4)} popups ${avg(5)}/${mx(5)} ink ${mx(6)} enemies ${mx(7)} thrown ${mx(8)} lights ${mx(9)} text ${R[R.length - 1][10]} ${R[R.length - 1][11]}ms`);
  }
  const longs = rows.filter((r) => r[1] > 25);
  console.log('long frames', longs.length, JSON.stringify(longs.slice(0, 12)));
  console.log('errors', errors.length);
  await browser.close();
})();
