# R35 — 몸 + 무기 겹쳐 보기(전 프레임): 쥔 자리 주변 확대. 무기 폴더 · 등급 · 시대를 바꿔 가며 확인
#  python3 -I tools/r35/fist_sheet.py <assets> <weapon-dir> <grips.json> <table> <hero-prefix> <era-key> <tier> <out.png> [R=92] [Z=2] [cols=8]
import sys, json
from PIL import Image, ImageDraw
A, WD, GJ, TB, PRE, EK, T, OUT = sys.argv[1:9]
R = int(sys.argv[9]) if len(sys.argv) > 9 else 92
Z = int(sys.argv[10]) if len(sys.argv) > 10 else 2
COLS = int(sys.argv[11]) if len(sys.argv) > 11 else 8
G = json.load(open(GJ, encoding='utf-8'))[TB]
GX, GY = 70, 60
wp = Image.open(f'{WD}/{EK}_t{T}.png').convert('RGBA')


def weapon_layer(size, x, y, ang, flip):
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if flip else wp
    gy = (w.height - GY) if flip else GY
    big = Image.new('RGBA', (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - GX, cy - gy))
    rot = big.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    lay.paste(rot, (int(round(x - cx)), int(round(y - cy))), rot)
    return lay


names = list(G.keys())
rows = (len(names) + COLS - 1) // COLS
cw = R * 2 * Z
sh = Image.new('RGB', (COLS * cw, rows * (cw + 18)), (18, 18, 22))
d = ImageDraw.Draw(sh)
for i, n in enumerate(names):
    g = G[n]
    body = Image.open(f'{A}/hero/{PRE}_{n}.webp').convert('RGBA')
    s = body.width / 512
    assert abs(s - 1) < 1e-6
    canvas = Image.new('RGBA', (512 + 2 * R + 400, 512 + 2 * R + 400), (58, 66, 84, 255))
    off = R + 200
    canvas.alpha_composite(body, (off, off))
    canvas.alpha_composite(weapon_layer(canvas.size, g[0] + off, g[1] + off, g[2], g[3]))
    c = canvas.crop((int(g[0] + off - R), int(g[1] + off - R), int(g[0] + off + R), int(g[1] + off + R))).resize((cw, cw), Image.LANCZOS).convert('RGB')
    ox, oy = (i % COLS) * cw, (i // COLS) * (cw + 18)
    sh.paste(c, (ox, oy + 18)); d.text((ox + 4, oy + 3), f'{n} {g}', fill=(255, 255, 0))
sh.save(OUT); print(OUT, sh.size)
