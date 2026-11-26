#!/usr/bin/env python3
"""R33 맨주먹 중심 — 쥔 자리 반경 안의 살색 덩어리(손가락·손등) 무게중심.
살색: α>200, R>G>B, R≥110, R-B≥35 (그림자 살색 포함, 갈색 가죽·청동은 대개 R-G 차가 작거나 어두워 빠짐).
사용: python3 -I skin_fist.py <hero 폴더> <접두사> <grips.json> [반경=26]
"""
import json
import sys
from collections import deque

import numpy as np
from PIL import Image

HD, PRE, GJ = sys.argv[1:4]
RAD = int(sys.argv[4]) if len(sys.argv) > 4 else 26
g = json.load(open(GJ, encoding='utf-8'))
for n, v in g.items():
    im = np.asarray(Image.open(f"{HD}/{PRE}_{n}.webp").convert('RGBA')).astype(np.int32)
    r, gg, b, a = im[..., 0], im[..., 1], im[..., 2], im[..., 3]
    m = (a > 200) & (r > gg) & (gg > b) & (r >= 110) & (r - b >= 35) & (r - gg >= 18)
    gx, gy = int(v[0]), int(v[1])
    H, W = m.shape
    seen = np.zeros_like(m)
    best = []
    for y in range(max(0, gy - RAD), min(H, gy + RAD + 1)):
        for x in range(max(0, gx - RAD), min(W, gx + RAD + 1)):
            if not m[y, x] or seen[y, x] or (x - gx) ** 2 + (y - gy) ** 2 > RAD * RAD:
                continue
            q = deque([(y, x)]); seen[y, x] = True; pts = []
            while q:
                cy, cx = q.popleft(); pts.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx] and (nx - gx) ** 2 + (ny - gy) ** 2 <= (RAD + 8) ** 2:
                            seen[ny, nx] = True; q.append((ny, nx))
            if len(pts) > len(best):
                best = pts
    if len(best) < 40:
        print(n.ljust(13), 'grip', [gx, gy], 'skin: 없음', len(best)); continue
    ys = np.array([p[0] for p in best]); xs = np.array([p[1] for p in best])
    fx, fy = xs.mean(), ys.mean()
    print(n.ljust(13), 'grip', [gx, gy], 'skin', [round(fx), round(fy)], 'off', round(((fx - gx) ** 2 + (fy - gy) ** 2) ** .5, 1), 'area', len(best), 'bbox', [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])
