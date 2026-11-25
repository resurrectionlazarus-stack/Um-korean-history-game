#!/usr/bin/env python3
"""R27 2차 성능 — 수묵 호흡을 마지막 합성 뒤 HD 오버레이에서 그려 프레임당 저해상도 층 전체 합성(flushLo) 1회를 줄인다."""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
a = s.index("      const drawBreathFx = (g) => {")
b = s.index("\n      };\n", a) + len("\n      };\n")
body = s[a:b]
head_old = """      const drawBreathFx = (g) => {
        const L = g.breathFx;
        if (!L || !L.length || PERF_OFF.particles) return;
        const now = performance.now();
        const F = frameAssets.cam;
        screen.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
        screen.save();
        applyCam(screen, F);
        screen.translate(-F.camRX, 0);
"""
assert body.startswith(head_old), "head mismatch"
head_new = """      // [R27 2차] S = 마지막 합성 뒤 HD 오버레이 컨텍스트(카메라 변환이 이미 걸려 있음)
      const drawBreathFx = (g, S) => {
        const L = g.breathFx;
        if (!L || !L.length || PERF_OFF.particles) return;
        const now = performance.now();
        const F = frameAssets.cam;
        S.save();
"""
tail_old = """        screen.restore();
      };
"""
assert body.endswith(tail_old), "tail mismatch"
mid = body[len(head_old):-len(tail_old)].replace("screen.", "S.")
new_body = head_new + mid + """        S.restore();
      };
"""
s = s[:a] + new_body + s[b:]
old_call = """        if (g.breathFx && g.breathFx.length) {
          flushLo();
          drawBreathFx(g);
        }
"""
assert s.count(old_call) == 1, "call anchor"
s = s.replace(old_call, """        // [R27 2차] 수묵 호흡은 마지막 합성 뒤 HD 오버레이에서(피해 숫자 아래) — 프레임당 저해상도 층 전체 합성 · 지우기 1회 절약
        if (g.breathFx && g.breathFx.length) overlay.push((o) => drawBreathFx(g, o));
""")
assert "screen." not in new_body
open(P, "w", encoding="utf-8").write(s)
print("R27 2차 perf patch ok —", mid.count("S."), "draw calls moved to overlay context")
