#!/usr/bin/env python3
"""R36 MANIFEST 병합 — 새 항목(둔기 '퍽' 4종 · 동물 울음 10종 · 함성 1종)만 추가. 옛 목록은 그대로.
사용: python3 -I tools/r36/manifest_r36.py shinsi-R36"""
import json
import os
import sys
import wave

root = sys.argv[1]
mp = os.path.join(root, "assets", "MANIFEST.json")
m = json.load(open(mp, encoding="utf-8"))
F = m["files"]
NEW = ["thud_hit_1", "thud_hit_2", "thud_heavy", "thud_crush", "wolf_howl", "wolf_snarl", "wolf_yelp", "hyena_cackle", "bear_roar", "bear_growl", "rhino_snort", "beast_groan", "tiger_roar", "tiger_snarl", "war_cry"]
added = []
for name in NEW:
    rel = f"assets/sfx/{name}.wav"
    p = os.path.join(root, rel)
    w = wave.open(p)
    e = {"sampleRate": w.getframerate(), "channels": w.getnchannels(), "bitDepth": w.getsampwidth() * 8, "durationSec": round(w.getnframes() / w.getframerate(), 2), "bytes": os.path.getsize(p), "kind": "sfx", "r36": "synth (tools/r36/synth_r36.py)"}
    if rel not in F:
        added.append(rel)
    F[rel] = e
m["r36"] = {"note": "R36 — 둔기 타격음 '퍽' 4종(thud_*) · 동물 울음 10종 · 병사 함성 1종 새 항목 추가(전부 직접 합성). 옛 목록은 그대로(R35의 rock_* 4종은 비교용으로 남김 — 게임에서는 받지 않음)", "addedSfx": len(NEW)}
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("added", len(added), "total", len(F))
