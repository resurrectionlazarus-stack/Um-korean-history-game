#!/usr/bin/env python3
"""R37 비교 이미지 — ① 예전 합성 소리(R35 · R36 WAV) ↔ 새 녹음(R37 · 전처리 결과)의 파형 · 스펙트로그램 6쌍
② 심리스 루프의 이음매(말발굽 · 후두 구호): 루프 끝 0.3초 → 루프 시작 0.3초를 이어 붙인 파형(끊김 · 튐이 없어야 함)
사용: python -I tools/r37/compose37.py <WAV 원본 폴더 또는 zip> <빌드 폴더> <출력 폴더>
(전처리 결과는 build_sfx.process()를 다시 돌려 얻는다 — MP3를 Python에서 디코딩할 도구가 이 PC에 없어서)"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_sfx as B  # noqa: E402

SRC = B.gather(sys.argv[1])
BUILD = sys.argv[2]
OUT = sys.argv[3]
os.makedirs(OUT, exist_ok=True)
for name in ("Malgun Gothic", "NanumGothic", "Apple SD Gothic Neo", "Noto Sans CJK KR", "WenQuanYi Zen Hei"):
    if any(f.name == name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = name
        break
plt.rcParams["axes.unicode_minus"] = False
SPEC = {k["key"]: k for k in B.K}


def new_audio(key):
    y, info = B.process(SPEC[key], SRC)
    return y.mean(axis=1), B.SR_OUT, info


def old_audio(name):
    sr, d = wavfile.read(os.path.join(BUILD, "assets", "sfx", name + ".wav"))
    x = d.astype(np.float64) / 32768.0
    if x.ndim == 2:
        x = x.mean(axis=1)
    return x, sr


def db(v):
    return 20 * np.log10(max(v, 1e-9))


def panel(ax, x, sr, title):
    f, t, S = signal.spectrogram(x, sr, nperseg=1024, noverlap=768, scaling="spectrum")
    Sdb = 10 * np.log10(np.maximum(S, 1e-12))
    ax.pcolormesh(t, f / 1000, Sdb, shading="auto", cmap="magma", vmin=Sdb.max() - 70, vmax=Sdb.max())
    ax.set_ylim(0, 8)
    ax.set_ylabel("kHz", fontsize=8)
    rms = db(float(np.sqrt(np.mean(x ** 2))))
    peak = db(float(np.max(np.abs(x))))
    ax.set_title(f"{title} — {len(x) / sr:.2f}초 · RMS {rms:.1f} · 피크 {peak:.1f} dBFS", fontsize=9)
    ax.tick_params(labelsize=7)


PAIRS = [("돌도끼 평타", "thud_hit_1", "sfx_stone_axe_hit_01"), ("칼 베기", "cut_light_1", "sfx_sword_slash_01"), ("동굴 곰 포효", "bear_roar", "sfx_bear_roar_01"),
         ("산군(호랑이) 포효", "tiger_roar", "sfx_tiger_roar_01"), ("병사 함성", "war_cry", "sfx_army_warcry_01"), ("범종 → 에밀레종", "buddha_temple_bell", "sfx_buddha_emille_bell")]
fig, axes = plt.subplots(len(PAIRS), 2, figsize=(13, 2.3 * len(PAIRS)))
for i, (label, old, new) in enumerate(PAIRS):
    xo, so = old_audio(old)
    xn, sn, info = new_audio(new)
    panel(axes[i][0], xo, so, f"예전 합성 · {old}.wav")
    panel(axes[i][1], xn, sn, f"R37 녹음 · {new}.mp3 ({info['src']})")
    axes[i][0].text(-0.12, 0.5, label, transform=axes[i][0].transAxes, rotation=90, va="center", ha="center", fontsize=10, fontweight="bold")
fig.suptitle("R37 — 예전 합성 소리 ↔ 새 녹음(전처리 뒤) 스펙트로그램 · 0~8kHz · 밝을수록 셈", fontsize=12)
fig.tight_layout(rect=(0.02, 0, 1, 0.97))
p1 = os.path.join(OUT, "R37-spectrograms.jpg")
fig.savefig(p1, dpi=110, pil_kwargs={"quality": 88})
plt.close(fig)

# ② 루프 이음매
LOOPS = [("말발굽 루프(4.0초 · 0.45초 크로스페이드)", "sfx_cavalry_hooves_loop"), ("후두 구호 루프(4.5초 · 0.45초 크로스페이드)", "sfx_nomad_chant_loop")]
fig, axes = plt.subplots(len(LOOPS), 1, figsize=(13, 3.2 * len(LOOPS)))
for ax, (label, key) in zip(axes, LOOPS):
    x, sr, info = new_audio(key)
    ls, le = info["loop"]
    n = int(0.3 * sr)
    a = x[int(le * sr) - n: int(le * sr)]
    b = x[int(ls * sr): int(ls * sr) + n]
    y = np.concatenate([a, b])
    t = np.arange(len(y)) / sr - 0.3
    ax.plot(t, y, lw=0.4, color="#2b6cb0")
    env = np.sqrt(np.convolve(y ** 2, np.ones(int(sr * 0.005)) / int(sr * 0.005), mode="same"))
    ax.plot(t, env, lw=1.2, color="#d97706", label="5ms RMS 엔벨로프")
    ax.plot(t, -env, lw=1.2, color="#d97706")
    ax.axvline(0, color="#dc2626", lw=1.5, ls="--", label="이음매(loopEnd → loopStart)")
    ax.set_xlim(-0.3, 0.3)
    ax.set_xlabel("이음매 기준 초", fontsize=8)
    ax.set_title(f"{label} — {key}.mp3 · 루프 지점 {ls:.2f}~{le:.2f}초 · 파일 {info['after_s']:.2f}초", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.tick_params(labelsize=7)
fig.suptitle("R37 — 심리스 루프의 이음매: 루프 끝 0.3초 → 루프 시작 0.3초를 이어 붙인 파형(튐 · 끊김이 없어야 함)", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.95))
p2 = os.path.join(OUT, "R37-loop-seams.jpg")
fig.savefig(p2, dpi=110, pil_kwargs={"quality": 88})
plt.close(fig)
print("wrote", p1, p2)
