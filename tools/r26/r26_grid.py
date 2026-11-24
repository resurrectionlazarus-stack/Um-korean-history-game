# 프레임 확대 + 원본 좌표 격자(20px 선 · 60px 숫자) — python3 -I r26_grid.py BODY_DIR PREFIX OUT f1 f2 ...
import sys
from PIL import Image, ImageDraw
body_dir, prefix, out = sys.argv[1:4]
names = sys.argv[4:]
X0, Y0, X1, Y1 = 80, 40, 480, 460
SC = 1.5
tw, th = int((X1 - X0) * SC), int((Y1 - Y0) * SC)
cols = 3
rows = (len(names) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * th), (40, 44, 54))
for i, n in enumerate(names):
    im = Image.open(f'{body_dir}/{prefix}_{n}.webp').convert('RGBA').crop((X0, Y0, X1, Y1))
    bg = Image.new('RGBA', im.size, (40, 44, 54, 255))
    bg.alpha_composite(im)
    t = bg.resize((tw, th), Image.LANCZOS)
    d = ImageDraw.Draw(t)
    for x in range(X0 - X0 % 20 + 20, X1, 20):
        px = (x - X0) * SC
        d.line([(px, 0), (px, th)], fill=(255, 255, 255) if x % 60 == 0 else (110, 110, 120), width=1)
        if x % 60 == 0:
            d.text((px + 2, 2), str(x), fill=(255, 255, 0))
    for y in range(Y0 - Y0 % 20 + 20, Y1, 20):
        py = (y - Y0) * SC
        d.line([(0, py), (tw, py)], fill=(255, 255, 255) if y % 60 == 0 else (110, 110, 120), width=1)
        if y % 60 == 0:
            d.text((2, py + 2), str(y), fill=(0, 255, 255))
    d.text((tw - 90, th - 16), n, fill=(255, 120, 120))
    sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
sheet.save(out)
print(out, sheet.size)
