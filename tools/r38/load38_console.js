// [R38] 6초 부하 테스트(built-in 브라우저 콘솔용) — R33~R37과 같은 장면: 4시대 1전선 거란 · 척준경 Lv.5 · T3 · 원화 몹 7 · 미션 · J 연타 1.5초 예열 뒤 6초 측정.
//  먼저 shim38_console.js 를 붙여 넣는다(window.__R38S). 그 다음 이 파일 → await __R38L.run6({ mode: 1 }) (R38 과밀) · run6({ mode: 0 }) (같은 페이지에서 끔 = R37 그리기)
//  R37 기준선은 http://127.0.0.1:8042/index.html 에서 같은 파일로(mode 인자 없이). 두 탭을 번갈아 잴 때 다른 탭은 __R38S.S.setHalt(true)로 멈춘다.
//  유효 조건: 창이 보이고(visibilityState visible) 측정 중 타이머 콜백 0(rafMode.timer === 0). 창이 안 보이면 10초만 기다렸다가 그대로 재고 valid=false로 표시한다.
//  판정: 최저 55fps · 품질 단계 0 유지 · 콘솔 에러 0 — 같은 기계에서 R37 기준선과 함께 본다. 이 PC는 같은 빌드도 25~56fps · 12~22ms로 흔들린다(R38-handoff.md 4절).
(() => {
  const H = window.__R38S;
  if (!H) throw new Error("shim38_console.js 를 먼저 붙여 넣으세요");
  const { S, sleep, press, G, D, waitFor, start, toEra, waitVisible } = H;
  const run6 = async (opts = {}) => {
    await start();
    const g = G();
    const Dv = D();
    const p = g.player;
    S.setHalt(false);
    g.quality.forced = true;
    g.quality.tier = 0;
    g.quality.ema = 16.7;
    await toEra(4);
    await sleep(1000);
    g.enemies.length = 0;
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.x = g.cameraX + 360;
    p.z = 430;
    p.facing = 1;
    p.invincibleTimer = 99999;
    ["JURCHEN_INF", "REDTURBAN_ELITE", "JURCHEN_CAV", "REDTURBAN_INF", "WAKOU_SWORD", "MONGOL_RIDER", "KHITAN_INF"].forEach((u, i) => Dv.spawnUnit(u, p.x + 90 + (i % 4) * 110, 380 + (i >> 1) * 30));
    g.enemies.forEach((e) => {
      e.state = "ACTIVE";
      e.hp = e.maxHp = 1e9;
    });
    Dv.setLevel(5);
    g.stats.weaponTier = 3;
    Dv.r31mission("jurchen");
    if (g.mission) g.mission.t0 = g.tick + 1e6;
    Dv.r31item("blade");
    Dv.r31item("seal");
    if (Dv.r38mode && opts.mode != null) Dv.r38mode(opts.mode);
    const visOk = await waitVisible(opts.waitMs == null ? 10000 : opts.waitMs);
    await sleep(opts.settle == null ? 2500 : opts.settle);
    let w0 = performance.now();
    while (performance.now() - w0 < 1500) {
      await press("j", "KeyJ", 74);
      await sleep(110);
    }
    if (g.r31buff) {
      g.r31buff.blade = 900;
      g.r31buff.seal = 720;
    }
    p.invincibleTimer = 99999;
    const q0 = { tier: g.quality.tier, dpr: g.quality.dpr };
    const m0 = { real: S.real, timer: S.timer };
    const ts = [];
    const tiers = new Set();
    const renders = [];
    const steps = [];
    let hfxMax = 0;
    let h38 = 0;
    let p38 = 0;
    let kMin = 1;
    const s0 = Dv.r38 ? Object.assign({}, Dv.r38().stat) : null;
    const t0 = performance.now();
    const done = new Promise((res) => {
      const loop = (t) => {
        ts.push(t);
        tiers.add(g.quality.tier);
        if (g.perf && g.perf.last != null) renders.push(g.perf.last);
        if (g.perf && g.perf.step != null) steps.push(g.perf.step);
        hfxMax = Math.max(hfxMax, g.hfxLive || 0);
        if (Dv.r38) {
          const s = Dv.r38().stat;
          h38 = Math.max(h38, s.liveH);
          p38 = Math.max(p38, s.liveP);
          kMin = Math.min(kMin, s.k);
        }
        if (t - t0 < 6000) requestAnimationFrame(loop);
        else res();
      };
      requestAnimationFrame(loop);
    });
    const jl = setInterval(() => press("j", "KeyJ", 74), 140);
    await done;
    clearInterval(jl);
    const dts = ts.slice(1).map((t, i) => t - ts[i]);
    const secs = [];
    for (let s = 0; s < 6; s++) secs.push(ts.filter((t) => t - ts[0] >= s * 1000 && t - ts[0] < (s + 1) * 1000).length);
    const sorted = dts.slice().sort((a, b) => a - b);
    const p95 = sorted[Math.floor(sorted.length * 0.95)];
    const rs = renders.slice().sort((a, b) => a - b);
    const avg = (a) => a.reduce((x, y) => x + y, 0) / Math.max(1, a.length);
    const s1 = Dv.r38 ? Dv.r38().stat : null;
    const E = Dv.r37 && Dv.r37().engine;
    const raf = { real: S.real - m0.real, timer: S.timer - m0.timer };
    const res = {
      build: location.port + location.search,
      mode: Dv.r38 ? Dv.r38().mode : null,
      valid: raf.timer === 0 && document.visibilityState === "visible",
      visOk,
      perSecond: secs,
      minSecFps: Math.min(...secs),
      avgFps: +(ts.length / 6).toFixed(1),
      p95FrameMs: +p95.toFixed(1),
      tier: q0.tier,
      tiersSeen: [...tiers],
      dpr: q0.dpr,
      renderAvgMs: +avg(renders).toFixed(2),
      renderP50Ms: +rs[Math.floor(rs.length / 2)].toFixed(2),
      renderP95Ms: +rs[Math.floor(rs.length * 0.95)].toFixed(2),
      renderMaxMs: +Math.max(...renders).toFixed(1),
      stepAvgMs: +avg(steps).toFixed(2),
      hfxLiveMax: hfxMax,
      r38: s1 ? { liveHmax: h38, livePmax: p38, hits: s1.hits - s0.hits, kills: s1.kills - s0.kills, hfx: s1.hfx - s0.hfx, part: s1.part - s0.part, rej: s1.rej - s0.rej, kMin: +kMin.toFixed(2), msH: +s1.msH.toFixed(2), msP: +s1.msP.toFixed(2) } : null,
      r37: E ? { state: E.state, failed: E.failed, loaded: E.loaded } : null,
      rafMode: raf,
      vis: document.visibilityState,
      viewport: [innerWidth, innerHeight, devicePixelRatio]
    };
    if (opts.haltAfter) S.setHalt(true);
    console.log("[R38 LOAD] " + JSON.stringify(res));
    return res;
  };
  window.__R38L = { run6 };
  return "R38L ready";
})();
