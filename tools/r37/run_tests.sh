#!/usr/bin/env bash
# R37 테스트 한 번에(클라우드 · Linux): 로컬 서버 켜기 → 기능 테스트(r37func.js) → 6초 부하(load37.js) → 서버 끄기
# 사용: bash tools/r37/run_tests.sh [빌드 폴더=shinsi-R37] [포트=8042] [캡처 출력=/tmp/r37test] [all|func|load]
#   기준선(이전 라운드)만 잴 때: bash tools/r37/run_tests.sh shinsi-R36.5-2 8042 /tmp/x load
# 준비물: Node 22 · Playwright(크로미움 사전 설치) · tools/npm(React UMD 사본) · tools/r37/h.js
# ※ 이 스크립트는 Windows PC(node 없음)에서 돌려 보지 못했다. 같은 항목을 built-in 브라우저에서 확인한 기록은 R37-handoff.md 6절.
set -u
cd "$(dirname "$0")/../.."
BUILD=${1:-shinsi-R37}; PORT=${2:-8042}; OUT=${3:-/tmp/r37test}; ONLY=${4:-all}
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$BUILD" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
curl -s --retry 30 --retry-connrefused --retry-delay 1 -o /dev/null "http://127.0.0.1:$PORT/index.html" || { echo "서버 안 뜸"; exit 1; }
cd tools/r37
F=-; L=-
if [ "$ONLY" != "load" ]; then node r37func.js "$OUT" "$PORT"; F=$?; fi
if [ "$ONLY" != "func" ]; then node load37.js "$PORT"; L=$?; fi
echo "기능 종료코드 $F · 부하 종료코드 $L · 기능 테스트 캡처: $OUT"
