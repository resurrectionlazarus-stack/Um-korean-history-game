// R27 핫픽스 기능 테스트 1회(콘솔 에러 0) — 1시대 대사냥꾼 질주 8장 교체: 로드 · 다리 움직임 · 달리는 동안 손에 든 무기
const { open, start } = require('./h');
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
(async () => {
  const { browser, page, errors } = await open('http://127.0.0.1:8027/index.html', { w: 1280, h: 720, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await page.waitForTimeout(600);
  // 구운 질주 8장의 발 위치(아래 30줄 불투명 x 범위) — 프레임마다 달라야 한다
  const baked = await page.evaluate(() => {
    const g = window.__RELIC, H = window.__RELIC_DEV.assets.debug.eras['1@' + (g.quality.dpr || 1)].data.hero;
    const feet = H.runs.map((n) => {
      const c = H.frames[n], cr = (H.crop && H.crop[n]) || { x: 0, y: 0, w: H.srcW, h: H.srcH }, k = c.width / cr.w;
      const x = c.getContext('2d'), h = c.height, w = c.width;
      const band = Math.max(4, Math.round(30 * k));
      const y0 = Math.max(0, Math.min(h - band, Math.round((H.groundY - 30 - cr.y) * k)));
      const D = x.getImageData(0, y0, w, band).data;
      let lo = w, hi = -1;
      for (let i = 3; i < D.length; i += 4) if (D[i] > 60) { const px = ((i - 3) / 4) % w; if (px < lo) lo = px; if (px > hi) hi = px; }
      return [Math.round(cr.x + lo / k), Math.round(cr.x + hi / k)];
    });
    return { runs: H.runs.length, frames: Object.keys(H.frames).length, feet, fails: window.__RELIC_DEV.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)) };
  });
  const spans = baked.feet.map((f) => f[1] - f[0]);
  const lefts = baked.feet.map((f) => f[0]);
  ok('A1 대사냥꾼 22장 · 질주 8장 로드 · 실패 0', baked.frames === 22 && baked.runs === 8 && baked.fails.length === 0, { frames: baked.frames, runs: baked.runs });
  ok('A2 질주 8장 발 위치가 프레임마다 달라짐(보폭 폭 차 ≥ 150 · 뒷발 위치 차 ≥ 100, 원본 px)', Math.max(...spans) - Math.min(...spans) >= 150 && Math.max(...lefts) - Math.min(...lefts) >= 100, { feet: baked.feet });
  // 실제로 달리기: 8장이 차례로 나오고 무기는 손에(T1), 이동 거리 정상
  const samp = page.evaluate(() => new Promise((res) => { const g = window.__RELIC, p = g.player; const out = []; const t0 = performance.now(); const L = () => { out.push([Math.round(p.x), g._assetMode && g._assetMode.hero, p._wDrawnTier || 0]); if (performance.now() - t0 < 1500) requestAnimationFrame(L); else res(out); }; requestAnimationFrame(L); }));
  await page.keyboard.down('ArrowRight');
  await page.waitForTimeout(1450);
  await page.keyboard.up('ArrowRight');
  const out = await samp;
  const runs = [...new Set(out.map((o) => o[1]).filter((n) => /^run/.test(n || '')))];
  ok('B1 달리는 동안 질주 8장 차례 재생 + 손에 든 무기(T1) + 이동', runs.length === 8 && out.filter((o) => /^run/.test(o[1] || '')).every((o) => o[2] === 1) && out[out.length - 1][0] - out[0][0] > 500, { runs: runs.length, dx: out[out.length - 1][0] - out[0][0] });
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  console.log(`R27 RUNFIX ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
