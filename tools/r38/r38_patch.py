#!/usr/bin/env python3
"""R38-1단계 「맵 확장 + 치트키급 과밀 이펙트 + 60fps 방어」 — shinsi-R37/index.html 위에 문자열 치환으로 적용.

사용: cp shinsi-R37/index.html shinsi-R38/index.html && python -I tools/r38/r38_patch.py shinsi-R38/index.html
      (Windows · Anaconda: powershell -File tools/r37/run_py.ps1 tools/r38/r38_patch.py shinsi-R38/index.html)
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R38] 주석으로 이유를 남긴다.
      앵커는 모두 ASCII 코드 줄에 건다(한글 주석 · \\uXXXX 문자열 앵커 없음).

보존(절대 손대지 않음 — tools/r38/guard38.py가 패치 전후 해시로 확인):
  권율(5시대 주인공) 걸음걸이 — ACTOR_SPEC.era5_hero · HERO_STEP* · heroRunRhythm · stepHeroWalk · heroPose/heroPose0 · stepAttract · 주인공 이동 적분 · drawHeroEnt · era5_hero 스프라이트 12장
  R37 사운드 엔진 — createR37Sfx · r37* 훅 9개 · 호출 자리 · assets/sfx · sfx_manifest.json · MANIFEST.json

바뀌는 것:
  1. 맵 1.5배: WORLD_WIDTH 6400 → 9600 · ZONE_CAM [480, 2850, 5100, 8640] · ZONE_TRIG(cam + 220/240/250/250) · 1-2 경계 4500 · 유물 방 x ×1.5  (?map38=1 → R37 길이)
  2. 구역 전투 카메라: Z1~Z3는 1.5화면(ZONE_SPAN 1440) 범위 추적 · 주인공 벽 · 구역 경계 기둥 · 스폰 기준점(지금 카메라) · 6시대 탐조등 중심. Z4는 고정 화면 그대로
  3. 과밀 이펙트(tools/r38/r38_fx.js): 고정 풀 2개 · 틱당 예산 · 밀도 계수 · 타격/처치/각성/구역 돌입·정리 훅  (?fx38=0/1/2)
  4. 파티클 상한 240/170/110 → 300/200/120 · DEV 훅 r38()
"""
import os
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0
HERE = os.path.dirname(os.path.abspath(__file__))
FX = open(os.path.join(HERE, "r38_fx.js"), encoding="utf-8").read().rstrip("\n")
FX_TOP, FX_APP = FX.split("// @@R38-APP@@\n")
FX_TOP = FX_TOP.rstrip("\n")
FX_APP = FX_APP.rstrip("\n")


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 1. 맵 상수(모든 월드 x의 뿌리) — RELIC_ROOMS(3474행)보다 앞에 있어야 하므로 ASSET_PAR 뒤 ─────────
rep('''  var ASSET_PAR = { far: 0.15, mid: 0.45, ground: 1 };''', '''  var ASSET_PAR = { far: 0.15, mid: 0.45, ground: 1 };
  // [R38] 맵 1.5배 — 월드 길이 · 구역 카메라 · 트리거 · 1-2 경계 · 유물 방 x를 이 상수 하나에서 파생한다. ?map38=1 → R37 길이(비교용) · 1~3 사이 값
  var R38_MAP_K = (() => {
    try {
      const v = new URLSearchParams(window.location.search).get("map38");
      if (v == null || v === "") return 1.5;
      const f = parseFloat(v);
      return f >= 1 && f <= 3 ? f : 1.5;
    } catch (e) {
      return 1.5;
    }
  })();
  var r38MapX = (x) => Math.round(x * R38_MAP_K);''')

# ───────── 2. 유물 방 x(시대별) — 월드 길이에 비례 ─────────
for x, obj in [(2620, "boulder"), (1320, "dolmen"), (2700, "stele"), (1500, "pagoda"), (2900, "lantern"), (1640, "brick")]:
    rep(f'{{ x: {x}, obj: "{obj}"', f'{{ x: r38MapX({x}), obj: "{obj}"')

# ───────── 3. 월드 폭 · 구역 카메라 · 트리거 · 구역 전투 카메라 범위 ─────────
rep('''  var WORLD_WIDTH = 6400;
  var MAX_CAM = WORLD_WIDTH - VIEW_W;''', '''  // [R38] 월드 6400 → 9600(R38_MAP_K 1.5). 카메라 상한 · 레이더 · 투사체 컬링 · 적/보스/위험물 clamp는 모두 WORLD_WIDTH에서 따라온다
  var WORLD_WIDTH = r38MapX(6400);
  var MAX_CAM = WORLD_WIDTH - VIEW_W;''')
rep('''  var ZONE_CAM = [480, 1900, 3400, 5440];
  var ZONE_TRIG = [700, 2140, 3650, 5690];''', '''  // [R38] 구역 카메라 [480, 2850, 5100, 8640](Z1은 시작 걸음 자리 그대로 · Z4 = MAX_CAM) · 트리거 = 카메라 + 220/240/250/250(R37과 같은 간격)
  var ZONE_CAM = [480, r38MapX(1900), r38MapX(3400), WORLD_WIDTH - VIEW_W];
  var ZONE_TRIG = [ZONE_CAM[0] + 220, ZONE_CAM[1] + 240, ZONE_CAM[2] + 250, ZONE_CAM[3] + 250];
  // [R38] 구역 전투 카메라 범위: Z1~Z3는 1.5화면(1440) 안에서 주인공을 따라가고, Z4 보스 아레나는 1화면 고정(보스 패턴이 고정 화면을 가정). ?map38=1이면 R37처럼 1화면
  var ZONE_SPAN = R38_MAP_K > 1 ? Math.round(VIEW_W * 1.5) : VIEW_W;
  var r38ZoneSpan = (zi) => zi < 3 ? ZONE_SPAN : VIEW_W;
  var r38ZoneCam = (g, follow) => {
    const L = ZONE_CAM[g.zoneIdx] != null ? ZONE_CAM[g.zoneIdx] : 0;
    const sp = r38ZoneSpan(g.zoneIdx);
    return sp > VIEW_W ? clamp(follow, L, L + sp - VIEW_W) : L;
  };
  // 웨이브 · 중간보스 스폰 기준점 = 지금 카메라(구역 범위 안으로 자름) → 화면 밖 ±60~130px에서 걸어 들어오는 등장이 그대로 유지된다
  var r38SpawnBase = (g) => {
    const zi = g.zoneIdx;
    const L = ZONE_CAM[zi] != null ? ZONE_CAM[zi] : g.cameraX;
    const sp = r38ZoneSpan(zi);
    return sp > VIEW_W ? clamp(g.cameraX, L, L + sp - VIEW_W) : L;
  };''')

# ───────── 4. 1시대 1-1/1-2 경계(석장리 → 신석기) ─────────
rep('''  var SEOKJANGRI_NEO_X = 3e3;''', '''  var SEOKJANGRI_NEO_X = r38MapX(3e3); // [R38] 월드 길이에 비례(Z2 화면 끝과 Z3 사이의 걷는 구간에 그대로 놓인다)''')

# ───────── 5. 구역 경계 기둥(저해상도 층) — 오른쪽 기둥을 구역 범위 끝으로 ─────────
rep('''    [L + 10, L + VIEW_W - 10].forEach((bx) => {''', '''    // [R38] 오른쪽 기둥 = 구역 전투 범위 끝(Z1~Z3 1.5화면 · Z4 1화면)
    [L + 10, L + r38ZoneSpan(g.zoneIdx) - 10].forEach((bx) => {''')

# ───────── 6. 스폰 기준점: 웨이브 · 1시대 곰 중간보스 · 2~6시대 중간보스 ─────────
rep('''      const L = ZONE_CAM[g.zoneIdx];
      const roles = g.paleoWaves && g.paleoWaves.length ? g.paleoWaves.shift() : null;''', '''      const L = r38SpawnBase(g); // [R38] 구역 카메라 고정값 → 지금 카메라(범위 추적 중에도 화면 밖 등장)
      const roles = g.paleoWaves && g.paleoWaves.length ? g.paleoWaves.shift() : null;''')
rep('''      const L = ZONE_CAM[g.zoneIdx];
      const mb = applyStage1PowerScaling(createStage1MidBoss(L + VIEW_W + 60, 416), g.stats);''', '''      const L = r38SpawnBase(g); // [R38] 지금 카메라 기준(화면 오른쪽 밖 60px)
      const mb = applyStage1PowerScaling(createStage1MidBoss(L + VIEW_W + 60, 416), g.stats);''')
rep('''      const L = ZONE_CAM[g.zoneIdx] != null ? ZONE_CAM[g.zoneIdx] : g.cameraX;''', '''      const L = r38SpawnBase(g); // [R38] 지금 카메라 기준(구역 범위 안으로 자름 · 구역 밖이면 카메라)''')

# ───────── 7. 6시대 탐조등 중심 = 구역 범위 가운데 ─────────
rep('''      if (era === 6) g.search = { cx: ZONE_CAM[zi] + VIEW_W / 2, x: ZONE_CAM[zi] + VIEW_W / 2, t: 0 };''', '''      // [R38] 탐조등은 구역 전투 범위(1.5화면)의 가운데를 중심으로 왕복한다
      if (era === 6) g.search = { cx: ZONE_CAM[zi] + r38ZoneSpan(zi) / 2, x: ZONE_CAM[zi] + r38ZoneSpan(zi) / 2, t: 0 };''')

# ───────── 8. 구역 전투 중 주인공 벽 · 카메라 목표 ─────────
rep('''        if (g.zoneState === "LOCKED") {
          const L = ZONE_CAM[g.zoneIdx];
          p.x = clamp(p.x, L + 46, L + VIEW_W - 46);
        }''', '''        if (g.zoneState === "LOCKED") {
          // [R38] 벽 = 구역 전투 범위(Z1~Z3 1.5화면 · Z4 1화면)
          const L = ZONE_CAM[g.zoneIdx];
          p.x = clamp(p.x, L + 46, L + r38ZoneSpan(g.zoneIdx) - 46);
        }''')
rep('''        if (g.zoneState === "LOCKED") targetCamX = ZONE_CAM[g.zoneIdx];''', '''        // [R38] 구역 전투(Z1~Z3)는 1.5화면 범위 안에서 주인공을 따라간다(Z4 보스 아레나는 고정 화면 그대로)
        if (g.zoneState === "LOCKED") targetCamX = r38ZoneCam(g, targetCamX);''')

# ───────── 9. 과밀 이펙트 엔진(최상위 · R31 고정 풀 바로 앞) ─────────
rep('''  var r31Hfx = (k, x, y, dur, o) => {''', FX_TOP + '''
  var r31Hfx = (k, x, y, dur, o) => {''')

# ───────── 10. 파티클 상한(옛 경로) 240/170/110 → 300/200/120 ─────────
rep('''    const particleCap = () => [240, 170, 110][gameRef.current.quality.tier];''', '''    const particleCap = () => [300, 200, 120][gameRef.current.quality.tier]; // [R38] 상한 ↑(링 덮어쓰기 그대로 · 과밀 이펙트는 별도 고정 풀)''')

# ───────── 11. App 안 훅(r31HitBurst 바로 앞) + 타격 자리 ─────────
rep('''    const r31HitBurst = (g, en, dir, hv, fin, vr) => {''', FX_APP + '''
    const r31HitBurst = (g, en, dir, hv, fin, vr) => {''')
rep('''      r31Hfx(1, x, y, hv ? 170 : 120, { s: (fin ? 1.35 : hv ? 1.15 : 1) * (big ? 1.15 : 1), c: C[2], c2: C[0], a: Math.random() * 6.28 });''', '''      r31Hfx(1, x, y, hv ? 170 : 120, { s: (fin ? 1.35 : hv ? 1.15 : 1) * (big ? 1.15 : 1), c: C[2], c2: C[0], a: Math.random() * 6.28 });
      // [R38] 과밀: 잉크 스플래시 · 2중 참격호 · 불꽃 다발(+강타 · 피니시: 충격 링 · 임팩트 라인 · 잉크 방울)
      r38Hit(g, en, x, y, dir, hv, fin, big, C);''')

# ───────── 12. 처치 · 각성 · 구역 돌입 · 구역 정리 ─────────
rep('''            if (!r37EnemyDown(en)) r36MobVoice(en, "die");''', '''            if (!r37EnemyDown(en)) r36MobVoice(en, "die");
            // [R38] 처치 연출(잉크 폭발 · 충격 링 · 임팩트 라인 · 불꽃 · 불씨)
            r38Kill(g, en);''')
rep('''      g.ultDarkness = 78;''', '''      g.ultDarkness = 78;
      r38Ult(g); // [R38] 각성 충격파''')
rep('''      g.zoneState = "LOCKED";
      g.waveSpawnCd = 34;''', '''      g.zoneState = "LOCKED";
      r38Burst(g, g.player.x, g.player.z, 1.6, eraObjOf().accentColor); // [R38] 구역 돌입 충격파
      g.waveSpawnCd = 34;''')
rep('''              addDamagePopup(p.x, p.z, 60, "ZONE CLEAR!", true, "+1,500 BONUS", 0, "#fde047");''', '''              addDamagePopup(p.x, p.z, 60, "ZONE CLEAR!", true, "+1,500 BONUS", 0, "#fde047");
              r38Burst(g, p.x, p.z, 2, "#fde047"); // [R38] 구역 정리 충격파''')

# ───────── 13. 그리기: 저해상도 층(파티클 뒤) · HD 오버레이(R31 풀 뒤) ─────────
rep('''        if (!PERF_OFF.particles) drawParticles(ctx, g.particles, bd);''', '''        if (!PERF_OFF.particles) drawParticles(ctx, g.particles, bd);
        drawR38Parts(ctx); // [R38] 과밀 파티클 고정 풀(불꽃 · 잉크 방울 · 불씨)''')
rep('''        overlay.push((o) => drawR31Hfx(g, o));''', '''        overlay.push((o) => drawR31Hfx(g, o));
        overlay.push((o) => drawR38Hfx(g, o)); // [R38] 과밀 이펙트 고정 풀(잉크 스플래시 · 참격호 · 충격 링 · 임팩트 라인)''')

# ───────── 14. 점검 훅 ─────────
rep('''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),''', '''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),
          // [R38] 검증: 맵 상수 · 구역 카메라 · 과밀 이펙트 풀 상태(살아 있는 칸 · 최대 · 예산 거절 · 밀도 계수) · 주인공 프레임 · 성능
          r38: () => {
            const g = gameRef.current;
            const p = g.player;
            return { mode: R38_FX_MODE, budget: R38_BUDGET.slice(), mapK: R38_MAP_K, world: WORLD_WIDTH, maxCam: MAX_CAM, zoneCam: ZONE_CAM.slice(), zoneTrig: ZONE_TRIG.slice(), span: ZONE_SPAN, neoX: SEOKJANGRI_NEO_X, cam: Math.round(g.cameraX), zone: g.zoneIdx, zoneState: g.zoneState, px: Math.round(p.x), frame: p._assetFrame || null, steps: p.steps || 0, stepT: p.stepT || 0, stat: Object.assign({}, R38_STAT), perf: g.perf ? { render: g.perf.render, last: g.perf.last, max: g.perf.max } : null, ema: g.quality.ema, tier: g.quality.tier, dpr: g.quality.dpr };
          },
          // [R38] 검증: 과밀 모드(0 끔 · 1 과밀 · 2 극과밀) · 틱당 예산을 실행 중에 바꾼다(같은 장면에서 A-B 비교용)
          r38mode: (m, budget, skip) => {
            if (m != null) R38_FX_MODE = Math.max(0, Math.min(2, m | 0));
            if (budget) for (let i = 0; i < 3; i++) if (budget[i] != null) R38_BUDGET[i] = budget[i];
            if (skip) for (const k of Object.keys(R38_SKIP)) R38_SKIP[k] = !!skip[k];
            R38_STAT.maxMsH = R38_STAT.maxMsP = R38_STAT.maxH = R38_STAT.maxP = 0;
            return { mode: R38_FX_MODE, budget: R38_BUDGET.slice(), skip: Object.assign({}, R38_SKIP) };
          },''')

open(P, "w", encoding="utf-8").write(s)
print("R38 patch ok —", n, "edits")
