#!/usr/bin/env python3
"""R30 비교 이미지 — 김유신 새 질주 · 연/한 정식 원화 · Lv 콤보 필름 · 조건부 일섬 · 오라 단계/시대색."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SCR, OUT, ROOT = sys.argv[1], sys.argv[2], sys.argv[3]
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
font = lambda sz: ImageFont.truetype(FONT, sz)


def label(im, text, xy=(10, 6), sz=20):
    d = ImageDraw.Draw(im)
    x, y = xy
    d.rectangle([x - 5, y - 3, x + d.textlength(text, font=font(sz)) + 5, y + sz + 7], fill=(8, 10, 16))
    d.text((x, y), text, font=font(sz), fill=(250, 236, 200))


def row(ims, gap=6, bg=(12, 12, 16)):
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    H = max(i.height for i in ims)
    R = Image.new("RGB", (W, H), bg)
    x = 0
    for i in ims:
        R.paste(i, (x, 0))
        x += i.width + gap
    return R


def stack(rows, title, gap=10, bg=(12, 12, 16)):
    W = max(r.width for r in rows) + 2 * gap
    H = sum(r.height for r in rows) + gap * (len(rows) + 1) + 44
    S = Image.new("RGB", (W, H), bg)
    ImageDraw.Draw(S).text((gap + 4, 8), title, font=font(26), fill=(253, 224, 140))
    y = 44 + gap
    for r in rows:
        S.paste(r, (gap, y))
        y += r.height + gap
    return S


def cap(text, w):
    im = Image.new("RGB", (w, 32), (12, 12, 16))
    ImageDraw.Draw(im).text((4, 4), text, font=font(19), fill=(220, 226, 236))
    return im


def frames(tag, idx, box, size):
    D = f"{SCR}/r30/cap/{tag}"
    fs = sorted(os.listdir(D))
    return [Image.open(f"{D}/{fs[i]}").convert("RGB").crop(box).resize(size, Image.LANCZOS) for i in idx if i < len(fs)]


# 1) 김유신 새 질주 8장 + 게임 화면
T = 200
sheet = []
for i in range(1, 9):
    nm = "era3_hero_run" + ("" if i == 1 else str(i)) + ".png"
    im = Image.open(f"{ROOT}/shinsi-R30/assets/hero/{nm}").convert("RGBA").resize((T, T), Image.LANCZOS)
    t = Image.new("RGBA", (T, T), (64, 70, 82, 255))
    t.alpha_composite(im)
    t = t.convert("RGB")
    label(t, nm.replace("era3_hero_", "").replace(".png", ""), sz=16)
    sheet.append(t)
film = frames("kimrun", [0, 4, 8, 12, 16, 20], (260, 330, 700, 650), (266, 194))
stack([cap("미술팀 정식 원화 8장(512×512 · groundY 470 · topY 34~35 · 머리 x 361~369 정렬) — R28 poseDX 보정 제거", 1650), row(sheet), cap("게임 화면 — 8장 차례 재생(프레임당 약 3.6틱)", 1650), row(film)], "R30 3시대 김유신 질주 8프레임(정식 원화)").save(f"{OUT}/R30-kim-run.png")

# 2) 연 · 한 정식 원화 + 게임 화면
M = f"{ROOT}/shinsi-R30/assets/mob"
T = 190
tiles = []
for k, nm in [("yan_pike", "연나라 창병"), ("yan_archer", "연나라 궁수"), ("han_pike", "한나라 극병"), ("han_archer", "한나라 궁수"), ("han_elite", "한나라 철갑 극병")]:
    for p in ["idle", "atk"]:
        im = Image.open(f"{M}/era2_{k}_{p}.webp").convert("RGBA").resize((T, T), Image.LANCZOS)
        t = Image.new("RGBA", (T, T), (64, 70, 82, 255))
        t.alpha_composite(im)
        t = t.convert("RGB")
        label(t, f"{nm} {p}", sz=14)
        tiles.append(t)
lineup = Image.open(f"{SCR}/r30/cap/era2_lineup.png").convert("RGB").crop((300, 250, 1280, 650))
stack([row(tiles[:5]), row(tiles[5:]), cap("게임 화면 — 정식 원화 5종(원본이 저채도 · 어두운 톤이라 굽기 톤다운 생략)", 980), lineup], "R30 2시대 연나라 · 한나라 병사 정식 원화 15장").save(f"{OUT}/R30-era2-official.png")

# 3) 레벨 콤보 필름
B = (200, 150, 1100, 650)
S0 = (300, 167)
spin = frames("spin", [36, 42, 48, 54, 60, 66], B, S0)
rush = frames("rush5", [36, 48, 66, 84, 90, 108], B, S0)
stack([cap("Lv.3 360° 원월 회전참 — 4타 피니시: 몸이 한 바퀴(가로 배율) · 앞뒤를 감싸는 두 겹 입체 원월(뒤쪽 반은 몸 뒤로) · 둘레 베기", 1830), row(spin),
       cap("Lv.4~5 — 4타 → J 질풍연참(원근 검기 · 잔상) → RUSH FINISH 일섬 → 도약 급강하 WAVE STRIKE(충격파 고리 + 양쪽 X자 검기)", 1830), row(rush)],
      "R30 레벨 연동 입체 콤보(Lv.1 가로 · 역 · 내려찍기 → Lv.2 비연 + X자 십자검기 → Lv.3 원월 → Lv.4 질풍연참 → Lv.5 파동격)").save(f"{OUT}/R30-combos.png")

# 4) 조건부 일섬
ink = Image.open(f"{SCR}/r30/func/r30_special_ink.png").convert("RGB").crop((200, 120, 1100, 620)).resize(S0, Image.LANCZOS)
drag = frames("dragon", [35, 45, 50, 60, 65], B, S0)
stack([cap("① 저스트 패링 뒤 1초 안 J(2시대 SOLAR FLASH · 수묵 암전) · ② 15콤보(S랭크) 이상 4타 적중(3시대 GOLDEN DRAGON — 황금 · 비취 용오름 → Z자 관통 → 착지 일제 양단)", 1830), row([ink] + drag)],
      "R30 조건부 일섬 「시공 일섬」 · 3시대 김유신 황금 용오름 일섬").save(f"{OUT}/R30-special.png")

# 5) 오라
st = [Image.open(f"{SCR}/r30/cap/aura_stage_{t}.png").convert("RGB").crop((296, 250, 596, 590)).resize((300, 340)) for t in ["s1", "s2", "s3", "s4"]]
for im, t in zip(st, ["1단계 Lv.1 · T1", "2단계 Lv.2~3 · T2", "3단계 Lv.4~5 · T3", "4단계 + S랭크 · 유물"]):
    label(im, t, sz=16)
er = [Image.open(f"{SCR}/r30/cap/aura_era{e}.png").convert("RGB").crop((316, 250, 576, 600)).resize((260, 300)) for e in range(1, 7)]
for im, t in zip(er, ["1 황토 · 불꽃", "2 금빛 태양", "3 황금 · 비취", "4 청룡 검기", "5 조선 홍염", "6 백 · 청 태극"]):
    label(im, t, sz=16)
stack([row(st), cap("시대별 고유색(3단계)", 1600), row(er)], "R30 주인공 오라 — 레벨 · 무기 진화 연동 단계 · 시대색(ctx.filter 없음 · 불티 고정 28칸)").save(f"{OUT}/R30-aura.png")
print("ok")
