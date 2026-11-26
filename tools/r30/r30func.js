// R30 기능 테스트 1회(콘솔 에러 0) — 김유신 새 질주 8장 · 연/한 정식 원화 · 2시대 동시 적 상한 · Lv.1~5 입체 콤보 · 조건부 일섬(패링 · 15콤보, 3시대 황금 용오름) · 3D 검기 · 잔상 · 오라
const { open, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const press = async (page, k, n, gap) => { for (let i = 0; i < n; i++) { await page.keyboard.press(k); await sleep(gap); } };
// 무대: 구역 전투가 걸리지 않는 Z1 앞(x 360) · 주인공 무적 · 적 배치(dx, dz, 체력)
const stage = (page, units, opt = {}) => ev(page, ({ units, opt }) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0; g.zoneIdx = 0; g.zoneState = 'ROAM'; g.waves = []; g.spawnQ = [];
  p.x = opt.x || 360; p.z = 430; p.y = 0; p.vy = 0; p.vx = 0; p.facing = 1; p.invincibleTimer = 99999;
  p.comboStep = 0; p.comboResetTimer = 0; p.cdDash = 0; p.cdUpper = 0; p.rush = null; p.plunge = false; p.ghosts.length = 0;
  g.special = null; g.specialCd = opt.noSpecial ? 1e9 : 0; g.stats.combo = opt.combo || 0; g.comboDecayTimer = opt.combo ? 900 : g.comboDecayTimer; g.cameraX = Math.max(0, p.x - 320);
  if (opt.lv) { D.setLevel(opt.lv); g.stats.level = opt.lv; }
  if (opt.tier) g.stats.weaponTier = opt.tier;
  units.forEach(([u, dx, dz, hp]) => { D.spawnUnit(u, p.x + dx, p.z + dz); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = hp; e.attackCooldown = 9999; e.speed = 0; });
}, { units, opt });
const snap = (page) => ev(page, () => { const g = window.__RELIC; return { fx3d: g.fx3dCount || 0, back: g.r3Back || 0, front: g.r3Front || 0, cross: g.crossWaves || 0, crossHits: g.crossHits || 0, spin: g.spinFinishers || 0, spinDrawn: g.spinDrawn || 0, areaBack: g.areaBack || 0, rush: g.rushes || 0, rushFin: g.rushFinishes || 0, dives: g.waveDives || 0, strikes: g.waveStrikes || 0, specials: g.specials || 0, sk: g.specialKills || 0, ink: g.inkDrawn || 0, helix: g.helixDrawn || 0, cut: g.cutKills || 0 }; });
(async () => {
  const { browser, page, errors } = await open('http://127.0.0.1:8031/index.html', { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  // ── A. 정식 원화 2종
  await toEra(page, 2);
  await sleep(1500);
  const a2 = await ev(page, async () => {
    const g = window.__RELIC, D = window.__RELIC_DEV, d = D.assets.debug.eras['2@' + (g.quality.dpr || 1)].data;
    const keys = ['yan_pike', 'yan_archer', 'han_pike', 'han_archer', 'han_elite'];
    const man = await (await fetch('assets/MANIFEST.json')).json();
    const meanOf = (src, w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.drawImage(src, 0, 0, w, h); const P = x.getImageData(0, 0, w, h).data; let s = 0, n = 0; for (let i = 0; i < P.length; i += 4) if (P[i + 3] > 220) { s += P[i] + P[i + 1] + P[i + 2]; n++; } return s / Math.max(1, n) / 3; };
    const img = new Image(); img.src = 'assets/mob/era2_han_pike_idle.webp'; await img.decode();
    const fc = d.mobs.han_pike.frames.idle;
    return { mobs: keys.map((k) => !!(d.mobs[k] && d.mobs[k].frames.idle && d.mobs[k].frames.walk && d.mobs[k].frames.atk)), r30: keys.every((k) => ['idle', 'walk', 'atk'].every((p) => (man.files[`assets/mob/era2_${k}_${p}.webp`] || {}).r30)), tone: +(meanOf(fc, fc.width, fc.height) / meanOf(img, img.naturalWidth, img.naturalHeight)).toFixed(3), fails: D.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)).length };
  });
  ok('A2 2시대 연 · 한 정식 원화 5종 15장(webp) 렌더 · MANIFEST r30 · 굽기 톤다운 생략(≈1.0) · 로드 실패 0', a2.mobs.every(Boolean) && a2.r30 && a2.tone > 0.96 && a2.tone < 1.04 && a2.fails === 0, a2);
  // ── B. 2시대 동시 적 상한 7 · 웨이브 분할
  const b1 = await ev(page, () => new Promise((res) => {
    const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
    g.enemies.length = 0; g.zoneIdx = 0; g.zoneState = 'ROAM'; g.maxAlive = 0; g.spawnQReleased = 0; p.invincibleTimer = 99999;
    for (let i = 0; i < 6; i++) { D.spawnUnit('YAN_PIKE', 640 + i * 40, 380 + (i % 3) * 40); const e = g.enemies[g.enemies.length - 1]; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }
    p.x = 720;
    setTimeout(() => {
      const a = { alive: g.enemies.filter((e) => e.state !== 'DYING').length, q: (g.spawnQ || []).length, waves: g.waves.slice() };
      g.enemies.forEach((e) => { e.hp = 0; });
      setTimeout(() => res({ ...a, maxAlive: g.maxAlive, released: g.spawnQReleased, qAfter: (g.spawnQ || []).length }), 2600);
    }, 1100);
  }));
  ok('B1 2시대 동시 활성 적 ≤ 7 — 넘친 웨이브는 대기열 → 자리가 나면 들여보냄', b1.alive <= 7 && b1.q >= 4 && b1.maxAlive <= 7 && b1.released >= 3, b1);
  // ── C. Lv.1~5 입체 콤보(2시대 해모수 · 칼)
  await stage(page, [['YAN_PIKE', 120, 0, 1e9], ['HAN_PIKE', 160, 26, 1e9]], { lv: 1 });
  await sleep(300);
  const c0 = await snap(page);
  await press(page, 'j', 3, 230);
  await sleep(450);
  const c1 = await snap(page);
  const chop = await ev(page, () => (window.__RELIC.slashFx || []).some((e) => e.a > 1.05 && e.a < 1.4) || (window.__RELIC.hitStopLog || []).length);
  ok('C1 Lv.1 3연참(가로 · 역 · 내려찍기) = 입체 검기 3개 · 뒤쪽(몸 뒤) · 앞쪽 패스 모두 그림', c1.fx3d - c0.fx3d >= 3 && c1.back > c0.back && c1.front > c0.front && !!chop, { fx3d: c1.fx3d - c0.fx3d, back: c1.back - c0.back, front: c1.front - c0.front });
  await stage(page, [['YAN_PIKE', 150, 0, 1e9], ['YAN_ARCHER', 260, 10, 1e9], ['HAN_PIKE', 360, -10, 1e9]], { lv: 2 });
  await sleep(1400);
  const c2a = await snap(page);
  await page.keyboard.press('l');
  await sleep(380);
  await press(page, 'j', 3, 170);
  await sleep(700);
  const c2 = await snap(page);
  ok('C2 Lv.2 비연 올려베기 + 공중 연타 X자 십자검기(관통 적중)', c2.cross - c2a.cross >= 1 && c2.crossHits - c2a.crossHits >= 1, { cross: c2.cross - c2a.cross, hits: c2.crossHits - c2a.crossHits });
  await stage(page, [['YAN_PIKE', 120, 0, 1e9], ['HAN_PIKE', -90, 10, 1e9]], { lv: 3, noSpecial: true });
  await sleep(1400);
  const c3a = await snap(page);
  await press(page, 'j', 4, 230);
  await sleep(250);
  await page.screenshot({ path: OUT + '/r30_spin.png' });
  await sleep(400);
  const c3 = await snap(page);
  ok('C3 Lv.3 360° 원월 회전참 = 몸 한 바퀴(가로 배율) · 뒤쪽 적까지 베기', c3.spin - c3a.spin >= 1 && c3.spinDrawn > c3a.spinDrawn && c3.areaBack - c3a.areaBack >= 1, { spin: c3.spin - c3a.spin, spinDrawn: c3.spinDrawn - c3a.spinDrawn, back: c3.areaBack - c3a.areaBack });
  await stage(page, [['YAN_PIKE', 120, -14, 1e9], ['HAN_ARCHER', 170, 18, 1e9], ['YAN_PIKE', 220, 0, 1e9]], { lv: 4, noSpecial: true });
  await sleep(1400);
  const c4a = await snap(page);
  const gh = ev(page, () => new Promise((res) => { const g = window.__RELIC; let mx = 0; const t0 = performance.now(); const L = () => { mx = Math.max(mx, g.player.ghosts.filter((x) => x.name).length); if (performance.now() - t0 < 1900) requestAnimationFrame(L); else res(mx); }; requestAnimationFrame(L); }));
  await press(page, 'j', 5, 190);
  await sleep(1800);
  const c4 = await snap(page);
  const ghosts = await gh;
  ok('C4 Lv.4 질풍연참 + 일섬 = 원근 검기 · 동작 잔상', c4.rush - c4a.rush >= 1 && c4.rushFin - c4a.rushFin >= 1 && ghosts >= 2, { rush: c4.rush - c4a.rush, fin: c4.rushFin - c4a.rushFin, namedGhostsMax: ghosts });
  await stage(page, [['YAN_PIKE', 120, -14, 1e9], ['HAN_ARCHER', 170, 18, 1e9], ['YAN_PIKE', 220, 0, 1e9]], { lv: 5, noSpecial: true });
  await sleep(1600);
  const c5a = await snap(page);
  await press(page, 'j', 5, 190);
  await sleep(2600);
  const c5 = await snap(page);
  ok('C5 Lv.5 일섬 뒤 공중 도약 급강하 파동격 = 착지 충격파 + 양쪽 X자 검기', c5.dives - c5a.dives >= 1 && c5.strikes - c5a.strikes >= 1 && c5.cross - c5a.cross >= 2, { dives: c5.dives - c5a.dives, strikes: c5.strikes - c5a.strikes, cross: c5.cross - c5a.cross });
  // ── D. 조건부 일섬
  await stage(page, [['YAN_PIKE', 140, -20, 1e9], ['HAN_PIKE', 260, 20, 1e9], ['YAN_ARCHER', -150, 0, 1e9], ['HAN_ARCHER', 360, 0, 1e9]], { lv: 3 });
  await sleep(1300);
  const d0 = await snap(page);
  await ev(page, () => { const g = window.__RELIC; g.enemies.forEach((e) => { e.hp = e.maxHp = 900; }); g.parryTick = g.tick; });
  await page.keyboard.press('j');
  await sleep(110);
  await page.screenshot({ path: OUT + '/r30_special_ink.png' });
  await sleep(1300);
  const d1 = await snap(page);
  const log1 = await ev(page, () => (window.__RELIC.specialLog || []).slice(-1)[0]);
  ok('D1 저스트 패링 뒤 1초 안 J = 시공 일섬(0.2초 수묵 암전 · Z자 관통 · 착지 뒤 일제 양단)', d1.specials - d0.specials === 1 && log1 && log1.reason === 'parry' && log1.n >= 3 && d1.ink > d0.ink && d1.sk - d0.sk >= 2 && d1.cut > d0.cut, { log: log1, ink: d1.ink - d0.ink, kills: d1.sk - d0.sk, cut: d1.cut - d0.cut });
  await toEra(page, 3);
  await sleep(1500);
  const k1 = await ev(page, () => { const g = window.__RELIC, H = window.__RELIC_DEV.assets.debug.eras['3@' + (g.quality.dpr || 1)].data.hero; return { runs: H.runs.length, poseDX: Object.keys(H.poseDX).filter((k) => /^run/.test(k)), anchorX: H.anchorX }; });
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 200; p.invincibleTimer = 99999; });
  await sleep(300);
  const smp = ev(page, () => new Promise((res) => { const g = window.__RELIC; const out = []; const t0 = performance.now(); const L = () => { out.push(g._assetMode && g._assetMode.hero); if (performance.now() - t0 < 1500) requestAnimationFrame(L); else res(out); }; requestAnimationFrame(L); }));
  await page.keyboard.down('ArrowRight');
  await sleep(700);
  await page.screenshot({ path: OUT + '/r30_kim_run.png' });
  await sleep(750);
  await page.keyboard.up('ArrowRight');
  const runs = new Set((await smp).filter((n) => /^run/.test(n || '')));
  ok('A1 3시대 김유신 새 질주 8장 · run 계열 poseDX 보정 없음 · 8장 차례 재생', k1.runs === 8 && k1.poseDX.length === 0 && runs.size === 8, { ...k1, played: runs.size });
  await stage(page, [['BJ_GUARD', 130, -16, 1e9], ['BJ_ARCHER', 200, 18, 1e9], ['BJ_GUARD', -120, 0, 1e9]], { lv: 4, combo: 20 });
  await sleep(1500);
  const e0 = await snap(page);
  await press(page, 'j', 4, 230);
  await sleep(420);
  await page.screenshot({ path: OUT + '/r30_golden_dragon.png' });
  await sleep(1200);
  const e1 = await snap(page);
  const log2 = await ev(page, () => (window.__RELIC.specialLog || []).slice(-1)[0]);
  const dbg2 = await ev(page, () => { const g = window.__RELIC; return { hs: (g.hitStopLog || []).slice(-4).map((h) => [h.step, h.area ? 'A' : '', h.back, h.stop]), combo: g.stats.combo, lv: g.stats.level, era: g.era, state: g.player.state, sp: g.special ? 1 : 0, cd: g.specialCd, tick: g.tick, ex: g.enemies.map((e) => [Math.round(e.x - g.player.x), e.state, Math.round(e.hp)]) }; });
  ok('D2 15콤보(S랭크) 이상 4타 피니시 적중 = 시공 일섬 · 3시대 황금 용오름(나선) 연출', e1.specials - e0.specials === 1 && log2 && log2.reason === 'combo' && log2.era === 3 && e1.helix > e0.helix, { log: log2, helixDraws: e1.helix - e0.helix, kills: e1.sk - e0.sk, dbg2 });
  // ── E. 오라 단계(레벨 · 무기 · 랭크) · 고정 풀
  const au = await ev(page, () => new Promise((res) => {
    const g = window.__RELIC, D = window.__RELIC_DEV, st = g.stats;
    const r = [];
    const set = (lv, t, c) => { st.level = lv; st.weaponTier = t; st.combo = c; g.relicBuff = null; g.relicFx = null; return D.auraStage(); };
    r.push(set(1, 1, 0), set(2, 1, 0), set(3, 1, 0), set(1, 2, 0), set(4, 1, 0), set(1, 3, 0), set(4, 3, 15), set(2, 1, 15));
    const a0 = g.auraDrawn || 0;
    set(5, 3, 30);
    setTimeout(() => res({ stages: r, drawn: (g.auraDrawn || 0) - a0, stageDrawn: g.auraStageDrawn, pool: g.auraPoolSize, live: g.auraLive }), 900);
  }));
  await page.screenshot({ path: OUT + '/r30_aura_full.png' });
  ok('E1 오라 단계 = Lv.1/T1 → 1 · Lv.2~3/T2 → 2 · Lv.4~5/T3 → 3 · 콤보 S랭크+ +1(최대 4) · 매 프레임 그림 · 불티 고정 28칸', au.stages.join() === '1,2,2,2,3,3,4,3' && au.drawn > 20 && au.stageDrawn === 4 && au.pool === 28 && au.live <= 28, au);
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  console.log(`R30 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
