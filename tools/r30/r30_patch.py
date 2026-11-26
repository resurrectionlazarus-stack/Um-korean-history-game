#!/usr/bin/env python3
"""R30 — 정식 원화 2종 연결 · 2시대 동시 적 상한 · Lv.1~5 입체 콤보 · 조건부 일섬(3시대 황금 용오름) · 3D 검기 리본 · 잔상 · 주인공 오라.

사용: python3 -I r30_patch.py <shinsi-R30/index.html>   (R29 index.html 위에 적용)
"""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"anchor count {c}: {old[:120]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 0. 정식 원화: 김유신 질주 8장 · 연/한 병사 5종 ─────────
rep('''    era3_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8"], poseDX: { run3: -23, run4: 4, run5: 18, run6: -23, run7: -28, run8: 8 }, groundY: 470, anchorX: 282,''',
    '''    // [R30] 미술팀 정식 김유신 질주 8장(run~run8 전면 재작성 · groundY 470 · topY 34~35 · 8장 머리 x 361~369로 이미 정렬) → R28 poseDX 보정 제거.
    //  anchorX 282 유지: 새 8장 허리 중심 258~307(평균 280) · idle 윗몸 중심 283.5와 맞음(앞으로 기운 질주라 머리만 앞으로 나감)
    era3_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8"], groundY: 470, anchorX: 282,''')

rep('''    yan_pike: { era: 2, unit: "YAN_PIKE", h: 132 },
    yan_archer: { era: 2, unit: "YAN_ARCHER", h: 128 },
    han_pike: { era: 2, unit: "HAN_PIKE", h: 134 },
    han_archer: { era: 2, unit: "HAN_ARCHER", h: 130 },
    han_elite: { era: 2, unit: "HAN_ELITE", h: 150 },''',
    '''    // [R30] 미술팀 정식 원화 15장(webp)으로 교체 — 원본이 저채도 · 어두운 톤(실측 밝기 38~41 · 채도 0.15~0.2, 톤다운된 4~6시대 몹 31~38과 같은 대)이라 굽기 톤다운 생략
    yan_pike: { era: 2, unit: "YAN_PIKE", h: 132, toned: true },
    yan_archer: { era: 2, unit: "YAN_ARCHER", h: 128, toned: true },
    han_pike: { era: 2, unit: "HAN_PIKE", h: 134, toned: true },
    han_archer: { era: 2, unit: "HAN_ARCHER", h: 130, toned: true },
    han_elite: { era: 2, unit: "HAN_ELITE", h: 150, toned: true },''')

# ───────── 1. 상수 · 오라 단계 ─────────
rep('''  // [R29] Lv.4 질풍연참 연참 수(마지막 일섬 제외)
  var R29_RUSH_HITS = 5;''',
    '''  // [R29] Lv.4 질풍연참 연참 수(마지막 일섬 제외)
  var R29_RUSH_HITS = 5;
  // [R30] 시대별 고유색 [주색, 보조색, 밝은 심] — 오라 · 입체 검기 · 시공 일섬
  //  1 황토 · 불꽃 / 2 고조선 금빛 태양 / 3 신라 황금 · 비취 / 4 고려 청룡 검기 / 5 조선 홍염 / 6 광복 백 · 청 태극 기류
  var R30_ERA_COL = { 1: ["#f59e0b", "#fb923c", "#fde68a"], 2: ["#facc15", "#fde047", "#fff7cc"], 3: ["#fbbf24", "#34d399", "#fef3c7"], 4: ["#22d3ee", "#38bdf8", "#e0f2fe"], 5: ["#ef4444", "#fb7185", "#fecaca"], 6: ["#f8fafc", "#3b82f6", "#dbeafe"] };
  // [R30] 조건부 일섬: 콤보 15(S랭크) 이상에서 4타 피니시 적중 · 저스트 패링 뒤 1초(60틱) 안에 J — 다시 터지기까지 8초(480틱)
  var R30_SPECIAL_COMBO = 15;
  var R30_PARRY_WINDOW = 60;
  var R30_SPECIAL_CD = 480;
  // [R30] 동시 활성 적 상한(2시대 7명) — 넘치는 적은 대기열에서 18틱마다 1명씩(웨이브 분할)
  var ACTIVE_CAP = { 2: 7 };
  // [R30] 오라 단계: 레벨(Lv.1 → 1 · Lv.2~3 → 2 · Lv.4~5 → 3)과 무기 진화(T1 → 1 · T2 → 2 · T3 → 3) 중 높은 쪽,
  //  콤보 S랭크 이상(S · SS · SSS) 또는 유물 각성 중이면 +1(최대 4 = 팽창)
  function auraStageOf(g) {
    const st = g.stats || {};
    const lv = st.level || 1;
    const wt = st.weaponTier || 1;
    let a = Math.max(lv >= 4 ? 3 : lv >= 2 ? 2 : 1, wt >= 3 ? 3 : wt >= 2 ? 2 : 1);
    const rk = getComboRank(st.combo || 0).rank;
    if (rk === "S" || rk === "SS" || rk === "SSS" || g.relicBuff || g.relicFx) a += 1;
    return Math.min(4, a);
  }
  // [R30] 오라 불꽃 스프라이트(색마다 32×72 한 장 · 둥근 밑동 → 투명한 끝 + 흰 심) — ctx.filter 없이 그라디언트로만 굽는다
  var _flameCache = /* @__PURE__ */ new Map();
  function flameSprite(col) {
    let c = _flameCache.get(col);
    if (c) return c;
    c = document.createElement("canvas");
    c.width = 32;
    c.height = 72;
    const x = c.getContext("2d");
    const rgb = hexRgb(col);
    const tear = () => {
      x.beginPath();
      x.moveTo(16, 4);
      x.bezierCurveTo(27, 26, 31, 52, 16, 70);
      x.bezierCurveTo(1, 52, 5, 26, 16, 4);
      x.closePath();
    };
    let gr = x.createLinearGradient(0, 70, 0, 4);
    gr.addColorStop(0, rgbaStr(rgb, 0.9));
    gr.addColorStop(0.5, rgbaStr(rgb, 0.55));
    gr.addColorStop(1, rgbaStr(rgb, 0));
    x.fillStyle = gr;
    tear();
    x.fill();
    x.save();
    x.translate(16, 70);
    x.scale(0.45, 0.6);
    x.translate(-16, -70);
    gr = x.createLinearGradient(0, 70, 0, 4);
    gr.addColorStop(0, "rgba(255,255,255,0.85)");
    gr.addColorStop(1, "rgba(255,255,255,0)");
    x.fillStyle = gr;
    tear();
    x.fill();
    x.restore();
    _flameCache.set(col, c);
    return c;
  }''')

rep('''    if (combo >= 18) return { rank: "S", title: "HEROIC VANGUARD", color: "#facc15" };''',
    '''    // [R30] S랭크 18 → 15(조건부 일섬 '15콤보 S랭크' 기준과 맞춤)
    if (combo >= 15) return { rank: "S", title: "HEROIC VANGUARD", color: "#facc15" };''')

# ───────── 2. 기술 해금 안내 ─────────
rep('''    2: { kind: "UNLOCK", title: "어퍼컷 · 띄우기 해금", short: "어퍼", key: "L · X", desc: "적을 띄워 공중 콤보로! 공중에서 J 3번 뒤 한 번 더 누르면 내리꽂기(AIR RAID)",''',
    '''    2: { kind: "UNLOCK", title: "비연 올려베기 · 공중 X자 십자검기", short: "비연", key: "L · X", desc: "L로 올려베어 띄우고, 공중 J 2 · 3타마다 X자 십자검기! 공중 J 3번 뒤 한 번 더 = 내리꽂기(AIR RAID)",''')
rep('''    3: { kind: "EVOLVE", title: "4타 피니시 · 돌진 진화", short: "4타 피니시", key: "J 4연타 · K", desc: "네 번째 타격이 피니시로 폭발하고, 돌진은 잔상을 남기며 더 멀리 · 더 세게! 돌진 뒤 J는 곧바로 3타(DASH LINK)",''',
    '''    3: { kind: "EVOLVE", title: "360° 원월 회전참 · 돌진 진화", short: "원월 회전참", key: "J 4연타 · K", desc: "4타 피니시가 앞뒤를 감싸 도는 360° 회전 검풍으로! 돌진은 더 멀리 · 더 세게, 돌진 뒤 J는 곧바로 3타(DASH LINK)",''')
rep('''    4: { kind: "EVOLVE", title: "5타 질풍연참", short: "질풍연참", key: "J 5연타", desc: "4타 피니시 직후 J 한 번 더 — 다섯 줄기 연참 뒤 화면을 가르는 일섬!",''',
    '''    4: { kind: "EVOLVE", title: "질풍연참 + 일섬", short: "질풍연참", key: "J 5연타", desc: "4타 피니시 직후 J 한 번 더 — 깊이감 있는 다섯 줄기 연참 · 잔상 뒤 화면을 가르는 일섬!",''')
rep('''    5: { kind: "AWAKEN", title: "진(眞) 각성 오의", short: "진 각성", key: "U · F", desc: "각성기가 진(眞) 각성으로 — 참격 5연 · 황금 빛기둥 · 피해 증가",''',
    '''    5: { kind: "AWAKEN", title: "진 각성 · 급강하 파동격", short: "파동격", key: "U · F · J", desc: "일섬 뒤 · 공중 내리꽂기가 도약 급강하 파동격(충격파 + 양쪽 X자 검기)으로! 각성기는 진(眞) 각성 — 참격 5연 · 황금 빛기둥",''')

# ───────── 3. 2시대 동시 적 상한 · 웨이브 분할 ─────────
rep('''      const n = roles ? roles.length : count;
      for (let i = 0; i < n; i++) {
        const side = i % 2 === 0 ? -1 : 1;
        const flank = side;
        const role = roles ? roles[i] : null;
        if (i % 3 === 2) {
          spawnEnemyAt(L + 180 + Math.random() * (VIEW_W - 360), 356 + Math.random() * 120, { circle: true, flank, role });
        } else {
          spawnEnemyAt(side < 0 ? L - 60 - Math.random() * 70 : L + VIEW_W + 60 + Math.random() * 70, 356 + Math.random() * 120, { flank, role });
        }
      }''',
    '''      const n = roles ? roles.length : count;
      // [R30] 동시 활성 적 상한(2시대 7명) — 넘치는 적은 대기열(g.spawnQ)에 넣고, 자리가 나면 18틱마다 1명씩 들여보낸다(웨이브 분할)
      const CAP = ACTIVE_CAP[g.era] || 0;
      let alive0 = 0;
      for (let i = 0; i < g.enemies.length; i++) if (g.enemies[i].state !== "DYING") alive0++;
      const put = (x, z, o) => {
        if (CAP && alive0 >= CAP) {
          (g.spawnQ || (g.spawnQ = [])).push({ x, z, o });
          return;
        }
        spawnEnemyAt(x, z, o);
        if (o.mobScale) g.enemies[g.enemies.length - 1].mobScale = o.mobScale;
        alive0++;
      };
      for (let i = 0; i < n; i++) {
        const side = i % 2 === 0 ? -1 : 1;
        const flank = side;
        const role = roles ? roles[i] : null;
        if (i % 3 === 2) {
          put(L + 180 + Math.random() * (VIEW_W - 360), 356 + Math.random() * 120, { circle: true, flank, role });
        } else {
          put(side < 0 ? L - 60 - Math.random() * 70 : L + VIEW_W + 60 + Math.random() * 70, 356 + Math.random() * 120, { flank, role });
        }
      }''')

rep('''          spawnEnemyAt(L + VIEW_W + 70 + k * 70, 384 + k * 56, { flank: 1, unit: "HAN_ELITE" });
          g.enemies[g.enemies.length - 1].mobScale = 1.18;''',
    '''          put(L + VIEW_W + 70 + k * 70, 384 + k * 56, { flank: 1, unit: "HAN_ELITE", mobScale: 1.18 });''')

rep('''        } else if (g.zoneState === "LOCKED") {
          let alive = 0;
          for (let i = 0; i < g.enemies.length; i++) if (g.enemies[i].state !== "DYING") alive++;''',
    '''        } else if (g.zoneState === "LOCKED") {
          let alive = 0;
          for (let i = 0; i < g.enemies.length; i++) if (g.enemies[i].state !== "DYING") alive++;
          // [R30] 대기열 적 들여보내기 — 상한 아래로 자리가 나면 18틱마다 1명
          const SQ = g.spawnQ;
          if (SQ && SQ.length && alive < (ACTIVE_CAP[g.era] || 99)) {
            g.spawnQcd = (g.spawnQcd || 0) - 1;
            if (g.spawnQcd <= 0) {
              const q = SQ.shift();
              spawnEnemyAt(q.x, q.z, q.o);
              if (q.o.mobScale) g.enemies[g.enemies.length - 1].mobScale = q.o.mobScale;
              g.spawnQcd = 18;
              alive++;
              g.spawnQReleased = (g.spawnQReleased || 0) + 1;
            }
          }
          const qn = SQ ? SQ.length : 0;
          if (alive > (g.maxAlive || 0)) g.maxAlive = alive;''')

rep('''          } else if (g.era === 2 && g.waves.length && alive <= 2 && !g.bossActive) {''',
    '''          } else if (g.era === 2 && g.waves.length && alive <= 2 && !qn && !g.bossActive) {''')
rep('''          } else if (alive === 0 && !g.bossActive) {
            if (g.waves.length) g.waveSpawnCd = 26;''',
    '''          } else if (alive === 0 && !qn && !g.bossActive) {
            if (g.waves.length) g.waveSpawnCd = 26;''')

rep('''      g.waves = era === 4 ? (ERA4_ZONE_WAVES[zi] || []).slice() : era === 2 ? (ERA2_ZONE_WAVES[zi] || []).slice() : ZONE_WAVES[zi].map((n) => n + bonus);''',
    '''      g.spawnQ = [];
      g.spawnQcd = 0;
      g.waves = era === 4 ? (ERA4_ZONE_WAVES[zi] || []).slice() : era === 2 ? (ERA2_ZONE_WAVES[zi] || []).slice() : ZONE_WAVES[zi].map((n) => n + bonus);''')

# ───────── 4. 저스트 패링 창 ─────────
rep('''    const justParry = () => {
      const g = gameRef.current;
      const p = g.player;
      const st = g.stats;
      p.guardTimer = 0;''',
    '''    const justParry = () => {
      const g = gameRef.current;
      const p = g.player;
      const st = g.stats;
      // [R30] 조건부 일섬 ① — 이 순간부터 1초 안에 J
      g.parryTick = g.tick;
      p.guardTimer = 0;''')

# ───────── 5. 콤보 · 특수기 함수(컴포넌트 범위) ─────────
rep('''    const triggerEraWeaponCombo = () => {''',
    '''    // ───────── [R30] 입체 콤보 · 조건부 일섬 ─────────
    const R30C = (g) => R30_ERA_COL[g.era] || R30_ERA_COL[1];
    // 입체 타원 검기 리본 등록 — follow면 주인공 몸을 따라다니는 원(중심 = 발 위 h · 앞 dx), 아니면 고정 (x, y 화면).
    //  a0 → a1: 타원 매개변수 각(sin > 0 = 앞쪽 · 전경). rot = 화면에서 타원 기울기
    const pushRibbon = (o) => {
      const g = gameRef.current;
      const p = g.player;
      const L = g.fx3d || (g.fx3d = []);
      if (L.length > 14) L.splice(0, L.length - 14);
      L.push({ kind: "ell", t0: performance.now() + (o.delay || 0), dur: o.dur || 300, follow: o.follow !== false, x: o.x, y: o.y, h: o.h || 60, dx: o.dx || 0, rx: o.rx || 120, ry: o.ry || 32, rot: o.rot || 0, a0: o.a0, a1: o.a1, w: o.w || 14, col: o.col || R30C(g)[0], dir: o.dir || p.facing });
      g.fx3dCount = (g.fx3dCount || 0) + 1;
    };
    // 용오름 나선(두 가닥 · 원근) — 3시대 김유신 황금 · 비취, 6시대 백 · 청 태극
    const pushHelix = (x, z, o) => {
      const g = gameRef.current;
      const L = g.fx3d || (g.fx3d = []);
      L.push({ kind: "helix", t0: performance.now(), dur: o.dur || 600, x, z, H: o.H || 180, R: o.R || 60, turns: o.turns || 2, cols: o.cols, strands: o.strands || 1 });
      g.helixCount = (g.helixCount || 0) + 1;
    };
    // 연격 입체 검기: 1타 가로 베기 · 2타 역베기(올려) · 3타 내려찍기 · Lv.3+ 4타 360° 원월 회전참(앞뒤를 감싸는 두 겹)
    const comboRibbon = (step, spin) => {
      const C = R30C(gameRef.current);
      if (spin) {
        pushRibbon({ h: 58, rx: 156, ry: 38, rot: -0.05, a0: Math.PI + 0.5, a1: Math.PI + 0.5 - Math.PI * 2.3, w: 18, dur: 420, col: C[0] });
        pushRibbon({ h: 86, rx: 120, ry: 30, rot: 0.16, a0: Math.PI + 0.2, a1: Math.PI + 0.2 - Math.PI * 2.1, w: 12, dur: 400, col: C[1], delay: 70 });
      } else if (step === 1) pushRibbon({ h: 64, dx: 18, rx: 132, ry: 32, rot: -0.06, a0: Math.PI + 0.45, a1: -0.4, w: 14, dur: 280, col: C[0] });
      else if (step === 2) pushRibbon({ h: 66, dx: 18, rx: 128, ry: 36, rot: 0.5, a0: 0.25, a1: Math.PI + 0.45, w: 14, dur: 290, col: C[1] });
      else if (step === 3) pushRibbon({ h: 62, dx: 44, rx: 112, ry: 38, rot: 1.27, a0: Math.PI - 0.35, a1: 0.3, w: 16, dur: 300, col: C[0] });
    };
    // Lv.4 질풍연참 원근 깊이: 연참마다 기울기 · 깊이를 번갈아 바꾸고, 마지막 일섬은 화면을 가로지르는 납작한 긴 타원
    const rushRibbon = (k, last) => {
      const C = R30C(gameRef.current);
      if (last) pushRibbon({ h: 60, dx: 150, rx: 430, ry: 30, rot: -0.03, a0: Math.PI + 0.25, a1: -0.25, w: 18, dur: 480, col: C[0] });
      else {
        const sg = k % 2 ? 1 : -1;
        pushRibbon({ h: 58 + sg * 10, dx: 30, rx: 150, ry: 48, rot: sg * 0.42, a0: sg > 0 ? Math.PI + 0.35 : 0.3, a1: sg > 0 ? -0.3 : Math.PI + 0.3, w: 13, dur: 240, col: C[k % 2 ? 0 : 1] });
      }
    };
    // X자 십자검기(투사체) — 적 3명까지 꿰뚫음(같은 적 1회) · HD 오버레이로 그림
    const launchCrossWave = (dir, y, size, ratio) => {
      const g = gameRef.current;
      const p = g.player;
      const C = R30C(g);
      g.projectiles.push({ x: p.x + dir * 46, z: p.z, y, vx: dir * 15, facing: dir, eraNum: g.era, color1: C[0], color2: C[1], size, dmgRatio: ratio, hitCount: 1, life: 32, cross: true, pierce: 3, hitIds: [] });
      g.crossWaves = (g.crossWaves || 0) + 1;
    };
    // 둘레 베기(회전참 · 파동격) — 주인공 앞뒤 반경 안의 적을 모두 베고(칼이면 막타 두 동강) 피니시 손맛(정지 · 쉐이크) 그대로
    const areaSlash = (radius, rz, dmgRatio, knock, launch, hitCount, forceCrit) => {
      const g = gameRef.current;
      const p = g.player;
      const SC = g._slashCtx = { ang: g._cutAng != null ? g._cutAng : 0.06, blade: heroWeaponClass(g.era, g.stats.weaponTier || 1) === "SWORD", kills: 0, n: 0 };
      let hits = 0;
      let back = 0;
      for (let i = 0; i < g.enemies.length; i++) {
        const en = g.enemies[i];
        if (en.state === "DYING" || en.state === "SPAWN") continue;
        const dx = en.x - p.x;
        if (Math.abs(dx) > radius || Math.abs(en.z - p.z) > rz) continue;
        const d = dx >= 0 ? 1 : -1;
        if (d !== p.facing) back++;
        applyDamageToEnemy(en, dmgRatio, knock, launch, hitCount, forceCrit, d);
        spawnElementHit(en.x, en.z, en.y + 46, true);
        if (SC.n++ < 5) pushSlashFx(en.x, en.z - en.y - 56 + rand(-10, 10), SC.ang + rand(-0.12, 0.12), d, { heavy: true, len: en._cut ? 270 : 200 });
        hits++;
      }
      if (g.bossActive && g.boss && !g.boss.dying) {
        const b = g.boss;
        if (Math.abs(b.x - p.x) <= radius + 75 && Math.abs(b.z - p.z) <= rz + 48) {
          const d = b.x >= p.x ? 1 : -1;
          applyDamageToEnemy(b, dmgRatio * 1.18, knock * 0.45, launch * 0.6, hitCount, forceCrit, d);
          pushSlashFx(b.x, b.z - b.y - 96, SC.ang, d, { heavy: true, len: 300 });
          hits++;
        }
      }
      g._slashCtx = null;
      if (hits) {
        g.hitStop = Math.max(g.hitStop, forceCrit && hitCount >= 2 ? HITSTOP_FIN : HITSTOP_HEAVY, SC.kills ? HITSTOP_KILL : 0);
        addTrauma(0.14 + hitCount * 0.05);
        g.kickX += p.facing * (3 + hitCount);
        kickDirShake(g, p.facing, 8);
        p._hitFlashMs = performance.now();
        p._hitHeavy = true;
        const HL = g.hitStopLog || (g.hitStopLog = []);
        HL.push({ tick: g.tick, heavy: true, stop: g.hitStop, step: p.comboStep, boss: false, kills: SC.kills, fin: true, area: true, back });
        if (HL.length > 16) HL.shift();
      }
      g.areaBack = (g.areaBack || 0) + back;
      return { hits, kills: SC.kills, back };
    };
    // 3타 내려찍기 — 칼끝이 닿는 앞쪽 지면에 먼지 · 작은 충격파
    const chopImpact = () => {
      const g = gameRef.current;
      const p = g.player;
      const ix = p.x + p.facing * 92;
      spawnDust(ix, p.z, 6, 3.2);
      addShock(ix, p.z, R30C(g)[0], 90, 12);
      addTrauma(0.08);
    };
    // Lv.5 공중 도약 급강하 파동격 — 땅이면 살짝 도약 → 대각선 급강하 → 착지 충격파 + 양쪽 X자 검기 폭발(airRaidImpact "wave")
    const startWaveDive = () => {
      const g = gameRef.current;
      const p = g.player;
      if (p.plunge || syncRef.current.gameState !== "PLAYING" || p.downTimer > 0) return;
      p.plunge = "wave";
      p._spinAtk = false;
      p.state = "ATTACK";
      p.atkAnim = "atk2";
      p._atkSrc = "air";
      p._fin = true;
      p.comboStep = 4;
      p.maxAttackTimer = 44;
      p.attackTimer = 44;
      p.invincibleTimer = Math.max(p.invincibleTimer || 0, 50);
      const grounded = p.y < 20;
      if (grounded) p.vy = Math.max(p.vy, 10.5);
      sfx("dash");
      g.waveDives = (g.waveDives || 0) + 1;
      addTimer(grounded ? 10 : 2, () => {
        const pp = gameRef.current.player;
        if (pp.plunge !== "wave") return;
        pp.vy = -21;
        pp.vx = pp.facing * 10;
        for (let i = 0; i < 4; i++) pp.ghosts.push({ x: pp.x - pp.facing * i * 22, z: pp.z, y: pp.y + i * 14, facing: pp.facing, anim: "run", fi: i, name: pp._assetFrame, alpha: 0.75 - i * 0.15 });
        pushSlashFx(pp.x + pp.facing * 30, pp.z - pp.y - 30, 1.0, pp.facing, { len: 220, w: 6, dur: 260, sparks: 5, heavy: true });
      });
    };
    // 조건부 일섬 「시공 일섬」 — 0.2초 수묵 암전 + 시대 오라 폭발 → 화면 안 적 3~4명을 Z자 입체 궤적으로 연속 관통(잔상 4겹) →
    //  착지 0.15초 정지 뒤 일제 양단. 3시대 김유신 = 붉은 망토 잔상 + 황금 · 비취 용오름 일섬 · 4~6시대도 시대색 · 궤적으로 차별화
    const SPECIAL_NAME = { 1: ["PRIMAL FLASH!", "🔥 시공 일섬 — 태고의 불꽃!"], 2: ["SOLAR FLASH!", "☀️ 시공 일섬 — 천제의 햇살!"], 3: ["GOLDEN DRAGON!", "🐉 황금 용오름 일섬!"], 4: ["AZURE DRAGON!", "🌊 시공 일섬 — 청룡 검기!"], 5: ["CRIMSON FLASH!", "🔥 시공 일섬 — 조선의 홍염!"], 6: ["TAEGEUK FLASH!", "☯️ 시공 일섬 — 태극 섬광!"] };
    const startSpecial = (reason) => {
      const g = gameRef.current;
      const p = g.player;
      if (g.special && g.tick - (g.special.tick0 || 0) > 240) g.special = null;
      if (g.special || syncRef.current.gameState !== "PLAYING" || p.downTimer > 0) return false;
      if ((g.specialCd || 0) > g.tick) return false;
      const C = R30C(g);
      const L0 = g.cameraX - 10;
      const L1 = g.cameraX + VIEW_W + 10;
      const pool = g.enemies.filter((e) => e.state !== "DYING" && e.state !== "SPAWN" && e.hp > 0 && e.x > L0 && e.x < L1);
      pool.sort((a, b) => Math.abs(a.x - p.x) - Math.abs(b.x - p.x));
      const targets = pool.slice(0, 4);
      if (targets.length < 4 && g.bossActive && g.boss && !g.boss.dying && g.boss.x > L0 && g.boss.x < L1) targets.push(g.boss);
      g.special = { reason, era: g.era, targets, tick0: g.tick, path: [[p.x, p.z - p.y - 60]] };
      g.specialCd = g.tick + R30_SPECIAL_CD;
      g.specials = (g.specials || 0) + 1;
      (g.specialLog || (g.specialLog = [])).push({ reason, era: g.era, n: targets.length, tick: g.tick });
      p.rush = null;
      p.plunge = false;
      p._spinAtk = false;
      p.bufferAtk = false;
      p.invincibleTimer = Math.max(p.invincibleTimer || 0, 150);
      p.state = "ATTACK";
      p.atkAnim = "atk1";
      p._atkSrc = "combo";
      p._fin = true;
      p.comboStep = 4;
      p.maxAttackTimer = 34;
      p.attackTimer = 34;
      for (let i = 0; i < targets.length; i++) {
        const en = targets[i];
        if (en === g.boss) continue;
        en.hitStun = Math.max(en.hitStun || 0, 90);
        en.windupTimer = 0;
        en.vx = 0;
      }
      g.inkDark = { t0: performance.now() };
      g.auraBurst = performance.now();
      addLight(p.x, p.z, 60, 220, C[0], 1, 20);
      addShock(p.x, p.z, C[0], 190, 18);
      sfx("breath");
      const nm = SPECIAL_NAME[g.era] || SPECIAL_NAME[1];
      addDamagePopup(p.x, p.z, p.y + 130, nm[0], true, reason === "parry" ? "PARRY LINK" : "COMBO 15+", 0, C[0]);
      setPlayerBubble(nm[1], 90);
      if (g.era === 3) pushHelix(p.x, p.z, { H: 230, R: 70, turns: 2.4, cols: ["#fbbf24", "#34d399"], dur: 760, strands: 2 });
      else if (g.era === 6) pushHelix(p.x, p.z, { H: 170, R: 80, turns: 1.6, cols: ["#f8fafc", "#3b82f6"], dur: 640, strands: 2 });
      else if (g.era === 4) pushHelix(p.x, p.z, { H: 120, R: 110, turns: 1.2, cols: [C[0], C[1]], dur: 560, strands: 2 });
      else pushHelix(p.x, p.z, { H: 180, R: 66, turns: 1.8, cols: [C[0], C[1]], dur: 600, strands: 1 });
      addTimer(12, () => specialDash(0));
      return true;
    };
    const specialDash = (k) => {
      const g = gameRef.current;
      const p = g.player;
      const S = g.special;
      if (!S || syncRef.current.gameState !== "PLAYING") {
        g.special = null;
        return;
      }
      if (k >= S.targets.length) {
        specialLand();
        return;
      }
      const C = R30_ERA_COL[S.era] || R30_ERA_COL[1];
      const en = S.targets[k];
      const x0 = p.x;
      const z0 = p.z;
      const dir = en.x >= x0 ? 1 : -1;
      const tx = clamp(en.x + dir * 70, 70, WORLD_WIDTH - 70);
      const tz = clamp(en.z + (k % 2 ? -22 : 22), 352, 484);
      for (let i = 0; i < 4; i++) {
        const f = i / 4;
        p.ghosts.push({ x: x0 + (tx - x0) * f, z: z0 + (tz - z0) * f, y: p.y, facing: dir, anim: "run", fi: i, name: p._assetFrame || "atk1", alpha: 0.85 - i * 0.16 });
      }
      p.facing = dir;
      p.x = tx;
      p.z = tz;
      p.vx = 0;
      p.atkAnim = k % 2 ? "atk2" : "atk1";
      p.maxAttackTimer = 10;
      p.attackTimer = 10;
      S.path.push([tx, tz - p.y - 60]);
      const yy = en.z - (en.y || 0) - (en === g.boss ? 96 : 56);
      pushSlashFx(en.x, yy, k % 2 ? -0.55 : 0.55, dir, { heavy: true, len: 230, w: 7, dur: 320, col: C[k % 2], sparks: 6 });
      pushRibbon({ follow: false, x: (x0 + tx) / 2, y: (z0 + tz) / 2 - 60, rx: Math.abs(tx - x0) / 2 + 30, ry: 26, rot: Math.max(-0.5, Math.min(0.5, (tz - z0) / Math.max(40, Math.abs(tx - x0)))), a0: Math.PI + 0.2, a1: -0.2, w: 12, dur: 300, col: C[k % 2], dir });
      if (S.era === 3) pushHelix(tx, tz, { H: 140, R: 46, turns: 1.6, cols: ["#fbbf24", "#34d399"], dur: 420, strands: 2 });
      sfx("slashLight");
      addTrauma(0.12);
      S.k = k + 1;
      addTimer(5, () => specialDash(k + 1));
    };
    const specialLand = () => {
      const g = gameRef.current;
      const p = g.player;
      const S = g.special;
      if (!S) return;
      const C = R30_ERA_COL[S.era] || R30_ERA_COL[1];
      (g.fx3d || (g.fx3d = [])).push({ kind: "zpath", t0: performance.now(), dur: 560, pts: S.path.slice(), col: C[0] });
      g.hitStop = Math.max(g.hitStop, 9);
      g.targetZoom = 1.06;
      addTimer(9, () => {
        gameRef.current.targetZoom = 1;
      });
      kickDirShake(g, p.facing, 8);
      addTrauma(0.45);
      g.flashAlpha = Math.max(g.flashAlpha, 0.4);
      g.flashColor = "#ffffff";
      pushSlashFx(p.x - p.facing * 160, p.z - p.y - 60, 0.03, p.facing, { len: 900, w: 10, dur: 460, heavy: true, sparks: 10, col: C[0] });
      if (S.era === 3) pushHelix(p.x, p.z, { H: 260, R: 90, turns: 2.6, cols: ["#fbbf24", "#34d399"], dur: 820, strands: 2 });
      else if (S.era === 6) pushHelix(p.x, p.z, { H: 150, R: 100, turns: 1.4, cols: ["#f8fafc", "#3b82f6"], dur: 600, strands: 2 });
      addTimer(1, () => {
        const g2 = gameRef.current;
        const S2 = g2.special;
        if (!S2) return;
        const p2 = g2.player;
        g2._slashCtx = { ang: 0.5, blade: heroWeaponClass(g2.era, g2.stats.weaponTier || 1) === "SWORD", kills: 0, n: 0 };
        let hits = 0;
        for (let i = 0; i < S2.targets.length; i++) {
          const en = S2.targets[i];
          const d = en.x >= p2.x ? 1 : -1;
          if (en === g2.boss) {
            if (g2.bossActive && !en.dying) {
              applyDamageToEnemy(en, 3.6, 2, 2, 3, true, d);
              hits++;
            }
            continue;
          }
          if (en.state === "DYING" || en.hp <= 0) continue;
          g2._slashCtx.ang = 0.3 + Math.random() * 0.5;
          applyDamageToEnemy(en, 3.4, 10, 7, 3, true, d);
          hits++;
        }
        const kills = g2._slashCtx.kills;
        g2._slashCtx = null;
        g2.specialKills = (g2.specialKills || 0) + kills;
        g2.specialHits = (g2.specialHits || 0) + hits;
        if (hits) addDamagePopup(p2.x, p2.z, p2.y + 150, kills ? `ALL CUT x${kills}` : "TIME SLASH!", true, null, 0, C[0]);
        sfx("hitHeavy");
        g2.slowMo = Math.max(g2.slowMo || 0, 16);
        g2.special = null;
      });
    };
    const triggerEraWeaponCombo = () => {''')

# ───────── 6. 연격 · 공중 · 돌진 · 어퍼 · 질풍연참 연결 ─────────
rep('''      g.lastAtkPress = g.tick;
      if (p.rush || p.plunge) return;
      if (p.guardTimer > 0) return;''',
    '''      g.lastAtkPress = g.tick;
      if (g.special && g.tick - (g.special.tick0 || 0) > 240) g.special = null;
      if (p.rush || p.plunge || g.special) return;
      // [R30] 조건부 일섬 ① — 저스트 패링 성공 뒤 1초 안에 J
      if (g.parryTick != null && g.tick - g.parryTick <= R30_PARRY_WINDOW && !(p.guardTimer > 0) && startSpecial("parry")) {
        g.parryTick = null;
        return;
      }
      if (p.guardTimer > 0) return;''')

rep('''        p.airHits = (p.airHits || 0) + 1;
        if (p.airHits >= 4) {
          p.airHits = 0;
          p.plunge = true;''',
    '''        p.airHits = (p.airHits || 0) + 1;
        p._spinAtk = false;
        if (p.airHits >= 4) {
          p.airHits = 0;
          // [R30] Lv.5 = 대각선 급강하 파동격
          if (g.stats.level >= 5) {
            startWaveDive();
            return;
          }
          p.plunge = true;''')

rep('''        queueActiveFrame(3, () => {
          const g2 = gameRef.current;
          g2._cutAng = ah % 2 ? 0.55 : -0.42;
          checkMeleeHitbox(155, 62, 1.3 + ah * 0.08, 6, 7.5, 1, ah === 3);
          g2._cutAng = null;
        });''',
    '''        queueActiveFrame(3, () => {
          const g2 = gameRef.current;
          const pp = g2.player;
          g2._cutAng = ah % 2 ? 0.55 : -0.42;
          checkMeleeHitbox(155, 62, 1.3 + ah * 0.08, 6, 7.5, 1, ah === 3);
          g2._cutAng = null;
          // [R30] 공중 입체 검기 · Lv.2+ 공중 2 · 3타 = X자 십자검기(비연 올려베기에서 이어지는 공중 연타)
          const C = R30C(g2);
          pushRibbon({ h: 60, dx: 26, rx: 104, ry: 30, rot: ah % 2 ? 0.62 : -0.62, a0: ah % 2 ? Math.PI + 0.3 : 0.3, a1: ah % 2 ? -0.3 : Math.PI + 0.3, w: 12, dur: 240, col: C[ah % 2 ? 0 : 1] });
          if (g2.stats.level >= SKILL_LV.upper && ah >= 2) launchCrossWave(pp.facing, pp.y + 50, 46, 0.75);
        });''')

rep('''      const step = p.comboStep;
      p._atkSrc = "combo";
      p._fin = step === 4;''',
    '''      const step = p.comboStep;
      p._atkSrc = "combo";
      p._fin = step === 4;
      // [R30] Lv.3+ 4타 = 360° 원월 회전참(피니시 스윙 동안 몸이 한 바퀴 돎 · 앞뒤 둘레 베기)
      p._spinAtk = step === 4 && g.stats.level >= SKILL_LV.finisher;''')

rep('''        if (isFinisher) {
          g.targetZoom = 1.075;
          addTimer(14, () => {
            gameRef.current.targetZoom = 1;
          });
        }''',
    '''        if (isFinisher) {
          // [R30] 피니시 착지 미세 줌 1.05 · 0.15초 안에 복귀 + 방향성 히트 쉐이크
          g.targetZoom = 1.05;
          addTimer(9, () => {
            gameRef.current.targetZoom = 1;
          });
          kickDirShake(g, p.facing, 7);
        }''')

rep('''        // [R29] 베기 선 각도: 1타 사선 내려베기 · 2타 올려베기 · 3타 수평 · 4타 가파른 사선 + X자
        g._cutAng = isFinisher ? 0.82 : step === 3 ? 0.08 : step === 2 ? -0.46 : 0.5;
        g._cutCross = isFinisher;
        if (cls === "AXE") {
          // [R23] 도끼: 헛스윙에도 걸리던 117~150ms 정지 제거(뻣뻣함의 원인) — 적중했을 때만 강타 규칙(3.7f + 방향 쉐이크)
          checkMeleeHitbox(150, 64, 1.25 + step * 0.35, isFinisher ? 16 : 7, isFinisher ? 13 : step === 2 ? 5 : 0, isFinisher ? 2 : 1, isFinisher || step === 3);
        } else if (cls === "SPEAR") checkMeleeHitbox(240, 30, 0.95 + step * 0.28, isFinisher ? 16 : 8, isFinisher ? 8 : 0, isFinisher ? 2 : 1, isFinisher);
        else checkMeleeHitbox(175, 62, 1 + step * 0.3, isFinisher ? 14 : 5, isFinisher ? 12.5 : step === 2 ? 6 : 0, isFinisher ? 2 : 1, isFinisher);
        g._bowlFin = false;
        g._comboStep = 0;
        g._cutAng = null;
        g._cutCross = false;
      });''',
    '''        // [R30] Lv.1 기본 3연참: 1타 가로 베기 · 2타 역베기 · 3타 내려찍기 / Lv.3+ 4타 = 360° 원월 회전참(앞뒤 둘레 베기 · 두 겹 입체 원월)
        const spin = isFinisher && g.stats.level >= SKILL_LV.finisher;
        g._cutAng = isFinisher ? spin ? 0.06 : 0.82 : step === 3 ? 1.22 : step === 2 ? -0.14 : 0.1;
        g._cutCross = isFinisher && !spin;
        comboRibbon(step, spin);
        let hitAny = false;
        if (spin) {
          for (let i = 0; i < 3; i++) p.ghosts.push({ x: p.x, z: p.z, y: p.y, facing: p.facing * (i % 2 ? -1 : 1), anim: "run", fi: 0, name: p._assetFrame, sx: [0.55, 0.25, 0.8][i], alpha: 0.7 - i * 0.15 });
          hitAny = areaSlash(cls === "SPEAR" ? 240 : 220, 78, 1.35 + step * 0.3, cls === "AXE" ? 16 : 14, 12.5, 2, true).hits > 0;
          g.spinFinishers = (g.spinFinishers || 0) + 1;
        } else if (cls === "AXE") {
          // [R23] 도끼: 헛스윙에도 걸리던 117~150ms 정지 제거(뻣뻣함의 원인) — 적중했을 때만 강타 규칙(3.7f + 방향 쉐이크)
          hitAny = checkMeleeHitbox(150, 64, 1.25 + step * 0.35, isFinisher ? 16 : 7, isFinisher ? 13 : step === 2 ? 5 : 0, isFinisher ? 2 : 1, isFinisher || step === 3);
        } else if (cls === "SPEAR") hitAny = checkMeleeHitbox(240, 30, 0.95 + step * 0.28, isFinisher ? 16 : 8, isFinisher ? 8 : 0, isFinisher ? 2 : 1, isFinisher);
        else hitAny = checkMeleeHitbox(175, 62, 1 + step * 0.3, isFinisher ? 14 : 5, isFinisher ? 12.5 : step === 2 ? 6 : 0, isFinisher ? 2 : 1, isFinisher);
        if (step === 3) chopImpact();
        g._bowlFin = false;
        g._comboStep = 0;
        g._cutAng = null;
        g._cutCross = false;
        // [R30] 조건부 일섬 ② — 15콤보(S랭크) 이상에서 4타 피니시 적중
        if (isFinisher && hitAny && g.stats.combo >= R30_SPECIAL_COMBO) startSpecial("combo");
      });''')

rep('''      p.rush = { k: 0 };
      p.comboStep = 0;
      p.comboResetTimer = 0;
      p.bufferAtk = false;''',
    '''      p.rush = { k: 0 };
      p.comboStep = 0;
      p.comboResetTimer = 0;
      p.bufferAtk = false;
      p._spinAtk = false;''')

rep('''      if (last) {
        for (let i = 0; i < 8; i++) p.ghosts.push({ x: p.x - p.facing * i * 24, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i % 6, alpha: 0.8 - i * 0.09, evo: true, col: eObj.bladeGlow });
        g.targetZoom = 1.09;
        g.speedlineAlpha = 0.6;
      }''',
    '''      if (last) {
        // [R30] 일섬 잔상 6겹(빛 굽기 없는 반투명 잔상) · 줌 1.06
        for (let i = 0; i < 6; i++) p.ghosts.push({ x: p.x - p.facing * i * 26, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i % 6, name: "run", alpha: 0.72 - i * 0.1 });
        g.targetZoom = 1.06;
        g.speedlineAlpha = 0.6;
      }
      // [R30] Lv.4 질풍연참 원근 깊이 · 잔상 2겹
      rushRibbon(k, last);
      if (!last) for (let i = 1; i <= 2; i++) p.ghosts.push({ x: p.x - p.facing * i * 18, z: p.z + (k % 2 ? -1 : 1) * i * 5, y: p.y, facing: p.facing, anim: "run", fi: i, name: p._assetFrame, alpha: 0.62 - i * 0.18 });''')

rep('''          addDamagePopup(pp.x, pp.z, pp.y + 120, "RUSH FINISH!", true, null, 0, "#f472b6");
          addTimer(18, () => {
            gameRef.current.targetZoom = 1;
          });
          g2.rushFinishes = (g2.rushFinishes || 0) + 1;''',
    '''          addDamagePopup(pp.x, pp.z, pp.y + 120, "RUSH FINISH!", true, null, 0, "#f472b6");
          // [R30] 피니시 줌 0.15초 안에 복귀 + 방향성 쉐이크 / Lv.5 = 일섬 뒤 공중 도약 급강하 파동격
          addTimer(9, () => {
            gameRef.current.targetZoom = 1;
          });
          kickDirShake(g2, pp.facing, 8);
          g2.rushFinishes = (g2.rushFinishes || 0) + 1;
          if (g2.stats.level >= 5) addTimer(8, () => startWaveDive());''')

rep('''    const airRaidImpact = () => {
      const g = gameRef.current;
      const p = g.player;
      const eObj = relicPal(g, eraObjOf());''',
    '''    const airRaidImpact = (kind) => {
      const g = gameRef.current;
      const p = g.player;
      const eObj = relicPal(g, eraObjOf());
      const wave = kind === "wave";''')
rep('''        if (Math.abs(dx) > 200 || Math.abs(en.z - p.z) > 76) continue;''',
    '''        if (Math.abs(dx) > (wave ? 250 : 200) || Math.abs(en.z - p.z) > (wave ? 90 : 76)) continue;''')
rep('''      addDamagePopup(p.x, p.z, 124, "AIR RAID!", true, hits ? hits + " HIT" : null, 0, "#fde047");
      sfx("hitHeavy");
      g.airRaids = (g.airRaids || 0) + 1;
    };''',
    '''      addDamagePopup(p.x, p.z, 124, wave ? "WAVE STRIKE!" : "AIR RAID!", true, hits ? hits + " HIT" : null, 0, wave ? "#f472b6" : "#fde047");
      sfx("hitHeavy");
      g.airRaids = (g.airRaids || 0) + 1;
      // [R30] 지면 충격파 입체 고리 · Lv.5 파동격 = 양쪽 교차 X자 검기 폭발 + 줌 1.06(0.15초 복귀)
      pushRibbon({ follow: false, x: p.x, y: p.z - 4, rx: wave ? 240 : 190, ry: wave ? 56 : 44, rot: 0, a0: Math.PI * 1.5, a1: Math.PI * 1.5 - Math.PI * 2.1, w: wave ? 16 : 12, dur: 420, col: R30C(g)[0], dir: 1 });
      if (wave) {
        launchCrossWave(1, 46, 60, 1.05);
        launchCrossWave(-1, 46, 60, 1.05);
        g.targetZoom = 1.06;
        addTimer(9, () => {
          gameRef.current.targetZoom = 1;
        });
        g.waveStrikes = (g.waveStrikes || 0) + 1;
      }
    };''')

rep('''            if (p.plunge) {
              p.plunge = false;
              airRaidImpact();
            }''',
    '''            if (p.plunge) {
              const pk = p.plunge;
              p.plunge = false;
              airRaidImpact(pk);
            }''')

rep('''      p._dashTick = g.tick;''', '''      p._dashTick = g.tick;
      p._spinAtk = false;''')

rep('''      p._atkSrc = "upper";''', '''      p._atkSrc = "upper";
      p._spinAtk = false;''')
rep('''        breathFX(2, -1.1);''', '''        breathFX(2, -1.1);
        // [R30] Lv.2 비연 올려베기 — 세로로 감아 올리는 입체 검기 + 솟구치는 잔상 3겹
        pushRibbon({ h: 70, dx: 34, rx: 132, ry: 40, rot: -1.32, a0: Math.PI - 0.25, a1: 0.25, w: 15, dur: 340, col: R30C(g)[0] });
        for (let i = 1; i <= 3; i++) p.ghosts.push({ x: p.x - p.facing * i * 10, z: p.z, y: Math.max(0, p.y - i * 18), facing: p.facing, anim: "run", fi: i, name: p._assetFrame, alpha: 0.6 - i * 0.14 });''')

rep('''      p.vx = p.facing * (gun ? -3 : cls === "SPEAR" ? step === 4 ? 16 : 9 : step === 4 ? 13 : cls === "AXE" ? 3 : 5);''',
    '''      p.vx = p.facing * (gun ? -3 : cls === "SPEAR" ? step === 4 ? 16 : 9 : step === 4 ? 13 : cls === "AXE" ? 3 : 5);
      // [R30] 원월 회전참은 제자리에서 돈다(앞으로 미끄러지면 뒤쪽 적이 둘레 밖으로 빠짐)
      if (p._spinAtk) p.vx = p.facing * 3;''')

# ───────── 7. 투사체: X자 십자검기 관통 · 두 동강 · HD 그리기 ─────────
rep('''          let hit = false;
          for (let e2 = 0; e2 < g.enemies.length && !hit; e2++) {
            const en = g.enemies[e2];
            if (en.state === "DYING" || en.state === "SPAWN") continue;
            if (Math.abs(en.x - prj.x) < 52 && Math.abs(en.z - prj.z) < 48) {
              hit = true;
              applyDamageToEnemy(en, prj.dmgRatio, 7, 5.5, prj.hitCount, true, prj.facing);
            }
          }''',
    '''          let hit = false;
          // [R30] X자 십자검기: 적 3명까지 꿰뚫고(같은 적 1회) 칼이면 막타 두 동강
          if (prj.cross) g._slashCtx = { ang: 0.62, blade: heroWeaponClass(g.era, g.stats.weaponTier || 1) === "SWORD", kills: 0, n: 0 };
          for (let e2 = 0; e2 < g.enemies.length && !hit; e2++) {
            const en = g.enemies[e2];
            if (en.state === "DYING" || en.state === "SPAWN") continue;
            if (Math.abs(en.x - prj.x) < 52 && Math.abs(en.z - prj.z) < 48) {
              if (prj.hitIds) {
                if (prj.hitIds.includes(en.id)) continue;
                prj.hitIds.push(en.id);
                applyDamageToEnemy(en, prj.dmgRatio, 7, 5.5, prj.hitCount, true, prj.facing);
                pushSlashFx(en.x, en.z - en.y - 56, 0.62, prj.facing, { cross: true, len: 150 });
                g.crossHits = (g.crossHits || 0) + 1;
                if (prj.hitIds.length >= (prj.pierce || 1)) hit = true;
                continue;
              }
              hit = true;
              applyDamageToEnemy(en, prj.dmgRatio, 7, 5.5, prj.hitCount, true, prj.facing);
            }
          }
          if (prj.cross) g._slashCtx = null;''')

rep('''        for (let i = 0; i < g.projectiles.length; i++) drawEraProjectile(ctx, g.projectiles[i]);''',
    '''        for (let i = 0; i < g.projectiles.length; i++) if (!g.projectiles[i].cross) drawEraProjectile(ctx, g.projectiles[i]);''')

# ───────── 8. 렌더: 입체 검기 · 오라 · 수묵 암전 · 십자검기 ─────────
rep('''      const drawBreathFx = (g, S) => {''',
    '''      // ───────── [R30] 입체 검기 리본 · 용오름 나선 · Z 궤적 ─────────
      //  앞쪽(전경, sin > 0)은 굵고 밝게 · 뒤쪽(후경)은 얇고 반투명하게. back 패스 = 주인공 몸 뒤(화면에 직접), front 패스 = 오버레이.
      //  구간별 사각형을 한 경로에 모아 한 번에 채움(리본 하나에 패스당 채우기 1~2번)
      const R3 = { xs: new Float32Array(72), ys: new Float32Array(72), ws: new Float32Array(72), ds: new Float32Array(72) };
      const r3Quads = (S, n, back, wMul) => {
        let any = false;
        S.beginPath();
        for (let i = 0; i < n; i++) {
          const dm = (R3.ds[i] + R3.ds[i + 1]) * 0.5;
          if (back ? dm >= 0 : dm < 0) continue;
          const x0 = R3.xs[i];
          const y0 = R3.ys[i];
          const x1 = R3.xs[i + 1];
          const y1 = R3.ys[i + 1];
          const tl = Math.hypot(x1 - x0, y1 - y0) || 1;
          const nx = -(y1 - y0) / tl;
          const ny = (x1 - x0) / tl;
          const w0 = R3.ws[i] * wMul * 0.5;
          const w1 = R3.ws[i + 1] * wMul * 0.5;
          S.moveTo(x0 + nx * w0, y0 + ny * w0);
          S.lineTo(x1 + nx * w1, y1 + ny * w1);
          S.lineTo(x1 - nx * w1, y1 - ny * w1);
          S.lineTo(x0 - nx * w0, y0 - ny * w0);
          S.closePath();
          any = true;
        }
        return any;
      };
      const ribbonPts = (g, e, t) => {
        const p = g.player;
        const head = 1 - Math.pow(1 - Math.min(1, t / 0.42), 2);
        const tail = Math.min(head - 0.03, Math.pow(Math.max(0, (t - 0.14) / 0.86), 1.25));
        const th = e.a0 + (e.a1 - e.a0) * head;
        const tt = e.a0 + (e.a1 - e.a0) * Math.max(0, tail);
        const cx = e.follow ? p.x + e.dir * e.dx : e.x;
        const cy = e.follow ? p.z - p.y - e.h : e.y;
        const N = 26;
        const cr = Math.cos(e.rot);
        const sr = Math.sin(e.rot);
        for (let i = 0; i <= N; i++) {
          const f = i / N;
          const a = tt + (th - tt) * f;
          const lx = e.rx * Math.cos(a);
          const ly = e.ry * Math.sin(a);
          R3.xs[i] = cx + e.dir * (lx * cr - ly * sr);
          R3.ys[i] = cy + lx * sr + ly * cr;
          const d = Math.sin(a);
          R3.ds[i] = d;
          R3.ws[i] = e.w * (0.3 + 0.35 * (d + 1)) * (0.22 + 0.78 * f);
        }
        return N;
      };
      const helixPts = (e, t, strand) => {
        const grow = Math.min(1, t / 0.45);
        const N = 34;
        const spin = t * 9;
        for (let i = 0; i <= N; i++) {
          const sv = i / N * grow;
          const a = e.turns * TAU * sv + spin + strand * Math.PI;
          const R = e.R * (1 - 0.45 * sv);
          R3.xs[i] = e.x + R * Math.cos(a);
          R3.ys[i] = e.z - e.H * sv + R * 0.24 * Math.sin(a);
          const d = Math.sin(a);
          R3.ds[i] = d;
          R3.ws[i] = 11 * (0.35 + 0.325 * (d + 1)) * (1 - 0.5 * sv) * (0.35 + 0.65 * (i / N));
        }
        return N;
      };
      const drawFx3dPass = (g, back, S0) => {
        const L = g.fx3d;
        if (!L || !L.length || PERF_OFF.particles) return;
        const now = performance.now();
        const F = frameAssets.cam;
        const S = back ? screen : S0;
        S.save();
        if (back) {
          S.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
          applyCam(S, F);
          S.translate(-F.camRX, 0);
        }
        S.globalCompositeOperation = "lighter";
        S.lineCap = "round";
        S.lineJoin = "round";
        for (let i = L.length - 1; i >= 0; i--) {
          const e = L[i];
          const t = (now - e.t0) / e.dur;
          if (t >= 1) {
            if (!back) L.splice(i, 1);
            continue;
          }
          if (t < 0) continue;
          const fade = t < 0.55 ? 1 : Math.max(0, 1 - (t - 0.55) / 0.45);
          if (e.kind === "ell" || e.kind === "helix") {
            const strands = e.kind === "helix" ? e.strands : 1;
            for (let sd = 0; sd < strands; sd++) {
              const N = e.kind === "helix" ? helixPts(e, t, sd) : ribbonPts(g, e, t);
              const col = e.kind === "helix" ? e.cols[sd % e.cols.length] : e.col;
              S.fillStyle = col;
              if (back) {
                S.globalAlpha = 0.3 * fade;
                if (r3Quads(S, N, true, 1.5)) S.fill();
              } else {
                S.globalAlpha = 0.55 * fade;
                if (r3Quads(S, N, false, 1.9)) {
                  S.fill();
                  S.globalAlpha = 0.95 * fade;
                  S.fillStyle = "#ffffff";
                  r3Quads(S, N, false, 0.45);
                  S.fill();
                }
              }
            }
          } else if (e.kind === "zpath" && !back && e.pts.length > 1) {
            S.beginPath();
            for (let k = 0; k < e.pts.length; k++) k ? S.lineTo(e.pts[k][0], e.pts[k][1]) : S.moveTo(e.pts[k][0], e.pts[k][1]);
            S.globalAlpha = 0.5 * fade;
            S.strokeStyle = e.col;
            S.lineWidth = 12 * (0.4 + 0.6 * fade);
            S.stroke();
            S.globalAlpha = 0.95 * fade;
            S.strokeStyle = "#ffffff";
            S.lineWidth = 3;
            S.stroke();
          }
          if (e.kind === "helix") g.helixDrawn = (g.helixDrawn || 0) + 1;
        }
        S.restore();
        if (back) g.r3Back = (g.r3Back || 0) + 1;
        else g.r3Front = (g.r3Front || 0) + 1;
      };
      // [R30] X자 십자검기(HD) — 시대색 초승달 두 장이 엇갈린 X + 빛 스프라이트
      const drawCrossWaves = (g, S) => {
        const L = g.projectiles;
        let any = false;
        for (let i = 0; i < L.length; i++) {
          const pr = L[i];
          if (!pr.cross) continue;
          if (!any) {
            S.save();
            S.globalCompositeOperation = "lighter";
            any = true;
          }
          const x = pr.x;
          const y = pr.z - pr.y;
          const sz = pr.size;
          const wob = Math.sin((pr.life || 0) * 0.5) * 0.06;
          S.globalAlpha = 0.5;
          S.drawImage(getGlowSprite(pr.color1), x - sz * 0.9, y - sz * 0.9, sz * 1.8, sz * 1.8);
          for (let q = 0; q < 2; q++) {
            const a = (q ? -0.62 : 0.62) + wob;
            const ux = Math.cos(a) * pr.facing;
            const uy = Math.sin(a);
            const nx = -uy;
            const ny = ux;
            const L2 = sz * 0.95;
            const x0 = x - ux * L2;
            const y0 = y - uy * L2;
            const x1 = x + ux * L2;
            const y1 = y + uy * L2;
            S.globalAlpha = 0.7;
            S.fillStyle = q ? pr.color2 : pr.color1;
            S.beginPath();
            S.moveTo(x0, y0);
            S.quadraticCurveTo(x + nx * sz * 0.32, y + ny * sz * 0.32, x1, y1);
            S.quadraticCurveTo(x - nx * sz * 0.1, y - ny * sz * 0.1, x0, y0);
            S.fill();
            S.globalAlpha = 0.95;
            S.fillStyle = "#ffffff";
            S.beginPath();
            S.moveTo(x0, y0);
            S.quadraticCurveTo(x + nx * sz * 0.12, y + ny * sz * 0.12, x1, y1);
            S.quadraticCurveTo(x - nx * sz * 0.03, y - ny * sz * 0.03, x0, y0);
            S.fill();
          }
        }
        if (any) {
          S.restore();
          g.crossDrawn = (g.crossDrawn || 0) + 1;
        }
      };
      // ───────── [R30] 주인공 오라 ─────────
      //  1단계 발밑 미세 기류 · 2단계 수묵 기류 + 상승 불티 · 3단계 몸 전체 풀 오라(몸빛 + 불꽃 혀) · 4단계(콤보 S랭크+ · 유물 각성) 팽창.
      //  성능: ctx.filter 없음 · 가산(lighter) 합성 · 불티는 고정 28칸 풀 재사용 · 저사양(LITE)은 불꽃 혀 생략 · 불티 절반
      const AURA_POOL = [];
      for (let i = 0; i < 28; i++) AURA_POOL.push({ on: false, x: 0, y: 0, vx: 0, vy: 0, life: 0, max: 1, s: 1, c: 0 });
      let auraT = 0;
      let auraAcc = 0;
      const drawFlames = (S, fx, by, bodyH, big, t, C, st, back) => {
        // 불꽃 혀: 둥근 밑동 → 끝으로 흐려지는 불꽃 스프라이트(색마다 한 번 구워 재사용) — 몸 둘레에서 길이 · 기울기가 흔들림
        const nF = back ? st >= 4 ? 8 : 6 : 3;
        for (let i = 0; i < nF; i++) {
          const ph = i / nF * TAU + (back ? 0 : 0.6);
          const x = fx + Math.cos(ph) * bodyH * 0.3 * big;
          const y0 = by - bodyH * (0.05 + 0.5 * ((Math.sin(ph * 2 + 1) + 1) * 0.5));
          const len = bodyH * (0.3 + 0.12 * Math.sin(t * 7 + i * 1.7)) * big;
          const wd = len * 0.42;
          const lean = Math.sin(t * 3 + i) * wd * 0.35;
          S.globalAlpha = Math.min(1, (back ? 0.42 : 0.3) * (st >= 4 ? 1.2 : 1));
          S.drawImage(flameSprite(i % 2 ? C[1] : C[0]), x - wd / 2 + lean, y0 - len, wd, len * 1.05);
        }
      };
      const auraEmbers = (S, p, bodyH, C, st, lite, now) => {
        const dt = Math.min(0.05, Math.max(0, (now - auraT) / 1e3));
        auraT = now;
        if (st >= 2) auraAcc += (st >= 4 ? 30 : st >= 3 ? 20 : 11) * (lite ? 0.5 : 1) * dt;
        if (auraAcc > 3) auraAcc = 3;
        const fx = p.x;
        const by = p.z - p.y;
        for (let i = 0; i < AURA_POOL.length && auraAcc >= 1; i++) {
          const q = AURA_POOL[i];
          if (q.on) continue;
          auraAcc -= 1;
          q.on = true;
          q.x = fx + (Math.random() - 0.5) * bodyH * 0.7;
          q.y = by - Math.random() * bodyH * 0.75;
          q.vx = (Math.random() - 0.5) * 18;
          q.vy = -(28 + Math.random() * 40);
          q.max = q.life = 0.6 + Math.random() * 0.7;
          q.s = 1 + Math.random() * 1.6;
          q.c = Math.random() < 0.5 ? 0 : 1;
        }
        for (let c = 0; c < 2; c++) {
          for (let b = 0; b < 2; b++) {
            let any = false;
            S.beginPath();
            for (let i = 0; i < AURA_POOL.length; i++) {
              const q = AURA_POOL[i];
              if (!q.on || q.c !== c || (q.life / q.max > 0.5 ? 1 : 0) !== b) continue;
              S.moveTo(q.x + q.s, q.y);
              S.arc(q.x, q.y, q.s, 0, TAU);
              any = true;
            }
            if (any) {
              S.globalAlpha = b ? 0.85 : 0.4;
              S.fillStyle = C[c];
              S.fill();
            }
          }
        }
        for (let i = 0; i < AURA_POOL.length; i++) {
          const q = AURA_POOL[i];
          if (!q.on) continue;
          q.life -= dt;
          if (q.life <= 0) {
            q.on = false;
            continue;
          }
          q.x += q.vx * dt + Math.sin(now / 300 + i) * 0.3;
          q.y += q.vy * dt;
        }
      };
      const drawHeroAura = (g, p, HA, back, S0) => {
        if (PERF_OFF.particles || !HA || !p) return;
        const st = auraStageOf(g);
        const now = performance.now();
        const C = R30_ERA_COL[g.era] || R30_ERA_COL[1];
        const lite = g.quality.tier >= 2;
        const bodyH = Math.max(90, (HA.groundY - (HA.topY || 0)) * HA.k);
        const fx = p.x;
        const fy = p.z;
        const by = p.z - p.y;
        const burst = g.auraBurst ? Math.max(0, 1 - (now - g.auraBurst) / 700) : 0;
        const big = (st >= 4 ? 1.22 : 1) * (1 + burst * 0.6);
        const t = now / 1e3;
        const F = frameAssets.cam;
        const S = back ? screen : S0;
        S.save();
        if (back) {
          S.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
          applyCam(S, F);
          S.translate(-F.camRX, 0);
          const rx = bodyH * 0.44 * big;
          const ry = bodyH * 0.12 * big;
          S.globalCompositeOperation = "lighter";
          S.lineCap = "round";
          S.strokeStyle = C[0];
          S.lineWidth = st >= 2 ? 2.4 : 1.6;
          S.globalAlpha = st >= 2 ? 0.5 : 0.22;
          S.beginPath();
          for (let k = 0; k < 2; k++) {
            const a = t * 1.7 + k * Math.PI;
            S.moveTo(fx + rx * Math.cos(a), fy + ry * Math.sin(a));
            S.ellipse(fx, fy, rx, ry, 0, a, a + 1.25);
          }
          S.stroke();
          if (st >= 2) {
            S.globalCompositeOperation = "source-over";
            S.strokeStyle = "rgba(8,10,16,0.42)";
            S.lineWidth = 5;
            S.globalAlpha = 1;
            S.beginPath();
            for (let k = 0; k < 3; k++) {
              const a = -t * 1.25 + k * TAU / 3;
              S.moveTo(fx + rx * 1.18 * Math.cos(a), fy + ry * 1.3 * Math.sin(a));
              S.ellipse(fx, fy, rx * 1.18, ry * 1.3, 0, a, a + 0.9);
            }
            S.stroke();
            S.globalCompositeOperation = "lighter";
          }
          if (st >= 3) {
            const w = bodyH * 0.95 * big;
            const h = bodyH * 1.32 * big;
            S.globalAlpha = Math.min(0.9, (st >= 4 ? 0.36 : 0.26) + 0.07 * Math.sin(t * 3.1) + burst * 0.3);
            S.drawImage(getGlowSprite(C[0]), fx - w / 2, by - h * 0.86, w, h);
            if (!lite) drawFlames(S, fx, by, bodyH, big, t, C, st, true);
          }
        } else {
          S.globalCompositeOperation = "lighter";
          auraEmbers(S, p, bodyH, C, st, lite, now);
          if (st >= 3 && !lite) drawFlames(S, fx, by, bodyH, big, t, C, st, false);
          g.auraDrawn = (g.auraDrawn || 0) + 1;
          g.auraStageDrawn = st;
          g.auraPoolSize = AURA_POOL.length;
          g.auraLive = AURA_POOL.reduce((a, q) => a + (q.on ? 1 : 0), 0);
        }
        S.restore();
      };
      // [R30] 시공 일섬 0.2초 수묵 암전 — 주인공 둘레만 밝게 남긴 먹빛(미리 구운 저해상도 비네트 1장을 늘려 그림 · 그라디언트 매 프레임 생성 없음)
      let inkVig = null;
      const drawInkDark = (g, c) => {
        const D = g.inkDark;
        if (!D) return;
        const e = (performance.now() - D.t0) / 380;
        if (e >= 1 || e < 0) {
          g.inkDark = null;
          return;
        }
        const a = e < 0.12 ? e / 0.12 : e < 0.55 ? 1 : 1 - (e - 0.55) / 0.45;
        if (!inkVig) {
          inkVig = document.createElement("canvas");
          inkVig.width = 192;
          inkVig.height = 108;
          const x = inkVig.getContext("2d");
          const gr = x.createRadialGradient(96, 54, 6, 96, 54, 100);
          gr.addColorStop(0, "rgba(5,6,10,0)");
          gr.addColorStop(0.22, "rgba(5,6,10,0.5)");
          gr.addColorStop(0.55, "rgba(4,5,9,0.86)");
          gr.addColorStop(1, "rgba(3,4,7,0.94)");
          x.fillStyle = gr;
          x.fillRect(0, 0, 192, 108);
        }
        const F = frameAssets.cam;
        const p = g.player;
        const hx = (p.x - F.camRX - F.cx + F.shX) * F.zoom + F.cx;
        const hy = (p.z - p.y - 60 - F.cy + F.shY) * F.zoom + F.cy;
        c.save();
        c.globalAlpha = a;
        c.drawImage(inkVig, hx - VIEW_W, hy - VIEW_H, VIEW_W * 2, VIEW_H * 2);
        c.restore();
        g.inkDrawn = (g.inkDrawn || 0) + 1;
      };
      const drawBreathFx = (g, S) => {''')

rep('''        if (HA) {
          flushLo();
          drawHeroRing(g, p, HA, true);
          for (let i = 0; i < p.ghosts.length; i++) {
            const gh = p.ghosts[i];
            if (gh.evo) drawAssetActor(HA, "run", gh.x, gh.z - gh.y, gh.facing, { alpha: Math.min(1, gh.alpha * 1.15), glow: { col: gh.col, a: 1 }, glowOnly: true });
            else drawAssetActor(HA, "run", gh.x, gh.z - gh.y, gh.facing, { alpha: gh.alpha * 0.32 });
          }''',
    '''        if (HA) {
          flushLo();
          drawHeroRing(g, p, HA, true);
          // [R30] 오라(몸 뒤) · 입체 검기의 뒤쪽 반(주인공 몸 뒤로 감기는 부분)
          drawHeroAura(g, p, HA, true);
          drawFx3dPass(g, true);
          if (p.ghosts.length > 12) p.ghosts.splice(0, p.ghosts.length - 12);
          for (let i = 0; i < p.ghosts.length; i++) {
            const gh = p.ghosts[i];
            if (gh.evo) drawAssetActor(HA, "run", gh.x, gh.z - gh.y, gh.facing, { alpha: Math.min(1, gh.alpha * 1.15), glow: { col: gh.col, a: 1 }, glowOnly: true });
            // [R30] 공격 잔상: 그 순간의 동작 프레임 · 가로 배율(회전참) 그대로 반투명
            else if (gh.name && HA.frames[gh.name]) drawAssetActor(HA, gh.name, gh.x, gh.z - gh.y, gh.facing, { sx: gh.sx || 1, alpha: gh.alpha * 0.45 });
            else drawAssetActor(HA, "run", gh.x, gh.z - gh.y, gh.facing, { alpha: gh.alpha * 0.32 });
          }
          // [R30] 360° 원월 회전참 — 피니시 스윙 동안 몸 가로 배율을 cos로 한 바퀴(손에 든 무기도 같은 P.sx로 따라 돎)
          if (p._spinAtk && p.state === "ATTACK" && p.attackTimer > 0 && p._atkSrc === "combo") {
            const pr = 1 - p.attackTimer / Math.max(1, p.maxAttackTimer);
            const u = Math.max(0, Math.min(1, (pr - 0.1) / 0.72));
            const cs = Math.cos(TAU * u);
            P.sx = (P.sx || 1) * (Math.abs(cs) < 0.12 ? cs < 0 ? -0.12 : 0.12 : cs);
            g.spinDrawn = (g.spinDrawn || 0) + 1;
          }''')

rep('''          } else if (P.arc) drawHeroSwingArc(HA, P, p, g, relicPal(g, eObj));''',
    '''          } else if (P.arc && !(g.fx3d && g.fx3d.length)) drawHeroSwingArc(HA, P, p, g, relicPal(g, eObj));''')

rep('''        if (g.slashFx && g.slashFx.length) overlay.push((o) => drawSlashFx(g, o));''',
    '''        // [R30] 오라(앞) · 입체 검기 앞쪽 반 · X자 십자검기 · 수묵 암전
        if (frameAssets.hero && sync.gameState !== "TITLE") overlay.push((o) => drawHeroAura(g, g.player, frameAssets.hero, false, o));
        if (g.fx3d && g.fx3d.length) overlay.push((o) => drawFx3dPass(g, false, o));
        if (g.projectiles.length) overlay.push((o) => drawCrossWaves(g, o));
        if (g.inkDark) screenOverlay.push((c) => drawInkDark(g, c));
        if (g.slashFx && g.slashFx.length) overlay.push((o) => drawSlashFx(g, o));''')

# ───────── 9. 검증 훅 ─────────
rep('''          // [R29] 시작 화면 로딩 가림막 상태(검증용)''',
    '''          // [R30] 검증 훅: 조건부 일섬 · 오라 단계
          special: (r) => startSpecial(r || "dev"),
          auraStage: () => auraStageOf(gameRef.current),
          // [R29] 시작 화면 로딩 가림막 상태(검증용)''')

open(P, "w", encoding="utf-8").write(s)
print("R30 patch ok —", n, "edits")
