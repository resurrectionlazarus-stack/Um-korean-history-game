# R35 — 1시대 대사냥꾼 무기 3장의 '손'을 하나로 통일
#  문제: 무기 그림마다 손이 따로 그려져 있고(1단계 = 손잡이 방향 팔뚝, 2단계 = 아래로 내려가는 팔뚝, 3단계 = 큰 손등 + 왼위 손목),
#        몸 원화의 팔(소매 끝)과 방향이 맞지 않는 자세에서 '손목이 하나 더' 보였다.
#  해결: 1단계의 주먹(팔뚝 없이 주먹만)을 세 무기에 똑같이 쓴다. 팔뚝 · 손목 토막은 지우고, 손잡이 끝(나무)만 남긴다.
#        쥔 자리(70,60) · 그림 크기 · 날 길이는 그대로 → 쥔 자리 표(R27_HUNTER_FRAMES)는 손대지 않는다.
#  python3 -I tools/r35/unify_fist.py <원본 폴더> <출력 폴더>
import sys
import numpy as np
from PIL import Image, ImageDraw

SRC, OUT = sys.argv[1], sys.argv[2]
FX0, FX1 = 44, 106       # 1단계 주먹이 차지하는 가로 범위(이 안의 불투명 픽셀 = 주먹)


def load(t):
    return np.asarray(Image.open(f'{SRC}/era1_t{t}.png').convert('RGBA')).astype(np.float32)


def poly_mask(shape, pts):
    m = Image.new('L', (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.asarray(m) > 0


t1, t2, t3 = load(1), load(2), load(3)
H = t1.shape[0]

# ① 1단계에서 주먹만 떼기(가죽끈 · 손가락 · 엄지 포함, 왼쪽 팔뚝 토막 제외)
fist = np.zeros((H, FX1 - FX0, 4), np.float32)
fist[:] = t1[:, FX0:FX1]
# 잘린 왼쪽 모서리: 선화처럼 어둡게 닫기 + 위아래 모서리 둥글게
col = fist[:, 0, 3] > 40
ys = np.where(col)[0]
ya, yb = ys.min(), ys.max()
fist[:, 0, :3] *= 0.22
fist[:, 1, :3] *= 0.5
fist[:, 2, :3] *= 0.8
for d, a in ((0, 0.0), (1, 0.45)):      # 모서리 둥글림
    fist[ya + d, 0, 3] *= a; fist[yb - d, 0, 3] *= a
fist[ya, 1, 3] *= 0.5; fist[yb, 1, 3] *= 0.5


# 주먹 밑으로 보이는 손잡이 조각(1단계의 밝은 나무색) — 다른 무기에 얹을 때는 그 무기 손잡이 색에 맞춘다
WOOD = poly_mask((H, FX1 - FX0), [(0, 56), (9, 56), (16, 61), (17, 74), (0, 74)])


def paste_fist(dst, wood_tint=None):
    f = fist.copy()
    if wood_tint is not None:
        f[WOOD, :3] *= np.array(wood_tint, np.float32)
    a = f[..., 3:4] / 255
    reg = dst[:, FX0:FX1]
    reg[..., :3] = f[..., :3] * a + reg[..., :3] * (1 - a)
    reg[..., 3:4] = np.maximum(reg[..., 3:4], f[..., 3:4])


def extend_cols(dst, src_x, xs, y0, y1, fade=None):
    # 손잡이 이어 붙이기: src_x 열의 세로 단면을 xs 열들에 복사(가려져 있던 손잡이 복원)
    for i, x in enumerate(xs):
        sx = src_x[i % len(src_x)]
        dst[y0:y1, x] = dst[y0:y1, sx]


# ② 1단계: 팔뚝 토막(가죽 감은 팔 + 살색 단면) 지우고 나무 손잡이 끝을 짧게
n1 = t1.copy()
n1[:, :FX0] = 0
# 손잡이 끝(8px): 주먹 오른쪽의 나무 손잡이 단면을 뒤집어 가져온다. 주먹 밑으로 보이는 손잡이(y 58~72)에 맞춰 3px 내림
hy0, hy1, dy = 50, 73, 3
for i in range(9):
    x = FX0 - 1 - i
    sx = 108 + i
    n1[hy0 + dy:hy1 + dy, x] = t1[hy0:hy1, sx]
# 끝 둥글리기 + 어두운 외곽선
xe = FX0 - 9
for x, cut in ((xe, 3), (xe + 1, 1)):
    colA = n1[:, x, 3] > 40
    ys = np.where(colA)[0]
    if len(ys):
        n1[ys.min():ys.min() + cut, x] = 0
        n1[ys.max() - cut + 1:ys.max() + 1, x] = 0
n1[:, xe, :3] *= 0.2
n1[:, xe + 1, :3] *= 0.6
paste_fist(n1)

# ③ 2단계(슴베찌르개): 손 + 아래로 내려가는 팔뚝 지우기 → 손잡이 복원 → 통일 주먹
n2 = t2.copy()
hand2 = poly_mask(n2.shape, [(44, 48), (48, 40), (56, 34), (68, 30), (80, 28), (90, 30), (98, 36), (102, 46), (103, 60), (103, 74), (98, 80), (90, 86), (90, 119), (42, 119), (42, 100), (44, 84), (44, 68), (47, 66), (47, 50)])
n2[hand2] = 0
# 손잡이(가려져 있던 부분) 복원: 왼쪽 끝동 단면(x 40~43)과 오른쪽 손잡이 단면(x 104~107)을 가운데로 이어 붙임
for x in range(44, 76):
    n2[46:72, x] = t2[46:72, 40 + (x - 44) % 4]
for x in range(76, 104):
    n2[46:72, x] = t2[46:72, 104 + (x - 76) % 4]
paste_fist(n2, (0.5, 0.48, 0.5))

# ④ 3단계(간돌도끼): 큰 손등 + 손목 지우기 → 손잡이 복원 → 통일 주먹
n3 = t3.copy()
hand3 = poly_mask(n3.shape, [(19, 38), (30, 30), (40, 26), (52, 22), (66, 21), (70, 22), (78, 24), (92, 30), (101, 36), (106, 46), (100, 47), (101, 52), (107, 66), (108, 80), (100, 84), (90, 87), (74, 87), (60, 84), (50, 79), (45, 73), (40, 62), (38, 51), (30, 47), (22, 43)])
n3[hand3] = 0
for x in range(34, 74):
    n3[50:78, x] = t3[50:78, 28 + (x - 34) % 5]
for x in range(74, 110):
    n3[44:72, x] = t3[44:72, 110 + (x - 74) % 4]
paste_fist(n3)

for t, arr in ((1, n1), (2, n2), (3, n3)):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    im.save(f'{OUT}/era1_t{t}.png', optimize=True)
    print(f'era1_t{t}.png', im.size)
