import json, sys, os, bisect
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 14)
def sheet(tag, start, n, out):
    d = f"runfilm/{tag}"
    ts = json.load(open(f"{d}/frames.json")); log = json.load(open(f"{d}/log.json"))
    lt = [l["t"] / 1000 for l in log]
    tiles = []
    for i in range(start, min(start + n, len(ts))):
        im = Image.open(f"{d}/f{i:03d}.png").convert("RGB")
        j = min(len(log) - 1, max(0, bisect.bisect_left(lt, ts[i]) - 1))
        L = log[j]
        sx = L["x"] - L["cam"]
        c = im.crop((int(sx - 110), 250, int(sx + 130), 500))
        dr = ImageDraw.Draw(c)
        dr.rectangle((0, 0, 239, 18), fill=(0, 0, 0)); dr.text((3, 1), f"#{i} {L['pose']} t{L['tick']} st{L['st']}", font=F, fill=(255, 255, 0))
        tiles.append(c)
    cols = 8
    S = Image.new("RGB", (240 * cols, 250 * ((len(tiles) + cols - 1) // cols)), (0, 0, 0))
    for k, t in enumerate(tiles): S.paste(t, ((k % cols) * 240, (k // cols) * 250))
    S.save(out); print(out, S.size)
sheet(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
