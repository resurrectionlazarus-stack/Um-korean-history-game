#!/usr/bin/env python3
"""빌드 폴더 점검 — ① MANIFEST 항목 = 디스크 파일(MANIFEST.json 제외) ② 같은 이름 png/webp 공존 ③ index.html 큰 <script> 문법(node --check)
사용: python3 -I tools/r33/check_build.py shinsi-R33   (실패하면 종료코드 1)"""
import json
import os
import re
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
s = open(os.path.join(root, "index.html"), encoding="utf-8").read()
big = max(re.findall(r"<script(?: [^>]*)?>(.*?)</script>", s, re.S), key=len)
tmp = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8")
tmp.write(big)
tmp.close()
r = subprocess.run(["node", "--check", tmp.name], capture_output=True, text=True)
os.unlink(tmp.name)
print("문법:", "OK" if r.returncode == 0 else "오류\n" + r.stderr[:3000])
sys.exit(0 if ok_man and not dup and r.returncode == 0 else 1)
