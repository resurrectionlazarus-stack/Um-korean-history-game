#!/usr/bin/env python3
"""R35 배경음악 — 국악기 · 군악대 악기를 수식으로 합성하는 라이브러리(녹음 소스 없음).

악기(모두 음 하나를 만들어 돌려주는 함수):
  줄      pluck(kind=gayageum|geomungo|konghu)        뜯는 현(배음별 감쇠 + 농현 + 뜯는 잡음 + 울림통)
          bowed(haegeum)                               활로 켜는 현(비음 포먼트 + 미끄러지는 음)
  관      flute(kind=daegeum|sogeum|hun|piccolo)       대나무 피리(숨소리 + 요성 + 대금의 청 울림)
          reed(kind=piri|taepyeongso)                  겹서(코맹맹이 포먼트 + 넓은 떨림 + 꾸밈음)
          brass(kind=nabal|trumpet|horn|trombone|tuba) 금관(세게 불수록 밝아짐)
          chant()                                      낮은 '아-' 합창(제의 느낌)
  쇠      bell(kind=pyeonjong|beomjong|rattle)         편종 · 범종 · 청동 방울
          jing() · kkwaenggwari() · jabara() · cymbal()
  가죽    buk() · janggu(stroke=gung|chae|deong|roll) · bak() · snare() · bassdrum() · woodblock()

음 높이는 MIDI 번호(60 = 가온 도). 모든 함수는 (rng, ...)를 받아 같은 시드면 같은 소리가 난다.
"""
import numpy as np
from scipy import signal

SR = 32000
TAU = 2 * np.pi


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def dbg(x):
    return 10 ** (x / 20.0)


def nsamp(sec):
    return max(1, int(round(sec * SR)))


def bpf(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, min(hi, SR * 0.49)], btype='band', fs=SR, output='sos'), x)


def lpf(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, min(fc, SR * 0.49), btype='low', fs=SR, output='sos'), x)


def hpf(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype='high', fs=SR, output='sos'), x)


def peak(x, f0, q, gain_db):
    """피킹 EQ(울림통 포먼트)."""
    A = 10 ** (gain_db / 40)
    w0 = TAU * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return signal.lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


def cosramp(n, up=True):
    r = 0.5 - 0.5 * np.cos(np.pi * np.arange(n) / max(1, n))
    return r if up else r[::-1]


def sustain_env(dur, a, r, swell=0.0, decay=0.0):
    """부는 · 켜는 악기 봉투선: 부드럽게 올라(a) 유지하다가 r 동안 사라진다. swell = 가운데가 부풀기 · decay = 서서히 줄기."""
    n = nsamp(dur + r)
    t = np.arange(n) / SR
    e = np.ones(n)
    na = min(n, nsamp(a))
    e[:na] = cosramp(na)
    if swell:
        e *= 1 + swell * np.sin(np.pi * np.clip(t / max(dur, 1e-3), 0, 1))
    if decay:
        e *= np.exp(-decay * t)
    nr = min(n, nsamp(r))
    e[-nr:] *= cosramp(nr, False)
    return e


def pitch_fac(n, rng, vib=None, scoop=None, glide=None, fall=None, jit=0.0015, bend=None):
    """음 높이 배율 곡선. vib = (빠르기Hz, 깊이, 시작 지연s, 커지는 시간s) · scoop = (아래에서 시작하는 양, 시간) ·
    glide = (시작 배율, 시간) 앞 음에서 미끄러져 옴 · fall = (끝에서 떨어지는 양, 시간) · bend = [(시각s, 배율), ...] 꺾는 음"""
    t = np.arange(n) / SR
    fac = np.ones(n)
    if vib:
        rate, depth, delay, ramp = vib
        w = np.clip((t - delay) / max(ramp, 1e-3), 0, 1)
        drift = 1 + 0.06 * np.sin(TAU * 0.7 * t + rng.uniform(0, TAU))
        fac *= 1 + depth * w * np.sin(TAU * rate * np.cumsum(drift) / SR + rng.uniform(0, TAU))
    if scoop:
        fac *= 1 - scoop[0] * np.exp(-t / scoop[1])
    if glide:
        fac *= glide[0] ** np.exp(-t / glide[1])
    if fall:
        T = n / SR
        u = np.clip((t - (T - fall[1])) / fall[1], 0, 1)
        fac *= 1 - fall[0] * u * u
    if bend:
        xs = [0.0] + [b[0] for b in bend] + [n / SR + 1]
        ys = [1.0] + [b[1] for b in bend] + [bend[-1][1]]
        fac *= np.interp(t, xs, ys)
    if jit:
        nz = rng.standard_normal(n // 400 + 4)
        sl = np.interp(np.arange(n) / 400.0, np.arange(len(nz)), nz)
        fac *= 1 + jit * sl
    return fac


def harmonics(f0, fac, amps, rng, inharm=0.0, rand_phase=True):
    """배음 합성. amps[k-1] = k번째 배음 크기(스칼라 또는 시간 배열)."""
    n = len(fac)
    phase = np.cumsum(TAU * f0 * fac / SR)
    out = np.zeros(n)
    fmax = f0 * float(np.max(fac))
    for k, a in enumerate(amps, start=1):
        st = np.sqrt(1 + inharm * k * k)
        if k * st * fmax > SR * 0.46:
            break
        if a is None:
            continue
        ph = rng.uniform(0, TAU) if rand_phase else 0.0
        out += a * np.sin(k * st * phase + ph)
    return out


def formant_gain(f, peaks, base=0.08):
    """f(Hz) 위치의 포먼트 이득. peaks = [(중심, 폭, 크기), ...]"""
    g = base
    for fc, bw, a in peaks:
        g = g + a / (1 + ((f - fc) / bw) ** 2)
    return g


# ───────────────────────────── 줄 ─────────────────────────────
PLUCK = {
    # beta = 뜯는 자리 · tau = 기음 감쇠(s) · d1/d2 = 높은 배음일수록 빨리 사라지는 정도 · body = 울림통 포먼트
    'gayageum': dict(beta=0.17, p=1.05, tau=1.05, d1=0.16, d2=0.012, inh=1.2e-4, click=0.5, click_f=(900, 4200), body=[(240, 2.5, 4), (520, 3, 3), (1150, 3, 2.5)], hp=90),
    'geomungo': dict(beta=0.11, p=1.2, tau=0.85, d1=0.22, d2=0.02, inh=2.5e-4, click=1.0, click_f=(300, 2600), body=[(150, 2, 5), (330, 2.5, 3), (780, 3, 2)], hp=55),
    'konghu': dict(beta=0.24, p=0.8, tau=1.7, d1=0.09, d2=0.006, inh=0.6e-4, click=0.3, click_f=(1500, 6000), body=[(310, 3, 2.5), (900, 3, 2), (2400, 3, 2)], hp=110),
}


def pluck(rng, m, dur, vel=0.8, kind='gayageum', nonghyeon=None, glide=None, bend=None, damp=None):
    """뜯는 현. dur = 다음 음까지(울림은 그 뒤로도 남는다) · nonghyeon = (빠르기, 깊이) 농현 · damp = 손으로 막는 시각(s)"""
    P = PLUCK[kind]
    f0 = hz(m)
    reg = np.clip((m - 55) / 24.0, -1, 1)                       # 낮은 줄일수록 오래 울린다
    tau1 = P['tau'] * (1 - 0.35 * reg)
    total = min(max(dur + 0.25, tau1 * 3.2), 4.0)
    n = nsamp(total)
    t = np.arange(n) / SR
    vib = (nonghyeon[0], nonghyeon[1], 0.09, 0.2) if nonghyeon else None
    fac = pitch_fac(n, rng, vib=vib, glide=glide, bend=bend, jit=0.0008)
    # 뜯는 순간 살짝 높았다가 내려앉는 음(줄이 당겨진 만큼)
    fac *= 1 + 0.006 * vel * np.exp(-t / 0.03)
    K = int(min(40, SR * 0.45 / f0))
    amps = []
    bright = 0.55 + 0.6 * vel
    for k in range(1, K + 1):
        a = abs(np.sin(k * np.pi * P['beta'])) / (k ** (P['p'] + (1 - bright) * 0.5))
        tk = tau1 / (1 + (k - 1) * P['d1'] + (k - 1) ** 2 * P['d2'])
        amps.append(a * np.exp(-t / tk))
    x = harmonics(f0, fac, amps, rng, inharm=P['inh'])
    x *= np.minimum(1, t / 0.0015)
    # 뜯는 · 치는 잡음
    nc = nsamp(0.012)
    ck = bpf(rng.standard_normal(nc + 64), *P['click_f'])[:nc] * np.exp(-np.arange(nc) / (SR * 0.0025))
    x[:nc] += ck / (np.max(np.abs(ck)) + 1e-9) * P['click'] * (0.35 + 0.5 * vel) * np.max(np.abs(x))
    if kind == 'geomungo':
        # 술대가 대모(가죽 덧판)를 치는 '둑'
        nt = nsamp(0.05)
        th = np.sin(TAU * 95 * np.arange(nt) / SR) * np.exp(-np.arange(nt) / (SR * 0.014))
        x[:nt] += th * 0.5 * vel * np.max(np.abs(x))
    for fc, q, g in P['body']:
        x = peak(x, fc, q, g)
    x = hpf(x, P['hp'])
    if damp is not None and damp < total:
        i = nsamp(damp)
        nr = min(n - i, nsamp(0.06))
        x[i:i + nr] *= cosramp(nr, False)
        x[i + nr:] = 0
    x[-nsamp(0.03):] *= cosramp(nsamp(0.03), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def bowed(rng, m, dur, vel=0.7, glide=None, vib=(5.4, 0.011, 0.12, 0.25), swell=0.25, bend=None):
    """해금: 두 줄을 활로 켜는 소리 — 코맹맹이 포먼트, 음을 미끄러뜨리며 들어온다."""
    f0 = hz(m)
    e = sustain_env(dur, 0.055, 0.11, swell=swell)
    n = len(e)
    fac = pitch_fac(n, rng, vib=vib, glide=glide, scoop=(0.012, 0.035) if not glide else None, bend=bend, jit=0.003)
    K = int(min(36, SR * 0.45 / f0))
    peaks = [(880, 260, 1.0), (1500, 300, 0.35), (2350, 420, 0.75), (3600, 700, 0.25)]
    fm = f0 * fac
    amps = [formant_gain(k * fm, peaks, 0.05) / (k ** 0.85) for k in range(1, K + 1)]
    x = harmonics(f0, fac, amps, rng)
    bow = bpf(rng.standard_normal(n), 1800, 6500) * 0.035 * (0.6 + 0.4 * np.sin(TAU * f0 * np.arange(n) / SR) ** 2)
    x = (x / (np.max(np.abs(x)) + 1e-9) + bow) * e
    return x / (np.max(np.abs(x)) + 1e-9) * vel


# ───────────────────────────── 관 ─────────────────────────────
FLUTE = {
    # h = 배음 크기 · breath = 숨소리 · buzz = 청(갈대 속청) 울림 · a/r = 시작/끝 시간
    'daegeum': dict(h=[1, 0.42, 0.30, 0.13, 0.09, 0.05, 0.03], breath=0.07, buzz=0.5, a=0.07, r=0.12, vib=(5.2, 0.012, 0.14, 0.3)),
    'sogeum': dict(h=[1, 0.3, 0.16, 0.06, 0.03], breath=0.06, buzz=0.12, a=0.045, r=0.09, vib=(5.8, 0.009, 0.1, 0.22)),
    'hun': dict(h=[1, 0.22, 0.12, 0.05, 0.025], breath=0.17, buzz=0.0, a=0.09, r=0.16, vib=(4.6, 0.008, 0.2, 0.35)),
    'piccolo': dict(h=[1, 0.34, 0.12, 0.05, 0.02], breath=0.045, buzz=0.0, a=0.03, r=0.06, vib=(6.0, 0.005, 0.12, 0.2)),
    'bone': dict(h=[1, 0.5, 0.3, 0.16, 0.08, 0.04], breath=0.2, buzz=0.0, a=0.05, r=0.14, vib=(4.8, 0.01, 0.16, 0.3)),   # 뼈피리: 밝고 숨이 많이 섞임
}


def flute(rng, m, dur, vel=0.7, kind='daegeum', scoop=0.02, glide=None, fall=None, vib=True, swell=0.18, bend=None, grace=None):
    """대나무 피리. grace = 앞꾸밈음의 반음 차(예: 2 = 온음 위에서 꺾어 내려옴)"""
    P = FLUTE[kind]
    f0 = hz(m)
    e = sustain_env(dur, P['a'], P['r'], swell=swell)
    n = len(e)
    bd = list(bend) if bend else []
    if grace:
        g = 2 ** (grace / 12.0)
        bd = [(0.0, g), (0.05, g), (0.075, 1.0)] + [(b[0] + 0.075, b[1]) for b in bd]
        fac = pitch_fac(n, rng, vib=P['vib'] if vib else None, fall=fall, jit=0.002)
        t = np.arange(n) / SR
        fac *= np.interp(t, [b[0] for b in bd] + [n / SR + 1], [b[1] for b in bd] + [bd[-1][1]])
    else:
        fac = pitch_fac(n, rng, vib=P['vib'] if vib else None, scoop=(scoop, 0.04) if scoop and not glide else None, glide=glide, fall=fall, bend=bd or None, jit=0.002)
    amps = [a * (0.75 + 0.5 * vel) ** (k - 1) if k > 1 else a for k, a in enumerate(P['h'], start=1)]
    x = harmonics(f0, fac, amps, rng)
    x /= np.max(np.abs(x)) + 1e-9
    if P['buzz']:
        # 청: 세게 불수록 2~5kHz에 갈대청이 떠는 밝은 울림이 얹힌다
        K = int(min(26, SR * 0.45 / f0))
        bz = harmonics(f0, fac, [None] * 4 + [formant_gain(k * f0, [(2700, 800, 1.0), (4300, 900, 0.5)], 0.02) / (k ** 0.3) for k in range(5, K + 1)], rng)
        bz /= np.max(np.abs(bz)) + 1e-9
        x += bz * P['buzz'] * (0.25 + 0.75 * vel) * e ** 1.6 * 0.5
    br = bpf(rng.standard_normal(n), max(300, f0 * 0.9), min(SR * 0.45, f0 * 5.5))
    br /= np.max(np.abs(br)) + 1e-9
    air = hpf(rng.standard_normal(n), 3500) * 0.25
    # 숨이 살짝 흔들리는 느낌
    flut = 1 + 0.06 * np.interp(np.arange(n) / 500.0, np.arange(n // 500 + 3), rng.standard_normal(n // 500 + 3))
    x = (x * flut + (br + air) * P['breath'] * (1.4 - 0.6 * vel)) * e
    # 혀로 끊어 부는 순간의 '후'
    nc = min(n, nsamp(0.03))
    x[:nc] += bpf(rng.standard_normal(nc + 64), f0 * 1.5, min(SR * 0.45, f0 * 6))[:nc] * np.exp(-np.arange(nc) / (SR * 0.008)) * 0.25
    return x / (np.max(np.abs(x)) + 1e-9) * vel


REED = {
    'piri': dict(peaks=[(1050, 320, 1.0), (1750, 260, 0.25), (2700, 520, 0.7), (3900, 700, 0.3)], roll=0.75, a=0.028, r=0.06, vib=(5.8, 0.016, 0.09, 0.2), noise=0.03),
    'taepyeongso': dict(peaks=[(1250, 480, 1.0), (2400, 500, 0.6), (3300, 700, 0.5), (5000, 900, 0.2)], roll=0.72, a=0.02, r=0.05, vib=(6.4, 0.014, 0.08, 0.16), noise=0.03, base=0.14),
}


def reed(rng, m, dur, vel=0.75, kind='piri', grace=None, glide=None, fall=None, bend=None, swell=0.1, vib=True):
    """겹서 악기(피리 · 태평소). grace = 앞꾸밈음 반음 차."""
    P = REED[kind]
    f0 = hz(m)
    e = sustain_env(dur, P['a'], P['r'], swell=swell)
    n = len(e)
    t = np.arange(n) / SR
    fac = pitch_fac(n, rng, vib=P['vib'] if vib and dur > 0.22 else None, glide=glide, fall=fall, bend=bend, jit=0.0025, scoop=(0.02, 0.022) if not (grace or glide) else None)
    if grace:
        g = 2 ** (grace / 12.0)
        fac *= np.interp(t, [0, 0.045, 0.068, n / SR + 1], [g, g, 1.0, 1.0])
    K = int(min(40, SR * 0.45 / f0))
    fm = f0 * fac
    amps = [formant_gain(k * fm, P['peaks'], P.get('base', 0.06)) / (k ** P['roll']) for k in range(1, K + 1)]
    x = harmonics(f0, fac, amps, rng)
    x /= np.max(np.abs(x)) + 1e-9
    nz = bpf(rng.standard_normal(n), 2200, 7000)
    x = (x + nz / (np.max(np.abs(nz)) + 1e-9) * P['noise']) * e
    # 서가 터지는 첫소리
    nc = min(n, nsamp(0.02))
    x[:nc] *= 1 + 0.5 * np.exp(-np.arange(nc) / (SR * 0.006))
    return x / (np.max(np.abs(x)) + 1e-9) * vel


BRASS = {
    'nabal': dict(form=[(520, 260, 1.0), (1050, 420, 0.6)], roll=1.0, a=0.06, r=0.16, bright=0.6),
    'trumpet': dict(form=[(1150, 500, 1.0), (2300, 700, 0.5)], roll=0.9, a=0.03, r=0.07, bright=1.0),
    'horn': dict(form=[(480, 260, 1.0), (950, 400, 0.4)], roll=1.4, a=0.045, r=0.09, bright=0.6),
    'trombone': dict(form=[(560, 300, 1.0), (1500, 600, 0.45)], roll=1.1, a=0.04, r=0.08, bright=0.85),
    'tuba': dict(form=[(240, 160, 1.0), (520, 300, 0.4)], roll=1.7, a=0.045, r=0.08, bright=0.45),
}


def brass(rng, m, dur, vel=0.75, kind='trumpet', vib=None, fall=None, swell=0.0, decay=0.0):
    """금관. 세게 불수록 높은 배음이 살아난다(밝아짐). 시작할 때 살짝 아래에서 올라온다."""
    P = BRASS[kind]
    f0 = hz(m)
    e = sustain_env(dur, P['a'], P['r'], swell=swell, decay=decay)
    n = len(e)
    fac = pitch_fac(n, rng, vib=vib, scoop=(0.018, 0.02), fall=fall, jit=0.0015)
    K = int(min(34, SR * 0.45 / f0))
    lvl = (0.35 + 0.65 * vel) * e                    # 순간 세기 → 밝기
    amps = []
    for k in range(1, K + 1):
        base = formant_gain(k * f0, P['form'], 0.07) / (k ** P['roll'])
        amps.append(base * lvl ** (1 + (k - 1) * 0.22 / P['bright']))
    x = harmonics(f0, fac, amps, rng)
    nc = min(n, nsamp(0.035))
    x[:nc] += bpf(rng.standard_normal(nc + 64), 500, 3500)[:nc] * np.exp(-np.arange(nc) / (SR * 0.01)) * 0.06 * np.max(np.abs(x))
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def chant(rng, m, dur, vel=0.5, vowel='a'):
    """낮은 남성 합창 '아-/오-'(제의). 세 목소리가 살짝 어긋나게."""
    F = {'a': [(700, 110, 1.0), (1150, 130, 0.6), (2600, 220, 0.25)], 'o': [(480, 100, 1.0), (850, 120, 0.5), (2500, 220, 0.15)]}[vowel]
    f0 = hz(m)
    e = sustain_env(dur, 0.45, 0.6, swell=0.2)
    n = len(e)
    out = np.zeros(n)
    for det in (-0.006, 0.0, 0.007):
        fac = pitch_fac(n, rng, vib=(4.6 + rng.uniform(-0.4, 0.4), 0.006, 0.4, 0.6), jit=0.004) * (1 + det)
        K = int(min(40, SR * 0.45 / f0))
        amps = [formant_gain(k * f0, F, 0.03) / (k ** 1.1) for k in range(1, K + 1)]
        out += harmonics(f0, fac, amps, rng)
    out = out * e + lpf(rng.standard_normal(n), 2500) * 0.004 * e
    return out / (np.max(np.abs(out)) + 1e-9) * vel


# ───────────────────────────── 쇠 ─────────────────────────────
def bell(rng, m, vel=0.7, kind='pyeonjong'):
    f0 = hz(m)
    if kind == 'pyeonjong':        # 편종: 작은 청동 종(뿔 망치) — 맑고 길게
        parts = [(0.5, 0.35, 1.6), (1.0, 1.0, 1.5), (1.19, 0.5, 1.0), (1.5, 0.3, 0.8), (2.0, 0.55, 0.7), (2.51, 0.3, 0.5), (3.01, 0.22, 0.35), (4.1, 0.14, 0.22), (5.4, 0.08, 0.14)]
        total, click = 2.6, 0.5
    elif kind == 'beomjong':       # 범종: 크고 낮은 종 — 맥놀이(웅- 웅-)
        parts = [(1.0, 1.0, 4.5), (1.006, 0.8, 4.2), (2.02, 0.55, 2.6), (2.03, 0.3, 2.4), (2.76, 0.4, 1.8), (3.52, 0.25, 1.2), (4.83, 0.16, 0.8), (5.9, 0.1, 0.5)]
        total, click = 5.5, 0.9
    else:                          # 청동 방울 한 알
        parts = [(1.0, 1.0, 0.5), (1.47, 0.7, 0.42), (2.09, 0.6, 0.33), (2.56, 0.4, 0.26), (3.3, 0.3, 0.2)]
        total, click = 0.9, 0.3
    n = nsamp(total)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for r, a, tau in parts:
        f = f0 * r * (1 + rng.uniform(-0.002, 0.002))
        if f > SR * 0.46:
            continue
        x += a * np.sin(TAU * f * t + rng.uniform(0, TAU)) * np.exp(-t / tau)
    x *= np.minimum(1, t / 0.002)
    nc = nsamp(0.02)
    ck = bpf(rng.standard_normal(nc + 64), min(f0 * 2, 5000), min(f0 * 9, 12000))[:nc] * np.exp(-np.arange(nc) / (SR * 0.004))
    x[:nc] += ck / (np.max(np.abs(ck)) + 1e-9) * click * 0.5
    if kind == 'beomjong':
        nt = nsamp(0.12)
        x[:nt] += np.sin(TAU * 62 * np.arange(nt) / SR) * np.exp(-np.arange(nt) / (SR * 0.035)) * 0.8
    x[-nsamp(0.08):] *= cosramp(nsamp(0.08), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def rattle(rng, dur=0.5, vel=0.6, density=28, base=84):
    """청동 방울 다발(팔주령)을 흔드는 소리: 높은 방울 여러 알이 잘게 부딪힌다."""
    n = nsamp(dur + 0.9)
    x = np.zeros(n)
    k = max(3, int(density * dur))
    for i in range(k):
        t0 = rng.uniform(0, dur) if i else 0.0
        b = bell(rng, base + rng.choice([0, 2, 5, 7, 9, 12, 14]) + rng.uniform(-0.3, 0.3), vel=rng.uniform(0.3, 1.0), kind='rattle')
        i0 = nsamp(t0)
        j = min(n, i0 + len(b))
        x[i0:j] += b[:j - i0]
    env = np.minimum(1, np.arange(n) / (SR * 0.01))
    x = hpf(x * env, 1500)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def jing(rng, vel=0.8, dur=3.2):
    """징: 낮게 웅- 하고 퍼지며 음이 살짝 내려앉는다."""
    n = nsamp(dur)
    t = np.arange(n) / SR
    droop = 1 - 0.035 * (1 - np.exp(-t / 0.5))
    x = np.zeros(n)
    for f, a, tau, bloom in [(152, 1.0, 2.6, 0.0), (221, 0.8, 2.2, 0.03), (296, 0.6, 1.8, 0.05), (367, 0.55, 1.5, 0.07), (455, 0.4, 1.2, 0.09), (548, 0.35, 1.0, 0.1), (764, 0.25, 0.8, 0.12), (1085, 0.16, 0.6, 0.14), (1490, 0.1, 0.45, 0.15)]:
        ph = np.cumsum(TAU * f * (1 + rng.uniform(-0.004, 0.004)) * droop / SR)
        b = 1 - np.exp(-t / bloom) if bloom else 1.0
        x += a * np.sin(ph + rng.uniform(0, TAU)) * np.exp(-t / tau) * b
    wash = bpf(rng.standard_normal(n), 300, 2400) * np.exp(-t / 0.5) * (1 - np.exp(-t / 0.06)) * 0.12
    x = x / (np.max(np.abs(x)) + 1e-9) + wash
    nt = nsamp(0.05)
    x[:nt] += np.sin(TAU * 80 * np.arange(nt) / SR) * np.exp(-np.arange(nt) / (SR * 0.02)) * 0.4
    x[-nsamp(0.2):] *= cosramp(nsamp(0.2), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def kkwaenggwari(rng, vel=0.7, open_=True):
    """꽹과리: open_ = 울리게(갠) / False = 손으로 막아(지)."""
    total = 0.5 if open_ else 0.11
    n = nsamp(total)
    t = np.arange(n) / SR
    x = np.zeros(n)
    k = 1.0 if open_ else 0.28
    for f, a, tau in [(835, 0.7, 0.22), (1262, 1.0, 0.2), (1644, 0.8, 0.17), (2180, 0.75, 0.14), (2862, 0.6, 0.11), (3610, 0.5, 0.09), (4420, 0.35, 0.07), (5370, 0.25, 0.055), (6800, 0.15, 0.04)]:
        x += a * np.sin(TAU * f * (1 + rng.uniform(-0.006, 0.006)) * t + rng.uniform(0, TAU)) * np.exp(-t / (tau * k))
    nc = nsamp(0.008)
    x[:nc] += hpf(rng.standard_normal(nc + 64), 2500)[:nc] * np.exp(-np.arange(nc) / (SR * 0.002)) * 1.2
    x[-nsamp(0.02):] *= cosramp(nsamp(0.02), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def jabara(rng, vel=0.7, choke=False, dur=1.1):
    """자바라 · 심벌즈: 맞부딪는 놋쇠판."""
    total = 0.16 if choke else dur
    n = nsamp(total)
    t = np.arange(n) / SR
    nz = bpf(rng.standard_normal(n), 2600, 12000)
    x = nz * np.exp(-t / (0.05 if choke else dur / 3.2))
    for f in rng.uniform(2200, 9000, 14):
        x += 0.12 * np.sin(TAU * f * t + rng.uniform(0, TAU)) * np.exp(-t / (0.04 if choke else rng.uniform(0.15, 0.5)))
    x *= np.minimum(1, t / 0.002)
    x[-nsamp(0.03):] *= cosramp(nsamp(0.03), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


# ───────────────────────────── 가죽 · 나무 ─────────────────────────────
def buk(rng, vel=0.8, pitch=1.0, big=False):
    """북 · 용고 · 대고. big = 큰북(더 낮고 길게)."""
    f0 = (64 if big else 92) * pitch
    total = 0.9 if big else 0.55
    n = nsamp(total)
    t = np.arange(n) / SR
    fq = f0 * (1 + 0.5 * vel * np.exp(-t / 0.035))
    ph = np.cumsum(TAU * fq / SR)
    tau = 0.3 if big else 0.17
    x = np.sin(ph) * np.exp(-t / tau)
    x += 0.45 * np.sin(1.59 * ph + 1.0) * np.exp(-t / (tau * 0.5))
    x += 0.25 * np.sin(2.14 * ph + 2.0) * np.exp(-t / (tau * 0.33))
    x += 0.15 * np.sin(2.65 * ph) * np.exp(-t / (tau * 0.25))
    nc = nsamp(0.03)
    ck = bpf(rng.standard_normal(nc + 64), 500, 3200)[:nc] * np.exp(-np.arange(nc) / (SR * 0.006))
    x[:nc] += ck / (np.max(np.abs(ck)) + 1e-9) * (0.35 + 0.3 * vel)
    sh = bpf(rng.standard_normal(n), 180, 700) * np.exp(-t / 0.06) * 0.18
    x = np.tanh((x + sh) * (1.2 + vel))
    x *= np.minimum(1, t / 0.001)
    x[-nsamp(0.03):] *= cosramp(nsamp(0.03), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def janggu(rng, stroke='deong', vel=0.8):
    """장구: gung(궁편 · 쿵) · chae(채편 · 덕) · deong(덩 = 함께) · gi(약한 채 · 기) · roll(더러러러)"""
    def gung(v):
        n = nsamp(0.42)
        t = np.arange(n) / SR
        fq = 98 * (1 + 0.35 * v * np.exp(-t / 0.03))
        ph = np.cumsum(TAU * fq / SR)
        x = np.sin(ph) * np.exp(-t / 0.14) + 0.4 * np.sin(1.6 * ph + 0.7) * np.exp(-t / 0.07)
        nc = nsamp(0.02)
        x[:nc] += bpf(rng.standard_normal(nc + 64), 300, 1500)[:nc] * np.exp(-np.arange(nc) / (SR * 0.005)) * 0.3
        x[-nsamp(0.03):] *= cosramp(nsamp(0.03), False)
        return x / (np.max(np.abs(x)) + 1e-9) * v

    def chae(v):
        n = nsamp(0.2)
        t = np.arange(n) / SR
        x = np.sin(TAU * 415 * t) * np.exp(-t / 0.035) * 0.6 + np.sin(TAU * 655 * t + 1) * np.exp(-t / 0.025) * 0.4
        nz = bpf(rng.standard_normal(n), 900, 7000) * np.exp(-t / 0.028)
        x = x + nz / (np.max(np.abs(nz)) + 1e-9) * 0.9
        x *= np.minimum(1, t / 0.0006)
        x[-nsamp(0.02):] *= cosramp(nsamp(0.02), False)
        return x / (np.max(np.abs(x)) + 1e-9) * v

    if stroke == 'gung':
        return gung(vel)
    if stroke == 'chae':
        return chae(vel)
    if stroke == 'gi':
        return chae(vel * 0.45)
    if stroke == 'deong':
        g, c = gung(vel), chae(vel * 0.8)
        g[:len(c)] += c
        return g / (np.max(np.abs(g)) + 1e-9) * vel
    if stroke == 'roll':
        n = nsamp(0.42)
        x = np.zeros(n)
        for i, (dt, v) in enumerate([(0.0, 1.0), (0.07, 0.7), (0.135, 0.55), (0.195, 0.42), (0.25, 0.32)]):
            c = chae(vel * v)
            i0 = nsamp(dt)
            j = min(n, i0 + len(c))
            x[i0:j] += c[:j - i0]
        return x
    raise ValueError(stroke)


def bak(rng, vel=0.8):
    """박: 나무판 여섯 쪽이 한꺼번에 딱 붙는 소리."""
    n = nsamp(0.16)
    x = np.zeros(n)
    for dt in (0.0, 0.004, 0.009, 0.013):
        m = nsamp(0.06)
        t = np.arange(m) / SR
        c = (np.sin(TAU * rng.uniform(1500, 2300) * t) * 0.6 + bpf(rng.standard_normal(m), 1200, 6000) * 0.8) * np.exp(-t / 0.012)
        i0 = nsamp(dt)
        x[i0:i0 + m] += c[:n - i0] * rng.uniform(0.6, 1.0)
    x[-nsamp(0.02):] *= cosramp(nsamp(0.02), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def woodblock(rng, vel=0.6, f=1050):
    n = nsamp(0.12)
    t = np.arange(n) / SR
    x = (np.sin(TAU * f * t) + 0.5 * np.sin(TAU * f * 2.63 * t)) * np.exp(-t / 0.02) + bpf(rng.standard_normal(n), 1500, 5000) * np.exp(-t / 0.006) * 0.5
    x[-nsamp(0.02):] *= cosramp(nsamp(0.02), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def stones(rng, vel=0.6, f=640):
    """돌 두 개를 맞부딪는 소리(선사 시대 타악)."""
    n = nsamp(0.14)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for r, a, tau in [(1.0, 1.0, 0.022), (1.71, 0.7, 0.016), (2.6, 0.5, 0.011), (3.83, 0.35, 0.008)]:
        x += a * np.sin(TAU * f * r * (1 + rng.uniform(-0.02, 0.02)) * t + rng.uniform(0, TAU)) * np.exp(-t / tau)
    x[:nsamp(0.004)] += hpf(rng.standard_normal(nsamp(0.004) + 64), 2000)[:nsamp(0.004)] * 0.8
    x[-nsamp(0.02):] *= cosramp(nsamp(0.02), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def snare(rng, vel=0.7, ghost=False):
    n = nsamp(0.26)
    t = np.arange(n) / SR
    tone = np.sin(TAU * 188 * t) * np.exp(-t / 0.05) + 0.6 * np.sin(TAU * 332 * t + 1) * np.exp(-t / 0.035)
    wires = bpf(rng.standard_normal(n), 1400, 9000) * np.exp(-t / (0.06 if ghost else 0.085))
    x = tone * 0.55 + wires / (np.max(np.abs(wires)) + 1e-9) * 0.9
    x *= np.minimum(1, t / 0.0006)
    x[-nsamp(0.03):] *= cosramp(nsamp(0.03), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel * (0.4 if ghost else 1.0)


def snare_roll(rng, dur, vel=0.6, rate=26, cresc=0.5):
    """작은북 굴리기: 빠른 잔 타격이 이어지며 점점 커진다."""
    n = nsamp(dur + 0.2)
    x = np.zeros(n)
    k = int(dur * rate)
    for i in range(k):
        s = snare(rng, vel=1.0, ghost=True)
        t0 = i / rate + rng.uniform(-0.004, 0.004)
        v = (1 - cresc) + cresc * (i / max(1, k - 1))
        i0 = max(0, nsamp(t0))
        j = min(n, i0 + len(s))
        x[i0:j] += s[:j - i0] * v
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def bassdrum(rng, vel=0.8):
    n = nsamp(0.6)
    t = np.arange(n) / SR
    fq = 52 * (1 + 0.8 * np.exp(-t / 0.02))
    x = np.sin(np.cumsum(TAU * fq / SR)) * np.exp(-t / 0.2)
    nc = nsamp(0.025)
    x[:nc] += bpf(rng.standard_normal(nc + 64), 250, 1800)[:nc] * np.exp(-np.arange(nc) / (SR * 0.006)) * 0.5
    x += bpf(rng.standard_normal(n), 120, 420) * np.exp(-t / 0.07) * 0.15
    x = np.tanh(x * 1.8)
    x[-nsamp(0.04):] *= cosramp(nsamp(0.04), False)
    return x / (np.max(np.abs(x)) + 1e-9) * vel


def cymbal(rng, vel=0.6, dur=1.6):
    return jabara(rng, vel=vel, choke=False, dur=dur)


# ───────────────────────────── 공간 · 마무리 ─────────────────────────────
def reverb_ir(rng, rt=1.5, pre=0.018, bright=5200):
    """공간 울림(임펄스 응답): 높은 소리가 먼저 사라지는 지수 감쇠 잡음."""
    n = nsamp(rt * 1.25)
    t = np.arange(n) / SR
    ir = np.zeros(n + nsamp(pre))
    for lo, hi, k in [(80, 400, 1.15), (400, 1500, 1.0), (1500, bright, 0.72), (bright, 11000, 0.4)]:
        b = bpf(rng.standard_normal(n), lo, hi) * np.exp(-t * 6.9 / (rt * k))
        ir[nsamp(pre):] += b / (np.sqrt(np.sum(b * b)) + 1e-9) * (1.0 if hi <= bright else 0.6)
    # 이른 반사 몇 개
    for dt, a in [(0.011, 0.5), (0.019, 0.42), (0.027, 0.35), (0.041, 0.28)]:
        ir[nsamp(dt)] += a * 0.12
    return ir / (np.sqrt(np.sum(ir * ir)) + 1e-9)


def soft_limit(x, knee=0.72):
    a = np.abs(x)
    over = a > knee
    y = x.copy()
    y[over] = np.sign(x[over]) * (knee + (1 - knee) * np.tanh((a[over] - knee) / (1 - knee)))
    return y
