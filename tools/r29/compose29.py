#!/usr/bin/env python3
"""R29 비교 이미지 — 시작 화면 전후 · 2시대 연/한 원화 · 두 동강 필름 · 콤보 필름."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SCR, OUT, MOB = sys.argv[1], sys.argv[2], sys.argv[3]
FONT = None
for f in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]:
    if os.path.exists(f):
        FONT = f
        break


def font(sz):
    return ImageFont.truetype(FONT, sz) if FONT else ImageFont.load_default()


def label(im, text, xy=(12, 8), sz=22):
    d = ImageDraw.Draw(im)
    x, y = xy
    d.rectangle([x - 6, y - 4, x + d.textlength(text, font=font(sz)) + 6, y + sz + 8], fill=(8, 10, 16))
    d.text((x, y), text, font=font(sz), fill=(250, 236, 200))


def strip(frames, crop, size, gap=6, bg=(12, 12, 16)):
    W = len(frames) * (size[0] + gap) - gap
    S = Image.new("RGB", (W, size[1]), bg)
    for i, f in enumerate(frames):
        S.paste(Image.open(f).convert("RGB").crop(crop).resize(size, Image.LANCZOS), (i * (size[0] + gap), 0))
    return S


def stack(rows, title, gap=10, bg=(12, 12, 16)):
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows) + gap * (len(rows) + 1) + 44
    S = Image.new("RGB", (W + 2 * gap, H), bg)
    d = ImageDraw.Draw(S)
    d.text((gap + 4, 8), title, font=font(26), fill=(253, 224, 140))
    y = 44 + gap
    for r in rows:
        S.paste(r, (gap, y))
        y += r.height + gap
    return S


# 1) 시작 화면: R28(옛 도트) → R29(수묵 가림막 · 예약) → 준비 후 바로 HD 시작
a = Image.open(f"{SCR}/title/t0_load.png").convert("RGB").resize((640, 360), Image.LANCZOS)
b = Image.open(f"{SCR}/r29/shots/r29_t0_curtain.png").convert("RGB").resize((640, 360), Image.LANCZOS)
c = Image.open(f"{SCR}/r29/shots/r29_t1_pending.png").convert("RGB").resize((640, 360), Image.LANCZOS)
d = Image.open(f"{SCR}/r29/shots/r29_t2_started.png").convert("RGB").resize((640, 360), Image.LANCZOS)
label(a, "R28 · 켠 직후 = 옛 도트 장면")
label(b, "R29 · 켠 직후 = 수묵 가림막 + 진행 붓질")
label(c, "R29 · 일찍 누른 START = '곧 시작' 예약")
label(d, "R29 · 원화 준비 즉시 HD 장면으로 시작")
row1 = Image.new("RGB", (1290, 360), (12, 12, 16)); row1.paste(a, (0, 0)); row1.paste(b, (650, 0))
row2 = Image.new("RGB", (1290, 360), (12, 12, 16)); row2.paste(c, (0, 0)); row2.paste(d, (650, 0))
stack([row1, row2], "R29 시작 화면 — 옛 도트 장면 없이 수묵 가림막 → 원화 준비 즉시 시작").save(f"{OUT}/R29-title-before-after.png")

# 2) 2시대 연 · 한 군대 임시 원화(원본 → 연 → 한 → 철갑 극병) + 게임 화면
T = 210
names = [("원본 고조선 창병", f"{MOB}/era2_pike_idle.png"), ("원본 고조선 궁수", f"{MOB}/era2_archer_idle.png"),
         ("연나라 창병", f"{MOB}/era2_yan_pike_idle.webp"), ("연나라 궁수", f"{MOB}/era2_yan_archer_atk.webp"),
         ("한나라 극병", f"{MOB}/era2_han_pike_idle.webp"), ("한나라 궁수(2발)", f"{MOB}/era2_han_archer_atk.webp"),
         ("한나라 철갑 극병", f"{MOB}/era2_han_elite_walk.webp")]
sheet = Image.new("RGB", (len(names) * (T + 6), T + 34), (70, 76, 88))
for i, (nm, p) in enumerate(names):
    im = Image.open(p).convert("RGBA").resize((T, T), Image.LANCZOS)
    tile = Image.new("RGBA", (T, T), (70, 76, 88, 255)); tile.alpha_composite(im)
    sheet.paste(tile.convert("RGB"), (i * (T + 6), 30))
    ImageDraw.Draw(sheet).text((i * (T + 6) + 8, 4), nm, font=font(18), fill=(250, 240, 220))
lineup = Image.open(f"{SCR}/r29/func/r29_era2_lineup.png").convert("RGB").crop((300, 200, 1280, 640)).resize((980, 440), Image.LANCZOS)
label(lineup, "게임 화면 — 연나라 창병 · 연나라 궁수 · 한나라 극병 · 한나라 궁수 · 철갑 극병")
stack([sheet, lineup], "R29 2시대 적 = 연나라 → 한나라 군대(디자인팀 부재 임시 원화)").save(f"{OUT}/R29-era2-yanhan.png")

# 3) 두 동강 필름(칼 막타 → 베기 선 · 섬광 → 윗몸이 베인 선 따라 미끄러짐 → 스러짐)
cut = sorted(os.listdir(f"{SCR}/r29/cap/cut"))
pick = [cut[i] for i in (8, 10, 12, 14, 16, 18) if i < len(cut)]
st = strip([f"{SCR}/r29/cap/cut/{f}" for f in pick], (540, 360, 820, 610), (336, 300))
stack([st], "R29 두 동강 — 칼 막타: 베기 선 + 막타 히트스톱 5f → 베인 선 위 · 아래로 갈라져 미끄러짐(프레임 순서 →)").save(f"{OUT}/R29-cut-film.png")

# 4) 콤보 필름: 질풍연참 + AIR RAID
rush = sorted(os.listdir(f"{SCR}/r29/cap/rush"))
air = sorted(os.listdir(f"{SCR}/r29/cap/air"))
print("rush", len(rush), "air", len(air))
r_pick = [rush[i] for i in (38, 46, 56, 66, 76, 82) if i < len(rush)]
a_pick = [air[i] for i in (8, 16, 28, 36, 40, 44) if i < len(air)]
r1 = strip([f"{SCR}/r29/cap/rush/{f}" for f in r_pick], (200, 140, 1100, 640), (360, 200))
r2 = strip([f"{SCR}/r29/cap/air/{f}" for f in a_pick], (200, 140, 1100, 640), (360, 200))
lab1 = Image.new("RGB", (r1.width, 34), (12, 12, 16)); ImageDraw.Draw(lab1).text((6, 4), "질풍연참(Lv.4): 4타 피니시(X자 베기) → J → 5-HIT RUSH(앞쪽 적 끌어당김 · 5연참) → RUSH FINISH(화면을 가르는 일섬 · 슬로우)", font=font(20), fill=(244, 194, 230))
lab2 = Image.new("RGB", (r2.width, 34), (12, 12, 16)); ImageDraw.Draw(lab2).text((6, 4), "AIR RAID: 점프 → 공중 J 3번(체공 연참) → 한 번 더 J = 내리꽂기 → 착지 충격파 · 2연 강타 · 띄우기", font=font(20), fill=(253, 230, 138))
stack([lab1, r1, lab2, r2], "R29 콤보 — 질풍연참 · AIR RAID (DASH LINK: 돌진 뒤 J = 곧바로 3타)").save(f"{OUT}/R29-combo-film.png")
print("combo ok", r_pick[0], a_pick[-1])
