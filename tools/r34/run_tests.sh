#!/usr/bin/env bash
# R34 테스트 한 번에: 로컬 서버 켜기 → 기능 테스트(r34func.js) → 6초 부하(load34.js) → 서버 끄기
# 사용: bash tools/r34/run_tests.sh [빌드 폴더=shinsi-R34] [포트=8037] [캡처 출력=/tmp/r34test]
# 준비물: Node 22 · Playwright(크로미움 사전 설치) · tools/npm(React UMD 사본) · tools/r34/h.js
set -u
cd "$(dirname "$0")/../.."
BUILD=${1:-shinsi-R34}; PORT=${2:-8037}; OUT=${3:-/tmp/r34test}
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$BUILD" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
curl -s --retry 30 --retry-connrefused --retry-delay 1 -o /dev/null "http://127.0.0.1:$PORT/index.html" || { echo "서버 안 뜸"; exit 1; }
cd tools/r34
node r34func.js "$OUT" "$PORT"; F=$?
node load34.js "$PORT"; L=$?
echo "기능 종료코드 $F · 부하 종료코드 $L · 기능 테스트 캡처: $OUT"
