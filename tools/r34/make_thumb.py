#!/usr/bin/env python3
"""R34 갤러리 썸네일(1200×630) — 게임 원화로 만든 키 아트: 개경 화염 전장 · 척준경(청룡 자세 + 장검 · 청룡 이펙트) vs 파두반 · 제목.
사용: python3 -I tools/r34/make_thumb.py <빌드 폴더> <grips_r33.json> <출력 png>"""
import json
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT, GJ, OUT = sys.argv[1:4]
A = ROOT + '/assets'
W, H = 1200, 630
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'

bg = Image.open(f'{A}/bg/era4_bg_kaegyeong_fire.webp').convert('RGB').resize((W, 675), Image.LANCZOS).crop((0, 30, W, 30 + H))
can = bg.convert('RGBA')
# 아래 · 왼쪽을 어둡게(인물 · 글자 대비)
g = np.zeros((H, W, 4), np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
dark = np.clip(0.30 + 0.45 * (yy / H) ** 2 + 0.25 * np.clip(1 - xx / 520, 0, 1), 0, 0.8)
g[..., 3] = (dark * 255).astype(np.uint8)
g[..., :3] = (8, 6, 10)
can.alpha_composite(Image.fromarray(g, 'RGBA'))


def with_sword(frame, grip, tier=3):
    body = Image.open(f'{A}/hero/era4_hero_{frame}.webp').convert('RGBA')
    wp = Image.open(f'{A}/weapon/era4_t{tier}.png').convert('RGBA')
    PAD = 260
    c = Image.new('RGBA', (512 + 2 * PAD, 512 + 2 * PAD), (0, 0, 0, 0))
    c.alpha_composite(body, (PAD, PAD))
    x, y, a, f = grip
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if f else wp
    gy = (w.height - 60) if f else 60
    big = Image.new('RGBA', (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - 70, cy - gy))
    rot = big.rotate(-a, center=(cx, cy), resample=Image.BICUBIC)
    lay = Image.new('RGBA', c.size, (0, 0, 0, 0))
    lay.paste(rot, (int(x + PAD - cx), int(y + PAD - cy)), rot)
    c.alpha_composite(lay)
    return c, PAD


def place(img, scale, cx, foot_y, src_foot_y, src_cx):
    im = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    can.alpha_composite(im, (int(cx - src_cx * scale), int(foot_y - src_foot_y * scale)))


def rim(img, col, r=6, a=0.55):
    """인물 둘레에 옅은 빛 테두리(배경과 분리)."""
    al = img.split()[3].filter(ImageFilter.GaussianBlur(r))
    glow = Image.new('RGBA', img.size, col + (0,))
    glow.putalpha(al.point(lambda v: int(v * a)))
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(img)
    return out


G = json.load(open(GJ, encoding='utf-8'))['R26_CJG_FRAMES']
# 청룡 이펙트(주인공 뒤 · 스크린 합성)
fx = Image.open(f'{A}/fx/era4_fx_azure_dragon.webp').convert('RGBA').resize((640, 640), Image.LANCZOS)
lay = Image.new('RGBA', can.size, (0, 0, 0, 0))
lay.alpha_composite(fx, (20, 60))
scr = ImageChops.screen(can.convert('RGB'), Image.composite(lay.convert('RGB'), Image.new('RGB', can.size, (0, 0, 0)), lay.split()[3]))
can = Image.blend(can.convert('RGB'), scr, 0.9).convert('RGBA')
hero, PAD = with_sword('dragon_stance', G['dragon_stance'])
place(rim(hero, (120, 200, 255)), 0.96, 330, 612, PAD + 470, PAD + 256)
boss = Image.open(f'{A}/boss/era4_boss_paduban_slash.webp').convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)
place(rim(boss, (255, 150, 60), 7, 0.5), 0.8, 900, 616, 600, 768 - 392)

# 제목: 금빛 그라데이션 글자 + 먹 테두리
d = ImageDraw.Draw(can)


def gold_text(xy, text, size, stroke):
    f = ImageFont.truetype(FONT, size)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    tw, th = bb[2] - bb[0] + 8, bb[3] - bb[1] + 8
    mask = Image.new('L', (tw, th), 0)
    ImageDraw.Draw(mask).text((4 - bb[0], 4 - bb[1]), text, font=f, fill=255)
    edge = Image.new('L', (tw, th), 0)
    ImageDraw.Draw(edge).text((4 - bb[0], 4 - bb[1]), text, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
    sh = Image.new('RGBA', (tw, th), (10, 6, 4, 0))
    sh.putalpha(edge)
    can.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)), (xy[0], xy[1] + 4))
    can.alpha_composite(sh, xy)
    grad = np.zeros((th, tw, 4), np.uint8)
    t = np.linspace(0, 1, th)[:, None]
    top, mid, bot = np.array([255, 244, 200]), np.array([250, 204, 21]), np.array([180, 100, 14])
    colr = np.where(t < 0.5, top + (mid - top) * (t / 0.5), mid + (bot - mid) * ((t - 0.5) / 0.5))
    grad[..., :3] = np.repeat(colr[:, None, :], tw, axis=1).astype(np.uint8)
    grad[..., 3] = np.asarray(mask)
    can.alpha_composite(Image.fromarray(grad, 'RGBA'), xy)
    return tw, th


def centered(text, size, stroke, y):
    f = ImageFont.truetype(FONT, size)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    return gold_text(((W - (bb[2] - bb[0] + 8)) // 2, y), text, size, stroke)


centered('신시 神市', 88, 7, 10)
centered('시공의 수호자들', 44, 5, 108)
f2 = ImageFont.truetype(FONT, 24)
tag = '한국사 여섯 시대를 베어 넘는 수묵 액션'
tw = d.textlength(tag, font=f2)
d.text(((W - tw) // 2, 584), tag, font=f2, fill=(238, 232, 220), stroke_width=3, stroke_fill=(12, 8, 6))
can.convert('RGB').save(OUT, quality=88, optimize=True)
print('thumb', can.size)
