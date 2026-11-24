# R25 검증 도구

- `h.js` — Playwright 공용 하네스(cdnjs React 요청을 로컬 npm 사본 `../npm/react-18.3.1` · `react-dom-18.3.1`로 돌려줌 — 경로는 환경에 맞게 수정).
- `r25func.js` — 수정 항목 기능 테스트 1회(`http://127.0.0.1:8025/index.html`, shinsi-R25 폴더를 `python3 -m http.server 8025`로 띄운 뒤 실행).
- `load25.js` — 핵심 전투 6초 부하 1회(`node load25.js 8025`).
- `cap25.js` — 비교 이미지 원본 캡처(`node cap25.js r25` · `node cap25.js r24` — R24는 8024 포트), `compose25.py` — 라벨 합성(문천역 정흑체).
