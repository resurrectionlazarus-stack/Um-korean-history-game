#!/usr/bin/env python3
"""R25 기본 무기 아이콘(유물 각성 배너의 '이전 무기 → 새 유물' 변환용) — 1 · 3 · 5 · 6시대 (SVG 256×256).
2 · 4시대 기본 무기와 4시대 새 유물(검)은 무기 스프라이트에서 만든다(weapon_icons.py).  사용: python3 icons25.py OUT_DIR
"""
import os
import sys

INK = "#07080b"
ST = f'stroke="{INK}" stroke-linejoin="round" stroke-linecap="round"'
DEFS = f'''<filter id="ol" x="-20%" y="-20%" width="140%" height="140%"><feMorphology in="SourceAlpha" operator="dilate" radius="3.2" result="d"/><feFlood flood-color="{INK}" result="c"/><feComposite in="c" in2="d" operator="in" result="o"/><feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="b6" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>'''


def glow(col, a=0.5):
    return (f'<defs><radialGradient id="gl" cx="128" cy="128" r="104" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{col}" stop-opacity="{a}"/>'
            f'<stop offset="0.55" stop-color="{col}" stop-opacity="{a * 0.35}"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient></defs><circle cx="128" cy="128" r="104" fill="url(#gl)"/>')


def spark(x, y, s, col="#ffffff"):
    return (f'<path d="M{x},{y - s} Q{x + s * .16},{y - s * .16} {x + s},{y} Q{x + s * .16},{y + s * .16} {x},{y + s} '
            f'Q{x - s * .16},{y + s * .16} {x - s},{y} Q{x - s * .16},{y - s * .16} {x},{y - s}Z" fill="{col}"/>')


def doc(body, extra=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><defs>{DEFS}{extra}</defs>{body}</svg>'


def base_era1():
    # 석장리 타제 주먹도끼: 눈물방울 모양 + 떼어 낸 박리면
    g = '<linearGradient id="st" x1="60" y1="40" x2="190" y2="220" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#d6c7a8"/><stop offset="0.5" stop-color="#8b7a5c"/><stop offset="1" stop-color="#4a3f2e"/></linearGradient>'
    facets = ["128,24 150,70 128,96 106,66", "150,70 178,120 150,140 128,96", "106,66 80,118 108,138 128,96", "128,96 150,140 140,200 116,200 108,138",
              "178,120 170,180 140,200 150,140", "80,118 88,180 116,200 108,138"]
    b = glow("#fb923c", 0.45) + '<g filter="url(#ol)" transform="translate(128 130) scale(0.82) rotate(-24) translate(-128 -128)">'
    b += f'<path d="M128,22 C160,60 186,110 178,160 C172,200 150,226 128,228 C106,226 84,200 78,160 C70,110 96,60 128,22Z" fill="url(#st)" {ST} stroke-width="2.6"/>'
    b += "".join(f'<polygon points="{p}" fill="#fff7e6" opacity="{0.08 + (i % 3) * 0.07}" stroke="#3b2f22" stroke-opacity="0.6" stroke-width="1.4"/>' for i, p in enumerate(facets))
    b += '</g>' + spark(176, 56, 13, "#fff7ed")
    return doc(b, g)


def base_era3():
    # 신라 환두대도: 곧은 외날 + 금빛 고리 자루
    g = ('<linearGradient id="bl" x1="0" y1="-12" x2="0" y2="12" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#f1f5f9"/><stop offset="0.5" stop-color="#94a3b8"/><stop offset="1" stop-color="#334155"/></linearGradient>'
         '<linearGradient id="au" x1="0" y1="-20" x2="0" y2="20" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff3c4"/><stop offset="0.5" stop-color="#e0a526"/><stop offset="1" stop-color="#7a4a0e"/></linearGradient>')
    b = glow("#f43f5e", 0.4) + '<g filter="url(#ol)" transform="translate(128 128) rotate(-40)">'
    b += f'<path d="M-40,-9 L104,-7 L118,0 L104,8 L-40,9Z" fill="url(#bl)" {ST} stroke-width="2.2"/><path d="M-36,-4 L106,-3" stroke="#fff" stroke-width="1.6" opacity="0.8"/>'
    b += f'<rect x="-50" y="-13" width="10" height="26" rx="3" fill="url(#au)" {ST} stroke-width="2"/><rect x="-92" y="-7" width="42" height="14" rx="4" fill="#7f1d1d" {ST} stroke-width="2"/>'
    b += f'<circle cx="-106" cy="0" r="15" fill="none" stroke="{INK}" stroke-width="11"/><circle cx="-106" cy="0" r="15" fill="none" stroke="url(#au)" stroke-width="7"/>'
    b += f'<path d="M-112,-4 q6,-6 12,0 q-6,8 -12,0Z" fill="#e0a526" {ST} stroke-width="1.2"/></g>'
    b += spark(196, 52, 13)
    return doc(b, g)


def base_era5():
    # 사인참사검: 칼날에 금으로 새긴 별자리(북두칠성) + 검붉은 자루
    g = ('<linearGradient id="bl" x1="0" y1="-12" x2="0" y2="12" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#f8fafc"/><stop offset="0.5" stop-color="#9aa5b3"/><stop offset="1" stop-color="#2a3038"/></linearGradient>')
    stars = [(-20, -1), (0, 2), (18, -2), (34, 1), (52, -3), (66, 2), (84, 0)]
    b = glow("#22d3ee", 0.4) + '<g filter="url(#ol)" transform="translate(128 128) rotate(-40)">'
    b += f'<path d="M-44,-9 L108,-8 L124,0 L108,8 L-44,9Z" fill="url(#bl)" {ST} stroke-width="2.2"/>'
    b += "".join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#facc15"/>' for x, y in stars) + '<path d="M-20,-1 L0,2 L18,-2 L34,1 L52,-3 L66,2 L84,0" fill="none" stroke="#facc15" stroke-width="1" opacity="0.8"/>'
    b += f'<path d="M-56,-16 L-44,-16 L-44,16 L-56,16Z" fill="#b45309" {ST} stroke-width="2"/><rect x="-98" y="-7" width="42" height="14" rx="4" fill="#1f0f0f" {ST} stroke-width="2"/>'
    b += "".join(f'<path d="M{-94 + k * 8},-7 l4,14" stroke="#dc2626" stroke-width="2.4"/>' for k in range(5))
    b += f'<circle cx="-104" cy="0" r="8" fill="#b45309" {ST} stroke-width="2"/></g>' + spark(200, 52, 13, "#ecfeff")
    return doc(b, g)


def base_era6():
    # 태극 광선검: 빛 칼날 + 태극 코등이
    g = ('<linearGradient id="lz" x1="0" y1="-14" x2="0" y2="14" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#e0f2fe" stop-opacity="0"/><stop offset="0.3" stop-color="#7dd3fc"/><stop offset="0.5" stop-color="#ffffff"/><stop offset="0.7" stop-color="#7dd3fc"/><stop offset="1" stop-color="#e0f2fe" stop-opacity="0"/></linearGradient>')
    b = glow("#38bdf8", 0.5) + '<g transform="translate(128 128) rotate(-40)">'
    b += '<rect x="-34" y="-16" width="158" height="32" rx="16" fill="#38bdf8" opacity="0.45" filter="url(#b6)"/><rect x="-34" y="-9" width="154" height="18" rx="9" fill="url(#lz)"/>'
    b += f'<g filter="url(#ol)"><circle cx="-44" cy="0" r="16" fill="#f8fafc" {ST} stroke-width="2"/>'
    b += '<path d="M-60,0 A16,16 0 0 1 -28,0 A8,8 0 0 1 -44,0 A8,8 0 0 0 -60,0Z" fill="#dc2626"/><path d="M-60,0 A16,16 0 0 0 -28,0 A8,8 0 0 1 -44,0 A8,8 0 0 0 -60,0Z" fill="#1d4ed8"/>'
    b += f'<rect x="-104" y="-8" width="46" height="16" rx="5" fill="#1f2937" {ST} stroke-width="2"/>' + "".join(f'<path d="M{-100 + k * 8},-8 l4,16" stroke="#94a3b8" stroke-width="2"/>' for k in range(5)) + '</g></g>'
    b += spark(206, 52, 14, "#ffffff")
    return doc(b, g)


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, fn in (("base_era1", base_era1), ("base_era3", base_era3), ("base_era5", base_era5), ("base_era6", base_era6)):
        with open(os.path.join(out, name + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(fn())
    print("base icons 4")


if __name__ == "__main__":
    main()
