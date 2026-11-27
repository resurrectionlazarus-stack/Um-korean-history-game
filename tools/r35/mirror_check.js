// R35 좌우 대칭 점검 — 같은 자세를 오른쪽 · 왼쪽으로 그려 찍는다(시뮬레이션은 hitStop으로 멈춤). 비교는 mirror_diff.py
//  node tools/r35/mirror_check.js <out-dir> [port] [eras=1,2,4]
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8038;
const ERAS = (process.argv[4] || '1,2,4').split(',').map(Number);
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const GR = require('../r33/grips_r33.json');
const FR = { 1: Object.keys(GR.R27_HUNTER_FRAMES), 2: Object.keys(GR.R26_HM_FRAMES), 4: Object.keys(GR.R26_CJG_FRAMES) };
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 2 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(800);
  await page.evaluate(() => window.__RELIC_DEV.r31autoQuiz(true));
  const meta = {};
  for (const era of ERAS) {
    await toEra(page, era);
    await sleep(2200);
    const geo = await page.evaluate(() => {
      const g = window.__RELIC, p = g.player;
      g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 1e9;
      p.x = g.cameraX + 480; p.z = 450; p.y = 0; p.vx = p.vy = 0; p.state = 'IDLE'; p.attackTimer = 0; p.flinch = 0;
      g.hitStop = 1e9; g.particles.length = 0;
      Object.assign(window.__PERF_OFF, { weather: true, particles: true, aura: true, lights: true, shock: true, popups: true });   // 움직이는 것 끄기(주인공 · 무기만 비교)
      const c = [...document.querySelectorAll('canvas')].sort((a, b) => b.width * b.height - a.width * a.height)[0];
      const r = c.getBoundingClientRect();
      return { left: r.left, top: r.top, w: r.width, h: r.height, px: p.x - g.cameraX, pz: p.z, tier: g.stats.weaponTier };
    });
    const sc = geo.w / 960;
    const cx = Math.round(geo.left + geo.px * sc), cy = Math.round(geo.top + geo.pz * sc);
    const clip = { x: cx - 250, y: cy - 330, width: 500, height: 420 };
    meta[era] = { geo, clip, shots: [] };
    const shot = async (tag, setup) => {
      for (const f of [1, -1]) {
        await page.evaluate(([s, f]) => {
          const g = window.__RELIC, p = g.player;
          p._r31pose = null; p.attackTimer = 0; p.state = 'IDLE'; p._spinAtk = 0; p.stepT = 0; p._fin = false; p._atkFrom = null; p._atkPrevT = 0; p._poseLast = null; p._wt = []; p._wLastF = null; p._wLastName = null; p._wBreak = true;
          g.hitStop = 1e9; g.particles.length = 0; if (g.fx3d) g.fx3d.length = 0; if (g.ghosts) g.ghosts.length = 0;
          p.facing = f;
          if (s.pose) p._r31pose = { name: s.pose, until: g.tick + 1e7, lift: 0 };
          if (s.atk) { p.state = 'ATTACK'; p._atkSrc = 'combo'; p.comboStep = s.atk[0]; p.maxAttackTimer = 14; p.attackTimer = (1 - s.atk[1]) * 14; p._fin = s.atk[0] === 4; p._atkPrevT = p.attackTimer; }
          if (s.run != null) { p.state = 'RUN'; p.stepT = s.run; }
          if (s.guard) p.guardTimer = 30; else p.guardTimer = 0;
        }, [setup, f]);
        await sleep(60);
        await page.evaluate(() => { window.__RELIC.player._wt = []; });   // 자세가 바뀌는 순간 생기는 궤적(시험 부산물) 지우기
        await sleep(60);
        await page.screenshot({ path: `${OUT}/e${era}_${tag}_${f > 0 ? 'R' : 'L'}.png`, clip });
      }
      meta[era].shots.push(tag);
    };
    // 배경(주인공 없음)
    await page.evaluate(() => { window.__PERF_OFF.actors = true; });
    await sleep(120);
    await page.screenshot({ path: `${OUT}/e${era}_BG.png`, clip });
    await page.evaluate(() => { window.__PERF_OFF.actors = false; });
    for (const tier of era === 1 ? [1, 2, 3] : [3]) {
      await page.evaluate((t) => { window.__RELIC.stats.weaponTier = t; }, tier);
      await sleep(150);
      const fl = era === 1 && tier < 3 ? ['idle', 'run3', 'atk1_2', 'atk2_2', 'atk3_2'] : FR[era];
      for (const nm of fl) await shot(`t${tier}_f_${nm}`, { pose: nm });
    }
    for (const st of [1, 2, 3, 4]) for (const pr of [0.12, 0.34, 0.5, 0.7, 0.9]) await shot(`atk${st}_${Math.round(pr * 100)}`, { atk: [st, pr] });
    for (const t of [0, 7, 14, 21, 28, 35, 42, 49]) await shot(`run_${t}`, { run: t });
    await shot('guard', { guard: 1 });
    await page.evaluate(() => { const g = window.__RELIC, p = g.player; g.hitStop = 0; p._r31pose = null; p.attackTimer = 0; p.guardTimer = 0; p.state = 'IDLE'; for (const k of ['weather', 'particles', 'aura', 'lights', 'shock', 'popups']) window.__PERF_OFF[k] = false; });
  }
  fs.writeFileSync(`${OUT}/meta.json`, JSON.stringify(meta));
  console.log('errors', errors.length, errors.slice(0, 3));
  await browser.close();
})().catch((e) => { console.error('CRASH', e); process.exit(1); });
