# 새 몸 + 새 무기 합성 점검 — 표 = {동작: [gx, gy, 각도, 뒤집기]} · python3 -I r26_preview2.py TABLE BODY_DIR PREFIX WEAPON OUT [frames...]
import sys, json
from PIL import Image, ImageDraw
tab, body_dir, prefix, weapon, out = sys.argv[1:6]
names = sys.argv[6:] or ['idle', 'run', 'run2', 'run3', 'run4', 'run5', 'run6', 'run7', 'run8', 'atk_prep', 'atk1', 'atk1_2', 'atk1_3',
         'atk2_prep', 'atk2', 'atk2_2', 'atk2_3', 'atk3_prep', 'atk3', 'atk3_2', 'atk3_3', 'hit']
R = json.load(open(tab, encoding='utf-8'))
W = Image.open(weapon).convert('RGBA')
def comp(n):
    body = Image.open(f'{body_dir}/{prefix}_{n}.webp').convert('RGBA')
    cv = Image.new('RGBA', (body.width + 300, body.height + 120), (0, 0, 0, 0))
    ox, oy = 150, 60
    cv.alpha_composite(body, (ox, oy))
    gx0, gy0, ang, flip = R[n]
    w = W.transpose(Image.FLIP_TOP_BOTTOM) if flip else W
    gx, gy = 70, (W.height - 60) if flip else 60
    big = Image.new('RGBA', (w.width * 2 + 40, w.width * 2 + 40), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - gx, cy - gy))
    big = big.rotate(-ang, resample=Image.BICUBIC, center=(cx, cy))
    cv.alpha_composite(big, (int(ox + gx0 - cx), int(oy + gy0 - cy)))
    d = ImageDraw.Draw(cv)
    d.text((ox + 4, oy + 4), n, fill=(255, 255, 0, 255))
    return cv
tiles = [comp(n) for n in names]
cols = 6 if len(tiles) > 6 else len(tiles)
T = 300
th = int(T * tiles[0].height / tiles[0].width)
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGBA', (cols * T, rows * th), (52, 58, 70, 255))
for i, t in enumerate(tiles):
    sheet.alpha_composite(t.resize((T, th), Image.LANCZOS), ((i % cols) * T, (i // cols) * th))
sheet.convert('RGB').save(out)
print(out, sheet.size)
