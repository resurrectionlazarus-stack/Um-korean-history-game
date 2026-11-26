#!/usr/bin/env python3
"""RXX — (지시 요약 한 줄).

사용: cp shinsi-R(이전)/index.html shinsi-RXX/index.html && python3 -I tools/rXX/rXX_patch.py shinsi-RXX/index.html
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [RXX] 주석으로 이유를 남긴다.
주의: 옛 코드의 한글은 \\uXXXX 이스케이프로 저장돼 있다. 그런 문구를 찾을 땐 esc("한글")을 쓴다
      (도구 입력에 역슬래시-u-16진수를 직접 쓰면 실제 글자로 바뀌어 버림 — chr(92)로 만드는 이유).
"""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0
B = chr(92)


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


def esc(t):
    """실제 글자 → 파일 속 이스케이프 표기(옛 부분 한글 찾기용)."""
    return "".join(B + "u%04X" % ord(c) if ord(c) > 127 else c for c in t)


# ───────── 1. (첫 작업) ─────────
# rep('''옛 원문(앞뒤 줄을 붙여 유일하게)''', '''새 원문''')

open(P, "w", encoding="utf-8").write(s)
print("RXX patch ok —", n, "edits")
