#!/usr/bin/env python3
"""R36.5-2 — 무기를 쥔 손을 '몸 원화와 같은 크기 · 같은 붓 그림'으로.

왜: 무기 그림에 그려져 있던 손은 몸 원화에 그려진 그 주인공의 주먹보다 컸다(1시대는 넓이로 1.7배).
    팔뚝 끝에서 손이 갑자기 커져 '주먹왕 랄프'처럼 보였다(오너 지적).
방법: 손을 새로 그리지 않는다. 미술팀이 달리기 원화에 그려 둔 그 주인공의 주먹(왼손 · 손바닥 쪽 —
    엄지가 위를 가로지르고 네 손가락이 나란히 감긴 모습)을 그대로 떼어, 손잡이를 감싸는 방향으로
    90° 돌려(무손실) 무기 그림의 쥔 자리에 얹는다. 크기를 바꾸지 않으므로 몸의 다른 손과 비율이 같다.
    ① 옛 손을 걷어 내고 그 밑의 손잡이를 양옆 무늬로 다시 잇는다
    ② 1시대는 손에 맞춰 굵게 그려져 있던 자루를 손 크기에 맞게 가늘게 한다(머리 쪽은 그대로)
    ③ 몸 원화의 주먹을 손목에서 둥글게 끊어(끊은 자리는 원화와 같은 먹선으로 닫음) 얹는다
그림 크기 · 쥔 자리 (70,60) · 날은 그대로 → 코드와 쥔 자리 표는 손대지 않는다.

사용: python3 -I tools/r36.5-2/natural_hand.py <옛 무기 폴더(R36 원본)> <몸 원화 폴더> <출력 폴더> [확대 비교.png]
      원본은 shinsi-R36/assets/weapon 에 그대로 있다(R36.5는 그 위에 엄지를 덧그린 판).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SRC_W, HERO, OUT = sys.argv[1:4]
SHEET = sys.argv[4] if len(sys.argv) > 4 else None
GX, GY = 70, 60   # 무기 그림의 쥔 자리(코드의 gx, gy)

# 몸 원화(달리기 1번 프레임)의 주먹
#   box  : 떼어 낼 네모(원화 좌표)
#   wrist: 손목 쪽(팔 보호대)을 잘라 낼 다각형 — 이 안은 버린다
#   pt   : 네 손가락 묶음의 가운데(손잡이가 지나가는 자리) → 무기 그림의 쥔 자리에 놓인다
FIST = {
    "era1": dict(frame="era1_hunter_run", box=(424, 158, 488, 220), pt=(466.0, 183.5),
                 wrist=[(420, 186), (432, 188.5), (437.5, 193.5), (441, 198.5), (447, 204.5), (454, 209.5), (460, 211.8), (466, 212.6), (472, 222), (420, 222)]),
    "era2": dict(frame="era2_hero_run", box=(424, 150, 488, 214), pt=(465.0, 175.0),
                 wrist=[(420, 180), (434, 182.5), (438.5, 187.5), (443, 191.5), (450, 196.5), (458, 199.8), (465, 201.6), (472, 202.2), (478, 216), (420, 216)]),
    "era4": dict(frame="era4_hero_run", box=(418, 138, 482, 202), pt=(459.0, 166.5),
                 wrist=[(414, 170), (428, 172.5), (432.5, 177.5), (437, 181.5), (444, 186.5), (451, 190.2), (457, 191.8), (464, 192.4), (470, 204), (414, 204)]),
}
# 무기 그림마다: hand = 옛 손이 차지한 열(x0..x1) · refL/refR = 손잡이 무늬를 따올 깨끗한 열 · thin = (가늘게 할 끝, 원래 굵기로 돌아오는 곳)
#   dx, dy = 주먹을 쥔 자리에서 옮길 양(코등이에 닿지 않게 · 소매 구멍을 덮게)
WEAPON = {
    "era1_t1": dict(hand=(44, 106), refL=(38, 43), refR=(107, 112), thin=(140, 178)),
    "era1_t2": dict(hand=(44, 106), refL=(38, 43), refR=(107, 112), thin=(118, 152)),
    "era1_t3": dict(hand=(44, 106), refL=(38, 43), refR=(107, 112), thin=(175, 222)),
    "era2_t1": dict(hand=(43, 85), refL=(37, 41), refR=(87, 91), band=(53, 67)),
    "era2_t2": dict(hand=(44, 87), refL=(38, 42), refR=(88, 89), band=(53, 67)),
    "era2_t3": dict(hand=(44, 87), refL=(37, 42), refR=(88, 90), band=(52, 66), clear=[(36, 43)]),
    "era4_t1": dict(hand=(45, 82), refL=(34, 43), refR=(84, 88), band=(53, 68)),
    "era4_t2": dict(hand=(43, 81), refL=(31, 36), refR=(82, 84), band=(54, 67), clear=[(36, 42), (82, 85)]),
    "era4_t3": dict(hand=(33, 74), refL=(19, 21), refR=(75, 76), band=(56, 67), clear=[(20, 32)], dx=-8),
}
SHAFT = 14.0      # 1시대 자루 굵기(px) — 손가락 한 마디의 2배쯤(12.5 · 14 · 15.5를 얹어 비교해 고름: 손에 쥐이면서도 무기가 가벼워 보이지 않는 굵기)
if os.environ.get("NH_SHAFT"):       # 비교 시험용
    SHAFT = float(os.environ["NH_SHAFT"])
# 주먹을 손가락 쪽으로 6px 내린다 → 손잡이가 주먹 한가운데를 지나고, 팔 보호대 끝의 구멍(소매 속)이 주먹에 덮인다
# (0 · 3 · 6 · 9px를 전 프레임에 얹어 비교해 고름: 0~3은 공격 프레임에서 구멍이 보이고, 9는 손잡이가 주먹 위쪽으로 치우친다)
DY = {"era1": 6, "era2": 6, "era4": 6}
if os.environ.get("NH_DY"):          # 비교 시험용
    DY = {k: int(os.environ["NH_DY"]) for k in DY}


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def over(dst, src, ox, oy):
    """src(RGBA float)를 dst 위에 얹는다(곱하지 않은 알파)."""
    h, w = src.shape[:2]
    reg = dst[oy:oy + h, ox:ox + w]
    a = src[..., 3:4] / 255
    ra = reg[..., 3:4] / 255
    oa = a + ra * (1 - a)
    reg[..., :3] = np.where(oa > 1e-4, (src[..., :3] * a + reg[..., :3] * ra * (1 - a)) / np.maximum(oa, 1e-4), 0)
    reg[..., 3:4] = oa * 255


def strip_hand(arr, hand, refL, refR, band=None, clear=None):
    """옛 손이 있던 열을 지우고, 양옆의 손잡이 열을 왔다 갔다 이어 붙여 손잡이를 다시 만든다(가운데에서 섞음).
    band=(ya, yb): 손잡이가 차지하는 행 — 그 밖은 비운다(옛 손의 장식 · 천 자락이 무늬에 섞이지 않게).
    clear=[(xa, xb), ...]: 손 바깥이지만 옛 손의 자락이 남은 열 — band 밖을 비운다."""
    out = arr.copy()
    x0, x1 = hand
    n = x1 - x0 + 1

    def cols(ref):
        a, b = ref
        c = arr[:, a:b + 1].copy()
        if band:
            c[:band[0]] = 0
            c[band[1] + 1:] = 0
        if c.shape[1] <= 3:      # 열이 너무 적으면 평균 한 줄로(왔다 갔다 하면 줄무늬가 생긴다)
            al = c[..., 3:4] / 255
            m = np.zeros((c.shape[0], 1, 4))
            m[:, 0, :3] = (c[..., :3] * al).sum(1) / np.maximum(al.sum(1), 1e-4)
            m[:, 0, 3] = c[..., 3].mean(1)
            c = m
        return c

    CL, CR = cols(refL), cols(refR)

    def tile(c, k, from_right):
        T = c.shape[1]
        j = k % (2 * T) if T > 1 else 0
        j = j if j < T else 2 * T - 1 - j
        return c[:, j if from_right else T - 1 - j]

    for i, x in enumerate(range(x0, x1 + 1)):
        Lc = tile(CL, i, False)
        Rc = tile(CR, n - 1 - i, True)
        t = smooth((i - n * 0.35) / (n * 0.3))
        la, ra = Lc[:, 3:4] / 255, Rc[:, 3:4] / 255
        a = la * (1 - t) + ra * t
        out[:, x, :3] = (Lc[:, :3] * la * (1 - t) + Rc[:, :3] * ra * t) / np.maximum(a, 1e-4)
        out[:, x, 3] = a[:, 0] * 255
    for xa, xb in (clear or []) if band else []:
        out[:band[0], xa:xb + 1] = 0
        out[band[1] + 1:, xa:xb + 1] = 0
    return out


def thin(arr, x_full, x_end, target):
    """자루를 가운뎃줄 쪽으로 눌러 가늘게: x <= x_full 은 target 굵기, x_end 에서 원래 굵기로 돌아온다."""
    H = arr.shape[0]
    out = arr.copy()
    al = arr[..., 3] > 128
    thick = float(np.median([al[:, x].sum() for x in range(8, x_full) if al[:, x].sum() > 4]))
    s0 = target / thick
    yy = np.arange(H)
    for x in range(0, x_end):
        col = al[:, x]
        if col.sum() < 3:
            continue
        ys = np.where(col)[0]
        yc = (ys.min() + ys.max()) / 2
        s = s0 + (1 - s0) * smooth((x - x_full) / max(1, x_end - x_full))
        src_y = yc + (yy - yc) / s
        pm = arr[:, x, :3] * (arr[:, x, 3:4] / 255)
        a_new = np.interp(src_y, yy, arr[:, x, 3], left=0, right=0)
        for ch in range(3):
            c = np.interp(src_y, yy, pm[:, ch], left=0, right=0)
            out[:, x, ch] = np.where(a_new > 1, c / np.maximum(a_new / 255, 1e-4), 0)
        out[:, x, 3] = a_new
    return out, thick


def body_fist(era):
    """몸 원화의 주먹을 떼어 손목에서 끊고(모서리를 둥글리고 먹선으로 닫음) 시계 방향으로 90° 돌린다 → (그림, 쥔 자리에 놓일 점)."""
    F = FIST[era]
    im = np.asarray(Image.open(os.path.join(HERO, F["frame"] + ".webp")).convert("RGBA")).astype(np.float64)
    x0, y0, x1, y1 = F["box"]
    p = im[y0:y1, x0:x1].copy()
    h, w = p.shape[:2]
    S = 4   # 자르는 선 · 둥글리기는 4배 크기에서 해 가장자리가 계단지지 않게 한다
    m = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(m).polygon([((x - x0) * S, (y - y0) * S) for x, y in F["wrist"]], fill=255)
    drop4 = np.asarray(m) > 127
    a4 = np.kron(p[..., 3], np.ones((S, S))) > 127
    mask4 = a4 & ~drop4
    # 주먹과 떨어진 부스러기는 버리고, 끊으면서 생긴 뾰족한 모서리는 둥글린다(반지름 3px 열림)
    lab, n = ndimage.label(mask4)
    if n > 1:
        mask4 = lab == (1 + int(np.argmax(ndimage.sum(mask4, lab, range(1, n + 1)))))
    r = 3 * S
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (xx * xx + yy * yy) <= r * r
    open4 = ndimage.binary_opening(mask4, structure=disk)
    grow4 = open4 | (ndimage.binary_dilation(open4, iterations=S) & ~mask4 & ~drop4)   # 원화의 반투명 가장자리 1px만 살린다
    wgt = grow4.reshape(h, S, w, S).mean(axis=(1, 3))
    cut = (drop4 & a4).reshape(h, S, w, S).mean(axis=(1, 3))      # 손목에서 잘려 나간 정도(0~1)
    alpha = p[..., 3] / 255 * wgt * (1 - cut)
    # 새로 드러난 가장자리(끊은 자리 · 둥글린 모서리)를 원화의 먹선 색으로 닫는다: 바깥에서 2px 띠
    a0 = p[..., 3] / 255
    dark = p[..., :3][(a0 > 0.9) & (p[..., :3].sum(-1) < 90)]
    ink = np.median(dark, axis=0) if len(dark) else np.array([12.0, 8.0, 6.0])
    removed = a0 * (1 - wgt * (1 - cut))                            # 원래 있었는데 없앤 곳
    near = ndimage.gaussian_filter(removed, 1.0)
    wline = np.clip(near * 3.0, 0, 1) * (alpha > 0.02)
    p[..., :3] = p[..., :3] * (1 - wline[..., None]) + ink * wline[..., None]
    p[..., 3] = alpha * 255
    fist = np.rot90(p, k=-1).copy()          # 시계 방향 90°: 원화의 위 → 무기 그림의 오른쪽(날 쪽)
    px, py = F["pt"]
    return fist, ((y1 - y0) - (py - y0), (px - x0))   # 돌린 뒤 (x, y)


def build(name):
    era = name.split("_")[0]
    W = WEAPON[name]
    arr = np.asarray(Image.open(os.path.join(SRC_W, name + ".png")).convert("RGBA")).astype(np.float64)
    arr = strip_hand(arr, W["hand"], W["refL"], W["refR"], W.get("band"), W.get("clear"))
    note = ""
    if "thin" in W:
        arr, thick = thin(arr, W["thin"][0], W["thin"][1], SHAFT)
        note = f"자루 {thick:.0f}px → {SHAFT}px"
    bare = arr.copy()
    fist, (fx, fy) = body_fist(era)
    ox = int(round(GX + W.get("dx", 0) - fx))
    oy = int(round(GY + DY[era] + W.get("dy", 0) - fy))
    over(arr, fist, ox, oy)
    al = fist[..., 3] > 128
    ys, xs = np.where(al)
    box = (ox + xs.min(), oy + ys.min(), ox + xs.max(), oy + ys.max())
    return arr, bare, box, note


def to_img(a):
    return Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), "RGBA")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cells = []
    for name in WEAPON:
        new, bare, box, note = build(name)
        to_img(new).save(os.path.join(OUT, name + ".png"), optimize=True)
        old = Image.open(os.path.join(SRC_W, name + ".png")).convert("RGBA")
        oa = np.asarray(old)[..., 3] > 128
        print(f"{name}: 새 손 {box[2] - box[0] + 1}x{box[3] - box[1] + 1}px (x {box[0]}~{box[2]}, y {box[1]}~{box[3]}) {note}")
        cells.append((name, old, to_img(new)))
    if SHEET:
        Z = 5
        cw, ch = 130 * Z, 90 * Z
        sh = Image.new("RGB", (3 * (cw * 2 + 14), 3 * (ch + 26)), (22, 24, 30))
        d = ImageDraw.Draw(sh)
        for i, (name, old, new) in enumerate(cells):
            px, py = (i % 3) * (cw * 2 + 14), (i // 3) * (ch + 26)
            for j, im in enumerate((old, new)):
                c = im.crop((0, 15, 130, 105)).resize((cw, ch), Image.LANCZOS)
                bg = Image.new("RGBA", c.size, (58, 66, 84, 255))
                bg.alpha_composite(c)
                sh.paste(bg.convert("RGB"), (px + j * (cw + 4), py + 22))
            d.text((px + 4, py + 4), name, fill=(255, 230, 120))
        sh.save(SHEET)
        print(SHEET, sh.size)
