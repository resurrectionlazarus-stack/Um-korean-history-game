#!/usr/bin/env python3
"""R25 비교 합성 4장(라벨: 문천역 정흑체 — 한글 포함)."""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1]
OUT = sys.argv[2]
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
F_T = ImageFont.truetype(FONT, 40)
F_L = ImageFont.truetype(FONT, 30)
BG = (14, 16, 24)


def load(n):
    return Image.open(f"{SRC}/{n}.png").convert("RGB"), json.load(open(f"{SRC}/{n}.json"))


def k_of(m):
    return m["w"] / 960 * 2


def crop_at(n, wx, wz, left, right, up, down):
    im, m = load(n)
    k = k_of(m)
    cx = (wx - m["cam"]) * k
    fy = wz * (m["h"] / 540) * 2
    return im.crop((int(cx - left), int(fy - up), int(cx + right), int(fy + down)))


def hero(n, left=300, right=440, up=600, down=90):
    _, m = load(n)
    return crop_at(n, m["p"][0], m["p"][1], left, right, up, down)


def label(img, text, col=(253, 224, 71)):
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=F_L)
    d.rounded_rectangle((14, 12, 14 + w + 28, 12 + 48), 12, fill=(0, 0, 0))
    d.text((28, 16), text, font=F_L, fill=col)
    return img


def sheet(title, rows, path, cell_gap=10):
    W = max(sum(t.width for t in r) + cell_gap * (len(r) - 1) for r in rows) + 40
    H = 90 + sum(max(t.height for t in r) for r in rows) + cell_gap * (len(rows) - 1) + 30
    S = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(S)
    d.text((20, 22), title, font=F_T, fill=(255, 255, 255))
    y = 90
    for r in rows:
        x = 20
        for t in r:
            S.paste(t, (x, y))
            x += t.width + cell_gap
        y += max(t.height for t in r) + cell_gap
    S.save(path, optimize=True)
    print(path, S.size)


# 1) 척준경: 창 · 화통 → 장검
r24 = [label(hero("r24_cjg_idle"), "R24 · 창 + 화통 (대기)", (248, 113, 113)), label(hero("r24_cjg_swing"), "R24 · 창 찌르기", (248, 113, 113))]
r25 = [label(hero("r25_cjg_idle"), "R25 · 결사대 흑철 장검 (대기)"), label(hero("r25_cjg_swing"), "R25 · 내려베기 + 칼끝 궤적")]
sheet("척준경 — R24 창·화통  →  R25 소드 마스터(장검 3등급 · 실제 칼끝 궤적)", [r24, r25], f"{OUT}/R25-compare-1-cheok-sword.png")

# 2) 2시대: 천군 무사 vs 청동 거신병 → 해모수 vs 한 무제
def boss_view(n, tag, col=(253, 224, 71)):
    im, m = load(n)
    k = k_of(m)
    px = (m["p"][0] - m["cam"]) * k
    bx = (m["b"][0] - m["cam"]) * k if m.get("b") else px + 700
    fy = m["p"][1] * (m["h"] / 540) * 2
    x0 = int(min(px, bx) - 360)
    x1 = int(max(px, bx) + 520)
    c = im.crop((max(0, x0), int(fy - 760), min(im.width, x1), int(min(im.height, fy + 120))))
    c = c.resize((int(c.width * 700 / c.height), 700))
    return label(c, tag, col)


sheet("2시대 — R24 천군 무사 vs 청동 거신병  →  R25 천제의 아들 해모수 vs 한 무제(기원전 108 왕검성)",
      [[boss_view("r24_e2_boss", "R24 · 아사달 천군 무사 / 청동 거신병", (248, 113, 113)), boss_view("r25_e2_boss", "R25 · 해모수(용광검) / 한 무제(면류관 · 장검)")],
       [label(hero("r24_e2_idle"), "R24 · 주인공 대기", (248, 113, 113)), label(hero("r25_e2_idle"), "R25 · 해모수 대기(오우관 · 진홍 망토)"), label(hero("r25_e2_swing"), "R25 · 용광검 내려베기")]],
      f"{OUT}/R25-compare-2-era2-haemosu-hanwu.png")

# 3) 동료: 다물군 전사 → 꼬마 선녀 단비
def comp(n, tag, col=(253, 224, 71)):
    _, m = load(n)
    c = crop_at(n, m["cp"][0], m["cp"][1], 230, 230, 420, 70)
    c = c.resize((c.width * 3 // 2, c.height * 3 // 2), Image.LANCZOS)
    return label(c, tag, col)


sheet("동료 — R24 다물군 전사(코드 픽셀)  →  R25 꼬마 선녀 단비(HD · 날갯짓 · 반짝이 가루)",
      [[comp("r24_e2_idle", "R24 · 다물군 전사", (248, 113, 113)), comp("r25_e2_idle", "R25 · 꼬마 선녀 단비"), comp("r25_cjg_idle", "R25 · 4시대에도 함께")]],
      f"{OUT}/R25-compare-3-fairy-companion.png")

# 4) 무기 변환: T1 → 옛 무기 흰빛 → 새 무기 빛줄기 → T2 참격 → T3
seq = [label(hero("r25_e2_swing", 260, 400, 560, 80), "① T1 해모수의 용광검"),
       label(hero("r25_swap_a_flash", 260, 400, 560, 80), "② 정답! 옛 무기가 흰빛으로"),
       label(hero("r25_swap_b_reveal", 260, 400, 560, 80), "③ 부서지고 새 무기 + 빛줄기"),
       label(hero("r25_swap_c_t2swing", 260, 400, 560, 80), "④ T2 세형 동검의 용광검"),
       label(hero("r25_swap_d_t3", 260, 400, 560, 80), "⑤ T3 고조선 철제 용광검")]
bim, _ = load("r25_swap_b_reveal")
ban = bim.crop((bim.width // 2 - 430, 196, bim.width // 2 + 430, 440))
sheet("무기 변환 — 퀴즈 정답 순간 손에 든 무기가 실제로 바뀐다(배너: 이전 무기 → 새 무기)", [seq[:3], seq[3:] + [ban]], f"{OUT}/R25-compare-4-weapon-swap.png")
