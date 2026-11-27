// [R38] built-in 브라우저 콘솔용 기능 테스트(이 PC에는 node · Playwright가 없다 — R37과 같은 방식).
//  쓰는 법: http://127.0.0.1:8043/index.html 을 열고(React는 cdnjs에서 받음) 콘솔에 이 파일 전체를 붙여 넣은 뒤
//   await __R38T.map()   맵 상수(월드 9600 · 구역 카메라 · 트리거 · 1-2 경계 · 범위 1440)
//   await __R38T.cam()   Z1 돌입 → 카메라 범위 추적(480~960) · 주인공 벽(526~1874) · 웨이브 스폰이 지금 카메라 기준 화면 밖 · Z4 고정 8640
//   await __R38T.fx()    4시대 J 연타 → 과밀 이펙트 풀 사용 · 처치 연출 · 풀 상한 · R37 엔진 실패 0
//   await __R38T.hero()  5시대 권율 우측 걷기 1.5초 → 질주 프레임 8종 · 박자(틱) · 걸음 수 · 이동 거리 (R37 8042에서도 같은 것을 돌려 비교)
//  합성 keydown은 document에 보낸다(window 리스너까지 버블).
(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const key = (k, code, kc, type) => document.dispatchEvent(new KeyboardEvent(type, { key: k, code, keyCode: kc, which: kc, bubbles: true }));
  const press = async (k, code, kc, hold = 40) => {
    key(k, code, kc, "keydown");
    await sleep(hold);
    key(k, code, kc, "keyup");
  };
  const G = () => window.__RELIC;
  const D = () => window.__RELIC_DEV;
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
    await waitFor(() => G() && D());
    if (!(G().player && G().stats && G().tick > 30)) {
      await press("Enter", "Enter", 13);
      await waitFor(() => G().player && G().stats && G().tick > 30);
    }
  };
  const toEra = async (era) => {
    for (let i = 0; i < 8 && G().era < era; i++) {
      D().advance();
      await sleep(400);
    }
    await waitFor(() => ["ready", "none", "failed"].includes(D().assets.status(era)), 60000);
  };
  const map = async () => {
    await waitFor(() => D() && D().r38);
    const r = D().r38();
    const ok = r.world === 9600 && r.maxCam === 8640 && JSON.stringify(r.zoneCam) === "[480,2850,5100,8640]" && JSON.stringify(r.zoneTrig) === "[700,3090,5350,8890]" && r.span === 1440 && r.neoX === 4500 && r.mapK === 1.5;
    return { ok, world: r.world, maxCam: r.maxCam, zoneCam: r.zoneCam, zoneTrig: r.zoneTrig, span: r.span, neoX: r.neoX, mapK: r.mapK, mode: r.mode };
  };
  const cam = async () => {
    await start();
    const g = G();
    const p = g.player;
    g.enemies.length = 0;
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.invincibleTimer = 99999;
    p.x = 720;
    const locked = await waitFor(() => g.zoneState === "LOCKED", 3000);
    // 첫 웨이브(카메라 480 기준)
    const wave1 = await waitFor(() => g.enemies.length > 0, 3000);
    const xs1 = g.enemies.map((e) => Math.round(e.x));
    // 오른쪽 끝 — 카메라는 L + 480(= 960)까지, 주인공 벽은 L + 1440 - 46(= 1874)
    p.x = 5000;
    await sleep(1000);
    const wallX = Math.round(p.x);
    const camR = Math.round(g.cameraX);
    // 둘째 웨이브: 적을 치우면 지금 카메라(960) 기준 화면 밖(±60~130)에서 나와야 한다(셋에 하나는 화면 안 원형 등장)
    g.enemies.length = 0;
    g.spawnQ = [];
    const wave2 = await waitFor(() => g.enemies.length > 0, 4000);
    const cam2 = Math.round(g.cameraX);
    const xs2 = g.enemies.map((e) => Math.round(e.x));
    const outside = xs2.filter((x) => x < cam2 - 40 || x > cam2 + 960 + 40).length;
    const inside = xs2.length - outside;
    // 왼쪽 끝
    p.x = 100;
    await sleep(1000);
    const wallL = Math.round(p.x);
    const camL = Math.round(g.cameraX);
    // Z4 보스 아레나는 고정 카메라
    g.enemies.length = 0;
    g.spawnQ = [];
    g.waves = [];
    g.zoneIdx = 3;
    g.zoneState = "LOCKED";
    p.x = 8700;
    await sleep(1300);
    const cam4 = Math.round(g.cameraX);
    const wall4 = (() => {
      p.x = 9999;
      return null;
    })();
    await sleep(200);
    const wall4R = Math.round(p.x);
    g.enemies.length = 0;
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.x = 400;
    const ok = locked && wave1 && camR === 960 && wallX === 1874 && wave2 && cam2 === 960 && xs2.length >= 3 && inside <= Math.ceil(xs2.length / 3) && outside >= 1 && camL === 480 && wallL === 526 && cam4 === 8640 && wall4R === 8640 + 960 - 46;
    return { ok, locked, wave1xs: xs1, camR, wallX, cam2, wave2xs: xs2, outside, inside, camL, wallL, cam4, wall4R };
  };
  const fx = async () => {
    await start();
    await toEra(4);
    await sleep(1200);
    const g = G();
    const p = g.player;
    g.enemies.length = 0;
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
    });
    D().setLevel(5);
    g.stats.weaponTier = 3;
    await sleep(400);
    const s0 = Object.assign({}, D().r38().stat);
    const h0 = D().r31().hitFxN;
    for (let i = 0; i < 12; i++) {
      await press("j", "KeyJ", 74, 30);
      await sleep(110);
    }
    await sleep(300);
    const s1 = Object.assign({}, D().r38().stat);
    const h1 = D().r31().hitFxN;
    g.enemies.forEach((e) => {
      e.hp = 1;
    });
    for (let i = 0; i < 6; i++) {
      await press("j", "KeyJ", 74, 30);
      await sleep(110);
    }
    await sleep(400);
    const s2 = Object.assign({}, D().r38().stat);
    const r37 = D().r37();
    const E = r37 && r37.engine;
    const ok = s1.hits > s0.hits && s1.hfx > s0.hfx && s1.part > s0.part && h1 > h0 && s2.kills > s1.kills && s2.maxH <= 256 && s2.maxP <= 384 && (!E || !E.failed);
    return { ok, mode: D().r38().mode, hits: s1.hits - s0.hits, hfx: s1.hfx - s0.hfx, part: s1.part - s0.part, r31hitFx: h1 - h0, kills: s2.kills - s1.kills, maxH: s2.maxH, maxP: s2.maxP, rej: s2.rej, k: +s2.k.toFixed(2), r37: E ? { state: E.state, loaded: E.loaded, failed: E.failed, hit: r37.hit } : null };
  };
  const hero = async () => {
    await start();
    await toEra(5);
    await sleep(1500);
    const g = G();
    const p = g.player;
    g.enemies.length = 0;
    g.zoneState = "ROAM";
    g.zoneIdx = 0;
    p.invincibleTimer = 99999;
    p.x = Math.max(p.x, g.cameraX + 300);
    await sleep(300);
    const seq = [];
    let lastF = null;
    const st0 = p.steps || 0;
    const x0 = p.x;
    const t0 = g.tick;
    key("ArrowRight", "ArrowRight", 39, "keydown");
    const stop = performance.now() + 1500;
    while (performance.now() < stop) {
      await new Promise(requestAnimationFrame);
      const f = p._assetFrame;
      if (f !== lastF) {
        seq.push([g.tick - t0, f]);
        lastF = f;
      }
    }
    key("ArrowRight", "ArrowRight", 39, "keyup");
    const runs = seq.filter((s) => s[1] && s[1].startsWith("run"));
    const uniq = [...new Set(runs.map((s) => s[1]))].sort();
    const beats = [];
    for (let i = 1; i < runs.length; i++) beats.push(runs[i][0] - runs[i - 1][0]);
    const avgBeat = beats.length ? +(beats.reduce((a, b) => a + b, 0) / beats.length).toFixed(2) : null;
    const order = runs.slice(0, 9).map((s) => s[1]);
    const ok = uniq.length === 8 && avgBeat != null && avgBeat >= 2.8 && avgBeat <= 4.3 && (p.steps || 0) > st0 && p.x > x0 + 150;
    return { ok, era: g.era, uniq, avgBeat, beats: beats.slice(0, 16), order, steps: (p.steps || 0) - st0, dx: Math.round(p.x - x0), idleFrame: p._assetFrame };
  };
  window.__R38T = { map, cam, fx, hero, start, toEra, press };
  return "R38T ready";
})();
