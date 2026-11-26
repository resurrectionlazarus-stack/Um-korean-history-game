// 부하 장면 CPU 프로파일(함수별 self 시간) — 원인 찾기용
const { open, start, toEra } = require('./h');
(async () => {
  const port = process.argv[2] || 8032;
  const variant = process.argv[3] || 'full';
  const offs = (process.argv[4] || '').split(',').filter(Boolean);
  const { browser, page, errors } = await open(`http://127.0.0.1:${port}/index.html`);
  await start(page);
  await toEra(page, 4);
  await page.waitForTimeout(1500);
  await page.evaluate((variant) => {
    const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player;
    g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 360; p.z = 430; p.facing = 1; p.invincibleTimer = 99999;
    ['JURCHEN_INF', 'REDTURBAN_ELITE', 'JURCHEN_CAV', 'REDTURBAN_INF', 'WAKOU_SWORD', 'MONGOL_RIDER', 'KHITAN_INF'].forEach((u, i) => D.spawnUnit(u, p.x + 90 + (i % 4) * 110, 380 + (i >> 1) * 30));
    g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; });
    D.setLevel(5); g.stats.weaponTier = 3;
    if (variant !== 'nobuff') { D.r31mission('jurchen'); g.mission.t0 = g.tick + 1e6; D.r31item('blade'); D.r31item('seal'); }
  }, variant);
  await page.waitForTimeout(4000);
  await page.evaluate((variant) => { const g = window.__RELIC; if (variant !== 'nobuff') { g.r31buff.blade = 900; g.r31buff.seal = 720; } g.player.invincibleTimer = 99999; }, variant);
  await page.evaluate((offs) => { offs.forEach((k) => { window.__PERF_OFF[k] = true; }); }, offs);
  const client = await page.context().newCDPSession(page);
  await client.send('Profiler.enable');
  await client.send('Profiler.setSamplingInterval', { interval: 200 });
  await client.send('Profiler.start');
  const meas = page.evaluate(() => new Promise((res) => { const g = window.__RELIC; const ts = []; const t0 = performance.now(); let parts = 0, maxParts = 0, pops = 0; const L = (t) => { ts.push(t); maxParts = Math.max(maxParts, g.particles.length); pops = Math.max(pops, g.damagePopups.length); if (t - t0 < 6000) requestAnimationFrame(L); else res({ n: ts.length, maxParts, pops, sec: g.perf && g.perf.sec, art: g.perf && g.perf.art, flush: g.perf && g.perf.flush }); }; requestAnimationFrame(L); }));
  const t0 = Date.now();
  while (Date.now() - t0 < 6000) { await page.keyboard.press('j'); await page.waitForTimeout(140); }
  const m = await meas;
  const { profile } = await client.send('Profiler.stop');
  const self = new Map();
  const total = profile.endTime - profile.startTime;
  const dt = profile.timeDeltas;
  const idx = new Map(profile.nodes.map((n) => [n.id, n]));
  const cnt = new Map();
  profile.samples.forEach((id, i) => cnt.set(id, (cnt.get(id) || 0) + (dt[i] || 0)));
  for (const [id, t] of cnt) { const n = idx.get(id); const k = n.callFrame.functionName || '(' + n.callFrame.url.split('/').pop() + ')'; self.set(k, (self.get(k) || 0) + t); }
  const top = [...self.entries()].sort((a, b) => b[1] - a[1]).slice(0, 28).map(([k, t]) => `${k}:${(t / 1000).toFixed(0)}ms`);
  console.log(variant, offs.join('+') || '-', 'frames', m.n, 'fps', (m.n / 6).toFixed(1), 'maxParticles', m.maxParts, 'popups', m.pops, 'sec', JSON.stringify(m.sec), 'art', m.art, 'flush', m.flush, 'profile ms', (total / 1000).toFixed(0));
  console.log(top.join('  '));
  console.log('errors', errors.length);
  await browser.close();
})();
