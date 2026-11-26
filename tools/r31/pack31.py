#!/usr/bin/env python3
"""R31 배포 묶음 — SHA256SUMS.txt · 전체 배포본(dist/shinsi-R31-deploy.zip) · 나눔 3개(공통 + 1 · 2시대 / 3 · 4시대 / 5 · 6시대 — 각 30MB 미만)."""
import hashlib
import os
import re
import zipfile

ROOT = "shinsi-R31"
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
    print(name, os.path.getsize(out), len(rels), h[:12])


# [R31] 총 66.5MB라 30MB 미만 2개로는 담을 수 없음(최대 60MB) → 시대별 3개(각 약 22MB): 공통 + 1 · 2시대 / 3 · 4시대 / 5 · 6시대
p2 = [r for r in allrel if re.match(r"era[34]_", r.split("/")[-1])]
p3 = [r for r in allrel if re.match(r"era[56]_", r.split("/")[-1])]
p1 = [r for r in allrel if r not in set(p2) | set(p3)]
print("sums", len(files))
build("shinsi-R31-deploy.zip", allrel, True)
build("shinsi-R31-part1-code-era12.zip", p1, False)
build("shinsi-R31-part2-era34.zip", p2, False)
build("shinsi-R31-part3-era56.zip", p3, False)
