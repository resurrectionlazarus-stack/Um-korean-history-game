#!/usr/bin/env python3
"""R27 패치 — 1시대 대사냥꾼 무기 분리 리그 · 주인공 시인성(영웅 링 · 몹 톤다운) · 전투 쾌감(잡몹 체력 · 수묵 호흡 피니시 ·
카운터 일섬 · 킬캠 · 공중/볼링) · 보행 리듬 통일 · 퀴즈 2건 교정 · 3시대 도트 전경 제거."""
import json
import sys

P, RIG = sys.argv[1], sys.argv[2]
s = open(P, encoding="utf-8").read()
n = 0


def rep(old, new, cnt=1):
    global s, n
    c = s.count(old)
    if c != cnt:
        raise SystemExit(f"anchor count {c} != {cnt}: {old[:110]!r}")
    s = s.replace(old, new)
    n += 1


def line_starting(prefix):
    i = s.index(prefix)
    return s[i:s.index("\n", i)]


hunter = json.load(open(RIG, encoding="utf-8"))
JS = lambda d: json.dumps(d, separators=(",", ":"), ensure_ascii=False)

# ───────── 1. 1시대 대사냥꾼: 무기 분리 몸 22장 + 손에 든 무기 3등급 ─────────
rep('''  var R26_CJG_FRAMES = ''', '''  // [R27] 1시대 대사냥꾼(무기 분리 몸 22장) 손 위치 — 주먹도끼 · 흑요석 슴베찌르개 · 신석기 간돌도끼를 퀴즈 정답 때 손에서 바꾼다
  var R27_HUNTER_FRAMES = ''' + JS(hunter) + ''';
  var R26_CJG_FRAMES = ''')
rep('''    // [R23] batch1: 사냥꾼 run3~run8 도착 → 8프레임 4틱 질주 · atk: legacy = R22 두 장 교차(atk1 망치 들기 ↔ atk2 도끼) 유지
    //  swing: 타격 프레임별 무기 끝단 궤적(원본 픽셀 · c 회전 중심 · r 반지름 · a [시작°, 끝°] — 화면 기준 시계방향 +)
''', '''    // [R23] batch1: 사냥꾼 run3~run8 도착 → 8프레임 4틱 질주(R23~R26: atk legacy 두 장 교차 + swing 궤적 프리셋 → R27 무기 분리 리그로 대체)
''')
old_h = line_starting('    hunter: { role: "hero", kind: "hero",')
EXTRA = 'extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8", "atk_prep", "atk1_2", "atk1_3", "atk2_prep", "atk2_2", "atk2_3", "atk3_prep", "atk3", "atk3_2", "atk3_3"], ext: "webp", '
rep(old_h, '''    // [R27] 미술팀 R27 1차: 대사냥꾼 무기 분리 몸 22장(webp) — 옛 R23 PNG 12장(무기 그린 몸) 대체. 무기는 assets/weapon/era1_t1~t3를 손에 얹는다
    hunter: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], ''' + EXTRA + '''groundY: 470, anchorX: 234, view: 0.28, topY: 24, footW: 70, feet: 38, atk: { melee: ["atk2", "atk1"], fin: "atk3" }, weapon: { frames: R27_HUNTER_FRAMES, sprites: {1:{w:295,h:120,gx:70,gy:60,L:185,glow:"#fb923c",name:"석장리 타제 주먹도끼"},2:{w:335,h:120,gx:70,gy:60,L:225,glow:"#a78bfa",name:"흑요석 슴베찌르개"},3:{w:344,h:120,gx:70,gy:60,L:234,glow:"#fbbf24",name:"신석기 간돌도끼"}} } },''')
rep('''        ...[2, 4].flatMap((e) => [1, 2, 3].map((t) => `assets/weapon/era${e}_t${t}.png`)),''',
    '''        ...[1, 2, 4].flatMap((e) => [1, 2, 3].map((t) => `assets/weapon/era${e}_t${t}.png`)),''')

# ───────── 2. 상수 ─────────
rep('''  var R26_DIFF_STD = { boss2: 1.06 };''', '''  var R26_DIFF_STD = { boss2: 1.06 };
  // [R27] 잡몹 체력 스펀지 해소 — 일반 몹(정예 포함)만 ×0.72(약 28% ↓, 4~6타에 썰리게). 중간보스 · 보스 체력과 패턴은 그대로
  var R27_MOB_HP_K = 0.72;
  // [R27] 주인공 발밑 영웅 링(시대별 고유색) · 3시대 옛 도트 전경 실루엣 끄기
  var R27_RING = { 1: "#fb923c", 2: "#facc15", 3: "#f43f5e", 4: "#22d3ee", 5: "#2dd4bf", 6: "#60a5fa" };
  var R27_FG_OFF = { 3: true };
  // [R27] 수묵 · 속성 '호흡' 피니시(3 · 4타 · 어퍼 · 돌진): 먹물 비산 + 시대 속성 검기
  var R27_BREATH = {
    1: { name: "화염 · 흑요석", c1: "#fb923c", c2: "#f97316", c3: "#a78bfa", kind: "flame" },
    2: { name: "태양 번개", c1: "#fde047", c2: "#facc15", c3: "#ffffff", kind: "bolt" },
    3: { name: "진홍 화랑 검풍", c1: "#f43f5e", c2: "#fb7185", c3: "#ffe4e6", kind: "wind" },
    4: { name: "칠흑 수묵 용오름", c1: "#0b0b10", c2: "#334155", c3: "#cbd5e1", kind: "inkdragon" },
    5: { name: "화차 폭염", c1: "#f97316", c2: "#fbbf24", c3: "#fff7ed", kind: "blast" },
    6: { name: "태극 백열 일섬", c1: "#ffffff", c2: "#60a5fa", c3: "#ef4444", kind: "flash" }
  };''')

# ───────── 3. 잡몹 체력 ×0.72 ─────────
rep('''    entity.maxHp = Math.round(entity.maxHp * hpK);
    entity.hp = entity.maxHp;
    if (typeof entity.speed === "number") entity.speed *= spdK;''', '''    if (!isBoss && !entity.isMidBoss) hpK *= R27_MOB_HP_K;
    entity.maxHp = Math.round(entity.maxHp * hpK);
    entity.hp = entity.maxHp;
    if (typeof entity.speed === "number") entity.speed *= spdK;''')

# ───────── 4. 원화 일반 몹 굽기 때 12% 톤다운 ─────────
rep('''    const k = view * dpr;
    for (let i = 0; i < poses.length; i++) {
      await nextFrame();
      const c = prescale(imgs[i], k);
      if (poses[i] === "walk" && t0) {''', '''    const k = view * dpr;
    for (let i = 0; i < poses.length; i++) {
      await nextFrame();
      const c = prescale(imgs[i], k);
      // [R27] 일반 몹 명도 12% ↓(굽기 때 1회 · 실행 비용 0) — 주인공이 몹 무리 위로 튀어나오게. 피격 흰 실루엣은 그대로
      {
        const tx = c.getContext("2d");
        tx.globalCompositeOperation = "source-atop";
        tx.fillStyle = "rgba(0,0,0,0.12)";
        tx.fillRect(0, 0, c.width, c.height);
        tx.globalCompositeOperation = "source-over";
      }
      if (poses[i] === "walk" && t0) {''')

# ───────── 5. 3시대 도트 전경 끄기 ─────────
rep('''        if (!PERF_OFF.fg) drawForegroundLayer(ctx, bd, camRX);''', '''        if (!PERF_OFF.fg && !R27_FG_OFF[g.era]) drawForegroundLayer(ctx, bd, camRX);''')

# ───────── 6. 영웅 링 + 수묵 호흡 · 카운터 일섬 HD 렌더러 ─────────
RENDER = r'''      // [R27] 주인공 발밑 영웅 링 — 그림자 위 · 몸 아래, 시대별 고유색 타원 오라(은은한 맥동). 높이 뛰면 옅어진다
      const drawHeroRing = (g, p, HA, onScreen) => {
        const col = R27_RING[g.era] || "#fde047";
        const rx = (HA ? HA.footW : 64) * 0.62 + 8;
        const pulse = 0.5 + 0.5 * Math.sin(g.rtick * 0.08);
        const air = Math.max(0.25, 1 - p.y / 150);
        const c2 = onScreen ? screen : ctx;
        c2.save();
        if (onScreen) {
          const F = frameAssets.cam;
          screen.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
          applyCam(screen, F);
          screen.translate(-F.camRX + p.x, p.z);
        } else c2.translate(p.x, p.z);
        c2.globalCompositeOperation = "lighter";
        c2.save();
        c2.scale(1, 0.28);
        c2.globalAlpha = (0.2 + 0.1 * pulse) * air;
        c2.drawImage(getGlowSprite(col), -rx * 1.3, -rx * 1.3, rx * 2.6, rx * 2.6);
        c2.restore();
        c2.globalAlpha = (0.6 + 0.22 * pulse) * air;
        c2.strokeStyle = col;
        c2.lineWidth = 2.4;
        c2.beginPath();
        c2.ellipse(0, 0, rx, rx * 0.27, 0, 0, TAU);
        c2.stroke();
        c2.globalAlpha = 0.4 * air;
        c2.strokeStyle = "#ffffff";
        c2.lineWidth = 1;
        c2.beginPath();
        c2.ellipse(0, 0, rx * 0.96, rx * 0.259, 0, 0, TAU);
        c2.stroke();
        c2.restore();
      };
      // [R27] 수묵 · 속성 호흡 이펙트(HD) — 먹물 붓터치 · 2시대 태양 번개 · 3시대 검풍 초승달 · 6시대 백열 일섬 · 패링 카운터 일섬. 시간 기준(ms)
      const drawBreathFx = (g) => {
        const L = g.breathFx;
        if (!L || !L.length || PERF_OFF.particles) return;
        const now = performance.now();
        const F = frameAssets.cam;
        screen.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
        screen.save();
        applyCam(screen, F);
        screen.translate(-F.camRX, 0);
        for (let i = L.length - 1; i >= 0; i--) {
          const e = L[i];
          const t = (now - e.t0) / e.dur;
          if (t >= 1) {
            L.splice(i, 1);
            continue;
          }
          if (t < 0) continue;
          const a = 1 - t;
          if (e.k === "ink") {
            const tt = (now - e.t0) / 16.7;
            const x = e.x + e.vx * tt;
            const y = e.y - e.vy * tt + 0.11 * tt * tt;
            screen.save();
            screen.translate(x, y);
            screen.rotate(e.rot + e.vr * tt);
            screen.globalAlpha = Math.min(1, a * 1.6) * e.al;
            screen.fillStyle = e.c;
            const len = e.len * (0.7 + 0.5 * Math.min(1, t * 3));
            const w = e.w * (1 - t * 0.5);
            screen.beginPath();
            screen.moveTo(-len * 0.5, 0);
            screen.quadraticCurveTo(-len * 0.1, -w, len * 0.5, -w * 0.25);
            screen.quadraticCurveTo(len * 0.62, 0, len * 0.5, w * 0.3);
            screen.quadraticCurveTo(-len * 0.05, w * 0.9, -len * 0.5, 0);
            screen.fill();
            if (e.drop) {
              screen.beginPath();
              screen.arc(len * 0.68, w * 0.1, w * 0.45, 0, TAU);
              screen.fill();
            }
            screen.restore();
          } else if (e.k === "bolt") {
            screen.save();
            screen.globalCompositeOperation = "lighter";
            screen.lineJoin = "round";
            const pts = e.pts;
            [[9, e.c2, 0.45], [3.2, e.c1, 0.95], [1.2, "#ffffff", 1]].forEach(([lw, c, al]) => {
              screen.globalAlpha = a * al;
              screen.strokeStyle = c;
              screen.lineWidth = lw;
              screen.beginPath();
              screen.moveTo(pts[0][0], pts[0][1]);
              for (let k = 1; k < pts.length; k++) screen.lineTo(pts[k][0], pts[k][1]);
              screen.stroke();
            });
            screen.restore();
          } else if (e.k === "arc") {
            screen.save();
            screen.globalCompositeOperation = "lighter";
            screen.translate(e.x + e.dir * 140 * t, e.y);
            screen.scale(e.dir, 1);
            const r = e.r * (0.8 + 0.5 * t);
            screen.globalAlpha = a * 0.75;
            screen.fillStyle = e.c2;
            screen.beginPath();
            screen.arc(0, 0, r, -1.15, 1.15);
            screen.arc(-r * 0.22, 0, r * 0.86, 1.05, -1.05, true);
            screen.closePath();
            screen.fill();
            screen.globalAlpha = a;
            screen.strokeStyle = e.c3;
            screen.lineWidth = 2;
            screen.beginPath();
            screen.arc(0, 0, r, -1.0, 1.0);
            screen.stroke();
            screen.restore();
          } else if (e.k === "slash") {
            // 화면을 가로지르는 백열 일섬(6시대 호흡 · 저스트 패링 카운터)
            const x0 = F.camRX - 40;
            const x1 = F.camRX + VIEW_W + 40;
            const grow = Math.min(1, t * 5);
            const xa = e.dir > 0 ? x0 : x1;
            const xb = xa + (x1 - x0) * grow * e.dir;
            screen.save();
            screen.globalCompositeOperation = "lighter";
            screen.lineCap = "round";
            [[e.w * 3.2, e.c2, 0.35], [e.w * 1.5, e.c3, 0.55], [e.w * 0.55, "#ffffff", 1]].forEach(([lw, c, al]) => {
              screen.globalAlpha = a * al;
              screen.strokeStyle = c;
              screen.lineWidth = lw * (0.6 + 0.4 * a);
              screen.beginPath();
              screen.moveTo(xa, e.y + e.tilt * (xa - e.x));
              screen.lineTo(xb, e.y + e.tilt * (xb - e.x));
              screen.stroke();
            });
            screen.restore();
          }
        }
        screen.restore();
      };
'''
rep('''      // [R25] 손에 든 무기 — 등급(TI.1~3) 스프라이트를''', RENDER + '''      // [R25] 손에 든 무기 — 등급(TI.1~3) 스프라이트를''')
# 링: HD 주인공은 flushLo 직후(그림자 위 · 몸 아래), 코드 스프라이트 주인공은 저해상도로
rep('''        if (HA) {
          flushLo();
          for (let i = 0; i < p.ghosts.length; i++) {''', '''        if (HA) {
          flushLo();
          drawHeroRing(g, p, HA, true);
          for (let i = 0; i < p.ghosts.length; i++) {''')
rep('''        drawContactShadow(ctx, p.x, p.z, HA ? HA.footW : sheet.footW || 64, p.y + (P && P.step != null ? P.lift * 4 : 0));
        if (p.ghosts.length && !HA) {''', '''        drawContactShadow(ctx, p.x, p.z, HA ? HA.footW : sheet.footW || 64, p.y + (P && P.step != null ? P.lift * 4 : 0));
        if (!HA) drawHeroRing(g, p, null, false);
        if (p.ghosts.length && !HA) {''')
rep('''        if (!PERF_OFF.particles) drawParticles(ctx, g.particles, bd);
        PSM();''', '''        if (!PERF_OFF.particles) drawParticles(ctx, g.particles, bd);
        if (g.breathFx && g.breathFx.length) {
          flushLo();
          drawBreathFx(g);
        }
        PSM();''')

# ───────── 7. 호흡 이펙트 생성 + 카운터 일섬 + 볼링 · 공중 ─────────
SPAWN = r'''    // [R27] 수묵 · 속성 '호흡' — 먹물 붓터치 비산 + 시대 속성 검기. power 1 = 3타 · 2 = 4타 피니시 · 어퍼 · 돌진
    const breathFX = (power = 1) => {
      const g = gameRef.current;
      const p = g.player;
      const B = R27_BREATH[g.era] || R27_BREATH[1];
      const now = performance.now();
      const L = g.breathFx || (g.breathFx = []);
      if (L.length > 90) L.splice(0, L.length - 90);
      const hx = p.x + p.facing * 70;
      const hy = p.z - p.y - 58;
      const qm = g.quality.tier >= 2 ? 0.5 : 1;
      const nInk = Math.round((power > 1 ? 12 : 8) * qm * (B.kind === "inkdragon" ? 1.6 : 1));
      for (let i = 0; i < nInk; i++) {
        const ang = (Math.random() - 0.5) * 1.6 + (p.facing > 0 ? 0 : Math.PI);
        const sp = rand(2.2, 6.5) * (power > 1 ? 1.25 : 1);
        const swirl = B.kind === "inkdragon";
        L.push({ k: "ink", t0: now + (swirl ? i * 14 : 0), dur: rand(380, 620), x: hx + rand(-18, 18), y: hy + rand(-22, 26), vx: Math.cos(ang) * sp + (swirl ? Math.sin(i) * 1.2 : 0), vy: swirl ? rand(2.5, 5) : Math.sin(-ang) * sp * 0.6 + rand(0.5, 2.5), rot: ang + rand(-0.4, 0.4), vr: rand(-0.03, 0.03), len: rand(16, 44) * (power > 1 ? 1.2 : 1), w: rand(3, 7.5), c: i % 4 === 0 ? "#1e1b2e" : "#07070b", al: rand(0.75, 0.95), drop: Math.random() < 0.4 });
      }
      if (B.kind === "flame") {
        for (let i = 0; i < 10 * qm; i++) spawnPart({ kind: "EMBER", x: hx + rand(-30, 30), z: p.z, y: p.y + 50 + rand(-20, 30), vx: p.facing * rand(1, 4), vy: rand(1.5, 4), size: rand(2, 3.6), c: i % 3 ? B.c1 : B.c2, seed: Math.random() * 10, life: 26, maxLife: 26 });
        for (let i = 0; i < 7 * qm; i++) spawnPart({ kind: "SPARK", x: hx, z: p.z + rand(-6, 6), y: p.y + 54, vx: p.facing * rand(6, 13), vz: rand(-1, 1), vy: rand(-1, 3), size: rand(2, 3.2), c: B.c3, life: 18, maxLife: 18 });
      } else if (B.kind === "bolt") {
        for (let b = 0; b < (power > 1 ? 2 : 1); b++) {
          const bx = hx + p.facing * (20 + b * 60);
          const pts = [];
          let x = bx + rand(-30, 30);
          for (let k = 0; k <= 6; k++) {
            pts.push([x, hy - 230 + k * 40]);
            x += rand(-16, 16);
          }
          pts[pts.length - 1] = [bx, hy + 30];
          L.push({ k: "bolt", t0: now + b * 60, dur: 230, pts, c1: B.c1, c2: B.c2 });
        }
        addLight(hx, p.z, p.y + 60, 120, B.c1, 1, 12);
      } else if (B.kind === "wind") {
        for (let k = 0; k < (power > 1 ? 3 : 2); k++) L.push({ k: "arc", t0: now + k * 55, dur: 340, x: hx - p.facing * 20, y: hy + (k - 1) * 18, dir: p.facing, r: 70 + k * 16, c2: B.c2, c3: B.c3 });
        for (let i = 0; i < 8 * qm; i++) spawnPart({ kind: "EMBER", x: hx + rand(-20, 40) * p.facing, z: p.z, y: p.y + 40 + rand(0, 50), vx: p.facing * rand(2, 5), vy: rand(0.5, 2), size: rand(1.6, 2.6), c: B.c2, seed: Math.random() * 10, life: 30, maxLife: 30 });
      } else if (B.kind === "inkdragon") {
        addShock(hx, p.z, "#94a3b8", 120, 18);
      } else if (B.kind === "blast") {
        explode(hx + p.facing * 20, p.z, 56, power > 1 ? 1.5 : 1.1, B.c1);
        for (let i = 0; i < 10 * qm; i++) spawnPart({ kind: "EMBER", x: hx + rand(-26, 26), z: p.z, y: p.y + 50 + rand(-10, 20), vx: p.facing * rand(1, 5), vy: rand(2, 5), size: rand(2.2, 3.8), c: i % 2 ? B.c1 : B.c2, seed: Math.random() * 10, life: 24, maxLife: 24 });
      } else if (B.kind === "flash") {
        L.push({ k: "slash", t0: now, dur: 300, x: p.x, y: hy + 6, dir: p.facing, tilt: -0.04, w: power > 1 ? 9 : 6, c2: B.c2, c3: B.c3 });
      }
      g.breathCount = (g.breathCount || 0) + 1;
    };
    // [R27] 저스트 패링 카운터 일섬 — 0.2초 슬로우 + 화면을 가로지르는 백열 일섬으로 앞쪽 적에게 반격(다음 틱에 판정)
    const parryCounter = () => {
      const g = gameRef.current;
      const p = g.player;
      g.slowMo = Math.max(g.slowMo || 0, 12);
      const L = g.breathFx || (g.breathFx = []);
      L.push({ k: "slash", t0: performance.now(), dur: 320, x: p.x, y: p.z - p.y - 60, dir: p.facing, tilt: -0.05, w: 10, c2: "#fde047", c3: "#fef9c3" });
      g.counterSlashes = (g.counterSlashes || 0) + 1;
      addTimer(1, () => {
        const gg = gameRef.current;
        const pp = gg.player;
        checkMeleeHitbox(430, 70, 1.8, 11, 0, 2, true);
        addDamagePopup(pp.x + pp.facing * 70, pp.z, pp.y + 80, "COUNTER!", true, null, 0, "#fef08a");
      });
    };
'''
rep('''    const justParry = () => {''', SPAWN + '''    const justParry = () => {''')
rep('''      addDamagePopup(p.x, p.z, p.y + 46, "JUST PARRY!", true, `\\uAC01\\uC131 +${PARRY_ULT_GAIN}`, 0, "#fde047");''',
    '''      addDamagePopup(p.x, p.z, p.y + 46, "JUST PARRY!", true, `\\uAC01\\uC131 +${PARRY_ULT_GAIN}`, 0, "#fde047");
      parryCounter();''')
# 3 · 4타 피니시: 호흡 + 볼링(살아남은 가벼운 적이 날아가 다른 적을 친다)
rep('''        if (cls === "AXE") {
          // [R23] 도끼: 헛스윙에도 걸리던 117~150ms 정지 제거(뻣뻣함의 원인) — 적중했을 때만 강타 규칙(3.7f + 방향 쉐이크)''',
    '''        if (step >= 3) breathFX(isFinisher ? 2 : 1);
        g._bowlFin = isFinisher;
        if (cls === "AXE") {
          // [R23] 도끼: 헛스윙에도 걸리던 117~150ms 정지 제거(뻣뻣함의 원인) — 적중했을 때만 강타 규칙(3.7f + 방향 쉐이크)''')
rep('''        else checkMeleeHitbox(175, 62, 1 + step * 0.3, isFinisher ? 14 : 5, isFinisher ? 12.5 : step === 2 ? 6 : 0, isFinisher ? 2 : 1, isFinisher);
      });
    };''', '''        else checkMeleeHitbox(175, 62, 1 + step * 0.3, isFinisher ? 14 : 5, isFinisher ? 12.5 : step === 2 ? 6 : 0, isFinisher ? 2 : 1, isFinisher);
        g._bowlFin = false;
      });
    };''')
rep('''      const heavy = isHeavyMob(target);
      const kMul = target.isMidBoss ? 0.25 : heavy ? 0.55 : 1;
      target.vx = dir * knockX * kMul;''', '''      const heavy = isHeavyMob(target);
      const kMul = target.isMidBoss ? 0.25 : heavy ? 0.55 : 1;
      target.vx = dir * knockX * kMul;
      // [R27] 4타 피니시 볼링: 살아남은 가벼운 적을 '던진 적'으로 날려 다른 적과 연쇄 충돌(STRIKE!)
      if (g._bowlFin && target.hp > 0 && target !== g.boss && !target.isMidBoss && !heavy && !target.thrown && !target.grabbed) {
        target.vx = dir * Math.max(Math.abs(target.vx), 15);
        target.vy = Math.max(target.vy, 5.5);
        target.thrown = { dir, t: 34, hit: [], gen: 1 };
        g.bowlLaunches = (g.bowlLaunches || 0) + 1;
      }''')
# 공중 연타 체공 소폭 ↑
rep('''      } else if (target.y > 8) {
        target.vy = Math.max(target.vy, 4.8);
      }''', '''      } else if (target.y > 8) {
        // [R27] 공중 연타 체공 소폭 ↑(4.8 → 5.6) + 저글 중 중력 완화
        target.vy = Math.max(target.vy, 5.6);
      }
      if (target.y > 8) target.juggleT = 26;''')
rep('''            en.y += en.vy;
            en.vy -= 0.75;''', '''            en.y += en.vy;
            en.vy -= en.juggleT > 0 ? 0.64 : 0.75;
            if (en.juggleT > 0) en.juggleT--;''')
rep('''        p._atkSrc = "air";
        p._fin = false;
        p.vy = Math.max(p.vy, 3);''', '''        p._atkSrc = "air";
        p._fin = false;
        p.vy = Math.max(p.vy, 3.8);''')
# 어퍼 · 돌진 호흡
rep('''        checkMeleeHitbox(205, 74, 1.9, 8.5, 16, 3, true);
      }, false);''', '''        breathFX(2);
        checkMeleeHitbox(205, 74, 1.9, 8.5, 16, 3, true);
      }, false);''')
rep('''        if (evo) {
          g.ribbonSlashes.push({ x: p.x + p.facing * 130,''', '''        breathFX(2);
        if (evo) {
          g.ribbonSlashes.push({ x: p.x + p.facing * 130,''')

# ───────── 8. 구역 마지막 적 킬캠 ─────────
rep('''              st.score += 1500;
              addDamagePopup(p.x, p.z, 60, "ZONE CLEAR!", true, "+1,500 BONUS", 0, "#fde047");''', '''              st.score += 1500;
              addDamagePopup(p.x, p.z, 60, "ZONE CLEAR!", true, "+1,500 BONUS", 0, "#fde047");
              // [R27] 구역 마지막 적 막타 킬캠: 0.3초 슬로우 + 짧은 화면 플래시 + 살짝 당겨 보기
              g.slowMo = Math.max(g.slowMo || 0, 18);
              g.flashAlpha = Math.max(g.flashAlpha, 0.38);
              g.flashColor = "#ffffff";
              g.targetZoom = 1.06;
              addTimer(22, () => {
                gameRef.current.targetZoom = 1;
              });
              addTrauma(0.22);
              g.killCams = (g.killCams || 0) + 1;''')

# ───────── 9. 보행 리듬 통일(속도 연동 3~4틱) + 착지 흙먼지 가시성 ─────────
rep('''    const stepHeroWalk = (p) => {
      p.stepT = (p.stepT || 0) + 1;
      if (p.stepT % (p._stepC || HERO_STEP) === 0) {
        p.steps = (p.steps || 0) + 1;
        // [R23] 발 구름 먼지를 앞발 · 뒷발 번갈아(좌 · 우 교대) — 같은 발로만 튀던 먼지가 한발 깡총 느낌을 키웠다
        const n = spawnStepDust(p.x, p.z + 2, p.facing, 1 + (p.steps & 1), p._assetFrame ? p._feet || 30 : 14, 1.08, p.steps & 1 ? 1 : -1);''',
    '''    const stepHeroWalk = (p) => {
      // [R27] 보행 리듬 통일: 8프레임 질주는 이동 속도에 맞춰 프레임당 3~4틱(보통 걸음 약 3.5 · 매혹 버프 · 대각선 3 · 출발 가속 4)
      const sp = Math.hypot(p.mvx || 0, (p.mvz || 0) * 1.6);
      const kk = Math.max(1, Math.min(4 / 3, sp / 6.3));
      const C = p._stepC || HERO_STEP;
      const T0 = p.stepT || 0;
      p.stepT = T0 + kk;
      if (Math.floor(p.stepT / C) > Math.floor(T0 / C)) {
        p.steps = (p.steps || 0) + 1;
        // [R23] 발 구름 먼지를 앞발 · 뒷발 번갈아(좌 · 우 교대) — [R27] 8프레임 질주는 한 줌 더 · 크게(어두운 바닥에서도 보이게)
        const big = C >= 16 && p._assetFrame ? 1 : 0;
        const n = spawnStepDust(p.x, p.z + 2, p.facing, 1 + (p.steps & 1) + big, p._assetFrame ? p._feet || 30 : 14, big ? 1.32 : 1.08, p.steps & 1 ? 1 : -1);''')
rep('''      } else if (pt.kind === "STEP") {
        const k = pt.life / pt.maxLife;
        ctx.globalAlpha = k * 0.62;''', '''      } else if (pt.kind === "STEP") {
        const k = pt.life / pt.maxLife;
        ctx.globalAlpha = k * 0.76;''')

# ───────── 10. 퀴즈 2건 교정(디렉터 문구 그대로) ─────────
rep('"고구려의 대막리지가 되어 권력을 잡았고, 천리장성 쌓는 일을 맡아 당의 침략에 대비하였다."',
    '"천리장성 쌓는 일을 감독하였고, 뒤에 대막리지가 되어 당의 침략에 강경하게 맞섰다."')
rep('"위화도에서 군대를 돌려 권력을 잡은 뒤, 1392년 새 나라를 세우고 도읍을 한양으로 옮겼다."',
    '"위화도에서 군대를 돌려 권력을 잡은 뒤, 1392년 새 나라를 세우고, 1394년 도읍을 한양으로 옮겼다."')
# 해설도 고친 문제와 맞춤(안시성 싸움의 주체를 연개소문 개인으로 읽히지 않게)
rep('"연개소문은 당에 강경하게 맞섰고, 당 태종의 침략을 안시성 등에서 막아 냈어요."',
    '"연개소문은 천리장성 쌓는 일을 감독했고, 대막리지가 되어 당에 강경하게 맞섰어요. 당 태종의 침략은 안시성 싸움 등으로 막아 냈어요."')
rep('"태조 이성계는 조선을 세우고 한양을 도읍으로 삼았어요."',
    '"태조 이성계는 1392년 조선을 세우고, 1394년 한양으로 도읍을 옮겼어요."')

open(P, "w", encoding="utf-8").write(s)
print("R27 patch ok —", n, "edits")
