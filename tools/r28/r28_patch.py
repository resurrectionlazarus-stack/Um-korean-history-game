#!/usr/bin/env python3
"""R28 1차 — 김유신 8프레임 질주(run3~8 몸 흔들림 보정) · 1시대 하이에나 · 코뿔소 원화(원본 톤다운 → 굽기 톤다운 생략)."""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"anchor count {c}: {old[:100]!r}")
    s = s.replace(old, new)
    n += 1


rep('''    era3_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2"], groundY: 470,''',
    '''    // [R28] 김유신 run3~run8 도착 → 8프레임 질주. 새 6장은 몸이 프레임마다 좌우로 −18 ~ +28px(원본) 떠돌아 idle 몸통에 맞춰 고정(poseDX, 윗몸 상관 실측)
    era3_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8"], poseDX: { run3: -23, run4: 4, run5: 18, run6: -23, run7: -28, run8: 8 }, groundY: 470,''')
rep('''    hyena: { era: 1, role: "HYENA", h: 64 },''', '''    // [R28] 1시대 하이에나 · 코뿔소 원화 — 원본이 12% 저채도 · 어두운 톤이라 굽기 톤다운 생략
    hyena: { era: 1, role: "HYENA", h: 64, toned: true },''')
rep('''    rhino: { era: 1, role: "RHINO", h: 80 },''', '''    rhino: { era: 1, role: "RHINO", h: 80, toned: true },''')
rep('''        // [R27 2차] 4~6시대 일반 몹 6종(미술팀 파일 이름 그대로)''', '''        // [R28] 1시대 하이에나 · 코뿔소
        ...mobFiles(1, "hyena"),
        ...mobFiles(1, "rhino"),
        // [R27 2차] 4~6시대 일반 몹 6종(미술팀 파일 이름 그대로)''')
open(P, "w", encoding="utf-8").write(s)
print("R28 patch ok —", n, "edits")
