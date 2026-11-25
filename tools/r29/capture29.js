// R29 문서용 장면 필름(CDP 스크린캐스트): 두 동강 · 질풍연참 · AIR RAID — 구역 전투가 걸리지 않는 Z1 앞(x 360)에서
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
const setup = (page, units, hp) => ev(page, ({ units, hp }) => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; g.zoneIdx = 0; g.zoneState = 'ROAM'; g.waves = []; p.x = 360; p.z = 430; p.facing = 1; p.vx = 0; p.invincibleTimer = 99999; p.comboStep = 0; p.comboResetTimer = 0; p.cdDash = 0; units.forEach(([u, dx, dz]) => D.spawnUnit(u, p.x + dx, p.z + dz)); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = hp; e.maxHp = Math.max(hp, 1000); e.attackCooldown = 9999; }); }, { units, hp });
(async () => {
  const { browser, page, errors } = await open('http://127.0.0.1:8030/index.html', { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await toEra(page, 2);
  await sleep(1500);
  await ev(page, () => { window.__RELIC_DEV.setLevel(4); const q = window.__RELIC.quality; q.forced = true; q.tier = 0; });
  await sleep(2500);
  await setup(page, [['HAN_PIKE', 112, 0], ['YAN_PIKE', 150, 34]], 1e9);
  await sleep(500);
  await film(page, 'cut', 900, async () => { await ev(page, () => window.__RELIC.enemies.forEach((e) => { e.hp = 1; })); await page.keyboard.press('j'); });
  await setup(page, [['YAN_PIKE', 125, -18], ['HAN_ARCHER', 175, 22], ['YAN_PIKE', 220, 0]], 1e9);
  await sleep(500);
  await film(page, 'rush', 2300, async () => { for (let i = 0; i < 5; i++) { await page.keyboard.press('j'); await sleep(190); } });
  await setup(page, [['YAN_PIKE', 120, -20], ['HAN_PIKE', -110, 16], ['YAN_ARCHER', 150, 30]], 1e9);
  await sleep(500);
  await film(page, 'air', 1500, async () => { await page.keyboard.press('c'); await sleep(170); for (let i = 0; i < 4; i++) { await page.keyboard.press('j'); await sleep(170); } });
  console.log('errors', errors.length, JSON.stringify(errors.slice(0, 3)));
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
