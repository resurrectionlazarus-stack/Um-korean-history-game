// R26 수정 항목 기능 테스트 1회(콘솔 에러 0) — 리페인트 원화 로드 · 손 위치 리그 · 새 무기 변환 · 난이도 완화 토글
const { open, start, toEra } = require('./h');
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const keyTap = async (page, k, n = 1, gap = 170) => { for (let i = 0; i < n; i++) { await page.keyboard.press(k); await page.waitForTimeout(gap); } };
const sample = (page, ms, fn) => ev(page, ({ ms, fn }) => new Promise((res) => {
  const f = new Function('g', fn); const out = []; const t0 = performance.now();
  const L = () => { out.push(f(window.__RELIC)); if (performance.now() - t0 < ms) requestAnimationFrame(L); else res(out); };
  requestAnimationFrame(L);
}), { ms, fn });
const heroOf = (page, era) => ev(page, (era) => {
  const g = window.__RELIC, E = window.__RELIC_DEV.assets.debug.eras[era + '@' + (g.quality.dpr || 1)], d = E && E.data, H = d && d.hero;
  return { frames: H ? Object.keys(H.frames).length : 0, weapons: H && H.weapons ? Object.values(H.weapons).map((w) => w.w) : [], L: H && H.weapon ? Object.values(H.weapon.sprites).map((s) => s.L) : [],
    rigIdle: H && H.weapon ? H.weapon.frames.idle : null, boss: d && d.boss && d.boss.kind, comp: d && d.comp ? [d.comp.name, d.comp.anchorX] : null,
    fails: window.__RELIC_DEV.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)) };
}, era);
(async () => {
  const URL = 'http://127.0.0.1:8026/index.html';
  const { browser, page, errors } = await open(URL, { w: 1280, h: 720, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  const prep = () => ev(page, () => { const g = window.__RELIC, p = g.player; p.invincibleTimer = 99999; g.enemies.forEach((e) => { e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }); });
  await page.waitForTimeout(800);
  const f1 = await ev(page, () => { const g = window.__RELIC, s = g._assetSeen || {}; return Object.keys(s).filter((k) => k.startsWith('fairy:') && g.tick - s[k] < 30); });
  ok('A1 리페인트 선녀 단비 표시(1시대)', f1.length >= 1, f1);

  // ── 2시대: 해모수 리페인트 + 새 무기 3등급 + 한 무제 ──
  await toEra(page, 2);
  await page.waitForTimeout(1500);
  await prep();
  const h2 = await heroOf(page, 2);
  ok('B1 해모수 몸 22장 · 새 무기 폭 320/345/375 · 칼 길이 210/235/265 · 해모수 전용 손 위치 · 한 무제 · 선녀(중심 127) · 로드 실패 0',
    h2.frames === 22 && h2.weapons.join() === '320,345,375' && h2.L.join() === '210,235,265' && h2.rigIdle && h2.rigIdle[0] === 345 && h2.boss === 'hanwu' && h2.comp && h2.comp[1] === 127 && h2.fails.length === 0, h2);
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2500);
  await prep();
  const smp = sample(page, 2800, 'const p = g.player; return [g._assetMode && g._assetMode.hero, p._wDrawnTier || 0, p._wt ? p._wt.length : 0];');
  await keyTap(page, 'j', 13, 185);
  const s2 = await smp;
  const poses = [...new Set(s2.map((x) => x[0]).filter((n) => /^atk/.test(n || '')))];
  ok('B2 연격 동작 사슬 12장 + 손에 든 T1 + 칼끝 궤적', poses.length >= 12 && s2.some((x) => x[1] === 1) && Math.max(...s2.map((x) => x[2])) >= 6, { poses: poses.length });
  await page.waitForTimeout(600);
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(0));
  await page.waitForTimeout(1000);
  await page.getByRole('button', { name: /세형 동검\(한국식 동검\)/ }).click();
  await page.waitForFunction(() => window.__RELIC.weaponFx && document.querySelector('[data-testid="relic-swap"]'), null, { timeout: 6000 });
  await page.waitForTimeout(900);
  const sw = await ev(page, () => ({ drawn: window.__RELIC.player._wDrawnTier, swap: document.querySelector('[data-testid="relic-swap"]').textContent, icons: [...document.querySelectorAll('[data-testid="relic-banner"] img')].map((i) => i.complete && i.naturalWidth) }));
  ok('B3 새 무기로 변환(T1 → T2) + 배너 아이콘 2장(옛 · 새) 256', sw.drawn === 2 && /해모수의 용광검 → 세형 동검의 용광검/.test(sw.swap) && sw.icons.length === 2 && sw.icons.every((w) => w === 256), sw);
  await page.waitForTimeout(2600);

  // ── 난이도 완화 토글(DEV 패널) ──
  const std = await ev(page, () => window.__RELIC_DEV.bossHpBase(2));
  await page.keyboard.press('`');
  await page.waitForTimeout(300);
  await page.locator('[data-testid="btn-diff"]').click();
  await page.waitForTimeout(200);
  const lite = await ev(page, () => ({ hp: window.__RELIC_DEV.bossHpBase(2), label: document.querySelector('[data-testid="btn-diff"]').textContent }));
  await page.locator('[data-testid="btn-diff"]').click();
  await page.waitForTimeout(200);
  const back = await ev(page, () => ({ hp: window.__RELIC_DEV.bossHpBase(2), label: document.querySelector('[data-testid="btn-diff"]').textContent }));
  await page.keyboard.press('`');
  ok('C1 DEV 난이도 버튼: 완화 = 2시대 보스 체력 × 0.9/1.06 · 다시 누르면 표준', Math.abs(lite.hp / std - 0.9 / 1.06) < 0.005 && /완화/.test(lite.label) && back.hp === std && /표준/.test(back.label), { std, lite, back });

  // ── 한 무제(리페인트) 보스전 ──
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneIdx = 3; g.zoneState = 'ROAM'; p.x = 5690 + 24; p.vx = 0; p.y = 0; p.vy = 0; g.cameraX = 5440; });
  await page.waitForFunction(() => window.__RELIC.bossActive && window.__RELIC.boss, null, { timeout: 10000 });
  await page.waitForTimeout(2400);
  const hw = await ev(page, () => { const g = window.__RELIC, s = g._assetSeen || {}; return Object.keys(s).filter((k) => k.startsWith('hanwu:')); });
  ok('D1 리페인트 한 무제 HD 원화로 보스전', hw.length >= 1, hw);

  // ── 4시대: 척준경 리페인트 ──
  await toEra(page, 4);
  await page.waitForTimeout(1500);
  await prep();
  const h4 = await heroOf(page, 4);
  ok('E1 척준경 몸 22장 · 새 무기 폭 330/355/385 · 칼 길이 220/245/275 · 척준경 전용 손 위치', h4.frames === 22 && h4.weapons.join() === '330,355,385' && h4.L.join() === '220,245,275' && h4.rigIdle && h4.rigIdle[0] === 350 && h4.fails.length === 0, h4);
  await keyTap(page, 'j', 4, 190);
  await page.waitForTimeout(500);

  // ── ?diff=lite 로 처음부터 완화 ──
  const { browser: b3, page: q, errors: e3 } = await open(URL + '?diff=lite', { w: 960, h: 540, dsf: 1 });
  const ql = await q.evaluate(() => window.__RELIC_DEV.bossHpBase(2));
  ok('C2 ?diff=lite 로 열면 처음부터 완화(2시대 보스 0.9)', Math.abs(ql / std - 0.9 / 1.06) < 0.005, { ql, std });
  await b3.close();
  ok('Z 콘솔 에러 0', errors.length === 0 && e3.length === 0, errors.concat(e3).slice(0, 6));
  console.log(`R26 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
