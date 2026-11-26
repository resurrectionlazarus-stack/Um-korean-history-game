#!/usr/bin/env python3
"""R33 쥔 자리 맞춤 — '무기 원화 속 주먹이 몸 원화의 손(맨주먹 살색 · 팔 보호대 끝 구멍)을 얼마나 덮는가'로 잰다.

손 픽셀(가림 대상):
  skin: 지금 쥔 자리 반경 RS 안, 살색(α>200, R>G>B, R≥85, R-B≥22) 덩어리 중 가장 큰 것
  hole: 지금 쥔 자리 반경 RH 안, 아주 어두운(밝기<34) 불투명 덩어리 중 가장 큰 것(2px 침식으로 외곽선 제거 후 다시 2px 팽창)
점수 = 세 단계 무기(t1~t3)에서 드러난 손 픽셀 합 + 0.6 × 이동 거리(px)  → ±R 범위 전수 탐색, 각도·뒤집기는 그대로.
사용: python3 -I grip_fit.py <hero 폴더> <접두사> <무기 접두사(예: weapon/era2)> <grips.json> <출력 json> [모드 json: {frame: skin|hole|auto}] [탐색 반경=9]
"""
import json
import sys
from collections import deque

import numpy as np
from PIL import Image

HD, PRE, WPRE, GJ, OUT = sys.argv[1:6]
MODES = json.load(open(sys.argv[6], encoding='utf-8')) if len(sys.argv) > 6 and sys.argv[6] != '-' else {}
SR = int(sys.argv[7]) if len(sys.argv) > 7 else 9
GX, GY = 70, 60
grips = json.load(open(GJ, encoding='utf-8'))
WPS = [Image.open(f"{WPRE}_t{t}.png").convert('RGBA') for t in (1, 2, 3)]


def wmask(wp, ang, flip):
    """쥔 자리를 (C,C)에 둔 무기 α 마스크(회전·뒤집기 적용)."""
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if flip else wp
    gy = (w.height - GY) if flip else GY
    C = 420
    big = Image.new('RGBA', (2 * C, 2 * C), (0, 0, 0, 0))
    big.alpha_composite(w, (C - GX, C - gy))
    rot = big.rotate(-ang, center=(C, C), resample=Image.BICUBIC)
    return np.asarray(rot)[..., 3] > 110, C


def comp(mask, gx, gy, rad):
    H, W = mask.shape
    seen = np.zeros_like(mask)
    best = []
    for y in range(max(0, gy - rad), min(H, gy + rad + 1)):
        for x in range(max(0, gx - rad), min(W, gx + rad + 1)):
            if not mask[y, x] or seen[y, x] or (x - gx) ** 2 + (y - gy) ** 2 > rad * rad:
                continue
            q = deque([(y, x)]); seen[y, x] = True; pts = []
            while q:
                cy, cx = q.popleft(); pts.append((cy, cx))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx] and (nx - gx) ** 2 + (ny - gy) ** 2 <= (rad + 14) ** 2:
                        seen[ny, nx] = True; q.append((ny, nx))
            if len(pts) > len(best):
                best = pts
    out = np.zeros_like(mask)
    for p in best:
        out[p] = True
    return out


def er(m):
    e = np.zeros_like(m); e[1:-1, 1:-1] = m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]; return e


def di(m):
    e = m.copy(); e[1:, :] |= m[:-1, :]; e[:-1, :] |= m[1:, :]; e[:, 1:] |= m[:, :-1]; e[:, :-1] |= m[:, 1:]; return e


res = {}
for n, v in grips.items():
    x0, y0, ang, flip = int(v[0]), int(v[1]), v[2], int(v[3])
    im = np.asarray(Image.open(f"{HD}/{PRE}_{n}.webp").convert('RGBA')).astype(np.int32)
    r, g, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    lum = (r * 3 + g * 6 + b) // 10
    skin = (a > 200) & (r > g) & (g > b) & (r >= 85) & (r - b >= 22)
    hole = er(er((a > 200) & (lum < 34)))
    mode = MODES.get(n, 'auto')
    hs = comp(skin, x0, y0, 30)
    hh = di(di(comp(hole, x0, y0, 18)))
    if mode == 'auto':
        mode = 'skin' if hs.sum() > 260 else 'hole'
    hand = hs if mode == 'skin' else hh
    ys, xs = np.nonzero(hand)
    if len(xs) == 0:
        res[n] = {'mode': mode, 'note': 'no hand pixels'}; print(n, mode, 'no hand pixels'); continue
    masks = [wmask(w, ang, flip) for w in WPS]
    best = None
    cur_unc = None
    for dy in range(-SR, SR + 1):
        for dx in range(-SR, SR + 1):
            unc = 0
            for m, C in masks:
                # 손 픽셀 (xs,ys)가 무기 마스크 좌표에서 어디인지
                mx = xs - (x0 + dx) + C; my = ys - (y0 + dy) + C
                ok = (mx >= 0) & (my >= 0) & (mx < m.shape[1]) & (my < m.shape[0])
                cov = np.zeros(len(xs), bool); cov[ok] = m[my[ok], mx[ok]]
                unc += int((~cov).sum())
            sc = unc + 0.6 * 3 * (dx * dx + dy * dy) ** 0.5
            if dx == 0 and dy == 0:
                cur_unc = unc
            if best is None or sc < best[0]:
                best = (sc, dx, dy, unc)
    _, dx, dy, unc = best
    res[n] = {'mode': mode, 'hand': int(len(xs)), 'cur': [x0, y0, ang, flip], 'cur_uncovered': cur_unc, 'best': [x0 + dx, y0 + dy, ang, flip], 'best_uncovered': unc, 'move': round((dx * dx + dy * dy) ** .5, 1)}
    print(n.ljust(13), mode.ljust(4), 'hand', str(len(xs)).rjust(4), '| now', [x0, y0], 'unc', str(cur_unc).rjust(4), '| best', [x0 + dx, y0 + dy], 'unc', str(unc).rjust(4), 'move', res[n]['move'])
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
