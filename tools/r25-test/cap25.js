// R25 비교 합성용 캡처(dsf 2) — 같은 자리 · 같은 동작에서 화면을 멈춰(ultFreeze + performance.now 고정) 찍는다.
//  사용: node cap25.js r25 | r24
const { open, start, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const OUT = path.join(__dirname, '..', 'cap25');
fs.mkdirSync(OUT, { recursive: true });
const which = process.argv[2] || 'r25';
const PORT = which === 'r24' ? 8024 : 8025;
const ev = (page, f, a) => page.evaluate(f, a);
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 2 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await ev(page, () => {
    window.__freeze = () => { const t = performance.now(); window.__realNow = window.__realNow || performance.now.bind(performance); performance.now = () => t; window.__RELIC.ultFreeze = 1e9; };
    window.__unfreeze = () => { if (window.__realNow) performance.now = window.__realNow; window.__RELIC.ultFreeze = 0; };
  });
  const hd = () => ev(page, () => { const q = window.__RELIC.quality; q.forced = true; q.tier = 0; });
  const stage = (dx = 430) => ev(page, (dx) => {
    const g = window.__RELIC, p = g.player;
    g.enemies.length = 0; g.projectiles && (g.projectiles.length = 0);
    p.x = g.cameraX + dx; p.z = 440; p.y = 0; p.vx = 0; p.vy = 0; p.facing = 1; p.invincibleTimer = 99999; p.attackTimer = 0; p.comboStep = 0;
    const cp = g.companion; if (cp) { cp.x = p.x - 95; cp.z = 426; }
  }, dx);
  // 동작 이름이 want가 되는 순간 멈춘다
  const freezeAt = (want, ms = 1500) => ev(page, ({ want, ms }) => new Promise((res) => {
    const g = window.__RELIC; const t0 = performance.now();
    const L = () => { const n = g._assetMode && g._assetMode.hero; if (want.includes(n)) { window.__freeze(); res(n); } else if (performance.now() - t0 > ms) res('timeout:' + n); else requestAnimationFrame(L); };
    requestAnimationFrame(L);
  }), { want, ms });
  const rectOf = () => ev(page, () => { const c = document.querySelector('canvas').getBoundingClientRect(); const g = window.__RELIC; return { l: c.left, t: c.top, w: c.width, h: c.height, cam: g.cameraX, p: [g.player.x, g.player.z], cp: g.companion ? [g.companion.x, g.companion.z] : null, b: g.boss ? [g.boss.x, g.boss.z] : null }; });
  const snap = async (name) => { const r = await rectOf(); fs.writeFileSync(path.join(OUT, name + '.png'), await page.screenshot()); fs.writeFileSync(path.join(OUT, name + '.json'), JSON.stringify(r)); };
  const swing = async (name, want) => {
    await page.keyboard.press('j');
    const got = await freezeAt(want);
    await page.waitForTimeout(250);
    await snap(name);
    await ev(page, () => window.__unfreeze());
    console.log(name, got);
    await page.waitForTimeout(700);
  };
  const toBoss = async () => {
    await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneIdx = 3; g.zoneState = 'ROAM'; p.x = 5690 + 24; p.vx = 0; p.y = 0; p.vy = 0; g.cameraX = 5440; });
    await page.waitForFunction(() => window.__RELIC.bossActive && window.__RELIC.boss, null, { timeout: 10000 });
    await page.waitForTimeout(2600);
    await ev(page, () => { const g = window.__RELIC, p = g.player, b = g.boss; p.invincibleTimer = 99999; b.hp = b.maxHp; g.enemies.length = 0; p.x = b.x - 230; p.z = b.z; p.facing = 1; const cp = g.companion; if (cp) { cp.x = p.x - 95; cp.z = p.z - 14; } });
  };

  // ── 2시대 주인공 · 동료 · 보스 ──
  await toEra(page, 2);
  await page.waitForTimeout(1500);
  await hd();
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await page.waitForTimeout(2500);
  await stage(430);
  await page.waitForTimeout(600);
  await ev(page, () => window.__freeze());
  await page.waitForTimeout(250);
  await snap(`${which}_e2_idle`);
  await ev(page, () => window.__unfreeze());
  await stage(430);
  await page.waitForTimeout(300);
  await swing(`${which}_e2_swing`, which === 'r24' ? ['atk1', 'atk2'] : ['atk1_2']);

  if (which === 'r25') {
    // ── 무기 변환: T1 → 옛 무기 흰빛(변환 섬광) → T2 + 배너 → T3 ──
    await stage(430);
    await page.waitForTimeout(400);
    await ev(page, () => window.__RELIC_DEV.openMidQuiz(0));
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: /세형 동검\(한국식 동검\)/ }).click();
    await page.waitForFunction(() => window.__RELIC.weaponFx && document.querySelector('[data-testid="relic-banner"]'), null, { timeout: 5000 });
    await ev(page, () => new Promise((r) => { const L = () => { const f = window.__RELIC.weaponFx; if (f && performance.now() - f.t0 > 150) { window.__freeze(); r(); } else requestAnimationFrame(L); }; requestAnimationFrame(L); }));
    await page.waitForTimeout(250);
    await snap('r25_swap_a_flash');
    await ev(page, () => window.__unfreeze());
    await ev(page, () => new Promise((r) => { const L = () => { const f = window.__RELIC.weaponFx; if (f && performance.now() - f.t0 > 420) { window.__freeze(); r(); } else requestAnimationFrame(L); }; requestAnimationFrame(L); }));
    await page.waitForTimeout(250);
    await snap('r25_swap_b_reveal');
    await ev(page, () => window.__unfreeze());
    await page.waitForTimeout(3600);
    await stage(430);
    await page.waitForTimeout(300);
    await swing('r25_swap_c_t2swing', ['atk1_2']);
    await ev(page, () => window.__RELIC_DEV.openMidQuiz(1));
    await page.waitForTimeout(1000);
    await page.getByRole('button', { name: /명도전/ }).first().click();
    await page.waitForFunction(() => window.__RELIC.stats.weaponTier === 3 && document.querySelector('[data-testid="relic-banner"]'), null, { timeout: 5000 });
    await ev(page, () => new Promise((r) => { const L = () => { const f = window.__RELIC.weaponFx; if (f && performance.now() - f.t0 > 900) { window.__freeze(); r(); } else requestAnimationFrame(L); }; requestAnimationFrame(L); }));
    await page.waitForTimeout(250);
    await snap('r25_swap_d_t3');
    await ev(page, () => window.__unfreeze());
    await page.waitForTimeout(3200);
  }

  // ── 2시대 보스 ──
  await toBoss();
  await ev(page, () => new Promise((r) => { const g = window.__RELIC; const t0 = performance.now(); const L = () => { const b = g.boss; const n = b && b._assetFrame; if (n === 'command' || n === 'slash' || n === 'smash' || n === 'thunder' || performance.now() - t0 > 9000) { window.__freeze(); r(n); } else requestAnimationFrame(L); }; requestAnimationFrame(L); }));
  await page.waitForTimeout(250);
  await snap(`${which}_e2_boss`);
  await ev(page, () => window.__unfreeze());
  // ── 4시대 척준경 ──
  await toEra(page, 4);
  await page.waitForTimeout(1500);
  await hd();
  await stage(430);
  await page.waitForTimeout(500);
  await swing(`${which}_cjg_swing`, which === 'r24' ? ['atk1_2', 'atk1'] : ['atk1_2']);
  await stage(430);
  await page.waitForTimeout(400);
  await ev(page, () => window.__freeze());
  await page.waitForTimeout(250);
  await snap(`${which}_cjg_idle`);
  await ev(page, () => window.__unfreeze());

  console.log('errors', JSON.stringify(errors.slice(0, 5)));
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
