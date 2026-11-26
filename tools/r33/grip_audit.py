#!/usr/bin/env python3
"""R33 손 ↔ 무기 쥔 자리 전수 점검 시트.

프레임마다 두 장:
  ① 전체 — 몸 원화 위에 실제 무기를 게임과 같은 방식으로 얹음(쥔 자리 gx,gy를 주먹에 · 각도 회전 · 뒤집기)
  ② 확대 — 쥔 자리 주변 120×120(원본 px)을 3배로, 무기 45% 반투명 · 빨간 십자(지금 쥔 자리) · 5px 눈금

사용: python3 -I grip_audit.py <index.html> <표 이름> <hero 폴더> <파일 접두사> <무기 png> <출력 png> [grips.json(표 대신)]
"""
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont

HTML, TAB, HD, PRE, WPN, OUT = sys.argv[1:7]
if len(sys.argv) > 7:
    grips = json.load(open(sys.argv[7], encoding='utf-8'))
else:
    s = open(HTML, encoding='utf-8').read()
    grips = json.loads(re.search(r'var ' + TAB + r' = (\{.*?\});', s).group(1))
GX, GY = 70, 60
try:
    FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 12)
except OSError:
    FONT = None
wp = Image.open(WPN).convert('RGBA')


def weapon_layer(size, x, y, ang, flip, alpha=1.0, off=(0, 0)):
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if flip else wp
    gy = (w.height - GY) if flip else GY
    big = Image.new('RGBA', (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - GX, cy - gy))
    rot = big.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
    if alpha < 1:
        a = rot.split()[3].point(lambda v: int(v * alpha))
        rot.putalpha(a)
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    lay.paste(rot, (int(round(x - cx + off[0])), int(round(y - cy + off[1]))), rot)
    return lay


names = list(grips.keys())
T = 200           # 전체 칸
Z = 3             # 확대 배율
R = 60            # 확대 반경(원본 px)
cols = 4
cellw = T + 2 * R * Z + 12
cellh = max(T, 2 * R * Z) + 18
rows = (len(names) + cols - 1) // cols
S = Image.new('RGB', (cols * cellw, rows * cellh), (22, 22, 26))
d = ImageDraw.Draw(S)
for i, n in enumerate(names):
    x, y, ang, flip = grips[n]
    body = Image.open(f"{HD}/{PRE}_{n}.webp").convert('RGBA')
    PAD = 260
    can = Image.new('RGBA', (512 + 2 * PAD, 512 + 2 * PAD), (58, 64, 76, 255))
    can.alpha_composite(body, (PAD, PAD))
    full = can.copy()
    full.alpha_composite(weapon_layer(full.size, x + PAD, y + PAD, ang, flip))
    # 전체: 몸 중심 512를 기준으로 무기가 보이게 여백 포함 축소
    fv = full.crop((PAD - 120, PAD - 120, PAD + 512 + 120, PAD + 512 + 120)).convert('RGB').resize((T, T))
    ox = (i % cols) * cellw
    oy = (i // cols) * cellh
    S.paste(fv, (ox, oy + 16))
    # 확대: 무기 45% · 십자 · 5px 눈금
    zc = can.copy()
    zc.alpha_composite(weapon_layer(zc.size, x + PAD, y + PAD, ang, flip, 0.45))
    crop = zc.crop((x + PAD - R, y + PAD - R, x + PAD + R, y + PAD + R)).resize((2 * R * Z, 2 * R * Z), Image.NEAREST)
    cd = ImageDraw.Draw(crop)
    for k in range(-R, R + 1, 5):
        c = (255, 255, 255, 70) if k % 10 else (255, 255, 255, 120)
        cd.line([((k + R) * Z, 0), ((k + R) * Z, 2 * R * Z)], fill=c, width=1)
        cd.line([(0, (k + R) * Z), (2 * R * Z, (k + R) * Z)], fill=c, width=1)
    cd.line([(R * Z - 12, R * Z), (R * Z + 12, R * Z)], fill=(255, 40, 40), width=2)
    cd.line([(R * Z, R * Z - 12), (R * Z, R * Z + 12)], fill=(255, 40, 40), width=2)
    S.paste(crop.convert('RGB'), (ox + T + 6, oy + 16))
    d.text((ox + 3, oy + 1), f"{n}  [{x},{y},{ang},{flip}]", fill=(240, 240, 240), font=FONT)
S.save(OUT)
print('ok', len(names), OUT)
