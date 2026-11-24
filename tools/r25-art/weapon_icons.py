#!/usr/bin/env python3
"""무기 스프라이트(PNG)에서 256×256 아이콘 만들기 — 대각선 배치 + 등급색 번짐 + 반짝임.
사용: python3 weapon_icons.py WEAPON_PNG OUT_PNG GLOW_HEX
"""
import sys
from PIL import Image, ImageFilter, ImageDraw

src, out, col = sys.argv[1], sys.argv[2], sys.argv[3]
w = Image.open(src).convert("RGBA")
# 무기 스프라이트는 손잡이 쥔 주먹까지 포함 → 아이콘에는 주먹이 보이지 않게 손잡이 영역을 남기되 그대로 둔다(작게 보임)
scale = 330 / w.width
w = w.resize((int(w.width * scale), int(w.height * scale)), Image.LANCZOS)
big = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
big.alpha_composite(w, ((420 - w.width) // 2, (420 - w.height) // 2))
big = big.rotate(40, resample=Image.BICUBIC)
icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
# 번짐
r, g, b = int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)
halo = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(halo)
for k in range(10, 0, -1):
    a = int(10 + 9 * (10 - k))
    rad = 10 + k * 10
    d.ellipse((128 - rad, 128 - rad, 128 + rad, 128 + rad), fill=(r, g, b, min(110, a // 2)))
halo = halo.filter(ImageFilter.GaussianBlur(14))
icon.alpha_composite(halo)
icon.alpha_composite(big.crop((82, 82, 338, 338)))
# 반짝임
sp = ImageDraw.Draw(icon)
x, y, s = 196, 54, 13
sp.polygon([(x, y - s), (x + 3, y - 3), (x + s, y), (x + 3, y + 3), (x, y + s), (x - 3, y + 3), (x - s, y), (x - 3, y - 3)], fill=(255, 255, 255, 235))
icon.save(out, optimize=True)
print("icon", out)
