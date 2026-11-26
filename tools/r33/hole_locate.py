#!/usr/bin/env python3
"""R33 팔 보호대(통) 끝 구멍 중심 찾기 — 손을 지운 원화는 팔 끝이 어두운 타원 구멍으로 끝난다.
불투명(α>200)·어두운(밝기<T) 픽셀을 2px 침식해 얇은 외곽선을 지우고, 쥔 자리 반경 안에서 가장 큰 덩어리의 무게중심을 구멍 중심으로 본다.
사용: python3 -I hole_locate.py <hero 폴더> <접두사> <grips.json> <출력 json> [반경=34] [밝기 T=48]
"""
import json
import sys
from collections import deque

import numpy as np
from PIL import Image

HD, PRE, GJ, OUT = sys.argv[1:5]
RAD = int(sys.argv[5]) if len(sys.argv) > 5 else 34
T = int(sys.argv[6]) if len(sys.argv) > 6 else 48
guess = json.load(open(GJ, encoding='utf-8'))


def erode(m):
    e = np.zeros_like(m)
    e[1:-1, 1:-1] = m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]
    return e


res = {}
for n, g in guess.items():
    im = np.asarray(Image.open(f"{HD}/{PRE}_{n}.webp").convert('RGBA')).astype(np.int32)
    lum = (im[..., 0] * 3 + im[..., 1] * 6 + im[..., 2]) // 10
    m = (im[..., 3] > 200) & (lum < T)
    m = erode(erode(m))
    gx, gy = int(g[0]), int(g[1])
    H, W = m.shape
    seen = np.zeros_like(m)
    best = None
    for y in range(max(0, gy - RAD), min(H, gy + RAD + 1)):
        for x in range(max(0, gx - RAD), min(W, gx + RAD + 1)):
            if not m[y, x] or seen[y, x] or (x - gx) ** 2 + (y - gy) ** 2 > RAD * RAD:
                continue
            q = deque([(y, x)]); seen[y, x] = True; pts = []
            while q:
                cy, cx = q.popleft(); pts.append((cy, cx))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
            if best is None or len(pts) > len(best):
                best = pts
    if not best or len(best) < 25:
        res[n] = {'guess': [gx, gy], 'hole': None, 'area': len(best or [])}
        continue
    ys = np.array([p[0] for p in best]); xs = np.array([p[1] for p in best])
    hx, hy = float(xs.mean()), float(ys.mean())
    res[n] = {'guess': [gx, gy], 'hole': [round(hx), round(hy)], 'off': round(((hx - gx) ** 2 + (hy - gy) ** 2) ** 0.5, 1), 'area': len(best),
              'bbox': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for n, r in res.items():
    print(n.ljust(14), 'grip', r['guess'], 'hole', r['hole'], 'off', r.get('off'), 'area', r['area'], r.get('bbox', ''))
