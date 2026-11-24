# @2x PNG → 1x PNG (정확히 절반) — 사용: python3 down2.py IN OUT
import sys, os
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith('@2x.png'): continue
    im = Image.open(os.path.join(src, f)).convert('RGBA')
    im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    a = im.getchannel('A').point(lambda v: 0 if v < 6 else v)
    im.putalpha(a)
    im.save(os.path.join(dst, f.replace('@2x', '')), optimize=True)
print('down ok')
