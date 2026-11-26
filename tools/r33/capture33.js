// R33 납품 이미지 — 전선 배경 4장(+ 교차 순간) · 4대 보스 공격 자세 · 부처님의 가호 3순간 (깜박임 없는 주인공 · 팝업 정리 뒤)
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8033;
fs.mkdirSync(OUT, { recursive: true });
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1000);
  await ev(page, () => window.__RELIC_DEV.r31autoQuiz(true));
  await toEra(page, 4);
  await sleep(2500);
  const calm = () => ev(page, () => { const g = window.__RELIC, p = g.player; p.invincibleTimer = 0; p.hp = p.maxHp || p.hp; g.stats.hp = g.stats.maxHp || g.stats.hp; });
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 330; p.z = 440; p.facing = 1; });
  for (let i = 0; i < 4; i++) {
    await ev(page, (i) => window.__RELIC_DEV.r33bg(i), i);
    if (i === 1) { await sleep(560); await calm(); await page.screenshot({ path: `${OUT}/map_fade_khitan_jurchen.png` }); }
    await sleep(2400);
    await calm();
    await page.screenshot({ path: `${OUT}/map${i + 1}.png` });
  }
  await ev(page, () => window.__RELIC_DEV.r33bg(null));
  // 전선 보스 3인 — 그 전선 배경 위 · 공격(slash) 자세
  const MID = [['MB_SOSON', 0], ['MB_AGUDA', 1], ['MB_SARTAI', 2]];
  for (const [key, z] of MID) {
    await ev(page, (z) => { const g = window.__RELIC; g.enemies.length = 0; g.zoneIdx = z; g.zoneState = 'ROAM'; g.mobTele && (g.mobTele.length = 0); }, z);
    await ev(page, (key) => { window.__RELIC_DEV.r33mid(key); }, key);
    await sleep(400);
    await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies = g.enemies.filter((e) => e.isMidBoss); const en = g.enemies[0]; en.state = 'ACTIVE'; en.attackCooldown = 99999; en.speed = 0; en.x = p.x + 250; en.z = p.z - 6; en.facing = -1; });
    await sleep(3000);
    await ev(page, () => { const g = window.__RELIC; g.mobTele && (g.mobTele.length = 0); const en = g.enemies.find((e) => e.isMidBoss); en.atkAnim = 13; en.windupTimer = 0; en.uBusy = 0; });
    await sleep(34);
    await calm();
    await page.screenshot({ path: `${OUT}/boss_${key}.png` });
  }
  // 최종 보스 파두반
  await ev(page, () => { const g = window.__RELIC; g.enemies.length = 0; g.zoneIdx = 3; g.zoneState = 'ROAM'; });
  await sleep(1500);
  await ev(page, () => window.__RELIC_DEV.r33final());
  await sleep(3300);
  const pin = () => ev(page, () => { const g = window.__RELIC, p = g.player, b = g.boss; if (!b) return; b.x = p.x + 270; b.z = p.z - 4; b.facing = -1; b.charge = b.chargePending = null; b.attackCooldown = 99999; g.bossTele && (g.bossTele.length = 0); });
  await pin();
  await sleep(200);
  await ev(page, () => { const b = window.__RELIC.boss; b.atkAnim = 18; b.lastPat = 'slash'; });
  await sleep(34);
  await calm();
  await page.screenshot({ path: `${OUT}/boss_paduban.png` });
  // 부처님의 가호 — 보스를 주인공 앞에 붙잡아 두고 3순간
  await ev(page, () => { const g = window.__RELIC; g.__pinB = true; const L = () => { const b = g.boss, p = g.player; if (b && g.__pinB) { b.x = p.x + 270; b.z = p.z - 4; b.facing = -1; b.charge = b.chargePending = null; } if (g.__pinB) requestAnimationFrame(L); }; L(); });
  await ev(page, () => window.__RELIC_DEV.r33hp('boss', 0.34));
  await page.waitForFunction(() => !!window.__RELIC.buddhaFx, null, { timeout: 8000 });
  for (const [t, nm] of [[46, 'a_descend'], [86, 'b_palm_hit'], [110, 'c_scrolls']]) {
    await page.waitForFunction((t) => !window.__RELIC.buddhaFx || window.__RELIC.buddhaFx.t >= t, t, { timeout: 8000 });
    await page.screenshot({ path: `${OUT}/buddha_${nm}.png` });
  }
  await ev(page, () => { window.__RELIC.__pinB = false; });
  console.log('capture errors', errors.length, errors.slice(0, 3));
  await browser.close();
})().catch((e) => { console.error('CAPTURE CRASH', e); process.exit(1); });
