// [R38] 6초 부하 테스트(built-in 브라우저 콘솔용) — R33~R37과 같은 장면: 4시대 1전선 거란 · 척준경 Lv.5 · T3 · 원화 몹 7 · 미션 · J 연타 1.5초 예열 뒤 6초 측정.
//  쓰는 법: 페이지를 열고(기준선 R37 = http://127.0.0.1:8042/index.html · R38 = http://127.0.0.1:8043/index.html?fx38=1) 콘솔에 전체를 붙여 넣은 뒤
//   await __R38L.run()  → JSON 한 줄(perSecond · minSecFps · p95FrameMs · renderAvgMs · r38 풀 최대 · r37 엔진). 브라우저 창은 보이는 상태로, 측정 중 창을 건드리지 않는다.
//  판정: 최저 55fps · 품질 단계 0 유지 · 콘솔 에러 0 — 같은 기계에서 R37 기준선과 함께 본다(R36.5 13절: 한 번 재서 55 근처면 여유가 없다는 뜻).
(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const key = (k, code, kc, type) => document.dispatchEvent(new KeyboardEvent(type, { key: k, code, keyCode: kc, which: kc, bubbles: true }));
  const press = async (k, code, kc, hold = 30) => {
    key(k, code, kc, "keydown");
    await sleep(hold);
    key(k, code, kc, "keyup");
  };
  const G = () => window.__RELIC;
  const waitFor = async (fn, ms = 20000) => {
    const t0 = performance.now();
    while (performance.now() - t0 < ms) {
      try {
        if (fn()) return true;
      } catch (e) {}
      await sleep(50);
    }
    return false;
  };
  const start = async () => {
    await waitFor(() => G() && window.__RELIC_DEV);
    if (!(G().player && G().stats && G().tick > 30)) {
      await press("Enter", "Enter", 13, 40);
      await waitFor(() => G().player && G().stats && G().tick > 30);
    }
  };
  const toEra = async (era) => {
    const D = window.__RELIC_DEV;
    for (let i = 0; i < 8 && G().era < era; i++) {
      D.advance();
      await sleep(400);
    }
    await waitFor(() => ["ready", "none", "failed"].includes(D.assets.status(era)), 60000);
  };
  const run = async () => {
    await start();
    await toEra(4);
    await sleep(1500);
    const g = G();
    const D = window.__RELIC_DEV;
    const p = g.player;
    g.enemies.length = 0;
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.x = g.cameraX + 360;
    p.z = 430;
    p.facing = 1;
    p.invincibleTimer = 99999;
    ["JURCHEN_INF", "REDTURBAN_ELITE", "JURCHEN_CAV", "REDTURBAN_INF", "WAKOU_SWORD", "MONGOL_RIDER", "KHITAN_INF"].forEach((u, i) => D.spawnUnit(u, p.x + 90 + (i % 4) * 110, 380 + (i >> 1) * 30));
    g.enemies.forEach((e) => {
      e.state = "ACTIVE";
      e.hp = e.maxHp = 1e9;
    });
    D.setLevel(5);
    g.stats.weaponTier = 3;
    D.r31mission("jurchen");
    if (g.mission) g.mission.t0 = g.tick + 1e6;
    D.r31item("blade");
    D.r31item("seal");
    await sleep(7000);
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
    const ts = [];
    const tiers = new Set();
    const renders = [];
    let hfxMax = 0;
    let h38 = 0;
    let p38 = 0;
    let kMin = 1;
    const s0 = D.r38 ? Object.assign({}, D.r38().stat) : null;
    const t0 = performance.now();
    const done = new Promise((res) => {
      const loop = (t) => {
        ts.push(t);
        tiers.add(g.quality.tier);
        if (g.perf && g.perf.last != null) renders.push(g.perf.last);
        hfxMax = Math.max(hfxMax, g.hfxLive || 0);
        if (D.r38) {
          const s = D.r38().stat;
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
    const rAvg = renders.reduce((a, b) => a + b, 0) / Math.max(1, renders.length);
    const s1 = D.r38 ? D.r38().stat : null;
    const E = D.r37 && D.r37().engine;
    const res = {
      url: location.port + location.search,
      perSecond: secs,
      minSecFps: Math.min(...secs),
      p95FrameMs: +p95.toFixed(1),
      tierStart: q0.tier,
      tiersSeen: [...tiers],
      dpr: q0.dpr,
      renderAvgMs: +rAvg.toFixed(2),
      renderMaxMs: +Math.max(...renders).toFixed(1),
      hfxLiveMax: hfxMax,
      r38: s1 ? { liveHmax: h38, livePmax: p38, hits: s1.hits - s0.hits, hfx: s1.hfx - s0.hfx, part: s1.part - s0.part, rej: s1.rej - s0.rej, kMin: +kMin.toFixed(2) } : null,
      r37: E ? { state: E.state, failed: E.failed, loaded: E.loaded } : null,
      enemies: g.enemies.length,
      viewport: [innerWidth, innerHeight, devicePixelRatio]
    };
    console.log("[R38 LOAD] " + JSON.stringify(res));
    return res;
  };
  window.__R38L = { run };
  return "R38L ready";
})();
