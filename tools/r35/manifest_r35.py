#!/usr/bin/env python3
"""R35 MANIFEST 병합 — 새 항목(합성 타격음 · 시대 배경음악)만 추가 · 바뀐 항목(1시대 무기 3장)의 bytes만 갱신. 옛 목록은 그대로.
사용: python3 -I tools/r35/manifest_r35.py shinsi-R35"""
import json
import os
import sys
import wave

root = sys.argv[1]
mp = os.path.join(root, "assets", "MANIFEST.json")
m = json.load(open(mp, encoding="utf-8"))
F = m["files"]
added, changed = [], []
HITS = ["cut_light_1", "cut_light_2", "cut_light_3", "cut_heavy", "cut_sever", "cut_armor", "cut_flurry", "rock_hit_1", "rock_hit_2", "rock_heavy", "rock_crush", "stab_1", "stab_2", "whoosh_blade", "whoosh_heavy"]
for name in HITS:
    rel = f"assets/sfx/{name}.wav"
    p = os.path.join(root, rel)
    w = wave.open(p)
    e = {"sampleRate": w.getframerate(), "channels": w.getnchannels(), "bitDepth": w.getsampwidth() * 8, "durationSec": round(w.getnframes() / w.getframerate(), 2), "bytes": os.path.getsize(p), "kind": "sfx", "r35": "synth (tools/r35/synth_hits.py)"}
    if rel not in F:
        added.append(rel)
    F[rel] = e
bdir = os.path.join(root, "assets", "bgm")
meta = {}
mj = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bgm_meta.json")
if os.path.exists(mj):
    meta = json.load(open(mj, encoding="utf-8"))
for fn in sorted(os.listdir(bdir)) if os.path.isdir(bdir) else []:
    if not fn.endswith(".mp3"):
        continue
    rel = f"assets/bgm/{fn}"
    p = os.path.join(root, rel)
    e = {"format": "mp3_32000hz_mono", "bytes": os.path.getsize(p), "kind": "bgm", "loop": "scheduled (sections in index.html R35_BGM)", "r35": "synth (tools/r35/bgm_render.py)"}
    k = fn[:-4]
    if k in meta:
        e["durationSec"] = meta[k].get("dur")
        e["title"] = meta[k].get("title")
    if rel not in F:
        added.append(rel)
    F[rel] = e
for t in (1, 2, 3):
    rel = f"assets/weapon/era1_t{t}.png"
    b = os.path.getsize(os.path.join(root, rel))
    if F[rel].get("bytes") != b or "r35" not in F[rel]:
        changed.append(rel)
    F[rel]["bytes"] = b
    F[rel]["r35"] = "unified fist (t1 fist on all tiers, forearm stub removed) — tools/r35/unify_fist.py · originals in tools/r35/era1_weapon_orig"
m.pop("r35ChangedFileCount", None)
nb = len([k for k in F if k.startswith("assets/bgm/")])
m["r35"] = {"note": "R35 — 합성 타격음 15종 · 시대 배경음악(mp3) 새 항목 추가 · 1시대 무기 3장 손 통일(그림 크기 · 쥔 자리 그대로, bytes만 갱신). 옛 목록은 그대로(예전 타격음 8종은 비교용으로 남김 — 게임에서는 받지 않음)", "addedSfx": len(HITS), "addedBgm": nb, "replaced": 3}
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("added", len(added), "changed", len(changed), "total", len(F))
