#!/usr/bin/env python3
"""R36 미술 발주용 기준 그림 — 무기를 쥐는 팔: 지금(먼 팔 = 왼손) → 요청(가까운 팔 = 오른손)
  ① 지금 모습: 몸 원화 + 무기를 게임과 같은 방식(쥔 자리 표 · 회전 · 뒤집기)으로 얹은 합성. 노란 원 = 지금 무기를 쥔 손(먼 팔) · 하늘색 원 = 가까운 팔의 빈 주먹
  ② 요청 모습: 막대 사람 그림(두 팔의 역할을 서로 바꿈)
사용: python3 -I tools/r36/hand_order_sheet.py <빌드 폴더> <출력 jpg>"""
import json
import math
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

BUILD, OUT = sys.argv[1:3]
HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "..", "r33", "grips_r33.json"), encoding="utf-8"))
src = open(os.path.join(BUILD, "index.html"), encoding="utf-8").read()
FN = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
F = ImageFont.truetype(FN, 22)
FS = ImageFont.truetype(FN, 17)
FB = ImageFont.truetype(FN, 34)
FM = ImageFont.truetype(FN, 26)
BG = (16, 18, 24)
CARD = (30, 34, 44)
INK = (232, 230, 223)
DIM = (160, 168, 186)
GOLD = (251, 191, 36)
CYAN = (56, 189, 248)
RED = (248, 113, 113)
GREEN = (74, 222, 128)


def meta(key):
    m = re.search(r"weapon: \{ frames: " + key + r", sprites: (\{.*?\}\}) \}", src)
    t = re.sub(r'name:"[^"]*"', 'name:""', m.group(1))
    t = re.sub(r"(\w+):", r'"\1":', t).replace('"glow":null', '"glow":null')
    return json.loads(t)


# [표 이름, 파일 머리말, 무기 머리말, 이름, 가까운 팔 빈 주먹 자리(눈으로 잡은 값) {프레임: (x, y)}]
HEROES = [
    ("R27_HUNTER_FRAMES", "era1_hunter", "era1", "1시대 대사냥꾼 (22장)", {"run": (195, 240), "atk1_2": (265, 268), "atk3_2": (265, 268), "idle": None}),
    ("R26_HM_FRAMES", "era2_hero", "era2", "2시대 해모수 (26장)", {"run": (206, 242), "atk1_2": (210, 283), "atk3_2": None, "idle": None}),
    ("R26_CJG_FRAMES", "era4_hero", "era4", "4시대 척준경 (26장)", {"run": (166, 230), "atk1_2": (189, 263), "atk3_2": None, "idle": None}),
]
FRAMES = [("idle", "서 있기"), ("run", "달리기"), ("atk1_2", "베기(1타)"), ("atk3_2", "내려찍기(마무리)")]
TIER = 3


def compose(pre, wpre, key, name):
    """몸 원화 위에 무기를 게임과 같은 변환으로 얹는다(512 좌표계 · 여백 200씩)."""
    PAD = 200
    body = Image.open(f"{BUILD}/assets/hero/{pre}_{name}.webp").convert("RGBA")
    s = body.width / 512
    if s != 1:
        body = body.resize((512, 512), Image.LANCZOS)
    cv = Image.new("RGBA", (512 + PAD * 2, 512 + PAD * 2), (0, 0, 0, 0))
    cv.alpha_composite(body, (PAD, PAD))
    x, y, ang, flip = G[key][name][:4]
    M = meta(key)[str(TIER)]
    w = Image.open(f"{BUILD}/assets/weapon/{wpre}_t{TIER}.png").convert("RGBA").resize((M["w"], M["h"]), Image.LANCZOS)
    if flip:
        w = w.transpose(Image.FLIP_TOP_BOTTOM)
        gy = M["h"] - M["gy"]
    else:
        gy = M["gy"]
    R = 520
    big = Image.new("RGBA", (R * 2, R * 2), (0, 0, 0, 0))
    big.alpha_composite(w, (R - M["gx"], R - gy))
    big = big.rotate(-ang, resample=Image.BICUBIC, center=(R, R))
    ox, oy = int(round(PAD + x - R)), int(round(PAD + y - R))
    tmp = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    # 캔버스 밖으로 나가는 부분은 잘라서 붙인다
    cx0, cy0 = max(0, -ox), max(0, -oy)
    cx1, cy1 = min(big.width, cv.width - ox), min(big.height, cv.height - oy)
    tmp.alpha_composite(big.crop((cx0, cy0, cx1, cy1)), (ox + cx0, oy + cy0))
    cv.alpha_composite(tmp)
    return cv, (PAD + x, PAD + y), PAD


CELL = 400     # 한 칸(잘라낸 뒤 크기)
CROP = (150, 96, 912, 858)   # 여백 포함 912 캔버스에서 잘라낼 영역(762 정사각 — 오른쪽으로 뻗는 무기 끝까지 보이게)
W = 60 + CELL * 4 + 30 * 3 + 60
rows_h = len(HEROES) * (CELL + 74)
H = 190 + rows_h + 590
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((60, 36), "무기를 쥐는 팔을 바꿔 주세요 — 지금: 먼 팔(왼손)  →  요청: 가까운 팔(오른손)", font=FB, fill=GOLD)
d.text((60, 90), "아래는 지금 게임 화면 그대로입니다(몸 원화 + 무기를 코드로 얹음 · 오른쪽을 보는 기준).", font=F, fill=INK)
d.text((60, 122), "노란 원 = 지금 무기를 쥔 손 — 몸 뒤쪽(먼) 팔이라 가슴 · 턱 뒤에서 무기가 튀어나옵니다.   하늘색 원 = 몸 앞쪽(가까운) 팔 — 빈 주먹으로 허리 옆에 있습니다.", font=FS, fill=DIM)
y0 = 176
k = CELL / (CROP[2] - CROP[0])
for hi, (key, pre, wpre, title, near) in enumerate(HEROES):
    d.text((60, y0 + 6), title, font=FM, fill=INK)
    for fi, (name, lab) in enumerate(FRAMES):
        cv, grip, PAD = compose(pre, wpre, key, name)
        card = Image.new("RGBA", cv.size, CARD + (255,))
        card.alpha_composite(cv)
        cd = ImageDraw.Draw(card)
        gx, gy = grip
        cd.ellipse((gx - 46, gy - 46, gx + 46, gy + 46), outline=GOLD + (255,), width=7)
        nf = near.get(name)
        if nf:
            nx, ny = PAD + nf[0], PAD + nf[1]
            cd.ellipse((nx - 40, ny - 40, nx + 40, ny + 40), outline=CYAN + (255,), width=7)
        cell = card.crop(CROP).resize((CELL, CELL), Image.LANCZOS).convert("RGB")
        px = 60 + fi * (CELL + 30)
        img.paste(cell, (px, y0 + 44))
        d.text((px + 10, y0 + 50), lab, font=FS, fill=GOLD)
    y0 += CELL + 74

# ── 요청 모습: 막대 사람
y1 = y0 + 14
d.text((60, y1), "이렇게 바꿔 주세요 — 두 팔의 역할을 서로 바꿉니다", font=FB, fill=GREEN)


def stick(ox, oy, near_weapon, title, col):
    """오른쪽을 보는 막대 사람. near_weapon = True면 가까운 팔이 무기를 쥠."""
    d.rounded_rectangle((ox, oy, ox + 640, oy + 470), radius=18, fill=CARD)
    d.text((ox + 22, oy + 16), title, font=FM, fill=col)
    hx, hy = ox + 250, oy + 150      # 어깨 중심
    hip = (ox + 235, oy + 300)
    FAR = (120, 128, 146)
    NEAR = (240, 238, 230)

    def limb(pts, c, w):
        d.line(pts, fill=c, width=w, joint="curve")
        for p in pts:
            d.ellipse((p[0] - w // 2, p[1] - w // 2, p[0] + w // 2, p[1] + w // 2), fill=c)

    def weapon(hand, ang_deg, c):
        a = math.radians(ang_deg)
        tip = (hand[0] + 190 * math.cos(a), hand[1] - 190 * math.sin(a))
        d.line([hand, tip], fill=(176, 132, 84), width=10)
        # 도끼 머리
        hx2, hy2 = hand[0] + 168 * math.cos(a), hand[1] - 168 * math.sin(a)
        d.ellipse((hx2 - 30, hy2 - 30, hx2 + 30, hy2 + 30), fill=(150, 156, 168), outline=c, width=5)
        d.ellipse((hand[0] - 15, hand[1] - 15, hand[0] + 15, hand[1] + 15), fill=c)

    # 뒤쪽(먼) 다리 · 팔 먼저(어둡게), 몸통, 앞쪽(가까운) 다리 · 팔 나중에(밝게)
    limb([hip, (hip[0] + 70, hip[1] + 70), (hip[0] + 95, hip[1] + 150)], FAR, 16)
    if near_weapon:
        # 먼 팔: 허리 옆으로 당긴 빈 주먹
        fa = [(hx + 14, hy + 4), (hx - 20, hy + 70), (hx + 30, hy + 104)]
        limb(fa, FAR, 15)
        d.ellipse((fa[-1][0] - 15, fa[-1][1] - 15, fa[-1][0] + 15, fa[-1][1] + 15), fill=FAR)
    else:
        # 먼 팔: 앞으로 뻗어 무기를 쥠 — 가슴 뒤에서 나옴
        fa = [(hx + 14, hy + 4), (hx + 90, hy + 30), (hx + 170, hy + 6)]
        limb(fa, FAR, 15)
        weapon(fa[-1], 38, GOLD)
    d.line([(hx, hy), hip], fill=NEAR, width=34)       # 몸통
    d.ellipse((hx + 2, hy - 86, hx + 70, hy - 18), fill=NEAR)   # 머리
    d.polygon([(hx + 66, hy - 52), (hx + 84, hy - 46), (hx + 66, hy - 40)], fill=NEAR)   # 코(보는 방향)
    limb([hip, (hip[0] - 46, hip[1] + 78), (hip[0] - 96, hip[1] + 140)], NEAR, 18)
    if near_weapon:
        na = [(hx - 8, hy + 6), (hx + 78, hy + 44), (hx + 160, hy + 22)]
        limb(na, NEAR, 18)
        weapon(na[-1], 38, GREEN)
        d.text((ox + 330, oy + 236), "가까운 팔(오른손)이 무기", font=FS, fill=GREEN)
        d.text((ox + 330, oy + 260), "몸 앞에 그려짐 · 손목까지만", font=FS, fill=GREEN)
        d.text((ox + 30, oy + 236), "먼 팔(왼손)", font=FS, fill=DIM)
        d.text((ox + 30, oy + 260), "빈 주먹 · 몸 뒤", font=FS, fill=DIM)
    else:
        na = [(hx - 8, hy + 6), (hx - 62, hy + 62), (hx - 22, hy + 110)]
        limb(na, NEAR, 18)
        d.ellipse((na[-1][0] - 17, na[-1][1] - 17, na[-1][0] + 17, na[-1][1] + 17), fill=CYAN)
        d.text((ox + 380, oy + 236), "먼 팔(왼손)이 무기", font=FS, fill=GOLD)
        d.text((ox + 380, oy + 260), "가슴 뒤에서 튀어나옴", font=FS, fill=GOLD)
        d.text((ox + 30, oy + 290), "가까운 팔(오른손)", font=FS, fill=CYAN)
        d.text((ox + 30, oy + 314), "빈 주먹", font=FS, fill=CYAN)
    d.line([(ox + 60, oy + 446), (ox + 580, oy + 446)], fill=(70, 78, 96), width=3)


stick(60, y1 + 60, False, "지금", RED)
stick(60 + 640 + 40, y1 + 60, True, "요청", GREEN)
tx = 60 + 640 * 2 + 80
notes = ["규칙", "① 화면 앞쪽(가까운) 팔 = 무기 팔.", "   몸통 앞에 그립니다.", "② 무기 팔은 손목까지만.", "   (손 · 무기는 코드가 얹습니다)", "③ 먼 팔은 빈 주먹.", "④ 크기 · 발 위치 · 파일 이름은", "   지금과 같게.", "⑤ 휘두를 때 팔 전체가", "   궤적을 따라 움직이게."]
for i, t in enumerate(notes):
    d.text((tx, y1 + 70 + i * 34), t, font=F if i else FM, fill=GREEN if i == 0 else INK)
img.save(OUT, quality=90)
print(OUT, img.size)
