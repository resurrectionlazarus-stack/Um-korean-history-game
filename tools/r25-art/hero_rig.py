#!/usr/bin/env python3
"""R25 코드 리그 원화 생성기 — 검을 든 주인공(척준경 · 해모수) + 2시대 보스 한 무제.

· 몸 원화에는 '검을 쥔 앞손 주먹'과 검을 그리지 않는다. 검 + 주먹은 등급(TI.1~3)별 별도 스프라이트로 만들고,
  동작마다 쥔 자리(grip) · 각도를 rig.json에 내보내 게임이 몸 위에 얹는다 → 유물 각성 때 손에 든 무기가 실제로 바뀐다.
· 자연스러운 8프레임 질주: 발뒤꿈치 착지 → 체중 흡수 → 발끝 차기 → 체공, 팔은 반대 다리와 엇갈려 흔들리고
  머리카락 · 망토는 한 박자 늦게 따라온다.
· 검 연격: 내려베기(atk_prep → atk1 → atk1_2 → atk1_3) · 올려베기(atk2_prep → atk2 ~ atk2_3) ·
  4타 피니시 양손 대도 내리찍기(atk3_prep → atk3 ~ atk3_3).
· 참고 이미지는 의상 · 분위기만 반영하고 얼굴은 특정 실존 인물을 닮지 않은 독자 디자인.

사용법: python3 hero_rig.py OUT_DIR {cjg|haemosu|hanwu} [pose ...]
"""
import json
import math
import os
import sys

# ───────────────────────── 기하 ─────────────────────────
def f(v):
    return f"{v:.1f}"


def pt(p):
    return f"{p[0]:.1f},{p[1]:.1f}"


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


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


def ik2(root, target, L1, L2, prefer):
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
        st = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>" for o, c, a in stops)
        self.defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{f(p0[0])}" y1="{f(p0[1])}" x2="{f(p1[0])}" y2="{f(p1[1])}">{st}</linearGradient>')
        return f"url(#{i})"

    def rad(self, c, r, stops):
        i = self.gid("r")
        st = "".join(f'<stop offset="{o}" stop-color="{col}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>" for o, col, a in stops)
        self.defs.append(f'<radialGradient id="{i}" gradientUnits="userSpaceOnUse" cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}">{st}</radialGradient>')
        return f"url(#{i})"


def S3(t):
    l, m, d = t
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
    return g_open(p0, ang(p0, p1) - 90), dist(p0, p1)


INK = "#07080b"
STROKE = f'stroke="{INK}" stroke-linejoin="round" stroke-linecap="round"'

# ───────────────────────── 의상 ─────────────────────────
COSTUMES = {
    "cjg": dict(
        name="고려 무신 척준경",
        skin=("#e2b18f", "#bf8865", "#7b4f3a"), hair=("#4a5363", "#15171c", "#060608"),
        cloth=("#3a3d45", "#1d1f25", "#0b0c0f"), armor=("#69727e", "#3b424c", "#16191e"),
        steel=("#b3bdc8", "#626c78", "#1c2026"), leather=("#4f3d30", "#2f241c", "#120d0a"),
        accent=("#c8352a", "#8f1d16", "#4a0d0a"), metal=("#d8b878", "#9a7a44", "#4d3a1c"),
        head="topknot", torso="scale", skirt="lamellar", cape=None, emblem="hex", blood=True, robe=False,
        wide_sleeve=False, beard=False, brow=4.2,
    ),
    "haemosu": dict(
        name="천제의 아들 해모수",
        skin=("#eec2a0", "#cf9a77", "#8c5c42"), hair=("#4a5366", "#16181e", "#060607"),
        cloth=("#fbf7ee", "#ddd5c2", "#9d9480"), armor=("#f6dc93", "#cfa64c", "#6e5121"),
        steel=("#f5e4ab", "#c79d47", "#5e4215"), leather=("#86532f", "#56331b", "#25150b"),
        accent=("#ef5a45", "#b4281f", "#5d100c"), metal=("#fff2bd", "#e1b94b", "#7a5a14"),
        head="crow_crown", torso="bronze", skirt="tassel", cape="crimson", emblem="sun", blood=False, robe=False,
        wide_sleeve=False, beard=False, brow=3.6,
    ),
    "hanwu": dict(
        name="한 무제",
        skin=("#e8c09c", "#c4936f", "#80563e"), hair=("#3d4250", "#121318", "#050506"),
        cloth=("#2d2a30", "#16141a", "#060508"), armor=("#3b1418", "#22090c", "#0d0304"),
        steel=("#d6dde5", "#7c8794", "#262c35"), leather=("#5a3a22", "#352114", "#150c07"),
        accent=("#d4483a", "#9b1b16", "#4f0b08"), metal=("#ffe9a6", "#d9a83a", "#76540f"),
        head="mianliu", torso="robe", skirt="robe_long", cape=None, emblem="dragon_belt", blood=False, robe=True,
        wide_sleeve=True, beard=True, brow=4.0, torso_sx=1.32,
    ),
}

GROUND = 470
ANKLE_H = 15
THIGH, SHIN = 95, 89
UARM, FARM = 70, 64
T_NECK = (8, -146)
T_SH_NEAR = (-26, -134)
T_SH_FAR = (40, -135)
T_HIP_NEAR = (-11, -4)
T_HIP_FAR = (13, -6)


def defs_static(C):
    return f'''
<pattern id="scale" width="12" height="10" patternUnits="userSpaceOnUse">
 <path d="M0,0 A6,6.5 0 0 0 12,0 M-6,5 A6,6.5 0 0 0 6,5 M6,5 A6,6.5 0 0 0 18,5" fill="none" stroke="{INK}" stroke-width="1.15" stroke-opacity="0.9"/>
 <path d="M2.2,1.4 Q6,5.8 9.8,1.4 M-3.8,6.4 Q0,10.8 3.8,6.4 M8.2,6.4 Q12,10.8 15.8,6.4" fill="none" stroke="#c3ccd6" stroke-width="0.8" stroke-opacity="0.42"/>
</pattern>
<pattern id="lam" width="8" height="17" patternUnits="userSpaceOnUse">
 <rect x="0.6" y="0.6" width="6.8" height="15.8" rx="2.4" fill="none" stroke="{INK}" stroke-width="1" stroke-opacity="0.85"/>
 <path d="M2.1,2.6 V13.6" stroke="#c7cfd8" stroke-width="0.8" stroke-opacity="0.35"/>
 <circle cx="4" cy="3.4" r="0.95" fill="{C['accent'][0]}"/><circle cx="4" cy="13.4" r="0.95" fill="{C['accent'][1]}"/>
</pattern>
<pattern id="plate" width="14" height="12" patternUnits="userSpaceOnUse">
 <rect x="0.8" y="0.8" width="12.4" height="10.4" rx="2.6" fill="none" stroke="{C['armor'][2]}" stroke-width="1.1" stroke-opacity="0.8"/>
 <path d="M2.6,2.4 H11" stroke="#fffbe8" stroke-width="0.9" stroke-opacity="0.55"/>
</pattern>
<pattern id="cloud" width="40" height="26" patternUnits="userSpaceOnUse">
 <path d="M4,18 q4,-8 10,-3 q3,-7 9,-2 q6,-4 8,4" fill="none" stroke="{C['metal'][1]}" stroke-width="1.6" stroke-opacity="0.75"/>
 <circle cx="31" cy="7" r="2" fill="none" stroke="{C['metal'][1]}" stroke-width="1.2" stroke-opacity="0.7"/>
</pattern>
<filter id="ol" x="-15%" y="-15%" width="130%" height="130%">
 <feMorphology in="SourceAlpha" operator="dilate" radius="2.3" result="d"/>
 <feFlood flood-color="{INK}" result="c"/>
 <feComposite in="c" in2="d" operator="in" result="o"/>
 <feOffset in="SourceAlpha" dx="3" dy="1.5" result="off"/>
 <feComposite in="SourceAlpha" in2="off" operator="out" result="edge"/>
 <feGaussianBlur in="edge" stdDeviation="0.6" result="edgeb"/>
 <feFlood flood-color="#a9bdd8" flood-opacity="0.55" result="rc"/>
 <feComposite in="rc" in2="edgeb" operator="in" result="rim"/>
 <feComposite in="rim" in2="SourceAlpha" operator="in" result="rim2"/>
 <feMerge><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/><feMergeNode in="rim2"/></feMerge>
</filter>
<filter id="glow4" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="4"/></filter>
'''


# ───────────────────────── 몸 ─────────────────────────
class Fig:
    def __init__(self, C, P):
        self.C, self.P = C, P
        self.s = SVG()
        self.info = {}
        pel = P["pelvis"]
        lean = P.get("lean", 0)
        self.pel, self.lean = pel, lean
        sh = P.get("shoulder_shift", 0)
        W = lambda q: add(pel, rot(q, lean))
        self.W = W
        self.neck = W(T_NECK)
        self.sh_n = W((T_SH_NEAR[0] + sh, T_SH_NEAR[1]))
        self.sh_f = W((T_SH_FAR[0] + sh * 0.5, T_SH_FAR[1]))
        self.hip_n, self.hip_f = W(T_HIP_NEAR), W(T_HIP_FAR)
        self.head_o = add(self.neck, rot((5, -15), lean + P.get("neck", 0)))
        self.head_deg = lean + P.get("neck", 0) + P.get("head", 0)
        fwd = lambda m: m[0]
        self.kn_n, self.an_n = ik2(self.hip_n, P["ank_n"], THIGH, SHIN, fwd)
        self.kn_f, self.an_f = ik2(self.hip_f, P["ank_f"], THIGH, SHIN, fwd)
        low = lambda back: (lambda m: m[1] + back * (-m[0]))
        self.grip = P["grip"]
        self.sword = P["sword"]
        # 앞(가까운) 손: 검 손잡이. 손목은 손잡이 중심에서 검 축의 수직 방향으로 살짝 떨어진 곳
        c1 = polar(self.grip, self.sword + 90, 9)
        c2 = polar(self.grip, self.sword - 90, 9)
        side = 1 if dist(c1, self.sh_n) <= dist(c2, self.sh_n) else -1
        self.side = side
        wr = c1 if side == 1 else c2
        self.ha_n_target = wr
        self.el_n, self.ha_n = ik2(self.sh_n, wr, UARM, FARM, low(P.get("elbow_n", 0.35)))
        hf = P.get("hand_f")
        if hf == "two":
            hf = polar(self.grip, self.sword + 180, 20)
            self.far_on_hilt = True
        else:
            self.far_on_hilt = False
        self.el_f, self.ha_f = ik2(self.sh_f, hf, UARM, FARM, low(P.get("elbow_f", 0.35)))

    # ── 다리 ──
    def leg(self, hip, kn, an, foot_deg, near):
        s, C = self.s, self.C
        o = []
        robe = C["robe"]
        if not robe:
            g0, L = seg_group(hip, kn)
            o.append(g0 + f'<path d="{limb_d(L + 6, 37, 27, 3)}" fill="{s.lin((-14, 0), (14, 0), S3(C["cloth"]))}" {STROKE} stroke-width="1.6"/>'
                     f'<path d="M-6,{f(L * 0.25)} q4,10 1,22 M5,{f(L * 0.45)} q-3,9 0,18" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="1.4"/></g>')
            g1, L2 = seg_group(kn, an)
            st = s.lin((-11, 0), (11, 0), [(0, C["steel"][2], None), (0.55, C["steel"][1], None), (0.8, C["steel"][0], None), (1, C["steel"][1], None)])
            o.append(g1 + f'<path d="{limb_d(L2, 27, 20, 1.5)}" fill="{s.lin((-12, 0), (12, 0), S3(C["cloth"]))}" {STROKE} stroke-width="1.6"/>'
                     f'<path d="M-12,-8 C-12,-20 12,-20 12,-8 L11,6 C4,10 -4,10 -11,6Z" fill="{st}" {STROKE} stroke-width="1.6"/>'
                     f'<path d="M-10,{f(L2 * 0.28)} L10,{f(L2 * 0.26)} L9,{f(L2 * 0.92)} L-9,{f(L2 * 0.92)}Z" fill="{st}" {STROKE} stroke-width="1.5"/>'
                     f'<path d="M-6,{f(L2 * 0.33)} V{f(L2 * 0.86)}" stroke="#ffffff" stroke-opacity="0.45" stroke-width="1.4"/>'
                     f'<path d="M-10,{f(L2 * 0.5)} H10 M-9.5,{f(L2 * 0.7)} H9.5" stroke="{INK}" stroke-width="1"/></g>')
        boot = s.lin((0, -16), (0, 16), [(0, C["leather"][0], None), (0.55, C["leather"][1], None), (1, C["leather"][2], None)])
        o.append(g_open(an, foot_deg) +
                 f'<path d="M-11,-16 L-12,8 C-12,13 -9,15 -4,15 L30,15 C35,15 37,11 33,7 C27,1 18,-2 12,-6 L10,-16Z" fill="{boot}" {STROKE} stroke-width="1.7"/>'
                 f'<path d="M-12,12 H33" stroke="{INK}" stroke-width="2.6"/><path d="M-9,-11 H9" stroke="{C["metal"][1]}" stroke-width="2"/></g>')
        body = "".join(o)
        if not near:
            body = f'<g>{body}<g opacity="0.24">' + body.replace('fill="url(#g', 'fill="#000" data-g="(#g') + "</g></g>"
        return body

    def tasset(self, hip, kn, near):
        s, C = self.s, self.C
        if C["skirt"] not in ("lamellar", "tassel"):
            return ""
        a = ang(hip, kn)
        if C["skirt"] == "lamellar":
            base = s.lin((-16, 0), (16, 0), [(0, C["armor"][2], None), (0.55, C["armor"][1], None), (0.85, C["armor"][0], None), (1, C["armor"][1], None)])
            d = "M-17,-10 L17,-10 L21,52 C8,58 -8,58 -21,52Z"
            extra = f'<path d="{d}" fill="url(#lam)"/><path d="M-21,52 C-8,58 8,58 21,52" fill="none" stroke="{C["accent"][1]}" stroke-width="2.4"/>'
        else:
            base = s.lin((-16, 0), (16, 0), S3(C["cloth"]))
            d = "M-18,-10 L18,-10 L22,46 L12,58 L2,47 L-8,58 L-21,46Z"
            extra = (f'<path d="M-19,4 H19" stroke="{C["metal"][1]}" stroke-width="3"/>'
                     f'<path d="M-21,46 L-8,58 L2,47 L12,58 L22,46" fill="none" stroke="{C["accent"][1]}" stroke-width="2.2"/>')
        sh = 0 if near else 0.28
        return (g_open(hip, a - 90) + f'<path d="{d}" fill="{base}" {STROKE} stroke-width="1.6"/>' + extra +
                (f'<path d="{d}" fill="#000" opacity="{sh}"/>' if sh else "") + "</g>")

    def robe_lower(self):
        # 긴 곤룡포 자락: 허리띠에서 발목까지, 앞 · 뒤 무릎 자리를 따라 펄럭
        s, C = self.s, self.C
        top_b = self.W((-34, -30))
        top_f = self.W((40, -34))
        back_k = (min(self.kn_n[0], self.kn_f[0]) - 26, (self.kn_n[1] + self.kn_f[1]) / 2)
        front_k = (max(self.kn_n[0], self.kn_f[0]) + 24, (self.kn_n[1] + self.kn_f[1]) / 2 - 4)
        back_a = (min(self.an_n[0], self.an_f[0]) - 26, GROUND - 14)
        front_a = (max(self.an_n[0], self.an_f[0]) + 26, GROUND - 18)
        sway = self.P.get("robe_sway", 0)
        hem = []
        n = 6
        for i in range(n + 1):
            t = i / n
            x = back_a[0] + (front_a[0] - back_a[0]) * t
            y = back_a[1] + (front_a[1] - back_a[1]) * t + (4 if i % 2 else -2) + sway * math.sin(t * 5)
            hem.append((x, y))
        d = (f"M{pt(top_b)} Q{pt(add(back_k, (-6 + sway * 3, 0)))} {pt(back_a)} L" + " L".join(pt(q) for q in hem) +
             f" Q{pt(add(front_k, (4 + sway * 4, 0)))} {pt(top_f)}Z")
        fill = s.lin((back_a[0], 0), (front_a[0], 0), [(0, C["armor"][2], None), (0.5, C["armor"][1], None), (0.85, C["armor"][0], None), (1, C["armor"][1], None)])
        out = f'<path d="{d}" fill="{fill}" {STROKE} stroke-width="1.8"/><path d="{d}" fill="url(#cloud)" opacity="0.55"/>'
        # 가운데 앞자락 금띠 · 붉은 단
        mid_top = self.W((10, -30))
        mid_bot = ((back_a[0] + front_a[0]) / 2 + 8, GROUND - 12)
        out += f'<path d="M{pt(mid_top)} L{pt(mid_bot)}" stroke="{C["metal"][1]}" stroke-width="7"/><path d="M{pt(mid_top)} L{pt(mid_bot)}" stroke="{C["accent"][1]}" stroke-width="3"/>'
        out += f'<path d="M{pt(hem[0])} L' + " L".join(pt(q) for q in hem[1:]) + f'" fill="none" stroke="{C["accent"][1]}" stroke-width="5"/>'
        for i in range(1, 4):
            a = add(top_b, ((top_f[0] - top_b[0]) * i / 4, (top_f[1] - top_b[1]) * i / 4))
            b = hem[min(n, i * 2)]
            out += f'<path d="M{pt(a)} Q{pt(add(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), (6, 0)))} {pt(b)}" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="1.6"/>'
        return out

    # ── 팔 ──
    def arm(self, sh, el, ha, near, fist=True):
        s, C = self.s, self.C
        o = []
        g0, L = seg_group(sh, el)
        if C["wide_sleeve"]:
            sl = s.lin((-18, 0), (18, 0), [(0, C["armor"][2], None), (0.55, C["armor"][1], None), (0.85, C["armor"][0], None), (1, C["armor"][1], None)])
            o.append(g0 + f'<path d="{limb_d(L + 6, 38, 34, 5)}" fill="{sl}" {STROKE} stroke-width="1.7"/></g>')
            g1, L2 = seg_group(el, ha)
            o.append(g1 + f'<path d="M-17,-6 L17,-6 L26,{f(L2 * 0.92)} C10,{f(L2 * 1.08)} -10,{f(L2 * 1.08)} -26,{f(L2 * 0.92)}Z" fill="{sl}" {STROKE} stroke-width="1.7"/>'
                     f'<path d="M-26,{f(L2 * 0.92)} C-10,{f(L2 * 1.08)} 10,{f(L2 * 1.08)} 26,{f(L2 * 0.92)}" fill="none" stroke="{C["metal"][1]}" stroke-width="4"/>'
                     f'<path d="M-10,{f(L2 * 0.2)} q-4,20 2,40" fill="none" stroke="#000" stroke-opacity="0.4" stroke-width="1.6"/></g>')
        else:
            o.append(g0 + f'<path d="{limb_d(L + 4, 32, 25, 3)}" fill="{s.lin((-14, 0), (14, 0), S3(C["cloth"]))}" {STROKE} stroke-width="1.6"/>'
                     f'<path d="M-5,{f(L * 0.3)} q5,8 2,18" fill="none" stroke="#000" stroke-opacity="0.4" stroke-width="1.3"/></g>')
            g1, L2 = seg_group(el, ha)
            bra = s.lin((-11, 0), (11, 0), [(0, C["leather"][2], None), (0.5, C["leather"][1], None), (0.82, C["leather"][0], None), (1, C["leather"][1], None)])
            o.append(g1 + f'<path d="{limb_d(L2, 25, 19, 1.5)}" fill="{s.lin((-12, 0), (12, 0), S3(C["cloth"]))}" {STROKE} stroke-width="1.6"/>'
                     f'<path d="M-11,{f(L2 * 0.34)} L11,{f(L2 * 0.32)} L9.5,{f(L2 * 0.98)} L-9.5,{f(L2 * 0.98)}Z" fill="{bra}" {STROKE} stroke-width="1.5"/>'
                     f'<path d="M-10.5,{f(L2 * 0.5)} H10.5 M-10,{f(L2 * 0.72)} H10" stroke="{C["metal"][1]}" stroke-width="2.2"/></g>')
        if fist:
            o.append(fist_svg(s, C, ha, ang(el, ha) - 90))
        body = "".join(o)
        if not near:
            body = f'<g>{body}<g opacity="0.24">' + body.replace('fill="url(#g', 'fill="#000" data-g="(#g') + "</g></g>"
        return body

    def pauldron(self, sh, el, dark=0.0, big=1.0):
        s, C = self.s, self.C
        style = C["torso"]
        a0 = ang(sh, el)
        prot = (a0 - 90) * 0.45 + self.lean * 0.55
        if style == "robe":
            return ""
        fillc = C["armor"]
        pd = s.lin((-20, -6), (20, 10), [(0, fillc[2], None), (0.55, fillc[1], None), (0.85, fillc[0], None), (1, fillc[1], None)])
        pat = "url(#scale)" if style == "scale" else "url(#plate)"
        o = [g_open(sh, prot, 1.28 * big, 1.22 * big)]
        for k in (0, 1, 2):
            d = f"M-20,{-14 + k * 11} C-12,{-24 + k * 11} 12,{-24 + k * 11} 20,{-14 + k * 11} L18,{2 + k * 11} C8,{8 + k * 11} -8,{8 + k * 11} -18,{2 + k * 11}Z"
            o.append(f'<path d="{d}" fill="{pd}" {STROKE} stroke-width="1.5"/><path d="{d}" fill="{pat}"/>'
                     f'<path d="M-18,{2 + k * 11} C-8,{8 + k * 11} 8,{8 + k * 11} 18,{2 + k * 11}" fill="none" stroke="{C["accent"][1]}" stroke-width="1.6"/>'
                     + (f'<path d="{d}" fill="#000" opacity="{dark}"/>' if dark else ""))
        o.append(f'<circle cx="0" cy="-12" r="2.4" fill="{C["metal"][0]}" {STROKE} stroke-width="0.8"/></g>')
        return "".join(o)

    # ── 몸통 ──
    def torso(self):
        s, C = self.s, self.C
        g = g_open(self.pel, self.lean, C.get("torso_sx", 1.16), 1.0)
        out = [g]
        robe = s.lin((-30, 0), (30, 0), S3(C["cloth"]))
        if not C["robe"]:
            out.append(f'<path d="M-30,-40 C-34,-10 -34,20 -30,44 L30,44 C33,20 34,-10 31,-40Z" fill="{robe}" {STROKE} stroke-width="1.5"/>')
        d = ("M-26,-132 C-16,-143 0,-148 14,-147 C26,-146 38,-140 42,-128 C48,-112 49,-92 45,-72 "
             "C42,-56 36,-44 33,-34 L-29,-32 C-34,-48 -38,-70 -38,-92 C-38,-110 -34,-124 -26,-132Z")
        A = C["armor"]
        body = s.lin((-40, -150), (46, -20), [(0, A[2], None), (0.45, A[1], None), (0.78, A[0], None), (1, A[1], None)])
        out.append(f'<path d="{d}" fill="{body}" {STROKE} stroke-width="1.8"/>')
        if C["torso"] == "scale":
            out.append(f'<path d="{d}" fill="url(#scale)"/>')
        elif C["torso"] == "bronze":
            out.append(f'<path d="{d}" fill="url(#plate)"/>')
        else:  # robe: 용 · 구름 금박 무늬 + 교차 깃
            out.append(f'<path d="{d}" fill="url(#cloud)" opacity="0.8"/>')
        out.append(f'<path d="M-38,-92 C-38,-110 -34,-124 -26,-132 C-22,-110 -22,-70 -29,-32 C-34,-48 -38,-70 -38,-92Z" fill="#000" opacity="0.32"/>')
        if C["robe"]:
            # 교차 깃(오른섶) + 붉은 안깃 + 넓은 금띠
            out.append(f'<path d="M-4,-150 C6,-120 20,-96 36,-74 L44,-80 C30,-100 16,-124 10,-150Z" fill="{C["accent"][1]}" {STROKE} stroke-width="1.5"/>'
                       f'<path d="M-14,-148 C0,-118 18,-92 40,-70" fill="none" stroke="{C["metal"][1]}" stroke-width="4"/>')
        else:
            out.append(f'<path d="M-6,-148 C2,-136 10,-128 18,-124 C24,-132 28,-140 30,-146 C20,-152 4,-154 -6,-148Z" fill="{C["accent"][1]}" {STROKE} stroke-width="1.4"/>'
                       f'<path d="M-14,-146 C-4,-134 8,-126 18,-120 L22,-126 C12,-132 2,-142 -4,-152Z" fill="{C["cloth"][1]}" {STROKE} stroke-width="1.4"/>'
                       f'<path d="M34,-146 C30,-136 24,-126 18,-120 L16,-127 C22,-134 26,-142 28,-150Z" fill="{C["cloth"][1]}" {STROKE} stroke-width="1.4"/>')
        cx, cy = 20, -98
        em = C["emblem"]
        if em == "hex":
            hexp = [(cx + 21 * math.cos(math.radians(-90 + k * 60)) * 0.82, cy + 21 * math.sin(math.radians(-90 + k * 60))) for k in range(6)]
            mir = s.lin((cx - 18, cy - 20), (cx + 18, cy + 20), [(0, C["steel"][0], None), (0.45, C["steel"][1], None), (1, C["steel"][2], None)])
            out.append(f'<path d="M{" L".join(pt(q) for q in hexp)}Z" fill="{mir}" {STROKE} stroke-width="1.8"/>')
            emb = s.rad((cx - 2, cy - 2), 10, [(0, "#f2e2b0", None), (0.5, C["metal"][0], None), (1, C["metal"][2], None)])
            out.append(f'<circle cx="{cx}" cy="{cy}" r="8.6" fill="{emb}" {STROKE} stroke-width="1.2"/>'
                       f'<path d="M{cx - 5},{cy + 2} C{cx - 6},{cy - 6} {cx + 3},{cy - 7} {cx + 3},{cy - 1} C{cx + 3},{cy + 3} {cx - 2},{cy + 3} {cx - 1},{cy - 1} M{cx + 5},{cy - 2} C{cx + 6},{cy + 6} {cx - 3},{cy + 7} {cx - 3},{cy + 1}" fill="none" stroke="{C["metal"][2]}" stroke-width="1.3"/>')
        elif em == "sun":
            sun = s.rad((cx - 3, cy - 3), 20, [(0, "#fffbe6", None), (0.45, "#fcd34d", None), (1, "#b45309", None)])
            rays = "".join(f'<path d="M{pt(polar((cx, cy), k * 30, 13))} L{pt(polar((cx, cy), k * 30 + 9, 22))} L{pt(polar((cx, cy), k * 30 + 18, 13))}Z" fill="#f59e0b" {STROKE} stroke-width="1"/>' for k in range(12))
            out.append(rays + f'<circle cx="{cx}" cy="{cy}" r="13" fill="{sun}" {STROKE} stroke-width="1.6"/>'
                       f'<path d="M{cx - 6},{cy - 2} q3,-4 6,0 q3,4 6,0" fill="none" stroke="#92400e" stroke-width="1.4"/><circle cx="{cx}" cy="{cy + 4}" r="1.8" fill="#92400e"/>')
        # 가슴 띠
        if not C["robe"]:
            out.append(f'<path d="M-36,-64 C-10,-58 20,-58 44,-66" fill="none" stroke="{C["steel"][2]}" stroke-width="5"/>'
                       f'<path d="M-36,-64 C-10,-58 20,-58 44,-66" fill="none" stroke="{C["steel"][1]}" stroke-width="2.4"/>')
        # 허리띠
        belt = s.lin((0, -44), (0, -22), [(0, C["leather"][0], None), (0.5, C["leather"][1], None), (1, C["leather"][2], None)])
        if C["robe"]:
            belt = s.lin((0, -44), (0, -22), [(0, C["metal"][0], None), (0.5, C["metal"][1], None), (1, C["metal"][2], None)])
        out.append(f'<path d="M-32,-44 C-6,-38 18,-38 36,-46 L35,-26 C16,-19 -8,-19 -32,-24Z" fill="{belt}" {STROKE} stroke-width="1.7"/>')
        for x in (-24, -12, 0, 30):
            out.append(f'<rect x="{x - 3.5}" y="-40" width="7" height="13" rx="1.2" fill="{"#6ee7b7" if C["robe"] else C["steel"][1]}" {STROKE} stroke-width="0.9"/>')
        buck = s.rad((14, -34), 10, [(0, "#f3e6bd", None), (0.55, C["metal"][0], None), (1, C["metal"][2], None)])
        out.append(f'<circle cx="15" cy="-33" r="8.2" fill="{buck}" {STROKE} stroke-width="1.4"/><circle cx="15" cy="-33" r="3.2" fill="none" stroke="{C["metal"][2]}" stroke-width="1.2"/>')
        if C["skirt"] == "lamellar":
            out.append(f'<path d="M6,-26 C2,-12 4,0 0,12 M10,-26 C10,-12 13,-2 11,10" fill="none" stroke="{C["accent"][1]}" stroke-width="3" stroke-linecap="round"/>')
            fr = s.lin((-14, 0), (30, 0), [(0, A[2], None), (0.6, A[1], None), (1, A[0], None)])
            dd = "M-8,-24 L34,-26 L36,34 C20,40 4,40 -10,34Z"
            out.append(f'<path d="{dd}" fill="{fr}" {STROKE} stroke-width="1.6"/><path d="{dd}" fill="url(#lam)"/>'
                       f'<path d="M-10,34 C4,40 20,40 36,34" fill="none" stroke="{C["accent"][1]}" stroke-width="2.4"/>')
        elif C["skirt"] == "tassel":
            # 붉은 허리 매듭(해모수)
            out.append(f'<path d="M8,-26 C4,-8 8,8 2,26 M14,-26 C16,-8 20,6 16,24" fill="none" stroke="{C["accent"][1]}" stroke-width="5" stroke-linecap="round"/>'
                       f'<path d="M8,-26 C4,-8 8,8 2,26 M14,-26 C16,-8 20,6 16,24" fill="none" stroke="{C["accent"][0]}" stroke-width="1.8" stroke-linecap="round"/>')
        out.append("</g>")
        return "".join(out)

    # ── 망토(해모수) ──
    def cape(self):
        C = self.C
        if not C["cape"]:
            return ""
        s = self.s
        P = self.P
        wind = P.get("wind", 0.3)
        ph = P.get("hair_ph", 0.0)
        a = self.W((-24, -138))
        b = self.W((30, -140))
        L = 190
        tipx = a[0] - 40 - wind * 120
        tipy = a[1] + L * (1 - wind * 0.55)
        pts = []
        n = 7
        for i in range(n + 1):
            t = i / n
            x = tipx + (b[0] - 40 - wind * 70 - tipx) * t
            y = tipy + (b[1] + L * 0.8 * (1 - wind * 0.5) - tipy) * t + math.sin(ph * 2 * math.pi + t * 7) * (6 + wind * 8)
            pts.append((x, y))
        d = f"M{pt(a)} Q{pt((a[0] - 30 - wind * 50, a[1] + 60))} {pt(pts[0])} L" + " L".join(pt(q) for q in pts[1:]) + f" Q{pt((b[0] - 10 - wind * 30, b[1] + 60))} {pt(b)}Z"
        fill = s.lin((tipx, 0), (b[0], 0), [(0, C["accent"][2], None), (0.5, C["accent"][1], None), (1, C["accent"][0], None)])
        folds = "".join(f'<path d="M{pt(add(a, ((b[0] - a[0]) * k / 4, 0)))} Q{pt((pts[k * 2 - 1][0] + 10, (a[1] + pts[k * 2 - 1][1]) / 2))} {pt(pts[k * 2 - 1])}" fill="none" stroke="#000" stroke-opacity="0.3" stroke-width="1.6"/>' for k in (1, 2, 3))
        return (f'<path d="{d}" fill="{fill}" {STROKE} stroke-width="1.8"/>' + folds +
                f'<path d="M{pt(pts[0])} L' + " L".join(pt(q) for q in pts[1:]) + f'" fill="none" stroke="{C["metal"][1]}" stroke-width="3"/>')

    # ── 머리 ──
    def back_hair(self):
        s, C, P = self.s, self.C, self.P
        if C["head"] == "mianliu":
            return ""
        wind = P.get("wind", 0.4)
        ph = P.get("hair_ph", 0.0)
        g = g_open(self.head_o, self.head_deg, 1.12, 1.12)
        hf = s.lin((-30, -40), (10, 90), [(0, C["hair"][1], None), (0.5, C["hair"][2], None), (1, C["hair"][2], None)])
        out = [g]
        strands = [(-14, -46, 118, 22, 0.0), (-20, -34, 138, 24, 0.7), (-8, -22, 104, 17, 1.4), (-24, -52, 92, 18, 2.1), (-4, -12, 82, 14, 2.8), (-18, -60, 72, 16, 3.5)]
        if C["head"] == "crow_crown":
            strands = [(-14, -46, 96, 20, 0.0), (-20, -34, 112, 22, 0.7), (-8, -22, 86, 15, 1.4), (-22, -50, 78, 16, 2.1)]
        hdeg = -self.head_deg
        for (x0, y0, L, w, off) in strands:
            sway = math.sin(ph * 2 * math.pi + off) * 7
            bx = -wind * 34 - L * 0.12 + sway
            p1 = add((x0, y0), rot((bx * 0.5, L * 0.5), hdeg))
            p2 = add((x0, y0), rot((bx, L), hdeg))
            n1 = add(p1, rot((w * 0.5, 0), hdeg))
            n2 = add(p1, rot((-w * 0.6, 0), hdeg))
            out.append(f'<path d="M{x0 + w * 0.5},{y0} Q{pt(n1)} {pt(p2)} Q{pt(n2)} {x0 - w * 0.5},{y0}Z" fill="{hf}" {STROKE} stroke-width="1.4"/>'
                       f'<path d="M{x0},{y0} Q{pt(p1)} {pt(add(p2, rot((2, -6), hdeg)))}" fill="none" stroke="{C["hair"][0]}" stroke-opacity="0.55" stroke-width="1.2"/>')
        out.append("</g>")
        return "".join(out)

    def head(self):
        s, C, P = self.s, self.C, self.P
        out = []
        nk = s.lin((-8, 0), (10, 0), [(0, C["skin"][2], None), (0.6, C["skin"][1], None), (1, C["skin"][0], None)])
        g, L = seg_group(self.neck, self.head_o)
        out.append(g + f'<path d="{limb_d(L + 6, 17, 15, 0)}" fill="{nk}" {STROKE} stroke-width="1.4"/></g>')
        out.append(g_open(self.head_o, self.head_deg, 1.12, 1.12))
        skin = s.lin((-22, -40), (36, -10), [(0, C["skin"][2], None), (0.45, C["skin"][1], None), (0.85, C["skin"][0], None), (1, C["skin"][1], None)])
        face = ("M-14,-8 C-26,-22 -27,-48 -12,-61 C0,-71 21,-67 29,-53 C32,-47 33,-41 32,-36 L34,-31 "
                "C35,-28 37,-24 39,-20 C38,-17 35,-16 33,-16 C34,-13 34,-10 32,-8 C33,-5 32,-2 29,0 "
                "C26,4 20,7 13,6 C6,4 0,-1 -4,-4Z")
        out.append(f'<path d="{face}" fill="{skin}" {STROKE} stroke-width="1.7"/>')
        out.append(f'<path d="M-4,-4 C2,-12 8,-14 14,-14 C18,-12 22,-6 26,0 C22,6 12,7 6,4 C2,2 -2,-1 -4,-4Z" fill="{C["skin"][2]}" opacity="0.42"/>')
        out.append(f'<path d="M-3,-31 C-9,-33 -11,-22 -5,-18 C-2,-17 0,-20 0,-24" fill="{C["skin"][1]}" {STROKE} stroke-width="1.3"/>')
        expr = P.get("expr", "fierce")
        if expr == "hurt":
            out.append(f'<path d="M18,-31 Q23,-33 28,-30" fill="none" stroke="{INK}" stroke-width="2.2"/><path d="M15,-38 L29,-41" stroke="{INK}" stroke-width="3.4"/>')
        else:
            out.append(f'<path d="M16.5,-31 Q22.5,-35.5 29.5,-31.8 Q23.5,-28.4 16.5,-31Z" fill="#efe3d3" {STROKE} stroke-width="1.2"/>'
                       f'<circle cx="25.2" cy="-31.7" r="2.4" fill="{INK}"/><circle cx="25.9" cy="-32.5" r="0.7" fill="#fff"/>'
                       f'<path d="M13.5,-38.5 C19,-38.6 25,-37.2 31.5,-33.6" fill="none" stroke="{INK}" stroke-width="{C["brow"]}"/>'
                       f'<path d="M18,-27.6 C21,-26.4 25,-26.6 28,-28" fill="none" stroke="{C["skin"][2]}" stroke-width="1.1"/>')
        mouth = "M26,-9.5 L32,-9" if expr != "shout" else "M25,-11 Q29,-5 33,-10"
        out.append(f'<path d="M31,-34 C32,-28 34,-24 35,-20" fill="none" stroke="{C["skin"][2]}" stroke-width="1.4"/>'
                   f'<path d="{mouth}" stroke="{INK}" stroke-width="1.6" fill="{"#5a1a12" if expr == "shout" else "none"}"/>')
        if C["beard"]:
            out.append(f'<path d="M24,-12 C28,-14 33,-13 35,-11 C32,-10 28,-10 24,-10Z" fill="{C["hair"][1]}" {STROKE} stroke-width="0.8"/>'
                       f'<path d="M20,-2 C24,2 28,8 26,20 C24,14 20,8 16,4Z" fill="{C["hair"][1]}" {STROKE} stroke-width="1"/>')
        if C["blood"]:
            out.append(f'<path d="M23,-55 C25,-48 22,-42 25,-36 C26,-33 24,-30 22,-27 C23,-32 21,-38 21,-44 C21,-49 21,-52 23,-55Z" fill="#b8231b" opacity="0.9"/>'
                       f'<path d="M12,-22 C16,-18 18,-12 17,-6 C15,-11 13,-15 10,-18Z" fill="#6b0c0c" opacity="0.85"/>')
        hf = s.lin((-20, -70), (30, -20), [(0, C["hair"][0], None), (0.3, C["hair"][1], None), (1, C["hair"][2], None)])
        cap = ("M29,-52 C24,-66 6,-73 -10,-66 C-24,-60 -30,-40 -24,-22 C-20,-12 -14,-6 -10,-4 "
               "C-12,-14 -8,-26 -2,-32 C4,-40 12,-46 20,-48 C24,-50 27,-50 29,-52Z")
        out.append(f'<path d="{cap}" fill="{hf}" {STROKE} stroke-width="1.6"/>'
                   f'<path d="M22,-58 C10,-64 -6,-62 -16,-50 M14,-62 C2,-64 -12,-56 -20,-40" fill="none" stroke="{C["hair"][0]}" stroke-opacity="0.6" stroke-width="1.3"/>')
        hd = C["head"]
        if hd == "topknot":
            bun = s.rad((-3, -78), 12, [(0, C["hair"][0], None), (0.6, C["hair"][1], None), (1, C["hair"][2], None)])
            crown = s.lin((-10, -88), (8, -72), [(0, "#7b8592", None), (0.5, "#3b424c", None), (1, "#15181d", None)])
            out.append(f'<ellipse cx="-3" cy="-72" rx="11" ry="8.5" fill="{bun}" {STROKE} stroke-width="1.4"/>'
                       f'<path d="M-10,-73 L-8,-85 C-4,-88 1,-88 4,-85 L6,-73 C1,-71 -5,-71 -10,-73Z" fill="{crown}" {STROKE} stroke-width="1.4"/>'
                       f'<path d="M-9.4,-77 H5.4" stroke="{C["metal"][0]}" stroke-width="1.5"/>'
                       f'<path d="M-15,-80 L11,-81.5" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/><path d="M-15,-80 L11,-81.5" stroke="#8f99a5" stroke-width="1.6" stroke-linecap="round"/>')
        elif hd == "crow_crown":
            # 오우관(烏羽冠): 까마귀 깃털 관 — 금테 관 위로 검은 깃이 뒤로 휘어 솟는다
            wind = P.get("wind", 0.3)
            feathers = []
            for k, (x0, L, a0) in enumerate(((-2, 46, -100), (-8, 54, -118), (-14, 50, -134), (-20, 40, -150), (4, 36, -86))):
                a = a0 - wind * 14
                tip = polar((x0, -74), a, L)
                ctrl = polar((x0, -74), a + 14, L * 0.6)
                w = 7 - k * 0.6
                lft = polar(ctrl, a - 90, w)
                rgt = polar(ctrl, a + 90, w)
                fg = s.lin((x0, -74), tip, [(0, "#2b3240", None), (0.6, "#0b0d12", None), (1, "#3d4a63", None)])
                feathers.append(f'<path d="M{x0 - 3},-74 Q{pt(lft)} {pt(tip)} Q{pt(rgt)} {x0 + 3},-74Z" fill="{fg}" {STROKE} stroke-width="1.2"/>'
                                f'<path d="M{x0},-74 Q{pt(ctrl)} {pt(tip)}" fill="none" stroke="#7b8bb0" stroke-opacity="0.6" stroke-width="1"/>')
            ring = s.lin((-14, -84), (10, -68), [(0, C["metal"][0], None), (0.5, C["metal"][1], None), (1, C["metal"][2], None)])
            out.append("".join(feathers) +
                       f'<path d="M-16,-70 L-13,-84 C-6,-90 4,-90 10,-84 L12,-70 C4,-66 -8,-66 -16,-70Z" fill="{ring}" {STROKE} stroke-width="1.5"/>'
                       f'<circle cx="-2" cy="-78" r="3.6" fill="#dc2626" {STROKE} stroke-width="1"/><circle cx="-3" cy="-79" r="1.2" fill="#fecaca"/>'
                       f'<path d="M-15,-73 H11" stroke="#fff7d1" stroke-width="1.2" stroke-opacity="0.8"/>')
        elif hd == "mianliu":
            # 면류관(冕旒冠): 평판(검은 겉 · 붉은 속) + 앞뒤로 늘어진 구슬 줄
            board = s.lin((-30, -100), (40, -86), [(0, "#1f2937", None), (1, "#0b0f16", None)])
            out.append(f'<path d="M-8,-66 L-6,-88 L12,-88 L14,-66Z" fill="#1f2433" {STROKE} stroke-width="1.4"/>'
                       f'<path d="M-6,-80 H12" stroke="{C["metal"][1]}" stroke-width="2"/>'
                       f'<path d="M-30,-96 L42,-90 L40,-84 L-32,-90Z" fill="{board}" {STROKE} stroke-width="1.6"/>'
                       f'<path d="M-31,-90 L40,-84" stroke="{C["accent"][1]}" stroke-width="2.4"/>'
                       f'<path d="M-24,-92 L-40,-70" stroke="{C["metal"][1]}" stroke-width="2"/>')
            for k in range(6):
                x = 18 + k * 4.2
                y0 = -87 + k * 0.5
                beads = "".join(f'<circle cx="{f(x + 0.4 * j)}" cy="{f(y0 + 6 + j * 6.2)}" r="2" fill="{["#fde68a", "#ef4444", "#22c55e"][j % 3]}" {STROKE} stroke-width="0.6"/>' for j in range(4))
                out.append(f'<path d="M{f(x)},{f(y0)} V{f(y0 + 28)}" stroke="#d1d5db" stroke-width="0.8"/>' + beads)
            for k in range(4):
                x = -28 + k * 4.4
                y0 = -92 + k * 0.5
                beads = "".join(f'<circle cx="{f(x)}" cy="{f(y0 + 6 + j * 6.2)}" r="2" fill="{["#fde68a", "#ef4444", "#22c55e"][j % 3]}" {STROKE} stroke-width="0.6"/>' for j in range(3))
                out.append(f'<path d="M{f(x)},{f(y0)} V{f(y0 + 22)}" stroke="#d1d5db" stroke-width="0.8"/>' + beads)
        wind = P.get("wind", 0.4)
        fs = P.get("front_sway", 0.0)
        if hd != "mianliu":
            for (x0, y0, x1, y1, w) in ((12, -50, 2 - wind * 6 + fs * 8, 6, 5.2), (6, -50, -6 - wind * 8 + fs * 10, 12, 6.0)):
                mx, my = (x0 + x1) / 2 + 5, (y0 + y1) / 2
                out.append(f'<path d="M{x0 - w / 2},{y0} Q{mx - w},{my} {x1},{y1} Q{mx + w * 0.3},{my} {x0 + w / 2},{y0}Z" fill="{C["hair"][1]}" {STROKE} stroke-width="1.2"/>')
            out.append(f'<path d="M24,-52 Q{f(30 - wind * 10 + fs * 6)},-44 {f(27 - wind * 12 + fs * 8)},-34" fill="none" stroke="{C["hair"][1]}" stroke-width="2.4" stroke-linecap="round"/>')
        out.append("</g>")
        return "".join(out)

    def build(self, extra_back="", extra_front="", wrap=None):
        C, P = self.C, self.P
        b = []
        b.append(self.cape())
        b.append(self.back_hair())
        b.append(extra_back)
        b.append(self.arm(self.sh_f, self.el_f, self.ha_f, near=False, fist=not self.far_on_hilt or True))
        if not C["robe"]:
            b.append(self.tasset(self.hip_f, self.kn_f, near=False))
            b.append(self.leg(self.hip_f, self.kn_f, self.an_f, P.get("foot_f", 0), near=False))
            b.append(self.leg(self.hip_n, self.kn_n, self.an_n, P.get("foot_n", 0), near=True))
        else:
            b.append(self.leg(self.hip_f, self.kn_f, self.an_f, P.get("foot_f", 0), near=False))
            b.append(self.leg(self.hip_n, self.kn_n, self.an_n, P.get("foot_n", 0), near=True))
            b.append(self.robe_lower())
        b.append(self.torso())
        if not C["robe"]:
            b.append(self.tasset(self.hip_n, self.kn_n, near=True))
        b.append(self.pauldron(self.sh_f, self.el_f, dark=0.18))
        b.append(self.head())
        b.append(self.arm(self.sh_n, self.el_n, self.ha_n, near=True, fist=P.get("near_fist", False)))
        b.append(extra_front)
        inner = "".join(b)
        if wrap:
            inner = f'<g transform="{wrap}">{inner}</g>'
        defs = defs_static(C) + "".join(self.s.defs)
        self.info.update({"grip": [round(self.grip[0], 1), round(self.grip[1], 1)], "sword": round(self.sword, 1), "flip": 1 if self.side < 0 else 0})
        return defs, f'<g filter="url(#ol)">{inner}</g>'


def fist_svg(s, C, at, deg):
    sk = s.lin((-9, 0), (9, 0), [(0, C["skin"][2], None), (0.6, C["skin"][1], None), (1, C["skin"][0], None)])
    return (g_open(at, deg) + f'<path d="M-9,-2 C-11,6 -9,15 -2,17 C5,18 10,13 10,5 C10,-1 7,-4 0,-4 C-4,-4 -8,-4 -9,-2Z" fill="{sk}" {STROKE} stroke-width="1.5"/>'
            f'<path d="M-6,5 C-2,8 3,8 7,6 M-5,10 C-1,12 3,12 6,10" fill="none" stroke="{C["skin"][2]}" stroke-width="1.1"/></g>')


# ───────────────────────── 무기 스프라이트(검 + 쥔 주먹) ─────────────────────────
WEAPONS = {
    "cjg": {
        1: dict(name="결사대 흑철 장검", blade=("#e8edf2", "#8a95a2", "#2a3038"), edge="#f8fafc", glow=None, L=196, w=13, guard="#3b424c", grip="#1c1d22", pommel="#7c8592", tassel=None),
        2: dict(name="별무반 신기군 장검", blade=("#eaf4ff", "#8fb6e6", "#1e3a8a"), edge="#bfdbfe", glow="#60a5fa", L=204, w=13.5, guard="#d8b878", grip="#1e3a8a", pommel="#d8b878", tassel="#2563eb"),
        3: dict(name="화통도감 화약 장검", blade=("#fff1d6", "#a8a29e", "#292524"), edge="#fb923c", glow="#f97316", L=212, w=14.5, guard="#b45309", grip="#7f1d1d", pommel="#f59e0b", tassel="#dc2626", ember=True),
    },
    "haemosu": {
        1: dict(name="해모수의 용광검", blade=("#fff7d1", "#e0b84a", "#7a5a14"), edge="#fffbeb", glow="#fde68a", L=184, w=14, guard="#d9a83a", grip="#7f1d1d", pommel="#dc2626", tassel=None, dragon=True),
        2: dict(name="세형 동검의 용광검", blade=("#e6fffb", "#5fb8a8", "#1f5f58"), edge="#99f6e4", glow="#2dd4bf", L=192, w=12, guard="#c9a14a", grip="#134e4a", pommel="#2dd4bf", tassel=None, dragon=True, notch=True),
        3: dict(name="고조선 철제 용광검", blade=("#f1f5f9", "#7d8794", "#262c35"), edge="#fdba74", glow="#f97316", L=206, w=14.5, guard="#78350f", grip="#450a0a", pommel="#f97316", tassel="#b91c1c", dragon=True, ember=True),
    },
}


def weapon_svg(kind, tier, C):
    W = WEAPONS[kind][tier]
    s = SVG()
    L, w = W["L"], W["w"]
    o = []
    # 은은한 날 광채(등급 2 · 3)
    if W["glow"]:
        o.append(f'<path d="M22,0 L{L - 10},{-w * 0.32} L{L + 8},0 L{L - 10},{w * 0.32}Z" fill="{W["glow"]}" opacity="0.55" filter="url(#glow4)"/>')
    bl = s.lin((0, -w), (0, w), [(0, W["blade"][0], None), (0.47, W["blade"][1], None), (0.53, W["blade"][2], None), (1, W["blade"][1], None)])
    if W.get("notch"):
        d = f"M20,{-w * 0.42} L60,{-w * 0.5} L66,{-w * 0.22} L72,{-w * 0.5} L{L - 14},{-w * 0.3} L{L + 6},0 L{L - 14},{w * 0.3} L72,{w * 0.5} L66,{w * 0.22} L60,{w * 0.5} L20,{w * 0.42}Z"
    else:
        d = f"M20,{-w * 0.48} L{L - 16},{-w * 0.42} L{L + 6},0 L{L - 16},{w * 0.42} L20,{w * 0.48}Z"
    o.append(f'<path d="{d}" fill="{bl}" {STROKE} stroke-width="1.8"/>')
    o.append(f'<path d="M24,{-w * 0.08} L{L - 6},{-w * 0.04}" stroke="{W["edge"]}" stroke-width="1.6" opacity="0.9"/>')
    o.append(f'<path d="M26,{-w * 0.38} L{L - 18},{-w * 0.33}" stroke="{W["edge"]}" stroke-width="1.1" opacity="0.7"/>')
    if W.get("ember"):
        for k in range(7):
            x = 40 + k * (L - 60) / 6
            o.append(f'<circle cx="{f(x)}" cy="{f(-w * 0.45 - (k % 3))}" r="{1.2 + (k % 2) * 0.8}" fill="#fdba74" opacity="0.9"/>')
    # 코등이(가드)
    gd = s.lin((10, -20), (22, 20), [(0, "#ffffff", None), (0.3, W["guard"], None), (1, "#1c1917", None)])
    if W.get("dragon"):
        o.append(f'<path d="M12,-20 C20,-24 28,-18 26,-10 C30,-8 30,8 26,10 C28,18 20,24 12,20 C16,10 16,-10 12,-20Z" fill="{gd}" {STROKE} stroke-width="1.6"/>'
                 f'<circle cx="22" cy="-12" r="2" fill="#dc2626"/><path d="M24,-6 L32,-2 L24,2" fill="none" stroke="#fff7d1" stroke-width="1.2"/>')
    else:
        o.append(f'<rect x="12" y="-17" width="10" height="34" rx="4" fill="{gd}" {STROKE} stroke-width="1.6"/>')
    # 손잡이 + 끈 감김 + 폼멜
    o.append(f'<rect x="-30" y="-6" width="44" height="12" rx="4" fill="{W["grip"]}" {STROKE} stroke-width="1.5"/>'
             + "".join(f'<path d="M{-26 + k * 7},-6 l4,12" stroke="#ffffff" stroke-opacity="0.25" stroke-width="1.4"/>' for k in range(6)))
    po = s.rad((-34, -2), 9, [(0, "#ffffff", None), (0.4, W["pommel"], None), (1, "#1c1917", None)])
    o.append(f'<circle cx="-34" cy="0" r="7.5" fill="{po}" {STROKE} stroke-width="1.5"/>')
    if W["tassel"]:
        o.append("".join(f'<path d="M-36,4 q{-4 + k * 3},14 {-8 + k * 5},30" fill="none" stroke="{W["tassel"]}" stroke-width="2.8" stroke-linecap="round"/>' for k in range(4)))
    # 쥔 주먹(가까운 손) — 손잡이 위
    o.append(fist_svg(s, C, (0, -6), 0))
    return s, "".join(o), W


# ───────────────────────── 동작 ─────────────────────────
def ground_ank(x, lift=0):
    return (x, GROUND - ANKLE_H - 3 - lift)


def hero_poses(kind):
    P = {}
    P["idle"] = dict(pelvis=(230, 297), lean=5, neck=-2, head=-3, ank_n=ground_ank(190), ank_f=ground_ank(278), foot_n=-4, foot_f=2,
                     grip=(268, 236), sword=-32, hand_f="two", wind=0.22, hair_ph=0.1, elbow_n=0.5, elbow_f=0.6)

    def run(i):
        ph = i / 8.0
        bx = 236
        pel_y = 291 - 4.5 * math.cos(4 * math.pi * (ph - 0.12))

        def leg(phase):
            u = phase % 1.0
            if u < 0.42:
                t = u / 0.42
                x = 50 - 96 * t
                if t < 0.15:
                    fdeg = -16 + 16 * t / 0.15
                elif t < 0.7:
                    fdeg = 0
                else:
                    fdeg = 26 * (t - 0.7) / 0.3
                lift = 0 if t < 0.7 else 9 * (t - 0.7) / 0.3
                return ground_ank(bx + x, lift), fdeg
            t = (u - 0.42) / 0.58
            sm = t * t * (3 - 2 * t)
            x = -46 + 96 * sm
            lift = 58 * math.sin(math.pi * t) ** 0.85 + (24 * (1 - t / 0.4) if t < 0.4 else 0)
            fdeg = 34 * (1 - t) - 16 * t
            return ground_ank(bx + x, lift), fdeg

        an_n, fn = leg(ph)
        an_f, ff = leg(ph + 0.5)
        sw = math.cos(2 * math.pi * ph)
        far_hand = polar((bx + 40, pel_y - 130), 90 - 52 * sw, 54)
        far_hand = (far_hand[0] + 10, far_hand[1] + 6 + 10 * abs(sw))
        grip = (bx - 6 + 8 * sw, pel_y - 26 + 3 * math.sin(4 * math.pi * ph))
        return dict(pelvis=(bx, pel_y), lean=12 + 1.6 * math.sin(4 * math.pi * ph), neck=-6, head=-2 - 1.5 * math.sin(4 * math.pi * ph),
                    ank_n=an_n, ank_f=an_f, foot_n=fn, foot_f=ff, grip=grip, sword=166 + 6 * sw, hand_f=far_hand,
                    shoulder_shift=-3 * sw, wind=0.95, hair_ph=ph - 0.12, front_sway=-0.3, elbow_n=0.2, elbow_f=0.9, wrist_side=-1)

    for i, n in enumerate(["run", "run2", "run3", "run4", "run5", "run6", "run7", "run8"]):
        P[n] = run(i)
    # 내려베기
    P["atk_prep"] = dict(pelvis=(220, 302), lean=-8, neck=4, head=-6, ank_n=ground_ank(170), ank_f=ground_ank(272), foot_n=-12, foot_f=4,
                         grip=(214, 168), sword=-150, hand_f=(286, 232), wind=0.1, hair_ph=0.3, elbow_n=0.9, elbow_f=0.2, wrist_side=1)
    P["atk1"] = dict(pelvis=(234, 302), lean=8, neck=-4, head=-4, ank_n=ground_ank(176), ank_f=ground_ank(296), foot_n=-14, foot_f=4,
                     grip=(282, 196), sword=-58, hand_f=(250, 268), wind=0.45, hair_ph=0.45, elbow_n=0.2, elbow_f=0.5, expr="shout")
    P["atk1_2"] = dict(pelvis=(244, 304), lean=14, neck=-8, head=-2, ank_n=ground_ank(168), ank_f=ground_ank(310), foot_n=-20, foot_f=4,
                       grip=(316, 228), sword=-6, hand_f=(246, 274), wind=0.7, hair_ph=0.6, elbow_n=0.05, elbow_f=0.6, expr="shout")
    P["atk1_3"] = dict(pelvis=(250, 308), lean=18, neck=-10, head=0, ank_n=ground_ank(164), ank_f=ground_ank(316), foot_n=-24, foot_f=4,
                       grip=(306, 266), sword=46, hand_f=(240, 270), wind=0.85, hair_ph=0.75, elbow_n=0.1, elbow_f=0.7)
    # 올려베기
    P["atk2_prep"] = dict(pelvis=(222, 304), lean=6, neck=0, head=-2, ank_n=ground_ank(172), ank_f=ground_ank(282), foot_n=-8, foot_f=2,
                          grip=(204, 282), sword=158, hand_f=(282, 232), wind=0.2, hair_ph=0.2, elbow_n=0.6, elbow_f=0.3, wrist_side=-1)
    P["atk2"] = dict(pelvis=(236, 304), lean=10, neck=-4, head=-2, ank_n=ground_ank(176), ank_f=ground_ank(298), foot_n=-12, foot_f=4,
                     grip=(282, 270), sword=34, hand_f=(250, 250), wind=0.5, hair_ph=0.45, elbow_n=0.3, elbow_f=0.5, expr="shout")
    P["atk2_2"] = dict(pelvis=(244, 300), lean=4, neck=-10, head=-6, ank_n=ground_ank(172), ank_f=ground_ank(304), foot_n=-16, foot_f=4,
                       grip=(306, 216), sword=-38, hand_f=(244, 246), wind=0.65, hair_ph=0.6, elbow_n=0.1, elbow_f=0.6, expr="shout")
    P["atk2_3"] = dict(pelvis=(246, 296), lean=-4, neck=-14, head=-10, ank_n=ground_ank(176), ank_f=ground_ank(300), foot_n=-12, foot_f=4,
                       grip=(286, 160), sword=-84, hand_f=(240, 250), wind=0.7, hair_ph=0.8, elbow_n=0.3, elbow_f=0.6)
    # 4타 피니시: 양손 대도 내리찍기
    P["atk3_prep"] = dict(pelvis=(222, 296), lean=-10, neck=6, head=-10, ank_n=ground_ank(174), ank_f=ground_ank(280), foot_n=-6, foot_f=2,
                          grip=(232, 128), sword=-118, hand_f="two", wind=0.2, hair_ph=0.3, elbow_n=0.9, elbow_f=0.9)
    P["atk3"] = dict(pelvis=(236, 302), lean=6, neck=-2, head=-4, ank_n=ground_ank(178), ank_f=ground_ank(300), foot_n=-12, foot_f=4,
                     grip=(286, 170), sword=-48, hand_f="two", wind=0.5, hair_ph=0.45, elbow_n=0.4, elbow_f=0.6, expr="shout")
    P["atk3_2"] = dict(pelvis=(248, 312), lean=18, neck=-10, head=-2, ank_n=ground_ank(166), ank_f=ground_ank(318), foot_n=-22, foot_f=4,
                       grip=(318, 236), sword=8, hand_f="two", wind=0.8, hair_ph=0.6, elbow_n=0.1, elbow_f=0.3, expr="shout")
    P["atk3_3"] = dict(pelvis=(252, 324), lean=26, neck=-14, head=4, ank_n=ground_ank(160), ank_f=ground_ank(320), foot_n=-28, foot_f=4,
                       grip=(312, 290), sword=52, hand_f="two", wind=0.9, hair_ph=0.75, elbow_n=0.1, elbow_f=0.3)
    P["hit"] = dict(pelvis=(222, 300), lean=-16, neck=8, head=12, expr="hurt", ank_n=ground_ank(186), ank_f=ground_ank(268, 16), foot_n=-6, foot_f=-18,
                    grip=(222, 270), sword=128, hand_f=(262, 214), wind=-0.4, hair_ph=0.9, front_sway=0.9, elbow_n=0.5, elbow_f=0.8, wrist_side=-1)
    return P


def boss_poses():
    P = {}
    base = dict(head=-2, neck=-2, wind=0.15, hair_ph=0.1)
    P["idle"] = dict(base, pelvis=(232, 296), lean=-2, ank_n=ground_ank(204), ank_f=ground_ank(262), grip=(252, 286), sword=52, hand_f=(282, 248), elbow_n=0.6, elbow_f=0.4, near_fist=False)
    P["walk1"] = dict(base, pelvis=(234, 292), lean=2, ank_n=ground_ank(196), ank_f=ground_ank(278, 6), foot_f=-8, grip=(246, 274), sword=128, hand_f=(286, 250), robe_sway=3, elbow_n=0.6, elbow_f=0.4)
    P["walk2"] = dict(base, pelvis=(234, 292), lean=2, ank_n=ground_ank(214, 6), ank_f=ground_ank(268), foot_n=-8, grip=(252, 276), sword=124, hand_f=(280, 246), robe_sway=-3, elbow_n=0.6, elbow_f=0.4)
    P["slash"] = dict(base, pelvis=(244, 300), lean=14, neck=-6, ank_n=ground_ank(176), ank_f=ground_ank(304), foot_n=-18, grip=(320, 222), sword=-4, hand_f=(248, 270), robe_sway=6, expr="shout", elbow_n=0.05, elbow_f=0.6)
    P["command"] = dict(base, pelvis=(230, 296), lean=-4, neck=-4, head=-6, ank_n=ground_ank(196), ank_f=ground_ank(272), grip=(244, 280), sword=128, hand_f=(330, 176), robe_sway=2, expr="shout", elbow_n=0.6, elbow_f=-0.3)
    P["hit"] = dict(base, pelvis=(222, 298), lean=-14, neck=8, head=10, expr="hurt", ank_n=ground_ank(196), ank_f=ground_ank(262, 10), grip=(226, 280), sword=126, hand_f=(262, 214), robe_sway=-6, elbow_n=0.5, elbow_f=0.8)
    return P


def boss_sword(s, C, grip, deg):
    W = dict(blade=("#f1f5f9", "#9aa5b3", "#2a3038"), L=230, w=16)
    L, w = W["L"], W["w"]
    bl = s.lin((0, -w), (0, w), [(0, W["blade"][0], None), (0.47, W["blade"][1], None), (0.53, W["blade"][2], None), (1, W["blade"][1], None)])
    o = [g_open(grip, deg)]
    o.append(f'<path d="M20,{-w * 0.48} L{L - 16},{-w * 0.42} L{L + 6},0 L{L - 16},{w * 0.42} L20,{w * 0.48}Z" fill="{bl}" {STROKE} stroke-width="1.8"/>'
             f'<path d="M24,{-w * 0.08} L{L - 6},{-w * 0.04}" stroke="#ffffff" stroke-width="1.6" opacity="0.9"/>'
             f'<path d="M12,-20 C22,-24 26,-12 24,0 C26,12 22,24 12,20 C16,10 16,-10 12,-20Z" fill="{C["metal"][1]}" {STROKE} stroke-width="1.6"/>'
             f'<rect x="-34" y="-6" width="48" height="12" rx="4" fill="#3b0d0d" {STROKE} stroke-width="1.5"/>'
             f'<circle cx="-38" cy="0" r="8" fill="none" stroke="{C["metal"][1]}" stroke-width="4"/><circle cx="-38" cy="0" r="8" fill="none" stroke="{INK}" stroke-width="1"/>')
    o.append(fist_svg(s, C, (0, -6), 0))
    o.append("</g>")
    return "".join(o)


def svg_doc(w, h, defs, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'


def main():
    out, kind = sys.argv[1], sys.argv[2]
    only = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    C = COSTUMES[kind]
    meta = {"kind": kind, "frames": {}, "weapons": {}}
    if kind in ("cjg", "haemosu"):
        P = hero_poses(kind)
        for name, pose in P.items():
            if only and name not in only:
                continue
            fg = Fig(C, pose)
            defs, body = fg.build()
            with open(os.path.join(out, name + ".svg"), "w", encoding="utf-8") as fh:
                fh.write(svg_doc(512, 512, defs, body))
            g = fg.info["grip"]
            meta["frames"][name] = {"grip": g, "ang": fg.info["sword"], "flip": fg.info["flip"]}
        for tier in (1, 2, 3):
            s, body, W = weapon_svg(kind, tier, C)
            # 무기 캔버스: 손잡이 중심(0,0)을 (70, 60)에 — 가로 70 + L + 30
            wdt = int(70 + W["L"] + 40)
            doc = svg_doc(wdt, 120, defs_static(C) + "".join(s.defs), f'<g transform="translate(70,60)"><g filter="url(#ol)">{body}</g></g>')
            with open(os.path.join(out, f"weapon_t{tier}.svg"), "w", encoding="utf-8") as fh:
                fh.write(doc)
            meta["weapons"][tier] = {"name": W["name"], "w": wdt, "h": 120, "gx": 70, "gy": 60, "L": W["L"], "glow": W["glow"]}
    else:
        P = boss_poses()
        for name, pose in P.items():
            if only and name not in only:
                continue
            fg = Fig(C, pose)
            sw = boss_sword(fg.s, C, fg.grip, fg.sword)
            defs, body = fg.build(extra_front=sw)
            # 보스 캔버스 768×640 · 접지선 600 · 1.36배
            S = 1.24
            wrap = f"translate({f(384 - 232 * S)},{f(600 - 470 * S)}) scale({S})"
            body = f'<g transform="{wrap}">{body}</g>'
            with open(os.path.join(out, name + ".svg"), "w", encoding="utf-8") as fh:
                fh.write(svg_doc(768, 640, defs, body))
            meta["frames"][name] = {"grip": [round(384 + (fg.grip[0] - 232) * S, 1), round(600 + (fg.grip[1] - 470) * S, 1)], "ang": fg.info["sword"]}
    with open(os.path.join(out, "rig.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(kind, "frames", len(meta["frames"]), "weapons", len(meta["weapons"]))


if __name__ == "__main__":
    main()
