// [R38-2B] 주인공 동작 확장 · 1.5배 구간 서사 회귀 테스트(built-in 브라우저 콘솔용). 먼저 tools/r38/shim38_console.js(window.__R38S)를 붙여 넣는다.
//  http://127.0.0.1:8045/index.html 에서: await __R38B.all()  → { branch1, branch3, branch5, flair, rushVar, story, frames } 각 ok와 수치.
//  대기는 게임 틱 기준. 창 가시성 대기는 하지 않는다.
//  branch{era}: 1타 뒤 ▶ 탭(자동 반복 아님) + J → 진격 베기(advance) · 1타 뒤 ◀ 탭 + J → 회피 베기(retreat · facing 유지 · vx 음수 · 무적 ≤ 8) · 둘 다 뒤 J 응답 · r38lock 복구 카운터 증가 0.
//  flair: Lv.5 4타 → 플러리시 카운터 · 잔심 6틱 뒤 해제 · J 응답.  rushVar: 연참 변주 카운터 · 연참 종료 · J 응답.
//  story: 2시대 Z1→Z2 첫 지점 → 경고(주인공) → 30틱 뒤 해설(단비) · 같은 지점 재통과 0건 · 3시대로 넘어가면 다시 발동 · 말풍선 중 J 응답 · 틱 진행(일시정지 아님).
//  frames: 갈래 · 플러리시 중 p._assetFrame이 null인 틱 0(없는 스프라이트 요청 없음).
(() => {
  const H = window.__R38S;
  if (!H) throw new Error("shim38_console.js 를 먼저 붙여 넣으세요");
  const { sleep, key, press, G, D, waitFor, waitTicks, start, toEra } = H;
  const scene = async (era) => {
    await start();
    await toEra(era);
    await waitTicks(40);
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
    p.rush = null;
    p.plunge = false;
    g.special = null;
    // 적은 그 시대 로스터에서(spawnUnit(undefined) = pickRosterUnit) · 1시대는 늑대 역할. 없는 unit 이름을 주면 HUD 이름표가 UNIT_SPECS[unit].name에서 터진다(첫 판의 "HAN_SPEAR" 콘솔 에러 원인)
    for (let i = 0; i < 2; i++) {
      if (era === 1) D().spawnRole("WOLF", p.x + 90 + i * 50, 420 + i * 10);
      else D().spawnUnit(void 0, p.x + 90 + i * 50, 420 + i * 10);
    }
    g.enemies.forEach((e) => {
      e.state = "ACTIVE";
      e.hp = e.maxHp = 1e9;
      e.attackCooldown = 99999;
      e.speed = 0;
      e.hitStun = 200;
      e.windupTimer = 0;
    });
    D().setLevel(5);
    g.stats.weaponTier = 3;
    await waitTicks(10);
    return { g, p };
  };
  const jResponds = async (p, g) => {
    const t0 = g.lastAtkPress;
    await press("j", "KeyJ", 74, 20);
    await waitTicks(3);
    return { ok: g.lastAtkPress !== t0 && p.attackTimer > 0, attackTimer: p.attackTimer, comboStep: p.comboStep };
  };
  const tapDir = (dir) => {
    const k = dir > 0 ? ["ArrowRight", "ArrowRight", 39] : ["ArrowLeft", "ArrowLeft", 37];
    key(k[0], k[1], k[2], "keydown");
    return () => key(k[0], k[1], k[2], "keyup");
  };
  const branch = async (era) => {
    const { g, p } = await scene(era);
    const c0 = Object.assign({}, D().r38lock().counts);
    const b0 = Object.assign({}, D().r38b().branch);
    let nullFrames = 0;
    let frames = 0;
    const sample = async (ticks) => {
      const t0 = g.tick;
      while (g.tick - t0 < ticks) {
        await sleep(8);
        if (p.attackTimer > 0 && g.tick !== sample.last) {
          sample.last = g.tick;
          frames++;
          if (!p._assetFrame) nullFrames++;
        }
      }
    };
    // 갈래마다 사슬을 1타부터 다시(comboStep 4에서 J는 질풍연참이 먼저다)
    const fresh = async () => {
      await waitFor(() => p.attackTimer <= 0 && !p.rush, 3000);
      p.comboStep = 0;
      p.comboResetTimer = 0;
      p._brLock = false;
      p.facing = 1;
      p.rush = null;
      g.enemies.forEach((e) => {
        e.hp = e.maxHp = 1e9;
        e.hitStun = 0;
      });
      await waitTicks(2);
    };
    // 진격 베기: 1타 → 16틱 → ▶ 탭 + J
    await fresh();
    await press("j", "KeyJ", 74, 20);
    await waitTicks(16);
    let up = tapDir(1);
    await waitTicks(1);
    await press("j", "KeyJ", 74, 20);
    await waitTicks(2);
    const advVx = p.vx;
    const advFacing = p.facing;
    const advAnim = p.atkAnim;
    const advStep = p.comboStep;
    await sample(14);
    up();
    await waitFor(() => p.attackTimer <= 0, 3000);
    await waitTicks(4);
    const j1 = await jResponds(p, g);
    const chainAfterAdv = p.comboStep;
    // 회피 베기: 1타 → 16틱 → ◀ 탭 + J (vx 음수 · 무적 ≤ 8 · 적중 순간 공격하던 쪽을 보고 베므로 오른쪽 적이 맞는다)
    await fresh();
    p.invincibleTimer = 0;
    await press("j", "KeyJ", 74, 20);
    await waitTicks(16);
    g.enemies.forEach((e) => {
      e.hp = e.maxHp = 1e9;
    });
    up = tapDir(-1);
    await waitTicks(1);
    await press("j", "KeyJ", 74, 20);
    await waitTicks(1);
    const retVx = p.vx;
    const retInv = p.invincibleTimer;
    const retAnim = p.atkAnim;
    const retRush = !!p.rush;
    await sample(12);
    up();
    p.invincibleTimer = 99999;
    await waitFor(() => p.attackTimer <= 0, 3000);
    const retHit = g.enemies.filter((e) => e.hp < 1e9).length;
    await waitTicks(4);
    const j2 = await jResponds(p, g);
    await waitFor(() => p.attackTimer <= 0, 3000);
    const b1 = D().r38b().branch;
    const c1 = D().r38lock().counts;
    const f = D().r38lock().flags;
    const recov = ["rush", "plunge", "special", "attack", "pending", "guard", "grab", "buffer", "brLock", "pose"].reduce((a, k) => a + ((c1[k] || 0) - (c0[k] || 0)), 0);
    const adv = (b1.advance || 0) - (b0.advance || 0);
    const ret = (b1.retreat || 0) - (b0.retreat || 0);
    const ok = adv === 1 && ret === 1 && advVx > 0 && advFacing === 1 && advAnim === "atk2" && chainAfterAdv === advStep + 1 && retVx < 0 && retInv > 0 && retInv <= 8 && retAnim === "atk1" && !retRush && retHit >= 1 && j1.ok && j2.ok && recov === 0 && !f.brLock && nullFrames === 0;
    return { ok, era, adv, ret, advVx: +advVx.toFixed(1), advFacing, advAnim, advStep, chainAfterAdv, retVx: +retVx.toFixed(1), retInv, retAnim, retRush, retHit, j1, j2, recov, brLock: f.brLock, frames, nullFrames };
  };
  const flair = async () => {
    const { g, p } = await scene(5);
    const f0 = D().r38b().flair;
    for (let i = 0; i < 4; i++) {
      await press("j", "KeyJ", 74, 20);
      await waitTicks(18);
    }
    await waitTicks(3);
    const poseHeld = D().r38lock().flags.pose;
    await waitTicks(12);
    const poseGone = !D().r38lock().flags.pose;
    await waitFor(() => p.attackTimer <= 0 && !p._r31pose, 3000);
    await waitTicks(4);
    const j = await jResponds(p, g);
    const f1 = D().r38b().flair;
    return { ok: f1 - f0 >= 1 && poseGone && j.ok, flairs: f1 - f0, poseHeld, poseGone, j };
  };
  const rushVar = async () => {
    const { g, p } = await scene(3);
    const r0 = D().r38b().rushVar;
    p.comboStep = 4;
    p.comboResetTimer = 50;
    p.attackTimer = 0;
    await press("j", "KeyJ", 74, 20);
    await waitTicks(2);
    const started = !!p.rush;
    const ended = await waitFor(() => !p.rush, 6000);
    await waitTicks(30);
    const j = await jResponds(p, g);
    const r1 = D().r38b().rushVar;
    return { ok: started && ended && r1 - r0 >= 3 && j.ok, started, ended, rushVar: r1 - r0, j };
  };
  const story = async () => {
    const { g, p } = await scene(2);
    g.enemies.length = 0;
    g.zoneIdx = 1;
    g.zoneState = "GO";
    g.r38roam = {};
    g.r38roamLog = [];
    g.r38story = { log: [] };
    g.player.bubbleTimer = 0;
    g.companion.bubbleTimer = 0;
    const r = D().r38();
    const x0 = r.zoneCam[0] + r.span;
    const x1 = r.zoneTrig[1];
    const px = x0 + (x1 - x0) * 0.35;
    p.x = px - 30;
    await waitTicks(20);
    p.x = px + 10;
    await waitTicks(2);
    const s1 = D().r38story();
    const warnShown = s1.player.timer > 0 && /⚠/.test(s1.player.text || "");
    const t1 = g.tick;
    await waitTicks(34);
    const s2 = D().r38story();
    const tickMoved = g.tick - t1 >= 30;
    const expl = s2.comp.timer > 0 && s2.comp.text === s2.last.text && !!s2.last.text && s2.last.era === 2 && s2.last.zone === 1 && s2.last.k === 0;
    const j = await jResponds(p, g);
    // 같은 지점 재통과 → 발동 0
    p.x = px - 30;
    await waitTicks(5);
    p.x = px + 10;
    await waitTicks(5);
    const logAfterRepass = D().r38story().log.length;
    // 3시대로 넘어가면 같은 지점이 다시 발동(시대별 키)
    g.enemies.length = 0;
    await toEra(3);
    await waitTicks(30);
    g.enemies.length = 0;
    g.zoneIdx = 1;
    g.zoneState = "GO";
    p.invincibleTimer = 99999;
    p.x = px - 30;
    await waitTicks(10);
    p.x = px + 10;
    await waitTicks(2);
    const s3 = D().r38story();
    const eraAgain = s3.log.length === 2 && s3.last.era === 3 && !!s3.last.text;
    g.enemies.length = 0;
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.x = 400;
    return { ok: warnShown && tickMoved && expl && j.ok && logAfterRepass === 1 && eraAgain, warn: s1.player.text, text: s2.last && s2.last.text, compTimer: s2.comp.timer, tickMoved, j, logAfterRepass, eraAgain, texts: s3.texts };
  };
  const all = async () => {
    const out = {};
    for (const [k, fn] of [["branch1", () => branch(1)], ["branch3", () => branch(3)], ["branch5", () => branch(5)], ["flair", flair], ["rushVar", rushVar], ["story", story]]) {
      try {
        out[k] = await fn();
      } catch (e) {
        out[k] = { ok: false, error: String(e) };
      }
    }
    out.allOk = Object.values(out).every((v) => v && v.ok);
    console.log("[R38-2B] " + JSON.stringify(out));
    return out;
  };
  window.__R38B = { branch, flair, rushVar, story, all };
  return "R38B ready";
})();
