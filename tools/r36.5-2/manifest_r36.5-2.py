#!/usr/bin/env python3
"""R36.5-2 MANIFEST 병합 — 바뀐 항목(무기 그림 9장)만 bytes 갱신 + 표식. 옛 목록 · 옛 표식은 그대로.
사용: python3 -I tools/r36.5-2/manifest_r36.5-2.py shinsi-R36.5-2"""
import json
import os
import sys

root = sys.argv[1]
mp = os.path.join(root, "assets", "MANIFEST.json")
m = json.load(open(mp, encoding="utf-8"))
F = m["files"]
changed = []
for era in (1, 2, 4):
    for t in (1, 2, 3):
        rel = f"assets/weapon/era{era}_t{t}.png"
        b = os.path.getsize(os.path.join(root, rel))
        if F[rel].get("bytes") != b or "r36_5_2" not in F[rel]:
            changed.append(rel)
        F[rel]["bytes"] = b
        F[rel]["r36_5_2"] = ("hand replaced by the hero's own fist from the body art (run frame 1, same scale, rotated 90 degrees so the fingers wrap the grip); "
                             "old oversized hand removed and the grip rebuilt under it" + ("; shaft thinned to 14px at the grip" if era == 1 else "")
                             + " — tools/r36.5-2/natural_hand.py (source: shinsi-R36/assets/weapon + assets/hero/*_run.webp)")
m["r36_5_2"] = {"note": "R36.5-2 — 무기 그림 9장의 손을 몸 원화의 주먹(같은 크기 · 같은 붓 그림)으로 교체. 1시대는 자루도 손에 맞게 가늘게. 그림 크기 · 쥔 자리 그대로, bytes만 갱신. 새 항목 없음", "replaced": 9}
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("changed", len(changed), "total", len(F))
