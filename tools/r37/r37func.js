// R37 기능 테스트 1회(콘솔 에러 0) — 새 효과음 엔진. built-in 브라우저에서 javascript로 확인한 항목(R37-handoff.md 6절)을 Playwright로 옮긴 것.
//  ※ 이 PC(Windows · node 없음)에서는 돌려 보지 못했다. 클라우드 세션에서 bash tools/r37/run_tests.sh 로 돌려 보고, 틀어지면 브라우저 판(같은 절)과 대조할 것.
//  ① 목록 520 · R37 표식 65 · 파일 크기 그대로 ② 엔진: 매니페스트 → 공용 + 1시대 미리 받기 · 전 시대 64개 디코딩 실패 0 · 디코더 지연 보정값
//  ③ 타격음 분기(돌도끼 · 흑요석 · 칼 + 신음) · 기합 ④ 피격(직접 · 실전) · 짐승 사망 ⑤ 병사 쓰러짐 절제(4명 → 1회) · 궁수 당김 · 발사
//  ⑥ 기병 경보 · 말발굽 루프 켜짐/꺼짐 · 돌격 · 화살비 자동 전환 · 덕킹 · 음소거 ⑦ 부처님 강림(에밀레종 · 오라) · 보스 최후 ⑧ ?r37=0 폴백
// 사용: node tools/r37/r37func.js <출력 폴더> [포트=8042]
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8042;
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const diff = (a, b) => { const o = {}; for (const k of Object.keys(b)) if ((b[k] || 0) - (a[k] || 0) > 0) o[k] = (b[k] || 0) - (a[k] || 0); return o; };
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  const ev = (f, a) => page.evaluate(f, a);
  await page.mouse.click(640, 360);
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC && window.__RELIC.player && window.__RELIC.tick > 30, null, { timeout: 30000 });
  await ev(() => window.__RELIC_DEV.r31autoQuiz(true));
  // ① 목록 · 파일
  const man = await ev(async () => {
    const m = await (await fetch('assets/MANIFEST.json')).json();
    const k = Object.keys(m.files); const w = k.filter((x) => m.files[x].r37); const sizes = [];
    for (const f of w) { const r = await fetch(f); const b = await r.arrayBuffer(); sizes.push([f, r.status, b.byteLength === m.files[f].bytes]); }
    return { n: k.length, marked: w.length, bad: sizes.filter((s) => !(s[1] === 200 && s[2])).map((s) => s[0]) };
  });
  ok('A0 MANIFEST 520항목 · R37 표식 65(mp3 64 + sfx_manifest.json)', man.n === 520 && man.marked === 65, { n: man.n, marked: man.marked });
  ok('A1 65개가 목록의 크기 그대로 받아짐', man.bad.length === 0, man.bad);
  // ② 엔진
  await sleep(2500);
  const e1 = await ev(() => { const E = window.__SHINSI_SFX__; return E && E.stats; });
  ok('A2 엔진 준비 · 공용 + 1시대 43개 디코딩 · 실패 0', e1 && e1.state === 'ready' && e1.loaded === 43 && e1.failed === 0, e1 && { state: e1.state, loaded: e1.loaded, failed: e1.failed, errors: e1.errors });
  const e2 = await ev(async () => { const E = window.__SHINSI_SFX__; for (const e of [2, 3, 4, 5, 6]) E.preload(e); await new Promise((r) => setTimeout(r, 3000)); const ks = E.keys(); const res = ks.map((k) => E.play(k, { v: 0.25 })); await new Promise((r) => setTimeout(r, 300)); const s = E.stats; return { keys: ks.length, loaded: s.loaded, failed: s.failed, errors: s.errors, allTrue: res.every((x) => x), onsetMs: s.onsetMs }; });
  ok('A3 전 시대 64개 디코딩 실패 0 · 키 37개 모두 재생 · 디코더 지연 보정 측정됨', e2.loaded === 64 && e2.failed === 0 && e2.allTrue && e2.onsetMs && e2.onsetMs[1] > 0, e2);
  // ③ 타격음 · 기합(1시대)
  await ev(() => { window.__press = () => { window.dispatchEvent(new KeyboardEvent('keydown', { key: 'j', code: 'KeyJ', bubbles: true })); setTimeout(() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'j', code: 'KeyJ', bubbles: true })), 60); }; });
  const c1 = await ev(async () => {
    const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player; const sl = (ms) => new Promise((r) => setTimeout(r, ms));
    g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 400; p.z = 430; p.facing = 1; p.invincibleTimer = 1e9; g.stats.weaponTier = 1;
    D.spawnRole('WOLF', p.x + 90, 430); D.spawnRole('BEAR', p.x + 150, 440); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; });
    const b0 = { ...D.r37().engine.by }; for (let i = 0; i < 10; i++) { window.__press(); await sl(170); } await sl(500);
    const r1 = D.r37(); const by1 = { ...r1.engine.by }; g.stats.weaponTier = 2; for (let i = 0; i < 8; i++) { window.__press(); await sl(170); } await sl(500);
    const r2 = D.r37(); return { axe: { hit: r1.hit, by: Object.fromEntries(Object.keys(by1).filter((k) => (by1[k] || 0) - (b0[k] || 0) > 0).map((k) => [k, by1[k] - (b0[k] || 0)])), voice: r1.voice }, spear: { by: Object.fromEntries(Object.keys(r2.engine.by).filter((k) => (r2.engine.by[k] || 0) - (by1[k] || 0) > 0).map((k) => [k, r2.engine.by[k] - (by1[k] || 0)])) } };
  });
  ok('B1 1시대 돌도끼 타격 = 새 엔진(stone_axe) · 창 = obsidian · 기합 울림', (c1.axe.by.sfx_stone_axe_hit || 0) > 0 && c1.axe.hit.r37 > 0 && ((c1.spear.by.sfx_obsidian_jab || 0) + (c1.spear.by.sfx_obsidian_hit || 0)) > 0 && Object.keys(c1.axe.voice).length > 0, c1);
  // ④ 피격 · 짐승 사망
  const d1 = await ev(async () => {
    const g = window.__RELIC, D = window.__RELIC_DEV, E = window.__SHINSI_SFX__, p = g.player; const sl = (ms) => new Promise((r) => setTimeout(r, ms));
    const by = () => D.r37().engine.by; const direct = [E.heroHit(true, 0), E.heroHit(false, 0)]; await sl(350);
    const b0 = { ...by() }; p.invincibleTimer = 0; g.hitStop = 0; let t0 = Date.now(); let got = false;
    while (Date.now() - t0 < 9000) { await sl(200); if ((by().sfx_hero_hit_light || 0) > (b0.sfx_hero_hit_light || 0)) { got = true; break; } }
    p.invincibleTimer = 1e9; g.enemies.forEach((e) => { e.hp = 1; }); const bb = { ...by() }; const k = D.r31killAll(); await sl(700);
    return { direct, got, killed: k, beastDeath: (by().sfx_beast_death || 0) - (bb.sfx_beast_death || 0), voice: D.r37().voice };
  });
  ok('B2 피격 목소리(직접 · 실전) · 곰 사망음(음높이 분기)', d1.direct[0] && d1.got && d1.beastDeath >= 1, d1);
  // ⑤ 2시대: 칼 + 신음 · 병사 쓰러짐 절제 · 궁수
  await toEra(page, 2); await sleep(1500);
  const f1 = await ev(async () => {
    const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player; const sl = (ms) => new Promise((r) => setTimeout(r, ms)); const by = () => D.r37().engine.by;
    g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 400; p.z = 430; p.facing = 1; p.invincibleTimer = 1e9; g.stats.weaponTier = 1;
    for (let i = 0; i < 4; i++) D.spawnUnit('YAN_PIKE', p.x + 90 + i * 40, 420 + i * 10); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; });
    const b0 = { ...by() }; for (let i = 0; i < 10; i++) { window.__press(); await sl(170); } await sl(400); const b1 = { ...by() };
    g.enemies.forEach((e) => { e.hp = 1; }); const v0 = D.r37().voice.soldierDown || 0; const k = D.r31killAll(); await sl(700); const b2 = { ...by() }; const v1 = D.r37().voice.soldierDown || 0;
    g.enemies.length = 0; for (let i = 0; i < 3; i++) D.spawnUnit('YAN_ARCHER', p.x + 300 + i * 30, 400 + i * 20); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; });
    let t0 = Date.now(); while (Date.now() - t0 < 12000) { await sl(300); const b = by(); if ((b.sfx_bow_shoot || 0) + (b.sfx_arrow_volley || 0) + (b.sfx_bow_full || 0) > (b2.sfx_bow_shoot || 0) + (b2.sfx_arrow_volley || 0) + (b2.sfx_bow_full || 0)) break; } await sl(1500);
    const b3 = by();
    const d = (a, b) => { const o = {}; for (const k2 of Object.keys(b)) if ((b[k2] || 0) - (a[k2] || 0) > 0) o[k2] = (b[k2] || 0) - (a[k2] || 0); return o; };
    return { melee: d(b0, b1), killed: k, soldierPlays: (b2.sfx_soldier_down || 0) - (b1.sfx_soldier_down || 0), soldierHandled: v1 - v0, archers: d(b2, b3) };
  });
  ok('C1 2시대 칼 = sword_slash + 신음 · 병사 4명 처치 → 갑옷 낙하 1회(절제)', (f1.melee.sfx_sword_slash || 0) > 0 && f1.soldierPlays === 1 && f1.soldierHandled === 4, f1);
  ok('C2 궁수: 당김 · 발사(또는 화살비)', (f1.archers.sfx_bow_draw || 0) > 0 && ((f1.archers.sfx_bow_shoot || 0) + (f1.archers.sfx_arrow_volley || 0)) > 0, f1.archers);
  // ⑥ 4시대: 기병 · 화살비 · 덕킹 · 음소거
  await toEra(page, 4); await sleep(1500);
  const g1 = await ev(async () => {
    const g = window.__RELIC, D = window.__RELIC_DEV, E = window.__SHINSI_SFX__, p = g.player; const sl = (ms) => new Promise((r) => setTimeout(r, ms)); const by = () => D.r37().engine.by;
    g.enemies.length = 0; g.zoneState = 'ROAM'; g.zoneIdx = 0; p.x = g.cameraX + 360; p.z = 430; p.facing = 1; p.invincibleTimer = 1e9;
    const b0 = { ...by() }; D.spawnUnit('MONGOL_RIDER', p.x + 420, 420); D.spawnUnit('MONGOL_RIDER', p.x + 480, 450); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; }); await sl(700);
    const c1 = { ...D.r37().cav }; const l1 = Object.keys(D.r37().engine.loops); let t0 = Date.now(); while (Date.now() - t0 < 10000) { await sl(300); if ((by().sfx_cavalry_charge || 0) > (b0.sfx_cavalry_charge || 0)) break; }
    const b1 = { ...by() }; g.enemies.forEach((e) => { e.hp = 1; }); D.r31killAll(); await sl(2800); const c2 = { ...D.r37().cav }; const l2 = Object.keys(D.r37().engine.loops);
    const a = [E.arrowShot(0), E.arrowShot(0), E.arrowShot(0)]; const b2 = { ...by() };
    E.duck(0.35, 0.3, 0.3); await sl(80); const gd = { ...window.__RELIC_SFX.r37gains }; await sl(900); const gd2 = { ...window.__RELIC_SFX.r37gains };
    window.__RELIC_SFX.setMuted(true); const gm = window.__RELIC_SFX.r37gains.trunk; window.__RELIC_SFX.setMuted(false); const gm2 = window.__RELIC_SFX.r37gains.trunk;
    return { horn: (b1.sfx_cavalry_horn || 0) - (b0.sfx_cavalry_horn || 0), hoof1: c1.hoof, loops1: l1, charge: (b1.sfx_cavalry_charge || 0) - (b0.sfx_cavalry_charge || 0), hoof2: c2.hoof, loops2: l2, arrow: a, volley: (b2.sfx_arrow_volley || 0) - (b1.sfx_arrow_volley || 0), duck: [gd.duckBus, gd2.duckBus], mute: [gm, gm2] };
  });
  ok('D1 기병: 경보 1 · 말발굽 루프 켜짐 → 돌격 1 → 모두 쓰러지면 루프 꺼짐', g1.horn === 1 && g1.hoof1 && g1.loops1.includes('sfx_cavalry_hooves_loop') && g1.charge >= 1 && !g1.hoof2 && g1.loops2.length === 0, g1);
  ok('D2 화살 3발 → 화살비 1회 · 덕킹 0.35 → 1 · 음소거 0 → 0.5', g1.volley === 1 && Math.abs(g1.duck[0] - 0.35) < 0.02 && g1.duck[1] === 1 && g1.mute[0] === 0 && g1.mute[1] === 0.5, g1);
  // ⑦ 부처님 강림 · 보스 최후
  const h1 = await ev(async () => {
    const g = window.__RELIC, D = window.__RELIC_DEV, E = window.__SHINSI_SFX__, p = g.player; const sl = (ms) => new Promise((r) => setTimeout(r, ms)); const by = () => D.r37().engine.by;
    g.enemies.length = 0; p.invincibleTimer = 1e9; const b0 = { ...by() }; D.r33final(); await sl(3500); D.r33hp('boss', 0.3);
    let t0 = Date.now(); while (Date.now() - t0 < 20000) { await sl(400); if ((by().sfx_buddha_emille_bell || 0) > (b0.sfx_buddha_emille_bell || 0)) break; }
    const b1 = { ...by() }; let n = 0; while (g.boss && !g.boss.dying && g.boss.hp > 0 && n < 400) { D.hitBoss(); n++; if (n % 20 === 0) await sl(50); }
    t0 = Date.now(); while (Date.now() - t0 < 20000 && !((by().sfx_boss_general_death || 0) > (b1.sfx_boss_general_death || 0))) await sl(400);
    return { bell: (b1.sfx_buddha_emille_bell || 0) - (b0.sfx_buddha_emille_bell || 0), aura: (b1.sfx_buddha_light_aura || 0) - (b0.sfx_buddha_light_aura || 0), bossDeath: (by().sfx_boss_general_death || 0) - (b1.sfx_boss_general_death || 0), ducks: E.stats.ducks, failed: E.stats.failed, errors: E.stats.errors };
  });
  ok('E1 부처님 강림 = 에밀레종 + 광명 오라 · 보스 최후 = 적장 최후(덕킹)', h1.bell === 1 && h1.aura === 1 && h1.bossDeath === 1 && h1.failed === 0, h1);
  await page.screenshot({ path: `${OUT}/e4_boss.png` });
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  // ⑧ ?r37=0 폴백(새 페이지)
  await page.goto(`http://127.0.0.1:${PORT}/index.html?r37=0`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__RELIC && window.__RELIC_DEV, null, { timeout: 30000 });
  await page.mouse.click(640, 360); await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC && window.__RELIC.player && window.__RELIC.tick > 30, null, { timeout: 30000 });
  const i1 = await ev(async () => {
    const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player; const sl = (ms) => new Promise((r) => setTimeout(r, ms));
    const press = () => { window.dispatchEvent(new KeyboardEvent('keydown', { key: 'j', code: 'KeyJ', bubbles: true })); setTimeout(() => window.dispatchEvent(new KeyboardEvent('keyup', { key: 'j', code: 'KeyJ', bubbles: true })), 60); };
    g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 400; p.z = 430; p.facing = 1; p.invincibleTimer = 1e9; g.stats.weaponTier = 1;
    D.spawnRole('WOLF', p.x + 90, 430); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; });
    for (let i = 0; i < 8; i++) { press(); await sl(170); } await sl(400); const r = D.r37(); return { state: r.engine && r.engine.state, k: r.k, hit: r.hit };
  });
  ok('F1 ?r37=0 → 새 엔진 꺼짐 · 타격음은 R35 소리로', i1.state === 'idle' && i1.k === 0 && i1.hit.r35 > 0 && !i1.hit.r37, i1);
  const fails = Object.keys(R).filter((k) => !R[k]);
  console.log(`\n${Object.keys(R).length - fails.length}/${Object.keys(R).length} PASS` + (fails.length ? ' — FAIL: ' + fails.join(' | ') : ''));
  await browser.close();
  process.exit(fails.length ? 1 : 0);
})();
