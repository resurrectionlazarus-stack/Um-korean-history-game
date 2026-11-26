#!/usr/bin/env python3
"""R31 — 전 시대 정식 원화 · 효과음 통합(83항목) · 2시대 해모수 신화 개편 · 4시대 척준경 5대 전선 · 스몰 미션 ·
6시대 약산 김원봉(의열단 폭탄 · 모젤 C96 · 야습 그림자 · 의열 폭파 일섬) · 타격 이펙트 5종(HD 고정 풀).

사용: python3 -I r31_patch.py <shinsi-R31/index.html>   (R30 index.html 위에 적용)
"""
import re
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:140]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 0. 무기 쥔 자리(실측) · 해모수 신화 자세 4장 · 이펙트 · 몹 ─────────
rep('''"run":[442,210,-25,0],"run2":[461,213,-15,0],"run3":[470,174,-30,0],"run4":[450,169,-35,0],"run5":[432,212,-25,0],"run6":[462,216,-15,0],"run7":[491,181,-30,0],"run8":[445,167,-35,0]''',
    '''"run":[462,192,-25,0],"run2":[462,193,-15,0],"run3":[454,183,-30,0],"run4":[458,187,-35,0],"run5":[461,192,-25,0],"run6":[458,193,-15,0],"run7":[455,182,-30,0],"run8":[457,190,-35,0]''')
rep('''"run":[407,210,15,0],"run2":[430,222,10,0],"run3":[356,247,25,0],"run4":[346,240,30,0],"run5":[390,204,15,0],"run6":[430,228,10,0],"run7":[366,249,25,0],"run8":[345,236,30,0]''',
    '''"run":[460,183,15,0],"run2":[456,178,10,0],"run3":[453,172,25,0],"run4":[457,178,30,0],"run5":[458,182,15,0],"run6":[462,187,10,0],"run7":[454,178,25,0],"run8":[457,178,30,0]''')
rep('''"atk3_3":[445,324,40,0],"hit":[344,231,120,1]};''',
    '''"atk3_3":[445,324,40,0],"heavy_cleave":[454,239,30,0],"slam_prep":[352,68,-120,1],"slam_hit":[442,243,70,0],"summon_sky":[393,36,-88,0],"hit":[344,231,120,1]};
  // [R31] 쥔 자리 실측 갱신 — 1시대 대사냥꾼 정식 질주 8장(run~run8) · 2시대 해모수 정식 질주 8장 + 신화 자세 4장(heavy_cleave · slam_prep · slam_hit · summon_sky).
  //  앞 주먹 자동 검출(앞쪽 가장자리 · 손목 높이) 뒤 무기 겹쳐 그리기 시트로 20장 모두 주먹 안 확인(tools/r31/grip_probe.py · grip_overlay.py)''')

rep('''    era2_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8", "atk_prep", "atk1_2", "atk1_3", "atk2_prep", "atk2_2", "atk2_3", "atk3_prep", "atk3", "atk3_2", "atk3_3"],''',
    '''    // [R31] 해모수 신화 자세 4장: 3타 강타(heavy_cleave) · 4타 · 급강하 내려찍기(slam_prep → slam_hit) · 일섬 · 각성 하늘 소환(summon_sky)
    era2_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8", "atk_prep", "atk1_2", "atk1_3", "atk2_prep", "atk2_2", "atk2_3", "atk3_prep", "atk3", "atk3_2", "atk3_3", "heavy_cleave", "slam_prep", "slam_hit", "summon_sky"],''')

rep('''  var FX_SPEC = { buddha_descent: { view: 0.3 } };''',
    '''  // [R31] 2시대 신화 이펙트 5종(512×512) — view = 굽는 배율(가장 크게 그릴 때 기준)
  var FX_SPEC = { buddha_descent: { view: 0.3 }, fx_tiger_claw: { view: 0.42 }, fx_bear_slam: { view: 0.46 }, fx_giant_lute_sword: { view: 0.66 }, fx_bronze_mirror_halo: { view: 0.46 }, fx_thunder_crack: { view: 0.54 } };''')

rep('''    bj_guard: { era: 3, unit: "BJ_GUARD", h: 130 },
    bj_archer: { era: 3, unit: "BJ_ARCHER", h: 134 },
    gg_pike: { era: 3, unit: "GG_PIKE", h: 140 },
    gg_cav: { era: 3, unit: "GG_CAV", h: 168 },''',
    '''    // [R31] 미술팀 정식 원화(webp) 11종 + 새 병종 5종 — 모두 원본이 12% 저채도 · 어두운 톤(MANIFEST tone 표식)이라 굽기 톤다운 생략
    bj_guard: { era: 3, unit: "BJ_GUARD", h: 130, toned: true },
    bj_archer: { era: 3, unit: "BJ_ARCHER", h: 134, toned: true },
    gg_pike: { era: 3, unit: "GG_PIKE", h: 140, toned: true },
    gg_cav: { era: 3, unit: "GG_CAV", h: 168, toned: true },''')
rep('''    wa_raider: { era: 3, unit: "WA_RAIDER", h: 130 },''', '''    wa_raider: { era: 3, unit: "WA_RAIDER", h: 130, toned: true },''')
rep('''    wakou_sword: { era: 4, unit: "WAKOU_SWORD", h: 130 },''',
    '''    wakou_sword: { era: 4, unit: "WAKOU_SWORD", h: 130, toned: true },
    // [R31] 4시대 5대 전선 새 병종 — 여진(동북 9성) 도끼병 · 기병 · 홍건적 도검병 · 선봉 쌍도 정예
    jurchen_inf: { era: 4, unit: "JURCHEN_INF", h: 136, toned: true },
    jurchen_cav: { era: 4, unit: "JURCHEN_CAV", h: 168, toned: true },
    redturban_inf: { era: 4, unit: "REDTURBAN_INF", h: 132, toned: true },
    redturban_elite: { era: 4, unit: "REDTURBAN_ELITE", h: 144, toned: true },''')
rep('''    qing_rider: { era: 5, unit: "QING_RIDER", h: 168 },''', '''    qing_rider: { era: 5, unit: "QING_RIDER", h: 168, toned: true },''')
rep('''    fr_rifle: { era: 6, unit: "FR_RIFLE", h: 134 },
    fr_bayonet: { era: 6, unit: "FR_BAYONET", h: 134 },
    us_rifle: { era: 6, unit: "US_RIFLE", h: 134 },
    us_bayonet: { era: 6, unit: "US_BAYONET", h: 134 }''',
    '''    fr_rifle: { era: 6, unit: "FR_RIFLE", h: 134, toned: true },
    fr_bayonet: { era: 6, unit: "FR_BAYONET", h: 134, toned: true },
    us_rifle: { era: 6, unit: "US_RIFLE", h: 134, toned: true },
    us_bayonet: { era: 6, unit: "US_BAYONET", h: 134, toned: true },
    // [R31] 6시대 Z4(1945 경성) 일본군 기수 장교(노란 군복 · 깃발 · 군도)
    jp_officer: { era: 6, unit: "JP_OFFICER", h: 140, toned: true }''')

# 새 병종 능력치 · 명단
rep('''color: "#e2e8f0" }
  };
  var ERA_ROSTER = {''',
    '''color: "#e2e8f0" },
    // [R31] 4시대 5대 전선 — 여진(1107 동북 9성) · 홍건적(1359 · 1361)
    JURCHEN_INF: { era: 4, name: "여진 도끼병", tactic: "pike", hp: 1.05, speed: 1.05, reach: 140, dmg: 1.05, color: "#a8a29e" },
    JURCHEN_CAV: { era: 4, name: "여진 기병", tactic: "cavalry", mounted: true, hp: 1.1, speed: 1.2, dmg: 1.2, color: "#d6d3d1" },
    REDTURBAN_INF: { era: 4, name: "홍건적 도검병", tactic: "rusher", hp: 0.95, speed: 1.25, reach: 100, dmg: 0.6, hits: 2, color: "#ef4444" },
    REDTURBAN_ELITE: { era: 4, name: "홍건적 선봉 쌍도병", tactic: "heavy", hp: 1.9, speed: 0.95, reach: 150, dmg: 1.35, color: "#b91c1c" },
    // [R31] 6시대 Z4(1945 경성) — 일본군 기수 장교: 군도 대참격 · 쓰러뜨리면 주변 병사가 동요(경직)
    JP_OFFICER: { era: 6, name: "일본군 기수 장교", tactic: "heavy", hp: 1.7, speed: 0.95, reach: 150, dmg: 1.3, color: "#facc15" }
  };
  var ERA_ROSTER = {''')
rep('''    5: { 0: ["JP_GUNNER", "SAMURAI", "SAMURAI"],''',
    '''    // [R31] 4시대 5대 전선(웨이브마다 R31_WAVE_FRONT가 병종을 고름) — 존 기본 명단은 코드 스프라이트 굽기 · 예비용
    4: { 0: ["KHITAN_INF", "KHITAN_INF", "KHITAN_INF"], 1: ["JURCHEN_INF", "JURCHEN_CAV", "JURCHEN_INF", "MONGOL_RIDER"], 2: ["WAKOU_SWORD", "REDTURBAN_INF", "REDTURBAN_ELITE"], 3: ["REDTURBAN_INF", "REDTURBAN_ELITE", "REDTURBAN_INF"] },
    5: { 0: ["JP_GUNNER", "SAMURAI", "SAMURAI"],''')
rep('''3: ["JP_BAYONET", "MG_NEST", "JP_BAYONET"] }
  };''', '''3: ["JP_BAYONET", "MG_NEST", "JP_BAYONET", "JP_OFFICER"] }
  };''')
rep('''  var MOUNTED_CAP = { 5: { 2: 3 } };''', '''  // [R31] 4시대 Z2(여진 기병 · 몽골 기마대)도 기병 돌격 간격을 엇갈리게
  var MOUNTED_CAP = { 4: { 1: 4 }, 5: { 2: 3 } };''')
rep('''  var ERA_EXTRA_UNITS = { 2: ["HAN_ELITE"] };''',
    '''  var ERA_EXTRA_UNITS = { 2: ["HAN_ELITE"], 4: ["KHITAN_INF", "JURCHEN_INF", "JURCHEN_CAV", "MONGOL_RIDER", "WAKOU_SWORD", "REDTURBAN_INF", "REDTURBAN_ELITE"], 6: ["JP_OFFICER"] };''')
# 몽골 천호장 = Z2 끝(3전선 몽골의 마무리) · 호위도 몽골 기병
rep('''    4: { key: "MB_MONGOL", name:''', '''    4: { key: "MB_MONGOL", zone: 1, escort: "MONGOL_RIDER", name:''')

# 코드 스프라이트(원화를 못 읽을 때 · 크기 기준)
rep('''    WAKOU_SWORD: { tor: ["#a8a29e", "#57534e", "#1c1917"],''',
    '''    // [R31] 여진 도끼병 · 홍건적 · 일본군 기수 장교 — 원화가 없을 때 쓰는 코드 스프라이트(여진 기병은 몽골 기병처럼 기마 스프라이트)
    JURCHEN_INF: { tor: SPEC(["#57534e", "#292524", "#0c0a09"]), leg: ["#44403c", "#1c1917", "#0c0a09"], arm: ["#78716c", "#44403c", "#1c1917"], trim: "#d6d3d1", helm: "khitan", mask: false, unitWeapon: "halberd", bulk: 1.15 },
    REDTURBAN_INF: { tor: ["#57534e", "#292524", "#0c0a09"], leg: ["#44403c", "#1c1917", "#0c0a09"], arm: SKIN, trim: "#dc2626", helm: "band", mask: false, unitWeapon: "saber" },
    REDTURBAN_ELITE: { tor: SPEC(["#3f3f46", "#18181b", "#09090b"]), leg: ["#44403c", "#1c1917", "#0c0a09"], arm: SPEC(["#3f3f46", "#18181b", "#09090b"]), trim: "#dc2626", helm: "band", mask: false, unitWeapon: "saber", wscale: 1.25, bulk: 1.3, cape: ["#7f1d1d", "#2a0a0a"] },
    JP_OFFICER: { tor: SPEC(["#c2b25a", "#7c6f2e", "#2e2a12"]), leg: ["#6b6b3a", "#3f3f24", "#1a1a0f"], arm: ["#c2b25a", "#7c6f2e", "#2e2a12"], trim: "#facc15", helm: "officer", mask: false, unitWeapon: "officerSaber", wscale: 1.15, bulk: 1.2 },
    WAKOU_SWORD: { tor: ["#a8a29e", "#57534e", "#1c1917"],''')

# ───────── 1. 상수 · 전선 · 미션 · 아이템 · 타격 이펙트 풀 ─────────
rep('''  var ACTIVE_CAP = { 2: 7 };''',
    r'''  // [R31] 4시대도 동시 7명(5대 전선 고밀도 전투 55fps 유지) — 넘치는 적은 같은 대기열로 나눠 들여보낸다
  var ACTIVE_CAP = { 2: 7, 4: 7 };
  // [R31] 2시대 해모수 '신화급 테토력' — 강타 히트스톱 +1.5프레임 · 검기 폭 ×1.4 · 강타음 가중(크게 · 낮게)
  var R31_E2_HEAVY_STOP = 1.5;
  var R31_E2_WAVE_W = 1.4;
  var R31_E2_HEAVY_SND = { v: 1.3, r: 0.9 };
  // [R31] 4시대 척준경 5대 전선 — 웨이브마다 전선(병종 · 역사 한 줄 · 선녀 해설 · 스몰 미션)
  //  Z1 거란 ×3 → Z2 여진 ×2 · 몽골(+천호장) → Z3 왜구 · 홍건적 ×2 → Z4 결전(보스 · 1362 개경 수복 해설)
  var R31_FRONTS = {
    khitan: { n: 1, roster: ["KHITAN_INF"], toast: ["1전선 · 993~1019 거란의 침입", "서북 국경 — 압록강을 건너온 거란 방패 보병을 막아라"], fairy: "📜 거란은 세 번 쳐들어왔어요. 서희는 담판으로 강동 6주를 얻었고, 1019년 강감찬이 귀주에서 크게 이겼어요(귀주 대첩)!" },
    jurchen: { n: 2, roster: ["JURCHEN_INF", "JURCHEN_INF", "JURCHEN_CAV"], toast: ["2전선 · 1107 여진 정벌 · 동북 9성", "함주 들판 — 윤관의 별무반과 함께 여진 도끼병 · 기병을 막아라"], fairy: "📜 1107년 윤관이 별무반을 이끌고 여진을 몰아낸 뒤 동북 9성을 쌓았어요. 척준경은 이 싸움에서 이름을 떨친 용장이에요!", mission: "jurchen" },
    mongol: { n: 3, roster: ["MONGOL_RIDER"], toast: ["3전선 · 1231~1259 몽골의 침입", "처인성 · 충주성 — 변발 기마대가 파도처럼 몰려온다"], fairy: "📜 몽골은 30년 가까이 쳐들어왔어요. 김윤후는 처인성에서 적장 살리타를 쓰러뜨렸고, 고려는 강화도로 도읍을 옮겨 버텼어요!", mission: "mongol" },
    wakou: { n: 4, roster: ["WAKOU_SWORD"], toast: ["4전선 · 14세기 왜구의 노략질", "남해안 포구 — 배에서 뛰어내린 왜구 칼잡이들이 마을을 노린다"], fairy: "📜 고려 말 왜구가 바닷가를 휩쓸었어요. 1380년 최무선의 화포가 진포에서, 이성계가 황산에서 왜구를 크게 무찔렀어요!", mission: "wakou" },
    redturban: { n: 5, roster: ["REDTURBAN_INF", "REDTURBAN_INF", "REDTURBAN_ELITE"], toast: ["5전선 · 1359~1361 홍건적의 침입", "개경 길목 — 붉은 두건의 대군이 도읍을 노린다"], fairy: "📜 홍건적은 두 번 쳐들어와 1361년엔 개경까지 빼앗았어요. 이듬해(1362) 고려군이 개경을 되찾았어요!", mission: "redturban" }
  };
  var R31_WAVE_FRONT = [["khitan", "khitan", "khitan"], ["jurchen", "jurchen", "mongol"], ["wakou", "redturban", "redturban"]];
  // [R31] 전선 스몰 미션(어려움) — 전선에 들어서면 상단 배너, 성공하면 징 소리 + 빛기둥 속 보상 아이템
  var R31_MISSIONS = {
    jurchen: { title: "동북 9성 사수", goal: "25초 안에 여진군 10명 격파", need: 10, time: 1500, item: "seal" },
    mongol: { title: "변발 기병 돌격 저지", goal: "패링 · 강타로 몽골 기병 5기 격파", need: 5, item: "banner" },
    wakou: { title: "왜구 소탕 연격", goal: "끊기지 않고 20콤보", need: 20, item: "elixir" },
    redturban: { title: "홍건적 선봉대 섬멸", goal: "피격 2회 이하로 돌파", need: 2, item: "blade" }
  };
  var R31_ITEMS = {
    seal: { name: "장군의 인장", eff: "12초 공격 속도 · 공격력 상승", col: "#fbbf24", dur: 720 },
    banner: { name: "삼별초 군기", eff: "8초 무적 · 오라 최대", col: "#f87171", dur: 480 },
    elixir: { name: "고려 인삼 영약", eff: "체력 60% · 각성 게이지 회복", col: "#34d399", dur: 0 },
    blade: { name: "청룡 보검", eff: "15초 모든 베기 양단 + 검기", col: "#38bdf8", dur: 900 }
  };
  var R31_SEAL_ATK = 1.3;
  // [R31] 피격 2프레임 백색 섬광(ms)
  var R31_WF_MS = 34;
  // [R31] 타격 이펙트 · 총기 · 폭탄 연출 고정 풀(128칸 고리 · 매 프레임 할당 없음)
  //  k: 1 히트스타 · 2 방향 스파크 · 3 먹 튐 · 4 충격 링 · 5 발밑 먼지 · 6 칼 베기선 · 7 도끼 파편 · 8 총 연기 고리 · 9 청백 금속 불꽃 ·
  //     10 예광탄 선 · 11 황금 탄피 · 12 총구 섬광 · 13 폭탄 화구 · 14 화약 연기 · 15 파편 불꽃 · 16 태극 광선
  var R31_HFX_N = 128;
  var R31_HFX = [];
  for (let i = 0; i < R31_HFX_N; i++) R31_HFX.push({ on: false, k: 0, x: 0, y: 0, t0: 0, dur: 1, dir: 1, a: 0, s: 1, c: "#ffffff", c2: "#ffffff", vx: 0, vy: 0, gy: 0, seed: 0, n: 0 });
  var r31HfxI = 0;
  // 종류별 누계(검증용)
  var R31_HFX_SEEN = {};
  var r31h = (v) => {
    const q = Math.sin(v * 127.1 + 311.7) * 43758.5453;
    return q - Math.floor(q);
  };
  var r31Hfx = (k, x, y, dur, o) => {
    const e = R31_HFX[r31HfxI];
    r31HfxI = (r31HfxI + 1) % R31_HFX_N;
    R31_HFX_SEEN[k] = (R31_HFX_SEEN[k] || 0) + 1;
    e.on = true;
    e.k = k;
    e.x = x;
    e.y = y;
    e.t0 = performance.now() + (o && o.delay || 0);
    e.dur = dur;
    e.dir = o && o.dir || 1;
    e.a = o && o.a || 0;
    e.s = o && o.s || 1;
    e.c = o && o.c || "#ffffff";
    e.c2 = o && o.c2 || "#fde047";
    e.vx = o && o.vx || 0;
    e.vy = o && o.vy || 0;
    e.gy = o && o.gy != null ? o.gy : y;
    e.n = o && o.n || 0;
    e.seed = Math.random() * 1000;
    return e;
  };''')

# 오라: 삼별초 군기 = 오라 최대
rep('''  function auraStageOf(g) {
    const st = g.stats || {};''', '''  function auraStageOf(g) {
    // [R31] 삼별초 군기(미션 보상) — 8초 오라 최대
    if (g.r31buff && g.r31buff.banner > 0) return 4;
    const st = g.stats || {};''')

# ───────── 2. 자원: 미션 아이템 아이콘 · 내장 목록 ─────────
rep('''    const weapons = {};
    const mobs = {};
    keys.forEach((k) => {
      const f = k.match(fxRe);''', '''    const weapons = {};
    const mobs = {};
    // [R31] 미션 보상 아이템 아이콘(assets/item/era{N}_*.webp · 256×256)
    const itemRe = new RegExp("(?:^|/)item/era" + era + "_([a-z0-9_]+)[.](?:png|webp)$");
    const items = {};
    keys.forEach((k) => {
      const it = k.match(itemRe);
      if (it) {
        items[it[1]] = k;
        return;
      }
      const f = k.match(fxRe);''')
rep('''actors: ok, mobs: mobOk, fx, weapons, horizonY: man.horizonY || 670 };''', '''actors: ok, mobs: mobOk, fx, weapons, items, horizonY: man.horizonY || 670 };''')
rep('''      const out = { era, dpr, bg: null, dawn: null, actors: {}, byKind: {}, fx: {}, mobs: {},''', '''      const out = { era, dpr, bg: null, dawn: null, actors: {}, byKind: {}, fx: {}, items: {}, mobs: {},''')
rep('''          fails.push("fx " + name + " " + e.message);
        }
      }''', '''          fails.push("fx " + name + " " + e.message);
        }
      }
      // [R31] 미션 보상 아이템 아이콘(반 크기로 굽기 — 배너 32px · 빛기둥 58px)
      for (const name of Object.keys(plan.items || {})) {
        try {
          const img = await loadImage(plan.items[name]);
          await nextFrame();
          out.items[name] = { name, img: prescale(img, 0.5 * dpr), w: img.width * 0.5, h: img.height * 0.5 };
        } catch (e) {
          fails.push("item " + name + " " + e.message);
        }
      }''')
rep('''        for (const f of Object.values(D.fx || {})) zero(f && f.img);''', '''        for (const f of Object.values(D.fx || {})) zero(f && f.img);
        for (const f of Object.values(D.items || {})) zero(f && f.img);''')
rep('''        ...bgFiles(4, "mid.webp"),''', '''        // [R31] 미술팀 정식 몹 16종(webp) · 2시대 신화 이펙트 5종 · 4시대 미션 아이템 4종
        ...[[3, "bj_guard"], [3, "bj_archer"], [3, "gg_pike"], [3, "gg_cav"], [3, "wa_raider"], [4, "wakou_sword"], [4, "jurchen_inf"], [4, "jurchen_cav"], [4, "redturban_inf"], [4, "redturban_elite"], [5, "qing_rider"], [6, "fr_rifle"], [6, "fr_bayonet"], [6, "us_rifle"], [6, "us_bayonet"], [6, "jp_officer"]].flatMap(([e, k]) => MOB_POSES.map((p) => `assets/mob/era${e}_${k}_${p}.webp`)),
        ...["tiger_claw", "bear_slam", "giant_lute_sword", "bronze_mirror_halo", "thunder_crack"].map((k) => `assets/fx/era2_fx_${k}.webp`),
        ...["seal", "banner", "elixir", "blade"].map((k) => `assets/item/era4_mission_${k}.webp`),
        ...bgFiles(4, "mid.webp"),''')

# ───────── 3. 효과음: 새 WAV 6종 · 재생 배율(볼륨 · 피치) ─────────
rep('''    const SMP = { slashLight: "slash_light", hitHeavy: "hit_heavy", breath: "breath_finisher", parryCounter: "parry_counter", relicAwaken: "relic_awaken", killcam: "killcam_slowmo" };
    const SMP_VOL = { slashLight: 0.7, hitHeavy: 0.75, breath: 0.75, parryCounter: 0.8, relicAwaken: 0.8, killcam: 0.8 };
    const SMP_MAXV = { slashLight: 3, hitHeavy: 3, breath: 2, parryCounter: 2, relicAwaken: 1, killcam: 1 };
    const SMP_JIT = { slashLight: 0.05, hitHeavy: 0.05, breath: 0.03, parryCounter: 0.02 };''',
    '''    // [R31] 미술팀 WAV 6종 추가(22050Hz · 16bit · 모노): 일반 1~3타 slice_crisp_1/2 번갈아(피치 ±6%) · 양단 slice_flesh_sever ·
    //  연참 · 일섬 slice_flurry_multi · 미션 성공 mission_clear_gong · 의열단 폭탄 bomb_uiyeol_blast
    const SMP = { slashLight: "slash_light", hitHeavy: "hit_heavy", breath: "breath_finisher", parryCounter: "parry_counter", relicAwaken: "relic_awaken", killcam: "killcam_slowmo", sliceCrisp1: "slice_crisp_1", sliceCrisp2: "slice_crisp_2", sliceSever: "slice_flesh_sever", sliceFlurry: "slice_flurry_multi", missionGong: "mission_clear_gong", bombBlast: "bomb_uiyeol_blast" };
    const SMP_VOL = { slashLight: 0.7, hitHeavy: 0.75, breath: 0.75, parryCounter: 0.8, relicAwaken: 0.8, killcam: 0.8, sliceCrisp1: 0.7, sliceCrisp2: 0.7, sliceSever: 0.8, sliceFlurry: 0.75, missionGong: 0.85, bombBlast: 0.85 };
    const SMP_MAXV = { slashLight: 3, hitHeavy: 3, breath: 2, parryCounter: 2, relicAwaken: 1, killcam: 1, sliceCrisp1: 3, sliceCrisp2: 3, sliceSever: 2, sliceFlurry: 1, missionGong: 1, bombBlast: 2 };
    const SMP_JIT = { slashLight: 0.05, hitHeavy: 0.05, breath: 0.03, parryCounter: 0.02, sliceCrisp1: 0.06, sliceCrisp2: 0.06, sliceSever: 0.04, bombBlast: 0.04 };''')
rep('''    const SMP_FALLBACK = { slashLight: "hit", hitHeavy: "crit", breath: "", parryCounter: "counter", relicAwaken: "ult", killcam: "" };''',
    '''    const SMP_FALLBACK = { slashLight: "hit", hitHeavy: "crit", breath: "", parryCounter: "counter", relicAwaken: "ult", killcam: "", sliceCrisp1: "hit", sliceCrisp2: "hit", sliceSever: "crit", sliceFlurry: "hit", missionGong: "levelup", bombBlast: "explosion" };''')
rep('''    const playSample = (name) => {''', '''    // [R31] o = { v: 볼륨 배율, r: 피치(재생 속도) 배율 } — 2시대 강타음 가중 등
    const playSample = (name, o) => {''')
rep('''      if (j) src.playbackRate.value = 1 + (Math.random() * 2 - 1) * j;
      const gn = ac.createGain();
      gn.gain.value = SMP_VOL[name] || 0.7;''', '''      const r0 = o && o.r || 1;
      if (j || r0 !== 1) src.playbackRate.value = r0 * (1 + (Math.random() * 2 - 1) * j);
      const gn = ac.createGain();
      gn.gain.value = (SMP_VOL[name] || 0.7) * (o && o.v || 1);''')
rep('''      play(name) {
        if (muted || !ensure()) return;''', '''      play(name, o) {
        if (muted || !ensure()) return;''')
rep('''            if (playSample(name)) return;''', '''            if (playSample(name, o)) return;''')
rep('''    const sfx = (name) => sfxRef.current && sfxRef.current.play(name);''', '''    const sfx = (name, o) => sfxRef.current && sfxRef.current.play(name, o);''')

# ───────── 4. 컴포넌트 도우미: 원화 이펙트 · 타격 이펙트 · 전선 · 미션 · 보상 · 김원봉 ─────────
rep('''    // Lv.5 공중 도약 급강하 파동격 — ''', r'''    // ───────── [R31] 해모수 신화 이펙트 · 타격 이펙트 5종 · 4시대 5대 전선 · 미션 · 6시대 김원봉 ─────────
    // 원화 이펙트(2시대 fx 5종) — k: claw 호랑이 발톱 · bear 곰 내려찍기 · thunder 천둥 · sword 하늘에서 꽂히는 거대 비파형 동검
    const pushArtFx = (name, x, y, o = {}) => {
      const g = gameRef.current;
      const L = g.artFx || (g.artFx = []);
      if (L.length > 10) L.splice(0, L.length - 10);
      L.push({ n: name, x, y, t0: performance.now() + (o.delay || 0), dur: o.dur || 500, dir: o.dir || 1, s: o.s || 1, k: o.k || "claw" });
      g.artFxCount = (g.artFxCount || 0) + 1;
    };
    // 2시대 3타 — 호랑이 발톱 강타(heavy_cleave 자세 + fx_tiger_claw)
    const r31Cleave = () => {
      const g = gameRef.current;
      const p = g.player;
      const x = p.x + p.facing * 118;
      pushArtFx("fx_tiger_claw", x, p.z - p.y - 62, { k: "claw", dur: 430, dir: p.facing });
      r31Hfx(4, x, p.z - 4, 320, { c: "#facc15", s: 1.3 });
      addTrauma(0.16);
      kickDirShake(g, p.facing, 6);
      g.e2Cleaves = (g.e2Cleaves || 0) + 1;
    };
    // 2시대 4타 · 급강하 착지 — 곰의 내려찍기(slam_hit 자세 + fx_bear_slam + fx_thunder_crack)
    const r31Slam = (x, z, big) => {
      const g = gameRef.current;
      pushArtFx("fx_bear_slam", x, z + 6, { k: "bear", dur: big ? 760 : 640, s: big ? 1.12 : 1 });
      pushArtFx("fx_thunder_crack", x, z + 8, { k: "thunder", dur: 540, s: big ? 1.1 : 0.95, delay: 30 });
      r31Hfx(4, x, z, 440, { c: "#facc15", s: big ? 2.5 : 2.1 });
      r31Hfx(4, x, z, 320, { c: "#ffffff", s: big ? 1.6 : 1.3, delay: 40 });
      r31Hfx(15, x, z - 20, 520, { n: 14, s: 0.9, c: "#fde047" });
      addGroundCraterDecal(x, z, big ? 112 : 92);
      spawnDust(x, z, 8, 4.2);
      // 4타마다 나오는 연출이라 전체 화면 섬광 없이(빛 반경도 작게) — 곰 · 천둥 원화와 링이 손맛을 맡는다
      addLight(x, z, 40, 110, "#facc15", 1, 12);
      addTrauma(big ? 0.55 : 0.45);
      g.e2Slams = (g.e2Slams || 0) + 1;
    };
    // 2시대 일섬 · 각성 — 하늘 소환(summon_sky 자세) + 몸 뒤에서 도는 청동 거울 광륜
    const r31Summon = (ult) => {
      const g = gameRef.current;
      const p = g.player;
      p._r31pose = { name: "summon_sky", until: g.tick + (ult ? 56 : 14) };
      g.r31halo = { t0: performance.now(), dur: ult ? 3400 : 2300, s: ult ? 1.4 : 1 };
      g.e2Summons = (g.e2Summons || 0) + 1;
    };
    // 하늘에서 거대 비파형 동검이 수직으로 꽂힌다(낙하 약 0.27초) → 천둥 · 곰 · 충격 링
    const r31SkySword = (x, z, delay, big) => {
      pushArtFx("fx_giant_lute_sword", x, z + 4, { k: "sword", dur: 900, s: big ? 1.12 : 1, delay });
      pushArtFx("fx_thunder_crack", x, z + 8, { k: "thunder", dur: 560, s: big ? 1.2 : 1.05, delay: delay + 250 });
      pushArtFx("fx_bear_slam", x, z + 6, { k: "bear", dur: 640, s: big ? 1.05 : 0.92, delay: delay + 260 });
      addTimer(Math.max(1, Math.round((delay + 260) / 16.7)), () => {
        const g = gameRef.current;
        r31Hfx(4, x, z, 470, { c: "#facc15", s: 2.7 });
        r31Hfx(15, x, z - 30, 560, { n: 18, s: 1.1, c: "#fde047" });
        addGroundCraterDecal(x, z, 124);
        addLight(x, z, 60, 220, "#fde047", 1, 18);
        addTrauma(0.5);
        g.flashAlpha = Math.max(g.flashAlpha, 0.42);
        g.flashColor = "#fff7cc";
        sfx("hitHeavy", R31_E2_HEAVY_SND);
        g.e2SkySwords = (g.e2SkySwords || 0) + 1;
      });
    };
    // 타격 이펙트 5종 — ① 히트스타 ② 방향 스파크(강타 ×2) ③ 먹 튐 + 충격 링(강타 · 피니시) ④ 2프레임 백색 섬광 + 넉백 발밑 먼지 ⑤ 무기 · 적 종류별
    const r31HitBurst = (g, en, dir, hv, fin, vr) => {
      if (g.tick === g._hbTick) {
        if (++g._hbN > 4) return;
      } else {
        g._hbTick = g.tick;
        g._hbN = 0;
      }
      const C = R30C(g);
      const big = en === g.boss || en.isMidBoss;
      const x = en.x - dir * 8;
      const y = en.z - (en.y || 0) - (big ? 92 : 56);
      g.hitFxN = (g.hitFxN || 0) + 1;
      r31Hfx(1, x, y, hv ? 170 : 120, { s: (fin ? 1.35 : hv ? 1.15 : 1) * (big ? 1.15 : 1), c: C[2], c2: C[0], a: Math.random() * 6.28 });
      // 붐비는 장면(이펙트 칸 40↑ · 저해상도 파티클 120↑ · 피해 숫자 24↑)에서는 히트스타 · 스파크만 — 이미 폭발 · 숫자로 가득한 순간이라 덜 보이고, 그 순간의 프레임을 지킨다
      const busy = (g.hfxLive || 0) > 40 || g.particles.length > 120 || g.damagePopups.length > 24;
      if (busy) g.hfxBusy = (g.hfxBusy || 0) + 1;
      r31Hfx(2, x, y, hv ? 240 : 180, { dir, n: busy ? 4 : hv ? 12 : 6, s: hv ? 1.3 : 1, c: C[0], a: g._cutAng != null ? g._cutAng : 0 });
      en._wf = performance.now();
      if (fin) r31Hfx(4, en.x, en.z - 2, 300, { c: C[0], s: 1.3 });
      if (busy) return;
      if (hv) r31Hfx(3, x, y, 440, { dir, s: fin ? 1.3 : 1 });
      if (!(en.y > 10)) r31Hfx(5, en.x - dir * 6, en.z, 420, { dir, s: hv ? 1.3 : 1 });
      if (vr === "gun") r31Hfx(8, x, y, 520, { dir });
      else if (vr === "axe") r31Hfx(7, x, y, 520, { dir, n: hv ? 9 : 6 });
      else if (vr === "metal") r31Hfx(9, x, y, 320, { dir, n: hv ? 10 : 7 });
      else r31Hfx(6, x, y, 220, { dir, a: (g._cutAng != null ? g._cutAng : 0.4) + rand(-0.15, 0.15), s: hv ? 1.25 : 1, c: C[0] });
    };
    // 4시대 5대 전선 — 전선 병종(웨이브 단위) · 전선 진입(역사 한 줄 토스트 + 선녀 해설 + 미션 배너)
    const r31FrontUnit = (g) => {
      const F = R31_FRONTS[g.front4];
      if (!F) return void 0;
      g.frontIdx = (g.frontIdx || 0) + 1;
      return F.roster[g.frontIdx % F.roster.length];
    };
    const r31EnterFront = (key) => {
      const g = gameRef.current;
      const F = R31_FRONTS[key];
      if (!F || g.front4 === key) return;
      if (g.front4) r31FrontEnd(g, g.front4);
      g.front4 = key;
      g.frontIdx = 0;
      (g.frontLog || (g.frontLog = [])).push({ key, zone: g.zoneIdx, tick: g.tick });
      setStageToast({ era: 4, fieldName: F.toast[0], name: eraObjOf().name, detail: F.toast[1] });
      setTimeout(() => setStageToast((t) => t && t.fieldName === F.toast[0] ? null : t), 2800);
      addTimer(70, () => setCompanionBubble(F.fairy, 210));
      if (F.mission && !(g.missionDone || {})[F.mission]) r31StartMission(F.mission);
    };
    const r31StartMission = (key) => {
      const g = gameRef.current;
      if (!R31_MISSIONS[key]) return;
      const c = g.stats.combo || 0;
      g.mission = { key, t0: g.tick, prog: 0, hits: 0, state: "run", tEnd: 0, base: c, last: c };
      (g.missionLog || (g.missionLog = [])).push({ key, ev: "start", tick: g.tick });
    };
    const r31MissionEnd = (g, ok) => {
      const M = g.mission;
      if (!M || M.state !== "run") return;
      M.state = ok ? "ok" : "fail";
      M.tEnd = g.tick;
      (g.missionDone || (g.missionDone = {}))[M.key] = M.state;
      (g.missionLog || (g.missionLog = [])).push({ key: M.key, ev: M.state, tick: g.tick, prog: M.prog, hits: M.hits });
      const D = R31_MISSIONS[M.key];
      const p = g.player;
      if (ok) {
        sfx("missionGong");
        addDamagePopup(p.x, p.z, p.y + 150, "MISSION CLEAR!", true, D.title, 0, "#fde047");
        r31GiveItem(D.item);
      } else {
        sfx("bad");
        addDamagePopup(p.x, p.z, p.y + 130, "MISSION FAILED", false, D.title, 0, "#94a3b8");
        addTimer(40, () => setCompanionBubble("😢 임무는 놓쳤지만 전선은 계속돼요! 다음 전선에서 만회해요!", 120));
      }
    };
    // 전선이 끝날 때(다음 전선 · 구역 정리) — 여진 · 몽골 · 왜구는 그때까지 못 이루면 실패, 홍건적은 피격 2회 이하면 성공
    const r31FrontEnd = (g, key) => {
      const M = g.mission;
      if (!M || M.state !== "run" || M.key !== key) return;
      r31MissionEnd(g, M.key === "redturban" && M.hits <= R31_MISSIONS.redturban.need);
    };
    const r31MissionTick = (g) => {
      const M = g.mission;
      if (!M || M.state !== "run") return;
      const D = R31_MISSIONS[M.key];
      if (M.key === "jurchen" && g.tick - M.t0 > D.time) r31MissionEnd(g, false);
      else if (M.key === "wakou") {
        const c = g.stats.combo || 0;
        if (c < M.last) M.base = 0;
        M.last = c;
        M.prog = c - M.base;
        if (M.prog >= D.need) r31MissionEnd(g, true);
      }
    };
    const r31OnKill = (g, en, heavy) => {
      if (en.unit === "JP_OFFICER") r31OfficerDown(g, en);
      const M = g.mission;
      if (!M || M.state !== "run") return;
      if (M.key === "jurchen" && (en.unit === "JURCHEN_INF" || en.unit === "JURCHEN_CAV")) M.prog++;
      else if (M.key === "mongol" && en.unit === "MONGOL_RIDER" && heavy) {
        M.prog++;
        addDamagePopup(en.x, en.z, en.y + 76, "STOP!", true, `${M.prog}/${R31_MISSIONS.mongol.need}`, 0, "#fbbf24");
      } else return;
      if (M.prog >= R31_MISSIONS[M.key].need) r31MissionEnd(g, true);
    };
    // 미션 보상 — 빛기둥 속 아이템 + 효과(인장 공속 · 공격력 / 군기 무적 · 오라 최대 / 영약 체력 · 각성 / 보검 양단 + 검기)
    const r31GiveItem = (id) => {
      const g = gameRef.current;
      const I = R31_ITEMS[id];
      if (!I) return;
      const p = g.player;
      const st = g.stats;
      const B = g.r31buff || (g.r31buff = {});
      g.r31pick = { id, t0: performance.now() };
      (g.itemLog || (g.itemLog = [])).push({ id, tick: g.tick });
      if (id === "seal") B.seal = I.dur;
      else if (id === "banner") {
        B.banner = I.dur;
        p.invincibleTimer = Math.max(p.invincibleTimer || 0, I.dur);
        g.auraBurst = performance.now();
      } else if (id === "elixir") {
        st.hp = Math.min(st.maxHp, st.hp + Math.round(st.maxHp * 0.6));
        st.ult = 100;
      } else if (id === "blade") B.blade = I.dur;
      g.flashAlpha = Math.max(g.flashAlpha, 0.35);
      g.flashColor = I.col;
      addShock(p.x, p.z, I.col, 170, 20);
      addLight(p.x, p.z, 80, 160, I.col, 1, 24);
      addTimer(20, () => setPlayerBubble(`🎁 [${I.name}] 획득! ${I.eff}`, 150));
    };
    // 6시대 약산 김원봉 — 의열단 폭탄(던지기 · 착지 폭발) · 모젤 C96(총구 섬광 · 관통 예광탄 · 황금 탄피) · 일본군 기수 장교
    const r31ThrowBomb = (power = 1) => {
      const g = gameRef.current;
      const p = g.player;
      g.throwables.push({ x: p.x + p.facing * 26, z: p.z, y: p.y + 70, vx: p.facing * 8.5, vy: 7.5, rot: 0, vr: p.facing * 0.3, era: 6, kind: "uiyeol", power });
      g.uiyeolThrows = (g.uiyeolThrows || 0) + 1;
      sfx("throw");
    };
    const r31UiyeolBlast = (x, z, y, power = 1, o = {}) => {
      const g = gameRef.current;
      const R = 165 * power;
      const SC = g._slashCtx = { ang: 0.5, blade: true, kills: 0, n: 0 };
      let hits = 0;
      for (let i = 0; i < g.enemies.length; i++) {
        const en = g.enemies[i];
        if (en.state === "DYING" || en.state === "SPAWN") continue;
        if (Math.abs(en.x - x) > R || Math.abs(en.z - z) > 76) continue;
        SC.ang = 0.3 + Math.random() * 0.5;
        applyDamageToEnemy(en, (o.special ? 1.6 : 2.4) * power, 13, 10.5, 2, true, en.x >= x ? 1 : -1);
        hits++;
      }
      if (g.bossActive && g.boss && !g.boss.dying && Math.abs(g.boss.x - x) < R + 50 && Math.abs(g.boss.z - z) < 84) {
        applyDamageToEnemy(g.boss, 1.9 * power, 3, 3, 2, true, g.boss.x >= x ? 1 : -1);
        hits++;
      }
      g._slashCtx = null;
      for (let i = g.crates.length - 1; i >= 0; i--) {
        if (Math.abs(g.crates[i].x - x) < R * 0.85 && Math.abs(g.crates[i].z - z) < 70) breakCrate(g.crates[i]);
      }
      const yy = z - Math.max(20, y);
      r31Hfx(13, x, yy, 560, { s: power });
      for (let k = 0; k < 4; k++) r31Hfx(14, x + rand(-34, 34), yy + rand(-16, 10), 1100 + k * 130, { s: power * (0.9 + k * 0.15), vx: rand(-24, 24), delay: 50 + k * 50 });
      r31Hfx(15, x, yy, 560, { n: 18, s: power, c: "#fdba74" });
      r31Hfx(4, x, z, 480, { c: "#fb923c", s: 2.3 * power });
      r31Hfx(4, x, z, 340, { c: "#ffffff", s: 1.5 * power, delay: 50 });
      explode(x, z, Math.max(20, y), 1.2 * power, "#fb923c");
      addGroundCraterDecal(x, z, 80 * power);
      addLight(x, z, 40, 200 * power, "#fb923c", 1, 16);
      addTrauma(0.36 * power);
      kickDirShake(g, g.player.facing, 7);
      g.hitStop = Math.max(g.hitStop, hits ? 5 : 3);
      if (g.tick !== g._bombSndT) {
        g._bombSndT = g.tick;
        sfx("bombBlast");
      }
      g.uiyeolBlasts = (g.uiyeolBlasts || 0) + 1;
      if (hits && !o.special) addDamagePopup(x, z, 86, "UIYEOL!", true, SC.kills ? `${SC.kills} KILL` : `${hits} HIT`, 0, "#fb923c");
      return hits;
    };
    const r31Mauser = (x, z, y, dir, slope) => {
      const yy = z - y;
      r31Hfx(12, x, yy, 95, { dir });
      r31Hfx(10, x, yy, 160, { dir, n: 560, vx: dir, vy: slope || 0 });
      r31Hfx(11, x - dir * 24, yy - 4, 950, { vx: -dir * rand(70, 130), vy: rand(230, 310), gy: z - 2 });
      const g = gameRef.current;
      g.mauserShots = (g.mauserShots || 0) + 1;
    };
    // 공중 3타 = 모젤 C96 2연사(비스듬히 아래로 · 관통 2명)
    const r31AirMauser = () => {
      const g = gameRef.current;
      const eObj = relicPal(g, eraObjOf());
      sfx("shot");
      g.airMauser = (g.airMauser || 0) + 1;
      [0, 4].forEach((d) => addTimer(d, () => {
        const g2 = gameRef.current;
        const pp = g2.player;
        const h = pp.y + 56;
        const vy = -Math.max(1.5, h / 20);
        g2.projectiles.push({ x: pp.x + pp.facing * 60, z: pp.z, y: h, vx: pp.facing * 26, vy, facing: pp.facing, eraNum: 6, color1: eObj.trailMid, color2: eObj.trailOuter, size: 28, dmgRatio: 0.85, hitCount: 1, life: 30, gun: true, bullet: true, hitIds: [], pierce: 2 });
        r31Mauser(pp.x + pp.facing * 60, pp.z, h, pp.facing, vy / 26);
      }));
    };
    const r31SpawnOfficer = (x, z, flank) => {
      const g = gameRef.current;
      spawnEnemyAt(x, z, { circle: true, flank, unit: "JP_OFFICER" });
      g.officerSpawns = (g.officerSpawns || 0) + 1;
      if (!g._officerIntro) {
        g._officerIntro = true;
        setCompanionBubble("⚠️ 일본군 기수 장교! 깃발을 든 장교를 먼저 쓰러뜨리면 주변 병사들이 동요해요!", 150);
      }
    };
    const r31OfficerDown = (g, en) => {
      g.officerDowns = (g.officerDowns || 0) + 1;
      addDamagePopup(en.x, en.z, en.y + 120, "FLAG DOWN!", true, "적 동요", 0, "#facc15");
      for (let i = 0; i < g.enemies.length; i++) {
        const e2 = g.enemies[i];
        if (e2 === en || e2.state === "DYING" || e2.isMidBoss) continue;
        if (Math.abs(e2.x - en.x) < 320) {
          e2.hitStun = Math.max(e2.hitStun || 0, 50);
          e2.windupTimer = 0;
          e2.shake = 6;
        }
      }
      addShock(en.x, en.z, "#facc15", 160, 18);
      if (!g._officerTip) {
        g._officerTip = true;
        addTimer(30, () => setCompanionBubble("🚩 기수 장교가 쓰러지자 일본군이 흔들려요! 지금이에요!", 130));
      }
    };
    // Lv.5 공중 도약 급강하 파동격 — ''')

# ───────── 5. 피해 · 효과음 · 처치 판정 · 히트스톱 ─────────
rep('''* (g.legend ? LEGEND_ATK : 1) * (target === g.boss && target.fortress ? 1 - BUDDHA_DR : 1)''',
    '''* (g.legend ? LEGEND_ATK : 1) * (g.r31buff && g.r31buff.seal > 0 ? R31_SEAL_ATK : 1) * (target === g.boss && target.fortress ? 1 - BUDDHA_DR : 1)''')
rep('''        if (SC.blade) {
          target._cut = { a: SC.ang + rand(-0.14, 0.14), dir, h: 0.44 + Math.random() * 0.16 };
          g.cutKills = (g.cutKills || 0) + 1;
        }''', '''        // [R31] 청룡 보검(미션 보상) 동안은 무기와 상관없이 막타가 모두 양단
        if (SC.blade || g.r31buff && g.r31buff.blade > 0) {
          target._cut = { a: SC.ang + rand(-0.14, 0.14), dir, h: 0.44 + Math.random() * 0.16 };
          g.cutKills = (g.cutKills || 0) + 1;
          // [R31] 양단음(slice_flesh_sever) — 한 틱에 한 번
          if (g.tick !== g._sevT) {
            g._sevT = g.tick;
            sfx("sliceSever");
          }
        }''')
rep('''      if (g.sfxHitGate <= 0) {
        sfx(isCounter ? "counter" : target === g.boss || g._comboStep >= 3 ? "hitHeavy" : g._comboStep >= 1 ? "slashLight" : dealtCrit ? "crit" : "hit");
        g.sfxHitGate = 2;
      }''', '''      // [R31] 타격 이펙트 5종(HD 고정 풀) — 무기 · 적 종류: 총(모젤 · 신기전) 연기 고리 · 갑주 · 방패 · 기병 · 패링 청백 금속 불꽃 · 도끼 파편 · 칼 베기선
      {
        const vr = g._r31gun ? "gun" : isCounter || g._r31par || target.guardRate > 0 || heavy || target === g.boss ? "metal" : heroWeaponClass(g.era, st.weaponTier || 1) === "AXE" ? "axe" : "sword";
        const fin = forceCrit && hitCount >= 2 || g._comboStep >= 4;
        r31HitBurst(g, target, dir, fin || forceCrit || hitCount > 1 || g._comboStep >= 3 || target === g.boss, fin, vr);
      }
      if (g.sfxHitGate <= 0) {
        // [R31] 일반 1~3타 = slice_crisp_1/2 번갈아(피치 ±6%) · 4타 · 보스 = 강타음 / 2시대는 3타부터 강타음(크게 · 낮게 가중)
        const e2 = g.era === 2;
        if (isCounter) sfx("counter");
        else if (target === g.boss || g._comboStep >= (e2 ? 3 : 4)) sfx("hitHeavy", e2 ? R31_E2_HEAVY_SND : null);
        else if (g._comboStep >= 1) sfx((g._r31alt = !g._r31alt) ? "sliceCrisp1" : "sliceCrisp2");
        else sfx(dealtCrit ? "crit" : "hit");
        g.sfxHitGate = 2;
      }
      // [R31] 처치 판정(미션 · 기수 장교) — 패링 · 강타 막타 여부
      if (target.hp <= 0 && !target._r31k && target !== g.boss) {
        target._r31k = 1;
        r31OnKill(g, target, isCounter || !!g._r31par || forceCrit || hitCount >= 2 || g._comboStep >= 3);
      }''')
rep('''        g.hitStop = Math.max(g.hitStop, finHit ? HITSTOP_FIN : heavyHit ? HITSTOP_HEAVY : HITSTOP_LIGHT, SC.kills ? HITSTOP_KILL : 0);''',
    '''        // [R31] 2시대 강타 히트스톱 +1.5프레임
        g.hitStop = Math.max(g.hitStop, (finHit ? HITSTOP_FIN : heavyHit ? HITSTOP_HEAVY : HITSTOP_LIGHT) + (g.era === 2 && heavyHit ? R31_E2_HEAVY_STOP : 0), SC.kills ? HITSTOP_KILL : 0);''')
rep('''        g.hitStop = Math.max(g.hitStop, forceCrit && hitCount >= 2 ? HITSTOP_FIN : HITSTOP_HEAVY, SC.kills ? HITSTOP_KILL : 0);''',
    '''        g.hitStop = Math.max(g.hitStop, (forceCrit && hitCount >= 2 ? HITSTOP_FIN : HITSTOP_HEAVY) + (g.era === 2 ? R31_E2_HEAVY_STOP : 0), SC.kills ? HITSTOP_KILL : 0);''')
rep('''      g.hitStop = Math.max(g.hitStop, hits ? HITSTOP_FIN : 3);''', '''      g.hitStop = Math.max(g.hitStop, hits ? HITSTOP_FIN + (g.era === 2 ? R31_E2_HEAVY_STOP : 0) : 3);''')
rep('''        checkMeleeHitbox(430, 70, 1.8, 11, 0, 2, true);''', '''        gg._r31par = true;
        checkMeleeHitbox(430, 70, 1.8, 11, 0, 2, true);
        gg._r31par = false;''')
rep('''      const dmg = Math.round(dmgBase * PLAYER_DMG_TAKEN);
      g.stats.hp = Math.max(0, g.stats.hp - dmg);''', '''      const dmg = Math.round(dmgBase * PLAYER_DMG_TAKEN);
      g.stats.hp = Math.max(0, g.stats.hp - dmg);
      // [R31] 홍건적 미션: 피격 수(3번째 피격에서 실패)
      const M31 = g.mission;
      if (M31 && M31.state === "run" && M31.key === "redturban") {
        M31.hits++;
        if (M31.hits > R31_MISSIONS.redturban.need) r31MissionEnd(g, false);
      }''')

# ───────── 6. 콤보 · 연참 · 급강하 · 일섬 · 각성 연결 ─────────
c0 = s.count('p._spinAtk = false;')
if c0 < 5:
    raise SystemExit(f"spinAtk reset count {c0}")
s = s.replace('p._spinAtk = false;', 'p._spinAtk = p._r31slam = false;')
n += 1
rep('''      p._spinAtk = step === 4 && g.stats.level >= SKILL_LV.finisher;''', '''      p._spinAtk = step === 4 && g.stats.level >= SKILL_LV.finisher && g.era !== 2;
      // [R31] 2시대 해모수: 3타 = 호랑이 발톱 강타(heavy_cleave) · Lv.3+ 4타 = 곰의 내려찍기(slam_prep → slam_hit)
      p._r31slam = step === 4 && g.stats.level >= SKILL_LV.finisher && g.era === 2;''')
rep('''      const T = gun ? { dur: 18, hit: 4 } : cls === "AXE" ? { dur: step === 4 ? 24 : 20, hit: step === 4 ? 9 : 8 } : cls === "SPEAR" ? { dur: step === 4 ? 18 : 13, hit: 3 } : { dur: step === 4 ? 20 : 15, hit: step === 4 ? 6 : 4 };''',
    '''      const T = gun ? { dur: 18, hit: 4 } : cls === "AXE" ? { dur: step === 4 ? 24 : 20, hit: step === 4 ? 9 : 8 } : cls === "SPEAR" ? { dur: step === 4 ? 18 : 13, hit: 3 } : { dur: step === 4 ? 20 : 15, hit: step === 4 ? 6 : 4 };
      // [R31] 2시대 3 · 4타는 더 무겁게 — 내려찍기는 들어 올리는 선딜(slam_prep)을 길게, 맞는 순간 slam_hit
      if (g.era === 2 && !gun && step >= 3) {
        T.dur += step === 4 ? 6 : 3;
        T.hit += step === 4 ? 3 : 1;
      }''')
rep('''      if (p._spinAtk) p.vx = p.facing * 3;''', '''      if (p._spinAtk) p.vx = p.facing * 3;
      if (p._r31slam) p.vx = p.facing * 2;''')
rep('''              hitCount: 1,
              life: 40
            });
          });
          if (g.era === 4) shot(0, 0, 70, 1.9);''', '''              hitCount: 1,
              life: 40,
              // [R31] 화기 탄(총 연기 고리 타격) · 6시대 모젤 C96 = 관통 2명 + 총구 섬광 · 예광탄 · 황금 탄피
              gun: true,
              bullet: g.era === 6,
              hitIds: g.era === 6 ? [] : void 0,
              pierce: g.era === 6 ? 2 : void 0
            });
            if (g.era === 6) r31Mauser(pp.x + pp.facing * 72, pp.z + dz, pp.y + 62, pp.facing, 0);
          });
          if (g.era === 4) shot(0, 0, 70, 1.9);''')
rep('''        const beam = cls === "SWORD" && (g.era <= 4 && step >= 3 || g.era >= 5 && isFinisher);''',
    '''        // [R31] 청룡 보검(미션 보상) 동안은 모든 베기에서 검기
        const beam = cls === "SWORD" && (g.era <= 4 && step >= 3 || g.era >= 5 && isFinisher) || !!(g.r31buff && g.r31buff.blade > 0);''')
rep('''            size: isFinisher ? 64 : 44,''', '''            size: (isFinisher ? 64 : 44) * (g.era === 2 ? R31_E2_WAVE_W : 1),
            wz: g.era === 2 ? R31_E2_WAVE_W : 1,
            r31b: !!(g.r31buff && g.r31buff.blade > 0),''')
rep('''        const spin = isFinisher && g.stats.level >= SKILL_LV.finisher;
        g._cutAng = isFinisher ? spin ? 0.06 : 0.82 : step === 3 ? 1.22 : step === 2 ? -0.14 : 0.1;
        g._cutCross = isFinisher && !spin;''', '''        // [R31] 2시대는 회전참 대신 곰의 내려찍기(slam) — 둘레 충격 + 곰 · 천둥 원화 이펙트
        const spin = isFinisher && g.stats.level >= SKILL_LV.finisher && g.era !== 2;
        const slam = isFinisher && g.stats.level >= SKILL_LV.finisher && g.era === 2;
        g._cutAng = isFinisher ? spin ? 0.06 : slam ? 1.3 : 0.82 : step === 3 ? 1.22 : step === 2 ? -0.14 : 0.1;
        g._cutCross = isFinisher && !spin && !slam;''')
rep('''        if (spin) {
          for (let i = 0; i < 3; i++) p.ghosts.push(''', '''        if (slam) {
          hitAny = areaSlash(220, 84, 1.45 + step * 0.3, 15, 13.5, 2, true).hits > 0;
          r31Slam(p.x + p.facing * 64, p.z, false);
        } else if (spin) {
          for (let i = 0; i < 3; i++) p.ghosts.push(''')
rep('''        else hitAny = checkMeleeHitbox(175, 62, 1 + step * 0.3, isFinisher ? 14 : 5, isFinisher ? 12.5 : step === 2 ? 6 : 0, isFinisher ? 2 : 1, isFinisher);''',
    '''        else {
          // [R31] 2시대 3타 = 호랑이 발톱 강타 — 사거리 · 피해 ↑ · 짧게 띄움
          const e2h = g.era === 2 && step === 3;
          hitAny = checkMeleeHitbox(e2h ? 195 : 175, 62, (1 + step * 0.3) * (e2h ? 1.15 : 1), isFinisher ? 14 : e2h ? 9 : 5, isFinisher ? 12.5 : step === 2 ? 6 : e2h ? 4 : 0, isFinisher ? 2 : 1, isFinisher);
        }''')
rep('''        if (step === 3) chopImpact();''', '''        if (step === 3) {
          chopImpact();
          if (g.era === 2) r31Cleave();
        }''')
rep('''        if (isFinisher && hitAny && g.stats.combo >= R30_SPECIAL_COMBO) startSpecial("combo");''', '''        if (isFinisher && hitAny && g.stats.combo >= R30_SPECIAL_COMBO) startSpecial("combo");
        // [R31] 6시대 4타 피니시 = 의열단 폭탄 투척
        if (isFinisher && g.era === 6) addTimer(2, () => r31ThrowBomb(1));''')
rep('''          if (g2.stats.level >= SKILL_LV.upper && ah >= 2) launchCrossWave(pp.facing, pp.y + 50, 46, 0.75);
        });
        return;''', '''          if (g2.stats.level >= SKILL_LV.upper && ah >= 2) launchCrossWave(pp.facing, pp.y + 50, 46, 0.75);
        });
        // [R31] 6시대 공중 3타 = 모젤 C96 2연사
        if (g.era === 6 && ah === 3) addTimer(4, () => r31AirMauser());
        return;''')
rep('''color1: C[0], color2: C[1], size, dmgRatio: ratio,''', '''color1: C[0], color2: C[1], size: size * (g.era === 2 ? R31_E2_WAVE_W : 1), wz: g.era === 2 ? R31_E2_WAVE_W : 1, dmgRatio: ratio,''')
rep('''        p.ghosts.push({ x: p.x + p.facing * i * (evo ? 30 : 25), z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i % 6, alpha: 0.85 - i * (evo ? 0.06 : 0.14), evo, col: eObj.bladeGlow });''',
    '''        // [R31] 6시대 = 야습 그림자 잔상(어두운 실루엣)
        p.ghosts.push({ x: p.x + p.facing * i * (evo ? 30 : 25), z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i % 6, alpha: 0.85 - i * (evo ? 0.06 : 0.14), evo: evo && g.era !== 6, col: eObj.bladeGlow, shadow: g.era === 6, name: g.era === 6 ? ["run", "run3", "run5", "run7"][i % 4] : void 0 });''')
rep('''      if (g.rushes <= 3) addDamagePopup(p.x, p.z, p.y + 118, "5-HIT RUSH!", true, null, 0, "#f472b6");''', '''      if (g.rushes <= 3) addDamagePopup(p.x, p.z, p.y + 118, "5-HIT RUSH!", true, null, 0, "#f472b6");
      sfx("sliceFlurry");''')
rep('''        for (let i = 0; i < 6; i++) p.ghosts.push({ x: p.x - p.facing * i * 26, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i % 6, name: "run", alpha: 0.72 - i * 0.1 });''',
    '''        for (let i = 0; i < 6; i++) p.ghosts.push({ x: p.x - p.facing * i * 26, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i % 6, name: "run", alpha: 0.72 - i * 0.1, shadow: g.era === 6 });''')
rep('''          g2.rushFinishes = (g2.rushFinishes || 0) + 1;''', '''          g2.rushFinishes = (g2.rushFinishes || 0) + 1;
          // [R31] 6시대 질풍연참 마무리 = 의열단 폭탄
          if (g2.era === 6) r31ThrowBomb(1.15);''')
rep('''      g.airRaids = (g.airRaids || 0) + 1;''', '''      g.airRaids = (g.airRaids || 0) + 1;
      // [R31] 2시대 = 곰의 내려찍기(착지 slam_hit 자세 · 곰 · 천둥) · 6시대 = 착지 지점 의열단 폭탄
      if (g.era === 2) {
        p._r31slamUntil = g.tick + 16;
        r31Slam(p.x + p.facing * 30, p.z, wave);
      } else if (g.era === 6) r31UiyeolBlast(p.x + p.facing * 40, p.z, 10, wave ? 1.2 : 1);''')
rep('''6: ["TAEGEUK FLASH!", "☯️ 시공 일섬 — 태극 섬광!"] };''', '''6: ["UIYEOL BLAST!", "💥 의열 폭파 일섬!"] };''')
rep('''      sfx("breath");
      const nm = SPECIAL_NAME[g.era]''', '''      sfx("breath");
      sfx("sliceFlurry");
      const nm = SPECIAL_NAME[g.era]''')
rep('''      else pushHelix(p.x, p.z, { H: 180, R: 66, turns: 1.8, cols: [C[0], C[1]], dur: 600, strands: 1 });
      addTimer(12, () => specialDash(0));''', '''      else pushHelix(p.x, p.z, { H: 180, R: 66, turns: 1.8, cols: [C[0], C[1]], dur: 600, strands: 1 });
      // [R31] 2시대 SOLAR FLASH = 하늘 소환 자세 + 청동 거울 광륜
      if (g.era === 2) r31Summon(false);
      addTimer(12, () => specialDash(0));''')
rep('''      const en = S.targets[k];
      const x0 = p.x;''', '''      const en = S.targets[k];
      // [R31] 의열 폭파 일섬 — Z자 돌진마다 표적에 폭탄 표식
      if (S.era === 6) {
        en._bombMark = performance.now();
        g._bombMarkUntil = performance.now() + 3200;
      }
      const x0 = p.x;''')
rep('''name: p._assetFrame || "atk1", alpha: 0.85 - i * 0.16 });''', '''name: p._assetFrame || "atk1", alpha: 0.85 - i * 0.16, shadow: S.era === 6 });''')
rep('''      else if (S.era === 6) pushHelix(p.x, p.z, { H: 150, R: 100, turns: 1.4, cols: ["#f8fafc", "#3b82f6"], dur: 600, strands: 2 });''',
    '''      else if (S.era === 6) pushHelix(p.x, p.z, { H: 150, R: 100, turns: 1.4, cols: ["#f8fafc", "#3b82f6"], dur: 600, strands: 2 });
      // [R31] 2시대 = 하늘에서 거대 비파형 동검이 꽂힌 뒤 일제 양단 · 6시대 = 표식 폭탄 연쇄 폭발 + 태극 광선
      if (S.era === 2) r31SkySword(clamp(p.x + p.facing * 40, g.cameraX + 170, g.cameraX + VIEW_W - 170), p.z, 0, false);
      if (S.era === 6) {
        r31Hfx(16, p.x, p.z - p.y - 60, 760, { s: 1.2, a: Math.random() * 6.28 });
        S.targets.forEach((en, i) => addTimer(2 + i * 5, () => {
          en._bombMark = 0;
          if (en.dying) return;
          r31UiyeolBlast(en.x, en.z, 30, 0.75, { special: true });
        }));
        g.uiyeolSpecials = (g.uiyeolSpecials || 0) + 1;
      }''')
rep('''      addTimer(1, () => {
        const g2 = gameRef.current;
        const S2 = g2.special;''', '''      addTimer(S.era === 2 ? 16 : 1, () => {
        const g2 = gameRef.current;
        const S2 = g2.special;''')
rep('''      g.player.invincibleTimer = 120;
      setPlayerBubble(trueUlt ?''', '''      g.player.invincibleTimer = 120;
      // [R31] 2시대 각성 = 하늘 소환(summon_sky) + 청동 거울 광륜 + 하늘에서 꽂히는 거대 비파형 동검 + 천둥 · 곰
      if (g.era === 2) {
        r31Summon(true);
        r31SkySword(g.cameraX + VIEW_W / 2, 424, 380, true);
      }
      setPlayerBubble(trueUlt ?''')
rep('''        addGroundCraterDecal(rx, 415, 82);''', '''        addGroundCraterDecal(rx, 415, 82);
        if (g.era === 2) pushArtFx("fx_thunder_crack", rx, 420, { k: "thunder", dur: 520, s: 0.9, delay: 420 + s * 80 });''')
rep('''    const detonateThrowable = (th) => {
      const g = gameRef.current;
      const eObj = eraObjOf();''', '''    const detonateThrowable = (th) => {
      const g = gameRef.current;
      const eObj = eraObjOf();
      // [R31] 의열단 폭탄 — 화구 · 화약 연기 · 파편 불꽃 · 충격 링 · bomb_uiyeol_blast
      if (th.kind === "uiyeol") {
        r31UiyeolBlast(th.x, th.z, th.y, th.power || 1);
        return;
      }''')

# 탄환: 비스듬한 탄도 · 화기 표시 · 검기 폭 판정 · 관통 탄은 베기선 없음
rep('''          prj.x += prj.vx;
          prj.life--;''', '''          prj.x += prj.vx;
          prj.life--;
          // [R31] 공중 모젤 탄: 비스듬히 아래로 · 땅에 닿으면 끝
          if (prj.vy) {
            prj.y += prj.vy;
            if (prj.y <= 2) prj.life = 0;
          }''')
rep('''          let hit = false;
          // [R30] X자 십자검기:''', '''          let hit = false;
          g._r31gun = !!prj.gun;
          // [R30] X자 십자검기:''')
rep('''            if (Math.abs(en.x - prj.x) < 52 && Math.abs(en.z - prj.z) < 48) {''', '''            if (Math.abs(en.x - prj.x) < 52 && Math.abs(en.z - prj.z) < 48 * (prj.wz || 1)) {''')
rep('''                pushSlashFx(en.x, en.z - en.y - 56, 0.62, prj.facing, { cross: true, len: 150 });
                g.crossHits = (g.crossHits || 0) + 1;''', '''                if (!prj.bullet) {
                  pushSlashFx(en.x, en.z - en.y - 56, 0.62, prj.facing, { cross: true, len: 150 });
                  g.crossHits = (g.crossHits || 0) + 1;
                }''')
rep('''          if (hit) explode(prj.x, prj.z, prj.y, 0.7);''', '''          if (hit && !prj.bullet && !prj.r31b) explode(prj.x, prj.z, prj.y, 0.7);''')
rep('''          if (hit || prj.life <= 0 || prj.x < 0 || prj.x > WORLD_WIDTH) g.projectiles.splice(i, 1);
        }''', '''          if (hit || prj.life <= 0 || prj.x < 0 || prj.x > WORLD_WIDTH) g.projectiles.splice(i, 1);
        }
        g._r31gun = false;''')

# ───────── 7. 4시대 전선 · 웨이브 · 미션 진행 · 6시대 기수 장교 ─────────
rep('''      for (let i = 0; i < n; i++) {
        const side = i % 2 === 0 ? -1 : 1;
        const flank = side;
        const role = roles ? roles[i] : null;
        if (i % 3 === 2) {
          put(L + 180 + Math.random() * (VIEW_W - 360), 356 + Math.random() * 120, { circle: true, flank, role });
        } else {
          put(side < 0 ? L - 60 - Math.random() * 70 : L + VIEW_W + 60 + Math.random() * 70, 356 + Math.random() * 120, { flank, role });
        }
      }''', '''      // [R31] 4시대 5대 전선 — 이번 웨이브의 전선(토스트 · 해설 · 미션) · 병종은 대기열에 넣을 때 정해 둔다
      const front = g.era === 4 && g.zoneIdx < 3 && !roles;
      if (front) {
        const WF = R31_WAVE_FRONT[g.zoneIdx] || [];
        r31EnterFront(WF[Math.max(0, Math.min(WF.length - 1, WF.length - 1 - g.waves.length))]);
      }
      for (let i = 0; i < n; i++) {
        const side = i % 2 === 0 ? -1 : 1;
        const flank = side;
        const role = roles ? roles[i] : null;
        const unit = front ? r31FrontUnit(g) : void 0;
        if (i % 3 === 2) {
          put(L + 180 + Math.random() * (VIEW_W - 360), 356 + Math.random() * 120, { circle: true, flank, role, unit });
        } else {
          put(side < 0 ? L - 60 - Math.random() * 70 : L + VIEW_W + 60 + Math.random() * 70, 356 + Math.random() * 120, { flank, role, unit });
        }
      }''')
rep('''          } else if (g.era === 2 && g.waves.length && alive <= 2 && !qn && !g.bossActive) {''', '''          } else if ((g.era === 2 || g.era === 4) && g.waves.length && alive <= 2 && !qn && !g.bossActive) {''')
rep('''              g.zoneState = "GO";
              g.goT = 0;
              g.zoneIdx++;''', '''              // [R31] 4시대: 구역이 정리되면 진행 중인 전선 미션 판정(몽골 · 홍건적)
              if (g.era === 4 && g.front4) r31FrontEnd(g, g.front4);
              g.zoneState = "GO";
              g.goT = 0;
              g.zoneIdx++;''')
rep('''      if (era === 2 && HIST2[zi]) addTimer(70, () => setCompanionBubble(HIST2[zi], 200));''', '''      if (era === 2 && HIST2[zi]) addTimer(70, () => setCompanionBubble(HIST2[zi], 200));
      // [R31] 4시대: 첫 구역에서 전선 · 미션 초기화 · Z4 결전 해설 / 6시대 Z4(1945 경성): 일본군 기수 장교
      if (era === 4 && zi === 0) {
        g.front4 = null;
        g.mission = null;
        g.missionDone = {};
      }
      if (era === 4 && zi === 3) addTimer(90, () => setCompanionBubble("📜 1362년 고려군은 홍건적에게 빼앗긴 개경을 되찾았어요. 이제 침략군의 철갑 공성 사령관만 남았어요!", 200));
      if (era === 6 && zi === 3) addTimer(240, () => r31SpawnOfficer(ZONE_CAM[3] + 150, 396, -1));''')
rep('''        spawnEnemyAt(ZONE_CAM[3] + 160, 390, { circle: true, flank: -1, unit: "JP_BAYONET" });
        spawnEnemyAt(ZONE_CAM[3] + VIEW_W - 160, 446, { circle: true, flank: 1, unit: "JP_BAYONET" });''', '''        // [R31] 1945 경성 — 단계마다 일본군 기수 장교(깃발 · 군도)가 총검병을 이끌고 들어온다
        r31SpawnOfficer(ZONE_CAM[3] + 160, 390, -1);
        spawnEnemyAt(ZONE_CAM[3] + VIEW_W - 160, 446, { circle: true, flank: 1, unit: "JP_BAYONET" });''')
rep('''360 + Math.random() * 110, { circle: true, unit: "JP_BAYONET" });''', '''360 + Math.random() * 110, { circle: true, unit: (b.reinfK = (b.reinfK || 0) + 1) % 2 ? "JP_BAYONET" : "JP_OFFICER" });''')
rep('''        if (p.attackTimer > 0) {
          p.attackTimer--;''', '''        // [R31] 4시대 미션 진행 · 보상 버프 시간(인장 = 공격 후딜 단축으로 공속 ↑)
        if (g.mission && g.mission.state === "run") r31MissionTick(g);
        const RB = g.r31buff;
        if (RB) {
          if (RB.seal > 0) {
            RB.seal--;
            if (p.attackTimer > 1 && !p.pendingHit && g.tick % 3 === 0) p.attackTimer--;
          }
          if (RB.banner > 0) RB.banner--;
          if (RB.blade > 0) RB.blade--;
        }
        if (p.attackTimer > 0) {
          p.attackTimer--;''')

# 4시대 동시 7명: 원소 타격(화염 폭발 ≈ 파티클 21개)이 파티클 상한을 채우면 작은 불꽃으로
rep('''      } else if (era === 4) {
        explode(x, z, y, heavy ? 0.6 : 0.38, "#fb923c");''', '''      } else if (era === 4) {
        // [R31] 동시 7명 고밀도 전투 — 파티클이 붐비면(110↑) 화염 폭발 대신 작은 불꽃(섬광 + 불티)으로 프레임을 지킨다
        if (g.particles.length > 110) {
          spawnPart({ kind: "FLASH", x, z, y, size: heavy ? 14 : 10, rot: Math.random() * TAU, c: "#fb923c", life: 6, maxLife: 6 });
          spawnSparks(x, z, y, heavy ? 5 : 3, g.player.facing);
          g.e4LiteHits = (g.e4LiteHits || 0) + 1;
        } else explode(x, z, y, heavy ? 0.6 : 0.38, "#fb923c");''')

# 동시 피해 숫자 36 → 28(고밀도 전투에서 화면 가림 · 그리기 비용 ↓)
rep('''      if (g.damagePopups.length > 36) g.damagePopups.shift();''', '''      // [R31] 동시 피해 숫자 36 → 28(동시 7명 고밀도 전투 — 화면 가림 · 그리기 비용 ↓)
      if (g.damagePopups.length > 28) g.damagePopups.shift();''')

# 2시대 해금 배너 문구(Lv.3 = 곰의 내려찍기 · Lv.5 = 하늘 소환 각성)
rep('''  var nextSkillOf = (lv) => {
    const ks = Object.keys(SKILL_UNLOCKS).map(Number).filter((k) => k > lv).sort((a, b) => a - b);
    return ks.length ? { lv: ks[0], short: SKILL_UNLOCKS[ks[0]].short } : null;
  };''', '''  // [R31] 2시대 해모수는 Lv.3 4타 = 곰의 내려찍기 · 각성 = 하늘 소환 — 해금 배너 · 다음 기술 안내 · 잠금 안내 문구도 시대에 맞춘다
  var R31_SKILL_E2 = {
    3: { kind: "EVOLVE", title: "곰의 내려찍기 · 돌진 진화", short: "곰 내려찍기", key: "J 4연타 · K", desc: "4타 피니시가 칼을 높이 들었다 땅을 내려찍는 곰의 일격(곰 · 천둥)으로! 3타는 호랑이 발톱 강타 · 돌진 뒤 J는 곧바로 3타(DASH LINK)", color: "#facc15", color2: "#ca8a04" },
    5: { kind: "AWAKEN", title: "진 각성 · 급강하 파동격", short: "파동격", key: "U · F · J", desc: "일섬 뒤 · 공중 내리꽂기가 급강하 파동격(곰 · 천둥 + 양쪽 X자 검기)으로! 각성은 하늘 소환 — 청동 거울 광륜 + 하늘에서 꽂히는 거대 비파형 동검", color: "#fde047", color2: "#f59e0b" }
  };
  var skillUnlockOf = (lv, era) => era === 2 && R31_SKILL_E2[lv] || SKILL_UNLOCKS[lv];
  var nextSkillOf = (lv, era) => {
    const ks = Object.keys(SKILL_UNLOCKS).map(Number).filter((k) => k > lv).sort((a, b) => a - b);
    return ks.length ? { lv: ks[0], short: skillUnlockOf(ks[0], era).short } : null;
  };''')
rep('''          const nx = nextSkillOf(hud.level);''', '''          const nx = nextSkillOf(hud.level, currentEra);''')
rep('''      const U = SKILL_UNLOCKS[lv];
      if (!U) return;''', '''      const U = skillUnlockOf(lv, gameRef.current.era);
      if (!U) return;''')
rep('''${SKILL_UNLOCKS[SKILL_LV[kind]].short}''', '''${skillUnlockOf(SKILL_LV[kind], g.era).short}''')

# ───────── 8. 그리기: 해모수 자세 · 그림자 잔상 · 광륜 · 원화 이펙트 · 타격 이펙트 · 보상 빛기둥 · 미션 배너 ─────────
rep('''      const heroAtkPlan = (A, p) => {
        const F = A.frames;
        const sp = A.atk || {};
        const shoot = p.atkAnim === "shoot";''', '''      const heroAtkPlan = (A, p) => {
        const F = A.frames;
        const sp = A.atk || {};
        const shoot = p.atkAnim === "shoot";
        // [R31] 2시대 해모수 신화 자세 — 착지 직후 slam_hit · 급강하 중 slam_prep · Lv.3+ 4타 slam_prep → slam_hit · 3타 atk3_prep → heavy_cleave
        if (F.slam_hit && F.slam_prep && !shoot) {
          const tk = gameRef.current.tick;
          if (p._r31slamUntil != null && tk < p._r31slamUntil) return { prep: "slam_hit", chain: ["slam_hit"], key: "atk3", shoot: false };
          if (p.plunge) return { prep: "slam_prep", chain: ["slam_prep"], key: "atk3", shoot: false };
          if (p._r31slam && p._atkSrc === "combo" && p.comboStep === 4) return { prep: "slam_prep", chain: ["slam_hit"], key: "atk3", shoot: false };
          if (F.heavy_cleave && p._atkSrc === "combo" && p.comboStep === 3 && !p.rush) return { prep: F.atk3_prep ? "atk3_prep" : "atk_prep", chain: ["heavy_cleave"], key: "atk3", shoot: false };
        }''')
rep('''      const heroPose0 = (p, g) => {
        const o = { name: "idle", sx: 1, sy: 1, rot: 0, lift: 0, dx: 0 };''', '''      const heroPose0 = (p, g) => {
        const o = { name: "idle", sx: 1, sy: 1, rot: 0, lift: 0, dx: 0 };
        // [R31] 해모수 하늘 소환(summon_sky) — 일섬 · 각성 순간 자세 고정(살짝 떠오름)
        const RP = p._r31pose;
        if (RP && !(p.downTimer > 0) && g.tick < RP.until && frameAssets.hero && frameAssets.hero.frames[RP.name]) {
          o.name = RP.name;
          o.lift = 5 * Math.min(1, (RP.until - g.tick) / 8);
          return o;
        }''')
rep('''        const fr = A.frames[name] || A.frames.idle;
        const k = A.k;''', '''        // [R31] o.img = 같은 크기의 대체 그림(6시대 그림자 잔상 실루엣)
        const fr = o.img || A.frames[name] || A.frames.idle;
        const k = A.k;''')
rep('''            if (gh.evo) drawAssetActor(HA, "run", gh.x, gh.z - gh.y, gh.facing, { alpha: Math.min(1, gh.alpha * 1.15), glow: { col: gh.col, a: 1 }, glowOnly: true });''',
    '''            // [R31] 6시대 야습 그림자 잔상 — 어두운 실루엣(앞쪽 가장자리 푸른 빛)
            if (gh.shadow) {
              const nm = gh.name && HA.frames[gh.name] ? gh.name : "run";
              drawAssetActor(HA, nm, gh.x, gh.z - gh.y, gh.facing, { sx: gh.sx || 1, img: darkOf(HA, nm), alpha: Math.min(1, gh.alpha) * 0.74 });
              g.shadowGhosts = (g.shadowGhosts || 0) + 1;
            } else if (gh.evo) drawAssetActor(HA, "run", gh.x, gh.z - gh.y, gh.facing, { alpha: Math.min(1, gh.alpha * 1.15), glow: { col: gh.col, a: 1 }, glowOnly: true });''')
rep('''          // [R30] 오라(몸 뒤) · 입체 검기의 뒤쪽 반(주인공 몸 뒤로 감기는 부분)
          drawHeroAura(g, p, HA, true);''', '''          // [R31] 해모수 청동 거울 광륜(몸 뒤에서 돎)
          if (g.r31halo) drawR31Halo(g, p, HA);
          // [R30] 오라(몸 뒤) · 입체 검기의 뒤쪽 반(주인공 몸 뒤로 감기는 부분)
          drawHeroAura(g, p, HA, true);''')
rep('''flash: en.flashTimer > 0 ? 0.6 * Math.min(1, en.flashTimer / 4) : 0, alpha });''', '''flash: en._wf && performance.now() - en._wf < R31_WF_MS ? 1 : en.flashTimer > 0 ? 0.6 * Math.min(1, en.flashTimer / 4) : 0, alpha });''')
rep('''flash: en.flashTimer > 0 ? 0.5 * Math.min(1, en.flashTimer / 6) : 0, alpha });''', '''flash: en._wf && performance.now() - en._wf < R31_WF_MS ? 0.9 : en.flashTimer > 0 ? 0.5 * Math.min(1, en.flashTimer / 6) : 0, alpha });''')
rep('''        frameAssets.fx = AS && AS.fx && !isLiberated ? AS.fx : null;''', '''        frameAssets.fx = AS && AS.fx && !isLiberated ? AS.fx : null;
        frameAssets.items = AS && AS.items ? AS.items : null;''')
rep('''        if (g.slashFx && g.slashFx.length) overlay.push((o) => drawSlashFx(g, o));''', '''        if (g.slashFx && g.slashFx.length) overlay.push((o) => drawSlashFx(g, o));
        // [R31] 해모수 신화 원화 이펙트 · 타격 이펙트 5종(총기 · 폭탄 포함) · 미션 보상 빛기둥 · 미션 배너 · 보상 버프
        if (g.artFx && g.artFx.length) overlay.push((o) => drawArtFx(g, o));
        overlay.push((o) => drawR31Hfx(g, o));
        if (g.r31pick) overlay.push((o) => drawR31Pick(g, o));
        if (g.mission || g.r31buff) screenOverlay.push((c) => drawR31Mission(g, c));''')

rep('''      const drawFx3dPass = (g, back, S0) => {''', r'''      // ───────── [R31] 그리기 ─────────
      // 6시대 그림자 잔상 — 프레임마다 한 번 굽는 어두운 실루엣(앞쪽 가장자리로 갈수록 푸른 빛)
      const darkOf = (A, name) => {
        const D = A._dark || (A._dark = {});
        if (D[name]) return D[name];
        const fr = A.frames[name] || A.frames.idle;
        const c = mkCanvas(fr.width, fr.height);
        const x = c.getContext("2d");
        x.drawImage(fr, 0, 0);
        x.globalCompositeOperation = "source-in";
        x.fillStyle = "#0a1020";
        x.fillRect(0, 0, c.width, c.height);
        x.globalCompositeOperation = "source-atop";
        const gr = x.createLinearGradient(0, 0, c.width, 0);
        gr.addColorStop(0, "rgba(59,130,246,0)");
        gr.addColorStop(1, "rgba(96,165,250,0.4)");
        x.fillStyle = gr;
        x.fillRect(0, 0, c.width, c.height);
        D[name] = c;
        return c;
      };
      // 해모수 청동 거울 광륜 — 몸 뒤(윗몸 중심)에서 천천히 돌며 맥동(원화 + 가산 번짐)
      const drawR31Halo = (g, p, HA) => {
        const H = g.r31halo;
        const now = performance.now();
        const t = (now - H.t0) / H.dur;
        if (t >= 1) {
          g.r31halo = null;
          return;
        }
        const FXA = frameAssets.fx && frameAssets.fx.fx_bronze_mirror_halo;
        if (!FXA || PERF_OFF.particles) return;
        const F = frameAssets.cam;
        const a = Math.min(1, t / 0.12) * (t > 0.78 ? (1 - t) / 0.22 : 1);
        const bodyH = Math.max(90, (HA.groundY - (HA.topY || 0)) * HA.k);
        const D = bodyH * 1.7 * H.s * (0.85 + 0.15 * Math.min(1, t / 0.12));
        screen.save();
        screen.setTransform(F.dpr, 0, 0, F.dpr, 0, 0);
        applyCam(screen, F);
        screen.translate(-F.camRX + p.x, p.z - p.y - bodyH * 0.62);
        screen.rotate((now - H.t0) / 1e3 * 1.1);
        screen.imageSmoothingEnabled = true;
        screen.globalAlpha = a * 0.92;
        screen.drawImage(FXA.img, -D / 2, -D / 2, D, D);
        if (now - H.t0 < 350) {
          screen.globalCompositeOperation = "lighter";
          screen.globalAlpha = a * 0.45 * (1 - (now - H.t0) / 350);
          screen.drawImage(FXA.img, -D / 2, -D / 2, D, D);
        }
        screen.restore();
        (g._assetSeen || (g._assetSeen = {}))["fx:fx_bronze_mirror_halo"] = g.tick;
      };
      // 2시대 신화 원화 이펙트(호랑이 발톱 · 곰 · 천둥 · 하늘에서 꽂히는 거대 비파형 동검) — 원화 그대로 + 가산 번짐 한 겹
      const ART_FX_FOOT = { bear: 0.94, thunder: 0.935, sword: 0.975 };
      const drawArtFx = (g, S) => {
        const L = g.artFx;
        const FX = frameAssets.fx;
        if (!L || !L.length || PERF_OFF.particles) return;
        const now = performance.now();
        for (let i = L.length - 1; i >= 0; i--) {
          const e = L[i];
          const t = (now - e.t0) / e.dur;
          if (t >= 1) {
            L.splice(i, 1);
            continue;
          }
          const A = FX && FX[e.n];
          if (t < 0 || !A) continue;
          let w = A.w * e.s;
          let h = A.h * e.s;
          let x = e.x;
          let y = e.y;
          let a = 1;
          let glow = 0;
          if (e.k === "claw") {
            const g1 = Math.min(1, t / 0.22);
            const sc = 0.55 + 0.5 * (1 - (1 - g1) * (1 - g1));
            w *= sc;
            h *= sc;
            x += e.dir * 46 * t;
            a = t < 0.45 ? 1 : 1 - (t - 0.45) / 0.55;
          } else if (e.k === "bear") {
            const g1 = Math.min(1, t / 0.25);
            const sc = 0.7 + 0.3 * g1;
            w *= sc;
            h *= sc;
            y -= 14 * g1;
            a = t < 0.55 ? Math.min(1, t / 0.08) : 1 - (t - 0.55) / 0.45;
            glow = t < 0.18 ? 0.5 : 0;
          } else if (e.k === "thunder") {
            a = t < 0.3 ? 0.6 + 0.4 * ((now / 33 | 0) & 1) : 1 - (t - 0.3) / 0.7;
            glow = t < 0.3 ? 0.75 : 0;
          } else if (e.k === "sword") {
            if (t < 0.3) {
              const u = t / 0.3;
              y -= (1 - u * u) * 760;
              a = Math.min(1, u * 3);
            } else a = t < 0.75 ? 1 : 1 - (t - 0.75) / 0.25;
            glow = t >= 0.3 && t < 0.45 ? 1 : 0;
          }
          const foot = ART_FX_FOOT[e.k];
          const dy = foot ? -h * foot : -h / 2;
          S.save();
          S.translate(x, y);
          if (e.dir < 0) S.scale(-1, 1);
          S.globalAlpha = a;
          S.drawImage(A.img, -w / 2, dy, w, h);
          if (glow > 0) {
            S.globalCompositeOperation = "lighter";
            S.globalAlpha = a * glow;
            S.drawImage(A.img, -w / 2, dy, w, h);
          }
          S.restore();
          (g._assetSeen || (g._assetSeen = {}))["fx:" + e.n] = g.tick;
        }
      };
      // 타격 이펙트 · 총기 · 폭탄 연출(R31_HFX 고정 풀) — ctx.filter 없음.
      //  자주 나오는 종류(① 히트스타 · ② 스파크 · ③ 먹 · ④ 먼지 · ⑤ 베기선 · 금속 불꽃)는 종류 × 투명도 3단계로 묶어 한 번에 칠한다
      //  (살아 있는 칸이 50개여도 그리기 호출 20~30회) · 충격 링과 드문 종류(총 · 폭탄 · 탄피 · 광선)는 칸마다
      const HFX_A = [0.3, 0.62, 0.95];
      const HFX_BASE = { 1: 1, 2: 1, 3: 0.82, 5: 0.34, 6: 1, 9: 1 };
      const hfxFade = (k, t) => k === 1 ? t < 0.3 ? 1 : 1 - (t - 0.3) / 0.7 : k === 3 ? t < 0.2 ? 1 : 1 - (t - 0.2) / 0.8 : 1 - t;
      // 한 칸의 모양을 지금 경로에 덧붙인다
      const hfxGeom = (S, e, t) => {
        const k = e.k;
        if (k === 1) {
          const g1 = Math.min(1, t / 0.3);
          const sc = (0.45 + 0.75 * (1 - (1 - g1) * (1 - g1))) * e.s;
          for (let j = 0; j < 16; j++) {
            const ang = e.a + j * Math.PI / 8;
            const r = (j % 2 ? 4.5 : j % 4 === 0 ? 30 : 15) * sc;
            const px = e.x + Math.cos(ang) * r;
            const py = e.y + Math.sin(ang) * r;
            if (j === 0) S.moveTo(px, py);
            else S.lineTo(px, py);
          }
          S.closePath();
        } else if (k === 2) {
          const u = 1 - (1 - t) * (1 - t);
          const base = e.dir > 0 ? e.a * 0.35 : Math.PI - e.a * 0.35;
          const sag = 30 * t * t;
          for (let j = 0; j < e.n; j++) {
            const ang = base + (r31h(e.seed + j * 1.9) - 0.5) * 1.3;
            const d = (55 + 115 * r31h(e.seed + j * 3.3)) * e.s * u;
            const L = (12 + 22 * r31h(e.seed + j * 5.1)) * (1 - t) * e.s;
            const cx = Math.cos(ang);
            const cy = Math.sin(ang);
            S.moveTo(e.x + cx * Math.max(0, d - L), e.y + cy * Math.max(0, d - L) + sag);
            S.lineTo(e.x + cx * d, e.y + cy * d + sag);
          }
        } else if (k === 3) {
          const gr = Math.min(1, t / 0.12);
          for (let j = 0; j < 6; j++) {
            const ang = (r31h(e.seed + j * 7.13) - 0.5) * 2.1 + (e.dir > 0 ? 0 : Math.PI);
            const d = (12 + 48 * r31h(e.seed + j * 3.7)) * e.s * gr;
            const r = (2.5 + 7 * r31h(e.seed + j * 5.3)) * e.s * (1 - 0.35 * t);
            const bx = e.x + Math.cos(ang) * d;
            const by = e.y + Math.sin(ang) * d * 0.7 + t * 12;
            S.moveTo(bx + r, by);
            S.arc(bx, by, r, 0, TAU);
          }
        } else if (k === 5) {
          for (let j = 0; j < 2; j++) {
            const r = (4 + 9 * t) * e.s * (0.85 + 0.3 * j);
            const bx = e.x - e.dir * (j * 13 + 10 * t) + (r31h(e.seed + j) - 0.5) * 10;
            const by = e.y - 4 - j * 3 - 14 * t;
            S.moveTo(bx + r, by);
            S.arc(bx, by, r, 0, TAU);
          }
        } else if (k === 6) {
          const L = 74 * e.s * Math.min(1, t / 0.2);
          const ux = Math.cos(e.a) * e.dir;
          const uy = Math.sin(e.a);
          S.moveTo(e.x - ux * L, e.y - uy * L);
          S.lineTo(e.x + ux * L, e.y + uy * L);
        } else if (k === 9) {
          const T = t * e.dur / 1e3;
          for (let j = 0; j < e.n; j++) {
            const ang = (e.dir > 0 ? -0.3 : Math.PI + 0.3) + (r31h(e.seed + j * 2.7) - 0.5) * 2.4 * (e.dir > 0 ? 1 : -1);
            const v = 160 + 240 * r31h(e.seed + j * 6.1);
            const vx = Math.cos(ang) * v;
            const vy0 = Math.sin(ang) * v;
            const bx = e.x + vx * T;
            const by = e.y + vy0 * T + 520 * T * T;
            S.moveTo(bx - vx * 0.022, by - (vy0 + 1040 * T) * 0.022);
            S.lineTo(bx, by);
          }
          if (t < 0.3) {
            const f = 1 - t / 0.3;
            S.moveTo(e.x - 26 * f, e.y);
            S.lineTo(e.x + 26 * f, e.y);
            S.moveTo(e.x, e.y - 18 * f);
            S.lineTo(e.x, e.y + 18 * f);
          }
        }
      };
      // 종류 K를 투명도 3단계로 묶어 칠한다(fill = 채우기 · 아니면 긋기)
      const hfxBatch = (S, P, K, fill, col, lw) => {
        for (let b = 0; b < 3; b++) {
          let any = false;
          for (let i = 0; i < R31_HFX_N; i++) {
            const e = P[i];
            if (!e.on || e.k !== K || e._b !== b) continue;
            if (!any) {
              any = true;
              S.beginPath();
            }
            hfxGeom(S, e, e._t);
          }
          if (!any) continue;
          S.globalAlpha = HFX_BASE[K] * HFX_A[b];
          if (fill) {
            S.fillStyle = col;
            S.fill();
          } else {
            S.strokeStyle = col;
            S.lineWidth = lw[b];
            S.stroke();
          }
        }
      };
      const HFX_LW = { 2: [2.4, 2.4, 2.4], 6: [1.2, 2, 2.8], 9: [1.8, 1.8, 1.8] };
      const drawR31Hfx = (g, S) => {
        if (PERF_OFF.particles || PERF_OFF.hfx) return;
        const now = performance.now();
        const P = R31_HFX;
        let live = 0;
        let c1 = null;
        let c2 = null;
        // 시간 · 투명도 단계 미리 계산(끝난 칸은 끈다)
        for (let i = 0; i < R31_HFX_N; i++) {
          const e = P[i];
          if (!e.on) continue;
          const t = (now - e.t0) / e.dur;
          if (t >= 1) {
            e.on = false;
            continue;
          }
          live++;
          e._t = t;
          if (t < 0) e._b = -1;
          else {
            const f = hfxFade(e.k, t);
            e._b = f > 0.66 ? 2 : f > 0.33 ? 1 : 0;
          }
          if (t >= 0 && e.k === 1 && !c1) c1 = e.c;
          if (t >= 0 && e.k === 2 && !c2) c2 = e.c;
        }
        g.hfxLive = live;
        if (!live) return;
        S.save();
        // 1패스 — 일반 합성: 먹 · 먼지(묶음) · 파편 · 연기 · 탄피(칸마다)
        hfxBatch(S, P, 3, true, "#07080d");
        hfxBatch(S, P, 5, true, "#a8a29e");
        for (let i = 0; i < R31_HFX_N; i++) {
          const e = P[i];
          if (!e.on || e._b < 0) continue;
          const k = e.k;
          if (k !== 7 && k !== 8 && k !== 11 && k !== 14) continue;
          const t = e._t;
          if (k === 7) {
            // ⑤ 도끼 파편 — 돌 · 나무 조각이 포물선으로
            const T = t * e.dur / 1e3;
            S.globalAlpha = 1 - t;
            for (let j = 0; j < e.n; j++) {
              const h1 = r31h(e.seed + j * 2.1);
              const h2 = r31h(e.seed + j * 4.7);
              const bx = e.x + e.dir * (60 + 160 * h1) * T * (j % 3 ? 1 : -0.4);
              const by = e.y - (110 + 160 * h2) * T + 900 * T * T;
              const sz = 3 + 4 * h2;
              const ca = Math.cos(h1 * 6 + T * 14);
              const sa = Math.sin(h1 * 6 + T * 14);
              S.fillStyle = j % 2 ? "#a16207" : "#78716c";
              S.beginPath();
              S.moveTo(bx - sz * ca - sz * 0.6 * sa, by - sz * sa + sz * 0.6 * ca);
              S.lineTo(bx + sz * ca - sz * 0.4 * sa, by + sz * sa + sz * 0.4 * ca);
              S.lineTo(bx + sz * sa, by - sz * ca);
              S.closePath();
              S.fill();
            }
          } else if (k === 8) {
            // ⑤ 총 연기 고리 — 회색 고리가 퍼지며 옅어짐 + 작은 연기 2덩이
            const u = 1 - (1 - t) * (1 - t);
            S.globalAlpha = 0.5 * (1 - t);
            S.strokeStyle = "#cbd5e1";
            S.lineWidth = 2 + 6 * (1 - t);
            S.beginPath();
            S.ellipse(e.x + e.dir * 10 * u, e.y, 8 + 30 * u, (8 + 30 * u) * 0.8, 0, 0, TAU);
            S.stroke();
            S.fillStyle = "#94a3b8";
            S.globalAlpha = 0.35 * (1 - t);
            S.beginPath();
            S.arc(e.x + e.dir * 22 * u, e.y - 14 * u, 6 + 10 * u, 0, TAU);
            S.arc(e.x - e.dir * 8 * u, e.y - 22 * u, 5 + 8 * u, 0, TAU);
            S.fill();
          } else if (k === 11) {
            // 황금 탄피 — 튀어 올라 떨어진 뒤 한 번 튕김
            const T = t * e.dur / 1e3;
            const G = 1400;
            const disc = e.vy * e.vy + 2 * G * (e.gy - e.y);
            const T1 = disc > 0 ? (e.vy + Math.sqrt(disc)) / G : T;
            let bx;
            let by;
            if (T < T1) {
              bx = e.x + e.vx * T;
              by = e.y - e.vy * T + 0.5 * G * T * T;
            } else {
              const T2 = T - T1;
              const vy2 = e.vy * 0.3;
              bx = e.x + e.vx * T1 + e.vx * 0.45 * Math.min(T2, 2 * vy2 / G);
              by = Math.min(e.gy, e.gy - vy2 * T2 + 0.5 * G * T2 * T2);
            }
            S.globalAlpha = t > 0.8 ? (1 - t) / 0.2 : 1;
            S.save();
            S.translate(bx, by);
            S.rotate(T * 20 * (e.vx < 0 ? -1 : 1));
            S.fillStyle = "#ca8a04";
            S.fillRect(-3.2, -1.4, 6.4, 2.8);
            S.fillStyle = "#fef08a";
            S.fillRect(-3.2, -1.4, 6.4, 1);
            S.restore();
          } else {
            // 화약 연기 — 짙은 회색 덩이가 부풀며 올라감
            const u = 1 - (1 - t) * (1 - t);
            S.globalAlpha = 0.5 * (1 - t);
            S.fillStyle = "#26262e";
            S.beginPath();
            S.arc(e.x + e.vx * t, e.y - 46 * u * e.s, (14 + 40 * u) * e.s, 0, TAU);
            S.fill();
          }
        }
        // 2패스 — 빛(가산): 링 · 강타 번짐 · 드문 종류는 칸마다, 나머지는 묶음
        S.globalCompositeOperation = "lighter";
        S.lineCap = "round";
        for (let i = 0; i < R31_HFX_N; i++) {
          const e = P[i];
          if (!e.on || e._b < 0) continue;
          const k = e.k;
          const t = e._t;
          if (k === 1) {
            // ① 강타 히트스타의 빛 번짐(앞 0.5만)
            if (e.s > 1.3 && t < 0.5) {
              const g1 = Math.min(1, t / 0.3);
              const sc = (0.45 + 0.75 * (1 - (1 - g1) * (1 - g1))) * e.s;
              S.globalAlpha = 0.6 * (t < 0.3 ? 1 : 1 - (t - 0.3) / 0.7);
              S.drawImage(getGlowSprite(e.c2), e.x - 30 * sc, e.y - 30 * sc, 60 * sc, 60 * sc);
            }
          } else if (k === 4) {
            // ③ 충격 링 — 바닥 원근 타원이 퍼짐
            const u = 1 - (1 - t) * (1 - t);
            const rx = (16 + 74 * u) * e.s;
            S.globalAlpha = 0.85 * (1 - t);
            S.strokeStyle = e.c;
            S.lineWidth = 0.8 + 5 * (1 - t);
            S.beginPath();
            S.ellipse(e.x, e.y, rx, rx * 0.3, 0, 0, TAU);
            S.stroke();
          } else if (k === 10) {
            // 예광탄 — 총구에서 뻗어 나가는 관통 빛줄기(꼬리부터 사라짐)
            const len = Math.sqrt(e.vx * e.vx + e.vy * e.vy) || 1;
            const ux = e.vx / len;
            const uy = e.vy / len;
            const L = e.n * Math.min(1, t / 0.22);
            const tail = L * Math.max(0, (t - 0.2) / 0.8);
            for (let q = 0; q < 2; q++) {
              S.globalAlpha = (1 - t) * (q ? 1 : 0.45);
              S.strokeStyle = q ? "#fffbeb" : "#fde047";
              S.lineWidth = q ? 1.5 : 4.5;
              S.beginPath();
              S.moveTo(e.x + ux * tail, e.y + uy * tail);
              S.lineTo(e.x + ux * L, e.y + uy * L);
              S.stroke();
            }
          } else if (k === 12) {
            // 총구 섬광 — 앞으로 뻗는 세 갈래 불꽃 + 빛 번짐
            const f = 1 - t;
            S.globalAlpha = f;
            S.drawImage(getGlowSprite("#fde047"), e.x - 26 * f + e.dir * 10, e.y - 26 * f, 52 * f, 52 * f);
            S.fillStyle = "#fffbeb";
            S.beginPath();
            S.moveTo(e.x, e.y - 5);
            S.lineTo(e.x + e.dir * 36 * f, e.y);
            S.lineTo(e.x, e.y + 5);
            S.moveTo(e.x, e.y - 3);
            S.lineTo(e.x + e.dir * 18 * f, e.y - 13 * f);
            S.lineTo(e.x + e.dir * 4, e.y);
            S.moveTo(e.x, e.y + 3);
            S.lineTo(e.x + e.dir * 18 * f, e.y + 13 * f);
            S.lineTo(e.x + e.dir * 4, e.y);
            S.fill();
          } else if (k === 13) {
            // 폭탄 화구 — 노랑 심 → 주황 → 붉은 바깥 불덩이가 부풀며 꺼짐
            const u = 1 - (1 - t) * (1 - t);
            const r = (30 + 70 * u) * e.s;
            const a = t < 0.2 ? 1 : 1 - (t - 0.2) / 0.8;
            S.globalAlpha = a * 0.55;
            S.drawImage(getGlowSprite("#ef4444"), e.x - r * 1.25, e.y - r * 1.25, r * 2.5, r * 2.5);
            S.globalAlpha = a * 0.85;
            S.drawImage(getGlowSprite("#f97316"), e.x - r * 0.9, e.y - r * 0.95, r * 1.8, r * 1.8);
            S.globalAlpha = a;
            S.drawImage(getGlowSprite("#fde047"), e.x - r * 0.55, e.y - r * 0.6, r * 1.1, r * 1.1);
            if (t < 0.15) {
              S.globalAlpha = 1 - t / 0.15;
              S.drawImage(getGlowSprite("#ffffff"), e.x - r * 0.5, e.y - r * 0.5, r, r);
            }
          } else if (k === 15) {
            // 파편 불꽃 — 사방으로 튀는 화약 · 쇳조각
            const T = t * e.dur / 1e3;
            S.globalAlpha = 1 - t;
            S.strokeStyle = e.c;
            S.lineWidth = 2;
            S.beginPath();
            for (let j = 0; j < e.n; j++) {
              const ang = j / e.n * TAU + (r31h(e.seed + j) - 0.5) * 0.5;
              const v = (220 + 260 * r31h(e.seed + j * 3.1)) * e.s;
              const bx = e.x + Math.cos(ang) * v * T;
              const by = e.y + Math.sin(ang) * v * T * 0.6 + 320 * T * T;
              const tl = 16 * (1 - t);
              S.moveTo(bx - Math.cos(ang) * tl, by - Math.sin(ang) * tl * 0.6);
              S.lineTo(bx, by);
            }
            S.stroke();
          } else if (k === 16) {
            // 태극 광선 — 붉은 · 푸른 빛살이 번갈아 퍼지며 천천히 돎
            const u = 1 - (1 - t) * (1 - t);
            const L = (120 + 280 * u) * e.s;
            const rot = e.a + t * 0.7;
            S.globalAlpha = 0.8 * (1 - t);
            for (let q = 0; q < 2; q++) {
              S.fillStyle = q ? "#3b82f6" : "#ef4444";
              S.beginPath();
              for (let j = q; j < 12; j += 2) {
                const ang = rot + j / 12 * TAU;
                S.moveTo(e.x, e.y);
                S.lineTo(e.x + Math.cos(ang - 0.05) * L, e.y + Math.sin(ang - 0.05) * L * 0.75);
                S.lineTo(e.x + Math.cos(ang + 0.05) * L, e.y + Math.sin(ang + 0.05) * L * 0.75);
                S.closePath();
              }
              S.fill();
            }
            S.globalAlpha = 0.9 * (1 - t);
            S.drawImage(getGlowSprite("#ffffff"), e.x - 60 * e.s, e.y - 60 * e.s, 120 * e.s, 120 * e.s);
          }
        }
        hfxBatch(S, P, 1, true, c1 || "#ffffff");
        hfxBatch(S, P, 2, false, c2 || "#fde047", HFX_LW[2]);
        hfxBatch(S, P, 6, false, "#ffffff", HFX_LW[6]);
        hfxBatch(S, P, 9, false, "#bfdbfe", HFX_LW[9]);
        // 의열 폭파 일섬 — 표적 머리 위 폭탄 표식(심지 불꽃 깜빡임) + 발밑 붉은 고리
        if (g._bombMarkUntil > now) {
          const L = g.enemies;
          const bl = (now / 90 | 0) & 1;
          for (let i = 0; i < L.length; i++) {
            const en = L[i];
            if (!en._bombMark || now - en._bombMark > 3000) continue;
            const bx = en.x;
            const by = en.z - (en.y || 0) - 150;
            S.globalCompositeOperation = "source-over";
            S.globalAlpha = 1;
            S.fillStyle = "#111318";
            S.beginPath();
            S.arc(bx, by, 8, 0, TAU);
            S.fill();
            S.strokeStyle = "#a16207";
            S.lineWidth = 2;
            S.beginPath();
            S.moveTo(bx + 4, by - 6);
            S.quadraticCurveTo(bx + 10, by - 14, bx + 6, by - 18);
            S.stroke();
            S.globalCompositeOperation = "lighter";
            S.globalAlpha = bl ? 1 : 0.55;
            S.drawImage(getGlowSprite("#fb923c"), bx - 6, by - 30, 24, 24);
            S.globalAlpha = 0.5 + 0.3 * Math.sin(now / 80);
            S.strokeStyle = "#ef4444";
            S.beginPath();
            S.ellipse(en.x, en.z, 40, 12, 0, 0, TAU);
            S.stroke();
          }
        }
        S.restore();
        g.hfxDrawn = (g.hfxDrawn || 0) + live;
      };
      // 미션 보상 — 하늘에서 내려오는 빛기둥 속 아이템(1.4초)
      const drawR31Pick = (g, S) => {
        const K = g.r31pick;
        const t = (performance.now() - K.t0) / 1400;
        if (t >= 1) {
          g.r31pick = null;
          return;
        }
        const p = g.player;
        const I = R31_ITEMS[K.id];
        const IT = frameAssets.items && frameAssets.items["mission_" + K.id];
        const a = t < 0.15 ? t / 0.15 : t > 0.7 ? (1 - t) / 0.3 : 1;
        const w = 70 * (1 - 0.4 * t);
        S.save();
        S.globalCompositeOperation = "lighter";
        S.globalAlpha = a * 0.75;
        S.drawImage(getGlowSprite(I.col), p.x - w, p.z - 470, w * 2, 480);
        S.globalAlpha = a * 0.9;
        S.drawImage(getGlowSprite("#ffffff"), p.x - w * 0.3, p.z - 440, w * 0.6, 440);
        S.globalCompositeOperation = "source-over";
        const u = Math.min(1, t / 0.55);
        const iy = p.z - p.y - 300 + 200 * (1 - (1 - u) * (1 - u));
        const sz = 58 * (t > 0.7 ? 1 - (t - 0.7) / 0.3 * 0.6 : 1);
        S.globalAlpha = a;
        if (IT) S.drawImage(IT.img, p.x - sz / 2, iy - sz / 2, sz, sz);
        else {
          S.fillStyle = I.col;
          S.beginPath();
          S.arc(p.x, iy, sz * 0.32, 0, TAU);
          S.fill();
        }
        S.restore();
      };
      // 전선 미션 배너(왼쪽 위 주인공 패널 바로 아래 · 작게 — 가운데 스테이지 패널 · 기술 해금 배너와 겹치지 않게) + 보상 버프 남은 시간
      const drawR31Mission = (g, c) => {
        const M = g.mission;
        const x0 = 8;
        let y0 = 84;
        c.save();
        c.textBaseline = "middle";
        c.textAlign = "left";
        if (M) {
          const D = R31_MISSIONS[M.key];
          const age = M.state === "run" ? 0 : g.tick - M.tEnd;
          if (D && age < 170) {
            const W = 268;
            const H = 40;
            const ok = M.state === "ok";
            const bad = M.state === "fail";
            c.globalAlpha = age > 140 ? (170 - age) / 30 : 1;
            c.fillStyle = "rgba(9,13,22,0.84)";
            c.beginPath();
            c.roundRect(x0, y0, W, H, 8);
            c.fill();
            c.strokeStyle = ok ? "#fde047" : bad ? "#64748b" : "#22d3ee";
            c.lineWidth = 1.6;
            c.stroke();
            const IT = frameAssets.items && frameAssets.items["mission_" + D.item];
            if (IT) c.drawImage(IT.img, x0 + 5, y0 + 4, 32, 32);
            let pr;
            if (ok) pr = "✔ 임무 완수";
            else if (bad) pr = "✖ 임무 실패";
            else if (M.key === "jurchen") pr = `${M.prog}/${D.need} · ${Math.max(0, Math.ceil((D.time - (g.tick - M.t0)) / 60))}초`;
            else if (M.key === "redturban") pr = `피격 ${M.hits}/${D.need}`;
            else pr = `${Math.max(0, M.prog)}/${D.need}`;
            c.fillStyle = ok ? "#fde047" : bad ? "#94a3b8" : "#67e8f9";
            c.font = "900 12px system-ui, sans-serif";
            c.fillText(`⚔ ${D.title} · ${pr}`, x0 + 44, y0 + 12);
            c.fillStyle = "#e2e8f0";
            c.font = "700 11px system-ui, sans-serif";
            c.fillText(ok ? `보상: ${R31_ITEMS[D.item].name} 획득!` : D.goal, x0 + 44, y0 + 28);
            y0 += 46;
          }
        }
        const B = g.r31buff;
        if (B) {
          const L = [];
          if (B.seal > 0) L.push(["seal", B.seal]);
          if (B.banner > 0) L.push(["banner", B.banner]);
          if (B.blade > 0) L.push(["blade", B.blade]);
          let x = x0;
          c.globalAlpha = 1;
          for (let i = 0; i < L.length; i++) {
            const id = L[i][0];
            const IT = frameAssets.items && frameAssets.items["mission_" + id];
            c.fillStyle = "rgba(9,13,22,0.8)";
            c.beginPath();
            c.roundRect(x, y0, 58, 26, 6);
            c.fill();
            if (IT) c.drawImage(IT.img, x + 2, y0 + 1, 24, 24);
            c.fillStyle = R31_ITEMS[id].col;
            c.font = "900 11px system-ui, sans-serif";
            c.fillText(`${Math.ceil(L[i][1] / 60)}s`, x + 30, y0 + 13);
            x += 62;
          }
        }
        c.restore();
      };
      const drawFx3dPass = (g, back, S0) => {''')

# ───────── 9. 검증 훅 ─────────
rep('''          auraStage: () => auraStageOf(gameRef.current),''', '''          auraStage: () => auraStageOf(gameRef.current),
          // [R31] 검증 훅: 타격 이펙트 풀 · 전선 · 미션 · 보상 · 해모수 신화 · 김원봉 연출
          r31: () => {
            const g = gameRef.current;
            let live = 0;
            for (let i = 0; i < R31_HFX_N; i++) if (R31_HFX[i].on) live++;
            return { hfxLive: live, hfxSeen: Object.assign({}, R31_HFX_SEEN), hfxDrawn: g.hfxDrawn || 0, hitFxN: g.hitFxN || 0, front: g.front4 || null, frontLog: (g.frontLog || []).slice(), mission: g.mission ? Object.assign({}, g.mission) : null, missionLog: (g.missionLog || []).slice(), buff: Object.assign({}, g.r31buff || {}), itemLog: (g.itemLog || []).slice(), artFx: g.artFxCount || 0, artLive: (g.artFx || []).length, e2: { cleaves: g.e2Cleaves || 0, slams: g.e2Slams || 0, summons: g.e2Summons || 0, skySwords: g.e2SkySwords || 0, halo: !!g.r31halo }, e6: { throws: g.uiyeolThrows || 0, blasts: g.uiyeolBlasts || 0, mauser: g.mauserShots || 0, airMauser: g.airMauser || 0, shadow: g.shadowGhosts || 0, officers: g.officerSpawns || 0, officerDowns: g.officerDowns || 0, specials: g.uiyeolSpecials || 0 } };
          },
          // 실제 피해 경로(applyDamageToEnemy)로 화면의 일반 적을 모두 처치 — heavy = 강타(미션 · 이펙트 판정 검증)
          r31killAll: (heavy) => {
            const g = gameRef.current;
            let k = 0;
            g.enemies.forEach((en) => {
              if (en.state === "DYING" || en.state === "SPAWN" || en.isMidBoss) return;
              en.hp = 1;
              en.guardTimer = 0;
              applyDamageToEnemy(en, 1, 4, 0, heavy ? 2 : 1, !!heavy, 1);
              k++;
            });
            return k;
          },
          r31autoQuiz: (v) => setAutoPassQuiz(!!v),
          r31front: (k) => r31EnterFront(k),
          r31mission: (k) => r31StartMission(k),
          r31missionEnd: (ok) => r31MissionEnd(gameRef.current, ok),
          r31item: (id) => r31GiveItem(id),
          r31bomb: (pw) => r31ThrowBomb(pw || 1),
          r31officer: () => r31SpawnOfficer(gameRef.current.player.x + 220, gameRef.current.player.z, 1),
          r31ult: () => {
            gameRef.current.stats.ult = 100;
            triggerTrueAwakeningUlt();
          },''')

open(P, "w", encoding="utf-8").write(s)
print("R31 patch ok —", n, "edits")
