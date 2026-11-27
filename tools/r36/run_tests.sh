#!/usr/bin/env bash
# R36 테스트 한 번에: 로컬 서버 켜기 → 기능 테스트(r36func.js) → 6초 부하(load36.js) → 서버 끄기
# 사용: bash tools/r36/run_tests.sh [빌드 폴더=shinsi-R36] [포트=8039] [캡처 출력=/tmp/r36test]
# 준비물: Node 22 · Playwright(크로미움 사전 설치) · tools/npm(React UMD 사본) · tools/r36/h.js
set -u
cd "$(dirname "$0")/../.."
BUILD=${1:-shinsi-R36}; PORT=${2:-8039}; OUT=${3:-/tmp/r36test}
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$BUILD" >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
curl -s --retry 30 --retry-connrefused --retry-delay 1 -o /dev/null "http://127.0.0.1:$PORT/index.html" || { echo "서버 안 뜸"; exit 1; }
cd tools/r36
node r36func.js "$OUT" "$PORT"; F=$?
node load36.js "$PORT"; L=$?
echo "기능 종료코드 $F · 부하 종료코드 $L · 기능 테스트 캡처: $OUT"
