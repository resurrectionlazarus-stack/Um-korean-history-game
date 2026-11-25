# R27 묶음 자동 검수: 해상도 · 접지선(맨 아래 불투명 y) · 프린지(반투명 가장자리의 흰/검 매트 번짐) · 떨어진 점(잡티) · R26 대비 신규/교체
import sys, os, json
from PIL import Image
import numpy as np
from collections import deque
pack, r26 = sys.argv[1], sys.argv[2]
exp = {'hero': ((512, 512), 469), 'boss': ((768, 640), 599)}
rows = []
for dp, _, fs in os.walk(os.path.join(pack, 'assets')):
    for f in sorted(fs):
        if f == 'MANIFEST.json':
            continue
        p = os.path.join(dp, f); rel = os.path.relpath(p, pack)
        im = Image.open(p); a = np.asarray(im.convert('RGBA')).astype(int)
        al = a[..., 3]
        ys, xs = np.nonzero(al > 20)
        bottom = int(ys.max()) if len(ys) else -1
        semi = (al > 8) & (al < 200)
        rgb = a[..., :3]
        lum = (rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114)
        white_fr = int(((lum > 235) & semi).sum())
        # 잡티: 큰 덩어리에서 떨어진 작은 불투명 조각(4-연결) 수
        m = al > 60
        seen = np.zeros_like(m); comps = []
        H, W = m.shape
        for y0, x0 in zip(*np.nonzero(m)):
            if seen[y0, x0]:
                continue
            q = deque([(y0, x0)]); seen[y0, x0] = 1; n = 0
            while q:
                y, x = q.popleft(); n += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = 1; q.append((yy, xx))
            comps.append(n)
        comps.sort(reverse=True)
        specks = sum(1 for c in comps[1:] if c < 40)
        kind = 'hero' if '/hero/' in rel else 'boss' if '/boss/' in rel else 'other'
        ok_size = kind == 'other' or im.size == exp[kind][0]
        ok_ground = kind == 'other' or bottom == exp[kind][1]
        old = os.path.join(r26, rel)
        status = 'replace' if os.path.exists(old) else 'NEW'
        rows.append((rel, im.format, im.mode, im.size, bottom, white_fr, specks, len(comps), status, ok_size and ok_ground))
for r in rows:
    print(' | '.join(str(x) for x in r))
bad = [r for r in rows if not r[-1] or r[5] > 0 or r[2] != 'RGBA']
print('TOTAL', len(rows), 'BAD(size/ground/fringe/mode)', len(bad))
for r in bad: print('  BAD', r)
