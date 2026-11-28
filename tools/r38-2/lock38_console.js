// [R38-2A] 입력 잠김 회귀 테스트 + 밸런스 · 로밍 확인(built-in 브라우저 콘솔용). 먼저 tools/r38/shim38_console.js(window.__R38S)를 붙여 넣는다.
//  http://127.0.0.1:8044/index.html 에서: await __R38K.all()  → { lock, ime, cycle, watchdog, balance, roam } 각 ok와 수치.
//  대기는 게임 틱 기준(창이 가려져도 같은 결과). 창 가시성 대기는 하지 않는다.
//  lock: 4시대 Lv.5에서 p.comboStep=4 + J로 질풍연참을 걸고 곧바로 L(어퍼) → 연참이 끝난 뒤(≤150틱) p.rush가 null이고 J에 공격이 나가야 한다(R38에서는 p.rush 고착).
//  ime: key "ㅓ" + code "KeyJ"(한글 모드 J)로 keydown → lastAtkPress가 갱신돼야 한다.
//  cycle: J 연타 · K · E · 일시정지(P) 전환 2회 · 방향 전환 뒤에도 J 응답 · 잠금 플래그 전부 해제.
//  watchdog: p.rush · attackTimer · special을 억지로 고착시켜 2틱 안에 풀리는지(r38lock 카운터).
//  balance: r382("KHITAN_INF") 표본 체력 · 공격 간격 · 상수 · 격파 목표(+21).  roam: Z1→Z2 걷기로 첫 지점을 넘으면 3명(roam 표식) 소환.
(() => {
  const H = window.__R38S;
  if (!H) throw new Error("shim38_console.js 를 먼저 붙여 넣으세요");
  const { sleep, key, press, G, D, waitFor, waitTicks, start, toEra } = H;
  const keyCode = (code, type) => document.dispatchEvent(new KeyboardEvent(type, { key: "ㅓ", code, keyCode: 74, which: 74, bubbles: true }));
  const scene = async () => {
    await start();
    await toEra(4);
    await waitTicks(60);
    const g = G();
    const p = g.player;
    g.enemies.length = 0;
    g.spawnQ = [];
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.x = g.cameraX + 360;
    p.z = 430;
    p.facing = 1;
    p.invincibleTimer = 99999;
    ["JURCHEN_INF", "REDTURBAN_ELITE", "JURCHEN_CAV"].forEach((u, i) => D().spawnUnit(u, p.x + 90 + i * 60, 400 + i * 20));
    g.enemies.forEach((e) => {
      e.state = "ACTIVE";
      e.hp = e.maxHp = 1e9;
      e.attackCooldown = 99999;
    });
    D().setLevel(5);
    g.stats.weaponTier = 3;
    await waitTicks(10);
    return { g, p };
  };
  const jResponds = async (p, g) => {
    const t0 = g.lastAtkPress;
    const c0 = p.comboStep;
    const a0 = p.attackTimer;
    await press("j", "KeyJ", 74, 20);
    await waitTicks(3);
    return { ok: g.lastAtkPress !== t0 && (p.attackTimer > a0 || p.comboStep !== c0 || p.attackTimer > 0), lastAtkPress: g.lastAtkPress, attackTimer: p.attackTimer, comboStep: p.comboStep };
  };
  const lock = async () => {
    const { g, p } = await scene();
    p.comboStep = 4;
    p.comboResetTimer = 50;
    p.attackTimer = 0;
    p.rush = null;
    p.plunge = false;
    g.special = null;
    const c0 = Object.assign({}, D().r38lock().counts);
    await press("j", "KeyJ", 74, 20);
    await waitTicks(2);
    const rushStarted = !!p.rush;
    await press("l", "KeyL", 76, 20);
    await waitTicks(2);
    const afterL = D().r38lock();
    const cleared = await waitFor(() => !p.rush, 6000);
    const ticksToClear = g.tick - (afterL.flags.tick || g.tick);
    await waitTicks(30);
    const j = await jResponds(p, g);
    const c1 = D().r38lock().counts;
    return { ok: rushStarted && cleared && j.ok, rushStarted, cleared, ticksToClear, upperRefused: (c1.upperDuringRush || 0) - (c0.upperDuringRush || 0), queueRefused: (c1.queueRefused || 0) - (c0.queueRefused || 0), watchdogRush: (c1.rush || 0) - (c0.rush || 0), j };
  };
  const ime = async () => {
    const { g, p } = await scene();
    const t0 = g.lastAtkPress;
    keyCode("KeyJ", "keydown");
    await sleep(20);
    keyCode("KeyJ", "keyup");
    await waitTicks(3);
    return { ok: g.lastAtkPress !== t0, lastAtkPress: g.lastAtkPress, before: t0, attackTimer: p.attackTimer };
  };
  const cycle = async () => {
    const { g, p } = await scene();
    for (let i = 0; i < 20; i++) {
      await press("j", "KeyJ", 74, 20);
      await sleep(60);
    }
    await press("k", "KeyK", 75, 20);
    await waitTicks(20);
    await press("e", "KeyE", 69, 20);
    await waitTicks(30);
    for (let i = 0; i < 2; i++) {
      await press("p", "KeyP", 80, 20);
      await sleep(300);
      await press("p", "KeyP", 80, 20);
      await sleep(300);
    }
    key("ArrowLeft", "ArrowLeft", 37, "keydown");
    await waitTicks(20);
    key("ArrowLeft", "ArrowLeft", 37, "keyup");
    key("ArrowRight", "ArrowRight", 39, "keydown");
    await waitTicks(20);
    key("ArrowRight", "ArrowRight", 39, "keyup");
    await waitFor(() => p.attackTimer <= 0 && !p.rush, 5000);
    await waitTicks(10);
    const j = await jResponds(p, g);
    const f = D().r38lock().flags;
    const clean = !f.rush && !f.plunge && !f.special && !f.grab && f.guardTimer <= 0 && f.attackTimer < 60;
    return { ok: j.ok && clean, j, flags: f, counts: D().r38lock().counts };
  };
  const watchdog = async () => {
    const { g, p } = await scene();
    const c0 = Object.assign({}, D().r38lock().counts);
    p.rush = { k: 1, t0: g.tick - 999 };
    await waitTicks(3);
    const rushCleared = !p.rush;
    p.maxAttackTimer = 20;
    p.attackTimer = 999;
    await waitTicks(3);
    const atkCleared = p.attackTimer <= 20;
    g.special = { tick0: g.tick - 999, targets: [], path: [] };
    await waitTicks(3);
    const specialCleared = !g.special;
    const c1 = D().r38lock().counts;
    return { ok: rushCleared && atkCleared && specialCleared, rushCleared, atkCleared, specialCleared, counts: { rush: (c1.rush || 0) - (c0.rush || 0), attack: (c1.attack || 0) - (c0.attack || 0), special: (c1.special || 0) - (c0.special || 0) } };
  };
  const balance = async () => {
    const { g } = await scene();
    const r = D().r382("KHITAN_INF");
    const r2 = D().r382("JURCHEN_INF");
    const okCd = r.sample && r.sample.attackCooldown <= Math.round(75 * r.mobCdK) + 1 && r.sample.attackCooldown >= Math.round(46 * r.mobCdK) - 1;
    return { ok: !!r.sample && r.hpK.mob === 2.2 && r.hpK.mid === 1.5 && r.hpK.boss === 1.35 && okCd && r.cap[3] === 7 && r.cap[6] === 7, hpK: r.hpK, mobCdK: r.mobCdK, midCd: r.midCd, cap: r.cap, killGoalEra4: r.killGoal, khitan: r.sample, jurchen: r2.sample };
  };
  const roam = async () => {
    const { g, p } = await scene();
    g.enemies.length = 0;
    g.zoneIdx = 1;
    g.zoneState = "GO";
    g.r38roam = {};
    g.r38roamLog = [];
    const r = D().r38();
    const x0 = r.zoneCam[0] + r.span;
    const x1 = r.zoneTrig[1];
    const px = x0 + (x1 - x0) * 0.35;
    p.x = px - 30;
    await waitTicks(30);
    const before = g.enemies.length;
    p.x = px + 10;
    await waitTicks(1);
    // 소환 직후(1틱)에 잰다 — 적은 바로 걸어 들어오고 카메라도 따라가므로 늦게 재면 '화면 밖' 판정이 흐려진다
    const spawned = g.enemies.filter((e) => e.roam);
    const log = (g.r38roamLog || []).slice();
    const xs = spawned.map((e) => Math.round(e.x));
    const cam = Math.round(g.cameraX);
    const outside = xs.filter((x) => x < cam - 20 || x > cam + 960 + 20).length;
    g.enemies.length = 0;
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.x = 400;
    return { ok: before === 0 && spawned.length === 3 && outside === 3 && log.length === 1, px: Math.round(px), xs, cam, outside, log };
  };
  const all = async () => {
    const out = {};
    for (const [k, fn] of [["lock", lock], ["ime", ime], ["cycle", cycle], ["watchdog", watchdog], ["balance", balance], ["roam", roam]]) {
      try {
        out[k] = await fn();
      } catch (e) {
        out[k] = { ok: false, error: String(e) };
      }
    }
    out.allOk = Object.values(out).every((v) => v && v.ok);
    console.log("[R38-2A LOCK] " + JSON.stringify(out));
    return out;
  };
  window.__R38K = { lock, ime, cycle, watchdog, balance, roam, all };
  return "R38K ready";
})();
