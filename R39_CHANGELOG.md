# R39 변경 요약 — 브랜치 `r39-mega` (기준: shinsi-R38-2B · iOS 핫픽스 커밋 d9247a9)

빌드: `shinsi-R39/index.html` = `shinsi-R38-2B/index.html`(핫픽스 포함) + `tools/r39/r39_p1_patch.py` → (Phase 2) `r39_p2_patch.py` → (Phase 3) `r39_p3_patch.py`. 에셋 · MANIFEST 변경 없음(520 = 520).
검증 도구: `tools/r39/check39.py <빌드> <phase>`(iOS 핫픽스 표식 + Phase 표식) · `tools/r38/guard38.py shinsi-R38-2B shinsi-R39`(권율 걸음걸이 · R37 엔진 · 효과음 · 2A 상수 보존) · `tools/r39/syntax_browser.js`(브라우저 V8 `new Function` 문법 점검 — 이 PC에 node 없음).

## Phase 1 — iOS 핫픽스 영구 반영 + UI/점수 결함 (커밋: r39-mega)

- **핫픽스 영구 반영**: 이 저장소에는 JSX 원본(App.jsx)이나 HTML 셸 템플릿이 따로 없다(번들된 index.html + rXX 패치 체인이 원본). 그래서 ① 핫픽스 커밋 d9247a9의 diff를 `tools/r39/ios_hotfix_r38-2b.diff`로 보존, ② R39 체인은 핫픽스가 든 R38-2B 빌드에서 시작, ③ `check39.py`가 빌드마다 19개 표식(viewport-fit · apple-mobile-web-app · touch-action/callout/user-select/tap-highlight/overflow-x/text-size-adjust · gesture·2핑거 touchmove·dblclick 차단 · 패드 pointer-events/z-index 45/translateZ · wide absolute · 버튼 자식·canvas pointer-events none · `display: contents` 없음 · `hover:opacity-100` 없음 · 100dvh/100dvw · safe-area · onPointerDown ≥ 14 · setPointerCapture 4 · 좌/우 `_dirT`)을 검사해 유실을 막는다. 중복돼 있던 v1 제스처 차단 `<script>`는 제거(v2 한 곳).
- **아이템 버튼 줄바꿈 결함**: 사용 버튼 안의 부적 · 유물 · 전설 성물 텍스트를 빼고, `pad-items` 맨 위 `buff-chips` 뱃지 바(칩 · `col-span-12` · `pointer-events-none`)로 분리. 버튼에는 아이콘 · 이름 · 수량만.
- **부활 점수**: `revivePlayer(true)`가 점수를 0으로 되돌리던 것을 25% 차감(`R39_REVIVE_PENALTY`)으로. 차감 누계 `stats.scoreLostByRevive`, 횟수 `stats.continues`를 HUD("부활 N") · 게임오버("· 부활 N회(25% 차감)") · 승리 화면에 표기.
- DEV: `__RELIC_DEV.r39()`(차감 비율 · 점수 · 횟수 · 칩 유무) · `r39revive()`.
- 검증: 문법 OK(1,205,790자) · check39 Phase 1 PASS · guard38 PASS · 콘솔 에러 0 · 부적 900틱 → 칩 "부적 15초" 표시 + 버튼 텍스트 "🪨 돌창 ×3 I"만 · 점수 1,000,000 → 부활 → 750,000 · continues 1 · HUD "부활 1".
