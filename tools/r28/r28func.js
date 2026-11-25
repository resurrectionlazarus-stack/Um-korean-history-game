// R28 기능 테스트 1회(콘솔 에러 0) — 김유신 8프레임 질주(몸 흔들림 보정) · 1시대 하이에나 · 코뿔소 원화(톤다운 생략) · 대사냥꾼 질주 임시본 유지
const { open, start, toEra } = require('./h');
const fs = require('fs');
const crypto = require('crypto');
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const toneOf = (page, era, key, file) => ev(page, async ({ era, key, file }) => {
  const g = window.__RELIC, d = window.__RELIC_DEV.assets.debug.eras[era + '@' + (g.quality.dpr || 1)].data;
  const fc = d.mobs && d.mobs[key] && d.mobs[key].frames.idle;
  if (!fc) return null;
  const meanOf = (src, w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.drawImage(src, 0, 0, w, h); const D = x.getImageData(0, 0, w, h).data; let s = 0, n = 0; for (let i = 0; i < D.length; i += 4) if (D[i + 3] > 220) { s += D[i] + D[i + 1] + D[i + 2]; n++; } return s / Math.max(1, n) / 3; };
  const img = new Image(); img.src = file; await img.decode();
  return +(meanOf(fc, fc.width, fc.height) / meanOf(img, img.naturalWidth, img.naturalHeight)).toFixed(3);
}, { era, key, file });
(async () => {
  const sha = (p) => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  const keep = ['run', 'run2', 'run3', 'run4', 'run5', 'run6', 'run7', 'run8'].every((r) => sha(`/home/user/Um-korean-history-game/shinsi-R28/assets/hero/era1_hunter_${r}.webp`) === sha(`/home/user/Um-korean-history-game/shinsi-R27/assets/hero/era1_hunter_${r}.webp`));
  ok('A0 대사냥꾼 질주 = R27 핫픽스 임시본 유지(묶음의 자세 고정 8장 미적용)', keep);
  const { browser, page, errors } = await open('http://127.0.0.1:8029/index.html', { w: 1280, h: 720, dsf: 1 });
  await start(page);
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await page.waitForTimeout(500);
  // 1시대 하이에나 · 코뿔소 원화 + 톤다운 생략
  const art1 = await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; g.enemies.length = 0; D.spawnRole('HYENA', p.x + 200, p.z); D.spawnRole('RHINO', p.x + 330, p.z); D.spawnRole('WOLF', p.x + 450, p.z); g.enemies.forEach((e) => { e.state = 'ACTIVE'; e.hp = e.maxHp = 1e9; e.attackCooldown = 9999; }); return new Promise((res) => setTimeout(() => res(g.enemies.map((e) => [e.mobRole, e._mobArt || null])), 600)); });
  const hy = await toneOf(page, 1, 'hyena', 'assets/mob/era1_hyena_idle.png');
  const wo = await toneOf(page, 1, 'wolf', 'assets/mob/era1_wolf_idle.png');
  ok('B1 1시대 하이에나 · 코뿔소 = 원화(늑대 그대로)', JSON.stringify(art1) === JSON.stringify([['HYENA', 'hyena'], ['RHINO', 'rhino'], ['WOLF', 'wolf']]), art1);
  ok('B2 하이에나 굽기 톤다운 생략(≈ 1.0) · 늑대는 기존 톤다운(≈ 0.88)', hy > 0.97 && hy < 1.03 && wo > 0.84 && wo < 0.92, { hyena: hy, wolf: wo });
  // 3시대 김유신 8프레임 질주 + 몸 흔들림 보정
  await toEra(page, 3);
  await page.waitForTimeout(1200);
  const kim = await ev(page, () => { const g = window.__RELIC, H = window.__RELIC_DEV.assets.debug.eras['3@' + (g.quality.dpr || 1)].data.hero; return { runs: H.runs, dx: ['run3', 'run4', 'run5', 'run6', 'run7', 'run8'].map((n) => H.poseDX[n]), fails: window.__RELIC_DEV.assets.debug.log.filter((l) => /실패|누락|failed/.test(l)) }; });
  ok('C1 김유신 질주 8장(run~run8) · 몸 흔들림 보정 poseDX 적용 · 로드 실패 0', kim.runs.length === 8 && kim.dx.join() === '-23,4,18,-23,-28,8' && kim.fails.length === 0, kim);
  await ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; p.x = g.cameraX + 200; p.invincibleTimer = 99999; });
  await page.waitForTimeout(300);
  const smp = ev(page, () => new Promise((res) => { const g = window.__RELIC, p = g.player; const out = []; const t0 = performance.now(); const L = () => { out.push([g.tick, g._assetMode && g._assetMode.hero, Math.round(p.x)]); if (performance.now() - t0 < 1600) requestAnimationFrame(L); else res(out); }; requestAnimationFrame(L); }));
  await page.keyboard.down('ArrowRight');
  await page.waitForTimeout(1550);
  await page.keyboard.up('ArrowRight');
  const out = await smp;
  const runs = out.filter((o) => /^run/.test(o[1] || ''));
  let ch = 0; for (let i = 1; i < runs.length; i++) if (runs[i][1] !== runs[i - 1][1]) ch++;
  const tpf = (runs[runs.length - 1][0] - runs[0][0]) / Math.max(1, ch);
  ok('C2 3시대 달리기 = 8장 차례 재생 · 프레임당 3~4틱 · 이동', new Set(runs.map((o) => o[1])).size === 8 && tpf >= 3 && tpf <= 4.2 && out[out.length - 1][2] - out[0][2] > 500, { frames: new Set(runs.map((o) => o[1])).size, ticksPerFrame: +tpf.toFixed(2), dx: out[out.length - 1][2] - out[0][2] });
  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 5));
  console.log(`R28 FUNC ${Object.values(R).filter(Boolean).length}/${Object.keys(R).length}`);
  await browser.close();
})().catch((e) => { console.error('ERR', e); process.exit(1); });
