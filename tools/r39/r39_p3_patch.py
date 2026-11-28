#!/usr/bin/env python3
"""R39 Phase 3 — 10스테이지 확장 + 한능검 연표 암기 시스템. Phase 2 결과(shinsi-R39/index.html) 위에 적용.

사용: python -I tools/r39/r39_p3_patch.py shinsi-R39/index.html   (P1 → P2 뒤에)
규칙: 앵커는 정확히 count번 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R39 P3] 주석. 에셋 · MANIFEST 변경 없음.

설계(원칙: 기존 6시대의 원화 · 전투 · 보스 · 배경 · 효과음 엔진은 '기본 시대 era'로 그대로):
  스테이지 층 R39_STAGES(1~10 · tools/r39/r39_stages.js) — era 매핑 1·2·3·3·4·4·5·5·6·6. R39_CUR_STAGE(최상위) · g.stage · HUD r39StageUi.
  진행: advanceToNextEraImmediate → r39SetStage(+1)(10 뒤 광복 엔딩) · switchEraDirectly 는 DEV 시대 버튼 · engineReset 때 그 시대의 첫 스테이지로 동기화.
  이름표: eraObjOf · HUD eraData · 시대 토스트가 스테이지 덮어쓰기(이름 · fieldName · heroTitle · bossName …)를 본다 · 중간보스 · 병종 이름표 · 로밍 해설 · 유물 각성 퀴즈 문항도 스테이지별.
  연표 두문자 바: 구역 라벨 그리드를 [두문자] 이름 + 연도(클리어 시 금빛)로 · 모바일(compact)에서도 표시.
  시공 순서 봉인(SEAL_TRIAL): spawnEraBoss 직전 5초 타임어택 — 사건 카드(≤4)를 순서대로 터치 · 성공 = 방어막(phaseInv) 파괴 · 3초 그로기 · 공격 +25%(1800틱) / 실패 = 광폭화(공격 ×1.3 · 속도 ×1.15 · 붉은 링).
  퀴즈 보강: QUIZ_BANK · HARD_QUIZ_BANK 에 남북국 · 후삼국 통일 · 동학 순서 · 무장 독립전쟁 순서 문항 추가.
"""
import os
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0
HERE = os.path.dirname(os.path.abspath(__file__))
STAGES = open(os.path.join(HERE, "r39_stages.js"), encoding="utf-8").read().rstrip("\n")


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 1. 최상위: 스테이지 데이터 · 헬퍼 ─────────
rep('''  var r39GuardUnit = (en) => {''', STAGES + '''
  var R39_CUR_STAGE = 1;
  var R39_FIRST_STAGE_OF_ERA = { 1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 9 };
  var r39Stage = (st) => R39_STAGES[st || R39_CUR_STAGE] || R39_STAGES[1];
  var R39_ERA_OBJ_CACHE = {};
  // 시대 객체 + 스테이지 덮어쓰기(이름 · fieldName · heroTitle · bossName …). 같은 시대를 쓰는 스테이지끼리 캐시가 따로다
  var r39EraObjFor = (era, stage) => {
    const base = ERAS_DATA[era - 1] || ERAS_DATA[0];
    const S = R39_STAGES[stage];
    if (!S || S.era !== era || !S.over) return base;
    const key = stage + ":" + era;
    if (!R39_ERA_OBJ_CACHE[key]) R39_ERA_OBJ_CACHE[key] = Object.assign({}, base, S.over);
    return R39_ERA_OBJ_CACHE[key];
  };
  var r39ZoneLabels = (stage) => (r39Stage(stage).zones || []).map((z) => ({ label: "[" + z.b + "] " + z.name, year: z.year, b: z.b, name: z.name }));
  var r39ZoneNames = (stage) => r39ZoneLabels(stage).map((z) => z.label);
  var r39UnitLabel = (U, en) => {
    const S = r39Stage();
    const L = S.units && en && en.unit && S.units[en.unit];
    return L || U.name;
  };
  var r39MidName = (M, zi, field) => {
    const S = r39Stage();
    const o = S.mids && S.mids[zi];
    return o && o[field] || M[field];
  };
  var r39MidQuizList = (era) => {
    const S = r39Stage();
    const base = MID_UPGRADE_QUIZZES[era] || [];
    if (!S.midQuiz) return base;
    return base.map((q, i) => S.midQuiz[i] ? Object.assign({}, q, S.midQuiz[i], { id: q.id + "_s" + S.id, badge: "🔨 유물 각성 퀴즈 (STAGE " + S.id + " · " + (i + 1) + "차 돌파)" }) : q);
  };
  // 시공 순서 봉인 상수 — 5초 · 카드 4 · 성공: 공격 +25% 1800틱 · 그로기 180틱 / 실패: 공격 ×1.3 · 속도 ×1.15
  var R39_SEAL = { sec: 5, cards: 4, atk: 1.25, buffTicks: 1800, groggy: 180, enrageDmg: 1.3, enrageSpd: 1.15 };
  var r39GuardUnit = (en) => {''')
rep('''  var zoneNamesFor = (era) => ZONE_NAMES_ERA[era] || ZONE_NAMES;''', '''  var zoneNamesFor = (era) => r39Stage().zones ? r39ZoneNames() : ZONE_NAMES_ERA[era] || ZONE_NAMES; // [R39 P3] 연표 구역 이름''')

# ───────── 2. 퀴즈 뱅크 보강(시험 · 하드) — 데이터(R39_QUIZ_EXTRA)가 정의된 뒤(1절 삽입 자리)에서 덧붙이고 크기를 다시 센다 ─────────
rep('''  var R39_SEAL = { sec: 5, cards: 4, atk: 1.25, buffTicks: 1800, groggy: 180, enrageDmg: 1.3, enrageSpd: 1.15 };''', '''  var R39_SEAL = { sec: 5, cards: 4, atk: 1.25, buffTicks: 1800, groggy: 180, enrageDmg: 1.3, enrageSpd: 1.15 };
  // [R39 P3] 10스테이지 구성에 맞춘 문항 보강(남북국 · 후삼국 통일 · 동학 순서 · 무장 독립전쟁 순서) — 기본 시대 뱅크에 덧붙이고 크기를 다시 센다(QUIZ_BANK_SIZE 는 위에서 먼저 계산됨)
  Object.keys(R39_QUIZ_EXTRA).forEach((e) => (QUIZ_BANK[e] = QUIZ_BANK[e] || []).push(...R39_QUIZ_EXTRA[e]));
  Object.keys(R39_HARD_EXTRA).forEach((e) => (HARD_QUIZ_BANK[e] = HARD_QUIZ_BANK[e] || []).push(...R39_HARD_EXTRA[e]));
  QUIZ_BANK_SIZE = Object.values(QUIZ_BANK).reduce((n, list) => n + list.length, 0);
  HARD_QUIZ_SIZE = Object.values(HARD_QUIZ_BANK).reduce((n, list) => n + list.length, 0);''')

# ───────── 3. React 상태 · 시대 객체 · HUD ─────────
rep('''    const [r39ModeUi, setR39ModeUi] = useState(R39_MODE); // [R39 P2] 타이틀 난이도 선택(표시용)''', '''    const [r39ModeUi, setR39ModeUi] = useState(R39_MODE); // [R39 P2] 타이틀 난이도 선택(표시용)
    const [r39StageUi, setR39StageUi] = useState(1); // [R39 P3] 지금 스테이지(HUD · 연표 바)
    const [sealTrial, setSealTrial] = useState(null); // [R39 P3] 시공 순서 봉인''')
rep('''    const eraData = ERAS_DATA[currentEra - 1] || ERAS_DATA[0];''', '''    const eraData = r39EraObjFor(currentEra, r39StageUi); // [R39 P3] 스테이지 이름표''')
rep('''    const eraObjOf = () => ERAS_DATA[gameRef.current.era - 1] || ERAS_DATA[0];''', '''    const eraObjOf = () => r39EraObjFor(gameRef.current.era, R39_CUR_STAGE); // [R39 P3] 시대 객체 + 스테이지 덮어쓰기''')
rep('''      const eObj = ERAS_DATA[currentEra - 1] || ERAS_DATA[0];''', '''      const eObj = r39EraObjFor(currentEra, R39_CUR_STAGE); // [R39 P3]''')

# ───────── 4. 스테이지 전환 · 진행 ─────────
rep('''      const eObj = ERAS_DATA[targetEra - 1] || ERAS_DATA[0];''', '''      // [R39 P3] DEV 시대 버튼 · engineReset 에서 바로 부르면 그 시대의 첫 스테이지로 동기화(r39SetStage 가 부를 땐 잠금)
      if (!g._r39stageLock) {
        R39_CUR_STAGE = R39_FIRST_STAGE_OF_ERA[targetEra] || 1;
        g.stage = R39_CUR_STAGE;
        g.r39sealDone = false;
        g.r39sealPending = null;
        setR39StageUi(R39_CUR_STAGE);
      }
      const eObj = r39EraObjFor(targetEra, R39_CUR_STAGE);''')
rep('''    const advanceToNextEraImmediate = () => {''', '''    // [R39 P3] 스테이지 전환 — 기본 시대로 switchEraDirectly 한 뒤 스테이지 층(이름표 · 연표 · 해설 · 퀴즈)을 올린다
    const r39SetStage = (st) => {
      const g = gameRef.current;
      const S = R39_STAGES[st];
      if (!S) return R39_CUR_STAGE;
      R39_CUR_STAGE = st;
      g.stage = st;
      g.r39sealDone = false;
      g.r39sealPending = null;
      g.r39sealBuff = null;
      g._r39stageLock = true;
      switchEraDirectly(S.era);
      g._r39stageLock = false;
      setR39StageUi(st);
      (g.r39stageLog || (g.r39stageLog = [])).push({ stage: st, era: S.era, tick: g.tick });
      return st;
    };
    const advanceToNextEraImmediate = () => {''')
rep('''      if (g.era < 6) {
        switchEraDirectly(g.era + 1);
        g.stats.atk += 110;
        r39SoftCap(g.stats, g.era); // [R39 P2] 시대별 공격력 소프트 캡''', '''      if (R39_CUR_STAGE < 10) { // [R39 P3] 10스테이지 — 마지막은 광복 엔딩
        r39SetStage(R39_CUR_STAGE + 1);
        g.stats.atk += 110;
        r39SoftCap(g.stats, g.era); // [R39 P2] 시대별 공격력 소프트 캡''')

# ───────── 5. 연표 두문자 바 ─────────
rep('''gameState !== "TITLE" && !(compact && !devMode) && /* @__PURE__ */ React.createElement("div", { className: "grid grid-cols-4 gap-1" }, zoneNamesFor(currentEra).map((zn, zi) => {''', '''gameState !== "TITLE" && /* @__PURE__ */ React.createElement("div", { className: "grid grid-cols-4 gap-1", "data-testid": "timeline-bar" }, r39ZoneLabels(r39StageUi).map((zo, zi) => {
          const zn = zo.label; // [R39 P3] 연표 두문자 바 — 모바일에서도 보이고, 클리어한 구역은 금빛 + 연도''')
rep('''            zn
          );
        }))''', '''            zn,
            done && zo.year ? /* @__PURE__ */ React.createElement("span", { className: "ml-0.5 text-[8px] text-amber-200/90" }, zo.year) : null
          );
        }))''')
# HUD 왼쪽 위 "STAGE N" — 시대 번호(1~6)가 아니라 스테이지 번호(1~10). 1시대(석장리)는 기존 1-1/1-2 코드 유지
rep('''getSeokjangriStageConfig(hud.zone).code : `STAGE ${currentEra}`)''', '''getSeokjangriStageConfig(hud.zone).code : `STAGE ${r39StageUi}`)''')

# ───────── 6. 이름표: 병종 · 중간보스 · 해설 · 퀴즈 ─────────
rep('''overlay.push((o) => drawTextSprite(o, U.name, tx, ty,''', '''overlay.push((o) => drawTextSprite(o, r39UnitLabel(U, en), tx, ty,''')
rep('''          name: M.name,
          title: M.title,''', '''          name: r39MidName(M, g.zoneIdx, "name"), // [R39 P3] 스테이지별 중간보스 이름표
          title: r39MidName(M, g.zoneIdx, "title"),''')
rep('''      const T = (R38B_STORY[era] && R38B_STORY[era][zi] || [])[k] || null;''', '''      const SS = r39Stage().story || R38B_STORY[era]; // [R39 P3] 스테이지별 해설(없으면 시대 해설)
      const T = (SS && SS[zi] || [])[k] || null;''')
rep('''      const list = MID_UPGRADE_QUIZZES[g.era];''', '''      const list = r39MidQuizList(g.era); // [R39 P3] 스테이지별 문항(보상은 시대 것)''')

# ───────── 7. 시공 순서 봉인 ─────────
rep('''    const spawnEraBoss = () => {''', '''    // [R39 P3] 시공 순서 봉인 — 보스 조우 직전 5초 타임어택: 이 스테이지의 사건 카드를 일어난 순서대로 터치(키보드 1~4). 그동안 세계는 멈춘다(stepUpdate 는 PLAYING 아닐 때 return)
    const sealTimerRef = useRef(null);
    const r39SealCards = () => {
      const S = r39Stage();
      const ev = (S.events || S.zones || []).map((z, i) => ({ k: i, name: z.name, year: z.year, b: z.b }));
      return ev.slice(0, Math.min(R39_SEAL.cards, ev.length));
    };
    const openSealTrial = () => {
      const g = gameRef.current;
      const take = r39SealCards();
      if (take.length < 3) return false;
      const cards = take.slice().sort(() => Math.random() - 0.5);
      if (cards.every((c, i) => c.k === take[i].k)) cards.reverse();
      const trial = { stage: R39_CUR_STAGE, cards, picked: [], phase: "ask", t0: performance.now(), ms: R39_SEAL.sec * 1000 };
      g.r39seal = trial;
      setSealTrial(trial);
      setStateNow("SEAL_TRIAL");
      clearTimeout(sealTimerRef.current);
      sealTimerRef.current = setTimeout(() => finishSealTrial(false, "time"), trial.ms);
      g.r39sealOpened = (g.r39sealOpened || 0) + 1;
      sfx("alarm");
      return true;
    };
    const finishSealTrial = (pass, why) => {
      const g = gameRef.current;
      const T = g.r39seal;
      if (!T || T.phase !== "ask") return;
      clearTimeout(sealTimerRef.current);
      T.phase = pass ? "pass" : "fail";
      T.why = why;
      T.pass = pass;
      setSealTrial(Object.assign({}, T));
      g.r39sealResult = { stage: T.stage, pass, why, ms: Math.round(performance.now() - T.t0) };
      (g.r39sealLog || (g.r39sealLog = [])).push(g.r39sealResult);
      sfx(pass ? "levelup" : "hurt");
      setTimeout(() => {
        const gg = gameRef.current;
        setSealTrial(null);
        gg.r39seal = null;
        if (syncRef.current.gameState === "SEAL_TRIAL") setStateNow("PLAYING");
        gg.r39sealPending = pass ? "pass" : "fail";
        spawnEraBoss();
      }, 1400);
    };
    const answerSealTrial = (i) => {
      const g = gameRef.current;
      const T = g.r39seal;
      if (!T || T.phase !== "ask" || syncRef.current.gameState !== "SEAL_TRIAL") return;
      if (i < 0 || i >= T.cards.length || T.picked.includes(i)) return;
      T.picked = T.picked.concat([i]);
      const order = T.cards.map((c) => c.k).slice().sort((a, b) => a - b);
      const okSoFar = T.cards[i].k === order[T.picked.length - 1];
      setSealTrial(Object.assign({}, T));
      if (!okSoFar) return finishSealTrial(false, "order");
      if (T.picked.length === T.cards.length) finishSealTrial(true, "done");
    };
    const answerSealRef = useRef(null);
    answerSealRef.current = answerSealTrial;
    // 봉인 결과를 보스에게 — 성공: 방어막(phaseInv) 파괴 · 3초 그로기 · 공격 +25% / 실패: 광폭화
    const r39ApplySeal = (res) => {
      const g = gameRef.current;
      const b = g.boss;
      if (!b || !res) return;
      if (res === "pass") {
        b.phaseInv = 0;
        b.hitStun = Math.max(b.hitStun || 0, R39_SEAL.groggy);
        b.windupTimer = 0;
        g.r39sealBuff = { until: g.tick + R39_SEAL.buffTicks, atk: R39_SEAL.atk };
        addDamagePopup(b.x, b.z, b.y + 90, "봉인 해제!", true, "방어막 파괴 · 3초 그로기 · 공격력 +25%", 0, "#fde047");
        r38Hfx(23, b.x, b.z, 600, 1, 0, 2.4, "#fde047", 0);
        g.flashAlpha = Math.max(g.flashAlpha, 0.3);
        g.flashColor = "#fde68a";
      } else {
        b.r39enraged = true;
        b.dmgMult = (b.dmgMult || 1) * R39_SEAL.enrageDmg;
        if (typeof b.speed === "number") b.speed *= R39_SEAL.enrageSpd;
        if (b.attackCooldown) b.attackCooldown = Math.max(20, Math.round(b.attackCooldown * 0.85));
        addDamagePopup(b.x, b.z, b.y + 90, "광폭화!", true, "봉인 실패 — 공격 ×1.3 · 속도 ×1.15", 0, "#f43f5e");
        g.flashAlpha = Math.max(g.flashAlpha, 0.35);
        g.flashColor = "#f43f5e";
      }
      (g.r39sealApplied || (g.r39sealApplied = [])).push({ stage: R39_CUR_STAGE, res, tick: g.tick });
    };
    const spawnEraBoss = () => {
      {
        const g0 = gameRef.current;
        // [R39 P3] 보스 조우 직전 봉인 타임어택 — 결과(r39sealPending)가 있으면 보스가 생긴 직후 적용
        if (!g0.bossActive && !g0.r39sealDone && !g0.r39sealPending && syncRef.current.gameState === "PLAYING" && !syncRef.current.autoPassQuiz && openSealTrial()) {
          g0.r39sealDone = true;
          return;
        }
        const res0 = g0.r39sealPending;
        g0.r39sealPending = null;
        g0.r39sealDone = true;
        if (res0) addTimer(2, () => r39ApplySeal(res0));
      }''')
rep('''(g.legend ? LEGEND_ATK : 1)''', '''(g.legend ? LEGEND_ATK : 1) * (g.r39sealBuff && g.tick < g.r39sealBuff.until ? g.r39sealBuff.atk : 1)''')
rep('''    const r39TickAll = (g) => {''', '''    const r39TickAll = (g) => {
      if (g.boss && g.boss.r39enraged && !g.boss.dying && g.tick % 24 === 0) r38Hfx(23, g.boss.x, g.boss.z, 700, 1, 0, 2, "#f43f5e", 0); // [R39 P3] 광폭화 오라''')
rep('''        if (syncRef.current.gameState === "REVIVE_EXAM") {''', '''        if (syncRef.current.gameState === "SEAL_TRIAL") {
          // [R39 P3] 시공 순서 봉인 — 키보드 1~4
          if (k >= "1" && k <= "4" && k.length === 1) {
            e.preventDefault();
            if (answerSealRef.current) answerSealRef.current(Number(k) - 1);
          }
          return;
        }
        if (syncRef.current.gameState === "REVIVE_EXAM") {''')
rep('''      })(), gameState === "REVIVE_EXAM" && reviveExam && (() => {''', '''      })(), gameState === "SEAL_TRIAL" && sealTrial && (() => {
        // [R39 P3] 시공 순서 봉인 오버레이 — 5초 바 · 사건 카드(터치 · 1~4) · 결과
        const T = sealTrial;
        const NUM = ["①", "②", "③", "④"];
        const fb = T.phase !== "ask";
        return /* @__PURE__ */ React.createElement("div", { className: "fixed inset-0 z-50 bg-slate-950/90 flex items-center justify-center p-3", "data-testid": "seal-trial" }, /* @__PURE__ */ React.createElement(
          "div",
          { className: "w-full max-w-sm bg-slate-900 border-2 border-amber-400/70 rounded-2xl p-4 text-center" },
          /* @__PURE__ */ React.createElement("div", { className: "text-[11px] font-black text-amber-300 tracking-widest" }, "⏳ 시공 순서 봉인 · " + R39_SEAL.sec + "초"),
          /* @__PURE__ */ React.createElement("div", { className: "mt-1 text-sm font-black text-white" }, "방금 지난 사건을 일어난 순서대로 터치!"),
          /* @__PURE__ */ React.createElement("div", { className: "mt-2 h-1.5 bg-slate-800 rounded-full overflow-hidden" }, /* @__PURE__ */ React.createElement("div", { className: "h-full bg-amber-400", style: { animation: fb ? "none" : `r39seal ${T.ms}ms linear forwards` } })),
          /* @__PURE__ */ React.createElement("div", { className: "mt-3 grid grid-cols-2 gap-2" }, T.cards.map((c, i) => {
            const picked = T.picked.indexOf(i) >= 0;
            return /* @__PURE__ */ React.createElement(
              "button",
              { key: i, "data-seal-card": i, onClick: () => answerSealTrial(i), disabled: fb || picked, className: `py-3 px-2 rounded-xl border-2 text-[12px] font-black leading-tight ${picked ? "bg-amber-400 text-slate-950 border-amber-200" : "bg-slate-800 text-slate-100 border-slate-600 active:scale-95"}` },
              /* @__PURE__ */ React.createElement("div", null, NUM[i], " ", c.name),
              picked || fb ? /* @__PURE__ */ React.createElement("div", { className: "text-[10px] font-bold opacity-80" }, c.year) : null
            );
          })),
          fb ? /* @__PURE__ */ React.createElement("div", { className: `mt-3 text-sm font-black ${T.pass ? "text-emerald-300" : "text-rose-300"}` }, T.pass ? "봉인 해제! 보스 방어막 파괴 · 3초 그로기 · 공격력 +25%" : (T.why === "time" ? "시간 초과 — " : "순서가 달라요 — ") + "보스가 광폭화합니다!") : /* @__PURE__ */ React.createElement("div", { className: "mt-3 text-[10px] font-bold text-slate-400" }, "키보드 1~4 로도 고를 수 있어요")
        ));
      })(), gameState === "REVIVE_EXAM" && reviveExam && (() => {''')
rep('''  /* [R39] iOS 핫픽스(커밋 d9247a9)는 tools/r39/ios_hotfix_r38-2b.diff 로 보존 · 빌드마다 tools/r39/check39.py 가 표식을 검사한다. 제스처 차단은 아래 ios-zoom-v2 한 곳 */''', '''  /* [R39] iOS 핫픽스(커밋 d9247a9)는 tools/r39/ios_hotfix_r38-2b.diff 로 보존 · 빌드마다 tools/r39/check39.py 가 표식을 검사한다. 제스처 차단은 아래 ios-zoom-v2 한 곳 */
  @keyframes r39seal { from { width: 100%; } to { width: 0%; } } /* [R39 P3] 시공 순서 봉인 5초 바 */''')

# ───────── 8. DEV 훅 ─────────
rep('''          r39revive: () => {''', '''          // [R39 P3] 검증: 스테이지 워프 · 스테이지 표 · 봉인 강제 열기/답하기 · 봉인 기록
          r39stage: (st) => {
            const g = gameRef.current;
            if (st) {
              r39SetStage(st);
              g.stats.hp = g.stats.maxHp;
            }
            const S = r39Stage();
            return { stage: R39_CUR_STAGE, era: g.era, name: eraObjOf().name, fieldName: eraObjOf().fieldName, heroTitle: eraObjOf().heroTitle, bossName: eraObjOf().bossName, zones: r39ZoneLabels(R39_CUR_STAGE), hasStory: !!S.story, midQuiz: r39MidQuizList(g.era).map((q) => q.title), log: (g.r39stageLog || []).slice(-3) };
          },
          r39stages: () => Object.values(R39_STAGES).map((S) => ({ id: S.id, era: S.era, zones: S.zones.map((z) => z.b).join("-"), name: S.over && S.over.name || null })),
          r39seal: () => openSealTrial(),
          r39sealAnswer: (i) => answerSealTrial(i),
          r39sealState: () => {
            const g = gameRef.current;
            return { open: !!g.r39seal, trial: g.r39seal ? { stage: g.r39seal.stage, cards: g.r39seal.cards.map((c) => c.k), picked: g.r39seal.picked.slice(), phase: g.r39seal.phase } : null, result: g.r39sealResult || null, applied: (g.r39sealApplied || []).slice(-3), pending: g.r39sealPending || null, done: !!g.r39sealDone, buff: g.r39sealBuff || null, boss: g.boss ? { hitStun: g.boss.hitStun, phaseInv: g.boss.phaseInv, enraged: !!g.boss.r39enraged, dmgMult: g.boss.dmgMult } : null, quizSizes: { bank: QUIZ_BANK_SIZE, hard: HARD_QUIZ_SIZE } };
          },
          r39revive: () => {''')

open(P, "w", encoding="utf-8").write(s)
print("R39 P3 patch ok —", n, "edits")
