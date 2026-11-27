#!/usr/bin/env python3
"""R34 척준경 옷 통일 — R32 새 원화(질주 8 · 무신 4: 갈색 소매 · 치마 천의 찰갑)를 옛 원화(흑철 비늘갑)의 색 계열로 맞춘다.

방법(그림은 그대로 · 색만):
  ① 살색(얼굴 · 주먹 · 목)을 먼저 가려 둔다 — '확실한 살색'을 씨앗으로 이웃한 '살색일 수 있는' 픽셀로 번져 나감
  ② 살색이 아닌 따뜻한 색(갈색 · 카키 천 · 가죽 · 테두리)의 채도를 낮추고(KEEP) 어둡게(DARK) 한 뒤 옛 갑옷의 찬 먹빛을 살짝 섞는다(COOL)
  ③ 이미 어둡거나 무채색인 곳(쇠 찰갑 · 목도리 · 머리카락)은 건드리지 않는다
사용: python3 -I cjg_regrade.py <원본 폴더> <출력 폴더> [KEEP=0.3] [DARK=0.66] [COOL=0.5] [프레임,...]
"""
import os
import sys

import numpy as np
from PIL import Image

SRC, DST = sys.argv[1:3]
KEEP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
DARK = float(sys.argv[4]) if len(sys.argv) > 4 else 0.66
COOL = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
FR = sys.argv[6].split(',') if len(sys.argv) > 6 else ['run', 'run2', 'run3', 'run4', 'run5', 'run6', 'run7', 'run8', 'cleave_prep', 'cleave_hit', 'charge', 'dragon_stance']
os.makedirs(DST, exist_ok=True)


def hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rm = m & (mx == r)
    gm = m & (mx == g) & ~rm
    bm = m & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    return h * 60, np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0), mx


def dilate(m, it):
    for _ in range(it):
        e = m.copy()
        e[1:, :] |= m[:-1, :]
        e[:-1, :] |= m[1:, :]
        e[:, 1:] |= m[:, :-1]
        e[:, :-1] |= m[:, 1:]
        m = e
    return m


def blur(a, it=2):
    for _ in range(it):
        p = np.pad(a, 1, mode='edge')
        a = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:] + p[1:-1, 1:-1] * 2) / 6
    return a


for n in FR:
    im = Image.open(f"{SRC}/era4_hero_{n}.webp").convert('RGBA')
    a = np.asarray(im).astype(np.float64) / 255
    rgb = a[..., :3]
    al = a[..., 3]
    H, S, V = hsv(rgb)
    opaque = al > 0.05
    # ① 살색
    seed = opaque & (H >= 8) & (H <= 30) & (S >= 0.24) & (S <= 0.62) & (V >= 0.6)
    maybe = opaque & (H >= 4) & (H <= 34) & (S >= 0.16) & (S <= 0.7) & (V >= 0.3)
    skin = seed.copy()
    for _ in range(14):
        skin = dilate(skin, 1) & maybe
    skin = dilate(skin, 1) & opaque                      # 외곽선 쪽 1px 여유
    # ② 따뜻한 천 · 가죽
    warm = opaque & ~skin & (H >= 8) & (H <= 62) & (S >= 0.1) & (V >= 0.12)
    w = blur(warm.astype(np.float64), 2) * warm              # 경계 부드럽게
    w *= np.clip((S - 0.08) / 0.14, 0, 1)                    # 채도가 낮은 곳일수록 덜 건드림
    lum = (rgb * [0.299, 0.587, 0.114]).sum(-1, keepdims=True)
    cool = lum * np.array([0.86, 0.95, 1.08])                # 옛 흑철의 찬 먹빛
    gray = lum * (1 - COOL) + cool * COOL
    tgt = (gray + (rgb - lum) * KEEP) * DARK
    out = rgb * (1 - w[..., None]) + tgt * w[..., None]
    res = np.dstack([np.clip(out, 0, 1), al])
    Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA').save(f"{DST}/era4_hero_{n}.webp", lossless=True, method=6, exact=True)  # 원본도 무손실 → 화질 손실 없음
    print(n, 'skin px', int(skin.sum()), 'warm px', int(warm.sum()), 'of', int(opaque.sum()))
