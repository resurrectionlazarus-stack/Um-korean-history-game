  // ───────── [R38] 과밀 이펙트 엔진(1단계) — tools/r38/r38_fx.js(r38_patch.py가 읽어 넣음) ─────────
  //  치트키급 밀도를 60fps 안에서 내는 규칙:
  //  ① 고정 풀 2개 — R38_HFX 256칸(HD 오버레이: 잉크 스플래시 · 2중 참격호 · 충격 링 · 임팩트 라인) · R38_PART 384칸(저해상도 층: 불꽃 · 잉크 방울 · 불씨)
  //  ② 프레임 중 할당 0 — 칸 재사용, 위치는 시작 시각 t0에서 해석적으로 계산(틱 갱신 루프 없음 · 히트스톱 중에도 R31 풀처럼 실시간으로 흐름)
  //  ③ 틱당 예산 R38_BUDGET(품질 단계 0 · 1 · 2 = 48 · 28 · 14) — 모자라면 그 틱의 나머지 이펙트는 건너뜀(살아 있는 것은 그대로)
  //  ④ 밀도 계수 R38_STAT.k — 프레임 EMA 17ms → 1, 24ms → 0.4 / 그리기 EMA 11ms → 1, 15ms → 0.4 / 품질 단계 1 · 2는 0.7 · 0.5 상한(개수에만 곱한다)
  //  ⑤ shadowBlur · ctx.filter · 프레임 중 그라디언트 생성 없음, 글로우는 getGlowSprite 캐시 drawImage, 종류 × 투명도 3단계 묶음으로 fill/stroke 1회
  //  URL: ?fx38=0 끔(R37 그대로 — 비교용) · 1 과밀(기본) · 2 극과밀(예산 ×1.6 · 계수 1 고정 — 부하 측정용). 소리는 ?r37=0/1로 따로 끄고 켠다
  var R38_FX_MODE = (() => {
    try {
      const v = new URLSearchParams(window.location.search).get("fx38");
      if (v == null || v === "") return 1;
      const n = parseInt(v, 10);
      return n >= 0 && n <= 2 ? n : 1;
    } catch (e) {
      return 1;
    }
  })();
  var R38_HFX_N = 256;
  var R38_HFX = [];
  for (let i = 0; i < R38_HFX_N; i++) R38_HFX.push({ on: false, k: 0, x: 0, y: 0, t0: 0, dur: 1, dir: 1, a: 0, s: 1, c: "#ffffff", n: 0, seed: 0, _t: 0, _b: 0 });
  var r38HfxI = 0;
  var R38_PART_N = 384;
  var R38_PART = [];
  for (let i = 0; i < R38_PART_N; i++) R38_PART.push({ on: false, k: 0, x: 0, y: 0, vx: 0, vy: 0, g: 0, t0: 0, dur: 1, s: 1, c: "#ffffff", seed: 0, _t: 0 });
  var r38PartI = 0;
  var R38_BUDGET = [48, 28, 14];
  var R38_HFX_A = [0.3, 0.62, 0.95];
  // 진단용 끄기 스위치(__RELIC_DEV.r38mode(모드, 예산, 끄기) — 종류별 그리기 비용을 가려낼 때만 쓴다 · 기본 모두 false)
  var R38_SKIP = { hfx: false, part: false, k21: false, k22: false, k23: false, k24: false, p1: false, p2: false, p3: false, flash: false };
  var R38_STAT = { tick: -1, used: 0, rej: 0, k: 1, hfx: 0, part: 0, hits: 0, kills: 0, liveH: 0, liveP: 0, maxH: 0, maxP: 0, ktick: -1, kused: 0, msH: 0, msP: 0, maxMsH: 0, maxMsP: 0 };
  var r38K = (g) => {
    if (R38_FX_MODE === 2) return 1;
    const q = g.quality || {};
    const ema = q.ema || 16.7;
    const r = g.perf && g.perf.render || 0;
    let k = Math.min(1 - (ema - 17) / 7, 1 - (r - 11) / 4);
    if (q.tier === 1) k = Math.min(k, 0.7);
    else if (q.tier >= 2) k = Math.min(k, 0.5);
    return k < 0.4 ? 0.4 : k > 1 ? 1 : k;
  };
  var r38Take = (g, cost) => {
    if (R38_STAT.tick !== g.tick) {
      R38_STAT.tick = g.tick;
      R38_STAT.used = 0;
      R38_STAT.k = r38K(g);
    }
    const lim = R38_BUDGET[g.quality && g.quality.tier || 0] * (R38_FX_MODE === 2 ? 1.6 : 1);
    if (R38_STAT.used + cost > lim) {
      R38_STAT.rej++;
      return false;
    }
    R38_STAT.used += cost;
    return true;
  };
  // 처치 연출은 타격 예산과 따로 틱당 3회까지 — 타격 예산이 바닥난 틱에도 처치의 쾌감은 지킨다(밀도 계수는 같이 갱신)
  var r38TakeKill = (g) => {
    if (R38_STAT.tick !== g.tick) r38Take(g, 0);
    if (R38_STAT.ktick !== g.tick) {
      R38_STAT.ktick = g.tick;
      R38_STAT.kused = 0;
    }
    if (R38_STAT.kused >= 3) {
      R38_STAT.rej++;
      return false;
    }
    R38_STAT.kused++;
    return true;
  };
  var r38Hfx = (k, x, y, dur, dir, a, s, c, n) => {
    const e = R38_HFX[r38HfxI];
    r38HfxI = (r38HfxI + 1) % R38_HFX_N;
    e.on = true;
    e.k = k;
    e.x = x;
    e.y = y;
    e.t0 = performance.now();
    e.dur = dur;
    e.dir = dir >= 0 ? 1 : -1;
    e.a = a || 0;
    e.s = s || 1;
    e.c = c || "#ffffff";
    e.n = n || 0;
    e.seed = Math.random() * 1000;
    R38_STAT.hfx++;
    return e;
  };
  var r38Part = (k, x, y, vx, vy, grav, dur, s, c) => {
    const e = R38_PART[r38PartI];
    r38PartI = (r38PartI + 1) % R38_PART_N;
    e.on = true;
    e.k = k;
    e.x = x;
    e.y = y;
    e.vx = vx;
    e.vy = vy;
    e.g = grav;
    e.t0 = performance.now();
    e.dur = dur;
    e.s = s;
    e.c = c;
    e.seed = Math.random() * 1000;
    R38_STAT.part++;
  };
  // 불꽃 다발 — dir 쪽 살짝 위로 부채꼴(spread rad) · 속도 v px/s · 중력 1300. spread ≥ 6이면 전방향
  var r38Sparks = (x, y, n, dir, v, c, spread) => {
    const base = spread >= 6 ? 0 : dir > 0 ? -0.3 : Math.PI + 0.3;
    for (let j = 0; j < n; j++) {
      const ang = base + (Math.random() - 0.5) * spread;
      const vv = v * (0.45 + 0.65 * Math.random());
      r38Part(1, x, y, Math.cos(ang) * vv, Math.sin(ang) * vv, 1300, 260 + Math.random() * 220, 1.4 + Math.random() * 1.6, c);
    }
  };
  // 잉크 방울 — 맞은 쪽 반대로 튀어 떨어진다(먹 톤)
  var r38Ink = (x, y, n, dir, s) => {
    for (let j = 0; j < n; j++) {
      const ang = (dir > 0 ? -0.5 : Math.PI + 0.5) + (Math.random() - 0.5) * 2.2;
      const vv = 120 + Math.random() * 260;
      r38Part(2, x, y, Math.cos(ang) * vv, Math.sin(ang) * vv - 80, 1500, 320 + Math.random() * 220, (1.6 + Math.random() * 2.6) * s, "#0b0c12");
    }
  };
  // 불씨 — 천천히 떠오르며 깜박임
  var r38Embers = (x, y, n, c) => {
    for (let j = 0; j < n; j++) r38Part(3, x + (Math.random() - 0.5) * 50, y + (Math.random() - 0.5) * 30, (Math.random() - 0.5) * 70, -40 - Math.random() * 90, -60, 520 + Math.random() * 380, 1.3 + Math.random() * 1.3, c);
  };
  // 한 칸의 모양을 지금 경로에 덧붙인다(R31 hfxGeom과 같은 방식 · 종류 21~24)
  var r38Geom = (S, e, t) => {
    const k = e.k;
    const u = 1 - (1 - t) * (1 - t);
    if (k === 21) {
      // 잉크 스플래시 — 맞은 방향으로 먹 방울이 흩어지며 아래로 처진다
      for (let j = 0; j < e.n; j++) {
        const h1 = r31h(e.seed + j * 7.13);
        const h2 = r31h(e.seed + j * 3.7);
        const h3 = r31h(e.seed + j * 5.3);
        const ang = (e.dir > 0 ? 0 : Math.PI) + (h1 - 0.5) * 1.7;
        const d = (8 + 76 * h2) * e.s * u;
        const r = (1.8 + 6.5 * h3) * e.s * (1 - 0.3 * t);
        const bx = e.x + Math.cos(ang) * d;
        const by = e.y + Math.sin(ang) * d * 0.6 + 46 * t * t * (0.5 + h3);
        S.moveTo(bx + r, by);
        S.arc(bx, by, r, 0, TAU);
      }
    } else if (k === 22) {
      // 2중 참격호 — 베는 각도 둘레로 두 겹의 호가 퍼지며 좁아진다
      const R = (22 + 58 * u) * e.s;
      const a0 = e.dir > 0 ? e.a : Math.PI - e.a;
      for (let j = 0; j < 2; j++) {
        const rr = R * (j ? 0.72 : 1);
        const off = j ? 0.35 : 0;
        const w = 0.95 - 0.45 * t;
        S.moveTo(e.x + Math.cos(a0 - w + off) * rr, e.y + Math.sin(a0 - w + off) * rr * 0.55);
        S.ellipse(e.x, e.y, rr, rr * 0.55, 0, a0 - w + off, a0 + w + off);
      }
    } else if (k === 23) {
      // 충격 링 — 발밑 원근 타원(R31 ④보다 크고 빠르게)
      const rx = (18 + 112 * u) * e.s;
      S.moveTo(e.x + rx, e.y);
      S.ellipse(e.x, e.y, rx, rx * 0.32, 0, 0, TAU);
    } else if (k === 24) {
      // 임팩트 라인 — 애니메이션 임팩트 프레임처럼 바깥으로 뻗는 속도선
      const r0 = (16 + 42 * u) * e.s;
      const L = (24 + 64 * (1 - t)) * e.s;
      for (let j = 0; j < e.n; j++) {
        const ang = e.a + j * TAU / e.n + (r31h(e.seed + j * 2.3) - 0.5) * 0.25;
        const cx = Math.cos(ang);
        const cy = Math.sin(ang) * 0.8;
        S.moveTo(e.x + cx * r0, e.y + cy * r0);
        S.lineTo(e.x + cx * (r0 + L), e.y + cy * (r0 + L));
      }
    }
  };
  // 종류 K를 투명도 3단계로 묶어 칠한다 — 색이 null이면 첫 살아 있는 칸의 색(한 시대 안에서는 같은 색)
  var r38Batch = (S, K, fill, col, lw) => {
    for (let b = 0; b < 3; b++) {
      let any = false;
      let c = col;
      for (let i = 0; i < R38_HFX_N; i++) {
        const e = R38_HFX[i];
        if (!e.on || e.k !== K || e._b !== b) continue;
        if (!any) {
          any = true;
          S.beginPath();
          if (!c) c = e.c;
        }
        r38Geom(S, e, e._t);
      }
      if (!any) continue;
      S.globalAlpha = R38_HFX_A[b] * (K === 21 ? 0.85 : 1);
      if (fill) {
        S.fillStyle = c;
        S.fill();
      } else {
        S.strokeStyle = c;
        S.lineWidth = lw[b];
        S.stroke();
      }
    }
  };
  // HD 오버레이(세계 좌표) — drawR31Hfx 바로 뒤에서 부른다. 그리기 시간(ms)은 EMA · 최대로 R38_STAT에 남긴다(r38() 훅)
  var drawR38Hfx = (g, S) => {
    const tA = performance.now();
    drawR38HfxBody(g, S);
    const d = performance.now() - tA;
    R38_STAT.msH = R38_STAT.msH * 0.9 + d * 0.1;
    if (d > R38_STAT.maxMsH) R38_STAT.maxMsH = d;
  };
  var drawR38HfxBody = (g, S) => {
    if (!R38_FX_MODE || PERF_OFF.particles || PERF_OFF.hfx || R38_SKIP.hfx) return;
    const now = performance.now();
    let live = 0;
    for (let i = 0; i < R38_HFX_N; i++) {
      const e = R38_HFX[i];
      if (!e.on) continue;
      const t = (now - e.t0) / e.dur;
      if (t >= 1) {
        e.on = false;
        continue;
      }
      live++;
      e._t = t;
      e._b = t < 0.34 ? 2 : t < 0.67 ? 1 : 0;
    }
    R38_STAT.liveH = live;
    if (live > R38_STAT.maxH) R38_STAT.maxH = live;
    if (!live) return;
    S.save();
    if (!R38_SKIP.k21) r38Batch(S, 21, true, "#07080d", null);
    S.globalCompositeOperation = "lighter";
    S.lineCap = "round";
    if (!R38_SKIP.k22) r38Batch(S, 22, false, null, [1.4, 2, 2.6]);
    if (!R38_SKIP.k23) r38Batch(S, 23, false, "#ffffff", [1.2, 2.6, 4.2]);
    if (!R38_SKIP.k24) r38Batch(S, 24, false, null, [1.2, 1.5, 1.8]);
    S.restore();
  };
  // 저해상도 층(세계 좌표 · 카메라 이동 적용된 ctx) — drawParticles 바로 뒤에서 부른다
  var drawR38Parts = (ctx) => {
    const tA = performance.now();
    drawR38PartsBody(ctx);
    const d = performance.now() - tA;
    R38_STAT.msP = R38_STAT.msP * 0.9 + d * 0.1;
    if (d > R38_STAT.maxMsP) R38_STAT.maxMsP = d;
  };
  var drawR38PartsBody = (ctx) => {
    if (!R38_FX_MODE || PERF_OFF.particles || R38_SKIP.part) return;
    const now = performance.now();
    let live = 0;
    let ink = 0;
    ctx.beginPath();
    for (let i = 0; i < R38_PART_N; i++) {
      const e = R38_PART[i];
      if (!e.on) continue;
      const t = (now - e.t0) / e.dur;
      if (t >= 1) {
        e.on = false;
        continue;
      }
      live++;
      e._t = t;
      if (e.k !== 2 || R38_SKIP.p2) continue;
      const T = t * e.dur / 1e3;
      const bx = e.x + e.vx * T;
      const by = e.y + e.vy * T + 0.5 * e.g * T * T;
      const r = e.s * (1 - 0.4 * t);
      ctx.moveTo(bx + r, by);
      ctx.arc(bx, by, r, 0, TAU);
      ink++;
    }
    R38_STAT.liveP = live;
    if (live > R38_STAT.maxP) R38_STAT.maxP = live;
    if (ink) {
      ctx.globalAlpha = 0.9;
      ctx.fillStyle = "#0b0c12";
      ctx.fill();
    }
    if (live === ink) {
      ctx.globalAlpha = 1;
      return;
    }
    const T0 = ctx.getTransform();
    ctx.save();
    ctx.globalCompositeOperation = "lighter";
    for (let i = 0; i < R38_PART_N; i++) {
      const e = R38_PART[i];
      if (!e.on || e.k === 2 || (e.k === 1 ? R38_SKIP.p1 : R38_SKIP.p3)) continue;
      const t = e._t;
      const T = t * e.dur / 1e3;
      const bx = e.x + e.vx * T;
      const by = e.y + e.vy * T + 0.5 * e.g * T * T;
      if (e.k === 1) {
        const vy = e.vy + e.g * T;
        const len = Math.min(26, Math.max(5, Math.hypot(e.vx, vy) * 0.045)) * e.s;
        ptXform(ctx, T0, bx, by, Math.atan2(vy, e.vx));
        ctx.globalAlpha = 1 - t;
        ctx.drawImage(getGlowSprite(e.c), -len / 2, -e.s * 1.6, len, e.s * 3.2);
        ctx.setTransform(T0);
      } else {
        const fl = 0.6 + Math.sin(t * 18 + e.seed) * 0.4;
        ctx.globalAlpha = (1 - t) * fl;
        const r = e.s * 2.2;
        ctx.drawImage(getGlowSprite(e.c), bx - r, by - r, r * 2, r * 2);
      }
    }
    ctx.restore();
    ctx.globalAlpha = 1;
  };
// @@R38-APP@@
    // [R38] 과밀 이펙트 훅 — 타격(r31HitBurst 안) · 처치 · 각성 · 구역 돌입/정리. 모두 예산(r38Take)과 밀도 계수(R38_STAT.k)를 거친다
    const r38Hit = (g, en, x, y, dir, hv, fin, big, C) => {
      if (!R38_FX_MODE || !r38Take(g, hv ? 6 : 3)) return;
      const kk = R38_STAT.k;
      R38_STAT.hits++;
      const sc = (big ? 1.25 : 1) * (fin ? 1.3 : hv ? 1.15 : 1);
      const ang = g._cutAng != null ? g._cutAng : 0.4;
      // 매 타: 잉크 스플래시(맞은 방향) · 2중 참격호 · 불꽃 다발
      r38Hfx(21, x, y, 300, dir, 0, sc, "#07080d", Math.max(3, Math.round((hv ? 9 : 6) * kk)));
      r38Hfx(22, x, y, hv ? 200 : 150, dir, ang, sc, C[0], 0);
      r38Sparks(x, y, Math.max(3, Math.round((hv ? 14 : 7) * kk)), dir, hv ? 520 : 380, C[0], 1.1);
      // 강타 · 피니시: 발밑 충격 링 · 임팩트 라인 · 잉크 방울 · 피니시는 짧은 백색 섬광(기존 flashAlpha)
      if ((hv || fin) && r38Take(g, 4)) {
        r38Hfx(23, en.x, en.z, 320, dir, 0, sc, "#ffffff", 0);
        r38Hfx(24, x, y, 140, dir, Math.random() * TAU, sc, C[0], Math.max(6, Math.round(10 * kk)));
        r38Ink(x, y, Math.max(2, Math.round(5 * kk)), dir, 1);
        if (fin && !R38_SKIP.flash) g.flashAlpha = Math.max(g.flashAlpha, 0.14);
      }
    };
    const r38Kill = (g, en) => {
      if (!R38_FX_MODE || !r38TakeKill(g)) return;
      const kk = R38_STAT.k;
      R38_STAT.kills++;
      const big = !!(en.isMidBoss || en.heavy || en.elite);
      const sc = big ? 1.5 : 1.1;
      const dir = en.facing > 0 ? -1 : 1;
      const y = en.z - (en.y || 0) - 40;
      const C = R30C(g);
      r38Hfx(23, en.x, en.z, 420, dir, 0, sc, "#ffffff", 0);
      r38Hfx(21, en.x, y, 420, dir, 0, sc * 1.2, "#07080d", Math.max(5, Math.round(12 * kk)));
      r38Hfx(24, en.x, y, 170, dir, Math.random() * TAU, sc, C[0], Math.max(6, Math.round(12 * kk)));
      r38Sparks(en.x, y, Math.max(6, Math.round(16 * kk)), dir, 460, C[0], 2.4);
      r38Ink(en.x, y, Math.max(3, Math.round(8 * kk)), dir, 1.3);
      r38Embers(en.x, y, Math.max(3, Math.round(8 * kk)), C[0]);
    };
    // 각성(드묾 — 예산을 거치지 않는 1회성): 충격 링 2겹 · 임팩트 라인 · 전방향 불꽃 36 · 불씨 24
    const r38Ult = (g) => {
      if (!R38_FX_MODE) return;
      const p = g.player;
      const C = R30C(g);
      const y = p.z - p.y - 60;
      r38Hfx(23, p.x, p.z, 520, p.facing, 0, 2.2, "#ffffff", 0);
      r38Hfx(23, p.x, p.z, 700, p.facing, 0, 3, C[0], 0);
      r38Hfx(24, p.x, y, 260, p.facing, Math.random() * TAU, 2.2, C[0], 16);
      r38Sparks(p.x, y, 36, p.facing, 620, C[0], 7);
      r38Embers(p.x, y, 24, C[0]);
    };
    // 구역 돌입 · 정리(1회성): 충격 링 · 임팩트 라인 · 불씨
    const r38Burst = (g, x, y, s, c) => {
      if (!R38_FX_MODE) return;
      r38Hfx(23, x, y, 480, 1, 0, s, c || "#ffffff", 0);
      r38Hfx(24, x, y - 50, 220, 1, Math.random() * TAU, s, c || "#fde047", 14);
      r38Embers(x, y - 50, 16, c || "#fde047");
    };
