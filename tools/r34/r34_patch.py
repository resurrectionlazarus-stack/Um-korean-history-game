#!/usr/bin/env python3
"""R34 「전장의 숨결」 — 전선 · 날씨 환경음(루프 4종 교차) · 번개 뒤 천둥 · 전선 보스 뿔나팔 · 격파 수 정합(전 시대) · 갤러리 썸네일 표식.

사용: cp shinsi-R33/index.html shinsi-R34/index.html && python3 -I tools/r34/r34_patch.py shinsi-R34/index.html
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R34] 주석으로 이유를 남긴다.
(척준경 옷 통일은 원화 보정이라 코드 패치가 아님 — tools/r34/cjg_regrade.py)
"""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 0. 갤러리 썸네일(아티팩트 카드 그림) ─────────
rep('''<title>신시(神市): 시공의 수호자들</title>''', '''<title>신시(神市): 시공의 수호자들</title>
<link rel="artifact-thumbnail" href="thumb.jpg">''')

# ───────── 1. 상수: 날씨 → 환경음 · 격파 목표 ─────────
rep('''  var R33_BG_PAR = 0.16;''', '''  var R33_BG_PAR = 0.16;
  // [R34] 날씨 → 환경음 [루프 이름, 세기]. 표에 없는 날씨(금빛 꽃가루 · 바다 안개 · 포연 · 광복의 빛)는 환경음 없음
  //  4시대 전선: 거란 폭우 · 여진 눈보라 · 몽골 황야 바람 · 개경 화염 / 1시대 빙하기 찬바람 · 3시대 전장 불티 · 5시대 2막 설원 · 6시대 폐허 바람은 약하게
  var R34_AMB_BY_WEATHER = { KHITAN_STORM: ["rain", 1], JURCHEN_BLIZZARD: ["blizzard", 1], MONGOL_ASH: ["wind", 1], FIRE_STORM: ["fire", 1], WINTER_SNOW: ["blizzard", 0.75], ASH_AND_SNOW: ["wind", 0.6], WAR_EMBERS: ["fire", 0.5], ASH_DIAGONAL: ["wind", 0.6], RUIN_ASH: ["wind", 0.5] };
  // [R34] 상단 '격파 N/M'의 M = 그 시대에 계획된 적 수(웨이브 + 중간보스 · 호위 2 + 정예) — 옛 고정값(requiredKills)은 R29 · R31 · R33 웨이브 개편 뒤 맞지 않았다(4시대 52 ↔ 실제 67).
  //  보스가 부르는 증원 · 6시대 기수 장교처럼 계획 밖의 적은 세지 않는다 → 표시는 min(격파, M)/M
  var R34_KILL_GOAL = {};
  var eraKillGoal = (era) => {
    if (R34_KILL_GOAL[era] != null) return R34_KILL_GOAL[era];
    let k = 0;
    for (let zi = 0; zi < 4; zi++) {
      if (zi === 3 && era !== 4) continue;
      const pal = getPaleolithicWaveQueue(zi, era);
      const w = pal ? pal.map((x) => x.length) : era === 4 ? ERA4_ZONE_WAVES[zi] || [] : era === 2 ? ERA2_ZONE_WAVES[zi] || [] : (ZONE_WAVES[zi] || []).map((q) => q + (era >= 4 ? 1 : 0));
      for (let i = 0; i < w.length; i++) k += w[i];
      if (era === 2 && zi === 2) k += w.length + 1;
      if (era >= 2 && midbossFor(era, zi)) k += 3;
    }
    if (era === 1) k += 1;
    return R34_KILL_GOAL[era] = k;
  };''')

# ───────── 2. 효과음 표: 천둥 2 · 뿔나팔 ─────────
rep('''gunPistol: "gun_pistol_crisp", gunRifle: "gun_rifle_heavy" };''', '''gunPistol: "gun_pistol_crisp", gunRifle: "gun_rifle_heavy", thunder1: "thunder_crack_1", thunder2: "thunder_roll_2", warHorn: "war_horn_call" };''')
rep('''gunPistol: 0.7, gunRifle: 0.85 };''', '''gunPistol: 0.7, gunRifle: 0.85, thunder1: 0.8, thunder2: 0.75, warHorn: 0.62 };''')
rep('''gunPistol: 3, gunRifle: 1 };''', '''gunPistol: 3, gunRifle: 1, thunder1: 1, thunder2: 1, warHorn: 1 };''')
rep('''gunPistol: "shot", gunRifle: "explosion" };''', '''gunPistol: "shot", gunRifle: "explosion", thunder1: "stomp", thunder2: "stomp", warHorn: "" };''')

# ───────── 3. 환경음 엔진(루프 교차) ─────────
rep('''        for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
        loadSamples();''', '''        for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
        loadSamples();
        loadAmb();''')
rep('''    return {
      unlock() {
        if (ensure() && ac.state === "suspended") ac.resume();
      },''', '''    // [R34] 환경음 — 끝과 처음이 이어지게 합성한 루프 WAV 4종(tools/r34/synth_audio.py)을 전선 · 날씨에 맞춰 약 1.6초 교차.
    //  마스터 볼륨 · 음소거를 그대로 따르고, 받기 · 디코딩에 실패하면 조용히 없음. ?amb=0 끄기 · ?amb=0.5~2 세기 조절(실기기 볼륨 맞춤용)
    const AMB = { rain: "amb_rain_loop", blizzard: "amb_blizzard_loop", wind: "amb_wind_loop", fire: "amb_fire_loop" };
    const AMB_VOL = { rain: 0.24, blizzard: 0.28, wind: 0.28, fire: 0.26 };
    const AMB_K = (() => {
      try {
        const q = readQuery().get("amb");
        if (q == null || q === "") return 1;
        const v = parseFloat(q);
        return isFinite(v) ? Math.max(0, Math.min(2, v)) : 1;
      } catch (e) {
        return 1;
      }
    })();
    const ambBuf = {};
    const ambStat = { loaded: 0, failed: 0, cur: null, vol: 0, starts: 0, log: [] };
    let ambCur = null;
    let ambWant = null;
    const ambApply = () => {
      if (!ac) return;
      const w = ambWant;
      const t = ac.currentTime;
      if (ambCur && (!w || w.name !== ambCur.name)) {
        const old = ambCur;
        try {
          old.gn.gain.cancelScheduledValues(t);
          old.gn.gain.setValueAtTime(old.gn.gain.value, t);
          old.gn.gain.linearRampToValueAtTime(0, t + 1.4);
          old.src.stop(t + 1.5);
        } catch (e) {
        }
        ambCur = null;
        ambStat.cur = null;
        ambStat.vol = 0;
      }
      if (!w) return;
      const target = (AMB_VOL[w.name] || 0.25) * w.vol * AMB_K;
      if (ambCur) {
        if (Math.abs(ambCur.vol - target) > 1e-3) {
          ambCur.gn.gain.cancelScheduledValues(t);
          ambCur.gn.gain.setValueAtTime(ambCur.gn.gain.value, t);
          ambCur.gn.gain.linearRampToValueAtTime(target, t + 0.8);
          ambCur.vol = ambStat.vol = target;
        }
        return;
      }
      const b = ambBuf[w.name];
      if (!b) return;
      const src = ac.createBufferSource();
      src.buffer = b;
      src.loop = true;
      const gn = ac.createGain();
      gn.gain.setValueAtTime(0, t);
      gn.gain.linearRampToValueAtTime(target, t + 1.6);
      src.connect(gn);
      gn.connect(master);
      src.start(t, Math.random() * b.duration);
      ambCur = { name: w.name, src, gn, vol: target };
      ambStat.cur = w.name;
      ambStat.vol = target;
      ambStat.starts++;
      if (ambStat.log.length < 40) ambStat.log.push(w.name);
    };
    const loadAmb = () => {
      if (smpOff || AMB_K <= 0 || !ac || typeof fetch !== "function") return;
      Object.keys(AMB).forEach((key) => {
        fetch(`assets/sfx/${AMB[key]}.wav`).then((r) => r.ok ? r.arrayBuffer() : Promise.reject(new Error(String(r.status)))).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej))).then((b) => {
          ambBuf[key] = b;
          ambStat.loaded++;
          if (ambWant && ambWant.name === key) ambApply();
        }).catch(() => {
          ambStat.failed++;
        });
      });
    };
    return {
      unlock() {
        if (ensure() && ac.state === "suspended") ac.resume();
      },
      // [R34] 환경음 요청 — amb("rain", 1) · amb(null) = 천천히 끔. 같은 요청은 아무 일도 하지 않으므로 매 프레임 불러도 된다
      amb(name, vol) {
        if (smpOff || AMB_K <= 0) return;
        const nm = name && AMB[name] ? name : null;
        const v = vol == null ? 1 : vol;
        if ((ambWant ? ambWant.name : null) === nm && (!nm || Math.abs(ambWant.vol - v) < 1e-3)) return;
        ambWant = nm ? { name: nm, vol: v } : null;
        ambApply();
      },
      get ambStats() {
        return { ...ambStat, log: ambStat.log.slice(), want: ambWant ? ambWant.name : null, wantVol: ambWant ? ambWant.vol : 0, off: smpOff || AMB_K <= 0, k: AMB_K };
      },''')

# ───────── 4. 날씨 종류 기억 → 환경음이 날씨를 따라감 ─────────
rep('''      arr.style = cfg.style || null;
      return arr;''', '''      arr.style = cfg.style || null;
      // [R34] 이 날씨의 종류(환경음 고르기용)
      arr.wt = WEATHER_CFG[eObj.weatherType] ? eObj.weatherType : "ASH_AND_SNOW";
      return arr;''')
rep('''      const syncBgm = (g, state2) => {
        const S = sfxRef.current;
        if (!S) return;''', '''      const syncBgm = (g, state2) => {
        const S = sfxRef.current;
        if (!S) return;
        // [R34] 환경음 — 전투 중에만, 지금 날씨에 맞춰(일시정지 · 시험 · 타이틀에서는 천천히 끔). 부처님의 가호 동안은 낮춰서 범종 · 차임이 또렷하게
        if (S.amb) {
          const AW = state2 === "PLAYING" && g.weatherMotes ? R34_AMB_BY_WEATHER[g.weatherMotes.wt] : null;
          S.amb(AW ? AW[0] : null, AW ? AW[1] * (g.buddhaFx ? 0.35 : 1) : 1);
        }''')

# ───────── 5. 번개 뒤 천둥 · 전선 보스 뿔나팔 ─────────
rep('''            if ((g.r33bolts & 1) === 1) sfx("stomp");''', '''            // [R34] 번개가 번쩍인 뒤 0.25~0.75초 늦게 천둥 — 가까운 벼락 · 먼 우르릉을 번갈아(빛이 먼저, 소리가 나중)
            const thName = g.r33bolts & 1 ? "thunder1" : "thunder2";
            const thVol = 0.75 + LB.seed % 26 / 100;
            setTimeout(() => sfx(thName, { v: thVol }), 250 + LB.seed % 500);''')
rep('''      (g.r33bossLog || (g.r33bossLog = [])).push({ key: M.key, ev: "spawn", tick: g.tick });
    };''', '''      (g.r33bossLog || (g.r33bossLog = [])).push({ key: M.key, ev: "spawn", tick: g.tick });
      // [R34] 전선 보스 등장 = 포효 뒤 뿔나팔 한 번 길게
      addTimer(20, () => sfx("warHorn"));
    };''')
rep('''              spawnEraBoss();
              (g.r33bossLog || (g.r33bossLog = [])).push({ key: "paduban", ev: "spawn", tick: g.tick });''', '''              spawnEraBoss();
              (g.r33bossLog || (g.r33bossLog = [])).push({ key: "paduban", ev: "spawn", tick: g.tick });
              // [R34] 최종 보스 파두반 = 더 낮고 크게 우는 뿔나팔
              addTimer(24, () => sfx("warHorn", { r: 0.84, v: 1.15 }));''')

# ───────── 6. 격파 수 정합(HUD) ─────────
rep('''            kills: st.kills,''', '''            kills: st.kills,
            killGoal: eraKillGoal(g.era),''')
rep('''hud.kills, "/", eraData.requiredKills''', '''Math.min(hud.kills, hud.killGoal || eraData.requiredKills), "/", hud.killGoal || eraData.requiredKills''')

# ───────── 7. 검증용 DEV 훅 ─────────
rep('''          // [R33] 검증용 — 전선 배경 강제(0~3 · null = 구역 따라) · 상태 · 전선 보스 즉시 소환 · 최종 보스 소환''', '''          // [R34] 검증용 — 환경음 상태 · 지금 날씨 종류 · 시대별 격파 목표
          r34: () => ({ amb: sfxRef.current ? sfxRef.current.ambStats : null, wt: gameRef.current.weatherMotes ? gameRef.current.weatherMotes.wt || null : null, goals: [1, 2, 3, 4, 5, 6].map((e) => eraKillGoal(e)), kills: gameRef.current.stats.kills }),
          // [R33] 검증용 — 전선 배경 강제(0~3 · null = 구역 따라) · 상태 · 전선 보스 즉시 소환 · 최종 보스 소환''')

open(P, "w", encoding="utf-8").write(s)
print("R34 patch ok —", n, "edits")
