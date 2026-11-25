// R27 비교 합성용 캡처(dsf 2) — 같은 자리 · 같은 동작에서 화면을 멈춰(ultFreeze + performance.now 고정) 찍는다.
//  사용: node cap27.js r27 | r26
const { open, start, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, '..', 'cap27');
fs.mkdirSync(OUT, { recursive: true });
const which = process.argv[2] || 'r27';
const PORT = which === 'r26' ? 8026 : 8027;
const NEW = which === 'r27';
const ONLY_FIN = process.argv[3] === 'fin';
const ev = (page, f, a) => page.evaluate(f, a);
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 2 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await ev(page, () => {
    window.__freeze = () => { const t = performance.now(); window.__realNow = window.__realNow || performance.now.bind(performance); performance.now = () => t; window.__RELIC.ultFreeze = 1e9; window.__RELIC.clearBeatUntil = 1e12; };
    window.__unfreeze = () => { if (window.__realNow) performance.now = window.__realNow; window.__RELIC.ultFreeze = 0; };
  });
  const hd = () => ev(page, () => { const q = window.__RELIC.quality; q.forced = true; q.tier = 0; });
  const stage = (dx = 430) => ev(page, (dx) => {
    const g = window.__RELIC, p = g.player;
    g.enemies.length = 0; g.projectiles && (g.projectiles.length = 0); g.breathFx && (g.breathFx.length = 0);
    p.x = g.cameraX + dx; p.z = 440; p.y = 0; p.vx = 0; p.vy = 0; p.facing = 1; p.invincibleTimer = 99999; p.attackTimer = 0; p.comboStep = 0;
    const cp = g.companion; if (cp) { cp.x = p.x - 95; cp.z = 426; }
  }, dx);
  const rectOf = () => ev(page, () => { const c = document.querySelector('canvas').getBoundingClientRect(); const g = window.__RELIC; return { l: c.left, t: c.top, w: c.width, h: c.height, cam: g.cameraX, p: [g.player.x, g.player.z], cp: g.companion ? [g.companion.x, g.companion.z] : null }; });
  const snap = async (name) => { const r = await rectOf(); fs.writeFileSync(path.join(OUT, name + '.png'), await page.screenshot()); fs.writeFileSync(path.join(OUT, name + '.json'), JSON.stringify(r)); console.log('snap', name); };
  const still = async (name) => { await ev(page, () => window.__freeze()); await page.waitForTimeout(250); await snap(name); await ev(page, () => window.__unfreeze()); };
  const freezeAt = (want, ms = 1500) => ev(page, ({ want, ms }) => new Promise((res) => {
    const g = window.__RELIC; const t0 = performance.now();
    const L = () => { const n = g._assetMode && g._assetMode.hero; if (want.includes(n)) { window.__freeze(); res(n); } else if (performance.now() - t0 > ms) res('timeout:' + n); else requestAnimationFrame(L); };
    requestAnimationFrame(L);
  }), { want, ms });
  const swing = async (name, want) => { await page.keyboard.press('j'); const got = await freezeAt(want); await page.waitForTimeout(250); await snap(name); await ev(page, () => window.__unfreeze()); console.log(name, got); await page.waitForTimeout(700); };
  const fxFreeze = (ms) => ev(page, (ms) => new Promise((r) => { const L = () => { const f = window.__RELIC.weaponFx; if (f && performance.now() - f.t0 > ms) { window.__freeze(); r(); } else requestAnimationFrame(L); }; requestAnimationFrame(L); }), ms);
  // 4타 피니시: 4번째 타격 판정이 나간 뒤 70ms에 멈춘다(두 빌드 같은 순간)
  const finisher = async (name, kind, role) => {
    await stage(430);
    await ev(page, ({ kind, role }) => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; [[110, 440], [170, 425], [215, 452]].forEach(([dx, z]) => { role ? D.spawnRole(kind, p.x + dx, z) : D.spawnUnit(kind, p.x + dx, z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }); }, { kind, role });
    await page.waitForTimeout(300);
    const armed = ev(page, () => new Promise((res) => { const g = window.__RELIC, p = g.player; let arm = false, fire = 0; const t0 = performance.now(); const L = () => { const now = performance.now(); if (p.comboStep === 4 && p.pendingHit) arm = true; if (arm && !p.pendingHit && !fire) fire = now; if (fire && now - fire > 70) { window.__freeze(); res('ok'); } else if (now - t0 > 4000) res('timeout'); else requestAnimationFrame(L); }; requestAnimationFrame(L); }));
    for (let i = 0; i < 10; i++) { if (await ev(page, () => window.__RELIC.ultFreeze > 1e8)) break; await page.keyboard.press('j'); await page.waitForTimeout(200); }
    console.log(name, await armed);
    await page.waitForTimeout(250);
    await snap(name);
    await ev(page, () => window.__unfreeze());
    await page.waitForTimeout(900);
  };

  // ── 1시대 대사냥꾼 ──
  await hd();
  if (ONLY_FIN) {
    await ev(page, () => window.__RELIC_DEV.setLevel(3));
    await page.waitForTimeout(2600);
    if (NEW) { await ev(page, () => { window.__RELIC.stats.weaponTier = 3; }); await finisher(`${which}_e1_fin`, 'WOLF', true); }
  } else {
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2600);
  await stage(430);
  await page.waitForTimeout(600);
  await still(`${which}_e1_idle`);
  if (NEW) {
    await stage(430);
    await page.waitForTimeout(300);
    await swing(`${which}_e1_swing`, ['atk1_2']);
  }
  await stage(430);
  await page.waitForTimeout(400);
  await ev(page, () => window.__RELIC_DEV.openMidQuiz(0));
  await page.waitForTimeout(1000);
  await page.getByRole('button', { name: /주먹도끼·찍개 등 뗀석기/ }).click();
  if (NEW) {
    await page.waitForFunction(() => window.__RELIC.weaponFx && document.querySelector('[data-testid="relic-banner"]'), null, { timeout: 5000 });
    await fxFreeze(150);
    await page.waitForTimeout(250);
    await snap(`${which}_e1swap_a_flash`);
    await ev(page, () => window.__unfreeze());
    await fxFreeze(430);
    await page.waitForTimeout(250);
    await snap(`${which}_e1swap_b_reveal`);
    await ev(page, () => window.__unfreeze());
  }
  await page.waitForTimeout(3600);
  await stage(430);
  await page.waitForTimeout(500);
  await still(`${which}_e1_t2idle`);
  if (NEW) {
    await stage(430);
    await page.waitForTimeout(300);
    await swing(`${which}_e1_t2swing`, ['atk1_2']);
    await ev(page, () => window.__RELIC_DEV.openMidQuiz(1));
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: /빗살무늬토기와 간석기/ }).click();
    await page.waitForTimeout(3800);
    await stage(430);
    await page.waitForTimeout(500);
    await still(`${which}_e1_t3idle`);
    await finisher(`${which}_e1_fin`, 'WOLF', true);
  }
  }

  // ── 2시대: 몹 무리 속 주인공(영웅 링 · 몹 톤다운) · 4타 피니시 호흡 ──
  await toEra(page, 2);
  await page.waitForTimeout(1500);
  await hd();
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2600);
  await stage(470);
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; [['GOJO_PIKE', -150, 430], ['GOJO_ARCHER', -95, 452], ['GOJO_PIKE', 110, 436], ['GOJO_ARCHER', 165, 455], ['GOJO_PIKE', 225, 425], ['GOJO_ARCHER', 60, 412]].forEach(([u, dx, z]) => { D.spawnUnit(u, p.x + dx, z); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; e.facing = dx > 0 ? -1 : 1; }); });
  await page.waitForTimeout(120);
  await still(`${which}_e2_crowd`);
  if (NEW || !ONLY_FIN) await finisher(`${which}_e2_fin`, 'GOJO_PIKE', false);

  console.log('errors', JSON.stringify(errors.slice(0, 5)));
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
