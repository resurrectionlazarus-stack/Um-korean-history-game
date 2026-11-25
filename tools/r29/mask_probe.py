# R29 원화 색 바꾸기 사전 점검 — 피부 마스크 시각화
import sys
import numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert("RGBA")).astype(np.float32) / 255
rgb = a[..., :3]
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
mx = rgb.max(-1); mn = rgb.min(-1)
d = np.maximum(mx - mn, 1e-6)
h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
v = mx
skin = (h > 0.0) & (h < 0.1) & (s > 0.28) & (s < 0.75) & (v > 0.42) & (r - b > 0.16) & (a[..., 3] > 0.5)
vis = np.zeros_like(a)
vis[..., :3] = rgb * 0.35
vis[..., 3] = a[..., 3]
vis[skin] = [1, 0.2, 0.6, 1]
Image.fromarray((vis * 255).astype(np.uint8)).save(out)
print(src, "skin px", int(skin.sum()))
