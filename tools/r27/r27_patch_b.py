#!/usr/bin/env python3
"""R27 패치 b — 검증용 표식 2개(영웅 링 그린 틱 · 전경 층 그린 틱). 실행 비용: 대입 1회."""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()


def rep(old, new):
    global s
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"anchor count {c}: {old[:90]!r}")
    s = s.replace(old, new)


rep('''      const drawHeroRing = (g, p, HA, onScreen) => {
        const col = R27_RING[g.era] || "#fde047";''', '''      const drawHeroRing = (g, p, HA, onScreen) => {
        g.ringTick = g.rtick;
        const col = R27_RING[g.era] || "#fde047";''')
rep('''        if (!PERF_OFF.fg && !R27_FG_OFF[g.era]) drawForegroundLayer(ctx, bd, camRX);''', '''        if (!PERF_OFF.fg && !R27_FG_OFF[g.era]) {
          drawForegroundLayer(ctx, bd, camRX);
          g.fgTick = g.rtick;
        }''')
open(P, "w", encoding="utf-8").write(s)
print("R27 patch b ok")

# [R27] 선녀 발밑 원(시대색)을 옅게 — 주인공 영웅 링과 헷갈리지 않게(0.55 → 0.3)
s = open(P, encoding="utf-8").read()
rep('''        ctx.rotate(cp.auraAngle);
        ctx.globalCompositeOperation = "lighter";
        ctx.strokeStyle = eObj.bladeGlow;
        ctx.lineWidth = 2.2;
        ctx.globalAlpha = 0.55;''', '''        ctx.rotate(cp.auraAngle);
        ctx.globalCompositeOperation = "lighter";
        ctx.strokeStyle = eObj.bladeGlow;
        ctx.lineWidth = 2.2;
        // [R27] 주인공 영웅 링과 헷갈리지 않게 선녀 발밑 원은 옅게(0.55 → 0.3)
        ctx.globalAlpha = 0.3;''')
open(P, "w", encoding="utf-8").write(s)
print("R27 patch b (fairy ring) ok")
