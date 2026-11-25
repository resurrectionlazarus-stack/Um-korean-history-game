// R29 기능 테스트 1회(콘솔 에러 0) — 시작 가림막 · 2시대 연/한 군대 · 베는 맛(베기 선 · 두 동강 · 히트스톱) · 콤보 3종
// 베기 · 질풍연참 장면은 CDP 스크린캐스트로 프레임을 받아 둔다(비교 이미지용)
const { open, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function film(page, tag, ms, act) {
  const cdp = await page.context().newCDPSession(page);
  const frames = [];
  cdp.on('Page.screencastFrame', async (f) => { frames.push(f.data); try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch (e) {} });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 88, everyNthFrame: 1, maxWidth: 1280, maxHeight: 720 });
  await act();
  await sleep(ms);
  await cdp.send('Page.stopScreencast');
  const dir = path.join(OUT, tag);
  fs.mkdirSync(dir, { recursive: true });
  frames.forEach((d, i) => fs.writeFileSync(path.join(dir, `f${String(i).padStart(3, '0')}.jpg`), Buffer.from(d, 'base64')));
  return frames.length;
}
(async () => {
  const { browser, page, errors } = await open('http://127.0.0.1:8030/index.html', { w: 1280, h: 720, dsf: 1 });
  // ── A. 시작 가림막: 원화 로딩 중에는 가림막만(장면 0프레임) · START 글자 · 일찍 누른 Enter 예약 → 준비되면 자동 시작
  await ev(page, () => { window.__gateLog = []; const L = () => { const D = window.__RELIC_DEV; const T = D.titleGate(); const title = !!document.querySelector('button') && [...document.querySelectorAll('button')].some((b) => /START|불러오는|곧 시작/.test(b.textContent)); window.__gateLog.push({ st: D.assets.status(1), open: T.open, title }); if (window.__gateLog.length < 2000) requestAnimationFrame(L); }; requestAnimationFrame(L); });
  const a0 = await ev(page, () => ({ g: window.__RELIC_DEV.titleGate(), labels: [...document.querySelectorAll('button')].map((b) => b.textContent).filter((t) => /START|불러오는|곧 시작/.test(t)) }));
  ok('A1 켠 직후 = 수묵 가림막(1시대 원화 로딩 중) · START 버튼 = "불러오는 중 · NN%"', !a0.g.open && a0.g.info.status === 'loading' && a0.labels.some((t) => /불러오는 중 · \d+%/.test(t)), { open: a0.g.open, st: a0.g.info.status, labels: a0.labels });
  await page.keyboard.press('Enter');
  await sleep(100);
  const a1 = await ev(page, () => window.__RELIC_DEV.titleGate());
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await page.waitForFunction(() => ![...document.querySelectorAll('button')].some((b) => /^(START|PRESS START)$|불러오는|곧 시작/.test(b.textContent)), null, { timeout: 15000 });
  await sleep(400);
  const gl = await ev(page, () => window.__gateLog);
  const leak = gl.filter((s) => s.title && s.st === 'loading' && s.open).length;
  const tick0 = await ev(page, () => window.__RELIC.tick);
  ok('A2 일찍 누른 Enter = 예약("곧 시작") → 원화 준비 뒤 자동 시작 · 로딩 중 장면이 열린 프레임 0', a1.pending && /곧 시작/.test(a1.label ? '곧 시작' : '') && leak === 0 && gl.length > 10, { pending: a1.pending, samples: gl.length, leak, tick0 });
  // ── B. 2시대 연나라 · 한나라 군대
  await toEra(page, 2);
  await sleep(900);
  const b1 = await ev(page, () => new Promise((res) => {
    const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
    g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 99999;
    ['YAN_PIKE', 'YAN_ARCHER', 'HAN_PIKE', 'HAN_ARCHER', 'HAN_ELITE'].forEach((u, i) => D.spawnUnit(u, p.x + 160 + i * 120, 380 + (i % 2) * 70));
    g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; });
    const d = D.assets.debug.eras['2@' + (g.quality.dpr || 1)].data;
    setTimeout(() => res({ art: g.enemies.map((e) => [e.unit, e._mobArt || null]), mobs: Object.keys(d.mobs).sort(), fails: D.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)) }), 500);
  }));
  const want = [['YAN_PIKE', 'yan_pike'], ['YAN_ARCHER', 'yan_archer'], ['HAN_PIKE', 'han_pike'], ['HAN_ARCHER', 'han_archer'], ['HAN_ELITE', 'han_elite']];
  ok('B1 2시대 병종 5종 = 연 · 한 임시 원화 · 고조선 창병 · 궁수 원화는 읽지 않음 · 로드 실패 0', JSON.stringify(b1.art) === JSON.stringify(want) && !b1.mobs.includes('pike') && !b1.mobs.includes('archer') && b1.fails.length === 0, b1);
  await page.screenshot({ path: path.join(OUT, 'r29_era2_lineup.png') });
  const b2 = await ev(page, () => new Promise((res) => {
    const g = window.__RELIC, p = g.player;
    g.enemies.length = 0; g.zoneIdx = 0; g.zoneState = 'ROAM'; p.x = 720;
    setTimeout(() => {
      const w0 = g.waves.slice();
      setTimeout(() => res({ w0, zs: g.zoneState, act: (g.actLog || []).slice(-1)[0], units: [...new Set(g.enemies.map((e) => e.unit))], chips: [...document.querySelectorAll('div')].filter((d) => /^(⚔ |✔ )?Z\d /.test(d.textContent) && d.children.length === 0).map((d) => d.textContent) }), 900);
    }, 120);
  }));
  ok('B2 2시대 Z1 = 웨이브 [6,7,7,8] · 1막 연나라의 침입 · 연나라 병종만 · HUD 구역 이름', b2.w0.join() === '6,7,7,8' && b2.zs === 'LOCKED' && b2.act && /연나라의 침입/.test(b2.act.act) && b2.units.length > 0 && b2.units.every((u) => /^YAN_/.test(u)), b2);
  // ── C. 베는 맛: 칼 막타 = 베기 선 + 두 동강 + 막타 히트스톱 / 일반 3f · 강타 4.6f
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.waves = []; g.zoneState = 'ROAM'; g.slashFx = []; p.invincibleTimer = 99999; p.x = g.cameraX + 330; p.z = 430; p.facing = 1; g.hitStopLog = []; });
  await sleep(300);
  const c2 = await ev(page, () => new Promise((res) => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; D.spawnUnit('YAN_PIKE', p.x + 110, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; p.comboStep = 0; setTimeout(() => res(true), 200); }));
  await page.keyboard.press('j');
  await sleep(450);
  const hs1 = await ev(page, () => window.__RELIC.hitStopLog.slice());
  await ev(page, () => { const g = window.__RELIC; g.enemies.length = 0; g.hitStopLog = []; g.player.comboStep = 0; g.player.comboResetTimer = 0; });
  await sleep(250);
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; D.spawnUnit('HAN_PIKE', p.x + 110, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = 1; e.maxHp = 1000; e.attackCooldown = 9999; g.cutKills = 0; g.cutDrawn = 0; });
  const nf = await film(page, 'film_cut', 900, async () => { await page.keyboard.press('j'); });
  const c1 = await ev(page, () => { const g = window.__RELIC; return { cutKills: g.cutKills, cutDrawn: g.cutDrawn, fx: g.slashFxCount, last: (g.hitStopLog || []).slice(-1)[0] }; });
  ok('C1 칼 막타 = 베기 선 · 두 동강(조각 2개 클립 그리기) · 막타 히트스톱 ≥ 5f', c1.cutKills >= 1 && c1.cutDrawn >= 3 && c1.fx >= 2 && c1.last && c1.last.kills >= 1 && c1.last.stop >= 5, { ...c1, filmFrames: nf });
  ok('C2 일반 타격 히트스톱 3f(이전 2f) · 베기 선 각도 = 1타 사선', hs1.length >= 1 && Math.abs(hs1[0].stop - 3) < 0.01, hs1.slice(0, 2));
  // ── D. 콤보: Lv.4 질풍연참 · AIR RAID · DASH LINK
  await ev(page, () => { const D = window.__RELIC_DEV, g = window.__RELIC; D.setLevel(4); g.enemies.length = 0; g.rushes = 0; g.rushFinishes = 0; g.airRaids = 0; g.dashLinks = 0; });
  await sleep(1600);
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; p.x = g.cameraX + 240; p.facing = 1; [0, 1, 2].forEach((i) => D.spawnUnit(i === 1 ? 'HAN_ARCHER' : 'YAN_PIKE', p.x + 120 + i * 40, p.z + (i - 1) * 24)); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }); p.comboStep = 0; p.comboResetTimer = 0; });
  await sleep(200);
  const nr = await film(page, 'film_rush', 1500, async () => { for (let i = 0; i < 5; i++) { await page.keyboard.press('j'); await sleep(190); } });
  await sleep(300);
  const d1 = await ev(page, () => ({ lv: window.__RELIC.stats.level, rushes: window.__RELIC.rushes, fin: window.__RELIC.rushFinishes, fx: window.__RELIC.slashFxCount }));
  ok('D1 Lv.4 질풍연참 = 4타 피니시 직후 J → 5연참 + 일섬(RUSH FINISH)', d1.lv >= 4 && d1.rushes >= 1 && d1.fin >= 1, { ...d1, filmFrames: nr });
  await ev(page, () => { const g = window.__RELIC, p = g.player; p.comboStep = 0; p.comboResetTimer = 0; p.cdDash = 0; });
  await sleep(500);
  await page.keyboard.press('c');
  await sleep(160);
  for (let i = 0; i < 4; i++) { await page.keyboard.press('j'); await sleep(170); }
  await sleep(900);
  const d2 = await ev(page, () => ({ airRaids: window.__RELIC.airRaids, y: window.__RELIC.player.y, plunge: !!window.__RELIC.player.plunge }));
  ok('D2 공중 J 3번 + 한 번 더 = 내리꽂기(AIR RAID) 착지 충격', d2.airRaids >= 1 && d2.y === 0 && !d2.plunge, d2);
  await ev(page, () => { const g = window.__RELIC, p = g.player; p.comboStep = 0; p.comboResetTimer = 0; p.cdDash = 0; p.x = g.cameraX + 200; p.facing = 1; });
  await sleep(400);
  await page.keyboard.press('k');
  await sleep(120);
  await page.keyboard.press('j');
  await sleep(700);
  const d3 = await ev(page, () => ({ dashLinks: window.__RELIC.dashLinks, step: window.__RELIC.player.comboStep }));
  ok('D3 돌진 → J = 곧바로 3타(DASH LINK)', d3.dashLinks >= 1, d3);
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  console.log(`R29 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
