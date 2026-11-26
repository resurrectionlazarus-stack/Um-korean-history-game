#!/usr/bin/env python3
"""R33 손 ↔ 무기 쥔 자리 검증 시트(납품 이미지)
① 고친 프레임 전 · 후(R31 값 → R33 값) 확대 비교  ② 시대별 전 프레임(최종 값) 무기 겹쳐 그리기 시트
사용: python3 -I grip_sheets.py <assets 폴더> <grips_r33.json> <출력 폴더>
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

A, GJ, OUT = sys.argv[1:4]
G = json.load(open(GJ, encoding='utf-8'))
F = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 15)
FB = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 22)
GX, GY = 70, 60
WP = {k: Image.open(f'{A}/weapon/{k}_t1.png').convert('RGBA') for k in ('era1', 'era2', 'era4')}


def weapon_layer(wp, size, x, y, ang, flip):
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if flip else wp
    gy = (w.height - GY) if flip else GY
    big = Image.new('RGBA', (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - GX, cy - gy))
    rot = big.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    lay.paste(rot, (int(round(x - cx)), int(round(y - cy))), rot)
    return lay


def panel(era, pre, frame, g, R, Z):
    PAD = 400
    body = Image.open(f'{A}/hero/{pre}_{frame}.webp').convert('RGBA')
    can = Image.new('RGBA', (512 + 2 * PAD, 512 + 2 * PAD), (58, 64, 76, 255))
    can.alpha_composite(body, (PAD, PAD))
    if g:
        x, y, a, f = g
        can.alpha_composite(weapon_layer(WP[era], can.size, x + PAD, y + PAD, a, f))
        cx, cy = x + PAD, y + PAD
    else:
        cx, cy = 256 + PAD, 256 + PAD
    crop = can.crop((cx - R, cy - R, cx + R, cy + R)).resize((2 * R * Z, 2 * R * Z), Image.LANCZOS)
    if g:
        d = ImageDraw.Draw(crop)
        c = R * Z
        d.line([(c - 9, c), (c + 9, c)], fill=(40, 255, 80), width=2)
        d.line([(c, c - 9), (c, c + 9)], fill=(40, 255, 80), width=2)
    return crop.convert('RGB')


# ① 전 · 후
OLD = {  # R31 값(R33 전)
    ('hunter', 'idle'): [456, 318, -40, 0],
    ('hm', 'slam_prep'): [352, 68, -120, 1], ('hm', 'heavy_cleave'): [454, 239, 30, 0], ('hm', 'atk3_2'): [452, 324, 10, 0],
    ('hm', 'slam_hit'): [442, 243, 70, 0], ('hm', 'summon_sky'): [393, 36, -88, 0],
    ('cjg', 'run'): [421, 164, 15, 0], ('cjg', 'run3'): [393, 170, 25, 0], ('cjg', 'run7'): [405, 173, 25, 0],
    ('cjg', 'cleave_prep'): None, ('cjg', 'dragon_stance'): None,
}
META = {'hunter': ('era1', 'era1_hunter', 'R27_HUNTER_FRAMES', '1시대 대사냥꾼'), 'hm': ('era2', 'era2_hero', 'R26_HM_FRAMES', '2시대 해모수'), 'cjg': ('era4', 'era4_hero', 'R26_CJG_FRAMES', '4시대 척준경')}
NOTE = {
    ('hunter', 'idle'): '주먹이 팔뚝 가운데(30px) → 팔 보호대 끝',
    ('hm', 'slam_prep'): '두 주먹 사이 허공(27px) → 오른 주먹',
    ('hm', 'heavy_cleave'): '맨주먹 80px 드러남 → 0',
    ('hm', 'atk3_2'): '보호대 끝 14px 드러남 → 1',
    ('hm', 'slam_hit'): '맨주먹 12px 드러남 → 0',
    ('hm', 'summon_sky'): '맨주먹 5px 드러남 → 0',
    ('cjg', 'run'): 'R32 새 질주 원화 — 옛 값은 손 밖(38px)',
    ('cjg', 'run3'): 'R32 새 질주 원화 — 옛 값은 손 밖(58px)',
    ('cjg', 'run7'): 'R32 새 질주 원화 — 옛 값은 손 밖(49px)',
    ('cjg', 'cleave_prep'): '무신 자세 새로 잼 — 머리 위 두 손 파지',
    ('cjg', 'dragon_stance'): '무신 자세 새로 잼 — 청룡 자세',
}
R, Z = 70, 3
pw = 2 * R * Z
rows = list(OLD.items())
S = Image.new('RGB', (2 * pw + 30 + 360, len(rows) * (pw + 34) + 50), (20, 20, 24))
d = ImageDraw.Draw(S)
d.text((10, 10), 'R33 손 ↔ 무기 쥔 자리 — 고친 프레임 전(R31) · 후(R33)   초록 십자 = 쥔 자리(무기 원화 손잡이 중심)', fill=(250, 250, 250), font=FB)
for i, ((h, fr), old) in enumerate(rows):
    era, pre, tab, nm = META[h]
    new = G[tab][fr]
    y = 50 + i * (pw + 34)
    d.text((10, y), f'{nm} · {fr}', fill=(253, 224, 71), font=F)
    d.text((10 + pw + 20, y), '→', fill=(250, 250, 250), font=F)
    S.paste(panel(era, pre, fr, old, R, Z) if old else Image.new('RGB', (pw, pw), (40, 40, 46)), (10, y + 22))
    if not old:
        d.text((30, y + 22 + pw // 2 - 10), '(R32 새 자세 — 쥔 자리 없음)', fill=(200, 200, 200), font=F)
    S.paste(panel(era, pre, fr, new, R, Z), (10 + pw + 20, y + 22))
    d.text((10 + 2 * pw + 30, y + 30), f'전 {old if old else "— (새 자세)"}', fill=(248, 113, 113), font=F)
    d.text((10 + 2 * pw + 30, y + 56), f'후 {new}', fill=(74, 222, 128), font=F)
    d.text((10 + 2 * pw + 30, y + 86), NOTE[(h, fr)], fill=(230, 230, 230), font=F)
# 두 단 배치(앞 6행 · 뒤 5행)
w, rowh, top, half = S.width, pw + 34, 50, (len(rows) + 1) // 2
T = Image.new('RGB', (2 * w + 10, top + half * rowh), (20, 20, 24))
T.paste(S.crop((0, 0, w, top)), (0, 0))
for i in range(len(rows)):
    T.paste(S.crop((0, top + i * rowh, w, top + (i + 1) * rowh)), ((0 if i < half else 1) * (w + 10), top + (i % half) * rowh))
T.save(f'{OUT}/R33-grip-before-after.png')
print('before-after', T.size)

# ② 전 프레임(최종 값)
for h, (era, pre, tab, nm) in META.items():
    frames = G[tab]
    R2, cols = 130, 7
    cw = 2 * R2
    rows2 = (len(frames) + cols - 1) // cols
    S = Image.new('RGB', (cols * (cw + 6) + 6, rows2 * (cw + 26) + 44), (20, 20, 24))
    d = ImageDraw.Draw(S)
    d.text((8, 8), f'R33 쥔 자리 전수 검증 — {nm} {len(frames)}장 · 무기 1등급 · 초록 십자 = 쥔 자리', fill=(250, 250, 250), font=FB)
    for i, (fr, g) in enumerate(frames.items()):
        x0 = 6 + (i % cols) * (cw + 6)
        y0 = 44 + (i // cols) * (cw + 26)
        d.text((x0 + 2, y0), f'{fr} {g}', fill=(230, 230, 230), font=F)
        S.paste(panel(era, pre, fr, g, R2, 1), (x0, y0 + 22))
    S.save(f'{OUT}/R33-grip-all-{h}.png')
    print(h, S.size)
