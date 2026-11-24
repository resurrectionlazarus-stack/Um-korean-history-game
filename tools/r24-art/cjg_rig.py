#!/usr/bin/env python3
"""R24 4시대 주인공 고려 무신 척준경 — 코드 리그(SVG) 원화 생성기.

참고 이미지(고려 장수 분위기: 투구 없이 상투관 · 길게 늘어뜨린 흑발 · 흑철 어린갑 · 호심경 · 흑색 전포 ·
피 묻은 결사대 무신)를 '의상 · 분위기' 레퍼런스로만 쓰고, 얼굴은 특정 실존 인물을 닮지 않은 독자 디자인.
무기는 R19 투자자 확정안(창 + 화통도감 화포)을 그대로 유지한다.

512x512 · 오른쪽 보기 · 접지선 y=470(신발 바닥 469) — assets/hero/era4_hero_{pose}.png 규격.
사용법: python3 cjg_rig.py OUT_DIR  → OUT_DIR/{pose}.svg + rig.json(창 궤적 등 좌표)
"""
import json
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
GROUND = 470
ANKLE_H = 15

THIGH, SHIN = 95, 89
UARM, FARM = 70, 64
T_NECK = (8, -146)
T_SH_NEAR = (-26, -134)
T_SH_FAR = (40, -135)
T_HIP_NEAR = (-11, -4)
T_HIP_FAR = (13, -6)

C = dict(
    arm_l="#69727e", arm_m="#3b424c", arm_d="#16191e",
    st_l="#b3bdc8", st_m="#626c78", st_d="#1c2026",
    cl_l="#3a3d45", cl_m="#1d1f25", cl_d="#0b0c0f",
    le_l="#4f3d30", le_m="#2f241c", le_d="#120d0a",
    br_l="#d8b878", br_m="#9a7a44", br_d="#4d3a1c",
    red_l="#c8352a", red_m="#8f1d16", red_d="#4a0d0a",
    sk_l="#e2b18f", sk_m="#bf8865", sk_d="#7b4f3a",
    ha_l="#4a5363", ha_m="#15171c", ha_d="#060608",
    bl_d="#6b0c0c", bl_l="#b8231b",
    wd_l="#7a573a", wd_m="#4b3323", wd_d="#22170f",
    bz_l="#d6a55f", bz_m="#8f6634", bz_d="#45301a",
    ink="#07080b",
)


def f(v):
    return f"{v:.1f}"


def pt(p):
    return f"{p[0]:.1f},{p[1]:.1f}"


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def rot(p, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def ang(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def polar(p, deg, L):
    r = math.radians(deg)
    return (p[0] + L * math.cos(r), p[1] + L * math.sin(r))


def lerp(a, b, t):
    return a + (b - a) * t


def ik2(root, target, L1, L2, prefer):
    """2관절 IK. prefer(elbow) → 두 해 중 점수가 큰 쪽."""
    d = dist(root, target)
    d = max(abs(L1 - L2) + 0.5, min(L1 + L2 - 0.5, d))
    a = math.atan2(target[1] - root[1], target[0] - root[0])
    cosA = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
    A = math.acos(max(-1.0, min(1.0, cosA)))
    best = None
    for sgn in (1, -1):
        a1 = a + sgn * A
        mid = (root[0] + L1 * math.cos(a1), root[1] + L1 * math.sin(a1))
        end = (root[0] + d * math.cos(a), root[1] + d * math.sin(a))
        sc = prefer(mid)
        if best is None or sc > best[0]:
            best = (sc, mid, end)
    return best[1], best[2]


class SVG:
    def __init__(self):
        self.defs = []
        self.uid = 0

    def gid(self, pre):
        self.uid += 1
        return f"{pre}{self.uid}"

    def lin(self, p0, p1, stops):
        i = self.gid("g")
        st = "".join(f'<stop offset="{o}" stop-color="{c}"{"" if a is None else f" stop-opacity={chr(34)}{a}{chr(34)}"}/>' for o, c, a in stops)
        self.defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{f(p0[0])}" y1="{f(p0[1])}" x2="{f(p1[0])}" y2="{f(p1[1])}">{st}</linearGradient>')
        return f"url(#{i})"

    def rad(self, c, r, stops, fx=None):
        i = self.gid("r")
        st = "".join(f'<stop offset="{o}" stop-color="{col}"{"" if a is None else f" stop-opacity={chr(34)}{a}{chr(34)}"}/>' for o, col, a in stops)
        fxs = f' fx="{f(fx[0])}" fy="{f(fx[1])}"' if fx else ""
        self.defs.append(f'<radialGradient id="{i}" gradientUnits="userSpaceOnUse" cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}"{fxs}>{st}</radialGradient>')
        return f"url(#{i})"


def S3(l, m, d):
    return [(0, d, None), (0.5, m, None), (0.82, l, None), (1, m, None)]


def g_open(o, deg=0.0, sx=1.0, sy=1.0):
    t = f"translate({f(o[0])},{f(o[1])})"
    if abs(deg) > 1e-4:
        t += f" rotate({f(deg)})"
    if sx != 1 or sy != 1:
        t += f" scale({sx:.3f},{sy:.3f})"
    return f'<g transform="{t}">'


def limb_d(L, w0, w1, bulge=0.0, bpos=0.42):
    h0, h1 = w0 / 2, w1 / 2
    by = L * bpos
    bx = h0 + (h1 - h0) * bpos + bulge
    k0, k1 = h0 * 1.25, h1 * 1.25
    return (f"M{f(-h0)},0 Q{f(-bx)},{f(by)} {f(-h1)},{f(L)} C{f(-h1)},{f(L + k1)} {f(h1)},{f(L + k1)} {f(h1)},{f(L)} "
            f"Q{f(bx)},{f(by)} {f(h0)},0 C{f(h0)},{f(-k0)} {f(-h0)},{f(-k0)} {f(-h0)},0Z")


def seg_group(p0, p1):
    a = ang(p0, p1)
    return g_open(p0, a - 90), dist(p0, p1)


DEFS_STATIC = f'''
<pattern id="scale" width="12" height="10" patternUnits="userSpaceOnUse">
 <path d="M0,0 A6,6.5 0 0 0 12,0 M-6,5 A6,6.5 0 0 0 6,5 M6,5 A6,6.5 0 0 0 18,5" fill="none" stroke="{C['ink']}" stroke-width="1.15" stroke-opacity="0.9"/>
 <path d="M2.2,1.4 Q6,5.8 9.8,1.4 M-3.8,6.4 Q0,10.8 3.8,6.4 M8.2,6.4 Q12,10.8 15.8,6.4" fill="none" stroke="#c3ccd6" stroke-width="0.8" stroke-opacity="0.42"/>
</pattern>
<pattern id="lam" width="8" height="17" patternUnits="userSpaceOnUse">
 <rect x="0.6" y="0.6" width="6.8" height="15.8" rx="2.4" fill="none" stroke="{C['ink']}" stroke-width="1" stroke-opacity="0.85"/>
 <path d="M2.1,2.6 V13.6" stroke="#c7cfd8" stroke-width="0.8" stroke-opacity="0.35"/>
 <circle cx="4" cy="3.4" r="0.95" fill="{C['red_l']}"/><circle cx="4" cy="13.4" r="0.95" fill="{C['red_m']}"/>
</pattern>
<pattern id="weave" width="6" height="6" patternUnits="userSpaceOnUse">
 <path d="M0,6 L6,0" stroke="#000" stroke-width="0.7" stroke-opacity="0.25"/>
</pattern>
<filter id="ol" x="-15%" y="-15%" width="130%" height="130%">
 <feMorphology in="SourceAlpha" operator="dilate" radius="2.3" result="d"/>
 <feFlood flood-color="{C['ink']}" result="c"/>
 <feComposite in="c" in2="d" operator="in" result="o"/>
 <feOffset in="SourceAlpha" dx="3" dy="1.5" result="off"/>
 <feComposite in="SourceAlpha" in2="off" operator="out" result="edge"/>
 <feGaussianBlur in="edge" stdDeviation="0.6" result="edgeb"/>
 <feFlood flood-color="#a9bdd8" flood-opacity="0.55" result="rc"/>
 <feComposite in="rc" in2="edgeb" operator="in" result="rim"/>
 <feComposite in="rim" in2="SourceAlpha" operator="in" result="rim2"/>
 <feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/><feMergeNode in="rim2"/></feMerge>
</filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="soft2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
'''

STROKE = f'stroke="{C["ink"]}" stroke-linejoin="round" stroke-linecap="round"'


class Rig:
    def __init__(self, P):
        self.P = P
        self.s = SVG()
        self.info = {}
        pel = P["pelvis"]
        lean = P.get("lean", 0)
        self.pel, self.lean = pel, lean
        W = lambda q: add(pel, rot(q, lean))
        self.W = W
        self.neck = W(T_NECK)
        self.sh_n, self.sh_f = W(T_SH_NEAR), W(T_SH_FAR)
        self.hip_n, self.hip_f = W(T_HIP_NEAR), W(T_HIP_FAR)
        self.head_o = add(self.neck, rot((5, -15), lean + P.get("neck", 0)))
        self.head_deg = lean + P.get("neck", 0) + P.get("head", 0)
        # 다리: 무릎은 앞(+x)으로
        fwd = lambda m: m[0]
        self.kn_n, self.an_n = ik2(self.hip_n, P["ank_n"], THIGH, SHIN, P.get("knee_n_pref", fwd))
        self.kn_f, self.an_f = ik2(self.hip_f, P["ank_f"], THIGH, SHIN, P.get("knee_f_pref", fwd))
        # 무기
        self.spear = P.get("spear")
        self.cannon = P.get("cannon", "hip")
        hn, hf = P.get("hand_n"), P.get("hand_f")
        if self.spear and self.spear.get("mode", "hands") == "hands":
            sp = self.spear
            hn = hn or sp["grip"]
            hf = hf or polar(sp["grip"], sp["ang"], sp["t_far"])
        if self.cannon == "hands":
            cn = P["cannon_line"]
            hn = hn or cn["grip"]
            hf = hf or polar(cn["grip"], cn["ang"], cn["t_far"])
        low = lambda m: m[1] + P.get("elbow_back", 0.35) * (-m[0])
        self.el_n, self.ha_n = ik2(self.sh_n, hn, UARM, FARM, P.get("elbow_n_pref", low))
        self.el_f, self.ha_f = ik2(self.sh_f, hf, UARM, FARM, P.get("elbow_f_pref", low))

    # ---------- 부위 ----------
    def leg(self, hip, kn, an, foot_deg, near):
        s = self.s
        o = []
        dark = 0.0 if near else 0.22
        # 허벅지(흑색 바지)
        g0, L = seg_group(hip, kn)
        fill = s.lin((-14, 0), (14, 0), S3(C["cl_l"], C["cl_m"], C["cl_d"]))
        o.append(g0 + f'<path d="{limb_d(L + 6, 37, 27, 3)}" fill="{fill}" {STROKE} stroke-width="1.6"/>'
                 f'<path d="M-6,{f(L*0.25)} q4,10 1,22 M5,{f(L*0.45)} q-3,9 0,18" fill="none" stroke="#000" stroke-opacity="0.45" stroke-width="1.4"/></g>')
        # 정강이 + 경갑(정강이 판)
        g1, L2 = seg_group(kn, an)
        fill2 = s.lin((-12, 0), (12, 0), S3(C["cl_l"], C["cl_m"], C["cl_d"]))
        st = s.lin((-11, 0), (11, 0), [(0, C["st_d"], None), (0.55, C["st_m"], None), (0.8, C["st_l"], None), (1, C["st_m"], None)])
        o.append(g1 + f'<path d="{limb_d(L2, 27, 20, 1.5)}" fill="{fill2}" {STROKE} stroke-width="1.6"/>'
                 # 무릎 보호대
                 f'<path d="M-12,-8 C-12,-20 12,-20 12,-8 L11,6 C4,10 -4,10 -11,6Z" fill="{st}" {STROKE} stroke-width="1.6"/>'
                 f'<circle cx="0" cy="-2" r="2.2" fill="{C["br_l"]}" {STROKE} stroke-width="0.8"/>'
                 # 정강이 판
                 f'<path d="M-10,{f(L2*0.28)} L10,{f(L2*0.26)} L9,{f(L2*0.92)} L-9,{f(L2*0.92)}Z" fill="{st}" {STROKE} stroke-width="1.5"/>'
                 f'<path d="M-6,{f(L2*0.33)} V{f(L2*0.86)}" stroke="#e4ebf2" stroke-opacity="0.5" stroke-width="1.4"/>'
                 f'<path d="M-10,{f(L2*0.5)} H10 M-9.5,{f(L2*0.7)} H9.5" stroke="{C["ink"]}" stroke-width="1"/>'
                 '</g>')
        # 신발(화) — 발목 기준, foot_deg 0 = 발바닥 수평
        boot = s.lin((0, -16), (0, 16), [(0, C["le_l"], None), (0.55, C["le_m"], None), (1, C["le_d"], None)])
        o.append(g_open(an, foot_deg) +
                 f'<path d="M-11,-16 L-12,8 C-12,13 -9,15 -4,15 L30,15 C35,15 37,11 33,7 C27,1 18,-2 12,-6 L10,-16Z" fill="{boot}" {STROKE} stroke-width="1.7"/>'
                 f'<path d="M-12,12 H33" stroke="{C["ink"]}" stroke-width="2.6"/>'
                 f'<path d="M-9,-11 H9" stroke="{C["br_m"]}" stroke-width="2"/>'
                 f'<path d="M14,-3 C20,0 27,4 31,9" fill="none" stroke="#a48468" stroke-opacity="0.45" stroke-width="1.3"/>'
                 '</g>')
        if dark:
            return f'<g opacity="1"><g>{"".join(o)}</g><g opacity="{dark}">' + "".join(o).replace('fill="url(', 'fill="#000" data-x="(') + '</g></g>'
        return "".join(o)

    def tasset(self, hip, kn, near):
        s = self.s
        a = ang(hip, kn)
        base = s.lin((-16, 0), (16, 0), [(0, C["arm_d"], None), (0.55, C["arm_m"], None), (0.85, C["arm_l"], None), (1, C["arm_m"], None)])
        sh = 0.0 if near else 0.3
        d = "M-17,-10 L17,-10 L21,52 C8,58 -8,58 -21,52Z"
        g = g_open(hip, a - 90)
        out = (g + f'<path d="{d}" fill="{base}" {STROKE} stroke-width="1.6"/>'
               f'<path d="{d}" fill="url(#lam)"/>'
               f'<path d="M-21,52 C-8,58 8,58 21,52" fill="none" stroke="{C["red_m"]}" stroke-width="2.4"/>'
               + (f'<path d="{d}" fill="#000" opacity="{sh}"/>' if sh else "") + '</g>')
        return out

    def arm(self, sh, el, ha, near, pauldron=True, grip=True, fist_deg=None):
        s = self.s
        o = []
        g0, L = seg_group(sh, el)
        sl = s.lin((-14, 0), (14, 0), S3(C["cl_l"], C["cl_m"], C["cl_d"]))
        o.append(g0 + f'<path d="{limb_d(L + 4, 32, 25, 3)}" fill="{sl}" {STROKE} stroke-width="1.6"/>'
                 f'<path d="M-5,{f(L*0.3)} q5,8 2,18" fill="none" stroke="#000" stroke-opacity="0.5" stroke-width="1.3"/></g>')
        g1, L2 = seg_group(el, ha)
        sl2 = s.lin((-12, 0), (12, 0), S3(C["cl_l"], C["cl_m"], C["cl_d"]))
        bra = s.lin((-11, 0), (11, 0), [(0, C["le_d"], None), (0.5, C["le_m"], None), (0.82, C["le_l"], None), (1, C["le_m"], None)])
        o.append(g1 + f'<path d="{limb_d(L2, 25, 19, 1.5)}" fill="{sl2}" {STROKE} stroke-width="1.6"/>'
                 # 완갑(팔뚝 가죽 + 쇠 띠)
                 f'<path d="M-11,{f(L2*0.34)} L11,{f(L2*0.32)} L9.5,{f(L2*0.96)} L-9.5,{f(L2*0.96)}Z" fill="{bra}" {STROKE} stroke-width="1.5"/>'
                 f'<path d="M-10.5,{f(L2*0.5)} H10.5 M-10,{f(L2*0.72)} H10" stroke="{C["st_m"]}" stroke-width="2.2"/>'
                 + "".join(f'<circle cx="{x}" cy="{f(L2*0.61)}" r="1.5" fill="{C["br_l"]}"/>' for x in (-6, 0, 6)) +
                 '</g>')
        # 손(주먹)
        a = ang(el, ha) if fist_deg is None else fist_deg
        sk = s.lin((-9, 0), (9, 0), [(0, C["sk_d"], None), (0.6, C["sk_m"], None), (1, C["sk_l"], None)])
        o.append(g_open(ha, a - 90) +
                 f'<path d="M-9,-2 C-11,6 -9,15 -2,17 C5,18 10,13 10,5 C10,-1 7,-4 0,-4 C-4,-4 -8,-4 -9,-2Z" fill="{sk}" {STROKE} stroke-width="1.5"/>'
                 f'<path d="M-6,5 C-2,8 3,8 7,6 M-5,10 C-1,12 3,12 6,10" fill="none" stroke="{C["sk_d"]}" stroke-width="1.1"/>'
                 '</g>')
        if pauldron:
            pd = s.lin((-20, -6), (20, 10), [(0, C["arm_d"], None), (0.55, C["arm_m"], None), (0.85, C["arm_l"], None), (1, C["arm_m"], None)])
            a0 = ang(sh, el)
            prot = (a0 - 90) * 0.45 + self.lean * 0.55
            o.insert(1, g_open(sh, prot, 1.28, 1.22) +
                     "".join(
                         f'<path d="M-20,{-14 + k*11} C-12,{-24 + k*11} 12,{-24 + k*11} 20,{-14 + k*11} L18,{2 + k*11} C8,{8 + k*11} -8,{8 + k*11} -18,{2 + k*11}Z" fill="{pd}" {STROKE} stroke-width="1.5"/>'
                         f'<path d="M-20,{-14 + k*11} C-12,{-24 + k*11} 12,{-24 + k*11} 20,{-14 + k*11} L18,{2 + k*11} C8,{8 + k*11} -8,{8 + k*11} -18,{2 + k*11}Z" fill="url(#scale)"/>'
                         f'<path d="M-18,{2 + k*11} C-8,{8 + k*11} 8,{8 + k*11} 18,{2 + k*11}" fill="none" stroke="{C["red_m"]}" stroke-width="1.6"/>'
                         for k in (0, 1, 2)) +
                     f'<circle cx="0" cy="-12" r="2.4" fill="{C["br_l"]}" {STROKE} stroke-width="0.8"/></g>')
        if not near:
            return f'<g>{"".join(o)}<g opacity="0.25">' + "".join(o).replace('fill="url(#g', 'fill="#000" data-g="(#g').replace('fill="url(#r', 'fill="#000" data-r="(#r') + "</g></g>"
        return "".join(o)

    def pauldron(self, sh, el, dark=0.0):
        s = self.s
        pd = s.lin((-20, -6), (20, 10), [(0, C["arm_d"], None), (0.55, C["arm_m"], None), (0.85, C["arm_l"], None), (1, C["arm_m"], None)])
        a0 = ang(sh, el)
        prot = (a0 - 90) * 0.45 + self.lean * 0.55
        o = [g_open(sh, prot, 1.28, 1.22)]
        for k in (0, 1, 2):
            d = f"M-20,{-14 + k*11} C-12,{-24 + k*11} 12,{-24 + k*11} 20,{-14 + k*11} L18,{2 + k*11} C8,{8 + k*11} -8,{8 + k*11} -18,{2 + k*11}Z"
            o.append(f'<path d="{d}" fill="{pd}" {STROKE} stroke-width="1.5"/><path d="{d}" fill="url(#scale)"/>'
                     f'<path d="M-18,{2 + k*11} C-8,{8 + k*11} 8,{8 + k*11} 18,{2 + k*11}" fill="none" stroke="{C["red_m"]}" stroke-width="1.6"/>'
                     + (f'<path d="{d}" fill="#000" opacity="{dark}"/>' if dark else ""))
        o.append(f'<circle cx="0" cy="-12" r="2.4" fill="{C["br_l"]}" {STROKE} stroke-width="0.8"/></g>')
        return "".join(o)

    def torso(self):
        s = self.s
        g = g_open(self.pel, self.lean, 1.16, 1.0)
        body = s.lin((-40, -150), (46, -20), [(0, C["arm_d"], None), (0.45, C["arm_m"], None), (0.78, C["arm_l"], None), (1, C["arm_m"], None)])
        # 흑색 전포(아래 자락) — 갑옷 밑으로 비치는 천
        robe = s.lin((-30, 0), (30, 0), S3(C["cl_l"], C["cl_m"], C["cl_d"]))
        out = [g, f'<path d="M-30,-40 C-34,-10 -34,20 -30,44 L30,44 C33,20 34,-10 31,-40Z" fill="{robe}" {STROKE} stroke-width="1.5"/>']
        # 몸통 갑옷
        d = ("M-26,-132 C-16,-143 0,-148 14,-147 C26,-146 38,-140 42,-128 C48,-112 49,-92 45,-72 "
             "C42,-56 36,-44 33,-34 L-29,-32 C-34,-48 -38,-70 -38,-92 C-38,-110 -34,-124 -26,-132Z")
        out.append(f'<path d="{d}" fill="{body}" {STROKE} stroke-width="1.8"/>')
        out.append(f'<path d="{d}" fill="url(#scale)"/>')
        # 가슴 측면 그늘(입체감)
        out.append(f'<path d="M-38,-92 C-38,-110 -34,-124 -26,-132 C-22,-110 -22,-70 -29,-32 C-34,-48 -38,-70 -38,-92Z" fill="#000" opacity="0.35"/>')
        # 목깃(흑색 전포 깃 + 붉은 안깃)
        out.append(f'<path d="M-6,-148 C2,-136 10,-128 18,-124 C24,-132 28,-140 30,-146 C20,-152 4,-154 -6,-148Z" fill="{C["red_m"]}" {STROKE} stroke-width="1.4"/>')
        out.append(f'<path d="M-14,-146 C-4,-134 8,-126 18,-120 L22,-126 C12,-132 2,-142 -4,-152Z" fill="{C["cl_m"]}" {STROKE} stroke-width="1.4"/>'
                   f'<path d="M34,-146 C30,-136 24,-126 18,-120 L16,-127 C22,-134 26,-142 28,-150Z" fill="{C["cl_m"]}" {STROKE} stroke-width="1.4"/>')
        # 호심경(육각 판 + 쌍룡 원 문양)
        cx, cy = 20, -98
        hexp = []
        for k in range(6):
            a = math.radians(-90 + k * 60)
            hexp.append((cx + 21 * math.cos(a) * 0.82, cy + 21 * math.sin(a)))
        mir = s.lin((cx - 18, cy - 20), (cx + 18, cy + 20), [(0, C["st_l"], None), (0.45, C["st_m"], None), (1, C["st_d"], None)])
        out.append(f'<path d="M{" L".join(pt(q) for q in hexp)}Z" fill="{mir}" {STROKE} stroke-width="1.8"/>')
        inner = [(cx + (q[0] - cx) * 0.74, cy + (q[1] - cy) * 0.74) for q in hexp]
        out.append(f'<path d="M{" L".join(pt(q) for q in inner)}Z" fill="none" stroke="{C["ink"]}" stroke-width="1" stroke-opacity="0.7"/>')
        emb = s.rad((cx - 2, cy - 2), 10, [(0, "#f2e2b0", None), (0.5, C["br_l"], None), (1, C["br_d"], None)])
        out.append(f'<circle cx="{cx}" cy="{cy}" r="8.6" fill="{emb}" {STROKE} stroke-width="1.2"/>'
                   f'<path d="M{cx-5},{cy+2} C{cx-6},{cy-6} {cx+3},{cy-7} {cx+3},{cy-1} C{cx+3},{cy+3} {cx-2},{cy+3} {cx-1},{cy-1} M{cx+5},{cy-2} C{cx+6},{cy+6} {cx-3},{cy+7} {cx-3},{cy+1}" fill="none" stroke="{C["br_d"]}" stroke-width="1.3"/>'
                   f'<path d="M{pt(hexp[0])} L{cx+4},{cy-12}" stroke="#fff" stroke-opacity="0.55" stroke-width="1.6"/>')
        # 가슴 쇠 띠 + 리벳
        out.append(f'<path d="M-36,-64 C-10,-58 20,-58 44,-66" fill="none" stroke="{C["st_d"]}" stroke-width="5"/>'
                   f'<path d="M-36,-64 C-10,-58 20,-58 44,-66" fill="none" stroke="{C["st_m"]}" stroke-width="2.4"/>')
        # 허리띠(가죽 + 쇠 장식 + 버클)
        belt = s.lin((0, -44), (0, -22), [(0, C["le_l"], None), (0.5, C["le_m"], None), (1, C["le_d"], None)])
        out.append(f'<path d="M-32,-44 C-6,-38 18,-38 36,-46 L35,-26 C16,-19 -8,-19 -32,-24Z" fill="{belt}" {STROKE} stroke-width="1.7"/>')
        for x in (-24, -12, 0, 30):
            out.append(f'<rect x="{x-3.5}" y="-40" width="7" height="13" rx="1.2" fill="{C["st_m"]}" {STROKE} stroke-width="0.9"/>')
        buck = s.rad((14, -34), 10, [(0, "#f3e6bd", None), (0.55, C["br_l"], None), (1, C["br_d"], None)])
        out.append(f'<circle cx="15" cy="-33" r="8.2" fill="{buck}" {STROKE} stroke-width="1.4"/>'
                   f'<circle cx="15" cy="-33" r="3.2" fill="none" stroke="{C["br_d"]}" stroke-width="1.2"/>')
        # 붉은 매듭 끈
        out.append(f'<path d="M6,-26 C2,-12 4,0 0,12 M10,-26 C10,-12 13,-2 11,10" fill="none" stroke="{C["red_m"]}" stroke-width="3" stroke-linecap="round"/>')
        # 앞 갑상(가운데 찰갑 자락)
        fr = s.lin((-14, 0), (30, 0), [(0, C["arm_d"], None), (0.6, C["arm_m"], None), (1, C["arm_l"], None)])
        dd = "M-8,-24 L34,-26 L36,34 C20,40 4,40 -10,34Z"
        out.append(f'<path d="{dd}" fill="{fr}" {STROKE} stroke-width="1.6"/><path d="{dd}" fill="url(#lam)"/>'
                   f'<path d="M-10,34 C4,40 20,40 36,34" fill="none" stroke="{C["red_m"]}" stroke-width="2.4"/>')
        out.append("</g>")
        return "".join(out)

    def cannon_hip(self):
        # 등에 비스듬히 멘 화통 — 자루 끝은 허리 뒤, 포구는 가까운 어깨 뒤 위로 비죽
        s = self.s
        base = self.W((-14, -34))
        a = self.lean - 116
        g = g_open(base, a)
        bz = s.lin((0, -7), (0, 7), [(0, C["bz_l"], None), (0.45, C["bz_m"], None), (1, C["bz_d"], None)])
        wd = s.lin((0, -4), (0, 4), [(0, C["wd_l"], None), (1, C["wd_d"], None)])
        return (g + f'<rect x="-6" y="-3.8" width="50" height="7.6" rx="3" fill="{wd}" {STROKE} stroke-width="1.4"/>'
                f'<path d="M40,-7 L104,-6 L108,-9.5 L110,9.5 L104,6 L40,7Z" fill="{bz}" {STROKE} stroke-width="1.6"/>'
                + "".join(f'<rect x="{x}" y="-8.6" width="5" height="17.2" rx="1.6" fill="{C["bz_m"]}" {STROKE} stroke-width="1"/>' for x in (44, 66, 90)) +
                f'<path d="M24,-10 L30,10" stroke="{C["le_m"]}" stroke-width="5"/><path d="M24,-10 L30,10" stroke="{C["le_l"]}" stroke-width="1.6"/></g>')

    def cannon_hands(self):
        s = self.s
        cn = self.P["cannon_line"]
        a = cn["ang"]
        g = g_open(cn["grip"], a)
        bz = s.lin((0, -9), (0, 9), [(0, C["bz_l"], None), (0.45, C["bz_m"], None), (1, C["bz_d"], None)])
        wd = s.lin((0, -4), (0, 4), [(0, C["wd_l"], None), (1, C["wd_d"], None)])
        L = cn["len"]
        out = (g + f'<rect x="-30" y="-4" width="{L*0.45+30}" height="8" rx="3.5" fill="{wd}" {STROKE} stroke-width="1.4"/>'
               f'<path d="M{f(L*0.4)},-8 L{f(L-6)},-7 L{f(L)},-11 L{f(L+3)},11 L{f(L-6)},7 L{f(L*0.4)},8Z" fill="{bz}" {STROKE} stroke-width="1.7"/>'
               + "".join(f'<rect x="{f(L*t)}" y="-9.5" width="5" height="19" rx="1.6" fill="{C["bz_m"]}" {STROKE} stroke-width="1"/>' for t in (0.46, 0.66, 0.84)) +
               f'<circle cx="{f(L*0.5)}" cy="-8" r="2" fill="{C["ink"]}"/></g>')
        self.info["muzzle"] = polar(cn["grip"], a, L + 4)
        return out

    def spear_svg(self, mode="hands"):
        s = self.s
        sp = self.spear
        if mode == "back":
            o = self.W(sp["back_at"])
            a = self.lean + sp["back_ang"]
        else:
            o, a = sp["grip"], sp["ang"]
        t0, t1, L = sp.get("butt", -46), sp.get("b0", 210), sp.get("tip", 262)
        g = g_open(o, a)
        wd = s.lin((0, -3.6), (0, 3.6), [(0, C["wd_l"], None), (0.5, C["wd_m"], None), (1, C["wd_d"], None)])
        bl = s.lin((t1, -8), (t1, 8), [(0, "#f4f7fa", None), (0.48, "#b4bec9", None), (0.52, "#5b6571", None), (1, "#2a3038", None)])
        out = [g, f'<rect x="{t0}" y="-3.6" width="{t1 - t0}" height="7.2" rx="3" fill="{wd}" {STROKE} stroke-width="1.5"/>']
        # 손잡이 끈 감김
        for c0 in sp.get("wraps", (8, 128)):
            out.append(f'<rect x="{c0 - 9}" y="-4.4" width="18" height="8.8" rx="2" fill="{C["le_m"]}" {STROKE} stroke-width="1"/>'
                       + "".join(f'<path d="M{c0 - 7 + k*4},-4 l2,8" stroke="{C["le_l"]}" stroke-width="1"/>' for k in range(4)))
        out.append(f'<rect x="{t0 - 6}" y="-4.6" width="10" height="9.2" rx="2.5" fill="{C["st_m"]}" {STROKE} stroke-width="1.2"/>')
        # 창날(잎새형) + 목 고리
        out.append(f'<rect x="{t1 - 9}" y="-5.5" width="12" height="11" rx="2" fill="{C["st_d"]}" {STROKE} stroke-width="1.2"/>')
        out.append(f'<path d="M{t1},0 C{t1+8},-9 {t1+26},-11 {L},0 C{t1+26},11 {t1+8},9 {t1},0Z" fill="{bl}" {STROKE} stroke-width="1.6"/>'
                   f'<path d="M{t1+3},0 L{L-4},0" stroke="#fff" stroke-opacity="0.7" stroke-width="1.2"/>')
        out.append("</g>")
        # 붉은 술(창 목에서 아래로 늘어짐)
        col = polar(o, a, t1 - 6)
        sway = self.P.get("tassel", 0)
        tas = []
        for k in range(5):
            dx = -6 + k * 3 + sway * (6 + k)
            tas.append(f'<path d="M{pt(col)} q{f(dx*0.5)},{9 + k} {f(dx)},{20 + k*2.2}" fill="none" stroke="{C["red_l"] if k % 2 else C["red_m"]}" stroke-width="2.8" stroke-linecap="round"/>')
        out.append(f'<g>{"".join(tas)}<circle cx="{f(col[0])}" cy="{f(col[1])}" r="4.2" fill="{C["red_m"]}" {STROKE} stroke-width="1"/></g>')
        self.info["spear_tip"] = polar(o, a, L)
        self.info["spear_grip"] = o
        return "".join(out)

    def back_hair(self):
        s = self.s
        P = self.P
        wind = P.get("wind", 0.4)
        ph = P.get("hair_ph", 0.0)
        g = g_open(self.head_o, self.head_deg, 1.12, 1.12)
        hf = s.lin((-30, -40), (10, 90), [(0, C["ha_m"], None), (0.5, C["ha_d"], None), (1, C["ha_d"], None)])
        out = [g]
        strands = [(-14, -46, 118, 22, 0.0), (-20, -34, 138, 24, 0.7), (-8, -22, 104, 17, 1.4), (-24, -52, 92, 18, 2.1), (-4, -12, 82, 14, 2.8), (-18, -60, 72, 16, 3.5)]
        hdeg = -self.head_deg
        for (x0, y0, L, w, off) in strands:
            sway = math.sin(ph * 2 * math.pi + off) * 7
            bx = -wind * 34 - L * 0.12 + sway
            # 머리 국소 좌표에서 '세계 아래' 방향으로 흐르게 회전 보정
            p1 = add((x0, y0), rot((bx * 0.5, L * 0.5), hdeg))
            p2 = add((x0, y0), rot((bx, L), hdeg))
            n1 = add(p1, rot((w * 0.5, 0), hdeg))
            n2 = add(p1, rot((-w * 0.6, 0), hdeg))
            out.append(f'<path d="M{x0 + w*0.5},{y0} Q{pt(n1)} {pt(p2)} Q{pt(n2)} {x0 - w*0.5},{y0}Z" fill="{hf}" {STROKE} stroke-width="1.4"/>'
                       f'<path d="M{x0},{y0} Q{pt(p1)} {pt(add(p2, rot((2, -6), hdeg)))}" fill="none" stroke="{C["ha_l"]}" stroke-opacity="0.55" stroke-width="1.2"/>')
        out.append("</g>")
        return "".join(out)

    def head(self):
        s = self.s
        P = self.P
        out = []
        # 목
        nk = s.lin((-8, 0), (10, 0), [(0, C["sk_d"], None), (0.6, C["sk_m"], None), (1, C["sk_l"], None)])
        g, L = seg_group(self.neck, self.head_o)
        out.append(g + f'<path d="{limb_d(L + 6, 17, 15, 0)}" fill="{nk}" {STROKE} stroke-width="1.4"/></g>')
        g = g_open(self.head_o, self.head_deg, 1.12, 1.12)
        out.append(g)
        skin = s.lin((-22, -40), (36, -10), [(0, C["sk_d"], None), (0.45, C["sk_m"], None), (0.85, C["sk_l"], None), (1, C["sk_m"], None)])
        face = ("M-14,-8 C-26,-22 -27,-48 -12,-61 C0,-71 21,-67 29,-53 C32,-47 33,-41 32,-36 L34,-31 "
                "C35,-28 37,-24 39,-20 C38,-17 35,-16 33,-16 C34,-13 34,-10 32,-8 C33,-5 32,-2 29,0 "
                "C26,4 20,7 13,6 C6,4 0,-1 -4,-4Z")
        out.append(f'<path d="{face}" fill="{skin}" {STROKE} stroke-width="1.7"/>')
        # 광대 · 턱 그늘
        out.append(f'<path d="M-4,-4 C2,-12 8,-14 14,-14 C18,-12 22,-6 26,0 C22,6 12,7 6,4 C2,2 -2,-1 -4,-4Z" fill="{C["sk_d"]}" opacity="0.45"/>'
                   f'<path d="M4,-6 C10,-2 18,2 27,0" fill="none" stroke="#3a3f4a" stroke-opacity="0.35" stroke-width="3"/>')
        # 귀
        out.append(f'<path d="M-3,-31 C-9,-33 -11,-22 -5,-18 C-2,-17 0,-20 0,-24" fill="{C["sk_m"]}" {STROKE} stroke-width="1.3"/>')
        expr = P.get("expr", "fierce")
        # 눈 · 눈썹
        if expr == "hurt":
            out.append(f'<path d="M18,-31 Q23,-33 28,-30" fill="none" stroke="{C["ink"]}" stroke-width="2.2"/>'
                       f'<path d="M15,-38 L29,-41" stroke="{C["ink"]}" stroke-width="3.4"/>')
        else:
            out.append(f'<path d="M16.5,-31 Q22.5,-35.5 29.5,-31.8 Q23.5,-28.4 16.5,-31Z" fill="#efe3d3" {STROKE} stroke-width="1.2"/>'
                       f'<circle cx="25.2" cy="-31.7" r="2.4" fill="{C["ink"]}"/><circle cx="25.9" cy="-32.5" r="0.7" fill="#fff"/>'
                       f'<path d="M13.5,-38.5 C19,-38.6 25,-37.2 31.5,-33.6" fill="none" stroke="{C["ink"]}" stroke-width="4.2"/>'
                       f'<path d="M18,-27.6 C21,-26.4 25,-26.6 28,-28" fill="none" stroke="{C["sk_d"]}" stroke-width="1.1"/>'
                       f'<path d="M9,-44 L16,-27" stroke="#f0c9a8" stroke-opacity="0.8" stroke-width="1.1"/>')
        # 코 · 입
        out.append(f'<path d="M31,-34 C32,-28 34,-24 35,-20" fill="none" stroke="{C["sk_d"]}" stroke-width="1.4"/>'
                   f'<path d="M26,-9.5 L32,-9" stroke="{C["ink"]}" stroke-width="1.6"/>'
                   f'<path d="M22,-4 C25,-3 28,-3 30,-4" fill="none" stroke="{C["sk_d"]}" stroke-width="1"/>')
        # 피 · 흉터
        out.append(f'<path d="M23,-55 C25,-48 22,-42 25,-36 C26,-33 24,-30 22,-27 C23,-32 21,-38 21,-44 C21,-49 21,-52 23,-55Z" fill="{C["bl_l"]}" opacity="0.9"/>'
                   f'<path d="M12,-22 C16,-18 18,-12 17,-6 C15,-11 13,-15 10,-18Z" fill="{C["bl_d"]}" opacity="0.85"/>'
                   f'<path d="M28,-24 l6,3 M29,-18 l4,2" stroke="{C["bl_d"]}" stroke-width="1.4"/>')
        # 머리카락(정수리 · 뒤통수 덮개)
        hf = s.lin((-20, -70), (30, -20), [(0, C["ha_l"], None), (0.3, C["ha_m"], None), (1, C["ha_d"], None)])
        cap = ("M29,-52 C24,-66 6,-73 -10,-66 C-24,-60 -30,-40 -24,-22 C-20,-12 -14,-6 -10,-4 "
               "C-12,-14 -8,-26 -2,-32 C4,-40 12,-46 20,-48 C24,-50 27,-50 29,-52Z")
        out.append(f'<path d="{cap}" fill="{hf}" {STROKE} stroke-width="1.6"/>'
                   f'<path d="M22,-58 C10,-64 -6,-62 -16,-50 M14,-62 C2,-64 -12,-56 -20,-40" fill="none" stroke="{C["ha_l"]}" stroke-opacity="0.6" stroke-width="1.3"/>')
        # 상투 + 상투관 + 동곳
        bun = s.rad((-3, -78), 12, [(0, C["ha_l"], None), (0.6, C["ha_m"], None), (1, C["ha_d"], None)])
        crown = s.lin((-10, -88), (8, -72), [(0, "#7b8592", None), (0.5, "#3b424c", None), (1, "#15181d", None)])
        out.append(f'<ellipse cx="-3" cy="-72" rx="11" ry="8.5" fill="{bun}" {STROKE} stroke-width="1.4"/>'
                   f'<path d="M-10,-73 L-8,-85 C-4,-88 1,-88 4,-85 L6,-73 C1,-71 -5,-71 -10,-73Z" fill="{crown}" {STROKE} stroke-width="1.4"/>'
                   f'<path d="M-9.4,-77 H5.4" stroke="{C["br_l"]}" stroke-width="1.5"/>'
                   f'<path d="M-15,-80 L11,-81.5" stroke="{C["ink"]}" stroke-width="3.4" stroke-linecap="round"/>'
                   f'<path d="M-15,-80 L11,-81.5" stroke="#8f99a5" stroke-width="1.6" stroke-linecap="round"/>')
        # 앞머리 가닥(얼굴 옆으로 흘러내림)
        wind = P.get("wind", 0.4)
        fs = P.get("front_sway", 0.0)
        for (x0, y0, x1, y1, w) in ((12, -50, 2 - wind * 6 + fs * 8, 6, 5.2), (6, -50, -6 - wind * 8 + fs * 10, 12, 6.0)):
            mx, my = (x0 + x1) / 2 + 5, (y0 + y1) / 2
            out.append(f'<path d="M{x0 - w/2},{y0} Q{mx - w},{my} {x1},{y1} Q{mx + w*0.3},{my} {x0 + w/2},{y0}Z" fill="{C["ha_m"]}" {STROKE} stroke-width="1.2"/>')
        # 이마로 흘러내린 잔머리 한 가닥(바람 방향)
        out.append(f'<path d="M24,-52 Q{f(30 - wind*10 + fs*6)},-44 {f(27 - wind*12 + fs*8)},-34" fill="none" stroke="{C["ha_m"]}" stroke-width="2.4" stroke-linecap="round"/>')
        out.append("</g>")
        return "".join(out)

    def far_hand_over(self):
        # 앞(먼 쪽) 손만 창대 위에 다시 그려 '쥔' 느낌
        s = self.s
        sk = s.lin((-9, 0), (9, 0), [(0, C["sk_d"], None), (0.6, C["sk_m"], None), (1, C["sk_l"], None)])
        a = ang(self.el_f, self.ha_f)
        return (g_open(self.ha_f, a - 90) +
                f'<path d="M-9,-2 C-11,6 -9,15 -2,17 C5,18 10,13 10,5 C10,-1 7,-4 0,-4 C-4,-4 -8,-4 -9,-2Z" fill="{sk}" {STROKE} stroke-width="1.5"/>'
                f'<path d="M-6,5 C-2,8 3,8 7,6 M-5,10 C-1,12 3,12 6,10" fill="none" stroke="{C["sk_d"]}" stroke-width="1.1"/>'
                f'<g opacity="0.25"><path d="M-9,-2 C-11,6 -9,15 -2,17 C5,18 10,13 10,5 C10,-1 7,-4 0,-4 C-4,-4 -8,-4 -9,-2Z" fill="#000"/></g></g>')

    def blast(self):
        s = self.s
        m = self.info.get("muzzle")
        if not m:
            return ""
        a = self.P["cannon_line"]["ang"]
        out = [g_open(m, a)]
        # 연기
        for (x, y, r, o) in ((26, -26, 22, 0.55), (54, 18, 26, 0.5), (90, -12, 30, 0.45), (8, 22, 16, 0.5)):
            sm = s.rad((x, y), r, [(0, "#9ca3af", 0.85), (0.7, "#6b7280", 0.5), (1, "#4b5563", 0)])
            out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{sm}" opacity="{o}"/>')
        # 불꽃
        def star(n, r0, r1, sx, seed):
            pts = []
            for k in range(n * 2):
                rr = r1 if k % 2 == 0 else r0
                jitter = 0.85 + 0.3 * ((math.sin(seed + k * 12.9898) * 43758.5453) % 1)
                aa = -math.pi * 0.42 + k * (math.pi * 0.84) / (n * 2 - 1)
                pts.append((math.cos(aa) * rr * jitter * sx, math.sin(aa) * rr * jitter))
            return "M0,0 L" + " L".join(pt(q) for q in pts) + "Z"
        f1 = s.rad((10, 0), 120, [(0, "#fff7d1", 1), (0.35, "#fbbf24", 0.95), (0.7, "#f97316", 0.85), (1, "#b91c1c", 0)])
        out.append(f'<path d="{star(9, 40, 118, 1.25, 1.3)}" fill="{f1}"/>')
        f2 = s.rad((6, 0), 70, [(0, "#ffffff", 1), (0.5, "#fde68a", 0.95), (1, "#f59e0b", 0)])
        out.append(f'<path d="{star(7, 22, 70, 1.15, 4.1)}" fill="{f2}"/>')
        out.append(f'<ellipse cx="10" cy="0" rx="22" ry="12" fill="#ffffff" opacity="0.95"/>')
        for k in range(9):
            aa = -0.7 + k * 0.17
            r0, r1 = 40 + (k * 13) % 30, 70 + (k * 29) % 60
            out.append(f'<path d="M{pt((math.cos(aa)*r0, math.sin(aa)*r0))} L{pt((math.cos(aa)*r1, math.sin(aa)*r1))}" stroke="#fde68a" stroke-width="{2.2 - k*0.12:.2f}" stroke-linecap="round" opacity="0.9"/>')
        out.append("</g>")
        return "".join(out)

    def build(self):
        P = self.P
        body = []
        body.append(self.back_hair())
        if self.cannon == "hip":
            body.append(self.cannon_hip())
        if self.spear and self.spear.get("mode") == "back":
            body.append(self.spear_svg("back"))
        body.append(self.arm(self.sh_f, self.el_f, self.ha_f, near=False, pauldron=False))
        body.append(self.tasset(self.hip_f, self.kn_f, near=False))
        body.append(self.leg(self.hip_f, self.kn_f, self.an_f, P.get("foot_f", 0), near=False))
        body.append(self.leg(self.hip_n, self.kn_n, self.an_n, P.get("foot_n", 0), near=True))
        body.append(self.torso())
        body.append(self.tasset(self.hip_n, self.kn_n, near=True))
        # 먼 쪽 어깨 갑(가슴 앞쪽 어깨)
        body.append(self.pauldron(self.sh_f, self.el_f, dark=0.18))
        body.append(self.head())
        if self.cannon == "hands":
            body.append(self.cannon_hands())
        if self.spear and self.spear.get("mode", "hands") == "hands":
            body.append(self.spear_svg("hands"))
            body.append(self.far_hand_over())
        body.append(self.arm(self.sh_n, self.el_n, self.ha_n, near=True, pauldron=True))
        fx = self.blast() if self.cannon == "hands" and P.get("blast") else ""
        defs = DEFS_STATIC + "".join(self.s.defs)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">'
               f'<defs>{defs}</defs><g filter="url(#ol)">{"".join(body)}</g>{fx}</svg>')
        self.info.update({
            "pelvis": self.pel, "neck": self.neck, "head": self.head_o,
            "hand_n": self.ha_n, "hand_f": self.ha_f, "ank_n": self.an_n, "ank_f": self.an_f,
        })
        return svg


# ---------------- 동작 정의 ----------------
def spear_hold(grip, deg, t_far=138, **kw):
    d = dict(mode="hands", grip=grip, ang=deg, t_far=t_far, butt=-46, b0=210, tip=262, wraps=(4, t_far))
    d.update(kw)
    return d


def ground_ank(x):
    return (x, GROUND - ANKLE_H - 3)


POSES = {}

POSES["idle"] = dict(
    pelvis=(230, 297), lean=5, neck=-2, head=-3,
    ank_n=ground_ank(192), ank_f=ground_ank(276), foot_n=-4, foot_f=2,
    spear=spear_hold((204, 266), -27, 136), wind=0.25, tassel=0.0, hair_ph=0.1,
)


def run_pose(i):
    ph = i / 8.0
    pel_y = 292 + 4.5 * math.cos(4 * math.pi * ph)
    base_x = 236

    def ank(phase):
        u = phase % 1.0
        if u < 0.46:  # 접지(앞 → 뒤)
            t = u / 0.46
            x = 44 - 92 * t
            lift = 0 if t < 0.82 else (t - 0.82) * 40
            return (base_x + x, GROUND - ANKLE_H - 3 - lift), (-4 if t < 0.8 else 18 * (t - 0.8) / 0.2)
        t = (u - 0.46) / 0.54  # 들어 올려 앞으로
        x = -48 + 92 * (1 - math.cos(math.pi * t)) / 2
        lift = 62 * math.sin(math.pi * t) ** 0.9 + (20 * (1 - t) if t < 0.35 else 0)
        foot = 30 * (1 - t) - 12 * t
        return (base_x + x, GROUND - ANKLE_H - 3 - lift), foot

    an_n, fn = ank(ph)
    an_f, ff = ank(ph + 0.5)
    bob = math.sin(2 * math.pi * ph * 2) * 1.5
    grip = (214, 262 + bob)
    return dict(
        pelvis=(base_x, pel_y), lean=12, neck=-6, head=-2,
        ank_n=an_n, ank_f=an_f, foot_n=fn, foot_f=ff,
        spear=spear_hold(grip, -14 + 2.5 * math.sin(2 * math.pi * ph), 132), wind=0.95, tassel=-0.9,
        hair_ph=ph, front_sway=-0.3,
    )


RUN_NAMES = ["run", "run2", "run3", "run4", "run5", "run6", "run7", "run8"]
for _i, _n in enumerate(RUN_NAMES):
    POSES[_n] = run_pose(_i)

POSES["atk_prep"] = dict(
    pelvis=(214, 306), lean=-8, neck=4, head=-5,
    ank_n=ground_ank(160), ank_f=ground_ank(272), foot_n=-12, foot_f=4,
    spear=spear_hold((152, 276), -6, 118), wind=0.1, tassel=0.7, hair_ph=0.3, elbow_back=0.7,
)
# 찌르기 2장은 캔버스 안에 창끝이 들어오도록 몸을 왼쪽으로 옮겨 그리고, 게임에서 poseDX로 되돌린다(rig.json poseDX)
POSES["atk1"] = dict(
    pelvis=(194, 304), lean=16, neck=-10, head=-2,
    ank_n=ground_ank(112), ank_f=ground_ank(278), foot_n=-22, foot_f=4,
    spear=spear_hold((258, 230), -22, 112), wind=0.6, tassel=-1.4, hair_ph=0.55, front_sway=-0.4,
    elbow_back=0.05, poseDX=44,
)
POSES["atk1_2"] = dict(
    pelvis=(200, 306), lean=20, neck=-12, head=-1,
    ank_n=ground_ank(108), ank_f=ground_ank(288), foot_n=-28, foot_f=4,
    spear=spear_hold((264, 236), -24, 110), wind=0.85, tassel=-1.8, hair_ph=0.75, front_sway=-0.6,
    elbow_back=0.0, poseDX=46,
)
POSES["atk2"] = dict(
    pelvis=(224, 299), lean=-7, neck=2, head=-2,
    ank_n=ground_ank(180), ank_f=ground_ank(282), foot_n=-6, foot_f=4,
    spear=dict(mode="back", back_at=(-30, -150), back_ang=74, butt=-50, b0=214, tip=266, wraps=(10, 120)),
    cannon="hands", cannon_line=dict(grip=(212, 262), ang=-8, t_far=78, len=118), blast=True,
    wind=0.1, tassel=0.8, hair_ph=0.2, elbow_back=0.4,
)
POSES["hit"] = dict(
    pelvis=(222, 300), lean=-16, neck=8, head=12, expr="hurt",
    ank_n=ground_ank(186), ank_f=(268, GROUND - ANKLE_H - 18), foot_n=-6, foot_f=-18,
    spear=spear_hold((212, 278), -62, 98), wind=-0.4, tassel=1.2, hair_ph=0.9, front_sway=0.9,
    elbow_back=0.5,
)


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    only = sys.argv[2:] if len(sys.argv) > 2 else list(POSES.keys())
    for name in only:
        r = Rig(POSES[name])
        svg = r.build()
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
            fh.write(svg)
        meta[name] = {k: [round(v[0], 1), round(v[1], 1)] for k, v in r.info.items()}
        if POSES[name].get("poseDX"):
            meta[name]["poseDX"] = POSES[name]["poseDX"]
    with open(os.path.join(OUT, "rig.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print("wrote", len(only), "poses →", OUT)


if __name__ == "__main__":
    main()
