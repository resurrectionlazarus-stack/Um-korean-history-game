#!/usr/bin/env python3
"""R35 「손맛과 가락」 — 오너 직접 피드백 3건: ① 무기 쥔 손 ② 타격음(칼 = 베는 소리 · 둔기 = 바위 깨는 소리) ③ 시대별 배경음악.

사용: cp shinsi-R(이전)/index.html shinsi-R35/index.html && python3 -I tools/r35/r35_patch.py shinsi-R35/index.html
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R35] 주석으로 이유를 남긴다.
주의: 옛 코드의 한글은 \\uXXXX 이스케이프로 저장돼 있다. 그런 문구를 찾을 땐 esc("한글")을 쓴다
      (도구 입력에 역슬래시-u-16진수를 직접 쓰면 실제 글자로 바뀌어 버림 — chr(92)로 만드는 이유).
"""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0
B = chr(92)


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


def esc(t):
    """실제 글자 → 파일 속 이스케이프 표기(옛 부분 한글 찾기용)."""
    return "".join(B + "u%04X" % ord(c) if ord(c) > 127 else c for c in t)


# ───────── 1. 무기 궤적: 휘두르는 도중 방향을 바꾸면 끊기 ─────────
#  (좌우 그리기는 171쌍 비교로 정확히 대칭임을 확인 — 어긋남은 없었고, 방향 전환 순간에만 오른쪽 끝 ↔ 왼쪽 끝을 잇는 가로 띠가 1~2프레임 보였다)
rep('''        if (!atk) p._wBreak = true;
        if (atk) {
          const prev = p._wLastF;''', '''        if (!atk) p._wBreak = true;
        // [R35] 휘두르는 도중 방향 전환 = 궤적 끊기(앞 방향의 궤적 · 보간 기준을 버림) — 몸을 가로지르는 띠가 생기지 않게
        if (p._wFace !== p.facing) {
          if (p._wFace != null) {
            WT.length = 0;
            p._wLastF = null;
            p._wBreak = true;
            g.r35TrailCut = (g.r35TrailCut || 0) + 1;
          }
          p._wFace = p.facing;
        }
        if (atk) {
          const prev = p._wLastF;''')

# ───────── 2. 타격음: 무기 종류별 새 소리(칼 = 베는 소리 · 둔기 = 바위 깨는 소리 · 창 = 찌르는 소리) ─────────
#  예전 타격음은 에너지의 65~76%가 4.8kHz 위(또는 77%가 300Hz 아래) → 휴대폰에서 '탁탁'(전기 모기채). 새 소리는 300~2400Hz가 46~83%.
#  더는 쓰지 않는 예전 8종(slice_crisp_1/2 · blade_slash_1/2 · hit_heavy · slice_flesh_sever · slice_flurry_multi · blade_armor_cleave)은
#  파일은 남기되(음향 점검 페이지의 '예전 ↔ 새' 비교용) 게임에서는 받지 않는다.
rep('''sliceCrisp1: "slice_crisp_1", sliceCrisp2: "slice_crisp_2", sliceSever: "slice_flesh_sever", sliceFlurry: "slice_flurry_multi", missionGong: "mission_clear_gong", bombBlast: "bomb_uiyeol_blast", buddhaBell: "buddha_temple_bell", buddhaChime: "buddha_mystic_chime", bladeSlash1: "blade_slash_1", bladeSlash2: "blade_slash_2", bladeArmor: "blade_armor_cleave", dragonRoar:''',
    '''missionGong: "mission_clear_gong", bombBlast: "bomb_uiyeol_blast", buddhaBell: "buddha_temple_bell", buddhaChime: "buddha_mystic_chime", cutLight1: "cut_light_1", cutLight2: "cut_light_2", cutLight3: "cut_light_3", cutHeavy: "cut_heavy", cutSever: "cut_sever", cutArmor: "cut_armor", cutFlurry: "cut_flurry", rockHit1: "rock_hit_1", rockHit2: "rock_hit_2", rockHeavy: "rock_heavy", rockCrush: "rock_crush", stab1: "stab_1", stab2: "stab_2", whooshBlade: "whoosh_blade", whooshHeavy: "whoosh_heavy", dragonRoar:''')
rep('''const SMP = { slashLight: "slash_light", hitHeavy: "hit_heavy", breath:''', '''const SMP = { slashLight: "slash_light", breath:''')
rep('''gunPistol: 0.7, gunRifle: 0.85, thunder1: 0.8, thunder2: 0.75, warHorn: 0.62 };''',
    '''gunPistol: 0.7, gunRifle: 0.85, thunder1: 0.8, thunder2: 0.75, warHorn: 0.62, cutLight1: 0.74, cutLight2: 0.74, cutLight3: 0.74, cutHeavy: 0.92, cutSever: 0.88, cutArmor: 0.82, cutFlurry: 0.9, rockHit1: 0.84, rockHit2: 0.84, rockHeavy: 0.98, rockCrush: 1, stab1: 0.78, stab2: 0.78, whooshBlade: 0.3, whooshHeavy: 0.36 };''')
rep('''gunPistol: 3, gunRifle: 1, thunder1: 1, thunder2: 1, warHorn: 1 };''',
    '''gunPistol: 3, gunRifle: 1, thunder1: 1, thunder2: 1, warHorn: 1, cutLight1: 2, cutLight2: 2, cutLight3: 2, cutHeavy: 2, cutSever: 2, cutArmor: 2, cutFlurry: 1, rockHit1: 2, rockHit2: 2, rockHeavy: 2, rockCrush: 1, stab1: 2, stab2: 2, whooshBlade: 2, whooshHeavy: 2 };''')
rep('''bladeSlash1: 0.06, bladeSlash2: 0.06, bladeArmor: 0.03, gunPistol: 0.05 };''',
    '''bladeSlash1: 0.06, bladeSlash2: 0.06, bladeArmor: 0.03, gunPistol: 0.05, cutLight1: 0.06, cutLight2: 0.06, cutLight3: 0.06, cutHeavy: 0.03, cutSever: 0.04, cutArmor: 0.04, rockHit1: 0.06, rockHit2: 0.06, rockHeavy: 0.03, rockCrush: 0.02, stab1: 0.06, stab2: 0.06, whooshBlade: 0.09, whooshHeavy: 0.08 };''')
rep('''gunRifle: "explosion", thunder1: "stomp", thunder2: "stomp", warHorn: "" };''',
    '''gunRifle: "explosion", thunder1: "stomp", thunder2: "stomp", warHorn: "", cutLight1: "hit", cutLight2: "hit", cutLight3: "hit", cutHeavy: "crit", cutSever: "crit", cutArmor: "crit", cutFlurry: "crit", rockHit1: "hit", rockHit2: "hit", rockHeavy: "crit", rockCrush: "crit", stab1: "hit", stab2: "hit", whooshBlade: "swing", whooshHeavy: "swing" };''')
# 합성음(샘플을 못 쓸 때 · 탄환 등): 삑 소리(사각파 880Hz)를 빼고 중역 몸통을 넣는다
rep('''      hit: () => {
        noise(0.08, 0.46, "lowpass", 900, 220);
        tone("sine", 165, 55, 0.11, 0.48);
      },
      crit: () => {
        noise(0.1, 0.52, "lowpass", 1400, 200);
        tone("sine", 210, 48, 0.14, 0.58);
        tone("square", 880, 320, 0.09, 0.1);
        tone("sawtooth", 240, 72, 0.12, 0.08);
      },''', '''      // [R35] 합성 타격음도 '탁'이 아니라 몸통이 있게: 중역 잡음(1.5k → 500Hz)을 훑어 내리고 삑 소리(사각파)는 뺀다
      hit: () => {
        noise(0.12, 0.4, "bandpass", 1500, 480, 0.9);
        noise(0.06, 0.3, "lowpass", 900, 220);
        tone("sine", 190, 70, 0.12, 0.42);
      },
      crit: () => {
        noise(0.18, 0.48, "bandpass", 2200, 500, 0.8);
        noise(0.09, 0.34, "lowpass", 1400, 200);
        tone("sine", 210, 58, 0.16, 0.52);
        tone("triangle", 420, 150, 0.13, 0.16);
      },''')
# 무기 종류별 타격음 고르기
rep('''    const sfx = (name, o) => sfxRef.current && sfxRef.current.play(name, o);
''', '''    const sfx = (name, o) => sfxRef.current && sfxRef.current.play(name, o);
    // [R35] 무기 종류별 타격음 — 칼(2~6시대): 베는 소리 · 둔기(1시대 주먹도끼 · 간돌도끼): 바위 깨는 소리 · 창(1시대 슴베찌르개): 찌르는 소리
    //  lv = "light"(1~3타) · "heavy"(4타 · 강타) · "crush"(내려찍기) · "sever"(양단 막타) · "armor"(갑옷 · 방패) · "flurry"(연참) · "gun"(탄환)
    const r35HitSnd = (lv, o) => {
      const g = gameRef.current;
      const cls = heroWeaponClass(g.era, g.stats.weaponTier || 1);
      const n = g._r35alt = ((g._r35alt || 0) + 1) % 6;
      let name;
      if (lv === "gun") name = n % 2 ? "stab1" : "stab2";
      else if (cls === "AXE") name = lv === "light" ? n % 2 ? "rockHit1" : "rockHit2" : lv === "crush" || lv === "sever" ? "rockCrush" : "rockHeavy";
      else if (cls === "SPEAR") name = lv === "light" ? n % 2 ? "stab1" : "stab2" : lv === "armor" ? "cutArmor" : lv === "sever" ? "cutSever" : lv === "flurry" ? "cutFlurry" : "cutHeavy";
      else name = lv === "light" ? "cutLight" + (n % 3 + 1) : lv === "sever" ? "cutSever" : lv === "armor" ? "cutArmor" : lv === "flurry" ? "cutFlurry" : "cutHeavy";
      const L = g.r35snd || (g.r35snd = {});
      L[name] = (L[name] || 0) + 1;
      sfx(name, lv === "gun" ? { v: 0.8, r: 1.18 } : o);
    };
    // 휘두르는 바람: 둔기는 낮게(부웅) · 칼 · 창은 가늘게(휙)
    const r35Whoosh = () => {
      const g = gameRef.current;
      sfx(heroWeaponClass(g.era, g.stats.weaponTier || 1) === "AXE" ? "whooshHeavy" : "whooshBlade");
    };
''')
rep('''            sfx("sliceSever");''', '''            r35HitSnd("sever");''')
rep('''        if (isCounter) sfx("counter");
        else if (target === g.boss || g._comboStep >= (e2 ? 3 : 4)) sfx("hitHeavy", e2 ? R31_E2_HEAVY_SND : null);
        else if (g._comboStep >= 1) sfx((g._r31alt = !g._r31alt) ? g.era === 4 ? "bladeSlash1" : "sliceCrisp1" : g.era === 4 ? "bladeSlash2" : "sliceCrisp2");
        else sfx(dealtCrit ? "crit" : "hit");''', '''        // [R35] 무기 종류별 새 타격음: 앞 타 = 가벼운 소리(타수가 오를수록 조금 크게 · 낮게) · 연타의 마지막 타 = 강타 ·
        //  방패 · 갑옷 몹 = 쇠 울림 · 보스 = 같은 소리를 조금 더 낮고 크게(예전에는 보스를 칠 때마다 저음뿐인 강타음 → 휴대폰에서 '탁')
        //  연타가 아닌 타격(동료 요정 · 투사체 · 기술): 여러 번 치는 큰 기술만 강타음, 나머지는 가벼운 소리(치명타라고 매번 '쾅' 하지 않게)
        const big = target === g.boss || target.isMidBoss;
        const cs = g._comboStep || 0;
        // 강타 = 연타의 마지막 타(피니시를 배우기 전에는 3타, 배운 뒤에는 4타) · 2시대는 3타부터
        const lastStep = e2 || st.level < SKILL_LV.finisher ? 3 : 4;
        if (isCounter) sfx("counter");
        else if (g._r31gun) r35HitSnd("gun");
        else if (cs >= lastStep) r35HitSnd("heavy", e2 ? R31_E2_HEAVY_SND : big ? { v: 1.08, r: 0.95 } : null);
        else if (!big && (target.guardRate > 0 || heavy)) r35HitSnd("armor");
        else if (cs >= 1) r35HitSnd("light", { v: (big ? 1.08 : 0.92) + cs * 0.05, r: (big ? 0.95 : 1.03) - cs * 0.02 });
        else r35HitSnd(hitCount >= 2 ? "heavy" : "light", hitCount >= 2 ? { v: 0.9 } : dealtCrit ? { v: 1, r: 0.95 } : { v: 0.85 });''')
rep('''            addTrauma(0.14);
            sfx("hitHeavy");''', '''            addTrauma(0.14);
            sfx("rockHit2", { r: 0.86 });''')
rep('''      sfx("sliceFlurry");
      if (g.era === 4) r33Storm();''', '''      r35HitSnd("flurry");
      if (g.era === 4) r33Storm();''')
rep('''      sfx("hitHeavy");
      g.airRaids = (g.airRaids || 0) + 1;''', '''      r35HitSnd("crush");
      g.airRaids = (g.airRaids || 0) + 1;''')
rep('''      sfx("bladeArmor");
      addTrauma(0.18);''', '''      sfx("cutArmor", { v: 1.1 });
      addTrauma(0.18);''')
rep('''        sfx("hitHeavy", R31_E2_HEAVY_SND);''', '''        r35HitSnd("heavy", R31_E2_HEAVY_SND);''')
rep('''      sfx("breath");
      sfx("sliceFlurry");''', '''      sfx("breath");
      r35HitSnd("flurry");''')
rep('''        sfx("hitHeavy");
        g2.slowMo = Math.max(g2.slowMo || 0, 16);''', '''        r35HitSnd("heavy");
        g2.slowMo = Math.max(g2.slowMo || 0, 16);''')
rep('''      const eObj = relicPal(g, eraObjOf());
      sfx("swing");
      if (p.y > 10) {''', '''      const eObj = relicPal(g, eraObjOf());
      r35Whoosh();
      if (p.y > 10) {''')

# ───────── 3. 시대 배경음악: 미리 구운 mp3(국악기 · 군악대 합성)를 이음매 없이 반복 ─────────
#  곡마다 A(전장) · B(보스전) 두 구간. 구간 위치는 tools/r35/bgm_meta.json(bgm_render.py가 씀)에서 읽어 표로 넣는다.
import json as _json
import os as _os

_meta = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bgm_meta.json"), encoding="utf-8"))
_rows = []
for _k, _v in sorted(_meta.items(), key=lambda kv: kv[1]["era"]):
    _rows.append('    %d: { f: "%s", t: "%s", a: [%s, %s], b: [%s, %s] }' % (_v["era"], _k, esc(_v["title"]), _v["a"][0], _v["a"][1], _v["b"][0], _v["b"][1]))
_tail = sorted(set(v["tail"] for v in _meta.values()))
assert len(_tail) == 1
BGM_TABLE = "  var R35_BGM = {\n" + ",\n".join(_rows) + "\n  };\n  var R35_BGM_TAIL = %s;\n" % _tail[0]

rep('''  function createSfxEngine() {
''', '''  // [R35] 시대 배경음악 — tools/r35/bgm_render.py가 합성해 구운 mp3(assets/bgm). f = 파일 · t = 곡 이름 · a = 전장 구간[시작, 길이](초) · b = 보스전 구간.
  //  시작 = 파일 맨 앞 '표지음'(2ms 삑, 재생하지 않음) 봉우리에서 잰 시각 → mp3 디코더마다 다른 앞쪽 지연을 기기에서 스스로 보정한다.
''' + BGM_TABLE + '''  //  반복: 구간 몸통 길이마다 새 소스를 정확한 시각에 겹쳐 튼다(앞 바퀴의 꼬리 = 잔향이 다음 바퀴 처음과 겹쳐 이음매가 없다).
  function createFileBgm(ac, destination, opts = {}) {
    const out = ac.createGain();
    out.gain.value = opts.volume != null ? opts.volume : 0.34;
    out.connect(destination);
    const cache = {};
    const stats = { loaded: 0, failed: 0, starts: 0, loops: 0, era: 0, sec: null, rate: 1, marks: {}, log: [] };
    let cur = null;
    let paused = null;
    const findMark = (buf) => {
      const d = buf.getChannelData(0);
      const n = Math.min(d.length, Math.floor(buf.sampleRate * 0.3));
      let pv = 0;
      let pi = 0;
      for (let i = 0; i < n; i++) {
        const v = d[i] < 0 ? -d[i] : d[i];
        if (v > pv) {
          pv = v;
          pi = i;
        }
      }
      return pi / buf.sampleRate;
    };
    const load = (era) => {
      const T = R35_BGM[era];
      if (!T || cache[era] || typeof fetch !== "function") return;
      const c = cache[era] = { state: "loading", buf: null, t0: 0 };
      fetch(`assets/bgm/${T.f}.mp3`).then((r) => r.ok ? r.arrayBuffer() : Promise.reject(new Error(String(r.status)))).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej))).then((b) => {
        c.buf = b;
        c.t0 = findMark(b);
        c.state = "ready";
        stats.loaded++;
        stats.marks[era] = Math.round(c.t0 * 1e4) / 1e4;
        if (opts.onReady) opts.onReady(era);
      }).catch(() => {
        c.state = "failed";
        stats.failed++;
      });
    };
    // 디코딩한 곡은 지금 시대 + 다음 시대만 들고 있는다(곡 하나 ≈ 10MB)
    const prune = (era) => {
      Object.keys(cache).forEach((k) => {
        const e = +k;
        if (e !== era && e !== era + 1 && cache[k].state !== "loading") delete cache[k];
      });
    };
    const posNow = (c) => {
      const p = c.refPos + (ac.currentTime - c.refT) * c.rate;
      return (p % c.len + c.len) % c.len;
    };
    const startIter = (c, when, pos) => {
      const src = ac.createBufferSource();
      src.buffer = c.buf;
      src.playbackRate.value = c.rate;
      src.connect(c.bus);
      src.start(when, c.t0 + c.start + pos, c.len - pos + R35_BGM_TAIL);
      c.srcs.push(src);
      src.onended = () => {
        const i = c.srcs.indexOf(src);
        if (i >= 0) c.srcs.splice(i, 1);
        try {
          src.disconnect();
        } catch (e) {
        }
      };
    };
    const pump = () => {
      const c = cur;
      if (!c) return;
      const now = ac.currentTime;
      if (c.nextT < now - 0.5) c.nextT = now + 0.05;
      while (c.nextT < now + 0.7) {
        startIter(c, c.nextT, 0);
        c.nextT += c.len / c.rate;
        stats.loops++;
      }
    };
    const kill = (c, sec) => {
      if (!c) return;
      if (c.timer) clearInterval(c.timer);
      c.timer = null;
      const t = ac.currentTime;
      try {
        c.bus.gain.cancelScheduledValues(t);
        c.bus.gain.setValueAtTime(c.bus.gain.value, t);
        c.bus.gain.linearRampToValueAtTime(1e-4, t + Math.max(0.02, sec));
      } catch (e) {
      }
      const srcs = c.srcs.slice();
      setTimeout(() => {
        srcs.forEach((s) => {
          try {
            s.stop();
          } catch (e) {
          }
        });
        try {
          c.bus.disconnect();
        } catch (e) {
        }
      }, (sec + 0.15) * 1e3);
    };
    const begin = (era, sec, pos, rate, fadeIn) => {
      const T = R35_BGM[era];
      const C = cache[era];
      const seg = T[sec];
      const bus = ac.createGain();
      const t = ac.currentTime;
      bus.gain.setValueAtTime(1e-4, t);
      bus.gain.linearRampToValueAtTime(1, t + fadeIn);
      bus.connect(out);
      const c = { era, sec, bus, buf: C.buf, t0: C.t0, start: seg[0], len: seg[1], rate, srcs: [], timer: null, refT: t + 0.05, refPos: pos, nextT: 0 };
      startIter(c, t + 0.05, pos);
      c.nextT = t + 0.05 + (c.len - pos) / rate;
      c.timer = setInterval(pump, 200);
      cur = c;
      paused = null;
      stats.starts++;
      stats.era = era;
      stats.sec = sec;
      stats.rate = rate;
      if (stats.log.length < 60) stats.log.push(era + sec + (pos > 0.01 ? "@" + Math.round(pos) : ""));
    };
    return {
      load,
      ready: (era) => !!(cache[era] && cache[era].state === "ready"),
      // 틀 수 있으면(곡이 준비됐으면) true. 아직이면 받아 두기만 하고 false → 부르는 쪽이 예전 합성 BGM으로 잇는다
      play(era, sec) {
        if (!R35_BGM[era]) return false;
        load(era);
        if (!cache[era] || cache[era].state !== "ready") return false;
        if (cur && cur.era === era && cur.sec === sec) return true;
        const had = !!cur;
        kill(cur, 0.4);
        cur = null;
        begin(era, sec, 0, 1, had ? 0.35 : 0.15);
        prune(era);
        load(era + 1);
        return true;
      },
      stop(sec = 0.3) {
        kill(cur, sec);
        cur = null;
        paused = null;
        stats.sec = null;
      },
      pause() {
        if (!cur) return;
        paused = { era: cur.era, sec: cur.sec, pos: posNow(cur), rate: cur.rate };
        kill(cur, 0.05);
        cur = null;
      },
      resume() {
        if (!paused || cur) return;
        const p = paused;
        if (cache[p.era] && cache[p.era].state === "ready") begin(p.era, p.sec, p.pos, p.rate, 0.12);
        paused = null;
      },
      // 보스 광폭화: 같은 자리에서 빠르기(= 음높이)만 올려 다시 잇는다
      setTempo(m) {
        if (!cur || Math.abs(cur.rate - m) < 1e-3) return;
        const c = cur;
        const pos = posNow(c);
        kill(c, 0.12);
        cur = null;
        begin(c.era, c.sec, pos, m, 0.12);
      },
      setVolume(v) {
        out.gain.value = v;
      },
      get active() {
        return !!cur;
      },
      get stats() {
        return { ...stats, playing: !!cur, paused: !!paused, pos: cur ? Math.round(posNow(cur) * 100) / 100 : null, live: cur ? cur.srcs.length : 0, cached: Object.keys(cache).map((k) => k + ":" + cache[k].state) };
      }
    };
  }
  function createSfxEngine() {
''')
rep('''    let bgmSeq = null;
    let resumeCalls = 0;''', '''    let bgmSeq = null;
    // [R35] 시대 배경음악(mp3). ?bgm=synth = 예전 합성 BGM만 · ?bgm=0.5~2 = 음악 세기(실기기 볼륨 맞춤용)
    let bgmFile = null;
    let bgmWant = null;
    let bgmEra = 0;
    let bgmFileOn = false;
    let bgmHold = false;
    const BGM_Q = (() => {
      try {
        return readQuery().get("bgm");
      } catch (e) {
        return null;
      }
    })();
    const BGM_K = BGM_Q == null || BGM_Q === "" || BGM_Q === "synth" || !isFinite(parseFloat(BGM_Q)) ? 1 : Math.max(0, Math.min(2, parseFloat(BGM_Q)));
    let resumeCalls = 0;''')
rep('''        loadSamples();
        loadAmb();
      } catch (e) {''', '''        loadSamples();
        loadAmb();
        // [R35] 첫 입력(오디오 잠금 해제) 때 1시대 곡을 미리 받아 둔다 — 게임이 시작될 즈음 바로 틀 수 있게
        bgmFileInit();
        if (bgmFile) bgmFile.load(1);
      } catch (e) {''')
rep('''    const env = (gn, t0, atk, peak, dec) => {
      gn.gain.setValueAtTime(1e-4, t0);''', '''    const bgmFileInit = () => {
      if (bgmFile || smpOff || BGM_Q === "synth" || BGM_K <= 0 || !ac) return;
      bgmFile = createFileBgm(ac, master, {
        volume: 0.34 * BGM_K,
        // 곡이 준비되면: 지금 그 시대 음악을 원하고 있을 때만 합성 BGM에서 넘어간다
        onReady: (era) => {
          if (!bgmWant || bgmHold || era !== bgmEra || bgmFileOn) return;
          if (bgmFile.play(era, bgmWant === "boss" ? "b" : "a")) {
            bgmFileOn = true;
            if (bgmSeq) bgmSeq.stop(0.5);
          }
        }
      });
    };
    const env = (gn, t0, atk, peak, dec) => {
      gn.gain.setValueAtTime(1e-4, t0);''')
rep('''        if (!bgmSeq) bgmSeq = createBgm(ac, master, { volume: 0.22 });
        if (ac.state === "suspended") ac.resume();
        try {
          if (bgmSeq[cmd]) bgmSeq[cmd](arg);
        } catch (e) {
        }
      },
      get bgmStats() {
        return bgmSeq ? bgmSeq.stats : null;
      },''', '''        if (!bgmSeq) bgmSeq = createBgm(ac, master, { volume: 0.22 });
        if (ac.state === "suspended") ac.resume();
        try {
          // [R35] 시대 배경음악(mp3)이 준비돼 있으면 그것을, 아니면(받는 중 · 실패 · file:// · ?bgm=synth) 예전 합성 BGM을 튼다
          bgmFileInit();
          if (cmd === "play") {
            const m = /^field(\\d)$/.exec(arg);
            if (m) bgmEra = +m[1];
            bgmWant = arg;
            bgmHold = false;
            const sec = arg === "boss" ? "b" : m ? "a" : null;
            if (bgmFile && sec && bgmEra && bgmFile.play(bgmEra, sec)) {
              if (!bgmFileOn) bgmSeq.stop(0.3);
              bgmFileOn = true;
              return;
            }
            if (bgmFileOn) {
              bgmFile.stop(0.3);
              bgmFileOn = false;
            }
            bgmSeq.play(arg);
            return;
          }
          if (cmd === "stop" || cmd === "jingle") {
            bgmWant = null;
            if (bgmFile) bgmFile.stop(cmd === "jingle" ? 0.12 : arg);
            bgmFileOn = false;
          }
          if (cmd === "pause") bgmHold = true;
          if (cmd === "resume") bgmHold = false;
          if (bgmFile && (cmd === "pause" || cmd === "resume" || cmd === "setTempo")) bgmFile[cmd](arg);
          if (bgmSeq[cmd]) bgmSeq[cmd](arg);
        } catch (e) {
        }
      },
      get bgmStats() {
        if (!bgmSeq) return null;
        const s = bgmSeq.stats;
        const f = bgmFile ? bgmFile.stats : null;
        return bgmFileOn ? { ...s, track: bgmWant, playing: true, file: f, fileOn: true } : { ...s, file: f, fileOn: false };
      },''')
# DEV 훅: 검증용
rep('''          relics: RELIC_ROOMS,
          startLegend: () => startLegendTrial(),''', '''          relics: RELIC_ROOMS,
          // [R35] 검증: 무기 종류별 타격음 횟수 · 방향 전환 궤적 끊기 횟수 · 배경음악 상태
          r35: () => ({ snd: { ...gameRef.current.r35snd || {} }, trailCut: gameRef.current.r35TrailCut || 0, bgm: sfxRef.current ? sfxRef.current.bgmStats : null, smp: sfxRef.current ? sfxRef.current.sampleStats : null }),
          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),
          startLegend: () => startLegendTrial(),''')

open(P, "w", encoding="utf-8").write(s)
print("R35 patch ok —", n, "edits")
