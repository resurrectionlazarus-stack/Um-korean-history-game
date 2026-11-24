#!/usr/bin/env python3
"""R26 비교 합성 4장 — R25 코드 원화 → R26 미술팀 리페인트."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
SRC, OUT, R25, R26 = sys.argv[1:5]
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
F_T, F_L, F_S = ImageFont.truetype(FONT, 40), ImageFont.truetype(FONT, 30), ImageFont.truetype(FONT, 20)
BG = (14, 16, 24)
def load(n):
    return Image.open(f"{SRC}/{n}.png").convert("RGB"), json.load(open(f"{SRC}/{n}.json"))
def crop_at(n, wx, wz, l, r, u, d):
    im, m = load(n); k = m["w"] / 960 * 2
    cx = (wx - m["cam"]) * k; fy = wz * (m["h"] / 540) * 2
    return im.crop((int(cx - l), int(fy - u), int(cx + r), int(fy + d)))
def hero(n, l=300, r=440, u=600, d=90):
    _, m = load(n); return crop_at(n, m["p"][0], m["p"][1], l, r, u, d)
def label(img, text, col=(253, 224, 71)):
    dr = ImageDraw.Draw(img); w = dr.textlength(text, font=F_L)
    dr.rounded_rectangle((14, 12, 14 + w + 28, 60), 12, fill=(0, 0, 0)); dr.text((28, 16), text, font=F_L, fill=col); return img
def sheet(title, rows, path, gap=10):
    W = max(sum(t.width for t in r) + gap * (len(r) - 1) for r in rows) + 40
    H = 90 + sum(max(t.height for t in r) for r in rows) + gap * (len(rows) - 1) + 30
    S = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(S); dr.text((20, 22), title, font=F_T, fill=(255, 255, 255))
    y = 90
    for r in rows:
        x = 20
        for t in r:
            S.paste(t, (x, y)); x += t.width + gap
        y += max(t.height for t in r) + gap
    S.save(path, optimize=True); print(path, S.size)
OLD, NEW = (248, 113, 113), (253, 224, 71)
# 1) 주인공
sheet("주인공 리페인트 — R25 코드 원화 → R26 미술팀 회화풍 (칼은 새로 잰 손 위치에 얹음)",
      [[label(hero("r25_e2_idle"), "R25 · 해모수", OLD), label(hero("r25_e2_swing"), "R25 · 내려베기", OLD), label(hero("r26_e2_idle"), "R26 · 해모수", NEW), label(hero("r26_e2_swing"), "R26 · 내려베기", NEW)],
       [label(hero("r25_cjg_idle"), "R25 · 척준경", OLD), label(hero("r25_cjg_swing"), "R25 · 내려베기", OLD), label(hero("r26_cjg_idle"), "R26 · 척준경", NEW), label(hero("r26_cjg_swing"), "R26 · 내려베기", NEW)]],
      f"{OUT}/R26-compare-1-heroes.png")
# 2) 한 무제 + 선녀
def boss_view(n, tag, col):
    im, m = load(n); k = m["w"] / 960 * 2
    px = (m["p"][0] - m["cam"]) * k; bx = (m["b"][0] - m["cam"]) * k; fy = m["p"][1] * (m["h"] / 540) * 2
    c = im.crop((max(0, int(min(px, bx) - 360)), int(fy - 760), min(im.width, int(max(px, bx) + 520)), int(min(im.height, fy + 120))))
    return label(c.resize((int(c.width * 640 / c.height), 640)), tag, col)
def comp(n, tag, col):
    _, m = load(n); c = crop_at(n, m["cp"][0], m["cp"][1], 230, 230, 420, 70)
    return label(c.resize((c.width * 3 // 2, c.height * 3 // 2), Image.LANCZOS), tag, col)
sheet("한 무제 · 꼬마 선녀 단비 리페인트 — R25 → R26",
      [[boss_view("r25_e2_boss", "R25 · 한 무제", OLD), boss_view("r26_e2_boss", "R26 · 한 무제", NEW)],
       [comp("r25_e2_idle", "R25 · 선녀 단비", OLD), comp("r26_e2_idle", "R26 · 선녀 단비", NEW), comp("r26_cjg_idle", "R26 · 4시대에도", NEW)]],
      f"{OUT}/R26-compare-2-hanwu-fairy.png")
# 3) 아이콘 23종
names = [l.split('|')[2].strip().strip('`').replace('.png', '') for l in open(sys.argv[5], encoding='utf-8') if l.startswith('| ') and '.png' in l]
kor = {l.split('|')[2].strip().strip('`').replace('.png', ''): l.split('|')[3].strip() for l in open(sys.argv[5], encoding='utf-8') if l.startswith('| ') and '.png' in l}
cell = 150; tiles = []
for n in names:
    t = Image.new("RGB", (cell * 2 + 8, cell + 40), (28, 32, 44)); dr = ImageDraw.Draw(t)
    for i, base in enumerate((R25, R26)):
        im = Image.open(f"{base}/assets/relic/{n}.png").convert("RGBA").resize((cell, cell), Image.LANCZOS)
        bg = Image.new("RGBA", (cell, cell), (28, 32, 44, 255)); bg.alpha_composite(im); t.paste(bg.convert("RGB"), (i * (cell + 8), 0))
    dr.text((6, cell + 8), kor[n], font=F_S, fill=(230, 230, 230))
    tiles.append(t)
rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
sheet("유물 · 무기 아이콘 23종 — 칸마다 왼쪽 R25(코드) · 오른쪽 R26(리페인트), 파일명 1:1 동일", rows, f"{OUT}/R26-compare-3-icons.png")
# 4) 무기 변환(새 칼)
seq = [label(hero("r26_e2_swing", 260, 400, 560, 80), "① T1 해모수의 용광검"), label(hero("r26_swap_a_flash", 260, 400, 560, 80), "② 정답! 옛 칼 흰빛"),
       label(hero("r26_swap_b_reveal", 260, 400, 560, 80), "③ 새 칼 + 빛줄기"), label(hero("r26_swap_c_t2swing", 260, 400, 560, 80), "④ T2 세형 동검의 용광검"),
       label(hero("r26_swap_d_t3", 260, 400, 560, 80), "⑤ T3 고조선 철제 용광검")]
bim, _ = load("r26_swap_b_reveal"); ban = bim.crop((bim.width // 2 - 430, 196, bim.width // 2 + 430, 440))
sheet("무기 변환 — 리페인트한 칼로도 정답 순간 손에 든 무기가 바뀐다", [seq[:3], seq[3:] + [ban]], f"{OUT}/R26-compare-4-weapon-swap.png")
