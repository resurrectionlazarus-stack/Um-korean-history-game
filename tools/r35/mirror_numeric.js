// R35 좌우 대칭 수치 확인 — 공격 자세마다 무기 끝 · 중간 지점의 화면 좌표(게임이 궤적용으로 계산하는 값)를 오른쪽 · 왼쪽에서 읽어
//  거울 축(두 x의 평균)이 모든 자세에서 같은지, 높이(y)가 같은지 본다. 배경 · 빛 효과와 무관한 좌표 비교.
//  node tools/r35/mirror_numeric.js [port=8038]
const { open, toEra } = require('./h');
const PORT = process.argv[2] || 8038;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(800);
  await page.evaluate(() => window.__RELIC_DEV.r31autoQuiz(true));
  for (const era of [1, 2, 4]) {
    await toEra(page, era); await sleep(1800);
    await page.evaluate(() => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 1e9; p.x = g.cameraX + 480; p.z = 450; p.y = 0; g.hitStop = 1e9; });
    const rows = [];
    for (const tier of era === 1 ? [1, 2, 3] : [3]) {
      await page.evaluate((t) => { window.__RELIC.stats.weaponTier = t; }, tier);
      await sleep(150);
      for (const st of [1, 2, 3, 4]) for (const pr of [0.34, 0.5, 0.7, 0.9]) {
        const pt = {};
        for (const f of [1, -1]) {
          await page.evaluate(([st, pr, f]) => { const g = window.__RELIC, p = g.player; g.hitStop = 1e9; p._r31pose = null; p.facing = f; p.state = 'ATTACK'; p._atkSrc = 'combo'; p.comboStep = st; p.maxAttackTimer = 14; p.attackTimer = (1 - pr) * 14; p._fin = st === 4; p._atkPrevT = p.attackTimer; p._atkFrom = null; p._poseLast = null; p._wt = []; p._wLastF = null; p._wLastName = null; p._spinAtk = 0; }, [st, pr, f]);
          await sleep(80);
          pt[f] = await page.evaluate(() => { const w = window.__RELIC.player._wt; const a = w && w[w.length - 1]; return a ? [a.tx, a.ty, a.mx, a.my] : null; });
        }
        if (pt[1] && pt[-1]) rows.push({ axisTip: (pt[1][0] + pt[-1][0]) / 2, axisMid: (pt[1][2] + pt[-1][2]) / 2, dyTip: pt[1][1] - pt[-1][1], dyMid: pt[1][3] - pt[-1][3] });
      }
    }
    const ax = rows.flatMap((r) => [r.axisTip, r.axisMid]);
    const mean = ax.reduce((a, b) => a + b, 0) / ax.length;
    const dev = Math.max(...ax.map((v) => Math.abs(v - mean)));
    const dy = Math.max(...rows.flatMap((r) => [Math.abs(r.dyTip), Math.abs(r.dyMid)]));
    console.log(`era ${era}: 자세 ${rows.length}개 · 거울 축 ${mean.toFixed(3)}px · 축 흔들림 최대 ${dev.toFixed(4)}px · 좌우 높이 차 최대 ${dy.toFixed(4)}px`);
    await page.evaluate(() => { const g = window.__RELIC, p = g.player; g.hitStop = 0; p.attackTimer = 0; p.state = 'IDLE'; });
  }
  console.log('errors', errors.length);
  await browser.close();
})().catch((e) => { console.error('CRASH', e); process.exit(1); });
