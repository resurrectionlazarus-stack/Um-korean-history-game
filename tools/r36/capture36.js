// R36 납품 이미지용 촬영 — 시대별 갈래 기술 4종(올려치기 · 공중 추격 · 내려찍기 · 관통 돌진)을 실제 입력으로 발동해 맞는 순간 앞뒤 2장씩 찍는다.
//  node tools/r36/capture36.js <out-dir> [포트=8039] [시대 목록=1,2,3,4,5,6]
//  합성은 compose36.py
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8039;
const ERAS = (process.argv[4] || '1,2,3,4,5,6').split(',').map(Number);
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  const ev = (f, a) => page.evaluate(f, a);
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await ev(() => window.__RELIC_DEV.r31autoQuiz(true));
  const tap = async (k = 'j') => { await page.keyboard.down(k); await sleep(40); await page.keyboard.up(k); };
  const setup = (era) => ev((era) => {
    const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
    g.stats.level = 3; g.stats.weaponTier = 3;
    g.enemies.length = 0; g.zoneState = 'ROAM'; g.waves = []; g.paleoWaves = null; g.spawnQ = [];
    p.invincibleTimer = 99999; p.x = 400; p.vx = 0; p.z = 440; p.y = 0; p.vy = 0; p.facing = 1;
    p.comboStep = 0; p.comboResetTimer = 0; p._brLock = false; p._finRot = null; p._chaseUntil = 0; p.attackTimer = 0; p.pendingHit = null; p.bufferAtk = false;
    // 가벼운 적 셋(앞 · 조금 뒤 · 등 뒤)
    const R = window.__RELIC_DATA.roster[era] || [];
    const U = window.__RELIC_DATA.units;
    const light = R.filter((u) => U[u] && !U[u].heavy && !U[u].ranged && !U[u].cav)[0] || R[0];
    const mk = (dx, dz) => { if (era === 1) D.spawnRole('WOLF', p.x + dx, p.z + dz); else D.spawnUnit(light, p.x + dx, p.z + dz); const en = g.enemies[g.enemies.length - 1]; en.x = p.x + dx; en.z = p.z + dz; en.hp = en.maxHp = 1e9; en.attackCooldown = 1e9; en.speed = 0; en.state = 'ACTIVE'; en.stateTimer = 0; en.guardCd = 1e9; en.facing = dx > 0 ? -1 : 1; return en; };
    g.__d = [mk(78, 0), mk(150, 16), mk(-84, -10)];
    return light;
  }, era);
  const shot = (name) => page.screenshot({ path: `${OUT}/${name}.png`, clip: { x: 0, y: 40, width: 1280, height: 640 } });
  for (const era of ERAS) {
    if (era > 1) { await toEra(page, era); await sleep(1600); }
    const unit = await setup(era);
    await sleep(500);
    // ① 올려치기 → ② 공중 추격
    await tap(); await sleep(430);
    await page.keyboard.down('w'); await sleep(30); await tap(); await sleep(30); await page.keyboard.up('w');
    await sleep(120); await shot(`e${era}_launch_a`);
    await sleep(60); await shot(`e${era}_launch_b`);
    await tap();
    await sleep(170); await shot(`e${era}_chase_a`);
    await sleep(90); await shot(`e${era}_chase_b`);
    for (let i = 0; i < 4; i++) { await tap(); await sleep(190); }
    await page.waitForFunction(() => window.__RELIC.player.y === 0, null, { timeout: 5000 }).catch(() => null);
    await sleep(900);
    // ③ 내려찍기
    await setup(era); await sleep(350);
    await tap(); await sleep(430);
    await page.keyboard.down('s'); await sleep(30); await tap();
    await sleep(190); await shot(`e${era}_slam_a`);
    await sleep(70); await shot(`e${era}_slam_b`);
    await page.keyboard.up('s');
    await sleep(900);
    // ④ 관통 돌진(마무리 돌림에서 차례가 오도록 맞춰 둔다)
    await setup(era); await sleep(350);
    await ev((era) => { const p = window.__RELIC.player; p.comboStep = 3; p.comboResetTimer = 50; p._finRot = era === 2 ? 0 : 1; }, era);
    await tap();
    await sleep(110); await shot(`e${era}_lunge_a`);
    await sleep(60); await shot(`e${era}_lunge_b`);
    await sleep(900);
    const b = await ev(() => window.__RELIC_DEV.r36().branch);
    console.log('era', era, 'unit', unit, JSON.stringify(b));
  }
  console.log('errors', errors.length, errors.slice(0, 3));
  await browser.close();
})().catch((e) => { console.error('CRASH', e); process.exit(1); });
