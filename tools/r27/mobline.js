// 시대별 일반 몹 줄 세우기 캡처(전후 비교용): node mobline.js <tag> [query]
const { open, start, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const tag = process.argv[2] || 'after';
const q = process.argv[3] || '';
const OUT = path.join(__dirname, '..', 'mobline');
fs.mkdirSync(OUT, { recursive: true });
const LINE = {
  4: [['U', 'KHITAN_INF'], ['U', 'MONGOL_RIDER'], ['U', 'WAKOU_SWORD']],
  5: [['U', 'JP_GUNNER'], ['U', 'SAMURAI'], ['U', 'QING_RIDER']],
  6: [['U', 'JP_BAYONET'], ['U', 'MG_NEST'], ['U', 'FR_RIFLE']]
};
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:8027/index.html${q}`, { w: 1280, h: 720, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await page.evaluate(() => {
    window.__freeze = () => { const t = performance.now(); window.__realNow = window.__realNow || performance.now.bind(performance); performance.now = () => t; window.__RELIC.ultFreeze = 1e9; window.__RELIC.clearBeatUntil = 1e12; };
    window.__unfreeze = () => { if (window.__realNow) performance.now = window.__realNow; window.__RELIC.ultFreeze = 0; };
  });
  for (const era of [4, 5, 6]) {
    await toEra(page, era); await page.waitForTimeout(1500);
    await page.evaluate(() => { const qq = window.__RELIC.quality; qq.forced = true; qq.tier = 0; });
    await page.evaluate((L) => {
      const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
      g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 300; p.z = 440; p.y = 0; p.facing = 1; p.invincibleTimer = 99999;
      L.forEach(([t, id], i) => { if (t === 'R') D.spawnRole(id, p.x + 120 + i * 105, i % 2 ? 452 : 428); else D.spawnUnit(id, p.x + 120 + i * 105, i % 2 ? 452 : 428); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; e.facing = -1; e.speed = 0; });
    }, LINE[era]);
    await page.waitForTimeout(700);
    const art = await page.evaluate(() => window.__RELIC.enemies.map((e) => [e.unit || e.mobRole, e._mobArt || null]));
    await page.evaluate(() => window.__freeze());
    await page.waitForTimeout(200);
    fs.writeFileSync(path.join(OUT, `${tag}_e${era}.png`), await page.screenshot());
    await page.evaluate(() => window.__unfreeze());
    console.log(tag, 'era', era, JSON.stringify(art));
  }
  console.log('errors', errors.length, errors.slice(0, 3));
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
