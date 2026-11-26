#!/usr/bin/env python3
"""R30 입력 원화 검수 — 크기 · 알파 · 맨 위/맨 아래 불투명 행 · 흰 매트 번짐 · 윗몸 중심(idle 대비 가로 상관)."""
import sys
import numpy as np
from PIL import Image


def stats(p):
    im = Image.open(p)
    a = np.asarray(im.convert("RGBA")).astype(np.int32)
    al = a[..., 3]
    ys, xs = np.nonzero(al > 8)
    rgb = a[..., :3]
    edge = (al > 8) & (al < 200)
    white = int(((rgb.min(-1) > 225) & edge).sum())
    return im.size, im.mode, int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max()), white, al


def upper_cx(al, top, h=150):
    band = (al[top:top + h] > 60).astype(np.float32)
    col = band.sum(0)
    xs = np.arange(col.size)
    return float((col * xs).sum() / max(1, col.sum()))


def xcorr_shift(a0, a1, top, h=150, rng=60):
    b0 = (a0[top:top + h] > 60).astype(np.float32).sum(0)
    b1 = (a1[top:top + h] > 60).astype(np.float32).sum(0)
    best, bs = -1, 0
    for s in range(-rng, rng + 1):
        c = float((b0 * np.roll(b1, s)).sum())
        if c > best:
            best, bs = c, s
    return bs


mode = sys.argv[1]
paths = sys.argv[2:]
if mode == "run":
    idle = paths[0]
    s0 = stats(idle)
    print("idle", s0[:7], "upperCX", round(upper_cx(s0[7], s0[2]), 1))
    for p in paths[1:]:
        s = stats(p)
        print(p.split("/")[-1], s[:7], "upperCX", round(upper_cx(s[7], s[2]), 1), "shift_vs_idle", xcorr_shift(s0[7], s[7], min(s0[2], s[2])))
else:
    for p in paths:
        s = stats(p)
        print(p.split("/")[-1], s[:7], "upperCX", round(upper_cx(s[7], s[2]), 1))
