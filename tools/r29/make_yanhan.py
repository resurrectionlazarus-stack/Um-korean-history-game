#!/usr/bin/env python3
"""R29 2시대 연나라 · 한나라 병사 임시 원화(디자인팀 부재 대체본).

원본 고조선 창병 · 궁수(assets/mob/era2_pike_* · era2_archer_*)를 바탕으로
- 얼굴 · 손 · 나무 자루(피부 · 나무 마스크 → 연결 덩어리 80px 이상만)는 그대로 두고
- 나머지(갑옷 · 옷)를 밝기 기준 색 지도(gradient map)로 다시 칠한다.
  연나라 = 남색 쇠미늘 · 한나라 = 흑칠 갑옷 + 붉은 전포(한의 붉은 깃발)
- 한나라 창(극)에는 붉은 술(紅纓) · 극(戟)의 곁날, 철갑 극병에는 투구 붉은 깃털을 더 그린다.
사용: python3 -I make_yanhan.py <assets/mob 폴더> <출력 폴더>
"""
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
POSES = ["idle", "walk", "atk"]

PAL = {
    # (밝기, RGB) — 어두운 쪽은 거의 검정, 가운데가 진영 색
    "yan": [(0.0, (6, 8, 12)), (0.12, (16, 24, 36)), (0.28, (36, 58, 82)), (0.45, (70, 98, 122)), (0.7, (150, 166, 176)), (1.0, (232, 236, 236))],
    "han": [(0.0, (8, 5, 5)), (0.14, (20, 9, 9)), (0.28, (66, 15, 13)), (0.44, (146, 30, 24)), (0.68, (204, 104, 66)), (1.0, (244, 212, 176))],
    "elite": [(0.0, (5, 4, 5)), (0.16, (18, 14, 16)), (0.3, (44, 34, 34)), (0.44, (128, 22, 20)), (0.66, (206, 92, 54)), (1.0, (248, 222, 170))],
}


def hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def keep_mask(a):
    rgb = a[..., :3]
    h, s, v = hsv(rgb)
    raw = (h > 0.0) & (h < 0.1) & (s > 0.28) & (s < 0.75) & (v > 0.42) & (rgb[..., 0] - rgb[..., 2] > 0.16) & (a[..., 3] > 0.5)
    H, W = raw.shape
    seen = np.zeros_like(raw)
    keep = np.zeros_like(raw)
    ys, xs = np.nonzero(raw)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        comp = []
        while q:
            y, x = q.popleft()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and raw[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        q.append((yy, xx))
        if len(comp) >= 80:
            for y, x in comp:
                keep[y, x] = True
    m = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    return np.asarray(m).astype(np.float32) / 255


def gmap(L, pal):
    xs = np.array([p[0] for p in pal])
    out = np.zeros(L.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(L, xs, np.array([p[1][c] for p in pal], np.float32) / 255)
    return out


def recolor(a, faction):
    rgb = a[..., :3]
    L = (0.3 * rgb[..., 0] + 0.59 * rgb[..., 1] + 0.11 * rgb[..., 2])
    L = np.clip(L * 1.08, 0, 1)
    mapped = gmap(L, PAL[faction])
    mapped = mapped * 0.88 + rgb * 0.12
    w = keep_mask(a)[..., None]
    out = a.copy()
    out[..., :3] = rgb * w + mapped * (1 - w)
    return out


def spear_head(a):
    """창날(밝은 청동 · 금빛 덩어리)의 끝점 T와 뿌리 S — 오른쪽 40% 영역에서."""
    rgb = a[..., :3]
    h, s, v = hsv(rgb)
    H, W = h.shape
    m = (h > 0.05) & (h < 0.14) & (s > 0.35) & (v > 0.45) & (a[..., 3] > 0.6)
    m[:, : int(W * 0.62)] = False
    ys, xs = np.nonzero(m)
    if len(xs) < 20:
        return None
    pts = np.stack([xs, ys], 1).astype(np.float32)
    c = pts.mean(0)
    u, sv, vt = np.linalg.svd(pts - c, full_matrices=False)
    ax = vt[0]
    if ax[0] < 0:
        ax = -ax
    t = (pts - c) @ ax
    T = c + ax * t.max()
    S = c + ax * t.min()
    return T, S, ax


def draw_extras(img, a, faction, kind):
    if kind != "pike":
        return img
    sh = spear_head(a)
    if sh is None:
        return img
    T, S, ax = sh
    K = 4
    big = Image.new("RGBA", (img.width * K, img.height * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    perp = np.array([ax[1], -ax[0]])  # 자루에 수직(화면 위쪽)
    if perp[1] > 0:
        perp = -perp
    if faction in ("han", "elite"):
        # 극(戟)의 곁날: 창날 뿌리 조금 뒤에서 위로 휘는 낫 모양 날
        base = S - ax * 6
        p0 = base + ax * 5
        p1 = base - ax * 7
        tip = base + perp * 40 + ax * 14
        ctrl = base + perp * 26 + ax * 2
        poly = [tuple(p0 * K), tuple((base + perp * 18 + ax * 9) * K), tuple(tip * K), tuple((ctrl - ax * 6) * K), tuple(p1 * K)]
        d.polygon(poly, fill=(58, 54, 58, 255), outline=(14, 12, 14, 255), width=K * 2)
        d.line([tuple((base + perp * 10 + ax * 6) * K), tuple((tip - ax * 1) * K)], fill=(176, 172, 160, 255), width=K * 2)
        # 붉은 술(紅纓): 창날 뿌리에서 아래로 늘어진 털 9가닥
        rng = np.random.default_rng(7)
        root = S - ax * 3
        for i in range(13):
            ln = 42 + rng.uniform(-8, 10)
            sway = rng.uniform(-9, 9)
            pts = []
            for k in range(8):
                f = k / 7
                p = root + np.array([sway * f * f - ax[0] * 10 * f, ln * f]) + perp * rng.uniform(-3, 3) * (1 - f)
                pts.append(tuple(p * K))
            col = (int(150 + rng.uniform(-30, 40)), int(16 + rng.uniform(0, 18)), int(14 + rng.uniform(0, 10)), 255)
            d.line(pts, fill=(30, 6, 6, 255), width=K * 5, joint="curve")
            d.line(pts, fill=col, width=K * 3, joint="curve")
    elif faction == "yan":
        # 연나라: 창날 아래 작은 검푸른 깃발(삼각기)
        root = S - ax * 14
        p2 = root - ax * 40
        tipf = root - ax * 18 + np.array([0, 36])
        d.polygon([tuple(root * K), tuple(p2 * K), tuple(tipf * K)], fill=(30, 52, 86, 255), outline=(8, 12, 20, 255), width=K * 2)
        d.line([tuple((root - ax * 4 + np.array([0, 6])) * K), tuple((tipf + ax * 4 - np.array([0, 4])) * K)], fill=(150, 170, 190, 200), width=K)
    small = big.resize(img.size, Image.LANCZOS)
    return Image.alpha_composite(img, small)


def plume(img, a):
    """철갑 극병: 투구 꼭대기 붉은 깃털."""
    al = a[..., 3]
    ys, xs = np.nonzero(al > 0.6)
    top = ys.min()
    row = xs[ys <= top + 6]
    cx = float(row.mean())
    K = 4
    big = Image.new("RGBA", (img.width * K, img.height * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    rng = np.random.default_rng(3)
    for i in range(11):
        ang = -np.pi / 2 + rng.uniform(-0.9, 0.5)
        ln = 26 + rng.uniform(-6, 10)
        pts = []
        for k in range(8):
            f = k / 7
            pts.append(((cx + np.cos(ang) * ln * f - 10 * f * f) * K, (top + 6 + np.sin(ang) * ln * f + 8 * f * f) * K))
        d.line(pts, fill=(34, 6, 6, 255), width=K * 5, joint="curve")
        d.line(pts, fill=(int(170 + rng.uniform(-30, 50)), int(20 + rng.uniform(0, 20)), 18, 255), width=K * 3, joint="curve")
    small = big.resize(img.size, Image.LANCZOS)
    return Image.alpha_composite(small, img) if False else Image.alpha_composite(img, small)


JOBS = [
    ("yan_pike", "pike", "yan"),
    ("yan_archer", "archer", "yan"),
    ("han_pike", "pike", "han"),
    ("han_archer", "archer", "han"),
    ("han_elite", "pike", "elite"),
]
for key, src, fac in JOBS:
    for pose in POSES:
        im = Image.open(f"{SRC}/era2_{src}_{pose}.png").convert("RGBA")
        a = np.asarray(im).astype(np.float32) / 255
        rc = recolor(a, fac)
        out = Image.fromarray((np.clip(rc, 0, 1) * 255).astype(np.uint8), "RGBA")
        out = draw_extras(out, a, fac, src)
        if fac == "elite":
            out = plume(out, a)
        p = f"{OUT}/era2_{key}_{pose}.webp"
        out.save(p, "WEBP", quality=90, method=6)
        print(p)
