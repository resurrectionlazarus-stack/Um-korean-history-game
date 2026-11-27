#!/usr/bin/env python3
"""R36.5 MANIFEST 병합 — 바뀐 항목(무기 그림 9장의 손)만 bytes 갱신 + 표식. 옛 목록은 그대로.
사용: python3 -I tools/r36.5/manifest_r36.5.py shinsi-R36.5"""
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
        if F[rel].get("bytes") != b or "r36_5" not in F[rel]:
            changed.append(rel)
        F[rel]["bytes"] = b
        F[rel]["r36_5"] = "hand redrawn as a left hand seen from the palm side: old thumb stub removed, thumb laid across the front" + (", nails added" if era == 1 else "") + " — tools/r36.5/redraw_hand.py (source: shinsi-R36/assets/weapon)"
m["r36_5"] = {"note": "R36.5 — 무기 그림 9장의 손을 손바닥 쪽에서 본 왼손으로(엄지가 앞을 가로지름 · 1시대는 손톱). 그림 크기 · 쥔 자리 그대로, bytes만 갱신. 새 항목 없음", "replaced": 9}
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("changed", len(changed), "total", len(F))
