# R35 좌우 대칭 점검 — mirror_check.js가 찍은 R/L 쌍을 비교: 왼쪽을 뒤집어 오른쪽과 겹쳐 본다
#  세밀한 선화는 1px만 밀려도 색 차이가 커서, 4px 흐림 뒤의 색 차이(주인공 근처만)와 최적 가로 밀림(px)을 함께 본다.
#  정상 = 모든 자세에서 밀림이 같은 값(거울 축) · 흐림 뒤 차이가 작음
#  python3 -I tools/r35/mirror_diff.py <dir> [sheet.png]
import sys, json, os
import numpy as np
from PIL import Image, ImageFilter

D = sys.argv[1]
meta = json.load(open(os.path.join(D, 'meta.json')))
rows = []
def close(m, k=9):
    # 실루엣 구멍 메우기(배경과 비슷한 색이라 빠진 곳) — 팽창 뒤 침식
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
    return np.asarray(im) > 127
def load(p, blur=4):
    im = Image.open(p).convert('RGB')
    return np.asarray(im).astype(np.int16), np.asarray(im.filter(ImageFilter.GaussianBlur(blur))).astype(np.int16)
for era, M in meta.items():
    bg, bgb = load(os.path.join(D, f'e{era}_BG.png'))
    H, W = bg.shape[:2]
    X0, X1 = W // 2 - 330, W // 2 + 330      # 가운데 띠(동료 요정 제외)
    for tag in M['shots']:
        R, Rb = load(os.path.join(D, f'e{era}_{tag}_R.png'))
        L, Lb = load(os.path.join(D, f'e{era}_{tag}_L.png'))
        mR = close(np.abs(R - bg).max(axis=2) > 18)
        mL = close(np.abs(L - bg).max(axis=2) > 18)[:, ::-1]
        Lbf = Lb[:, ::-1]
        # 배경이 좌우로 달라 겹쳐 비교가 안 되므로: 주인공 픽셀(양쪽 모두 주인공인 곳)만 색 비교, 실루엣은 XOR
        best = None
        for s in range(-12, 13):
            a = mR[:, X0 + s:X1 + s]; b = mL[:, X0:X1]
            x = int((a ^ b).sum())
            if best is None or x < best[0]: best = (x, s)
        s = best[1]
        a = mR[:, X0 + s:X1 + s]; b = mL[:, X0:X1]
        uni = int((a | b).sum()); xor = best[0]
        inter = a & b
        d = np.abs(Rb[:, X0 + s:X1 + s] - Lbf[:, X0:X1]).max(axis=2)
        col = float(d[inter].mean()) if inter.sum() else 0
        rows.append((era, tag, uni, xor, s, col, R[:, X0 + s:X1 + s], L[:, ::-1][:, X0:X1], a ^ b))
rows.sort(key=lambda r: -r[3] / max(1, r[2]))
print('era tag unionPx xorPx shift xor% meanColorDiff')
for r in rows[:16]:
    print(r[0], r[1], r[2], r[3], r[4], round(100 * r[3] / max(1, r[2]), 2), round(r[5], 1))
tot = {}
for r in rows:
    t = tot.setdefault(r[0], [0, 0, 0, {}, 0])
    q = r[3] / max(1, r[2])
    t[0] += 1; t[1] += q; t[2] = max(t[2], q); t[3][r[4]] = t[3].get(r[4], 0) + 1; t[4] = max(t[4], r[5])
for e, t in tot.items():
    print('era', e, 'pairs', t[0], 'mean xor%', round(100 * t[1] / t[0], 2), 'max xor%', round(100 * t[2], 2), 'max colorDiff', round(t[4], 1), 'shifts', dict(sorted(t[3].items())))
if len(sys.argv) > 2:
    top = rows[:6]
    h, w = top[0][6].shape[:2]
    sheet = Image.new('RGB', (w * 3, h * len(top)), (20, 20, 20))
    for i, r in enumerate(top):
        dm = np.zeros(r[8].shape + (3,), np.uint8); dm[r[8]] = (255, 60, 60)
        for j, arr in enumerate([r[6].astype(np.uint8), r[7].astype(np.uint8), dm]):
            sheet.paste(Image.fromarray(arr), (j * w, i * h))
    sheet = sheet.resize((sheet.width // 2, sheet.height // 2))
    sheet.save(sys.argv[2])
