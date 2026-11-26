#!/usr/bin/env python3
"""R33 주먹 중심 자동 추정 — 지금 쥔 자리(또는 첫 추정) 주변에서 실루엣이 가장 두꺼운 점(주먹 덩어리 중심)을 찾는다.

거리 변환: numpy로 십자 · 정사각 침식을 번갈아 해 팔각형 거리를 근사(scipy 없이).
판정: 반경 안 최댓값 능선(dmax-1 이상)의 무게중심 = 주먹 중심. 최댓값이 22를 넘으면(몸통 안쪽) · 반경 가장자리면 '확인 필요'.

사용: python3 -I fist_locate.py <hero 폴더> <파일 접두사> <grips.json(첫 추정)> <출력 json> [반경=30]
"""
import json
import sys

import numpy as np
from PIL import Image

HD, PRE, GJ, OUT = sys.argv[1:5]
RAD = int(sys.argv[5]) if len(sys.argv) > 5 else 30
guess = json.load(open(GJ, encoding='utf-8'))


def dt_approx(mask, maxit=48):
    d = np.zeros(mask.shape, np.int32)
    cur = mask.copy()
    for i in range(1, maxit + 1):
        d[cur] = i
        c = cur
        er = c[1:-1, 1:-1] & c[:-2, 1:-1] & c[2:, 1:-1] & c[1:-1, :-2] & c[1:-1, 2:]
        if i % 2 == 0:
            er = er & c[:-2, :-2] & c[:-2, 2:] & c[2:, :-2] & c[2:, 2:]
        nxt = np.zeros_like(c)
        nxt[1:-1, 1:-1] = er
        cur = nxt
        if not cur.any():
            break
    return d


res = {}
for n, g in guess.items():
    a = np.asarray(Image.open(f"{HD}/{PRE}_{n}.webp").convert('RGBA'))[..., 3] > 60
    d = dt_approx(a)
    gx, gy = g[0], g[1]
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    disk = (xx - gx) ** 2 + (yy - gy) ** 2 <= RAD * RAD
    dd = np.where(disk, d, 0)
    dmax = int(dd.max())
    if dmax == 0:
        res[n] = {'guess': g[:2], 'fist': None, 'dmax': 0, 'flag': 'no-pixels'}
        continue
    ridge = disk & (d >= dmax - 1)
    ys, xs = np.nonzero(ridge)
    fx, fy = float(xs.mean()), float(ys.mean())
    edge = ((fx - gx) ** 2 + (fy - gy) ** 2) ** 0.5 > RAD - 6
    flag = 'body?' if dmax > 22 else 'edge?' if edge else ''
    res[n] = {'guess': [gx, gy], 'fist': [round(fx), round(fy)], 'off': round(((fx - gx) ** 2 + (fy - gy) ** 2) ** 0.5, 1), 'dmax': dmax, 'flag': flag}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for n, r in res.items():
    print(n.ljust(14), 'grip', r['guess'], 'fist', r['fist'], 'off', r.get('off'), 'dmax', r['dmax'], r['flag'])
