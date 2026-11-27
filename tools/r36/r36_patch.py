#!/usr/bin/env python3
"""R36 「짐승의 기척 · 갈래 기술」 — 오너 직접 피드백: ① 둔기 = 둔탁한 '퍽퍽' ② 동물 울음 · 함성(몹의 존재감) ③ 단조로운 콤보 → 갈래 기술.
(④ 왼손 파지는 코드로 못 고침 — 오른손 원화 발주서 `R36-art-order.md`)

사용: cp shinsi-R35/index.html shinsi-R36/index.html && python3 -I tools/r36/r36_patch.py shinsi-R36/index.html
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R36] 주석으로 이유를 남긴다.
주의: 옛 코드의 한글은 \\uXXXX 이스케이프로 저장돼 있다. 그런 문구를 찾을 땐 esc("한글")을 쓴다
      (도구 입력에 역슬래시-u-16진수를 직접 쓰면 실제 글자로 바뀌어 버림 — chr(92)로 만드는 이유).
      화면에 나오는 새 문자열도 esc()로 넣는다(파일을 직접 열 때 글자 깨짐 방지).
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
    """실제 글자 → 파일 속 이스케이프 표기(옛 부분 한글 찾기용 · 새 문자열 넣기용)."""
    return "".join((B + "u{%X}" % ord(c) if ord(c) > 0xFFFF else B + "u%04X" % ord(c)) if ord(c) > 127 else c for c in t)


# ───────── 1. 소리 표: 둔기 = thud_*(퍽) · 동물 울음 · 함성 ─────────
#  R35의 rock_*(돌 맞부딪는 울림 + 울리는 부스러기)는 "플라스틱 · 쇠파이프 깡깡"으로 들렸다(오너) → 울리는 음이 없는 thud_*로 교체.
#  rock_* 파일은 남기되(음향 점검 페이지 비교용) 게임에서는 받지 않는다.
rep('rockHit1: "rock_hit_1", rockHit2: "rock_hit_2", rockHeavy: "rock_heavy", rockCrush: "rock_crush",',
    'thudHit1: "thud_hit_1", thudHit2: "thud_hit_2", thudHeavy: "thud_heavy", thudCrush: "thud_crush",')
rep('thunder1: "thunder_crack_1", thunder2: "thunder_roll_2", warHorn: "war_horn_call" };',
    'thunder1: "thunder_crack_1", thunder2: "thunder_roll_2", warHorn: "war_horn_call", wolfHowl: "wolf_howl", wolfSnarl: "wolf_snarl", wolfYelp: "wolf_yelp", hyenaCackle: "hyena_cackle", bearRoar: "bear_roar", bearGrowl: "bear_growl", rhinoSnort: "rhino_snort", beastGroan: "beast_groan", tigerRoar: "tiger_roar", tigerSnarl: "tiger_snarl", warCry: "war_cry" };')
rep('rockHit1: 0.84, rockHit2: 0.84, rockHeavy: 0.98, rockCrush: 1,', 'thudHit1: 0.95, thudHit2: 0.95, thudHeavy: 1.05, thudCrush: 1.05,')
rep('whooshBlade: 0.3, whooshHeavy: 0.36 };',
    'whooshBlade: 0.3, whooshHeavy: 0.36, wolfHowl: 0.5, wolfSnarl: 0.62, wolfYelp: 0.5, hyenaCackle: 0.55, bearRoar: 0.85, bearGrowl: 0.75, rhinoSnort: 0.75, beastGroan: 0.7, tigerRoar: 1, tigerSnarl: 0.85, warCry: 0.5 };')
rep('rockHit1: 2, rockHit2: 2, rockHeavy: 2, rockCrush: 1,', 'thudHit1: 2, thudHit2: 2, thudHeavy: 2, thudCrush: 1,')
rep('whooshBlade: 2, whooshHeavy: 2 };',
    'whooshBlade: 2, whooshHeavy: 2, wolfHowl: 1, wolfSnarl: 2, wolfYelp: 2, hyenaCackle: 1, bearRoar: 1, bearGrowl: 2, rhinoSnort: 2, beastGroan: 2, tigerRoar: 1, tigerSnarl: 1, warCry: 1 };')
rep('rockHit1: 0.06, rockHit2: 0.06, rockHeavy: 0.03, rockCrush: 0.02,', 'thudHit1: 0.07, thudHit2: 0.07, thudHeavy: 0.04, thudCrush: 0.02,')
rep('whooshBlade: 0.09, whooshHeavy: 0.08 };',
    'whooshBlade: 0.09, whooshHeavy: 0.08, wolfHowl: 0.04, wolfSnarl: 0.1, wolfYelp: 0.12, hyenaCackle: 0.08, bearRoar: 0.05, bearGrowl: 0.08, rhinoSnort: 0.08, beastGroan: 0.08, tigerRoar: 0.03, tigerSnarl: 0.06, warCry: 0.05 };')
rep('rockHit1: "hit", rockHit2: "hit", rockHeavy: "crit", rockCrush: "crit",', 'thudHit1: "hit", thudHit2: "hit", thudHeavy: "crit", thudCrush: "crit",')
rep('whooshBlade: "swing", whooshHeavy: "swing" };',
    'whooshBlade: "swing", whooshHeavy: "swing", wolfHowl: "", wolfSnarl: "", wolfYelp: "", hyenaCackle: "", bearRoar: "bossRoar", bearGrowl: "", rhinoSnort: "", beastGroan: "", tigerRoar: "bossRoar", tigerSnarl: "bossRoar", warCry: "" };')
rep('''      else if (cls === "AXE") name = lv === "light" ? n % 2 ? "rockHit1" : "rockHit2" : lv === "crush" || lv === "sever" ? "rockCrush" : "rockHeavy";''',
    '''      // [R36] 둔기 = 둔탁한 '퍽'(thud_*) — R35의 돌 소리(rock_*)는 울리는 음 때문에 파이프 · 플라스틱처럼 들렸다
      else if (cls === "AXE") name = lv === "light" ? n % 2 ? "thudHit1" : "thudHit2" : lv === "crush" || lv === "sever" ? "thudCrush" : "thudHeavy";''')
rep('''            sfx("rockHit2", { r: 0.86 });''', '''            sfx("thudHit2", { r: 0.92 });''')

# ───────── 2. 몹의 목소리: 등장 · 공격 예고 · 쓰러질 때 · 기척 · 보스 포효 ─────────
rep('''    // 휘두르는 바람: 둔기는 낮게(부웅) · 칼 · 창은 가늘게(휙)
''', '''    // [R36] 몹의 목소리 — "동물들은 소리가 없나요? 몹이 압도해 줘야 하는데"(오너).
    //  같은 소리가 겹쳐 시끄럽지 않게 소리마다 최소 간격(gap 틱)을 둔다. 재생 횟수는 g.r36voice에 남긴다(검증용)
    const r36Voice = (key, gap, o) => {
      const g = gameRef.current;
      const V = g._r36v || (g._r36v = {});
      if (g.tick - (V[key] != null ? V[key] : -1e9) < gap) return false;
      V[key] = g.tick;
      const L = g.r36voice || (g.r36voice = {});
      L[key] = (L[key] || 0) + 1;
      sfx(key, o);
      return true;
    };
    // 1시대 짐승: [소리, 음높이, 볼륨] — atk = 공격 예고(덮치기 0.3초 전 · 귀로도 피할 수 있게) · die = 쓰러질 때 · idle = 기척
    const R36_BEAST = {
      WOLF: { atk: ["wolfSnarl", 1, 0.9], die: ["wolfYelp", 1, 0.9], idle: ["wolfSnarl", 0.84, 0.42] },
      HYENA: { atk: ["wolfSnarl", 1.3, 0.78], die: ["wolfYelp", 1.22, 0.85], idle: ["hyenaCackle", 1, 0.5] },
      BEAR: { atk: ["bearGrowl", 1, 1], die: ["beastGroan", 1, 1], idle: ["bearGrowl", 0.86, 0.5] },
      RHINO: { atk: ["rhinoSnort", 1, 1], die: ["beastGroan", 0.86, 1], idle: ["rhinoSnort", 0.9, 0.5] }
    };
    const r36MobVoice = (en, ev) => {
      const T = en && en.mobRole && R36_BEAST[en.mobRole];
      if (!T) return;
      const [key, r, v] = T[ev];
      const big = en.isMidBoss ? 0.8 : en.elite ? 0.9 : 1;
      r36Voice(key, ev === "die" ? 8 : ev === "idle" ? 90 : 26, { r: r * big, v: v * (en.isMidBoss ? 1.15 : 1) });
    };
    // 보스 포효: 1시대 = 산군(호랑이) · 동굴 곰의 울음 / 그 밖의 시대 = 기존 합성 포효
    const r36Roar = (kind) => {
      const g = gameRef.current;
      if (g.era !== 1) {
        sfx("bossRoar");
        return;
      }
      const L = g.r36voice || (g.r36voice = {});
      const key = kind === "bear" ? "bearRoar" : kind === "snarl" ? "tigerSnarl" : "tigerRoar";
      L[key] = (L[key] || 0) + 1;
      // 곰 = 더 낮고 크게 · 쓰러질 때 = 낮게 늘어지는 마지막 포효
      sfx(key, kind === "bear" ? { v: 1.15, r: 0.88 } : kind === "death" ? { r: 0.82 } : null);
    };
    // 휘두르는 바람: 둔기는 낮게(부웅) · 칼 · 창은 가늘게(휙)
''')
# 웨이브 등장: 무리의 울음 / 병사들의 함성(못 쓰면 예전 경보음)
rep('''      sfx("alarm");
    };
    const announceSubStage = (zi) => {''', '''      // [R36] 웨이브 등장 소리 — 1시대: 그 무리의 울음(곰 · 코뿔소 · 늑대 · 하이에나 가운데 둘까지, 조금씩 엇갈려) · 2~6시대: 병사들의 함성.
      //  울음 · 함성이 방금 났으면(최소 간격) 예전 경보음으로 대신한다
      let cue = 0;
      if (g.era === 1 && roles) {
        [["BEAR", "bearRoar", 420, 0.85, 4], ["RHINO", "rhinoSnort", 300, 0.9, 14], ["WOLF", "wolfHowl", 480, 0.9, 2], ["HYENA", "hyenaCackle", 300, 0.9, 20]].forEach(([role, key, gap, v, delay]) => {
          if (cue >= 2 || roles.indexOf(role) < 0) return;
          const V = g._r36v || (g._r36v = {});
          if (g.tick - (V[key] != null ? V[key] : -1e9) < gap) return;
          cue++;
          addTimer(delay, () => {
            r36Voice(key, 0, { v });
            // 큰 짐승의 울음은 화면도 살짝 흔든다
            if (role === "BEAR" || role === "RHINO") addTrauma(role === "BEAR" ? 0.22 : 0.14);
          });
        });
      } else if (g.era >= 2 && r36Voice("warCry", 420, { v: Math.min(1.15, 0.8 + n * 0.04), r: 0.95 + Math.random() * 0.1 })) cue++;
      if (!cue) sfx("alarm");
    };
    const announceSubStage = (zi) => {''')
# 공격 예고 · 쓰러질 때
rep('''                if (en.attackCooldown === 18) en.windupTimer = 18;''', '''                if (en.attackCooldown === 18) {
                  en.windupTimer = 18;
                  // [R36] 덮치기 직전의 으르렁 — 공격 예고
                  r36MobVoice(en, "atk");
                }''')
rep('''            en.state = "DYING";
''', '''            en.state = "DYING";
            // [R36] 쓰러지는 소리(늑대 · 하이에나 = 깨갱 / 곰 · 코뿔소 = 낮은 신음)
            r36MobVoice(en, "die");
''')
# 기척: 살아 있는 짐승이 4~7초마다 한 번 낮게 운다
rep('''        if (g.sfxHitGate > 0) g.sfxHitGate--;''', '''        if (g.sfxHitGate > 0) g.sfxHitGate--;
        // [R36] 짐승의 기척(1시대): 4~7초마다 살아 있는 한 마리가 낮게 운다 — 화면 밖에서 다가오는 무리가 귀로 느껴지게
        if (g.era === 1) {
          g._r36idle = (g._r36idle == null ? 150 : g._r36idle) - 1;
          if (g._r36idle <= 0) {
            g._r36idle = 240 + Math.floor(Math.random() * 190);
            let pick = null;
            let k = 0;
            for (let i = 0; i < g.enemies.length; i++) {
              const e2 = g.enemies[i];
              if (e2.mobRole && e2.state === "ACTIVE" && Math.random() < 1 / ++k) pick = e2;
            }
            if (pick) r36MobVoice(pick, "idle");
          }
        }''')
# 보스 · 중간보스 포효
rep('''      g.slowMo = 26;
      sfx("bossRoar");
      for (let k = 0; k < 5; k++) {''', '''      g.slowMo = 26;
      r36Roar("death");
      for (let k = 0; k < 5; k++) {''')
rep('''      addTrauma(0.5);
      sfx("bossRoar");
      setPlayerBubble(`\\u{1F479} ''' + esc("중간보스") + ''' [${mb.name}] ''' + esc("출현") + '''!`, 120);''', '''      addTrauma(0.5);
      r36Roar("bear");
      setPlayerBubble(`\\u{1F479} ''' + esc("중간보스") + ''' [${mb.name}] ''' + esc("출현") + '''!`, 120);''')
rep('''      addTimer(56, () => {
        sfx("bossRoar");''', '''      addTimer(56, () => {
        r36Roar("roar");''')
rep('''          b.facing = dir;
          sfx("bossRoar");''', '''          b.facing = dir;
          r36Roar("snarl");''')
rep('''              b.enraged = true;
              sfx("bossRoar");''', '''              b.enraged = true;
              r36Roar("roar");''')

# ───────── 3. 갈래 기술: 연타의 마무리가 매번 같지 않게 ─────────
rep('''    const triggerEraWeaponCombo = () => {
      var _a;''', '''    // [R36] 갈래 기술 — "단조로운 콤보 아쉽습니다"(오너).
    //  ① 연타 2타째부터 ▲ + 공격 = 올려치기(적을 높이 띄움 → 이어서 공격 = 뛰어올라 공중 추격) · ▼ + 공격 = 내려찍기(둘레 충격 · 기절)
    //  ② 방향 없이 연타만 해도 마지막 타가 바퀴마다 바뀐다: 기존 마무리 → 내려찍기 → 관통 돌진(낮은 레벨 · 2시대는 조금 다름)
    //  새 원화 없이 있는 동작으로: 올려치기 = atk2 · 내려찍기 = atk3(없으면 atk1) · 관통 돌진 = atk1(4시대는 돌진 자세)
    const R36_BR = { launch: ["''' + esc("올려치기!") + '''", "#38bdf8"], slam: ["''' + esc("내려찍기!") + '''", "#f59e0b"], lunge: ["''' + esc("관통 돌진!") + '''", "#22d3ee"], chase: ["''' + esc("공중 추격!") + '''", "#a78bfa"] };
    // 이름표 글자를 미리 구워 둔다(전투 중 처음 그릴 때의 프레임 튐 방지 — drawDamagePopups와 같은 글꼴 · 색 인자)
    const r36WarmText = () => {
      try {
        const c = document.createElement("canvas");
        c.width = c.height = 8;
        const x = c.getContext("2d");
        Object.keys(R36_BR).forEach((k) => drawTextSprite(x, R36_BR[k][0], 0, 0, "italic 900 26px system-ui, sans-serif", 26, "", "#090d16", 5, `-18,4|0:#ffffff;1:${R36_BR[k][1]}`));
      } catch (e) {
      }
    };
    const r36Pop = (kind, h = 112) => {
      const g = gameRef.current;
      const p = g.player;
      const L = g.r36branch || (g.r36branch = { launch: 0, slam: 0, lunge: 0, chase: 0, classic: 0 });
      L[kind]++;
      addDamagePopup(p.x, p.z, p.y + h, R36_BR[kind][0], true, null, 0, R36_BR[kind][1]);
    };
    //  위력은 '몇 타째에 썼나'(pos = 1~N)에 따라 — 일찍 끊을수록 약하게(▼만 반복하는 것이 정답이 되지 않게) · 마지막 자리에서는 기존 마무리와 비슷하게
    const r36Branch = (kind, N, eObj, pos) => {
      const g = gameRef.current;
      const p = g.player;
      const cls = heroWeaponClass(g.era, g.stats.weaponTier || 1);
      const axe = cls === "AXE";
      const C = R30C(g);
      const full = pos >= N;
      const big = N === 4 && full;
      // 마무리 기술로 친다: Lv.3+ 는 4타 자리(뒤이은 질풍연참 연결 그대로) · 낮은 레벨은 처음 타로 돌아감
      p._brLock = true;
      p.comboStep = N === 4 ? 4 : 0;
      p.comboResetTimer = 58;
      p._spinAtk = p._r31slam = false;
      p.state = "ATTACK";
      p.lastAttackClass = cls;
      r36Pop(kind);
      if (kind === "launch") {
        p._atkSrc = "branch";
        p._fin = false;
        p.atkAnim = "atk2";
        p.maxAttackTimer = p.attackTimer = axe ? 18 : 15;
        p.vx = p.facing * 4;
        queueActiveFrame(axe ? 6 : 4, () => {
          const g2 = gameRef.current;
          const pp = g2.player;
          const ix = pp.x + pp.facing * 60;
          spawnDust(ix, pp.z, 7, 3.2);
          addShock(ix, pp.z, eObj.bladeGlow, 96, 16);
          pushRibbon({ h: 70, dx: 30, rx: 120, ry: 40, rot: -1.3, a0: Math.PI - 0.25, a1: 0.25, w: 15, dur: 320, col: C[1] });
          g2._comboStep = 4;
          g2._cutAng = -1.15;
          const hit = checkMeleeHitbox(175, 66, 1.15 + pos * 0.15, 2.5, 17, 1, true);
          g2._comboStep = 0;
          g2._cutAng = null;
          // 띄웠으면 0.7초 동안 '공격 = 뛰어올라 추격'
          if (hit) pp._chaseUntil = g2.tick + 44;
        });
      } else if (kind === "slam") {
        // 2시대 해모수 Lv.3+ = 기존 '곰의 내려찍기' 자세(slam_prep → slam_hit) · 곰 · 천둥 원화 이펙트 그대로
        const e2 = g.era === 2;
        p._atkSrc = e2 && N === 4 ? "combo" : "branch";
        p._r31slam = e2 && N === 4;
        p._fin = true;
        p.atkAnim = "atk1";
        p.maxAttackTimer = p.attackTimer = axe ? 26 : e2 ? 24 : 22;
        p.vx = p.facing * 2;
        queueActiveFrame(axe ? 11 : e2 ? 10 : 9, () => {
          const g2 = gameRef.current;
          const pp = g2.player;
          const ix = pp.x + pp.facing * 66;
          if (e2) r31Slam(ix, pp.z, false);
          else {
            addGroundCraterDecal(ix, pp.z, 86);
            spawnShards(ix, pp.z, 12, 18, pp.facing);
            spawnDust(ix, pp.z, 12, 4.4);
            addTrauma(0.5);
          }
          addShock(ix, pp.z, eObj.bladeGlow, 210, 22);
          addShock(ix, pp.z, "#ffffff", 120, 14);
          kickDirShake(g2, pp.facing, 9);
          pushRibbon({ h: 66, dx: 44, rx: 118, ry: 44, rot: 1.32, a0: Math.PI - 0.38, a1: 0.32, w: 18, dur: 320, col: C[0] });
          // 땅을 치는 소리(빗나가도 난다)
          sfx(axe ? "thudCrush" : "thudHeavy", { v: axe ? 0.9 : 0.7 });
          g2._comboStep = 4;
          g2._cutAng = 1.3;
          // Lv.3+ = 2연 강타 · Lv.1~2 = 한 번(기본 3타 사슬보다 지나치게 세지 않게)
          const R = areaSlash(200, 84, N === 4 ? 1.5 + pos * (axe ? 0.28 : 0.24) : 1.3 + pos * 0.3, 7, 11.5, N === 4 ? 2 : 1, true);
          g2._comboStep = 0;
          g2._cutAng = null;
          // 충격에 휘말린 적은 잠깐 기절(중간보스 제외)
          if (R.hits) {
            for (let i = 0; i < g2.enemies.length; i++) {
              const en = g2.enemies[i];
              if (en.state !== "DYING" && !en.isMidBoss && Math.abs(en.x - pp.x) <= 200 && Math.abs(en.z - pp.z) <= 84) en.hitStun = Math.max(en.hitStun || 0, 38);
            }
          }
          g2.targetZoom = 1.05;
          addTimer(9, () => {
            gameRef.current.targetZoom = 1;
          });
          breathFX(2);
        });
      } else {
        p._atkSrc = "dash";
        // 진짜 돌진이 아니므로 '돌진 → 공격 연결(DASH LINK)'은 걸리지 않게
        p._dashTick = -999;
        p._fin = false;
        p.atkAnim = "atk1";
        p.maxAttackTimer = p.attackTimer = 15;
        p.vx = p.facing * 24;
        p.invincibleTimer = Math.max(p.invincibleTimer || 0, 14);
        for (let i = 1; i <= 3; i++) p.ghosts.push({ x: p.x - p.facing * i * 22, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i, name: p._assetFrame, alpha: 0.55 - i * 0.12 });
        spawnDust(p.x - p.facing * 16, p.z, 5, 2.6);
        sfx("dash", { v: 0.6 });
        queueActiveFrame(4, () => {
          const g2 = gameRef.current;
          const pp = g2.player;
          pushRibbon({ h: 58, dx: 110, rx: 290, ry: 24, rot: -0.02, a0: Math.PI + 0.25, a1: -0.25, w: 16, dur: 380, col: C[0] });
          pushSlashFx(pp.x + pp.facing * 110, pp.z - pp.y - 58, 0.03, pp.facing, { len: 520, w: 8, dur: 300, heavy: true, sparks: 8 });
          g2._comboStep = 4;
          g2._cutAng = 0.04;
          g2._bowlFin = true;
          const hit = checkMeleeHitbox(250, 44, big ? 2.3 : 1.8, 17, 4, big ? 2 : 1, true);
          g2._bowlFin = false;
          g2._comboStep = 0;
          g2._cutAng = null;
          if (hit) kickDirShake(g2, pp.facing, 8);
        });
      }
    };
    const triggerEraWeaponCombo = () => {
      var _a;''')
# 공중 추격: 올려치기로 띄운 직후의 공격 = 남은 동작을 끊고 뛰어오름(이어지는 공격은 기존 공중 연타)
rep('''      if (p.attackTimer > 4) {
        p.bufferAtk = true;
        return;
      }
      const eObj = relicPal(g, eraObjOf());
      r35Whoosh();''', '''      if (!g._r36warm) {
        g._r36warm = true;
        r36WarmText();
      }
      // [R36] 공중 추격 — 올려치기로 띄운 뒤 0.7초 안의 공격: 남은 동작을 끊고 뛰어올라 쫓아간다(다음 공격부터 기존 공중 연타 → AIR RAID)
      if (p._chaseUntil && g.tick <= p._chaseUntil && p.y <= 2 && !p.grab) {
        p._chaseUntil = 0;
        p.attackTimer = 0;
        p.pendingHit = null;
        p.comboStep = 0;
        p.airHits = 0;
        p.vy = 15.6;
        p.vx = p.facing * 3.5;
        p.bufferAtk = false;
        // 조금 떠오른 다음(5틱 뒤) 첫 공중 베기가 저절로 나간다 — 그 뒤는 누르는 대로 공중 연타
        addTimer(5, () => {
          const pp = gameRef.current.player;
          if (pp.y > 10 && !pp.plunge && pp.attackTimer <= 4 && !(pp.downTimer > 0)) triggerEraWeaponCombo();
        });
        sfx("jump");
        spawnDust(p.x, p.z, 6, 2.6);
        addShock(p.x, p.z, eraObjOf().bladeGlow, 70, 14);
        // 바로 앞의 '올려치기!' 이름표와 겹치지 않게 조금 낮게
        r36Pop("chase", 70);
        return;
      }
      if (p.attackTimer > 4) {
        p.bufferAtk = true;
        return;
      }
      const eObj = relicPal(g, eraObjOf());
      r35Whoosh();''')
rep('''      p.comboStep = p.comboStep % (g.stats.level >= SKILL_LV.finisher ? 4 : 3) + 1;''', '''      // [R36] 갈래 기술 고르기 — ▲/▼를 누른 채면 그 기술, 아니면 마지막 타 자리에서 바퀴마다 돌아가며
      {
        const N = g.stats.level >= SKILL_LV.finisher ? 4 : 3;
        let br = null;
        const pos = p.comboStep % N + 1;
        if (p.comboStep >= 1 && p.comboResetTimer > 0 && !dashLink && !p._brLock) {
          if (g.keys.up && !g.keys.down) br = "launch";
          else if (g.keys.down && !g.keys.up) br = "slam";
          if (br) g.r36dirUsed = (g.r36dirUsed || 0) + 1;
        }
        if (!br && !dashLink && pos === N) {
          // 마무리 돌림: 기본 = 기존 → 내려찍기 → 관통 돌진 · 2시대(기존 마무리가 내려찍기) = 기존 → 관통 돌진 → 올려치기 · Lv.1~2 = 기존 → 관통 돌진
          const ROT = N === 3 ? [null, "lunge"] : g.era === 2 ? [null, "lunge", "launch"] : [null, "slam", "lunge"];
          p._finRot = ((p._finRot == null ? -1 : p._finRot) + 1) % ROT.length;
          br = ROT[p._finRot];
          g.r36fin = (g.r36fin || 0) + 1;
          if (!br) (g.r36branch || (g.r36branch = { launch: 0, slam: 0, lunge: 0, chase: 0, classic: 0 })).classic++;
          // 세 번째 마무리쯤, 방향 갈래를 아직 안 써 봤으면 한 번 알려 준다
          if (g.r36fin === 3 && !g.r36dirUsed && !g.r36hint) {
            g.r36hint = true;
            setCompanionBubble("''' + esc("💡 연타 중에 ▲ + 공격 = 올려치기, ▼ + 공격 = 내려찍기! 띄운 다음 공격을 누르면 뛰어올라 쫓아가요") + '''", 210);
          }
        }
        if (br) {
          r36Branch(br, N, eObj, pos);
          return;
        }
        p._brLock = false;
      }
      p.comboStep = p.comboStep % (g.stats.level >= SKILL_LV.finisher ? 4 : 3) + 1;''')
# 조작 안내(타이틀 · 일시정지 화면)
rep(esc("크래시는 체력 10%로 포위 탈출") + '")',
    esc("크래시는 체력 10%로 포위 탈출") + '", /* @__PURE__ */ React.createElement("br", null), "' + esc("연타 중 ▲ + 공격 = 올려치기 · ▼ + 공격 = 내려찍기 · 띄운 뒤 공격 = 공중 추격") + '")')
rep('["' + esc("돌진 / 어퍼") + '", "K ' + B + 'xB7 Z / L ' + B + 'xB7 X"],',
    '["' + esc("돌진 / 어퍼") + '", "K ' + B + 'xB7 Z / L ' + B + 'xB7 X"],\n        ["' + esc("갈래 기술 (연타 중)") + '", "' + esc("▲+공격 올려치기 · ▼+공격 내려찍기") + '"],')

# ───────── 4. DEV 훅(검증용) ─────────
rep('''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),''', '''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),
          // [R36] 검증: 갈래 기술 횟수 · 몹 목소리 횟수 · 마무리 돌림 위치
          r36: () => ({ branch: { ...gameRef.current.r36branch || {} }, voice: { ...gameRef.current.r36voice || {} }, fin: gameRef.current.r36fin || 0, dirUsed: gameRef.current.r36dirUsed || 0, hint: !!gameRef.current.r36hint, rot: gameRef.current.player._finRot }),''')

open(P, "w", encoding="utf-8").write(s)
print("R36 patch ok —", n, "edits")
