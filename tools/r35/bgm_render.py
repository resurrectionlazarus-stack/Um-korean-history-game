#!/usr/bin/env python3
"""R35 시대 배경음악 — 악보(아래)를 합성 악기(bgm_lib.py)로 연주해 mp3로 굽는다. 전부 새로 지은 곡 · 녹음 소스 없음 · 시드 고정.

  era1  「돌과 불」        구석기 · 신석기   뼈피리 · 돌 타악 · 통나무북 · 낮은 '오-' 합창
  era2  「아사달」        고조선            훈(질나발) · 공후 · 청동 방울 · 큰북 · 제의 합창            (계면조 · 4/4)
  era3  「화랑」          삼국              가야금 · 거문고 · 대금 · 장구 · 북 · 징                    (평조 · 자진모리 12/8)
  era4  「전선의 북소리」  고려              피리 · 해금 · 거문고 · 가야금 · 편종 · 범종 · 장구 · 북     (계면조 · 휘모리 4/4)
  era5  「행주의 함성」    조선              태평소 · 나발 · 꽹과리 · 장구 · 북 · 징 · 자바라(대취타 + 풍물) (평조 · 휘모리 4/4)
  era6  「광복 행진곡」    대한제국 · 광복   군악대: 트럼펫 · 호른 · 트롬본 · 튜바 · 피콜로 · 작은북 · 큰북 · 심벌즈 (행진곡 4/4)

곡마다 두 구간: A = 전장(필드) · B = 보스전(같은 가락을 더 몰아침). 파일 = [표지음][A 몸통 + 꼬리][B 몸통 + 꼬리]
게임은 표지음(짧은 삑, 재생되지 않음) 위치로 mp3 디코더 지연을 보정하고, 몸통 길이마다 새로 겹쳐 틀어 이음매 없이 돈다(꼬리의 잔향이 다음 바퀴 처음에 겹친다).

사용: python3 tools/r35/bgm_render.py <출력 폴더(assets/bgm)> [era ...] [--meta json] [--wav 폴더] [--sheet png]
      (--meta = 구간 위치표. 기본 tools/r35/bgm_meta.json — r35_patch.py가 읽어 index.html의 R35_BGM 표로 넣는다)
필요: numpy · scipy · ffmpeg(libmp3lame). 게임 실행에는 필요 없음
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bgm_lib as L  # noqa: E402

SR = L.SR
TAIL = 2.0            # 구간 뒤 꼬리(잔향 · 남은 울림) 길이
PRE = 0.12            # 파일 처음 ~ A 몸통 시작(표지음 봉우리는 0.02s) → 표지음 ~ A 시작 = 0.1s
GAP = 0.1             # A 꼬리 ~ B 몸통 사이
NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi(name):
    i = 1
    v = NOTE[name[0]]
    while name[i] in '#b':
        v += 1 if name[i] == '#' else -1
        i += 1
    return v + 12 * (int(name[i:]) + 1)


def parse(line, unit=1.0):
    """'G4:3 A4:1~ r:2 | D5:3^' → [(시작, 길이, MIDI, 꾸밈)] (길이 단위 × unit). 꾸밈: ~ 농현 · ^ 위 꾸밈음 · v 아래 꾸밈음 · / 미끄러져 옴 · \\ 끝을 떨굼 · ! 세게 · , 여리게"""
    out = []
    pos = 0.0
    for tok in line.replace('|', ' ').split():
        name, _, rest = tok.partition(':')
        num = ''
        i = 0
        while i < len(rest) and (rest[i].isdigit() or rest[i] == '.'):
            num += rest[i]
            i += 1
        d = float(num) * unit
        if name != 'r':
            out.append((pos, d, midi(name), rest[i:]))
        pos += d
    return out, pos


class Song:
    def __init__(self, seed, bar_sec, bars):
        self.rng = np.random.default_rng(seed)
        self.bar = bar_sec
        self.body = bars * bar_sec
        self.n = L.nsamp(self.body + TAIL)
        self.stems = {}

    def stem(self, name, gain_db=0.0, send=0.2, hp=None):
        if name not in self.stems:
            self.stems[name] = dict(buf=np.zeros(self.n), gain=L.dbg(gain_db), send=send, hp=hp)
        return self.stems[name]

    def add(self, name, x, t, gain=1.0, human=0.0):
        s = self.stems[name]
        if human:
            t += self.rng.uniform(-human, human)
        i = int(round(t * SR))
        if i < 0:
            x = x[-i:]
            i = 0
        j = min(self.n, i + len(x))
        if j > i:
            s['buf'][i:j] += x[:j - i] * gain

    def mix(self, ir):
        dry = np.zeros(self.n)
        send = np.zeros(self.n)
        info = {}
        for name, s in self.stems.items():
            b = s['buf']
            if s['hp']:
                b = L.hpf(b, s['hp'])
            b = b * s['gain']
            dry += b
            send += b * s['send']
            info[name] = float(np.sqrt(np.mean(b[:L.nsamp(self.body)] ** 2)))
        wet = signal.fftconvolve(send, ir)[:self.n]
        out = dry + wet * 0.9
        # 꼬리 끝은 조용히 닫는다
        nf = L.nsamp(0.35)
        out[-nf:] *= L.cosramp(nf, False)
        return out, info


def master(parts, target_rms=0.115):
    """A · B를 같은 기준으로 마무리: 낮은 울림 정리 → 음량 맞춤 → 부드러운 한계."""
    parts = [p + 0.5 * L.hpf(p, 2800) for p in parts]      # 높은 쪽 살짝 올림(약 +3.5dB): 작은 스피커에서 악기 결이 또렷하게
    allx = np.concatenate(parts)
    allx = L.hpf(allx, 38)
    g = target_rms / (np.sqrt(np.mean(allx ** 2)) + 1e-12)
    out = []
    for p in parts:
        y = L.hpf(p, 38) * g
        y = L.soft_limit(y, 0.7)
        out.append(np.clip(y, -0.98, 0.98))
    return out


# ───────────────────────── 공통 연주 도우미 ─────────────────────────
def drums(S, stem, pattern_bars, step, table, bar0=0, vel=1.0, human=0.004):
    """글자 악보 연주. pattern_bars = 마디마다 문자열(글자 하나 = step초) · table[글자] = (악기 함수, 세기)"""
    for b, pat in enumerate(pattern_bars):
        for i, ch in enumerate(pat):
            if ch in table:
                fn, v = table[ch]
                v2 = v * vel * S.rng.uniform(0.9, 1.05)
                S.add(stem, fn(S.rng, v2), (bar0 + b) * S.bar + i * step, human=human)


def play_line(S, stem, notes, unit_sec, t0, fn, vel=0.75, legato=0.96, human=0.006, **kw):
    """가락 연주. fn(rng, midi, dur_sec, vel, flags, prev_midi) → 소리"""
    prev = None
    for (pos, d, m, fl) in notes:
        v = vel * (1.12 if '!' in fl else 0.8 if ',' in fl else 1.0) * S.rng.uniform(0.95, 1.04)
        x = fn(S.rng, m, d * unit_sec * legato, min(1.0, v), fl, prev, **kw)
        S.add(stem, x, t0 + pos * unit_sec, human=human)
        prev = m


def gaya(rng, m, dur, vel, fl, prev, kind='gayageum'):
    ng = (4.8, 0.013) if '~' in fl else ((5.2, 0.005) if dur > 0.5 else None)
    gl = (2 ** (-2 / 12.0), 0.05) if 'v' in fl else (2 ** (2 / 12.0), 0.05) if '^' in fl else None
    bd = [(dur * 0.55, 1.0), (dur * 0.8, 2 ** (-1 / 12.0))] if '\\' in fl else None
    return L.pluck(rng, m, dur, vel, kind, nonghyeon=ng, glide=gl, bend=bd)


def geom(rng, m, dur, vel, fl, prev):
    return L.pluck(rng, m, dur, vel, 'geomungo', nonghyeon=(4.4, 0.012) if '~' in fl else None, glide=(2 ** (-1 / 12.0), 0.06) if 'v' in fl else None)


def harp(rng, m, dur, vel, fl, prev):
    return L.pluck(rng, m, dur, vel, 'konghu')


def wind(kind):
    def f(rng, m, dur, vel, fl, prev):
        gr = 2 if '^' in fl else -2 if 'v' in fl else None
        gl = (L.hz(prev) / L.hz(m), 0.05) if '/' in fl and prev else None
        fa = (0.03, min(0.18, dur * 0.4)) if '\\' in fl else None
        return L.flute(rng, m, dur, vel, kind, grace=gr, glide=gl, fall=fa, vib=dur > 0.3, swell=0.22 if dur > 0.6 else 0.05)
    return f


def reedf(kind):
    def f(rng, m, dur, vel, fl, prev):
        gr = 2 if '^' in fl else -2 if 'v' in fl else None
        gl = (L.hz(prev) / L.hz(m), 0.045) if '/' in fl and prev else None
        fa = (0.035, min(0.16, dur * 0.4)) if '\\' in fl else None
        return L.reed(rng, m, dur, vel, kind, grace=gr, glide=gl, fall=fa, swell=0.14 if dur > 0.5 else 0.0)
    return f


def haeg(rng, m, dur, vel, fl, prev):
    gl = (L.hz(prev) / L.hz(m), 0.07) if '/' in fl and prev else None
    bd = [(dur * 0.6, 1.0), (dur * 0.9, 2 ** (-1 / 12.0))] if '\\' in fl else None
    return L.bowed(rng, m, dur, vel, glide=gl, bend=bd, swell=0.3 if dur > 0.5 else 0.1)


def brassf(kind, **kw):
    def f(rng, m, dur, vel, fl, prev):
        return L.brass(rng, m, dur, vel, kind, fall=(0.04, min(0.15, dur * 0.4)) if '\\' in fl else None, **kw)
    return f


J = dict(D=(lambda r, v: L.janggu(r, 'deong', v), 0.85), G=(lambda r, v: L.janggu(r, 'gung', v), 0.75), K=(lambda r, v: L.janggu(r, 'chae', v), 0.75),
         k=(lambda r, v: L.janggu(r, 'gi', v), 0.8), R=(lambda r, v: L.janggu(r, 'roll', v), 0.7))
BK = dict(B=(lambda r, v: L.buk(r, v), 0.9), b=(lambda r, v: L.buk(r, v), 0.55), T=(lambda r, v: L.buk(r, v, big=True), 0.95), t=(lambda r, v: L.buk(r, v, big=True), 0.6),
          x=(lambda r, v: L.woodblock(r, v), 0.5), s=(lambda r, v: L.stones(r, v), 0.6), S=(lambda r, v: L.stones(r, v, f=520), 0.8))
KW = dict(X=(lambda r, v: L.kkwaenggwari(r, v, True), 0.7), x=(lambda r, v: L.kkwaenggwari(r, v, False), 0.55))


# ───────────────────────── 3시대 삼국 「화랑」 ─────────────────────────
def era3(sec):
    P = 0.2                       # 8분음 하나(자진모리: 점4분 = 100)
    bar = 12 * P
    if sec == 'A':
        S = Song(3301, bar, 16)
        S.stem('gaya', -5.5, 0.22); S.stem('gaya2', -11, 0.2); S.stem('geom', -6, 0.16, hp=45); S.stem('dae', -7.5, 0.34)
        S.stem('jang', -7, 0.12); S.stem('buk', -9.5, 0.14, hp=40); S.stem('jing', -13, 0.35); S.stem('bak', -6, 0.25)
        S.add('bak', L.bak(S.rng, 0.8), 0)
        S.add('jing', L.jing(S.rng, 0.7), 0); S.add('jing', L.jing(S.rng, 0.6), 8 * bar)
        P1, P2, P3 = 'D..G..G.KG..', 'D.kG.kG.KG.k', 'D..G.KG.KGR.'
        drums(S, 'jang', [P1, P2, P1, P3] * 4, P, J)
        drums(S, 'buk', ['B.....b.....', 'B.....b.....', 'B.....b.....', 'B.....b..b.b'] * 4, P, BK)
        roots = ['G2', 'G2', 'C3', 'G2', 'D3', 'C3', 'G2', 'G2'] * 2
        for b, r in enumerate(roots):
            m = midi(r)
            for pu, dm, v in [(0, 0, 0.9), (3, 7, 0.6), (6, 0, 0.78), (9, 7, 0.6)]:
                S.add('geom', L.pluck(S.rng, m + dm, 3 * P, v, 'geomungo'), b * bar + pu * P, human=0.005)
                S.add('gaya2', L.pluck(S.rng, m + dm + 12, 3 * P, v * 0.5, 'gayageum'), b * bar + pu * P, human=0.006)
        mel = ('G4:3 A4:1 C5:2 D5:3 C5:1 A4:2 | G4:3 E4:1 G4:2 A4:6~ | C5:3 D5:1 E5:2 D5:3 C5:1 A4:2 | G4:2 A4:1 G4:3 G4:6~ | '
               'D5:3 E5:1 G5:2 E5:3 D5:1 C5:2 | D5:3 C5:1 A4:2 C5:6~ | A4:2 C5:1 D5:3 C5:2 A4:1 G4:3 | A4:3 G4:1 E4:2 G4:6~')
        notes, _ = parse(mel)
        play_line(S, 'gaya', notes, P, 0, gaya, vel=0.82)
        # 9~16마디: 대금이 가락을 받고 가야금은 잔가락(분산)으로
        dm = ('D5:6 E5:3^ D5:3 | C5:6 A4:6\\ | G4:3 A4:3 C5:3 D5:3 | E5:9^ D5:3 | G5:6^ E5:3 D5:3 | E5:6 C5:6\\ | D5:3 C5:3 A4:3 G4:3 | G4:12')
        notes, _ = parse(dm)
        play_line(S, 'dae', notes, P, 8 * bar, wind('daegeum'), vel=0.78, legato=0.98, human=0.01)
        arp = {'G2': 'G3:1 D4:1 G4:1 D4:1 E4:1 D4:1 G3:1 D4:1 G4:1 A4:1 G4:1 D4:1', 'C3': 'C4:1 G4:1 C5:1 G4:1 A4:1 G4:1 C4:1 G4:1 C5:1 D5:1 C5:1 G4:1', 'D3': 'D4:1 A4:1 D5:1 A4:1 C5:1 A4:1 D4:1 A4:1 D5:1 E5:1 D5:1 A4:1'}
        for b in range(8, 16):
            notes, _ = parse(arp[roots[b]])
            play_line(S, 'gaya', notes, P, b * bar, gaya, vel=0.6)
    else:
        S = Song(3302, bar, 8)
        S.stem('gaya', -6, 0.2); S.stem('geom', -7, 0.14, hp=45); S.stem('dae', -7, 0.32); S.stem('jang', -6.5, 0.12); S.stem('buk', -9, 0.14, hp=40); S.stem('jing', -12, 0.35); S.stem('bak', -6, 0.25)
        S.add('bak', L.bak(S.rng, 0.9), 0)
        for b in (0, 2, 4, 6):
            S.add('jing', L.jing(S.rng, 0.75), b * bar)
        drums(S, 'jang', ['D.KG.KD.KG.K', 'D.KG.KD.KGKK', 'D.KG.KD.KG.K', 'DKKG.KD.KGR.'] * 2, P, J)
        drums(S, 'buk', ['B..b..B..b..', 'B..b..B..b.b', 'B..b..B..b..', 'B..b..B.bB.B'] * 2, P, BK)
        roots = ['G2', 'G2', 'C3', 'G2', 'D3', 'C3', 'G2', 'G2']
        for b, r in enumerate(roots):
            m = midi(r)
            for pu in range(0, 12, 1):
                acc = pu % 3 == 0
                S.add('geom', L.pluck(S.rng, m + (7 if pu % 6 == 3 else 0), P, 0.85 if acc else 0.5, 'geomungo'), b * bar + pu * P, human=0.004)
        riff = {'G2': 'G4:1 A4:1 C5:1 D5:1 C5:1 A4:1 D5:1 E5:1 G5:1 E5:1 D5:1 C5:1', 'C3': 'C5:1 D5:1 E5:1 G5:1 E5:1 D5:1 C5:1 A4:1 C5:1 D5:1 C5:1 A4:1', 'D3': 'D5:1 E5:1 G5:1 A5:1 G5:1 E5:1 D5:1 C5:1 D5:1 E5:1 D5:1 A4:1'}
        for b, r in enumerate(roots):
            notes, _ = parse(riff[r])
            play_line(S, 'gaya', notes, P, b * bar, gaya, vel=0.8, human=0.004)
        dm = ('G5:12^ | E5:9 D5:3 | D5:6 E5:6^ | G5:12 | A5:12^ | G5:6 E5:6 | D5:6 C5:3 A4:3 | G4:12')
        notes, _ = parse(dm)
        play_line(S, 'dae', notes, P, 0, wind('daegeum'), vel=0.86, legato=0.98, human=0.008)
    return S


# ───────────────────────── 2시대 고조선 「아사달」 ─────────────────────────
def era2(sec):
    beat = 60 / 92.0
    bar = 4 * beat
    st = beat / 2                                   # 8분음
    HARP = {'E': 'E3 B3 E4 B3 G4 B3 E4 B3', 'G': 'G3 D4 G4 D4 B4 D4 G4 D4', 'D': 'D3 A3 D4 A3 G4 A3 D4 A3'}
    if sec == 'A':
        S = Song(2201, bar, 16)
        S.stem('hun', -9, 0.4); S.stem('harp', -7.5, 0.3); S.stem('chant', -10.5, 0.45); S.stem('drum', -7, 0.16, hp=36); S.stem('wood', -8, 0.2); S.stem('bells', -7.5, 0.42)
        Pa, Pb, Pc, Pd = 'T..b..T.', 'T..b.bT.', 'T.bT..T.', 'T.bT.bTT'
        drums(S, 'drum', [Pa, Pb, Pa, Pc, Pa, Pb, Pa, Pd] * 2, st, BK)
        drums(S, 'wood', ['..x...x.'] * 16, st, BK)
        roots = ['E', 'E', 'G', 'E', 'G', 'D', 'E', 'D', 'E', 'G', 'D', 'E', 'G', 'E', 'E', 'E']
        for b, r in enumerate(roots):
            for i, nm in enumerate(HARP[r].split()):
                S.add('harp', L.pluck(S.rng, midi(nm), st * 2, 0.75 if i % 4 == 0 else 0.5, 'konghu'), b * bar + i * st, human=0.006)
        for b in range(0, 16, 2):
            S.add('chant', L.chant(S.rng, 40, 2 * bar - 0.3, 0.5, 'o' if b % 4 == 0 else 'a'), b * bar)
            S.add('chant', L.chant(S.rng, 47, 2 * bar - 0.3, 0.4, 'o'), b * bar)
        S.add('bells', L.rattle(S.rng, 1.1, 0.7, 26), 0)
        for b in range(1, 16, 2):
            S.add('bells', L.rattle(S.rng, 0.3, 0.5, 30), b * bar + 2 * beat)
        for b in (7, 15):
            S.add('bells', L.rattle(S.rng, 1.3, 0.7, 24), b * bar + 2 * beat)
        mel = ('E4:2 G4:1 A4:1 | B4:3~ A4:1 | G4:1 A4:1 G4:1 E4:1 | E4:4~\\ | '
               'B4:2 D5:1^ B4:1 | A4:2 G4:1 A4:1 | B4:1 A4:1 G4:1 E4:1 | D4:2 E4:2~ | '
               'E5:2^ D5:1 B4:1 | D5:2 B4:1 A4:1 | B4:1 A4:1 G4:1 A4:1 | B4:4~ | '
               'G4:1 A4:1 B4:1 D5:1 | E5:2^ D5:1 B4:1 | A4:1 G4:1 E4:1 G4:1 | E4:4~\\')
        notes, _ = parse(mel)
        play_line(S, 'hun', notes, beat, 0, wind('hun'), vel=0.8, legato=0.97, human=0.012)
    else:
        S = Song(2202, bar, 8)
        S.stem('hun', -9.5, 0.38); S.stem('sog', -11, 0.4); S.stem('harp', -8, 0.28); S.stem('chant', -9.5, 0.45); S.stem('drum', -6.5, 0.16, hp=36); S.stem('wood', -7.5, 0.2); S.stem('bells', -7.5, 0.42); S.stem('horn', -8.5, 0.4)
        drums(S, 'drum', ['T.bT.bTb', 'T.bT.bTT', 'T.bT.bTb', 'TbbT.bTT'] * 2, st, BK)
        drums(S, 'wood', ['.x.x.x.x'] * 8, st, BK)
        roots = ['E', 'G', 'D', 'E', 'G', 'E', 'D', 'E']
        for b, r in enumerate(roots):
            seq = HARP[r].split()
            for i in range(16):
                S.add('harp', L.pluck(S.rng, midi(seq[i % 8]) + (12 if i % 2 else 0), st, 0.7 if i % 4 == 0 else 0.48, 'konghu'), b * bar + i * st / 2, human=0.004)
        for b in range(0, 8, 2):
            S.add('chant', L.chant(S.rng, 40, 2 * bar - 0.3, 0.55, 'a'), b * bar)
            S.add('chant', L.chant(S.rng, 47, 2 * bar - 0.3, 0.45, 'a'), b * bar)
            S.add('chant', L.chant(S.rng, 52, 2 * bar - 0.3, 0.35, 'a'), b * bar)
            S.add('horn', L.brass(S.rng, 52, 1.5 * beat, 0.7, 'nabal'), b * bar)
        for b in range(8):
            S.add('bells', L.rattle(S.rng, 0.5, 0.6, 30), b * bar + 2 * beat)
        mel = ('E5:2^ D5:1 B4:1 | D5:2 B4:1 A4:1 | B4:1 A4:1 G4:1 A4:1 | B4:4~ | '
               'G4:1 A4:1 B4:1 D5:1 | E5:2^ D5:1 B4:1 | A4:1 G4:1 E4:1 G4:1 | E4:4~')
        notes, _ = parse(mel)
        play_line(S, 'hun', notes, beat, 0, wind('hun'), vel=0.85, legato=0.97, human=0.01)
        up = [(p, d, m + 12, f) for (p, d, m, f) in notes]
        play_line(S, 'sog', up, beat, 0, wind('sogeum'), vel=0.7, legato=0.95, human=0.012)
    return S


# ───────────────────────── 4시대 고려 「전선의 북소리」 ─────────────────────────
def era4(sec):
    beat = 60 / 126.0
    bar = 4 * beat
    st = beat / 2
    OST = {'A': 'A3 E4 A4 E4 C5 E4 A4 E4', 'G': 'G3 D4 G4 D4 A4 D4 G4 D4', 'C': 'C4 G4 C5 G4 E5 G4 C5 G4', 'D': 'D4 A4 D5 A4 E5 A4 D5 A4'}
    ROOT = {'A': 45, 'G': 43, 'C': 48, 'D': 50}

    def comp(S, roots, bar0=0, dense=False, gv=0.55):
        for b, r in enumerate(roots):
            t0 = (bar0 + b) * bar
            for i, nm in enumerate(OST[r].split()):
                S.add('gaya', L.pluck(S.rng, midi(nm), st * 1.5, gv * (1.25 if i % 4 == 0 else 1.0), 'gayageum'), t0 + i * st, human=0.005)
            m = ROOT[r]
            hits = [(0, 0, 0.92), (2, 0, 0.5), (3, 0, 0.62), (4, 7, 0.75), (6, 0, 0.62), (7, 7, 0.5)] if dense else [(0, 0, 0.92), (3, 0, 0.58), (4, 7, 0.72), (6, 0, 0.6)]
            for i, dm, v in hits:
                S.add('geom', L.pluck(S.rng, m + dm, st * 2, v, 'geomungo'), t0 + i * st, human=0.004)
                S.add('gaya2', L.pluck(S.rng, m + dm + 12, st * 2, v * 0.45, 'gayageum'), t0 + i * st, human=0.005)

    if sec == 'A':
        S = Song(4401, bar, 20)
        S.stem('piri', -8, 0.3); S.stem('haeg', -7, 0.32); S.stem('gaya', -9.5, 0.22); S.stem('gaya2', -12, 0.2); S.stem('geom', -7, 0.15, hp=45)
        S.stem('jang', -7.5, 0.12); S.stem('buk', -10, 0.14, hp=40); S.stem('pj', -9, 0.45); S.stem('bj', -10.5, 0.5, hp=40)
        J1, J2, J3 = 'D.K.GKG.', 'D.K.GKGK', 'D.K.GKR.'
        drums(S, 'jang', [J1, J2, J1, J3] * 5, st, J)
        drums(S, 'buk', ['B...b...', 'B...b.b.', 'B...b...', 'B.b.B.bB'] * 5, st, BK)
        roots = ['A', 'A', 'A', 'A', 'C', 'C', 'G', 'A', 'A', 'G', 'C', 'A', 'D', 'A', 'G', 'A', 'A', 'G', 'C', 'A']
        comp(S, roots)
        for b in (0, 8, 16):
            S.add('bj', L.bell(S.rng, 45, 0.8, 'beomjong'), b * bar)
        for b in (0, 4, 8, 12):
            S.add('pj', L.bell(S.rng, 81, 0.6, 'pyeonjong'), b * bar)
            S.add('pj', L.bell(S.rng, 76, 0.5, 'pyeonjong'), b * bar + 0.02)
        pm = ('A4:1.5 C5:.5 D5:1 E5:1 | E5:2~ D5:.5 C5:.5 D5:1 | C5:1 A4:1 G4:1 A4:1 | A4:3~\\ r:1 | '
              'E5:1.5 G5:.5^ E5:1 D5:1 | C5:1 D5:1 E5:2~ | D5:1 C5:1 A4:1 G4:1 | A4:4~')
        notes, _ = parse(pm)
        play_line(S, 'piri', notes, beat, 0, reedf('piri'), vel=0.78, legato=0.96, human=0.008)
        hm = ('A5:2 G5:1/ E5:1/ | G5:1.5 E5:.5/ D5:2~ | C5:1 D5:1/ E5:1/ G5:1/ | E5:4~\\ | '
              'D5:1 E5:1/ D5:1/ C5:1/ | A4:2~ C5:1/ D5:1/ | E5:1 D5:1/ C5:1/ A4:1/ | A4:4~')
        notes, _ = parse(hm)
        play_line(S, 'haeg', notes, beat, 8 * bar, haeg, vel=0.74, legato=1.0, human=0.01)
        # 17~20마디: 가락 없이 편종이 받는 사이 가락
        bm = 'A5:2 E5:2 | G5:2 D5:2 | C5:1 D5:1 E5:2 | A5:4'
        notes, _ = parse(bm)
        for (pos, d, m, fl) in notes:
            S.add('pj', L.bell(S.rng, m, 0.7, 'pyeonjong'), 16 * bar + pos * beat, human=0.004)
    else:
        S = Song(4402, bar, 8)
        S.stem('piri', -8.5, 0.3); S.stem('haeg', -8.5, 0.32); S.stem('gaya', -9.5, 0.2); S.stem('gaya2', -12, 0.2); S.stem('geom', -7, 0.14, hp=45)
        S.stem('jang', -7, 0.12); S.stem('buk', -9, 0.14, hp=40); S.stem('bj', -10.5, 0.5, hp=40); S.stem('jab', -9, 0.3)
        drums(S, 'jang', ['DKK.GKGK', 'D.KKGKGK', 'DKK.GKGK', 'D.KKGKR.'] * 2, st, J)
        drums(S, 'buk', ['B.b.B.b.', 'B.b.B.bb', 'B.b.B.b.', 'B.bbB.BB'] * 2, st, BK)
        roots = ['A', 'A', 'C', 'G', 'A', 'A', 'D', 'A']
        comp(S, roots, dense=True, gv=0.6)
        for b in (0, 4):
            S.add('bj', L.bell(S.rng, 45, 0.85, 'beomjong'), b * bar)
            S.add('jab', L.jabara(S.rng, 0.8), b * bar)
        for b in range(8):
            for i in (2, 6):
                S.add('jab', L.jabara(S.rng, 0.45, choke=True), b * bar + i * st)
        bm = ('E5:1! E5:.5 D5:.5 E5:1 G5:1 | A5:2~ G5:1 E5:1 | G5:1 E5:1 D5:1 C5:1 | D5:3~ r:1 | '
              'E5:1! E5:.5 D5:.5 E5:1 G5:1 | A5:1.5 G5:.5 A5:2~ | G5:1 E5:1 D5:1 C5:1 | A4:4~')
        notes, _ = parse(bm)
        play_line(S, 'piri', notes, beat, 0, reedf('piri'), vel=0.82, legato=0.95, human=0.007)
        play_line(S, 'haeg', [(p, d, m, f + '/') for (p, d, m, f) in notes], beat, 0, haeg, vel=0.72, legato=1.0, human=0.012)
    return S


# ───────────────────────── 5시대 조선 「행주의 함성」 ─────────────────────────
def era5(sec):
    beat = 60 / 132.0
    bar = 4 * beat
    st = beat / 2

    def samul(S, n, kk, jj, bb, jing_every=2, nabal_bars=()):
        drums(S, 'kkw', kk, st, KW)
        drums(S, 'jang', jj, st, J)
        drums(S, 'buk', bb, st, BK)
        for b in range(0, n, jing_every):
            S.add('jing', L.jing(S.rng, 0.7), b * bar)
        for b in nabal_bars:
            S.add('nabal', L.brass(S.rng, 50, 3.6 * beat, 0.75, 'nabal', swell=0.2), b * bar)
            S.add('nabal', L.brass(S.rng, 57, 3.6 * beat, 0.55, 'nabal', swell=0.2), b * bar)
            S.add('nabal', L.brass(S.rng, 62, 3.6 * beat, 0.4, 'nabal', swell=0.2), b * bar)

    if sec == 'A':
        S = Song(5501, bar, 20)
        S.stem('tps', -7.5, 0.32); S.stem('nabal', -10.5, 0.35); S.stem('kkw', -9.5, 0.22); S.stem('jang', -6.5, 0.12); S.stem('buk', -11.5, 0.14, hp=40); S.stem('jing', -12.5, 0.38)
        K1, K2, K3, K4 = 'X.xxX.x.', 'X.xxXxx.', 'XxxxX.x.', 'XxXxXxXX'
        samul(S, 20, [K1, K2, K1, K3] * 4 + [K3, K2, K3, K4], ['D.K.GKG.', 'D.KKGKG.', 'D.K.GKG.', 'DKK.GKR.'] * 5, ['B...B...', 'B...B.b.', 'B...B...', 'B.b.B.BB'] * 5, nabal_bars=(0, 2, 4, 6, 8, 10, 12, 14, 16, 17, 18, 19))
        tm = ('D5:1 E5:.5 G5:.5 A5:2~ | B5:1^ A5:.5 G5:.5 A5:2 | G5:1 E5:1 D5:1 E5:1 | D5:3~\\ r:1 | '
              'A5:1 B5:.5 A5:.5 G5:1 E5:1 | G5:2~ A5:1 B5:1 | D6:2^ B5:1 A5:1 | A5:4~ | '
              'B5:1 D6:1 B5:1 A5:1 | G5:1 A5:1 B5:2~ | A5:1 G5:1 E5:1 D5:1 | E5:4~\\ | '
              'D5:1 E5:1 G5:1 A5:1 | B5:2^ D6:2 | B5:1 A5:1 G5:1 E5:1 | D5:4~')
        notes, _ = parse(tm)
        play_line(S, 'tps', notes, beat, 0, reedf('taepyeongso'), vel=0.72, legato=0.95, human=0.008)
    else:
        S = Song(5502, bar, 8)
        S.stem('tps', -7.5, 0.32); S.stem('nabal', -10, 0.35); S.stem('kkw', -9, 0.22); S.stem('jang', -6, 0.12); S.stem('buk', -10.5, 0.14, hp=40); S.stem('jing', -12.5, 0.38); S.stem('jab', -9.5, 0.3)
        samul(S, 8, ['XxxxX.xx', 'XxXxXxx.', 'XxxxX.xx', 'XxXxXxXX'] * 2, ['DKK.GKGK', 'D.KKGKGK', 'DKK.GKGK', 'DKKKGKR.'] * 2, ['B.b.B.b.', 'B.b.B.bb', 'B.b.B.b.', 'B.bbB.BB'] * 2, jing_every=1, nabal_bars=(0, 1, 2, 3, 4, 5, 6, 7))
        for b in (0, 4):
            S.add('jab', L.jabara(S.rng, 0.8), b * bar)
        tm = ('D6:1! B5:.5 A5:.5 B5:1 D6:1 | E6:2~ D6:1 B5:1 | A5:1 B5:1 D6:1 B5:1 | A5:3~ r:1 | '
              'D6:1! B5:.5 A5:.5 B5:1 D6:1 | E6:1.5 D6:.5 E6:2~ | D6:1 B5:1 A5:1 G5:1 | A5:1 B5:1 D6:2~')
        notes, _ = parse(tm)
        play_line(S, 'tps', notes, beat, 0, reedf('taepyeongso'), vel=0.76, legato=0.94, human=0.007)
    return S


# ───────────────────────── 6시대 대한제국 · 광복 「광복 행진곡」 ─────────────────────────
def era6(sec):
    beat = 60 / 116.0
    bar = 4 * beat
    s16 = beat / 4
    SN = dict(S=(lambda r, v: L.snare(r, v), 0.8), s=(lambda r, v: L.snare(r, v, ghost=True), 0.9))
    CH = {'Bb': (34, [58, 62, 65]), 'Eb': (39, [58, 63, 67]), 'F': (41, [57, 60, 65]), 'Gm': (43, [58, 62, 67]), 'Cm': (36, [60, 63, 67]), 'D': (38, [57, 62, 66])}

    def band(S, chords, tb_vel=0.8, pound=False):
        """튜바(1 · 3박) + 호른(2 · 4박 뒷박) + 큰북 · 작은북. chords = 마디마다 [앞 두 박, 뒤 두 박]"""
        for b, (c1, c2) in enumerate(chords):
            for h, c in enumerate((c1, c2)):
                root, tri = CH[c]
                t0 = b * bar + h * 2 * beat
                S.add('tuba', L.brass(S.rng, root if h == 0 else root + 7 - (12 if root + 7 > 45 else 0), beat * 0.8, tb_vel, 'tuba'), t0, human=0.004)
                S.add('tuba2', L.brass(S.rng, (root if h == 0 else root + 7 - (12 if root + 7 > 45 else 0)) + 12, beat * 0.7, tb_vel * 0.6, 'trombone'), t0, human=0.004)
                if pound:
                    S.add('tuba', L.brass(S.rng, root, beat * 0.7, tb_vel * 0.8, 'tuba'), t0 + beat, human=0.004)
                for m in tri[:2] if not pound else tri:
                    S.add('horn', L.brass(S.rng, m, beat * 0.45, 0.6, 'horn'), t0 + beat, human=0.006)
                S.add('bd', L.bassdrum(S.rng, 0.85 if h == 0 else 0.7), t0)

    if sec == 'A':
        S = Song(6601, bar, 16)
        S.stem('tp', -8, 0.26); S.stem('tb', -12, 0.26); S.stem('horn', -12, 0.24); S.stem('tuba', -9.5, 0.12, hp=34); S.stem('tuba2', -11.5, 0.14); S.stem('picc', -14, 0.3)
        S.stem('sn', -6.5, 0.16); S.stem('bd', -9.5, 0.12, hp=34); S.stem('cym', -11, 0.3)
        chords = [('Bb', 'Bb'), ('Eb', 'Bb'), ('Eb', 'F'), ('F', 'F'), ('Bb', 'Bb'), ('Eb', 'Bb'), ('F', 'F'), ('Bb', 'Bb'),
                  ('Eb', 'Bb'), ('Eb', 'Bb'), ('Bb', 'Bb'), ('Bb', 'Bb'), ('Eb', 'Bb'), ('F', 'F'), ('Bb', 'Eb'), ('Bb', 'Bb')]
        band(S, chords)
        N1, N2, N3 = 'S...S.ssS...S.ss', 'S...S.ssS.ssS.ss', 'S...S.ssS.ssSsss'
        drums(S, 'sn', [N1, N2, N1, N3] * 4, s16, SN, human=0.003)
        for b in (3, 7, 11, 15):
            S.add('sn', L.snare_roll(S.rng, beat * 0.95, 0.7), b * bar + 3 * beat)
        for b in (0, 4, 8, 12):
            S.add('cym', L.cymbal(S.rng, 0.7), b * bar)
        tm = ('F4:1 Bb4:1 D5:1.5 C5:.5 | Bb4:1 G4:1 F4:2 | G4:1 Bb4:1 C5:1 D5:1 | C5:3 r:1 | '
              'F4:1 Bb4:1 D5:1.5 F5:.5 | G5:1 F5:1 D5:2 | C5:1 D5:1 F5:1 D5:1 | Bb4:3 r:1 | '
              'G5:1.5 F5:.5 D5:1 F5:1 | G5:2 F5:2 | D5:1 C5:1 Bb4:1 C5:1 | D5:2 F5:2 | '
              'G5:1 G5:1 F5:1 D5:1 | C5:1 D5:1 F5:2 | D5:1 C5:1 Bb4:1 G4:1 | Bb4:3 r:1')
        notes, _ = parse(tm)
        play_line(S, 'tp', notes, beat, 0, brassf('trumpet'), vel=0.8, legato=0.88, human=0.006)
        # 두 번째 트럼펫: 3도 · 6도 아래 화음(9마디부터)
        lo = [(p, d, m - (3 if (m % 12) in (2, 5, 10) else 4), f) for (p, d, m, f) in notes if p >= 32]
        play_line(S, 'tp', lo, beat, 0, brassf('trumpet'), vel=0.5, legato=0.88, human=0.008)
        # 트롬본: 긴 화음음(9마디부터)
        for b in range(8, 16):
            for h, c in enumerate(chords[b]):
                S.add('tb', L.brass(S.rng, CH[c][1][1] - 12, 2 * beat * 0.92, 0.6, 'trombone'), b * bar + h * 2 * beat, human=0.006)
        # 피콜로: 9마디부터 높은 잔가락
        pat = {'Bb': 'Bb5:.5 C6:.5 D6:.5 F6:.5', 'Eb': 'Bb5:.5 Eb6:.5 G6:.5 Eb6:.5', 'F': 'A5:.5 C6:.5 F6:.5 C6:.5'}
        for b in range(8, 16):
            for h, c in enumerate(chords[b]):
                ns, _ = parse(pat[c])
                play_line(S, 'picc', ns, beat, b * bar + h * 2 * beat, wind('piccolo'), vel=0.6, legato=0.8, human=0.005)
    else:
        S = Song(6602, bar, 8)
        S.stem('tp', -8, 0.26); S.stem('tb', -11, 0.26); S.stem('horn', -12, 0.24); S.stem('tuba', -9, 0.12, hp=34); S.stem('tuba2', -11, 0.14)
        S.stem('sn', -6, 0.16); S.stem('bd', -9, 0.12, hp=34); S.stem('cym', -10.5, 0.3)
        chords = [('Gm', 'Gm'), ('Gm', 'Gm'), ('Eb', 'Eb'), ('D', 'D'), ('Gm', 'Gm'), ('Cm', 'Cm'), ('D', 'D'), ('Gm', 'Gm')]
        band(S, chords, tb_vel=0.85, pound=True)
        drums(S, 'sn', ['S.ssS.ssS.ssS.ss', 'S.ssS.ssSsssS.ss', 'S.ssS.ssS.ssS.ss', 'S.ssSsssS.ssSsss'] * 2, s16, SN, human=0.003)
        for b in (3, 7):
            S.add('sn', L.snare_roll(S.rng, beat * 1.9, 0.75), b * bar + 2 * beat)
        for b in (0, 2, 4, 6):
            S.add('cym', L.cymbal(S.rng, 0.75), b * bar)
        tm = ('G4:1! Bb4:1 D5:1.5 D5:.5 | Eb5:1 D5:1 Bb4:2 | Eb5:1! G5:1 Eb5:1 C5:1 | D5:3 r:1 | '
              'G4:1! Bb4:1 D5:1.5 D5:.5 | Eb5:1 G5:1 C5:2 | D5:1 F#5:1 A5:1 F#5:1 | G5:3 r:1')
        notes, _ = parse(tm)
        play_line(S, 'tp', notes, beat, 0, brassf('trumpet'), vel=0.86, legato=0.86, human=0.005)
        play_line(S, 'tb', [(p, d, m - 12, f) for (p, d, m, f) in notes], beat, 0, brassf('trombone'), vel=0.7, legato=0.86, human=0.007)
    return S


# ───────────────────────── 1시대 구석기 · 신석기 「돌과 불」 ─────────────────────────
def era1(sec):
    P = 0.26                      # 8분음 하나(느린 12/8)
    bar = 12 * P
    if sec == 'A':
        S = Song(1101, bar, 12)
        S.stem('fl', -8.5, 0.42); S.stem('chant', -9.5, 0.45); S.stem('log', -8, 0.18, hp=36); S.stem('st', -4, 0.25); S.stem('rat', -8, 0.4)
        drums(S, 'log', ['T.....t..t..', 'T.....t.....', 'T.....t..t..', 'T..t..t..t.t'] * 3, P, BK)
        drums(S, 'st', ['..s..s..s..s', '..s..s.ss..s', '..s..s..s..s', '.ss..s.ss.Ss'] * 3, P, BK)
        for b in range(0, 12, 2):
            S.add('chant', L.chant(S.rng, 45, 2 * bar - 0.4, 0.5, 'o'), b * bar)
            S.add('chant', L.chant(S.rng, 52, 2 * bar - 0.4, 0.38, 'o'), b * bar)
        for b in (3, 7, 11):
            S.add('rat', L.rattle(S.rng, 0.8, 0.6, 18, base=79), b * bar + 6 * P)
        mel = ('E4:6 G4:3 A4:3 | B4:9~ A4:3 | G4:3 A4:3 G4:3 E4:3 | E4:12~\\ | '
               'B4:6^ A4:3 G4:3 | A4:6 B4:6~ | G4:3 E4:3 D4:3 E4:3 | E4:12~ | '
               'E5:6^ B4:3 A4:3 | B4:6 G4:6 | A4:3 G4:3 E4:3 G4:3 | E4:12~\\')
        notes, _ = parse(mel)
        notes = [(p_, d, m + 5, f) for (p_, d, m, f) in notes]          # 라(A) 계면조: 뼈피리 음역(A4~A5)
        play_line(S, 'fl', notes, P, 0, wind('bone'), vel=0.8, legato=0.97, human=0.014)
    else:
        S = Song(1102, bar, 6)
        S.stem('fl', -8.5, 0.42); S.stem('chant', -8.5, 0.45); S.stem('log', -8, 0.18, hp=36); S.stem('st', -3.5, 0.25); S.stem('rat', -7.5, 0.4)
        drums(S, 'log', ['T..t..T..t..', 'T..t..T..t.t', 'T..t..T..t..', 'T.tt..T.tT.T', 'T..t..T..t..', 'T.tT.tT.tTtT'], P, BK)
        drums(S, 'st', ['.ss.ss.ss.ss', '.ss.ss.ss.Ss', '.ss.ss.ss.ss', '.sS.ss.sS.Ss', '.ss.ss.ss.ss', 'sSs.sSs.sSsS'], P, BK)
        for b in range(0, 6, 2):
            S.add('chant', L.chant(S.rng, 45, 2 * bar - 0.4, 0.55, 'a'), b * bar)
            S.add('chant', L.chant(S.rng, 52, 2 * bar - 0.4, 0.45, 'a'), b * bar)
            S.add('chant', L.chant(S.rng, 57, 2 * bar - 0.4, 0.35, 'a'), b * bar)
        for b in range(6):
            S.add('rat', L.rattle(S.rng, 0.5, 0.6, 20, base=79), b * bar + 6 * P)
        mel = ('E5:6^ B4:3 A4:3 | B4:6 D5:6~ | E5:3 D5:3 B4:3 A4:3 | B4:12~ | A4:3 B4:3 D5:3 E5:3 | E5:12~')
        notes, _ = parse(mel)
        notes = [(p_, d, m + 5, f) for (p_, d, m, f) in notes]
        play_line(S, 'fl', notes, P, 0, wind('bone'), vel=0.86, legato=0.97, human=0.012)
        play_line(S, 'fl', [(p_, d, m - 12, f) for (p_, d, m, f) in notes], P, 0, wind('hun'), vel=0.6, legato=0.97, human=0.014)
    return S


ERAS = {
    1: dict(key='era1_stone_fire', title='돌과 불', fn=era1),
    2: dict(key='era2_asadal', title='아사달', fn=era2),
    3: dict(key='era3_hwarang', title='화랑', fn=era3),
    4: dict(key='era4_frontline', title='전선의 북소리', fn=era4),
    5: dict(key='era5_haengju', title='행주의 함성', fn=era5),
    6: dict(key='era6_march', title='광복 행진곡', fn=era6),
}


def marker():
    """디코더 지연 보정용 표지음: 2ms짜리 4kHz 삑(봉우리 = 0.02s). 게임은 이 구간을 재생하지 않는다."""
    n = L.nsamp(PRE)
    x = np.zeros(n)
    m = L.nsamp(0.002)
    c = L.nsamp(0.02)
    x[c - m // 2:c - m // 2 + m] = np.sin(L.TAU * 4000 * (np.arange(m) - m / 2) / SR + np.pi / 2) * np.hanning(m) * 0.9
    return x


def write_wav(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def band_report(x):
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    tot = X.sum() + 1e-12
    ed = [0, 150, 300, 600, 1200, 2400, 4800, 16000]
    return [int(round(100 * X[(f >= a) & (f < b)].sum() / tot)) for a, b in zip(ed[:-1], ed[1:])]


if __name__ == '__main__':
    args = sys.argv[1:]
    out = args[0]
    wavdir = None
    sheet = None
    mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bgm_meta.json')
    eras = []
    i = 1
    while i < len(args):
        if args[i] == '--wav':
            wavdir = args[i + 1]
            i += 2
        elif args[i] == '--sheet':
            sheet = args[i + 1]
            i += 2
        elif args[i] == '--meta':
            mp = args[i + 1]
            i += 2
        else:
            eras.append(int(args[i]))
            i += 1
    eras = eras or sorted(ERAS)
    os.makedirs(out, exist_ok=True)
    if wavdir:
        os.makedirs(wavdir, exist_ok=True)
    ir = L.reverb_ir(np.random.default_rng(77), rt=1.5)
    meta = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else {}
    sheets = []
    for e in eras:
        E = ERAS[e]
        parts = []
        lens = []
        for sec in ('A', 'B'):
            S = E['fn'](sec)
            x, info = S.mix(ir)
            parts.append(x)
            lens.append(S.body)
            print(f"era{e} {sec}: body {S.body:.3f}s  stems(rms) " + ' '.join(f'{k}={v:.3f}' for k, v in info.items()))
        pa, pb = master(parts)
        full = np.concatenate([marker(), pa, np.zeros(L.nsamp(GAP)), pb])
        a0 = 0.1
        b0 = a0 + lens[0] + TAIL + GAP
        wavp = os.path.join(wavdir or out, E['key'] + '.wav')
        write_wav(wavp, full)
        mp3 = os.path.join(out, E['key'] + '.mp3')
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wavp, '-ac', '1', '-ar', str(SR), '-c:a', 'libmp3lame', '-b:a', '72k', mp3], check=True)
        if not wavdir:
            os.remove(wavp)
        meta[E['key']] = dict(era=e, title=E['title'], a=[round(a0, 4), round(lens[0], 4)], b=[round(b0, 4), round(lens[1], 4)], tail=TAIL, dur=round(len(full) / SR, 2), bytes=os.path.getsize(mp3))
        for nm, p in (('A', pa), ('B', pb)):
            print(f"  {nm}: rms {np.sqrt(np.mean(p ** 2)):.3f} peak {np.max(np.abs(p)):.2f} bands[~150,~300,~600,~1.2k,~2.4k,~4.8k,4.8k~] {band_report(p)}")
        print(f"  → {mp3} {os.path.getsize(mp3) / 1024:.0f}KB  A {lens[0]:.2f}s  B {lens[1]:.2f}s")
        sheets.append((E['key'], full))
    meta = dict(sorted(meta.items(), key=lambda kv: kv[1]['era']))
    json.dump(meta, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if sheet:
        from PIL import Image, ImageDraw
        W, H = 1400, 150
        im = Image.new('RGB', (W, (H + 18) * len(sheets)), (12, 14, 20))
        dr = ImageDraw.Draw(im)
        for i, (k, x) in enumerate(sheets):
            f, t, Sx = signal.spectrogram(x, SR, nperseg=1024, noverlap=512)
            Sx = 10 * np.log10(Sx[:260] + 1e-10)
            Sx = np.clip((Sx - Sx.max() + 70) / 70, 0, 1)[::-1]
            g = Image.fromarray((Sx * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
            rgb = Image.merge('RGB', (g.point(lambda v: min(255, int(v * 1.6))), g.point(lambda v: int(v * 0.85)), g.point(lambda v: int(60 + v * 0.3))))
            im.paste(rgb, (0, i * (H + 18) + 18))
            dr.text((4, i * (H + 18) + 3), f'{k}  {len(x) / SR:.1f}s  (0~8kHz)', fill=(255, 230, 120))
        im.save(sheet)
