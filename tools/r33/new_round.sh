#!/usr/bin/env bash
# 새 라운드 작업 폴더 만들기: shinsi-R{이전} → shinsi-R{N}(assets · index · README 복사, 옛 인수인계 · 체크섬 제외) + tools/r{N}/(패치 틀 · 하네스)
# 사용: bash tools/r33/new_round.sh 34 [이전=33]
set -eu
cd "$(dirname "$0")/../.."
N=$1; P=${2:-33}
SRC="shinsi-R$P"; DST="shinsi-R$N"
[ -d "$SRC" ] || { echo "$SRC 없음"; exit 1; }
[ -e "$DST" ] && { echo "$DST 이미 있음"; exit 1; }
mkdir -p "$DST" "tools/r$N"
cp -r "$SRC/assets" "$DST/"
cp "$SRC/index.html" "$DST/index.html"
cp "$SRC/README-배포.txt" "$DST/"
cp tools/r33/h.js "tools/r$N/"
sed -e "s/RXX/R$N/g" -e "s/rXX/r$N/g" tools/r33/rXX_patch_template.py > "tools/r$N/r${N}_patch.py"
echo "만듦: $DST · tools/r$N/r${N}_patch.py · tools/r$N/h.js"
echo "다음: 원화 통합 → MANIFEST 병합 → 패치 작성 →"
echo "  cp $SRC/index.html $DST/index.html && python3 -I tools/r$N/r${N}_patch.py $DST/index.html && python3 -I tools/r33/check_build.py $DST"
python3 -I tools/r33/check_build.py "$DST"
