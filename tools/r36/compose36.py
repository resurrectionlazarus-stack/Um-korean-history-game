#!/usr/bin/env python3
"""R36 납품 이미지 합성
  ① R36-combo-branches.jpg   갈래 기술 4종(올려치기 · 공중 추격 · 내려찍기 · 관통 돌진) × 1 · 2 · 4시대 — capture36.js 촬영본
  ② R36-blunt-sounds.png     둔기 타격음 R35(rock_*) ↔ R36(thud_*): 주파수 대역별 에너지 + 600Hz 위 꼬리 길이
  ③ R36-voices.png           짐승 · 병사 목소리 11종 스펙트로그램(0~5kHz) + 한글 이름
사용: python3 -I tools/r36/compose36.py <촬영 폴더(capture36)> <빌드 폴더> <출력 폴더>"""
import os
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import signal

CAP, BUILD, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
FN = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
F = ImageFont.truetype(FN, 20)
FS = ImageFont.truetype(FN, 15)
FB = ImageFont.truetype(FN, 28)
BG = (16, 18, 24)
CARD = (30, 34, 44)
INK = (232, 230, 223)
DIM = (154, 163, 181)
GOLD = (251, 191, 36)
NEW = (56, 189, 248)
OLD = (107, 115, 133)

# ① 갈래 기술
MOVES = [("launch_a", "올려치기", "연타 중 ▲ + 공격"), ("chase_a", "공중 추격", "띄운 뒤 공격"), ("slam_a", "내려찍기", "연타 중 ▼ + 공격"), ("lunge_a", "관통 돌진", "마무리 돌림(연타만)")]
ERAS = [(1, "1시대 대사냥꾼"), (2, "2시대 해모수"), (4, "4시대 척준경")]
cw, ch = 470, 300
pad = 14
left = 150
top = 118
W = left + (cw + pad) * 4 + 20
H = top + (ch + pad) * len(ERAS) + 16
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((20, 16), "R36 갈래 기술 — 연타의 마무리가 매번 달라집니다", font=FB, fill=GOLD)
for ci, (_, name, key) in enumerate(MOVES):
    x = left + ci * (cw + pad)
    d.text((x + 4, 62), name, font=F, fill=INK)
    d.text((x + 4, 88), key, font=FS, fill=NEW)
for ri, (era, title) in enumerate(ERAS):
    y = top + ri * (ch + pad)
    for i, part in enumerate(title.split(" ")):
        d.text((20, y + 110 + i * 26), part, font=F, fill=INK if i else GOLD)
    for ci, (mv, _, _) in enumerate(MOVES):
        p = f"{CAP}/e{era}_{mv}.png"
        im = Image.open(p).convert("RGB")
        # 1280×640 촬영본에서 싸움이 벌어지는 가운데(버튼 · 점수판 제외)
        c = im.crop((150, 90, 150 + 800, 90 + 510)).resize((cw, ch), Image.LANCZOS)
        img.paste(c, (left + ci * (cw + pad), y))
img.save(f"{OUT}/R36-combo-branches.jpg", quality=88)
print("combo", img.size)


# ② 둔기 타격음 비교
def read(path):
    w = wave.open(path)
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    return x, w.getframerate()


EDGES = [0, 150, 300, 600, 1200, 2400, 4800, 11025]
BL = ["~150", "~300", "~600", "~1.2k", "~2.4k", "~4.8k", "4.8k~"]


def bands(x, sr):
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / sr)
    e = np.array([X[(f >= EDGES[i]) & (f < EDGES[i + 1])].sum() for i in range(7)])
    return e / e.sum() * 100


def tail(x, sr):
    """'울림 꼬리'(ms): 600Hz 위 소리가 가장 클 때부터 20dB 줄어들 때까지 — synth_r36.py의 ring()과 같은 정의."""
    b, a = signal.butter(3, 600 / (sr / 2), "high")
    h = signal.lfilter(b, a, x)
    b2, a2 = signal.butter(2, 60 / (sr / 2), "low")
    e = np.maximum(signal.lfilter(b2, a2, h * h), 1e-12)
    pk = int(np.argmax(e))
    below = np.where(e[pk:] < e[pk] * 0.01)[0]
    return float(below[0] / sr * 1000) if len(below) else float((len(e) - pk) / sr * 1000)


PAIRS = [("가벼운 타격 1", "rock_hit_1", "thud_hit_1"), ("가벼운 타격 2", "rock_hit_2", "thud_hit_2"), ("강타", "rock_heavy", "thud_heavy"), ("내려찍기", "rock_crush", "thud_crush")]
pw, ph = 420, 300
W2 = 30 + (pw + 20) * 4 + 10
H2 = 150 + ph + 110
im2 = Image.new("RGB", (W2, H2), BG)
d2 = ImageDraw.Draw(im2)
d2.text((30, 16), "R36 둔기 타격음 — R35 바위 소리(회색) ↔ 새 '퍽'(파랑)", font=FB, fill=GOLD)
d2.text((30, 58), "막대 = 주파수 대역별 에너지(%). 새 소리는 높은 쪽(1.2kHz 위)을 줄이고, 울리는 음을 모두 뺐습니다.", font=FS, fill=INK)
d2.text((30, 82), "아래 숫자 = 600Hz 위 소리가 가장 클 때부터 20dB 줄어들 때까지 걸리는 시간. 짧을수록 '깡' 하는 꼬리가 없습니다.", font=FS, fill=DIM)
rows = []
for pi, (title, o, n) in enumerate(PAIRS):
    x0 = 30 + pi * (pw + 20)
    y0 = 124
    d2.rounded_rectangle((x0, y0, x0 + pw, y0 + ph + 104), radius=12, fill=CARD)
    d2.text((x0 + 14, y0 + 10), title, font=F, fill=INK)
    xo, so = read(f"{BUILD}/assets/sfx/{o}.wav")
    xn, sn = read(f"{BUILD}/assets/sfx/{n}.wav")
    bo, bn = bands(xo, so), bands(xn, sn)
    to, tn = tail(xo, so), tail(xn, sn)
    rows.append((title, o, n, [round(v) for v in bo], [round(v) for v in bn], round(to), round(tn)))
    base = y0 + ph - 6
    mx = 50.0
    for bi in range(7):
        bx = x0 + 18 + bi * 56
        ho = min(1, bo[bi] / mx) * (ph - 90)
        hn = min(1, bn[bi] / mx) * (ph - 90)
        d2.rectangle((bx, base - ho, bx + 20, base), fill=OLD)
        d2.rectangle((bx + 22, base - hn, bx + 42, base), fill=NEW)
        d2.text((bx - 2, base + 6), BL[bi], font=FS, fill=DIM)
    d2.text((x0 + 14, y0 + ph + 40), f"꼬리 길이  R35 {to:.0f}ms", font=FS, fill=OLD)
    d2.text((x0 + 14, y0 + ph + 64), f"                새 소리 {tn:.0f}ms", font=FS, fill=NEW)
    d2.text((x0 + 230, y0 + ph + 52), f"-{(1 - tn / to) * 100:.0f}%" if tn < to else "", font=F, fill=NEW)
im2.save(f"{OUT}/R36-blunt-sounds.png")
print("blunt", im2.size)
for r in rows:
    print(" ", r)

# ③ 목소리 스펙트로그램
VO = [("wolf_howl", "늑대 하울링"), ("wolf_snarl", "늑대 으르렁"), ("wolf_yelp", "깨갱"), ("hyena_cackle", "하이에나 낄낄"), ("bear_roar", "곰 포효"), ("bear_growl", "곰 으르렁"),
      ("rhino_snort", "코뿔소 콧김"), ("beast_groan", "큰 짐승 신음"), ("tiger_roar", "호랑이 포효"), ("tiger_snarl", "호랑이 으르렁"), ("war_cry", "병사 함성")]
sw, sh = 300, 150
cols = 4
rws = (len(VO) + cols - 1) // cols
W3 = 30 + (sw + 16) * cols + 14
H3 = 110 + rws * (sh + 46)
im3 = Image.new("RGB", (W3, H3), BG)
d3 = ImageDraw.Draw(im3)
d3.text((30, 16), "R36 짐승 · 병사의 목소리 11종 — 스펙트로그램(가로 = 시간 · 세로 = 0~5kHz)", font=FB, fill=GOLD)
d3.text((30, 58), "모두 직접 합성했습니다(성대 펄스 → 입 모양 공명 → 숨소리). 줄무늬 = 울음의 음높이, 뿌연 면 = 으르렁 · 숨소리.", font=FS, fill=INK)
for i, (fn, lab) in enumerate(VO):
    x, sr = read(f"{BUILD}/assets/sfx/{fn}.wav")
    f, t, S = signal.spectrogram(x, sr, nperseg=512, noverlap=384)
    S = 10 * np.log10(S[f <= 5000] + 1e-12)
    S = np.clip((S - S.max() + 70) / 70, 0, 1)[::-1]
    g = (S * 255).astype(np.uint8)
    rgb = np.stack([g, (g.astype(np.float64) ** 1.25 / 255 ** 0.25).astype(np.uint8), (60 + g * 0.45).astype(np.uint8)], -1)
    sp = Image.fromarray(rgb).resize((sw, sh), Image.BILINEAR)
    px = 30 + (i % cols) * (sw + 16)
    py = 96 + (i // cols) * (sh + 46)
    im3.paste(sp, (px, py + 26))
    d3.text((px + 2, py + 2), f"{lab}  {len(x) / sr:.1f}초", font=FS, fill=INK)
im3.save(f"{OUT}/R36-voices.png")
print("voices", im3.size)
