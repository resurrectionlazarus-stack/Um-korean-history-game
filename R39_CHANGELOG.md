# R39 변경 요약 — 브랜치 `r39-mega` (기준: shinsi-R38-2B · iOS 핫픽스 커밋 d9247a9)

빌드: `shinsi-R39/index.html` = `shinsi-R38-2B/index.html`(핫픽스 포함) + `tools/r39/r39_p1_patch.py` → (Phase 2) `r39_p2_patch.py` → (Phase 3) `r39_p3_patch.py`. 에셋 · MANIFEST 변경 없음(520 = 520).
검증 도구: `tools/r39/check39.py <빌드> <phase>`(iOS 핫픽스 표식 + Phase 표식) · `tools/r38/guard38.py shinsi-R38-2B shinsi-R39`(권율 걸음걸이 · R37 엔진 · 효과음 · 2A 상수 보존) · `tools/r39/syntax_browser.js`(브라우저 V8 `new Function` 문법 점검 — 이 PC에 node 없음).

## Phase 1 — iOS 핫픽스 영구 반영 + UI/점수 결함 (커밋: r39-mega)

- **핫픽스 영구 반영**: 이 저장소에는 JSX 원본(App.jsx)이나 HTML 셸 템플릿이 따로 없다(번들된 index.html + rXX 패치 체인이 원본). 그래서 ① 핫픽스 커밋 d9247a9의 diff를 `tools/r39/ios_hotfix_r38-2b.diff`로 보존, ② R39 체인은 핫픽스가 든 R38-2B 빌드에서 시작, ③ `check39.py`가 빌드마다 19개 표식(viewport-fit · apple-mobile-web-app · touch-action/callout/user-select/tap-highlight/overflow-x/text-size-adjust · gesture·2핑거 touchmove·dblclick 차단 · 패드 pointer-events/z-index 45/translateZ · wide absolute · 버튼 자식·canvas pointer-events none · `display: contents` 없음 · `hover:opacity-100` 없음 · 100dvh/100dvw · safe-area · onPointerDown ≥ 14 · setPointerCapture 4 · 좌/우 `_dirT`)을 검사해 유실을 막는다. 중복돼 있던 v1 제스처 차단 `<script>`는 제거(v2 한 곳).
- **아이템 버튼 줄바꿈 결함**: 사용 버튼 안의 부적 · 유물 · 전설 성물 텍스트를 빼고, `pad-items` 맨 위 `buff-chips` 뱃지 바(칩 · `col-span-12` · `pointer-events-none`)로 분리. 버튼에는 아이콘 · 이름 · 수량만.
- **부활 점수**: `revivePlayer(true)`가 점수를 0으로 되돌리던 것을 25% 차감(`R39_REVIVE_PENALTY`)으로. 차감 누계 `stats.scoreLostByRevive`, 횟수 `stats.continues`를 HUD("부활 N") · 게임오버("· 부활 N회(25% 차감)") · 승리 화면에 표기.
- DEV: `__RELIC_DEV.r39()`(차감 비율 · 점수 · 횟수 · 칩 유무) · `r39revive()`.
- 검증: 문법 OK(1,205,790자) · check39 Phase 1 PASS · guard38 PASS · 콘솔 에러 0 · 부적 900틱 → 칩 "부적 15초" 표시 + 버튼 텍스트 "🪨 돌창 ×3 I"만 · 점수 1,000,000 → 부활 → 750,000 · continues 1 · HUD "부활 1".

## Phase 2 — 전투 밸런스 전면 개편(무쌍 × D&D2) — `tools/r39/r39_p2_patch.py`(15곳)

- **난이도 2트랙**(타이틀 START 위 두 버튼 · localStorage `shinsi.mode` · HUD 태그): 무쌍(스토리 · 초등) = 체력 ×1.0 · 적 공격 ×1.0 · 정면 가드 경감 50% · 콤보 브레이크 40 HIT · 패링 각성 +25 · 드롭 ×1.0 / 정사(D&D2 · 한능검) = 체력 ×1.2 · 적 공격 ×1.25 · 경감 75% · 25 HIT · +40 · 드롭 ×0.6. `R39_MODES` · `r39Mode()` · `__RELIC_DEV.r39mode(m)`.
- **시대별 공격력 소프트 캡** `r39SoftCap`: 다음 시대 진입 때 `atk = 210 + 110×(시대−1) + 초과분 15%`, `awakenedTier ≤ 1.45`, `powerAtEraStart` 재계산(예: ATK 3,110 · 각성 2.35 → 739 · 1.45). 11,835 ATK 폭증 차단.
- **구역 리듬** `R39_ZONE_K`: Z1 체력 ×1.15 · 적 공격 ×1.1 → Z2 · Z3 ×0.9 → Z4(보스 · 중간보스는 구역 배율 제외).
- **콤보 브레이크** `r39ComboBreak`: 같은 적 90틱 창 안 연속 HIT가 모드 임계(40/25)에 닿으면 붉은 섬광 · 슈퍼아머 48틱(피해 50% · 경직 · 넉백 · 띄우기 없음) · 주인공 튕겨내기(vx 16 · flinch) · 적 공격 간격 0으로 즉시 반격.
- **가드 브레이크 병종** `r39GuardUnit`(방패 · 철갑 · 기병 · 정예 · 장교): 정면 평타 경감(모드별) + "GUARD" 표시 / 저스트 패링 · 어퍼 · 돌진 · 갈래 · 공중 · 등 뒤(경직 중 돌아 들어가기) · 카운터 · 확정 크리면 "BREAK!" 180틱 → 정상 +10%. 기존 `guardTimer` 가드와는 겹치지 않음.
- **저스트 패링 보상**: 반경 300 경직 ×2 · 가드 병종 BREAK · 보스 경직 20 · 각성 게이지 모드별 추가 · 90틱 확정 크리티컬 반격 창구(`g.r39ParryCrit`) · "반격 창구!" 표시.
- 검증(8046 · 4시대): 모드 버튼 2 · 선택 유지 · HUD "무쌍" / 거란 보병 체력 무쌍 3,935 ↔ 정사 4,722(×1.2) / 콤보 브레이크 41타에 발동 · 슈퍼아머 45틱 · 밀어내기 · 붉은 섬광 / 방패병 정면 3회 모두 ×0.5(1.3 → 0.65) · 경직 중 등 뒤 → BREAK 158틱 · 붕괴 중 ×1.1 · 돌진(K) → BREAK · 정사 정면 ×0.25 / 패링 창구 88틱 · 각성 100 / 소프트 캡 3,110 → 739 · 각성 1.45 / 문법 OK · 콘솔 에러 0 · guard38 PASS · check39 Phase 2 PASS.

## Phase 3 — 10스테이지 캠페인 · 연표 두문자 바 · 시공 순서 봉인 — `tools/r39/r39_p3_patch.py`(24곳) + `tools/r39/r39_stages.js`(스테이지 데이터)

- **10스테이지** `R39_STAGES`(기준 시대 1,2,3,3,4,4,5,5,6,6): 1 선사 [석-주-암-빗] · 2 고조선 [단-진-위-왕] · 3 삼국 [살-황-평-매] · **4 남북국 [천-발-청-후]** · 5 고려 전기 [공-고-훤·신-일] · 6 고려 후기 [무-처-공-홍] · 7 조선·양란 [건-옥·한-진·행-병] · **8 개항기·동학 [고-고·백-황·황·전·집-우]** · **9 일제 I [의-봉-청-간·자·삼·미]** · 10 일제 II~광복 [의-한-광-해]. 신규 스테이지는 **에셋 추가 없이** 기준 시대의 원화 · 병종 · 배경 · BGM을 그대로 쓰고, 이름표(`over`: name · fieldName · heroTitle · bossName …) · 중간보스 이름(`mids`) · 병종 이름표(`units`) · 로밍 해설(`story`) · 중간 퀴즈(`midQuiz`) 층만 덮어쓴다(`r39EraObjFor` · `r39UnitLabel` · `r39MidName` · `r39MidQuizList`). 에셋이 없어도 로딩 멈춤 · 404 경로 없음. 원화 없는 인물은 "(임시 원화: …)" 꼬리표 → 발주서 `R39_ASSET_TODO.md`.
- **진행**: `advanceToNextEraImmediate` → `r39SetStage(+1)`(기준 시대가 바뀌면 `switchEraDirectly`) · 스테이지 10 뒤 기존 광복 엔딩. DEV 시대 버튼 · `engineReset`은 그 시대의 첫 스테이지로 동기화(`R39_FIRST_STAGE_OF_ERA`). HUD "STAGE N"은 스테이지 번호(1시대는 기존 1-1/1-2 코드 유지).
- **연표 두문자 바**(`timeline-bar`): 모바일(compact)에서도 항상 표시 · 클리어한 구역은 ✔ 금빛 + 연도(예 "✔ [공] 공산 전투 927") · 현재 구역 ⚔.
- **시공 순서 봉인**(상태 `SEAL_TRIAL` · 상수 `R39_SEAL`): 보스 조우 직전(`spawnEraBoss` 첫 호출) 5초 안에 이 스테이지의 사건 카드 4장(섞음)을 일어난 순서대로 터치 또는 키보드 1~4. 그동안 세계는 멈춘다. 성공 → 보스 등장 직후 방어막(`phaseInv`) 파괴 · 180틱 그로기 · 공격 +25%(1800틱 · 피해식 `g.r39sealBuff`) / 실패(순서 틀림 · 5초 초과) → 광폭화(공격 ×1.3 · 속도 ×1.15 · 공격 간격 ×0.85 · 붉은 오라). 스테이지당 1회(`r39sealDone`) · 자동 퀴즈 통과(autoPassQuiz) 때는 건너뜀.
- **퀴즈 보강**: 부활 · 하드 시험 뱅크에 `R39_QUIZ_EXTRA`(3 · 4 · 5 · 6시대 각 4문 — 남북국 · 후삼국 · 동학 · 무장 독립전쟁) · `R39_HARD_EXTRA`(각 1문) → QUIZ_BANK 72 → 88 · HARD 36 → 40. 신규 스테이지 중간 퀴즈 2문씩(4 · 5 · 6 · 8 · 9 · 10 — 뱃지 "유물 각성 퀴즈 (STAGE N · n차 돌파)").
- DEV: `r39stage(n)`(워프 · 현황) · `r39stages()` · `r39seal()` · `r39sealAnswer(i)` · `r39sealState()`.
- 검증(8046): 문법 OK(1,245,969자) · check39 Phase 3 PASS · guard38 PASS · 콘솔 에러 0(새 로드) · 스테이지 1~10 워프 전부 assets ready · 이름표 · 구역 4칸 · 중간 퀴즈 제목 확인 · 스테이지 3 → 4(같은 3시대) → 5(4시대 · 소프트 캡 540) 진행 · 스테이지 10 → 광복 엔딩 · 봉인 성공(938ms · 보스 hitStun 139 · phaseInv 0 · 공격 ×1.25 1800틱) · 순서 실패(dmgMult ×1.3 · enraged) · 시간 초과(5,004ms → 광폭화) · 연표 "✔ 공산 전투 927 · ✔ 고창 전투 930" 금빛 · 퀴즈 뱃지 "STAGE 5 · 1차 돌파" / "STAGE 10 · 2차 돌파 한국광복군 창설" · 스테이지 8 구역 1 해설 말풍선(병인 · 신미양요 → 갑신정변) + 로밍 증원 4.
