# 몸 원화 + 무기 스프라이트(grip · 각도 · 뒤집기)를 게임과 같은 방식으로 합성한 미리보기 — 사용: python3 preview.py ART_DIR TIER OUT.png [frames...]
import sys, os, json, math
from PIL import Image
art, tier, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
names = sys.argv[4:]
rig = json.load(open(os.path.join(art, 'svg', 'rig.json'), encoding='utf-8'))
W = rig['weapons'][str(tier)]
wimg = Image.open(os.path.join(art, 'png', f'weapon_t{tier}.png')).convert('RGBA')
def comp(name):
    body = Image.open(os.path.join(art, 'png', name + '.png')).convert('RGBA')
    fr = rig['frames'][name]
    canvas = Image.new('RGBA', (body.width + 400, body.height + 200), (0, 0, 0, 0))
    ox, oy = 200, 100
    canvas.alpha_composite(body, (ox, oy))
    w = wimg.transpose(Image.FLIP_TOP_BOTTOM) if fr.get('flip') else wimg
    gx, gy = W['gx'], (W['h'] - W['gy']) if fr.get('flip') else W['gy']
    # 손잡이 중심이 회전 중심이 되도록 큰 캔버스에 놓고 회전
    big = Image.new('RGBA', (w.width * 2 + 40, w.width * 2 + 40), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - gx, cy - gy))
    big = big.rotate(-fr['ang'], resample=Image.BICUBIC, center=(cx, cy))
    canvas.alpha_composite(big, (int(ox + fr['grip'][0] - cx), int(oy + fr['grip'][1] - cy)))
    return canvas.crop((100, 40, 100 + body.width + 200, 40 + body.height + 80))
tiles = [comp(n) for n in names]
T = 300
sheet = Image.new('RGBA', (T * len(tiles), int(T * tiles[0].height / tiles[0].width)), (52, 58, 70, 255))
for i, t in enumerate(tiles):
    t2 = t.resize((T, int(T * t.height / t.width)), Image.LANCZOS)
    sheet.alpha_composite(t2, (i * T, 0))
sheet.convert('RGB').save(out)
print('preview', out)
