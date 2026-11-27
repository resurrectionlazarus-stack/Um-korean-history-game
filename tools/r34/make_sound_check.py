#!/usr/bin/env python3
"""R34 음향 점검 페이지(sound-check.html) 만들기 — index.html의 효과음 표(SMP · SMP_VOL · AMB · AMB_VOL)를 읽어
게임과 같은 볼륨 비율(마스터 0.5 · 컴프레서 같음)로 한 개씩 들어 볼 수 있는 정적 페이지를 만든다. 실기기에서 볼륨을 맞출 때 쓴다.
사용: python3 -I tools/r34/make_sound_check.py <빌드 폴더>"""
import json
import re
import sys

root = sys.argv[1]
s = open(root + "/index.html", encoding="utf-8").read()


def table(name):
    m = re.search(r"const " + name + r" = (\{[^}]*\});", s)
    return json.loads(re.sub(r"(\w+):", r'"\1":', m.group(1)))


SMP, VOL, AMB, AVOL = table("SMP"), table("SMP_VOL"), table("AMB"), table("AMB_VOL")
LAB = {"slashLight": "가벼운 베기(옛 1 · 2타)", "hitHeavy": "강타 · 보스 적중", "breath": "호흡 피니시", "parryCounter": "패링 카운터", "relicAwaken": "유물 각성", "killcam": "킬캠 슬로우",
       "sliceCrisp1": "일반 베기 1", "sliceCrisp2": "일반 베기 2", "sliceSever": "양단", "sliceFlurry": "연참 · 일섬", "missionGong": "미션 성공 징", "bombBlast": "의열단 폭탄",
       "buddhaBell": "부처님의 가호 범종", "buddhaChime": "부처님의 가호 차임", "bladeSlash1": "4시대 베기 1", "bladeSlash2": "4시대 베기 2", "bladeArmor": "4시대 갑옷 쪼개기", "dragonRoar": "4시대 청룡",
       "gunPistol": "6시대 모젤 권총", "gunRifle": "6시대 소총", "thunder1": "가까운 벼락", "thunder2": "먼 천둥", "warHorn": "전선 보스 뿔나팔"}
ALAB = {"rain": "폭우 — 4시대 1전선 거란", "blizzard": "눈보라 — 2전선 여진 · 5시대 2막 설원(약하게)", "wind": "황야 바람 — 3전선 몽골 · 1시대 빙하기 · 6시대 폐허(약하게)", "fire": "화염 — 4전선 개경 · 3시대 전장(약하게)"}
NEW = ["thunder1", "thunder2", "warHorn"]
data = {"smp": [[k, SMP[k], VOL.get(k, 0.7), LAB.get(k, k), k in NEW] for k in SMP], "amb": [[k, AMB[k], AVOL.get(k, 0.25), ALAB.get(k, k)] for k in AMB]}
html = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>신시 음향 점검</title>
<style>
  :root { --bg: #0f1218; --card: #1a1f2a; --line: #2c3444; --ink: #e8e6df; --dim: #9aa3b5; --gold: #fbbf24; --new: #38bdf8; }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 16px; background: var(--bg); color: var(--ink); font: 15px/1.5 system-ui, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }
  main { max-width: 760px; margin: 0 auto; }
  h1 { font-size: 20px; margin: 4px 0 4px; color: var(--gold); }
  h2 { font-size: 15px; margin: 22px 0 8px; color: var(--dim); font-weight: 600; }
  p { margin: 4px 0 10px; color: var(--dim); font-size: 13px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 8px; }
  button { width: 100%; text-align: left; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: var(--card); color: var(--ink); font: inherit; cursor: pointer; }
  button small { display: block; color: var(--dim); font-size: 11px; }
  button.on { border-color: var(--gold); box-shadow: 0 0 0 1px var(--gold) inset; }
  button.new { border-color: var(--new); }
  button:active { transform: translateY(1px); }
  .row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin: 8px 0; }
  input[type=range] { flex: 1; min-width: 160px; }
  code { background: #0b0d12; padding: 1px 6px; border-radius: 6px; color: var(--gold); }
</style>
</head>
<body>
<main>
<h1>신시 R34 음향 점검</h1>
<p>버튼을 누르면 게임과 같은 볼륨 비율로 들립니다. 실기기에서 들어 보고 크거나 작은 소리를 알려 주세요. 파란 테두리 = R34에서 새로 합성한 소리.</p>
<h2>환경음 루프(하나를 누르면 서로 교차 · 다시 누르면 끔)</h2>
<div class="grid" id="amb"></div>
<div class="row"><span>환경음 세기</span><input id="k" type="range" min="0" max="2" step="0.05" value="1"><span id="kv">×1.00</span></div>
<p>세기를 바꿔 마음에 드는 값을 찾으면 게임 주소 끝에 <code id="hint">?amb=1</code> 를 붙여 같은 세기로 플레이할 수 있습니다(<code>?amb=0</code> = 환경음 끔).</p>
<h2>연출 순서</h2>
<div class="grid">
  <button id="seqB">부처님의 가호<small>범종 → 0.3초 뒤 차임</small></button>
  <button id="seqT">번개 → 천둥<small>번쩍(소리 없음) 뒤 0.5초 늦게 벼락</small></button>
  <button id="seqH">전선 보스 등장<small>뿔나팔(최종 보스는 더 낮고 크게 — 두 번 이어 들려줌)</small></button>
</div>
<h2>효과음</h2>
<div class="grid" id="smp"></div>
</main>
<script>
const DATA = __DATA__;
let ac = null, master = null;
const buf = {};
let cur = null, K = 1;
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
function load(file) {
  if (!buf[file]) buf[file] = fetch("assets/sfx/" + file + ".wav").then((r) => r.arrayBuffer()).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej)));
  return buf[file];
}
function play(file, vol, rate) {
  ensure();
  return load(file).then((b) => {
    const s = ac.createBufferSource();
    s.buffer = b;
    if (rate) s.playbackRate.value = rate;
    const g = ac.createGain();
    g.gain.value = vol;
    s.connect(g);
    g.connect(master);
    s.start();
  });
}
function amb(key, file, vol, btn) {
  ensure();
  const t = ac.currentTime;
  document.querySelectorAll("#amb button").forEach((b) => b.classList.remove("on"));
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
  load(file).then((b) => {
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
  });
}
const byKey = Object.fromEntries(DATA.smp.map((x) => [x[0], x]));
const one = (k, o) => play(byKey[k][1], byKey[k][2] * ((o && o.v) || 1), o && o.r);
DATA.amb.forEach(([key, file, vol, lab]) => {
  const b = document.createElement("button");
  b.className = "new";
  b.innerHTML = lab + "<small>" + file + ".wav · 볼륨 " + vol + "</small>";
  b.onclick = () => amb(key, file, vol, b);
  document.getElementById("amb").appendChild(b);
});
DATA.smp.forEach(([key, file, vol, lab, isNew]) => {
  const b = document.createElement("button");
  if (isNew) b.className = "new";
  b.innerHTML = lab + "<small>" + file + ".wav · 볼륨 " + vol + "</small>";
  b.onclick = () => one(key);
  document.getElementById("smp").appendChild(b);
});
document.getElementById("k").oninput = (e) => {
  K = parseFloat(e.target.value);
  document.getElementById("kv").textContent = "×" + K.toFixed(2);
  document.getElementById("hint").textContent = "?amb=" + K;
  if (cur && ac) cur.g.gain.setTargetAtTime(cur.vol * K, ac.currentTime, 0.1);
};
document.getElementById("seqB").onclick = () => { one("buddhaBell"); setTimeout(() => one("buddhaChime"), 300); };
document.getElementById("seqT").onclick = () => { ensure(); setTimeout(() => one("thunder1", { v: 0.9 }), 500); };
document.getElementById("seqH").onclick = () => { one("warHorn"); setTimeout(() => one("warHorn", { r: 0.84, v: 1.15 }), 3400); };
</script>
</body>
</html>
"""
open(root + "/sound-check.html", "w", encoding="utf-8", newline="\n").write(html.replace("__DATA__", json.dumps(data, ensure_ascii=False)))
print("sound-check.html", len(data["smp"]), "효과음 ·", len(data["amb"]), "루프")
