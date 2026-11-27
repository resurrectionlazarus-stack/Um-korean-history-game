#!/usr/bin/env python3
"""R37 「리얼리티 효과음」 — 음향감독 발주서: 실제 녹음 효과음 64개(tools/r37/build_sfx.py)를 Web Audio 엔진(createR37Sfx · tools/r37/r37_engine.js)으로 게임에 연결.

사용: cp shinsi-R36.5-2/index.html shinsi-R37/index.html && python3 -I tools/r37/r37_patch.py shinsi-R37/index.html
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R37] 주석으로 이유를 남긴다.
주의: 옛 코드의 한글은 \\uXXXX 이스케이프로 저장돼 있다 → esc("한글")로 찾는다(chr(92)로 만든다 — 도구 입력의 역슬래시-u가 실제 글자로 바뀌는 일 방지).

연결 원칙: 새 엔진이 준비됐으면(MP3 받아 디코딩됨 · ?r37=0이 아님) 새 소리, 아니면 예전 소리(R35 · R36)로 그대로 — 어느 기기에서도 소리가 비는 일이 없게.
"""
import os
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0
B = chr(92)
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = open(os.path.join(HERE, "r37_engine.js"), encoding="utf-8").read().rstrip("\n")


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


def esc(t):
    return "".join((B + "u{%X}" % ord(c) if ord(c) > 0xFFFF else B + "u%04X" % ord(c)) if ord(c) > 127 else c for c in t)


# ───────── 1. 엔진 본체(createSfxEngine 바로 앞) ─────────
rep('''  function createSfxEngine() {
    let bgmSeq = null;''', ENGINE + '''
  function createSfxEngine() {
    let bgmSeq = null;''')

# ───────── 2. createSfxEngine 안: 세기 옵션 · 버스 재구성 · 음소거 · 바깥 API ─────────
rep('''    let resumeCalls = 0;
    let resumeHits = 0;
    let ac = null;
    let master = null;''', '''    let resumeCalls = 0;
    let resumeHits = 0;
    let ac = null;
    let master = null;
    // [R37] 새 효과음 엔진 세기 — ?r37=0 끔(R36 소리로 비교) · ?r37=0.5~2 세기(실기기 볼륨 맞춤용)
    const R37_Q = (() => {
      try {
        return readQuery().get("r37");
      } catch (e) {
        return null;
      }
    })();
    const R37_K = R37_Q == null || R37_Q === "" ? 1 : Math.max(0, Math.min(2, parseFloat(R37_Q) || 0));
    let trunk = null;
    let r37 = null;''')
rep('''        ac = new AC();
        master = ac.createGain();
        master.gain.value = 0.5;
        const comp = ac.createDynamicsCompressor();
        comp.threshold.value = -16;
        comp.ratio.value = 8;
        master.connect(comp);
        comp.connect(ac.destination);''', '''        ac = new AC();
        // [R37] 마스터 사슬: (옛 소리 · 음악 · 환경음 → master = 덕킹 버스) → trunk(0.5 · 음소거) → 컴프레서(-16dB · 8:1 · R35까지와 같음) → 출력.
        //  새 엔진(createR37Sfx)은 자기 컴프레서(-10dB · 4:1)를 거쳐 trunk로 간다. 덕킹은 master와 새 엔진의 mob 버스만 낮춘다
        trunk = ac.createGain();
        trunk.gain.value = muted ? 0 : 0.5;
        master = ac.createGain();
        master.gain.value = 1;
        const comp = ac.createDynamicsCompressor();
        comp.threshold.value = -16;
        comp.ratio.value = 8;
        master.connect(trunk);
        trunk.connect(comp);
        comp.connect(ac.destination);
        r37 = createR37Sfx(ac, trunk, master, { k: smpOff ? 0 : R37_K });
        r37.init();
        r37.preload(1);''')
rep('''        if (master) master.gain.value = m ? 0 : 0.5;''', '''        // [R37] 음소거는 trunk(옛 소리 · 음악 · 새 엔진이 모두 지나는 자리)에서
        if (trunk) trunk.gain.value = m ? 0 : 0.5;''')
rep('''      get audioState() {
        return ac ? ac.state : "none";
      },''', '''      // [R37] 새 효과음 엔진(첫 입력 전에는 null) · 시대별 미리 받기
      get r37() {
        return r37;
      },
      r37preload(era) {
        if (r37) r37.preload(era);
      },
      // [R37] 검증: 음소거 · 덕킹 버스의 지금 게인
      get r37gains() {
        return { trunk: trunk ? trunk.gain.value : null, duckBus: master ? master.gain.value : null };
      },
      get audioState() {
        return ac ? ac.state : "none";
      },''')

# ───────── 3. App 안 연결 함수(r35HitSnd · r36Voice 뒤) ─────────
rep('''    const eraObjOf = () => ERAS_DATA[gameRef.current.era - 1] || ERAS_DATA[0];''', '''    // [R37] 리얼리티 효과음 연결 — 새 엔진이 준비됐으면 새 소리, 아니면 예전 소리(R35 · R36). 횟수는 g.r37snd · g.r37voice에(검증용 · DEV r37())
    const r37 = () => sfxRef.current && sfxRef.current.r37;
    // 좌우 패닝: 화면 가운데 0 · 가장자리 ±0.55
    const r37Pan = (x) => {
      const g = gameRef.current;
      return Math.max(-1, Math.min(1, (x - g.cameraX - VIEW_W / 2) / (VIEW_W / 2))) * 0.55;
    };
    // 무기 종류 → 소리 묶음: 주먹도끼 · 간돌도끼 = stone_axe · 슴베찌르개 = obsidian · 칼(2~6시대) = sword
    const r37Weapon = () => {
      const g = gameRef.current;
      const c = heroWeaponClass(g.era, g.stats.weaponTier || 1);
      return c === "AXE" ? "stone_axe" : c === "SPEAR" ? "obsidian" : "sword";
    };
    // 타격음(r35HitSnd와 같은 lv): 콤보 수만큼 피치 ↑(+1.5%/콤보 · 최대 8) · 강타 · 내려찍기 · 양단 = 임팩트 소리 · 총탄(gun) = 사람 적의 총탄 피격.
    //  [청음 반영 1차] 갑옷 · 방패 타격(armor)은 R35의 쇠 울림(cutArmor) 대신 새 녹음의 베기를 낮고 작게(v 0.7 · 피치 0.93) — 고려 · 조선 구간의 '깡깡'이 주로 여기서 났다(오너).
    //  사람 적을 칼로 벨 때 얹는 베임 소리(날 소리)는 셋에 하나 · 0.4로
    const r37Hit = (lv, o, target) => {
      const E = r37();
      const g = gameRef.current;
      let ok = false;
      if (E) {
        const pan = target ? r37Pan(target.x) : 0;
        if (lv === "gun") ok = !!target && !target.mobRole && E.play("sfx_enemy_bullet_hurt", { pan });
        else {
          const w = r37Weapon();
          const combo = Math.min(8, g.stats.combo || 0);
          if (lv === "armor") ok = E.melee(w, combo, false, pan, { v: 0.7, r: 0.93 });
          else {
            ok = E.melee(w, combo, lv === "heavy" || lv === "crush" || lv === "sever", pan, o);
            if (ok && target && !target.mobRole && w === "sword" && Math.random() < 0.3) E.play("sfx_enemy_katana_hurt", { pan, v: 0.4, d: 0.02 });
          }
        }
      }
      const L = g.r37snd || (g.r37snd = { r37: 0, r35: 0 });
      if (ok) L.r37++;
      else L.r35++;
      if (!ok) r35HitSnd(lv, o);
    };
    // 기합: 평타 1~2타 35% 짧은 기합 · 마지막 타 · 갈래 기술 · 질풍연참 100% · 각성 100%. 총 공격은 없음.
    //  [청음 반영 1차] 1시대의 긴 '으허!'(원시 포효 · 강한 기합)가 필살기처럼 자주 들린다(오너) → 마지막 타도 짧은 단음 위주:
    //   1시대 마지막 타 = 짧은 기합 75% · 강한 기합 15% · 원시 포효 10%(6초 쿨다운) / 그 밖 시대 = 짧은 60% · 강한 40% / 각성 = 1시대 원시 포효 · 그 밖 강한 기합
    const r37Effort = (step, N, kind) => {
      const E = r37();
      if (!E || kind === "gun") return;
      const g = gameRef.current;
      const heavy = kind === "heavy" || kind === "ult" || step >= N;
      if (!heavy && Math.random() >= 0.35) return;
      let key = "sfx_hero_effort_light";
      if (kind === "ult") key = g.era === 1 ? "sfx_hero_barbarian_roar" : "sfx_hero_effort_heavy";
      else if (heavy) {
        const r = Math.random();
        if (g.era === 1) key = r < 0.1 ? "sfx_hero_barbarian_roar" : r < 0.25 ? "sfx_hero_effort_heavy" : "sfx_hero_effort_light";
        else key = r < 0.4 ? "sfx_hero_effort_heavy" : "sfx_hero_effort_light";
      }
      if (E.play(key, { pan: 0 })) {
        const V = g.r37voice || (g.r37voice = {});
        V[key] = (V[key] || 0) + 1;
      }
    };
    // 적이 쓰러질 때: 곰 · 코뿔소 = 공용 사망음(음높이 곰 0.85 · 코뿔소 0.78 · 호랑이 1.06) · 중간보스 = 적장 최후(덕킹 35%) · 사람 병사 = 갑옷 낙하(400ms 쿨다운 · 동시 1)
    //  늑대 · 하이에나는 새 녹음이 없어 R36 깨갱 그대로(false)
    const R37_BEAST_PITCH = { TIGER: 1.06, BEAR: 0.85, RHINO: 0.78 };
    const r37EnemyDown = (en) => {
      const E = r37();
      if (!E) return false;
      const pan = r37Pan(en.x);
      let ok = false;
      if (en.mobRole) {
        const r = R37_BEAST_PITCH[en.mobRole];
        if (!r) return false;
        ok = E.play("sfx_beast_death", { r, pan, v: en.isMidBoss ? 1.15 : 1 });
        if (ok && en.isMidBoss) E.duck(0.35, 0.5, 0.5);
      } else if (en.isMidBoss) {
        ok = E.play("sfx_boss_general_death", { pan, force: true });
        if (ok) E.duck(0.35, 0.5, 0.5);
      } else ok = E.soldierDown(pan);
      if (ok) {
        const V = gameRef.current.r37voice || (gameRef.current.r37voice = {});
        const k = en.mobRole ? "beastDeath" : en.isMidBoss ? "midDeath" : "soldierDown";
        V[k] = (V[k] || 0) + 1;
      }
      return ok;
    };
    // 시대 보스가 쓰러질 때: 1시대 = 야수 보스 최후 붕괴 · 그 밖 = 적장 최후(모두 최우선 · 0.6초 덕킹)
    const r37BossDeath = () => {
      const E = r37();
      if (!E) return false;
      const g = gameRef.current;
      const ok = E.play(g.era === 1 ? "sfx_beast_boss_death" : "sfx_boss_general_death", { force: true, v: 1.1 });
      if (ok) {
        E.duck(0.35, 0.6, 0.6);
        const V = g.r37voice || (g.r37voice = {});
        V.bossDeath = (V.bossDeath || 0) + 1;
      }
      return ok;
    };
    // 웨이브 등장 함성: 몽골 전선(4시대 3전선)은 북방 기병 괴성 · 그 밖은 정규군 함성
    const r37WarCry = (cnt) => {
      const E = r37();
      if (!E) return false;
      const g = gameRef.current;
      const nomad = g.era === 4 && (g.front4 === "mongol" || g.zoneIdx === 2);
      const ok = E.play(nomad ? "sfx_nomad_horde_cry" : "sfx_army_warcry", { v: Math.min(1.15, 0.8 + cnt * 0.04) });
      if (ok) {
        const V = g.r37voice || (g.r37voice = {});
        V.warCry = (V.warCry || 0) + 1;
      }
      return ok;
    };
    // 12틱마다: 기마 적이 보이면 경보(4시대 여진 · 몽골 전선 = 기습 괴성, 그 밖 = 뿔피리 · 좌우 ±0.6) → 말발굽 루프를 로패스 350→18000Hz · 볼륨 0.2→1.0로 2초 동안 열어 접근감 ·
    //  기마 적이 모두 쓰러지면 약 1.6초 뒤 0.6초 페이드아웃. 몽골 전선 구역 전투 중(보스 전 아닐 때)에는 포위 대치 후두 구호 루프를 낮게 깐다
    const r37Step = (g) => {
      const E = r37();
      if (!E) return;
      let riders = 0;
      let rx = 0;
      for (let i = 0; i < g.enemies.length; i++) {
        const e = g.enemies[i];
        if (e.state === "DYING") continue;
        const U = e.unit && UNIT_SPECS[e.unit];
        if (U && U.mounted || e.mid && e.mid.mounted) {
          riders++;
          rx += e.x;
        }
      }
      const H = g._r37 || (g._r37 = { hoof: false, quiet: 0, chant: false, cues: 0 });
      if (riders > 0) {
        H.quiet = 0;
        const v = Math.min(1, 0.55 + riders * 0.15);
        if (!H.hoof) {
          H.hoof = true;
          H.cues++;
          const pan = Math.max(-0.6, Math.min(0.6, r37Pan(rx / riders) * 1.5));
          E.play(g.era === 4 && g.zoneIdx >= 1 ? "sfx_nomad_ambush_cry" : "sfx_cavalry_horn", { pan, v: 0.95 });
          E.loop("sfx_cavalry_hooves_loop", true, { v, v0: 0.2, fadeIn: 2, lowpass: [350, 18e3], sweep: 2 });
        } else E.loop("sfx_cavalry_hooves_loop", true, { v });
      } else if (H.hoof && ++H.quiet >= 8) {
        H.hoof = false;
        H.quiet = 0;
        E.loop("sfx_cavalry_hooves_loop", false, { fadeOut: 0.6 });
      }
      const chant = g.era === 4 && g.front4 === "mongol" && g.zoneState === "LOCKED" && !g.bossActive;
      if (chant !== H.chant) {
        H.chant = chant;
        E.loop("sfx_nomad_chant_loop", chant, chant ? { v: 1, fadeIn: 1.5 } : { fadeOut: 1.2 });
      }
    };
    const eraObjOf = () => ERAS_DATA[gameRef.current.era - 1] || ERAS_DATA[0];''')

# ───────── 4. 짐승 · 보스 목소리(R36 함수 안에서 새 녹음을 먼저) ─────────
rep('''    const r36MobVoice = (en, ev) => {
      const T = en && en.mobRole && R36_BEAST[en.mobRole];
      if (!T) return;
      const [key, r, v] = T[ev];''', '''    const r36MobVoice = (en, ev) => {
      const T = en && en.mobRole && R36_BEAST[en.mobRole];
      if (!T) return;
      // [R37] 덮치기 예고: 늑대 = 새 공격 녹음 · 코뿔소 = 새 돌진 녹음(곰 · 하이에나는 R36 소리)
      if (ev === "atk" && r37() && (en.mobRole === "WOLF" && r37().play("sfx_wolf_attack", { pan: r37Pan(en.x), v: 0.8 }) || en.mobRole === "RHINO" && r37().play("sfx_rhino_charge", { pan: r37Pan(en.x), v: 0.9 }))) return;
      const [key, r, v] = T[ev];''')
rep('''      if (g.era !== 1) {
        sfx("bossRoar");
        return;
      }
      const L = g.r36voice || (g.r36voice = {});
      const key = kind === "bear" ? "bearRoar" : kind === "snarl" ? "tigerSnarl" : "tigerRoar";''', '''      if (g.era !== 1) {
        sfx("bossRoar");
        return;
      }
      // [R37] 산군 포효 · 동굴 곰 포효는 새 녹음(돌진 직전 으르렁 · 쓰러질 때는 다른 자리에서)
      if ((kind === "roar" || kind === "bear") && r37() && r37().play(kind === "bear" ? "sfx_bear_roar" : "sfx_tiger_roar", { v: kind === "bear" ? 1.1 : 1 })) {
        const V = g.r37voice || (g.r37voice = {});
        const kk = kind === "bear" ? "bearRoar" : "tigerRoar";
        V[kk] = (V[kk] || 0) + 1;
        return;
      }
      const L = g.r36voice || (g.r36voice = {});
      const key = kind === "bear" ? "bearRoar" : kind === "snarl" ? "tigerSnarl" : "tigerRoar";''')

# ───────── 5. 타격음 자리(r35HitSnd → r37Hit) ─────────
rep('''            r35HitSnd("sever");''', '''            r37Hit("sever", null, target);''')
rep('''        if (isCounter) sfx("counter");
        else if (g._r31gun) r35HitSnd("gun");
        else if (cs >= lastStep) r35HitSnd("heavy", e2 ? R31_E2_HEAVY_SND : big ? { v: 1.08, r: 0.95 } : null);
        else if (!big && (target.guardRate > 0 || heavy)) r35HitSnd("armor");
        else if (cs >= 1) r35HitSnd("light", { v: (big ? 1.08 : 0.92) + cs * 0.05, r: (big ? 0.95 : 1.03) - cs * 0.02 });
        else r35HitSnd(hitCount >= 2 ? "heavy" : "light", hitCount >= 2 ? { v: 0.9 } : dealtCrit ? { v: 1, r: 0.95 } : { v: 0.85 });''',
    '''        if (isCounter) sfx("counter");
        // [R37] 새 녹음 타격음(무기별 · 콤보 피치 · 강타 임팩트 · 사람 적의 신음) — 못 쓰면 R35 타격음(r37Hit 안에서)
        else if (g._r31gun) r37Hit("gun", null, target);
        else if (cs >= lastStep) r37Hit("heavy", e2 ? R31_E2_HEAVY_SND : big ? { v: 1.08, r: 0.95 } : null, target);
        else if (!big && (target.guardRate > 0 || heavy)) r37Hit("armor", null, target);
        else if (cs >= 1) r37Hit("light", { v: (big ? 1.08 : 0.92) + cs * 0.05, r: (big ? 0.95 : 1.03) - cs * 0.02 }, target);
        else r37Hit(hitCount >= 2 ? "heavy" : "light", hitCount >= 2 ? { v: 0.9 } : dealtCrit ? { v: 1, r: 0.95 } : { v: 0.85 }, target);''')
rep('''      r35HitSnd("flurry");
      if (g.era === 4) r33Storm();''', '''      r37Hit("flurry");
      r37Effort(4, 4, "heavy");
      if (g.era === 4) r33Storm();''')
rep('''      sfx("breath");
      r35HitSnd("flurry");''', '''      sfx("breath");
      r37Hit("flurry");''')
rep('''      r35HitSnd("crush");''', '''      r37Hit("crush");''')
rep('''        r35HitSnd("heavy", R31_E2_HEAVY_SND);''', '''        r37Hit("heavy", R31_E2_HEAVY_SND);''')
rep('''        r35HitSnd("heavy");''', '''        r37Hit("heavy");''')

# ───────── 6. 주인공 기합(연타 단계 확정 자리 · 갈래 기술 · 각성) ─────────
rep('''      const step = p.comboStep;
      p._atkSrc = "combo";''', '''      const step = p.comboStep;
      // [R37] 기합: 1~2타 35% · 마지막 타 100%(총 공격은 없음)
      r37Effort(step, g.stats.level >= SKILL_LV.finisher ? 4 : 3, HERO_FIREARM[g.era] && step === 3 ? "gun" : null);
      p._atkSrc = "combo";''')
rep('''      r36Pop(kind);''', '''      r36Pop(kind);
      r37Effort(4, 4, "heavy");''')
rep('''      sfx("ult");
      g.player.invincibleTimer = 120;''', '''      sfx("ult");
      r37Effort(4, 4, "ult");
      g.player.invincibleTimer = 120;''')

# ───────── 7. 주인공 피격 · 사망 ─────────
rep('''    const hurtPlayer = (dmgBase, label, color) => {''', '''    const hurtPlayer = (dmgBase, label, color, heavy) => {''')
rep('''      g.hurtFlash = 13;
      addTrauma(0.28);
      sfx("hurt");''', '''      g.hurtFlash = 13;
      addTrauma(0.28);
      // [R37] 피격 목소리(새 녹음 · 전장 소음을 뚫고 · 쿨다운 300ms). 보스 · 중간보스의 강타(heavy) = 묵직한 피격 + 90ms(5틱) 히트스톱
      if (!(r37() && r37().heroHit(!!heavy, 0))) sfx("hurt");
      if (heavy) g.hitStop = Math.max(g.hitStop, 5);''')
rep('''"#f97316");
            if (res !== "parry") p.vx = c.dir * 18 * (res === "guard" ? GUARD_KNOCK_MULT : 1);''', '''"#f97316", true);
            if (res !== "parry") p.vx = c.dir * 18 * (res === "guard" ? GUARD_KNOCK_MULT : 1);''')
rep('''            const res = hurtPlayer(Math.floor(tl.dmg), tl.label, "#f43f5e");''', '''            const res = hurtPlayer(Math.floor(tl.dmg), tl.label, "#f43f5e", true);''')
rep('''"BOSS STOMP!", "#f43f5e");''', '''"BOSS STOMP!", "#f43f5e", true);''')
rep(esc("곰 지배자 내려찍기!") + '''", "#f97316");''', esc("곰 지배자 내려찍기!") + '''", "#f97316", true);''')
rep('''        const res = hurtPlayer(Math.floor(tl.dmg), tl.label, "#fb7185");''', '''        const res = hurtPlayer(Math.floor(tl.dmg), tl.label, "#fb7185", !!o.mid);''')
rep('''            const res = hurtPlayer(Math.floor(c.dmg), c.label, "#f97316");''', '''            const res = hurtPlayer(Math.floor(c.dmg), c.label, "#f97316", !!en.mid);''')
rep('''          g.hurtFlash = 20;
          sfx("ko");''', '''          g.hurtFlash = 20;
          // [R37] 사망: 새 목소리(최우선) · 말발굽 루프 0.25초 페이드아웃 · 음악 · 잡몹 소리 30%로 덕킹(쓰러지는 1.7초 동안)
          {
            const E = r37();
            if (E && E.play("sfx_hero_death", { force: true })) {
              E.loop("sfx_cavalry_hooves_loop", false, { fadeOut: 0.25 });
              E.duck(0.3, 1.5, 0.6);
            } else sfx("ko");
          }''')

# ───────── 8. 적 · 보스가 쓰러질 때 ─────────
rep('''            r36MobVoice(en, "die");''', '''            // [R37] 곰 · 코뿔소 = 공용 사망음(음높이 분기) · 중간보스 = 적장 최후 · 사람 병사 = 갑옷 낙하(절제). 없으면 R36 소리
            if (!r37EnemyDown(en)) r36MobVoice(en, "die");''')
rep('''      g.slowMo = 26;
      r36Roar("death");''', '''      g.slowMo = 26;
      // [R37] 보스 최후: 1시대 야수 보스 붕괴 · 그 밖 적장 최후(최우선 · 0.6초 덕킹). 없으면 R36 마지막 포효
      if (!r37BossDeath()) r36Roar("death");''')

# ───────── 9. 웨이브 등장 소리 ─────────
rep('''            r36Voice(key, 0, { v });''', '''            // [R37] 곰 포효 · 코뿔소 돌진은 새 녹음으로(늑대 하울링 · 하이에나는 R36 소리)
            if (!(r37() && (role === "BEAR" && r37().play("sfx_bear_roar", { v }) || role === "RHINO" && r37().play("sfx_rhino_charge", { v })))) r36Voice(key, 0, { v });''')
rep('''} else if (g.era >= 2 && r36Voice("warCry", 420, { v: Math.min(1.15, 0.8 + n * 0.04), r: 0.95 + Math.random() * 0.1 })) cue++;''',
    '''} else if (g.era >= 2 && (r37WarCry(n) || r36Voice("warCry", 420, { v: Math.min(1.15, 0.8 + n * 0.04), r: 0.95 + Math.random() * 0.1 }))) cue++;''')

# ───────── 10. 기병 · 대치 루프(12틱마다) ─────────
rep('''        if (g.sfxHitGate > 0) g.sfxHitGate--;''', '''        if (g.sfxHitGate > 0) g.sfxHitGate--;
        // [R37] 기병 경보 · 말발굽 루프 · 몽골 전선 후두 구호 루프 관리(12틱마다 한 번 — 매 프레임 할당 없음)
        if (g.tick % 12 === 0) r37Step(g);''')

# ───────── 11. 기병 돌격 · 보스 기마 돌격 ─────────
rep('''          o.uBusy = 0;
          sfx("dash");
          return;''', '''          o.uBusy = 0;
          // [R37] 기마 적 · 기마 중간보스의 돌격 = 정면 돌격 쇄도 녹음(좌우 패닝). 그 밖은 예전 대시 소리
          {
            const U = o.unit && UNIT_SPECS[o.unit];
            if (!((U && U.mounted || o.mid && o.mid.mounted) && r37() && r37().play("sfx_cavalry_charge", { pan: r37Pan(o.x) }))) sfx("dash");
          }
          return;''')
rep('''          b.chargePending = null;
          sfx("dash");''', '''          b.chargePending = null;
          // [R37] 기마 보스(3시대 소정방 · 5시대 용골대)의 돌격 = 기병 돌격 쇄도
          if (!((g.era === 3 || g.era === 5) && r37() && r37().play("sfx_cavalry_charge", { pan: r37Pan(b.x) }))) sfx("dash");''')

# ───────── 12. 궁수: 당김(조준 시작) · 발사(화살비 자동 전환) · 총탄 · 보스 부채꼴 화살 ─────────
rep('''        } else if (S.tactic === "ranged") {
          first = S.aim;''', '''        } else if (S.tactic === "ranged") {
          first = S.aim;
          // [R37] 활을 당기는 소리(조준 시작 · 작게 · 좌우)
          if (S.shot === "arrow" && r37()) r37().play("sfx_bow_draw", { pan: r37Pan(en.x) });''')
rep('''          first += 8;
        } else if (pat === "bombard") {''', '''          first += 8;
          // [R37] 기마 중간보스의 일제 사격 = 활 당김(세 발이 150ms 안에 나가 화살비로 묶인다)
          if (M.mounted && r37()) r37().play("sfx_bow_draw", { pan: r37Pan(en.x), v: 1.1 });
        } else if (pat === "bombard") {''')
rep('''fireMobShot(g, en, { sx: en.x + en.facing * 60, sz: en.z, ux: F.ux, uz: F.uz + rand(-0.03, 0.03), dmg: F.dmg, shot: "bullet", label: "''',
    '''fireMobShot(g, en, { sx: en.x + en.facing * 60, sz: en.z, ux: F.ux, uz: F.uz + rand(-0.03, 0.03), dmg: F.dmg, shot: "bullet", mg: true, label: "''')
rep('''        sfx(tl.shot === "arrow" ? "throw" : "shot");
        if (tl.shot !== "arrow") {''', '''        // [R37] 화살 = 활 발사(기마 궁수는 전투 활 · 150ms 안 3발이면 화살비 한 번으로) · 총탄 = 소총(5시대 조총은 조금 낮게) · 기관총(mg)은 예전 소리
        if (!(r37() && !tl.mg && (tl.shot === "arrow" ? r37().arrowShot(r37Pan(tl.sx), { full: !!mounted }) : r37().play("sfx_rifle_shot", { pan: r37Pan(tl.sx), r: g.era === 5 ? 0.92 : 1 })))) sfx(tl.shot === "arrow" ? "throw" : "shot");
        if (tl.shot !== "arrow") {''')
rep('''          addBeam(g, { kind: "arrows", x: tl.x, z: tl.z, ang: tl.ang, len: tl.len, life: 14, seed: Math.random() * 100 });
          sfx("throw");''', '''          addBeam(g, { kind: "arrows", x: tl.x, z: tl.z, ang: tl.ang, len: tl.len, life: 14, seed: Math.random() * 100 });
          // [R37] 보스의 부채꼴 화살 세례 = 화살비 한 번(다섯 줄기가 0.4초 안에 풀리므로 쿨다운으로 한 번만)
          if (!(r37() && r37().play("sfx_arrow_volley", { pan: r37Pan(tl.x), cool: 400 }))) sfx("throw");''')

# ───────── 13. 주인공 화기(6시대 모젤 · 소총 · 3타 사격) ─────────
rep('''      sfx("gunPistol");
      g.airMauser = (g.airMauser || 0) + 1;''', '''      // [R37] 모젤 권총 = 새 권총 녹음(소총 #2 +18% 가공)
      if (!(r37() && r37().play("sfx_pistol_shot"))) sfx("gunPistol");
      g.airMauser = (g.airMauser || 0) + 1;''')
rep('''      sfx("gunRifle");
      const E6 = g.r33e6 || (g.r33e6 = {});''', '''      // [R37] 각성 소총 = 새 볼트액션 소총 녹음(조금 낮고 크게)
      if (!(r37() && r37().play("sfx_rifle_shot", { v: 1.1, r: 0.95 }))) sfx("gunRifle");
      const E6 = g.r33e6 || (g.r33e6 = {});''')
rep('''          sfx(g.era === 6 ? "gunPistol" : "shot");''', '''          // [R37] 6시대 3타 모젤 = 새 권총 녹음(5시대 신기전은 예전 소리)
          if (!(g.era === 6 && r37() && r37().play("sfx_pistol_shot"))) sfx(g.era === 6 ? "gunPistol" : "shot");''')
rep('''        const eObj = eraObjOf();
        sfx("shot");''', '''        const eObj = eraObjOf();
        // [R37] 6시대 투척 무기(총격)도 새 권총 녹음
        if (!(g.era === 6 && r37() && r37().play("sfx_pistol_shot"))) sfx("shot");''')

# ───────── 14. 부처님의 가호 ─────────
rep('''      sfx("buddhaBell");
      setTimeout(() => sfx("buddhaChime"), 300);''', '''      // [R37] 에밀레종(새 녹음 · 최우선 · 0.6초 덕킹) → 0.3초 뒤 차임(R33) → 0.5초 뒤 광명 오라. 새 소리를 못 쓰면 R33 범종
      {
        const E = r37();
        if (E && E.play("sfx_buddha_emille_bell", { force: true })) {
          E.duck(0.35, 0.6, 0.5);
          E.play("sfx_buddha_light_aura", { force: true, d: 0.5, v: 0.85 });
        } else sfx("buddhaBell");
      }
      setTimeout(() => sfx("buddhaChime"), 300);''')

# ───────── 15. 시대별 미리 받기(Lazy preload) ─────────
rep('''      g.era = targetEra;
      setCurrentEra(targetEra);''', '''      g.era = targetEra;
      // [R37] 이 시대의 효과음 묶음을 받아 둔다(원화와 같은 때)
      if (sfxRef.current) sfxRef.current.r37preload(targetEra);
      setCurrentEra(targetEra);''')
rep('''              if (g.era < 6) loadEraAssets(g.era + 1, g.quality.dpr || 1);''', '''              if (g.era < 6) loadEraAssets(g.era + 1, g.quality.dpr || 1);
              // [R37] 다음 시대 효과음도 함께
              if (g.era < 6 && sfxRef.current) sfxRef.current.r37preload(g.era + 1);''')

# ───────── 16. 점검 훅 ─────────
rep('''        window.__RELIC_SFX = sfxRef.current;''', '''        window.__RELIC_SFX = sfxRef.current;
        // [R37] 음향감독 점검 훅: __SHINSI_SFX__.play("sfx_tiger_roar") · .loop(key, on) · .duck(0.35, 0.5, 0.5) · .stats · .keys() — 첫 입력(오디오 잠금 해제) 뒤에 엔진이 생긴다
        Object.defineProperty(window, "__SHINSI_SFX__", { configurable: true, get: () => sfxRef.current && sfxRef.current.r37 || null });''')
rep('''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),''', '''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),
          // [R37] 검증: 새 효과음 엔진 상태(받은 수 · 재생 수 · 키별 · 루프 · 덕킹 · 오류) · 새/옛 타격음 횟수 · 목소리 횟수 · 기병 루프 상태
          r37: () => {
            const E = sfxRef.current && sfxRef.current.r37;
            const g = gameRef.current;
            return { engine: E ? E.stats : null, k: E ? E.k : null, hit: { ...g.r37snd || {} }, voice: { ...g.r37voice || {} }, cav: g._r37 ? { ...g._r37 } : null };
          },''')

open(P, "w", encoding="utf-8").write(s)
print("R37 patch ok —", n, "edits")
