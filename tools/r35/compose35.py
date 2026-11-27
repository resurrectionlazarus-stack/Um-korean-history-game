#!/usr/bin/env python3
"""R35 납품 이미지 합성
  ① R35-weapon-hold.jpg      1시대 무기 쥔 손: R34(위) ↔ R35(아래) · 무기 3단계 × 자세 5
  ② R35-mirror-check.jpg     좌우 대칭 확인: 오른쪽 · 왼쪽 · 왼쪽을 뒤집어 겹친 차이
  ③ R35-fist-sprites.png     무기 그림 3장의 손: 원본 ↔ 통일
  ④ R35-hit-sounds.png       타격음 예전 ↔ 새: 주파수 대역별 에너지(휴대폰이 잘 내는 300~2400Hz 강조)
사용: python3 -I tools/r35/compose35.py <촬영 폴더(capture35)> <좌우 촬영 폴더(mirror_check)> <빌드 폴더> <출력 폴더>"""
import os
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CAP, MIR, BUILD, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
FN = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
F = ImageFont.truetype(FN, 20)
FS = ImageFont.truetype(FN, 15)
FB = ImageFont.truetype(FN, 28)
BG = (16, 18, 24)
INK = (232, 230, 223)
DIM = (154, 163, 181)
GOLD = (251, 191, 36)

# ① 무기 쥔 손 전 · 후
POSES = [('idle', '서 있기'), ('atk1_2', '찌르기'), ('atk_prep', '들어 올리기'), ('atk2_3', '올려치기'), ('hit', '맞음')]
TIERS = [(1, '1단계 주먹도끼'), (2, '2단계 슴베찌르개'), (3, '3단계 간돌도끼')]
cw, ch = 300, 300
pad = 14
W = 150 + len(POSES) * (cw + 6)
H = 70 + len(TIERS) * (2 * (ch + 4) + 46)
im = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(im)
d.text((pad, 14), 'R35 무기를 쥔 손 — 대사냥꾼 · 위 = R34(무기마다 손이 따로 그려져 팔과 어긋남) · 아래 = R35(같은 주먹 하나로 통일)', font=F, fill=GOLD)
for j, (pk, pl) in enumerate(POSES):
    d.text((150 + j * (cw + 6) + 8, 44), pl, font=FS, fill=DIM)
y = 70
for t, tl in TIERS:
    d.text((pad, y + 6), tl, font=FS, fill=INK)
    for r, tag in enumerate(('r34', 'r35')):
        d.text((pad, y + 40 + r * (ch + 4) + ch // 2 - 10), 'R34' if r == 0 else 'R35', font=FB, fill=DIM if r == 0 else GOLD)
        for j, (pk, pl) in enumerate(POSES):
            src = Image.open(f'{CAP}/{tag}_t{t}_{pk}_R.png').convert('RGB')
            sw, sh = src.size
            c = src.crop((sw // 2 - 300, sh - 640, sw // 2 + 300, sh - 40)).resize((cw, ch), Image.LANCZOS)
            im.paste(c, (150 + j * (cw + 6), y + 30 + r * (ch + 4)))
    y += 2 * (ch + 4) + 46
im.save(f'{OUT}/R35-weapon-hold.jpg', quality=88)
print('R35-weapon-hold.jpg', im.size)

# ② 좌우 대칭
rows = [('1', 't3_f_idle', '1시대 서 있기'), ('1', 'atk2_50', '1시대 휘두르는 중'), ('2', 't3_f_idle', '2시대 서 있기'), ('4', 'atk3_50', '4시대 휘두르는 중')]
cw2, ch2 = 330, 277
im = Image.new('RGB', (pad * 2 + 170 + 4 * (cw2 + 6), 78 + len(rows) * (ch2 + 8)), BG)
d = ImageDraw.Draw(im)
d.text((pad, 12), 'R35 좌우 확인 — 왼쪽을 볼 때의 그림은 오른쪽 그림을 정확히 뒤집은 것(무기 위치 어긋남 없음)', font=F, fill=GOLD)
for j, lab in enumerate(['오른쪽 보기', '왼쪽 보기', '왼쪽을 뒤집어 놓음', '두 그림의 차이(주인공 윤곽)']):
    d.text((pad + 170 + j * (cw2 + 6) + 6, 48), lab, font=FS, fill=DIM)
for i, (era, tag, lab) in enumerate(rows):
    R = Image.open(f'{MIR}/e{era}_{tag}_R.png').convert('RGB')
    L = Image.open(f'{MIR}/e{era}_{tag}_L.png').convert('RGB')
    Bg = Image.open(f'{MIR}/e{era}_BG.png').convert('RGB')
    Lf = L.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.asarray(R).astype(np.int16); b = np.asarray(Lf).astype(np.int16); g = np.asarray(Bg).astype(np.int16); gf = g[:, ::-1]
    mR = np.abs(a - g).max(axis=2) > 18
    mL = np.abs(b - gf).max(axis=2) > 18
    # 윤곽(실루엣 테두리)만 비교: 배경이 좌우로 달라 속 무늬는 비교하지 않는다
    def edge(m):
        mm = Image.fromarray((m * 255).astype(np.uint8))
        from PIL import ImageFilter
        cl = mm.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
        return np.asarray(cl) > 127
    eR, eL = edge(mR), edge(mL)
    diff = np.zeros(a.shape, np.uint8)
    diff[eR & eL] = (70, 78, 96)
    diff[eR ^ eL] = (255, 80, 80)
    y0 = 74 + i * (ch2 + 8)
    d.text((pad, y0 + ch2 // 2 - 20), lab, font=FS, fill=INK)
    # 수치는 그림에 보이는 가운데 띠(주인공) 안에서만 잰다 — 띠 밖의 동료 요정은 주인공 뒤를 따라 자리를 바꾸므로 뺀다
    hh, ww = eR.shape
    sl = (slice(hh - 600, hh - 46), slice(ww // 2 - 330, ww // 2 + 330))
    x1 = int((eR[sl] ^ eL[sl]).sum()); un = int((eR[sl] | eL[sl]).sum())
    d.text((pad, y0 + ch2 // 2 + 4), f'윤곽 차이 {100 * x1 / max(1, un):.1f}%', font=FS, fill=DIM)
    d.text((pad, y0 + ch2 // 2 + 26), '(빛 테두리 · 발밑 고리의', font=FS, fill=DIM)
    d.text((pad, y0 + ch2 // 2 + 46), ' 깜빡임만큼)', font=FS, fill=DIM)
    for j, arr in enumerate([R, L, Lf, Image.fromarray(diff)]):
        sw, sh = arr.size
        c = arr.crop((sw // 2 - 330, sh - 600, sw // 2 + 330, sh - 46)).resize((cw2, ch2), Image.LANCZOS)
        im.paste(c, (pad + 170 + j * (cw2 + 6), y0))
im.save(f'{OUT}/R35-mirror-check.jpg', quality=88)
print('R35-mirror-check.jpg', im.size)

# ③ 무기 그림의 손
Z = 4
im = Image.new('RGB', (pad * 3 + 2 * 180 * Z, 60 + 3 * (100 * Z + 34)), BG)
d = ImageDraw.Draw(im)
d.text((pad, 12), 'R35 무기 그림의 손 — 왼쪽 = 원본(팔뚝 방향이 제각각) · 오른쪽 = 통일(같은 주먹 · 팔뚝 토막 없음)', font=F, fill=GOLD)
for i, t in enumerate((1, 2, 3)):
    for j, src in enumerate((os.path.join(os.path.dirname(os.path.abspath(__file__)), 'era1_weapon_orig'), f'{BUILD}/assets/weapon')):
        w = Image.open(f'{src}/era1_t{t}.png').convert('RGBA')
        bgc = Image.new('RGBA', w.size, (58, 66, 84, 255)); bgc.alpha_composite(w)
        c = bgc.crop((0, 18, 180, 118)).resize((180 * Z, 100 * Z), Image.NEAREST).convert('RGB')
        im.paste(c, (pad + j * (180 * Z + pad), 52 + i * (100 * Z + 34) + 26))
    d.text((pad, 52 + i * (100 * Z + 34) + 2), TIERS[i][1], font=FS, fill=INK)
im.save(f'{OUT}/R35-fist-sprites.png', optimize=True)
print('R35-fist-sprites.png', im.size)

# ④ 타격음 대역 에너지
def bands(path):
    w = wave.open(path); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64) / 32768
    X = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / sr); tot = X.sum() + 1e-12
    ed = [0, 300, 2400, 4800, 11025]
    return [X[(f >= a) & (f < b)].sum() / tot for a, b in zip(ed[:-1], ed[1:])]

OLD = [('slice_crisp_1', '예전 베기 1'), ('slice_crisp_2', '예전 베기 2'), ('blade_slash_1', '예전 4시대 베기'), ('hit_heavy', '예전 강타'), ('slice_flesh_sever', '예전 양단'), ('slice_flurry_multi', '예전 연참'), ('blade_armor_cleave', '예전 갑옷 쪼개기')]
NEW = [('cut_light_1', '새 베기 1'), ('cut_light_2', '새 베기 2'), ('cut_light_3', '새 베기 3'), ('cut_heavy', '새 칼 강타'), ('cut_sever', '새 양단'), ('cut_flurry', '새 연참'), ('cut_armor', '새 쇠 울림'),
       ('rock_hit_1', '새 바위 타격 1'), ('rock_hit_2', '새 바위 타격 2'), ('rock_heavy', '새 바위 강타'), ('rock_crush', '새 내려찍기'), ('stab_1', '새 찌르기 1'), ('stab_2', '새 찌르기 2')]
COL = [(72, 84, 110), (56, 189, 248), (148, 163, 184), (248, 113, 113)]
LEG = ['300Hz 아래(휴대폰에서 거의 안 들림)', '300~2400Hz(휴대폰이 가장 잘 내는 몸통)', '2400~4800Hz', '4800Hz 위(날카로운 쇳소리)']
rowh = 30
bw = 760
im = Image.new('RGB', (pad * 2 + 230 + bw + 90, 150 + (len(OLD) + len(NEW) + 1) * rowh + 30), BG)
d = ImageDraw.Draw(im)
d.text((pad, 12), 'R35 타격음 — 소리 에너지가 어느 높이에 있는가(막대 = 100%)', font=F, fill=GOLD)
for i, (c, l) in enumerate(zip(COL, LEG)):
    d.rectangle([pad + (i % 2) * 520, 50 + (i // 2) * 26, pad + (i % 2) * 520 + 18, 50 + (i // 2) * 26 + 16], fill=c)
    d.text((pad + (i % 2) * 520 + 26, 48 + (i // 2) * 26), l, font=FS, fill=INK)
y = 116
for group, items in (('예전 타격음', OLD), ('새 타격음', NEW)):
    d.text((pad, y), group, font=FS, fill=GOLD)
    y += rowh
    for fn, lab in items:
        b = bands(f'{BUILD}/assets/sfx/{fn}.wav')
        d.text((pad, y + 4), lab, font=FS, fill=INK)
        x = pad + 230
        for v, c in zip(b, COL):
            w_ = int(round(v * bw))
            d.rectangle([x, y + 3, x + w_, y + rowh - 7], fill=c)
            x += w_
        d.text((pad + 230 + bw + 10, y + 4), f'몸통 {b[1] * 100:.0f}%', font=FS, fill=(56, 189, 248) if b[1] >= 0.4 else (248, 113, 113))
        y += rowh
im.save(f'{OUT}/R35-hit-sounds.png', optimize=True)
print('R35-hit-sounds.png', im.size)
