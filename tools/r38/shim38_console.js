// [R38] built-in 브라우저 콘솔용 공통 shim + 도우미 — func38_console.js · load38_console.js 보다 먼저 붙여 넣는다(window.__R38S).
//  왜: 데스크톱 앱의 브라우저 창(pane)이 가려지면 ① 게임이 document.hidden을 보고 자동 일시정지하고 ② requestAnimationFrame이 멈춰
//      시간 기준 테스트가 전부 깨진다(R38-handoff.md 5절). 또 자동 일시정지는 '재개' 버튼(trusted click)으로만 풀리는 때가 있다.
//  무엇: ① rAF 대체 — 창이 보이면 실제 rAF(120ms 안에 안 오면 타이머로), 가려지면 16.67ms 간격 타이머(게임 루프가 계속 돈다)
//        ② visibilitychange · blur · pagehide 캡처 차단(자동 일시정지 방지) ③ setHalt(true) — 루프 정지(다른 탭을 잴 때 CPU를 비움)
//        ④ 도우미 — sleep · key/press(document에 dispatch → window까지 버블) · waitFor · waitTicks(게임 틱 기준) · start(Enter) · toEra ·
//           waitVisible(기본 최대 10초 · 부하 측정은 창이 보일 때만 유효) · resume('재개' 버튼 click)
//  측정값 해석: S.real(실제 rAF 콜백 수) · S.timer(타이머 콜백 수) — 부하 측정 중 timer가 0이고 visibilityState가 visible이어야 유효.
(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let S = window.__r38shim;
  if (!S) {
    const raf0 = window.requestAnimationFrame.bind(window);
    const caf0 = window.cancelAnimationFrame.bind(window);
    S = window.__r38shim = { real: 0, timer: 0, blocked: 0, last: performance.now(), Q: [], t: null, H: [], halt: false };
    const fire = () => {
      S.t = null;
      const cbs = S.Q.splice(0);
      S.last = performance.now();
      S.timer++;
      for (const cb of cbs) {
        try {
          cb(S.last);
        } catch (e) {
          console.error(e);
        }
      }
    };
    const hybrid = (cb) => {
      if (document.visibilityState === "visible") {
        let done = false;
        const id = raf0((t) => {
          if (done) return;
          done = true;
          clearTimeout(wd);
          S.real++;
          S.last = performance.now();
          cb(t);
        });
        const wd = setTimeout(() => {
          if (done) return;
          done = true;
          caf0(id);
          S.Q.push(cb);
          if (!S.t) S.t = setTimeout(fire, 0);
        }, 120);
        return id;
      }
      S.Q.push(cb);
      if (!S.t) S.t = setTimeout(fire, Math.max(0, S.last + 16.667 - performance.now()));
      return 0;
    };
    window.requestAnimationFrame = (cb) => {
      if (S.halt) {
        S.H.push(cb);
        return 0;
      }
      return hybrid(cb);
    };
    S.setHalt = (v) => {
      S.halt = !!v;
      if (!S.halt) {
        const cbs = S.H.splice(0);
        for (const cb of cbs) hybrid(cb);
      }
      return S.halt;
    };
    const block = (e) => {
      if (e.type !== "visibilitychange" || document.visibilityState === "hidden") {
        S.blocked++;
        e.stopImmediatePropagation();
      }
    };
    for (const t of ["visibilitychange", "blur", "pagehide"]) {
      document.addEventListener(t, block, true);
      window.addEventListener(t, block, true);
    }
  }
  const key = (k, code, kc, type) => document.dispatchEvent(new KeyboardEvent(type, { key: k, code, keyCode: kc, which: kc, bubbles: true }));
  const press = async (k, code, kc, hold = 30) => {
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
  const waitTicks = async (n, maxMs = 15000) => {
    const g = G();
    const t0 = g.tick;
    const p0 = performance.now();
    while (g.tick - t0 < n && performance.now() - p0 < maxMs) await sleep(16);
    return g.tick - t0;
  };
  const resume = () => {
    const b = [...document.querySelectorAll("button")].find((x) => x.innerText.trim() === "재개");
    if (b) b.click();
    return !!b;
  };
  const start = async () => {
    await waitFor(() => G() && D(), 30000);
    if (!(G().player && G().stats && G().tick > 30)) {
      await press("Enter", "Enter", 13, 40);
      await waitFor(() => G().player && G().stats && G().tick > 30);
    }
    resume();
  };
  const toEra = async (era) => {
    for (let i = 0; i < 8 && G().era < era; i++) {
      D().advance();
      await sleep(400);
    }
    return await waitFor(() => ["ready", "none", "failed"].includes(D().assets.status(era)), 60000);
  };
  // 창이 보이고 실제 rAF가 0.5초에 18번 이상 오면 true. 기본 10초까지만 기다린다(토큰 · 시간 낭비 방지)
  const waitVisible = async (maxMs = 10000) => {
    const p0 = performance.now();
    while (performance.now() - p0 < maxMs) {
      const r0 = S.real;
      const t0 = S.timer;
      await sleep(500);
      if (document.visibilityState === "visible" && S.real - r0 >= 18 && S.timer - t0 === 0) return true;
    }
    return false;
  };
  window.__R38S = { S, sleep, key, press, G, D, waitFor, waitTicks, start, toEra, waitVisible, resume };
  return "R38S ready";
})();
