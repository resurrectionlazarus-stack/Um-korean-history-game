#!/usr/bin/env python3
"""R37 배포 묶음 — SHA256SUMS.txt · 전체 배포본(dist/shinsi-R37-deploy.zip) · 나눔 3개(각 30MB 미만) ·
바뀐 것만(dist/shinsi-R37-changed-code-sfx.zip — R36.5-2 배포 폴더 위에 덮어쓰면 R37이 된다: index.html · 목록 · 새 효과음 64 + 표 · 안내문 · 점검 페이지) ·
새 방 인수인계 묶음(dist/shinsi-handover-R37.zip) · 저장소 반영 묶음(dist/shinsi-R37-repo-delta.zip — git이 없는 PC에서 만든 결과를 클라우드 세션이 커밋할 때 푸는 것).
저장소 루트에서 실행: python -I tools/r37/pack37.py [handover | delta]"""
import hashlib
import os
import re
import sys
import zipfile

ROOT = "shinsi-R37"
LIMIT = 30 * 1000 * 1000
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
DOCS = ["NEXT-SESSION.md", "HANDOVER.md", "ROADMAP.md", "R37-handoff.md", "R36.5-2-handoff.md", "R36.5-handoff.md", "R36-handoff.md", "R36-art-request.md"]
SHOTS = "R37-screenshots"


def zwrite(z, path, arc):
    z.write(path, arc)


def handover():
    out = os.path.join("dist", "shinsi-handover-R37.zip")
    shots = sorted(os.listdir(SHOTS)) if os.path.isdir(SHOTS) else []
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in DOCS:
            zwrite(z, f, f)
        for f in shots:
            zwrite(z, os.path.join(SHOTS, f), SHOTS + "/" + f)
    open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sha(out)}  {os.path.basename(out)}\n")
    print(os.path.basename(out), os.path.getsize(out), len(DOCS) + len(shots))


CHANGED = ["index.html", "assets/MANIFEST.json", "assets/sfx/sfx_manifest.json", "README-배포.txt", "R37-handoff.md", "sound-check.html"]


def changed_list():
    return CHANGED + sorted("assets/sfx/" + f for f in os.listdir(os.path.join(ROOT, "assets", "sfx")) if re.match(r"^sfx_.*\.mp3$", f))


def delta():
    """저장소 반영 묶음: tools/r37(원본 WAV 제외) · 문서 · .gitignore · 비교 이미지 · 바뀐 빌드 파일(shinsi-R37/ 아래 — 나머지는 shinsi-R36.5-2를 복사) · 적용 안내."""
    out = os.path.join("dist", "shinsi-R37-repo-delta.zip")
    n = 0
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for d, _, fs in os.walk("tools/r37"):
            for f in fs:
                if f.endswith(".wav") or f.endswith(".zip") or "src_wav" in d:
                    continue
                p = os.path.join(d, f).replace(os.sep, "/")
                zwrite(z, p, p)
                n += 1
        for f in DOCS[:4] + [".gitignore"]:
            zwrite(z, f, f)
            n += 1
        if os.path.isdir(SHOTS):
            for f in sorted(os.listdir(SHOTS)):
                zwrite(z, os.path.join(SHOTS, f), SHOTS + "/" + f)
                n += 1
        for rel in changed_list():
            zwrite(z, os.path.join(ROOT, rel), ROOT + "/" + rel)
            n += 1
        z.writestr("APPLY-ON-CLOUD.md", APPLY)
    open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sha(out)}  {os.path.basename(out)}\n")
    print(os.path.basename(out), os.path.getsize(out), n + 1)


APPLY = """# R37 저장소 반영 — 클라우드(git 있는) 세션에서

이 묶음은 git이 없는 PC에서 만든 R37 결과물입니다. 작업 브랜치 claude/r23-attack-walk-visibility-mob-ocesrz 의 최신 커밋(f038c6a 이후)에서:

    git fetch origin claude/r23-attack-walk-visibility-mob-ocesrz && git checkout claude/r23-attack-walk-visibility-mob-ocesrz && git pull
    cp -r shinsi-R36.5-2 shinsi-R37                    # 바뀌지 않은 원화 · 효과음 WAV · 음악은 R36.5-2와 같다
    rm shinsi-R37/R36.5-2-handoff.md shinsi-R37/SHA256SUMS.txt
    unzip -o shinsi-R37-repo-delta.zip                 # tools/r37 · 문서 · .gitignore · R37-screenshots · shinsi-R37의 바뀐 파일(index.html · MANIFEST · 새 효과음 · 안내문)
    python3 -I tools/r37/check_build37.py shinsi-R37   # MANIFEST 520 · 디스크 520 · 문법 OK(node 있음)
    python3 -I tools/r37/pack37.py                     # SHA256SUMS · dist/shinsi-R37-deploy.zip(+.sha256) · 나눔 3 · 바뀐 것만 · 인수인계 묶음
    bash tools/r37/run_tests.sh                        # (선택) Playwright 기능 · 부하 — 이 PC에서는 못 돌려 봄(R37-handoff.md 6절)
    git add -A && git commit -m "R37: realistic SFX pipeline (64 MP3 from the sound director's recordings) + Web Audio engine" && git push origin claude/r23-attack-walk-visibility-mob-ocesrz

- 원본 WAV(신시 효과음.zip · 120.7MB)는 커밋하지 않습니다(.gitignore). 다시 굽고 싶으면 zip을 아무 데나 두고 `python3 -I tools/r37/build_sfx.py <zip> shinsi-R37`.
- dist/*part*.zip 은 gitignore(메신저용). deploy zip과 .sha256은 pack37.py가 그 자리에서 다시 만듭니다(이 PC에서 만든 zip과 시각만 다름).
"""

if len(sys.argv) > 1 and sys.argv[1] == "handover":
    handover()
    sys.exit(0)
if len(sys.argv) > 1 and sys.argv[1] == "delta":
    delta()
    sys.exit(0)
files = []
for d, _, fs in os.walk(ROOT):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
        if rel != "SHA256SUMS.txt":
            files.append(rel)
files.sort()
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
            zwrite(z, os.path.join(ROOT, rel), ROOT + "/" + rel)
    h = sha(out)
    open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{h}  {name}\n")
    size = os.path.getsize(out)
    print(name, size, len(rels), h[:12])
    return size


# 나눔: 공통(코드 · 효과음 · 음향 점검) + 1 · 5시대 / 2 · 4시대 / 3 · 6시대 — 새 효과음 64개(2.1MB · 이름에 시대 번호 없음)는 공통으로
era = lambda r: (re.match(r"era(\d)_", r.split("/")[-1]) or [None, None])[1]
p2 = [r for r in allrel if era(r) in ("2", "4")]
p3 = [r for r in allrel if era(r) in ("3", "6")]
p1 = [r for r in allrel if r not in set(p2) | set(p3)]
assert sorted(p1 + p2 + p3) == allrel
print("sums", len(files))
build("shinsi-R37-deploy.zip", allrel, True)
sizes = [build("shinsi-R37-part1-code-sfx-era15.zip", p1, False), build("shinsi-R37-part2-era24.zip", p2, False), build("shinsi-R37-part3-era36.zip", p3, False)]
assert all(s < LIMIT for s in sizes), sizes
print("parts < 30MB ok")

NOTE = """신시 R37 — 바뀐 것만 담은 묶음(코드 + 새 효과음)

무엇이 들었나
  index.html                      게임 전체(R37 새 효과음 엔진이 들어감)
  assets/MANIFEST.json            원화 · 효과음 목록(65항목 추가 → 520)
  assets/sfx/sfx_*.mp3 (64개)     음향감독 녹음에서 선별 · 다듬은 효과음
  assets/sfx/sfx_manifest.json    키 → 파일 표(엔진이 읽음)
  README-배포.txt · R37-handoff.md · sound-check.html   안내문 · 인수인계서 · 음향 점검 페이지

쓰는 법
  R36.5-2 배포 폴더(shinsi-R36.5-2) 위에 이 묶음을 풀어 덮어쓰면 R37과 똑같이 동작합니다(원화 · 예전 WAV · 음악은 그대로 쓰입니다).
  (체크섬 파일 SHA256SUMS.txt는 전체 배포본에만 들어 있습니다.)
"""
out = os.path.join("dist", "shinsi-R37-changed-code-sfx.zip")
ch = changed_list()
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.writestr("읽어주세요.txt", NOTE)
    for rel in ch:
        zwrite(z, os.path.join(ROOT, rel), rel)
open(out + ".sha256", "w", encoding="utf-8", newline="\n").write(f"{sha(out)}  {os.path.basename(out)}\n")
print(os.path.basename(out), os.path.getsize(out), len(ch) + 1)
handover()
delta()
