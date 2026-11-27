#!/usr/bin/env python3
"""플레이 링크(아티팩트)를 올릴 때 쓰는 파일 묶음 목록 만들기.

한 번의 게시에는 파일 255개 · 64MB까지만 실을 수 있다. 게임은 약 457개 · 80MB라 두 번에 나눠 올린다.
  1차: 새 아티팩트로 게시 — file_path = <빌드>/index.html · root = <빌드> · files = A 묶음 · icon 지정
  2차: 같은 주소(url)에 다시 게시 — files = B 묶음(MANIFEST.json · thumb.jpg 포함). 앞서 올린 파일은 그대로 남는다.
그림만 바뀐 판도 새 링크로 올린다(같은 주소에 덮어쓰면 휴대폰이 옛 그림을 기억해 그대로 보여 줄 수 있다).

사용: python3 -I tools/r36.5-2/make_batches.py <빌드 폴더> [출력 json]
      → {"A": [{"path": ...}, ...], "B": [...]} (게시 도구의 files 인자에 그대로 넣는 꼴)"""
import json
import os
import sys

ROOT = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else None
SKIP = {"index.html", "README-배포.txt", "SHA256SUMS.txt", "sound-check.html"}   # index.html은 file_path로 따로 간다
MAXN, MAXB = 250, 60 * 1000 * 1000

files = []
for d, _, fs in os.walk(ROOT):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
        if rel in SKIP or rel.endswith("-handoff.md"):
            continue
        files.append((os.path.getsize(os.path.join(ROOT, rel)), rel))
files.sort(reverse=True)
bins = {"A": [], "B": []}
size = {"A": 0, "B": 0}
for b, rel in files:                       # 큰 파일부터, 지금 더 가벼운 묶음에
    k = min(size, key=size.get)
    bins[k].append(rel)
    size[k] += b
for k in bins:
    bins[k].sort()
    assert len(bins[k]) <= MAXN and size[k] <= MAXB, (k, len(bins[k]), size[k])
    print(k, len(bins[k]), "files", size[k], "bytes")
res = {k: [{"path": p} for p in v] for k, v in bins.items()}
if OUT:
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("→", OUT)
