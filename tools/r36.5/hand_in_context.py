#!/usr/bin/env python3
"""R36.5 — 새 손을 실제 자세에 얹어 보기: 몸 원화 + 무기를 게임과 같은 변환으로 합성(옛 무기 ↔ 새 무기).
  ① 손 둘레 확대(무기 쥔 자리 ±70px · 3배)  ② 게임 화면 크기(전신 · 0.5배)
사용: python3 -I tools/r36.5/hand_in_context.py <몸 원화가 있는 빌드> <옛 무기 폴더> <새 무기 폴더> <출력 png> [프레임 이름들(쉼표)] [단계=3]"""
import json
import os
import re
import sys

from PIL import Image, ImageDraw

BUILD, OLD, NEW, OUT = sys.argv[1:5]
FR = sys.argv[5].split(",") if len(sys.argv) > 5 else ["idle", "run", "run5", "atk_prep", "atk1_2", "atk2_3", "atk3_2", "hit"]
TIER = int(sys.argv[6]) if len(sys.argv) > 6 else 3
HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "..", "r33", "grips_r33.json"), encoding="utf-8"))
src = open(os.path.join(BUILD, "index.html"), encoding="utf-8").read()
HEROES = [("R27_HUNTER_FRAMES", "era1_hunter", "era1"), ("R26_HM_FRAMES", "era2_hero", "era2"), ("R26_CJG_FRAMES", "era4_hero", "era4")]
PAD = 200


def meta(key):
    m = re.search(r"weapon: \{ frames: " + key + r", sprites: (\{.*?\}\}) \}", src)
    t = re.sub(r'name:"[^"]*"', 'name:""', m.group(1))
    return json.loads(re.sub(r"(\w+):", r'"\1":', t))


def compose(pre, wdir, wpre, key, name, facing=1):
    body = Image.open(f"{BUILD}/assets/hero/{pre}_{name}.webp").convert("RGBA").resize((512, 512), Image.LANCZOS)
    cv = Image.new("RGBA", (512 + PAD * 2, 512 + PAD * 2), (0, 0, 0, 0))
    cv.alpha_composite(body, (PAD, PAD))
    x, y, ang, flip = G[key][name][:4]
    M = meta(key)[str(TIER)]
    w = Image.open(f"{wdir}/{wpre}_t{TIER}.png").convert("RGBA").resize((M["w"], M["h"]), Image.LANCZOS)
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
    if facing < 0:
        cv = cv.transpose(Image.FLIP_LEFT_RIGHT)
        return cv, (cv.width - (PAD + x), PAD + y)
    return cv, (PAD + x, PAD + y)


Z, RAD = 3, 62
cell = RAD * 2 * Z
small = 250
W = 90 + len(FR) * (cell + 8)
rows = []
for key, pre, wpre in HEROES:
    names = [n for n in FR if n in G[key]]
    for label, wdir in (("old", OLD), ("new", NEW)):
        row = Image.new("RGB", (W, cell + small + 12), (22, 24, 30))
        d = ImageDraw.Draw(row)
        d.text((6, 6), f"{wpre}\n{label}", fill=(255, 230, 120))
        for i, n in enumerate(names):
            cv, (gx, gy) = compose(pre, wdir, wpre, key, n)
            bg = Image.new("RGBA", cv.size, (58, 66, 84, 255))
            bg.alpha_composite(cv)
            c = bg.crop((int(gx - RAD), int(gy - RAD), int(gx + RAD), int(gy + RAD))).resize((cell, cell), Image.LANCZOS)
            row.paste(c.convert("RGB"), (90 + i * (cell + 8), 0))
            d.text((94 + i * (cell + 8), 4), n, fill=(255, 255, 255))
            full = bg.crop((PAD - 60, PAD - 40, PAD + 512 + 190, PAD + 512 + 10)).resize((int(762 * small / 562), small), Image.LANCZOS)
            row.paste(full.convert("RGB").crop((0, 0, min(full.width, cell), small)), (90 + i * (cell + 8), cell + 8))
        rows.append(row)
sheet = Image.new("RGB", (W, sum(r.height for r in rows)), (22, 24, 30))
y = 0
for r in rows:
    sheet.paste(r, (0, y))
    y += r.height
sheet.save(OUT)
print(OUT, sheet.size)
