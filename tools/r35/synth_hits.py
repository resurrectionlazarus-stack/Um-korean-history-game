#!/usr/bin/env python3
"""R35 타격음 — 무기 종류별 타격음 15종을 수식으로 합성한다(녹음 소스 없음 · 시드 고정 → 다시 만들어도 같은 파일).

왜: 예전 타격음(slice_crisp · blade_slash · hit_heavy)은 에너지의 65~76%가 4.8kHz 위, 또는 77%가 300Hz 아래에 몰려 있고
    300~2400Hz(휴대폰 스피커가 가장 잘 내는 대역)가 거의 비어 있었다 → 짧고 얇은 '탁탁'(전기 모기채) 소리.
방향(오너): 칼 = 맛깔나게 베이는 소리 · 둔기 = 바위를 부수는 무게(귀멸의 칼날 '암주'를 모티프로 한 느낌만 — 원음 복제 없음, 전부 새로 합성)

  칼(SWORD)   cut_light_1/2/3  휙 → 서걱(아래로 훑는 잡음 + 거친 결) + 살 무게 + 젖은 꼬리 + 은은한 쇠울림
              cut_heavy        4타 · 강타: 두 겹 베기 + 묵직한 몸통 + 긴 쇠울림
              cut_sever        양단 막타: 베기 + 흩뿌려지는 물기 + 늦게 떨어지는 무게
              cut_armor        갑옷 · 방패: 쇳덩이 울림(캉) + 베기
              cut_flurry       연참 · 일섬: 다섯 번 잇달아 베고 마지막에 크게
  둔기(AXE)   rock_hit_1/2     딱(돌 맞부딪는 울림) + 쿵(몸통) + 와르르(부스러기)
              rock_heavy       4타 · 강타: 더 낮고 긴 쿵 + 땅 울림 + 긴 부스러기
              rock_crush       내려찍기 · 막타: 두 번 무너지는 바위
  창(SPEAR)   stab_1/2         슉 → 푹(낮은 몸통 + 짧은 물기)
  휘두름      whoosh_blade     칼 바람(휙) · whoosh_heavy 둔기 바람(부웅)

사용: python3 -I tools/r35/synth_hits.py <출력 폴더(assets/sfx)> [검증 시트 png]
형식: 22050Hz · 16bit · 모노(기존 효과음과 같음). scipy 필요(pip install scipy) — 게임 실행에는 필요 없음
"""
import os
import sys
import wave

import numpy as np
from scipy import signal

SR = 22050
OUT = sys.argv[1]
SHEET = sys.argv[2] if len(sys.argv) > 2 else None
TAU = 2 * np.pi


def ms(v):
    return int(round(SR * v / 1000.0))


def bpf(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, min(hi, SR * 0.49)], btype='band', fs=SR, output='sos'), x)


def lpf(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype='low', fs=SR, output='sos'), x)


def hpf(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype='high', fs=SR, output='sos'), x)


def svf_bp(x, fc, q):
    """시간에 따라 중심이 움직이는 띠 거르개(TPT 상태변수 필터) — '서걱'의 훑는 소리."""
    n = len(x)
    y = np.zeros(n)
    g = np.tan(np.pi * np.clip(fc, 30, SR * 0.45) / SR)
    k = 1.0 / q
    ic1 = ic2 = 0.0
    for i in range(n):
        gi = g[i]
        a1 = 1.0 / (1.0 + gi * (gi + k))
        a2 = gi * a1
        a3 = gi * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2 * v1 - ic1
        ic2 = 2 * v2 - ic2
        y[i] = v1
    return y * k        # 중심 주파수에서 이득 1


def tms(n):
    return np.arange(n) / SR * 1000.0


def env(n, tau, atk=1.0):
    t = tms(n)
    return np.minimum(1.0, t / max(atk, 1e-6)) * np.exp(-t / tau)


def env2(n, tau1, tau2, w=0.5, atk=1.5):
    """2단 감쇠: 빠른 첫 감쇠(tau1) + 느린 꼬리(tau2) — 짧은 '탁'이 아니라 '서걱-' 하고 남는 몸통."""
    t = tms(n)
    return np.minimum(1.0, t / max(atk, 1e-6)) * (w * np.exp(-t / tau1) + (1 - w) * np.exp(-t / tau2))


def sweep(f0, f1, n, tau):
    """f0 → f1 지수 접근(시간상수 tau ms)."""
    return f1 + (f0 - f1) * np.exp(-tms(n) / tau)


def tone_sweep(f0, f1, n, tau_f, tau_a, atk=0.6):
    f = sweep(f0, f1, n, tau_f)
    ph = np.cumsum(f) * TAU / SR
    return np.sin(ph) * env(n, tau_a, atk)


def soft(x, drive):
    return np.tanh(x * drive) / np.tanh(drive)


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


def grains(n, rng, rate0, rate1, tau_rate, f_lo, f_hi, len_lo, len_hi, tonal=0.0):
    """알갱이(물방울 · 돌 부스러기): 발생 빈도가 rate0 → rate1(1/s)로 줄어드는 포아송 사건마다 짧은 울림 하나."""
    out = np.zeros(n)
    t = 0.0
    T = n / SR
    while True:
        rate = rate1 + (rate0 - rate1) * np.exp(-t * 1000 / tau_rate)
        t += rng.exponential(1.0 / max(rate, 1e-3))
        if t >= T:
            break
        L = ms(rng.uniform(len_lo, len_hi))
        f = np.exp(rng.uniform(np.log(f_lo), np.log(f_hi)))
        tt = np.arange(L) / SR
        dec = np.exp(-tt / (L / SR / 4.5))
        body = np.sin(TAU * f * tt + rng.uniform(0, TAU)) * tonal + rng.standard_normal(L) * (1 - tonal)
        g = body * dec * rng.uniform(0.25, 1.0)
        i = int(t * SR)
        j = min(n, i + L)
        out[i:j] += g[:j - i]
    return out


def reverb(x, rng, ms_len=140, mix=0.12, lo=300, hi=5000):
    """짧은 공간감(지수 감쇠 잡음 임펄스) — 소리가 '점'이 아니라 '공간'에서 나게."""
    L = ms(ms_len)
    ir = rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 5.0))
    ir = bpf(ir, lo, hi)
    ir /= np.sqrt(np.sum(ir * ir)) + 1e-12
    wet = signal.fftconvolve(x, ir)
    out = np.zeros(len(wet))
    out[:len(x)] = x
    return out + wet * mix


def finish(x, peak=0.89, fade_ms=10):
    x = x - np.mean(x)
    x = hpf(x, 45)
    # 부드러운 한계기: 0.7 위부터 눌러 순간 봉우리만 잡는다(몸통은 그대로)
    m = np.max(np.abs(x)) + 1e-12
    x = x / m
    k = 0.7
    a = np.abs(x)
    over = a > k
    x[over] = np.sign(x[over]) * (k + (1 - k) * np.tanh((a[over] - k) / (1 - k) * 1.6) / np.tanh(1.6))
    x = x / (np.max(np.abs(x)) + 1e-12) * peak
    f = ms(fade_ms)
    x[-f:] *= np.linspace(1, 0, f) ** 2
    return x


# ───────────────────────── 칼: 베는 소리 ─────────────────────────
def cut_layers(rng, n_ms, f_hi, f_lo, tau_f, tau_a, rough_hz, rough_depth, q=1.3, tail=3.0, w=0.5):
    """서걱: 흰 잡음을 f_hi → f_lo로 훑는 띠 거르개에 통과 + 거친 결(톱니 진폭 변조)."""
    n = ms(n_ms)
    x = rng.standard_normal(n)
    fc = sweep(f_hi, f_lo, n, tau_f)
    y = svf_bp(x, fc, q)
    t = tms(n)
    rf = sweep(rough_hz * 1.3, rough_hz * 0.8, n, 50)
    saw = signal.sawtooth(np.cumsum(rf) * TAU / SR)
    rough = 1 + rough_depth * np.exp(-t / 70) * saw
    return y * rough * env2(n, tau_a, tau_a * tail, w)


def steel_ring(rng, n_ms, base, taus, glide=0.008):
    n = ms(n_ms)
    t = tms(n)
    out = np.zeros(n)
    for i, (f, tau) in enumerate(zip(base, taus)):
        f = f * (1 + rng.uniform(-0.02, 0.02))
        fr = f * (1 + glide * (1 - np.exp(-t / 25)))
        out += np.sin(np.cumsum(fr) * TAU / SR + rng.uniform(0, TAU)) * np.exp(-t / tau) * (0.9 ** i)
    return out * np.minimum(1, t / 2.0)


def wet_tail(rng, n_ms, lo, hi, tau, rate0=420, grain_mix=0.6):
    n = ms(n_ms)
    hiss = bpf(rng.standard_normal(n), lo, hi) * env(n, tau, 12)
    gr = bpf(grains(n, rng, rate0, 25, 70, lo * 1.2, hi * 1.1, 3, 9), lo, hi * 1.2) * np.exp(-tms(n) / (tau * 1.6))
    hiss /= np.max(np.abs(hiss)) + 1e-12
    gr /= np.max(np.abs(gr)) + 1e-12
    return hiss * (1 - grain_mix) + gr * grain_mix


def pre_whoosh(rng, n_ms, f0, f1, q=1.6):
    n = ms(n_ms)
    x = rng.standard_normal(n)
    fc = np.exp(np.linspace(np.log(f0), np.log(f1), n))
    y = svf_bp(x, fc, q)
    e = (np.arange(n) / n) ** 2.2
    return y * e


def flesh_thump(rng, n_ms, f0, f1, tau_a, drive=2.2, noise_lo=320, noise_hi=950, noise_tau=22, sub=0.35):
    n = ms(n_ms)
    s = soft(tone_sweep(f0, f1, n, 30, tau_a), drive)                      # 낮은 몸통(이어폰 · 큰 스피커)
    s2 = soft(tone_sweep(f0 * 2.1, f1 * 2.1, n, 26, tau_a * 0.8), drive)   # 한 옥타브 위(휴대폰 스피커)
    nz = bpf(rng.standard_normal(n), noise_lo, noise_hi) * env2(n, noise_tau, noise_tau * 2.5, 0.6, 1.0)
    nz /= np.max(np.abs(nz)) + 1e-12
    return s * sub + s2 * 0.5 + nz * 1.0


def make_cut_light(seed, f_hi, f_lo, rough, thump_f, ring_scale, sh=1.0):
    rng = np.random.default_rng(seed)
    M = Mix(300, pre_ms=18)
    M.add(pre_whoosh(rng, 18, 1300, 4300), -18, -11)
    click = rng.standard_normal(ms(3)) * np.exp(-tms(ms(3)) / 0.55)
    M.add(hpf(click, 1200), 0, -7)
    c = cut_layers(rng, 280, f_hi, f_lo, 52, 42 * sh, rough, 0.55, tail=3.0, w=0.5)
    M.add(c / (np.max(np.abs(c)) + 1e-12), 0, -2.5)
    # 낮은 결 한 겹 더(500~1500Hz): 휴대폰에서도 '서걱'의 몸이 들리게
    c2 = cut_layers(rng, 260, f_hi * 0.44, f_lo * 0.55, 46, 40, rough * 0.8, 0.7, q=0.9, tail=2.8, w=0.5)
    M.add(c2 / (np.max(np.abs(c2)) + 1e-12), 2, -1.0)
    th = flesh_thump(rng, 110, thump_f, thump_f * 0.52, 26, sub=0.22)
    M.add(th / (np.max(np.abs(th)) + 1e-12), 1, -8)
    w = wet_tail(rng, 260, 700, 2800, 80)
    M.add(w, 14, -8.5)
    r = steel_ring(rng, 290, [2350 * ring_scale, 3540 * ring_scale, 5180 * ring_scale, 6900 * ring_scale], [95, 72, 52, 36])
    M.add(r / (np.max(np.abs(r)) + 1e-12), 0, -21)
    return finish(reverb(M.b, rng, 110, 0.10))


def make_cut_heavy(seed):
    rng = np.random.default_rng(seed)
    M = Mix(560, pre_ms=30)
    M.add(pre_whoosh(rng, 30, 700, 3600, q=1.3), -30, -8)
    click = rng.standard_normal(ms(4)) * np.exp(-tms(ms(4)) / 0.7)
    M.add(hpf(click, 900), 0, -6)
    c = cut_layers(rng, 380, 3600, 850, 60, 44, 105, 0.6, tail=3.4)
    M.add(c / (np.max(np.abs(c)) + 1e-12), 0, -2.5)
    c2 = cut_layers(rng, 360, 1500, 420, 50, 44, 82, 0.75, q=0.9, tail=3.2)
    M.add(c2 / (np.max(np.abs(c2)) + 1e-12), 3, -0.5)
    # 두 번째 결(조금 늦게 · 더 낮게) — '촤-악'
    c3 = cut_layers(rng, 340, 2600, 620, 66, 50, 88, 0.5, tail=3.0)
    M.add(c3 / (np.max(np.abs(c3)) + 1e-12), 38, -4.5)
    th = flesh_thump(rng, 190, 185, 84, 55, drive=3.0, noise_lo=240, noise_hi=820, noise_tau=40, sub=0.3)
    M.add(th / (np.max(np.abs(th)) + 1e-12), 2, -5.5)
    w = wet_tail(rng, 440, 650, 2700, 120, rate0=520)
    M.add(w, 20, -8)
    r = steel_ring(rng, 520, [1980, 2960, 4420, 6150], [210, 160, 110, 70], glide=0.012)
    M.add(r / (np.max(np.abs(r)) + 1e-12), 0, -18.5)
    return finish(reverb(M.b, rng, 190, 0.16))


def make_cut_sever(seed):
    rng = np.random.default_rng(seed)
    M = Mix(620, pre_ms=22)
    M.add(pre_whoosh(rng, 22, 1000, 4200), -22, -10)
    c = cut_layers(rng, 320, 3900, 1000, 50, 36, 120, 0.6, tail=3.4)
    M.add(c / (np.max(np.abs(c)) + 1e-12), 0, -2.5)
    c2 = cut_layers(rng, 300, 1700, 500, 46, 36, 92, 0.75, q=0.9, tail=3.2)
    M.add(c2 / (np.max(np.abs(c2)) + 1e-12), 2, -1)
    th = flesh_thump(rng, 130, 215, 108, 30, sub=0.22)
    M.add(th / (np.max(np.abs(th)) + 1e-12), 1, -8)
    # 흩뿌려지는 물기(굵은 방울 → 잔 방울)
    n = ms(480)
    drops = bpf(grains(n, rng, 260, 18, 130, 500, 2600, 5, 16, tonal=0.25), 420, 3400)
    drops *= np.exp(-tms(n) / 190) * np.minimum(1, tms(n) / 25)
    M.add(drops / (np.max(np.abs(drops)) + 1e-12), 45, -6)
    # 늦게 떨어지는 무게
    th2 = flesh_thump(rng, 160, 160, 76, 48, drive=2.6, noise_lo=220, noise_hi=700, noise_tau=36, sub=0.3)
    M.add(th2 / (np.max(np.abs(th2)) + 1e-12), 150, -9)
    r = steel_ring(rng, 360, [2500, 3760, 5480], [120, 88, 60])
    M.add(r / (np.max(np.abs(r)) + 1e-12), 0, -21)
    return finish(reverb(M.b, rng, 170, 0.14))


def make_cut_armor(seed):
    rng = np.random.default_rng(seed)
    M = Mix(520, pre_ms=14)
    M.add(pre_whoosh(rng, 14, 1500, 4500), -14, -12)
    click = rng.standard_normal(ms(3)) * np.exp(-tms(ms(3)) / 0.5)
    M.add(hpf(click, 1500), 0, -5)
    # 쇳덩이 울림(캉): 두드린 철판의 비정수 배음
    n = ms(480)
    t = tms(n)
    f0 = 690.0
    clang = np.zeros(n)
    for i, (m, tau, a) in enumerate([(1.0, 150, 1.0), (1.59, 125, 0.8), (2.14, 100, 0.7), (2.65, 85, 0.55), (3.52, 60, 0.42), (4.48, 44, 0.3), (5.9, 30, 0.2)]):
        f = f0 * m * (1 + rng.uniform(-0.012, 0.012))
        clang += np.sin(TAU * f * t / 1000 + rng.uniform(0, TAU)) * np.exp(-t / tau) * a
    clang *= np.minimum(1, t / 0.8)
    M.add(clang / (np.max(np.abs(clang)) + 1e-12), 0, -3.5)
    c = cut_layers(rng, 220, 3300, 1100, 36, 28, 135, 0.5, tail=3.0)
    M.add(c / (np.max(np.abs(c)) + 1e-12), 0, -4)
    th = flesh_thump(rng, 120, 200, 92, 30, drive=3.0, noise_lo=280, noise_hi=860, noise_tau=26, sub=0.25)
    M.add(th / (np.max(np.abs(th)) + 1e-12), 1, -7)
    sp = bpf(grains(ms(200), rng, 380, 30, 60, 1800, 5200, 2, 5, tonal=0.5), 1500, 6000) * np.exp(-tms(ms(200)) / 70)
    M.add(sp / (np.max(np.abs(sp)) + 1e-12), 6, -15)
    return finish(reverb(M.b, rng, 200, 0.17))


def make_cut_flurry(seed):
    """연참 · 일섬: 다섯 번 잇달아 베고 마지막에 크게 — 예전 slice_flurry_multi(고음 71%)를 대신한다."""
    rng = np.random.default_rng(seed)
    M = Mix(820, pre_ms=18)
    M.add(pre_whoosh(rng, 18, 1200, 4200), -18, -11)
    plan = [(0, 3700, 1150, 128, 230, -5.0), (88, 3300, 980, 112, 205, -4.0), (170, 4000, 1250, 140, 245, -3.5), (256, 3450, 1020, 118, 215, -2.5), (352, 3000, 800, 98, 180, 0.0)]
    for i, (at, fh, fl, rough, thf, lv) in enumerate(plan):
        last = i == len(plan) - 1
        c = cut_layers(rng, 300 if last else 200, fh, fl, 50, 44 if last else 30, rough, 0.55, tail=3.0 if last else 2.4)
        M.add(c / (np.max(np.abs(c)) + 1e-12), at, lv - 2.5)
        c2 = cut_layers(rng, 280 if last else 190, fh * 0.44, fl * 0.55, 44, 40 if last else 28, rough * 0.8, 0.7, q=0.9, tail=2.8 if last else 2.2)
        M.add(c2 / (np.max(np.abs(c2)) + 1e-12), at + 2, lv - 1.0)
        th = flesh_thump(rng, 120 if last else 90, thf, thf * 0.52, 30 if last else 22, sub=0.25)
        M.add(th / (np.max(np.abs(th)) + 1e-12), at + 1, lv - (5.5 if last else 8.5))
        wh = pre_whoosh(rng, 34, 900, 3600)
        if i:
            M.add(wh, at - 34, lv - 12)
    M.add(wet_tail(rng, 420, 650, 2700, 120, rate0=480), 360, -8)
    r = steel_ring(rng, 460, [2100, 3150, 4650, 6400], [190, 140, 100, 64], glide=0.012)
    M.add(r / (np.max(np.abs(r)) + 1e-12), 352, -19)
    return finish(reverb(M.b, rng, 190, 0.15))


# ───────────────────────── 둔기: 바위를 부수는 소리 ─────────────────────────
def stone_knock(rng, n_ms, freqs, taus):
    n = ms(n_ms)
    t = tms(n)
    out = np.zeros(n)
    for i, (f, tau) in enumerate(zip(freqs, taus)):
        f = f * (1 + rng.uniform(-0.03, 0.03))
        out += np.sin(TAU * f * t / 1000 + rng.uniform(0, TAU)) * np.exp(-t / tau) * (0.88 ** i)
    return out * np.minimum(1, t / 0.4)


def boom(rng, n_ms, f0, f1, tau_a, drive, mid_lo, mid_hi, mid_tau, sub=0.3):
    n = ms(n_ms)
    s = soft(tone_sweep(f0, f1, n, 38, tau_a, atk=1.2), drive)                       # 땅을 치는 낮은 쿵(이어폰 · 큰 스피커)
    s2 = soft(tone_sweep(f0 * 2.6, f1 * 2.4, n, 32, tau_a * 0.75, atk=1.0), drive)   # 그 위 '덩'(휴대폰 스피커가 내는 몸통)
    mid = bpf(rng.standard_normal(n), mid_lo, mid_hi) * env2(n, mid_tau, mid_tau * 2.6, 0.55, 1.5)
    mid /= np.max(np.abs(mid)) + 1e-12
    return s * sub + s2 * 0.62 + mid * 1.0


def rubble(rng, n_ms, rate0, tau_rate, tau_a, lo=600, hi=3400):
    n = ms(n_ms)
    g = grains(n, rng, rate0, 30, tau_rate, lo, hi, 2, 7, tonal=0.55)
    g = bpf(g, lo * 0.7, hi * 1.2) * np.exp(-tms(n) / tau_a)
    return g / (np.max(np.abs(g)) + 1e-12)


def make_rock_light(seed, pitch=1.0):
    rng = np.random.default_rng(seed)
    M = Mix(360, pre_ms=8)
    # 다가오는 공기(낮은 바람 한 줌)
    M.add(pre_whoosh(rng, 8, 400, 1500, q=1.0), -8, -14)
    click = rng.standard_normal(ms(4)) * np.exp(-tms(ms(4)) / 0.9)
    M.add(hpf(click, 900), 0, -7)
    k = stone_knock(rng, 200, [520 * pitch, 870 * pitch, 1340 * pitch, 1990 * pitch, 2780 * pitch], [64, 48, 34, 22, 14])
    M.add(k / (np.max(np.abs(k)) + 1e-12), 0, -2.5)
    b = boom(rng, 240, 150 * pitch, 62 * pitch, 62, 2.6, 230, 760, 44)
    M.add(b / (np.max(np.abs(b)) + 1e-12), 0, -1)
    M.add(rubble(rng, 320, 620, 80, 110), 10, -7.5)
    return finish(reverb(M.b, rng, 150, 0.15, lo=200, hi=4200))


def make_rock_heavy(seed):
    rng = np.random.default_rng(seed)
    M = Mix(680, pre_ms=22)
    M.add(pre_whoosh(rng, 22, 240, 1200, q=0.9), -22, -9)
    click = rng.standard_normal(ms(5)) * np.exp(-tms(ms(5)) / 1.0)
    M.add(hpf(click, 800), 0, -6)
    k = stone_knock(rng, 260, [410, 690, 1080, 1620, 2290, 3050], [90, 66, 46, 30, 19, 12])
    M.add(k / (np.max(np.abs(k)) + 1e-12), 0, -1.5)
    b = boom(rng, 400, 128, 46, 105, 3.2, 220, 760, 70, sub=0.22)
    M.add(b / (np.max(np.abs(b)) + 1e-12), 0, -0.5)
    # 땅 울림(큰 스피커 · 이어폰용) + 그 배음(휴대폰용)
    n = ms(420)
    rum = lpf(rng.standard_normal(n), 140, 3) * env(n, 150, 8)
    rum = soft(rum / (np.max(np.abs(rum)) + 1e-12), 2.2)
    M.add(rum, 6, -16)
    M.add(rubble(rng, 560, 900, 110, 190), 12, -5.5)
    M.add(rubble(rng, 420, 220, 160, 200, lo=300, hi=1400), 40, -7.5)
    return finish(reverb(M.b, rng, 240, 0.2, lo=160, hi=4000))


def make_rock_crush(seed):
    rng = np.random.default_rng(seed)
    M = Mix(940, pre_ms=28)
    M.add(pre_whoosh(rng, 28, 200, 1000, q=0.9), -28, -8)
    click = rng.standard_normal(ms(5)) * np.exp(-tms(ms(5)) / 1.0)
    M.add(hpf(click, 800), 0, -6)
    k = stone_knock(rng, 300, [360, 610, 960, 1450, 2060, 2800], [105, 76, 52, 34, 21, 13])
    M.add(k / (np.max(np.abs(k)) + 1e-12), 0, -1.5)
    b = boom(rng, 480, 118, 40, 130, 3.4, 210, 740, 85, sub=0.24)
    M.add(b / (np.max(np.abs(b)) + 1e-12), 0, -0.5)
    n = ms(560)
    rum = lpf(rng.standard_normal(n), 130, 3) * env(n, 200, 10)
    rum = soft(rum / (np.max(np.abs(rum)) + 1e-12), 2.4)
    M.add(rum, 8, -15)
    # 두 번째 무너짐(갈라진 바위가 내려앉는 소리)
    k2 = stone_knock(rng, 180, [470, 790, 1220, 1830], [50, 38, 26, 16])
    M.add(k2 / (np.max(np.abs(k2)) + 1e-12), 150, -8)
    b2 = boom(rng, 320, 105, 44, 90, 2.8, 210, 680, 60, sub=0.22)
    M.add(b2 / (np.max(np.abs(b2)) + 1e-12), 150, -6)
    M.add(rubble(rng, 820, 1100, 150, 280), 12, -5)
    M.add(rubble(rng, 700, 300, 220, 300, lo=280, hi=1300), 60, -7)
    return finish(reverb(M.b, rng, 300, 0.22, lo=150, hi=3800))


# ───────────────────────── 창: 찌르는 소리 ─────────────────────────
def make_stab(seed, pitch=1.0):
    rng = np.random.default_rng(seed)
    M = Mix(260, pre_ms=14)
    M.add(pre_whoosh(rng, 14, 1800, 5200, q=2.2), -14, -10)
    click = rng.standard_normal(ms(3)) * np.exp(-tms(ms(3)) / 0.6)
    M.add(hpf(click, 1400), 0, -9)
    th = flesh_thump(rng, 130, 200 * pitch, 92 * pitch, 32, drive=2.6, noise_lo=300, noise_hi=1000, noise_tau=26, sub=0.22)
    M.add(th / (np.max(np.abs(th)) + 1e-12), 0, -2.5)
    # 푹 들어가는 결(짧고 낮게 훑음)
    c = cut_layers(rng, 200, 2100 * pitch, 620 * pitch, 28, 26, 70, 0.8, q=0.9, tail=3.0)
    M.add(c / (np.max(np.abs(c)) + 1e-12), 0, -1.5)
    w = wet_tail(rng, 210, 650, 2400, 60, rate0=300)
    M.add(w, 12, -9)
    return finish(reverb(M.b, rng, 100, 0.10))


# ───────────────────────── 휘두르는 바람 ─────────────────────────
def make_whoosh(seed, f_a, f_b, f_c, dur, q, low_mix=0.0):
    rng = np.random.default_rng(seed)
    n = ms(dur)
    u = np.arange(n) / n
    # 중심이 올랐다 내려오는 호(날이 지나가는 순간이 가장 밝게)
    fc = np.exp(np.log(f_a) + (np.log(f_b) - np.log(f_a)) * np.sin(np.pi * np.minimum(u / 0.62, 1) / 2) ** 1.0)
    fc = np.where(u > 0.62, np.exp(np.log(f_b) + (np.log(f_c) - np.log(f_b)) * ((u - 0.62) / 0.38)), fc)
    y = svf_bp(rng.standard_normal(n), fc, q)
    e = np.sin(np.pi * u ** 0.75) ** 1.6
    out = y * e
    if low_mix:
        lo = bpf(rng.standard_normal(n), 140, 420) * np.sin(np.pi * u) ** 2
        out = out / (np.max(np.abs(out)) + 1e-12) + lo / (np.max(np.abs(lo)) + 1e-12) * low_mix
    return finish(out, peak=0.8, fade_ms=14)


SOUNDS = [
    ('cut_light_1', lambda: make_cut_light(3511, 3500, 1050, 118, 215, 1.00)),
    ('cut_light_2', lambda: make_cut_light(3512, 3950, 1220, 138, 238, 1.06)),
    ('cut_light_3', lambda: make_cut_light(3513, 3150, 920, 102, 196, 0.94, sh=1.15)),
    ('cut_heavy', lambda: make_cut_heavy(3520)),
    ('cut_sever', lambda: make_cut_sever(3530)),
    ('cut_armor', lambda: make_cut_armor(3540)),
    ('cut_flurry', lambda: make_cut_flurry(3545)),
    ('rock_hit_1', lambda: make_rock_light(3551, 1.00)),
    ('rock_hit_2', lambda: make_rock_light(3552, 0.9)),
    ('rock_heavy', lambda: make_rock_heavy(3560)),
    ('rock_crush', lambda: make_rock_crush(3570)),
    ('stab_1', lambda: make_stab(3581, 1.0)),
    ('stab_2', lambda: make_stab(3582, 1.1)),
    ('whoosh_blade', lambda: make_whoosh(3591, 620, 2500, 1000, 160, 1.5, low_mix=0.18)),
    ('whoosh_heavy', lambda: make_whoosh(3592, 260, 950, 380, 210, 1.3, low_mix=0.55)),
]


def write_wav(path, x):
    d = np.clip(x, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((d * 32767).astype('<i2').tobytes())


def metrics(d):
    X = np.abs(np.fft.rfft(d)) ** 2
    f = np.fft.rfftfreq(len(d), 1 / SR)
    tot = X.sum() + 1e-12
    edges = [0, 150, 300, 600, 1200, 2400, 4800, 11025]
    bands = [int(round(100 * X[(f >= a) & (f < b)].sum() / tot)) for a, b in zip(edges[:-1], edges[1:])]
    e = np.cumsum(d ** 2)
    e /= e[-1]
    t10 = np.searchsorted(e, 0.1) / SR * 1000
    t90 = np.searchsorted(e, 0.9) / SR * 1000
    mid = int(round(100 * X[(f >= 300) & (f < 2400)].sum() / tot))
    return bands, t10, t90, mid


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    made = []
    print('name                dur(ms) peak  rms   t10  t90   [~150,~300,~600,~1.2k,~2.4k,~4.8k,4.8k~]  300~2400Hz')
    for name, fn in SOUNDS:
        x = fn()
        write_wav(os.path.join(OUT, name + '.wav'), x)
        b, t10, t90, mid = metrics(x)
        print(f'{name:18s} {len(x) / SR * 1000:6.0f}  {np.max(np.abs(x)):.2f}  {np.sqrt(np.mean(x * x)):.3f} {t10:4.0f} {t90:4.0f}   {b}  {mid}%')
        made.append((name, x))
    if SHEET:
        from PIL import Image, ImageDraw
        cw, ch = 300, 150
        cols = 5
        rows = (len(made) + cols - 1) // cols
        sh = Image.new('RGB', (cols * cw, rows * (ch + 18)), (12, 14, 20))
        dr = ImageDraw.Draw(sh)
        for i, (name, x) in enumerate(made):
            f, t, S = signal.spectrogram(x, SR, nperseg=256, noverlap=224)
            S = 10 * np.log10(S + 1e-10)
            S = np.clip((S - S.max() + 70) / 70, 0, 1)[::-1]
            im = Image.fromarray((S * 255).astype(np.uint8)).resize((cw, ch), Image.BILINEAR)
            rgb = Image.merge('RGB', (im.point(lambda v: min(255, int(v * 1.6))), im.point(lambda v: int(v * 0.85)), im.point(lambda v: int(60 + v * 0.3))))
            ox, oy = (i % cols) * cw, (i // cols) * (ch + 18)
            sh.paste(rgb, (ox, oy + 18))
            dr.text((ox + 4, oy + 3), f'{name}  {len(x) / SR * 1000:.0f}ms  (0~11kHz)', fill=(255, 230, 120))
        sh.save(SHEET)
        print('sheet', SHEET)
