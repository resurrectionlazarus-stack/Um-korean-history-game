// R36.5-2 기능 테스트 1회(콘솔 에러 0) — 바뀐 것은 무기 그림 9장뿐이다(코드 변경 없음).
//  ① 목록 455 = 표식 9 · 무기 9장이 목록의 크기대로 받아짐
//  ② 무기 그림의 손이 몸 원화의 주먹이다(1시대: 손 길이 ≤ 40px · 자루 ≤ 15px / 2 · 4시대: 맨주먹 살색)
//  ③ 1 · 2 · 4시대에서 무기 3단계가 모두 그려짐(오른쪽 · 왼쪽 보기)
//  ④ 확대 촬영(납품 이미지용): 서 있기 · 달리기 · 공격 × 좌우
// 사용: node tools/r36.5-2/r36.5-2func.js <출력 폴더> [포트=8041]
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8041;
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
    const w = k.filter((x) => m.files[x].r36_5_2);
    const sizes = [];
    for (const f of w) { const r = await fetch(f); const b = await r.arrayBuffer(); sizes.push([f.split('/').pop(), r.status, b.byteLength === m.files[f].bytes]); }
    return { n: k.length, marked: w.length, block: m.r36_5_2 ? m.r36_5_2.replaced : null, sizes };
  });
  ok('A0 MANIFEST 455항목 · R36.5-2 표식 9(무기 그림)', man.n === 455 && man.marked === 9 && man.block === 9, { n: man.n, marked: man.marked });
  ok('A1 무기 9장이 목록의 크기 그대로 받아짐', man.sizes.length === 9 && man.sizes.every((s) => s[1] === 200 && s[2]), man.sizes.filter((s) => !(s[1] === 200 && s[2])));
  // ② 손 크기(그림을 직접 잰다 — 옛 그림은 떨어지고 새 그림만 통과하는 잣대)
  //   1시대: 쥔 자리(70)에서 좌우로 '자루보다 8px 넘게 두꺼운 열'이 이어지는 길이 = 손 길이(예전 56~60px) · 자루 굵기(예전 16~21px)
  //   2 · 4시대: 손 자리의 살색 픽셀 수(예전 건틀릿은 46 이하 — 맨주먹이면 200 안팎)
  const hand = await ev(async () => {
    const out = {};
    for (const era of [1, 2, 4]) for (const t of [1, 2, 3]) {
      const img = new Image(); img.src = `assets/weapon/era${era}_t${t}.png`; await img.decode();
      const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
      const x = c.getContext('2d'); x.drawImage(img, 0, 0);
      const d = x.getImageData(0, 0, c.width, c.height).data;
      const col = (cx) => { let n = 0; for (let y = 0; y < c.height; y++) if (d[(y * c.width + cx) * 4 + 3] > 128) n++; return n; };
      const o = { w: img.width, h: img.height };
      if (era === 1) {
        const sh = []; for (let cx = 100; cx <= 112; cx++) sh.push(col(cx));
        sh.sort((p, q) => p - q); o.shaft = sh[sh.length >> 1];
        let L = 70, Rr = 70;
        while (L > 5 && col(L - 1) > o.shaft + 8) L--;
        while (Rr < c.width - 2 && col(Rr + 1) > o.shaft + 8) Rr++;
        o.len = Rr - L + 1;
      } else {
        const [x0, x1] = era === 4 && t === 3 ? [34, 80] : [42, 88];
        let skin = 0;
        for (let y = 30; y < 80; y++) for (let cx = x0; cx < x1; cx++) {
          const i = (y * c.width + cx) * 4, r = d[i], g = d[i + 1], b = d[i + 2];
          if (d[i + 3] > 200 && r > 150 && g > 110 && r - b >= 20 && r - b <= 95 && r > g && g >= b) skin++;
        }
        o.skin = skin;
      }
      out[`era${era}_t${t}`] = o;
    }
    return out;
  });
  const E1 = ['era1_t1', 'era1_t2', 'era1_t3'], E24 = ['era2_t1', 'era2_t2', 'era2_t3', 'era4_t1', 'era4_t2', 'era4_t3'];
  ok('A2 그림 크기 그대로(높이 120 · 9장)', Object.values(hand).every((v) => v.h === 120), Object.values(hand).map((v) => v.w + 'x' + v.h));
  ok('A3 1시대 손 길이 40px 이하(예전 56~60px) · 자루 굵기 15px 이하(예전 16~21px)', E1.every((k) => hand[k].len <= 40 && hand[k].len >= 28 && hand[k].shaft <= 15), E1.map((k) => [hand[k].len, hand[k].shaft]));
  ok('A4 2 · 4시대 손이 몸 원화와 같은 맨주먹(살색 150픽셀 이상 · 예전 건틀릿 46 이하)', E24.every((k) => hand[k].skin >= 150), E24.map((k) => hand[k].skin));
  // ③ · ④ 시대별 무기 단계 · 촬영
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
