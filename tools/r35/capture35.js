// R35 납품 이미지용 촬영 — 1시대 대사냥꾼이 무기 3단계를 쥔 모습(자세 고정 · 좌우)을 한 빌드에서 찍는다. 비교 합성은 compose35.py
//  node tools/r35/capture35.js <out-dir> <port> <tag>      (R34 = 8037 · R35 = 8038 처럼 두 번 실행)
const { open } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8038;
const TAG = process.argv[4] || 'r35';
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const POSES = ['idle', 'atk1_2', 'atk_prep', 'atk2_3', 'hit'];
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 2 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1800);
  const geo = await page.evaluate(() => {
    const g = window.__RELIC, p = g.player;
    g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 1e9;
    p.x = g.cameraX + 480; p.z = 450; p.y = 0; p.vx = p.vy = 0; p.state = 'IDLE'; p.attackTimer = 0; p.flinch = 0;
    g.hitStop = 1e9; g.particles.length = 0;
    Object.assign(window.__PERF_OFF, { weather: true, particles: true, aura: true, lights: true, shock: true, popups: true });
    const c = [...document.querySelectorAll('canvas')].sort((a, b) => b.width * b.height - a.width * a.height)[0];
    const r = c.getBoundingClientRect();
    return { left: r.left, top: r.top, w: r.width, px: p.x - g.cameraX, pz: p.z };
  });
  const sc = geo.w / 960;
  const cx = Math.round(geo.left + geo.px * sc), cy = Math.round(geo.top + geo.pz * sc);
  const clip = { x: cx - 230, y: cy - 320, width: 460, height: 360 };
  for (const tier of [1, 2, 3]) {
    await page.evaluate((t) => { window.__RELIC.stats.weaponTier = t; }, tier);
    await sleep(200);
    for (const pose of POSES) for (const f of [1, -1]) {
      await page.evaluate(([pose, f]) => { const g = window.__RELIC, p = g.player; g.hitStop = 1e9; p.attackTimer = 0; p.state = 'IDLE'; p.facing = f; p._wt = []; p._wLastF = null; p._wLastName = null; p._r31pose = { name: pose, until: g.tick + 1e7, lift: 0 }; }, [pose, f]);
      await sleep(70);
      await page.evaluate(() => { window.__RELIC.player._wt = []; });
      await sleep(60);
      await page.screenshot({ path: `${OUT}/${TAG}_t${tier}_${pose}_${f > 0 ? 'R' : 'L'}.png`, clip });
    }
  }
  // 게임 화면 한 장(효과 다시 켜고 평소 상태)
  await page.evaluate(() => { const g = window.__RELIC, p = g.player; for (const k of Object.keys(window.__PERF_OFF)) window.__PERF_OFF[k] = false; g.hitStop = 0; p._r31pose = null; p.facing = 1; g.stats.weaponTier = 3; });
  await sleep(900);
  await page.screenshot({ path: `${OUT}/${TAG}_ingame.png` });
  console.log(TAG, 'errors', errors.length, errors.slice(0, 2));
  await browser.close();
})().catch((e) => { console.error('CRASH', e); process.exit(1); });
