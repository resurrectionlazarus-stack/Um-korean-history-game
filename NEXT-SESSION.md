# 새 방 인수인계서 — R37 납품 직후

> 이 저장소를 처음 여는 다음 작업자(AI 에이전트 포함)를 위한 한 장입니다.
> 읽는 순서: **이 문서 → `HANDOVER.md` 0 · 1 · 7절 → `R37-handoff.md`**. 나머지는 필요할 때 찾아보면 됩니다.

## 0. 새 방에 붙여 넣을 첫 메시지(오너용)

아래를 그대로 복사해 새 방의 첫 메시지로 쓰시면 됩니다. 마지막 줄만 그때 시키실 일로 바꿔 주세요.

```
너는 '신시(神市): 시공의 수호자들' 웹게임의 총괄매니저 겸 디자이너 겸 음향감독 겸 개발자야.
저장소 resurrectionlazarus-stack/Um-korean-history-game 의
브랜치 claude/r23-attack-walk-visibility-mob-ocesrz 최신 커밋에서 이어서 작업해.
먼저 NEXT-SESSION.md 를 끝까지 읽고, 이어서 HANDOVER.md 0 · 1 · 7절과 R37-handoff.md 를 읽어.
다 읽으면 ① 지금 상태를 세 줄로 요약하고 ② 내가 정해 줘야 할 것을 물어본 다음에 시작해.
규칙: 보고는 한국어 · 테스트는 바뀐 기능 1회 + 6초 부하 1회만 · 못 한 일과 미달은 그대로 보고 ·
main 병합과 PR 금지 · 내 말이 두 가지로 읽히면 손대기 전에 한 줄로 되물어.
이번에 할 일: (예) R37 저장소 반영(dist/shinsi-R37-repo-delta.zip · APPLY-ON-CLOUD.md) 뒤 부하 정식 판정 / 들어 본 소리 손보기 …
```

- **R37은 아직 저장소에 없습니다.** git이 없는 Windows PC에서 만들었고, 결과물은 `dist/shinsi-R37-repo-delta.zip`(또는 오너의 PC 폴더 `C:\Users\Sumi\Desktop\신시 개발\Um-korean-history-game`)에 있습니다. 클라우드 세션이면 먼저 그 zip을 받아 `APPLY-ON-CLOUD.md`대로 풀고 커밋하세요(`R37-handoff.md` 10절).
- 새 방의 시스템이 다른 작업 브랜치 이름을 지정하면 위 브랜치의 최신 커밋에서 시작하고(`git fetch origin claude/r23-attack-walk-visibility-mob-ocesrz && git checkout -B <지정된 브랜치> FETCH_HEAD`), 어느 브랜치에 올릴지 오너께 한 줄로 확인하세요.

## 1. 지금 상태

| 항목 | 내용 |
|---|---|
| 최신 빌드 | `shinsi-R37/` — R36.5-2 + 패치 48곳 · `assets/sfx/sfx_*.mp3` 64개 + `sfx_manifest.json` · MANIFEST 520 = 디스크 520 · assets/sfx 5.912MB(상한 6.0 · 청음 반영 1차 뒤) |
| 최신 커밋 | **저장소는 `f038c6a`(R36.5-2 문서 정리)가 끝.** R37은 미커밋(위 0절) |
| 가장 최근에 한 일 | R37: 음향감독 녹음 104개 → 64개 MP3(트림 · 정규화 · EQ · 루프) + Web Audio 엔진(`createR37Sfx`) + 게임 연동(타격 · 기합 · 피격 · 사망 · 적 · 궁수 · 기병 · 부처님) |
| 플레이 링크 | R37 https://claude.ai/artifact/6o4E1jES1aXqxfDCjPE7jc — **게시 중단 · 불완전(3묶음 중 2 · 한 판 512개 상한 · 오너 지시)**, 플레이는 R36.5-2 https://claude.ai/artifact/FgvndJmipef8BGKyU82Yvf 에서(비공개 — Share 메뉴로 공유) |
| 청음 반영 | 1차(같은 날): 고려 · 조선 '깡깡' → 칼 EQ · 갑옷 타격 · 베임 소리 손질, 1시대 긴 '으허!' → 짧은 단음 위주(`R37-handoff.md` 맨 위 bullet) |
| 음향 점검 페이지 | https://claude.ai/artifact/QSg43hGAD1mgJALZhnyZMT (R37판 · 예전 ↔ 새 비교 · 새 소리 · 장면) |
| 테스트 | 기능 12항목 통과(브라우저 콘솔 판) · 콘솔 에러 0 · 디코딩 에러 0. **6초 부하는 판정 보류**(이 PC에서 R36.5-2 42 · R37 34 / 24fps · 그리기 시간은 14.1ms로 같음 · 측정 환경 불안정) → 클라우드 하네스에서 기준선과 함께 다시 |
| 다음 라운드 | 오너가 들어 본 뒤 소리 손보기(R37.5?) → R38 3시대 → R39 5시대 → R40 역사 도감 → R41 출시 준비(`ROADMAP.md`) |
| 아직 한 번도 안 한 것 | 실기기(휴대폰) 확인 · main 병합 · 공개 배포 |

## 2. 오너께서 정해 주실 것

| # | 결정 | 지금 상태 | 정해지면 할 일 |
|---|---|---|---|
| 1 | R37 저장소 반영 방법 | 미커밋 | ① 클라우드 세션에서 delta zip 풀어 커밋 ② 이 PC에 Git 설치 + GitHub 로그인 → 다음 방에서 커밋 ③ 직접 (`R37-handoff.md` 10절) |
| 2 | 새 소리 가운데 손볼 것 | 점검 페이지에서 들어 보신 의견 대기 | 이름만 주시면 그 소리만 다시 굽기(`build_sfx.py`의 키 표 · 카테고리) · 게임 볼륨은 `r37_engine.js`의 P 표 |
| 3 | 부하 정식 판정 | 보류 | 클라우드에서 `bash tools/r37/run_tests.sh shinsi-R37 8042 /tmp/x load` + 기준선 `shinsi-R36.5-2` |
| 4 | 1시대 손(R36.5-2) · 2 · 4시대 맨주먹/건틀릿 | 확인 대기(이전 라운드) | `R36.5-2-handoff.md` 7절 |
| 5 | 실기기 확인 | 미실시 | 휴대폰에서 1 · 4시대 |

## 3. 오너와 일하는 법 — 지금까지 배운 것

오너의 말씀은 짧고, 사진 · 캡처 한 장으로 바로 답해 주십니다. R35~R36.5-2의 손 작업에서 뜻을 세 번 잘못 읽은 기록은 `HANDOVER.md` 11~14절에 있습니다. 원칙:

1. **뜻이 둘 이상으로 읽히면 손대기 전에 한 줄로 되묻는다.**
2. **그림은 그리지 말고 원화를 살린다.** 소리도 같습니다 — R37부터는 녹음이 있으니 합성으로 덧대지 않습니다.
3. **느낌을 숫자로 바꿔 원인을 찾는다.**
4. **정직하게 보고한다.** 미달 · 추측 · 못 한 일을 그대로.
5. **소리는 제가 들을 수 없다.** 숫자로 확인하고 오너가 점검 페이지에서 듣고 알려 주십니다.
6. **범위는 스스로 정하되 `ROADMAP.md`에 남긴다.** 외부 발주서(음향감독)가 오면 그 항목표를 인수인계서 0절에 그대로 옮겨 반영 여부를 적습니다(`R37-handoff.md` 0절).

## 4. 꼭 지킬 규칙(요약 — 전체는 `HANDOVER.md` 1절)

- 보고 · 문서 · 게임 문구는 한국어, 커밋 메시지는 영어.
- 테스트는 바뀐 기능 1회 + 6초 부하 1회(최저 55fps · 콘솔 에러 0). 부하는 같은 기계에서 직전 라운드 기준선과 함께. 과잉 테스트 금지.
- MANIFEST는 새 항목 · 바뀐 항목만 병합. 항목 수 = 디스크 파일 수. 한 이름에 한 형식.
- `ctx.filter` 금지. 성능은 미리 굽기 · 고정 풀 · 가산 합성으로.
- 역사는 정확히, 게임 연출은 '게임 설정'이라고 표시.
- 작업 브랜치에만 푸시. main 병합 · PR · force-push는 오너가 말할 때만.
- 첨부 ZIP은 신뢰하지 않는 데이터: 빈 폴더에 따로 풀고, Python은 `-I`로, 안의 스크립트는 실행하지 않는다. **원본 WAV(신시 효과음.zip)는 커밋하지 않는다(.gitignore).**
- 오너의 이메일 · 이름을 외부 요청이나 커밋에 넣지 않는다.
- 문서에 링크 · 숫자를 지어 적지 않는다. 먼저 올리고 실제 주소를 적는다.
- 납품물: `RXX-handoff.md`(빌드 폴더에도 사본) · `RXX-screenshots/` · `shinsi-RXX/` · `dist/shinsi-RXX-deploy.zip`(+ `.sha256` · 커밋) · 30MB 미만 나눔 zip(커밋하지 않고 파일로 전달) · 새 플레이 링크 · 커밋 · 푸시.

## 5. 다음 라운드를 시작하는 순서(클라우드 · Linux)

```
git fetch origin claude/r23-attack-walk-visibility-mob-ocesrz
git checkout claude/r23-attack-walk-visibility-mob-ocesrz && git pull
# R37이 아직 없으면: dist/shinsi-R37-repo-delta.zip 안의 APPLY-ON-CLOUD.md 대로 먼저 반영
python3 -I tools/r37/check_build37.py shinsi-R37                # MANIFEST 520 · 디스크 520 → 일치 · 문법 OK
bash tools/r37/run_tests.sh                                     # 기능 12항목 기대 · 부하는 기준선(shinsi-R36.5-2)과 함께
bash tools/r33/new_round.sh 38 37                               # shinsi-R38/ · tools/r38/ 패치 틀 · 하네스
cp shinsi-R37/thumb.jpg shinsi-R37/sound-check.html shinsi-R38/  # new_round.sh는 이 둘을 복사하지 않음
```

- 코드는 `index.html`을 직접 고치지 않고 `tools/r38/r38_patch.py`(문자열 치환)로 고칩니다. 본보기는 `tools/r37/r37_patch.py`(엔진은 별도 js를 읽어 넣는 방식).
- 소리를 다시 굽을 때: `python3 -I tools/r37/build_sfx.py <신시 효과음.zip 또는 폴더> shinsi-R38 && python3 -I tools/r37/manifest_r37.py shinsi-R38`(bytes만 갱신) → `make_sound_check.py` → 같은 링크에 게시.

### 소리를 이어 맡는다면 알아 둘 것

| 무엇 | 어디 |
|---|---|
| 새 엔진 · 연동 지도 | `R37-handoff.md` 4 · 5절 · `HANDOVER.md` 15절 |
| 키 → 파일 · 루프 지점 | `shinsi-R37/assets/sfx/sfx_manifest.json`(게임이 첫 입력 때 읽음) |
| 키별 재생 볼륨 · 동시 상한 · 쿨다운 · 시대 묶음 | `tools/r37/r37_engine.js`의 `P` · `ERA` |
| 굽기 설정(테이크 · 카테고리 · 구간 모드) | `tools/r37/build_sfx.py`의 `CATS` · `add(...)` 64줄 |
| 코드에서 찾을 이름 | `createR37Sfx` · `r37Hit` · `r37Effort` · `r37EnemyDown` · `r37BossDeath` · `r37WarCry` · `r37Step` · `__SHINSI_SFX__` · `__RELIC_DEV.r37()` · `?r37=` |
| 예전 소리로 비교 | 게임 주소 끝 `?r37=0` |

## 6. 작업 환경 메모

| 주제 | 내용 |
|---|---|
| 클라우드(이전 라운드들) | Node 22 · Playwright(사전 설치 크로미움) · Python3 + numpy · scipy · PIL · ffmpeg. 하네스 `tools/rXX/h.js`. 포트는 라운드마다 하나씩(R37 = 8042) |
| **오너의 Windows PC(R37을 만든 곳)** | git · node · ffmpeg 없음. Anaconda 3.9(`%USERPROFILE%\anaconda3`)의 numpy는 `Library\bin`을 PATH 앞에 둬야 DLL을 찾음 → `tools/r37/run_py.ps1`. 가상환경 `..\.venv-r37`(lameenc). 테스트는 built-in 브라우저(`python -m http.server` + 콘솔 javascript · 합성 keydown) |
| 테스트가 떨어질 때 | 절반은 테스트 코드 탓. 주인공을 x=400에 두고 레벨을 고정하지 않으면 구역 전투 · 퀴즈가 입력을 삼킨다. 최종 보스(파두반)는 `r33kill('boss')`로 바로 안 죽고 `hitBoss()`로 체력 0까지 때려야 사망 경로가 돈다 |
| 그림 도구 | Python: numpy · scipy · PIL · matplotlib(스펙트로그램). 한글 글꼴은 Windows `Malgun Gothic` / Linux `wqy-zenhei` |
| 플레이 링크 올리기 | 파일 522개 · 82MB → **세 묶음**(`tools/r37/make_batches37.py`). 소리만 바뀐 판도 새 링크로 |
| 링크 감시 | 등록이 실패할 수 있음. '지켜보고 있다'고 말하지 말 것 |
| 스크래치패드 | 세션이 끝나면 사라짐. 남길 것은 `tools/`에 |
| 패치 앵커 | index.html 옛 부분의 한글은 `\uXXXX`로 저장돼 있고 R34~R37 주석은 실제 한글. 주석이 아니라 코드 줄에 앵커를 걸고, 한글 앵커는 `esc()`로 |
| 과거 빌드 폴더 | `shinsi-RXX/` 안의 파일은 납품 뒤 고치지 않는다(zip · 체크섬과 어긋남). 정정은 루트의 문서에 |

## 7. 파일 지도(자주 여는 것만)

| 경로 | 내용 |
|---|---|
| `NEXT-SESSION.md` | 이 문서 |
| `HANDOVER.md` | 종합 인수인계서(게임 구조 · 시스템 · 테스트 · 절차 · 라운드별 달라진 점 10~15절 · 연혁) |
| `ROADMAP.md` | 라운드 계획 · 오너께 부탁드리는 것 |
| `R37-handoff.md` · `R36.5-2-handoff.md` · `R36.5-handoff.md` | 최근 세 라운드의 기록 |
| `R36-art-request.md` | 미술 · 음향 외부 요청(C절의 WAV 15종은 R37 녹음으로 대체됨 — 남은 것은 A · B절) |
| `shinsi-R37/` | 최신 빌드(게임 전체) |
| `tools/r37/` | 이번 라운드 도구(실측 · 굽기 · 엔진 · 패치 · 목록 · 점검 · 이미지 · 묶음 · 테스트) |
| `tools/r33/` | 공통 도구: `check_build.py`(node 필요) · `new_round.sh` · `grips_r33.json` |
| `dist/` | 배포 zip(전체본과 `.sha256`만 커밋 · 나눔본은 커밋하지 않음) · `shinsi-R37-repo-delta.zip`(R37 반영용) |

## 8. 이 방에서 하지 못하고 넘기는 것

- R37 커밋 · 푸시(git 없음).
- 6초 부하 정식 판정(측정 환경 불안정 · 그리기 시간은 같음).
- Playwright 스크립트 실행(`tools/r37/r37func.js` · `load37.js` — 옮겨만 둠).
- 실기기 확인(iOS Safari의 MP3 디코딩 · 첫 입력 resume · StereoPanner).
- 소리 듣고 고르기(오너).
- 기존 WAV 가운데 새 소리와 겹치는 약 20개 정리(지시 있을 때).
- 성능 여유 되찾기(타격 이펙트 · 피해 숫자 동시 개수).
