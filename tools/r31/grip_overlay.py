#!/usr/bin/env python3
"""R31 무기 쥔 자리 검증 시트 — 몸 원화 위에 무기 스프라이트를 게임과 같은 방식(쥔 자리 gx,gy를 주먹에 · 각도 회전 · 뒤집기)으로 얹는다.
사용: python3 -I grip_overlay.py <grips.json> <몸 폴더> <접두사> <무기 png> <출력 png>"""
import json
import math
import sys

from PIL import Image, ImageDraw

G, D, pre, wpath, out = sys.argv[1:6]
grips = json.load(open(G))
wp = Image.open(wpath).convert("RGBA")
GX, GY = 70, 60
T = 256
names = list(grips.keys())
W = Image.new("RGB", (len(names) * (T + 4), T + 18), (24, 24, 28))
dr = ImageDraw.Draw(W)
for i, n in enumerate(names):
    x, y, ang, flip = grips[n]
    body = Image.open(f"{D}/{pre}_{n}.webp").convert("RGBA")
    can = Image.new("RGBA", (512, 512), (70, 76, 88, 255))
    can.alpha_composite(body)
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if flip else wp
    gy = (w.height - GY) if flip else GY
    big = Image.new("RGBA", (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - GX, cy - gy))
    rot = big.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
    can.alpha_composite(rot, (int(x - cx), int(y - cy)))
    d = ImageDraw.Draw(can)
    d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(255, 60, 60, 255), width=2)
    W.paste(can.convert("RGB").resize((T, T)), (i * (T + 4), 18))
    dr.text((i * (T + 4) + 4, 2), f"{n} {x},{y} {ang}", fill=(240, 240, 240))
W.save(out)
print("ok", len(names))
