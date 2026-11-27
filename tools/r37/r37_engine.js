  // [R37] 리얼리티 효과음 엔진 — assets/sfx/sfx_manifest.json(tools/r37/build_sfx.py가 만듦)의 키를 MP3 AudioBuffer로 받아 재생한다.
  //  · 매 프레임 할당 없음. 재생 때만 BufferSource · Gain(· StereoPanner) 노드를 만든다(Web Audio 규격상 소스는 1회용 · 끝나면 끊음).
  //  · 시대별 Lazy preload: 공용 묶음 + 지금 시대만 먼저, 다음 시대는 보스를 쓰러뜨릴 때(원화와 같은 때) 받는다.
  //  · 변주(_01~_03)는 직전 번호를 피하는 셔플 + 피치 ±5~8% · 같은 키 동시 상한(maxv) · 쿨다운(cool) · 좌우 패닝.
  //  · 버스 둘: mob(덕킹 대상 · 잡몹 · 환경) · force(주인공 피격 · 사망 · 적장 사망 · 에밀레종 — 전장 소음을 뚫고) → 컴프레서(-10dB · 4:1) → trunk.
  //  · 덕킹: duck(level, hold, release) — 옛 소리 · 음악 버스(duckBus)와 mob 버스를 함께 낮춘다.
  //  · MP3 디코더마다 앞머리 지연(약 25ms · LAME 머리말 없음)이 달라서, 디코딩 뒤 첫 소리 지점을 재서 그만큼 건너뛰고 시작한다(0ms 어택).
  //  · 루프 파일은 루프 지점(loopStart · loopEnd)이 파일 안쪽에 있다(앞뒤 0.1초 주기 연장) → 디코더 지연과 무관하게 이음매 없음.
  function createR37Sfx(ac, trunk, duckBus, opts = {}) {
    const K = opts.k == null ? 1 : opts.k;
    // 키별 재생 규칙: v 볼륨 · maxv 동시 상한 · jit 피치 흔들림 · cool 쿨다운(ms) · bus "force" = 덕킹 안 받음
    const P = {
      // [청음 반영 1차] 칼은 조금 작게(고려 · 조선 구간의 금속성 피크 — 파일 쪽 EQ와 함께)
      sfx_sword_slash: { v: 0.85, maxv: 3, jit: 0.07 },
      sfx_sword_cut_hit: { v: 0.9, maxv: 2, jit: 0.05 },
      // 돌도끼 '퍽'은 수십 ms에 에너지가 몰려 피크 -1dB 제약 때문에 파일 RMS가 칼보다 3~4dB 낮다(build_sfx 로그) → 재생 볼륨으로 맞춘다
      sfx_stone_axe_hit: { v: 1.3, maxv: 3, jit: 0.07 },
      sfx_stone_axe_heavy: { v: 1.1, maxv: 2, jit: 0.04 },
      sfx_obsidian_jab: { v: 0.8, maxv: 3, jit: 0.08 },
      sfx_obsidian_hit: { v: 1, maxv: 2, jit: 0.05 },
      sfx_hero_effort_light: { v: 0.75, maxv: 1, jit: 0.05, cool: 180 },
      // [청음 반영 1차] 긴 기합 · 원시 포효는 드물게(빈도는 게임 쪽 r37Effort · 쿨다운 1.2초 · 6초)
      sfx_hero_effort_heavy: { v: 0.8, maxv: 1, jit: 0.04, cool: 1200 },
      sfx_hero_barbarian_roar: { v: 0.85, maxv: 1, jit: 0.03, cool: 6e3 },
      sfx_hero_hit_light: { v: 1, maxv: 1, jit: 0.05, cool: 300, bus: "force" },
      sfx_hero_hit_heavy: { v: 1.05, maxv: 1, jit: 0.03, cool: 300, bus: "force" },
      sfx_hero_death: { v: 1.1, maxv: 1, jit: 0.02, cool: 1500, bus: "force" },
      sfx_wolf_attack: { v: 0.85, maxv: 2, jit: 0.08, cool: 250 },
      sfx_rhino_charge: { v: 0.9, maxv: 1, jit: 0.06, cool: 600 },
      sfx_bear_roar: { v: 1, maxv: 1, jit: 0.04, cool: 800 },
      sfx_tiger_roar: { v: 1, maxv: 1, jit: 0.03, cool: 1200 },
      sfx_beast_death: { v: 1, maxv: 2, jit: 0.04, cool: 150 },
      sfx_beast_boss_death: { v: 1.1, maxv: 1, jit: 0.02, bus: "force" },
      sfx_bow_full: { v: 0.8, maxv: 2, jit: 0.06 },
      sfx_bow_shoot: { v: 0.8, maxv: 3, jit: 0.07 },
      sfx_bow_draw: { v: 0.45, maxv: 3, jit: 0.08 },
      sfx_arrow_volley: { v: 0.9, maxv: 1, jit: 0.04, cool: 400 },
      sfx_rifle_shot: { v: 0.95, maxv: 2, jit: 0.05, cool: 60 },
      sfx_pistol_shot: { v: 0.9, maxv: 3, jit: 0.06 },
      sfx_enemy_katana_hurt: { v: 0.4, maxv: 1, jit: 0.07, cool: 350 },
      sfx_enemy_bullet_hurt: { v: 0.8, maxv: 2, jit: 0.07, cool: 120 },
      sfx_boss_general_death: { v: 1, maxv: 1, jit: 0.02, bus: "force" },
      sfx_soldier_down: { v: 0.9, maxv: 1, jit: 0.06, cool: 400 },
      sfx_cavalry_hooves_loop: { v: 0.9 },
      sfx_cavalry_charge: { v: 0.9, maxv: 1, jit: 0.04, cool: 700 },
      sfx_cavalry_horn: { v: 0.9, maxv: 1, jit: 0.02, cool: 3e3 },
      sfx_army_warcry: { v: 1, maxv: 1, jit: 0.04, cool: 2500 },
      sfx_nomad_horde_cry: { v: 1, maxv: 1, jit: 0.04, cool: 2500 },
      sfx_nomad_chant_loop: { v: 0.6 },
      sfx_nomad_ambush_cry: { v: 0.95, maxv: 1, jit: 0.05, cool: 1500 },
      sfx_buddha_emille_bell: { v: 1, maxv: 1, jit: 0, bus: "force" },
      sfx_buddha_light_aura: { v: 0.9, maxv: 1, jit: 0, bus: "force" }
    };
    // 시대별 미리 받을 키(0 = 공용). 2~6시대의 칼 소리는 공용에 있다
    const ERA = {
      0: ["sfx_hero_effort_light", "sfx_hero_effort_heavy", "sfx_hero_hit_light", "sfx_hero_hit_heavy", "sfx_hero_death", "sfx_sword_slash", "sfx_sword_cut_hit", "sfx_enemy_katana_hurt", "sfx_soldier_down", "sfx_boss_general_death", "sfx_army_warcry"],
      1: ["sfx_stone_axe_hit", "sfx_stone_axe_heavy", "sfx_obsidian_jab", "sfx_obsidian_hit", "sfx_hero_barbarian_roar", "sfx_wolf_attack", "sfx_rhino_charge", "sfx_bear_roar", "sfx_tiger_roar", "sfx_beast_death", "sfx_beast_boss_death"],
      2: ["sfx_bow_draw", "sfx_bow_shoot", "sfx_bow_full", "sfx_arrow_volley"],
      3: ["sfx_bow_draw", "sfx_bow_shoot", "sfx_bow_full", "sfx_arrow_volley", "sfx_cavalry_hooves_loop", "sfx_cavalry_charge", "sfx_cavalry_horn"],
      4: ["sfx_bow_draw", "sfx_bow_shoot", "sfx_bow_full", "sfx_arrow_volley", "sfx_cavalry_hooves_loop", "sfx_cavalry_charge", "sfx_cavalry_horn", "sfx_nomad_horde_cry", "sfx_nomad_chant_loop", "sfx_nomad_ambush_cry", "sfx_buddha_emille_bell", "sfx_buddha_light_aura"],
      5: ["sfx_bow_draw", "sfx_bow_shoot", "sfx_bow_full", "sfx_arrow_volley", "sfx_rifle_shot", "sfx_cavalry_hooves_loop", "sfx_cavalry_charge", "sfx_cavalry_horn"],
      6: ["sfx_rifle_shot", "sfx_pistol_shot", "sfx_enemy_bullet_hurt"]
    };
    const WEAPON = { sword: ["sfx_sword_slash", "sfx_sword_cut_hit"], stone_axe: ["sfx_stone_axe_hit", "sfx_stone_axe_heavy"], obsidian: ["sfx_obsidian_jab", "sfx_obsidian_hit"] };
    const S = { state: "idle", loaded: 0, failed: 0, played: 0, capped: 0, cooled: 0, dropped: 0, ducks: 0, by: {}, errors: [], preloaded: [], loops: {}, duck: 1 };
    const man = { keys: null, files: null };
    const bufs = {};
    const onset = {};
    const loading = {};
    const live = {};
    const lastIdx = {};
    const lastT = {};
    const loops = {};
    const pending = [];
    let liveTotal = 0;
    // 노드: mob · force → comp(-10dB · 4:1) → out(세기 K) → trunk
    const comp = ac.createDynamicsCompressor();
    comp.threshold.value = -10;
    comp.ratio.value = 4;
    comp.knee.value = 6;
    comp.attack.value = 3e-3;
    comp.release.value = 0.12;
    const out = ac.createGain();
    out.gain.value = K;
    const mob = ac.createGain();
    const force = ac.createGain();
    mob.connect(comp);
    force.connect(comp);
    comp.connect(out);
    out.connect(trunk);
    const hasPan = typeof ac.createStereoPanner === "function";
    // 첫 소리 지점(초): 앞 120ms 안에서 |x| > 0.01을 처음 넘는 곳의 4ms 앞(디코더 앞머리 지연 보정)
    const findOnset = (b) => {
      const d = b.getChannelData(0);
      const n = Math.min(d.length, Math.floor(b.sampleRate * 0.12));
      for (let i = 0; i < n; i++) if (d[i] > 0.01 || d[i] < -0.01) return Math.max(0, i / b.sampleRate - 4e-3);
      return 0;
    };
    const loadFile = (fn) => {
      if (bufs[fn] || loading[fn]) return;
      loading[fn] = true;
      fetch(`assets/sfx/${fn}`).then((r) => r.ok ? r.arrayBuffer() : Promise.reject(new Error(String(r.status)))).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej))).then((b) => {
        bufs[fn] = b;
        onset[fn] = findOnset(b);
        S.loaded++;
      }).catch((e) => {
        S.failed++;
        if (S.errors.length < 20) S.errors.push(fn + ": " + (e && e.message || e));
      }).then(() => {
        loading[fn] = false;
      });
    };
    const loadKey = (key) => {
      const e = man.keys && man.keys[key];
      if (e) e.files.forEach(loadFile);
    };
    const preload = (era) => {
      if (!man.keys) {
        if (pending.indexOf(era) < 0) pending.push(era);
        return;
      }
      if (S.preloaded.indexOf(era) >= 0) return;
      S.preloaded.push(era);
      (ERA[era] || []).forEach(loadKey);
    };
    const init = () => {
      if (S.state !== "idle" || K <= 0) return;
      S.state = "loading";
      fetch("assets/sfx/sfx_manifest.json").then((r) => r.ok ? r.json() : Promise.reject(new Error(String(r.status)))).then((m) => {
        man.keys = m.keys;
        man.files = m.files;
        S.state = "ready";
        preload(0);
        pending.splice(0).forEach(preload);
      }).catch((e) => {
        S.state = "failed";
        S.errors.push("manifest: " + (e && e.message || e));
      });
    };
    // 변주 고르기: 직전 번호를 피한다 · 아직 안 받아진 파일이면 받아진 것 가운데서
    const pick = (key) => {
      const e = man.keys && man.keys[key];
      if (!e) return null;
      const fs = e.files;
      const n = fs.length;
      let i = 0;
      if (n > 1) {
        const last = lastIdx[key];
        if (last == null) i = Math.floor(Math.random() * n);
        else {
          i = Math.floor(Math.random() * (n - 1));
          if (i >= last) i++;
        }
      }
      if (!bufs[fs[i]]) {
        const j = fs.findIndex((f) => !!bufs[f]);
        if (j < 0) return null;
        i = j;
      }
      lastIdx[key] = i;
      return fs[i];
    };
    // o = { v 볼륨 배율, r 피치 배율, pan -1~1, d 지연(초), force, cool(ms), maxv, jit }
    //  돌려주는 값: true = 처리됨(재생 · 또는 쿨다운 · 상한으로 일부러 안 냄), false = 못 냄(부르는 쪽이 예전 소리로)
    const play = (key, o) => {
      if (K <= 0 || S.state !== "ready") return false;
      const p = P[key] || {};
      const now = performance.now();
      const cool = o && o.cool != null ? o.cool : p.cool || 0;
      if (cool && lastT[key] != null && now - lastT[key] < cool) {
        S.cooled++;
        return true;
      }
      const fn = pick(key);
      if (!fn) return false;
      const maxv = o && o.maxv || p.maxv || 3;
      if ((live[key] || 0) >= maxv || liveTotal >= 24) {
        S.capped++;
        return true;
      }
      const b = bufs[fn];
      const src = ac.createBufferSource();
      src.buffer = b;
      const jit = o && o.jit != null ? o.jit : p.jit == null ? 0.06 : p.jit;
      const rate = (o && o.r || 1) * (jit ? 1 + (Math.random() * 2 - 1) * jit : 1);
      if (rate !== 1) src.playbackRate.value = rate;
      const gn = ac.createGain();
      gn.gain.value = (p.v == null ? 1 : p.v) * (o && o.v != null ? o.v : 1);
      src.connect(gn);
      let tail = gn;
      if (hasPan && o && o.pan) {
        const pn = ac.createStereoPanner();
        pn.pan.value = Math.max(-1, Math.min(1, o.pan));
        gn.connect(pn);
        tail = pn;
      }
      tail.connect(o && o.force || p.bus === "force" ? force : mob);
      live[key] = (live[key] || 0) + 1;
      liveTotal++;
      src.onended = () => {
        live[key]--;
        liveTotal--;
        try {
          src.disconnect();
          gn.disconnect();
          if (tail !== gn) tail.disconnect();
        } catch (e) {
        }
      };
      src.start(ac.currentTime + (o && o.d || 0), onset[fn] || 0);
      lastT[key] = now;
      S.played++;
      S.by[key] = (S.by[key] || 0) + 1;
      return true;
    };
    // 루프: loop(key, true, { v, v0, fadeIn, lowpass: [f0, f1], sweep, pan }) · loop(key, false, { fadeOut }). 켜진 루프에 다시 켜기 = 볼륨만 갱신
    const loop = (key, on, o) => {
      const cur = loops[key];
      const t = ac.currentTime;
      if (!on) {
        if (!cur) return;
        const fo = o && o.fadeOut != null ? o.fadeOut : 0.6;
        try {
          cur.gn.gain.cancelScheduledValues(t);
          cur.gn.gain.setValueAtTime(cur.gn.gain.value, t);
          cur.gn.gain.linearRampToValueAtTime(0, t + fo);
          cur.src.stop(t + fo + 0.05);
        } catch (e) {
        }
        delete loops[key];
        delete S.loops[key];
        return;
      }
      const p = P[key] || {};
      const target = (p.v == null ? 1 : p.v) * (o && o.v != null ? o.v : 1);
      if (cur) {
        if (Math.abs(cur.target - target) > 1e-3) {
          cur.gn.gain.cancelScheduledValues(t);
          cur.gn.gain.setValueAtTime(cur.gn.gain.value, t);
          cur.gn.gain.linearRampToValueAtTime(target, t + 0.6);
          cur.target = target;
          S.loops[key].v = Math.round(target * 100) / 100;
        }
        return;
      }
      if (K <= 0 || S.state !== "ready") return;
      const e = man.keys && man.keys[key];
      if (!e) return;
      const fn = e.files[0];
      const b = bufs[fn];
      if (!b) {
        loadFile(fn);
        return;
      }
      const src = ac.createBufferSource();
      src.buffer = b;
      src.loop = true;
      if (e.loop) {
        src.loopStart = e.loop[0];
        src.loopEnd = Math.min(b.duration, e.loop[1]);
      }
      const gn = ac.createGain();
      const fi = o && o.fadeIn != null ? o.fadeIn : 1;
      gn.gain.setValueAtTime(o && o.v0 != null ? o.v0 * target : 1e-4, t);
      gn.gain.linearRampToValueAtTime(target, t + fi);
      let head = src;
      if (o && o.lowpass) {
        const flt = ac.createBiquadFilter();
        flt.type = "lowpass";
        flt.Q.value = 0.7;
        flt.frequency.setValueAtTime(Math.max(40, o.lowpass[0]), t);
        flt.frequency.exponentialRampToValueAtTime(Math.min(ac.sampleRate / 2 - 1, o.lowpass[1]), t + (o.sweep || 2));
        src.connect(flt);
        head = flt;
      }
      head.connect(gn);
      let tail = gn;
      if (hasPan && o && o.pan) {
        const pn = ac.createStereoPanner();
        pn.pan.value = Math.max(-1, Math.min(1, o.pan));
        gn.connect(pn);
        tail = pn;
      }
      tail.connect(mob);
      src.start(t, e.loop ? e.loop[0] : 0);
      loops[key] = { src, gn, target };
      S.loops[key] = { v: Math.round(target * 100) / 100, at: Math.round(t * 10) / 10 };
      S.by[key] = (S.by[key] || 0) + 1;
    };
    // 덕킹: mob 버스와 옛 소리 · 음악 버스를 level로(40ms) → hold초 유지 → release초 동안 복귀
    let duckTimer = 0;
    const duck = (level, hold, release) => {
      const t = ac.currentTime;
      [mob, duckBus].forEach((g) => {
        if (!g) return;
        g.gain.cancelScheduledValues(t);
        g.gain.setValueAtTime(g.gain.value, t);
        g.gain.linearRampToValueAtTime(level, t + 0.04);
        g.gain.setValueAtTime(level, t + 0.04 + hold);
        g.gain.linearRampToValueAtTime(1, t + 0.04 + hold + release);
      });
      S.duck = level;
      S.ducks++;
      clearTimeout(duckTimer);
      duckTimer = setTimeout(() => {
        S.duck = 1;
      }, (0.04 + hold + release) * 1e3);
    };
    // [리니지식 콤보 상승] weaponType = sword · stone_axe · obsidian · combo가 쌓일수록 피치 +1.5%/콤보(최대 8) · 치명타 · 강타 = 임팩트 소리
    const melee = (weaponType, combo, isCrit, pan, o) => {
      const W = WEAPON[weaponType] || WEAPON.sword;
      const c = Math.max(0, Math.min(8, combo | 0));
      return play(isCrit ? W[1] : W[0], { r: (1 + 0.015 * c) * (o && o.r || 1), pan, v: o && o.v });
    };
    // [주인공 피격 최우선] 전장 소음을 뚫고(force) · 쿨다운 300ms
    const heroHit = (heavy, pan) => play(heavy ? "sfx_hero_hit_heavy" : "sfx_hero_hit_light", { force: true, cool: 300, pan });
    // [자동 화살비 전환] 최근 150ms 안 3발 이상이면 단발을 끊고 화살비 한 번(그 뒤 0.5초 동안 단발 없음)
    const shots = [];
    let volleyUntil = 0;
    const arrowShot = (pan, o) => {
      const now = performance.now();
      while (shots.length && now - shots[0] > 150) shots.shift();
      shots.push(now);
      if (now < volleyUntil) return true;
      if (shots.length >= 3) {
        volleyUntil = now + 500;
        shots.length = 0;
        return play("sfx_arrow_volley", { pan });
      }
      return play(o && o.full ? "sfx_bow_full" : "sfx_bow_shoot", { pan });
    };
    // [일반 병사 사망 절제] 갑옷 낙하 소리만 · 쿨다운 400ms · 동시 1
    const soldierDown = (pan) => play("sfx_soldier_down", { pan, cool: 400, maxv: 1 });
    return {
      init,
      preload,
      play,
      loop,
      duck,
      melee,
      heroHit,
      arrowShot,
      soldierDown,
      has: (key) => !!(man.keys && man.keys[key] && man.keys[key].files.some((f) => !!bufs[f])),
      keys: () => man.keys ? Object.keys(man.keys) : [],
      setVolume: (v) => {
        out.gain.value = v;
      },
      get k() {
        return K;
      },
      get stats() {
        // onsetMs = 디코딩 뒤 잰 첫 소리 지점(ms)의 최소 · 최대 — 디코더 앞머리 지연 보정이 실제로 작동하는지 확인용
        const on = Object.keys(onset).map((f) => onset[f] * 1e3);
        return { ...S, by: { ...S.by }, live: { ...live }, loops: { ...S.loops }, errors: S.errors.slice(), bufs: Object.keys(bufs).length, keyCount: man.keys ? Object.keys(man.keys).length : 0, liveTotal, onsetMs: on.length ? [Math.round(Math.min(...on) * 10) / 10, Math.round(Math.max(...on) * 10) / 10] : null };
      }
    };
  }
