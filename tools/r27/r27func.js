// R27 수정 항목 기능 테스트 1회(콘솔 에러 0) — 1시대 무기 분리 리그 · 손에 든 무기 3단 교체 · 영웅 링 · 몹 톤다운 · 잡몹 체력 ·
//  수묵 호흡 피니시 · 패링 카운터 일섬 · 킬캠 · 공중 체공 · 볼링 · 보행 리듬 · 3시대 전경 끄기 · 퀴즈 2건
const { open, start, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const keyTap = async (page, k, n = 1, gap = 170) => { for (let i = 0; i < n; i++) { await page.keyboard.press(k); await page.waitForTimeout(gap); } };
const sample = (page, ms, fn) => ev(page, ({ ms, fn }) => new Promise((res) => {
  const f = new Function('g', fn); const out = []; const t0 = performance.now();
  const L = () => { out.push(f(window.__RELIC)); if (performance.now() - t0 < ms) requestAnimationFrame(L); else res(out); };
  requestAnimationFrame(L);
}), { ms, fn });
const OUT = path.join(__dirname, '..', 'cap27');
fs.mkdirSync(OUT, { recursive: true });
const heroOf = (page, era) => ev(page, (era) => {
  const g = window.__RELIC, E = window.__RELIC_DEV.assets.debug.eras[era + '@' + (g.quality.dpr || 1)], d = E && E.data, H = d && d.hero;
  return { frames: H ? Object.keys(H.frames).length : 0, runs: H ? H.runs.length : 0, weapons: H && H.weapons ? Object.values(H.weapons).map((w) => w.w) : [],
    L: H && H.weapon ? Object.values(H.weapon.sprites).map((s) => s.L) : [], rigIdle: H && H.weapon ? H.weapon.frames.idle : null,
    fails: window.__RELIC_DEV.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)) };
}, era);
(async () => {
  const URL = 'http://127.0.0.1:8027/index.html';
  const { browser, page, errors } = await open(URL, { w: 1280, h: 720, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  const prep = () => ev(page, () => { const g = window.__RELIC, p = g.player; p.invincibleTimer = 99999; g.enemies.forEach((e) => { e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }); });
  await page.waitForTimeout(800);
  await prep();

  // ── A. 1시대 대사냥꾼: 무기 분리 몸 22장 + 손에 든 무기 3등급 ──
  const h1 = await heroOf(page, 1);
  ok('A1 대사냥꾼 몸 22장(webp) · 질주 8장 · 무기 폭 295/335/344 · 날 길이 185/225/234 · 사냥꾼 전용 손 위치 · 로드 실패 0',
    h1.frames === 22 && h1.runs === 8 && h1.weapons.join() === '295,335,344' && h1.L.join() === '185,225,234' && h1.rigIdle && h1.rigIdle[0] === 456 && h1.fails.length === 0, h1);
  const ring = await ev(page, () => { const g = window.__RELIC; return { ring: g.ringTick, rt: g.rtick }; });
  ok('B1 주인공 발밑 영웅 링(1시대 주황) 매 프레임 그림', ring.ring != null && ring.rt - ring.ring <= 3, ring);
  // 일반 몹 원화 굽기 톤다운 12%: 구운 idle의 불투명 픽셀 평균 밝기 ÷ 원본 평균
  const tone = await ev(page, async () => {
    const g = window.__RELIC, d = window.__RELIC_DEV.assets.debug.eras['1@' + (g.quality.dpr || 1)].data;
    const fc = d.mobs && d.mobs.wolf && d.mobs.wolf.frames.idle;
    if (!fc) return null;
    const meanOf = (src, w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.drawImage(src, 0, 0, w, h); const D = x.getImageData(0, 0, w, h).data; let s = 0, n = 0; for (let i = 0; i < D.length; i += 4) if (D[i + 3] > 220) { s += D[i] + D[i + 1] + D[i + 2]; n++; } return s / Math.max(1, n) / 3; };
    const img = new Image(); img.src = 'assets/mob/era1_wolf_idle.png'; await img.decode();
    const a = meanOf(fc, fc.width, fc.height), b = meanOf(img, img.naturalWidth, img.naturalHeight);
    return { baked: +a.toFixed(1), src: +b.toFixed(1), ratio: +(a / b).toFixed(3) };
  });
  ok('B2 일반 몹 원화 굽기 톤다운(밝기 약 88%)', tone && tone.ratio > 0.84 && tone.ratio < 0.92, tone);

  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2500);
  await prep();
  const b0 = await ev(page, () => window.__RELIC.breathCount || 0);
  const smp = sample(page, 2800, 'const p = g.player; const L = g.breathFx || []; return [g._assetMode && g._assetMode.hero, p._wDrawnTier || 0, p._wt ? p._wt.length : 0, L.filter((e) => e.k === "ink").length];');
  await keyTap(page, 'j', 13, 185);
  const s1 = await smp;
  const b1 = await ev(page, () => window.__RELIC.breathCount || 0);
  const poses = [...new Set(s1.map((x) => x[0]).filter((n) => /^atk/.test(n || '')))];
  ok('A2 1시대 연격 동작 사슬 12장 + 손에 든 T1 주먹도끼 + 날끝 궤적', poses.length >= 12 && s1.some((x) => x[1] === 1) && Math.max(...s1.map((x) => x[2])) >= 6, { poses: poses.length });
  ok('C1 3 · 4타 피니시 수묵 호흡(먹물 붓터치 비산)', b1 - b0 >= 2 && Math.max(...s1.map((x) => x[3])) >= 6, { breaths: b1 - b0, inkMax: Math.max(...s1.map((x) => x[3])) });
  await page.waitForTimeout(600);
  // 무기 교체: 정답 → 주먹도끼가 부서지고 흑요석 슴베찌르개 → 다음 정답에 신석기 간돌도끼
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(0));
  await page.waitForTimeout(1000);
  await page.getByRole('button', { name: /주먹도끼·찍개 등 뗀석기/ }).click();
  await page.waitForFunction(() => window.__RELIC.weaponFx && document.querySelector('[data-testid="relic-swap"]'), null, { timeout: 6000 });
  await page.waitForTimeout(900);
  const sw1 = await ev(page, () => ({ drawn: window.__RELIC.player._wDrawnTier, tier: window.__RELIC.stats.weaponTier, swap: document.querySelector('[data-testid="relic-swap"]').textContent, icons: [...document.querySelectorAll('[data-testid="relic-banner"] img')].map((i) => i.complete && i.naturalWidth) }));
  ok('A3 정답 → 손에서 주먹도끼 → 흑요석 슴베찌르개(T2) + 배너 아이콘 2장', sw1.drawn === 2 && sw1.tier === 2 && /석장리 타제 주먹도끼 → 흑요석 슴베찌르개/.test(sw1.swap) && sw1.icons.length === 2 && sw1.icons.every((w) => w > 0), sw1);
  await page.waitForTimeout(2600);
  await prep();
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(1));
  await page.waitForTimeout(1000);
  await page.getByRole('button', { name: /빗살무늬토기와 간석기/ }).click();
  await page.waitForFunction(() => window.__RELIC.stats.weaponTier === 3 && document.querySelector('[data-testid="relic-swap"]'), null, { timeout: 6000 });
  await page.waitForTimeout(900);
  const sw2 = await ev(page, () => ({ drawn: window.__RELIC.player._wDrawnTier, swap: document.querySelector('[data-testid="relic-swap"]').textContent }));
  ok('A4 다음 정답 → 흑요석 슴베찌르개 → 신석기 간돌도끼(T3)', sw2.drawn === 3 && /흑요석 슴베찌르개 → 신석기 간돌도끼/.test(sw2.swap), sw2);
  await page.waitForTimeout(2600);

  // ── D. 저스트 패링 → 0.2초 슬로우 + 백열 카운터 일섬 ──
  await prep();
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; p.facing = 1; p.vx = 0; p.vy = 0; p.y = 0; p.attackTimer = 0; p.guardCd = 0; p.flinch = 0; p.pendingHit = null; D.spawnRole('WOLF', p.x + 240, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; window.__pe = e; });
  await page.waitForTimeout(400);
  await ev(page, () => { const g = window.__RELIC, p = g.player; p.invincibleTimer = 0; });
  await page.keyboard.press('e');
  const par = await ev(page, () => new Promise((res) => {
    const g = window.__RELIC, p = g.player, e = window.__pe, hp0 = e.hp;
    (g.mobShots || (g.mobShots = [])).push({ x: p.x + p.facing * 36, z: p.z, y: 54, vx: -p.facing * 12, vz: 0, life: 20, dmg: 60, kind: 'arrow', label: 'TEST', src: 'TEST' });
    let slow = 0, slash = 0; const t0 = performance.now();
    const L = () => { slow = Math.max(slow, g.slowMo || 0); slash = Math.max(slash, (g.breathFx || []).filter((x) => x.k === 'slash').length); if (performance.now() - t0 < 900) requestAnimationFrame(L); else res({ parry: g.parryCount || 0, counter: g.counterSlashes || 0, slow, slash, dmg: hp0 - e.hp, pop: g.damagePopups.some((d) => d.text === 'COUNTER!') }); };
    requestAnimationFrame(L);
  }));
  ok('D1 저스트 패링 → 슬로우(12틱 ≈ 0.2초) + 화면 가로 백열 일섬 + 앞 적 반격', par.parry >= 1 && par.counter >= 1 && par.slow >= 8 && par.slash >= 1 && par.dmg > 0, par);
  await ev(page, () => { window.__RELIC.player.invincibleTimer = 99999; });

  // ── 2시대: 태양 번개 호흡 · 어퍼/돌진 호흡 · 공중 체공 · 볼링 · 킬캠 · 보행 리듬 ──
  await toEra(page, 2);
  await page.waitForTimeout(1500);
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2500);
  await prep();
  const spawnRow = (kind, n, dx0 = 90, gap = 60) => ev(page, ({ kind, n, dx0, gap }) => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; p.facing = 1; p.vx = 0; p.y = 0; p.vy = 0; p.attackTimer = 0; p.comboStep = 0; for (let i = 0; i < n; i++) { D.spawnUnit(kind, p.x + dx0 + i * gap, p.z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; } }, { kind, n, dx0, gap });
  await spawnRow('GOJO_ARCHER', 4, 80, 55);
  await page.waitForTimeout(300);
  const bw0 = await ev(page, () => ({ b: window.__RELIC.bowlLaunches || 0, c: (window.__RELIC.grabLog || {}).chainHits || 0 }));
  const s2 = sample(page, 1800, 'const L = g.breathFx || []; return [L.filter((e) => e.k === "bolt").length, g.damagePopups.some((d) => /STRIKE/.test(String(d.text))) ? 1 : 0];');
  await keyTap(page, 'j', 4, 200);
  const s2r = await s2;
  const bw1 = await ev(page, () => ({ b: window.__RELIC.bowlLaunches || 0, c: (window.__RELIC.grabLog || {}).chainHits || 0 }));
  ok('C2 2시대 피니시 호흡 = 먹물 + 태양 번개', Math.max(...s2r.map((x) => x[0])) >= 1, { boltMax: Math.max(...s2r.map((x) => x[0])) });
  ok('F2 4타 피니시 볼링: 살아남은 적이 날아가 뒤 적과 연쇄 충돌(STRIKE!)', bw1.b > bw0.b && bw1.c > bw0.c && s2r.some((x) => x[1]), { launches: bw1.b - bw0.b, chainHits: bw1.c - bw0.c });
  await page.waitForTimeout(800);
  await spawnRow('GOJO_PIKE', 3, 70, 40);
  await ev(page, () => { const p = window.__RELIC.player; p.cdUpper = 0; p.cdDash = 0; });
  await page.waitForTimeout(250);
  const u0 = await ev(page, () => window.__RELIC.breathCount || 0);
  const s3 = sample(page, 1500, 'return Math.max(0, ...g.enemies.map((e) => e.juggleT || 0));');
  await page.keyboard.press('l');
  await page.waitForTimeout(260);
  await keyTap(page, 'j', 3, 150);
  const s3r = await s3;
  const u1 = await ev(page, () => window.__RELIC.breathCount || 0);
  ok('F1 어퍼 뒤 공중 연타 체공 연장(저글 중 중력 완화)', Math.max(...s3r) >= 20, { juggleMax: Math.max(...s3r) });
  await page.waitForTimeout(700);
  await ev(page, () => { const p = window.__RELIC.player; p.cdDash = 0; p.attackTimer = 0; });
  await page.keyboard.press('k');
  await page.waitForTimeout(700);
  const u2 = await ev(page, () => window.__RELIC.breathCount || 0);
  ok('C3 어퍼(L) · 돌진(K)도 호흡 이펙트', u1 - u0 >= 1 && u2 - u1 >= 1, { upper: u1 - u0, dash: u2 - u1 });
  // 킬캠: 잠긴 구역의 마지막 적을 쓰러뜨리면 0.3초 슬로우 + 짧은 플래시
  const kc = await ev(page, () => new Promise((res) => {
    const g = window.__RELIC; const k0 = g.killCams || 0;
    g.zoneState = 'LOCKED'; g.waves = []; g.waveSpawnCd = 0; g.bossActive = false; (g.midSpawned || (g.midSpawned = {}))[g.zoneIdx] = true; const z0 = g.zoneIdx;
    g.enemies.forEach((e) => { e.hp = 0; });
    let slow = 0, flash = 0; const t0 = performance.now();
    const L = () => { slow = Math.max(slow, g.slowMo || 0); flash = Math.max(flash, g.flashAlpha || 0); if (performance.now() - t0 < 700) requestAnimationFrame(L); else res({ cams: (g.killCams || 0) - k0, slow, flash: +flash.toFixed(2), zone: [z0, g.zoneIdx], state: g.zoneState }); };
    requestAnimationFrame(L);
  }));
  ok('E1 구역 마지막 적 킬캠(슬로우 18틱 ≈ 0.3초 + 플래시) → ZONE CLEAR', kc.cams === 1 && kc.slow >= 12 && kc.flash >= 0.3 && kc.zone[1] === kc.zone[0] + 1, kc);
  await page.waitForTimeout(800);
  // 보행 리듬: 8프레임 질주가 이동 속도에 맞춰 프레임당 3~4틱 + 발 구름 흙먼지
  await ev(page, () => { const g = window.__RELIC; g.enemies.length = 0; });
  await page.keyboard.down('d');
  const wk = await sample(page, 1700, 'const p = g.player; return [g.tick, g._assetMode && g._assetMode.hero, p.steps || 0, p.lastStepDust ? p.lastStepDust.n : 0, Math.hypot(p.mvx || 0, (p.mvz || 0) * 1.6)];');
  await page.keyboard.up('d');
  const runs = wk.filter((x) => /^run/.test(x[1] || '')).slice(12);
  let ch = 0; for (let i = 1; i < runs.length; i++) if (runs[i][1] !== runs[i - 1][1]) ch++;
  const tpf = runs.length > 1 ? (runs[runs.length - 1][0] - runs[0][0]) / Math.max(1, ch) : 0;
  const steps = wk[wk.length - 1][2] - wk[0][2];
  ok('G1 2시대 8프레임 질주 프레임당 3~4틱(속도 연동) + 발 구름 흙먼지', tpf >= 3 && tpf <= 4.1 && steps >= 4 && Math.max(...wk.map((x) => x[3])) >= 2, { ticksPerFrame: +tpf.toFixed(2), steps, speed: +Math.max(...wk.map((x) => x[4])).toFixed(2) });
  const fg2 = await ev(page, () => { const g = window.__RELIC; return { fg: g.fgTick, rt: g.rtick }; });

  // ── 3시대: 옛 도트 전경 실루엣 끄기 ──
  await toEra(page, 3);
  await page.waitForTimeout(1800);
  const fg3 = await ev(page, () => { const g = window.__RELIC; return { fg: g.fgTick, rt: g.rtick, era: g.era }; });
  fs.writeFileSync(path.join(OUT, 'r27_e3_nofg.png'), await page.screenshot());
  ok('H1 3시대 하단 중앙 옛 도트 전경 끄기(2시대는 그대로)', fg2.fg != null && fg2.rt - fg2.fg <= 3 && fg3.era === 3 && fg3.rt - fg3.fg > 60, { fg2, fg3 });

  // ── 잡몹 체력 ×0.72 · 중간보스 그대로(R26 대비, 같은 새 판 상태) ──
  const hpOf = async (port) => {
    const { browser: b, page: q, errors: e } = await open(`http://127.0.0.1:${port}/index.html`, { w: 960, h: 540, dsf: 1 });
    await start(q);
    await q.waitForTimeout(600);
    const r = await q.evaluate(() => { const g = window.__RELIC, D = window.__RELIC_DEV, p = g.player; D.spawnRole('WOLF', p.x + 300, p.z); const w = g.enemies[g.enemies.length - 1].maxHp; D.spawnRole('HYENA', p.x + 330, p.z); const h = g.enemies[g.enemies.length - 1].maxHp; const bear = D.spawnBear().maxHp; return { w, h, bear }; });
    await b.close();
    return { r, e };
  };
  const o26 = await hpOf(8026);
  const o27 = await hpOf(8027);
  const rw = o27.r.w / o26.r.w, rh = o27.r.h / o26.r.h, rb = o27.r.bear / o26.r.bear;
  ok('I1 일반 몹 체력 ×0.72(늑대 · 하이에나) · 중간보스(곰) 그대로', Math.abs(rw - 0.72) < 0.01 && Math.abs(rh - 0.72) < 0.01 && Math.abs(rb - 1) < 0.001, { r26: o26.r, r27: o27.r, rw: +rw.toFixed(3), rh: +rh.toFixed(3), rb });

  // ── 퀴즈 2건 교정 ──
  const html = fs.readFileSync('/home/user/Um-korean-history-game/shinsi-R27/index.html', 'utf8');
  const q1 = html.includes('"천리장성 쌓는 일을 감독하였고, 뒤에 대막리지가 되어 당의 침략에 강경하게 맞섰다."') && !html.includes('고구려의 대막리지가 되어 권력을 잡았고, 천리장성 쌓는 일을 맡아');
  const q2 = html.includes('1392년 새 나라를 세우고, 1394년 도읍을 한양으로 옮겼다."') && !html.includes('1392년 새 나라를 세우고 도읍을 한양으로 옮겼다."');
  ok('J1 퀴즈 H3-04 · H5-01 디렉터 문구 반영', q1 && q2, { q1, q2 });

  const errs = errors.concat(o26.e, o27.e);
  ok('Z 콘솔 에러 0', errs.length === 0, errs.slice(0, 6));
  console.log(`R27 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
