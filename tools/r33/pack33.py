#!/usr/bin/env python3
"""R33 배포 묶음 — SHA256SUMS.txt · 전체 배포본(dist/shinsi-R33-deploy.zip) ·
나눔 3개(공통 + 1 · 5시대 / 2 · 4시대 / 3 · 6시대 — 각 30MB 미만). 저장소 루트에서 실행."""
import hashlib
import os
import re
import zipfile

ROOT = "shinsi-R33"
LIMIT = 30 * 1000 * 1000
files = []
for d, _, fs in os.walk(ROOT):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
        if rel != "SHA256SUMS.txt":
            files.append(rel)
files.sort()
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
with open(os.path.join(ROOT, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as fh:
    for rel in files:
        fh.write(f"{sha(os.path.join(ROOT, rel))}  {rel}\n")
allrel = sorted(files + ["SHA256SUMS.txt"])
os.makedirs("dist", exist_ok=True)


def build(name, rels, folder_entry):
    out = os.path.join("dist", name)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        if folder_entry:
            z.writestr(zipfile.ZipInfo(ROOT + "/"), "")
        for rel in rels:
            z.write(os.path.join(ROOT, rel), ROOT + "/" + rel)
    h = sha(out)
    open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{h}  {name}\n")
    size = os.path.getsize(out)
    print(name, size, len(rels), h[:12])
    return size


# [R33] 총 약 75MB — 4시대가 18MB로 커져 시대 크기가 고르게 짝지음: 공통 + 1 · 5시대 / 2 · 4시대 / 3 · 6시대
era = lambda r: (re.match(r"era(\d)_", r.split("/")[-1]) or [None, None])[1]
p2 = [r for r in allrel if era(r) in ("2", "4")]
p3 = [r for r in allrel if era(r) in ("3", "6")]
p1 = [r for r in allrel if r not in set(p2) | set(p3)]
assert sorted(p1 + p2 + p3) == allrel
print("sums", len(files))
build("shinsi-R33-deploy.zip", allrel, True)
sizes = [build("shinsi-R33-part1-code-era15.zip", p1, False), build("shinsi-R33-part2-era24.zip", p2, False), build("shinsi-R33-part3-era36.zip", p3, False)]
assert all(s < LIMIT for s in sizes), sizes
print("parts < 30MB ok")
