#!/usr/bin/env python3
"""R33 쥔 자리 확대(몸만) — 무기 없이 몸 원화를 Z배로, 5px 눈금(10px마다 진하게, 축 숫자는 지금 쥔 자리 기준 px).
빨간 십자 = 지금 쥔 자리, 초록 원 = 후보(있으면).
사용: python3 -I grip_zoom.py <hero 폴더> <접두사> "프레임,x,y[,후보x,후보y];..." <출력 png> [R=40] [Z=4] [cols=4]"""
import sys
from PIL import Image, ImageDraw, ImageFont
HD, PRE, SPEC, OUT = sys.argv[1:5]
R = int(sys.argv[5]) if len(sys.argv) > 5 else 40
Z = int(sys.argv[6]) if len(sys.argv) > 6 else 4
COLS = int(sys.argv[7]) if len(sys.argv) > 7 else 4
F = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 12)
items = [t.split(',') for t in SPEC.split(';') if t]
cw = 2 * R * Z
rows = (len(items) + COLS - 1) // COLS
W = Image.new('RGB', (COLS * (cw + 6), rows * (cw + 18)), (22, 22, 26))
d = ImageDraw.Draw(W)
for i, it in enumerate(items):
    n, x, y = it[0], int(it[1]), int(it[2])
    cand = (int(it[3]), int(it[4])) if len(it) >= 5 else None
    body = Image.open(f"{HD}/{PRE}_{n}.webp").convert('RGBA')
    can = Image.new('RGBA', (512 + 2 * R, 512 + 2 * R), (58, 64, 76, 255))
    can.alpha_composite(body, (R, R))
    crop = can.crop((x, y, x + 2 * R, y + 2 * R)).resize((cw, cw), Image.NEAREST).convert('RGB')
    cd = ImageDraw.Draw(crop)
    for k in range(-R, R + 1, 5):
        if k == 0:
            continue
        c = (150, 150, 150) if k % 10 else (230, 230, 230)
        for t in range(0, cw, 3 if k % 10 else 2):
            cd.point(((k + R) * Z, t), fill=c)
            cd.point((t, (k + R) * Z), fill=c)
        if k % 20 == 0:
            cd.text(((k + R) * Z + 2, 2), str(k), fill=(255, 255, 0), font=F)
            cd.text((2, (k + R) * Z + 2), str(k), fill=(255, 255, 0), font=F)
    cd.line([(R * Z - 14, R * Z), (R * Z + 14, R * Z)], fill=(255, 50, 50), width=2)
    cd.line([(R * Z, R * Z - 14), (R * Z, R * Z + 14)], fill=(255, 50, 50), width=2)
    if cand:
        cx, cy = (cand[0] - x + R) * Z, (cand[1] - y + R) * Z
        cd.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(40, 255, 80), width=2)
    ox, oy = (i % COLS) * (cw + 6), (i // COLS) * (cw + 18)
    W.paste(crop, (ox, oy + 18))
    lab = f"{n} [{x},{y}]" + (f" 후보[{cand[0]},{cand[1]}]" if cand else "")
    d.text((ox + 2, oy + 2), lab, fill=(240, 240, 240), font=F)
W.save(OUT)
print('ok', OUT, W.size)
