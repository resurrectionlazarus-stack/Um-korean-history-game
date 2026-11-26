#!/usr/bin/env python3
"""R30 배포 묶음 — SHA256SUMS.txt · 전체 배포본(dist/shinsi-R30-deploy.zip) · 나눔 2개(4~6시대 원화 = part2, 나머지 = part1)."""
import hashlib
import os
import re
import zipfile

ROOT = "shinsi-R30"
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


p2 = [r for r in allrel if re.match(r"era[456]_", r.split("/")[-1])]
p1 = [r for r in allrel if r not in set(p2)]
print("sums", len(files))
build("shinsi-R30-deploy.zip", allrel, True)
build("shinsi-R30-part1-code-era123.zip", p1, False)
build("shinsi-R30-part2-era456.zip", p2, False)
