#!/usr/bin/env python3
"""빌드 폴더 점검(R33 check_build.py와 같은 것 + node가 없는 기계용) — ① MANIFEST 항목 = 디스크 파일 ② 같은 이름 png/webp 공존 ③ 큰 <script> 문법.
문법은 node --check가 있으면 그것으로, 없으면 건너뛰고 '브라우저에서 확인할 것'을 찍는다(이 PC에는 node가 없어 built-in 브라우저의 V8로 new Function(src) 컴파일로 대신 확인했다 — R37-handoff.md 6절).
또 ④ assets/sfx 총용량(발주서 상한 6.0MB) ⑤ sfx_manifest.json의 파일이 모두 디스크에 있는지.
사용: python -I tools/r37/check_build37.py shinsi-R37"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

root = sys.argv[1]
man = json.load(open(os.path.join(root, "assets", "MANIFEST.json"), encoding="utf-8"))
keys = set(man["files"])
disk = set()
for d, _, fs in os.walk(os.path.join(root, "assets")):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
        if rel != "assets/MANIFEST.json":
            disk.add(rel)
ok_man = keys == disk
print(f"MANIFEST {len(keys)} · 디스크 {len(disk)} → {'일치' if ok_man else '불일치'}")
for k in sorted(keys - disk)[:30]:
    print("  목록에만:", k)
for k in sorted(disk - keys)[:30]:
    print("  디스크에만:", k)
stems = {}
for k in disk:
    stems.setdefault(re.sub(r"\.(png|webp)$", "", k), []).append(k)
dup = [v for v in stems.values() if len(v) > 1]
print("같은 이름 두 형식:", len(dup), dup[:5])
bad_bytes = [k for k in keys & disk if man["files"][k].get("bytes") not in (None, os.path.getsize(os.path.join(root, k)))]
print("bytes 불일치:", len(bad_bytes), bad_bytes[:5])
sfx_dir = os.path.join(root, "assets", "sfx")
sfx_total = sum(os.path.getsize(os.path.join(sfx_dir, f)) for f in os.listdir(sfx_dir))
print(f"assets/sfx 총용량 {sfx_total / 1e6:.3f} MB → {'상한 6.0MB 안' if sfx_total <= 6.0e6 else '상한 초과'}")
sm = json.load(open(os.path.join(sfx_dir, "sfx_manifest.json"), encoding="utf-8"))
miss = [f for k in sm["keys"].values() for f in k["files"] if not os.path.exists(os.path.join(sfx_dir, f))]
print(f"sfx_manifest.json: 키 {len(sm['keys'])} · 파일 {len(sm['files'])} · 디스크에 없는 파일 {len(miss)}", miss[:5])
s = open(os.path.join(root, "index.html"), encoding="utf-8").read()
big = max(re.findall(r"<script(?: [^>]*)?>(.*?)</script>", s, re.S), key=len)
syntax_ok = True
if shutil.which("node"):
    tmp = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8")
    tmp.write(big)
    tmp.close()
    r = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
    os.unlink(tmp.name)
    syntax_ok = r.returncode == 0
    print("문법(node --check):", "OK" if syntax_ok else "오류\n" + r.stderr[:3000])
else:
    print(f"문법: node 없음 → 건너뜀(큰 <script> {len(big):,}자 · 브라우저 콘솔 에러 0으로 확인할 것)")
sys.exit(0 if ok_man and not dup and not bad_bytes and not miss and sfx_total <= 6.0e6 and syntax_ok else 1)
