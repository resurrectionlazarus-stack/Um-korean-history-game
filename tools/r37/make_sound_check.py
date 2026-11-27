#!/usr/bin/env python3
"""R37 음향 점검 페이지(sound-check.html) 만들기 — R36 페이지(tools/r36/make_sound_check.py)에 R37 실제 녹음 효과음 64개를 맨 위에 더한다.
① 예전(R35 · R36 합성) ↔ 새 녹음 비교 줄 ② 새로 생긴 소리(주인공 목소리 · 적 · 활 · 기병 · 부처님) ③ 장면(기병 접근 스윕 · 연타 + 기합 · 강림 · 피격 → 사망 덕킹)
④ 그 아래는 R36 페이지 그대로(둔기 비교 · 짐승 목소리 · 장면 · 칼 · 창 · 배경음악 · 환경음 · 그 밖).
볼륨 · 음높이는 게임과 같다(새 엔진 P 표의 v · 마스터 0.5 · 컴프레서 -16dB 8:1 · 새 소리는 자기 컴프레서 -10dB 4:1을 거침 · 디코더 앞머리 지연 보정도 같음).
사용: python -I tools/r37/make_sound_check.py <빌드 폴더> [아티팩트 게시용 출력 html]"""
import json
import os
import re
import sys

root = sys.argv[1]
s = open(os.path.join(root, "index.html"), encoding="utf-8").read()
sm = json.load(open(os.path.join(root, "assets", "sfx", "sfx_manifest.json"), encoding="utf-8"))


def table(name):
    m = re.search(r"const " + name + r" = (\{[^}]*\});", s)
    return json.loads(re.sub(r"(\w+):", r'"\1":', m.group(1)))


def unesc(t):
    return re.sub(r"\\u([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), t)


SMP, VOL, AMB, AVOL = table("SMP"), table("SMP_VOL"), table("AMB"), table("AMB_VOL")
bt = re.search(r"const R36_BEAST = (\{.*?\n    \});", s, re.S).group(1)
BEAST = json.loads(re.sub(r"(\w+):", r'"\1":', bt))
# 새 엔진의 키별 재생 볼륨(v) — createR37Sfx 안 P 표
PV = {m.group(1): float(m.group(2)) for m in re.finditer(r"(sfx_[a-z_]+): \{ v: ([\d.]+)", s)}
bm = re.search(r"var R35_BGM = \{(.*?)\n  \};", s, re.S).group(1)
BGM = []
DESC = {1: "뼈피리 · 돌 타악 · 통나무북 · 낮은 합창", 2: "훈 · 공후 · 청동 방울 · 큰북 · 제의 합창", 3: "가야금 · 거문고 · 대금 · 장구 · 북 (자진모리)",
        4: "피리 · 해금 · 거문고 · 편종 · 범종 · 장구 (휘모리)", 5: "태평소 · 나발 · 꽹과리 · 장구 · 북 · 징 (대취타 + 풍물)", 6: "군악대: 트럼펫 · 호른 · 튜바 · 피콜로 · 작은북"}
ERA = {1: "1 구석기 · 신석기", 2: "2 고조선", 3: "3 삼국", 4: "4 고려", 5: "5 조선", 6: "6 대한제국 · 광복"}
for m in re.finditer(r'(\d): \{ f: "([^"]+)", t: "([^"]+)", a: \[([\d.]+), ([\d.]+)\], b: \[([\d.]+), ([\d.]+)\] \}', bm):
    e = int(m.group(1))
    BGM.append([e, m.group(2), unesc(m.group(3)), float(m.group(4)), float(m.group(5)), float(m.group(6)), float(m.group(7)), DESC[e], ERA[e]])
TAIL = float(re.search(r"var R35_BGM_TAIL = ([\d.]+);", s).group(1))
LAB = {"slashLight": "돌진 베기", "breath": "호흡 피니시", "parryCounter": "패링 카운터", "relicAwaken": "유물 각성", "killcam": "킬캠 슬로우", "missionGong": "미션 성공 징", "bombBlast": "의열단 폭탄",
       "buddhaBell": "부처님의 가호 범종(R33)", "buddhaChime": "부처님의 가호 차임", "dragonRoar": "4시대 청룡", "gunPistol": "6시대 모젤 권총(R31)", "gunRifle": "6시대 소총(R31)", "thunder1": "가까운 벼락", "thunder2": "먼 천둥", "warHorn": "전선 보스 뿔나팔"}
ALAB = {"rain": "폭우 — 4시대 1전선 거란", "blizzard": "눈보라 — 2전선 여진 · 5시대 2막 설원(약하게)", "wind": "황야 바람 — 3전선 몽골 · 1시대 빙하기 · 6시대 폐허(약하게)", "fire": "화염 — 4전선 개경 · 3시대 전장(약하게)"}
VOICE = {"wolfHowl", "wolfSnarl", "wolfYelp", "hyenaCackle", "bearRoar", "bearGrowl", "rhinoSnort", "beastGroan", "tigerRoar", "tigerSnarl", "warCry"}
HITS = {"cutLight1", "cutLight2", "cutLight3", "cutHeavy", "cutSever", "cutArmor", "cutFlurry", "thudHit1", "thudHit2", "thudHeavy", "thudCrush", "stab1", "stab2", "whooshBlade", "whooshHeavy"} | VOICE
OLD = {"rockHit1": ["rock_hit_1", 0.84], "rockHit2": ["rock_hit_2", 0.84], "rockHeavy": ["rock_heavy", 0.98], "rockCrush": ["rock_crush", 1.0]}
NAME = {"cutLight1": "베기 1", "cutLight2": "베기 2", "cutLight3": "베기 3", "cutHeavy": "강타", "cutSever": "양단", "cutArmor": "쇠 울림", "cutFlurry": "연참",
        "rockHit1": "R35 바위 타격 1", "rockHit2": "R35 바위 타격 2", "rockHeavy": "R35 바위 강타", "rockCrush": "R35 내려찍기",
        "thudHit1": "R36 퍽 1", "thudHit2": "R36 퍽 2", "thudHeavy": "R36 묵직한 퍽", "thudCrush": "R36 내려찍기", "stab1": "찌르기 1", "stab2": "찌르기 2", "whooshBlade": "칼 바람", "whooshHeavy": "둔기 바람",
        "bearRoar": "R36 곰 포효", "tigerRoar": "R36 호랑이 포효", "rhinoSnort": "R36 코뿔소 콧김", "wolfSnarl": "R36 늑대 으르렁", "beastGroan": "R36 짐승 신음", "warCry": "R36 함성",
        "gunPistol": "R31 모젤", "gunRifle": "R31 소총", "buddhaBell": "R33 범종"}
# ───────── R37: 새 녹음 — 키 묶음(키 → 변주 파일은 sfx_manifest.json에서) ─────────
# 비교 줄: [제목, 설명, [예전 키...], [새 키...]]
CMP37 = [
    ["칼 — 베기 · 절단", "2~6시대 주인공의 칼. 연타 앞 타 = 검격 셋 변주(피치 ±7% · 콤보마다 +1.5%) · 마지막 타 · 양단 = 절단 타격. [청음 반영] 4~7kHz 부스트를 빼고 5kHz 위를 깎고 봉우리를 둥글림 · 갑옷 · 방패 타격도 R35 쇠 울림 대신 이 베기를 낮고 작게", ["cutLight1", "cutLight2", "cutHeavy", "cutArmor"], ["sfx_sword_slash", "sfx_sword_cut_hit"]],
    ["돌도끼 — 평타 · 강공격", "1시대 주먹도끼 · 간돌도끼. '퍽' 셋 변주 · 강공격 '콰직' 둘(1.5~3.5kHz +2dB · 재생 볼륨 1.3배)", ["thudHit1", "thudHit2", "thudHeavy"], ["sfx_stone_axe_hit", "sfx_stone_axe_heavy"]],
    ["슴베찌르개 — 스윙 · 명중", "1시대 2단계. 직선 스윙 둘 · 명중 = 검격 #4 피치 +10% + 돌도끼 어택 80ms(파생)", ["stab1", "stab2"], ["sfx_obsidian_jab", "sfx_obsidian_hit"]],
    ["동굴 곰 · 산군 — 포효", "웨이브 등장 · 보스 등장 · 광폭화. 새 녹음은 스테레오", ["bearRoar", "tigerRoar"], ["sfx_bear_roar", "sfx_tiger_roar"]],
    ["늑대 · 코뿔소 — 덮치기 · 돌진", "공격 예고(덮치기 직전) · 웨이브 등장", ["wolfSnarl", "rhinoSnort"], ["sfx_wolf_attack", "sfx_rhino_charge"]],
    ["짐승 — 쓰러짐", "공용 사망음 한 종을 곰 0.85 · 코뿔소 0.78 · 호랑이 1.06으로 분기. 보스 산군 = 최후 붕괴", ["beastGroan"], ["sfx_beast_death", "sfx_beast_boss_death"]],
    ["병사들 — 함성", "웨이브 등장. 몽골 전선은 북방 기병의 괴성", ["warCry"], ["sfx_army_warcry", "sfx_nomad_horde_cry"]],
    ["6시대 — 모젤 · 소총", "권총 = 소총 #2 피치 +18% · 0.55초(파생). 5시대 조총 적은 소총을 0.92배로", ["gunPistol", "gunRifle"], ["sfx_pistol_shot", "sfx_rifle_shot"]],
    ["부처님의 가호 — 종 · 광명", "에밀레종(저역 맥놀이가 깊은 #2) → 0.5초 뒤 광명 오라. 차임(R33)은 그대로", ["buddhaBell"], ["sfx_buddha_emille_bell", "sfx_buddha_light_aura"]],
]
# 새로 생긴 소리(예전에 없던 것): [제목, 설명, [[버튼 이름, 언제 나나, 키, 음높이, 볼륨 배율], ...]]
NEW37 = [
    ["주인공 목소리", "지금까지 없던 소리입니다. [청음 반영] 짧은 단음 위주: 평타 1~2타 35% 짧은 기합 · 마지막 타 = 1시대 짧은 75% / 강한 15% / 원시 포효 10%(6초 쿨다운) · 그 밖 시대 짧은 60% / 강한 40% · 각성 = 1시대 원시 포효 · 그 밖 강한 기합. 강한 기합은 0.9초 · 포효는 1.4초까지만.", [
        ["짧은 기합", "평타(35%) · 마지막 타(1시대 75%)", "sfx_hero_effort_light", 1, 1], ["강한 기합", "마지막 타(1시대 15% · 그 밖 40%) · 각성(2~6시대)", "sfx_hero_effort_heavy", 1, 1], ["원시 포효", "1시대 각성 · 마지막 타 10%", "sfx_hero_barbarian_roar", 1, 1],
        ["피격", "맞을 때(300ms 쿨다운 · 전장 소음을 뚫고)", "sfx_hero_hit_light", 1, 1], ["강타 피격", "보스 · 중간보스의 강타(+90ms 히트스톱)", "sfx_hero_hit_heavy", 1, 1], ["사망", "K.O.(말발굽 멈춤 · 음악 30%로)", "sfx_hero_death", 1, 1]]],
    ["적 — 베임 · 총탄 · 쓰러짐 · 적장 최후", "사람 적을 칼로 베면 셋에 하나 베임 소리를 작게(실측상 날 소리가 주 — [청음 반영] 4kHz 위 -8dB · 볼륨 0.4). 병사 쓰러짐은 갑옷 낙하 0.35초만(400ms 쿨다운 · 동시 1 — 비명 스팸 없음).", [
        ["칼 베임", "사람 적을 칼로 벨 때(30%)", "sfx_enemy_katana_hurt", 1, 1], ["총탄 피격", "6시대 모젤 · 소총 명중", "sfx_enemy_bullet_hurt", 1, 1], ["병사 쓰러짐", "일반 병사 처치", "sfx_soldier_down", 1, 1], ["적장 최후", "중간보스 · 시대 보스(덕킹 35%)", "sfx_boss_general_death", 1, 1]]],
    ["활 · 화살비", "궁수 조준 시작 = 당김(작게 · 좌우) · 발사 = 단발. 150ms 안 3발 이상이면 단발을 끊고 화살비 한 번. 기마 궁수는 전투 활 원테이크(무음 1.3초를 0.25초로 줄임).", [
        ["당김", "조준 시작", "sfx_bow_draw", 1, 1], ["단발", "발사", "sfx_bow_shoot", 1, 1], ["전투 활 원테이크", "기마 궁수", "sfx_bow_full", 1, 1], ["화살비", "일제 사격 · 보스 부채꼴 화살", "sfx_arrow_volley", 1, 1]]],
    ["기병 · 대치", "기마 적이 보이면 경보(뿔피리 / 여진 · 몽골 전선은 기습 괴성) → 말발굽 루프를 로패스 350→18000Hz · 0.2→1.0으로 2초 열어 접근감. 몽골 전선 구역 전투 중 후두 구호가 낮게 깔립니다.", [
        ["뿔피리", "기병 경보(3시대 · 4시대 1전선 · 5시대)", "sfx_cavalry_horn", 1, 1], ["기습 괴성", "기병 경보(여진 · 몽골 전선)", "sfx_nomad_ambush_cry", 1, 1], ["돌격 쇄도", "기마 적 · 기마 보스의 돌격", "sfx_cavalry_charge", 1, 1],
        ["말발굽 루프 켜기/끄기", "기마 적이 있는 동안(끝과 처음이 이어짐)", "loop:sfx_cavalry_hooves_loop", 1, 1], ["후두 구호 루프 켜기/끄기", "몽골 전선 대치", "loop:sfx_nomad_chant_loop", 1, 1]]],
]
NEWNAME = {"sfx_sword_slash": "검격", "sfx_sword_cut_hit": "절단 타격", "sfx_stone_axe_hit": "돌도끼 퍽", "sfx_stone_axe_heavy": "돌도끼 콰직", "sfx_obsidian_jab": "흑요석 스윙", "sfx_obsidian_hit": "흑요석 명중",
           "sfx_bear_roar": "곰 포효", "sfx_tiger_roar": "산군 포효", "sfx_wolf_attack": "늑대 덮치기", "sfx_rhino_charge": "코뿔소 돌진", "sfx_beast_death": "짐승 사망", "sfx_beast_boss_death": "야수 보스 붕괴",
           "sfx_army_warcry": "정규군 함성", "sfx_nomad_horde_cry": "북방 기병 괴성", "sfx_pistol_shot": "모젤", "sfx_rifle_shot": "소총", "sfx_buddha_emille_bell": "에밀레종", "sfx_buddha_light_aura": "광명 오라"}
snd = {k: [SMP[k], VOL.get(k, 0.7)] for k in SMP}
snd.update(OLD)
new = {k: {"files": v["files"], "v": PV.get(k, 1), "loop": v.get("loop")} for k, v in sm["keys"].items()}
data = {"snd": snd, "name": NAME, "newname": NEWNAME, "new": new, "cmp37": CMP37, "new37": NEW37, "bgm": BGM, "tail": TAIL, "beast": BEAST,
        "smp": [[k, SMP[k], VOL.get(k, 0.7), LAB.get(k, k)] for k in SMP if k not in HITS],
        "amb": [[k, AMB[k], AVOL.get(k, 0.25), ALAB.get(k, k)] for k in AMB],
        "voices36": [["늑대 · 하이에나 (R36)", "깨갱 · 낄낄 · 하울링은 R36 소리 그대로", [["하울링", "웨이브 등장", "wolfHowl", 1, 0.9], ["깨갱", "쓰러질 때", "wolfYelp", 1, 0.9], ["낄낄", "하이에나 등장", "hyenaCackle", 1, 0.9], ["곰 으르렁", "내려치기 직전(R36)", "bearGrowl", 1, 1], ["산군 으르렁", "돌진 직전(R36)", "tigerSnarl", 1, 1]]]]}
HEAD = """<title>신시 음향 점검 — R37</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
  :root { color-scheme: dark; --bg: #0f1218; --card: #1a1f2a; --line: #2c3444; --ink: #e8e6df; --dim: #9aa3b5; --gold: #fbbf24; --new: #38bdf8; --old: #6b7385; --code: #0b0d12;
    --font: system-ui, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif; }
  @media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) { color-scheme: light; --bg: #eef0f3; --card: #ffffff; --line: #cfd5de; --ink: #161a22; --dim: #586174; --gold: #9a5b00; --new: #0b6aa8; --old: #8a93a5; --code: #e3e7ed; } }
  :root[data-theme="light"] { color-scheme: light; --bg: #eef0f3; --card: #ffffff; --line: #cfd5de; --ink: #161a22; --dim: #586174; --gold: #9a5b00; --new: #0b6aa8; --old: #8a93a5; --code: #e3e7ed; }
  * { box-sizing: border-box; }
  body { margin: 0; padding-block: 16px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); background: var(--bg); color: var(--ink); font: 15px/1.5 var(--font); }
  main { max-width: 760px; margin: 0 auto; }
  h1 { font-size: 20px; margin: 4px 0; color: var(--gold); text-wrap: balance; }
  h2 { font-size: 16px; margin: 26px 0 6px; color: var(--ink); font-weight: 700; }
  h3 { font-size: 14px; margin: 0 0 2px; font-weight: 700; }
  p { margin: 4px 0 10px; color: var(--dim); font-size: 13px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(220px, 100%), 1fr)); gap: 8px; }
  .row3 { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(150px, 100%), 1fr)); gap: 6px; }
  .card { border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; margin: 8px 0; background: color-mix(in srgb, var(--card) 55%, transparent); }
  .card p { margin: 0 0 8px; font-size: 12px; }
  .lane { font-size: 11px; color: var(--dim); margin: 6px 0 4px; letter-spacing: .02em; }
  button { width: 100%; min-width: 0; text-align: left; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: var(--card); color: var(--ink); font: inherit; cursor: pointer; }
  button small { display: block; color: var(--dim); font-size: 11px; overflow-wrap: anywhere; }
  button.on { border-color: var(--gold); box-shadow: 0 0 0 1px var(--gold) inset; }
  button.new { border-color: var(--new); }
  button.old { border-color: var(--old); border-style: dashed; }
  button:focus-visible, input:focus-visible { outline: 2px solid var(--gold); outline-offset: 2px; }
  button:active { transform: translateY(1px); }
  @media (prefers-reduced-motion: reduce) { button:active { transform: none; } }
  .row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin: 8px 0; }
  input[type=range] { flex: 1; min-width: 160px; accent-color: var(--gold); }
  .num { font-variant-numeric: tabular-nums; }
  code { background: var(--code); padding: 1px 6px; border-radius: 6px; color: var(--gold); }
  .note { border-left: 3px solid var(--gold); padding: 6px 10px; background: color-mix(in srgb, var(--card) 55%, transparent); border-radius: 0 8px 8px 0; color: var(--ink); }
</style>
"""
BODY = """<main>
<h1>신시 R37 음향 점검 — 실제 녹음 효과음</h1>
<p>버튼을 누르면 게임과 같은 볼륨 비율로 들립니다. 이번 라운드에는 음향감독이 준 녹음 104개 가운데 64개를 골라 다듬어 넣었습니다(앞 무음 0ms · 카테고리별 음량 통일 · 44.1kHz MP3). 파란 테두리 = 새 녹음, 점선 = 예전 합성 소리(비교용). 게임 주소 끝에 <code>?r37=0</code>을 붙이면 예전 소리로 플레이됩니다(비교용), <code>?r37=0.5~2</code>는 새 소리 세기입니다.</p>
<p class="note">만든 쪽은 귀로 들어 볼 수 없어 수치로만 맞췄습니다. 거슬리는 소리 · 너무 크거나 작은 소리의 이름을 알려 주시면 그것만 다시 다듬습니다. 휴대폰 스피커로도 한 번 들어 봐 주세요.</p>
<p class="note">청음 반영 1차: ① 고려 · 조선 구간의 '깡깡' — 칼 소리의 4~7kHz 부스트를 빼고 5kHz 위를 깎고 봉우리를 둥글렸습니다. 갑옷 · 방패 타격은 R35 쇠 울림(점선 '쇠 울림') 대신 베기를 낮고 작게, 베임 소리는 작고 드물게. ② 1시대 긴 '으허!' — 강한 기합 0.9초 · 원시 포효 1.4초로 줄이고 마지막 타도 짧은 단음 위주(원시 포효는 각성 때와 10%).</p>

<h2>1. 예전 소리 ↔ 새 녹음</h2>
<div id="cmp37"></div>

<h2>2. 새로 생긴 소리</h2>
<div id="new37"></div>
<div class="row"><label for="rk">새 소리 세기</label><input id="rk" type="range" min="0" max="2" step="0.05" value="1"><span id="rkv" class="num">×1.00</span></div>
<p>마음에 드는 세기를 찾으면 게임 주소 끝에 <code id="rhint">?r37=1</code> 을 붙여 같은 세기로 플레이할 수 있습니다.</p>

<h2>3. 장면으로 들어 보기(R37)</h2>
<div class="grid">
  <button id="s37cav" type="button" class="new">기병이 다가온다<small>기습 괴성 → 말발굽이 멀리서(둔탁) 가까이(선명) → 돌격 쇄도</small></button>
  <button id="s37axe" type="button" class="new">돌도끼 연타 + 기합<small>퍽 ×3(피치 상승) + 콰직 + 짧은 기합(마지막 타 75%)</small></button>
  <button id="s37swd" type="button" class="new">칼 연타 + 적의 베임<small>검격 ×3 + 절단 + 베임(작게) + 병사 쓰러짐</small></button>
  <button id="s37arm" type="button" class="new">갑옷 · 방패 타격 — 예전 ↔ 지금<small>R35 쇠 울림 ×2 → 새 베기 낮고 작게 ×2</small></button>
  <button id="s37bud" type="button" class="new">부처님의 가호<small>에밀레종(음악 덕킹) → 차임 → 광명 오라</small></button>
  <button id="s37hit" type="button" class="new">피격 → 사망<small>피격 둘, 강타 피격, 사망(음악 30%로 덕킹)</small></button>
  <button id="s37bow" type="button" class="new">궁수 셋의 일제 사격<small>당김 ×3 → 화살비 한 번(단발 세 번 대신)</small></button>
</div>

<h2>4. 둔기 타격음 — R35 · R36 · R37</h2>
<div class="grid">
  <button id="rkO" type="button" class="old">둔기 연타 — R35 바위 소리</button>
  <button id="rkN" type="button" class="old">둔기 연타 — R36 퍽</button>
  <button id="rk37" type="button" class="new">둔기 연타 — R37 녹음</button>
</div>

<h2>5. 짐승 · 병사의 목소리(R36 소리 가운데 남은 것)</h2>
<div id="voices"></div>

<h2>6. 시대 배경음악</h2>
<p>곡마다 전장 구간과 보스전 구간이 있습니다(다른 버튼을 누르면 바뀌고, 같은 버튼을 다시 누르면 멈춤). 적장 최후 · 에밀레종 · 사망 때 잠깐 작아지는 것(덕킹)도 3절 장면에서 들을 수 있습니다.</p>
<div id="bgm"></div>
<div class="row"><label for="bk">음악 세기</label><input id="bk" type="range" min="0" max="2" step="0.05" value="1"><span id="bkv" class="num">×1.00</span></div>
<p>게임 주소 끝에 <code id="bhint">?bgm=1</code> 을 붙이면 같은 세기로 플레이합니다.</p>

<h2>7. 환경음 루프</h2>
<div class="grid" id="amb"></div>
<div class="row"><label for="k">환경음 세기</label><input id="k" type="range" min="0" max="2" step="0.05" value="1"><span id="kv" class="num">×1.00</span></div>
<p>게임 주소 끝에 <code id="hint">?amb=1</code> 을 붙이면 같은 세기로 플레이합니다.</p>

<h2>8. 그 밖의 효과음(R31~R36)</h2>
<div class="grid" id="smp"></div>
</main>
<script>
const DATA = __DATA__;
let ac = null, master = null, trunk = null, duckBus = null, r37mob = null, r37force = null;
const buf = {};
const onset = {};
let cur = null, K = 1, BK = 1, RK = 1;
function ensure() {
  if (ac) { if (ac.state === "suspended") ac.resume(); return; }
  const AC = window.AudioContext || window.webkitAudioContext;
  ac = new AC();
  // 게임과 같은 사슬: (옛 소리 · 음악 → master = 덕킹 버스) → trunk 0.5 → 컴프레서 -16dB 8:1 → 출력 / 새 소리 → mob(덕킹) · force → 컴프레서 -10dB 4:1 → trunk
  trunk = ac.createGain(); trunk.gain.value = 0.5;
  master = ac.createGain(); master.gain.value = 1;
  const comp = ac.createDynamicsCompressor(); comp.threshold.value = -16; comp.ratio.value = 8;
  master.connect(trunk); trunk.connect(comp); comp.connect(ac.destination);
  const c2 = ac.createDynamicsCompressor(); c2.threshold.value = -10; c2.ratio.value = 4; c2.knee.value = 6; c2.attack.value = 0.003; c2.release.value = 0.12;
  const out = ac.createGain(); out.gain.value = RK; window.__r37out = out;
  r37mob = ac.createGain(); r37force = ac.createGain();
  r37mob.connect(c2); r37force.connect(c2); c2.connect(out); out.connect(trunk);
  duckBus = master;
}
function load(path) {
  if (!buf[path]) buf[path] = fetch(path).then((r) => r.arrayBuffer()).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej))).then((b) => {
    const d = b.getChannelData(0), n = Math.min(d.length, Math.floor(b.sampleRate * 0.12));
    let o = 0; for (let i = 0; i < n; i++) if (d[i] > 0.01 || d[i] < -0.01) { o = Math.max(0, i / b.sampleRate - 0.004); break; }
    onset[path] = o; return b;
  });
  return buf[path];
}
// 옛 소리(wav · master 버스)
function play(file, vol, rate, delay) {
  ensure();
  const when = ac.currentTime + (delay || 0);
  return load("assets/sfx/" + file + ".wav").then((b) => {
    const s = ac.createBufferSource(); s.buffer = b; if (rate) s.playbackRate.value = rate;
    const g = ac.createGain(); g.gain.value = vol; s.connect(g); g.connect(master); s.start(Math.max(ac.currentTime, when));
  }).catch(() => {});
}
const one = (k, o) => play(DATA.snd[k][0], DATA.snd[k][1] * ((o && o.v) || 1), o && o.r, o && o.d);
// 새 소리(mp3 · 변주 셔플 · 디코더 지연 보정 · force = 덕킹 안 받음)
const lastIdx = {};
function playNew(key, o) {
  ensure();
  const e = DATA.new[key]; if (!e) return Promise.resolve();
  const fs = e.files; let i = Math.floor(Math.random() * fs.length);
  if (fs.length > 1 && lastIdx[key] === i) i = (i + 1) % fs.length;
  lastIdx[key] = i;
  const path = "assets/sfx/" + fs[i];
  const when = ac.currentTime + (o && o.d || 0);
  return load(path).then((b) => {
    const s = ac.createBufferSource(); s.buffer = b;
    const jit = o && o.jit != null ? o.jit : 0.06;
    s.playbackRate.value = (o && o.r || 1) * (1 + (Math.random() * 2 - 1) * jit);
    const g = ac.createGain(); g.gain.value = e.v * ((o && o.v) || 1);
    s.connect(g); g.connect(o && o.force ? r37force : r37mob);
    s.start(Math.max(ac.currentTime, when), onset[path] || 0);
  }).catch(() => {});
}
const loops = {};
function loopNew(key, o) {
  ensure();
  const e = DATA.new[key]; if (!e) return;
  const t = ac.currentTime;
  if (loops[key]) { const L = loops[key]; L.g.gain.cancelScheduledValues(t); L.g.gain.setValueAtTime(L.g.gain.value, t); L.g.gain.linearRampToValueAtTime(0, t + 0.6); L.s.stop(t + 0.7); delete loops[key]; return false; }
  const path = "assets/sfx/" + e.files[0];
  load(path).then((b) => {
    const t2 = ac.currentTime;
    const s = ac.createBufferSource(); s.buffer = b; s.loop = true;
    if (e.loop) { s.loopStart = e.loop[0]; s.loopEnd = Math.min(b.duration, e.loop[1]); }
    const g = ac.createGain(); g.gain.setValueAtTime((o && o.v0 != null ? o.v0 : 1) * e.v, t2); g.gain.linearRampToValueAtTime(e.v, t2 + (o && o.fadeIn || 1));
    let head = s;
    if (o && o.lowpass) { const f = ac.createBiquadFilter(); f.type = "lowpass"; f.Q.value = 0.7; f.frequency.setValueAtTime(o.lowpass[0], t2); f.frequency.exponentialRampToValueAtTime(o.lowpass[1], t2 + 2); s.connect(f); head = f; }
    head.connect(g); g.connect(r37mob);
    s.start(t2, e.loop ? e.loop[0] : 0);
    loops[key] = { s, g };
  });
  return true;
}
function duck(level, hold, release) {
  ensure();
  const t = ac.currentTime;
  [r37mob, duckBus].forEach((g) => { g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.linearRampToValueAtTime(level, t + 0.04); g.gain.setValueAtTime(level, t + 0.04 + hold); g.gain.linearRampToValueAtTime(1, t + 0.04 + hold + release); });
}
const mk = (cls, lab, sub) => { const b = document.createElement("button"); b.type = "button"; if (cls) b.className = cls; b.append(lab); const sm = document.createElement("small"); sm.textContent = sub; b.append(sm); return b; };
// 1. 비교
DATA.cmp37.forEach(([title, desc, olds, news]) => {
  const c = document.createElement("div"); c.className = "card";
  const h = document.createElement("h3"); h.textContent = title; const p = document.createElement("p"); p.textContent = desc; c.append(h, p);
  const lane = (label, keys, cls, isNew) => {
    const l = document.createElement("div"); l.className = "lane"; l.textContent = label;
    const r = document.createElement("div"); r.className = "row3";
    keys.forEach((k) => {
      const e = isNew ? DATA.new[k] : null;
      const b = mk(cls, isNew ? (DATA.newname[k] || k) : (DATA.name[k] || k), isNew ? e.files.join(" · ") + " · 볼륨 " + e.v : DATA.snd[k][0] + ".wav");
      b.onclick = () => isNew ? playNew(k) : one(k);
      r.appendChild(b);
    });
    c.append(l, r);
  };
  lane("새 녹음(R37)", news, "new", true);
  lane("예전 소리", olds, "old", false);
  document.getElementById("cmp37").appendChild(c);
});
// 2. 새로 생긴 소리
DATA.new37.forEach(([title, desc, list]) => {
  const c = document.createElement("div"); c.className = "card";
  const h = document.createElement("h3"); h.textContent = title; const p = document.createElement("p"); p.textContent = desc;
  const r = document.createElement("div"); r.className = "row3";
  list.forEach(([lab, when, key, rate, vol]) => {
    const isLoop = key.startsWith("loop:"); const k = isLoop ? key.slice(5) : key;
    const e = DATA.new[k];
    const b = mk("new", lab, when + " · " + (e ? e.files.length + "개 · 볼륨 " + e.v : ""));
    b.setAttribute("aria-pressed", "false");
    b.onclick = () => { if (isLoop) { const on = loopNew(k, { v0: 1 }); b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false"); } else playNew(k, { r: rate, v: vol }); };
    r.appendChild(b);
  });
  c.append(h, p, r);
  document.getElementById("new37").appendChild(c);
});
document.getElementById("rk").oninput = (e) => { RK = parseFloat(e.target.value); document.getElementById("rkv").textContent = "×" + RK.toFixed(2); document.getElementById("rhint").textContent = "?r37=" + RK; if (window.__r37out) window.__r37out.gain.setTargetAtTime(RK, ac.currentTime, 0.05); };
// 3. 장면
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
document.getElementById("s37cav").onclick = async () => { ensure(); playNew("sfx_nomad_ambush_cry", { v: 0.95 }); if (!loops.sfx_cavalry_hooves_loop) loopNew("sfx_cavalry_hooves_loop", { v0: 0.2, fadeIn: 2, lowpass: [350, 18000] }); await sleep(2600); playNew("sfx_cavalry_charge"); await sleep(3500); if (loops.sfx_cavalry_hooves_loop) loopNew("sfx_cavalry_hooves_loop"); };
const G = 0.36, H = 0.09;
document.getElementById("s37axe").onclick = () => { ensure(); [0, 1, 2].forEach((i) => { one("whooshHeavy", { d: i * G }); playNew("sfx_stone_axe_hit", { d: i * G + H, r: 1 + 0.015 * (i + 1) }); if (i === 1) playNew("sfx_hero_effort_light", { d: i * G }); }); one("whooshHeavy", { d: 3 * G }); playNew("sfx_stone_axe_heavy", { d: 3 * G + H, r: 1.06 }); playNew("sfx_hero_effort_light", { d: 3 * G }); };
document.getElementById("s37swd").onclick = () => { ensure(); [0, 1, 2].forEach((i) => { one("whooshBlade", { d: i * G }); playNew("sfx_sword_slash", { d: i * G + H, r: 1 + 0.015 * (i + 1) }); if (i === 1) playNew("sfx_enemy_katana_hurt", { d: i * G + H + 0.02 }); }); one("whooshBlade", { d: 3 * G }); playNew("sfx_sword_cut_hit", { d: 3 * G + H, r: 1.06 }); playNew("sfx_hero_effort_light", { d: 3 * G }); playNew("sfx_soldier_down", { d: 3 * G + H + 0.25 }); };
document.getElementById("s37arm").onclick = () => { ensure(); [0, 1].forEach((i) => { one("whooshBlade", { d: i * G }); one("cutArmor", { d: i * G + H }); }); [2, 3].forEach((i) => { one("whooshBlade", { d: i * G + 0.3 }); playNew("sfx_sword_slash", { d: i * G + 0.3 + H, v: 0.7, r: 0.93 }); }); };
document.getElementById("s37bud").onclick = () => { ensure(); playNew("sfx_buddha_emille_bell", { force: true, jit: 0 }); duck(0.35, 0.6, 0.5); one("buddhaChime", { d: 0.3 }); playNew("sfx_buddha_light_aura", { force: true, d: 0.5, v: 0.85, jit: 0 }); };
document.getElementById("s37hit").onclick = () => { ensure(); playNew("sfx_hero_hit_light", { force: true }); playNew("sfx_hero_hit_light", { force: true, d: 0.6 }); playNew("sfx_hero_hit_heavy", { force: true, d: 1.3 }); playNew("sfx_hero_death", { force: true, d: 2.4 }); setTimeout(() => duck(0.3, 1.5, 0.6), 2400); };
document.getElementById("s37bow").onclick = () => { ensure(); [0, 0.05, 0.1].forEach((d) => playNew("sfx_bow_draw", { d })); playNew("sfx_arrow_volley", { d: 0.7 }); };
document.getElementById("rkO").onclick = () => { ensure(); [["whooshHeavy", 0], ["rockHit1", H], ["whooshHeavy", G], ["rockHit2", G + H], ["whooshHeavy", 2 * G], ["rockHeavy", 2 * G + H]].forEach(([k, t]) => one(k, { d: t })); };
document.getElementById("rkN").onclick = () => { ensure(); [["whooshHeavy", 0], ["thudHit1", H], ["whooshHeavy", G], ["thudHit2", G + H], ["whooshHeavy", 2 * G], ["thudHeavy", 2 * G + H]].forEach(([k, t]) => one(k, { d: t })); };
document.getElementById("rk37").onclick = () => { ensure(); [0, 1].forEach((i) => { one("whooshHeavy", { d: i * G }); playNew("sfx_stone_axe_hit", { d: i * G + H }); }); one("whooshHeavy", { d: 2 * G }); playNew("sfx_stone_axe_heavy", { d: 2 * G + H }); };
// 5. R36 목소리(남은 것)
DATA.voices36.forEach(([title, desc, list]) => {
  const c = document.createElement("div"); c.className = "card";
  const h = document.createElement("h3"); h.textContent = title; const p = document.createElement("p"); p.textContent = desc;
  const r = document.createElement("div"); r.className = "row3";
  list.forEach(([lab, when, k, rate, vol]) => { const b = mk("old", lab, when); b.onclick = () => one(k, { r: rate, v: vol }); r.appendChild(b); });
  c.append(h, p, r);
  document.getElementById("voices").appendChild(c);
});
// 6. 배경음악(게임과 같은 방식)
let bg = null;
const findMark = (b) => { const d = b.getChannelData(0), n = Math.min(d.length, Math.floor(b.sampleRate * 0.3)); let pv = 0, pi = 0; for (let i = 0; i < n; i++) { const v = Math.abs(d[i]); if (v > pv) { pv = v; pi = i; } } return pi / b.sampleRate; };
function bgStop() {
  if (!bg) return;
  clearInterval(bg.timer);
  const t = ac.currentTime, o = bg;
  o.bus.gain.cancelScheduledValues(t); o.bus.gain.setValueAtTime(o.bus.gain.value, t); o.bus.gain.linearRampToValueAtTime(0.0001, t + 0.4);
  setTimeout(() => { o.srcs.forEach((x) => { try { x.stop(); } catch (e) {} }); o.bus.disconnect(); }, 600);
  if (o.btn) { o.btn.classList.remove("on"); o.btn.setAttribute("aria-pressed", "false"); }
  bg = null;
}
function bgPlay(row, sec, btn) {
  ensure();
  const id = row[1] + sec; const same = bg && bg.id === id;
  bgStop();
  if (same) return;
  btn.classList.add("on"); btn.setAttribute("aria-pressed", "true");
  const st = { id, btn, srcs: [], timer: null, bus: ac.createGain() };
  st.bus.gain.value = 0.34 * BK; st.bus.connect(master); bg = st;
  fetch("assets/bgm/" + row[1] + ".mp3").then((r) => r.arrayBuffer()).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej))).then((b) => {
    if (bg !== st) return;
    const t0 = findMark(b), start = sec === "a" ? row[3] : row[5], len = sec === "a" ? row[4] : row[6];
    let next = ac.currentTime + 0.08;
    const pump = () => { while (next < ac.currentTime + 0.7) { const s = ac.createBufferSource(); s.buffer = b; s.connect(st.bus); s.start(next, t0 + start, len + DATA.tail); st.srcs.push(s); if (st.srcs.length > 3) st.srcs.shift(); next += len; } };
    pump(); st.timer = setInterval(pump, 200);
  }).catch(() => { if (bg === st) bgStop(); });
}
DATA.bgm.forEach((row) => {
  const c = document.createElement("div"); c.className = "card";
  const h = document.createElement("h3"); h.textContent = row[8] + " — 「" + row[2] + "」"; const p = document.createElement("p"); p.textContent = row[7];
  const r = document.createElement("div"); r.className = "row3";
  [["a", "전장", row[4]], ["b", "보스전", row[6]]].forEach(([sec, lab, len]) => { const b = mk("", lab, "한 바퀴 " + Math.round(len) + "초"); b.setAttribute("aria-pressed", "false"); b.onclick = () => bgPlay(row, sec, b); r.appendChild(b); });
  c.append(h, p, r);
  document.getElementById("bgm").appendChild(c);
});
document.getElementById("bk").oninput = (e) => { BK = parseFloat(e.target.value); document.getElementById("bkv").textContent = "×" + BK.toFixed(2); document.getElementById("bhint").textContent = "?bgm=" + BK; if (bg && ac) bg.bus.gain.setTargetAtTime(0.34 * BK, ac.currentTime, 0.1); };
// 7. 환경음
function amb(key, file, vol, btn) {
  ensure();
  const t = ac.currentTime;
  document.querySelectorAll("#amb button").forEach((b) => { b.classList.remove("on"); b.setAttribute("aria-pressed", "false"); });
  if (cur) { cur.g.gain.cancelScheduledValues(t); cur.g.gain.setValueAtTime(cur.g.gain.value, t); cur.g.gain.linearRampToValueAtTime(0, t + 1.4); cur.s.stop(t + 1.5); const same = cur.key === key; cur = null; if (same) return; }
  btn.classList.add("on"); btn.setAttribute("aria-pressed", "true");
  load("assets/sfx/" + file + ".wav").then((b) => { const s = ac.createBufferSource(); s.buffer = b; s.loop = true; const g = ac.createGain(); g.gain.setValueAtTime(0, ac.currentTime); g.gain.linearRampToValueAtTime(vol * K, ac.currentTime + 1.6); s.connect(g); g.connect(master); s.start(); cur = { key, s, g, vol }; }).catch(() => {});
}
DATA.amb.forEach(([key, file, vol, lab]) => { const b = mk("", lab, file + ".wav · 볼륨 " + vol); b.setAttribute("aria-pressed", "false"); b.onclick = () => amb(key, file, vol, b); document.getElementById("amb").appendChild(b); });
document.getElementById("k").oninput = (e) => { K = parseFloat(e.target.value); document.getElementById("kv").textContent = "×" + K.toFixed(2); document.getElementById("hint").textContent = "?amb=" + K; if (cur && ac) cur.g.gain.setTargetAtTime(cur.vol * K, ac.currentTime, 0.1); };
// 8. 그 밖
DATA.smp.forEach(([key, file, vol, lab]) => { const b = mk("", lab, file + ".wav · 볼륨 " + vol); b.onclick = () => one(key); document.getElementById("smp").appendChild(b); });
</script>
"""
dj = json.dumps(data, ensure_ascii=False)
full = '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + HEAD + '</head>\n<body>\n' + BODY.replace("__DATA__", dj) + '</body>\n</html>\n'
open(os.path.join(root, "sound-check.html"), "w", encoding="utf-8", newline="\n").write(full)
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(HEAD + BODY.replace("__DATA__", dj))
print("sound-check.html", len(CMP37), "비교 줄 ·", sum(len(v[2]) for v in NEW37), "새 소리 버튼 ·", len(new), "새 키 ·", len(data["bgm"]), "곡 ·", len(data["smp"]), "효과음 ·", len(data["amb"]), "루프", "· 아티팩트용" if len(sys.argv) > 2 else "")
