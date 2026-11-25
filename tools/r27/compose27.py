#!/usr/bin/env python3
"""R27 비교 합성 3장 — ① 1시대 손에 든 무기 교체(주먹도끼 → 흑요석 슴베찌르개 → 간돌도끼) ② 영웅 링 시인성 ③ 수묵 호흡 피니시."""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1:3]
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
F_T, F_L = ImageFont.truetype(FONT, 40), ImageFont.truetype(FONT, 30)
BG = (14, 16, 24)
OLD, NEW = (248, 113, 113), (253, 224, 71)


def load(n):
    return Image.open(f"{SRC}/{n}.png").convert("RGB"), json.load(open(f"{SRC}/{n}.json"))


def crop_at(n, wx, wz, l, r, u, d):
    im, m = load(n)
    k = m["w"] / 960 * 2
    cx = (wx - m["cam"]) * k
    fy = wz * (m["h"] / 540) * 2
    return im.crop((int(cx - l), int(fy - u), int(cx + r), int(fy + d)))


def hero(n, l=260, r=400, u=560, d=80):
    _, m = load(n)
    return crop_at(n, m["p"][0], m["p"][1], l, r, u, d)


def label(img, text, col=NEW):
    dr = ImageDraw.Draw(img)
    w = dr.textlength(text, font=F_L)
    dr.rounded_rectangle((14, 12, 14 + w + 28, 60), 12, fill=(0, 0, 0))
    dr.text((28, 16), text, font=F_L, fill=col)
    return img


def sheet(title, rows, path, gap=10):
    W = max(sum(t.width for t in r) + gap * (len(r) - 1) for r in rows) + 40
    H = 90 + sum(max(t.height for t in r) for r in rows) + gap * (len(rows) - 1) + 30
    S = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(S)
    dr.text((20, 22), title, font=F_T, fill=(255, 255, 255))
    y = 90
    for r in rows:
        x = 20
        for t in r:
            S.paste(t, (x, y))
            x += t.width + gap
        y += max(t.height for t in r) + gap
    S.save(path, optimize=True)
    print(path, S.size)


# ① 1시대 손에 든 무기 교체
bim, _ = load("r27_e1swap_b_reveal")
ban = bim.crop((bim.width // 2 - 430, 196, bim.width // 2 + 430, 440))
sheet("1시대 대사냥꾼 — 퀴즈 정답 때 손에 든 무기가 부서지고 바뀐다 (R26: 무기를 그린 몸이라 그대로)",
      [[label(hero("r26_e1_idle"), "R26 · 처음", OLD), label(hero("r26_e1_t2idle"), "R26 · 정답 뒤에도 같은 도끼", OLD)],
       [label(hero("r27_e1_idle"), "① T1 석장리 타제 주먹도끼"), label(hero("r27_e1swap_a_flash"), "② 정답! 옛 무기 흰빛"), label(hero("r27_e1swap_b_reveal"), "③ 흑요석 슴베찌르개 등장")],
       [label(hero("r27_e1_t2idle"), "④ T2 슴베찌르개를 쥔 대기"), label(hero("r27_e1_t2swing"), "⑤ T2 슴베찌르개 베기"), label(hero("r27_e1_t3idle"), "⑥ T3 신석기 간돌도끼")],
       [ban]],
      f"{OUT}/R27-compare-1-era1-weapon-swap.png")

# ② 영웅 링 시인성 — 같은 자리 · 같은 병사 6명
def crowd(n, tag, col):
    return label(hero(n, 560, 760, 640, 150), tag, col)


ring1 = label(hero("r27_e1_idle", 300, 420, 560, 110), "1시대 주황 링")
e3 = Image.open(f"{SRC}/r27_e3_nofg.png").convert("RGB")
e3c = e3.crop((210, 300, 570, 600)).resize((720, 600), Image.LANCZOS)
sheet("주인공 시인성 — 발밑 영웅 링(시대색) + 일반 몹 원화 12% 톤다운 (R26 → R27, 같은 장면)",
      [[crowd("r26_e2_crowd", "R26 · 병사 6명 사이 해모수", OLD), crowd("r27_e2_crowd", "R27 · 노란 영웅 링 + 몹 톤다운", NEW)],
       [ring1, label(e3c, "3시대 진홍 링 · 하단 도트 전경 제거")]],
      f"{OUT}/R27-compare-2-hero-ring.png")

# ③ 수묵 호흡 피니시 — 4번째 타격 판정 70ms 뒤(두 빌드 같은 순간)
def fin(n, tag, col):
    return label(hero(n, 380, 760, 640, 140), tag, col)


sheet("4타 피니시 '호흡' — 먹 붓질 초승달 + 먹물 비산 + 시대 속성 (판정 70ms 뒤 정지 화면)",
      [[fin("r26_e2_fin", "R26 · 2시대 피니시", OLD), fin("r27_e2_fin", "R27 · 먹 붓질 + 태양 번개", NEW)],
       [fin("r27_e1_fin", "R27 · 1시대 먹 붓질 + 화염 · 흑요석 파편", NEW)]],
      f"{OUT}/R27-compare-3-ink-breath.png")
