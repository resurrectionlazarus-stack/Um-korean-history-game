#!/usr/bin/env python3
"""R39 Phase 1 — iOS 핫픽스 영구 반영 + UI/점수 결함 수정. 기준: shinsi-R38-2B/index.html(커밋 d9247a9 · iOS 핫픽스 포함) 복사본 위에 적용.

사용: cp shinsi-R38-2B/index.html shinsi-R39/index.html && python -I tools/r39/r39_p1_patch.py shinsi-R39/index.html
규칙: 앵커(옛 원문)는 정확히 count번 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R39] 주석.

이 저장소에는 JSX 원본(App.jsx)이나 HTML 셸 템플릿이 따로 없다 — index.html(번들)과 rXX 패치 체인이 원본이다. 그래서 iOS 핫픽스의 '영구 반영'은
  ① 핫픽스 커밋(d9247a9)의 diff를 tools/r39/ios_hotfix_r38-2b.diff 로 보존하고 ② R39 체인이 핫픽스가 든 R38-2B 빌드에서 시작하며
  ③ tools/r39/check39.py 가 핫픽스 표식(viewport-fit · gesture 차단 · touch-action · 패드 pointer-events · onPointerDown · dvh · safe-area)을 빌드마다 검사하는 것으로 한다.
Phase 1 수정:
  1. 중복된 제스처 차단 <script>(v1) 제거 — ios-zoom-v2 가 같은 일 + 2핑거 touchmove 까지 한다
  2. 세로 모드 아이템 버튼 안에 들어 있던 부적 · 유물 · 전설 성물 텍스트를 버튼 밖 상단 뱃지 바(칩)로 분리(줄바꿈 깨짐 · 겹침)
  3. 부활 시 점수 0 초기화 → 25% 차감(R39_REVIVE_PENALTY) + 부활 횟수 HUD · 게임오버 · 승리 화면 표기
  4. DEV 훅 r39()
"""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0
B = chr(92)


def esc(t):
    # 옛 코드의 한글은 \\uXXXX 로 저장돼 있다 — 도구 입력의 역슬래시-u 가 실제 글자로 바뀌므로 chr(92)로 조립한다(HANDOVER 7절)
    return "".join((B + "u{%X}" % ord(c) if ord(c) > 0xFFFF else B + "u%04X" % ord(c)) if ord(c) > 127 else c for c in t)


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 1. 중복 제스처 스크립트 제거 + 보존 안내 ─────────
rep('''<script>
  ["gesturestart", "gesturechange", "gestureend"].forEach(function (ev) {
    document.addEventListener(ev, function (e) { e.preventDefault(); }, { passive: false });
  });
  document.addEventListener("dblclick", function (e) { e.preventDefault(); }, { passive: false });
</script>
<style id="ios-fix-v2">''', '''<style id="ios-fix-v2">
  /* [R39] iOS 핫픽스(커밋 d9247a9)는 tools/r39/ios_hotfix_r38-2b.diff 로 보존 · 빌드마다 tools/r39/check39.py 가 표식을 검사한다. 제스처 차단은 아래 ios-zoom-v2 한 곳 */''')

# ───────── 2. 최상위 상수 ─────────
rep('''  var R38B_DIR_TAP = 10;''', '''  // [R39] 부활 점수 차감 비율(0으로 되돌리지 않는다)
  var R39_REVIVE_PENALTY = 0.25;
  var R38B_DIR_TAP = 10;''')

# ───────── 3. 아이템 패드: 버프 칩을 버튼 밖으로 ─────────
rep('''        (() => {
          const it = hud.item || { slot: 0 };''', '''        /* [R39] 활성 버프(부적 · 유물 · 전설 성물)는 버튼 밖 상단 뱃지 바(칩)로 — 세로 모드에서 아이템 버튼 안 줄바꿈이 깨지고 겹치던 결함 */
        (hud.relic || hud.legend || hud.item && hud.item.charmT > 0) && /* @__PURE__ */ React.createElement(
          "div",
          { className: "col-span-12 flex flex-wrap justify-center gap-1 pointer-events-none", "data-testid": "buff-chips" },
          hud.item && hud.item.charmT > 0 && /* @__PURE__ */ React.createElement("span", { className: "px-2 py-0.5 rounded-full bg-yellow-500/20 border border-yellow-400/60 text-yellow-200 text-[9px] font-black whitespace-nowrap" }, "부적 ", Math.ceil(hud.item.charmT / 60), "초"),
          hud.relic && /* @__PURE__ */ React.createElement("span", { className: "px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-400/60 text-amber-200 text-[9px] font-black whitespace-nowrap" }, hud.relic.icon, " ", hud.relic.name, " ", Math.ceil(hud.relic.t / 60), "초"),
          hud.legend && /* @__PURE__ */ React.createElement("span", { className: "px-2 py-0.5 rounded-full bg-yellow-400/20 border border-yellow-300/60 text-yellow-100 text-[9px] font-black whitespace-nowrap" }, "🏆 ", hud.legend.name)
        ),
        (() => {
          const it = hud.item || { slot: 0 };''')
rep('''            it.charmT > 0 && /* @__PURE__ */ React.createElement("span", { className: "text-[9px] text-yellow-200" }, "''' + esc("부적 ") + '''", Math.ceil(it.charmT / 60), "''' + esc("초") + '''"),
            hud.relic && /* @__PURE__ */ React.createElement("span", { className: "text-[9px] text-amber-300" }, hud.relic.icon, " ", hud.relic.name, " ", Math.ceil(hud.relic.t / 60), "''' + esc("초") + '''"),
            hud.legend && /* @__PURE__ */ React.createElement("span", { className: "text-[9px] text-yellow-300" }, "''' + esc("🏆 ") + '''", hud.legend.name),
''', '''''')

# ───────── 4. 부활 점수: 0 초기화 → 25% 차감 · 횟수 표기 ─────────
rep('''      if (isContinue) {
        commitHiScore(st.score);
        st.lives = 3;
        st.score = 0;
        st.continues = (st.continues || 0) + 1;
      }''', '''      if (isContinue) {
        commitHiScore(st.score);
        st.lives = 3;
        // [R39] 점수를 0으로 되돌리지 않고 25% 차감(실기기 완주 리포트: 하이스코어 1,742,950 ↔ 최종 38,150) · 횟수는 HUD · 결과 화면에 표기
        st.scoreLostByRevive = (st.scoreLostByRevive || 0) + Math.floor(st.score * R39_REVIVE_PENALTY);
        st.score = Math.floor(st.score * (1 - R39_REVIVE_PENALTY));
        st.continues = (st.continues || 0) + 1;
      }''')
rep('''            score: st.score,''', '''            score: st.score,
            continues: st.continues || 0, // [R39] 부활 횟수''')
rep('''hud.score.toLocaleString())), /* @__PURE__ */ React.createElement("span", { className: "text-slate-400" }, "HI "''', '''hud.score.toLocaleString()), hud.continues > 0 && /* @__PURE__ */ React.createElement("span", { className: "ml-1 text-rose-300" }, "부활 ", hud.continues)), /* @__PURE__ */ React.createElement("span", { className: "text-slate-400" }, "HI "''')
rep('''"SCORE ", hud.score.toLocaleString()), /* @__PURE__ */ React.createElement("div", { className: "mt-1 text-xs font-black text-amber-300 tabular-nums" }, "HI-SCORE "''', '''"SCORE ", hud.score.toLocaleString(), hud.continues > 0 ? ` · 부활 ${hud.continues}회(25% 차감)` : null), /* @__PURE__ */ React.createElement("div", { className: "mt-1 text-xs font-black text-amber-300 tabular-nums" }, "HI-SCORE "''')
rep('''hud.score.toLocaleString(), " ''' + esc("점") + '''"))''', '''hud.score.toLocaleString(), " ''' + esc("점") + '''", hud.continues > 0 ? ` (부활 ${hud.continues}회 · 25% 차감)` : null))''')

# ───────── 5. DEV 훅 ─────────
rep('''          spawnUnit: (id, x, z) => spawnEnemyAt(x, z, { unit: id, keepPos: true }),''', '''          spawnUnit: (id, x, z) => spawnEnemyAt(x, z, { unit: id, keepPos: true }),
          // [R39] 검증: 부활 점수 차감 · 횟수 · 버프 칩 유무
          r39: () => {
            const st = gameRef.current.stats;
            return { penalty: R39_REVIVE_PENALTY, score: st.score, continues: st.continues || 0, lost: st.scoreLostByRevive || 0, chips: !!document.querySelector('[data-testid="buff-chips"]') };
          },
          r39revive: () => {
            revivePlayer(true);
            return gameRef.current.stats.score;
          },''')

open(P, "w", encoding="utf-8").write(s)
print("R39 P1 patch ok —", n, "edits")
