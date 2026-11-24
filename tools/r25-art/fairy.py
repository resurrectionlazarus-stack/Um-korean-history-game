#!/usr/bin/env python3
"""R25 동료 '꼬마 선녀 단비' — 신시(神市)에서 내려와 시공의 수호자를 돕는 작은 선녀(요정) 3장(256×256, 오른쪽 보기).
idle(날개 위) · idle2(날개 아래 — 날갯짓) · cast(꽃방울 지팡이를 들어 주술).  사용: python3 fairy.py OUT_DIR
"""
import math
import os
import sys

INK = "#2a1630"
ST = f'stroke="{INK}" stroke-linejoin="round" stroke-linecap="round"'


def wings(up):
    a = -32 if up else 6
    out = []
    for (cx, cy, rx, ry, rot, op) in ((96, 112, 56, 30, a - 20, 0.75), (98, 132, 40, 20, a + 28, 0.7)):
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx + rx * 0.7} {cy})" fill="url(#wing)" opacity="{op}" stroke="#a5f3fc" stroke-width="2"/>')
        out.append(f'<path d="M{cx + rx * 0.7},{cy} Q{cx},{cy - 6} {cx - rx * 0.6},{cy - 2}" transform="rotate({rot} {cx + rx * 0.7} {cy})" fill="none" stroke="#ffffff" stroke-width="1.4" opacity="0.8"/>')
    return "".join(out)


def body(pose):
    wand_up = pose == "cast"
    o = []
    # 치마(분홍 · 흰 겹치마) — 아래로 퍼지며 흔들림
    sway = {"idle": 0, "idle2": 4, "cast": -3}[pose]
    o.append(f'<path d="M108,150 C96,170 90,196 86,{214 + sway} C104,{222 + sway} 132,{224 - sway} 150,{214 - sway} C146,196 140,170 132,150Z" fill="url(#skirt)" {ST} stroke-width="2.4"/>')
    o.append(f'<path d="M98,190 C112,196 128,196 144,190" fill="none" stroke="#f9a8d4" stroke-width="2"/>')
    o.append(f'<path d="M90,{210 + sway} C108,{218 + sway} 128,{219 - sway} 148,{210 - sway}" fill="none" stroke="#fde68a" stroke-width="3"/>')
    # 노리개(옥 장식)
    o.append(f'<path d="M122,154 L124,176" stroke="#dc2626" stroke-width="2"/><circle cx="124" cy="180" r="5" fill="#34d399" {ST} stroke-width="1.6"/>'
             f'<path d="M121,185 l-2,10 M124,186 v11 M127,185 l2,10" stroke="#dc2626" stroke-width="1.6"/>')
    # 저고리(흰 몸판 + 붉은 고름)
    o.append(f'<path d="M104,118 C100,132 102,146 108,154 L134,154 C140,146 142,132 136,118 C128,112 112,112 104,118Z" fill="#fff7ed" {ST} stroke-width="2.4"/>'
             f'<path d="M110,120 L124,138 L136,120" fill="none" stroke="#f472b6" stroke-width="2.4"/>'
             f'<path d="M124,138 C118,146 116,152 112,158 M124,138 C130,148 132,152 134,160" fill="none" stroke="#dc2626" stroke-width="3"/>')
    # 색동 소매 팔(뒤 팔 · 앞 팔)
    def sleeve(x0, y0, x1, y1, w):
        L = math.hypot(x1 - x0, y1 - y0)
        a = math.degrees(math.atan2(y1 - y0, x1 - x0))
        stripes = "".join(f'<rect x="{6 + k * (L - 10) / 5:.1f}" y="{-w / 2:.1f}" width="{(L - 10) / 5 + 0.6:.1f}" height="{w:.1f}" fill="{c}"/>' for k, c in enumerate(["#ef4444", "#facc15", "#22c55e", "#3b82f6", "#ec4899"]))
        return (f'<g transform="translate({x0},{y0}) rotate({a:.1f})"><clipPath id="cp{x0}{y0}"><rect x="0" y="{-w / 2}" width="{L}" height="{w}" rx="{w / 2}"/></clipPath>'
                f'<g clip-path="url(#cp{x0}{y0})">{stripes}</g><rect x="0" y="{-w / 2}" width="{L}" height="{w}" rx="{w / 2}" fill="none" {ST} stroke-width="2.2"/>'
                f'<circle cx="{L + 3}" cy="0" r="6" fill="#ffe4d1" {ST} stroke-width="2"/></g>')
    o.append(sleeve(108, 124, 92, 152, 13))
    if wand_up:
        o.append(sleeve(132, 122, 160, 96, 13))
        hand = (166, 92)
    else:
        o.append(sleeve(132, 124, 156, 146, 13))
        hand = (162, 150)
    # 꽃방울 지팡이(복숭아꽃 + 방울)
    tip = (hand[0] + 16, hand[1] - 44) if wand_up else (hand[0] + 22, hand[1] - 30)
    o.append(f'<path d="M{hand[0]},{hand[1] + 6} L{tip[0]},{tip[1]}" stroke="#92400e" stroke-width="4" stroke-linecap="round"/>')
    for k in range(5):
        a = math.radians(k * 72 - 90)
        px, py = tip[0] + math.cos(a) * 7, tip[1] + math.sin(a) * 7
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" fill="#fbcfe8" {ST} stroke-width="1.4"/>')
    o.append(f'<circle cx="{tip[0]}" cy="{tip[1]}" r="3.6" fill="#fde047" {ST} stroke-width="1.2"/>')
    o.append(f'<circle cx="{tip[0] - 4}" cy="{tip[1] + 14}" r="4" fill="#fcd34d" {ST} stroke-width="1.2"/>')
    if wand_up:
        o.append(f'<circle cx="{tip[0]}" cy="{tip[1]}" r="22" fill="url(#spark)"/>')
        for k in range(6):
            a = math.radians(k * 60 + 15)
            x, y = tip[0] + math.cos(a) * 30, tip[1] + math.sin(a) * 30
            o.append(f'<path d="M{x:.1f},{y - 6:.1f} L{x + 1.6:.1f},{y - 1.6:.1f} L{x + 6:.1f},{y:.1f} L{x + 1.6:.1f},{y + 1.6:.1f} L{x:.1f},{y + 6:.1f} L{x - 1.6:.1f},{y + 1.6:.1f} L{x - 6:.1f},{y:.1f} L{x - 1.6:.1f},{y - 1.6:.1f}Z" fill="#fef9c3"/>')
    # 머리(크게 · 귀엽게): 뒷머리 → 얼굴 → 앞머리 · 쌍상투 · 댕기
    o.append(f'<ellipse cx="116" cy="84" rx="40" ry="38" fill="#1f1530" {ST} stroke-width="2.4"/>')
    for (cx, cy) in ((90, 48), (134, 44)):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="15" fill="#1f1530" {ST} stroke-width="2.2"/><path d="M{cx - 8},{cy - 6} q8,-6 16,0" fill="none" stroke="#6d5a8a" stroke-width="2"/>')
    # 댕기: 상투 아래 붉은 나비매듭 + 뒤로 늘어진 리본
    for (bx, by, tail) in ((86, 60, -1), (142, 56, 1)):
        o.append(f'<path d="M{bx},{by} l-9,-6 l0,12Z M{bx},{by} l9,-6 l0,12Z" fill="#ef4444" {ST} stroke-width="1.6"/><circle cx="{bx}" cy="{by}" r="3" fill="#b91c1c"/>'
                 f'<path d="M{bx - 2},{by + 4} q{-6 + tail * 2},14 {-10 + tail * 4},28 M{bx + 2},{by + 4} q{-2 + tail * 4},16 {-2 + tail * 6},30" fill="none" stroke="#dc2626" stroke-width="3.4" stroke-linecap="round"/>')
    o.append(f'<path d="M84,86 C84,64 100,54 120,54 C140,54 154,66 154,86 C154,106 140,120 120,120 C100,120 84,108 84,86Z" fill="url(#skin)" {ST} stroke-width="2.4"/>')
    o.append(f'<path d="M84,84 C86,62 104,50 124,52 C142,54 156,66 154,84 C146,72 134,66 122,70 C112,64 96,70 84,84Z" fill="#1f1530" {ST} stroke-width="2"/>'
             f'<path d="M100,64 q10,-6 20,0 M126,62 q10,-4 18,4" fill="none" stroke="#6d5a8a" stroke-width="2"/>')
    # 눈 · 볼 · 입 (오른쪽 보기 3/4)
    blink = pose == "idle2"
    for (ex, s) in ((122, 1.0), (142, 0.86)):
        if blink:
            o.append(f'<path d="M{ex - 6 * s},{90} q{6 * s},5 {12 * s},0" fill="none" stroke="{INK}" stroke-width="2.6"/>')
        else:
            o.append(f'<ellipse cx="{ex}" cy="90" rx="{6 * s:.1f}" ry="8" fill="{INK}"/><circle cx="{ex + 2 * s:.1f}" cy="87" r="2.4" fill="#fff"/><circle cx="{ex - 2 * s:.1f}" cy="93" r="1.2" fill="#fff"/>')
    o.append(f'<ellipse cx="112" cy="102" rx="7" ry="4" fill="#fb7185" opacity="0.55"/><ellipse cx="148" cy="101" rx="5" ry="3.4" fill="#fb7185" opacity="0.5"/>'
             f'<path d="M128,106 q5,5 10,0" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    return "".join(o)


def doc(pose):
    defs = '''<radialGradient id="wing" cx="0.5" cy="0.5" r="0.6"><stop offset="0" stop-color="#ffffff" stop-opacity="0.95"/><stop offset="0.55" stop-color="#a5f3fc" stop-opacity="0.7"/><stop offset="1" stop-color="#f0abfc" stop-opacity="0.55"/></radialGradient>
<linearGradient id="skirt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fdf2f8"/><stop offset="0.6" stop-color="#fbcfe8"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
<radialGradient id="skin" cx="0.55" cy="0.45" r="0.6"><stop offset="0" stop-color="#fff1e6"/><stop offset="1" stop-color="#ffd6bd"/></radialGradient>
<radialGradient id="spark" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fffbeb" stop-opacity="0.95"/><stop offset="1" stop-color="#fde047" stop-opacity="0"/></radialGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fef9c3" stop-opacity="0.55"/><stop offset="1" stop-color="#fef9c3" stop-opacity="0"/></radialGradient>'''
    up = pose != "idle2"
    body_svg = f'<circle cx="122" cy="130" r="100" fill="url(#halo)"/>' + wings(up) + body(pose)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><defs>{defs}</defs>{body_svg}</svg>'


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for p in ("idle", "idle2", "cast"):
        with open(os.path.join(out, p + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(doc(p))
    print("fairy 3")


if __name__ == "__main__":
    main()
