# R35 자세 모음 — mirror_check.js가 찍은 그림을 한 장으로(시대 · 방향별) 모아 눈으로 확인
#  python3 -I tools/r35/pose_sheet.py <dir> <era> <R|L> <out.png> [prefix=t3_f_] [cols=6]
import sys, json, os
from PIL import Image, ImageDraw
D, era, side, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
pre = sys.argv[5] if len(sys.argv) > 5 else 't3_f_'
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 6
M = json.load(open(os.path.join(D, 'meta.json')))[era]
tags = [t for t in M['shots'] if t.startswith(pre)]
cw, ch = 330, 380
rows = (len(tags) + cols - 1) // cols
sh = Image.new('RGB', (cw * cols, ch * rows), (16, 16, 16))
for i, t in enumerate(tags):
    im = Image.open(os.path.join(D, f'e{era}_{t}_{side}.png')).convert('RGB')
    W, H = im.size
    c = im.crop((W // 2 - 330, H - 760, W // 2 + 330, H)).resize((cw, ch), Image.LANCZOS)
    d = ImageDraw.Draw(c); d.text((6, 4), t.replace(pre, ''), fill=(255, 255, 0))
    sh.paste(c, ((i % cols) * cw, (i // cols) * ch))
sh.save(out); print(out, sh.size, len(tags))
