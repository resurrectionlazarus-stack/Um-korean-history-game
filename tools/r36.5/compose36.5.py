#!/usr/bin/env python3
"""R36.5 납품 이미지 합성
  ① R36.5-hand-sprites.jpg   무기 그림 9장의 손: 예전 ↔ 새 그림(6배 확대)
  ② R36.5-hand-in-poses.jpg  실제 자세에 얹은 모습: 예전(위) ↔ 새 그림(아래) — 1시대 4자세 · 2 · 4시대 2자세씩(3배 확대)
  ③ R36.5-ingame.jpg         게임 화면(1시대 · 3단계 무기 · 4자세 × 좌우) + 손 확대 3컷
사용: python3 -I tools/r36.5/compose36.5.py <옛 빌드> <새 빌드> <게임 촬영 폴더(r36.5func.js)> <출력 폴더>"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

OLD, NEW, CAP, OUT = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
FN = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
F = ImageFont.truetype(FN, 22)
FS = ImageFont.truetype(FN, 16)
FB = ImageFont.truetype(FN, 30)
BG = (16, 18, 24)
CARD = (58, 66, 84)
INK = (232, 230, 223)
DIM = (160, 168, 186)
GOLD = (251, 191, 36)
NEWC = (74, 222, 128)

# ① 무기 그림의 손
NAMES = [("era1_t1", "1시대 1단계 주먹도끼"), ("era1_t2", "1시대 2단계 슴베찌르개"), ("era1_t3", "1시대 3단계 간돌도끼"), ("era2_t1", "2시대 1단계"), ("era2_t2", "2시대 2단계"), ("era2_t3", "2시대 3단계"),
         ("era4_t1", "4시대 1단계"), ("era4_t2", "4시대 2단계"), ("era4_t3", "4시대 3단계")]
Z = 5
cw, ch = 88 * Z, 66 * Z
pad = 12
W = 40 + 3 * (cw * 2 + 6 + pad * 2)
H = 150 + 3 * (ch + 44)
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((40, 22), "R36.5 무기를 쥔 손 — 예전(왼쪽) → 새 그림(오른쪽)", font=FB, fill=GOLD)
d.text((40, 66), "오른쪽을 볼 때 무기를 든 손은 왼손입니다. 왼손을 이쪽에서 보면 엄지가 앞을 가로지르고 손끝이 보여야 합니다(주신 사진과 같은 모습).", font=FS, fill=INK)
d.text((40, 92), "그려져 있던 손가락은 그대로 두고 ① 아래로 삐져나온 엄지를 지우고 ② 엄지를 앞에 얹고 ③ 맨손(1시대)에는 손톱을 그렸습니다.", font=FS, fill=DIM)
for i, (n, lab) in enumerate(NAMES):
    gx = 40 + (i % 3) * (cw * 2 + 6 + pad * 2)
    gy = 136 + (i // 3) * (ch + 44)
    d.text((gx, gy), lab, font=FS, fill=INK)
    for k, root in enumerate((OLD, NEW)):
        im = Image.open(f"{root}/assets/weapon/{n}.png").convert("RGBA").crop((26, 28, 114, 94)).resize((cw, ch), Image.LANCZOS)
        bg = Image.new("RGBA", im.size, CARD + (255,))
        bg.alpha_composite(im)
        img.paste(bg.convert("RGB"), (gx + k * (cw + 6), gy + 24))
img.save(f"{OUT}/R36.5-hand-sprites.jpg", quality=90)
print("sprites", img.size)

# ② 실제 자세에 얹은 모습 — hand_in_context.py로 만든 판에서 잘라 붙인다
tmp = os.path.join(OUT, "_ctx.png")
subprocess.run([sys.executable, "-I", os.path.join(HERE, "hand_in_context.py"), OLD, f"{OLD}/assets/weapon", f"{NEW}/assets/weapon", tmp, "idle,run,atk1_2,atk3_2,hit", "3"], check=True, stdout=subprocess.DEVNULL)
ctx = Image.open(tmp).convert("RGB")
cell = 62 * 2 * 3
rowh = ctx.height // 6
PICK = [(0, "1시대 대사냥꾼", [0, 1, 2, 4], ["서 있기", "달리기", "베기", "맞음"]), (2, "2시대 해모수", [0, 2], ["서 있기", "베기"]), (4, "4시대 척준경", [0, 2], ["서 있기", "베기"])]
cs = 300
cols = 4
W2 = 40 + cols * (cs + 10) * 2 + 40
img2 = Image.new("RGB", (W2, 110 + 2 * (cs * 2 + 70)), BG)
d2 = ImageDraw.Draw(img2)
d2.text((40, 22), "R36.5 실제 자세에 얹은 모습 — 위: 예전 · 아래: 새 그림", font=FB, fill=GOLD)
d2.text((40, 66), "몸 원화 위에 무기를 게임과 같은 방식으로 얹어 3배로 키운 그림입니다(3단계 무기).", font=FS, fill=INK)
slots = []
for hero_row, title, idxs, labs in PICK:
    for i, lab in zip(idxs, labs):
        slots.append((hero_row, title, i, lab))
for s, (hero_row, title, i, lab) in enumerate(slots):
    px = 40 + (s % 8) * (cs + 10)
    py = 110 + (s // 8) * (cs * 2 + 70)
    d2.text((px, py), f"{title} · {lab}", font=FS, fill=INK)
    for k in (0, 1):
        c = ctx.crop((90 + i * (cell + 8), (hero_row + k) * rowh, 90 + i * (cell + 8) + cell, (hero_row + k) * rowh + cell)).resize((cs, cs), Image.LANCZOS)
        img2.paste(c, (px, py + 24 + k * (cs + 6)))
    d2.rectangle((px - 1, py + 24 + cs + 5, px + cs, py + 24 + cs * 2 + 6), outline=NEWC, width=2)
img2 = img2.crop((0, 0, W2, 110 + cs * 2 + 70))
img2.save(f"{OUT}/R36.5-hand-in-poses.jpg", quality=90)
os.remove(tmp)
print("poses", img2.size)

# ③ 게임 화면
names = [("idle", "서 있기"), ("run3", "달리기"), ("atk1_2", "베기"), ("atk3_2", "내려찍기")]
w, h = 450, 338
W3 = 40 + 4 * (w + 8) + 32
img3 = Image.new("RGB", (W3, 110 + 2 * (h + 8) + 330), BG)
d3 = ImageDraw.Draw(img3)
d3.text((40, 22), "R36.5 게임 화면 — 1시대 대사냥꾼 · 3단계 간돌도끼(위: 오른쪽 보기 · 아래: 왼쪽 보기)", font=FB, fill=GOLD)
d3.text((40, 66), "왼쪽을 볼 때는 같은 그림을 거울처럼 뒤집어 씁니다.", font=FS, fill=DIM)
for r, f in enumerate("RL"):
    for c, (n, lab) in enumerate(names):
        im = Image.open(f"{CAP}/e1_t3_{n}_{f}.png").convert("RGB").resize((w, h), Image.LANCZOS)
        img3.paste(im, (40 + c * (w + 8), 104 + r * (h + 8)))
        if r == 0:
            d3.text((46 + c * (w + 8), 108), lab, font=FS, fill=GOLD)
y3 = 104 + 2 * (h + 8) + 12
d3.text((40, y3), "손 확대(게임 화면 그대로)", font=F, fill=INK)
crops = [("e1_t3_idle_R", (560, 330, 920, 630)), ("e1_t3_run3_R", (440, 60, 800, 360)), ("e1_t3_atk1_2_L", (0, 180, 360, 480)), ("e1_t1_idle_R", (560, 330, 920, 630))]
for i, (n, box) in enumerate(crops):
    im = Image.open(f"{CAP}/{n}.png").convert("RGB").crop(box).resize((432, 360), Image.LANCZOS).crop((0, 40, 432, 320))
    img3.paste(im, (40 + i * (432 + 26), y3 + 34))
img3.save(f"{OUT}/R36.5-ingame.jpg", quality=90)
print("ingame", img3.size)
