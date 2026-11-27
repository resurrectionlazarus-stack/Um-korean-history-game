#!/usr/bin/env python3
"""R36.5-2 배포 묶음 — SHA256SUMS.txt · 전체 배포본(dist/shinsi-R36.5-2-deploy.zip) ·
나눔 3개(공통 + 1 · 5시대 / 2 · 4시대 / 3 · 6시대 — 각 30MB 미만) ·
바뀐 그림만(dist/shinsi-R36.5-2-changed-sprites.zip — R36.5 배포 폴더 위에 덮어쓰면 R36.5-2가 된다) ·
새 방 인수인계 묶음(dist/shinsi-handover-R36.5-2.zip). 저장소 루트에서 실행.
인자 handover를 주면 인수인계 묶음만 다시 만든다(문서만 고쳤을 때 — 전체 배포본의 체크섬을 건드리지 않게)."""
import hashlib
import os
import re
import sys
import zipfile

ROOT = "shinsi-R36.5-2"
LIMIT = 30 * 1000 * 1000
files = []
for d, _, fs in os.walk(ROOT):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
        if rel != "SHA256SUMS.txt":
            files.append(rel)
files.sort()
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def handover():
    """새 방 인수인계 묶음: 문서 + 비교 이미지(저장소에도 같은 파일이 있다)."""
    docs = ["NEXT-SESSION.md", "HANDOVER.md", "ROADMAP.md", "R36.5-2-handoff.md", "R36.5-handoff.md", "R36-handoff.md", "R36-art-request.md"]
    out = os.path.join("dist", "shinsi-handover-R36.5-2.zip")
    shots = sorted(os.listdir("R36.5-2-screenshots"))
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in docs:
            z.write(f, f)
        for f in shots:
            z.write(os.path.join("R36.5-2-screenshots", f), "R36.5-2-screenshots/" + f)
    open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sha(out)}  {os.path.basename(out)}\n")
    print(os.path.basename(out), os.path.getsize(out), len(docs) + len(shots))


if len(sys.argv) > 1 and sys.argv[1] == "handover":   # 문서만 고친 뒤: python3 -I tools/r36.5-2/pack36.5-2.py handover
    handover()
    sys.exit(0)
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


# [R34] 총 약 75MB — 4시대가 18MB로 커져 시대 크기가 고르게 짝지음: 공통 + 1 · 5시대 / 2 · 4시대 / 3 · 6시대
# [R35] 시대 배경음악 mp3(assets/bgm/era{N}_*.mp3 · 곡마다 약 0.45MB)도 파일 이름의 시대 번호를 따라 같은 묶음으로 간다 → 총 약 78MB
era = lambda r: (re.match(r"era(\d)_", r.split("/")[-1]) or [None, None])[1]
p2 = [r for r in allrel if era(r) in ("2", "4")]
p3 = [r for r in allrel if era(r) in ("3", "6")]
p1 = [r for r in allrel if r not in set(p2) | set(p3)]
assert sorted(p1 + p2 + p3) == allrel
print("sums", len(files))
build("shinsi-R36.5-2-deploy.zip", allrel, True)
sizes = [build("shinsi-R36.5-2-part1-code-era15.zip", p1, False), build("shinsi-R36.5-2-part2-era24.zip", p2, False), build("shinsi-R36.5-2-part3-era36.zip", p3, False)]
assert all(s < LIMIT for s in sizes), sizes
print("parts < 30MB ok")

# 바뀐 그림만: 무기 9장 + 목록 + 안내문(배포 폴더에 덮어쓰는 경로 그대로) + 비교 이미지
changed = [f"assets/weapon/era{e}_t{t}.png" for e in (1, 2, 4) for t in (1, 2, 3)] + ["assets/MANIFEST.json", "README-배포.txt", "R36.5-2-handoff.md"]
NOTE = """신시 R36.5-2 — 바뀐 그림만 담은 묶음

무엇이 들었나
  assets/weapon/era1_t1~t3.png · era2_t1~t3.png · era4_t1~t3.png   무기 그림 9장(손을 몸 원화의 주먹과 같은 크기로)
  assets/MANIFEST.json                                             원화 목록(9항목의 파일 크기만 바뀜)
  README-배포.txt · R36.5-2-handoff.md                              안내문 · 인수인계서
  비교이미지/                                                       R36.5 ↔ R36.5-2 비교 4장

쓰는 법
  R36.5 배포 폴더(shinsi-R36.5) 위에 이 묶음을 풀어 덮어쓰면 R36.5-2와 똑같이 동작합니다.
  게임 코드(index.html)는 R36 · R36.5 · R36.5-2가 같아서 그림과 목록만 바꾸면 됩니다.
  (체크섬 파일 SHA256SUMS.txt는 전체 배포본에만 들어 있습니다.)
"""
out = os.path.join("dist", "shinsi-R36.5-2-changed-sprites.zip")
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("읽어주세요.txt", NOTE)
    for rel in changed:
        z.write(os.path.join(ROOT, rel), rel)
    for f in sorted(os.listdir("R36.5-2-screenshots")):
        z.write(os.path.join("R36.5-2-screenshots", f), "비교이미지/" + f)
open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sha(out)}  {os.path.basename(out)}\n")
print(os.path.basename(out), os.path.getsize(out), len(changed) + 1 + len(os.listdir("R36.5-2-screenshots")))

handover()
