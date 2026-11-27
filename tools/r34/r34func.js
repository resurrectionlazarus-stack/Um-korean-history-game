// R34 기능 테스트 1회(콘솔 에러 0) — 환경음(날씨 · 전선 따라 교차) · 천둥 · 뿔나팔 · 부처님 장면 환경음 낮춤 ·
//  격파 수 정합(4시대 실제 진행으로 확인) · 척준경 색 보정 원화 · WAV 로드
// 사용: node r34func.js <출력 폴더> [포트=8037]   (같은 폴더의 h.js 하네스)
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8037;
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const r34 = (page) => ev(page, () => window.__RELIC_DEV.r34());
const r33 = (page) => ev(page, () => window.__RELIC_DEV.r33());
const ZONE_TRIG = [700, 2140, 3650, 5690];
// 환경음이 원하는 루프로 실제 재생될 때까지 기다린 뒤 상태를 돌려준다
const ambOf = async (page, want, ms = 6000) => {
  await page.waitForFunction((want) => { const a = window.__RELIC_DEV.r34().amb; return a && a.want === want && a.cur === want; }, want, { timeout: ms }).catch(() => null);
  return r34(page);
};
const calm = (page) => ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; g.waves = []; g.spawnQ = []; p.invincibleTimer = 99999; });

(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await ev(page, () => window.__RELIC_DEV.r31autoQuiz(true));
  // ── A. MANIFEST · WAV
  const man = await ev(page, async () => { const m = await (await fetch('assets/MANIFEST.json')).json(); const k = Object.keys(m.files); return { n: k.length, r34: k.filter((x) => m.files[x].r34).length, amb: k.filter((x) => m.files[x].kind === 'ambience').length, block: m.r34 && [m.r34.added, m.r34.replaced] }; });
  ok('A0 MANIFEST 419항목 · R34 표식 19(새 효과음 7 · 색 보정 12) · 환경음 루프 4', man.n === 419 && man.r34 === 19 && man.amb === 4 && man.block.join() === '7,12', man);
  await page.waitForFunction(() => { const D = window.__RELIC_DEV; const s = D.sfxStats(); const a = D.r34().amb; return s && s.loaded + s.failed >= 23 && a && a.loaded + a.failed >= 4; }, null, { timeout: 15000 }).catch(() => null);
  const st0 = await ev(page, () => ({ s: window.__RELIC_DEV.sfxStats(), a: window.__RELIC_DEV.r34().amb }));
  ok('A1 WAV 23종(기존 20 + 천둥 2 · 뿔나팔) + 환경음 루프 4종 로드 · 실패 0', st0.s.loaded === 23 && st0.s.failed === 0 && st0.a.loaded === 4 && st0.a.failed === 0, { sfx: [st0.s.loaded, st0.s.failed], amb: [st0.a.loaded, st0.a.failed] });
  // ── B. 시대별 날씨 → 환경음
  await calm(page);
  const AMBS = {};
  const snap = async (era, want) => { const s = want ? await ambOf(page, want) : (await sleep(2200), await r34(page)); AMBS[era] = [s.wt, s.amb.want, s.amb.cur, Math.round(s.amb.wantVol * 100) / 100]; };
  await snap(1, 'wind');
  await toEra(page, 2); await sleep(900); await calm(page); await snap(2, null);
  await toEra(page, 3); await sleep(900); await calm(page); await snap(3, 'fire');
  await toEra(page, 4); await sleep(1500); await calm(page);
  // ── C. 4시대 격파 수: 실제 구역 진행(구역 진입 → 웨이브 · 전선 보스 전멸 → 다음 구역 … Z4 웨이브 뒤 최종 보스 등장)으로 센다
  const goals = (await r34(page)).goals;
  await ev(page, () => { const g = window.__RELIC; g.stats.kills = 0; g.zoneIdx = 0; g.zoneState = 'ROAM'; g.midSpawned = {}; g.r33final = false; });
  const t0 = Date.now();
  let horn0 = (await ev(page, () => window.__RELIC_DEV.sfxStats())).by.warHorn || 0;
  let seen = 0;
  while (Date.now() - t0 < 150000) {
    const s = await ev(page, (TR) => {
      const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
      p.invincibleTimer = 99999;
      const spawns = (g.r33bossLog || []).filter((e) => e.ev === 'spawn').length;
      if (g.boss) return { done: true, spawns };
      if ((g.zoneState === 'ROAM' || g.zoneState === 'GO') && g.zoneIdx < 4) p.x = TR[g.zoneIdx] + 30;
      else if (!g.enemies.some((e) => e.isMidBoss && e.state !== 'DYING')) D.r31killAll(false);
      return { done: false, spawns };
    }, ZONE_TRIG);
    if (s.spawns > seen) {
      // 보스가 나오면 뿔나팔(3초)이 끝날 때까지 기다렸다가 처치 — 빨리 감기에서 뿔나팔이 겹쳐 동시 발음 상한(1)에 걸리지 않게
      seen = s.spawns;
      await sleep(3400);
      await ev(page, () => { window.__RELIC_DEV.r31killAll(false); window.__RELIC_DEV.r33kill('mid'); });
    }
    if (s.done) break;
    await sleep(160);
  }
  await sleep(1500);
  const run = await ev(page, () => { const g = window.__RELIC; return { kills: g.stats.kills, boss: !!g.boss, zone: g.zoneIdx, log: (g.r33bossLog || []).map((e) => e.key + ':' + e.ev).join(' '), bg: (g.r33bgLog || []).map((e) => e.bg).join('>') }; });
  const hud = await ev(page, () => { const el = [...document.querySelectorAll('span')].find((e) => /^\d+\/\d+$/.test(e.textContent.trim()) && e.className.includes('sky')); return el ? el.textContent.trim() : null; });
  await page.screenshot({ path: `${OUT}/r34_killgoal.png` });
  ok(`C1 4시대 격파 수 = 계획(웨이브 58 + 전선 보스 3 + 호위 6 = 67) — 실제 진행 ${run.kills}명 · 상단 표시 ${hud}`, goals[3] === 67 && run.kills === 67 && run.boss && hud === '67/67', { goals, run, hud, sec: Math.round((Date.now() - t0) / 1000) });
  const horn1 = (await ev(page, () => window.__RELIC_DEV.sfxStats())).by.warHorn || 0;
  ok('C2 전선 보스 3인 + 최종 보스 등장마다 뿔나팔(4회)', horn1 - horn0 === 4, { horns: horn1 - horn0 });
  // ── D. 부처님의 가호 동안 환경음 낮춤(범종 · 차임이 또렷하게)
  await sleep(2500);
  const a0 = (await ambOf(page, 'fire')).amb;
  await ev(page, () => window.__RELIC_DEV.r33hp('boss', 0.34));
  await page.waitForFunction(() => !!window.__RELIC.buddhaFx, null, { timeout: 9000 });
  await sleep(700);
  const a1 = (await r34(page)).amb;
  await page.waitForFunction(() => !window.__RELIC.buddhaFx, null, { timeout: 9000 });
  await sleep(500);
  const a2 = (await r34(page)).amb;
  ok('D1 부처님의 가호 동안 환경음 35%로 낮췄다가 되돌림', a0.cur === 'fire' && Math.abs(a1.wantVol - 0.35) < 0.01 && Math.abs(a2.wantVol - 1) < 0.01, { before: a0.wantVol, during: a1.wantVol, after: a2.wantVol });
  // ── E. 전선별 환경음 교차 · 번개 뒤 천둥
  await ev(page, () => { const g = window.__RELIC; g.boss = null; g.bossActive = false; g.buddhaFx = null; g.enemies.length = 0; g.zoneState = 'ROAM'; g.bossTele && (g.bossTele.length = 0); });
  const FR = [];
  for (let i = 0; i < 4; i++) {
    await ev(page, (i) => window.__RELIC_DEV.r33bg(i), i);
    const s = await ambOf(page, ['rain', 'blizzard', 'wind', 'fire'][i]);
    FR.push([s.wt, s.amb.cur, Math.round(s.amb.vol * 100) / 100]);
    if (i === 0) {
      const b0 = (await r33(page)).bolts;
      const th0 = await ev(page, () => { const b = window.__RELIC_DEV.sfxStats().by; return (b.thunder1 || 0) + (b.thunder2 || 0); });
      await page.waitForFunction((b0) => window.__RELIC_DEV.r33().bolts > b0, b0, { timeout: 12000 }).catch(() => null);
      await page.screenshot({ path: `${OUT}/r34_khitan_bolt.png` });
      await sleep(1100);
      const th1 = await ev(page, () => { const b = window.__RELIC_DEV.sfxStats().by; return (b.thunder1 || 0) + (b.thunder2 || 0); });
      FR.thunder = [(await r33(page)).bolts - b0, th1 - th0];
    }
  }
  await ev(page, () => window.__RELIC_DEV.r33bg(null));
  ok('E1 4시대 전선 환경음 — 거란 폭우 → 여진 눈보라 → 몽골 황야 바람 → 개경 화염(교차)', FR.map((x) => x[1]).join() === 'rain,blizzard,wind,fire' && FR.every((x) => x[2] > 0), FR);
  ok('E2 번개 뒤 천둥(늦게 울림)', FR.thunder && FR.thunder[0] >= 1 && FR.thunder[1] >= 1, { boltsAndThunders: FR.thunder });
  // ── F. 척준경 색 보정 원화(달리기 프레임의 붉은 기 = 옛 서 있는 자세 수준)
  const warm = await ev(page, () => { const g = window.__RELIC; const H = window.__RELIC_DEV.assets.debug.eras['4@' + (g.quality.dpr || 1)].data.hero; const w = (c) => { const x = c.getContext('2d', { willReadFrequently: true }); const d = x.getImageData(0, 0, c.width, c.height).data; let s = 0, n = 0; for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 128) { s += d[i] - d[i + 2]; n++; } return Math.round(s / n * 10) / 10; }; return { idle: w(H.frames.idle), run: w(H.frames.run), run5: w(H.frames.run5), cleave_hit: w(H.frames.cleave_hit), dragon: w(H.frames.dragon_stance), frames: Object.keys(H.frames).length }; });
  ok('F1 척준경 새 원화 12장 색 보정 적용 — 달리기 · 무신 자세의 붉은 기(R−B)가 서 있는 자세와 ±1.5 안', warm.frames === 26 && ['run', 'run5', 'cleave_hit', 'dragon'].every((k) => Math.abs(warm[k] - warm.idle) <= 1.5), warm);
  // ── B(계속). 5 · 6시대 날씨 → 환경음
  await toEra(page, 5); await sleep(900); await calm(page); await snap(5, null);
  await toEra(page, 6); await sleep(900); await calm(page); await snap(6, 'wind');
  const g5 = (await r34(page)).goals;
  ok('B1 시대별 환경음 — 1 빙하기 찬바람(0.6) · 2 없음 · 3 전장 불티(0.5) · 5 없음 · 6 폐허 바람(0.5)', AMBS[1].join() === 'ASH_AND_SNOW,wind,wind,0.6' && AMBS[2][1] === null && AMBS[3].join() === 'WAR_EMBERS,fire,fire,0.5' && AMBS[5][1] === null && AMBS[6].join() === 'RUIN_ASH,wind,wind,0.5', AMBS);
  ok('B2 시대별 격파 목표(계획 적 수)', g5.every((x) => x > 20), { goals: g5 });
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  console.log(`R34 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  fs.writeFileSync(OUT + '/r34func.json', JSON.stringify(R, null, 1));
  await browser.close();
})().catch((e) => { console.error('TEST CRASH', e); process.exit(1); });
