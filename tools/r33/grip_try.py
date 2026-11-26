#!/usr/bin/env python3
"""R33 쥔 자리 후보 비교 — 프레임마다 후보 [x,y,ang,flip]로 실제 무기를 얹어 나란히 본다.
칸: 쥔 자리 주변 R(원본 px)을 Z배 · 무기 불투명 · 작은 초록 십자(후보 쥔 자리) · 10px 점 눈금.
flip 자리에 -1을 주면 무기 없이 몸 원화만(주먹 모양 확인용).
사용: python3 -I grip_try.py <hero 폴더> <접두사> <무기 png> <출력 png> "프레임:x,y,ang,flip|프레임:x,y,ang,flip|..." [R=110] [Z=2] [cols=4]
"""
import sys
from PIL import Image, ImageDraw, ImageFont
HD, PRE, WPN, OUT, SPEC = sys.argv[1:6]
R = int(sys.argv[6]) if len(sys.argv) > 6 else 110
Z = int(sys.argv[7]) if len(sys.argv) > 7 else 2
COLS = int(sys.argv[8]) if len(sys.argv) > 8 else 4
F = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 12)
GX, GY = 70, 60
wp = Image.open(WPN).convert('RGBA')


def weapon_layer(size, x, y, ang, flip, alpha=1.0):
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if flip else wp
    gy = (w.height - GY) if flip else GY
    big = Image.new('RGBA', (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - GX, cy - gy))
    rot = big.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
    if alpha < 1:
        rot.putalpha(rot.split()[3].point(lambda v: int(v * alpha)))
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    lay.paste(rot, (int(round(x - cx)), int(round(y - cy))), rot)
    return lay


items = []
for t in SPEC.split('|'):
    if not t.strip():
        continue
    n, v = t.split(':')
    x, y, a, f = [float(q) for q in v.split(',')]
    items.append((n.strip(), x, y, a, int(f)))
cw, ch = 2 * R * Z, 2 * R * Z + 16
rows = (len(items) + COLS - 1) // COLS
S = Image.new('RGB', (COLS * (cw + 6), rows * ch), (22, 22, 26))
d = ImageDraw.Draw(S)
PAD = 400
cache = {}
for i, (n, x, y, a, f) in enumerate(items):
    if n not in cache:
        body = Image.open(f"{HD}/{PRE}_{n}.webp").convert('RGBA')
        can = Image.new('RGBA', (512 + 2 * PAD, 512 + 2 * PAD), (58, 64, 76, 255))
        can.alpha_composite(body, (PAD, PAD))
        cache[n] = can
    can = cache[n].copy()
    if f >= 0:  # flip -1 = 몸만(무기 없이) 보기
        can.alpha_composite(weapon_layer(can.size, x + PAD, y + PAD, a, f))
    cx, cy = int(round(x)) + PAD, int(round(y)) + PAD
    crop = can.crop((cx - R, cy - R, cx + R, cy + R)).resize((2 * R * Z, 2 * R * Z), Image.LANCZOS)
    cd = ImageDraw.Draw(crop)
    for gx in range(-R - (-R % 10), R + 1, 10):
        for gy in range(-R - (-R % 10), R + 1, 10):
            px, py = (gx + R) * Z, (gy + R) * Z
            cd.point((px, py), fill=(255, 255, 255, 255))
    cd.line([(R * Z - 8, R * Z), (R * Z + 8, R * Z)], fill=(40, 255, 80), width=1)
    cd.line([(R * Z, R * Z - 8), (R * Z, R * Z + 8)], fill=(40, 255, 80), width=1)
    ox, oy = (i % COLS) * (cw + 6), (i // COLS) * ch
    S.paste(crop.convert('RGB'), (ox, oy + 16))
    d.text((ox + 2, oy + 1), f"{n} [{x:g},{y:g},{a:g},{f}]", fill=(240, 240, 240), font=F)
S.save(OUT)
print('ok', OUT, S.size)
