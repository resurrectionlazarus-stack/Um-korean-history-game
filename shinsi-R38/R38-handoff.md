# R38 인수인계 — 1단계(맵 1.5배 + 치트키급 과밀 이펙트 + 60fps 방어 · 1~6절) · 2A단계(입력 잠김 수정 + 전투 밸런스 + 로밍 스폰 · 7절)

- 빌드: `shinsi-R38/` = `shinsi-R37/` 복사 + `tools/r38/r38_patch.py`(문자열 치환 28곳 · `[R38]` 표식 24). **에셋 변경 없음**(MANIFEST 520 = 디스크 520 · assets/sfx 5.912MB 그대로).
- 적용: `cp shinsi-R37/index.html shinsi-R38/index.html && python -I tools/r38/r38_patch.py shinsi-R38/index.html` (Windows: `powershell -File tools/r37/run_py.ps1 tools/r38/r38_patch.py shinsi-R38/index.html`).
- 보존 검증: `python -I tools/r38/guard38.py shinsi-R37 shinsi-R38` → **PASS**(2절). 커밋 · 푸시 · zip은 오너가 직접(이 세션에서 실행하지 않음 · 로컬 git은 `d12cab1 r38-1`까지).
- URL 비교 손잡이: `?fx38=0`(과밀 끔 = R37 그리기) · `1`(기본) · `2`(극과밀 · 측정용) / `?map38=1`(R37 길이) / `?r37=0`(옛 소리) — 소리 부하와 그리기 부하를 따로 볼 수 있다.

## 1. 바뀐 것(코드는 `shinsi-R38/index.html`만)

| 영역 | 내용 | `r38_patch.py` |
|---|---|---|
| 맵 1.5배 | `WORLD_WIDTH` 6400 → 9600 · `MAX_CAM` 8640 · `ZONE_CAM` [480, 2850, 5100, 8640] · `ZONE_TRIG` [700, 3090, 5350, 8890](카메라 + 220/240/250/250) · 1-2 경계 `SEOKJANGRI_NEO_X` 4500 · 유물 방 x(6시대) ×1.5 — 모두 `R38_MAP_K`(1.5) 하나에서 파생. 레이더 · 투사체 컬링 · 적/보스/위험물 clamp는 `WORLD_WIDTH`를 따라 자동 | 1~4절 |
| 구역 전투 카메라 | Z1~Z3는 1.5화면(`ZONE_SPAN` 1440) 안에서 주인공 추적(`r38ZoneCam`) · 주인공 벽 L+46 ~ L+1394 · 구역 기둥 오른쪽 = 범위 끝 · 웨이브 · 1시대 곰 · 2~6시대 중간보스 스폰 기준점 = 지금 카메라(`r38SpawnBase` · 화면 밖 ±60~130 등장 유지) · 6시대 탐조등 중심 = 범위 가운데. **Z4 보스 아레나는 1화면 고정 그대로**(보스 패턴이 고정 화면 가정) | 5~8절 |
| 과밀 이펙트 | `tools/r38/r38_fx.js`(패치가 읽어 넣음): 고정 풀 2개(`R38_HFX` 256 = HD 오버레이 잉크 스플래시 21 · 2중 참격호 22 · 충격 링 23 · 임팩트 라인 24 / `R38_PART` 384 = 저해상도 불꽃 1 · 잉크 방울 2 · 불씨 3) · 프레임 중 할당 0(위치는 t로 해석적 계산 · 틱 갱신 없음) · 틱당 예산 `R38_BUDGET` 48/28/14(품질 단계) · 처치는 예산과 별도 틱당 3회 · 밀도 계수 k(프레임 EMA 17 → 24ms · 그리기 11 → 15ms에서 1 → 0.4 · 품질 1/2 단계는 0.7/0.5 상한) · shadowBlur · filter · 프레임 중 그라디언트 없음 · 글로우는 `getGlowSprite` 캐시 · 종류 × 투명도 3단계 묶음 fill/stroke. 훅: 타격(`r31HitBurst` 안 `r38Hit`) · 처치(`r38Kill`) · 각성(`r38Ult`) · 구역 돌입/정리(`r38Burst`). 피니시는 기존 `flashAlpha` 0.14 | 9 · 11~13절 |
| 상한 · 훅 | 옛 파티클 상한 240/170/110 → 300/200/120 · `__RELIC_DEV.r38()`(맵 상수 · 카메라 · 풀 상태 · 그리기 ms `msH/msP` · 주인공 프레임 · 성능) · `r38mode(모드, 예산, 끄기)`(실행 중 A/B · 진단 스위치 `R38_SKIP`) | 10 · 14절 |

## 2. 보존 검증 — `guard38.py` PASS(최종 2026-11-28)

- 권율 걸음걸이 9구간 SHA-256 동일: `ACTOR_SPEC.era5_hero` · `HERO_STEP/STEP4/STEP8 · BOUNCE · LEAN · heroRunRhythm` · `stepHeroWalk` · `heroPose/heroPose0` · `stepAttract` · 주인공 이동 적분 · `drawHeroEnt`. era5_hero 스프라이트 12장 바이트 동일. 보존 구간 안 `[R38]` 표식 0.
- R37 엔진 `createR37Sfx` 350줄 · r37 훅 146줄 동일 · `[R37]` 32 · 호출 19 · `r37preload` 3 그대로. assets/sfx 122개 · MANIFEST.json 바이트 동일.
- 고정 상수 그대로: VIEW 960×540 · HORIZON 335 · LO_RES 0.5 · ASSET_VIEW_SCALE 0.5 · STEP_MS · ACTIVE_CAP · ASSET_PAR · R31_HFX_N 128 · ctx.filter 사용 0.

## 3. 기능 테스트(built-in 브라우저 콘솔 · 8043 · `tools/r38/shim38_console.js` + `func38_console.js`) — 통과

- 맵 상수 `r38()`: world 9600 · maxCam 8640 · zoneCam/zoneTrig/span 1440/neoX 4500 기대값 그대로. 콘솔 에러 0(큰 `<script>` 파싱 · 실행 확인).
- 카메라: Z1 돌입 → 첫 웨이브 x 371 · 401(왼쪽 밖) · 1501 · 1535(오른쪽 밖) · 1131(화면 안 원형) / 오른쪽 끝에서 카메라 960 · 주인공 벽 1874 / 카메라 960일 때 둘째 웨이브 883 · 902 · 2009 · 2036(밖) · 1341 · 1404(안 2 = 셋에 하나) / 왼쪽 480 · 526 / Z4 카메라 8640 고정 · 벽 8686 ~ 9525(월드 경계).
- 과밀 이펙트(4시대 J 연타): hits 10 · HFX 26 · 파티클 58 · R31 이펙트도 그대로(17) · R37 새 타격음 17 · 엔진 loaded 59 · failed 0. **처치 연출**(처치 전용 예산으로 고친 뒤 재확인): 적 3명 처치 → `kills 3`(3/3) · 풀 최대 liveH 24 · liveP 109(상한 256 · 384 안).
- 권율(5시대 우측 걷기 1.5초): 프레임 run → run8 순서 · 박자 3~4틱(평균 3.48 = HERO_STEP8 4 × 속도 보정) · 걸음 6 · 이동 641px — 코드가 R37과 같으므로(해시 동일) 동작도 같다.

## 4. 6초 부하 — **조건부 통과**(같은 PC 한계 · 정식 판정은 클라우드 하네스 또는 실기기로)

같은 장면(4시대 1전선 · 척준경 Lv.5 · T3 · 원화 몹 7 · J 연타), 이 PC built-in 브라우저, 1280×720 에뮬레이션 · dpr 1.75 · 품질 단계 0 고정. **창이 보일 때(실제 rAF)만 유효**로 쳤다.

| 판 | 초당 fps | 최저 | 그리기 평균(ms) |
|---|---|---|---|
| R37 기준선(8042) 1 · 2 · 3회 | 49 51 39 51 52 42 / 30 30 42 42 42 36 / 30 30 30 28 26 25 | 39 · 30 · 25 | 12.6 · 21.7 · 20.1 |
| R38 과밀(8043 `?fx38=1`) 1 · 2회 | 28 33 33 37 33 26 / 40 25 38 36 44 46 | 26 · 25 | 18.8 · 19.0 |
| R38 끔(같은 페이지 모드 0) | 58 54 45 57 57 53 | 45 | 12.8 |
| 같은 페이지 3초 A/B(과밀 → 끔 → HFX만 끔 → 파티클만 끔 → 섬광만 끔 → 과밀) | 44 → 52 → 51 → 49 → 55 → 56 fps | — | 12.3 → 10.9 → 15.6 → 13.6 → 14.1 → 12.1 |

판정 근거:
1. **같은 설정이 25 ↔ 56fps · 11 ↔ 22ms로 흔들려**(R37 기준선도 39 → 30 → 25) 측정 편차가 빌드 차이보다 크다. 3초 A/B에서는 과밀 켬 · 끔 차이가 편차 안(12.3 ↔ 10.9ms · 마지막 과밀 56fps).
2. 과밀 이펙트의 JS 그리기 시간(엔진 내부 타이머 `r38().stat.msH/msP`)은 **프레임당 0.5ms 이하**(0.02~0.07 + 0.08~0.43 · 최대 0.7 / 2.6). 틱 갱신 0 · 할당 0이라 GC 스파이크 요인 없음.
3. 이 PC에서는 밀도 계수가 바닥(0.4)에 머물고, 품질 단계가 내려가면 0.7 · 0.5로 더 깎인다 — 느린 기기에서는 스스로 줄어드는 구조.
4. 어느 빌드도 55fps 미달은 **R37 때와 같은 PC 한계**(R37-handoff 6-2절). R38 때문에 생긴 회귀로 볼 근거가 없다.
5. 2026-11-28 재측정 1회는 창이 가려져(타이머 모드 8fps) 무효 — 오너 지시대로 대기 루프 없이 중단.

→ **R38-1 부하: 조건부 통과.** 정식 판정은 ① 클라우드 하네스(`tools/r37/run_tests.sh`의 load를 R38용으로 복사 · R37 기준선과 함께) 또는 ② 실기기(휴대폰 · GPU)에서. 미달이면 `R38_BUDGET` → 밀도 하한(0.4) → `R38_SKIP`으로 비싼 종류부터 줄인다(`r38mode`로 실행 중 확인 가능).

### 측정 방법(이 PC · 다음에도 같은 방식)

- `tools/r38/shim38_console.js`(먼저) → `func38_console.js` / `load38_console.js`. shim이 하는 일: 창이 가려지면 게임이 `document.hidden`으로 자동 일시정지하고 rAF가 멈추므로 ① rAF를 하이브리드로 대체(보이면 실제 rAF · 120ms 안에 안 오면 타이머 · 가려지면 16.67ms 타이머) ② `visibilitychange/blur/pagehide` 캡처 차단 ③ `setHalt(true)`로 다른 탭 루프 정지 ④ 틱 기준 대기 · 창 대기 최대 10초.
- 유효 조건: 측정 중 타이머 콜백 0 · visible. 자동 일시정지가 걸렸으면 '재개' 버튼 click(`__R38S.resume()`).
- 처음 입력 때 MP3 43개 동시 fetch에서 "Failed to fetch" 2건이 한 번 났지만(8043 · 서버 쪽 일시) 다시 열면 0 — 빌드 문제 아님(바이트 동일).

## 5. 남은 것 · R38-2단계 진입 안내

- 남은 것: 부하 정식 판정(위 ①②) · 오너 눈 확인(8043에서 `?fx38=0/1/2` · `?map38=1` 비교 — 구역 1.5화면 스크롤 감 · 잉크 스플래시 · 참격호 · 충격 링 · 임팩트 라인 · 처치 폭발) · `R38-screenshots/` 없음(오너 확인 뒤 필요하면).
- 1단계에서 하지 않은 것(설계대로): 구역 사이 걷는 거리가 1.5배(약 3.3 → 5초)인데 로밍 스폰은 2단계 밸런스 범위라 넣지 않았다. 피해 숫자 합산도 넣지 않았다(상한 28 그대로).
- **R38-2단계(전투 밸런스 + 주인공 동작 다채로움)** 시작 순서: `shinsi-R38/`을 복사해 `shinsi-R38-2/` → `tools/r38-2/r38_2_patch.py`(R38 index.html 위에 적용 · r38_patch.py 방식) → 보존 검증은 `python -I tools/r38/guard38.py shinsi-R38 shinsi-R38-2`(같은 구간 · 권율 · R37 엔진) → 기능 테스트는 shim38 + func38 재사용. 밸런스 손잡이: `applyHardcoreStageScaling`(TTK 역산) · `R25_TTK` · `ACTIVE_CAP` · `ZONE_WAVES/ERA2_ZONE_WAVES/ERA4_ZONE_WAVES` · 로밍 스폰(구역 사이 `g.zoneState === "GO"/"ROAM"` 구간). 주인공 동작: `heroAtkPlan · heroAttackPose · r36Branch(갈래 기술) · startRush` — 단, 권율 걸음걸이 구간(2절)은 그대로.
- 3단계(사운드 2차 + 6초 부하): `guard` · `guardUp` · 패링 소리(`R37-handoff.md` 맨 위 bullet) + 부하 정식 판정.

## 6. 파일

`shinsi-R38/`(index.html 패치 · README 맨 위 'R38에서 바뀐 것') · `tools/r38/r38_patch.py` · `r38_fx.js` · `guard38.py` · `shim38_console.js` · `func38_console.js` · `load38_console.js` · 이 문서 · `NEXT-SESSION.md` · `HANDOVER.md` 16절.

## 7. R38-2A단계 — 입력 잠김 수정 + 전투 밸런스 + 로밍 스폰(2026-11-28 · 실플레이 피드백)

- 빌드: `shinsi-R38-2/` = `shinsi-R38/` 복사 + `tools/r38-2/r38_2_patch.py`(문자열 치환 21곳 · `[R38-2A]` 표식 23). **에셋 변경 없음.** 적용: `cp shinsi-R38/index.html shinsi-R38-2/index.html && python -I tools/r38-2/r38_2_patch.py shinsi-R38-2/index.html`.
- 보존: `python -I tools/r38/guard38.py shinsi-R38 shinsi-R38-2` → **PASS**(권율 9구간 · 스프라이트 12 · R37 엔진/훅 · 효과음 122 · MANIFEST 520 · 고정 상수). guard38은 r37 훅 호출 수를 '줄지 않음'으로, `ACTIVE_CAP`는 전 시대 7 형태도 허용하도록 고쳤다(로밍 스폰이 `r37WarCry`를 새로 부름 · CAP 변경은 의도).
- 주인공 신규 동작 · 1.5배 구간 스토리 · 대사는 **R38-2B**로 분리(7-5절). 커밋 · 푸시 · zip은 오너가 직접.

### 7-1. 입력 잠김(평타 · 일부 공격 키 무반응) — 원인과 수정

| 원인(코드) | 수정 |
|---|---|
| A. 질풍연참(`rushSlash`)의 마무리 콜백(취소 불가 `pendingHit`)이 `p.rush`를 풀어 주는데, 연참 중 어퍼(L · `triggerEraUpperSkill`)가 `queueActiveFrame`으로 그 한 칸을 덮어써 콜백이 사라짐 → `p.rush` 영구 고착 → `triggerEraWeaponCombo`(J) · `triggerEraDashSkill`(K)이 입구 `if (p.rush …) return`에서 막힘. L만 살아 있음 | 어퍼 입구에 `p.rush \|\| p.plunge` 가드(돌진과 동일) · `queueActiveFrame`은 취소 불가 콜백이 걸려 있으면 일반 공격 · 기술이 덮어쓰지 못함(`queueRefused` 카운터) · `startRush`가 시작 틱을 기록 |
| B. 키 판정이 `e.key`뿐 → 한/영 전환 뒤 글자 키(J K L U I E Q WASD) 전부 무시(Space · 방향키만 삼) | `r38KeyNorm(e)`: `e.code`(KeyJ → j · Digit1 → 1) 우선 · `e.key` 폴백 — keydown · keyup 둘 다. blur 때 `bufferAtk`도 해제 |
| C. 비정상 지연 시 자동 복구 없음 | 틱 감시 `r38LockWatch`(주인공 갱신 · pendingHit 처리 앞): rush 150틱 · plunge 지상 20틱 · special 240틱 · attackTimer > max + 40 · pendingHit 120틱 · guardTimer 180틱 · 죽은 적을 잡은 grab · bufferAtk 60틱 → 즉시 해제 + `g.r38lock` 카운터(`__RELIC_DEV.r38lock()` = 카운터 + 지금 플래그) |

회귀 테스트 `tools/r38-2/lock38_console.js`(shim38 뒤 · 8044 · 틱 기준) — 모두 PASS: **lock**(Lv.5 4시대 · `comboStep 4` + J로 연참 시작 → 곧바로 L → `upperDuringRush 1` · 29틱 뒤 `p.rush` 해제 · J 응답 attackTimer 9) · **ime**(key "ㅓ" + code KeyJ → `lastAtkPress` 갱신 · attackTimer 11) · **cycle**(J 20연타 · K · E · 일시정지 2회 · 좌우 전환 뒤 J 응답 · rush/plunge/special/grab 없음 · guardTimer 0) · **watchdog**(rush · attackTimer 999 · special을 강제로 고착 → 3틱 안 해제 · 카운터 각 1).

### 7-2. 밸런스(전투력 비례 모델은 그대로 · 배율만)

| 항목 | R38 | R38-2A | 비고 |
|---|---|---|---|
| 일반 몹 체력 | `R27_MOB_HP_K` 0.72 | × `R38_HP_K.mob` 2.2 | 4시대 Lv.5 ATK 700(무기 보너스 0) 표본: 거란 보병 10,220 → **22,483** · 여진 도끼병 8,254 → **18,159**(이전 값은 ÷2.2 계산값) — 1콤보 → 2~3콤보 |
| 중간보스 / 시대 보스 체력 | — | × 1.5 / × 1.35 | 1시대 곰 `hpMult` 16 → 24 · `applyHardcoreStageScaling` 한 줄로 1시대 포함 |
| 일반 몹 공격 간격 | 46~75틱(스폰) · 재장전 `UNIT_CD`/58~77 | × `R38_MOB_CD_K` 0.85 → 39~64틱(표본 49 · 51) | 재장전 2곳 · 1시대 짐승(`baseAttackCd`)도 · 기병 돌격 · 기관총 간격은 그대로(정수 반올림 — `attackCooldown === 18` 예고 판정 보존) |
| 중간보스 공격 간격 | 0.78배 | `R38_MID_CD` 0.72배 | 시대 보스 `R25_BOSS_CD` 0.7 그대로 |
| `ACTIVE_CAP` | {2:7, 4:7} | 전 시대 7 | 3 · 5 · 6시대 Z3(8명)도 대기열 — 60fps 보호 |
| 적 공격력 `ERA_DIFF` · 피격 배율 2.6 · 웨이브 표 | 그대로 | 그대로 | 어린이 기준 불합리 회피 |
| 격파 목표(4시대) | 67 | **88** | 로밍 21 가산(`eraKillGoal`) |

### 7-3. 로밍 스폰(맵 1.5배 체감 보강)

- 구역 zi(1~3)로 가는 길에서 '앞 구역 범위 끝(`ZONE_CAM[zi-1] + span`) ~ 트리거(`ZONE_TRIG[zi]`)' 비율 지점 `R38_ROAM_PTS` = Z1→Z2 [0.35, 0.7] · Z2→Z3 [0.35, 0.7] · Z3→Z4 [0.3, 0.55, 0.8]을 주인공이 넘으면 오른쪽 화면 밖(+70 · +130) 증원 2 + 왼쪽 화면 밖(−80) 매복 1. 동시 로밍 `R38_ROAM_CAP` 4명 상한 · 카메라 잠금 없음 · 1시대 늑대 · 하이에나 · 2시대+ 로스터(`pickRosterUnit`) · 경보 `r37WarCry`/`alarm`. 적에 `roam` 표식 · `g.r38roamLog` · `__RELIC_DEV.r382()`.
- 검증(4시대 Z1→Z2): 첫 지점 x 2330 통과 → 3명(여진 도끼병 · 여진 기병 · 여진 도끼병) 모두 화면 밖(2905 · 2960 / 1817 · 카메라 1909) · 둘째 지점 → 상한으로 1명만 추가(총 4) · 로그 2. 1단계 `func38` 4항목(맵 · 카메라 · 이펙트 처치 3/3 · 권율 run→run8 박자 3.52) · 콘솔 에러 0 그대로.
- 6초 부하: 2A는 그리기 코드 변경이 없어 1단계 조건부 통과를 그대로 둔다(체력 ↑로 전투가 길어질 뿐 · ACTIVE_CAP 7 유지).

### 7-4. 손잡이

`R38_HP_K`(mob · mid · boss) · `R38_MOB_CD_K` · `R38_MID_CD` · `ACTIVE_CAP` · `R38_ROAM_PTS` · `R38_ROAM_N`(3) · `R38_ROAM_CAP`(4) · `R38_ROAM_TOTAL`(21 = 7지점 × 3 — PTS · N을 바꾸면 같이) · `R38_LOCK_MAX`(감시 상한). 오너 체감 확인 뒤 과하면 `R38_HP_K`와 `R38_MOB_CD_K`만 낮춘다.

### 7-5. R38-2B 진입 안내

- 범위: 주인공 신규 동작 확장(`heroAtkPlan` · `heroAttackPose` · `r36Branch` · `startRush` — 권율 걸음걸이 구간은 그대로) + 1.5배 구간용 추가 스토리 · 대사 스크립트(로밍 지점의 단비 해설 · 매복 경고 말풍선 — `r38Roam`의 로그 자리에 `setCompanionBubble` 훅을 두면 됨).
- 시작: `shinsi-R38-2/` 복사 → `shinsi-R38-2B/` + `tools/r38-2b/r38_2b_patch.py`(R38-2 index.html 위) → 보존 검증 `guard38.py shinsi-R38-2 shinsi-R38-2B` → 테스트 shim38 + func38 + lock38 재사용(8045 포트 하나).
- 오너 확인 부탁(8044): 2~3콤보 체감 · 중간보스 길이 · 로밍 템포. 그 뒤 3단계(guard/guardUp/패링 소리 2차 + 6초 부하 정식 판정).
