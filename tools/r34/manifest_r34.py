#!/usr/bin/env python3
"""R34 MANIFEST 병합 — 새 항목(합성 효과음 7) 추가 · 바뀐 항목(척준경 색 보정 12)의 bytes만 갱신. 옛 목록은 그대로.
사용: python3 -I tools/r34/manifest_r34.py shinsi-R34"""
import json
import os
import sys
import wave

root = sys.argv[1]
mp = os.path.join(root, "assets", "MANIFEST.json")
m = json.load(open(mp, encoding="utf-8"))
F = m["files"]
added, changed = [], []
SFX = {"amb_rain_loop": "ambience", "amb_blizzard_loop": "ambience", "amb_wind_loop": "ambience", "amb_fire_loop": "ambience", "thunder_crack_1": "sfx", "thunder_roll_2": "sfx", "war_horn_call": "sfx"}
for name, kind in SFX.items():
    rel = f"assets/sfx/{name}.wav"
    p = os.path.join(root, rel)
    w = wave.open(p)
    e = {"sampleRate": w.getframerate(), "channels": w.getnchannels(), "bitDepth": w.getsampwidth() * 8, "durationSec": round(w.getnframes() / w.getframerate(), 2), "bytes": os.path.getsize(p), "kind": kind, "r34": "synth (tools/r34/synth_audio.py)"}
    if kind == "ambience":
        e["loop"] = True
    if rel not in F:
        added.append(rel)
    F[rel] = e
for n in ["run", "run2", "run3", "run4", "run5", "run6", "run7", "run8", "cleave_prep", "cleave_hit", "charge", "dragon_stance"]:
    rel = f"assets/hero/era4_hero_{n}.webp"
    b = os.path.getsize(os.path.join(root, rel))
    if F[rel].get("bytes") != b or "r34" not in F[rel]:
        F[rel]["bytes"] = b
        F[rel]["r34"] = "color regrade to the black-iron palette (tools/r34/cjg_regrade.py · originals in tools/r34/cjg_r32_orig)"
        changed.append(rel)
m["r34"] = {"note": "R34 — 합성 효과음 7종(환경음 루프 4 · 천둥 2 · 뿔나팔) 새 항목 추가 · 척준경 R32 원화 12장 색 보정(그림 · 투명 영역 그대로, bytes만 갱신). 옛 목록은 그대로", "added": 7, "replaced": 12}
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("added", len(added), "changed", len(changed), "total", len(F))
