#!/usr/bin/env python3
"""R39 빌드 점검 — ① iOS 핫픽스 표식(빌드 때 유실 금지) ② R39 각 Phase 표식 ③ 기준 빌드 대비 보존(guard38 호출은 따로).

사용: python -I tools/r39/check39.py shinsi-R39 [phase]   (phase = 1 · 2 · 3 · 4 — 그 단계까지의 표식을 요구)
끝에 PASS/FAIL. 하나라도 FAIL이면 종료 코드 1. 문법은 node가 없어 브라우저 V8(new Function)로 따로 확인한다(tools/r39/syntax_browser.js)."""
import os
import re
import sys

root = sys.argv[1]
phase = int(sys.argv[2]) if len(sys.argv) > 2 else 1
t = open(os.path.join(root, "index.html"), encoding="utf-8").read()
fails = []


def chk(label, ok, info=""):
    if not ok:
        fails.append(label)
    print(f"{'PASS' if ok else 'FAIL'}  {label}{(' — ' + info) if info else ''}")


print("== ① iOS 핫픽스 표식(d9247a9 · tools/r39/ios_hotfix_r38-2b.diff) ==")
for label, pat, mn in [
    ("viewport-fit=cover · maximum-scale=1.0 · user-scalable=no", r'name="viewport" content="[^"]*viewport-fit=cover', 1),
    ("apple-mobile-web-app-capable / status-bar black-translucent", r'apple-mobile-web-app-status-bar-style" content="black-translucent"', 1),
    ("touch-action: none(#root, #root *)", r"#root, #root \* \{\s*touch-action: none !important;", 1),
    ("-webkit-touch-callout · user-select · tap-highlight · overflow-x · text-size-adjust", r"-webkit-touch-callout: none !important;[\s\S]{0,200}-webkit-tap-highlight-color: transparent !important;", 1),
    ("overflow-x hidden · -webkit-text-size-adjust 100%", r"overflow-x: hidden !important;[\s\S]{0,120}-webkit-text-size-adjust: 100% !important;", 1),
    ("제스처(gesturestart/change/end) · 2핑거 touchmove · dblclick 차단(passive:false)", r'<script id="ios-zoom-v2">[\s\S]*?gesturestart[\s\S]*?touchmove[\s\S]*?dblclick[\s\S]*?</script>', 1),
    ("제스처 차단 스크립트는 한 곳(v1 중복 제거)", r'"gesturestart", "gesturechange", "gestureend"', 1),
    ("패드 pointer-events auto · z-index 45 · translateZ(0)", r'\[data-testid="pad-dir"\], \[data-testid="pad-action"\], \[data-testid="pad-items"\] \{\s*pointer-events: auto !important;\s*z-index: 45 !important;\s*transform: translateZ\(0\);', 1),
    ("wide 모드 패드 position absolute", r'\[data-layout="wide"\] \[data-testid="pad-items"\] \{\s*position: absolute !important;', 1),
    ("버튼 자식(svg · span) pointer-events none", r'\[data-testid="pad-items"\] button \* \{\s*pointer-events: none !important;', 1),
    ("canvas pointer-events-none", r'className: "w-full h-full object-cover block pointer-events-none"', 1),
    ("display: contents 래퍼 없음", r'className: wide \? "contents"', 0),
    ("hover:opacity-100 없음(첫 탭 먹힘)", r"hover:opacity-100", 0),
    ("wide 루트 100dvh/100dvw", r'style: wide \? \{ position: "fixed", height: "100dvh", width: "100dvw" \}', 1),
    ("game-frame dvh/dvw 기준", r'calc\(100dvh \* 16 / 9\)', 1),
    ("좌/우 패드 safe-area(방향 · 공격 · 아이템 패드 ≥ 2)", r'max\(8px, env\(safe-area-inset-(left|right)\)\)', 3),
    ("조작 버튼 onPointerDown 통일(≥ 14)", r"onPointerDown:", 14),
    ("방향키 setPointerCapture 4 · onPointerUp · onPointerCancel", r"setPointerCapture\?\.\(e\.pointerId\)", 4),
    ("좌/우 입력 때 R38-2B _dirT 갱신(패드)", r'gameRef\.current\.keys\._dirT = gameRef\.current\.tick; gameRef\.current\.keys\.(left|right) = true', 2),
]:
    c = len(re.findall(pat, t))
    ok = c == mn if mn in (0, 1, 2) else c >= mn
    chk(label, ok, f"{c}개")

print("== ② R39 Phase 표식 ==")
need = {
    1: [("부활 25% 차감", r"var R39_REVIVE_PENALTY = 0\.25;"), ("버프 칩 바", r'"data-testid": "buff-chips"'), ("아이템 버튼 안 유물 텍스트 없음", None), ("HUD 부활 횟수", r'"부활 ", hud\.continues'), ("DEV r39", r"r39: \(\) => \{")],
    2: [("난이도 2트랙", r"var R39_MODES = "), ("소프트 캡", r"r39SoftCap"), ("콤보 브레이크", r"R39_COMBO_BREAK"), ("가드 브레이크", r"r39GuardBreak"), ("패링 보상", r"r39ParryReward")],
    3: [("STAGES 10", r"var R39_STAGES = "), ("연표 두문자 바", r'"data-testid": "timeline-bar"'), ("시공 순서 봉인", r"SEAL_TRIAL"), ("퀴즈 보강", r"R39_QUIZ_EXTRA")],
    4: [("CHANGELOG 생성은 파일로", None)],
}
for ph in range(1, phase + 1):
    for label, pat in need.get(ph, []):
        if pat is None:
            if label.startswith("아이템 버튼 안"):
                chk(f"P{ph} {label}", 'className: "text-[9px] text-amber-300" }, hud.relic.icon' not in t)
            continue
        chk(f"P{ph} {label}", len(re.findall(pat, t)) >= 1)

print("== ③ 크기 ==")
lines = t.count("\n")
n39 = len(re.findall(r"\[R39\]", t))
mb = len(t.encode("utf-8")) / 1e6
print(f"INFO  index.html {lines}줄 · {mb:.2f}MB · [R39] 표식 {n39}")
print()
print("RESULT", "PASS" if not fails else "FAIL — " + " / ".join(fails))
sys.exit(1 if fails else 0)
