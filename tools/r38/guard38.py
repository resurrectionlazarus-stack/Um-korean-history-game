#!/usr/bin/env python3
"""R38 보존 점검 — 권율(5시대 주인공) 걸음걸이 코드 · R37 사운드 엔진이 패치 전후 100% 같은지 확인.

사용: python -I tools/r38/guard38.py shinsi-R37 shinsi-R38
① index.html의 보존 구간(함수 이름 앵커 → 다음 함수 앵커)을 둘에서 잘라 SHA-256 비교
② [R37] 표식 수 · r37* 호출 수 같음 · 보존 구간 안에 [R38] 표식 0
③ assets/hero/era5_hero_*.png 12장 · assets/sfx/* · MANIFEST.json 바이트 동일
④ 고정 해상도 · 저해상도 배율 · 지평선 · 배경 톤 상수 그대로
끝에 PASS/FAIL 요약. 하나라도 FAIL이면 종료 코드 1."""
import hashlib
import os
import re
import sys

A, B = sys.argv[1], sys.argv[2]
fails = []


def lines_of(root):
    return open(os.path.join(root, "index.html"), encoding="utf-8").read().split("\n")


LA, LB = lines_of(A), lines_of(B)

# (이름, 시작 앵커(부분 문자열 · 첫 일치), 끝 앵커 정규식(시작 뒤 첫 일치 · None이면 한 줄))
SPANS = [
    ("ACTOR_SPEC.era5_hero(권율 원화 사양 · run~run8)", '    era5_hero: { role: "hero"', None),
    ("HERO_STEP · HERO_STEP4 · HERO_STEP8 · HERO_BOUNCE · HERO_LEAN · heroRunRhythm", "  var HERO_STEP = 9;", r"^  var BOSS_PATTERNS = \{"),
    ("stepHeroWalk(보행 리듬 · 발 먼지)", "    const stepHeroWalk = (p) => {", r"^    const stepBigGait = "),
    ("heroPose · heroPose0(걸음 프레임 · 바운스 · 기울기)", "      const heroPose = (p, g) => {", r"^      const gyebaekPose = "),
    ("stepAttract(타이틀 자동 걷기)", "      const stepAttract = (g) => {", r"^      const stepUpdate = "),
    ("주인공 이동 적분(mvx · stepHeroWalk 호출 · vx)", "        p.mvx += (mx * 7.2 * spd - p.mvx) * 0.34;", r"^        p\.prevY = p\.y;"),
    ("drawHeroEnt(주인공 그리기)", "      const drawHeroEnt = (g, eObj, qt) => {", r"^      const drawCompEnt = "),
    ("createR37Sfx(R37 효과음 엔진 본체)", "  function createR37Sfx(ac, trunk, duckBus, opts = {}) {", r"^  function createSfxEngine\(\) \{"),
    ("r37 훅 9개(r37 · r37Pan · r37Weapon · r37Hit · r37Effort · r37EnemyDown · r37BossDeath · r37WarCry · r37Step)", "    const r37 = () => sfxRef.current && sfxRef.current.r37;", r"^    const eraObjOf = "),
]


def cut(L, start, end_re):
    i = next((k for k, ln in enumerate(L) if start in ln), None)
    if i is None:
        return None, None
    if end_re is None:
        return L[i : i + 1], (i + 1, i + 1)
    j = next((k for k in range(i + 1, len(L)) if re.match(end_re, L[k])), None)
    if j is None:
        return None, None
    return L[i:j], (i + 1, j)


def sha(txt):
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()[:16]


print("== ① 보존 구간 해시(R37 ↔ R38) ==")
for name, start, end_re in SPANS:
    sa, ra = cut(LA, start, end_re)
    sb, rb = cut(LB, start, end_re)
    if sa is None or sb is None:
        fails.append(name)
        print(f"FAIL  {name}: 앵커를 못 찾음 (R37 {ra} · R38 {rb})")
        continue
    ha, hb = sha("\n".join(sa)), sha("\n".join(sb))
    r38mark = sum(1 for ln in sb if "[R38]" in ln)
    ok = ha == hb and r38mark == 0
    if not ok:
        fails.append(name)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {len(sa)}줄 R37 {ra[0]}~{ra[1]} / R38 {rb[0]}~{rb[1]} · sha {ha} {'=' if ha == hb else '≠'} {hb} · [R38] 표식 {r38mark}")

print("== ② 표식 · 호출 수 ==")
ta, tb = "\n".join(LA), "\n".join(LB)
for label, pat in [("[R37] 표식", r"\[R37\]"), ("r37 훅 호출(r37Hit · r37Effort · r37EnemyDown · r37BossDeath · r37WarCry · r37Step)", r"\br37(Hit|Effort|EnemyDown|BossDeath|WarCry|Step)\("), ("createR37Sfx 등장", r"createR37Sfx"), ("r37preload 호출", r"r37preload\(")]:
    ca, cb = len(re.findall(pat, ta)), len(re.findall(pat, tb))
    # 훅 호출은 새 자리가 늘어나는 것은 허용(R38-2A 로밍 스폰의 r37WarCry 등) · 줄어들면 FAIL. 엔진 · preload 등장 수는 같아야 함
    ok = cb >= ca if label.startswith("r37 훅 호출") else ca == cb
    if not ok:
        fails.append(label)
    print(f"{'PASS' if ok else 'FAIL'}  {label}: 이전 {ca} · 새 빌드 {cb}{' (+' + str(cb - ca) + ' 새 호출 자리)' if cb > ca else ''}")
n38 = len(re.findall(r"\[R38\]", tb))
print(f"INFO  [R38] 표식 전체: {n38} · R38 index.html {len(LB)}줄 (R37 {len(LA)}줄)")

print("== ③ 에셋 바이트 ==")


def fsha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def tree(root, sub, pat):
    d = os.path.join(root, sub)
    out = {}
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if re.search(pat, f):
            out[f] = fsha(os.path.join(d, f))
    return out


for label, sub, pat in [("권율 스프라이트 assets/hero/era5_hero_*", "assets/hero", r"^era5_hero_.*\.(png|webp)$"), ("효과음 assets/sfx/*(MP3 64 + WAV 57 + sfx_manifest.json)", "assets/sfx", r"."), ("MANIFEST.json", "assets", r"^MANIFEST\.json$")]:
    xa, xb = tree(A, sub, pat), tree(B, sub, pat)
    ok = xa == xb and len(xa) > 0
    if not ok:
        fails.append(label)
    diff = sorted(set(xa) ^ set(xb)) + sorted(k for k in xa if k in xb and xa[k] != xb[k])
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {len(xa)}개 {'모두 동일' if ok else '다름 ' + ', '.join(diff[:8])}")

print("== ④ 고정 상수 ==")
for label, pat in [("VIEW_W 960", r"var VIEW_W = 960;"), ("VIEW_H 540", r"var VIEW_H = 540;"), ("HORIZON 335", r"var HORIZON = 335;"), ("LO_RES 0.5", r"var LO_RES = 0\.5;"), ("ASSET_VIEW_SCALE 0.5", r"var ASSET_VIEW_SCALE = 0\.5;"), ("STEP_MS 1/60", r"var STEP_MS = 1e3 / 60;"), ("ACTIVE_CAP 2 · 4시대 7(R38-2A부터 전 시대 7 허용)", r"var ACTIVE_CAP = \{ 2: 7, (?:3: 7, )?4: 7(?:, 5: 7, 6: 7)? \};"), ("ASSET_PAR far/mid/ground", r"var ASSET_PAR = \{ far: 0\.15, mid: 0\.45, ground: 1 \};"), ("R31_HFX_N 128(옛 풀 그대로)", r"var R31_HFX_N = 128;"), ("ctx.filter 사용 0(검사용 feature-detect 1건 제외)", None)]:
    if pat is None:
        ca = len(re.findall(r"\.filter = \"blur\(", ta))
        cb = len(re.findall(r"\.filter = \"blur\(", tb))
        ok = ca == cb
    else:
        ca, cb = len(re.findall(pat, ta)), len(re.findall(pat, tb))
        ok = ca == cb == 1
    if not ok:
        fails.append(label)
    print(f"{'PASS' if ok else 'FAIL'}  {label}: R37 {ca} · R38 {cb}")

print()
print("RESULT", "PASS — 보존 구간 · 에셋 · 상수 모두 동일" if not fails else "FAIL — " + " / ".join(fails))
sys.exit(1 if fails else 0)
