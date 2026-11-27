#!/usr/bin/env python3
"""R34 음향 — 환경음 루프 4종 · 천둥 2종 · 전선 보스 뿔나팔을 수식으로 합성한다(녹음 소스 없음 · 시드 고정 → 다시 만들어도 같은 파일).

  amb_rain_loop      1전선 거란 폭우        잡음 빗소리 + 빗방울 알갱이 + 낮은 바닥 울림
  amb_blizzard_loop  2전선 여진 눈보라      돌풍 봉투선 + 휘파람처럼 오르내리는 바람 울음 + 눈 쓸리는 소리
  amb_wind_loop      3전선 몽골 황야 바람   낮고 마른 바람 + 모래 쓸리는 소리
  amb_fire_loop      4전선 개경 화염        낮은 불길 포효 + 탁탁 튀는 불티
  thunder_crack_1    가까운 벼락(쩍 갈라지는 소리 + 우르릉)
  thunder_roll_2     먼 천둥(구르는 우르릉)
  war_horn_call      전선 보스 등장 뿔나팔(나각 · 대각) — 낮은 금관 합주 한 번 길게

루프는 모두 '주기 신호'로 만든다: 잡음은 주파수 영역에서 무작위 위상으로 합성(끝과 처음이 이어짐) ·
알갱이는 끝을 넘으면 처음으로 감기 · 잔향은 원형 합성곱 · 봉투선은 정수 주기 사인 합.

사용: python3 -I tools/r34/synth_audio.py <출력 폴더(assets/sfx)> [검증 시트 png]
형식: 22050Hz · 16bit · 모노(기존 효과음과 같음)
"""
import os
import sys
import wave

import numpy as np

SR = 22050
OUT = sys.argv[1]
SHEET = sys.argv[2] if len(sys.argv) > 2 else None
TAU = 2 * np.pi


def pnoise(n, shape, rng):
    """주기 잡음: 크기 스펙트럼 shape(f) · 무작위 위상."""
    f = np.fft.rfftfreq(n, 1 / SR)
    mag = shape(np.maximum(f, 1e-6))
    mag[0] = 0
    ph = rng.uniform(0, TAU, len(f))
    x = np.fft.irfft(mag * np.exp(1j * ph), n)
    return x / (np.sqrt(np.mean(x * x)) + 1e-12)


def lp(f, fc, order=4):
    return 1 / np.sqrt(1 + (f / fc) ** (2 * order))


def hp(f, fc, order=4):
    return 1 / np.sqrt(1 + (fc / f) ** (2 * order))


def bp(f, f0, q):
    return 1 / np.sqrt(1 + (q * (f / f0 - f0 / f)) ** 2)


def env_cycles(n, comps, rng, base=1.0):
    """정수 주기 사인 합 봉투선(루프 길이에 딱 맞음)."""
    t = np.arange(n) / n
    e = np.full(n, base)
    for cyc, amp in comps:
        e += amp * np.sin(TAU * cyc * t + rng.uniform(0, TAU))
    return e


def slow_noise_env(n, fc, rng):
    """천천히 흔들리는 0~1 봉투선(주기)."""
    x = pnoise(n, lambda f: lp(f, fc, 2), rng)
    x = (x - x.min()) / (x.max() - x.min() + 1e-12)
    return x


def add_wrap(buf, pos, grain):
    n = len(buf)
    idx = (pos + np.arange(len(grain))) % n
    np.add.at(buf, idx, grain)


def reverb_ir(seconds, t60, rng, bright=6000.0):
    m = int(SR * seconds)
    t = np.arange(m) / SR
    ir = rng.standard_normal(m) * np.exp(-6.91 * t / t60)
    F = np.fft.rfft(ir)
    f = np.fft.rfftfreq(m, 1 / SR)
    ir = np.fft.irfft(F * lp(np.maximum(f, 1e-6), bright, 1) * hp(np.maximum(f, 1e-6), 120, 1), m)
    ir[: int(SR * 0.004)] *= np.linspace(0, 1, int(SR * 0.004))
    return ir / np.sqrt(np.sum(ir * ir))


def circ_reverb(x, ir, wet):
    n = len(x)
    h = np.zeros(n)
    h[: min(n, len(ir))] = ir[: min(n, len(ir))]
    y = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(h), n)
    y *= np.sqrt(np.mean(x * x)) / (np.sqrt(np.mean(y * y)) + 1e-12)
    return x * (1 - wet) + y * wet


def lin_reverb(x, ir, wet, tail):
    n = len(x) + int(SR * tail)
    m = 1
    while m < n + len(ir):
        m *= 2
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:n]
    y *= np.sqrt(np.mean(x * x)) / (np.sqrt(np.mean(y[: len(x)] ** 2)) + 1e-12)
    d = np.zeros(n)
    d[: len(x)] = x
    return d * (1 - wet) + y * wet


def glide_voice(n, f0, glides, rng):
    """오르내리는 휘파람 음(주기): 주파수 = f0 · 2^(Σ a·sin(정수 주기)). 위상이 루프 끝에서 정수 바퀴가 되게 f0를 미세 조정."""
    t = np.arange(n) / n
    semi = np.zeros(n)
    for cyc, amp in glides:
        semi += amp * np.sin(TAU * cyc * t + rng.uniform(0, TAU))
    f = f0 * 2 ** (semi / 12)
    cyc_total = np.sum(f) / SR
    f *= np.round(cyc_total) / cyc_total
    ph = TAU * np.cumsum(f) / SR
    return np.sin(ph), f


def norm_rms(x, rms, knee=0.55, lim=0.9):
    """RMS를 맞추고, 무릎(knee)을 넘는 드문 뾰족한 알갱이만 부드럽게 눌러 준다(몸통은 그대로 · 클리핑 방지)."""
    x = x - np.mean(x)
    x = x * (rms / (np.sqrt(np.mean(x * x)) + 1e-12))
    a = np.abs(x)
    over = a > knee
    y = x.copy()
    y[over] = np.sign(x[over]) * (knee + (lim - knee) * np.tanh((a[over] - knee) / (lim - knee)))
    return y


def norm_peak(x, peak=0.94):
    return x * (peak / (np.max(np.abs(x)) + 1e-12))


def save(name, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    p = os.path.join(OUT, name + ".wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return p


RES = {}

# ───────── 1. 폭우 ─────────
rng = np.random.default_rng(3401)
n = int(SR * 8.0)
hiss = pnoise(n, lambda f: hp(f, 600, 2) * lp(f, 8000, 3) * f ** -0.32, rng)
mid = pnoise(n, lambda f: bp(f, 1400, 1.1), rng)
low = pnoise(n, lambda f: lp(f, 240, 2) * hp(f, 45, 2), rng)
gust = np.clip(env_cycles(n, [(1, 0.16), (3, 0.09), (7, 0.05)], rng), 0.55, 1.5)
drops = np.zeros(n)
for _ in range(1500):  # 잔 빗방울: 짧은 감쇠 사인 '톡'
    f0 = np.exp(rng.uniform(np.log(1800), np.log(7000)))
    tau = rng.uniform(0.0012, 0.005)
    m = int(SR * tau * 6)
    t = np.arange(m) / SR
    g = np.sin(TAU * f0 * t + rng.uniform(0, TAU)) * np.exp(-t / tau) * np.exp(rng.uniform(np.log(0.15), np.log(1.0)))
    add_wrap(drops, rng.integers(0, n), g)
for _ in range(70):  # 가까운 굵은 방울: 낮고 길게
    f0 = np.exp(rng.uniform(np.log(500), np.log(1500)))
    tau = rng.uniform(0.008, 0.02)
    m = int(SR * tau * 6)
    t = np.arange(m) / SR
    g = np.sin(TAU * f0 * (1 + 0.25 * np.exp(-t / 0.004)) * t) * np.exp(-t / tau) * rng.uniform(0.8, 2.0)
    add_wrap(drops, rng.integers(0, n), g)
drops /= np.sqrt(np.mean(drops * drops))
x = (hiss * 1.0 + mid * 0.42 + drops * 0.5) * gust + low * 0.3
x = circ_reverb(x, reverb_ir(0.6, 0.5, rng), 0.18)
RES["amb_rain_loop"] = norm_rms(x, 0.17)

# ───────── 2. 눈보라 ─────────
rng = np.random.default_rng(3402)
n = int(SR * 9.0)
gust = np.clip(env_cycles(n, [(1, 0.3), (2, 0.17), (5, 0.1), (9, 0.05)], rng, base=0.6), 0.14, 1.3)
body = pnoise(n, lambda f: bp(f, 420, 0.9) * lp(f, 2500, 2), rng)
rumble = pnoise(n, lambda f: lp(f, 150, 2) * hp(f, 35, 2), rng)
snow = pnoise(n, lambda f: hp(f, 2600, 2) * lp(f, 8500, 3), rng)
howl = np.zeros(n)
for f0, gl, a in [(520, [(1, 2.6), (3, 1.3), (4, 0.7)], 1.0), (760, [(2, 2.2), (3, 1.6), (7, 0.5)], 0.7), (1040, [(1, 1.8), (5, 1.4)], 0.42)]:
    s, f = glide_voice(n, f0, gl, rng)
    rough = 0.45 + 0.55 * slow_noise_env(n, 14, rng)        # 숨결처럼 거친 떨림
    swell = slow_noise_env(n, 0.5, rng) ** 1.6               # 가끔 세게 우는 구간
    howl += s * rough * swell * a
howl *= gust ** 1.5
howl /= np.sqrt(np.mean(howl * howl))
x = body * gust * 1.0 + rumble * (0.35 + 0.4 * gust) + snow * gust ** 2 * 0.32 + howl * 0.36
x = circ_reverb(x, reverb_ir(1.2, 1.0, rng, 4500), 0.3)
RES["amb_blizzard_loop"] = norm_rms(x, 0.16)

# ───────── 3. 황야 바람(낮고 마름) ─────────
rng = np.random.default_rng(3403)
n = int(SR * 9.0)
gust = np.clip(env_cycles(n, [(1, 0.26), (2, 0.2), (3, 0.1), (6, 0.06)], rng, base=0.62), 0.2, 1.3)
body = pnoise(n, lambda f: bp(f, 340, 0.7) * lp(f, 1700, 2), rng)
rumble = pnoise(n, lambda f: lp(f, 110, 2) * hp(f, 30, 2), rng)
sand = pnoise(n, lambda f: bp(f, 3800, 1.4), rng)
moan = np.zeros(n)
for f0, gl, a in [(262, [(1, 1.6), (2, 0.9)], 1.0), (392, [(1, 1.2), (3, 0.8)], 0.5)]:
    s, f = glide_voice(n, f0, gl, rng)
    moan += s * (0.5 + 0.5 * slow_noise_env(n, 9, rng)) * slow_noise_env(n, 0.4, rng) ** 1.4 * a
moan *= gust
moan /= np.sqrt(np.mean(moan * moan))
x = body * gust + rumble * (0.22 + 0.2 * gust) + sand * gust ** 2.4 * 0.2 + moan * 0.24
x = circ_reverb(x, reverb_ir(1.0, 0.9, rng, 2800), 0.25)
RES["amb_wind_loop"] = norm_rms(x, 0.16)

# ───────── 4. 화염 ─────────
rng = np.random.default_rng(3404)
n = int(SR * 8.0)
roar = pnoise(n, lambda f: f ** -0.75 * lp(f, 900, 2) * hp(f, 60, 2), rng)
flut = 0.55 + 0.45 * slow_noise_env(n, 7, rng)
mid = pnoise(n, lambda f: bp(f, 1300, 0.9), rng) * (0.4 + 0.6 * slow_noise_env(n, 3, rng))
crack = np.zeros(n)
for _ in range(210):  # 탁탁: 아주 짧은 잡음 알갱이
    tau = rng.uniform(0.0006, 0.003)
    m = int(SR * tau * 7) + 4
    t = np.arange(m) / SR
    g = rng.standard_normal(m) * np.exp(-t / tau)
    g = np.diff(g, prepend=0)                                 # 고역 강조
    a = min(6.0, rng.pareto(1.6) + 0.25)
    add_wrap(crack, rng.integers(0, n), g * a)
for _ in range(16):  # 가끔 크게 '퍽'
    tau = rng.uniform(0.006, 0.014)
    m = int(SR * tau * 7)
    t = np.arange(m) / SR
    f0 = rng.uniform(260, 620)
    g = (np.sin(TAU * f0 * t) * 0.7 + rng.standard_normal(m) * 0.5) * np.exp(-t / tau)
    add_wrap(crack, rng.integers(0, n), g * rng.uniform(2.5, 5.0))
crack /= np.sqrt(np.mean(crack * crack))
x = roar * flut * 1.0 + mid * 0.42 + crack * 0.55
x = circ_reverb(x, reverb_ir(0.5, 0.4, rng, 5000), 0.14)
RES["amb_fire_loop"] = norm_rms(x, 0.16)

# ───────── 5. 천둥 ─────────


def thunder(seed, dur, crack_amp, bumps, lp0, lp1, attack):
    rng = np.random.default_rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    # 우르릉: 낮은 잡음 × 여러 번 부푸는 봉투선
    base = rng.standard_normal(n)
    F = np.fft.rfft(base)
    f = np.maximum(np.fft.rfftfreq(n, 1 / SR), 1e-6)
    lo = np.fft.irfft(F * lp(f, lp1, 1) * hp(f, 40, 2) * f ** -0.35, n)
    hi = np.fft.irfft(F * lp(f, lp0, 2) * hp(f, 90, 2), n)
    lo /= np.sqrt(np.mean(lo * lo))
    hi /= np.sqrt(np.mean(hi * hi))
    e = np.zeros(n)
    for _ in range(bumps):
        t0 = rng.uniform(0.0, dur * 0.5)
        a = rng.uniform(0.45, 1.0) * np.exp(-t0 / (dur * 0.5))
        rise = rng.uniform(0.03, 0.12) + attack
        dec = rng.uniform(0.35, 0.9)
        k = t - t0
        e += a * np.where(k < 0, 0, np.minimum(1, k / rise) * np.exp(-np.maximum(0, k - rise) / dec))
    bright = np.exp(-t / (dur * 0.22))                         # 처음엔 밝고 갈수록 어둡게
    x += (lo * (1 - 0.6 * bright) + hi * 0.9 * bright) * e
    # 쩍 갈라지는 소리(가까운 벼락만)
    if crack_amp > 0:
        for _ in range(4):
            t0 = rng.uniform(0.0, 0.16)
            m = int(SR * 0.25)
            k = np.arange(m) / SR
            g = rng.standard_normal(m) * np.exp(-k / rng.uniform(0.02, 0.06))
            G = np.fft.rfft(g)
            fg = np.maximum(np.fft.rfftfreq(m, 1 / SR), 1e-6)
            g = np.fft.irfft(G * hp(fg, 350, 2) * lp(fg, 7000, 2), m)
            i0 = int(SR * t0)
            x[i0: i0 + m] += g[: n - i0][:m] * crack_amp * rng.uniform(0.6, 1.0) * 2.4
    # 배를 울리는 저음
    x += np.sin(TAU * (34 * t + 26 * 0.9 * (1 - np.exp(-t / 0.9)))) * np.exp(-t / (dur * 0.3)) * 0.5 * np.minimum(1, t / 0.05)
    x *= np.minimum(1, (dur - t) / 0.35)
    x = lin_reverb(x, reverb_ir(2.0, 1.8, rng, 2200), 0.35, 0.6)
    k = np.arange(len(x)) / SR
    x *= np.minimum(1, (len(x) / SR - k) / 0.5)
    return norm_peak(x, 0.94)


RES["thunder_crack_1"] = thunder(3411, 2.6, 1.0, 5, 1800, 260, 0.0)
RES["thunder_roll_2"] = thunder(3412, 3.2, 0.0, 7, 900, 330, 0.12)

# ───────── 6. 뿔나팔 ─────────
rng = np.random.default_rng(3421)
dur = 2.1
n = int(SR * dur)
t = np.arange(n) / SR
amp = np.minimum(1, t / 0.13) ** 0.8 * (1 + 0.1 * np.exp(-((t - 0.2) / 0.1) ** 2)) * (0.86 + 0.14 * np.minimum(1, t / 1.2)) * np.minimum(1, np.maximum(0, (dur - t) / 0.42)) ** 1.2
x = np.zeros(n)
for det, lev, f0 in [(-6, 1.0, 146.83), (0, 1.0, 146.83), (7, 0.9, 146.83), (3, 0.5, 73.42), (-4, 0.34, 220.0)]:
    cents = det - 70 * np.exp(-t / 0.07) + 7 * np.sin(TAU * 4.6 * t + rng.uniform(0, TAU)) * np.minimum(1, np.maximum(0, (t - 0.5) / 0.5)) - 14 * np.maximum(0, (t - (dur - 0.4)) / 0.4)
    f = f0 * 2 ** (cents / 1200)
    ph = TAU * np.cumsum(f) / SR + rng.uniform(0, TAU)
    v = np.zeros(n)
    for h in range(1, 27):
        fh = f0 * h
        if fh > 9500:
            break
        roll = 2.3 - 1.25 * amp                               # 세게 불수록 밝아진다(금관 특성)
        form = 1 + 1.6 * np.exp(-((fh - 620) / 330) ** 2) + 0.7 * np.exp(-((fh - 1350) / 420) ** 2)
        v += np.sin(h * ph + rng.uniform(0, TAU)) * h ** -roll * form
    x += v * lev
breath = rng.standard_normal(n)
B = np.fft.rfft(breath)
fb = np.maximum(np.fft.rfftfreq(n, 1 / SR), 1e-6)
breath = np.fft.irfft(B * bp(fb, 900, 0.8), n)
x = x / np.max(np.abs(x)) * amp + breath / np.max(np.abs(breath)) * amp * 0.035
x = lin_reverb(x, reverb_ir(1.8, 1.5, rng, 3200), 0.3, 0.9)
k = np.arange(len(x)) / SR
x *= np.minimum(1, (len(x) / SR - k) / 0.35)
RES["war_horn_call"] = norm_peak(x, 0.94)

# ───────── 저장 · 수치 검증 ─────────
os.makedirs(OUT, exist_ok=True)
print(f"{'파일':22s} 길이  peak   rms   이음매(끝→처음 / 평균 변화)  0~300Hz 300~2k 2k~11k 에너지비")
for name, x in RES.items():
    save(name, x)
    d = np.abs(np.diff(x))
    seam = abs(x[0] - x[-1]) / (np.mean(d) + 1e-12)
    S = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    tot = S.sum()
    b = [S[f < 300].sum() / tot, S[(f >= 300) & (f < 2000)].sum() / tot, S[f >= 2000].sum() / tot]
    loop = name.startswith("amb_")
    print(f"{name:22s} {len(x) / SR:4.1f}s {np.max(np.abs(x)):.2f}  {np.sqrt(np.mean(x * x)):.3f}  {('%.2f' % seam) if loop else '  — ':>6s}                   {b[0]:.2f}  {b[1]:.2f}  {b[2]:.2f}")

if SHEET:
    from PIL import Image, ImageDraw, ImageFont

    F = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 14)
    LAB = {"amb_rain_loop": "폭우(1전선 거란) — 고른 빗소리 + 빗방울 알갱이", "amb_blizzard_loop": "눈보라(2전선 여진) — 돌풍 + 오르내리는 바람 울음",
           "amb_wind_loop": "황야 바람(3전선 몽골) — 낮고 마른 바람", "amb_fire_loop": "화염(4전선 개경) — 낮은 불길 + 탁탁 불티",
           "thunder_crack_1": "가까운 벼락", "thunder_roll_2": "먼 천둥", "war_horn_call": "전선 보스 뿔나팔 — 배음이 층층이(금관)"}
    W, H = 620, 150
    sheet = Image.new("RGB", (2 * (W + 12) + 12, 4 * (H + 34) + 40), (18, 18, 22))
    dr = ImageDraw.Draw(sheet)
    dr.text((12, 8), "R34 합성 효과음 스펙트로그램(가로 = 시간 · 세로 = 0~11kHz · 밝을수록 큼) — 루프는 한 바퀴 반을 이어 붙여 이음매(흰 세로선)를 보임", fill=(240, 240, 240), font=F)
    for i, (name, x) in enumerate(RES.items()):
        loop = name.startswith("amb_")
        y = np.concatenate([x, x[: len(x) // 2]]) if loop else x
        win = 512
        hop = max(64, (len(y) - win) // W)
        fr = np.array([y[k: k + win] * np.hanning(win) for k in range(0, len(y) - win, hop)])
        S = 20 * np.log10(np.abs(np.fft.rfft(fr, axis=1)) + 1e-6)
        S = np.clip((S - S.max() + 78) / 78, 0, 1).T[::-1]
        im = Image.fromarray((S * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        col = Image.merge("RGB", (im.point(lambda v: min(255, int(v * 1.5))), im.point(lambda v: int(v * 0.85)), im.point(lambda v: int(255 - abs(v - 90) * 1.6) if v < 150 else int(v * 0.4))))
        ox = 12 + (i % 2) * (W + 12)
        oy = 40 + (i // 2) * (H + 34)
        sheet.paste(col, (ox, oy + 20))
        if loop:
            sx = ox + int(W * len(x) / len(y))
            dr.line([(sx, oy + 20), (sx, oy + 20 + H)], fill=(255, 255, 255), width=1)
        dr.text((ox, oy), f"{name}.wav — {LAB[name]}  ({len(x) / SR:.1f}s)", fill=(253, 224, 71), font=F)
    sheet.save(SHEET)
    print("sheet", SHEET, sheet.size)
