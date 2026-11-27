#!/usr/bin/env python3
"""R36 소리 — ① 둔기 타격음을 '퍽퍽'(둔탁하게)으로 다시 · ② 동물 울음 · 함성(몹의 존재감). 전부 수식 합성 · 시드 고정.

① 둔기(오너: "퍽퍽 둔탁한 소리가 나야 하는데 플라스틱과 쇠파이프 깡깡 소리가 거북해요")
   R35의 rock_* 는 '돌 맞부딪는 울림'(사인 배음 5개)과 '부스러기'(울리는 알갱이)가 들어 있어 파이프 · 플라스틱처럼 들렸다.
   → 300Hz 위에는 음높이가 들리는 울림을 하나도 두지 않는다. 잡음을 낮게 걸러 짧게 끊은 '퍽' + 낮은 몸통 '쿵'만.
     thud_hit_1/2   퍽(가벼운 타)          thud_heavy   퍼억(연타 마지막 타 · 강타)          thud_crush   쾅 + 땅 울림(내려찍기)

② 동물 · 함성(오너: "동물들은 소리가 없나요? 몹이 압도해 줘야 하는데")
   성대(떨리는 펄스 + 갈라짐) → 입(포먼트 공명) → 숨소리를 섞는 방식.
     wolf_howl 늑대 울음(멀리서 길게) · wolf_snarl 으르렁-컹 · wolf_yelp 깨갱
     hyena_cackle 하이에나 낄낄 · bear_roar 곰 포효 · bear_growl 곰 으르렁(공격)
     rhino_snort 코뿔소 콧김 + 낮은 울음 · beast_groan 큰 짐승 쓰러지는 신음
     tiger_roar 산군(호랑이) 포효 · tiger_snarl 산군 으르렁(공격)
     war_cry 병사들의 함성(2~6시대 웨이브 등장)

사용: python3 -I tools/r36/synth_r36.py <출력 폴더(assets/sfx)> [검증 시트 png]
형식: 22050Hz · 16bit · 모노. scipy 필요 — 게임 실행에는 필요 없음
"""
import os
import sys
import wave

import numpy as np
from scipy import signal

SR = 22050
TAU = 2 * np.pi


def ms(v):
    return int(round(SR * v / 1000.0))


def sec(v):
    return int(round(SR * v))


def bpf(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, min(hi, SR * 0.49)], btype='band', fs=SR, output='sos'), x)


def lpf(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, min(fc, SR * 0.49), btype='low', fs=SR, output='sos'), x)


def hpf(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype='high', fs=SR, output='sos'), x)


def tms(n):
    return np.arange(n) / SR * 1000.0


def env(n, tau, atk=1.0):
    t = tms(n)
    return np.minimum(1.0, t / max(atk, 1e-6)) * np.exp(-t / tau)


def env2(n, tau1, tau2, w=0.5, atk=1.5):
    t = tms(n)
    return np.minimum(1.0, t / max(atk, 1e-6)) * (w * np.exp(-t / tau1) + (1 - w) * np.exp(-t / tau2))


def nz(x):
    return x / (np.max(np.abs(x)) + 1e-12)


def soft(x, drive):
    return np.tanh(x * drive) / np.tanh(drive)


def tone_sweep(f0, f1, n, tau_f, tau_a, atk=1.0):
    f = f1 + (f0 - f1) * np.exp(-tms(n) / tau_f)
    return np.sin(np.cumsum(f) * TAU / SR) * env(n, tau_a, atk)


class Mix:
    def __init__(self, dur_ms, pre_ms=0):
        self.n = ms(dur_ms + pre_ms)
        self.pre = ms(pre_ms)
        self.b = np.zeros(self.n)

    def add(self, x, at_ms=0.0, gain_db=0.0):
        i = self.pre + ms(at_ms)
        g = 10 ** (gain_db / 20)
        if i < 0:
            x = x[-i:]
            i = 0
        j = min(self.n, i + len(x))
        if j > i:
            self.b[i:j] += x[:j - i] * g


def reverb(x, rng, ms_len=140, mix=0.12, lo=200, hi=4000):
    L = ms(ms_len)
    ir = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 5.0))
    ir = bpf(ir, lo, hi)
    ir /= np.sqrt(np.sum(ir * ir)) + 1e-12
    wet = signal.fftconvolve(x, ir)
    out = np.zeros(len(wet))
    out[:len(x)] = x
    return out + wet * mix


def finish(x, peak=0.89, fade_ms=12, hp=40):
    x = x - np.mean(x)
    x = hpf(x, hp)
    x = x / (np.max(np.abs(x)) + 1e-12)
    k = 0.7
    a = np.abs(x)
    over = a > k
    x[over] = np.sign(x[over]) * (k + (1 - k) * np.tanh((a[over] - k) / (1 - k) * 1.6) / np.tanh(1.6))
    x = x / (np.max(np.abs(x)) + 1e-12) * peak
    f = ms(fade_ms)
    x[-f:] *= np.linspace(1, 0, f) ** 2
    return x


# ───────────────────────── ① 둔기: 퍽 ─────────────────────────
def thud_core(rng, n_ms, body_lo, body_hi, tau1, tau2, low_f0, low_f1, low_tau, knock_db=-7.0, low_db=-13.0, puff_db=-7.0):
    """퍽: 공기 터지는 '퍼'(아주 짧은 낮은 잡음) + 살 · 가죽이 받는 몸통(낮게 거른 잡음) + 바닥까지 가는 낮은 쿵. 울리는 음(배음)은 없다."""
    n = ms(n_ms)
    out = np.zeros(n)
    # 공기 '퍼': 2ms에 올라 9ms에 사라짐 · 2.2kHz 위는 잘라 딱딱한 '틱'이 되지 않게
    puff = lpf(hpf(rng.standard_normal(n), 250), 2200, 3) * env(n, 9, 2.0)
    out += nz(puff) * 10 ** (puff_db / 20)
    # 몸통: 폭이 넓은(공명 없는) 띠 잡음 · 2단 감쇠
    body = bpf(rng.standard_normal(n), body_lo, body_hi, 2) * env2(n, tau1, tau2, 0.6, 2.5)
    out += nz(body)
    # 몸통 아랫부분(150~330Hz 잡음): 무게감 — 사인이 아니라 잡음이라 '통' 하고 울리지 않는다
    lowb = bpf(rng.standard_normal(n), 130, 330, 2) * env2(n, tau1 * 1.3, tau2 * 1.2, 0.5, 3.0)
    out += nz(lowb) * 0.9
    # 윗몸통(휴대폰 스피커용): 500~1400Hz 잡음을 아주 짧게 — 음높이 없이 '퍽'의 윤곽만
    knock = bpf(rng.standard_normal(n), 500, 1400, 1) * env(n, 13, 1.5)
    out += nz(knock) * 10 ** (knock_db / 20)
    # 낮은 쿵(이어폰 · 큰 스피커): 음높이가 빠르게 떨어지는 사인 하나(300Hz 아래라 '울림'이 아니라 '무게'로 들림)
    low = soft(tone_sweep(low_f0, low_f1, n, 28, low_tau, 1.5), 2.0)
    out += low * 10 ** (low_db / 20)
    return out


def make_thud_light(seed, pitch=1.0):
    rng = np.random.default_rng(seed)
    M = Mix(300, pre_ms=5)
    M.add(thud_core(rng, 280, 230 * pitch, 880 * pitch, 24, 62, 138 * pitch, 60 * pitch, 58), 0, 0)
    # 가죽 · 털이 스치는 아주 작은 꼬리
    tail = bpf(rng.standard_normal(ms(160)), 300, 1100) * env(ms(160), 42, 10)
    M.add(nz(tail), 12, -19)
    return finish(lpf(reverb(M.b, rng, 90, 0.07, 150, 1800), 3000, 2))


def make_thud_heavy(seed):
    rng = np.random.default_rng(seed)
    M = Mix(520, pre_ms=8)
    M.add(thud_core(rng, 460, 190, 760, 36, 105, 118, 46, 100, knock_db=-8.0, low_db=-10.0), 0, 0)
    # 뼈 · 나무가 꺾이는 마른 소리(잡음 알갱이 몇 개 · 낮게 거름 · 음높이 없음)
    n = ms(90)
    cr = np.zeros(n)
    for t0 in (4, 13, 21, 34):
        L = ms(rng.uniform(5, 9))
        i = ms(t0 + rng.uniform(-2, 2))
        cr[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 3.5)) * rng.uniform(0.5, 1.0)
    M.add(nz(bpf(cr, 600, 1900, 1)), 3, -13)
    # 한 박 늦게 바닥이 받는 쿵
    M.add(thud_core(rng, 260, 160, 520, 30, 80, 92, 42, 90, knock_db=-14.0, low_db=-9.0, puff_db=-16.0), 85, -8)
    return finish(lpf(reverb(M.b, rng, 150, 0.1, 120, 1600), 2800, 2))


def make_thud_crush(seed):
    rng = np.random.default_rng(seed)
    M = Mix(900, pre_ms=10)
    M.add(thud_core(rng, 620, 170, 700, 46, 150, 104, 38, 140, knock_db=-9.0, low_db=-9.0), 0, 0)
    # 땅 울림: 200Hz 아래 잡음이 길게
    n = ms(700)
    rum = lpf(rng.standard_normal(n), 190, 3) * env(n, 190, 12)
    M.add(soft(nz(rum), 2.0), 6, -12)
    # 흙 · 돌 부스러기: 낮게 거른 잡음을 잘게 부숴(음높이 없는 알갱이) 스르르 사라지게
    n = ms(760)
    g = np.zeros(n)
    t = 0.0
    while True:
        rate = 30 + 420 * np.exp(-t * 1000 / 150)
        t += rng.exponential(1.0 / rate)
        if t >= n / SR:
            break
        L = ms(rng.uniform(4, 11))
        i = int(t * SR)
        j = min(n, i + L)
        g[i:j] += (rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 3.0)))[:j - i] * rng.uniform(0.3, 1.0)
    M.add(nz(bpf(g, 260, 1500, 1) * np.exp(-tms(n) / 240)), 20, -11)
    M.add(thud_core(rng, 320, 150, 500, 34, 95, 84, 40, 110, knock_db=-15.0, low_db=-9.0, puff_db=-18.0), 150, -6)
    return finish(lpf(reverb(M.b, rng, 260, 0.14, 100, 1500), 2600, 2))


# ───────────────────────── ② 동물: 성대 → 입 → 숨 ─────────────────────────
def slow_noise(n, rate_hz, rng):
    """천천히 흔들리는 잡음(−1~1) — 떨림 · 불규칙함."""
    k = max(4, int(n / SR * rate_hz) + 4)
    pts = rng.standard_normal(k)
    return np.interp(np.arange(n) / SR * rate_hz, np.arange(k), pts)


def glottal(n, f0, rng, jitter=0.03, shimmer=0.12, sub=0.0, tilt=1100.0):
    """성대 펄스: 톱니 + 주기마다 흔들림(jitter · shimmer) + 한 주기 걸러 약해짐(sub = 갈라지는 목소리)."""
    f = f0 * (1 + jitter * slow_noise(n, 90, rng))
    ph = np.cumsum(f) / SR
    cyc = np.floor(ph).astype(int)
    nc = cyc.max() + 2
    amp = 1 + shimmer * rng.standard_normal(nc)
    if sub:
        amp[1::2] *= 1 - sub
    saw = 2 * (ph - np.floor(ph)) - 1
    src = saw * amp[cyc]
    return lpf(src, tilt, 1), ph


def formants(x, F):
    """입 모양 공명: [(중심Hz, 폭Hz, 크기)] 를 나란히 통과시켜 더한다."""
    out = np.zeros(len(x))
    for fc, bw, a in F:
        out += bpf(x, max(40, fc - bw / 2), fc + bw / 2, 1) * a
    return out


def voice(rng, dur, f0_pts, F_a, F_b=None, open_pts=None, rough=0.0, rough_hz=30.0, sub=0.0, breath=0.2, jitter=0.03, shimmer=0.12, tilt=1100.0, amp_pts=None, direct=0.12, breath_lp=2600.0):
    """울음 하나. f0_pts · amp_pts · open_pts = [(시각 0~1, 값)] 꺾은선. F_a → F_b 로 입이 벌어짐(open 0~1)."""
    n = sec(dur)
    u = np.arange(n) / n
    f0 = np.interp(u, [p[0] for p in f0_pts], [p[1] for p in f0_pts])
    src, ph = glottal(n, f0, rng, jitter, shimmer, sub, tilt)
    if rough:
        # 으르렁: 25~40Hz로 거칠게 떨리되 박자가 고르지 않게
        rf = rough_hz * (1 + 0.18 * slow_noise(n, 6, rng))
        tri = 0.5 + 0.5 * np.sin(np.cumsum(rf) * TAU / SR + rng.uniform(0, TAU))
        src = src * (1 - rough + rough * tri ** 1.6)
    # 숨소리: 성대가 열릴 때 더 새는 잡음
    turb = rng.standard_normal(n) * (0.55 + 0.45 * (0.5 + 0.5 * np.sin(TAU * ph)))
    ex = src + lpf(hpf(turb, 400), breath_lp, 2) * breath * 1.5
    ya = formants(ex, F_a)
    if F_b is not None:
        yb = formants(ex, F_b)
        op = np.interp(u, [p[0] for p in open_pts], [p[1] for p in open_pts]) if open_pts else u
        y = ya * (1 - op) + yb * op
    else:
        y = ya
    y = nz(y) + nz(lpf(src, 600, 1)) * direct
    a = np.interp(u, [p[0] for p in amp_pts], [p[1] for p in amp_pts]) if amp_pts else np.ones(n)
    return y * a


BIG = [(420, 240, 1.0), (980, 340, 0.75), (2300, 600, 0.2)]          # 큰 짐승 다문 입
BIG_OPEN = [(620, 280, 1.0), (1250, 400, 0.85), (2600, 700, 0.24)]      # 크게 벌린 입(아)
DOG = [(650, 260, 1.0), (1500, 420, 0.75), (2700, 700, 0.4)]
DOG_OPEN = [(850, 300, 1.0), (1750, 480, 0.8), (3000, 800, 0.45)]
NASAL = [(900, 240, 1.0), (1850, 380, 0.7), (3000, 700, 0.3)]


def make_wolf_howl(seed):
    rng = np.random.default_rng(seed)
    # 길게 올라가 머물다 내려오는 울음 — 맑은 소리(갈라짐 거의 없음) + 살짝 떨림
    v = voice(rng, 2.1, [(0, 290), (0.16, 470), (0.3, 520), (0.72, 505), (1.0, 360)], [(560, 320, 1.0), (1150, 420, 0.8), (2300, 700, 0.4)],
              rough=0.12, rough_hz=11, sub=0.0, breath=0.1, jitter=0.02, shimmer=0.07, tilt=1700, amp_pts=[(0, 0), (0.1, 0.7), (0.3, 1.0), (0.75, 0.85), (1.0, 0)], direct=0.1)
    # 멀리서 두 번째 늑대가 조금 늦게 화답
    v2 = voice(rng, 1.6, [(0, 330), (0.2, 560), (0.7, 540), (1.0, 400)], [(600, 320, 1.0), (1200, 420, 0.75), (2400, 700, 0.35)], rough=0.1, rough_hz=13, breath=0.1, jitter=0.02, shimmer=0.07, tilt=1700,
               amp_pts=[(0, 0), (0.15, 0.8), (0.7, 0.8), (1.0, 0)], direct=0.1)
    n = sec(2.5)
    x = np.zeros(n)
    x[:len(v)] += nz(v)
    i = sec(0.75)
    x[i:i + len(v2)] += nz(v2)[:n - i] * 0.38
    return finish(reverb(x, rng, 600, 0.4, 300, 3000), peak=0.85, fade_ms=120)


def make_wolf_snarl(seed):
    rng = np.random.default_rng(seed)
    # 으르르(낮게 떨다가) → 컹(짧게 벌림)
    g = voice(rng, 0.34, [(0, 118), (1, 138)], DOG, rough=0.75, rough_hz=34, sub=0.45, breath=0.28, jitter=0.05, shimmer=0.2, tilt=1500, amp_pts=[(0, 0), (0.15, 0.7), (0.9, 0.9), (1, 0.6)])
    b = voice(rng, 0.2, [(0, 230), (0.3, 210), (1, 130)], DOG, DOG_OPEN, [(0, 0.2), (0.25, 1), (1, 0.3)], rough=0.35, rough_hz=42, sub=0.3, breath=0.32, jitter=0.05, shimmer=0.2, tilt=1900,
              amp_pts=[(0, 0.5), (0.1, 1), (0.6, 0.6), (1, 0)])
    x = np.concatenate([nz(g) * 0.7, nz(b)])
    return finish(reverb(x, rng, 110, 0.1, 300, 3500))


def make_wolf_yelp(seed):
    rng = np.random.default_rng(seed)
    v = voice(rng, 0.26, [(0, 760), (0.12, 980), (1, 430)], [(1000, 420, 1.0), (2100, 600, 0.7), (3100, 800, 0.3)], rough=0.15, rough_hz=48, breath=0.16, jitter=0.03, shimmer=0.1, tilt=2600,
              amp_pts=[(0, 0), (0.08, 1), (0.5, 0.7), (1, 0)], direct=0.2)
    return finish(reverb(nz(v), rng, 140, 0.14, 400, 4000))


def make_hyena_cackle(seed):
    rng = np.random.default_rng(seed)
    # 낄-낄-낄: 짧게 치솟는 높은 소리 여섯 번(높이 · 간격이 들쭉날쭉)
    out = np.zeros(sec(1.15))
    t = 0.0
    for k in range(6):
        f = rng.uniform(430, 560) * (1 + 0.06 * k)
        d = rng.uniform(0.085, 0.12)
        y = voice(rng, d, [(0, f), (0.6, f * rng.uniform(1.45, 1.75)), (1, f * 1.2)], NASAL, rough=0.35, rough_hz=55, sub=0.3, breath=0.2, jitter=0.04, shimmer=0.14, tilt=2600,
                  amp_pts=[(0, 0), (0.15, 1), (0.7, 0.8), (1, 0)], direct=0.15)
        i = sec(t)
        out[i:i + len(y)] += nz(y) * rng.uniform(0.7, 1.0)
        t += d + rng.uniform(0.045, 0.085)
    return finish(reverb(out, rng, 160, 0.14, 400, 4000))


def make_bear_roar(seed):
    rng = np.random.default_rng(seed)
    v = voice(rng, 1.35, [(0, 82), (0.12, 104), (0.5, 96), (1, 68)], BIG, BIG_OPEN, [(0, 0), (0.18, 1), (0.6, 0.9), (1, 0.2)], rough=0.72, rough_hz=27, sub=0.5, breath=0.22, jitter=0.05, shimmer=0.22,
              tilt=1250, amp_pts=[(0, 0), (0.08, 0.6), (0.2, 1), (0.65, 0.85), (1, 0)], direct=0.2)
    x = nz(v)
    # 가슴 울림
    n = len(x)
    x += nz(lpf(np.abs(x), 60, 1) * np.sin(TAU * 52 * np.arange(n) / SR)) * 0.25
    return finish(reverb(x, rng, 420, 0.24, 150, 2800), fade_ms=60)


def make_bear_growl(seed):
    rng = np.random.default_rng(seed)
    v = voice(rng, 0.6, [(0, 88), (0.3, 112), (1, 80)], BIG, BIG_OPEN, [(0, 0), (0.3, 0.8), (1, 0.1)], rough=0.78, rough_hz=30, sub=0.5, breath=0.24, jitter=0.05, shimmer=0.22, tilt=1300,
              amp_pts=[(0, 0), (0.12, 1), (0.6, 0.8), (1, 0)], direct=0.2)
    return finish(reverb(nz(v), rng, 220, 0.16, 150, 2800), fade_ms=40)


def make_rhino_snort(seed):
    rng = np.random.default_rng(seed)
    # 푸르르(콧김) → 낮은 울음
    n = sec(0.28)
    pf = formants(rng.standard_normal(n), [(300, 200, 1.0), (760, 300, 0.8), (1700, 600, 0.4)])
    flap = 0.55 + 0.45 * np.sin(TAU * 24 * np.arange(n) / SR) ** 2
    sn = nz(pf * flap * env2(n, 60, 160, 0.5, 6))
    v = voice(rng, 0.5, [(0, 92), (0.4, 80), (1, 62)], [(300, 200, 1.0), (760, 300, 0.7), (1800, 600, 0.25)], rough=0.55, rough_hz=22, sub=0.4, breath=0.3, jitter=0.04, shimmer=0.18, tilt=900,
              amp_pts=[(0, 0), (0.15, 1), (0.6, 0.7), (1, 0)], direct=0.3)
    x = np.zeros(sec(0.72))
    x[:len(sn)] += sn * 0.9
    i = sec(0.16)
    x[i:i + len(v)] += nz(v)[:len(x) - i]
    return finish(reverb(x, rng, 260, 0.18, 120, 2400), fade_ms=40)


def make_beast_groan(seed):
    rng = np.random.default_rng(seed)
    v = voice(rng, 0.75, [(0, 128), (0.2, 118), (1, 58)], BIG_OPEN, BIG, [(0, 0), (1, 1)], rough=0.5, rough_hz=20, sub=0.45, breath=0.26, jitter=0.05, shimmer=0.2, tilt=1000,
              amp_pts=[(0, 0), (0.08, 1), (0.5, 0.6), (1, 0)], direct=0.25)
    return finish(reverb(nz(v), rng, 300, 0.2, 150, 2500), fade_ms=60)


def make_tiger_roar(seed):
    rng = np.random.default_rng(seed)
    # 크르르(목 깊은 떨림) → 어흥(입을 크게 벌려 터뜨림) → 길게 가라앉음
    g = voice(rng, 0.5, [(0, 74), (1, 96)], BIG, rough=0.85, rough_hz=24, sub=0.55, breath=0.2, jitter=0.05, shimmer=0.22, tilt=1100, amp_pts=[(0, 0), (0.3, 0.5), (1, 0.8)], direct=0.25)
    r = voice(rng, 1.7, [(0, 118), (0.1, 150), (0.35, 132), (1, 78)], BIG, BIG_OPEN, [(0, 0.2), (0.12, 1), (0.55, 0.95), (1, 0.15)], rough=0.66, rough_hz=29, sub=0.5, breath=0.26, jitter=0.055, shimmer=0.24,
              tilt=1500, amp_pts=[(0, 0.6), (0.08, 1), (0.5, 0.9), (1, 0)], direct=0.18)
    x = np.concatenate([nz(g) * 0.55, nz(r)])
    n = len(x)
    x += nz(lpf(np.abs(x), 50, 1) * np.sin(TAU * 46 * np.arange(n) / SR)) * 0.3
    return finish(reverb(x, rng, 700, 0.3, 120, 3000), peak=0.9, fade_ms=120)


def make_tiger_snarl(seed):
    rng = np.random.default_rng(seed)
    v = voice(rng, 0.55, [(0, 105), (0.2, 150), (1, 92)], BIG, BIG_OPEN, [(0, 0.1), (0.25, 1), (1, 0.2)], rough=0.75, rough_hz=32, sub=0.5, breath=0.28, jitter=0.05, shimmer=0.22, tilt=1600,
              amp_pts=[(0, 0), (0.1, 1), (0.55, 0.8), (1, 0)], direct=0.18)
    return finish(reverb(nz(v), rng, 240, 0.18, 150, 3200), fade_ms=40)


def make_war_cry(seed):
    rng = np.random.default_rng(seed)
    # 여러 사람이 한꺼번에 지르는 '와아!': 남자 목소리 14명 — 시작 시각 · 높이 · 길이가 제각각
    A = [(720, 240, 1.0), (1180, 300, 0.8), (2600, 600, 0.35)]
    O = [(520, 220, 1.0), (900, 280, 0.6), (2500, 600, 0.2)]
    n = sec(1.9)
    out = np.zeros(n)
    for k in range(14):
        f = rng.uniform(128, 230)
        d = rng.uniform(0.95, 1.4)
        y = voice(rng, d, [(0, f * 0.9), (0.15, f * 1.18), (0.6, f * 1.1), (1, f * 0.82)], O, A, [(0, 0), (0.2, 1), (1, 0.8)], rough=0.3, rough_hz=rng.uniform(26, 40), sub=0.25,
                  breath=0.3, jitter=0.03, shimmer=0.14, tilt=1700, amp_pts=[(0, 0), (0.1, 1), (0.6, 0.8), (1, 0)], direct=0.1)
        i = sec(rng.uniform(0, 0.28))
        j = min(n, i + len(y))
        out[i:j] += nz(y)[:j - i] * rng.uniform(0.5, 1.0)
    return finish(reverb(out, rng, 600, 0.3, 250, 3500), peak=0.85, fade_ms=120)


SOUNDS = [
    ('thud_hit_1', lambda: make_thud_light(3611, 1.0)),
    ('thud_hit_2', lambda: make_thud_light(3612, 0.88)),
    ('thud_heavy', lambda: make_thud_heavy(3620)),
    ('thud_crush', lambda: make_thud_crush(3630)),
    ('wolf_howl', lambda: make_wolf_howl(3641)),
    ('wolf_snarl', lambda: make_wolf_snarl(3642)),
    ('wolf_yelp', lambda: make_wolf_yelp(3643)),
    ('hyena_cackle', lambda: make_hyena_cackle(3650)),
    ('bear_roar', lambda: make_bear_roar(3660)),
    ('bear_growl', lambda: make_bear_growl(3661)),
    ('rhino_snort', lambda: make_rhino_snort(3670)),
    ('beast_groan', lambda: make_beast_groan(3680)),
    ('tiger_roar', lambda: make_tiger_roar(3690)),
    ('tiger_snarl', lambda: make_tiger_snarl(3691)),
    ('war_cry', lambda: make_war_cry(3700)),
]


def write_wav(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def read_wav(path):
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float64) / 32768


def metrics(d):
    X = np.abs(np.fft.rfft(d)) ** 2
    f = np.fft.rfftfreq(len(d), 1 / SR)
    tot = X.sum() + 1e-12
    ed = [0, 150, 300, 600, 1200, 2400, 4800, 11025]
    bands = [int(round(100 * X[(f >= a) & (f < b)].sum() / tot)) for a, b in zip(ed[:-1], ed[1:])]
    e = np.cumsum(d ** 2)
    e /= e[-1]
    return bands, np.searchsorted(e, 0.1) / SR * 1000, np.searchsorted(e, 0.9) / SR * 1000


def ring(d):
    """'울림 꼬리' 지표(ms): 600Hz 위 소리가 가장 클 때부터 20dB 줄어들 때까지 걸리는 시간.
    돌 · 쇠 · 플라스틱처럼 울리거나 잘그락거리는 소리는 길고, 둔탁한 '퍽'은 짧다."""
    x = hpf(d, 600, 3)
    e = lpf(x * x, 60, 2)
    e = np.maximum(e, 1e-12)
    pk = int(np.argmax(e))
    thr = e[pk] * 0.01
    below = np.where(e[pk:] < thr)[0]
    return float(below[0] / SR * 1000) if len(below) else float((len(e) - pk) / SR * 1000)


if __name__ == '__main__':
    OUT = sys.argv[1]
    SHEET = sys.argv[2] if len(sys.argv) > 2 else None
    os.makedirs(OUT, exist_ok=True)
    made = []
    print('name            dur(ms) peak  rms   t10  t90   [~150,~300,~600,~1.2k,~2.4k,~4.8k,4.8k~]  600Hz 위 꼬리(ms)')
    for name, fn in SOUNDS:
        x = fn()
        write_wav(os.path.join(OUT, name + '.wav'), x)
        b, t10, t90 = metrics(x)
        print(f'{name:14s} {len(x) / SR * 1000:6.0f}  {np.max(np.abs(x)):.2f}  {np.sqrt(np.mean(x * x)):.3f} {t10:4.0f} {t90:5.0f}   {b}  {ring(x):5.0f}')
        made.append((name, x))
    for old in ('rock_hit_1', 'rock_hit_2', 'rock_heavy', 'rock_crush'):
        p = os.path.join(OUT, old + '.wav')
        if os.path.exists(p):
            d = read_wav(p)
            b, t10, t90 = metrics(d)
            print(f'(R35) {old:10s} {len(d) / SR * 1000:4.0f}  {np.max(np.abs(d)):.2f}  {np.sqrt(np.mean(d * d)):.3f} {t10:4.0f} {t90:5.0f}   {b}  {ring(d):5.0f}')
    if SHEET:
        from PIL import Image, ImageDraw
        cw, ch = 300, 150
        cols = 5
        rows = (len(made) + cols - 1) // cols
        sh = Image.new('RGB', (cols * cw, rows * (ch + 18)), (12, 14, 20))
        dr = ImageDraw.Draw(sh)
        for i, (name, x) in enumerate(made):
            f, t, S = signal.spectrogram(x, SR, nperseg=512, noverlap=448)
            S = 10 * np.log10(S[:120] + 1e-10)                  # 0~5.2kHz
            S = np.clip((S - S.max() + 65) / 65, 0, 1)[::-1]
            im = Image.fromarray((S * 255).astype(np.uint8)).resize((cw, ch), Image.BILINEAR)
            rgb = Image.merge('RGB', (im.point(lambda v: min(255, int(v * 1.6))), im.point(lambda v: int(v * 0.85)), im.point(lambda v: int(60 + v * 0.3))))
            ox, oy = (i % cols) * cw, (i // cols) * (ch + 18)
            sh.paste(rgb, (ox, oy + 18))
            dr.text((ox + 4, oy + 3), f'{name}  {len(x) / SR * 1000:.0f}ms  (0~5kHz)', fill=(255, 230, 120))
        sh.save(SHEET)
        print('sheet', SHEET)
