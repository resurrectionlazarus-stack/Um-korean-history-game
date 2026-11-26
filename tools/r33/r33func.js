// R33 기능 테스트 1회(콘솔 에러 0) — 4시대 전선 배경 4장 실시간 전환(교차) · 전선 날씨 · 번개 · 4대 보스(소손녕 · 아골타 · 살리타이 · 파두반) 출현 · 2페이즈 · 격파 ·
//  거란 · 몽골 리뉴얼 원화 · 부처님의 가호 3FX + 2WAV · R32 무신 4자세 · 이펙트 4 · 김원봉 총기 4자세 · WAV 8종
// 사용: node r33func.js <출력 폴더> [포트]   (tools/r30/h.js 하네스)
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8033;
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const press = async (page, k, n, gap) => { for (let i = 0; i < n; i++) { await page.keyboard.press(k); await sleep(gap); } };
const r33 = (page) => ev(page, () => window.__RELIC_DEV.r33());
const sampleHero = (page, ms) => ev(page, (ms) => new Promise((res) => { const g = window.__RELIC; const out = []; const t0 = performance.now(); const L = () => { const n = g._assetMode && g._assetMode.hero; if (n && out[out.length - 1] !== n) out.push(n); if (performance.now() - t0 < ms) requestAnimationFrame(L); else res(out); }; requestAnimationFrame(L); }), ms);
const seen = (page, key) => ev(page, (key) => { const g = window.__RELIC; return g._assetSeen && g._assetSeen[key] != null ? g.tick - g._assetSeen[key] : -1; }, key);
const stage = (page, units, opt = {}) => ev(page, ({ units, opt }) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0; g.zoneState = 'ROAM'; g.waves = []; g.spawnQ = []; g.mobTele && (g.mobTele.length = 0);
  if (opt.zone != null) g.zoneIdx = opt.zone;
  p.z = 430; p.y = 0; p.vy = 0; p.vx = 0; p.facing = 1; p.invincibleTimer = 99999;
  p.comboStep = 0; p.comboResetTimer = 0; p.cdDash = 0; p.cdUpper = 0; p.rush = null; p.plunge = false; p.ghosts.length = 0;
  g.special = null; g.specialCd = opt.noSpecial ? 1e9 : 0; g.stats.combo = opt.combo || 0; g.comboDecayTimer = 900;
  if (opt.lv) { D.setLevel(opt.lv); g.stats.level = opt.lv; }
  units.forEach(([u, dx, dz, hp]) => { D.spawnUnit(u, p.x + dx, p.z + dz); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = hp; e.attackCooldown = 9999; e.speed = 0; });
}, { units, opt });
const MID = {
  MB_SOSON: { z: 0, bg: 'khitan', labels: ['소손녕의 언월도 베기!', '거란 철기 돌진!', '거란 궁기병 일제 사격!', '80만 대군 호령 연격!'], art: 'boss_sosonnyeong' },
  MB_AGUDA: { z: 1, bg: 'jurchen', labels: ['아골타의 거대 도끼 내려찍기!', '여진 철기 돌격!', '도끼 돌진 베기!', '완안부 도끼 폭풍!', '아골타 3연 도약 참격!'], art: 'boss_aguda' },
  MB_SARTAI: { z: 2, bg: 'mongol', labels: ['몽골 기사(騎射) 일제 사격!', '만곡도 돌진 베기!', '살리타이 만곡도 참격!', '변발 기마대 돌격!', '초원의 3연 돌격!', '만곡도 회오리 연격!'], art: 'boss_sartai' }
};

(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1200);
  await ev(page, () => window.__RELIC_DEV.r31autoQuiz(true));
  // ── A0. MANIFEST 412 = 디스크 · R33 31항목 · 옛 거란 · 몽골 PNG 없음
  const man = await ev(page, async () => { const m = await (await fetch('assets/MANIFEST.json')).json(); const k = Object.keys(m.files); return { n: k.length, r33: k.filter((x) => m.files[x].r33).length, r33added: m.r33.added, oldPng: k.filter((x) => /era4_(khitan_inf|mongol_cav)_.*\.png$/.test(x)).length, webp: k.filter((x) => /era4_(khitan_inf|mongol_cav)_.*\.webp$/.test(x)).length }; });
  ok('A0 MANIFEST 412항목 · R33 31항목 · 거란 보병 · 몽골 기병 webp 6장(옛 png 0)', man.n === 412 && man.r33 === 31 && man.r33added === 31 && man.oldPng === 0 && man.webp === 6, man);
  await toEra(page, 4);
  await sleep(1500);
  const a4 = await ev(page, () => { const g = window.__RELIC; const E = window.__RELIC_DEV.assets.debug.eras['4@' + (g.quality.dpr || 1)]; const d = E.data; return { fronts: Object.keys(d.bg.fronts), actors: Object.keys(d.actors), mobs: Object.keys(d.mobs), fx: Object.keys(d.fx), poses: Object.keys(d.hero.frames) }; });
  ok('A1 4시대 원화 로드 — 전선 배경 4 · 4대 보스 4 · 거란 · 몽골 리뉴얼 몹 · 부처님 3FX · 무신 4FX · 척준경 무신 4자세', a4.fronts.length === 4 && ['boss_sosonnyeong', 'boss_aguda', 'boss_sartai', 'boss_paduban'].every((k) => a4.actors.includes(k)) && ['khitan_inf', 'mongol_cav'].every((k) => a4.mobs.includes(k)) && ['fx_buddha_lotus_halo', 'fx_buddha_palm_light', 'fx_tripitaka_scrolls', 'fx_armor_break', 'fx_fortress_ram', 'fx_azure_dragon', 'fx_blade_storm'].every((k) => a4.fx.includes(k)) && ['cleave_prep', 'cleave_hit', 'charge', 'dragon_stance'].every((k) => a4.poses.includes(k)), a4);
  // ── B. 전선 배경 4장 실시간 전환(교차) · 전선 날씨 · 번개
  await stage(page, []);
  const BG = [], W = [];
  for (let i = 0; i < 4; i++) {
    await ev(page, (i) => window.__RELIC_DEV.r33bg(i), i);
    if (i === 1) { await sleep(650); BG.mid = await r33(page); }
    await sleep(2300);
    const s = await r33(page);
    BG.push(s.bg); W.push([s.weather, s.motes]);
    if (i === 0 && s.bolts === 0) await sleep(4500);
    if (i === 0) BG.bolts = (await r33(page)).bolts;
    await page.screenshot({ path: `${OUT}/r33_map${i + 1}.png` });
  }
  ok('B1 전선 배경 4장 실시간 전환 — 거란 → 여진 → 몽골 → 개경 화염(교차 중 반투명 확인)', BG.map((b) => b.cur).join() === 'khitan,jurchen,mongol,kaegyeong_fire' && BG.every((b) => !b.prev && b.a === 1) && BG.mid.bg.prev === 'khitan' && BG.mid.bg.a > 0 && BG.mid.bg.a < 1, { cur: BG.map((b) => b.cur), mid: BG.mid.bg });
  ok('B2 전선 날씨 — 거란 폭우(빗줄기) · 여진 눈보라 · 몽골 잿가루 · 개경 불티 + 거란 번개', W[0][0] === 'rain' && W[0][1] === 84 && W[1][1] === 96 && W[2][1] === 70 && W[3][1] === 86 && BG.bolts >= 1, { W, bolts: BG.bolts });
  await ev(page, () => window.__RELIC_DEV.r33bg(null));
  // ── C. 몹 리뉴얼 원화(거란 보병 · 몽골 기병)
  const art = await ev(page, () => new Promise((res) => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; ['KHITAN_INF', 'MONGOL_RIDER'].forEach((u, i) => { D.spawnUnit(u, p.x + 160 + i * 160, 420); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; e.speed = 0; }); setTimeout(() => res(g.enemies.map((e) => [e.unit, e._mobArt || null])), 700); }));
  ok('C1 거란 보병 · 몽골 변발 기병 리뉴얼 원화(webp) 렌더', art.length === 2 && art[0][1] === 'khitan_inf' && art[1][1] === 'mongol_cav', art);
  // ── D. 전선 보스 3인 — 실제 구역 흐름(웨이브를 다 막으면 출현) · 기술 예고 문구 · 2페이즈(50%) · 격파 → 구역 정리
  let bi = 1;
  for (const key of Object.keys(MID)) {
    const M = MID[key];
    await ev(page, (z) => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.waves = []; g.spawnQ = []; g.mobTele && (g.mobTele.length = 0); g.zoneIdx = z; g.zoneState = 'LOCKED'; g.midSpawned = {}; g.waveSpawnCd = 0; p.invincibleTimer = 99999; p.z = 430; p.y = 0; }, M.z);
    await page.waitForFunction(() => window.__RELIC.enemies.some((e) => e.isMidBoss), null, { timeout: 8000 });
    await sleep(700);
    await ev(page, () => { const g = window.__RELIC, p = g.player; p.x = g.cameraX + 330; p.facing = 1; g.enemies.filter((e) => !e.isMidBoss).forEach((e) => { e.hp = 1e9; e.attackCooldown = 9999; e.speed = 0; e.x = g.cameraX + 60; }); });
    const lab = await ev(page, () => new Promise((res) => { const g = window.__RELIC; const t0 = performance.now(); const L = () => { const en = g.enemies.find((e) => e.isMidBoss); if (en && en.attackCooldown > 20) en.attackCooldown = 20; const t = (g.mobTele || []).find((x) => x.owner && x.owner.isMidBoss && x.label); if (t) return res(t.label); if (performance.now() - t0 > 7000) return res(null); requestAnimationFrame(L); }; L(); }));
    await sleep(500);
    await ev(page, () => window.__RELIC_DEV.r33hp('mid', 0.45));
    await sleep(500);
    const mid = await ev(page, () => { const g = window.__RELIC; const en = g.enemies.find((e) => e.isMidBoss); return en ? { key: en.mid.key, name: en.name, p2: !!en.r33p2, pats: en.mid.patterns, frame: en._assetFrame } : null; });
    // 공격 자세(slash) 순간 캡처
    await ev(page, () => new Promise((res) => { const g = window.__RELIC; const t0 = performance.now(); const L = () => { const en = g.enemies.find((e) => e.isMidBoss); if (en && en.attackCooldown > 10) en.attackCooldown = 10; if ((en && en._assetFrame === 'slash') || performance.now() - t0 > 5000) return res(); requestAnimationFrame(L); }; L(); }));
    await page.screenshot({ path: `${OUT}/r33_boss${bi}_${key}.png` });
    const sn = await ev(page, (a) => { const g = window.__RELIC; return Object.keys(g._assetSeen || {}).filter((k) => k.startsWith(a + ':')); }, M.art);
    await ev(page, () => window.__RELIC_DEV.r31killAll(false));
    await sleep(300);
    await ev(page, () => window.__RELIC_DEV.r33kill('mid'));
    await page.waitForFunction((z) => window.__RELIC.zoneIdx === z + 1 || window.__RELIC.zoneState === 'GO', M.z, { timeout: 9000 }).catch(() => null);
    await sleep(400);
    const st = await r33(page);
    const logK = st.bossLog.filter((e) => e.key === key).map((e) => e.ev);
    const zs = await ev(page, () => ({ zone: window.__RELIC.zoneIdx, state: window.__RELIC.zoneState, bg: (window.__RELIC._r33bgState || {}).cur }));
    ok(`D${bi} 전선 보스 ${mid && mid.name} — ${M.bg} 전선 클라이맥스 출현 · 원화 ${sn.length}자세 · 기술 예고 '${lab}' · 2페이즈 · 격파 → 구역 정리`, mid && mid.key === key && M.labels.includes(lab) && mid.p2 && sn.length >= 2 && logK.join() === 'spawn,p2,down' && zs.zone === M.z + 1, { mid, sn, logK, zs });
    bi++;
    await ev(page, () => { const g = window.__RELIC; g.enemies.length = 0; g.zoneState = 'ROAM'; });
    await sleep(900);
  }
  // ── E. R32 무신 자세 · 이펙트(4시대): 3타 갑옷 쪼개기 · 돌진 요새 충차 · 일섬 청룡 · 질풍연참 칼날 폭풍 · 베기음
  await ev(page, () => { window.__RELIC.zoneIdx = 1; });
  await stage(page, [['KHITAN_INF', 110, 0, 1e9], ['KHITAN_INF', 190, 10, 1e9]], { lv: 5, noSpecial: true });
  await sleep(900);
  const e0 = await r33(page);
  const h3 = sampleHero(page, 1500);
  await press(page, 'j', 3, 250);
  await sleep(700);
  const f3 = await h3;
  await stage(page, [['KHITAN_INF', 200, 0, 1e9]], { lv: 5, noSpecial: true });
  await sleep(500);
  const hk = sampleHero(page, 700);
  await page.keyboard.press('k');
  await sleep(140);
  await page.screenshot({ path: `${OUT}/r33_e4_charge.png` });
  const fk = await hk;
  await sleep(600);
  await stage(page, [['KHITAN_INF', 140, 0, 1e9], ['KHITAN_INF', 220, 10, 1e9]], { lv: 5, noSpecial: true });
  await sleep(500);
  const hu = sampleHero(page, 1300);
  await ev(page, () => window.__RELIC_DEV.r31ult());
  await sleep(420);
  await page.screenshot({ path: `${OUT}/r33_e4_dragon.png` });
  const fu = await hu;
  await sleep(1600);
  // 질풍연참: Lv.4+ 4타 피니시 직후 J
  await stage(page, [['KHITAN_INF', 110, 0, 1e9], ['KHITAN_INF', 170, 10, 1e9]], { lv: 5, noSpecial: true });
  await sleep(600);
  await press(page, 'j', 4, 260);
  await page.keyboard.press('j');
  await sleep(300);
  await page.screenshot({ path: `${OUT}/r33_e4_storm.png` });
  await sleep(1200);
  const e1 = await r33(page);
  const fxSeen = await ev(page, () => { const g = window.__RELIC; return ['fx_armor_break', 'fx_fortress_ram', 'fx_azure_dragon', 'fx_blade_storm'].filter((k) => g._assetSeen && g._assetSeen['fx:' + k] != null); });
  ok('E1 척준경 무신 자세 — 3타 cleave_prep → cleave_hit · 돌진 charge · 각성 dragon_stance', f3.includes('cleave_prep') && f3.includes('cleave_hit') && fk.includes('charge') && fu.includes('dragon_stance'), { combo: f3, dash: fk, ult: fu });
  ok('E2 무신 이펙트 4종 — 갑옷 쪼개기 · 요새 충차 · 청룡 · 칼날 폭풍', e1.e4.cleaves > e0.e4.cleaves && e1.e4.rams > e0.e4.rams && e1.e4.dragons > e0.e4.dragons && e1.e4.storms > e0.e4.storms && fxSeen.length === 4, { e4: e1.e4, fxSeen });
  // ── F. 최종 보스 파두반 — Z4 웨이브를 막으면 출현 · 예고 문구 · 부처님의 가호(3FX + 2WAV) · 격파
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.waves = []; g.spawnQ = []; g.zoneIdx = 3; g.zoneState = 'LOCKED'; g.r33final = false; g.waveSpawnCd = 0; p.invincibleTimer = 99999; p.z = 430; p.y = 0; });
  await page.waitForFunction(() => !!window.__RELIC.boss, null, { timeout: 8000 });
  const bname = await ev(page, () => window.__RELIC_DATA.eras[3].bossName);
  await sleep(1700);
  await ev(page, () => { const g = window.__RELIC, p = g.player; p.x = g.boss.x - 230; p.facing = 1; });
  const blab = await ev(page, () => new Promise((res) => { const g = window.__RELIC; const t0 = performance.now(); const L = () => { const b = g.boss; if (b && b.attackCooldown > 20) b.attackCooldown = 20; const t = (g.bossTele || []).find((x) => x.label); if (t) return res(t.label); if (performance.now() - t0 > 7000) return res(null); requestAnimationFrame(L); }; L(); }));
  await ev(page, () => new Promise((res) => { const g = window.__RELIC; const t0 = performance.now(); const L = () => { if ((g._assetMode && g._assetMode.boss === 'slash') || performance.now() - t0 > 4000) return res(); requestAnimationFrame(L); }; L(); }));
  await page.screenshot({ path: `${OUT}/r33_boss4_paduban.png` });
  const bseen = await ev(page, () => Object.keys(window.__RELIC._assetSeen || {}).filter((k) => k.startsWith('boss_paduban:')));
  ok(`F1 최종 보스 ${bname} — Z4 웨이브 정리 뒤 출현 · 원화 ${bseen.length}자세 · 예고 '${blab}'`, bname === '홍건적 대장 파두반' && bseen.length >= 2 && ['파두반 쌍도 참격!', '홍건적 화공 포격!'].includes(blab), { bseen, blab });
  const s0 = await ev(page, () => window.__RELIC_DEV.sfxStats());
  await ev(page, () => window.__RELIC_DEV.r33hp('boss', 0.34));
  await page.waitForFunction(() => !!window.__RELIC.buddhaFx, null, { timeout: 8000 });
  const shots = [[44, 'a'], [86, 'b'], [112, 'c']];
  for (const [t, nm] of shots) {
    await page.waitForFunction((t) => !window.__RELIC.buddhaFx || window.__RELIC.buddhaFx.t >= t, t, { timeout: 8000 });
    await page.screenshot({ path: `${OUT}/r33_buddha_${nm}.png` });
  }
  await page.waitForFunction(() => !window.__RELIC.buddhaFx, null, { timeout: 8000 });
  await sleep(300);
  const s1 = await ev(page, () => window.__RELIC_DEV.sfxStats());
  const bd = await r33(page);
  const blog = await ev(page, () => (window.__RELIC.buddhaLog || []).map((e) => e.ev));
  const halo = await seen(page, 'fx:fx_buddha_lotus_halo');
  ok('F2 부처님의 가호 — 범종 → 0.3초 뒤 차임 · 연꽃 광륜 회전 · 손바닥 빛기둥 강림 · 대장경 두루마리 상승 · 결계 파쇄', (s1.by.buddhaBell || 0) > (s0.by.buddhaBell || 0) && (s1.by.buddhaChime || 0) > (s0.by.buddhaChime || 0) && halo >= 0 && bd.buddha && bd.buddha.palm > 20 && bd.buddha.scroll > 20 && blog.includes('shatter'), { bell: s1.by.buddhaBell, chime: s1.by.buddhaChime, buddha: bd.buddha, blog });
  await ev(page, () => window.__RELIC_DEV.r33kill('boss'));
  // 격파 → 약 2초 STAGE CLEAR 숨 고르기(체력 1 유지) → 시험(자동 통과) → 쓰러짐 → 다음 시대
  const bdown = await page.waitForFunction(() => { const g = window.__RELIC; return g.era === 5 || !g.boss || g.boss.dying; }, null, { timeout: 15000 }).then(() => ev(page, () => { const g = window.__RELIC; return { era: g.era, boss: g.boss ? { dying: !!g.boss.dying, hp: g.boss.hp } : null }; })).catch(() => ev(page, () => { const g = window.__RELIC; return { timeout: true, era: g.era, beat: g.clearBeatUntil - g.tick, hp: g.boss && g.boss.hp }; }));
  ok('F3 최종 보스 파두반 격파(STAGE CLEAR 숨 고르기 → 쓰러짐)', !bdown.timeout, bdown);
  // ── G. 6시대 김원봉 총기 4자세(권총 · 쌍권총 · 폭탄 · 소총) · 총소리
  await sleep(2500);
  await toEra(page, 6);
  await sleep(1500);
  await stage(page, [['JP_BAYONET', 120, 0, 1e9], ['JP_BAYONET', 210, 10, 1e9], ['JP_BAYONET', 300, -10, 1e9]], { lv: 3, noSpecial: true });
  await sleep(1200);
  const h6 = sampleHero(page, 2600);
  await press(page, 'j', 2, 250);
  await page.keyboard.press('j');
  await sleep(200);
  await page.screenshot({ path: `${OUT}/r33_e6_pistol.png` });
  await sleep(120);
  await page.keyboard.press('j');
  await sleep(160);
  await page.screenshot({ path: `${OUT}/r33_e6_bomb.png` });
  await sleep(1200);
  const f6 = await h6;
  await stage(page, [['JP_BAYONET', 160, 0, 1e9], ['JP_BAYONET', 240, 10, 1e9]], { lv: 3, noSpecial: true });
  await sleep(1000);
  const h6b = sampleHero(page, 1500);
  await page.keyboard.press('c');
  await sleep(160);
  await press(page, 'j', 3, 150);
  await sleep(900);
  const f6b = await h6b;
  const h6c = sampleHero(page, 1200);
  await ev(page, () => window.__RELIC_DEV.r31ult());
  await sleep(380);
  await page.screenshot({ path: `${OUT}/r33_e6_rifle.png` });
  const f6c = await h6c;
  await sleep(800);
  const e6 = (await r33(page)).e6;
  ok('G1 김원봉 총기 자세 — 모젤 pistol · 폭탄 bomb · 공중 쌍권총 dual · 각성 소총 rifle', f6.includes('pistol') && f6.includes('bomb') && f6b.includes('dual') && f6c.includes('rifle'), { ground: f6, air: f6b, ult: f6c, e6 });
  // ── H. WAV 8종(R32 6 + R33 2) 로드 · 재생
  const smp = await ev(page, () => window.__RELIC_DEV.sfxStats());
  const need = ['buddhaBell', 'buddhaChime', 'bladeSlash1', 'bladeSlash2', 'bladeArmor', 'dragonRoar', 'gunPistol', 'gunRifle'];
  ok('H1 WAV 20종 로드(기존 12 + 새 8) · 새 8종 모두 재생', smp.loaded === 20 && smp.failed === 0 && need.every((k) => (smp.by[k] || 0) >= 1), { loaded: smp.loaded, failed: smp.failed, by: Object.fromEntries(need.map((k) => [k, smp.by[k] || 0])) });
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  console.log(`R33 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  fs.writeFileSync(OUT + '/r33func.json', JSON.stringify(R, null, 1));
  await browser.close();
})().catch((e) => { console.error('TEST CRASH', e); process.exit(1); });
