#!/usr/bin/env bash
# R36.5-2 테스트 한 번에: 로컬 서버 켜기 → 기능 테스트(r36.5-2func.js) → 6초 부하(load36.5-2.js) → 서버 끄기
# 사용: bash tools/r36.5-2/run_tests.sh [빌드 폴더=shinsi-R36.5-2] [포트=8041] [캡처 출력=/tmp/r36.5-2test]
#   기준선(이전 라운드)만 잴 때: bash tools/r36.5-2/run_tests.sh shinsi-R36.5 8041 /tmp/x load
# 준비물: Node 22 · Playwright(크로미움 사전 설치) · tools/npm(React UMD 사본) · tools/r36.5-2/h.js
set -u
cd "$(dirname "$0")/../.."
BUILD=${1:-shinsi-R36.5-2}; PORT=${2:-8041}; OUT=${3:-/tmp/r36.5-2test}; ONLY=${4:-all}
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$BUILD" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
curl -s --retry 30 --retry-connrefused --retry-delay 1 -o /dev/null "http://127.0.0.1:$PORT/index.html" || { echo "서버 안 뜸"; exit 1; }
cd tools/r36.5-2
F=-; L=-
if [ "$ONLY" != "load" ]; then node r36.5-2func.js "$OUT" "$PORT"; F=$?; fi
if [ "$ONLY" != "func" ]; then node load36.5-2.js "$PORT"; L=$?; fi
echo "기능 종료코드 $F · 부하 종료코드 $L · 기능 테스트 캡처: $OUT"
