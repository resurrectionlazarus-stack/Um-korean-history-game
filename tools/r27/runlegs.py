#!/usr/bin/env python3
"""[R27 핫픽스] 1시대 대사냥꾼 질주 임시 원화: R27 새 몸(run~run8 · 윗몸 · 손 · 무기 쥔 자리 그대로) +
   같은 캐릭터 옛 원화(R23 미술팀 run~run8)의 질주 다리를 허리천 아래에 이식.
   R27 1차 질주 8장은 다리가 거의 움직이지 않아(프레임 간 다리 변화 6.7% · 두 발 위치 고정) 제자리 자세로 미끄러져 보였다."""
import sys, json
import numpy as np
from PIL import Image

NEW, OLD, OUT = sys.argv[1:4]
YH = 312          # 이음매 가운데(허리천 아랫단)
B = 20            # 섞는 폭
CAPE_X = 125      # 망토 꼬리(왼쪽) 구역: 이 x보다 왼쪽은 y 345까지 새 몸 그대로
CAPE_Y = 345
DX = -10          # 옛 다리 가로 맞춤(가랑이 위치)
POSES = ["run", "run2", "run3", "run4", "run5", "run6", "run7", "run8"]


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).astype(float) / 255.0


def pm(a):
    return np.concatenate([a[..., :3] * a[..., 3:4], a[..., 3:4]], -1)


# 색 맞춤: 다리(정강이 · 발) 불투명 픽셀 평균색을 새 원화에 맞춘다(채널별 이득)
def leg_mean(frames):
    acc = []
    for a in frames:
        m = a[380:468, :, 3] > 0.9
        acc.append(a[380:468][m][:, :3])
    v = np.concatenate(acc)
    return v.mean(0)


news = {p: load(f"{NEW}/era1_hunter_{p}.webp") for p in POSES}
olds = {p: np.roll(load(f"{OLD}/era1_hunter_{p}.png"), DX, axis=1) for p in POSES}
gain = leg_mean(news.values()) / np.maximum(leg_mean(olds.values()), 1e-3)
gain = np.clip(gain, 0.8, 1.25)
H, W = 512, 512
Y, X = np.mgrid[0:H, 0:W].astype(float)
# 새 몸을 자르는 곡선 y_cut(x): 허리천 아랫단 · 망토 꼬리 · 앞 허벅지 윗부분을 따라가는 부드러운 선(원본 512 픽셀, 8장 공통 —
#  R27 질주 8장은 아랫몸이 거의 같다). 곡선 위는 새 몸, 아래는 옛 질주 다리. 옛 다리는 곡선보다 14px 위에서 시작(틈 없음)
CUT = [(0, 332), (125, 332), (142, 310), (185, 318), (215, 345), (250, 352), (285, 340), (300, 302), (316, 286), (512, 286)]
cx_, cy_ = zip(*CUT)
y_cut = np.interp(np.arange(W), cx_, cy_)
y_cut = np.convolve(np.pad(y_cut, 6, mode="edge"), np.ones(13) / 13, mode="valid")   # 꺾임 다듬기
YC = y_cut[None, :].repeat(H, 0)
w_new = 1 - smooth((Y - (YC - 4)) / 8)
seam_old = np.where(X < 150, np.maximum(YC - 14, 340), YC - 14)
w_old = smooth((Y - (seam_old - 5)) / 10)
meta = {"gain": [round(float(g), 3) for g in gain], "cut": CUT, "dx": DX}
# 옛 run 한 장은 도끼를 허리 높이로 들고 있어 손 · 자루 · 돌 머리가 다리 위로 비친다 →
#  그 장만 앞쪽(x ≥ 285)은 새 몸 앞 허벅지를 y 326까지 남기고, 옛 그림은 y 322 아래만 쓴다
OLD_FIX = {"run": (285, 326)}
for p in POSES:
    wn = w_new
    wo = w_old
    if p in OLD_FIX:
        fx, fy = OLD_FIX[p]
        yc2 = np.where(X >= fx, np.maximum(YC, fy), YC)
        wn = 1 - smooth((Y - (yc2 - 4)) / 8)
        so = np.where(X >= fx - 15, np.maximum(seam_old, fy - 4), seam_old)
        wo = smooth((Y - (so - 5)) / 10)
    n = pm(news[p]) * wn[..., None]
    o = olds[p].copy()
    o[..., :3] = np.clip(o[..., :3] * gain, 0, 1)
    o = pm(o) * wo[..., None]
    out = n + o * (1 - n[..., 3:4])
    al = out[..., 3:4]
    rgb = np.where(al > 1e-4, out[..., :3] / np.maximum(al, 1e-4), 0)
    img = (np.clip(np.concatenate([rgb, al], -1), 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(img, "RGBA").save(f"{OUT}/era1_hunter_{p}.webp", "WEBP", quality=92, method=6)
    a = img[..., 3] > 20
    ys = np.nonzero(a.any(axis=1))[0]
    xs = np.nonzero(a[440:470].any(axis=0))[0]
    meta[p] = {"bottomOpaqueY": int(ys.max()), "feetX": [int(xs.min()), int(xs.max())] if len(xs) else None}
json.dump(meta, open(f"{OUT}/runlegs.json", "w"), indent=1)
print(json.dumps(meta))
