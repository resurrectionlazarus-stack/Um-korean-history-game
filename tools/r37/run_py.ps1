# R37 — 이 PC(Windows · git · node · ffmpeg 없음 · Anaconda만 있음)에서 Python 도구를 돌리는 wrapper.
# Anaconda의 numpy는 conda 환경을 활성화하지 않으면 DLL을 못 찾는다 → Library\bin을 PATH 앞에 둔다.
# 가상환경 ..\.venv-r37(저장소 폴더 밖 · --system-site-packages · lameenc만 추가)의 python을 -I(격리)로 부른다.
# 사용: powershell -File tools/r37/run_py.ps1 <스크립트> [인자...]
param([Parameter(Mandatory = $true)][string]$Script, [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest)
$a = Join-Path $env:USERPROFILE "anaconda3"
$env:PATH = "$a;$a\Library\bin;$a\Scripts;$env:PATH"
# 한글 로그가 깨지지 않게(콘솔 UTF-8 · 파이썬은 -X utf8 — -I가 PYTHON* 환경 변수를 무시하므로 플래그로 준다)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$py = Join-Path (Split-Path $repo -Parent) ".venv-r37\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = Join-Path $a "python.exe" }
& $py -I -X utf8 $Script @Rest
exit $LASTEXITCODE
