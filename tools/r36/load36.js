// [R36] 6초 부하 테스트 1회(R33 ~ R35와 같은 장면 · 갈래 기술 · 병사 함성 포함) — 4시대 고밀도: 1전선 거란(전선 배경 원화 + 폭우 + 번개) · 척준경 Lv.5 · T3 vs 원화 몹 7 · 미션
//  청룡 보검(모든 베기 검기) · 장군의 인장(공속) · 7초 대기 + 1.5초 예열 뒤 6초 · J 연타(무신 3타 갑옷 쪼개기 이펙트 포함)
//  사용: node load33.js [포트]   (tools/r30/h.js 하네스와 같은 폴더에서)
//  청룡 보검(모든 베기 검기 + 양단) · 장군의 인장(공속) · 타격 이펙트 5종 · 오라 · 선녀 · HD 55fps+
const { open, start, toEra } = require('./h');
(async () => {
  const port = process.argv[2] || 8039;
  const { browser, page, errors } = await open(`http://127.0.0.1:${port}/index.html`);
  await start(page);
  await toEra(page, 4);
  await page.waitForTimeout(1500);
  await page.evaluate(() => {
    const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player;
    g.enemies.length = 0; g.zoneState = 'ROAM'; g.zoneIdx = 0; p.x = g.cameraX + 360; p.z = 430; p.facing = 1; p.invincibleTimer = 99999;
    ['JURCHEN_INF', 'REDTURBAN_ELITE', 'JURCHEN_CAV', 'REDTURBAN_INF', 'WAKOU_SWORD', 'MONGOL_RIDER', 'KHITAN_INF'].forEach((u, i) => D.spawnUnit(u, p.x + 90 + (i % 4) * 110, 380 + (i >> 1) * 30));
    g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; });
    D.setLevel(5); g.stats.weaponTier = 3;
    D.r31mission('jurchen'); g.mission.t0 = g.tick + 1e6;
    D.r31item('blade'); D.r31item('seal');
  });
  // 레벨업 배너가 끝난 뒤의 정상 전투 구간을 잰다(보상 버프는 다시 채움)
  await page.waitForTimeout(7000);
  // 측정 전 1.5초 전투 예열(첫 타격 · 글자 굽기 · 레벨업 배너 정리 뒤의 안정 구간을 잰다)
  { const w0 = Date.now(); while (Date.now() - w0 < 1500) { await page.keyboard.press('j'); await page.waitForTimeout(140); } }
  await page.evaluate(() => { const g = window.__RELIC; g.r31buff.blade = 900; g.r31buff.seal = 720; g.player.invincibleTimer = 99999; });
  const q0 = await page.evaluate(() => ({ tier: window.__RELIC.quality.tier, dpr: window.__RELIC.quality.dpr }));
  const meas = page.evaluate(() => new Promise((res) => {
    const g = window.__RELIC; const ts = []; const tiers = new Set(); const t0 = performance.now(); const renders = []; const h0 = window.__RELIC_DEV.r31(); const q0 = window.__RELIC_DEV.r33();
    let hfxMax = 0;
    const loop = (t) => { ts.push(t); tiers.add(g.quality.tier); if (g.perf && g.perf.last != null) renders.push(g.perf.last); hfxMax = Math.max(hfxMax, g.hfxLive || 0); if (t - t0 < 6000) requestAnimationFrame(loop); else { const h1 = window.__RELIC_DEV.r31(); res({ ts, tiers: [...tiers], renders, mobs: g.enemies.filter((e) => e._mobArt).length, n: g.enemies.length, alive: g.enemies.filter((e) => e.state !== 'DYING').length, hitFx: h1.hitFxN - h0.hitFxN, hfxMax, mission: g.mission && g.mission.key, buff: Object.assign({}, g.r31buff), aura: g.auraStageDrawn, r33: (() => { const q1 = window.__RELIC_DEV.r33(); return { bg: q1.bg && q1.bg.cur, weather: q1.weather, bolts: q1.bolts - q0.bolts, cleaves: q1.e4.cleaves - q0.e4.cleaves }; })(), smp: window.__RELIC_DEV.sfxStats && window.__RELIC_DEV.sfxStats() }); } };
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
  const longF = dts.map((x, i) => [+((m.ts[i + 1] - m.ts[0]) / 1000).toFixed(2), +x.toFixed(1)]).filter((x) => x[1] > 25);
  const res = { longFrames: longF, perSecond: secs, minSecFps: Math.min(...secs), p95FrameMs: +p95.toFixed(1), tierStart: q0.tier, tiersSeen: m.tiers, dpr: q0.dpr, renderAvgMs: +rAvg.toFixed(2), renderMaxMs: +Math.max(...m.renders).toFixed(1), artMobs: m.mobs, enemies: m.n, alive: m.alive, hitFx: m.hitFx, hfxLiveMax: m.hfxMax, mission: m.mission, buff: m.buff, auraStage: m.aura, r33: m.r33, samples: m.smp && { loaded: m.smp.loaded, played: m.smp.played, capped: m.smp.capped }, errors: errors.length };
  console.log(JSON.stringify(res));
  console.log(res.minSecFps >= 55 && res.tiersSeen.every((t) => t === 0) && errors.length === 0 ? 'LOAD PASS (HD 55fps+)' : 'LOAD FAIL');
  await browser.close();
})();
