// 달리기 동작 필름: 오른쪽으로 달리는 1.1초를 CDP 스크린캐스트로 매 프레임 받아(타임스탬프 · 주인공 위치 함께) 저장
const { open, start, toEra } = require('./h');
const fs = require('fs');
const path = require('path');
const [port, era, tag] = [process.argv[2], +process.argv[3], process.argv[4]];
const OUT = path.join(__dirname, '..', 'runfilm', tag);
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${port}/index.html`, { w: 960, h: 540, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  if (era > 1) { await toEra(page, era); await page.waitForTimeout(1200); }
  await page.evaluate(() => { const q = window.__RELIC.quality; q.forced = true; q.tier = 0; });
  await page.evaluate(() => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 150; p.z = 440; p.invincibleTimer = 0; window.__log = []; });
  await page.waitForTimeout(400);
  const cdp = await page.context().newCDPSession(page);
  const frames = [];
  cdp.on('Page.screencastFrame', async (f) => { frames.push({ data: f.data, t: f.metadata.timestamp }); try { await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }); } catch (e) {} });
  // 매 rAF마다 게임 상태 기록(렌더 시각 · 위치 · 동작)
  await page.evaluate(() => { const g = window.__RELIC, p = g.player; const L = () => { window.__log.push({ t: performance.timeOrigin + performance.now(), tick: g.tick, x: +p.x.toFixed(1), cam: +g.cameraX.toFixed(1), pose: g._assetMode && g._assetMode.hero, st: +(p.stepT || 0).toFixed(2), lift: 0 }); if (window.__log.length < 600) requestAnimationFrame(L); }; requestAnimationFrame(L); });
  await page.keyboard.down('ArrowRight');
  await page.waitForTimeout(500);
  await cdp.send('Page.startScreencast', { format: 'png', everyNthFrame: 1, maxWidth: 960, maxHeight: 540 });
  await page.waitForTimeout(1100);
  await cdp.send('Page.stopScreencast');
  await page.keyboard.up('ArrowRight');
  const log = await page.evaluate(() => window.__log);
  frames.forEach((f, i) => fs.writeFileSync(path.join(OUT, `f${String(i).padStart(3, '0')}.png`), Buffer.from(f.data, 'base64')));
  fs.writeFileSync(path.join(OUT, 'frames.json'), JSON.stringify(frames.map((f) => f.t)));
  fs.writeFileSync(path.join(OUT, 'log.json'), JSON.stringify(log));
  console.log(tag, 'frames', frames.length, 'log', log.length, 'errors', errors.length);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
