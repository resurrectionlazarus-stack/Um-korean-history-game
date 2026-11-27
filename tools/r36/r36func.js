// R36 기능 테스트 1회(콘솔 에러 0) — ① 둔기 타격음 = thud_*(rock_* 안 씀) ② 몹의 목소리(웨이브 울음 · 공격 예고 · 쓰러질 때 · 기척 · 곰/호랑이 포효 · 병사 함성)
//  ③ 갈래 기술(마무리 돌림 · ▲ 올려치기 → 공중 추격 · ▼ 내려찍기 + 기절 · 잠금 · 2시대 곰의 내려찍기 · 안내 문구)
// 사용: node tools/r36/r36func.js <출력 폴더> [포트=8039]
const { open, toEra } = require('./h');
const fs = require('fs');
const OUT = process.argv[2];
const PORT = process.argv[3] || 8039;
fs.mkdirSync(OUT, { recursive: true });
const R = {};
const ok = (k, v, info) => { R[k] = !!v; console.log((v ? 'PASS ' : 'FAIL ') + k, info !== undefined ? JSON.stringify(info) : ''); };
const ev = (page, f, a) => page.evaluate(f, a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const r35 = (page) => ev(page, () => window.__RELIC_DEV.r35());
const r36 = (page) => ev(page, () => window.__RELIC_DEV.r36());
// 주인공은 첫 구역 발동 지점(x 700) 앞 x 400에 붙잡아 둔다 — 관통 돌진으로 앞으로 나가다 구역 전투 · 중간 퀴즈가 열리면 그동안의 입력이 무시돼 시험이 흐트러진다(2회차 실패 원인)
const calm = (page) => ev(page, () => { const g = window.__RELIC, p = g.player; g.enemies.length = 0; g.zoneState = 'ROAM'; g.waves = []; g.paleoWaves = null; g.spawnQ = []; p.invincibleTimer = 99999; p.x = g.__baseX = 400; p.vx = 0; p.z = 440; p.y = 0; p.vy = 0; p.facing = 1; p.comboStep = 0; p.comboResetTimer = 0; p._brLock = false; p._chaseUntil = 0; p.bufferAtk = false; });
// 맞아 줄 적 하나를 주인공 앞에 세운다(체력 크게 · 공격 안 함). kind: 'bear'(중간보스 곰) · 'role:WOLF'(1시대 짐승) · 병종 이름
const dummy = (page, kind, hp = 1e9) => ev(page, ([kind, hp]) => {
  const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV;
  g.enemies.length = 0;
  let en = null;
  if (kind === 'bear') en = D.spawnBear();
  else if (kind.startsWith('role:')) { D.spawnRole(kind.slice(5), p.x + 74, p.z); en = g.enemies[g.enemies.length - 1]; }
  else { D.spawnUnit(kind, p.x + 74, p.z); en = g.enemies[g.enemies.length - 1]; }
  if (!en) return null;
  en.x = p.x + 74; en.z = p.z; en.y = 0; en.hp = en.maxHp = hp; en.state = 'ACTIVE'; en.stateTimer = 0; en.attackCooldown = 1e9; en.spawnTimer = 0; en.vx = en.vz = 0; en.speed = 0; en.guardCd = 1e9;
  g.__dummy = en;
  return { role: en.mobRole || null, unit: en.unit || null, mid: !!en.isMidBoss };
}, [kind, hp]);
const pin = (page) => ev(page, () => { const g = window.__RELIC, p = g.player, en = g.__dummy; if (g.__baseX && p.y === 0) { p.x = g.__baseX; p.facing = 1; } if (en && en.state !== 'DYING') { en.x = p.x + 74 * p.facing; en.z = p.z; en.y = 0; en.vx = en.vy = 0; en.attackCooldown = 1e9; en.guardCd = 1e9; en.guardTimer = 0; if (en.hitStun > 4) en.hitStun = 4; } p.invincibleTimer = 99999; });
const tap = async (page, key = 'j') => { await page.keyboard.down(key); await sleep(40); await page.keyboard.up(key); };
const combo = async (page, n, gap = 420) => { for (let i = 0; i < n; i++) { await pin(page); await tap(page); await sleep(gap); } await sleep(350); };
// 레벨을 고정한 채 연타(시험 도중 경험치로 레벨이 올라 '마무리 → 질풍연참'이 끼어들면 돌림 확인이 길어진다)
const comboLv = async (page, n, lv, gap = 420) => { for (let i = 0; i < n; i++) { await ev(page, (lv) => { window.__RELIC.stats.level = lv; }, lv); await pin(page); await tap(page); await sleep(gap); } await sleep(350); };
const diff = (a, b) => { const o = {}; for (const k of Object.keys(b)) if ((b[k] || 0) - (a[k] || 0) > 0) o[k] = b[k] - (a[k] || 0); return o; };
const resetCombo = (page) => ev(page, () => { const p = window.__RELIC.player; p.comboStep = 0; p.comboResetTimer = 0; p._brLock = false; p._finRot = null; p._chaseUntil = 0; p.attackTimer = 0; p.pendingHit = null; p.bufferAtk = false; });

(async () => {
  const { browser, page, errors } = await open(`http://127.0.0.1:${PORT}/index.html`, { w: 1280, h: 720, dsf: 1 });
  // ── E0. 시작 화면 안내 문구
  const t0 = await ev(page, () => document.body.innerText);
  ok('E0 시작 화면 조작 안내에 갈래 기술 한 줄', t0.includes('연타 중 ▲ + 공격 = 올려치기') && t0.includes('▼ + 공격 = 내려찍기'), t0.split('\n').filter((l) => l.includes('올려치기')).map((l) => l.slice(0, 80)));
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => window.__RELIC_DEV.assets.status(1) === 'ready', null, { timeout: 60000 });
  await sleep(1500);
  await ev(page, () => window.__RELIC_DEV.r31autoQuiz(true));
  // ── A. 목록 · 샘플 로드
  const man = await ev(page, async () => { const m = await (await fetch('assets/MANIFEST.json')).json(); const k = Object.keys(m.files); return { n: k.length, r36: k.filter((x) => m.files[x].r36).length, block: m.r36 ? m.r36.addedSfx : null }; });
  ok('A0 MANIFEST 455항목 · R36 표식 15(둔기 4 · 동물 10 · 함성 1)', man.n === 455 && man.r36 === 15 && man.block === 15, man);
  await page.waitForFunction(() => { const s = window.__RELIC_DEV.sfxStats(); return s && s.loaded + s.failed >= 41; }, null, { timeout: 15000 }).catch(() => null);
  const s0 = await ev(page, () => window.__RELIC_DEV.sfxStats());
  ok('A1 효과음 41종 로드(R35 30 − rock 4 + thud 4 + 동물 · 함성 11) · 실패 0', s0.loaded === 41 && s0.failed === 0, [s0.loaded, s0.failed]);

  // ── B. 둔기 = thud_*
  await calm(page);
  await dummy(page, 'bear');
  let a0 = (await r35(page)).snd;
  await ev(page, () => { window.__RELIC.stats.weaponTier = 1; });
  await combo(page, 5);
  let a1 = (await r35(page)).snd;
  let df = diff(a0, a1);
  const by1 = (await r35(page)).smp.by;
  ok("B1 1시대 둔기: '퍽'(thud_hit 1 · 2 번갈아 + 강타 thud_heavy/crush) · rock_* · 칼 소리 없음", (df.thudHit1 || 0) >= 1 && (df.thudHit2 || 0) >= 1 && (df.thudHeavy || 0) + (df.thudCrush || 0) >= 1 && !Object.keys(df).some((k) => k.startsWith('rock') || k.startsWith('cut')), df);
  ok('B2 실제 재생된 샘플에도 thud_* 만(rock_* 재생 0)', (by1.thudHit1 || 0) + (by1.thudHit2 || 0) >= 2 && !Object.keys(by1).some((k) => k.startsWith('rock')), Object.fromEntries(Object.entries(by1).filter(([k]) => /thud|rock/.test(k))));

  // ── D. 갈래 기술(1시대 사냥꾼 · Lv.1 = 3타 사슬): 마무리 돌림 = 기존 → 관통 돌진
  await calm(page); await resetCombo(page);
  await dummy(page, 'bear');
  let b0 = (await r36(page)).branch;
  const lv0 = await ev(page, () => window.__RELIC.stats.level);
  await ev(page, () => { const g = window.__RELIC; g.r36fin = 0; g.r36dirUsed = 0; g.r36hint = false; });
  await combo(page, 12);
  let b1 = await r36(page);
  df = diff(b0, b1.branch);
  ok('D1 Lv.1~2 마무리 돌림: 기존 3타 ↔ 관통 돌진이 번갈아', lv0 < 3 && (df.classic || 0) >= 1 && (df.lunge || 0) >= 1 && !df.slam, { lv: lv0, df, fin: b1.fin });
  ok('D2 세 번째 마무리쯤 선녀가 방향 갈래를 한 번 알려 줌', b1.hint === true, { hint: b1.hint, fin: b1.fin, dirUsed: b1.dirUsed });

  // Lv.3(4타 사슬): 기존 → 내려찍기 → 관통 돌진
  await ev(page, () => window.__RELIC_DEV.setLevel(3));
  await sleep(4500);
  await calm(page); await resetCombo(page);
  await dummy(page, 'bear');
  b0 = (await r36(page)).branch;
  a0 = (await r35(page)).snd;
  await comboLv(page, 13, 3);
  b1 = await r36(page);
  df = diff(b0, b1.branch);
  ok('D3 Lv.3 마무리 돌림: 기존(회전참) → 내려찍기 → 관통 돌진', (df.classic || 0) >= 1 && (df.slam || 0) >= 1 && (df.lunge || 0) >= 1, { df, lv: await ev(page, () => window.__RELIC.stats.level) });
  // Lv.4: 갈래 기술도 마무리 취급 — 뒤이어 공격 = 질풍연참(기존 연결 그대로)
  await calm(page); await resetCombo(page);
  await dummy(page, 'bear');
  await ev(page, () => { window.__RELIC.stats.level = 4; });
  let rushSeen = false;
  for (let i = 0; i < 6 && !rushSeen; i++) { await pin(page); await tap(page); for (let k = 0; k < 14; k++) { await sleep(30); if (await ev(page, () => !!window.__RELIC.player.rush)) { rushSeen = true; break; } } }
  ok('D3b Lv.4: 마무리(갈래 포함) 뒤 공격 = 질풍연참 연결 그대로', rushSeen, { rushSeen });
  await page.waitForFunction(() => !window.__RELIC.player.rush, null, { timeout: 6000 }).catch(() => null);
  await sleep(600);

  // ▲ + 공격 = 올려치기 → 공격 = 공중 추격
  await calm(page); await resetCombo(page);
  await dummy(page, 'role:WOLF');
  b0 = (await r36(page)).branch;
  await pin(page); await tap(page); await sleep(400);
  await pin(page);
  await page.keyboard.down('w'); await sleep(30);
  await tap(page);
  await sleep(40); await page.keyboard.up('w');
  let maxY = 0, chaseArmed = false;
  for (let i = 0; i < 14; i++) { await sleep(22); const s = await ev(page, () => { const g = window.__RELIC; return { y: g.__dummy ? g.__dummy.y : 0, armed: g.player._chaseUntil > g.tick }; }); maxY = Math.max(maxY, s.y); chaseArmed = chaseArmed || s.armed; if (s.armed && s.y > 40) break; }
  b1 = await r36(page);
  ok('D4 연타 중 ▲ + 공격 = 올려치기(적이 떠오름 · 추격 대기 켜짐)', (b1.branch.launch || 0) - (b0.launch || 0) === 1 && maxY > 40 && chaseArmed, { launch: (b1.branch.launch || 0) - (b0.launch || 0), dummyY: +maxY.toFixed(0), chaseArmed, dirUsed: b1.dirUsed });
  await tap(page);
  let heroY = 0, air = 0; maxY = 0;
  for (let i = 0; i < 22; i++) { await sleep(25); const s = await ev(page, () => { const g = window.__RELIC, p = g.player; return { hy: p.y, air: p.airHits || 0, ey: g.__dummy ? g.__dummy.y : 0 }; }); heroY = Math.max(heroY, s.hy); air = Math.max(air, s.air); maxY = Math.max(maxY, s.ey); }
  b1 = await r36(page);
  ok('D5 띄운 뒤 공격 = 공중 추격(주인공이 뛰어오름 · 첫 공중 베기 자동 · 적은 100px 넘게 뜸)', (b1.branch.chase || 0) - (b0.chase || 0) === 1 && heroY > 60 && air >= 1 && maxY > 100, { chase: (b1.branch.chase || 0) - (b0.chase || 0), heroY: +heroY.toFixed(0), airHits: air, dummyMaxY: +maxY.toFixed(0) });
  // 공중 연타 → 내리꽂기까지 눌러 보고 착지 확인
  for (let i = 0; i < 4; i++) { await tap(page); await sleep(200); }
  await page.waitForFunction(() => window.__RELIC.player.y === 0, null, { timeout: 4000 }).catch(() => null);
  ok('D6 공중 연타 뒤 착지(공중 경로 끝까지 오류 없음)', (await ev(page, () => window.__RELIC.player.y)) === 0, { y: await ev(page, () => window.__RELIC.player.y) });
  await sleep(700);

  // ▼ + 공격 = 내려찍기(둘레 충격 · 기절) + 잠금(연달아 안 나감)
  await calm(page); await resetCombo(page);
  await dummy(page, 'role:WOLF');
  b0 = (await r36(page)).branch;
  await pin(page); await tap(page); await sleep(400);
  await pin(page);
  await page.keyboard.down('s'); await sleep(30);
  await tap(page);
  let stun = 0;
  for (let i = 0; i < 16; i++) { await sleep(25); stun = Math.max(stun, await ev(page, () => window.__RELIC.__dummy ? window.__RELIC.__dummy.hitStun || 0 : 0)); }
  const mid = (await r36(page)).branch;
  // ▼를 누른 채 곧바로 한 번 더 — 잠금 때문에 내려찍기가 연달아 나가면 안 된다
  await sleep(200); await tap(page); await sleep(380);
  await page.keyboard.up('s');
  b1 = await r36(page);
  ok('D7 연타 중 ▼ + 공격 = 내려찍기(휘말린 적 기절 30틱 이상)', (mid.slam || 0) - (b0.slam || 0) === 1 && stun >= 30, { slam: (mid.slam || 0) - (b0.slam || 0), stun });
  ok('D8 갈래 기술 잠금: ▼를 누른 채 바로 또 눌러도 연달아 안 나감(보통 공격을 한 번 거쳐야 함)', (b1.branch.slam || 0) === (mid.slam || 0), { slamAfter: (b1.branch.slam || 0) - (b0.slam || 0) });
  await page.screenshot({ path: `${OUT}/r36-era1-branches.png` });

  // ── C. 몹의 목소리(1시대)
  await calm(page); await resetCombo(page);
  let v0 = (await r36(page)).voice;
  // 시험 도중 자연 발생한 웨이브가 방금 울었을 수 있으므로 소리별 최소 간격 기록을 비우고 시작
  await ev(page, () => { const g = window.__RELIC; g._r36v = {}; g.zoneState = 'LOCKED'; g.paleoWaves = [['WOLF', 'WOLF', 'BEAR']]; g.waves = [3]; g.waveSpawnCd = 2; });
  await sleep(900);
  let v1 = (await r36(page)).voice;
  df = diff(v0, v1);
  const wave1 = await ev(page, () => window.__RELIC.enemies.map((e) => e.mobRole));
  ok('C1 웨이브 등장: 그 무리의 울음(늑대 하울링 + 곰 포효) — 예전 경보음 대신', (df.wolfHowl || 0) === 1 && (df.bearRoar || 0) === 1, { df, wave: wave1 });
  await page.waitForFunction((v) => { const x = window.__RELIC_DEV.r36().voice; return (x.wolfSnarl || 0) + (x.bearGrowl || 0) > (v.wolfSnarl || 0) + (v.bearGrowl || 0); }, v1, { timeout: 12000 }).catch(() => null);
  let v2 = (await r36(page)).voice;
  df = diff(v1, v2);
  ok('C2 덮치기 직전의 으르렁(공격 예고)', (df.wolfSnarl || 0) + (df.bearGrowl || 0) >= 1, df);
  await ev(page, () => { window.__RELIC.enemies.forEach((e) => { e.hp = 0; }); });
  await sleep(500);
  let v3 = (await r36(page)).voice;
  df = diff(v2, v3);
  ok('C3 쓰러질 때: 늑대 깨갱 + 곰의 낮은 신음', (df.wolfYelp || 0) >= 1 && (df.beastGroan || 0) >= 1, df);
  await calm(page);
  await ev(page, () => { const g = window.__RELIC, p = g.player, D = window.__RELIC_DEV; D.spawnRole('RHINO', p.x + 300, p.z); D.spawnRole('HYENA', p.x + 340, p.z - 30); g.enemies.forEach((e) => { e.attackCooldown = 1e9; e.speed = 0; e.state = 'ACTIVE'; }); g._r36idle = 2; });
  await sleep(300);
  let v4 = (await r36(page)).voice;
  df = diff(v3, v4);
  ok('C4 기척: 살아 있는 짐승이 가끔 낮게 운다(코뿔소 콧김 또는 하이에나 웃음)', (df.rhinoSnort || 0) + (df.hyenaCackle || 0) === 1, df);
  await calm(page);
  await ev(page, () => window.__RELIC_DEV.spawnBear());
  await sleep(300);
  let v5 = (await r36(page)).voice;
  df = diff(v4, v5);
  ok('C5 중간보스 동굴 곰 등장 = 곰 포효', (df.bearRoar || 0) === 1, df);
  await calm(page);
  await ev(page, () => window.__RELIC_DEV.r33final());
  await sleep(1800);
  let v6 = (await r36(page)).voice;
  df = diff(v5, v6);
  const by2 = (await r35(page)).smp.by;
  ok('C6 1시대 보스 산군 등장 = 호랑이 포효(실제 샘플 재생)', (df.tigerRoar || 0) >= 1 && (by2.tigerRoar || 0) >= 1, { df, played: Object.fromEntries(Object.entries(by2).filter(([k]) => /wolf|bear|tiger|rhino|hyena|beast|warCry/.test(k))) });
  await page.screenshot({ path: `${OUT}/r36-era1-boss.png` });

  // ── 2시대: 병사 함성 · 해모수 내려찍기(곰의 내려찍기 자세 · 이펙트) · 돌림 = 기존 → 관통 돌진 → 올려치기
  await toEra(page, 2); await sleep(1500); await calm(page); await resetCombo(page);
  v0 = (await r36(page)).voice;
  await ev(page, () => { const g = window.__RELIC; g._r36v = {}; g.zoneState = 'LOCKED'; g.waves = [3]; g.waveSpawnCd = 2; });
  await sleep(900);
  v1 = (await r36(page)).voice;
  df = diff(v0, v1);
  ok('C7 2시대 웨이브 등장 = 병사들의 함성', (df.warCry || 0) === 1 && !df.wolfHowl, { df, n: await ev(page, () => window.__RELIC.enemies.length) });
  await calm(page); await resetCombo(page);
  await ev(page, () => { window.__RELIC.stats.level = 3; });
  const lv2 = 3;
  await dummy(page, 'YAN_PIKE');
  b0 = (await r36(page)).branch;
  const e2s0 = await ev(page, () => window.__RELIC.e2Slams || 0);
  await pin(page); await tap(page); await sleep(400);
  await pin(page);
  await page.keyboard.down('s'); await sleep(30); await tap(page);
  await sleep(60);
  const pose = await ev(page, () => { const p = window.__RELIC.player; return { slam: !!p._r31slam, src: p._atkSrc, step: p.comboStep }; });
  await sleep(420); await page.keyboard.up('s');
  b1 = await r36(page);
  const e2s1 = await ev(page, () => window.__RELIC.e2Slams || 0);
  ok('D9 2시대 ▼ + 공격 = 곰의 내려찍기(기존 slam 자세 · 곰 · 천둥 원화 이펙트)', (b1.branch.slam || 0) - (b0.slam || 0) === 1 && e2s1 - e2s0 === 1 && (lv2 < 3 || pose.slam), { lv: lv2, pose, e2Slams: e2s1 - e2s0 });
  await calm(page); await resetCombo(page);
  await dummy(page, 'YAN_PIKE');
  b0 = (await r36(page)).branch;
  await comboLv(page, 13, 3, 440);
  b1 = await r36(page);
  df = diff(b0, b1.branch);
  ok('D10 2시대 마무리 돌림(Lv.3): 기존(곰의 내려찍기) → 관통 돌진 → 올려치기', (df.classic || 0) >= 1 && (df.lunge || 0) >= 1 && (df.launch || 0) >= 1, { df });
  await page.screenshot({ path: `${OUT}/r36-era2.png` });
  // ── E1. 일시정지 화면 조작표
  await sleep(1200);
  await page.keyboard.press('p'); await sleep(600);
  const t1 = await ev(page, () => document.body.innerText);
  ok('E1 일시정지 화면 조작표에 갈래 기술 줄', t1.includes('갈래 기술') && t1.includes('올려치기'), t1.split('\n').filter((l) => l.includes('갈래') || l.includes('올려치기')).map((l) => l.slice(0, 60)));
  await page.keyboard.press('p'); await sleep(400);

  ok('Z 콘솔 에러 0', errors.length === 0, errors.slice(0, 6));
  const fails = Object.keys(R).filter((k) => !R[k]);
  console.log(`\n${Object.keys(R).length - fails.length}/${Object.keys(R).length} PASS` + (fails.length ? ' — FAIL: ' + fails.join(' | ') : ''));
  await browser.close();
  process.exit(fails.length ? 1 : 0);
})();
