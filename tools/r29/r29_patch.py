#!/usr/bin/env python3
"""R29 — 시작 화면 로딩 가림막 · 2시대 연나라/한나라 군대(길고 어렵게) · 베는 맛(베기 선 · 두 동강 · 히트스톱) · 콤보(질풍연참 · AIR RAID · DASH LINK).

사용: python3 -I r29_patch.py <shinsi-R29/index.html>
"""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"anchor count {c}: {old[:120]!r}")
    s = s.replace(old, new)
    n += 1


# ───────────────────────── A. 시작 화면 로딩 가림막 ─────────────────────────
rep(r'''    img.onload = () => img.decode ? img.decode().then(() => res(img), () => res(img)) : res(img);
    img.onerror = () => rej(new Error("load " + src));''',
    r'''    // [R29] 시작 화면 로딩 진행률용 — 끝난 이미지 수(성공 · 실패 모두)
    const fin = () => {
      state.imgDone = (state.imgDone || 0) + 1;
    };
    img.onload = () => img.decode ? img.decode().then(() => (fin(), res(img)), () => (fin(), res(img))) : (fin(), res(img));
    img.onerror = () => (fin(), rej(new Error("load " + src)));''')

rep(r'''        const ms = mobSpecOf(mb[1]);
        if (!ms) {''',
    r'''        const ms = mobSpecOf(mb[1]);
        // [R29] 쓰지 않는 몹 원화(2시대 고조선 창병 · 궁수 → 연나라 · 한나라 군대로 교체)는 읽지 않는다
        if (ms && ms.skip) return;
        if (!ms) {''')

rep(r'''    const entry = { status: "loading", data: null, error: null };''',
    r'''    const entry = { status: "loading", data: null, error: null, t0: performance.now() };''')

rep(r'''      const plan = planFor(man, era);
      if (!plan) {
        entry.status = "none";
        return null;
      }''',
    r'''      const plan = planFor(man, era);
      if (!plan) {
        entry.status = "none";
        return null;
      }
      // [R29] 로딩 진행률 분모 = 계획에 잡힌 이미지 수
      entry.base = state.imgDone || 0;
      entry.total = countPlanImages(plan);''')

rep(r'''  function eraAssetStatus(era, dpr = 1) {''',
    r'''  // [R29] 시작 화면 로딩 가림막 — 진행률(계획에 잡힌 이미지 수 대비 끝난 이미지 수)
  function countPlanImages(plan) {
    let cnt = 0;
    const walk = (o, d) => {
      if (!o || d > 4) return;
      for (const k in o) {
        const v = o[k];
        if (typeof v === "string") {
          if (/\.(?:png|webp|jpe?g)$/i.test(v)) cnt++;
        } else if (v && typeof v === "object" && k !== "meta" && k !== "spec") walk(v, d + 1);
      }
    };
    walk(plan, 0);
    return cnt;
  }
  function eraLoadInfo(era) {
    let best = null;
    for (const k in state.eras) {
      if (k.split("@")[0] !== String(era)) continue;
      const E = state.eras[k];
      if (E.status === "ready") return { status: "ready", p: 1, t0: E.t0 || 0 };
      if (!best || E.status === "loading") best = E;
    }
    if (!best) return { status: state.disabled ? "disabled" : "idle", p: 0, t0: 0 };
    const done = Math.max(0, (state.imgDone || 0) - (best.base || 0));
    return { status: best.status, p: best.total ? Math.min(0.97, done / best.total) : 0.02, t0: best.t0 || 0 };
  }
  //  1시대 원화가 다 구워질 때까지 옛 도트 장면 대신 수묵 가림막을 보여 준다. START · Enter를 미리 누르면 예약 → 준비되는 즉시 시작.
  //  원화를 껐거나(?assets=off) 실패 · 없음이면 막지 않고, 30초(예약 뒤 12초)를 넘기면 그대로 연다
  var TITLE_GATE = { pending: false, pendT: 0, shown: 0, closed: false, fade0: 0 };
  function titleGate() {
    const L = eraLoadInfo(1);
    const now = performance.now();
    const loading = L.status === "loading" || L.status === "idle" && now < 2500;
    const open = !loading || L.status === "loading" && now - L.t0 > 3e4 || TITLE_GATE.pending && now - TITLE_GATE.pendT > 12e3;
    return { open, p: L.p };
  }
  function titleLoadLabel() {
    const TG = titleGate();
    if (TG.open) return null;
    return { p: Math.round(Math.max(0, Math.min(0.99, TITLE_GATE.shown)) * 100), pend: !!TITLE_GATE.pending };
  }
  function drawTitleCurtain(c, W, H, p, alpha) {
    const t = performance.now() / 1e3;
    if (alpha >= 1) TITLE_GATE.shown += (p - TITLE_GATE.shown) * 0.12;
    const shown = alpha >= 1 ? TITLE_GATE.shown : 1;
    c.save();
    c.globalAlpha = alpha;
    let gr = c.createLinearGradient(0, 0, 0, H);
    gr.addColorStop(0, "#141b2b");
    gr.addColorStop(0.55, "#1e2536");
    gr.addColorStop(1, "#0a0b10");
    c.fillStyle = gr;
    c.fillRect(0, 0, W, H);
    // 달무리 · 달
    const mx = W * 0.78;
    const my = H * 0.2;
    const mr = H * 0.075;
    gr = c.createRadialGradient(mx, my, mr * 0.8, mx, my, mr * 4.8);
    gr.addColorStop(0, "rgba(255,244,214,0.34)");
    gr.addColorStop(1, "rgba(255,244,214,0)");
    c.fillStyle = gr;
    c.fillRect(mx - mr * 4.8, my - mr * 4.8, mr * 9.6, mr * 9.6);
    c.fillStyle = "#fff8e8";
    c.beginPath();
    c.arc(mx, my, mr, 0, Math.PI * 2);
    c.fill();
    // 수묵 산 세 겹(먼 산은 밑동이 안개로 스러짐) · 산자락 안개
    const LAY = [
      [0.56, 0.22, "122,131,152", 0.72, 4, 1.2],
      [0.67, 0.18, "72,80,99", 0.92, 9, 2],
      [0.82, 0.15, "20,22,30", 1, 16, 3.1]
    ];
    for (let li = 0; li < LAY.length; li++) {
      const [base, amp, rgb, a0, spd, fq] = LAY[li];
      const off = t * spd;
      c.beginPath();
      c.moveTo(0, H);
      for (let x = 0; x <= W + 8; x += 8) {
        const u = (x + off) / W * fq;
        const r = 0.55 * Math.abs(Math.sin(u * 2.3 + li * 1.7)) + 0.3 * Math.sin(u * 5.1 + 0.7 + li) + 0.15 * Math.sin(u * 12.7 + li * 3.1);
        c.lineTo(x, H * (base - amp * r));
      }
      c.lineTo(W, H);
      c.closePath();
      const lg = c.createLinearGradient(0, H * (base - amp), 0, H * Math.min(1, base + 0.16));
      lg.addColorStop(0, `rgba(${rgb},${a0})`);
      lg.addColorStop(1, li === LAY.length - 1 ? `rgba(${rgb},1)` : `rgba(${rgb},0)`);
      c.fillStyle = lg;
      c.fill();
      const my2 = H * (base + 0.02);
      const mg = c.createLinearGradient(0, my2 - 26, 0, my2 + 26);
      mg.addColorStop(0, "rgba(176,184,198,0)");
      mg.addColorStop(0.5, `rgba(190,198,212,${0.11 - li * 0.03})`);
      mg.addColorStop(1, "rgba(176,184,198,0)");
      c.fillStyle = mg;
      c.fillRect(0, my2 - 26, W, 52);
    }
    // 불티
    c.globalCompositeOperation = "lighter";
    for (let i = 0; i < 24; i++) {
      const x = (i * 137.5 + t * (7 + i % 5 * 3)) % (W + 40) - 20;
      const y = H - (t * (12 + i % 7 * 4) + i * 53) % (H * 0.85);
      c.globalAlpha = alpha * (0.22 + 0.34 * Math.abs(Math.sin(t * 1.7 + i)));
      c.fillStyle = i % 4 ? "#f59e0b" : "#fde68a";
      c.beginPath();
      c.arc(x, y, 0.9 + i % 3 * 0.55, 0, Math.PI * 2);
      c.fill();
    }
    c.globalCompositeOperation = "source-over";
    c.globalAlpha = alpha;
    // 진행 붓질
    const bw = W * 0.34;
    const bx = (W - bw) / 2;
    const by = H * 0.72;
    c.lineCap = "round";
    c.strokeStyle = "rgba(255,255,255,0.1)";
    c.lineWidth = 3;
    c.beginPath();
    c.moveTo(bx, by);
    c.lineTo(bx + bw, by);
    c.stroke();
    const pw = bw * Math.max(0.02, Math.min(1, shown));
    gr = c.createLinearGradient(bx, 0, bx + bw, 0);
    gr.addColorStop(0, "#fbbf24");
    gr.addColorStop(1, "#f97316");
    c.fillStyle = gr;
    c.beginPath();
    c.moveTo(bx, by);
    for (let x = 0; x <= pw; x += 5) c.lineTo(bx + x, by - 2.4 - 0.9 * Math.sin(x * 0.09 + t * 3));
    c.lineTo(bx + pw, by);
    for (let x = pw; x >= 0; x -= 5) c.lineTo(bx + x, by + 2.4 + 0.9 * Math.sin(x * 0.07 + 1 + t * 2.4));
    c.closePath();
    c.fill();
    c.globalCompositeOperation = "lighter";
    gr = c.createRadialGradient(bx + pw, by, 0, bx + pw, by, 15);
    gr.addColorStop(0, "rgba(253,230,138,0.9)");
    gr.addColorStop(1, "rgba(253,230,138,0)");
    c.fillStyle = gr;
    c.fillRect(bx + pw - 15, by - 15, 30, 30);
    c.globalCompositeOperation = "source-over";
    c.font = "700 12px system-ui, sans-serif";
    c.textAlign = "center";
    c.textBaseline = "alphabetic";
    c.fillStyle = "rgba(226,232,240,0.8)";
    c.fillText("시공의 문을 여는 중 · " + Math.round(shown * 100) + "%", W / 2, by + 22);
    c.restore();
  }
  function eraAssetStatus(era, dpr = 1) {''')

# 렌더: 가림막(닫힘이면 장면을 그리지 않고 가림막만) · 걷힐 때 0.52초 페이드
rep(r'''        const bd = bgRef.current;
        if (!bd || !spritesRef.current) return;
        PS.t.length = 0;''',
    r'''        const bd = bgRef.current;
        if (!bd || !spritesRef.current) return;
        // [R29] 시작 화면 로딩 가림막 — 1시대 원화가 준비되기 전에는 옛 도트 장면 대신 수묵 가림막만 그린다
        if (sync.gameState === "TITLE") {
          const TG = titleGate();
          if (!TG.open) {
            TITLE_GATE.closed = true;
            screen.setTransform(canvas.width / VIEW_W, 0, 0, canvas.height / VIEW_H, 0, 0);
            screen.imageSmoothingEnabled = true;
            drawTitleCurtain(screen, VIEW_W, VIEW_H, TG.p, 1);
            return;
          }
        }
        if (TITLE_GATE.closed) {
          TITLE_GATE.closed = false;
          TITLE_GATE.fade0 = performance.now();
        }
        PS.t.length = 0;''')

rep(r'''        overlay.length = 0;
        screenOverlay.length = 0;
        const tr = g.trauma * g.trauma;''',
    r'''        overlay.length = 0;
        screenOverlay.length = 0;
        // [R29] 가림막이 걷히는 0.52초 — 준비된 장면 위로 수묵 가림막이 서서히 사라진다
        if (TITLE_GATE.fade0) {
          const fe = (performance.now() - TITLE_GATE.fade0) / 520;
          if (fe >= 1 || fe < 0) TITLE_GATE.fade0 = 0;
          else screenOverlay.push((c) => drawTitleCurtain(c, VIEW_W, VIEW_H, 1, 1 - fe * fe * (3 - 2 * fe)));
        }
        const tr = g.trauma * g.trauma;''')

rep(r'''    const startGame = () => {
      if (syncRef.current.gameState !== "TITLE") return;
      if (sfxRef.current) sfxRef.current.unlock();
      sfx("coin");
      engineReset();
    };''',
    r'''    const startGame = () => {
      if (syncRef.current.gameState !== "TITLE") return;
      if (sfxRef.current) sfxRef.current.unlock();
      // [R29] 1시대 원화가 다 구워지기 전에 누르면 예약 → 준비되는 즉시 시작(옛 도트 장면으로 시작하지 않게)
      if (!titleGate().open) {
        if (!TITLE_GATE.pending) {
          TITLE_GATE.pending = true;
          TITLE_GATE.pendT = performance.now();
          sfx("coin");
          putTitleLoad(titleLoadLabel());
        }
        return;
      }
      if (!TITLE_GATE.pending) sfx("coin");
      TITLE_GATE.pending = false;
      engineReset();
    };''')

rep(r'''    const startGameRef = useRef(null);
    startGameRef.current = startGame;''',
    r'''    const startGameRef = useRef(null);
    startGameRef.current = startGame;
    // [R29] 시작 화면 로딩 표시(START 버튼 글자) · 미리 누른 START 예약 → 원화가 준비되면 바로 시작
    //  글자가 실제로 바뀔 때만 상태를 바꾼다(게임 중에는 React 다시 그리기 0회)
    const [titleLoad, setTitleLoad] = useState(() => titleLoadLabel());
    const titleLoadRef = useRef(titleLoad);
    const putTitleLoad = (v) => {
      const o = titleLoadRef.current;
      if (o === v || o && v && o.p === v.p && o.pend === v.pend) return;
      titleLoadRef.current = v;
      setTitleLoad(v);
    };
    useEffect(() => {
      const id = setInterval(() => {
        const onTitle = syncRef.current.gameState === "TITLE";
        if (!onTitle) TITLE_GATE.pending = false;
        const v = onTitle ? titleLoadLabel() : null;
        putTitleLoad(v);
        if (onTitle && !v && TITLE_GATE.pending && startGameRef.current) startGameRef.current();
      }, 150);
      return () => clearInterval(id);
    }, []);''')

rep(r'''            className: "rh-blink mt-5 px-8 py-2.5 rounded-xl bg-gradient-to-r from-amber-400 to-orange-500 text-slate-950 font-black text-sm tracking-[0.25em] shadow-lg active:scale-95"
          },
          "PRESS START"''',
    r'''            className: "rh-blink mt-5 px-8 py-2.5 rounded-xl bg-gradient-to-r from-amber-400 to-orange-500 text-slate-950 font-black text-sm tracking-[0.25em] shadow-lg active:scale-95"
          },
          titleLoad ? (titleLoad.pend ? "곧 시작 " : "불러오는 중 ") + titleLoad.p + "%" : "PRESS START"''')

rep(r'''            className: "w-full max-w-xs py-4 rounded-2xl bg-gradient-to-r from-amber-400 via-amber-500 to-orange-500 text-slate-950 font-black text-base tracking-[0.3em] shadow-lg active:scale-95"
          },
          "START"''',
    r'''            className: "w-full max-w-xs py-4 rounded-2xl bg-gradient-to-r from-amber-400 via-amber-500 to-orange-500 text-slate-950 font-black text-base tracking-[0.3em] shadow-lg active:scale-95"
          },
          titleLoad ? (titleLoad.pend ? "곧 시작 · " : "불러오는 중 · ") + titleLoad.p + "%" : "START"''')

# ───────────────────────── B. 2시대 연나라 · 한나라 군대 ─────────────────────────
rep(r'''    pike: { era: 2, unit: "GOJO_PIKE", h: 132 },
    archer: { era: 2, unit: "GOJO_ARCHER", h: 128 },''',
    r'''    // [R29] 2시대 적 = 연나라 · 한나라 군대 — 고조선 창병 · 궁수 원화는 읽지 않음(skip).
    //  아래 5종은 고조선 원화를 다시 칠한 임시 원화(연 = 남색 쇠미늘 · 한 = 흑칠 갑옷 + 붉은 전포 · 극의 곁날 · 붉은 술) — 디자인팀 정식 원화가 오면 같은 이름으로 교체
    pike: { era: 2, unit: "GOJO_PIKE", h: 132, skip: true },
    archer: { era: 2, unit: "GOJO_ARCHER", h: 128, skip: true },
    yan_pike: { era: 2, unit: "YAN_PIKE", h: 132 },
    yan_archer: { era: 2, unit: "YAN_ARCHER", h: 128 },
    han_pike: { era: 2, unit: "HAN_PIKE", h: 134 },
    han_archer: { era: 2, unit: "HAN_ARCHER", h: 130 },
    han_elite: { era: 2, unit: "HAN_ELITE", h: 150 },''')

rep(r'''        ...mobFiles(2, "archer"),''',
    r'''        ...mobFiles(2, "archer"),
        // [R29] 2시대 연나라 · 한나라 병사(임시 원화 webp)
        ...["yan_pike", "yan_archer", "han_pike", "han_archer", "han_elite"].flatMap((k) => MOB_POSES.map((p) => `assets/mob/era2_${k}_${p}.webp`)),''')

rep(r'''    // 3. 삼국 [R14 삼국통일전] Z1·Z2 백제 → Z3 고구려 → Z4 당군''',
    r'''    // [R29] 2시대 적군 = 중국 연나라 → 한나라: Z1 연나라 장수 진개의 침입(기원전 3세기) · Z2 위만과 연나라 무리(기원전 194) · Z3~Z4 한 무제의 침공(기원전 109~108)
    YAN_PIKE: { era: 2, name: "연나라 창병", tactic: "pike", hp: 1.05, speed: 0.95, reach: 175, dmg: 1.1, color: "#93c5fd" },
    YAN_ARCHER: { era: 2, name: "연나라 궁수", tactic: "ranged", shot: "arrow", hp: 0.75, speed: 0.9, keep: 300, aim: 44, dmg: 0.85, color: "#bfdbfe" },
    HAN_PIKE: { era: 2, name: "한나라 극병", tactic: "pike", hp: 1.25, speed: 1, reach: 185, dmg: 1.2, color: "#f87171" },
    HAN_ARCHER: { era: 2, name: "한나라 궁수", tactic: "ranged", shot: "arrow", volley: 2, hp: 0.85, speed: 0.95, keep: 320, aim: 40, dmg: 0.8, color: "#fca5a5" },
    HAN_ELITE: { era: 2, name: "한나라 철갑 극병", tactic: "heavy", hp: 2.3, speed: 0.85, reach: 160, dmg: 1.5, color: "#ef4444" },
    // 3. 삼국 [R14 삼국통일전] Z1·Z2 백제 → Z3 고구려 → Z4 당군''')

rep(r'''    2: ["GOJO_PIKE", "GOJO_PIKE", "GOJO_ARCHER"],''',
    r'''    2: ["YAN_PIKE", "YAN_PIKE", "YAN_ARCHER"],''')

rep(r'''    // [R14] 3시대 삼국통일전: Z1·Z2 황산벌 백제 결사대 → Z3 고구려 철갑병 → Z4 당군''',
    r'''    // [R29] 2시대: Z1 요동 국경 · Z2 패수(연나라) → Z3 왕검성 외곽 · Z4 왕검성(한나라 대군, 철갑 극병은 Z3 웨이브마다 따로)
    2: { 0: ["YAN_PIKE", "YAN_ARCHER", "YAN_PIKE"], 1: ["YAN_PIKE", "YAN_ARCHER", "YAN_PIKE", "YAN_ARCHER"], 2: ["HAN_PIKE", "HAN_ARCHER", "HAN_PIKE", "HAN_PIKE", "HAN_ARCHER"], 3: ["HAN_PIKE", "HAN_ARCHER", "HAN_PIKE"] },
    // [R14] 3시대 삼국통일전: Z1·Z2 황산벌 백제 결사대 → Z3 고구려 철갑병 → Z4 당군''')

rep(r'''  var eraUnitIds = (era) => [.../* @__PURE__ */ new Set([...ERA_ROSTER[era] || [], ...Object.values(ZONE_ROSTER[era] || {}).flat()])];''',
    r'''  // [R29] 명단 밖에서 따로 나오는 병종(코드 스프라이트 · 크기 기준도 굽는다)
  var ERA_EXTRA_UNITS = { 2: ["HAN_ELITE"] };
  var eraUnitIds = (era) => [.../* @__PURE__ */ new Set([...ERA_ROSTER[era] || [], ...Object.values(ZONE_ROSTER[era] || {}).flat(), ...ERA_EXTRA_UNITS[era] || []])];''')

rep(r'''    2: { key: "MB_WIMAN", name: "위만",''',
    r'''    2: { key: "MB_WIMAN", zone: 1, name: "위만",''')

rep(r'''    // [R14] 삼국통일전: 백제 결사대 · 고구려 철갑병 · 계백 · 연개소문''',
    r'''    // [R29] 2시대 연나라(남색 쇠미늘) · 한나라(흑칠 갑옷 + 붉은 전포) — 원화가 없을 때 쓰는 코드 스프라이트
    YAN_PIKE: { tor: SPEC(["#64748b", "#334155", "#0f172a"]), leg: ["#475569", "#1e293b", "#0b1120"], arm: SKIN, trim: "#93c5fd", helm: "gojo", mask: false, unitWeapon: "bronzeSpear", wscale: 1.25 },
    YAN_ARCHER: { tor: ["#64748b", "#334155", "#0f172a"], leg: ["#475569", "#1e293b", "#0b1120"], arm: SKIN, trim: "#bfdbfe", helm: "band", mask: false, unitWeapon: "bow", cape: ["#1e3a8a", "#0b1430"] },
    HAN_PIKE: { tor: SPEC(["#7f1d1d", "#3f0a0a", "#140404"]), leg: ["#991b1b", "#5b0f0f", "#1c0505"], arm: SKIN, trim: "#fca5a5", helm: "gojo", mask: false, unitWeapon: "bronzeSpear", wscale: 1.3 },
    HAN_ARCHER: { tor: ["#991b1b", "#5b0f0f", "#1c0505"], leg: ["#44403c", "#1c1917", "#0c0a09"], arm: SKIN, trim: "#fca5a5", helm: "band", mask: false, unitWeapon: "bow", cape: ["#7f1d1d", "#2a0a0a"] },
    HAN_ELITE: { tor: SPEC(["#27272a", "#18181b", "#09090b"]), leg: ["#991b1b", "#5b0f0f", "#1c0505"], arm: SPEC(["#3f3f46", "#18181b", "#09090b"]), trim: "#ef4444", helm: "gojo", mask: false, unitWeapon: "longSpear", wscale: 1.35, bulk: 1.3 },
    // [R14] 삼국통일전: 백제 결사대 · 고구려 철갑병 · 계백 · 연개소문''')

rep(r'''GOJO_ARCHER: "bow", BJ_ARCHER: "bow",''',
    r'''GOJO_ARCHER: "bow", YAN_ARCHER: "bow", HAN_ARCHER: "bow", BJ_ARCHER: "bow",''')

rep(r'''  var ULT_GAIN_PER_HIT = 1.5;''',
    r'''  // [R29] 2시대 구역 이름 · 웨이브 — 구석기 · 신석기(1시대 72마리)보다 길고 어렵게: 96마리 + 한나라 철갑 극병 5 + 위만(Z2) · 한 무제
  //  (남은 적 2명 이하이면 다음 웨이브가 곧바로 합류 · 한나라 궁수 2발 일제 사격). 길이 조절 손잡이 = ERA2_ZONE_WAVES
  var ZONE_NAMES_ERA = { 2: ["Z1 요동 국경", "Z2 패수 나루", "Z3 왕검성 외곽", "Z4 왕검성"] };
  var zoneNamesFor = (era) => ZONE_NAMES_ERA[era] || ZONE_NAMES;
  var ERA2_ZONE_WAVES = [
    [6, 7, 7, 8],
    [7, 8, 8, 9],
    [8, 9, 9, 10]
  ];
  var ULT_GAIN_PER_HIT = 1.5;''')

rep(r'''      g.waves = era === 4 ? (ERA4_ZONE_WAVES[zi] || []).slice() : ZONE_WAVES[zi].map((n) => n + bonus);''',
    r'''      g.waves = era === 4 ? (ERA4_ZONE_WAVES[zi] || []).slice() : era === 2 ? (ERA2_ZONE_WAVES[zi] || []).slice() : ZONE_WAVES[zi].map((n) => n + bonus);''')

rep(r'''[${ZONE_NAMES[zi]}]''', r'''[${zoneNamesFor(era)[zi]}]''')

rep(r'''      const ACTS = {
''',
    r'''      const ACTS = {
        // [R29] 2시대 3막: 연나라 진개의 침입 → 위만 → 한 무제의 침공
        2: { 0: ["1막 · 기원전 3세기 연나라의 침입", "요동 국경 — 연나라 장수 진개의 군대가 고조선 서쪽 땅으로 밀려든다", null], 1: ["2막 · 기원전 194 위만", "패수 — 연나라에서 건너온 위만의 무리가 왕검성을 노린다", null], 2: ["3막 · 기원전 109 한 무제의 침공", "왕검성 외곽 — 한나라 대군이 육로와 바닷길로 몰려온다", null] },
''')

rep(r'''      if (era === 1 && (zi === 0 || zi === 2)) {
        announceSubStage(zi);''',
    r'''      // [R29] 2시대 막마다 동료 선녀의 역사 한 줄
      const HIST2 = ["📜 기원전 3세기 초, 연나라 장수 진개가 쳐들어와 고조선은 서쪽 땅 2천여 리를 빼앗겼어요!", "📜 기원전 194년, 연나라에서 건너온 위만이 준왕을 몰아내고 왕이 돼요. 이때 철기 문화가 더 널리 퍼졌죠!", "📜 기원전 109년 한 무제가 쳐들어와요. 왕검성은 1년 가까이 버텼지만 기원전 108년에 무너졌어요."];
      if (era === 2 && HIST2[zi]) addTimer(70, () => setCompanionBubble(HIST2[zi], 200));
      if (era === 1 && (zi === 0 || zi === 2)) {
        announceSubStage(zi);''')

rep(r'''      if (withElite && g.era === 1) {''',
    r'''      // [R29] 2시대 Z3 왕검성 외곽: 웨이브마다 한나라 철갑 극병 1명(마지막 웨이브 2명) — 몸집 1.18배 · 무거운 몸(넉백 ↓)
      if (g.era === 2 && g.zoneIdx === 2) {
        const ne = g.waves.length === 0 ? 2 : 1;
        for (let k = 0; k < ne; k++) {
          spawnEnemyAt(L + VIEW_W + 70 + k * 70, 384 + k * 56, { flank: 1, unit: "HAN_ELITE" });
          g.enemies[g.enemies.length - 1].mobScale = 1.18;
        }
        if (!g._hanEliteMsg) {
          g._hanEliteMsg = true;
          setCompanionBubble("⚠️ 한나라 철갑 극병! 붉은 부채꼴(대참격)이 보이면 물러났다가 빈틈에 베세요!", 150);
        }
      }
      if (withElite && g.era === 1) {''')

rep(r'''          } else if (alive === 0 && !g.bossActive) {
            if (g.waves.length) g.waveSpawnCd = 26;''',
    r'''          } else if (g.era === 2 && g.waves.length && alive <= 2 && !g.bossActive) {
            // [R29] 2시대 증원 — 남은 적이 2명 이하면 다음 웨이브가 곧바로 합류(쉴 틈 없는 대군)
            g.waveSpawnCd = 30;
          } else if (alive === 0 && !g.bossActive) {
            if (g.waves.length) g.waveSpawnCd = 26;''')

rep(r'''        logUnit(g, "shots");
        sfx(tl.shot === "arrow" ? "throw" : "shot");''',
    r'''        logUnit(g, "shots");
        // [R29] 한나라 궁수 = 2발 일제 사격(살짝 벌어지게)
        const VU = o.unit && UNIT_SPECS[o.unit];
        if (VU && VU.volley > 1) {
          for (let k = 1; k < VU.volley; k++) {
            const sp = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 0.13;
            g.mobShots.push({ x: tl.sx, z: tl.sz + (k % 2 ? 6 : -6), y: mounted ? 76 : 54, vx: (tl.ux - tl.uz * sp) * spd, vz: (tl.uz + tl.ux * sp) * spd, life: Math.ceil(760 / spd), dmg: tl.dmg * 0.8, kind: tl.shot, label: tl.label, src: o.unit });
          }
          logUnit(g, "volley");
        }
        sfx(tl.shot === "arrow" ? "throw" : "shot");''')

rep(r'''ZONE_NAMES.map((zn, zi) => {''', r'''zoneNamesFor(currentEra).map((zn, zi) => {''')

# ───────────────────────── C. 베는 맛 ─────────────────────────
rep(r'''  var HITSTOP_HEAVY = 3.7;
  var HITSTOP_LIGHT = 2;''',
    r'''  // [R29] 손맛 '탁탁' 재조정: 일반 2 → 3f(50ms) · 강타 3.7 → 4.6f(77ms) · 피니시(2연 강타) 6.5f(108ms) · 막타(처치) 5f(83ms)
  var HITSTOP_HEAVY = 4.6;
  var HITSTOP_LIGHT = 3;
  var HITSTOP_FIN = 6.5;
  var HITSTOP_KILL = 5;
  // [R29] Lv.4 질풍연참 연참 수(마지막 일섬 제외)
  var R29_RUSH_HITS = 5;''')

rep(r'''      let hitAny = false;
      let hitBossNow = false;
      let ix = null;
      let iz = 0;
      for (let i = 0; i < g.enemies.length; i++) {''',
    r'''      let hitAny = false;
      let hitBossNow = false;
      let ix = null;
      let iz = 0;
      // [R29] 베기 문맥 — 베기 선 각도 · 칼(SWORD)이면 막타 두 동강 · 처치 수(막타 히트스톱)
      const SC = g._slashCtx = { ang: g._cutAng != null ? g._cutAng : p._atkSrc === "dash" ? 0.06 : p.atkAnim === "atk2" ? -0.46 : 0.5, blade: heroWeaponClass(g.era, g.stats.weaponTier || 1) === "SWORD", kills: 0, n: 0 };
      const finHit = forceCrit && hitCount >= 2;
      for (let i = 0; i < g.enemies.length; i++) {''')

rep(r'''          applyDamageToEnemy(en, dmgRatio, knockX, launchY, hitCount, forceCrit);
          spawnElementHit(en.x, en.z, en.y + 46, forceCrit || hitCount > 1);''',
    r'''          applyDamageToEnemy(en, dmgRatio, knockX, launchY, hitCount, forceCrit);
          spawnElementHit(en.x, en.z, en.y + 46, forceCrit || hitCount > 1);
          if (SC.n++ < 4) pushSlashFx(en.x - p.facing * 4, en.z - en.y - 56 + rand(-12, 10), SC.ang + rand(-0.1, 0.1), p.facing, { heavy: !!en._cut || finHit || hitCount > 1, cross: finHit && !!g._cutCross, len: en._cut ? 270 : null });''')

rep(r'''          applyDamageToEnemy(b, dmgRatio * 1.18, knockX * 0.45, launchY * 0.6, hitCount, forceCrit);
          spawnElementHit(b.x - p.facing * 20, b.z, b.y + 80, forceCrit || hitCount > 1);''',
    r'''          applyDamageToEnemy(b, dmgRatio * 1.18, knockX * 0.45, launchY * 0.6, hitCount, forceCrit);
          spawnElementHit(b.x - p.facing * 20, b.z, b.y + 80, forceCrit || hitCount > 1);
          pushSlashFx(b.x - p.facing * 24, b.z - b.y - 96 + rand(-14, 14), SC.ang, p.facing, { heavy: finHit || hitCount > 1, cross: finHit && !!g._cutCross, len: 300 });''')

rep(r'''        const heavyHit = forceCrit || hitCount >= 2 || p.attackTimer > 0 && p.comboStep >= 3 || hitBossNow;
        g.hitStop = Math.max(g.hitStop, heavyHit ? HITSTOP_HEAVY : HITSTOP_LIGHT);
        addTrauma(heavyHit ? 0.1 + hitCount * 0.04 : 0.03);
        g.kickX += p.facing * (heavyHit ? 2 + hitCount : 1);
        if (heavyHit) kickDirShake(g, p.facing, hitCount >= 2 || forceCrit ? 6 : 5);''',
    r'''        const heavyHit = forceCrit || hitCount >= 2 || p.attackTimer > 0 && p.comboStep >= 3 || hitBossNow;
        // [R29] 손맛 '탁탁' — 일반 3f · 강타 4.6f · 피니시 6.5f · 막타 5f 이상 + 일반 타격에도 짧은 방향 쉐이크 · 흔들림 ↑
        g.hitStop = Math.max(g.hitStop, finHit ? HITSTOP_FIN : heavyHit ? HITSTOP_HEAVY : HITSTOP_LIGHT, SC.kills ? HITSTOP_KILL : 0);
        addTrauma(heavyHit ? 0.12 + hitCount * 0.05 : 0.06);
        g.kickX += p.facing * (heavyHit ? 3 + hitCount : 2);
        kickDirShake(g, p.facing, finHit ? 8 : heavyHit ? hitCount >= 2 || forceCrit ? 6 : 5 : 3);''')

rep(r'''        g.hitStopLog.push({ tick: g.tick, heavy: heavyHit, stop: g.hitStop, step: p.comboStep, boss: hitBossNow });
        if (g.hitStopLog.length > 16) g.hitStopLog.shift();
      }
      return hitAny;
    };''',
    r'''        g.hitStopLog.push({ tick: g.tick, heavy: heavyHit, stop: g.hitStop, step: p.comboStep, boss: hitBossNow, kills: SC.kills, fin: finHit });
        if (g.hitStopLog.length > 16) g.hitStopLog.shift();
      }
      g._slashCtx = null;
      return hitAny;
    };''')

rep(r'''      const heavy = isHeavyMob(target);
      const kMul = target.isMidBoss ? 0.25 : heavy ? 0.55 : 1;''',
    r'''      // [R29] 칼 막타 → 두 동강(일반 몹만) · 처치 수(막타 히트스톱)
      const SC = g._slashCtx;
      if (SC && target.hp <= 0 && target !== g.boss && !target.isMidBoss && !target._cut) {
        SC.kills++;
        if (SC.blade) {
          target._cut = { a: SC.ang + rand(-0.14, 0.14), dir, h: 0.44 + Math.random() * 0.16 };
          g.cutKills = (g.cutKills || 0) + 1;
        }
      }
      const heavy = isHeavyMob(target);
      const kMul = target.isMidBoss ? 0.25 : heavy ? 0.55 : 1;''')

rep(r'''          if (en.hp <= 0 && en.state !== "DYING") {
            en.state = "DYING";
            en.stateTimer = 20;''',
    r'''          if (en.hp <= 0 && en.state !== "DYING") {
            en.state = "DYING";
            // [R29] 두 동강 처치는 조각이 미끄러져 떨어질 시간 26틱
            en.stateTimer = en._cut ? 26 : 20;''')

# 베기 선 · 두 동강 그리기(렌더 범위)
rep(r'''      const drawBreathFx = (g, S) => {''',
    r'''      // [R29] 베기 선 그리기 — 가산 합성: 시대색 번짐(넓은 초승달) + 흰 칼날 심(가는 초승달) + 평행 잔선 2줄 + 선을 따라 튀는 불티 ·
      //  강타는 중심 섬광, 피니시는 X자. 0~16%에 선이 뻗고 이후 가늘어지며 사라진다(히트스톱 동안에도 실제 시간으로 재생)
      const drawSlashFx = (g, S) => {
        const L = g.slashFx;
        if (!L || !L.length || PERF_OFF.particles) return;
        const now = performance.now();
        S.save();
        S.globalCompositeOperation = "lighter";
        S.lineCap = "round";
        for (let i = L.length - 1; i >= 0; i--) {
          const e = L[i];
          const t = (now - e.t0) / e.dur;
          if (t >= 1) {
            L.splice(i, 1);
            continue;
          }
          if (t < 0) continue;
          const grow = Math.min(1, t / 0.16);
          const gq = 1 - (1 - grow) * (1 - grow);
          const fade = t < 0.16 ? 1 : Math.pow(1 - (t - 0.16) / 0.84, 1.5);
          for (let q = 0; q < (e.cross ? 2 : 1); q++) {
            const a = q ? -e.a * 0.85 : e.a;
            const ux = Math.cos(a) * e.dir;
            const uy = Math.sin(a);
            const nx = -uy;
            const ny = ux;
            const len = e.len * (0.3 + 0.7 * gq);
            const x0 = e.x - ux * e.len * 0.5;
            const y0 = e.y - uy * e.len * 0.5;
            const x1 = x0 + ux * len;
            const y1 = y0 + uy * len;
            const mx = (x0 + x1) * 0.5;
            const my = (y0 + y1) * 0.5;
            const w = e.w * (0.45 + 0.55 * fade);
            S.globalAlpha = 0.5 * fade;
            S.fillStyle = e.col;
            S.beginPath();
            S.moveTo(x0, y0);
            S.quadraticCurveTo(mx + nx * w * 2.6, my + ny * w * 2.6, x1, y1);
            S.quadraticCurveTo(mx - nx * w * 1, my - ny * w * 1, x0, y0);
            S.fill();
            S.globalAlpha = fade;
            S.fillStyle = "#ffffff";
            S.beginPath();
            S.moveTo(x0, y0);
            S.quadraticCurveTo(mx + nx * w, my + ny * w, x1, y1);
            S.quadraticCurveTo(mx - nx * w * 0.2, my - ny * w * 0.2, x0, y0);
            S.fill();
            S.globalAlpha = 0.55 * fade;
            S.strokeStyle = "#ffffff";
            S.lineWidth = 1.1;
            S.beginPath();
            S.moveTo(x0 + ux * len * 0.2 + nx * w * 2.8, y0 + uy * len * 0.2 + ny * w * 2.8);
            S.lineTo(x0 + ux * len * 0.8 + nx * w * 2.8, y0 + uy * len * 0.8 + ny * w * 2.8);
            S.moveTo(x0 + ux * len * 0.32 - nx * w * 2.2, y0 + uy * len * 0.32 - ny * w * 2.2);
            S.lineTo(x0 + ux * len * 0.66 - nx * w * 2.2, y0 + uy * len * 0.66 - ny * w * 2.2);
            S.stroke();
          }
          if (e.sp.length && t < 0.85) {
            const ux = Math.cos(e.a) * e.dir;
            const uy = Math.sin(e.a);
            S.globalAlpha = 1 - t / 0.85;
            S.strokeStyle = "#fff4cc";
            S.lineWidth = 2;
            S.beginPath();
            for (let k = 0; k < e.sp.length; k++) {
              const sp = e.sp[k];
              const dd = e.len * sp.d + sp.v * t * 150;
              const px = e.x + ux * dd - uy * sp.s * 22 * t;
              const py = e.y + uy * dd + ux * sp.s * 22 * t + t * t * 34;
              const sl = 12 * (1 - t);
              S.moveTo(px, py);
              S.lineTo(px - ux * sl, py - uy * sl);
            }
            S.stroke();
          }
          if (e.heavy && t < 0.32) {
            const k2 = 1 - t / 0.32;
            const r = 34 * (0.6 + 0.4 * k2);
            S.globalAlpha = k2;
            S.drawImage(getGlowSprite("#fffbe6"), e.x - r, e.y - r, r * 2, r * 2);
          }
        }
        S.restore();
      };
      // [R29] 두 동강 처치 — 칼 막타로 쓰러진 원화 몹을 베인 선(월드 좌표) 위 · 아래로 잘라(클립) 윗몸은 칼 방향으로 미끄러지며 떨어지고
      //  아랫몸은 그 자리에서 스러진다. 조각마다 같은 강체 변환(평행 이동 + 베인 점 기준 회전)을 클립과 그림에 함께 건다
      const drawCutMob = (en, MB, P, S, x, yS, col) => {
        const c = en._cut;
        const e = 1 - Math.max(0, Math.min(1, en.stateTimer / 26));
        const F = frameAssets.cam;
        const lift = (P.lift || 0) * S;
        const fy = yS - lift;
        const cxp = x;
        const cyp = yS - MB.topH * S * c.h;
        const ux = Math.cos(c.a) * c.dir;
        const uy = Math.sin(c.a);
        let nx = -uy;
        let ny = ux;
        if (ny > 0) {
          nx = -nx;
          ny = -ny;
        }
        const R = 420;
        // 위 조각: 틈만큼 떠오른 뒤 칼 방향으로 미끄러지며 떨어지고 기운다 · 아래 조각: 조금 가라앉으며 뒤로 기운다
        const fadeA = e < 0.62 ? 1 : Math.max(0, 1 - (e - 0.62) / 0.38);
        const gap = 3 + 9 * Math.min(1, e * 3);
        const slide = 10 + 70 * Math.pow(e, 0.9);
        const parts = [
          { side: 1, ox: ux * slide + nx * gap, oy: uy * slide + ny * gap + 40 * e * e, r: c.dir * 0.45 * e },
          { side: -1, ox: -ux * 4 * e - nx * gap * 0.4, oy: 6 * e - ny * gap * 0.4, r: -c.dir * 0.1 * e }
        ];
        for (let k = 0; k < 2; k++) {
          const pt = parts[k];
          screen.save();
          screen.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
          applyCam(screen, F);
          screen.translate(-F.camRX, 0);
          screen.translate(cxp + pt.ox, cyp + pt.oy);
          screen.rotate(pt.r);
          screen.translate(-cxp, -cyp);
          screen.beginPath();
          screen.moveTo(cxp - ux * R, cyp - uy * R);
          screen.lineTo(cxp + ux * R, cyp + uy * R);
          screen.lineTo(cxp + ux * R + nx * R * pt.side, cyp + uy * R + ny * R * pt.side);
          screen.lineTo(cxp - ux * R + nx * R * pt.side, cyp - uy * R + ny * R * pt.side);
          screen.closePath();
          screen.clip();
          const vx = x - cxp;
          const vy = fy - cyp;
          const cr = Math.cos(pt.r);
          const sr = Math.sin(pt.r);
          const fx = cxp + pt.ox + vx * cr - vy * sr;
          const fyy = cyp + pt.oy + vx * sr + vy * cr;
          drawAssetActor(MB, P.name, fx, fyy + lift, en.facing, { sx: P.sx * S, sy: P.sy * S, rot: pt.r * en.facing, lift, flash: e < 0.25 ? 0.7 * (1 - e / 0.25) : 0, alpha: fadeA });
          screen.restore();
        }
        // 베인 자리 빛 — 아래 조각 윗면을 따라 흰 심 + 시대색 번짐이 0.5까지 사그라든다
        if (e < 0.5) {
          const k = 1 - e / 0.5;
          const hw = 50 * S;
          const sx0 = cxp - ux * 4 * e - nx * gap * 0.4;
          const sy0 = cyp + 6 * e - ny * gap * 0.4;
          screen.save();
          screen.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
          applyCam(screen, F);
          screen.translate(-F.camRX, 0);
          screen.globalCompositeOperation = "lighter";
          screen.lineCap = "round";
          screen.beginPath();
          screen.moveTo(sx0 - ux * hw, sy0 - uy * hw);
          screen.lineTo(sx0 + ux * hw, sy0 + uy * hw);
          screen.globalAlpha = 0.6 * k;
          screen.strokeStyle = col || "#fde047";
          screen.lineWidth = 10 * k + 2;
          screen.stroke();
          screen.globalAlpha = k;
          screen.strokeStyle = "#ffffff";
          screen.lineWidth = 2.4 * k + 0.6;
          screen.stroke();
          screen.restore();
        }
      };
      const drawBreathFx = (g, S) => {''')

rep(r'''          drawAssetActor(MB, P.name, en.x + shk + en.facing * P.dx * S, en.z - en.y + yOff, en.facing, { sx: P.sx * S, sy: P.sy * S, rot: P.rot - air * 0.45, lift: P.lift * S, flash: en.flashTimer > 0 ? 0.6 * Math.min(1, en.flashTimer / 4) : 0, alpha });''',
    r'''          if (en._cut && dyingT >= 0) {
            drawCutMob(en, MB, P, S, en.x + shk + en.facing * P.dx * S, en.z - en.y + yOff, g.fx && g.fx.glowHex);
            g.cutDrawn = (g.cutDrawn || 0) + 1;
          } else drawAssetActor(MB, P.name, en.x + shk + en.facing * P.dx * S, en.z - en.y + yOff, en.facing, { sx: P.sx * S, sy: P.sy * S, rot: P.rot - air * 0.45, lift: P.lift * S, flash: en.flashTimer > 0 ? 0.6 * Math.min(1, en.flashTimer / 4) : 0, alpha });''')

rep(r'''        if (g.breathFx && g.breathFx.length) overlay.push((o) => drawBreathFx(g, o));''',
    r'''        if (g.breathFx && g.breathFx.length) overlay.push((o) => drawBreathFx(g, o));
        if (g.slashFx && g.slashFx.length) overlay.push((o) => drawSlashFx(g, o));''')

# ───────────────────────── D. 콤보 ─────────────────────────
rep(r'''  var SKILL_LV = { upper: 2, finisher: 3, dashEvo: 3, ultTrue: 5 };''',
    r'''  var SKILL_LV = { upper: 2, finisher: 3, dashEvo: 3, rush: 4, ultTrue: 5 };''')

rep(r'''    2: { kind: "UNLOCK", title: "어퍼컷 · 띄우기 해금", short: "어퍼", key: "L · X", desc: "적을 띄워 공중 콤보로 이어 가세요!",''',
    r'''    2: { kind: "UNLOCK", title: "어퍼컷 · 띄우기 해금", short: "어퍼", key: "L · X", desc: "적을 띄워 공중 콤보로! 공중에서 J 3번 뒤 한 번 더 누르면 내리꽂기(AIR RAID)",''')

rep(r'''desc: "네 번째 타격이 피니시로 폭발하고, 돌진은 잔상을 남기며 더 멀리 · 더 세게!", color: "#38bdf8", color2: "#0ea5e9" },''',
    r'''desc: "네 번째 타격이 피니시로 폭발하고, 돌진은 잔상을 남기며 더 멀리 · 더 세게! 돌진 뒤 J는 곧바로 3타(DASH LINK)", color: "#38bdf8", color2: "#0ea5e9" },
    // [R29] Lv.4 질풍연참
    4: { kind: "EVOLVE", title: "5타 질풍연참", short: "질풍연참", key: "J 5연타", desc: "4타 피니시 직후 J 한 번 더 — 다섯 줄기 연참 뒤 화면을 가르는 일섬!", color: "#f472b6", color2: "#db2777" },''')

rep(r'''    const triggerEraWeaponCombo = () => {''',
    r'''    // [R29] 베기 선 FX 등록 — 월드 x · 화면 y(= z − 높이) · 각도 a(0 = 수평, + = 칼 방향으로 내려 벰) · dir = 칼 방향
    const pushSlashFx = (x, y, a, dir, o = {}) => {
      const g = gameRef.current;
      const L = g.slashFx || (g.slashFx = []);
      if (L.length > 20) L.splice(0, L.length - 20);
      const ns = o.sparks != null ? o.sparks : o.heavy ? 6 : 3;
      const sp = [];
      for (let i = 0; i < ns; i++) sp.push({ d: rand(-0.25, 0.45), v: rand(0.5, 1.4), s: rand(-1, 1) });
      L.push({ t0: performance.now() + (o.delay || 0), dur: o.dur || (o.heavy ? 270 : 200), x, y, a, dir, len: o.len || (o.heavy ? 240 : 175), w: o.w || (o.heavy ? 7.5 : 4.6), col: o.col || g.fx && g.fx.glowHex || "#fde047", heavy: !!o.heavy, cross: !!o.cross, sp });
      g.slashFxCount = (g.slashFxCount || 0) + 1;
    };
    // [R29] Lv.4 질풍연참 — 4타 피니시 직후 J: 7틱 간격 5연참(가벼운 넉백으로 적을 붙잡아 둔다) → 화면을 가르는 일섬(2연 강타 · 볼링 · 슬로우)
    const startRush = () => {
      const g = gameRef.current;
      const p = g.player;
      p.rush = { k: 0 };
      p.comboStep = 0;
      p.comboResetTimer = 0;
      p.bufferAtk = false;
      g.rushes = (g.rushes || 0) + 1;
      if (g.rushes <= 3) addDamagePopup(p.x, p.z, p.y + 118, "5-HIT RUSH!", true, null, 0, "#f472b6");
      rushSlash(1);
    };
    const rushSlash = (k) => {
      const g = gameRef.current;
      const p = g.player;
      if (!p.rush || syncRef.current.gameState !== "PLAYING" || p.downTimer > 0) {
        p.rush = null;
        return;
      }
      const last = k > R29_RUSH_HITS;
      const eObj = relicPal(g, eraObjOf());
      p.rush.k = k;
      p.state = "ATTACK";
      p._atkSrc = "combo";
      p.comboStep = last ? 4 : k % 2 ? 1 : 2;
      p.atkAnim = k % 2 ? "atk1" : "atk2";
      p._fin = last;
      p.maxAttackTimer = last ? 24 : 7;
      p.attackTimer = p.maxAttackTimer;
      p.vx = p.facing * (last ? 30 : 5);
      p.invincibleTimer = Math.max(p.invincibleTimer || 0, last ? 30 : 12);
      sfx(last ? "dash" : "swing");
      if (k === 1) {
        // 첫 연참: 앞쪽 가벼운 적을 칼끝 앞으로 끌어당긴다(피니시 볼링으로 날아간 적까지 — 5연참이 이어지게)
        const tx = p.x + p.facing * 95;
        for (let i = 0; i < g.enemies.length; i++) {
          const en = g.enemies[i];
          if (en.state === "DYING" || en.state === "SPAWN" || en.isMidBoss || en.heavy) continue;
          const dx = (en.x - p.x) * p.facing;
          if (dx < -40 || dx > 340 || Math.abs(en.z - p.z) > 90) continue;
          en.x += (tx - en.x) * 0.7;
          en.z += (p.z - en.z) * 0.5;
          en.vx = 0;
          en.thrown = null;
          en.hitStun = Math.max(en.hitStun || 0, 20);
        }
      }
      if (last) {
        for (let i = 0; i < 8; i++) p.ghosts.push({ x: p.x - p.facing * i * 24, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i % 6, alpha: 0.8 - i * 0.09, evo: true, col: eObj.bladeGlow });
        g.targetZoom = 1.09;
        g.speedlineAlpha = 0.6;
      }
      queueActiveFrame(last ? 4 : 2, () => {
        const g2 = gameRef.current;
        const pp = g2.player;
        g2._comboStep = last ? 4 : 2;
        if (last) {
          g2._cutAng = 0.03;
          g2._cutCross = false;
          g2._bowlFin = true;
          checkMeleeHitbox(300, 84, 2.6, 18, 10, 2, true);
          g2._bowlFin = false;
          g2.hitStop = Math.max(g2.hitStop, HITSTOP_FIN);
          pushSlashFx(pp.x + pp.facing * 140, pp.z - pp.y - 58, 0.02, pp.facing, { len: 980, w: 10, dur: 430, heavy: true, sparks: 10 });
          breathFX(2, 0);
          g2.slowMo = Math.max(g2.slowMo || 0, 14);
          g2.flashAlpha = Math.max(g2.flashAlpha, 0.32);
          g2.flashColor = "#ffffff";
          addTrauma(0.35);
          addDamagePopup(pp.x, pp.z, pp.y + 120, "RUSH FINISH!", true, null, 0, "#f472b6");
          addTimer(18, () => {
            gameRef.current.targetZoom = 1;
          });
          g2.rushFinishes = (g2.rushFinishes || 0) + 1;
          pp.rush = null;
          pp.comboStep = 0;
        } else {
          g2._cutAng = (k % 2 ? 0.52 : -0.48) + rand(-0.12, 0.12);
          checkMeleeHitbox(190, 68, 0.6, 2.5, 0, 1, false);
          if (k === 3) breathFX(1, 0.35);
        }
        g2._cutAng = null;
        g2._comboStep = 0;
      }, false);
      if (!last) addTimer(7, () => rushSlash(k + 1));
    };
    // [R29] 내리꽂기(AIR RAID) 착지 — 주변 원형 충격: 2연 강타 + 띄우기 · 세로 베기 선(칼이면 막타 두 동강) · 피니시 히트스톱
    const airRaidImpact = () => {
      const g = gameRef.current;
      const p = g.player;
      const eObj = relicPal(g, eraObjOf());
      p.maxAttackTimer = 16;
      p.attackTimer = 9;
      p._fin = true;
      p.vx = 0;
      p.landSquash = 14;
      g._slashCtx = { ang: -1.3, blade: heroWeaponClass(g.era, g.stats.weaponTier || 1) === "SWORD", kills: 0, n: 0 };
      let hits = 0;
      for (let i = 0; i < g.enemies.length; i++) {
        const en = g.enemies[i];
        if (en.state === "DYING" || en.state === "SPAWN") continue;
        const dx = en.x - p.x;
        if (Math.abs(dx) > 200 || Math.abs(en.z - p.z) > 76) continue;
        const d = dx >= 0 ? 1 : -1;
        applyDamageToEnemy(en, 1.9, 9, 10.5, 2, true, d);
        if (hits++ < 5) pushSlashFx(en.x, en.z - en.y - 56, -1.3 + rand(-0.15, 0.15), d, { heavy: true, len: en._cut ? 250 : 190 });
      }
      if (g.bossActive && g.boss && !g.boss.dying && Math.abs(g.boss.x - p.x) <= 240 && Math.abs(g.boss.z - p.z) <= 110) {
        applyDamageToEnemy(g.boss, 2.1, 2, 3, 2, true, g.boss.x >= p.x ? 1 : -1);
        hits++;
      }
      g._slashCtx = null;
      addShock(p.x, p.z, eObj.bladeGlow, 210, 22);
      addGroundCraterDecal(p.x, p.z, 92);
      spawnDust(p.x, p.z, 14, 4.4);
      spawnShards(p.x, p.z, 10, 14, p.facing);
      addLight(p.x, p.z, 24, 170, eObj.bladeGlow, 1, 14);
      addTrauma(0.5);
      kickDirShake(g, p.facing, 7);
      g.hitStop = Math.max(g.hitStop, hits ? HITSTOP_FIN : 3);
      g.flashAlpha = Math.max(g.flashAlpha, 0.28);
      g.flashColor = "#ffffff";
      pushSlashFx(p.x, p.z - 26, 0, p.facing, { len: 420, w: 6, dur: 320, heavy: true, sparks: 8 });
      addDamagePopup(p.x, p.z, 124, "AIR RAID!", true, hits ? hits + " HIT" : null, 0, "#fde047");
      sfx("hitHeavy");
      g.airRaids = (g.airRaids || 0) + 1;
    };
    const triggerEraWeaponCombo = () => {''')

rep(r'''      g.lastAtkPress = g.tick;
      if (p.guardTimer > 0) return;''',
    r'''      g.lastAtkPress = g.tick;
      if (p.rush || p.plunge) return;
      if (p.guardTimer > 0) return;''')

rep(r'''      if (p.y > 10) {
        p.maxAttackTimer = 12;
        p.attackTimer = 12;
        p.state = "ATTACK";
        p.atkAnim = "atk1";
        p._atkSrc = "air";
        p._fin = false;
        p.vy = Math.max(p.vy, 3.8);
        queueActiveFrame(3, () => checkMeleeHitbox(155, 62, 1.3, 6, 7.5, 1, false));
        return;
      }''',
    r'''      if (p.y > 10) {
        // [R29] 공중 연참: 1~3타는 번갈아 베며 체공 → 4번째 J는 내리꽂기(AIR RAID) — 착지 충격파가 주변 적을 쓸어 띄운다
        p.airHits = (p.airHits || 0) + 1;
        if (p.airHits >= 4) {
          p.airHits = 0;
          p.plunge = true;
          p.maxAttackTimer = 40;
          p.attackTimer = 40;
          p.state = "ATTACK";
          p.atkAnim = "atk2";
          p._atkSrc = "air";
          p._fin = true;
          p.vy = -22;
          p.vx = p.facing * 4;
          p.invincibleTimer = Math.max(p.invincibleTimer || 0, 34);
          sfx("dash");
          pushSlashFx(p.x + p.facing * 30, p.z - p.y - 40, 1.45, p.facing, { len: 200, w: 5, dur: 240, sparks: 4 });
          return;
        }
        const ah = p.airHits;
        p.maxAttackTimer = 12;
        p.attackTimer = 12;
        p.state = "ATTACK";
        p.atkAnim = ah % 2 ? "atk1" : "atk2";
        p._atkSrc = "air";
        p._fin = false;
        p.vy = Math.max(p.vy, 3.8);
        queueActiveFrame(3, () => {
          const g2 = gameRef.current;
          g2._cutAng = ah % 2 ? 0.55 : -0.42;
          checkMeleeHitbox(155, 62, 1.3 + ah * 0.08, 6, 7.5, 1, ah === 3);
          g2._cutAng = null;
        });
        return;
      }''')

rep(r'''      // [R24] Lv.1~2는 3단 콤보, Lv.3부터 4타 피니시 개방
      p.comboStep = p.comboStep % (g.stats.level >= SKILL_LV.finisher ? 4 : 3) + 1;''',
    r'''      // [R29] Lv.4 질풍연참: 4타 피니시 직후 J 한 번 더 → 다섯 줄기 연참 + 화면을 가르는 일섬
      if (p.comboStep === 4 && p.comboResetTimer > 0 && g.stats.level >= SKILL_LV.rush) {
        startRush();
        return;
      }
      // [R29] 돌진 → J 연결(DASH LINK): 돌진 중 · 직후(약 0.55초) J는 곧바로 3타(강타)로 이어진다
      let dashLink = false;
      if (p._atkSrc === "dash" && g.tick - (p._dashTick != null ? p._dashTick : -99) <= 34) {
        p.comboStep = 2;
        dashLink = true;
      }
      // [R24] Lv.1~2는 3단 콤보, Lv.3부터 4타 피니시 개방
      p.comboStep = p.comboStep % (g.stats.level >= SKILL_LV.finisher ? 4 : 3) + 1;''')

rep(r'''      const step = p.comboStep;
      p._atkSrc = "combo";
      p._fin = step === 4;''',
    r'''      const step = p.comboStep;
      p._atkSrc = "combo";
      p._fin = step === 4;
      if (dashLink) {
        g.dashLinks = (g.dashLinks || 0) + 1;
        if (g.dashLinks <= 3) addDamagePopup(p.x, p.z, p.y + 110, "DASH LINK!", true, null, 0, "#22d3ee");
      }''')

rep(r'''        g._bowlFin = isFinisher;
        g._comboStep = step;
        if (cls === "AXE") {''',
    r'''        g._bowlFin = isFinisher;
        g._comboStep = step;
        // [R29] 베기 선 각도: 1타 사선 내려베기 · 2타 올려베기 · 3타 수평 · 4타 가파른 사선 + X자
        g._cutAng = isFinisher ? 0.82 : step === 3 ? 0.08 : step === 2 ? -0.46 : 0.5;
        g._cutCross = isFinisher;
        if (cls === "AXE") {''')

rep(r'''        g._bowlFin = false;
        g._comboStep = 0;
      });
    };
    const triggerEraDashSkill = () => {''',
    r'''        g._bowlFin = false;
        g._comboStep = 0;
        g._cutAng = null;
        g._cutCross = false;
      });
    };
    const triggerEraDashSkill = () => {''')

rep(r'''      if (p.cdDash > 0) return;
      const eObj = relicPal(g, eraObjOf());
      const evo = g.stats.level >= SKILL_LV.dashEvo;
      p.cdDash = 150;''',
    r'''      if (p.cdDash > 0 || p.rush || p.plunge) return;
      const eObj = relicPal(g, eraObjOf());
      const evo = g.stats.level >= SKILL_LV.dashEvo;
      p.cdDash = 150;
      p._dashTick = g.tick;''')

rep(r'''          if (p.y <= 0) {
            p.y = 0;
            p.vy = 0;
            if (p.prevY > 4) {''',
    r'''          if (p.y <= 0) {
            p.y = 0;
            p.vy = 0;
            // [R29] 공중 연참 횟수 초기화 · 내리꽂기(AIR RAID) 착지 충격
            p.airHits = 0;
            if (p.plunge) {
              p.plunge = false;
              airRaidImpact();
            }
            if (p.prevY > 4) {''')

# 검증 훅: 시작 화면 로딩 가림막 상태
rep(r'''          stageToast: (t) => setStageToast(t),''',
    r'''          // [R29] 시작 화면 로딩 가림막 상태(검증용)
          titleGate: () => Object.assign({}, TITLE_GATE, titleGate(), { info: eraLoadInfo(1), label: titleLoadLabel() }),
          stageToast: (t) => setStageToast(t),''')

open(P, "w", encoding="utf-8").write(s)
print("R29 patch ok —", n, "edits")
