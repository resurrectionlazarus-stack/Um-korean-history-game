#!/usr/bin/env python3
"""R37 — 효과음 원본 WAV 실측(선별 · 트림 기준을 숫자로 잡기 위한 도구).
사용: python -I tools/r37/analyze_wavs.py <WAV 폴더> [출력 JSON]
파일 이름 규칙: <prefix>_#<take>-<timestamp>.wav (음향감독 납품 형식)

파일마다 잰 것:
  dur      길이(초)
  peak     피크(dBFS)
  rms      RMS(dBFS · 앞뒤 무음을 뺀 구간)
  lead     앞 무음(ms): 피크 대비 -32dBFS 또는 절대값 0.025 가운데 큰 쪽을 처음 넘는 지점
  tail     뒤 무음(ms): 마지막으로 -42dBFS(절대)를 넘은 지점 뒤에 남은 길이
  atk      어택(ms): 돌파 지점 → 피크까지
  cent     스펙트럼 중심(Hz · 무음 뺀 구간)
  mid      300~2400Hz 에너지 비율(휴대폰 스피커가 잘 내는 몸통 · R35 기준 45% 이상 권장)
  lo       150Hz 아래 에너지 비율
  corr     좌우 상관(1 = 모노와 같음 · 낮을수록 넓은 스테레오)
  dense    0.5초 RMS 창이 가장 센 시각(초) — 긴 파일의 하이라이트 자리
"""
import json
import os
import re
import sys

import numpy as np
from scipy.io import wavfile

LEAD_REL_DB = -32.0
LEAD_ABS = 0.025
TAIL_DB = -42.0


def db(x):
    return 20 * np.log10(max(x, 1e-9))


def analyze(path):
    sr, d = wavfile.read(path)
    if d.ndim == 1:
        d = d[:, None]
    x = d.astype(np.float64) / 32768.0
    n, ch = x.shape
    amax = np.max(np.abs(x), axis=1)
    peak = float(amax.max())
    pi = int(amax.argmax())
    thr = max(peak * 10 ** (LEAD_REL_DB / 20), LEAD_ABS)
    above = np.nonzero(amax > thr)[0]
    lead_i = int(above[0]) if len(above) else 0
    tail_thr = 10 ** (TAIL_DB / 20)
    above2 = np.nonzero(amax > tail_thr)[0]
    last_i = int(above2[-1]) if len(above2) else n - 1
    mono = x.mean(axis=1)
    seg = mono[lead_i:last_i + 1]
    rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    # 스펙트럼(무음 뺀 구간 · 최대 8초만)
    s2 = seg[: min(len(seg), sr * 8)]
    if len(s2) > 64:
        w = np.hanning(len(s2))
        spec = np.abs(np.fft.rfft(s2 * w)) ** 2
        f = np.fft.rfftfreq(len(s2), 1 / sr)
        tot = spec.sum() + 1e-18
        cent = float((spec * f).sum() / tot)
        mid = float(spec[(f >= 300) & (f < 2400)].sum() / tot)
        lo = float(spec[f < 150].sum() / tot)
    else:
        cent = mid = lo = 0.0
    if ch == 2:
        L, R = x[:, 0], x[:, 1]
        corr = float(np.corrcoef(L, R)[0, 1]) if L.std() > 0 and R.std() > 0 else 1.0
    else:
        corr = 1.0
    # 0.5초 RMS 창(50ms 걸음)
    win = int(sr * 0.5)
    hop = int(sr * 0.05)
    if n > win:
        e = mono ** 2
        cs = np.concatenate([[0.0], np.cumsum(e)])
        starts = np.arange(0, n - win, hop)
        wr = np.sqrt((cs[starts + win] - cs[starts]) / win)
        dense = float(starts[int(wr.argmax())] / sr)
        wr_db = [round(db(v), 1) for v in wr]
    else:
        dense = 0.0
        wr_db = []
    return {
        "dur": round(n / sr, 3), "sr": sr, "ch": ch,
        "peak": round(db(peak), 1), "rms": round(db(rms), 1),
        "lead": round(lead_i / sr * 1000, 1), "tail": round((n - 1 - last_i) / sr * 1000, 1),
        "atk": round(max(0, pi - lead_i) / sr * 1000, 1),
        "cent": round(cent), "mid": round(mid, 3), "lo": round(lo, 3), "corr": round(corr, 3),
        "dense": round(dense, 2), "win_db": wr_db,
    }


def main():
    folder = sys.argv[1]
    out_json = sys.argv[2] if len(sys.argv) > 2 else None
    rows = {}
    for fn in sorted(os.listdir(folder)):
        m = re.match(r"^(.+?)_#(\d+)-\d+\.wav$", fn)
        if not m:
            continue
        r = analyze(os.path.join(folder, fn))
        r["file"] = fn
        rows.setdefault(m.group(1), {})[int(m.group(2))] = r
    print(f"{sum(len(v) for v in rows.values())} files · {len(rows)} prefixes")
    print(f"{'prefix':22s} {'#':>2s} {'dur':>6s} {'peak':>6s} {'rms':>6s} {'lead':>7s} {'tail':>7s} {'atk':>6s} {'cent':>5s} {'mid':>5s} {'lo':>5s} {'corr':>5s} {'dense':>5s}")
    for prefix in rows:
        for take in sorted(rows[prefix]):
            r = rows[prefix][take]
            print(f"{prefix:22s} {take:2d} {r['dur']:6.2f} {r['peak']:6.1f} {r['rms']:6.1f} {r['lead']:7.1f} {r['tail']:7.1f} {r['atk']:6.1f} {r['cent']:5d} {r['mid']:5.2f} {r['lo']:5.2f} {r['corr']:5.2f} {r['dense']:5.2f}")
    if out_json:
        json.dump(rows, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("wrote", out_json)


if __name__ == "__main__":
    main()
