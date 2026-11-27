// R35 기능 테스트 1회(콘솔 에러 0) — 무기 종류별 타격음(둔기 · 창 · 칼 · 갑옷 · 양단) · 휘두르는 바람 · 방향 전환 궤적 끊기 ·
//  시대 배경음악(mp3: 로드 · 표지음 보정 · 전장/보스 구간 · 반복 · 광폭화 빠르기 · 일시정지/재개 · 시대 전환 · ?bgm=synth)
// 사용: node tools/r35/r35func.js <출력 폴더> [포트=8038]
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8038;
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const r35 = (page) => ev(page, () => window.__RELIC_DEV.r35());
const calm = (page) => ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; g.waves = []; g.spawnQ = []; p.invincibleTimer = 99999; p.x = g.cameraX + 420; p.z = 440; p.facing = 1; });
// 맞아 줄 적 하나를 주인공 앞에 세운다(체력 크게 · 공격 안 함)
const dummy = (page, unit, hp = 1e9) => ev(page, ([unit, hp]) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0;
  let en = null;
  if (unit === 'bear') en = D.spawnBear();
  else { D.spawnUnit(unit, p.x + 74, p.z); en = g.enemies[g.enemies.length - 1]; }
  if (!en) return null;
  en.x = p.x + 74; en.z = p.z; en.y = 0; en.hp = en.maxHp = hp; en.state = 'ACTIVE'; en.attackCooldown = 1e9; en.spawnTimer = 0; en.vx = en.vz = 0; en.speed = 0; en.knockRes = 1;
  g.__dummy = en;
  return { unit: en.unit || en.kind || null, heavy: !!en.heavy, guard: en.guardRate || 0, mid: !!en.isMidBoss };
}, [unit, hp]);
const pin = (page) => ev(page, () => { const g = window.__RELIC, p = g.player, en = g.__dummy; if (en && en.state !== 'DYING') { en.x = p.x + 74 * p.facing; en.z = p.z; en.y = 0; en.vx = en.vy = 0; en.attackCooldown = 1e9; if (en.hitStun > 4) en.hitStun = 4; } p.invincibleTimer = 99999; });
const combo = async (page, n) => {
  for (let i = 0; i < n; i++) {
    await pin(page);
    await page.keyboard.down('j'); await sleep(40); await page.keyboard.up('j');
    await sleep(330);
  }
  await sleep(350);
};
const sndDiff = (a, b) => { const o = {}; for (const k of Object.keys(b)) if ((b[k] || 0) - (a[k] || 0) > 0) o[k] = b[k] - (a[k] || 0); return o; };

(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await ev(page, () => window.__RELIC_DEV.r31autoQuiz(true));
  // ── A. 목록 · 샘플 로드
  const man = await ev(page, async () => { const m = await (await fetch('assets/MANIFEST.json')).json(); const k = Object.keys(m.files); return { n: k.length, r35: k.filter((x) => m.files[x].r35).length, bgm: k.filter((x) => m.files[x].kind === 'bgm').length, block: m.r35 ? [m.r35.addedSfx, m.r35.addedBgm, m.r35.replaced] : null }; });
  ok('A0 MANIFEST 440항목 · R35 표식 24(타격음 15 · 배경음악 6 · 무기 3)', man.n === 440 && man.r35 === 24 && man.bgm === 6 && man.block.join() === '15,6,3', man);
  await page.waitForFunction(() => { const s = window.__RELIC_DEV.sfxStats(); return s && s.loaded + s.failed >= 30; }, null, { timeout: 15000 }).catch(() => null);
  const s0 = await ev(page, () => window.__RELIC_DEV.sfxStats());
  ok('A1 효과음 30종 로드(예전 타격음 8종 빼고 새 15종) · 실패 0', s0.loaded === 30 && s0.failed === 0, [s0.loaded, s0.failed]);
  // ── D1. 배경음악: 시작하자마자 1시대 곡(전장 구간)
  await page.waitForFunction(() => { const b = window.__RELIC_DEV.r35().bgm; return b && b.fileOn && b.file.playing; }, null, { timeout: 12000 }).catch(() => null);
  let b = (await r35(page)).bgm;
  ok('D1 1시대 곡 재생(mp3 · 전장 구간) · 표지음 보정값 · 합성 BGM은 한 음도 안 냄', b.fileOn && b.track === 'field1' && b.file.era === 1 && b.file.sec === 'a' && b.file.marks[1] > 0.01 && b.file.marks[1] < 0.09 && b.notes === 0, { track: b.track, era: b.file.era, sec: b.file.sec, mark: b.file.marks[1], synthNotes: b.notes, cached: b.file.cached });
  // ── B. 타격음: 1시대 둔기(주먹도끼) → 창(슴베찌르개)
  await calm(page);
  let d = await dummy(page, 'bear');
  let a0 = (await r35(page)).snd, m0 = (await r35(page)).smp.by;
  await ev(page, () => { window.__RELIC.stats.weaponTier = 1; });
  await combo(page, 5);
  let a1 = (await r35(page)).snd, m1 = (await r35(page)).smp.by;
  let df = sndDiff(a0, a1);
  ok('B1 1시대 둔기: 바위 타격음(rock_hit 1 · 2 번갈아 + 연타 마지막 타 rock_heavy) · 칼 소리 없음', (df.rockHit1 || 0) >= 1 && (df.rockHit2 || 0) >= 1 && (df.rockHeavy || 0) >= 1 && !Object.keys(df).some((k) => k.startsWith('cut')), df);
  ok('B2 휘두를 때 둔기 바람(whoosh_heavy)', (m1.whooshHeavy || 0) - (m0.whooshHeavy || 0) >= 3 && !(m1.whooshBlade > 0), { heavy: m1.whooshHeavy || 0, blade: m1.whooshBlade || 0 });
  await ev(page, () => { window.__RELIC.stats.weaponTier = 2; });
  a0 = a1;
  await combo(page, 3);
  a1 = (await r35(page)).snd;
  df = sndDiff(a0, a1);
  ok('B3 1시대 창(슴베찌르개): 찌르는 소리(stab 1 · 2)', (df.stab1 || 0) + (df.stab2 || 0) >= 2 && !df.rockHit1 && !df.rockHit2, df);
  await ev(page, () => { window.__RELIC.stats.weaponTier = 1; });
  // ── C. 휘두르는 도중 방향 전환 → 궤적 끊기
  await calm(page);
  const tc0 = (await r35(page)).trailCut;
  await page.keyboard.press('ArrowRight'); await sleep(150);
  await page.keyboard.down('j'); await sleep(40); await page.keyboard.up('j');
  await sleep(110);
  await page.keyboard.down('ArrowLeft'); await sleep(60);
  const mid = await ev(page, () => { const p = window.__RELIC.player; return { f: p.facing, at: p.attackTimer, wt: (p._wt || []).length }; });
  await sleep(120); await page.keyboard.up('ArrowLeft');
  const tc1 = (await r35(page)).trailCut;
  ok('C1 공격 도중 방향 전환 → 궤적 끊김(가로 띠 없음)', tc1 > tc0 && mid.f === -1, { cut: [tc0, tc1], mid });
  // ── D2. 반복: 빠르기를 6배로 올려(한 바퀴 ≈ 6.2초) 두 바퀴 이상 이어지는지
  await ev(page, () => window.__RELIC_DEV.r35bgm('setTempo', 6));
  await sleep(14500);
  b = (await r35(page)).bgm;
  ok('D2 반복 재생: 6배속 14.5초 동안 2바퀴 이상 이어짐 · 겹친 소스 ≤ 3', b.file.loops >= 2 && b.file.live >= 1 && b.file.live <= 3 && b.file.rate === 6, { loops: b.file.loops, live: b.file.live, pos: b.file.pos });
  await ev(page, () => window.__RELIC_DEV.r35bgm('setTempo', 1));
  await sleep(400);
  // ── D3. 일시정지 → 재개(같은 자리에서)
  const p0 = (await r35(page)).bgm.file.pos;
  await page.keyboard.press('p'); await sleep(700);
  const bp = (await r35(page)).bgm;
  await page.keyboard.press('p'); await sleep(900);
  const br = (await r35(page)).bgm;
  ok('D3 일시정지 = 음악 멈춤 → 재개 = 멈춘 자리에서 이어짐', bp.file.paused && !bp.file.playing && br.file.playing && br.file.pos >= p0 && br.file.pos < p0 + 3, { before: p0, paused: [bp.file.paused, bp.file.playing], after: br.file.pos, log: br.file.log.slice(-4) });
  // ── B. 2시대 칼(해모수): 베는 소리 · 3타부터 강타
  await toEra(page, 2); await sleep(1200); await calm(page);
  b = (await r35(page)).bgm;
  ok('D4 2시대로 넘어가면 2시대 곡(아사달) · 지난 곡은 내려놓고 다음 곡을 미리 받음', b.fileOn && b.track === 'field2' && b.file.era === 2 && b.file.sec === 'a' && !b.file.cached.some((c) => c.startsWith('1:')), { era: b.file.era, cached: b.file.cached });
  d = await dummy(page, 'YAN_PIKE');
  a0 = (await r35(page)).snd; m0 = (await r35(page)).smp.by;
  await combo(page, 5);
  a1 = (await r35(page)).snd; m1 = (await r35(page)).smp.by;
  df = sndDiff(a0, a1);
  ok('B4 2시대 칼: 베는 소리(cut_light) + 마지막 타 강타(cut_heavy) · 바위 소리 없음', (df.cutLight1 || 0) + (df.cutLight2 || 0) + (df.cutLight3 || 0) >= 2 && (df.cutHeavy || 0) >= 1 && !Object.keys(df).some((k) => k.startsWith('rock')), df);
  ok('B5 휘두를 때 칼 바람(whoosh_blade)', (m1.whooshBlade || 0) - (m0.whooshBlade || 0) >= 3, { blade: m1.whooshBlade || 0 });
  // 양단 막타
  await dummy(page, 'YAN_PIKE', 1);
  a0 = (await r35(page)).snd;
  await combo(page, 2);
  a1 = (await r35(page)).snd;
  df = sndDiff(a0, a1);
  ok('B6 막타로 베어 넘기면 양단음(cut_sever)', (df.cutSever || 0) >= 1, df);
  // ── B. 3시대 방패병: 쇠 울림
  await toEra(page, 3); await sleep(1200); await calm(page);
  d = await dummy(page, 'TANG_SHIELD');
  a0 = (await r35(page)).snd;
  await combo(page, 3);
  a1 = (await r35(page)).snd;
  df = sndDiff(a0, a1);
  ok('B7 3시대 방패 · 갑옷 몹: 쇠 울림(cut_armor)', (df.cutArmor || 0) >= 1, { df, d });
  // ── D5. 4시대: 전장 → 보스전 구간 → 광폭화 빠르기
  await toEra(page, 4); await sleep(1500); await calm(page);
  b = (await r35(page)).bgm;
  const f4 = b.fileOn && b.file.era === 4 && b.file.sec === 'a';
  await ev(page, () => window.__RELIC_DEV.r33final());
  await page.waitForFunction(() => { const g = window.__RELIC; return g.boss && g.bossActive; }, null, { timeout: 20000 }).catch(() => null);
  await sleep(1500);
  const bb = (await r35(page)).bgm;
  // 보스 등장 연출이 끝난 뒤 보스 앞에 붙어 3번 휘두른다(보스가 움직이므로 휘두르기 직전마다 자리 맞춤)
  await page.waitForFunction(() => { const g = window.__RELIC, b2 = g.boss; return b2 && !(g.bossIntro > 0) && !(b2.phaseInv > 0) && b2.state === 'ACTIVE'; }, null, { timeout: 20000 }).catch(() => null);
  await sleep(600);
  a0 = (await r35(page)).snd;
  const hp0 = await ev(page, () => window.__RELIC.boss.hp);
  for (let i = 0; i < 3; i++) {
    // 시험에서는 보스 투기장까지 걸어가지 않았으므로 보스를 주인공 앞으로 데려온다(호위는 멀리)
    await ev(page, () => { const g = window.__RELIC, p = g.player, b2 = g.boss; b2.attackCooldown = 1e9; b2.charge = b2.chargePending = null; g.enemies.forEach((e) => { if (e !== b2) { e.x = p.x + 900; e.attackCooldown = 1e9; } }); b2.x = p.x + 70; b2.z = p.z; b2.y = 0; p.facing = 1; p.invincibleTimer = 99999; });
    await page.keyboard.down('j'); await sleep(40); await page.keyboard.up('j'); await sleep(330);
  }
  a1 = (await r35(page)).snd;
  df = sndDiff(a0, a1);
  const hpLost = await ev(page, (h) => Math.round(h - window.__RELIC.boss.hp), hp0);
  const geo = await ev(page, () => { const g = window.__RELIC, p = g.player, b2 = g.boss; return { dx: Math.round(b2.x - p.x), dz: Math.round(b2.z - p.z), bx: Math.round(b2.x - g.cameraX), intro: g.bossIntro, inv: b2.phaseInv || 0, st: b2.state }; });
  ok('B8 보스 타격: 베는 소리(cut_light · 조금 낮고 크게) — 예전처럼 매번 저음 강타음이 아님', hpLost > 0 && (df.cutLight1 || 0) + (df.cutLight2 || 0) + (df.cutLight3 || 0) >= 1 && !Object.keys(df).some((k) => k.startsWith('rock')), { df, hpLost, geo });
  await ev(page, () => { const b2 = window.__RELIC.boss; if (b2) b2.enraged = true; });
  await sleep(900);
  const be = (await r35(page)).bgm;
  ok('D5 4시대 전장 곡 → 최종 보스 등장 = 보스전 구간 → 광폭화 = 1.12배', f4 && bb.track === 'boss' && bb.file.era === 4 && bb.file.sec === 'b' && bb.file.rate === 1 && be.file.rate === 1.12 && be.file.sec === 'b', { field: f4, boss: [bb.track, bb.file.sec, bb.file.rate], enraged: be.file.rate, log: be.file.log.slice(-5) });
  await page.screenshot({ path: `${OUT}/e4_boss.png` });
  const fin = await r35(page);
  ok('E1 효과음 실패 0 · 음악 로드 실패 0 · 콘솔 에러 0', fin.smp.failed === 0 && fin.bgm.file.failed === 0 && errors.length === 0, { smp: [fin.smp.loaded, fin.smp.failed], bgm: [fin.bgm.file.loaded, fin.bgm.file.failed], errors: errors.slice(0, 3), by: fin.smp.by });
  await browser.close();
  // ── D6. ?bgm=synth → 예전 합성 BGM(비교 · 비상용)
  const o2 = await open(`http://127.0.0.1:${PORT}/index.html?bgm=synth`, { w: 1280, h: 720, dsf: 1 });
  await o2.page.keyboard.press('Enter');
  await o2.page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(2500);
  const bs = (await ev(o2.page, () => window.__RELIC_DEV.r35())).bgm;
  ok('D6 ?bgm=synth: mp3 없이 예전 합성 BGM으로 재생', bs && !bs.fileOn && !bs.file && bs.track === 'field1' && bs.notes > 0 && o2.errors.length === 0, bs ? { fileOn: bs.fileOn, file: !!bs.file, track: bs.track, notes: bs.notes } : null);
  await o2.browser.close();
  const pass = Object.values(R).filter(Boolean).length;
  console.log(`RESULT ${pass}/${Object.keys(R).length}`);
  fs.writeFileSync(`${OUT}/r35func.json`, JSON.stringify(R, null, 1));
})().catch((e) => { console.error('TEST CRASH', e); process.exit(1); });
