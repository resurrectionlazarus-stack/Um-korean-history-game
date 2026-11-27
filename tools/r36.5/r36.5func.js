// R36.5 기능 테스트 1회(콘솔 에러 0) — 바뀐 것은 무기 그림 9장의 손뿐이다(코드 변경 없음).
//  ① 목록 455 = 표식 9 · 무기 9장이 목록의 크기대로 받아짐 ② 1 · 2 · 4시대에서 무기 3단계가 모두 그려짐(오른쪽 · 왼쪽 보기)
//  ③ 확대 촬영(납품 이미지용): 서 있기 · 달리기 · 공격 × 좌우
// 사용: node tools/r36.5/r36.5func.js <출력 폴더> [포트=8040]
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8040;
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const POSES = ['idle', 'run3', 'atk1_2', 'atk3_2'];
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 3 });
  const ev = (f, a) => page.evaluate(f, a);
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await ev(() => window.__RELIC_DEV.r31autoQuiz(true));
  // ① 목록 · 파일
  const man = await ev(async () => {
    const m = await (await fetch('assets/MANIFEST.json')).json();
    const k = Object.keys(m.files);
    const w = k.filter((x) => m.files[x].r36_5);
    const sizes = [];
    for (const f of w) { const r = await fetch(f); const b = await r.arrayBuffer(); sizes.push([f.split('/').pop(), r.status, b.byteLength === m.files[f].bytes]); }
    return { n: k.length, marked: w.length, block: m.r36_5 ? m.r36_5.replaced : null, sizes };
  });
  ok('A0 MANIFEST 455항목 · R36.5 표식 9(무기 그림)', man.n === 455 && man.marked === 9 && man.block === 9, { n: man.n, marked: man.marked });
  ok('A1 무기 9장이 목록의 크기 그대로 받아짐', man.sizes.length === 9 && man.sizes.every((s) => s[1] === 200 && s[2]), man.sizes.filter((s) => !(s[1] === 200 && s[2])));
  // ② · ③ 시대별 무기 단계 · 촬영
  for (const era of [1, 2, 4]) {
    if (era > 1) { await toEra(page, era); await sleep(1600); }
    const geo = await ev(() => {
      const g = window.__RELIC, p = g.player;
      g.enemies.length = 0; g.zoneState = 'ROAM'; g.waves = []; g.paleoWaves = null; p.invincibleTimer = 1e9;
      p.x = g.cameraX + 480; p.z = 450; p.y = 0; p.vx = p.vy = 0; p.state = 'IDLE'; p.attackTimer = 0;
      g.hitStop = 1e9; g.particles.length = 0;
      Object.assign(window.__PERF_OFF, { weather: true, particles: true, aura: true, lights: true, shock: true, popups: true });
      const c = [...document.querySelectorAll('canvas')].sort((a, b) => b.width * b.height - a.width * a.height)[0];
      const r = c.getBoundingClientRect();
      return { left: r.left, top: r.top, w: r.width, px: p.x - g.cameraX, pz: p.z };
    });
    const sc = geo.w / 960;
    const cx = Math.round(geo.left + geo.px * sc), cy = Math.round(geo.top + geo.pz * sc);
    const clip = { x: cx - 150, y: cy - 205, width: 300, height: 225 };
    const drawn = [];
    for (const tier of [1, 2, 3]) {
      await ev((t) => { window.__RELIC.stats.weaponTier = t; }, tier);
      await sleep(250);
      for (const f of [1, -1]) {
        for (const pose of (tier === 3 ? POSES : ['idle'])) {
          await ev(([pose, f]) => { const g = window.__RELIC, p = g.player; g.hitStop = 1e9; p.attackTimer = 0; p.state = 'IDLE'; p.facing = f; p._wt = []; p._wLastF = null; p._wLastName = null; p._r31pose = { name: pose, until: g.tick + 1e7, lift: 0 }; }, [pose, f]);
          await sleep(90);
          await ev(() => { window.__RELIC.player._wt = []; });
          await sleep(70);
          await page.screenshot({ path: `${OUT}/e${era}_t${tier}_${pose}_${f > 0 ? 'R' : 'L'}.png`, clip });
        }
        drawn.push(await ev(() => window.__RELIC.player._wDrawnTier));
      }
    }
    ok(`B${era} ${era}시대: 무기 1 · 2 · 3단계가 좌우 모두 그 단계 그림으로 그려짐`, drawn.join() === '1,1,2,2,3,3', drawn);
    await ev(() => { const g = window.__RELIC, p = g.player; for (const k of Object.keys(window.__PERF_OFF)) window.__PERF_OFF[k] = false; g.hitStop = 0; p._r31pose = null; p.facing = 1; });
    await sleep(500);
    await page.screenshot({ path: `${OUT}/e${era}_ingame.png` });
  }
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  const fails = Object.keys(R).filter((k) => !R[k]);
  console.log(`\n${Object.keys(R).length - fails.length}/${Object.keys(R).length} PASS` + (fails.length ? ' — FAIL: ' + fails.join(' | ') : ''));
  await browser.close();
  process.exit(fails.length ? 1 : 0);
})();
