# R26 도구 — 리페인트 점검 · 손 위치 재측정 · 검증

- `hm.json` · `cjg.json` — 해모수 · 척준경 손 위치 표 `{동작: [쥔 x, 쥔 y, 칼 각도, 뒤집기]}` (index.html의 `R26_HM_FRAMES` · `R26_CJG_FRAMES`와 같은 값)
- `r26_inspect.py ROOT R25_DIR` — 리페인트 묶음(ROOT/p1 · p2)의 크기 · 형식 · 투명 · 파일명 1:1 점검
- `r26_fist.py BODY_DIR PREFIX` — 상체 띠에서 앞 팔 끝(주먹) 자동 후보
- `r26_grid.py BODY_DIR PREFIX OUT 동작...` — 원본 좌표 격자 확대(주먹 위치 직접 읽기)
- `r26_preview2.py TABLE BODY_DIR PREFIX WEAPON OUT` — 표대로 칼을 얹은 22동작 합성 시트
- `r26func.js` — R26 수정 항목 기능 테스트(shinsi-R26을 `python3 -m http.server 8026`으로 띄운 뒤), `load25.js 8026` — 6초 부하 1회
- `cap25.js r25|r26` · `compose26.py` — 비교 이미지 캡처 · 합성 (h.js = Playwright 하네스, React는 로컬 npm 사본으로 돌림)
- 묶음 파일 이름은 받은 그대로 다루고, 압축은 각각 빈 폴더에 풀어 점검했습니다(실행 파일 없음).
