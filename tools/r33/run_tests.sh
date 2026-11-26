#!/usr/bin/env bash
# R33 테스트 한 번에: 로컬 서버 켜기 → 기능 테스트(r33func.js) → 6초 부하(load33.js) → 서버 끄기
# 사용: bash tools/r33/run_tests.sh [빌드 폴더=shinsi-R33] [포트=8033] [캡처 출력=/tmp/r33test]
# 준비물: Node 22 · Playwright(크로미움 사전 설치) · tools/npm(React UMD 사본) · tools/r33/h.js
set -u
cd "$(dirname "$0")/../.."
BUILD=${1:-shinsi-R33}; PORT=${2:-8033}; OUT=${3:-/tmp/r33test}
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$BUILD" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
curl -s --retry 30 --retry-connrefused --retry-delay 1 -o /dev/null "http://127.0.0.1:$PORT/index.html" || { echo "서버 안 뜸"; exit 1; }
cd tools/r33
node r33func.js "$OUT" "$PORT"; F=$?
node load33.js "$PORT"; L=$?
echo "기능 종료코드 $F · 부하 종료코드 $L · 기능 테스트 캡처: $OUT"
