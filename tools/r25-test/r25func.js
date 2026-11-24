// R25 수정 항목 기능 테스트 1회(콘솔 에러 0) — 결과 캡처는 비교 합성용 원본(dsf 2)
//  A 선녀 단비 · B 해모수 HD + 용광검 3등급 + 한 무제 · C 걸음 8프레임 · 3단/4타 동작 사슬 · 칼끝 궤적 ·
//  D 입력 보호 + 무기 변환 연출 · E 난이도 곡선 · F 한 무제 패턴 · G 보스 격파 숨 고르기 + 전설 시험(기본 라벨 · 입력 보호) · H 척준경 검
const { open, start, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const SHOT = path.join(__dirname, '..', 'shots25');
fs.mkdirSync(SHOT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const keyTap = async (page, k, n = 1, gap = 170) => { for (let i = 0; i < n; i++) { await page.keyboard.press(k); await page.waitForTimeout(gap); } };
const shot = async (page, name) => fs.writeFileSync(path.join(SHOT, name), await page.screenshot());
const sample = (page, ms, fn) => ev(page, ({ ms, fn }) => new Promise((res) => {
  const f = new Function('g', fn); const out = []; const t0 = performance.now();
  const L = () => { out.push(f(window.__RELIC)); if (performance.now() - t0 < ms) requestAnimationFrame(L); else res(out); };
  requestAnimationFrame(L);
}), { ms, fn });
(async () => {
  const { browser, page, errors } = await open('http://127.0.0.1:8025/index.html', { w: 1280, h: 720, dsf: 2 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  const hd = () => ev(page, () => { const q = window.__RELIC.quality; q.forced = true; q.tier = 0; });
  const prep = () => ev(page, () => {
    const g = window.__RELIC, p = g.player; p.invincibleTimer = 99999;
    g.enemies.forEach((e) => { e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; });
  });
  await hd();
  await page.waitForTimeout(900);

  // ── A. 동료 = 꼬마 선녀 단비 ──
  const a1 = await ev(page, () => { const g = window.__RELIC, s = g._assetSeen || {}; const k = Object.keys(s).filter((x) => x.startsWith('fairy:')); return { keys: k, fresh: k.some((x) => g.tick - s[x] < 20), title: (window.__RELIC_DATA.eras || []).map((e) => e.companionTitle) }; });
  ok('A1 1~6시대 동료 = 꼬마 선녀 단비 · 1시대 HD 원화로 떠서 따라옴', a1.fresh && a1.title.every((t) => t === '꼬마 선녀 단비'), a1);

  // ── B. 2시대: 해모수 HD + 용광검 3등급 + 한 무제 + 위만 ──
  await toEra(page, 2);
  await page.waitForTimeout(1500);
  await hd();
  await prep();
  const b1 = await ev(page, () => {
    const g = window.__RELIC, E = window.__RELIC_DEV.assets.debug.eras['2@' + (g.quality.dpr || 1)], d = E && E.data;
    const H = d && d.hero;
    return { frames: H ? Object.keys(H.frames).length : 0, runs: H ? H.runs.length : 0, tiers: H && H.weapons ? Object.keys(H.weapons) : [], names: H && H.weapon ? Object.values(H.weapon.sprites).map((w) => w.name) : [], boss: d && d.boss && d.boss.kind, comp: d && d.comp && d.comp.name, eraName: window.__RELIC_DATA.eras[1].heroTitle, boss2: window.__RELIC_DATA.eras[1].bossName, mid: window.__RELIC_DATA.mids[2].name };
  });
  ok('B1 2시대 주인공 해모수(몸 22장 · 8프레임 질주) + 손에 든 용광검 3등급 + 보스 한 무제 + 중간보스 위만', b1.frames === 22 && b1.runs === 8 && b1.tiers.join() === '1,2,3' && b1.boss === 'hanwu' && b1.comp === 'fairy' && b1.eraName === '천제의 아들 해모수' && b1.boss2 === '한 무제' && b1.mid === '위만', b1);

  // ── C. 걸음 · 3단 · 4타 피니시 · 칼끝 궤적 ──
  await page.keyboard.down('ArrowRight');
  const walk = await sample(page, 1600, 'return g._assetMode && g._assetMode.hero;');
  await page.keyboard.up('ArrowRight');
  const runSet = [...new Set(walk.filter((n) => /^run/.test(n || '')))];
  ok('C1 해모수 걸음: 8프레임 질주(run~run8) 전부 사용', runSet.length === 8, runSet.sort());
  await page.waitForTimeout(400);
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2600);
  await prep();
  const smp = sample(page, 3000, 'const p = g.player; return [g._assetMode && g._assetMode.hero, p.comboStep, p._wt ? p._wt.length : 0, !!p._fin, p._wDrawnTier || 0];');
  await keyTap(page, 'j', 14, 185);
  const s3 = await smp;
  const poses = [...new Set(s3.map((x) => x[0]).filter((n) => /^atk/.test(n || '')))].sort();
  const need = ['atk_prep', 'atk1', 'atk1_2', 'atk1_3', 'atk2_prep', 'atk2', 'atk2_2', 'atk2_3', 'atk3_prep', 'atk3', 'atk3_2', 'atk3_3'];
  ok('C2 연격 동작 사슬: 내려베기(1) · 올려베기(2) · 두손 피니시(4타) — 예비 · 3장 · 마무리 전부', need.every((n) => poses.includes(n)), poses);
  const trailMax = Math.max(...s3.map((x) => x[2]));
  ok('C3 칼끝 HD 궤적(실제 칼끝 · 동작 사이 보간) + 손에 든 무기 T1', trailMax >= 6 && s3.some((x) => x[4] === 1), { trailMax });
  await page.waitForTimeout(500);
  await prep();
  await keyTap(page, 'j', 1, 130);
  await shot(page, 'r25_haemosu_slash.png');
  await page.waitForTimeout(700);

  // ── D. 문제 입력 보호 + 무기 변환 연출(손에 든 무기 · 배너 '이전 → 새 무기') ──
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(0));
  await page.getByRole('button', { name: /세형 동검\(한국식 동검\)/ }).click({ timeout: 1500 });
  await page.waitForTimeout(120);
  const d0 = await ev(page, () => ({ tier: window.__RELIC.stats.weaponTier, quiz: !!document.querySelector('.fixed.inset-0.z-50') }));
  ok('D1 문제 입력 보호: 뜬 직후 0.9초 안의 클릭은 무시', d0.tier === 1 && d0.quiz, d0);
  await page.waitForTimeout(950);
  await page.getByRole('button', { name: /세형 동검\(한국식 동검\)/ }).click();
  try {
    await page.waitForFunction(() => window.__RELIC.weaponFx && document.querySelector('[data-testid="relic-swap"]'), null, { timeout: 5000 });
  } catch (e) {
    console.log('D-DIAG', JSON.stringify(await ev(page, () => ({ tier: window.__RELIC.stats.weaponTier, fx: window.__RELIC.weaponFx || null, quiz: !!document.querySelector('.fixed.inset-0.z-50'), done: window.__RELIC.midQuizDone, txt: document.body.innerText.slice(0, 300) }))), JSON.stringify(errors.slice(0, 6)));
    throw e;
  }
  await page.waitForTimeout(140);
  const d1 = await ev(page, () => ({ fx: window.__RELIC.weaponFx && [window.__RELIC.weaponFx.from, window.__RELIC.weaponFx.to], drawn: window.__RELIC.player._wDrawnTier, swap: document.querySelector('[data-testid="relic-swap"]').textContent, old: (document.querySelector('[data-testid="relic-old"]') || {}).src || '' }));
  await shot(page, 'r25_swap_1_old.png');
  await page.waitForTimeout(650);
  const d2 = await ev(page, () => ({ drawn: window.__RELIC.player._wDrawnTier, tier: window.__RELIC.stats.weaponTier, relic: window.__RELIC.stats.relicId }));
  await shot(page, 'r25_swap_2_new.png');
  ok('D2 정답 → 손에 든 무기 교체(옛 무기 흰빛 점멸 → 새 무기) + 배너 "무기 변환 · 해모수의 용광검 → 세형 동검의 용광검"', d1.fx && d1.fx.join() === '1,2' && d1.drawn === 1 && d2.drawn === 2 && d2.tier === 2 && /해모수의 용광검 → 세형 동검의 용광검/.test(d1.swap) && /relic\/base_era2\.png$/.test(d1.old), { d1, d2 });
  await page.waitForTimeout(2600);
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(1));
  await page.waitForTimeout(1000);
  await page.getByRole('button', { name: /철제 무기와 명도전|명도전/ }).first().click();
  await page.waitForFunction(() => window.__RELIC.stats.weaponTier === 3 && document.querySelector('[data-testid="relic-swap"]'), null, { timeout: 5000 });
  const d3 = await ev(page, () => ({ swap: document.querySelector('[data-testid="relic-swap"]').textContent, old: (document.querySelector('[data-testid="relic-old"]') || {}).src || '' }));
  await page.waitForTimeout(700);
  const d4 = await ev(page, () => ({ drawn: window.__RELIC.player._wDrawnTier, chip: (document.querySelector('[data-testid="hud-relic"]') || {}).src || '' }));
  ok('D3 2차 정답 → 고조선 철제 용광검(TI.3) · 배너 옛 아이콘 = 세형 동검 · HUD 칩', /세형 동검의 용광검 → 고조선 철제 용광검/.test(d3.swap) && /era2_slender_dagger\.png$/.test(d3.old) && d4.drawn === 3 && /era2_iron_sword\.png$/.test(d4.chip), { d3, d4 });
  await page.waitForTimeout(2200);

  // ── E. 난이도 곡선(체감 TTK = 체력 ÷ (전투력 × 각성 배율)) ──
  const e1 = await ev(page, () => {
    const D = window.__RELIC_DEV, RD = window.__RELIC_DATA, g = window.__RELIC;
    const boss = {}; for (let e = 2; e <= 6; e++) boss[e] = Math.round(D.bossHpBase(e) / RD.powerRef);
    const p = g.player; g.stats.awakenedTier = 1.45;
    D.spawnUnit('GOJO_PIKE', p.x + 300, p.z); const u = g.enemies[g.enemies.length - 1];
    const pf = D.powerFactor(2);
    const unitK = u.maxHp / ((900 + 2 * 700) * 1 * pf);
    u.hp = 0;
    return { boss, era1Boss: Math.round(RD.r25Diff.ttk.boss), unitK: +unitK.toFixed(3), wantUnitK: +(RD.r25Diff.ttk.mob * RD.r25Diff.curve.mob[2] * RD.powerRef / ((900 + 2 * 700) * RD.r25Diff.unitAvg[2])).toFixed(3), pf: +pf.toFixed(3) };
  });
  const bs = Object.values(e1.boss);
  ok('E1 2~6시대 보스 체감 TTK ≥ 1시대 매머드(447) · 시대마다 증가(4시대 장기전) · 일반 몹 hpK 역산 · 각성 배율 반영', bs.every((v) => v >= e1.era1Boss) && bs[1] > bs[0] && bs[3] > bs[1] && Math.abs(e1.unitK - e1.wantUnitK) < 0.02 && e1.pf > 1.3, e1);

  // ── F. 한 무제(쇠뇌 부채꼴 · 황제의 일섬 · 투석 포격 · 일격) ──
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneIdx = 3; g.zoneState = 'ROAM'; p.x = 5690 + 24; p.vx = 0; p.y = 0; p.vy = 0; g.cameraX = 5440; });
  await page.waitForFunction(() => window.__RELIC.bossActive && window.__RELIC.boss, null, { timeout: 10000 });
  await page.waitForTimeout(2200);
  await ev(page, () => { const g = window.__RELIC; g.player.invincibleTimer = 99999; g.boss.hp = g.boss.maxHp; });
  const bossSmp = sample(page, 9000, 'const b = g.boss; return b ? [b.lastPat || null, b._assetFrame || null] : [null, null];');
  await page.waitForTimeout(2600);
  await ev(page, () => { const g = window.__RELIC, p = g.player, b = g.boss; p.x = b.x - 170; p.z = b.z; p.facing = 1; });
  await shot(page, 'r25_era2_boss.png');
  const bsm = await bossSmp;
  const pats = [...new Set(bsm.map((x) => x[0]).filter(Boolean))];
  const bposes = [...new Set(bsm.map((x) => x[1]).filter(Boolean))];
  ok('F1 한 무제 HD 원화 + 패턴(쇠뇌 부채꼴 · 일섬 · 투석 포격) · 지휘/베기 자세', pats.includes('arrowfan') && pats.includes('slash') && pats.includes('bombard') && bposes.includes('command') && bposes.includes('slash'), { pats, bposes });

  // ── G. 보스 격파 숨 고르기(약 2초) + 전설 시험(기본 라벨 · 입력 보호) ──
  await ev(page, () => { const g = window.__RELIC; g.boss.hp = 1; g.bossTele && (g.bossTele.length = 0); });
  await ev(page, () => window.__RELIC_DEV.hitBoss());
  const tKill = Date.now();
  await page.waitForTimeout(400);
  const g0 = await ev(page, () => ({ trial: !!document.querySelector('[data-testid="legend-trial"]'), qt: window.__RELIC.boss && window.__RELIC.boss.quizTriggered, inv: window.__RELIC.player.invincibleTimer, popup: (window.__RELIC.damagePopups || []).some((d) => /STAGE CLEAR/.test(String(d.text))) }));
  await page.waitForSelector('[data-testid="legend-trial"]', { timeout: 6000 });
  const delay = Date.now() - tKill;
  await page.locator('[data-testid="legend-trial"] button').filter({ hasText: /^[①②③④]/ }).first().click({ timeout: 1500 });
  await page.waitForTimeout(80);
  const lt1 = await ev(page, () => ({ res: window.__RELIC_DEV.legend.current.results.length, phase: window.__RELIC_DEV.legend.current.phase }));
  const lt0 = await ev(page, () => ({ head: document.querySelector('[data-testid="legend-trial"]').textContent.slice(0, 160), res: window.__RELIC_DEV.legend.current.results.length }));
  await shot(page, 'r25_legend_basic.png');
  ok('G1 격파 순간 시험 안 뜸 → 약 2초 STAGE CLEAR(무적) 뒤 시험', !g0.trial && g0.qt && g0.inv > 100 && g0.popup && delay >= 1700 && delay < 4500, { ...g0, delayMs: delay });
  ok('G2 전설 시험 라벨 "한국사 기본 3문항" + 뜬 직후 클릭 무시(입력 보호)', /한국사 기본 3문항/.test(lt0.head) && !/고난도/.test(lt0.head) && lt1.res === 0 && lt1.phase === 'ask', { lt0, lt1 });
  await page.waitForTimeout(950);
  for (let k = 0; k < 3; k++) {
    const q = await ev(page, () => { const L = window.__RELIC_DEV.legend.current; const q = L.qs[L.idx]; return { a: q.opts[q.a], idx: L.idx }; });
    const esc = q.a.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    await page.locator('[data-testid="legend-trial"] button').filter({ hasText: new RegExp('^[①②③④]' + esc + '$') }).first().click();
    await page.waitForTimeout(k < 2 ? 1300 : 1100);
  }
  const lt2 = await ev(page, () => ({ phase: window.__RELIC_DEV.legend.current && window.__RELIC_DEV.legend.current.phase, res: window.__RELIC_DEV.legend.current && window.__RELIC_DEV.legend.current.results }));
  ok('G3 기본 3문항 정답 → 통과(다음 문제도 0.42초 보호 뒤 정상 입력)', lt2.phase === 'pass' && lt2.res.length === 3, lt2);
  await page.waitForTimeout(2500);

  // ── H. 4시대 척준경 = 소드 마스터(장검 · 사격 없음 · 3타 검기) ──
  await toEra(page, 4);
  await page.waitForTimeout(1500);
  await hd();
  await prep();
  const h1 = await ev(page, () => {
    const g = window.__RELIC, E = window.__RELIC_DEV.assets.debug.eras['4@' + (g.quality.dpr || 1)], H = E && E.data && E.data.hero;
    return { frames: H ? Object.keys(H.frames).length : 0, tiers: H && H.weapons ? Object.keys(H.weapons) : [], names: H && H.weapon ? Object.values(H.weapon.sprites).map((w) => w.name) : [], weaponName: window.__RELIC_DATA.eras[3].weaponName };
  });
  const smp4 = sample(page, 2200, 'const p = g.player; return [p.atkAnim, g.projectiles.filter((x) => x.eraNum === 4).length, g._assetMode && g._assetMode.hero];');
  await keyTap(page, 'j', 3, 200);
  const s4 = await smp4;
  await prep();
  await keyTap(page, 'j', 1, 140);
  await shot(page, 'r25_cjg_sword.png');
  ok('H1 척준경 장검 3등급(결사대 흑철 → 별무반 신기군 → 화통도감 화약) · 화통 사격 없음 · 3타 검기', h1.frames === 22 && h1.tiers.join() === '1,2,3' && h1.names[0] === '결사대 흑철 장검' && h1.weaponName === '결사대 흑철 장검' && !s4.some((x) => x[0] === 'shoot') && s4.some((x) => x[1] > 0), { h1, beams: Math.max(...s4.map((x) => x[1])) });
  await page.waitForTimeout(600);
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(0));
  await page.waitForTimeout(1000);
  await page.getByRole('button', { name: /별무반/ }).first().click();
  await page.waitForFunction(() => window.__RELIC.stats.relicId === 'era4_byeolmuban_sword' && document.querySelector('[data-testid="relic-swap"]'), null, { timeout: 5000 });
  const h2 = await ev(page, () => ({ swap: document.querySelector('[data-testid="relic-swap"]').textContent, img: (() => { const i = document.querySelector('[data-testid="relic-banner"] img.r25-new'); return i ? i.complete && i.naturalWidth : -1; })() }));
  ok('H2 4시대 유물 = 별무반 신기군 장검(아이콘 256) · "결사대 흑철 장검 → 별무반 신기군 장검"', /결사대 흑철 장검 → 별무반 신기군 장검/.test(h2.swap) && h2.img === 256, h2);
  await page.waitForTimeout(1500);
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 6));
  const pass = Object.values(R).filter(Boolean).length;
  console.log(`R25 FUNC ${pass}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
