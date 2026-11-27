# R37 인수인계 — 리얼리티 효과음(음향감독 녹음 104개 → 64개) + Web Audio 엔진

- 플레이 링크: https://claude.ai/artifact/6o4E1jES1aXqxfDCjPE7jc — **게시 중단(불완전)**. 세 묶음 가운데 둘(349개)만 올라간 상태에서 셋째 묶음이 아티팩트 한 판 상한(512개 · 이번 빌드는 523개)에 걸렸고, 오너 지시로 게시를 멈췄습니다. 이 링크로는 아직 플레이가 안 됩니다. 다시 올릴 때는 게임이 읽지 않는 보존용 파일(옛 몽골 천호장 · 공성 사령관 원화 8 · 고조선 창병 · 궁수 PNG 6 · R35 rock_* 4)을 빼야 합니다.
  - R36.5-2 링크(https://claude.ai/artifact/FgvndJmipef8BGKyU82Yvf)는 그대로(예전 소리와 비교용). 게임 주소 끝에 `?r37=0`을 붙여도 예전 소리로 플레이됩니다.
- **청음 반영 1차(같은 날 · 오너 피드백)**: ① 고려 · 조선 구간의 '깡깡' 금속성 · 단단한 피크 → 칼 소리의 4~7kHz 부스트 제거 · 5kHz 위 -5dB · 7.5kHz -4dB · 봉우리 둥글림(tanh) · 목표 -14.5dB · 재생 볼륨 0.85/0.9, 갑옷 · 방패 타격은 R35 쇠 울림(`cutArmor`) 대신 새 베기를 낮고 작게(0.7 · 피치 0.93), 적 베임 소리는 4kHz 위 -8dB · 0.4 · 셋에 하나 ② 1시대 긴 '으허!' → 강한 기합 0.9초 · 원시 포효 1.4초로 줄이고, 마지막 타는 짧은 기합 75% · 강한 15% · 원시 포효 10%(6초 쿨다운), 포효 100%는 각성 때만. 바뀐 파일: `tools/r37/build_sfx.py` · `r37_engine.js` · `r37_patch.py` · `make_sound_check.py`, 다시 구운 MP3 10개(`sfx_sword_slash_01~03` · `sfx_sword_cut_hit` · `sfx_enemy_katana_hurt_01~02` · `sfx_hero_effort_heavy_01~02` · `sfx_hero_barbarian_roar_01~02`) · `sfx_manifest.json` · `MANIFEST.json`(bytes) · `index.html`(재패치) · `sound-check.html`. 부하 테스트는 오너 지시로 생략. 아직 안 건드린 것: 막을 때의 `guard` · `guardUp`(R-old 합성 삼각파)와 패링 소리 — '깡' 느낌이 거기서도 난다면 알려 주세요.
- 음향 점검 페이지: https://claude.ai/artifact/QSg43hGAD1mgJALZhnyZMT (같은 주소에 R37판으로 덮어 올림 — 예전 소리 ↔ 새 녹음 비교 · 새 소리 · 장면)
- 전체 배포본: `dist/shinsi-R37-deploy.zip` (+ `.sha256`) · 나눔 3개(`shinsi-R37-part1-code-sfx-era15.zip` · `part2-era24.zip` · `part3-era36.zip`, 각 30MB 미만)
- **바뀐 것만**: `dist/shinsi-R37-changed-code-sfx.zip` — index.html · 목록 · 새 효과음 64 + 표 · 안내문 · 점검 페이지. R36.5-2 배포 폴더 위에 덮어쓰면 R37이 됩니다.
- **저장소 반영 묶음**: `dist/shinsi-R37-repo-delta.zip` — 이 PC에 git이 없어 커밋 · 푸시를 하지 못했습니다(10절). 안의 `APPLY-ON-CLOUD.md`대로 클라우드 세션에서 풀면 커밋할 수 있습니다.
- 작업 폴더: `shinsi-R37/` (index.html 패치 48곳 · assets/sfx에 MP3 64개 + `sfx_manifest.json` · MANIFEST 455 → 520)
- 비교 이미지: `R37-screenshots/R37-spectrograms.jpg`(예전 합성 ↔ 새 녹음 6쌍) · `R37-loop-seams.jpg`(루프 이음매 파형)
- 새 방으로 넘어가실 때: `NEXT-SESSION.md` + `dist/shinsi-handover-R37.zip`

## 0. 발주서와 반영

| 발주서 | 한 일 | 자세히 |
|---|---|---|
| [하드 룰 1] 원본 WAV 104개(126.5MB) 커밋 금지 · `tools/r37/build_sfx.py`로 선별 · 트림 · 정규화 · MP3 · `assets/sfx/` 6.0MB 이하 | 원본은 `.gitignore`(`신시 효과음.zip` · `신시 효과음/`). 새 MP3 64개 = 2.02MB. `assets/sfx/` 전체(기존 WAV 57개 포함) **5.912MB** | 2절 |
| [하드 룰 2] MP3 통일(단발 모노 96~128 · 공간감 스테레오 128kbps · 44.1kHz) | 모노 96(타격 · 스윙) / 112(목소리 · 활 · 총) · 스테레오 128. OGG 없음 | 2절 |
| [하드 룰 3] 게임 로직 · check_build · run_tests 무결성 · FPS 회귀 0% | 코드는 패치 48곳, 모두 "새 엔진이 준비됐으면 새 소리, 아니면 예전 소리"의 구조라 새 소리를 못 받는 기기에서도 R36.5-2와 똑같이 동작. 빌드 점검 통과. **FPS는 이 PC에서 판정하지 못했습니다(6-2절 — 그리기 시간은 같음)** | 5 · 6절 |
| [작업 1] 전처리 파이프라인(앞 무음 0ms 컷 · 하이라이트 · 심리스 루프 · 정규화 · EQ) | `tools/r37/build_sfx.py` — 발주서 공정을 그대로, 다른 점은 2-3절 | 1 · 2절 |
| [작업 2] 33개 프리픽스 선별 · 게임 키 매핑표 | 발주서의 테이크 번호 그대로 61개 테이크 → 키 64개(파생 4개 포함) | 3절 |
| [작업 3] h.js Web Audio 엔진 · 실전 연출 규격 · DEV 훅 | **엔진은 index.html에 넣었습니다**(h.js는 Playwright 테스트 하네스라 게임 코드가 아닙니다). `createR37Sfx`(tools/r37/r37_engine.js) + 게임 연결 패치. `window.__SHINSI_SFX__` · `__RELIC_DEV.r37()` | 4 · 5절 |
| [작업 4] QA 리포트(로그 · check_build · run_tests · 6초 부하 · .gitignore · 커밋/푸시) | 로그 2-4절 · 빌드 점검 6-3절 · 기능 6-1절 · 부하 6-2절 · .gitignore ○ · **커밋/푸시 ×(10절)** | 6 · 10절 |

## 1. 원본 실측(선별 전)

`python -I tools/r37/analyze_wavs.py <WAV 폴더>` — 104개 · 33개 프리픽스 · 모두 48kHz · 16bit · 스테레오 · 120.7MB(발주서의 126.5MB는 zip 크기로 보입니다).

| 잰 것 | 결과 |
|---|---|
| 앞 무음(피크 대비 -32dBFS 또는 0.025 최초 돌파) | 0~944ms. 발주서가 짚은 `heavy_wooden_hunting #1` 854ms · `massive_volley_of_do #4` 802ms 그대로 확인. 단발 타격도 72~470ms |
| RMS(무음 뺀 구간) | -12.6(`short_sharp_masculin #2`) ~ -33.0dBFS(`hundreds_of_ancient_ #1`) — 20dB 편차 |
| 긴 클립 | 10~25초 8종은 발주서대로 하이라이트 · 루프 가공. 6~8초(곰 · 호랑이 · 사망 · 종 · 오라)는 발주서에 길이가 없어 자연스러운 끝(가장 센 창보다 24dB 아래로 꺼진 뒤 0.3초)에서 잘랐습니다 |
| 눈에 띈 것 | ① `razor_sharp_katana_b`(적 베임 신음)는 스펙트럼 중심 5~7kHz · 300~2400Hz 비율 7%로 **날 소리가 주**(목소리라면 60% 이상) ② `heavy_wooden_warbow_`(활 원테이크)는 당김과 발사 사이에 1.3~1.8초 무음 ③ `deep_masculine_warri #3`에는 후반부 갑옷 낙하 사건이 없고 #1(2.2~2.6초)에 있음 ④ `menacing_army_of_anc #3`(후두 구호)의 약 4초 리듬은 자기상관 0.16으로 뚜렷하지 않음 |

## 2. 전처리 공정 — `tools/r37/build_sfx.py`

### 2-1. 공정(파일마다)

1. 26Hz 2차 하이패스 → 키 그룹 EQ: 검격 220Hz HPF + 5.3kHz +2.5dB(Q 0.9 · 4~7kHz) / 돌도끼 2.3kHz +2dB(1.5~3.5kHz) / 코뿔소 · 말발굽 · 기병 돌격 78Hz +2dB(60~100Hz) + 3kHz 위 -1.5dB 셸프
2. 구간 고르기 — `trim`(앞 무음: 피크 대비 -32dBFS 또는 0.025 최초 돌파 5ms 앞 / 뒤 무음: -42dBFS 마지막 돌파 뒤 40ms) · `natural`(긴 소리) · `dense`(0.5초 RMS 창으로 가장 밀도 높은 L초) · `loop`(L초 + 0.45초 등출력 크로스페이드, 파일 앞뒤에 0.1초 주기 연장을 덧대고 루프 지점을 안쪽에 둠) · 파생 4종
3. 3ms 페이드인 · 25ms 페이드아웃(자연 끝) / 소리 중간을 끊은 자리는 120~500ms
4. 44.1kHz 폴리페이즈 리샘플 · 모노 또는 스테레오
5. RMS 정규화 → 피크 -1.0dBFS 룩어헤드 리미터(3ms · 릴리스 60ms). 리미터가 상한(타격 5dB · 그 밖 8dB)보다 많이 깎아야 하면 게인을 줄이고 미달량을 로그에 적음
6. MP3 CBR(lameenc · 품질 2). lameenc가 없으면 ffmpeg(libmp3lame)

### 2-2. 카테고리 목표(발주서의 세 단계 그대로)

| 카테고리 | 목표 RMS | 창 | 형식 |
|---|---|---|---|
| 타격(돌도끼 · 흑요석 명중 · 검격은 청음 반영 1차부터 -14.5) · 주인공 피격 · 보스 포효 · 짐승 사망 · 에밀레종 · 소총 · 권총 | -13.5 dBFS | 0.1초(타격 · 총) / 0.4초 | 모노 96~112 / 스테레오 128 |
| 스윙 · 기합 · 활 · 야수 일반(늑대 · 코뿔소) · 적 신음 · 적장 사망 · 화살비 | -15.5 | 0.1초(스윙 · 활) / 0.4초 | 모노 96~112 / 스테레오 128 |
| 기습 괴성 · 뿔피리 · 기병 돌격 | -16.0 | 0.4초 | 스테레오 128 |
| 루프(말발굽 · 후두 구호) · 함성 · 광명 오라 | -19.0 | 0.4초 | 스테레오 128 |

- **RMS의 창**: 발주서는 창을 정하지 않았습니다. 돌도끼 '퍽'처럼 수십 ms에 에너지가 몰린 소리를 0.4초 창으로 재면 피크 -1dB 제약 때문에 -22dB에서 더 올라갈 수 없어(1차 굽기에서 확인) 타격 · 스윙 · 활 · 총은 0.1초 창으로 쟀습니다. 그래도 못 미친 파일은 2-4절 표에 그대로 적었고, 돌도끼는 게임 안 재생 볼륨(1.3배)으로 보완했습니다.

### 2-3. 발주서와 다르게 한 것(이유)

| 발주서 | 한 일 | 왜 |
|---|---|---|
| `sfx_soldier_down` = `deep_masculine_warri #3` 후반부 갑옷 낙하 0.35초 | **#1**의 2.23초 사건(앞 골짜기 12dB)에서 떼어 냄 | #3은 1.2초 뒤로 비명이 그냥 줄어들 뿐 다시 커지는 사건이 없음(30ms 창 실측). 1차 굽기에서 #3의 꼬리 잡음(-70dB)을 잡아 +47dB로 올린 일이 있어 '가장 센 창보다 8dB 안 + 앞 0.6초에 10dB 골짜기' 조건을 둠 |
| `sfx_nomad_chant_loop` 4.5초 | 4.5초 그대로(리듬 주기에 맞추려 했으나 감지 세기 0.16 < 문턱 0.25) | 이음매에서 구호 리듬이 어긋날 수 있음 — 점검 페이지에서 들어 봐 주세요 |
| `sfx_bow_full` 원테이크 | 당김 → 발사 사이의 무음(#3 0.94~2.21초 · #1 2.18~3.10초)을 0.25초로 줄임 | 게임의 조준 예고가 0.7초라 1.3~1.8초 무음은 쓸 수 없음 |
| `sfx_enemy_katana_hurt` '칼 베임 신음' | 그대로 넣되 게임에서는 사람 적을 칼로 벨 때 둘에 하나, 볼륨 0.55로 절단 소리 밑에 얹음 | 실측상 날 소리가 주(1절) — 신음으로 쓰기엔 목소리 성분이 적음 |
| 루프 파일 = 4.0 · 4.5초 | 파일은 4.2 · 4.7초(앞뒤 0.1초 주기 연장) · 루프 지점 0.1~4.1 · 0.1~4.6초 | MP3 디코더의 앞머리 지연(약 25ms)이 기기마다 달라도 이음매가 어긋나지 않게 |
| 뒤 페이드아웃 15~30ms | 자연 끝은 25ms. 소리 중간을 끊은 끝(하이라이트 · 상한 컷)은 120~500ms | 중간을 25ms로 끊으면 뚝 끊김 |
| 6~8초 클립(곰 · 호랑이 · 사망 · 종 · 오라)의 길이 | 3.0~5.0초 상한(2-4절) | 발주서에 없음. 용량 상한(6.0MB)과 게임 속 길이를 보고 정함 |

### 2-4. 굽기 로그(64개 — 발주서 [작업 4]-1)

열: 원본 테이크 · 길이 전 → 후(초) · 앞 무음 제거(ms) · 게인(dB) · 리미터 최대 감소(dB) · 결과 RMS(dBFS) · 크기(KB). 전체 수치는 `tools/r37/build_sfx_log.json`.

| 키 | 원본 | 전 → 후 | 앞 컷 | 게인 | 리미터 | RMS | KB |
|---|---|---|---|---|---|---|---|
| sfx_sword_slash_01 (청음 1차) | ultra_sharp_thin_ste #3 | 2.00 → 0.66 | 114 | -5.3 | 0 | -14.5(피크 -5.3) | 8 |
| sfx_sword_slash_02 (청음 1차) | ultra_sharp_thin_ste #4 | 2.00 → 0.67 | 86 | -6.3 | 0 | -14.5(피크 -6.3) | 8 |
| sfx_sword_slash_03 (청음 1차) | ultra_sharp_thin_ste #1 | 2.00 → 0.97 | 137 | -6.8 | 0 | -14.5(피크 -6.8) | 12 |
| sfx_sword_cut_hit (청음 1차) | razor_sharp_steel_bl #4 | 2.00 → 0.54 | 304 | -3.7 | 0 | -14.5(피크 -3.7) | 7 |
| sfx_stone_axe_hit_01 | heavy_rough_stone_ax #3 | 2.00 → 1.24 | 192 | +3.0 | -4.0 | **-16.3** | 15 |
| sfx_stone_axe_hit_02 | heavy_rough_stone_ax #4 | 2.00 → 0.50 | 470 | +2.1 | -4.0 | **-16.5** | 6 |
| sfx_stone_axe_hit_03 | heavy_rough_stone_ax #2 | 2.00 → 0.60 | 130 | +4.8 | -5.0 | **-17.8** | 8 |
| sfx_stone_axe_heavy_01 | massive_prehistoric_ #2 | 3.00 → 1.94 | 89 | -3.2 | 0 | -13.5 | 24 |
| sfx_stone_axe_heavy_02 | massive_prehistoric_ #4 | 3.00 → 2.34 | 26 | -1.7 | 0 | -13.5 | 29 |
| sfx_obsidian_jab_01 | fast_tight_wooden_sp #1 | 2.00 → 0.37 | 130 | -3.9 | 0 | -15.5 | 5 |
| sfx_obsidian_jab_02 | fast_tight_wooden_sp #4 | 2.00 → 0.41 | 179 | -1.8 | 0 | -15.5 | 5 |
| sfx_obsidian_hit | razor_sharp_steel_bl #4 ×1.10 + heavy_rough_stone_ax #3 앞 80ms ×0.3 | 2.00 → 0.56 | 292 | +1.7 | -1.6 | -14.6 | 7 |
| sfx_hero_effort_light_01 | short_tight_masculin #1 | 0.49 → 0.35 | 33 | -0.6 | 0 | -15.5 | 5 |
| sfx_hero_effort_light_02 | short_tight_masculin #2 | 0.49 → 0.39 | 32 | +4.4 | -1.1 | -16.0 | 6 |
| sfx_hero_effort_light_03 | short_tight_masculin #3 | 0.49 → 0.35 | 69 | +3.2 | 0 | -15.5 | 5 |
| sfx_hero_effort_heavy_01 (청음 1차 · 0.9초까지) | brief_heavy_masculin #4 | 2.00 → 0.90 | 89 | +1.3 | -0.4 | -15.6 | 13 |
| sfx_hero_effort_heavy_02 (청음 1차 · 0.9초까지) | brief_heavy_masculin #2 | 2.00 → 0.90 | 121 | +1.1 | -0.1 | -15.5 | 13 |
| sfx_hero_barbarian_roar_01 (청음 1차 · 1.4초까지) | fierce_muscular_prim #1 | 3.00 → 1.40 | 115 | -1.1 | 0 | -15.5 | 20 |
| sfx_hero_barbarian_roar_02 (청음 1차 · 1.4초까지) | fierce_muscular_prim #4 | 3.00 → 1.40 | 138 | -1.4 | 0 | -15.5 | 20 |
| sfx_hero_hit_light_01 | short_sharp_masculin #4 | 1.00 → 0.49 | 50 | -0.2 | 0 | -13.5 | 7 |
| sfx_hero_hit_light_02 | short_sharp_masculin #2 | 1.00 → 0.35 | 54 | -0.2 | -0.5 | -13.7 | 5 |
| sfx_hero_hit_light_03 | short_sharp_masculin #1 | 1.00 → 0.41 | 63 | +2.7 | -2.8 | -14.4 | 6 |
| sfx_hero_hit_heavy_01 | heavy_breathless_mas #3 | 3.00 → 1.64 | 442 | +1.8 | -1.0 | -13.9 | 23 |
| sfx_hero_hit_heavy_02 | heavy_breathless_mas #2 | 3.00 → 2.12 | 290 | +4.5 | 0 | -13.5 | 30 |
| sfx_hero_death_01 | heroic_masculine_war #4 | 4.00 → 3.43 | 114 | -0.4 | -0.3 | -13.6 | 49 |
| sfx_hero_death_02 | heroic_masculine_war #1 | 4.00 → 3.02 | 116 | 0.0 | 0 | -13.5 | 43 |
| sfx_wolf_attack_01 | ferocious_wild_wolf_ #2 | 10.00 → 2.50 | 200 | -0.4 | 0 | -15.5 | 41 |
| sfx_wolf_attack_02 | ferocious_wild_wolf_ #4 | 10.00 → 2.50 | 150 | +2.2 | -1.0 | -15.7 | 41 |
| sfx_rhino_charge_01 | massive_furious_preh #3 | 12.00 → 3.50 | 500 | -5.5 | 0 | -15.5 | 56 |
| sfx_rhino_charge_02 | massive_furious_preh #1 | 12.00 → 3.50 | 650 | -3.7 | 0 | -15.5 | 56 |
| sfx_bear_roar_01 | enormous_angry_grizz #1 | 6.00 → 3.32 | 137 | -1.3 | 0 | -13.5 | 54 |
| sfx_bear_roar_02 | enormous_angry_grizz #2 | 6.00 → 3.04 | 1750(앞 낮은 으르렁 제외) | -3.1 | 0 | -13.5 | 49 |
| sfx_tiger_roar_01 | massive_Siberian_tig #4 | 8.00 → 4.30 | 149 | -1.6 | 0 | -13.5 | 69 |
| sfx_tiger_roar_02 | massive_Siberian_tig #3 | 8.00 → 2.46 | 1180 | -1.0 | -0.1 | -13.5 | 40 |
| sfx_beast_death | massive_wild_apex_pr #3 | 8.00 → 3.50 | 193 | -3.6 | 0 | -13.5 | 56 |
| sfx_beast_boss_death | enormous_prehistoric #1 | 8.00 → 2.96 | 367 | -0.9 | -0.2 | -13.5 | 48 |
| sfx_bow_full_01 | heavy_wooden_warbow_ #3(무음 0.94~2.21초 → 0.25초) | 4.00 → 2.43 | 116 | +2.2 | -2.9 | -16.1 | 34 |
| sfx_bow_full_02 | heavy_wooden_warbow_ #1(무음 2.18~3.10초 → 0.25초) | 4.00 → 2.88 | 77 | +3.9 | -1.7 | -16.2 | 41 |
| sfx_bow_shoot_01 | heavy_wooden_hunting #4 | 3.00 → 1.60 | 285 | +4.0 | -3.0 | **-17.3** | 23 |
| sfx_bow_shoot_02 | heavy_wooden_hunting #1 | 3.00 → 0.43 | **857** | +2.0 | 0 | -15.5 | 7 |
| sfx_bow_draw | heavy_wooden_warbow_ #3 앞 1.0초 | 4.00 → 1.00 | 116 | +2.2 | -2.9 | -16.5 | 15 |
| sfx_arrow_volley | massive_volley_of_do #4 | 6.00 → 2.68 | **1110** | -1.2 | 0 | -15.5 | 43 |
| sfx_rifle_shot_01 | vintage_early_1900s_ #4 | 4.00 → 1.15 | 0 | +1.7 | -1.7 | -14.9 | 17 |
| sfx_rifle_shot_02 | vintage_early_1900s_ #1 | 4.00 → 1.52 | 108 | +1.4 | -0.2 | -13.6 | 22 |
| sfx_pistol_shot | vintage_early_1900s_ #2 ×1.18 · 0.55초 | 4.00 → 0.55 | 4 | +6.5 | -1.0 | -14.1 | 8 |
| sfx_enemy_katana_hurt_01 (청음 1차 · 4kHz 위 -8dB) | razor_sharp_katana_b #2 | 3.00 → 0.68 | 130 | +2.9 | -2.3 | **-16.6** | 10 |
| sfx_enemy_katana_hurt_02 (청음 1차) | razor_sharp_katana_b #1 | 3.00 → 0.86 | 364 | +3.4 | -0.1 | -15.5 | 12 |
| sfx_enemy_bullet_hurt_01 | heavy_dull_bullet_im #4 | 2.00 → 0.70 | 8 | -0.6 | -0.1 | -15.5 | 10 |
| sfx_enemy_bullet_hurt_02 | heavy_dull_bullet_im #3 | 2.00 → 0.84 | 25 | +1.4 | -0.1 | -15.5 | 12 |
| sfx_boss_general_death_01 | deep_masculine_warri #3 | 4.00 → 2.88 | 72 | -3.4 | 0 | -15.5 | 47 |
| sfx_boss_general_death_02 | deep_masculine_warri #1 | 4.00 → 3.60 | 177 | -0.3 | 0 | -15.5 | 58 |
| sfx_soldier_down | deep_masculine_warri **#1** 2.23초부터 0.35초 | 4.00 → 0.35 | — | +0.3 | 0 | -15.5 | 6 |
| sfx_cavalry_hooves_loop | massive_horde_of_hun #4 8.75초부터(말발굽 주기 0.40초 × 10 = 4.0초) | 20.00 → 4.20 | 8750 | -2.5 | 0 | -19.0 | 68 |
| sfx_cavalry_charge | fierce_armored_caval #3 4.10초부터 | 15.00 → 3.50 | 4100 | +6.3 | -4.2 | **-17.7** | 56 |
| sfx_cavalry_horn | ominous_deep_ancient #3 뿔피리 시작점부터 | 12.00 → 4.00 | 423 | -4.2 | 0 | -16.0 | 65 |
| sfx_army_warcry_01 | hundreds_of_ancient_ #4 | 12.00 → 4.00 | 850 | -4.6 | 0 | -19.0 | 65 |
| sfx_army_warcry_02 | hundreds_of_ancient_ #2 | 12.00 → 4.00 | 600 | -0.2 | 0 | -19.0 | 65 |
| sfx_nomad_horde_cry_01 | terrifying_horde_of_ #2 | 20.00 → 4.50 | 700 | -4.3 | 0 | -19.0 | 73 |
| sfx_nomad_horde_cry_02 | terrifying_horde_of_ #1 | 20.00 → 4.50 | 1700 | -4.8 | 0 | -19.0 | 73 |
| sfx_nomad_chant_loop | menacing_army_of_anc #3 4.45초부터 | 25.00 → 4.70 | 4450 | -4.2 | 0 | -19.0 | 76 |
| sfx_nomad_ambush_cry_01 | sudden_chilling_noma #1 | 4.00 → 2.45 | 124 | -4.9 | 0 | -16.0 | 40 |
| sfx_nomad_ambush_cry_02 | sudden_chilling_noma #2 | 4.00 → 2.07 | 127 | -6.2 | 0 | -16.0 | 34 |
| sfx_buddha_emille_bell | giant_ancient_Korean #2(저역이 더 깊은 테이크) | 8.00 → 5.00 | 134 | +0.3 | 0 | -13.5 | 81 |
| sfx_buddha_light_aura | warm_radiant_golden_ #1 | 8.00 → 4.00 | 301 | +0.2 | 0 | -19.0 | 65 |

- 굵은 RMS = 목표에 1dB 넘게 못 미친 8개(피크 -1dB 제약 · 리미터 상한). 돌도끼 셋은 게임 재생 볼륨 1.3배로 보완했습니다. 칼 넷은 청음 반영 1차에서 봉우리를 둥글려(tanh) 피크가 -4~-7dB까지 내려왔고 리미터가 전혀 안 깎습니다 — '단단한 피크'가 사라진 수치입니다.
- 합계(청음 반영 1차 뒤): 새 MP3 64개 **2.02MB** · `assets/sfx/` 전체 **5.912MB**(기존 WAV 57개 3.7MB는 폴백으로 그대로 둠 · 발주서 상한 6.0MB 안).
- lameenc는 LAME/Xing 머리말을 쓰지 않아 디코더가 앞머리 지연(약 25ms)을 스스로 잘라 내지 못합니다 → 엔진이 디코딩 뒤 첫 소리 지점을 재서 그만큼 건너뛰고 시작합니다(4절). 실측 6.9~52.1ms.

## 3. 키 표(발주서 [작업 2] 그대로) — 어디서 나는가

| 묶음 | 키(변주 수) | 게임에서 나는 때 |
|---|---|---|
| A 무기 | `sfx_sword_slash`(3) · `sfx_sword_cut_hit` | 2~6시대 칼: 앞 타 = 검격 변주(콤보마다 피치 +1.5% · 최대 8) · 마지막 타 · 내려찍기 · 양단 = 절단 |
| | `sfx_stone_axe_hit`(3) · `sfx_stone_axe_heavy`(2) | 1시대 주먹도끼 · 간돌도끼 |
| | `sfx_obsidian_jab`(2) · `sfx_obsidian_hit`(파생) | 1시대 2단계 슴베찌르개 |
| B 주인공 | `sfx_hero_effort_light`(3) · `_heavy`(2) · `sfx_hero_barbarian_roar`(2) | 평타 1~2타 35% 짧은 기합 · 마지막 타 · 갈래 기술 · 질풍연참 100%(1시대: 짧은 75% · 강한 15% · 원시 포효 10% / 그 밖: 짧은 60% · 강한 40%) · 각성 = 1시대 원시 포효 · 그 밖 강한 기합 — 청음 반영 1차 |
| | `sfx_hero_hit_light`(3) · `_heavy`(2) · `sfx_hero_death`(2) | 피격(300ms 쿨다운 · 덕킹 안 받음) · 보스 · 중간보스 강타 = heavy + 90ms 히트스톱 · K.O. |
| C 야수 | `sfx_wolf_attack`(2) · `sfx_rhino_charge`(2) · `sfx_bear_roar`(2) · `sfx_tiger_roar`(2) | 늑대 덮치기 예고 · 코뿔소 돌진 예고 · 웨이브 등장 · 곰 지배자 등장 · 산군 등장 · 광폭화 |
| | `sfx_beast_death` · `sfx_beast_boss_death` | 곰 0.85 · 코뿔소 0.78 · (호랑이 1.06 표만) · 산군 최후 |
| D 원거리 | `sfx_bow_draw` · `sfx_bow_shoot`(2) · `sfx_bow_full`(2) · `sfx_arrow_volley` | 궁수 조준 시작 · 발사(기마 궁수는 원테이크) · 150ms 안 3발 이상이면 화살비 · 보스 부채꼴 화살 |
| | `sfx_rifle_shot`(2) · `sfx_pistol_shot`(파생) | 5시대 조총병(0.92배) · 6시대 소총병 · 김원봉 각성 소총 / 모젤(3타 · 공중 · 투척) |
| E 적 | `sfx_enemy_katana_hurt`(2) · `sfx_enemy_bullet_hurt`(2) | 사람 적을 칼로 벨 때 30% · 작게(0.4) · 총탄 명중 |
| | `sfx_boss_general_death`(2) · `sfx_soldier_down`(파생) | 중간보스 · 2~6시대 보스 최후(덕킹 35%) · 일반 병사(400ms 쿨다운 · 동시 1) |
| F 기병 | `sfx_cavalry_horn` · `sfx_nomad_ambush_cry`(2) · `sfx_cavalry_hooves_loop` · `sfx_cavalry_charge` | 기마 적이 보이면 경보(여진 · 몽골 전선은 괴성) → 말발굽 루프 접근 스윕 → 돌격 쇄도 |
| | `sfx_army_warcry`(2) · `sfx_nomad_horde_cry`(2) · `sfx_nomad_chant_loop` | 웨이브 등장(몽골 전선은 괴성) · 몽골 전선 구역 전투 중 대치 루프 |
| G 부처님 | `sfx_buddha_emille_bell` · `sfx_buddha_light_aura` | 강림(덕킹 35% · 0.6초) → 0.3초 차임(R33) → 0.5초 광명 오라 |

- 발주서의 "총 50개 내외"보다 많은 64개입니다. 발주서가 적은 키 목록(파생 4개 포함)을 하나도 빼지 않은 결과이고, 용량은 상한 안입니다.
- 새 녹음이 없어 R36 소리를 그대로 쓰는 자리: 늑대 하울링 · 깨갱, 하이에나, 곰 · 산군의 짧은 으르렁(공격 예고), 환경음 · 천둥 · 뿔나팔(전선 보스) · 범종 차임 · 2~6시대 보스 포효, 막을 때(`guard`) · 패링. 갑옷 · 방패 타격의 R35 쇠 울림(`cutArmor`)은 청음 반영 1차에서 새 베기(낮고 작게)로 바꿨고, 새 엔진을 못 쓸 때만 남습니다.

## 4. 엔진 — `createR37Sfx` (`tools/r37/r37_engine.js` → index.html)

| 발주서 | 구현 |
|---|---|
| AudioContext + AudioBuffer · HTMLAudioElement 금지 | 기존 `createSfxEngine`의 AudioContext를 같이 씁니다. 파일은 `fetch` → `decodeAudioData` → AudioBuffer |
| 마스터 체인 Source → Gain → StereoPanner → Compressor(-10dB · 4:1) → MasterGain → destination | 새 소리: Source → Gain → (StereoPanner, 있으면) → mob 또는 force 버스 → **컴프레서 -10dB · 4:1**(knee 6 · attack 3ms · release 120ms) → out(세기 K) → trunk. 기존 마스터 컴프레서(-16dB · 8:1)는 trunk 뒤에 그대로 두었습니다(R35~36 소리의 균형을 바꾸지 않으려고) |
| iOS: 첫 pointerdown/touchstart/keydown에서 resume | 기존 `unlock()`(pointerdown · keydown)이 그대로 하고, 그때 엔진을 만듭니다 |
| 시대별 Lazy preload | 첫 입력 때 공용 11키(23파일) + 1시대 11키(20파일) · 시대가 바뀔 때 그 시대 · 보스를 쓰러뜨릴 때 다음 시대(원화와 같은 때) |
| Zero GC · 60fps | 매 프레임 할당 없음. 재생 때만 BufferSource · Gain(· Panner) — Web Audio 규격상 소스는 1회용이라 이 둘은 피할 수 없고, 기존 엔진도 같습니다. 기병 · 대치 루프 관리는 12틱마다 한 번 |
| 변주 셔플 + 피치 ±5~8% | 직전 번호를 피하는 셔플 · 키별 jit(0.02~0.08) |
| 동시 상한 · 쿨다운 | 키별 `maxv`(1~3) · `cool`(ms) · 전체 24 |
| 덕킹 | `duck(level, hold, release)` — 옛 소리 · 음악 버스(`master`)와 새 엔진의 mob 버스를 함께 낮춤. force 버스(주인공 피격 · 사망 · 적장 사망 · 종 · 오라)는 안 받음 |
| 앞머리 0ms | 디코딩 뒤 첫 소리 지점(앞 120ms에서 |x| > 0.01) - 4ms를 `start(when, offset)`으로 건너뜀 |
| UI 음소거 · 볼륨 | 음소거 버튼은 그대로(trunk 게인). **SFX 볼륨 슬라이더는 원래 게임에 없습니다** → `?r37=0.5~2`(세기) · `?r37=0`(끔 · R36 소리) · `setVolume(v)` |
| `window.__SHINSI_SFX__` | `play(key, {v, r, pan, d, force, cool, maxv, jit})` · `loop(key, on, {...})` · `duck(...)` · `melee(weapon, combo, crit, pan)` · `heroHit(heavy)` · `arrowShot(pan)` · `soldierDown(pan)` · `stats`(받은 수 · 실패 · 재생 수 · 키별 · 루프 · 덕킹 · 오류 · 디코더 보정값) · `keys()`. `__RELIC_DEV.r37()`은 여기에 새/옛 타격음 횟수 · 목소리 횟수 · 기병 상태를 더해 줍니다 |

마스터 사슬(패치 뒤):

```
옛 소리 · 합성 · 환경음 · 음악 ──► master(덕킹 버스) ──┐
새 소리 ─► mob(덕킹) ─┐                               ├─► trunk(0.5 · 음소거) ─► 컴프레서 -16dB 8:1 ─► 출력
새 소리 ─► force ─────┴─► 컴프레서 -10dB 4:1 ─► out(K) ─┘
```

## 5. 게임 연동(발주서 [작업 3]-2) — 규칙 ↔ 코드

| 규칙 | 어디 · 어떻게 | 다른 점 |
|---|---|---|
| `playMeleeHit(weaponType, combo, isCrit, pan)` · 무기 자동 분기 · 콤보 피치 +1.5%/콤보(최대 8) · 크리 = 임팩트 | `r37Hit(lv, o, target)`가 `applyDamageToEnemy`의 타격음 자리(6곳) + 연참 · 내려찍기 자리(5곳)에서 `E.melee(무기, min(8, 콤보 수), 강타 여부, 좌우)`. 무기 = `heroWeaponClass`(AXE → stone_axe · SPEAR → obsidian · 그 밖 sword) | 갑옷 · 방패 타격(armor)은 청음 반영 1차부터 새 베기를 낮고 작게(0.7 · 0.93 — 그전엔 R35 `cutArmor` 쇠 울림). 콤보 수는 화면의 콤보 카운터(`stats.combo`) |
| 기합 확률 35% / 100% | `r37Effort(step, N, kind)` — 연타 단계 확정 자리 · 갈래 기술 · 질풍연참 · 각성 | 총 공격(5 · 6시대 3타)은 없음. 청음 반영 1차: 마지막 타의 100% 안에서 짧은 기합 위주(1시대 75/15/10 · 그 밖 60/40) · 원시 포효 100%는 각성 때만 · 쿨다운 6초 |
| 피격 force · 쿨다운 300ms · 보스 강타 heavy + 90ms 히트스톱 · 사망 = 말발굽 0.25초 페이드 + 음악 30% | `hurtPlayer(…, heavy)`에 넷째 인자 추가(보스 돌진 · 보스 예고 · 보스 밟기 · 곰 지배자 내려찍기 · 중간보스 예고 · 중간보스 돌진 = heavy) → `E.heroHit(heavy)` + `g.hitStop ≥ 5틱`. K.O. 자리에서 `sfx_hero_death` + 루프 끔 + `duck(0.3, 1.5, 0.6)` | |
| 병사 사망 절제: `sfx_soldier_down`만 · 400ms · 동시 1 | `r37EnemyDown(en)` — 적이 DYING이 되는 한 자리 | 시험: 4명 동시 처치 → 재생 1회 |
| 적장 사망 · 에밀레종 덕킹 35% · 0.4~0.6초 | 중간보스 0.5초 · 보스 0.6초 · 종 0.6초 | |
| 맹수 사망 음높이 1.06 · 0.85 · 0.78 | `R37_BEAST_PITCH` — 곰 · 코뿔소(호랑이 몹은 없음 · 보스 산군은 `sfx_beast_boss_death`) | 늑대 · 하이에나는 R36 깨갱 |
| 자동 화살비: 120ms 안 3회 | **150ms**(기마 중간보스의 일제 사격이 4틱 = 67ms 간격 3발이라 120ms로는 첫 · 셋째가 134ms 떨어져 안 묶임) · 화살비 뒤 0.5초 단발 없음 | 보스 부채꼴 화살은 바로 화살비(쿨다운 400ms) |
| 기병 2초 선행: 뿔피리 / 기습 괴성(pan ±0.6) → 말발굽 루프 로패스 350→18000Hz · 볼륨 0.2→1.0 | `r37Step(g)` 12틱마다: 기마 적이 보이면 경보(4시대 여진 · 몽골 전선 = 괴성, 그 밖 = 뿔피리 · 기마 적 평균 위치 쪽 pan ±0.6) + 루프 2초 스윕. 모두 쓰러지면 약 1.6초 뒤 0.6초 페이드아웃. 몽골 전선 구역 전투 중 후두 구호 루프(0.6) | **"스폰 2초 전"은 못 했습니다.** 웨이브 예약이 스폰 0.45초 전(`waveSpawnCd` 26~30틱)에만 생기고, 웨이브 구성도 스폰 때 정해집니다. 2초 전에 울리려면 웨이브를 1.5초 미뤄야 해서(게임플레이 변경) 스폰 시점 경보 + 2초 접근 스윕으로 했습니다. 기마 적이 화면 밖(±60~130px)에서 걸어 들어오는 1~2초와 겹칩니다 |
| 기병 돌격 | 기마 적 · 기마 중간보스의 돌격 시작(`resolveMobTele` charge) · 기마 보스(3시대 소정방 · 5시대 용골대) 돌진 | |
| 궁수 | 조준 시작 = 당김(0.45 · 좌우) · 발사 = `arrowShot`(기마 궁수는 원테이크) · 5시대 조총 = 소총 0.92배 · 6시대 소총 · 기관총은 R31 소리 | |
| 부처님 강림 | `startBuddhaDescent`: 종(force · 덕킹) → 0.3초 차임(R33) → 0.5초 오라 | |
| 시대 미리 받기 | `switchEraDirectly` · 보스 처치 뒤 다음 시대 원화 로드 자리 | |

모든 자리는 `새 엔진이 재생했으면 끝, 아니면 예전 소리` 꼴이라 MP3를 못 받는 기기 · `file://` · `?r37=0`에서는 R36.5-2와 같은 소리가 납니다(기능 테스트 F1).

## 6. 검증

이 PC에는 node · Playwright가 없어 **built-in 브라우저**(Chromium)에서 `python -m http.server` + 콘솔 javascript로 같은 항목을 확인했습니다(합성 keydown으로 J 연타). 같은 내용을 Playwright로 옮긴 `tools/r37/r37func.js` · `load37.js` · `run_tests.sh`는 **돌려 보지 못했습니다**(클라우드 세션에서 확인 부탁 — 10절).

### 6-1. 기능 테스트 1회 — 전부 통과 · 콘솔 에러 0 · 오디오 디코딩 에러 0

| 확인 | 결과 |
|---|---|
| A0 MANIFEST 520항목 · R37 표식 65(mp3 64 + sfx_manifest.json) · 파일 크기 그대로 받아짐 | 520 · 65 · 65개 모두 200 · bytes 일치 |
| A2 첫 입력 뒤 엔진 준비 · 공용 + 1시대 43개 디코딩 · 실패 0 | state ready · loaded 43 · failed 0 · 디코더 보정 22.4~52.1ms |
| A3 전 시대 64개 디코딩 실패 0 · 키 37개 모두 재생 | loaded 64 · failed 0 · errors [] · 37/37 true · 보정 6.9~52.1ms |
| B1 1시대 돌도끼 = stone_axe(평타 3 · 강타 1) · 창 = obsidian(스윙 2 · 명중 1) · 기합 | 새 엔진 4 · 7 / 옛 1(쇠 울림) · 원시 포효 2 · 강한 기합 1 |
| B2 피격(직접 · 늑대에게 실제로 물림) · 곰 사망음 | 피격 3회 · 곰 사망 1 |
| C1 2시대 칼 = 검격 5 · 절단 3 · 신음 3 · 기합 3+1 · 병사 4명 동시 처치 → 갑옷 낙하 **1회**(처리 4) | 통과 |
| C2 궁수 셋: 당김 6 · 발사 3 | 통과(세 궁수가 따로 쏴 화살비는 안 묶임 — D2에서 직접 확인) |
| D1 4시대 몽골 기병 둘: 경보(뿔피리 1) · 말발굽 루프 켜짐(0.77) → 돌격 1 → 모두 쓰러진 뒤 루프 꺼짐 | 통과 |
| D2 화살 3발 → 화살비 1 · 덕킹 0.35 → 1.0 · 음소거 trunk 0 → 0.5 | 통과 |
| E1 부처님 강림(에밀레종 1 · 오라 1) · 최종 보스 처치 = 적장 최후 1(덕킹) | 통과(보스 처치는 `hitBoss()`로 체력 0까지 때린 뒤) |
| F1 `?r37=0`: 엔진 idle · 타격음 R35 6회 · 새 엔진 0 | 통과 |

### 6-2. 6초 부하 — **판정 보류(측정 환경)**

같은 장면(4시대 1전선 · 척준경 Lv.5 · T3 · 원화 몹 7 · J 연타 · R33~R36.5-2와 같은 스크립트)을 이 PC의 built-in 브라우저에서 쟀습니다.

| 판 | 초당 fps | 최저 | 그리기 평균(ms) | 품질 단계 · dpr | 비고 |
|---|---|---|---|---|---|
| R36.5-2 기준선 | 54 52 48 46 42 53 | 42 | **14.11** | 1 · 1.5 | 1280×720 |
| R37 1회 | 42 34 43 49 50 49 | 34 | **14.16** | 1 · 1.5 | 1280×720 · 새 엔진 29회 재생 · 말발굽 루프 켜짐 · 디코딩 실패 0 |
| R37 2회 | 40 37 44 43 24 31 | 24 | 16.26 | 0 → 1 · 1.25 | 창 폭이 바뀌어 뷰포트가 초기화된 뒤 |

- **세 판 모두 55fps에 못 미쳤고, R37 두 회끼리의 차이(34 ↔ 24)가 기준선과의 차이보다 큽니다.** 측정 중 브라우저 창이 조정되고 페이지가 조작된 흔적이 있어(도구 기록) 이 수치로는 회귀 여부를 가릴 수 없습니다. 창을 숨긴 채 잰 첫 회차(최저 10fps · 백그라운드 페이지)는 버렸습니다.
- 게임 코드가 한 프레임을 그리는 시간(`g.perf.last` 평균)은 **14.11 ↔ 14.16ms로 같습니다.** 새 엔진은 그리기 경로를 건드리지 않고, 틱마다 하는 일은 12틱에 한 번 적 배열을 훑는 것뿐입니다(재생 때 노드 둘).
- **정식 판정은 클라우드 하네스(SwiftShader · `bash tools/r37/run_tests.sh shinsi-R37 8042 /tmp/x load` + 기준선 `shinsi-R36.5-2`)에서 해 주세요.** R36부터 여유가 없던 장면이라 여기서도 기준선과 함께 잰 숫자를 봐야 합니다.

### 6-3. 빌드 점검

`python -I tools/r37/check_build37.py shinsi-R37` → MANIFEST 520 · 디스크 520 일치 · 같은 이름 두 형식 0 · bytes 불일치 0 · assets/sfx 5.912MB(상한 안 · 청음 반영 1차 뒤) · sfx_manifest 키 37 · 파일 64 모두 있음 · 문법은 node가 없어 건너뜀 → 브라우저에서 index.html이 콘솔 에러 0으로 뜨는 것으로 대신(큰 `<script>`가 V8에서 파싱 · 실행됨).

## 7. 음향 점검 페이지

`python -I tools/r37/make_sound_check.py shinsi-R37 <아티팩트용>` → 같은 링크(QSg43hGAD1mgJALZhnyZMT)에 게시. ① 예전 소리 ↔ 새 녹음 9쌍(칼 · 돌도끼 · 창 · 곰 · 산군 · 늑대 · 코뿔소 · 사망 · 함성 · 총 · 종) ② 새로 생긴 소리 19개(주인공 목소리 · 적 · 활 · 기병 — 루프는 켜기/끄기) ③ 장면 6(기병 접근 스윕 · 돌도끼 연타 + 기합 · 칼 연타 + 신음 · 강림 · 피격 → 사망 덕킹 · 궁수 일제 사격) ④ 둔기 R35 · R36 · R37 ⑤ R36 소리 가운데 남은 것 ⑥ 배경음악 ⑦ 환경음 ⑧ 그 밖. 새 소리 세기 슬라이더 = `?r37=`.

## 8. 파일 · 도구(`tools/r37/`)

| 파일 | 내용 |
|---|---|
| `analyze_wavs.py` | 원본 실측(1절) |
| `build_sfx.py` · `build_sfx_log.json` | 전처리 파이프라인(2절) · 굽기 로그. `python -I tools/r37/build_sfx.py <WAV 폴더 또는 zip> shinsi-R37` |
| `r37_engine.js` · `r37_patch.py` | 엔진 본체 · 패치(48곳). `cp shinsi-R36.5-2/index.html shinsi-R37/index.html && python3 -I tools/r37/r37_patch.py shinsi-R37/index.html` |
| `manifest_r37.py` · `check_build37.py` | MANIFEST 65항목 병합 · 빌드 점검(node 없으면 문법 건너뜀 + sfx 용량 · sfx_manifest 확인) |
| `make_sound_check.py` · `compose37.py` | 점검 페이지 · 비교 이미지(스펙트로그램 · 루프 이음매) |
| `pack37.py` · `make_batches37.py` | 배포 묶음(전체 · 나눔 3 · 바뀐 것만 · 인수인계 · 저장소 반영 delta) · 플레이 링크 세 묶음 목록 |
| `r37func.js` · `load37.js` · `run_tests.sh` · `h.js` | Playwright 기능 · 부하(포트 8042) — **이 PC에서 미실행** |
| `run_py.ps1` | Windows용 실행 wrapper(Anaconda DLL 경로 · UTF-8 · `-I -X utf8`) |

빌드 계보: `shinsi-R36.5-2/index.html` + `r37_patch.py` = `shinsi-R37/index.html`(48곳). 원화 · 옛 효과음 · 음악은 R36.5-2와 같습니다.

## 9. 남은 점 · 못 한 것(정직하게)

1. **커밋 · 푸시를 못 했습니다.** 이 PC에 git이 없습니다(10절).
2. **6초 부하 판정 보류**(6-2절). 그리기 시간은 같지만 fps 숫자로는 가릴 수 없었습니다.
3. **Playwright 테스트 미실행**(node 없음). 브라우저 콘솔 판으로 같은 항목을 확인했고, 스크립트는 옮겨만 두었습니다.
4. **실기기(휴대폰) 미확인.** 특히 iOS Safari에서 MP3 디코딩 · 첫 입력 때 `resume()` · StereoPanner.
5. 소리는 제가 들을 수 없습니다. 수치로만 맞췄으니 점검 페이지에서 들어 보신 뒤 이름을 알려 주세요. 특히 ① 후두 구호 루프의 이음매 ② 칼 베임 '신음'(날 소리가 주) ③ 돌도끼 평타의 세기(1.3배) ④ 기합 빈도(35%).
6. 기병 2초 선행 경보는 "스폰 시점 경보 + 2초 접근 스윕"으로 바꿨습니다(5절).
7. 목표 RMS 미달 7개(2-4절 굵은 글씨).
8. 기존 WAV 57개는 그대로 두었습니다(폴백). 새 소리가 확정되면 겹치는 것(thud_* · cut_* · stab_* · bear_roar · tiger_roar · war_cry · gun_* · buddha_temple_bell 등 약 20개 · 0.8MB)을 지우고 MANIFEST에서 빼는 것이 다음 정리 후보입니다. 지시가 있을 때만.
9. 성능 여유 되찾기(타격 이펙트 · 피해 숫자 동시 개수 줄이기)는 이번에 손대지 않았습니다.

## 10. 저장소 반영 — 이 PC에서 못 한 이유와 방법

이 PC에는 git · gh · node · ffmpeg가 없고 Python도 Microsoft Store 껍데기뿐입니다(Anaconda 3.9를 찾아 썼습니다). 저장소는 공개라 `tools/`는 읽어 왔지만, 커밋 · 푸시는 할 수 없었습니다. 세 가지 가운데 골라 주세요.

| 방법 | 하는 일 | 장단점 |
|---|---|---|
| ① 클라우드 세션에서 반영 | `dist/shinsi-R37-repo-delta.zip`을 새 클라우드 세션(저장소 있음)에 올리고 안의 `APPLY-ON-CLOUD.md`대로(복사 → 풀기 → 점검 → pack37 → 커밋 · 푸시). 그 세션에서 Playwright 테스트도 돌릴 수 있음 | 가장 확실. 배포 zip은 그쪽에서 다시 만들어짐(내용 같음 · 시각만 다름) |
| ② 이 PC에 Git 설치 | `winget install Git.Git` 뒤 GitHub 로그인(브라우저 인증) → 다음 방에서 제가 clone · 복사 · 커밋 · 푸시 | 이후 라운드도 이 PC에서 가능. 설치 · 로그인은 오너가 |
| ③ 직접 | GitHub 웹에서 올리기 | 파일이 많아(tools 16 + 빌드 70 + 문서) 권하지 않음 |

## 11. 오너께 부탁드리는 것

1. **들어 보기**: 점검 페이지(https://claude.ai/artifact/QSg43hGAD1mgJALZhnyZMT) 1~3절. 거슬리는 소리 · 세기의 이름만 알려 주시면 그것만 다시 다듬습니다. 게임에서는 `?r37=0`으로 예전 소리와 바로 비교됩니다.
2. **저장소 반영 방법**(10절) 선택.
3. **부하 정식 판정**: 클라우드에서 `run_tests.sh` 부하만(R37 + R36.5-2 기준선).
4. **실기기**: 휴대폰에서 1시대 돌도끼 연타 · 4시대 기병 · 부처님 강림 한 번씩.
