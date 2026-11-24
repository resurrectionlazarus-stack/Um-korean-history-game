# 앞 팔 끝(주먹) 자동 후보: 상체 띠(y0~y1)에서 가장 오른쪽 불투명 점 → 그 행 주변 평균 y, 끝에서 안쪽으로 d만큼
import sys, json
from PIL import Image
import numpy as np
body_dir, prefix = sys.argv[1], sys.argv[2]
names = ['idle', 'run', 'run2', 'run3', 'run4', 'run5', 'run6', 'run7', 'run8', 'atk_prep', 'atk1', 'atk1_2', 'atk1_3',
         'atk2_prep', 'atk2', 'atk2_2', 'atk2_3', 'atk3_prep', 'atk3', 'atk3_2', 'atk3_3', 'hit']
res = {}
for n in names:
    a = np.asarray(Image.open(f'{body_dir}/{prefix}_{n}.webp').convert('RGBA'))[..., 3] > 60
    y0, y1 = 60, 330
    best = None
    for y in range(y0, y1):
        xs = np.nonzero(a[y])[0]
        if len(xs):
            x = xs.max()
            if best is None or x > best[0]:
                best = (int(x), y)
    x, y = best
    rows = [yy for yy in range(max(y0, y - 25), min(y1, y + 25)) if len(np.nonzero(a[yy])[0]) and np.nonzero(a[yy])[0].max() >= x - 6]
    yc = int(round(sum(rows) / len(rows)))
    res[n] = [x - 12, yc]
print(json.dumps(res))
