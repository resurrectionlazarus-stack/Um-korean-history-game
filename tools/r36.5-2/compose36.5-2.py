#!/usr/bin/env python3
"""R36.5-2 납품 이미지 합성
  ① R36.5-2-hand-sprites.jpg   무기 그림 9장의 손: R36.5(왼쪽) → R36.5-2(오른쪽) · 5배 확대
  ② R36.5-2-proportion.jpg     비율: 어디서 가져온 손인가(몸 원화의 주먹) + 전신 비교(세 주인공 · 서 있기 / 달리기 / 베기)
  ③ R36.5-2-hand-in-poses.jpg  실제 자세에 얹은 모습(3배): 세 주인공 × 5자세 · 위 예전 / 아래 새 그림
  ④ R36.5-2-ingame.jpg         게임 화면 촬영(기능 테스트가 찍은 그대로): 세 주인공 × 4자세 · 위 R36.5 / 아래 R36.5-2
사용: python3 -I tools/r36.5-2/compose36.5-2.py <옛 빌드(R36.5)> <새 빌드> <옛 촬영 폴더> <새 촬영 폴더> <출력 폴더>
      ② · ③은 몸 원화 위에 무기를 게임과 같은 변환(쥔 자리 표 tools/r33/grips_r33.json)으로 얹은 합성이다."""
import json
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OLD, NEW, CAP_OLD, CAP_NEW, OUT = sys.argv[1:6]
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
OLDC = (248, 113, 113)

G = json.load(open(os.path.join(HERE, "..", "r33", "grips_r33.json"), encoding="utf-8"))
SRC = open(os.path.join(NEW, "index.html"), encoding="utf-8").read()
HEROES = [("R27_HUNTER_FRAMES", "era1_hunter", "era1", "1시대 대사냥꾼"), ("R26_HM_FRAMES", "era2_hero", "era2", "2시대 해모수"), ("R26_CJG_FRAMES", "era4_hero", "era4", "4시대 척준경")]
PAD = 200


def meta(key):
    m = re.search(r"weapon: \{ frames: " + key + r", sprites: (\{.*?\}\}) \}", SRC)
    t = re.sub(r'name:"[^"]*"', 'name:""', m.group(1))
    return json.loads(re.sub(r"(\w+):", r'"\1":', t))


def compose(root, hi, name, tier=3):
    """몸 원화 + 무기(게임과 같은 변환) → (그림, 쥔 자리)."""
    key, pre, wpre, _ = HEROES[hi]
    body = Image.open(f"{NEW}/assets/hero/{pre}_{name}.webp").convert("RGBA").resize((512, 512), Image.LANCZOS)
    cv = Image.new("RGBA", (512 + PAD * 2, 512 + PAD * 2), (0, 0, 0, 0))
    cv.alpha_composite(body, (PAD, PAD))
    x, y, ang, flip = G[key][name][:4]
    M = meta(key)[str(tier)]
    w = Image.open(f"{root}/assets/weapon/{wpre}_t{tier}.png").convert("RGBA").resize((M["w"], M["h"]), Image.LANCZOS)
    gy = M["gy"]
    if flip:
        w = w.transpose(Image.FLIP_TOP_BOTTOM)
        gy = M["h"] - M["gy"]
    R = 520
    big = Image.new("RGBA", (R * 2, R * 2), (0, 0, 0, 0))
    big.alpha_composite(w, (R - M["gx"], R - gy))
    big = big.rotate(-ang, resample=Image.BICUBIC, center=(R, R))
    ox, oy = int(round(PAD + x - R)), int(round(PAD + y - R))
    tmp = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    cx0, cy0 = max(0, -ox), max(0, -oy)
    cx1, cy1 = min(big.width, cv.width - ox), min(big.height, cv.height - oy)
    tmp.alpha_composite(big.crop((cx0, cy0, cx1, cy1)), (ox + cx0, oy + cy0))
    cv.alpha_composite(tmp)
    bg = Image.new("RGBA", cv.size, CARD + (255,))
    bg.alpha_composite(cv)
    return bg.convert("RGB"), (PAD + x, PAD + y)


def on_card(im, size, resample=Image.LANCZOS):
    im = im.resize(size, resample)
    bg = Image.new("RGBA", im.size, CARD + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


# ① 무기 그림의 손
NAMES = [("era1_t1", "1시대 1단계 주먹도끼"), ("era1_t2", "1시대 2단계 슴베찌르개"), ("era1_t3", "1시대 3단계 간돌도끼"), ("era2_t1", "2시대 1단계"), ("era2_t2", "2시대 2단계"), ("era2_t3", "2시대 3단계"),
         ("era4_t1", "4시대 1단계"), ("era4_t2", "4시대 2단계"), ("era4_t3", "4시대 3단계")]
Z = 5
cw, ch = 100 * Z, 66 * Z
pad = 12
W = 40 + 3 * (cw * 2 + 6 + pad * 2)
H = 150 + 3 * (ch + 44)
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((40, 22), "R36.5-2 무기를 쥔 손 — R36.5(왼쪽) → 새 그림(오른쪽)", font=FB, fill=GOLD)
d.text((40, 66), "손을 새로 그리지 않고, 미술팀이 달리기 원화에 그려 둔 그 주인공의 주먹을 같은 크기 그대로 옮겼습니다(손잡이를 감싸도록 90° 돌림).", font=FS, fill=INK)
d.text((40, 92), "1시대는 큰 손에 맞춰 굵게 그려져 있던 자루도 손에 맞게 가늘게 했습니다. 그림 크기 · 쥔 자리 · 날은 그대로입니다(5배 확대).", font=FS, fill=DIM)
for i, (n, lab) in enumerate(NAMES):
    gx = 40 + (i % 3) * (cw * 2 + 6 + pad * 2)
    gy = 136 + (i // 3) * (ch + 44)
    d.text((gx, gy), lab, font=FS, fill=INK)
    x0 = 14 if n == "era4_t3" else 20
    for k, root in enumerate((OLD, NEW)):
        im = on_card(Image.open(f"{root}/assets/weapon/{n}.png").convert("RGBA").crop((x0, 26, x0 + 100, 92)), (cw, ch))
        img.paste(im, (gx + k * (cw + 6), gy + 24))
    d.rectangle((gx + cw + 5, gy + 23, gx + cw * 2 + 6, gy + 24 + ch), outline=NEWC, width=2)
img.save(f"{OUT}/R36.5-2-hand-sprites.jpg", quality=90)
print("sprites", img.size)

# ② 비율
ZF = 6
W2 = 2240
img2 = Image.new("RGB", (W2, 2900), BG)
d2 = ImageDraw.Draw(img2)
d2.text((40, 22), "R36.5-2 손 비율 — 팔뚝 끝에서 손이 갑자기 커지지 않게", font=FB, fill=GOLD)
d2.text((40, 66), "예전 무기 그림의 손은 몸 원화의 주먹보다 컸습니다(1시대는 길이 63px ↔ 몸의 주먹 42px · 팔 보호대 굵기 31px). 그래서 팔 끝에서 손이 부풀어 보였습니다.", font=FS, fill=INK)
d2.text((40, 92), "새 손은 몸 원화에 그려진 주먹 그 자체입니다 → 같은 주인공의 다른 손과 크기 · 붓 자국 · 색이 같습니다.", font=FS, fill=DIM)
BOX = {0: (424, 158, 488, 220), 1: (424, 150, 488, 214), 2: (418, 138, 482, 202)}
y = 130
for hi, (key, pre, wpre, title) in enumerate(HEROES):
    bx = BOX[hi]
    x = 40
    d2.text((x, y), title, font=F, fill=GOLD)
    y += 34
    d2.text((x, y), "① 달리기 원화의 주먹(미술팀 그림)", font=FS, fill=INK)
    src = Image.open(f"{NEW}/assets/hero/{pre}_run.webp").convert("RGBA").crop(bx)
    c1 = on_card(src, (src.width * ZF, src.height * ZF), Image.NEAREST)
    img2.paste(c1, (x, y + 24))
    x += c1.width + 24
    d2.text((x, y), "② 예전 무기 손(R36.5)", font=FS, fill=OLDC)
    x0 = 14 if hi == 2 else 20
    c2 = on_card(Image.open(f"{OLD}/assets/weapon/{wpre}_t3.png").convert("RGBA").crop((x0, 26, x0 + 100, 26 + 64)), (100 * ZF, 64 * ZF), Image.NEAREST)
    img2.paste(c2, (x, y + 24))
    x += c2.width + 24
    d2.text((x, y), "③ 새 무기 손(①을 90° 돌려 손잡이에) — ① ② ③ 모두 6배라 크기를 그대로 비교할 수 있습니다", font=FS, fill=NEWC)
    c3 = on_card(Image.open(f"{NEW}/assets/weapon/{wpre}_t3.png").convert("RGBA").crop((x0, 26, x0 + 100, 26 + 64)), (100 * ZF, 64 * ZF), Image.NEAREST)
    img2.paste(c3, (x, y + 24))
    d2.rectangle((x - 1, y + 23, x + c3.width, y + 24 + c3.height), outline=NEWC, width=2)
    y += 24 + 64 * ZF + 16
    # 전신: 서 있기 · 달리기 · 베기 — 위 예전 / 아래 새 그림을 나란히
    cells = []
    for name in ("idle", "run", "atk1_2"):
        for root in (OLD, NEW):
            im, _ = compose(root, hi, name)
            cells.append(im.crop((PAD + 40, PAD - 10, PAD + 512 + 150, PAD + 500)).resize((349, 286), Image.LANCZOS))
    labs = ["서 있기", "달리기", "베기"]
    for i, c in enumerate(cells):
        px = 40 + i * (349 + 10) + (i // 2) * 14
        img2.paste(c, (px, y + 24))
        col = NEWC if i % 2 else OLDC
        d2.text((px + 6, y + 28), f"{labs[i // 2]} · {'새 그림' if i % 2 else 'R36.5'}", font=FS, fill=col)
        if i % 2:
            d2.rectangle((px - 1, y + 23, px + 349, y + 24 + 286), outline=NEWC, width=2)
    y += 24 + 286 + 34
img2 = img2.crop((0, 0, W2, y))
img2.save(f"{OUT}/R36.5-2-proportion.jpg", quality=90)
print("proportion", img2.size)

# ③ 실제 자세에 얹은 모습(손 둘레 3배)
POSES = [("idle", "서 있기"), ("run", "달리기"), ("atk1_2", "베기"), ("atk3_2", "내려찍기"), ("hit", "맞음")]
RAD, ZP = 50, 3
cs = RAD * 2 * ZP
W3 = 40 + len(POSES) * (cs + 10) + 30
img3 = Image.new("RGB", (W3, 110 + 3 * (cs * 2 + 70)), BG)
d3 = ImageDraw.Draw(img3)
d3.text((40, 22), "R36.5-2 실제 자세에 얹은 모습 — 위: R36.5 · 아래: 새 그림", font=FB, fill=GOLD)
d3.text((40, 66), "몸 원화 위에 3단계 무기를 게임과 같은 방식으로 얹어 3배로 키운 그림입니다.", font=FS, fill=INK)
for hi, (key, pre, wpre, title) in enumerate(HEROES):
    py = 110 + hi * (cs * 2 + 70)
    for i, (name, lab) in enumerate(POSES):
        px = 40 + i * (cs + 10)
        d3.text((px, py), f"{title} · {lab}", font=FS, fill=INK)
        for k, root in enumerate((OLD, NEW)):
            im, (gx, gy) = compose(root, hi, name)
            c = im.crop((int(gx - RAD), int(gy - RAD), int(gx + RAD), int(gy + RAD))).resize((cs, cs), Image.LANCZOS)
            img3.paste(c, (px, py + 24 + k * (cs + 6)))
        d3.rectangle((px - 1, py + 24 + cs + 5, px + cs, py + 24 + cs * 2 + 6), outline=NEWC, width=2)
img3.save(f"{OUT}/R36.5-2-hand-in-poses.jpg", quality=90)
print("poses", img3.size)

# ④ 게임 화면
names = [("idle", "R", "서 있기"), ("run3", "R", "달리기"), ("atk1_2", "R", "베기"), ("atk3_2", "L", "내려찍기(왼쪽 보기)")]
w, h = 450, 338
W4 = 40 + 4 * (w + 8) + 32
img4 = Image.new("RGB", (W4, 110 + 3 * (2 * (h + 6) + 46)), BG)
d4 = ImageDraw.Draw(img4)
d4.text((40, 22), "R36.5-2 게임 화면 — 3단계 무기(위: R36.5 · 아래: 새 그림)", font=FB, fill=GOLD)
d4.text((40, 66), "기능 테스트가 게임을 실제로 돌려 찍은 화면입니다. 왼쪽을 볼 때는 같은 그림을 거울처럼 뒤집어 씁니다.", font=FS, fill=DIM)
for hi, era in enumerate((1, 2, 4)):
    py = 104 + hi * (2 * (h + 6) + 46)
    d4.text((40, py), HEROES[hi][3], font=F, fill=INK)
    for r, cap in enumerate((CAP_OLD, CAP_NEW)):
        for c, (n, f, lab) in enumerate(names):
            im = Image.open(f"{cap}/e{era}_t3_{n}_{f}.png").convert("RGB").resize((w, h), Image.LANCZOS)
            px, qy = 40 + c * (w + 8), py + 32 + r * (h + 6)
            img4.paste(im, (px, qy))
            d4.text((px + 6, qy + 4), f"{lab} · {'새 그림' if r else 'R36.5'}", font=FS, fill=NEWC if r else OLDC)
            if r:
                d4.rectangle((px - 1, qy - 1, px + w, qy + h), outline=NEWC, width=2)
img4.save(f"{OUT}/R36.5-2-ingame.jpg", quality=88)
print("ingame", img4.size)
