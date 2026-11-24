#!/usr/bin/env python3
"""R24 유물 각성 아이콘 17종 — SVG(256×256, 투명 배경) 생성기.
사용법: python3 relic_icons.py OUT_DIR → OUT_DIR/{id}.svg
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
INK = "#07080b"
ST = f'stroke="{INK}" stroke-linejoin="round" stroke-linecap="round"'

COMMON_DEFS = f'''
<filter id="ol" x="-20%" y="-20%" width="140%" height="140%">
 <feMorphology in="SourceAlpha" operator="dilate" radius="3.2" result="d"/>
 <feFlood flood-color="{INK}" result="c"/><feComposite in="c" in2="d" operator="in" result="o"/>
 <feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<filter id="blur6" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="blur2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2"/></filter>
'''


def lin(i, x1, y1, x2, y2, stops):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>'


def rad(i, cx, cy, r, stops, op=None):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>" for o, c, a in stops)
    return f'<radialGradient id="{i}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}">{st}</radialGradient>'


def glow(color, r=96, a=0.55):
    return (f'<defs>{rad("glw", 128, 128, r, [(0, color, a), (0.55, color, a * 0.35), (1, color, 0)])}</defs>'
            f'<circle cx="128" cy="128" r="{r}" fill="url(#glw)"/>')


def sparkle(x, y, s, col="#ffffff", a=0.95):
    return (f'<path d="M{x},{y - s} Q{x + s*0.16},{y - s*0.16} {x + s},{y} Q{x + s*0.16},{y + s*0.16} {x},{y + s} '
            f'Q{x - s*0.16},{y + s*0.16} {x - s},{y} Q{x - s*0.16},{y - s*0.16} {x},{y - s}Z" fill="{col}" opacity="{a}"/>')


def svg(body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
            f'<defs>{COMMON_DEFS}{defs}</defs>{body}</svg>')


ICONS = {}


def icon(fn):
    ICONS[fn.__name__] = fn
    return fn


# ───────── 1시대 ─────────
@icon
def era1_obsidian():
    # 흑요석 슴베찌르개: 잎새형 찌르개 + 아래 슴베(자루 꽂는 부분), 유리질 박리면
    d = lin("ob", 70, 60, 190, 200, [(0, "#4c3a8a"), (0.35, "#1b1430"), (0.7, "#0a0812"), (1, "#2c2154")])
    edge = "#b7a6ff"
    pts = "128,18 160,70 166,120 150,160 140,176 116,176 106,160 90,120 96,70"
    facets = [
        "128,18 140,62 128,96 116,60", "140,62 160,70 166,120 146,112 128,96", "116,60 96,70 90,120 110,112 128,96",
        "128,96 146,112 150,160 128,150", "128,96 110,112 106,160 128,150", "150,160 140,176 128,150", "106,160 116,176 128,150",
    ]
    body = glow("#8b5cf6", 104, 0.6)
    g = [f'<g filter="url(#ol)" transform="rotate(28 128 128)">']
    # 슴베 + 나무 자루 끝 + 감은 끈
    g.append(f'<path d="M116,176 L140,176 L134,214 L122,214Z" fill="#241a3d" {ST} stroke-width="2"/>')
    g.append(f'<rect x="113" y="198" width="30" height="46" rx="7" fill="#5b3b22" {ST} stroke-width="2"/>')
    g.append("".join(f'<path d="M113,{204 + k*7} L143,{208 + k*7}" stroke="#c9a46a" stroke-width="3"/>' for k in range(4)))
    g.append(f'<polygon points="{pts}" fill="url(#ob)" {ST} stroke-width="2.4"/>')
    for i, fp in enumerate(facets):
        op = [0.22, 0.12, 0.28, 0.1, 0.2, 0.3, 0.16][i]
        g.append(f'<polygon points="{fp}" fill="#c4b5fd" opacity="{op}" stroke="#d8ccff" stroke-opacity="0.45" stroke-width="1.2"/>')
    g.append(f'<path d="M128,22 L120,60 M100,74 L94,118" stroke="{edge}" stroke-width="2.4" opacity="0.9"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(166, 62, 16, "#ede9fe") + sparkle(92, 150, 9, "#c4b5fd", 0.8)
    return svg(body, d)


@icon
def era1_polished_axe():
    # 신석기 간돌도끼(마제석부): 매끈하게 간 돌 날 + 나무 자루 + 가죽끈
    d = (lin("st", 60, 70, 170, 170, [(0, "#d7d3c4"), (0.35, "#8f8a78"), (0.75, "#4c4a40"), (1, "#2a2924")]) +
         lin("wd", 0, 0, 30, 0, [(0, "#8a5a32"), (0.5, "#5a3a20"), (1, "#2e1d10")]))
    body = glow("#f59e0b", 104, 0.55)
    g = ['<g filter="url(#ol)">']
    g.append(f'<g transform="rotate(-38 128 140)"><rect x="116" y="70" width="24" height="176" rx="9" fill="url(#wd)" {ST} stroke-width="2.2"/>'
             f'<path d="M122,80 V236" stroke="#b07a48" stroke-width="2.4" opacity="0.6"/></g>')
    # 돌 날(자루를 감싸 묶은 형태)
    g.append(f'<path d="M58,92 C62,64 92,50 118,58 L150,72 C162,78 164,96 154,106 L120,124 C94,136 62,126 58,92Z" fill="url(#st)" {ST} stroke-width="2.6"/>')
    g.append(f'<path d="M62,88 C68,70 90,60 112,64" fill="none" stroke="#fffbeb" stroke-width="4" opacity="0.7"/>')
    g.append(f'<path d="M58,92 C62,112 82,128 104,128" fill="none" stroke="#f8e7c4" stroke-width="2.2" opacity="0.55"/>')
    # 가죽끈 감기
    g.append("".join(f'<path d="M{132 + k*6},{70 + k*3} L{120 + k*6},{118 + k*2}" stroke="#7c4a24" stroke-width="5"/>'
                     f'<path d="M{132 + k*6},{70 + k*3} L{120 + k*6},{118 + k*2}" stroke="#c48a52" stroke-width="1.6"/>' for k in range(4)))
    g.append("</g>")
    body += "".join(g) + sparkle(70, 76, 15, "#fff7ed") + sparkle(178, 64, 9, "#fde68a", 0.85)
    return svg(body, d)


# ───────── 2시대 ─────────
@icon
def era2_slender_dagger():
    # 세형 동검(한국식 동검): 가늘고 곧은 날 + 가운데 등대 + 날 아래 마디(결입부) + 검자루
    d = (lin("bz", 100, 0, 156, 0, [(0, "#2a5f58"), (0.35, "#c8a24a"), (0.55, "#f7e2a0"), (0.7, "#b48a36"), (1, "#3e6b5f")]) +
         lin("hl", 0, 180, 0, 250, [(0, "#9b7a3c"), (1, "#4a3618")]))
    body = glow("#2dd4bf", 104, 0.5)
    g = ['<g filter="url(#ol)" transform="rotate(32 128 128)">']
    g.append(f'<path d="M128,10 C136,40 140,70 141,96 L146,104 L141,112 C142,140 141,160 139,176 L117,176 C115,160 114,140 115,112 L110,104 L115,96 C116,70 120,40 128,10Z" fill="url(#bz)" {ST} stroke-width="2.2"/>')
    g.append(f'<path d="M128,16 V174" stroke="#fff3c4" stroke-width="2.6" opacity="0.85"/><path d="M131,20 V172" stroke="#5b4320" stroke-width="1.4" opacity="0.7"/>')
    g.append(f'<rect x="110" y="174" width="36" height="12" rx="3" fill="#7a5a26" {ST} stroke-width="2"/>')
    g.append(f'<rect x="119" y="186" width="18" height="44" rx="4" fill="url(#hl)" {ST} stroke-width="2"/>')
    g.append(f'<path d="M104,236 C112,226 144,226 152,236 C146,246 110,246 104,236Z" fill="#b48a36" {ST} stroke-width="2"/>')
    g.append(f'<circle cx="128" cy="236" r="4" fill="#2dd4bf"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(168, 50, 15, "#ecfeff") + sparkle(96, 196, 8, "#99f6e4", 0.8)
    return svg(body, d)


@icon
def era2_iron_sword():
    # 고조선 후기 철제 장검: 곧은 쇠 날, 붉게 달군 날 끝
    d = (lin("ir", 108, 0, 148, 0, [(0, "#2b2f36"), (0.45, "#9aa3ad"), (0.55, "#e6ebf0"), (0.7, "#6b7480"), (1, "#22262c")]) +
         lin("hot", 0, 14, 0, 110, [(0, "#fff1c2"), (0.35, "#f97316"), (1, "#f97316")]))
    body = glow("#ef4444", 104, 0.45)
    g = ['<g filter="url(#ol)" transform="rotate(-34 128 128)">']
    g.append(f'<path d="M128,8 L144,30 L142,184 L114,184 L112,30Z" fill="url(#ir)" {ST} stroke-width="2.2"/>')
    g.append(f'<path d="M128,10 L144,30 L143,96 C136,80 132,60 128,40Z" fill="url(#hot)" opacity="0.75"/>')
    g.append(f'<path d="M128,14 V182" stroke="#f8fafc" stroke-width="2" opacity="0.7"/>')
    g.append(f'<path d="M98,184 H158 L152,196 H104Z" fill="#3b3f46" {ST} stroke-width="2"/>')
    g.append(f'<rect x="118" y="196" width="20" height="40" rx="4" fill="#3a2a1e" {ST} stroke-width="2"/>')
    g.append("".join(f'<path d="M118,{202 + k*8} L138,{206 + k*8}" stroke="#7a5a3c" stroke-width="2.4"/>' for k in range(4)))
    g.append(f'<circle cx="128" cy="242" r="9" fill="#4a4f57" {ST} stroke-width="2"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(84, 56, 14, "#fff7ed") + sparkle(60, 96, 7, "#fdba74", 0.9) + sparkle(98, 34, 6, "#fde68a", 0.9)
    return svg(body, d)


# ───────── 3시대 ─────────
@icon
def era3_hwarang_sword():
    # 화랑 임전무퇴 검: 고리자루(환두) + 붉은 매듭 + 꽃잎
    d = (lin("bl", 112, 0, 144, 0, [(0, "#3a3f47"), (0.5, "#dfe5eb"), (1, "#4b5260")]) +
         lin("au", 0, 170, 0, 250, [(0, "#fde68a"), (0.5, "#d4a017"), (1, "#7c5a12")]))
    body = glow("#fb7185", 104, 0.5)
    g = ['<g filter="url(#ol)" transform="rotate(34 128 128)">']
    g.append(f'<path d="M128,10 L141,28 L140,170 L116,170 L115,28Z" fill="url(#bl)" {ST} stroke-width="2.2"/>')
    g.append(f'<path d="M128,14 V168" stroke="#ffffff" stroke-width="2" opacity="0.75"/>')
    g.append(f'<rect x="108" y="168" width="40" height="10" rx="3" fill="url(#au)" {ST} stroke-width="2"/>')
    g.append(f'<rect x="119" y="178" width="18" height="40" rx="4" fill="#5b1220" {ST} stroke-width="2"/>')
    g.append(f'<circle cx="128" cy="232" r="15" fill="none" stroke="{INK}" stroke-width="10"/><circle cx="128" cy="232" r="15" fill="none" stroke="url(#au)" stroke-width="6"/>')
    g.append(f'<path d="M128,247 C120,262 112,266 104,268 M128,247 C134,262 142,266 150,266" fill="none" stroke="#be123c" stroke-width="4"/>')
    g.append("</g>")
    for (x, y, r, a) in ((60, 70, 10, 20), (196, 150, 8, -30), (80, 188, 7, 60), (184, 70, 6, 10)):
        body_p = f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.55}" transform="rotate({a} {x} {y})" fill="#fda4af" stroke="#9d174d" stroke-width="1.6"/>'
        g.append(body_p)
    body += "".join(g) + sparkle(170, 46, 14, "#fff1f2")
    return svg(body, d)


@icon
def era3_golden_dagger():
    # 계림로 황금 보검: 금판 칼집 + 석류석(붉은 보석) 상감 무늬
    d = (lin("gd", 90, 0, 166, 0, [(0, "#7c5a12"), (0.35, "#f6d365"), (0.55, "#fff3c4"), (0.75, "#d4a017"), (1, "#6b4b0e")]))
    body = glow("#facc15", 108, 0.55)
    g = ['<g filter="url(#ol)" transform="rotate(-30 128 128)">']
    # 칼집(아래로 넓어지는 방패꼴 머리 + 긴 몸)
    g.append(f'<path d="M100,40 C100,24 156,24 156,40 L150,60 L146,196 C146,214 110,214 110,196 L106,60Z" fill="url(#gd)" {ST} stroke-width="2.4"/>')
    g.append(f'<path d="M92,52 C88,34 104,18 128,18 C152,18 168,34 164,52 C150,62 106,62 92,52Z" fill="url(#gd)" {ST} stroke-width="2.4"/>')
    gem = lambda x, y, rx, ry: (f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#9f1239" {ST} stroke-width="1.6"/>'
                                f'<ellipse cx="{x - rx*0.3}" cy="{y - ry*0.35}" rx="{rx*0.35}" ry="{ry*0.3}" fill="#fecdd3" opacity="0.85"/>')
    g.append(gem(128, 38, 12, 9) + gem(108, 40, 5, 6) + gem(148, 40, 5, 6))
    for k in range(5):
        y = 76 + k * 24
        g.append(f'<path d="M116,{y} C120,{y - 10} 136,{y - 10} 140,{y} C136,{y + 10} 120,{y + 10} 116,{y}Z" fill="none" stroke="#7c5a12" stroke-width="2.6"/>')
        g.append(gem(128, y, 6, 5))
    g.append(f'<path d="M118,206 C122,222 134,222 138,206" fill="none" stroke="#7c5a12" stroke-width="3"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(178, 64, 16, "#fffbeb") + sparkle(76, 174, 9, "#fde68a", 0.9)
    return svg(body, d)


# ───────── 4시대 ─────────
@icon
def era4_byeolmuban_spear():
    # 별무반 신기군 장창: 창날 + 붉은 술 + 신기군 깃발(神騎)
    d = (lin("bl", 108, 0, 148, 0, [(0, "#2b3038"), (0.48, "#d8e0e8"), (0.52, "#7d8794"), (1, "#22262d")]) +
         lin("fl", 140, 60, 220, 120, [(0, "#1e3a8a"), (1, "#0f1f4d")]))
    body = glow("#38bdf8", 104, 0.5)
    g = ['<g filter="url(#ol)" transform="rotate(30 128 128)">']
    g.append(f'<rect x="122" y="88" width="12" height="170" rx="4" fill="#5a3b22" {ST} stroke-width="2"/>')
    g.append(f'<path d="M128,6 C142,30 146,56 140,82 L116,82 C110,56 114,30 128,6Z" fill="url(#bl)" {ST} stroke-width="2.2"/>')
    g.append(f'<path d="M128,12 V80" stroke="#ffffff" stroke-width="2" opacity="0.7"/>')
    g.append(f'<rect x="118" y="80" width="20" height="12" rx="3" fill="#3b424c" {ST} stroke-width="2"/>')
    g.append("".join(f'<path d="M{124 + k*2},92 q{-10 + k*4},18 {-14 + k*6},34" fill="none" stroke="{"#dc2626" if k % 2 else "#991b1b"}" stroke-width="4"/>' for k in range(5)))
    g.append(f'<path d="M134,104 L206,118 L188,140 L206,162 L134,166Z" fill="url(#fl)" {ST} stroke-width="2.2"/>')
    g.append(f'<text x="150" y="146" font-family="serif" font-weight="900" font-size="26" fill="#e0f2fe">神騎</text>')
    g.append("</g>")
    body += "".join(g) + sparkle(84, 40, 14, "#e0f2fe")
    return svg(body, d)


@icon
def era4_hwatong_cannon():
    # 화통도감 화포: 청동 총통 + 띠 + 심지 불꽃
    d = (lin("bz", 0, 96, 0, 160, [(0, "#f1c27d"), (0.35, "#b07d3f"), (0.75, "#6b4a22"), (1, "#3a2812")]))
    body = glow("#f97316", 104, 0.55)
    g = ['<g filter="url(#ol)" transform="rotate(-18 128 128)">']
    g.append(f'<rect x="20" y="118" width="70" height="20" rx="8" fill="#5a3b22" {ST} stroke-width="2"/>')
    g.append(f'<path d="M80,100 L206,104 L214,96 L222,96 L222,160 L214,160 L206,152 L80,156 C72,146 72,110 80,100Z" fill="url(#bz)" {ST} stroke-width="2.4"/>')
    for x in (98, 132, 170):
        g.append(f'<rect x="{x}" y="96" width="10" height="64" rx="3" fill="#8a6230" {ST} stroke-width="1.8"/>')
    g.append(f'<ellipse cx="222" cy="128" rx="6" ry="30" fill="#2a1d0e" {ST} stroke-width="2"/>')
    g.append(f'<path d="M86,106 L200,110" stroke="#ffe8b8" stroke-width="4" opacity="0.7"/>')
    g.append(f'<path d="M112,100 C108,84 116,74 110,62" fill="none" stroke="#3a2812" stroke-width="3"/>')
    g.append("</g>")
    body += "".join(g)
    body += (f'<circle cx="100" cy="64" r="16" fill="#fbbf24" filter="url(#blur6)" opacity="0.9"/>'
             + sparkle(100, 64, 16, "#fff7d1") + sparkle(122, 50, 8, "#fde68a", 0.9) + sparkle(84, 46, 6, "#fb923c", 0.9))
    return svg(body, d)


# ───────── 5시대 ─────────
@icon
def era5_bigyeok():
    # 비격진천뢰: 둥근 무쇠 포탄 + 대나무 심지통 + 불꽃
    d = (rad("ir", 104, 112, 120, [(0, "#9aa3ad", None), (0.45, "#4a5058", None), (1, "#15181c", None)]))
    body = glow("#eab308", 104, 0.5)
    g = ['<g filter="url(#ol)">']
    g.append(f'<circle cx="128" cy="146" r="78" fill="url(#ir)" {ST} stroke-width="2.6"/>')
    g.append(f'<path d="M50,146 C90,160 166,160 206,146" fill="none" stroke="#2a2e34" stroke-width="6"/>'
             f'<path d="M50,146 C90,160 166,160 206,146" fill="none" stroke="#6b7480" stroke-width="2"/>')
    for k in range(7):
        x = 64 + k * 21
        g.append(f'<circle cx="{x}" cy="{150 + (3 if 1 < k < 5 else 0)}" r="3.4" fill="#8a929c" {ST} stroke-width="1"/>')
    g.append(f'<ellipse cx="100" cy="112" rx="22" ry="14" fill="#e5e7eb" opacity="0.35" transform="rotate(-30 100 112)"/>')
    g.append(f'<rect x="116" y="58" width="24" height="18" rx="3" fill="#7c6a3a" {ST} stroke-width="2"/>'
             f'<rect x="120" y="36" width="16" height="24" rx="3" fill="#a3925a" {ST} stroke-width="2"/>'
             f'<path d="M124,44 H132 M124,52 H132" stroke="#5b4e2a" stroke-width="2"/>')
    g.append("</g>")
    body += "".join(g)
    body += (f'<circle cx="128" cy="30" r="14" fill="#facc15" filter="url(#blur6)" opacity="0.9"/>'
             + sparkle(128, 28, 17, "#fffbeb") + sparkle(150, 18, 7, "#fde68a", 0.9) + sparkle(108, 16, 6, "#fb923c", 0.9))
    return svg(body, d)


@icon
def era5_hwacha():
    # 행주대첩 화차: 바퀴 달린 나무 수레 + 신기전 발사 틀(구멍 격자) + 불화살
    d = lin("wd", 0, 70, 0, 170, [(0, "#a87447"), (0.5, "#6b4527"), (1, "#3a2414")])
    body = glow("#22d3ee", 104, 0.45)
    g = ['<g filter="url(#ol)">']
    g.append(f'<g transform="rotate(-14 128 120)"><rect x="58" y="62" width="140" height="92" rx="6" fill="url(#wd)" {ST} stroke-width="2.4"/>')
    for r in range(4):
        for c in range(7):
            g.append(f'<circle cx="{74 + c*18}" cy="{78 + r*20}" r="6.2" fill="#1a120b" stroke="#c8935e" stroke-width="1.4"/>')
    g.append("</g>")
    g.append(f'<path d="M60,170 L200,140" stroke="#4a3018" stroke-width="10"/><path d="M60,170 L200,140" stroke="#8a5a32" stroke-width="4"/>')
    for (x, y) in ((84, 186), (176, 166)):
        g.append(f'<circle cx="{x}" cy="{y}" r="28" fill="none" stroke="{INK}" stroke-width="12"/><circle cx="{x}" cy="{y}" r="28" fill="none" stroke="#8a5a32" stroke-width="7"/>'
                 + "".join(f'<path d="M{x},{y} L{x + 26*math.cos(a):.1f},{y + 26*math.sin(a):.1f}" stroke="#5a3b22" stroke-width="4"/>' for a in [k * math.pi / 4 for k in range(8)])
                 + f'<circle cx="{x}" cy="{y}" r="7" fill="#3b424c" {ST} stroke-width="2"/>')
    g.append("</g>")
    body += "".join(g)
    for k in range(4):
        x0, y0 = 160 + k * 10, 60 - k * 12
        body += (f'<path d="M{x0},{y0} L{x0 + 44},{y0 - 26}" stroke="#7dd3fc" stroke-width="3" stroke-linecap="round"/>'
                 f'<circle cx="{x0}" cy="{y0}" r="6" fill="#fb923c" filter="url(#blur2)"/>')
    body += sparkle(214, 26, 12, "#ecfeff")
    return svg(body, d)


# ───────── 6시대 ─────────
@icon
def era6_bongodong_rifle():
    # 봉오동 장총(볼트액션 소총 — 특정 상표 형태 아님): 나무 개머리 + 쇠 총열 + 총검꽂이
    d = (lin("wd", 0, 120, 0, 170, [(0, "#a46a3c"), (0.5, "#6e4424"), (1, "#3e2412")]) +
         lin("mt", 0, 100, 0, 122, [(0, "#b9c2cc"), (0.5, "#4b525c"), (1, "#1f2328")]))
    body = glow("#fde047", 104, 0.45)
    g = ['<g filter="url(#ol)" transform="rotate(-24 128 128)">']
    g.append(f'<path d="M14,128 L60,116 L190,118 L190,132 L84,136 L70,160 L22,170 C12,160 10,140 14,128Z" fill="url(#wd)" {ST} stroke-width="2.2"/>')
    g.append(f'<rect x="96" y="104" width="148" height="12" rx="3" fill="url(#mt)" {ST} stroke-width="2"/>')
    g.append(f'<rect x="96" y="114" width="98" height="8" rx="2" fill="#5a3b22" {ST} stroke-width="1.6"/>')
    g.append(f'<path d="M110,104 L112,92 L122,92 L124,104" fill="#4b525c" {ST} stroke-width="1.8"/>')
    g.append(f'<path d="M122,96 C132,90 138,94 136,100" fill="none" stroke="#2b3038" stroke-width="4"/>')
    g.append(f'<path d="M104,132 C104,146 118,148 120,136" fill="none" stroke="#2b3038" stroke-width="3"/>')
    g.append(f'<path d="M38,150 L72,142" stroke="#d9a066" stroke-width="2.4" opacity="0.6"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(226, 62, 14, "#fefce8") + sparkle(206, 42, 6, "#fde047", 0.9)
    return svg(body, d)


@icon
def era6_cheongsanri_saber():
    # 청산리 군도: 휜 군도 + 손잡이 + 태극 코등이
    d = (lin("bl", 90, 40, 170, 200, [(0, "#e8edf2"), (0.5, "#8a95a2"), (1, "#2a3038")]))
    body = glow("#ef4444", 100, 0.38) + glow("#3b82f6", 80, 0.3)
    g = ['<g filter="url(#ol)">']
    g.append(f'<path d="M206,24 C190,60 160,110 112,156 L100,146 C150,104 182,58 200,20Z" fill="url(#bl)" {ST} stroke-width="2.2"/>')
    g.append(f'<path d="M202,26 C186,62 156,108 108,150" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.75"/>')
    g.append(f'<circle cx="104" cy="152" r="17" fill="#f8fafc" {ST} stroke-width="2.2"/>')
    g.append(f'<path d="M87,152 A17,17 0 0 1 121,152 A8.5,8.5 0 0 1 104,152 A8.5,8.5 0 0 0 87,152Z" fill="#dc2626"/>'
             f'<path d="M87,152 A17,17 0 0 0 121,152 A8.5,8.5 0 0 1 104,152 A8.5,8.5 0 0 0 87,152Z" fill="#1d4ed8"/>')
    g.append(f'<path d="M96,160 L60,206 C56,212 62,218 68,214 L104,168Z" fill="#2a1d14" {ST} stroke-width="2"/>')
    g.append("".join(f'<path d="M{90 - k*7},{168 + k*9} l9,5" stroke="#c8a96e" stroke-width="2.4"/>' for k in range(4)))
    g.append(f'<path d="M66,210 C58,222 52,232 46,240" fill="none" stroke="#b91c1c" stroke-width="4"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(216, 30, 14, "#ffffff") + sparkle(180, 88, 7, "#93c5fd", 0.9) + sparkle(150, 118, 6, "#fca5a5", 0.9)
    return svg(body, d)


# ───────── 전설 성물(2~6시대 시작) ─────────
@icon
def legend2_cheonbuin():
    # 천부인: 청동 거울 · 청동 검 · 청동 방울(팔주령)
    d = (rad("mr", 100, 92, 70, [(0, "#fff3c4", None), (0.4, "#d6a54a", None), (1, "#5a3e14", None)]) +
         lin("bz", 0, 0, 20, 0, [(0, "#5a3e14"), (0.5, "#f1cf7a"), (1, "#5a3e14")]))
    body = glow("#fde047", 108, 0.5)
    g = ['<g filter="url(#ol)">']
    g.append(f'<circle cx="104" cy="96" r="58" fill="url(#mr)" {ST} stroke-width="2.4"/>')
    g.append("".join(f'<circle cx="104" cy="96" r="{r}" fill="none" stroke="#7c5a1a" stroke-width="1.4" opacity="0.8"/>' for r in (46, 38, 30, 14)))
    g.append("".join(f'<path d="M{104 + 30*math.cos(a):.1f},{96 + 30*math.sin(a):.1f} L{104 + 46*math.cos(a + 0.2):.1f},{96 + 46*math.sin(a + 0.2):.1f}" stroke="#7c5a1a" stroke-width="1.2"/>' for a in [k * math.pi / 8 for k in range(16)]))
    g.append(f'<rect x="96" y="90" width="16" height="11" rx="5" fill="#a8792c" {ST} stroke-width="1.6"/><path d="M100,95.5 H108" stroke="#5a3e14" stroke-width="2"/>')
    g.append(f'<g transform="rotate(30 186 130)"><path d="M186,40 C194,70 196,110 192,170 L180,170 C176,110 178,70 186,40Z" fill="url(#bz)" {ST} stroke-width="2"/>'
             f'<rect x="174" y="168" width="24" height="8" rx="2" fill="#7c5a1a" {ST} stroke-width="1.6"/><rect x="180" y="176" width="12" height="30" rx="3" fill="#5a3e14" {ST} stroke-width="1.6"/></g>')
    cx, cy = 92, 196
    g.append(f'<circle cx="{cx}" cy="{cy}" r="24" fill="#c9973f" {ST} stroke-width="2"/>')
    for k in range(8):
        a = k * math.pi / 4
        x, y = cx + 34 * math.cos(a), cy + 34 * math.sin(a)
        g.append(f'<path d="M{cx + 22*math.cos(a):.1f},{cy + 22*math.sin(a):.1f} L{x:.1f},{y:.1f}" stroke="#7c5a1a" stroke-width="4"/>'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#e0b257" {ST} stroke-width="1.8"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#7c5a1a"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(72, 64, 14, "#fffbeb")
    return svg(body, d)


@icon
def legend3_hyangno():
    # 백제 금동대향로(단순화): 봉황 · 산봉우리 뚜껑 · 연꽃 몸통 · 용 받침 + 향 연기
    d = (lin("gb", 80, 0, 176, 0, [(0, "#6b4b0e"), (0.4, "#f6d365"), (0.6, "#fff3c4"), (0.8, "#c7921c"), (1, "#5a3e0b")]))
    body = glow("#f59e0b", 108, 0.5)
    g = ['<g filter="url(#ol)">']
    # 받침(용 똬리)
    g.append(f'<path d="M86,232 C78,214 94,200 112,204 C120,190 140,190 148,204 C166,200 180,214 170,232Z" fill="url(#gb)" {ST} stroke-width="2.2"/>')
    g.append(f'<path d="M96,222 C108,212 124,226 136,214 C146,206 158,214 162,222" fill="none" stroke="#7c5a12" stroke-width="3"/>')
    # 몸통(연꽃)
    g.append(f'<path d="M78,150 C78,184 100,204 128,204 C156,204 178,184 178,150Z" fill="url(#gb)" {ST} stroke-width="2.4"/>')
    for k in range(5):
        x = 86 + k * 21
        g.append(f'<path d="M{x},152 C{x + 4},172 {x + 14},182 {x + 10},196 C{x + 2},184 {x - 4},170 {x},152Z" fill="#e8b43c" stroke="#7c5a12" stroke-width="1.4"/>')
    # 뚜껑(산봉우리)
    g.append(f'<path d="M74,150 C80,126 92,118 100,104 C104,112 110,110 114,98 C118,108 124,104 128,90 C132,104 138,108 142,98 C146,110 152,112 156,104 C164,118 176,126 182,150Z" fill="url(#gb)" {ST} stroke-width="2.4"/>')
    g.append(f'<path d="M92,132 C100,124 108,128 114,120 M134,122 C142,128 150,124 158,132" fill="none" stroke="#7c5a12" stroke-width="2.4"/>')
    # 봉황
    g.append(f'<path d="M128,90 C118,80 116,66 124,56 C130,48 142,50 146,58 C138,58 134,62 136,70 C150,62 166,64 172,74 C158,74 146,80 140,90Z" fill="url(#gb)" {ST} stroke-width="2.2"/>')
    g.append(f'<circle cx="132" cy="60" r="2.6" fill="{INK}"/>')
    g.append("</g>")
    # 향 연기
    for (x, k) in ((110, 0), (146, 1)):
        body += f'<path d="M{x},{100 - k*6} C{x - 14},{80} {x + 14},{64} {x - 4},{40 - k*8} C{x - 14},{28} {x + 6},{16} {x},{6}" fill="none" stroke="#fde68a" stroke-width="4" opacity="0.55" filter="url(#blur2)"/>'
    body += "".join(g) + sparkle(64, 120, 13, "#fffbeb") + sparkle(196, 168, 8, "#fde68a", 0.9)
    return svg(body, d)


@icon
def legend4_gwiju_flag():
    # 귀주 대첩의 깃발: 바람에 펄럭이는 붉은 군기 + 창날 깃대
    d = (lin("fl", 80, 40, 230, 150, [(0, "#ef4444"), (0.5, "#b91c1c"), (1, "#5f0f0f")]))
    body = glow("#f97316", 104, 0.45)
    g = ['<g filter="url(#ol)">']
    g.append(f'<rect x="64" y="40" width="10" height="210" rx="4" fill="#5a3b22" {ST} stroke-width="2"/>')
    g.append(f'<path d="M69,8 C76,20 78,30 74,42 L64,42 C60,30 62,20 69,8Z" fill="#cbd5e1" {ST} stroke-width="2"/>')
    g.append(f'<path d="M74,48 C110,40 140,62 176,50 C200,42 218,48 236,58 C224,74 222,92 232,110 C206,100 186,112 160,120 C128,130 104,112 74,120Z" fill="url(#fl)" {ST} stroke-width="2.4"/>')
    g.append(f'<path d="M74,120 C104,112 128,130 160,120 C186,112 206,100 232,110" fill="none" stroke="#fbbf24" stroke-width="4"/>')
    g.append(f'<circle cx="146" cy="84" r="22" fill="#fef3c7" {ST} stroke-width="2"/>')
    g.append(f'<text x="146" y="94" text-anchor="middle" font-family="serif" font-weight="900" font-size="28" fill="#7f1d1d">高</text>')
    g.append("".join(f'<path d="M{74 + k*6},126 q-4,14 0,26" fill="none" stroke="#fbbf24" stroke-width="3"/>' for k in range(3)))
    g.append("</g>")
    body += "".join(g) + sparkle(210, 30, 13, "#fff7ed") + sparkle(40, 120, 7, "#fdba74", 0.9)
    return svg(body, d)


@icon
def legend5_turtle_dragon():
    # 거북선 용머리: 나무 조각 용두(옆모습) + 입에서 뿜는 연기
    d = lin("wd", 60, 60, 190, 200, [(0, "#d97706"), (0.4, "#9a3412"), (1, "#431407")])
    body = glow("#f97316", 104, 0.45)
    # 연기(뒤)
    for (x, y, r) in ((196, 120, 26), (222, 96, 20), (214, 146, 18), (236, 124, 14)):
        body += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9ca3af" opacity="0.6" filter="url(#blur2)"/>'
    g = ['<g filter="url(#ol)">']
    g.append(f'<path d="M40,214 C40,170 60,140 86,120 C88,96 98,74 120,64 C136,56 152,60 162,72 C176,76 186,86 186,98 L174,104 C180,112 182,122 176,130 L150,128 C140,140 124,150 108,154 L104,214Z" fill="url(#wd)" {ST} stroke-width="2.6"/>')
    # 뿔 · 갈기
    g.append(f'<path d="M118,64 C112,44 116,30 128,22 C126,38 130,48 136,58Z" fill="#fbbf24" {ST} stroke-width="2"/>')
    g.append(f'<path d="M100,76 C86,62 70,60 58,66 C72,70 82,80 88,92Z" fill="#b45309" {ST} stroke-width="2"/>')
    g.append(f'<path d="M86,120 C70,128 60,142 56,160 M80,140 C66,150 60,166 60,184" fill="none" stroke="#fbbf24" stroke-width="4"/>')
    # 눈 · 이빨 · 콧수염
    g.append(f'<circle cx="148" cy="84" r="8" fill="#fef3c7" {ST} stroke-width="2"/><circle cx="150" cy="84" r="3.6" fill="{INK}"/>')
    g.append(f'<path d="M150,128 L156,120 L160,128 L166,120 L170,128" fill="#ffffff" {ST} stroke-width="1.4"/>')
    g.append(f'<path d="M174,104 L162,110 L170,114 L158,118" fill="none" stroke="#ffffff" stroke-width="2.2"/>')
    g.append(f'<path d="M184,98 C200,92 210,98 214,108" fill="none" stroke="#fbbf24" stroke-width="3"/>')
    # 비늘 무늬
    g.append("".join(f'<path d="M{70 + k*14},{190 - k*6} q7,-8 14,0" fill="none" stroke="#fde68a" stroke-width="2" opacity="0.7"/>' for k in range(5)))
    g.append("</g>")
    body += "".join(g)
    body += f'<path d="M178,112 C196,108 210,112 228,104" stroke="#fb923c" stroke-width="5" stroke-linecap="round" opacity="0.8" filter="url(#blur2)"/>'
    body += sparkle(60, 40, 12, "#fff7ed")
    return svg(body, d)


@icon
def legend6_seal():
    # 대한민국 임시 정부 태극 인장: 손잡이 달린 인장 + 태극 · 붉은 인주 자국
    d = (lin("gd", 60, 0, 196, 0, [(0, "#6b4b0e"), (0.35, "#e8c063"), (0.6, "#fff3c4"), (1, "#7c5a12")]))
    body = glow("#3b82f6", 104, 0.35) + glow("#ef4444", 70, 0.3)
    g = ['<g filter="url(#ol)">']
    # 인주 자국(아래)
    g.append(f'<rect x="58" y="184" width="140" height="44" rx="6" fill="#b91c1c" opacity="0.85" {ST} stroke-width="2"/>')
    g.append(f'<text x="128" y="215" text-anchor="middle" font-family="serif" font-weight="900" font-size="24" fill="#fee2e2">大韓民國</text>')
    # 인장 몸(사각) + 손잡이
    g.append(f'<path d="M74,128 L182,128 L190,176 L66,176Z" fill="url(#gd)" {ST} stroke-width="2.4"/>')
    g.append(f'<path d="M100,128 C96,104 104,86 128,82 C152,86 160,104 156,128Z" fill="url(#gd)" {ST} stroke-width="2.4"/>')
    g.append(f'<circle cx="128" cy="62" r="26" fill="#f8fafc" {ST} stroke-width="2.4"/>')
    g.append(f'<path d="M102,62 A26,26 0 0 1 154,62 A13,13 0 0 1 128,62 A13,13 0 0 0 102,62Z" fill="#dc2626"/>'
             f'<path d="M102,62 A26,26 0 0 0 154,62 A13,13 0 0 1 128,62 A13,13 0 0 0 102,62Z" fill="#1d4ed8"/>')
    g.append(f'<path d="M80,136 L176,136" stroke="#fff3c4" stroke-width="3" opacity="0.7"/>')
    g.append("</g>")
    body += "".join(g) + sparkle(176, 40, 13, "#ffffff") + sparkle(64, 92, 7, "#bfdbfe", 0.9)
    return svg(body, d)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in ICONS.items():
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(fn())
    print("icons", len(ICONS))


if __name__ == "__main__":
    main()
