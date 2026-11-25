#!/usr/bin/env python3
"""R27 패치 c — 수묵 호흡 가독성: 피니시 · 어퍼 · 돌진에 굵은 먹 붓질 초승달(붓이 지나가듯 80ms에 그어짐) + 먹물 비산 1.35배."""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()


def rep(old, new):
    global s
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"anchor count {c}: {old[:90]!r}")
    s = s.replace(old, new)


# 1) 그리기: inkarc(먹 붓질 초승달) — 끝이 가늘어지는 띠 + 마른 붓결 2줄
rep('''          } else if (e.k === "bolt") {
            screen.save();
            screen.globalCompositeOperation = "lighter";''', '''          } else if (e.k === "inkarc") {
            const sw = Math.min(1, t * 5.5);
            const n = 20;
            const A0 = e.a0;
            const A1 = e.a0 + (e.a1 - e.a0) * sw;
            screen.save();
            screen.translate(e.x, e.y);
            screen.scale(e.dir, 1);
            screen.rotate(e.rot);
            screen.globalAlpha = Math.min(1, a * 1.6) * 0.92;
            screen.fillStyle = "#07070b";
            screen.beginPath();
            for (let k = 0; k <= n; k++) {
              const an = A0 + (A1 - A0) * k / n;
              screen.lineTo(Math.cos(an) * e.r, Math.sin(an) * e.r);
            }
            for (let k = n; k >= 0; k--) {
              const u = k / n;
              const an = A0 + (A1 - A0) * u;
              const th = e.w * Math.pow(Math.sin(Math.PI * Math.min(1, u * 1.08)), 0.65) * (0.55 + 0.45 * sw);
              screen.lineTo(Math.cos(an) * (e.r - th), Math.sin(an) * (e.r - th));
            }
            screen.closePath();
            screen.fill();
            screen.globalAlpha = Math.min(1, a * 1.6) * 0.55;
            screen.strokeStyle = "#3b3550";
            screen.lineWidth = 1.4;
            for (let j = 1; j <= 2; j++) {
              screen.beginPath();
              screen.arc(0, 0, e.r - e.w * (0.25 + 0.22 * j), A0 + 0.25, Math.max(A0 + 0.26, A1 - 0.3));
              screen.stroke();
            }
            screen.restore();
          } else if (e.k === "bolt") {
            screen.save();
            screen.globalCompositeOperation = "lighter";''')
# 2) 생성: breathFX(power, rot) — power 2(피니시 · 어퍼 · 돌진)에 붓질 초승달, 비산 먹물 1.35배
rep('''    const breathFX = (power = 1) => {''', '''    const breathFX = (power = 1, rot = 0.35) => {''')
rep('''rot: ang + rand(-0.4, 0.4), vr: rand(-0.03, 0.03), len: rand(16, 44) * (power > 1 ? 1.2 : 1), w: rand(3, 7.5), c:''',
    '''rot: ang + rand(-0.4, 0.4), vr: rand(-0.03, 0.03), len: rand(22, 58) * (power > 1 ? 1.2 : 1), w: rand(4, 10), c:''')
rep('''      if (B.kind === "flame") {
        for (let i = 0; i < 10 * qm; i++) spawnPart({ kind: "EMBER", x: hx + rand(-30, 30)''', '''      if (power > 1) L.push({ k: "inkarc", t0: now, dur: 470, x: p.x + p.facing * 34, y: hy - 4, dir: p.facing, rot, a0: -1.45, a1: 1.25, r: 108, w: 30 });
      if (B.kind === "flame") {
        for (let i = 0; i < 10 * qm; i++) spawnPart({ kind: "EMBER", x: hx + rand(-30, 30)''')
# 어퍼는 위로 올려 긋고(−1.1) · 돌진은 수평으로(0.05)
rep('''        breathFX(2);
        checkMeleeHitbox(205, 74, 1.9, 8.5, 16, 3, true);''', '''        breathFX(2, -1.1);
        checkMeleeHitbox(205, 74, 1.9, 8.5, 16, 3, true);''')
rep('''        breathFX(2);
        if (evo) {''', '''        breathFX(2, 0.05);
        if (evo) {''')
open(P, "w", encoding="utf-8").write(s)
print("R27 patch c ok")
