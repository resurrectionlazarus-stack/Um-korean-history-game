#!/usr/bin/env python3
"""R31 비교 이미지 — 질주 8장 신구(무기 얹은 상태) · 해모수 신화 자세 4장 + 이펙트 5종 · 새 몹 16종 · 게임 장면 묶음.
사용: python3 -I compose31.py <R30 assets> <R31 assets> <장면 png 폴더> <출력 폴더>"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

A30, A31, CAP, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
GX, GY = 70, 60
BG = (52, 58, 70)
OLD = {
    'era1_hunter': {"run": [442, 210, -25, 0], "run2": [461, 213, -15, 0], "run3": [470, 174, -30, 0], "run4": [450, 169, -35, 0], "run5": [432, 212, -25, 0], "run6": [462, 216, -15, 0], "run7": [491, 181, -30, 0], "run8": [445, 167, -35, 0]},
    'era2_hero': {"run": [407, 210, 15, 0], "run2": [430, 222, 10, 0], "run3": [356, 247, 25, 0], "run4": [346, 240, 30, 0], "run5": [390, 204, 15, 0], "run6": [430, 228, 10, 0], "run7": [366, 249, 25, 0], "run8": [345, 236, 30, 0]},
}
NEW = {
    'era1_hunter': {"run": [462, 192, -25, 0], "run2": [462, 193, -15, 0], "run3": [454, 183, -30, 0], "run4": [458, 187, -35, 0], "run5": [461, 192, -25, 0], "run6": [458, 193, -15, 0], "run7": [455, 182, -30, 0], "run8": [457, 190, -35, 0]},
    'era2_hero': {"run": [460, 183, 15, 0], "run2": [456, 178, 10, 0], "run3": [453, 172, 25, 0], "run4": [457, 178, 30, 0], "run5": [458, 182, 15, 0], "run6": [462, 187, 10, 0], "run7": [454, 178, 25, 0], "run8": [457, 178, 30, 0],
                  "heavy_cleave": [454, 239, 30, 0], "slam_prep": [352, 68, -120, 1], "slam_hit": [442, 243, 70, 0], "summon_sky": [393, 36, -88, 0]},
}
WPN = {'era1_hunter': 'era1_t1.png', 'era2_hero': 'era2_t1.png'}
try:
    FONT = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 13)
except OSError:
    FONT = None


def body_with_weapon(adir, key, pose, grip, pad=(0, 250, 0)):
    """무기가 512 캔버스 밖으로 뻗는 만큼 여백(왼 · 오른 · 위)을 붙여 칼 전체가 보이게 한다"""
    pl, pr, pt = pad
    body = Image.open(f"{adir}/hero/{key}_{pose}.webp").convert('RGBA')
    can = Image.new('RGBA', (512 + pl + pr, 512 + pt), BG + (255,))
    wp = Image.open(f"{adir}/weapon/{WPN[key]}").convert('RGBA')
    x, y, ang, flip = grip
    x += pl
    y += pt
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if flip else wp
    gy = (w.height - GY) if flip else GY
    big = Image.new('RGBA', (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - GX, cy - gy))
    rot = big.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
    can.alpha_composite(body, (pl, pt))
    big2 = Image.new('RGBA', can.size, (0, 0, 0, 0))
    big2.paste(rot, (int(x - cx), int(y - cy)))
    can.alpha_composite(big2)
    return can


def label(d, xy, t, col=(240, 240, 240)):
    d.text(xy, t, fill=col, font=FONT)


# 1) 질주 8장 신구 비교(무기 전체가 보이게 오른쪽 여백 250)
T = 130
TW = int(T * 762 / 512)
W = Image.new('RGB', (8 * (TW + 2) + 60, 4 * (T + 18) + 8), (24, 24, 28))
d = ImageDraw.Draw(W)
r = 0
for key, name in (('era1_hunter', '1시대 대사냥꾼'), ('era2_hero', '2시대 해모수')):
    for tag, adir, G in (('R30', A30, OLD[key]), ('R31', A31, NEW[key])):
        y = 4 + r * (T + 18)
        label(d, (8, y + T // 2), f"{tag}", (253, 224, 71) if tag == 'R31' else (148, 163, 184))
        for i, p in enumerate(["run", "run2", "run3", "run4", "run5", "run6", "run7", "run8"]):
            im = body_with_weapon(adir, key, p, G[p]).convert('RGB').resize((TW, T))
            W.paste(im, (60 + i * (TW + 2), y + 16))
            label(d, (60 + i * (TW + 2) + 3, y), f"{name + ' ' if i == 0 else ''}{p}")
        r += 1
W.save(f"{OUT}/R31-run-frames.png")
# 2) 해모수 신화 자세 4장(무기 얹음) + 이펙트 5종
T = 200
PW, PH = int(T * 872 / 512), int(T * 752 / 512)
W = Image.new('RGB', (4 * (PW + 2), PH + 18 + T + 18), (24, 24, 28))
d = ImageDraw.Draw(W)
for i, p in enumerate(["heavy_cleave", "slam_prep", "slam_hit", "summon_sky"]):
    im = body_with_weapon(A31, 'era2_hero', p, NEW['era2_hero'][p], pad=(140, 220, 240)).convert('RGB').resize((PW, PH))
    W.paste(im, (i * (PW + 2), 16))
    label(d, (i * (PW + 2) + 3, 1), p)
for i, f in enumerate(["tiger_claw", "bear_slam", "giant_lute_sword", "bronze_mirror_halo", "thunder_crack"]):
    fx = Image.open(f"{A31}/fx/era2_fx_{f}.webp").convert('RGBA')
    can = Image.new('RGBA', fx.size, (28, 30, 40, 255))
    can.alpha_composite(fx)
    W.paste(can.convert('RGB').resize((T, T)), (i * (T + 2), PH + 36))
    label(d, (i * (T + 2) + 3, PH + 19), f"fx_{f}")
W.save(f"{OUT}/R31-mythic-art.png")
# 3) 새 몹 16종(idle · atk)
mobs = [('era3', 'bj_guard'), ('era3', 'bj_archer'), ('era3', 'gg_pike'), ('era3', 'gg_cav'), ('era3', 'wa_raider'), ('era4', 'wakou_sword'), ('era4', 'jurchen_inf'), ('era4', 'jurchen_cav'),
        ('era4', 'redturban_inf'), ('era4', 'redturban_elite'), ('era5', 'qing_rider'), ('era6', 'fr_rifle'), ('era6', 'fr_bayonet'), ('era6', 'us_rifle'), ('era6', 'us_bayonet'), ('era6', 'jp_officer')]
T = 130
cols = 8
W = Image.new('RGB', (cols * (T * 2 + 6), 2 * (T + 18)), (24, 24, 28))
d = ImageDraw.Draw(W)
for i, (e, k) in enumerate(mobs):
    x0 = (i % cols) * (T * 2 + 6)
    y0 = (i // cols) * (T + 18)
    for j, p in enumerate(['idle', 'atk']):
        im = Image.open(f"{A31}/mob/{e}_{k}_{p}.webp").convert('RGBA')
        can = Image.new('RGBA', im.size, BG + (255,))
        can.alpha_composite(im)
        W.paste(can.convert('RGB').resize((T, T)), (x0 + j * T, y0 + 16))
    label(d, (x0 + 3, y0 + 1), f"{e} {k}")
W.save(f"{OUT}/R31-new-mobs.png")


# 4) 게임 장면 묶음(JPEG)
def grid(names, out, cols=2, w=960, h=540):
    rows = (len(names) + cols - 1) // cols
    G = Image.new('RGB', (cols * w, rows * h), (20, 20, 24))
    for i, n in enumerate(names):
        im = Image.open(f"{CAP}/{n}.png").convert('RGB').resize((w, h))
        G.paste(im, ((i % cols) * w, (i // cols) * h))
    G.save(f"{OUT}/{out}", quality=86)


grid(['cap_e2_claw', 'cap_e2_slam', 'cap_e2_summon', 'cap_e2_sky_sword'], 'R31-era2-mythic.jpg')
grid(['cap_e4_front', 'cap_e4_item'], 'R31-era4-front-mission.jpg')
grid(['cap_e6_mauser', 'cap_e6_bomb', 'cap_e6_uiyeol', 'cap_e6_shadow'], 'R31-era6-uiyeol.jpg')
Image.open(f"{CAP}/cap_e2_ult.png").convert('RGB').save(f"{OUT}/R31-era2-ult.jpg", quality=86)
z = Image.open(f"{CAP}/cap_hitfx_zoom.png").convert('RGB')
z.resize((z.width * 2, z.height * 2), Image.LANCZOS).save(f"{OUT}/R31-hitfx-zoom.jpg", quality=88)
print('ok', sorted(os.listdir(OUT)))
