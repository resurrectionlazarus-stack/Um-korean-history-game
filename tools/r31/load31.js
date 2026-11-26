// [R31] 핵심 전투 장면 6초 부하 1회 — R30 표준 2시대 고밀도 장면(해모수 Lv.5 · T3 · 유물 vs 연 · 한 정식 원화 6 + 동시 적 상한 7) ·
//  해모수 신화 연출(3타 호랑이 발톱 · 4타 곰 내려찍기 · 질풍연참 · 급강하 곰 · 천둥 · 15콤보 SOLAR FLASH 하늘 소환 + 광륜 + 거대 비파형 동검) ·
//  타격 이펙트 5종 · 검기 ×1.4 · 강타 히트스톱 +1.5 · 오라 · 선녀 · HD 55fps+
//  측정: 배치 뒤 7초(레벨업 배너 정리) + 1.5초 전투 예열 뒤의 6초(안정 고밀도 구간)
const { open, start, toEra } = require('./h');
(async () => {
  const port = process.argv[2] || 8032;
  const { browser, page, errors } = await open(`http://127.0.0.1:${port}/index.html`);
  await start(page);
  await toEra(page, 2);
  await page.waitForTimeout(1500);
  await page.evaluate(() => {
    const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player;
    g.enemies.length = 0; p.x = g.cameraX + 360; p.z = 430; p.facing = 1; p.invincibleTimer = 99999;
    ['YAN_PIKE', 'HAN_ARCHER', 'HAN_PIKE', 'YAN_ARCHER', 'HAN_ELITE', 'YAN_PIKE'].forEach((u, i) => D.spawnUnit(u, p.x + 90 + (i % 4) * 110, 380 + (i >> 1) * 30));
    g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; }); D.setLevel(5); g.stats.relicId = 'era2_iron_sword'; g.stats.weaponTier = 3;
  });
  await page.waitForTimeout(7000);
  { const w0 = Date.now(); while (Date.now() - w0 < 1500) { await page.keyboard.press('j'); await page.waitForTimeout(140); } }
  const q0 = await page.evaluate(() => ({ tier: window.__RELIC.quality.tier, dpr: window.__RELIC.quality.dpr }));
  const meas = page.evaluate(() => new Promise((res) => {
    const g = window.__RELIC; const ts = []; const tiers = new Set(); const t0 = performance.now(); const renders = []; const h0 = window.__RELIC_DEV.r31();
    let hfxMax = 0;
    const loop = (t) => { ts.push(t); tiers.add(g.quality.tier); if (g.perf && g.perf.last != null) renders.push(g.perf.last); hfxMax = Math.max(hfxMax, g.hfxLive || 0); if (t - t0 < 6000) requestAnimationFrame(loop); else { const h1 = window.__RELIC_DEV.r31(); res({ ts, tiers: [...tiers], renders, mobs: g.enemies.filter((e) => e._mobArt).length, n: g.enemies.length, alive: g.enemies.filter((e) => e.state !== 'DYING').length, hitFx: h1.hitFxN - h0.hitFxN, hfxMax, artFx: h1.artFx - h0.artFx, cleaves: h1.e2.cleaves - h0.e2.cleaves, slams: h1.e2.slams - h0.e2.slams, swords: h1.e2.skySwords - h0.e2.skySwords, summons: h1.e2.summons - h0.e2.summons, rushes: g.rushes || 0, specials: g.specials || 0, aura: g.auraStageDrawn, maxAlive: g.maxAlive || 0, smp: window.__RELIC_DEV.sfxStats && window.__RELIC_DEV.sfxStats() }); } };
    requestAnimationFrame(loop);
  }));
  const t0 = Date.now();
  while (Date.now() - t0 < 6000) { await page.keyboard.press('j'); await page.waitForTimeout(140); }
  const m = await meas;
  const dts = m.ts.slice(1).map((t, i) => t - m.ts[i]);
  const secs = [];
  for (let s = 0; s < 6; s++) secs.push(m.ts.filter((t) => t - m.ts[0] >= s * 1000 && t - m.ts[0] < (s + 1) * 1000).length);
  const sorted = dts.slice().sort((a, b) => a - b);
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  const rAvg = m.renders.reduce((a, b) => a + b, 0) / Math.max(1, m.renders.length);
  const res = { perSecond: secs, minSecFps: Math.min(...secs), p95FrameMs: +p95.toFixed(1), longFrames: dts.filter((x) => x > 25).length, tierStart: q0.tier, tiersSeen: m.tiers, dpr: q0.dpr, renderAvgMs: +rAvg.toFixed(2), renderMaxMs: +Math.max(...m.renders).toFixed(1), artMobs: m.mobs, enemies: m.n, alive: m.alive, hitFx: m.hitFx, hfxLiveMax: m.hfxMax, artFx: m.artFx, cleaves: m.cleaves, slams: m.slams, skySwords: m.swords, summons: m.summons, rushes: m.rushes, specials: m.specials, auraStage: m.aura, samples: m.smp && { loaded: m.smp.loaded, played: m.smp.played, capped: m.smp.capped }, errors: errors.length };
  console.log(JSON.stringify(res));
  console.log(res.minSecFps >= 55 && res.tiersSeen.every((t) => t === 0) && errors.length === 0 ? 'LOAD PASS (HD 55fps+)' : 'LOAD FAIL');
  await browser.close();
})();
