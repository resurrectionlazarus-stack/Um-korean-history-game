#!/usr/bin/env python3
"""R37 MANIFEST 병합 — 새 항목(assets/sfx/sfx_*.mp3 64개 + sfx_manifest.json)만 더한다. 옛 항목 · 옛 표식은 그대로.
사용: python -I tools/r37/manifest_r37.py shinsi-R37
규칙: 항목 수 = 디스크 파일 수(check_build.py로 확인) · 한 이름에 한 형식."""
import json
import os
import re
import sys

root = sys.argv[1]
mp = os.path.join(root, "assets", "MANIFEST.json")
m = json.load(open(mp, encoding="utf-8"))
F = m["files"]
sfx_dir = os.path.join(root, "assets", "sfx")
sm = json.load(open(os.path.join(sfx_dir, "sfx_manifest.json"), encoding="utf-8"))
added, updated = [], []
for fn in sorted(os.listdir(sfx_dir)):
    if not (re.match(r"^sfx_.*\.mp3$", fn) or fn == "sfx_manifest.json"):
        continue
    rel = f"assets/sfx/{fn}"
    b = os.path.getsize(os.path.join(sfx_dir, fn))
    if rel in F:
        if F[rel].get("bytes") != b:
            updated.append(rel)
    else:
        added.append(rel)
    info = sm["files"].get(fn)
    e = F.setdefault(rel, {})
    e["bytes"] = b
    if fn == "sfx_manifest.json":
        e["kind"] = "meta"
        e["r37"] = "key → file table for the R37 realistic SFX engine (createR37Sfx reads it at first input)"
    else:
        e["kind"] = "sfx"
        e["format"] = "mp3 44.1kHz " + ("stereo" if info["stereo"] else "mono") + f" {info['kbps']}kbps"
        e["dur"] = info["dur"]
        e["r37"] = f"from {info['src']} (sound director's take) via tools/r37/build_sfx.py — trimmed/normalized/EQ'd"
m["r37"] = {"note": "R37 — 음향감독 발주서: 실제 녹음 효과음 104개 가운데 선별 · 트림 · 정규화 · EQ · MP3 변환한 64개 + 키 표(sfx_manifest.json). "
                    "원본 WAV(120.7MB)는 저장소에 넣지 않음(.gitignore). 기존 WAV 57개는 그대로(새 소리를 못 받을 때의 폴백).",
            "added": len([k for k in F if "r37" in F[k]]), "updated_this_run": len(updated), "mp3": len([k for k in F if k.startswith("assets/sfx/sfx_") and k.endswith(".mp3")])}
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("added", len(added), "updated", len(updated), "total", len(F))
