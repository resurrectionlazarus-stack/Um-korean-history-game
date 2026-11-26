#!/usr/bin/env python3
"""R31 무기 쥔 자리 실측 — 질주 프레임: 윗몸 높이(위 60 ~ 320px)에서 가장 앞(오른쪽)으로 나온 주먹 덩어리의 가운데.
사용: python3 -I grip_probe.py <프레임 폴더> <접두사> <출력 json>"""
import json
import sys

import numpy as np
from PIL import Image

D, pre, out = sys.argv[1], sys.argv[2], sys.argv[3]
res = {}
for i in range(1, 9):
    nm = "run" + ("" if i == 1 else str(i))
    a = np.asarray(Image.open(f"{D}/{pre}_{nm}.webp").convert("RGBA"))[..., 3] > 60
    ys, xs = np.nonzero(a)
    top = ys.min()
    band = a[top + 60:320]
    cols = np.nonzero(band.any(0))[0]
    xmax = cols.max()
    # 맨 앞 열에서 왼쪽 30px 안의 불투명 덩어리 — 그 행 범위의 가운데
    win = band[:, xmax - 30:xmax + 1]
    rr = np.nonzero(win.any(1))[0]
    # 맨 앞 점이 있는 행 근처(±26px)만
    rx = np.nonzero(band[:, xmax])[0]
    yc = int(np.median(rx))
    sel = rr[(rr > yc - 26) & (rr < yc + 26)]
    y0, y1 = sel.min(), sel.max()
    cy = (y0 + y1) / 2 + top + 60
    cx = xmax - 15
    res[nm] = [int(round(cx)), int(round(cy))]
json.dump(res, open(out, "w"))
print(json.dumps(res))
