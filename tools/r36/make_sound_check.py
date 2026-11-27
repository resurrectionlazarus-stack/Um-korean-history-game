#!/usr/bin/env python3
"""R36 음향 점검 페이지(sound-check.html) 만들기 — index.html의 효과음 표(SMP · SMP_VOL · AMB · AMB_VOL) · 짐승 목소리 표(R36_BEAST) · 배경음악 표(R35_BGM)를 읽어
게임과 같은 볼륨 비율(마스터 0.5 · 컴프레서 같음)로 들어 볼 수 있는 정적 페이지를 만든다. 실기기에서 듣고 볼륨 · 느낌을 맞출 때 쓴다.
R36: ① 둔기 타격음 'R35 바위 소리 ↔ 새 퍽 소리' 비교 ② 짐승 · 병사의 목소리(게임 속 음높이 · 볼륨 그대로) ③ 장면으로 들어 보기 ④ 칼 · 창 타격음 ⑤ 시대 배경음악 ⑥ 환경음 ⑦ 그 밖
사용: python3 -I tools/r36/make_sound_check.py <빌드 폴더> [아티팩트 게시용 출력 html]"""
import json
import re
import sys

root = sys.argv[1]
s = open(root + "/index.html", encoding="utf-8").read()


def table(name):
    m = re.search(r"const " + name + r" = (\{[^}]*\});", s)
    return json.loads(re.sub(r"(\w+):", r'"\1":', m.group(1)))


def unesc(t):
    return re.sub(r"\\u([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), t)


SMP, VOL, AMB, AVOL = table("SMP"), table("SMP_VOL"), table("AMB"), table("AMB_VOL")
bt = re.search(r"const R36_BEAST = (\{.*?\n    \});", s, re.S).group(1)
BEAST = json.loads(re.sub(r"(\w+):", r'"\1":', bt))
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
       "buddhaBell": "부처님의 가호 범종", "buddhaChime": "부처님의 가호 차임", "dragonRoar": "4시대 청룡", "gunPistol": "6시대 모젤 권총", "gunRifle": "6시대 소총", "thunder1": "가까운 벼락", "thunder2": "먼 천둥", "warHorn": "전선 보스 뿔나팔"}
ALAB = {"rain": "폭우 — 4시대 1전선 거란", "blizzard": "눈보라 — 2전선 여진 · 5시대 2막 설원(약하게)", "wind": "황야 바람 — 3전선 몽골 · 1시대 빙하기 · 6시대 폐허(약하게)", "fire": "화염 — 4전선 개경 · 3시대 전장(약하게)"}
VOICE = {"wolfHowl", "wolfSnarl", "wolfYelp", "hyenaCackle", "bearRoar", "bearGrowl", "rhinoSnort", "beastGroan", "tigerRoar", "tigerSnarl", "warCry"}
HITS = {"cutLight1", "cutLight2", "cutLight3", "cutHeavy", "cutSever", "cutArmor", "cutFlurry", "thudHit1", "thudHit2", "thudHeavy", "thudCrush", "stab1", "stab2", "whooshBlade", "whooshHeavy"} | VOICE
# R35의 둔기 소리(게임에서는 더 받지 않음 · 비교용으로만 파일을 남김): [파일, R35 볼륨]
OLD = {"rockHit1": ["rock_hit_1", 0.84], "rockHit2": ["rock_hit_2", 0.84], "rockHeavy": ["rock_heavy", 0.98], "rockCrush": ["rock_crush", 1.0]}
# 비교 줄: [제목, 설명, [예전 키...], [새 키...]]
CMP = [
    ["둔기 — 가벼운 타격", "연타의 앞 타. 울리는 음 없이 짧게 '퍽'", ["rockHit1", "rockHit2"], ["thudHit1", "thudHit2"]],
    ["둔기 — 강타", "연타의 마지막 타. 더 낮고 묵직하게", ["rockHeavy"], ["thudHeavy"]],
    ["둔기 — 내려찍기", "땅까지 울리는 가장 큰 타격", ["rockCrush"], ["thudCrush"]],
]
# 칼 · 창(R35와 같음): [제목, 설명, [키...]]
BLADE = [
    ["칼 — 베기", "가벼운 베기 셋 · 강타 · 양단 막타", ["cutLight1", "cutLight2", "cutLight3", "cutHeavy", "cutSever"]],
    ["칼 — 갑옷 · 연참", "쇠 울림 · 여러 번 잇달아 베기", ["cutArmor", "cutFlurry"]],
    ["창 — 찌르기 · 휘두르는 바람", "슉 → 푹 · 칼 = 휙 · 둔기 = 부웅", ["stab1", "stab2", "whooshBlade", "whooshHeavy"]],
]
NAME = {"cutLight1": "베기 1", "cutLight2": "베기 2", "cutLight3": "베기 3", "cutHeavy": "강타", "cutSever": "양단", "cutArmor": "쇠 울림", "cutFlurry": "연참",
        "rockHit1": "R35 바위 타격 1", "rockHit2": "R35 바위 타격 2", "rockHeavy": "R35 바위 강타", "rockCrush": "R35 내려찍기",
        "thudHit1": "새 퍽 1", "thudHit2": "새 퍽 2", "thudHeavy": "새 묵직한 퍽", "thudCrush": "새 내려찍기", "stab1": "찌르기 1", "stab2": "찌르기 2", "whooshBlade": "칼 바람", "whooshHeavy": "둔기 바람"}
# 짐승 · 병사의 목소리: [이름, 설명, [[버튼 이름, 언제 나나, 키, 음높이, 볼륨], ...]] — 음높이 · 볼륨은 게임 속 값(R36_BEAST · 웨이브 · 포효 코드)과 같게
def bv(role, ev):
    k, r, v = BEAST[role][ev]
    return [k, r, v]
VOICES = [
    ["늑대", "빠르게 에워싸는 무리. 멀리서 길게 울고, 덮치기 직전에 으르렁거립니다.", [
        ["하울링", "웨이브 등장", "wolfHowl", 1, 0.9], ["으르렁", "덮치기 직전(공격 예고)"] + bv("WOLF", "atk"), ["깨갱", "쓰러질 때"] + bv("WOLF", "die"), ["낮은 으르렁", "기척(4~7초에 한 번)"] + bv("WOLF", "idle")]],
    ["하이에나", "기습해 뛰어드는 무리. 높게 낄낄거립니다.", [
        ["낄낄", "웨이브 등장", "hyenaCackle", 1, 0.9], ["으르렁", "덮치기 직전"] + bv("HYENA", "atk"), ["깨갱", "쓰러질 때"] + bv("HYENA", "die"), ["낄낄(작게)", "기척"] + bv("HYENA", "idle")]],
    ["동굴 곰", "느리지만 한 방이 무거운 강타형. 중간보스는 더 낮고 크게 웁니다.", [
        ["포효", "웨이브 등장(화면이 살짝 흔들림)", "bearRoar", 1, 0.85], ["포효(중간보스)", "동굴 곰 지배자 등장", "bearRoar", 0.88, 1.15], ["으르렁", "내려치기 직전"] + bv("BEAR", "atk"), ["신음", "쓰러질 때"] + bv("BEAR", "die"),
        ["낮은 으르렁", "기척"] + bv("BEAR", "idle")]],
    ["털코뿔소", "곧게 들이받는 돌진형. 콧김을 내뿜습니다.", [
        ["콧김", "웨이브 등장", "rhinoSnort", 1, 0.9], ["콧김", "돌진 직전"] + bv("RHINO", "atk"), ["신음", "쓰러질 때"] + bv("RHINO", "die"), ["콧김(작게)", "기척"] + bv("RHINO", "idle")]],
    ["산군 — 1시대 보스 호랑이", "보스전의 포효. 등장 · 광폭화 때 길게, 돌진 직전에 짧게.", [
        ["포효", "등장 · 광폭화", "tigerRoar", 1, 1], ["으르렁", "돌진 직전", "tigerSnarl", 1, 1], ["마지막 포효", "쓰러질 때(낮게)", "tigerRoar", 0.82, 1]]],
    ["병사들 — 2~6시대", "웨이브가 들어올 때 여럿이 한꺼번에 지르는 함성(예전에는 경보음이었습니다).", [
        ["함성", "웨이브 등장", "warCry", 1, 1]]],
]
snd = {k: [SMP[k], VOL.get(k, 0.7)] for k in SMP}
snd.update(OLD)
data = {"snd": snd, "name": NAME, "cmp": CMP, "blade": BLADE, "voices": VOICES, "bgm": BGM, "tail": TAIL,
        "smp": [[k, SMP[k], VOL.get(k, 0.7), LAB.get(k, k)] for k in SMP if k not in HITS],
        "amb": [[k, AMB[k], AVOL.get(k, 0.25), ALAB.get(k, k)] for k in AMB]}
HEAD = """<title>신시 음향 점검</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
  /* 한 줄 배치: 좁은 한 단 · 버튼 격자(폭이 좁아지면 한 줄에 하나) — 게임의 먹빛 화면을 따라 어두운 쪽이 기본 */
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
<h1>신시 R36 음향 점검</h1>
<p>버튼을 누르면 게임과 같은 볼륨 비율로 들립니다. 이번 라운드에는 둔기 타격음을 둔탁한 '퍽'으로 다시 만들고, 짐승의 울음과 병사의 함성을 새로 넣었습니다. 파란 테두리 = 새 소리, 점선 = R35 소리(비교용)입니다.</p>
<p class="note">이 소리들은 모두 직접 합성한 것이고, 만든 쪽은 귀로 들어 볼 수 없어 수치(음역 분포 · 울림 꼬리 길이)로만 맞췄습니다. 휴대폰 스피커로 들어 보고 거슬리는 소리의 이름을 알려 주시면 그것만 다시 만들거나 뺍니다.</p>

<h2>1. 둔기 타격음 — R35 소리와 새 소리 비교</h2>
<p>R35의 바위 소리는 울리는 음이 섞여 '깡깡' 하고 들렸습니다. 새 소리는 울리는 음을 모두 빼고 높은 음역을 낮춘 짧은 '퍽'입니다. 가벼운 타격은 높은 쪽 꼬리가 절반 가까이 짧아졌습니다.</p>
<div id="cmp"></div>
<div class="grid">
  <button id="rkN" type="button" class="new">둔기 연타 — 새 소리<small>부웅-퍽 ×2, 묵직한 퍽</small></button>
  <button id="rkO" type="button" class="old">둔기 연타 — R35 소리<small>비교용</small></button>
  <button id="slN" type="button" class="new">내려찍기(갈래 기술)<small>부웅, 땅을 치는 소리, 맞는 소리</small></button>
</div>

<h2>2. 짐승과 병사의 목소리</h2>
<p>버튼마다 게임 속 음높이와 볼륨 그대로 들립니다. 작은 글씨는 그 소리가 나는 때입니다.</p>
<div id="voices"></div>

<h2>3. 장면으로 들어 보기</h2>
<p>게임에서 이어지는 순서대로 묶었습니다.</p>
<div class="grid">
  <button id="scW" type="button" class="new">늑대와 곰이 몰려온다<small>하울링, 곰 포효(웨이브 등장)</small></button>
  <button id="scF" type="button" class="new">덮치기, 반격, 쓰러짐<small>으르렁, 부웅-퍽, 깨갱</small></button>
  <button id="scH" type="button" class="new">하이에나와 코뿔소<small>콧김, 낄낄(웨이브 등장)</small></button>
  <button id="scT" type="button" class="new">보스 산군 등장<small>호랑이 포효, 돌진 직전 으르렁</small></button>
  <button id="scC" type="button" class="new">병사들의 돌격<small>함성, 이어서 칼 연타</small></button>
</div>

<h2>4. 칼 · 창 타격음</h2>
<p>R35에서 만든 그대로입니다.</p>
<div id="blade"></div>
<div class="grid">
  <button id="cbN" type="button">칼 연타<small>휙-서걱 ×3, 강타</small></button>
  <button id="stN" type="button">창 연타<small>슉-푹 ×2, 강타</small></button>
  <button id="flN" type="button">연참 뒤 양단<small>연참, 이어서 양단 막타</small></button>
</div>

<h2>5. 시대 배경음악</h2>
<p>곡마다 전장 구간과 보스전 구간이 있습니다. 게임과 같은 방식으로 끊김 없이 반복됩니다(다른 버튼을 누르면 바뀌고, 같은 버튼을 다시 누르면 멈춤).</p>
<div id="bgm"></div>
<div class="row"><label for="bk">음악 세기</label><input id="bk" type="range" min="0" max="2" step="0.05" value="1"><span id="bkv" class="num">×1.00</span></div>
<p>마음에 드는 세기를 찾으면 게임 주소 끝에 <code id="bhint">?bgm=1</code> 을 붙여 같은 세기로 플레이할 수 있습니다. <code>?bgm=synth</code> 는 예전 합성 음악으로 되돌립니다.</p>

<h2>6. 환경음 루프</h2>
<p>누르면 서로 교차하고, 다시 누르면 꺼집니다.</p>
<div class="grid" id="amb"></div>
<div class="row"><label for="k">환경음 세기</label><input id="k" type="range" min="0" max="2" step="0.05" value="1"><span id="kv" class="num">×1.00</span></div>
<p>게임 주소 끝에 <code id="hint">?amb=1</code> 을 붙이면 같은 세기로 플레이합니다. <code>?amb=0</code> 은 환경음 끔입니다.</p>

<h2>7. 연출 순서 · 그 밖의 효과음</h2>
<div class="grid">
  <button id="seqB" type="button">부처님의 가호<small>범종, 0.3초 뒤 차임</small></button>
  <button id="seqT" type="button">번개 뒤 천둥<small>0.5초 늦게 가까운 벼락</small></button>
  <button id="seqH" type="button">전선 보스 등장<small>뿔나팔, 이어서 최종 보스용(더 낮고 크게)</small></button>
</div>
<div class="grid" id="smp" style="margin-top:8px"></div>
</main>
<script>
const DATA = __DATA__;
let ac = null, master = null;
const buf = {};
let cur = null, K = 1, BK = 1;
function ensure() {
  if (ac) { if (ac.state === "suspended") ac.resume(); return; }
  const AC = window.AudioContext || window.webkitAudioContext;
  ac = new AC();
  master = ac.createGain();
  master.gain.value = 0.5;
  const comp = ac.createDynamicsCompressor();
  comp.threshold.value = -16;
  comp.ratio.value = 8;
  master.connect(comp);
  comp.connect(ac.destination);
}
function load(path) {
  if (!buf[path]) buf[path] = fetch(path).then((r) => r.arrayBuffer()).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej)));
  return buf[path];
}
function play(file, vol, rate, delay) {
  ensure();
  const when = ac.currentTime + (delay || 0);
  return load("assets/sfx/" + file + ".wav").then((b) => {
    const s = ac.createBufferSource();
    s.buffer = b;
    if (rate) s.playbackRate.value = rate;
    const g = ac.createGain();
    g.gain.value = vol;
    s.connect(g);
    g.connect(master);
    s.start(Math.max(ac.currentTime, when));
  }).catch(() => {});
}
// 키(게임 속 이름)로 한 번 재생. o = { v 볼륨 배율, r 음높이, d 지연(초) }
const one = (k, o) => play(DATA.snd[k][0], DATA.snd[k][1] * ((o && o.v) || 1), o && o.r, o && o.d);
const mk = (cls, lab, sub) => {
  const b = document.createElement("button");
  b.type = "button";
  if (cls) b.className = cls;
  b.append(lab);
  const sm = document.createElement("small");
  sm.textContent = sub;
  b.append(sm);
  return b;
};
// 1. 비교
DATA.cmp.forEach(([title, desc, olds, news]) => {
  const c = document.createElement("div");
  c.className = "card";
  const h = document.createElement("h3");
  h.textContent = title;
  const p = document.createElement("p");
  p.textContent = desc;
  c.append(h, p);
  const lane = (label, keys, cls) => {
    if (!keys.length) return;
    const l = document.createElement("div");
    l.className = "lane";
    l.textContent = label;
    const r = document.createElement("div");
    r.className = "row3";
    keys.forEach((k) => {
      const b = mk(cls, DATA.name[k] || k, DATA.snd[k][0] + ".wav");
      b.dataset.k = k;
      b.onclick = () => one(k);
      r.appendChild(b);
    });
    c.append(l, r);
  };
  lane("새 소리", news, "new");
  lane("R35 소리", olds, "old");
  document.getElementById("cmp").appendChild(c);
});
// 짐승 · 병사의 목소리: [버튼 이름, 언제, 키, 음높이, 볼륨]
DATA.voices.forEach(([title, desc, list]) => {
  const c = document.createElement("div");
  c.className = "card";
  const h = document.createElement("h3");
  h.textContent = title;
  const p = document.createElement("p");
  p.textContent = desc;
  const r = document.createElement("div");
  r.className = "row3";
  list.forEach(([lab, when, k, rate, vol]) => {
    const b = mk("new", lab, when);
    b.dataset.k = k;
    b.onclick = () => one(k, { r: rate, v: vol });
    r.appendChild(b);
  });
  c.append(h, p, r);
  document.getElementById("voices").appendChild(c);
});
// 칼 · 창(R35와 같음)
DATA.blade.forEach(([title, desc, keys]) => {
  const c = document.createElement("div");
  c.className = "card";
  const h = document.createElement("h3");
  h.textContent = title;
  const p = document.createElement("p");
  p.textContent = desc;
  const r = document.createElement("div");
  r.className = "row3";
  keys.forEach((k) => {
    const b = mk("", DATA.name[k] || k, DATA.snd[k][0] + ".wav");
    b.dataset.k = k;
    b.onclick = () => one(k);
    r.appendChild(b);
  });
  c.append(h, p, r);
  document.getElementById("blade").appendChild(c);
});
// 2. 연타: [키, 시각(초), 옵션]
const seq = (list) => { ensure(); list.forEach(([k, t, o]) => one(k, Object.assign({ d: t }, o || {}))); };
const G = 0.36, H = 0.09;   // 타 간격 · 휘두른 뒤 맞는 순간까지
document.getElementById("cbN").onclick = () => seq([["whooshBlade", 0], ["cutLight1", H, { v: 0.97, r: 1.01 }], ["whooshBlade", G], ["cutLight2", G + H, { v: 1.02, r: 0.99 }], ["whooshBlade", 2 * G], ["cutLight3", 2 * G + H, { v: 1.07, r: 0.97 }], ["whooshBlade", 3 * G], ["cutHeavy", 3 * G + H]]);
document.getElementById("rkN").onclick = () => seq([["whooshHeavy", 0], ["thudHit1", H, { v: 0.97, r: 1.01 }], ["whooshHeavy", G], ["thudHit2", G + H, { v: 1.02, r: 0.99 }], ["whooshHeavy", 2 * G], ["thudHeavy", 2 * G + H]]);
document.getElementById("rkO").onclick = () => seq([["whooshHeavy", 0], ["rockHit1", H, { v: 0.97, r: 1.01 }], ["whooshHeavy", G], ["rockHit2", G + H, { v: 1.02, r: 0.99 }], ["whooshHeavy", 2 * G], ["rockHeavy", 2 * G + H]]);
document.getElementById("slN").onclick = () => seq([["whooshHeavy", 0], ["thudCrush", 0.18, { v: 0.9 }], ["thudHeavy", 0.2], ["thudHeavy", 0.26, { r: 0.96 }]]);
// 장면
document.getElementById("scW").onclick = () => seq([["wolfHowl", 0.03, { v: 0.9 }], ["bearRoar", 0.07, { v: 0.85 }]]);
document.getElementById("scF").onclick = () => seq([["wolfSnarl", 0, { v: 0.9 }], ["whooshHeavy", 0.42], ["thudHit1", 0.42 + H], ["whooshHeavy", 0.42 + G], ["thudHeavy", 0.42 + G + H], ["wolfYelp", 0.42 + G + H + 0.06, { v: 0.9 }]]);
document.getElementById("scH").onclick = () => seq([["rhinoSnort", 0.23, { v: 0.9 }], ["hyenaCackle", 0.33, { v: 0.9 }]]);
document.getElementById("scT").onclick = () => seq([["tigerRoar", 0], ["tigerSnarl", 3.4]]);
document.getElementById("scC").onclick = () => seq([["warCry", 0], ["whooshBlade", 1.5], ["cutLight1", 1.5 + H], ["whooshBlade", 1.5 + G], ["cutLight2", 1.5 + G + H], ["whooshBlade", 1.5 + 2 * G], ["cutHeavy", 1.5 + 2 * G + H]]);
document.getElementById("stN").onclick = () => seq([["whooshBlade", 0], ["stab1", H], ["whooshBlade", G], ["stab2", G + H], ["whooshBlade", 2 * G], ["cutHeavy", 2 * G + H]]);
document.getElementById("flN").onclick = () => seq([["cutFlurry", 0], ["cutSever", 0.75]]);
// 3. 배경음악: 표지음(파일 맨 앞의 짧은 삑)으로 시작 위치를 보정하고, 구간 길이마다 새로 겹쳐 틀어 이음매 없이 반복(게임과 같은 방식)
let bg = null;
const findMark = (b) => { const d = b.getChannelData(0), n = Math.min(d.length, Math.floor(b.sampleRate * 0.3)); let pv = 0, pi = 0; for (let i = 0; i < n; i++) { const v = Math.abs(d[i]); if (v > pv) { pv = v; pi = i; } } return pi / b.sampleRate; };
function bgStop() {
  if (!bg) return;
  clearInterval(bg.timer);
  const t = ac.currentTime, o = bg;
  o.bus.gain.cancelScheduledValues(t);
  o.bus.gain.setValueAtTime(o.bus.gain.value, t);
  o.bus.gain.linearRampToValueAtTime(0.0001, t + 0.4);
  setTimeout(() => { o.srcs.forEach((x) => { try { x.stop(); } catch (e) {} }); o.bus.disconnect(); }, 600);
  if (o.btn) { o.btn.classList.remove("on"); o.btn.setAttribute("aria-pressed", "false"); }
  bg = null;
}
function bgPlay(row, sec, btn) {
  ensure();
  const id = row[1] + sec;
  const same = bg && bg.id === id;
  bgStop();
  if (same) return;
  btn.classList.add("on");
  btn.setAttribute("aria-pressed", "true");
  const st = { id, btn, srcs: [], timer: null, bus: ac.createGain(), dead: false };
  st.bus.gain.value = 0.34 * BK;
  st.bus.connect(master);
  bg = st;
  load("assets/bgm/" + row[1] + ".mp3").then((b) => {
    if (bg !== st) return;
    const t0 = findMark(b), start = sec === "a" ? row[3] : row[5], len = sec === "a" ? row[4] : row[6];
    let next = ac.currentTime + 0.08;
    const pump = () => {
      while (next < ac.currentTime + 0.7) {
        const s = ac.createBufferSource();
        s.buffer = b;
        s.connect(st.bus);
        s.start(next, t0 + start, len + DATA.tail);
        st.srcs.push(s);
        if (st.srcs.length > 3) st.srcs.shift();
        next += len;
      }
    };
    pump();
    st.timer = setInterval(pump, 200);
  }).catch(() => { if (bg === st) bgStop(); });
}
DATA.bgm.forEach((row) => {
  const c = document.createElement("div");
  c.className = "card";
  const h = document.createElement("h3");
  h.textContent = row[8] + " — 「" + row[2] + "」";
  const p = document.createElement("p");
  p.textContent = row[7];
  const r = document.createElement("div");
  r.className = "row3";
  [["a", "전장", row[4]], ["b", "보스전", row[6]]].forEach(([sec, lab, len]) => {
    const b = mk("new", lab, "한 바퀴 " + Math.round(len) + "초");
    b.id = "bgm-" + row[0] + sec;
    b.setAttribute("aria-pressed", "false");
    b.onclick = () => bgPlay(row, sec, b);
    r.appendChild(b);
  });
  c.append(h, p, r);
  document.getElementById("bgm").appendChild(c);
});
document.getElementById("bk").oninput = (e) => {
  BK = parseFloat(e.target.value);
  document.getElementById("bkv").textContent = "×" + BK.toFixed(2);
  document.getElementById("bhint").textContent = "?bgm=" + BK;
  if (bg && ac) bg.bus.gain.setTargetAtTime(0.34 * BK, ac.currentTime, 0.1);
};
// 4. 환경음
function amb(key, file, vol, btn) {
  ensure();
  const t = ac.currentTime;
  document.querySelectorAll("#amb button").forEach((b) => { b.classList.remove("on"); b.setAttribute("aria-pressed", "false"); });
  if (cur) {
    cur.g.gain.cancelScheduledValues(t);
    cur.g.gain.setValueAtTime(cur.g.gain.value, t);
    cur.g.gain.linearRampToValueAtTime(0, t + 1.4);
    cur.s.stop(t + 1.5);
    const same = cur.key === key;
    cur = null;
    if (same) return;
  }
  btn.classList.add("on");
  btn.setAttribute("aria-pressed", "true");
  load("assets/sfx/" + file + ".wav").then((b) => {
    const s = ac.createBufferSource();
    s.buffer = b;
    s.loop = true;
    const g = ac.createGain();
    g.gain.setValueAtTime(0, ac.currentTime);
    g.gain.linearRampToValueAtTime(vol * K, ac.currentTime + 1.6);
    s.connect(g);
    g.connect(master);
    s.start();
    cur = { key, s, g, vol };
  }).catch(() => {});
}
DATA.amb.forEach(([key, file, vol, lab]) => {
  const b = mk("", lab, file + ".wav · 볼륨 " + vol);
  b.id = "amb-" + key;
  b.setAttribute("aria-pressed", "false");
  b.onclick = () => amb(key, file, vol, b);
  document.getElementById("amb").appendChild(b);
});
document.getElementById("k").oninput = (e) => {
  K = parseFloat(e.target.value);
  document.getElementById("kv").textContent = "×" + K.toFixed(2);
  document.getElementById("hint").textContent = "?amb=" + K;
  if (cur && ac) cur.g.gain.setTargetAtTime(cur.vol * K, ac.currentTime, 0.1);
};
// 5. 그 밖
DATA.smp.forEach(([key, file, vol, lab]) => {
  const b = mk("", lab, file + ".wav · 볼륨 " + vol);
  b.id = "smp-" + key;
  b.onclick = () => one(key);
  document.getElementById("smp").appendChild(b);
});
document.getElementById("seqB").onclick = () => { one("buddhaBell"); one("buddhaChime", { d: 0.3 }); };
document.getElementById("seqT").onclick = () => { one("thunder1", { v: 0.9, d: 0.5 }); };
document.getElementById("seqH").onclick = () => { one("warHorn"); one("warHorn", { r: 0.84, v: 1.15, d: 3.4 }); };
</script>
"""
dj = json.dumps(data, ensure_ascii=False)
# ① 배포 폴더용(혼자 서는 완전한 HTML) ② 아티팩트 게시용(머리 · 몸통 뼈대 없이 내용만 — 게시할 때 뼈대가 씌워짐)
full = '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + HEAD + '</head>\n<body>\n' + BODY.replace("__DATA__", dj) + '</body>\n</html>\n'
open(root + "/sound-check.html", "w", encoding="utf-8", newline="\n").write(full)
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(HEAD + BODY.replace("__DATA__", dj))
print("sound-check.html", len(data["cmp"]), "비교 줄 ·", sum(len(v[2]) for v in VOICES), "목소리 버튼 ·", len(data["bgm"]), "곡 ·", len(data["smp"]), "효과음 ·", len(data["amb"]), "루프", "· 아티팩트용" if len(sys.argv) > 2 else "")
