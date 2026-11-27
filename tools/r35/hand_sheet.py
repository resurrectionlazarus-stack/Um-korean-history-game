# R35 — 몸 원화의 '손'만 확대(무기 없이): 쥔 자리(초록 십자) 주변 120px(원본)을 3배로
#  python3 -I tools/r35/hand_sheet.py <assets> <grips.json> <table> <prefix> <out.png>
import sys, json
from PIL import Image, ImageDraw
A, GJ, TB, PRE, OUT = sys.argv[1:6]
G = json.load(open(GJ, encoding='utf-8'))[TB]
names = list(G.keys())
R, Z = 64, 3
cols = 9
rows = (len(names) + cols - 1) // cols
sh = Image.new('RGB', (cols * R * 2 * Z, rows * (R * 2 * Z + 18)), (18, 18, 22))
d = ImageDraw.Draw(sh)
for i, n in enumerate(names):
    g = G[n]
    im = Image.open(f'{A}/hero/{PRE}_{n}.webp').convert('RGBA')
    s = im.width / 512
    x, y = g[0] * s, g[1] * s
    bg = Image.new('RGBA', im.size, (58, 66, 84, 255)); bg.alpha_composite(im)
    c = bg.crop((int(x - R * s), int(y - R * s), int(x + R * s), int(y + R * s))).resize((R * 2 * Z, R * 2 * Z), Image.LANCZOS).convert('RGB')
    cd = ImageDraw.Draw(c)
    cd.line([(R * Z - 9, R * Z), (R * Z + 9, R * Z)], fill=(0, 255, 0), width=1); cd.line([(R * Z, R * Z - 9), (R * Z, R * Z + 9)], fill=(0, 255, 0), width=1)
    ox, oy = (i % cols) * R * 2 * Z, (i // cols) * (R * 2 * Z + 18)
    sh.paste(c, (ox, oy + 18)); d.text((ox + 4, oy + 3), f'{n} {g}', fill=(255, 255, 0))
sh.save(OUT); print(OUT, sh.size, len(names))
