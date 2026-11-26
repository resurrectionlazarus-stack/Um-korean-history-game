// R30 문서용 장면: 오라 1~4단계 · 시대별 오라 · 회전참/질풍연참/황금 용오름 필름 · 연·한 정식 원화 줄 · 김유신 질주
const { open, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function film(page, tag, ms, act) {
  const cdp = await page.context().newCDPSession(page);
  const frames = [];
  cdp.on('Page.screencastFrame', async (f) => { frames.push(f.data); try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch (e) {} });
  await cdp.send('Page.startScreencast', { format: 'png', everyNthFrame: 1, maxWidth: 1280, maxHeight: 720 });
  await act();
  await sleep(ms);
  await cdp.send('Page.stopScreencast');
  const dir = path.join(OUT, tag);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  frames.forEach((d, i) => fs.writeFileSync(path.join(dir, `f${String(i).padStart(3, '0')}.png`), Buffer.from(d, 'base64')));
  console.log(tag, frames.length);
}
const stage = (page, units, opt = {}) => ev(page, ({ units, opt }) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0; g.zoneIdx = 0; g.zoneState = 'ROAM'; g.waves = []; g.spawnQ = [];
  p.x = opt.x || 380; p.z = 440; p.y = 0; p.vy = 0; p.vx = 0; p.facing = 1; p.invincibleTimer = 99999; p.ghosts.length = 0;
  p.comboStep = 0; p.comboResetTimer = 0; p.cdDash = 0; p.cdUpper = 0; p.rush = null; p.plunge = false;
  g.special = null; g.specialCd = opt.noSpecial ? 1e9 : 0; g.stats.combo = opt.combo || 0; g.comboDecayTimer = 900; g.cameraX = Math.max(0, p.x - 380);
  if (opt.lv) { D.setLevel(opt.lv); g.stats.level = opt.lv; }
  if (opt.tier) g.stats.weaponTier = opt.tier;
  g.relicBuff = null;
  units.forEach(([u, dx, dz, hp]) => { D.spawnUnit(u, p.x + dx, p.z + dz); const e = g.enemies[g.enemies.length - 1]; e.state = 'ACTIVE'; e.hp = e.maxHp = hp; e.attackCooldown = 9999; e.speed = 0; });
}, { units, opt });
(async () => {
  const { browser, page, errors } = await open('http://127.0.0.1:8031/index.html', { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await ev(page, () => { const q = window.__RELIC.quality; q.forced = true; q.tier = 0; });
  // 1) 시대별 풀 오라(3단계) — 1시대부터 6시대까지
  for (let era = 1; era <= 6; era++) {
    if (era > 1) { await toEra(page, era); await sleep(1500); }
    await stage(page, [], { lv: 4, tier: 1, noSpecial: true });
    await sleep(900);
    await page.screenshot({ path: `${OUT}/aura_era${era}.png` });
    if (era === 2) {
      // 2) 2시대: 오라 1~4단계 + 연·한 정식 원화 줄 + 회전참 · 질풍연참 필름
      for (const [lv, tier, combo, tag] of [[1, 1, 0, 's1'], [2, 1, 0, 's2'], [4, 1, 0, 's3'], [5, 3, 30, 's4']]) {
        await ev(page, ({ lv, tier, combo }) => { const g = window.__RELIC; g.stats.level = lv; g.stats.weaponTier = tier; g.stats.combo = combo; g.comboDecayTimer = 900; }, { lv, tier, combo });
        await sleep(800);
        await page.screenshot({ path: `${OUT}/aura_stage_${tag}.png` });
      }
      await stage(page, [['YAN_PIKE', 150, -30, 1e9], ['YAN_ARCHER', 260, 10, 1e9], ['HAN_PIKE', 370, -20, 1e9], ['HAN_ARCHER', 480, 25, 1e9], ['HAN_ELITE', 600, 0, 1e9]], { lv: 1, noSpecial: true, x: 300 });
      await sleep(900);
      await page.screenshot({ path: `${OUT}/era2_lineup.png` });
      await stage(page, [['YAN_PIKE', 120, -10, 1e9], ['HAN_PIKE', -110, 12, 1e9], ['YAN_ARCHER', 170, 24, 1e9]], { lv: 3, tier: 2, noSpecial: true });
      await sleep(1400);
      await film(page, 'spin', 1300, async () => { for (let i = 0; i < 4; i++) { await page.keyboard.press('j'); await sleep(230); } });
      await stage(page, [['YAN_PIKE', 120, -14, 1e9], ['HAN_ARCHER', 170, 18, 1e9], ['YAN_PIKE', 220, 0, 1e9]], { lv: 5, tier: 3, noSpecial: true });
      await sleep(1600);
      await film(page, 'rush5', 3000, async () => { for (let i = 0; i < 5; i++) { await page.keyboard.press('j'); await sleep(190); } });
    }
    if (era === 3) {
      // 3) 김유신 질주 필름 · 황금 용오름 일섬 필름
      await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 220; });
      await sleep(300);
      await page.keyboard.down('ArrowRight');
      await sleep(400);
      await film(page, 'kimrun', 700, async () => {});
      await page.keyboard.up('ArrowRight');
      await stage(page, [['BJ_GUARD', 130, -16, 1e9], ['BJ_ARCHER', 200, 18, 1e9], ['BJ_GUARD', -120, 0, 1e9], ['GG_PIKE', 300, -10, 1e9]], { lv: 4, combo: 20 });
      await sleep(1500);
      await ev(page, () => { const g = window.__RELIC; g.enemies.forEach((e) => { e.hp = e.maxHp = 1e9; }); g.stats.combo = 20; g.comboDecayTimer = 900; });
      await film(page, 'dragon', 2400, async () => { for (let i = 0; i < 4; i++) { await page.keyboard.press('j'); await sleep(230); } });
    }
  }
  console.log('errors', errors.length, JSON.stringify(errors.slice(0, 3)));
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
