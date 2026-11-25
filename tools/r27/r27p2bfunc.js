// R27 2차 기능 테스트 1회(콘솔 에러 0) — 4~6시대 일반 몹 6종 원화(유닛 키 매핑 · 톤다운 생략) · 전투 효과음 WAV 6종(디코딩 · 트리거 · 폴백) · 김유신 질주 프레임 수
const { open, start, toEra } = require('./h');
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const keyTap = async (page, k, n = 1, gap = 170) => { for (let i = 0; i < n; i++) { await page.keyboard.press(k); await page.waitForTimeout(gap); } };
const by = (page) => ev(page, () => { const s = window.__RELIC_DEV.sfxStats(); return s ? { ...s.by } : {}; });
// 구운 idle 평균 밝기 ÷ 원본 평균 밝기(불투명 픽셀) — 굽기 톤다운이 걸렸는지
const toneOf = (page, era, key, file) => ev(page, async ({ era, key, file }) => {
  const g = window.__RELIC, d = window.__RELIC_DEV.assets.debug.eras[era + '@' + (g.quality.dpr || 1)].data;
  const fc = d.mobs && d.mobs[key] && d.mobs[key].frames.idle;
  if (!fc) return null;
  const meanOf = (src, w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.drawImage(src, 0, 0, w, h); const D = x.getImageData(0, 0, w, h).data; let s = 0, n = 0; for (let i = 0; i < D.length; i += 4) if (D[i + 3] > 220) { s += D[i] + D[i + 1] + D[i + 2]; n++; } return s / Math.max(1, n) / 3; };
  const img = new Image(); img.src = file; await img.decode();
  return +(meanOf(fc, fc.width, fc.height) / meanOf(img, img.naturalWidth, img.naturalHeight)).toFixed(3);
}, { era, key, file });
const artOf = (page, list) => ev(page, (list) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0; g.zoneState = 'ROAM'; p.invincibleTimer = 99999;
  list.forEach((u, i) => { D.spawnUnit(u, p.x + 160 + i * 130, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; });
  return new Promise((res) => setTimeout(() => res(g.enemies.map((e) => [e.unit, e._mobArt || null])), 600));
}, list);
(async () => {
  const URL = 'http://127.0.0.1:8027/index.html';
  const { browser, page, errors } = await open(URL, { w: 1280, h: 720, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await page.waitForFunction(() => { const s = window.__RELIC_DEV.sfxStats(); return s && s.loaded + s.failed >= 6; }, null, { timeout: 20000 });
  const st0 = await ev(page, () => window.__RELIC_DEV.sfxStats());
  ok('S1 첫 입력 때 WAV 6종 디코딩 캐시(실패 0)', st0.loaded === 6 && st0.failed === 0 && !st0.off, { loaded: st0.loaded, failed: st0.failed });
  const wolfTone = await toneOf(page, 1, 'wolf', 'assets/mob/era1_wolf_idle.png');

  // ── 1시대 연격: 1 · 2타 검격 · 3 · 4타 강타 · 호흡 피니시 · 볼링 ──
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2500);
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; p.invincibleTimer = 99999; p.facing = 1; [90, 150, 210, 265].forEach((dx) => { D.spawnRole('WOLF', p.x + dx, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }); });
  await page.waitForTimeout(300);
  const b0 = await by(page);
  const bowl0 = await ev(page, () => window.__RELIC.bowlLaunches || 0);
  await keyTap(page, 'j', 9, 200);
  await page.waitForTimeout(600);
  const b1 = await by(page);
  const bowl1 = await ev(page, () => window.__RELIC.bowlLaunches || 0);
  const d = (k) => (b1[k] || 0) - (b0[k] || 0);
  ok('S2 연격 1 · 2타 = slash_light · 3 · 4타(+볼링 충돌) = hit_heavy · 피니시 = breath_finisher', d('slashLight') > 0 && d('hitHeavy') > 0 && d('breath') > 0 && bowl1 > bowl0, { slashLight: d('slashLight'), hitHeavy: d('hitHeavy'), breath: d('breath'), bowling: bowl1 - bowl0 });
  // 어퍼(L) · 돌진(K)도 호흡 피니시음
  await ev(page, () => { const p = window.__RELIC.player; p.cdUpper = 0; p.cdDash = 0; p.attackTimer = 0; });
  await page.keyboard.press('l');
  await page.waitForTimeout(900);
  await ev(page, () => { const p = window.__RELIC.player; p.cdDash = 0; p.attackTimer = 0; });
  await page.keyboard.press('k');
  await page.waitForTimeout(700);
  const b2 = await by(page);
  ok('S3 어퍼 · 돌진 = breath_finisher', (b2.breath || 0) - (b1.breath || 0) >= 2, { breath: (b2.breath || 0) - (b1.breath || 0) });
  // 저스트 패링 → 카운터 일섬
  await page.waitForTimeout(600);
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; p.attackTimer = 0; p.guardCd = 0; p.flinch = 0; p.pendingHit = null; p.y = 0; p.vy = 0; D.spawnRole('WOLF', p.x + 240, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; });
  await page.waitForTimeout(400);
  await ev(page, () => { window.__RELIC.player.invincibleTimer = 0; });
  await page.keyboard.press('e');
  await ev(page, () => { const g = window.__RELIC, p = g.player; (g.mobShots || (g.mobShots = [])).push({ x: p.x + p.facing * 36, z: p.z, y: 54, vx: -p.facing * 12, vz: 0, life: 20, dmg: 60, kind: 'arrow', label: 'TEST', src: 'TEST' }); });
  await page.waitForTimeout(900);
  const b3 = await by(page);
  ok('S4 저스트 패링 카운터 일섬 = parry_counter', (b3.parryCounter || 0) > (b2.parryCounter || 0), { parryCounter: b3.parryCounter || 0 });
  await ev(page, () => { window.__RELIC.player.invincibleTimer = 99999; });
  // 퀴즈 보상 유물 각성
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(0));
  await page.waitForTimeout(1000);
  await page.getByRole('button', { name: /주먹도끼·찍개 등 뗀석기/ }).click();
  await page.waitForTimeout(900);
  const b4 = await by(page);
  ok('S5 퀴즈 보상 유물 각성 빛기둥 = relic_awaken', (b4.relicAwaken || 0) > (b3.relicAwaken || 0), { relicAwaken: b4.relicAwaken || 0 });
  await page.waitForTimeout(2600);
  // 구역 막타 킬캠
  const kc = await ev(page, () => new Promise((res) => { const g = window.__RELIC; const k0 = g.killCams || 0; g.zoneState = 'LOCKED'; g.waves = []; g.waveSpawnCd = 0; g.bossActive = false; g.enemies.forEach((e) => { e.hp = 0; }); if (!g.enemies.length) { const D = window.__RELIC_DEV, p = g.player; D.spawnRole('WOLF', p.x + 200, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = 0; } setTimeout(() => res({ cams: (g.killCams || 0) - k0 }), 700); }));
  const b5 = await by(page);
  ok('S6 구역 막타 킬캠 = killcam_slowmo', kc.cams === 1 && (b5.killcam || 0) > (b4.killcam || 0), { cams: kc.cams, killcam: b5.killcam || 0 });

  // ── 3시대 김유신 질주 프레임 수(정보) ──
  await toEra(page, 3);
  await page.waitForTimeout(800);
  const kim = await ev(page, () => { const g = window.__RELIC, H = window.__RELIC_DEV.assets.debug.eras['3@' + (g.quality.dpr || 1)].data.hero; return H.runs.length; });
  console.log('INFO K1 김유신 질주 프레임', kim, '(run3~8 원화 미수령)');

  // ── 4 · 5 · 6시대 일반 몹 6종: 유닛 키 매핑 · 톤다운 생략 ──
  const res = {};
  await toEra(page, 4);
  await page.waitForTimeout(800);
  res[4] = await artOf(page, ['KHITAN_INF', 'MONGOL_RIDER']);
  const khTone = await toneOf(page, 4, 'khitan_inf', 'assets/mob/era4_khitan_inf_idle.png');
  await toEra(page, 5);
  await page.waitForTimeout(800);
  res[5] = await artOf(page, ['JP_GUNNER', 'SAMURAI']);
  await toEra(page, 6);
  await page.waitForTimeout(800);
  res[6] = await artOf(page, ['JP_BAYONET', 'MG_NEST']);
  const want = { KHITAN_INF: 'khitan_inf', MONGOL_RIDER: 'mongol_cav', JP_GUNNER: 'gunner', SAMURAI: 'samurai', JP_BAYONET: 'jp_bayonet', MG_NEST: 'mg_nest' };
  const pairs = [].concat(res[4], res[5], res[6]);
  const fails = await ev(page, () => window.__RELIC_DEV.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)));
  ok('M1 4~6시대 일반 몹 6종 = 원화(MONGOL_RIDER→mongol_cav · JP_GUNNER→gunner 포함) · 로드 실패 0', pairs.length === 6 && pairs.every(([u, a]) => want[u] === a) && fails.length === 0, { pairs, fails: fails.length });
  ok('M2 원본 톤다운 몹은 굽기 톤다운 생략(거란 보병 ≈ 1.0) · 기존 몹은 그대로(늑대 ≈ 0.88)', khTone > 0.97 && khTone < 1.03 && wolfTone > 0.84 && wolfTone < 0.92, { khitan_inf: khTone, wolf: wolfTone });
  // 보스 적중 = 강타
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneIdx = 3; g.zoneState = 'ROAM'; p.x = 5714; p.vx = 0; p.y = 0; p.vy = 0; g.cameraX = 5440; });
  await page.waitForFunction(() => window.__RELIC.bossActive && window.__RELIC.boss, null, { timeout: 12000 });
  await page.waitForTimeout(3200);
  const bh0 = (await by(page)).hitHeavy || 0;
  const hb = await ev(page, () => { const g = window.__RELIC; g.sfxHitGate = 0; g.boss.phaseInv = 0; return window.__RELIC_DEV.hitBoss(); });
  const bh1 = (await by(page)).hitHeavy || 0;
  ok('S7 보스 적중 = hit_heavy', hb > 0 && bh1 > bh0, { dmg: hb, hitHeavy: bh1 - bh0 });

  // ── ?sfx=synth: 샘플 안 받고 합성음 ──
  const { browser: b2b, page: q, errors: e2 } = await open(URL + '?sfx=synth', { w: 960, h: 540, dsf: 1 });
  await start(q);
  await q.waitForTimeout(800);
  const sy = await q.evaluate(() => window.__RELIC_DEV.sfxStats());
  ok('C1 ?sfx=synth = 샘플 끔(합성음 폴백)', sy && sy.off && sy.loaded === 0, { off: sy && sy.off, loaded: sy && sy.loaded });
  await b2b.close();
  ok('Z 콘솔 에러 0', errors.length === 0 && e2.length === 0, errors.concat(e2).slice(0, 6));
  console.log(`R27 2차 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
