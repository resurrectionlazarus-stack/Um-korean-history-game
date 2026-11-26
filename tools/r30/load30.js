// [R30] 핵심 전투 장면 6초 부하 1회 — 2시대 해모수 Lv.5 · T3 · 유물(4단계 오라) vs 연 · 한 정식 원화 6 + 동시 적 상한 7 · 회전참 · 질풍연참 · 파동격 · 15콤보 시공 일섬 포함(T3 + 칼끝 궤적 + 유물 오라) + 선녀 + 톤다운 원화 몹 6 + 영웅 링 + 수묵/태양 번개 호흡 + 피니시 볼링 · Lv.5 · HD 55fps+
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
    ['YAN_PIKE', 'HAN_ARCHER', 'HAN_PIKE', 'YAN_ARCHER', 'HAN_ELITE', 'YAN_PIKE'].forEach((u, i) => D.spawnUnit(u, p.x + 90 + (i % 3) * 120, 380 + (i >> 1) * 40));
    g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; }); D.setLevel(5); g.stats.relicId = 'era2_iron_sword'; g.stats.weaponTier = 3;
  });
  // 레벨업 3회(2 · 3 · 5) 배너가 끝난 뒤의 정상 전투 구간을 잰다
  await page.waitForTimeout(4000);
  const q0 = await page.evaluate(() => ({ tier: window.__RELIC.quality.tier, dpr: window.__RELIC.quality.dpr }));
  const meas = page.evaluate(() => new Promise((res) => {
    const g = window.__RELIC; const ts = []; const tiers = new Set(); const t0 = performance.now(); let renders = []; const b0 = g.breathCount || 0, w0 = g.bowlLaunches || 0;
    const loop = (t) => { ts.push(t); tiers.add(g.quality.tier); if (g.perf && g.perf.last != null) renders.push(g.perf.last); if (t - t0 < 6000) requestAnimationFrame(loop); else res({ ts, tiers: [...tiers], renders, mobs: g.enemies.filter((e) => e._mobArt).length, n: g.enemies.length, hs: (g.hitStopLog || []).length, bakes: (g.glowBakeLog || []).slice(), relicHits: g.relicHits || 0, slashFx: g.slashFxCount || 0, rushes: g.rushes || 0, fx3d: g.fx3dCount || 0, specials: g.specials || 0, ink: g.inkDrawn || 0, dives: g.waveDives || 0, cross: g.crossWaves || 0, spins: g.spinFinishers || 0, aura: g.auraStageDrawn, maxAlive: g.maxAlive || 0, alive: g.enemies.filter((e) => e.state !== 'DYING').length, wTier: g.player._wDrawnTier, trail: g.player._wt ? g.player._wt.length : 0, fairy: Object.keys(g._assetSeen || {}).filter((k) => k.startsWith('fairy:') && g.tick - g._assetSeen[k] < 30).length, breaths: (g.breathCount || 0) - b0, bowls: (g.bowlLaunches || 0) - w0, ring: g.rtick - (g.ringTick || 0), flush: g.perf && g.perf.flush, smp: window.__RELIC_DEV.sfxStats && window.__RELIC_DEV.sfxStats() }); };
    requestAnimationFrame(loop);
  }));
  const t0 = Date.now();
  while (Date.now() - t0 < 6000) { await page.keyboard.press('j'); await page.waitForTimeout(140); }
  const m = await meas;
  const dts = m.ts.slice(1).map((t, i) => t - m.ts[i]);
  const secs = [];
  for (let s = 0; s < 6; s++) secs.push(m.ts.filter((t) => t - m.ts[0] >= s * 1000 && t - m.ts[0] < (s + 1) * 1000).length);
  const avg = 1000 * (m.ts.length - 1) / (m.ts[m.ts.length - 1] - m.ts[0]);
  const sorted = dts.slice().sort((a, b) => a - b);
  const p95 = sorted[Math.floor(sorted.length * 0.95)];
  const rAvg = m.renders.reduce((a, b) => a + b, 0) / m.renders.length;
  const longF = dts.map((x, i) => [+((m.ts[i + 1] - m.ts[0]) / 1000).toFixed(2), +x.toFixed(1)]).filter((x) => x[1] > 25);
  const res = { longFrames: longF, perSecond: secs, minSecFps: Math.min(...secs), p95FrameMs: +p95.toFixed(1), tierStart: q0.tier, tiersSeen: m.tiers, dpr: q0.dpr, renderAvgMs: +rAvg.toFixed(2), renderMaxMs: +Math.max(...m.renders).toFixed(1), artMobs: m.mobs, enemies: m.n, hitStops: m.hs, glowBakesMs: m.bakes, relicHits: m.relicHits, slashFx: m.slashFx, rushes: m.rushes, fx3d: m.fx3d, specials: m.specials, inkFrames: m.ink, waveDives: m.dives, crossWaves: m.cross, spins: m.spins, auraStage: m.aura, maxAlive: m.maxAlive, aliveEnd: m.alive, weaponTierDrawn: m.wTier, fairyDrawn: m.fairy, breathFx: m.breaths, bowlLaunches: m.bowls, ringAge: m.ring, samples: m.smp && { loaded: m.smp.loaded, played: m.smp.played, capped: m.smp.capped }, errors: errors.length };
  console.log(JSON.stringify(res));
  console.log(res.minSecFps >= 55 && res.tiersSeen.every((t) => t === 0) && errors.length === 0 ? 'LOAD PASS (HD 55fps+)' : 'LOAD FAIL');
  await browser.close();
})();
