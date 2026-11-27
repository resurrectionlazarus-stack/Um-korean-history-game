#!/usr/bin/env python3
"""R34 음향 점검 페이지(sound-check.html) 만들기 — index.html의 효과음 표(SMP · SMP_VOL · AMB · AMB_VOL)를 읽어
게임과 같은 볼륨 비율(마스터 0.5 · 컴프레서 같음)로 한 개씩 들어 볼 수 있는 정적 페이지를 만든다. 실기기에서 볼륨을 맞출 때 쓴다.
사용: python3 -I tools/r34/make_sound_check.py <빌드 폴더> [아티팩트 게시용 출력 html]"""
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
HEAD = """<title>신시 음향 점검</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
  /* 한 줄 배치: 좁은 한 단 · 버튼 격자(폭이 좁아지면 한 줄에 하나) — 게임의 먹빛 화면을 따라 어두운 쪽이 기본 */
  :root { color-scheme: dark; --bg: #0f1218; --card: #1a1f2a; --line: #2c3444; --ink: #e8e6df; --dim: #9aa3b5; --gold: #fbbf24; --new: #38bdf8; --code: #0b0d12;
    --font: system-ui, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif; }
  @media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) { color-scheme: light; --bg: #eef0f3; --card: #ffffff; --line: #cfd5de; --ink: #161a22; --dim: #586174; --gold: #9a5b00; --new: #0b6aa8; --code: #e3e7ed; } }
  :root[data-theme="light"] { color-scheme: light; --bg: #eef0f3; --card: #ffffff; --line: #cfd5de; --ink: #161a22; --dim: #586174; --gold: #9a5b00; --new: #0b6aa8; --code: #e3e7ed; }
  * { box-sizing: border-box; }
  body { margin: 0; padding-block: 16px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); background: var(--bg); color: var(--ink); font: 15px/1.5 var(--font); }
  main { max-width: 760px; margin: 0 auto; }
  h1 { font-size: 20px; margin: 4px 0; color: var(--gold); text-wrap: balance; }
  h2 { font-size: 15px; margin: 22px 0 8px; color: var(--dim); font-weight: 600; }
  p { margin: 4px 0 10px; color: var(--dim); font-size: 13px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(220px, 100%), 1fr)); gap: 8px; }
  button { width: 100%; min-width: 0; text-align: left; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: var(--card); color: var(--ink); font: inherit; cursor: pointer; }
  button small { display: block; color: var(--dim); font-size: 11px; overflow-wrap: anywhere; }
  button.on { border-color: var(--gold); box-shadow: 0 0 0 1px var(--gold) inset; }
  button.new { border-color: var(--new); }
  button:focus-visible, input:focus-visible { outline: 2px solid var(--gold); outline-offset: 2px; }
  button:active { transform: translateY(1px); }
  @media (prefers-reduced-motion: reduce) { button:active { transform: none; } }
  .row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin: 8px 0; }
  input[type=range] { flex: 1; min-width: 160px; accent-color: var(--gold); }
  #kv { font-variant-numeric: tabular-nums; }
  code { background: var(--code); padding: 1px 6px; border-radius: 6px; color: var(--gold); }
</style>
"""
BODY = """<main>
<h1>신시 R34 음향 점검</h1>
<p>버튼을 누르면 게임과 같은 볼륨 비율로 들립니다. 실기기에서 들어 보고 크거나 작은 소리를 알려 주세요. 파란 테두리는 R34에서 새로 합성한 소리입니다.</p>
<h2>환경음 루프 (누르면 서로 교차, 다시 누르면 끔)</h2>
<div class="grid" id="amb"></div>
<div class="row"><label for="k">환경음 세기</label><input id="k" type="range" min="0" max="2" step="0.05" value="1"><span id="kv">×1.00</span></div>
<p>마음에 드는 세기를 찾으면 게임 주소 끝에 <code id="hint">?amb=1</code> 를 붙여 같은 세기로 플레이할 수 있습니다. <code>?amb=0</code> 은 환경음 끔입니다.</p>
<h2>연출 순서</h2>
<div class="grid">
  <button id="seqB" type="button">부처님의 가호<small>범종, 0.3초 뒤 차임</small></button>
  <button id="seqT" type="button">번개 뒤 천둥<small>0.5초 늦게 가까운 벼락</small></button>
  <button id="seqH" type="button">전선 보스 등장<small>뿔나팔, 이어서 최종 보스용(더 낮고 크게)</small></button>
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
  }).catch(() => {});
}
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
  }).catch(() => {});
}
const byKey = Object.fromEntries(DATA.smp.map((x) => [x[0], x]));
const one = (k, o) => play(byKey[k][1], byKey[k][2] * ((o && o.v) || 1), o && o.r);
const mk = (id, cls, lab, file, vol) => {
  const b = document.createElement("button");
  b.type = "button";
  b.id = id;
  if (cls) b.className = cls;
  b.append(lab);
  const sm = document.createElement("small");
  sm.textContent = file + ".wav · 볼륨 " + vol;
  b.append(sm);
  return b;
};
DATA.amb.forEach(([key, file, vol, lab]) => {
  const b = mk("amb-" + key, "new", lab, file, vol);
  b.setAttribute("aria-pressed", "false");
  b.onclick = () => amb(key, file, vol, b);
  document.getElementById("amb").appendChild(b);
});
DATA.smp.forEach(([key, file, vol, lab, isNew]) => {
  const b = mk("smp-" + key, isNew ? "new" : "", lab, file, vol);
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
"""
dj = json.dumps(data, ensure_ascii=False)
# ① 배포 폴더용(혼자 서는 완전한 HTML) ② 아티팩트 게시용(머리 · 몸통 뼈대 없이 내용만 — 게시할 때 뼈대가 씌워짐)
full = '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + HEAD + '</head>\n<body>\n' + BODY.replace("__DATA__", dj) + '</body>\n</html>\n'
open(root + "/sound-check.html", "w", encoding="utf-8", newline="\n").write(full)
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(HEAD + BODY.replace("__DATA__", dj))
print("sound-check.html", len(data["smp"]), "효과음 ·", len(data["amb"]), "루프", "· 아티팩트용" if len(sys.argv) > 2 else "")
