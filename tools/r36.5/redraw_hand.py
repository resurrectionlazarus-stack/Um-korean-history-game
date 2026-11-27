#!/usr/bin/env python3
"""R36.5 — 무기를 쥔 손을 '손바닥 쪽에서 본 왼손'으로(오너가 준 사진과 같은 모습)

왜: 오른쪽을 볼 때 무기를 든 팔은 몸 뒤쪽(먼) 팔 = 왼팔이다. 왼손이 쥔 것을 이쪽(주인공의 오른편)에서 보면
    엄지가 앞을 가로지르고, 손가락이 손잡이를 감아 손끝(손톱)이 이쪽으로 돌아 나온다.
    옛 그림은 손등 쪽 주먹(엄지가 아래로 삐져나옴)이라 '왼팔에 오른손이 붙은 것'처럼 보였다.

어떻게: 그려져 있는 손가락은 그대로 살린다(회화풍 유지). 바꾸는 것은 세 가지뿐이다.
    ① 아래로 삐져나온 옛 엄지를 지운다
    ② 엄지를 앞에 얹는다 — 같은 그림의 손가락 한 줄을 떼어 굵기 · 길이를 맞추고 비스듬히 놓는다(위에서 나와 검지 쪽으로 내려옴)
       먹선 · 아래 그림자를 넣고, 손목 끈(1시대)은 엄지 뿌리 위로 다시 덮어 끈 밑에서 나온 것처럼 보이게 한다
    ③ 맨손(1시대)은 손끝에 손톱을 그린다(엄지에 덮이지 않는 손가락 + 엄지)
    그림 크기 · 쥔 자리 (70,60) · 날은 그대로 → 쥔 자리 표는 손대지 않는다.

사용: python3 -I tools/r36.5/redraw_hand.py <원본 무기 폴더(shinsi-R36/assets/weapon)> <출력 폴더> [확대 비교 png]"""
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SS = 8
INK = np.array([26.0, 15.0, 11.0])

# 무기별 설정(무기 그림 좌표)
#  stub  : 지울 옛 엄지(다각형) · cut : 지운 자리 가장자리에 먹선을 넣을지
#  band  : 엄지로 쓸 손가락 한 줄 = 끝이 둥근 막대 [(x0, y0), (x1, y1), r0, r1]
#  thumb : [뿌리 (x, y), 끝 (x, y), 굵기 배율, 길이 배율]
#  nails : 손톱 [가운데 x, 손끝 y, 폭] · tnail : 엄지 손톱 [막대 위 시작 0~1, 끝 0~1, 반폭]
#  strap : 엄지 뿌리 위로 다시 덮을 끈(원본에서 y < strap 인 어두운 픽셀)
E1 = dict(stub=[(85, 79.6), (92, 79.9), (99, 79.2), (104.5, 77.2), (107, 75.5), (108, 92), (84, 92)], band=[(74.3, 46.5), (74.6, 69.0), 5.6, 5.9], thumb=[(79.5, 39.5), (95.5, 63.0), 1.2, 0.88],
          nails=[(62.3, 46.8, 6.4), (73.9, 43.9, 6.8), (98.3, 43.8, 6.8)], tnail=[0.6, 0.86, 2.8], strap=42, kind="skin")
SPEC = {
    "era1_t1": E1, "era1_t2": E1, "era1_t3": E1,
    # 2시대 황금 건틀릿 · 4시대 흑철 건틀릿: 손가락은 갑옷 판 그대로, 엄지만 앞에 얹는다(손톱 없음)
    "era2_t1": dict(stub=[(63, 74.4), (69, 75.5), (76, 75.2), (81, 73.8), (85, 71.5), (86, 82), (62, 82)], band=[(65.5, 46.5), (66.0, 67.5), 4.5, 4.5], thumb=[(60.5, 42.5), (74.5, 62.0), 1.18, 0.85], kind="gold"),
    "era2_t2": dict(stub=[(65, 74.6), (71, 75.7), (78, 75.4), (83, 74.0), (87, 71.8), (88, 82), (64, 82)], band=[(66.5, 46.5), (67.0, 67.5), 4.5, 4.5], thumb=[(61.5, 42.5), (75.5, 62.0), 1.18, 0.85], kind="gold"),
    "era2_t3": dict(stub=[(67, 74.8), (73, 75.8), (80, 75.6), (85, 74.4), (89, 72.6), (90, 82), (66, 82)], band=[(73.0, 46.0), (73.5, 68.0), 4.6, 4.6], thumb=[(63.5, 41.5), (78.0, 61.5), 1.16, 0.84], kind="gold"),
    "era4_t1": dict(stub=None, band=[(66.5, 54.5), (66.5, 70.5), 4.3, 4.3], thumb=[(60.0, 43.0), (73.0, 61.5), 1.2, 0.95], kind="steel"),
    "era4_t2": dict(stub=[(74, 74.5), (84, 73.5), (84, 81), (73, 81)], band=[(67.5, 56.0), (68.0, 72.0), 4.6, 4.6], thumb=[(60.5, 42.0), (75.0, 62.0), 1.16, 1.0], kind="steel"),
    "era4_t3": dict(stub=[(64, 77.0), (77, 75.5), (78, 84), (63, 84)], band=[(49.0, 59.5), (49.5, 74.0), 4.6, 4.6], thumb=[(47.0, 42.5), (62.0, 62.5), 1.16, 1.06], kind="steel"),
}


def lum(c):
    return c[..., 0] * 0.299 + c[..., 1] * 0.587 + c[..., 2] * 0.114


def cap(d, p0, p1, r0, r1):
    for i in range(41):
        t = i / 40
        x = (p0[0] + (p1[0] - p0[0]) * t) * SS
        y = (p0[1] + (p1[1] - p0[1]) * t) * SS
        r = (r0 + (r1 - r0) * t) * SS
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)


class Art:
    def __init__(self, src):
        self.src = src
        self.out = src.copy()
        self.H, self.W = src.shape[:2]

    def mask(self, fn):
        im = Image.new("L", (self.W * SS, self.H * SS), 0)
        fn(ImageDraw.Draw(im))
        return (np.asarray(im, np.float64) / 255).reshape(self.H, SS, self.W, SS).mean((1, 3))

    def blend(self, mask, color, k=1.0):
        m = np.clip(mask, 0, 1)[..., None] * k
        self.out[..., :3] = np.asarray(color, np.float64)[None, None, :] * m + self.out[..., :3] * (1 - m)

    def opaque(self):
        return self.out[..., 3] > 128

    def nail(self, c0, c1, r0, r1, clip, tones, along):
        """손톱 하나: 살보다 조금 밝고 분홍 · 끝(자라는 쪽)에 밝은 초승달 · 뿌리와 옆에 가는 선 · 왼위 반짝임.
        c0 = 뿌리 쪽 중심, c1 = 끝 쪽 중심. along = 뿌리 → 끝으로 0 → 1이 되는 값."""
        nm = self.mask(lambda d: cap(d, c0, c1, r0, r1)) * clip
        rim = np.clip(ndimage.gaussian_filter(self.mask(lambda d: cap(d, c0, c1, r0 + 0.75, r1 + 0.75)), 0.35) - nm, 0, 1) * clip
        self.blend(rim, tones["line"], 0.62)
        base = tones["nail"]
        col = base[None, None, :] * (1 - 0.1 * (1 - along[..., None])) + np.array([18.0, 16.0, 16.0])[None, None, :] * np.clip((along[..., None] - 0.72) / 0.28, 0, 1)
        self.out[..., :3] = np.clip(col, 0, 255) * nm[..., None] + self.out[..., :3] * (1 - nm[..., None])
        # 왼쪽으로 치우친 가는 반짝임
        dx, dy = c1[0] - c0[0], c1[1] - c0[1]
        L = np.hypot(dx, dy) + 1e-9
        nx, ny = -dy / L, dx / L
        if nx > 0 or (abs(nx) < 1e-6 and ny > 0):
            nx, ny = -nx, -ny
        k = r0 * 0.42
        h0 = (c0[0] + nx * k + dx * 0.12, c0[1] + ny * k + dy * 0.12)
        h1 = (c0[0] + nx * k + dx * 0.72, c0[1] + ny * k + dy * 0.72)
        hl = ndimage.gaussian_filter(self.mask(lambda d: cap(d, h0, h1, 0.55, 0.4)), 0.45)
        self.blend(hl * nm, (255, 249, 242), 0.5)


def tones_for(src, kind):
    px = src[src[..., 3] > 200][:, :3]
    L = lum(px)
    if kind == "skin":
        sk = px[(px[:, 0] > px[:, 2] * 1.3) & (L > 95)]
        Ls = lum(sk)

        def at(p):
            v = np.percentile(Ls, p)
            return sk[np.abs(Ls - v) < 6].mean(0)
        hi, lo = at(93), at(22)
        nail = np.clip(hi * np.array([1.0, 0.985, 1.0]) + np.array([8.0, 9.0, 12.0]), 0, 255)       # 살 하이라이트보다 조금 밝고 분홍
        return dict(nail=nail, line=lo * 0.62)
    return dict(nail=px.mean(0), line=INK)


def redo(src, sp):
    A = Art(src)
    out = A.out
    H, W = A.H, A.W
    tones = tones_for(src, sp["kind"])
    yy = np.arange(H)[:, None] * np.ones((1, W))
    xx = np.arange(W)[None, :] * np.ones((H, 1))

    # ① 옛 엄지 지우기 + 잘린 가장자리 먹선
    if sp.get("stub"):
        stub = A.mask(lambda d: d.polygon([(x * SS, y * SS) for x, y in sp["stub"]], fill=255))
        out[..., 3] = out[..., 3] * (1 - stub)
        edge = ndimage.binary_dilation(stub > 0.5, iterations=1) & A.opaque()
        out[edge, :3] = out[edge, :3] * 0.3 + INK * 0.7

    # ③ 손톱(엄지가 덮지 않는 손가락) — 엄지보다 먼저 그려 엄지 그림자가 그 위에 지게 한다
    for nx, ny, nw in sp.get("nails", []):
        c1 = (nx, ny + nw * 0.5)                   # 끝(위)
        c0 = (nx + 0.25, ny + nw * 0.5 + nw * 0.62)  # 뿌리(아래)
        along = np.clip((c0[1] + nw * 0.5 - yy) / (nw * 1.6), 0, 1)
        A.nail(c0, c1, nw * 0.47, nw * 0.43, A.opaque() * 1.0, tones, along)

    # ② 엄지: 손가락 한 줄을 떼어 비스듬히 얹는다
    b0, b1, br0, br1 = sp["band"]
    bm = A.mask(lambda d: cap(d, b0, b1, br0, br1))
    band = src.copy()
    band[..., 3] = band[..., 3] * bm
    x0, x1 = int(min(b0[0], b1[0]) - max(br0, br1) - 2), int(max(b0[0], b1[0]) + max(br0, br1) + 3)
    y0, y1 = int(min(b0[1], b1[1]) - max(br0, br1) - 2), int(max(b0[1], b1[1]) + max(br0, br1) + 3)
    bim = Image.fromarray(np.clip(band, 0, 255).astype(np.uint8), "RGBA").crop((x0, y0, x1, y1))
    base, tip, kw, kl = sp["thumb"]
    bim = bim.resize((max(2, int(round(bim.width * kw))), max(2, int(round(bim.height * kl)))), Image.LANCZOS)
    ang = np.degrees(np.arctan2(tip[0] - base[0], tip[1] - base[1]))
    R = 64
    big = Image.new("RGBA", (R * 2, R * 2), (0, 0, 0, 0))
    big.alpha_composite(bim, (R - bim.width // 2, R - bim.height // 2))
    big = big.rotate(ang, resample=Image.BICUBIC, center=(R, R))
    cx, cy = (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2
    ox, oy = int(round(cx - R)), int(round(cy - R))
    th = np.zeros_like(out)
    tb = np.asarray(big).astype(np.float64)
    ys, xs, ye, xe = max(0, oy), max(0, ox), min(H, oy + R * 2), min(W, ox + R * 2)
    th[ys:ye, xs:xe] = tb[ys - oy:ye - oy, xs - ox:xe - ox]
    ux, uy = tip[0] - base[0], tip[1] - base[1]
    L = np.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    s = ((xx - base[0]) * ux + (yy - base[1]) * uy) / L          # 뿌리 0 → 끝 1
    # 엄지 제 모양: 끝이 둥글고 뿌리에서 끝으로 조금 가늘어지는 막대. 옛 손 윤곽 밖으로는 나가지 않는다
    r0 = max(br0, br1) * kw
    r1 = r0 * 0.86
    shape = A.mask(lambda d: cap(d, (base[0] + ux * r0, base[1] + uy * r0), (tip[0] - ux * r1, tip[1] - uy * r1), r0, r1))
    inside = ndimage.binary_dilation(src[..., 3] > 128, iterations=1)
    th[..., 3] = th[..., 3] * shape * inside
    ta = th[..., 3] / 255
    # 끝(오른아래)으로 갈수록 조금 가라앉힌다
    th[..., :3] *= (1 - 0.16 * np.clip((s - 0.55) / 0.5, 0, 1))[..., None]
    # 그림자(오른아래로) → 먹선 → 엄지
    sh = ndimage.gaussian_filter(np.roll(np.roll(ta, 2, 0), 2, 1), 1.4)
    out[..., :3] *= (1 - np.clip(sh, 0, 1) * 0.5 * (1 - ta) * A.opaque())[..., None]
    o = np.clip(ndimage.gaussian_filter((ndimage.binary_dilation(ta > 0.5, iterations=1) & ~(ta > 0.5)).astype(float), 0.45) * 1.7, 0, 1)
    A.blend(o, INK, 0.95)
    out[..., 3] = np.maximum(out[..., 3], o * 255 * 0.95)
    out[..., :3] = th[..., :3] * ta[..., None] + out[..., :3] * (1 - ta[..., None])
    out[..., 3] = np.maximum(out[..., 3], th[..., 3])
    if sp["kind"] != "skin":
        # 건틀릿 엄지: 가운데를 따라 가는 금속 빛 한 줄(어두운 쇠에서도 엄지가 읽히게)
        px = src[src[..., 3] > 200][:, :3]
        hi = px[lum(px) >= np.percentile(lum(px), 96)].mean(0)
        h0 = (base[0] + ux * L * 0.2 - uy * 1.0, base[1] + uy * L * 0.2 + ux * 1.0)
        h1 = (base[0] + ux * L * 0.72 - uy * 1.0, base[1] + uy * L * 0.72 + ux * 1.0)
        hl = ndimage.gaussian_filter(A.mask(lambda d: cap(d, h0, h1, 0.8, 0.5)), 0.5)
        if sp["kind"] == "gold":
            hi = hi * np.array([1.0, 0.93, 0.66])          # 흰빛이 아니라 금빛으로
        A.blend(hl * (ta > 0.5), hi, 0.36 if sp["kind"] == "gold" else 0.3)
    if sp.get("tnail"):
        t0, t1, hw = sp["tnail"]
        c0 = (base[0] + ux * L * t0, base[1] + uy * L * t0)
        c1 = (base[0] + ux * L * t1, base[1] + uy * L * t1)
        A.nail(c0, c1, hw, hw * 0.9, (ta > 0.5) * 1.0, tones, np.clip((s - t0) / (t1 - t0 + 0.12), 0, 1))
    # 손목 끈을 엄지 뿌리 위로 다시 덮는다(끈 밑에서 엄지가 나온 것처럼)
    if sp.get("strap"):
        st = (src[..., 3] > 128) & (lum(src) < 92) & (yy < sp["strap"]) & ~((src[..., 0] > src[..., 2] * 1.45) & (lum(src) > 70))
        st = ndimage.binary_opening(st, iterations=1)
        k = ndimage.gaussian_filter(st.astype(float), 0.5)[..., None]
        out[..., :3] = src[..., :3] * k + out[..., :3] * (1 - k)
        out[..., 3] = np.maximum(out[..., 3], src[..., 3] * k[..., 0])
    return out


if __name__ == "__main__":
    SRC, OUT = sys.argv[1], sys.argv[2]
    SHEET = sys.argv[3] if len(sys.argv) > 3 else None
    cells = []
    for name, sp in SPEC.items():
        src = np.asarray(Image.open(f"{SRC}/{name}.png").convert("RGBA")).astype(np.float64)
        dst = redo(src, sp)
        im = Image.fromarray(np.clip(dst, 0, 255).astype(np.uint8), "RGBA")
        im.save(f"{OUT}/{name}.png", optimize=True)
        ch = int((np.abs(dst - src).max(-1) > 6).sum())
        print(f"{name}.png {im.size} 바뀐 픽셀 {ch}")
        cells.append((name, src, dst))
    if SHEET:
        Z = 6
        cw, chh = 88 * Z, 66 * Z
        sh = Image.new("RGB", ((cw * 2 + 6) * 3 + 20, (chh + 6) * 3), (20, 20, 24))
        dr = ImageDraw.Draw(sh)
        for i, (name, a, b) in enumerate(cells):
            gx, gy = (i % 3) * (cw * 2 + 16), (i // 3) * (chh + 6)
            for k, arr in enumerate((a, b)):
                im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA").crop((26, 28, 114, 94)).resize((cw, chh), Image.LANCZOS)
                bg = Image.new("RGBA", im.size, (74, 82, 100, 255))
                bg.alpha_composite(im)
                sh.paste(bg.convert("RGB"), (gx + k * (cw + 4), gy))
            dr.text((gx + 6, gy + 4), name + "   before | after", fill=(255, 255, 0))
        sh.save(SHEET)
        print("sheet", SHEET, sh.size)
