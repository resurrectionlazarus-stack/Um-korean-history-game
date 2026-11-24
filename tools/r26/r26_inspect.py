import sys, os, json
from PIL import Image
import numpy as np
root, r25 = sys.argv[1], sys.argv[2]
rows = []
for pack in ("p1", "p2"):
    base = os.path.join(root, pack)
    for dp, _, fs in os.walk(base):
        for f in sorted(fs):
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, base)
            if rel.endswith(".json"):
                continue
            im = Image.open(p)
            old = os.path.join(r25, rel)
            oim = Image.open(old) if os.path.exists(old) else None
            a = np.asarray(im.convert("RGBA"))[..., 3]
            ys, xs = np.nonzero(a > 20)
            bb = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None
            corner = int(a[:6, :6].max())
            rows.append((pack, rel, im.format, im.mode, im.size, oim.size if oim else None, bb, corner))
bad = [r for r in rows if r[5] is None or r[4] != r[5] or r[7] > 20 or r[3] not in ("RGBA", "LA", "P")]
for r in rows:
    print(*r, sep=" | ")
print("TOTAL", len(rows), "MISMATCH/BAD", len(bad))
for r in bad:
    print("BAD", r)
