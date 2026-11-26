// R31 기능 테스트 1회(콘솔 에러 0) — 1 · 2시대 정식 질주 8장 · 새 몹 16종 원화(코드 렌더 0) · 해모수 신화 자세 4장 + 이펙트 5종 ·
//  4시대 5대 전선 · 미션 4종 · 보상 아이템 4종 · 동시 적 7 · 6시대 의열단 폭탄 · 모젤 예광탄 · 탄피 · 그림자 잔상 · 의열 폭파 일섬 · 기수 장교 ·
//  타격 이펙트 5종 · WAV 6종
// 사용: node r31func.js <출력 폴더> [포트]   (tools/r30/h.js 하네스 — cdnjs React를 로컬 npm 사본으로 돌림)
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8032;
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const press = async (page, k, n, gap) => { for (let i = 0; i < n; i++) { await page.keyboard.press(k); await sleep(gap); } };
const r31 = (page) => ev(page, () => window.__RELIC_DEV.r31());
// 무대: 구역 전투가 걸리지 않는 곳 · 주인공 무적 · 적 배치(병종, dx, dz, 체력)
const stage = (page, units, opt = {}) => ev(page, ({ units, opt }) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0; g.zoneState = 'ROAM'; g.waves = []; g.spawnQ = [];
  if (opt.zone != null) g.zoneIdx = opt.zone;
  p.z = 430; p.y = 0; p.vy = 0; p.vx = 0; p.facing = 1; p.invincibleTimer = 99999;
  p.comboStep = 0; p.comboResetTimer = 0; p.cdDash = 0; p.cdUpper = 0; p.rush = null; p.plunge = false; p.ghosts.length = 0;
  g.special = null; g.specialCd = opt.noSpecial ? 1e9 : 0; g.stats.combo = opt.combo || 0; g.comboDecayTimer = 900;
  if (opt.lv) { D.setLevel(opt.lv); g.stats.level = opt.lv; }
  if (opt.tier) g.stats.weaponTier = opt.tier;
  units.forEach(([u, dx, dz, hp]) => { D.spawnUnit(u, p.x + dx, p.z + dz); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = hp; e.attackCooldown = 9999; e.speed = 0; });
}, { units, opt });
// 프레임마다 주인공 원화 동작 이름을 모은다
const sampleHero = (page, ms) => ev(page, (ms) => new Promise((res) => { const g = window.__RELIC; const out = []; const t0 = performance.now(); const L = () => { const n = g._assetMode && g._assetMode.hero; if (n && out[out.length - 1] !== n) out.push(n); if (performance.now() - t0 < ms) requestAnimationFrame(L); else res(out); }; requestAnimationFrame(L); }), ms);
const seen = (page, key) => ev(page, (key) => { const g = window.__RELIC; return g._assetSeen && g._assetSeen[key] != null ? g.tick - g._assetSeen[key] : -1; }, key);
// 원화 몹 렌더 확인: 병종을 세워 몇 프레임 그린 뒤 _mobArt(원화 이름)가 붙었는지
const artOf = (page, units) => ev(page, (units) => new Promise((res) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0; g.zoneState = 'ROAM';
  units.forEach((u, i) => { D.spawnUnit(u, p.x + 120 + (i % 4) * 110, 380 + (i >> 2) * 60); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; e.speed = 0; });
  setTimeout(() => res(g.enemies.map((e) => [e.unit, e._mobArt || null])), 700);
}), units);

(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await ev(page, () => window.__RELIC_DEV.r31autoQuiz(true));
  // ── A0. MANIFEST = 디스크(369) · R31 표식 83
  const man = await ev(page, async () => { const m = await (await fetch('assets/MANIFEST.json')).json(); const f = m.files; return { n: Object.keys(f).length, r31: Object.values(f).filter((e) => e.r31).length, added: m.r31 && m.r31.added, replaced: m.r31 && m.r31.replaced.length }; });
  ok('A0 MANIFEST 369항목(디스크와 같음) · R31 패치 83항목(새 67 · 교체 16)', man.n === 369 && man.r31 === 83 && man.added === 67 && man.replaced === 16, man);
  // ── A1. 1시대 대사냥꾼 정식 질주 8장 + 손에 든 무기
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 99999; });
  const h1 = sampleHero(page, 1500);
  await page.keyboard.down('ArrowRight');
  await sleep(650);
  await page.screenshot({ path: OUT + '/r31_hunter_run.png' });
  await sleep(850);
  await page.keyboard.up('ArrowRight');
  const run1 = (await h1).filter((n) => /^run/.test(n));
  const w1 = await ev(page, () => { const g = window.__RELIC, H = window.__RELIC_DEV.assets.debug.eras['1@' + (g.quality.dpr || 1)].data.hero; return { runs: H.runs.length, weapon: !!(H.weapon && H.weapons && H.weapons[1]), drawnTier: g.player._wDrawnTier || null }; });
  ok('A1 1시대 대사냥꾼 정식 질주 8장 차례 재생 · 무기 손에 얹힘', w1.runs === 8 && new Set(run1).size === 8 && w1.weapon, { ...w1, played: new Set(run1).size });
  // 1시대 도끼 타격 = 파편 이펙트
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 99999; p.facing = 1; p.comboStep = 0; D.spawnRole('WOLF', p.x + 110, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; e.speed = 0; });
  await sleep(400);
  const ax0 = (await r31(page)).hfxSeen;
  await press(page, 'j', 3, 240);
  await sleep(500);
  const ax1 = (await r31(page)).hfxSeen;
  // ── B. 2시대 해모수 신화급 개편
  await toEra(page, 2);
  await sleep(1500);
  const e2 = await ev(page, () => { const g = window.__RELIC, D = window.__RELIC_DEV, d = D.assets.debug.eras['2@' + (g.quality.dpr || 1)].data; return { runs: d.hero.runs.length, poses: ['heavy_cleave', 'slam_prep', 'slam_hit', 'summon_sky'].filter((k) => d.hero.frames[k]), fx: Object.keys(d.fx).filter((k) => /^fx_/.test(k)), fails: D.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)).length }; });
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 99999; });
  const h2 = sampleHero(page, 1500);
  await page.keyboard.down('ArrowRight');
  await sleep(650);
  await page.screenshot({ path: OUT + '/r31_haemosu_run.png' });
  await sleep(850);
  await page.keyboard.up('ArrowRight');
  const run2 = new Set((await h2).filter((n) => /^run/.test(n)));
  ok('B1 해모수 정식 질주 8장 차례 재생 · 신화 자세 4장 · 이펙트 5종 로드(실패 0)', e2.runs === 8 && run2.size === 8 && e2.poses.length === 4 && e2.fx.length === 5 && e2.fails === 0, { ...e2, played: run2.size });
  // B2. 3타 = heavy_cleave + 호랑이 발톱 · 검기 폭 ×1.4 · 강타 히트스톱 +1.5
  await stage(page, [['YAN_PIKE', 120, 0, 1e9], ['HAN_PIKE', 170, 24, 1e9]], { lv: 2, noSpecial: true });
  await sleep(1400);
  const b2a = await r31(page);
  const hp2 = sampleHero(page, 1500);
  await press(page, 'j', 2, 240);
  await page.keyboard.press('j');
  const beam = ev(page, () => new Promise((res) => { const g = window.__RELIC; let mx = 0; const P0 = g.projectiles.push; g.projectiles.push = function (...a) { a.forEach((q) => { if (!q.cross) mx = Math.max(mx, q.size); }); return P0.apply(this, a); }; setTimeout(() => { delete g.projectiles.push; res(mx); }, 700); }));
  await sleep(150);
  await page.screenshot({ path: OUT + '/r31_e2_claw.png' });
  const beamSize = await beam;
  await sleep(600);
  const poses2 = await hp2;
  const b2 = await r31(page);
  const hs2 = await ev(page, () => (window.__RELIC.hitStopLog || []).slice(-6).map((h) => [h.step, h.heavy, +h.stop.toFixed(2)]));
  ok('B2 3타 = atk3_prep → heavy_cleave + 호랑이 발톱(fx_tiger_claw) · 검기 폭 ×1.4(44 → 61.6) · 강타 히트스톱 4.6 → 6.1', poses2.includes('heavy_cleave') && b2.e2.cleaves - b2a.e2.cleaves >= 1 && (await seen(page, 'fx:fx_tiger_claw')) >= 0 && Math.abs(beamSize - 61.6) < 0.5 && hs2.some((h) => h[1] && h[2] >= 6.05), { poses: poses2, beamSize, hs: hs2 });
  // B3. Lv.3 4타 = 곰의 내려찍기(slam_prep → slam_hit + 곰 · 천둥)
  await stage(page, [['YAN_PIKE', 110, 0, 1e9], ['HAN_PIKE', -100, 10, 1e9]], { lv: 3, noSpecial: true });
  await sleep(1400);
  const b3a = await r31(page);
  const hp3 = sampleHero(page, 2000);
  await press(page, 'j', 3, 260);
  await page.keyboard.press('j');
  await sleep(300);
  await page.screenshot({ path: OUT + '/r31_e2_slam.png' });
  await sleep(900);
  const poses3 = await hp3;
  const b3 = await r31(page);
  ok('B3 Lv.3 4타 = slam_prep → slam_hit + 곰(fx_bear_slam) · 천둥(fx_thunder_crack) · 둘레 충격', poses3.includes('slam_prep') && poses3.includes('slam_hit') && b3.e2.slams - b3a.e2.slams >= 1 && (await seen(page, 'fx:fx_bear_slam')) >= 0 && (await seen(page, 'fx:fx_thunder_crack')) >= 0, { poses: poses3.filter((n) => !/^run|idle/.test(n)), slams: b3.e2.slams - b3a.e2.slams });
  // B4. Lv.5 급강하 파동격 = 공중 slam_prep → 착지 slam_hit + 곰 · 천둥
  await stage(page, [['YAN_PIKE', 120, -14, 1e9], ['HAN_ARCHER', 170, 18, 1e9], ['YAN_PIKE', 220, 0, 1e9]], { lv: 5, noSpecial: true });
  await sleep(1600);
  const b4a = await r31(page);
  const hp4 = sampleHero(page, 4200);
  await press(page, 'j', 4, 260);
  await sleep(280);
  await page.keyboard.press('j');
  await sleep(3400);
  const poses4 = await hp4;
  const b4 = await r31(page);
  const dv = await ev(page, () => ({ dives: window.__RELIC.waveDives || 0, strikes: window.__RELIC.waveStrikes || 0 }));
  ok('B4 Lv.5 급강하 파동격 = 공중 slam_prep → 착지 slam_hit + 곰 · 천둥', dv.dives >= 1 && dv.strikes >= 1 && poses4.includes('slam_prep') && poses4.includes('slam_hit') && b4.e2.slams - b4a.e2.slams >= 1, { ...dv, slams: b4.e2.slams - b4a.e2.slams });
  // B5. SOLAR FLASH = 하늘 소환 + 광륜 + 거대 비파형 동검
  await stage(page, [['YAN_PIKE', 140, -20, 3000], ['HAN_PIKE', 260, 20, 3000], ['YAN_ARCHER', -150, 0, 3000], ['HAN_ARCHER', 360, 0, 3000]], { lv: 5 });
  await sleep(1500);
  const b5a = await r31(page);
  const hp5 = sampleHero(page, 2400);
  await ev(page, () => window.__RELIC_DEV.special('dev'));
  await sleep(230);
  await page.screenshot({ path: OUT + '/r31_e2_summon.png' });
  await sleep(800);
  await page.screenshot({ path: OUT + '/r31_e2_sky_sword.png' });
  await sleep(1300);
  const poses5 = await hp5;
  const b5 = await r31(page);
  ok('B5 SOLAR FLASH = summon_sky + 몸 뒤 청동 거울 광륜 + 하늘에서 꽂히는 거대 비파형 동검 + 천둥', poses5.includes('summon_sky') && b5.e2.summons - b5a.e2.summons >= 1 && b5.e2.skySwords - b5a.e2.skySwords >= 1 && (await seen(page, 'fx:fx_bronze_mirror_halo')) >= 0 && (await seen(page, 'fx:fx_giant_lute_sword')) >= 0, { poses: poses5.filter((n) => !/^run|idle/.test(n)), summons: b5.e2.summons - b5a.e2.summons, swords: b5.e2.skySwords - b5a.e2.skySwords });
  // B6. 각성 = 하늘 소환 + 광륜(크게) + 거대 동검
  await stage(page, [['YAN_PIKE', 160, -20, 1e9], ['HAN_PIKE', 280, 20, 1e9]], { lv: 5, noSpecial: true });
  await sleep(1200);
  const b6a = await r31(page);
  await ev(page, () => window.__RELIC_DEV.r31ult());
  await sleep(950);
  await page.screenshot({ path: OUT + '/r31_e2_ult.png' });
  await sleep(1600);
  const b6 = await r31(page);
  ok('B6 각성 = 하늘 소환 + 광륜 + 거대 동검 + 천둥 5줄기', b6.e2.summons - b6a.e2.summons >= 1 && b6.e2.skySwords - b6a.e2.skySwords >= 1, { summons: b6.e2.summons - b6a.e2.summons, swords: b6.e2.skySwords - b6a.e2.skySwords });
  // ── C. 3시대 정식 원화 5종
  await toEra(page, 3);
  await sleep(1500);
  const a3 = await artOf(page, ['BJ_GUARD', 'BJ_ARCHER', 'GG_PIKE', 'GG_CAV', 'WA_RAIDER']);
  await page.screenshot({ path: OUT + '/r31_mobs_e3.png' });
  // ── D. 4시대 5대 전선 · 미션 · 보상 · 동시 적 7
  await toEra(page, 4);
  await sleep(1500);
  const a4 = await artOf(page, ['WAKOU_SWORD', 'JURCHEN_INF', 'JURCHEN_CAV', 'REDTURBAN_INF', 'REDTURBAN_ELITE']);
  await page.screenshot({ path: OUT + '/r31_mobs_e4.png' });
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; g.zoneIdx = 0; g.zoneState = 'ROAM'; g.waves = []; g.spawnQ = []; g.maxAlive = 0; g.spawnQReleased = 0; p.invincibleTimer = 99999; D.setLevel(5); g.stats.level = 5; });
  await sleep(600);
  const shots = {};
  const t4 = Date.now();
  let last = null;
  while (Date.now() - t4 < 150000) {
    const st = await ev(page, () => { const g = window.__RELIC; return { zs: g.zoneState, zi: g.zoneIdx, boss: !!g.bossActive, front: g.front4, m: g.mission && g.mission.key + ':' + g.mission.state, gs: window.__RELIC.gameState || null }; });
    if (st.zi >= 3 && st.boss) break;
    if (st.zs === 'LOCKED') {
      await page.keyboard.up('ArrowRight');
      if (!shots[st.front] && st.front) {
        await sleep(450);
        await page.screenshot({ path: OUT + `/r31_e4_front_${st.front}.png` });
        shots[st.front] = 1;
      }
      await ev(page, () => { const g = window.__RELIC; if (g.front4 === 'wakou' && g.mission && g.mission.key === 'wakou' && g.mission.state === 'run') { g.stats.combo += 25; g.comboDecayTimer = 900; } g.enemies.forEach((e) => { if (e.isMidBoss && e.state !== 'DYING') e.hp = 0; }); window.__RELIC_DEV.r31killAll(true); });
      if (st.m !== last) {
        last = st.m;
        if (/:ok$/.test(st.m || '')) { await sleep(320); await page.screenshot({ path: OUT + `/r31_e4_item_${st.m.split(':')[0]}.png` }); }
      }
      await sleep(380);
    } else {
      await page.keyboard.down('ArrowRight');
      await sleep(300);
    }
  }
  await page.keyboard.up('ArrowRight');
  const d4 = await ev(page, () => { const g = window.__RELIC; return { frontLog: (g.frontLog || []).map((f) => f.key + '@Z' + (f.zone + 1)), missionLog: (g.missionLog || []).filter((m) => m.ev !== 'start').map((m) => m.key + ':' + m.ev), items: (g.itemLog || []).map((i) => i.id), maxAlive: g.maxAlive, released: g.spawnQReleased || 0, zone: g.zoneIdx, boss: !!g.bossActive }; });
  ok('D1 4시대 5대 전선 순서 = 거란(Z1) → 여진(Z2) → 몽골(Z2 · 천호장) → 왜구(Z3) → 홍건적(Z3) → Z4 결전', d4.frontLog.join() === 'khitan@Z1,jurchen@Z2,mongol@Z2,wakou@Z3,redturban@Z3' && d4.zone === 3 && d4.boss, d4);
  ok('D2 스몰 미션 4종 성공 → 보상 4종(인장 · 군기 · 영약 · 보검) 지급', d4.missionLog.join() === 'jurchen:ok,mongol:ok,wakou:ok,redturban:ok' && d4.items.join() === 'seal,banner,elixir,blade', { missions: d4.missionLog, items: d4.items });
  ok('D3 4시대 동시 활성 적 ≤ 7 · 넘친 적은 대기열로 나눠 들여보냄', d4.maxAlive <= 7 && d4.released >= 1, { maxAlive: d4.maxAlive, released: d4.released });
  // D4. 실패 경로(여진 25초 초과) · 보상 효과(인장 공격력 · 군기 무적/오라 4 · 영약 회복 · 보검 검기 + 양단)
  const d5 = await ev(page, () => new Promise((res) => {
    const g = window.__RELIC, D = window.__RELIC_DEV, st = g.stats, p = g.player;
    g.mission = null; D.r31mission('jurchen'); g.mission.t0 = g.tick - 1600;
    setTimeout(() => {
      const fail = g.mission.state;
      g.r31buff = {}; p.invincibleTimer = 0; st.hp = Math.round(st.maxHp * 0.3); st.ult = 0;
      D.r31item('banner'); const inv = p.invincibleTimer, aura = D.auraStage();
      D.r31item('elixir'); const hp = +(st.hp / st.maxHp).toFixed(2), ult = st.ult;
      D.r31item('seal'); D.r31item('blade');
      res({ fail, inv, aura, hp, ult, buff: Object.assign({}, g.r31buff) });
    }, 300);
  }));
  ok('D4 미션 실패 판정(여진 25초 초과) · 군기 = 무적 8초 · 오라 4 · 영약 = 체력 +60% · 각성 100 · 인장/보검 타이머', d5.fail === 'fail' && d5.inv >= 470 && d5.aura === 4 && d5.hp >= 0.89 && d5.ult === 100 && d5.buff.seal > 700 && d5.buff.blade > 880, d5);
  await ev(page, () => { const g = window.__RELIC; g.bossActive = false; g.boss = null; g.bossIntro = 0; g.letterboxTarget = 0; });
  await stage(page, [['JURCHEN_INF', 110, 0, 1e9], ['REDTURBAN_INF', 150, 20, 1e9]], { zone: 0, noSpecial: true });
  await sleep(900);
  // 체력 1은 누르기 직전에(기다리는 동안 선녀 동료의 빛탄이 먼저 쓰러뜨리지 않게)
  const bl0 = await ev(page, () => { const g = window.__RELIC; g.enemies.forEach((e) => { e.hp = 1; }); return { cross: g.cutKills || 0, prj: 0 }; });
  const prjMax = ev(page, () => new Promise((res) => { const g = window.__RELIC; let mx = 0; const P0 = g.projectiles.push; g.projectiles.push = function (...a) { mx += a.filter((q) => !q.cross).length; return P0.apply(this, a); }; setTimeout(() => { delete g.projectiles.push; res(mx); }, 900); }));
  await page.keyboard.press('j');
  await sleep(160);
  await page.screenshot({ path: OUT + '/r31_e4_blade.png' });
  const pm = await prjMax;
  const bl1 = await ev(page, () => ({ cut: window.__RELIC.cutKills || 0 }));
  ok('D5 청룡 보검 = 1타에도 검기 발사 · 막타 양단', pm >= 1 && bl1.cut - bl0.cross >= 1, { beams: pm, cuts: bl1.cut - bl0.cross });
  // ── E. 5시대 청 팔기군 기병
  await toEra(page, 5);
  await sleep(1500);
  const a5 = await artOf(page, ['QING_RIDER']);
  // ── F. 6시대 약산 김원봉
  await toEra(page, 6);
  await sleep(1500);
  const a6 = await artOf(page, ['FR_RIFLE', 'FR_BAYONET', 'US_RIFLE', 'US_BAYONET', 'JP_OFFICER']);
  await page.screenshot({ path: OUT + '/r31_mobs_e6.png' });
  const fails = await ev(page, () => window.__RELIC_DEV.assets.debug.log.filter((l) => /실패|누락|failed|코드 렌더링/.test(l)));
  const all = [...a3, ...a4, ...a5, ...a6];
  ok('A2 새 몹 16종(3시대 5 · 4시대 5 · 5시대 1 · 6시대 5) 모두 원화 렌더 · 코드 스프라이트 대체 0 · 로드 실패 0', all.length === 16 && all.every((x) => x[1]) && fails.length === 0, { art: all.map((x) => x[0] + '=' + x[1]), fails });
  // F1. 3타 모젤 C96(총구 섬광 · 관통 예광탄 · 황금 탄피) → 4타 의열단 폭탄
  await stage(page, [['JP_BAYONET', 120, 0, 1e9], ['JP_BAYONET', 210, 10, 1e9], ['JP_BAYONET', 300, -10, 1e9]], { lv: 3, noSpecial: true });
  await sleep(1400);
  const f0 = await r31(page);
  await press(page, 'j', 2, 250);
  await page.keyboard.press('j');
  await sleep(200);
  await page.screenshot({ path: OUT + '/r31_e6_mauser.png' });
  await sleep(120);
  await page.keyboard.press('j');
  await sleep(700);
  await page.screenshot({ path: OUT + '/r31_e6_bomb.png' });
  await sleep(900);
  const f1 = await r31(page);
  ok('F1 3타 모젤 C96 3연사(관통 예광탄 · 총구 섬광 · 황금 탄피) → 4타 의열단 폭탄 투척 · 폭발(화구 · 화약 연기 · 파편 · 충격 링)', f1.e6.mauser - f0.e6.mauser >= 3 && f1.e6.throws - f0.e6.throws >= 1 && f1.e6.blasts - f0.e6.blasts >= 1 && [10, 11, 12, 13, 14, 15].every((k) => (f1.hfxSeen[k] || 0) > (f0.hfxSeen[k] || 0)), { mauser: f1.e6.mauser - f0.e6.mauser, throws: f1.e6.throws - f0.e6.throws, blasts: f1.e6.blasts - f0.e6.blasts });
  // F2. 공중 3타 모젤 2연사 · F3. 돌진 = 야습 그림자 잔상
  await stage(page, [['JP_BAYONET', 160, 0, 1e9], ['JP_BAYONET', 240, 10, 1e9]], { lv: 3, noSpecial: true });
  await sleep(1200);
  const f2a = await r31(page);
  await page.keyboard.press('c');
  await sleep(160);
  await press(page, 'j', 3, 150);
  await sleep(900);
  await page.keyboard.press('k');
  await sleep(90);
  await page.screenshot({ path: OUT + '/r31_e6_shadow.png' });
  await sleep(700);
  const f2 = await r31(page);
  ok('F2 공중 3타 모젤 2연사 · 돌진 = 어두운 야습 그림자 잔상', f2.e6.airMauser - f2a.e6.airMauser >= 1 && f2.e6.shadow - f2a.e6.shadow >= 3, { air: f2.e6.airMauser - f2a.e6.airMauser, shadowDraws: f2.e6.shadow - f2a.e6.shadow });
  // F4. 의열 폭파 일섬(UIYEOL BLAST)
  await stage(page, [['JP_BAYONET', 140, -20, 3000], ['JP_BAYONET', 260, 20, 3000], ['JP_BAYONET', -150, 0, 3000], ['MG_NEST', 360, 0, 3000]], { lv: 4 });
  await sleep(1300);
  const f4a = await r31(page);
  await ev(page, () => window.__RELIC_DEV.special('dev'));
  await sleep(560);
  await page.screenshot({ path: OUT + '/r31_e6_uiyeol_mark.png' });
  await sleep(330);
  await page.screenshot({ path: OUT + '/r31_e6_uiyeol_blast.png' });
  await sleep(1400);
  const f4 = await r31(page);
  const sl = await ev(page, () => (window.__RELIC.specialLog || []).slice(-1)[0]);
  ok('F4 의열 폭파 일섬 = Z자 돌진 표적에 폭탄 표식 → 착지 연쇄 폭발 + 태극 광선 + 양단', f4.e6.specials - f4a.e6.specials >= 1 && f4.e6.blasts - f4a.e6.blasts >= 3 && (f4.hfxSeen[16] || 0) > (f4a.hfxSeen[16] || 0) && sl && sl.era === 6, { blasts: f4.e6.blasts - f4a.e6.blasts, log: sl });
  // F5. 일본군 기수 장교(원화) — 쓰러뜨리면 주변 병사 동요
  await stage(page, [['JP_BAYONET', 160, 20, 1e9], ['JP_BAYONET', 300, -20, 1e9]], { lv: 4, noSpecial: true });
  await ev(page, () => { window.__RELIC_DEV.r31officer(); });
  await sleep(1100);
  await page.screenshot({ path: OUT + '/r31_e6_officer.png' });
  const f5 = await ev(page, () => { const g = window.__RELIC; const o = g.enemies.find((e) => e.unit === 'JP_OFFICER'); o.state = 'ACTIVE'; o.hp = 1; window.__RELIC_DEV.r31killAll(false); return { art: o._mobArt, stun: g.enemies.filter((e) => e.unit === 'JP_BAYONET').map((e) => e.hitStun) }; });
  await sleep(300);
  const f5b = await r31(page);
  ok('F5 일본군 기수 장교 원화 · 처치 = FLAG DOWN(주변 병사 경직)', !!f5.art && f5b.e6.officers >= 1 && f5b.e6.officerDowns >= 1, { ...f5, officers: f5b.e6.officers, downs: f5b.e6.officerDowns });
  // ── G. 타격 이펙트 5종 · 2프레임 백색 섬광
  await stage(page, [['JP_BAYONET', 110, 0, 1e9], ['MG_NEST', 170, 20, 1e9]], { lv: 4, noSpecial: true });
  await sleep(900);
  await press(page, 'j', 2, 240);
  await sleep(60);
  await page.screenshot({ path: OUT + '/r31_hitfx.png' });
  await sleep(500);
  const gfx = await r31(page);
  const wf = await ev(page, () => window.__RELIC.enemies.filter((e) => e._wf).length);
  const sv = gfx.hfxSeen;
  ok('G1 타격 이펙트 5종 = ① 히트스타 ② 방향 스파크 ③ 먹 튐 + 충격 링 ④ 2프레임 백색 섬광 + 발밑 먼지 ⑤ 칼 베기선 · 도끼 파편 · 총 연기 고리 · 청백 금속 불꽃(고정 풀 128)', [1, 2, 3, 4, 5, 6, 8, 9].every((k) => sv[k] > 0) && (ax1[7] || 0) > (ax0[7] || 0) && wf >= 1 && gfx.hfxDrawn > 100, { seen: sv, axe: (ax1[7] || 0) - (ax0[7] || 0), whiteFlash: wf, drawn: gfx.hfxDrawn });
  // ── H. WAV 6종
  const smp = await ev(page, () => window.__RELIC_DEV.sfxStats());
  const need = ['sliceCrisp1', 'sliceCrisp2', 'sliceSever', 'sliceFlurry', 'missionGong', 'bombBlast'];
  ok('H1 WAV 12종 로드(기존 6 + 새 6) · 새 6종 모두 재생(crisp 1/2 번갈아 · 양단 · 연참/일섬 · 미션 징 · 의열단 폭탄)', smp.loaded === 12 && smp.failed === 0 && need.every((k) => (smp.by[k] || 0) >= 1), { loaded: smp.loaded, failed: smp.failed, by: Object.fromEntries(need.map((k) => [k, smp.by[k] || 0])) });
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  console.log(`R31 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
