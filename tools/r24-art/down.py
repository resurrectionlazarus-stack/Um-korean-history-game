import sys, os
from PIL import Image
src, dst, size = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 512
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.endswith('@2x.png'): continue
    im = Image.open(os.path.join(src, f)).convert('RGBA')
    im = im.resize((size, size), Image.LANCZOS)
    im.save(os.path.join(dst, f.replace('@2x', '')), optimize=True)
print('down ok')
