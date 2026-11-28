#!/usr/bin/env python3
"""R39 Phase 2 — 전투 밸런스 전면 개편(무쌍 × D&D2 하이브리드). Phase 1 결과(shinsi-R39/index.html) 위에 적용.

사용: python -I tools/r39/r39_p2_patch.py shinsi-R39/index.html   (P1 뒤에)
규칙: 앵커는 정확히 count번 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R39] 주석. R38-2A 밸런스 상수(R38_HP_K 등)는 그대로 두고 곱한다.

1. 난이도 2트랙(타이틀에서 선택 · localStorage "shinsi.mode" · 최상위 R39_MODE):
   musou  무쌍 모드(스토리 · 초등): 체력 ×1.0 · 적 공격 ×1.0 · 정면 가드 경감 50% · 콤보 브레이크 40 HIT · 패링 각성 +25 · 드롭 ×1.0
   jeongsa 정사 모드(D&D2 · 한능검): 체력 ×1.2 · 적 공격 ×1.25 · 정면 가드 경감 75% · 콤보 브레이크 25 HIT · 패링 각성 +40 · 드롭 ×0.6
2. 시대별 공격력 소프트 캡: 다음 시대 진입 때 atk = 기준(210 + 110×(시대−1)) + 초과분의 15% · awakenedTier ≤ 1.45(각성 1단계만 이월) → 11,835 ATK 폭증 차단.
   구역 리듬: Z1 체력 ×1.15 · 적 공격 ×1.1(빡빡) → Z2 · Z3 ×0.9(퀴즈 · 유물 각성 뒤 폭딜) → Z4 보스 ×1.0(패턴 공략).
3. 무한 콤보 차단 · 패링 유도:
   콤보 브레이크 — 같은 적에게 90틱 안 연속 N HIT(모드별 40/25) → 붉은 섬광 · 슈퍼아머 48틱(피해 50% · 경직 · 넉백 · 띄우기 없음) · 주인공 튕겨내기 + 즉시 반격(공격 간격 0).
   가드 브레이크 병종 — 방패(shield) · 철갑(heavy) · 기병(mounted) · 정예(elite) · 장교(OFFICER): 정면 평타 피해 경감(모드별 50/75%).
     저스트 패링 · 어퍼(L) · 돌진(K) · 갈래/공중 기술 · 등 뒤 공격 · 카운터 · 치명 확정 공격이면 자세 붕괴(BREAK 180틱) → 정상 · 추가 피해.
   저스트 패링 보상 — 반경 300 · 경직 ×2 · 가드 브레이크 병종 BREAK · 각성 게이지 모드별 +25/+40 · 90틱 확정 크리티컬 반격 창구(g.r39ParryCrit).
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


# ───────── 1. 최상위 상수 · 모드 · 소프트 캡 ─────────
rep('''  var R39_REVIVE_PENALTY = 0.25;''', '''  var R39_REVIVE_PENALTY = 0.25;
  // [R39 P2] 난이도 2트랙 — 타이틀에서 고른다(localStorage "shinsi.mode"). 게임 로직은 R39_MODES[R39_MODE]만 본다
  var R39_MODES = {
    musou: { key: "musou", name: "무쌍 모드", sub: "스토리 · 초등", tag: "무쌍", hp: 1, dmg: 1, guardDR: 0.5, comboBreak: 40, parryUlt: 25, drop: 1, color: "#f59e0b" },
    jeongsa: { key: "jeongsa", name: "정사 모드", sub: "D&D2 · 한능검", tag: "정사", hp: 1.2, dmg: 1.25, guardDR: 0.75, comboBreak: 25, parryUlt: 40, drop: 0.6, color: "#a78bfa" }
  };
  var R39_MODE = (() => {
    try {
      const m = window.localStorage.getItem("shinsi.mode");
      return R39_MODES[m] ? m : "musou";
    } catch (e) {
      return "musou";
    }
  })();
  var r39Mode = () => R39_MODES[R39_MODE] || R39_MODES.musou;
  var r39SetMode = (m) => {
    if (!R39_MODES[m]) return R39_MODE;
    R39_MODE = m;
    try {
      window.localStorage.setItem("shinsi.mode", m);
    } catch (e) {}
    return R39_MODE;
  };
  // [R39 P2] 구역 리듬: Z1 빡빡(D&D2) → Z2 · Z3 폭딜(무쌍) → Z4 보스 패턴
  var R39_ZONE_K = [{ hp: 1.15, dmg: 1.1 }, { hp: 0.9, dmg: 1 }, { hp: 0.9, dmg: 1 }, { hp: 1, dmg: 1 }];
  // [R39 P2] 시대별 공격력 소프트 캡 — 다음 시대 진입 때 기준 전투력으로 되돌리되 초과분 15% · 각성 1단계(1.45)만 이월
  var R39_SOFTCAP = { excessKeep: 0.15, awakenKeep: 1.45 };
  var r39SoftCap = (st, era) => {
    const base = 210 + 110 * (era - 1);
    const before = st.atk;
    const excess = Math.max(0, st.atk - base);
    st.atk = base + Math.round(excess * R39_SOFTCAP.excessKeep);
    st.awakenedTier = Math.min(st.awakenedTier || 1, R39_SOFTCAP.awakenKeep);
    st.powerAtEraStart = st.atk + st.level * 38;
    st.r39cap = { era, before, after: st.atk, awaken: st.awakenedTier };
    return st.r39cap;
  };
  // [R39 P2] 콤보 브레이크 · 가드 브레이크 상수
  var R39_COMBO_BREAK = { window: 90, armor: 48, armorDmg: 0.5, push: 16 };
  var R39_BREAK_T = 180;
  var r39GuardUnit = (en) => {
    if (!en || en.isMidBoss) return false;
    const S = en.unit ? UNIT_SPECS[en.unit] : null;
    return !!(en.elite || S && (S.tactic === "shield" || S.tactic === "heavy" || S.mounted) || en.unit && /OFFICER/.test(en.unit));
  };''')

# ───────── 2. 체력 · 공격력 배율(모드 · 구역 리듬) · 드롭 ─────────
rep('''    hpK *= entity.isMidBoss ? R38_HP_K.mid : isBoss ? R38_HP_K.boss : R38_HP_K.mob; // [R38-2A] 체력 배율(1시대 포함)''', '''    hpK *= entity.isMidBoss ? R38_HP_K.mid : isBoss ? R38_HP_K.boss : R38_HP_K.mob; // [R38-2A] 체력 배율(1시대 포함)
    // [R39 P2] 난이도 모드 × 구역 리듬(보스 · 중간보스는 구역 배율 제외 — 보스전은 패턴으로)
    {
      const M9 = r39Mode();
      const Z9 = isBoss || entity.isMidBoss ? null : R39_ZONE_K[Math.max(0, Math.min(3, zoneIdx || 0))];
      hpK *= M9.hp * (Z9 ? Z9.hp : 1);
      dmgK *= M9.dmg * (Z9 ? Z9.dmg : 1);
      entity.r39k = { mode: M9.key, hp: +(M9.hp * (Z9 ? Z9.hp : 1)).toFixed(3), dmg: +(M9.dmg * (Z9 ? Z9.dmg : 1)).toFixed(3) };
    }''')
rep('''      } else if (Math.random() < 0.6) {
        g.buffOrbs.push({ x: en.x, z: en.z, anim: 0 });''', '''      } else if (Math.random() < 0.6 * r39Mode().drop) { // [R39 P2] 정사 모드는 드롭 ×0.6(자원 관리)
        g.buffOrbs.push({ x: en.x, z: en.z, anim: 0 });''')

# ───────── 3. 소프트 캡(다음 시대 진입) ─────────
rep('''        switchEraDirectly(g.era + 1);
        g.stats.atk += 110;''', '''        switchEraDirectly(g.era + 1);
        g.stats.atk += 110;
        r39SoftCap(g.stats, g.era); // [R39 P2] 시대별 공격력 소프트 캡''')

# ───────── 4. 콤보 브레이크 · 가드 브레이크 · 패링 창구(App 안 도우미) ─────────
rep('''    const r38bFlair = (g, p, fin) => {''', '''    // [R39 P2] 타격 전처리 — ① 슈퍼아머 중이면 피해 50% ② 같은 적 연속 HIT 수(90틱 창) → 임계면 콤보 브레이크 ③ 가드 브레이크 병종의 정면 평타 경감 / 브레이커면 자세 붕괴 ④ 패링 반격 창구 = 확정 크리티컬
    const r39PreHit = (g, target, dir, ratio, forceCrit) => {
      const M9 = r39Mode();
      const p = g.player;
      let crit = g.r39ParryCrit > g.tick;
      if (target.superArmor > 0) ratio *= R39_COMBO_BREAK.armorDmg;
      if (g.tick - (target._cbT != null ? target._cbT : -999) > R39_COMBO_BREAK.window) target._cbN = 0;
      target._cbN = (target._cbN || 0) + 1;
      target._cbT = g.tick;
      if (target._cbN >= M9.comboBreak && !(target.superArmor > 0) && target.state !== "DYING") r39ComboBreak(g, target, dir);
      if (r39GuardUnit(target) && !(target.guardTimer > 0)) {
        const frontal = target.facing === -dir;
        const src = p._atkSrc;
        const breaker = !!forceCrit || crit || target.windupTimer > 0 || src === "dash" || src === "upper" || src === "branch" || src === "air" || !frontal || g._r31par;
        if (target.breakT > 0) {
          // 자세 붕괴 중: 정상 피해 + 10% 추가
          ratio *= 1.1;
        } else if (breaker) {
          target.breakT = R39_BREAK_T;
          target.hitStun = Math.max(target.hitStun || 0, 36);
          target.superArmor = 0;
          g.r39breaks = (g.r39breaks || 0) + 1;
          addDamagePopup(target.x, target.z, target.y + 24, "BREAK!", true, !frontal ? "등 뒤" : null, 0, "#fb7185");
          r38Hfx(23, target.x, target.z, 360, dir, 0, 1.3, "#fb7185", 0);
          sfx("cutArmor", { v: 0.9 });
        } else {
          ratio *= 1 - M9.guardDR;
          g.r39guarded = (g.r39guarded || 0) + 1;
          if (g.tick - (target._gdT || -99) > 20) {
            target._gdT = g.tick;
            addDamagePopup(target.x, target.z, target.y + 20, "GUARD", false, `정면 −${Math.round(M9.guardDR * 100)}%`, 0, "#94a3b8");
            spawnSparks(target.x - dir * 14, target.z, target.y + 44, 3, -dir);
          }
        }
      }
      g.r39last = { unit: target.unit || target.mobRole || (target === g.boss ? "boss" : null), frontal: target.facing === -dir, src: p._atkSrc, ratio: +ratio.toFixed(3), crit, armor: target.superArmor || 0, brk: target.breakT || 0, cb: target._cbN || 0, tick: g.tick };
      return { ratio, crit };
    };
    // 콤보 브레이크 — 붉은 섬광 · 슈퍼아머 48틱 · 주인공을 튕겨내고 곧바로 반격(공격 간격 0 · 예고 짧게)
    const r39ComboBreak = (g, target, dir) => {
      const p = g.player;
      target.superArmor = R39_COMBO_BREAK.armor;
      target._cbN = 0;
      target.hitStun = 0;
      target.vx = 0;
      target.thrown = null;
      target.state = target.state === "KNOCKDOWN" ? "ACTIVE" : target.state;
      if (target.attackCooldown != null) target.attackCooldown = 0;
      p.vx = -dir * R39_COMBO_BREAK.push;
      p.flinch = Math.max(p.flinch || 0, 8);
      if (p.pendingHit && p.pendingHit.cancelable) {
        p.pendingHit = null;
        p.attackTimer = 0;
      }
      g.flashAlpha = Math.max(g.flashAlpha, 0.35);
      g.flashColor = "#f43f5e";
      g.hitStop = Math.max(g.hitStop, 4);
      addTrauma(0.3);
      kickDirShake(g, -dir, 7);
      addDamagePopup(target.x, target.z, target.y + 70, "COMBO BREAK!", true, "슈퍼아머 · 반격", 0, "#f43f5e");
      r38Hfx(23, target.x, target.z, 480, dir, 0, 1.8, "#f43f5e", 0);
      r38Hfx(24, target.x, target.z - (target.y || 0) - 50, 180, dir, Math.random() * TAU, 1.6, "#f43f5e", 14);
      g.r39comboBreaks = (g.r39comboBreaks || 0) + 1;
      sfx("bossRoar", { v: 0.6, r: 1.3 });
    };
    // 틱마다: 슈퍼아머 · 자세 붕괴 타이머
    const r39TickAll = (g) => {
      for (let i = 0; i < g.enemies.length; i++) {
        const e = g.enemies[i];
        if (e.superArmor > 0) e.superArmor--;
        if (e.breakT > 0) e.breakT--;
      }
      if (g.boss) {
        if (g.boss.superArmor > 0) g.boss.superArmor--;
        if (g.boss.breakT > 0) g.boss.breakT--;
      }
    };
    const r38bFlair = (g, p, fin) => {''')
rep('''      const dir = dirOverride !== null ? dirOverride : g.player.facing;''', '''      const dir = dirOverride !== null ? dirOverride : g.player.facing;
      // [R39 P2] 콤보 브레이크 · 가드 브레이크 · 패링 반격 창구(피해 배율 · 확정 크리티컬)
      {
        const r9 = r39PreHit(g, target, dir, dmgRatio, forceCrit);
        dmgRatio = r9.ratio;
        if (r9.crit) forceCrit = true;
      }''')
rep('''      target.vx = dir * knockX * kMul;''', '''      if (!(target.superArmor > 0)) target.vx = dir * knockX * kMul; // [R39 P2] 슈퍼아머 중엔 넉백 없음''')
rep('''      if (launchY > 0) {
        const ly = launchY * (target.isMidBoss ? 0.3 : heavy ? 0.7 : 1);''', '''      if (launchY > 0 && !(target.superArmor > 0)) { // [R39 P2] 슈퍼아머 중엔 띄우기 없음
        const ly = launchY * (target.isMidBoss ? 0.3 : heavy ? 0.7 : 1);''')
rep('''      target.hitStun = Math.max(target.hitStun || 0, target.isMidBoss ? 5 : heavy ? 13 : 24);''', '''      if (!(target.superArmor > 0)) target.hitStun = Math.max(target.hitStun || 0, target.isMidBoss ? 5 : heavy ? 13 : 24); // [R39 P2] 슈퍼아머 중엔 경직 없음''')
rep('''        if (g.zoneState === "ROAM" || g.zoneState === "GO") {''', '''        r39TickAll(g); // [R39 P2] 슈퍼아머 · 자세 붕괴 타이머
        if (g.zoneState === "ROAM" || g.zoneState === "GO") {''')

# ───────── 5. 저스트 패링 보상 ─────────
rep('''      g.parryCount = (g.parryCount || 0) + 1;''', '''      g.parryCount = (g.parryCount || 0) + 1;
      // [R39 P2] 패링 보상 상향 — 반경 300 경직(기본의 2배) · 가드 브레이크 병종 자세 붕괴 · 각성 게이지 모드별 추가 · 90틱 확정 크리티컬 반격 창구
      {
        const M9 = r39Mode();
        st.ult = Math.min(100, st.ult + M9.parryUlt);
        g.r39ParryCrit = g.tick + 90;
        for (let i = 0; i < g.enemies.length; i++) {
          const en = g.enemies[i];
          if (en.state === "DYING" || en.state === "SPAWN") continue;
          if (Math.abs(en.x - p.x) < 300 && Math.abs(en.z - p.z) < 90) {
            en.hitStun = Math.max(en.hitStun || 0, PARRY_STUN * 2);
            en.superArmor = 0;
            if (r39GuardUnit(en)) en.breakT = Math.max(en.breakT || 0, R39_BREAK_T);
          }
        }
        if (g.boss && !g.boss.dying && Math.abs(g.boss.x - p.x) < 300) g.boss.hitStun = Math.max(g.boss.hitStun || 0, 20);
        addDamagePopup(p.x, p.z, p.y + 96, "반격 창구!", true, `각성 +${M9.parryUlt} · 확정 크리티컬 1.5초`, 0, "#f0abfc");
      }''')

# ───────── 6. 타이틀 모드 선택 · HUD 표기 ─────────
rep('''    const [stageToast, setStageToast] = useState(null);''', '''    const [stageToast, setStageToast] = useState(null);
    const [r39ModeUi, setR39ModeUi] = useState(R39_MODE); // [R39 P2] 타이틀 난이도 선택(표시용)''')
rep('''        /* @__PURE__ */ React.createElement(
          "button",
          {
            onClick: startGame,
            className: "w-full max-w-xs py-4 rounded-2xl bg-gradient-to-r from-amber-400 via-amber-500 to-orange-500 text-slate-950 font-black text-base tracking-[0.3em] shadow-lg active:scale-95"
          },''', '''        /* [R39 P2] 난이도 2트랙 — 무쌍(스토리 · 초등) / 정사(D&D2 · 한능검). 선택은 localStorage에 남는다 */
        /* @__PURE__ */ React.createElement(
          "div",
          { className: "w-full max-w-xs grid grid-cols-2 gap-2", "data-testid": "mode-select" },
          Object.values(R39_MODES).map((M) => /* @__PURE__ */ React.createElement(
            "button",
            {
              key: M.key,
              onClick: () => {
                sfx("ui");
                setR39ModeUi(r39SetMode(M.key));
              },
              "data-mode": M.key,
              "aria-pressed": r39ModeUi === M.key,
              className: `py-2 rounded-xl border font-black text-[11px] leading-tight active:scale-95 ${r39ModeUi === M.key ? "bg-slate-100 text-slate-950 border-white" : "bg-slate-900/70 text-slate-300 border-slate-600"}`
            },
            /* @__PURE__ */ React.createElement("div", null, M.name),
            /* @__PURE__ */ React.createElement("div", { className: "text-[9px] font-bold opacity-70" }, M.sub)
          ))
        ),
        /* @__PURE__ */ React.createElement(
          "button",
          {
            onClick: startGame,
            className: "w-full max-w-xs py-4 rounded-2xl bg-gradient-to-r from-amber-400 via-amber-500 to-orange-500 text-slate-950 font-black text-base tracking-[0.3em] shadow-lg active:scale-95"
          },''')
rep('''/* @__PURE__ */ React.createElement("span", { className: "text-slate-400" }, "HI "''', '''/* @__PURE__ */ React.createElement("span", { className: "text-[9px] px-1.5 rounded-full border", style: { color: r39Mode().color, borderColor: r39Mode().color }, "data-testid": "mode-tag" }, r39Mode().tag), /* @__PURE__ */ React.createElement("span", { className: "text-slate-400" }, "HI "''')

# ───────── 7. DEV 훅 ─────────
rep('''          r39revive: () => {''', '''          // [R39 P2] 검증: 모드 바꾸기 · 밸런스 상태(소프트 캡 · 콤보 브레이크 · 가드 · 패링 창구) · 패링 강제
          r39mode: (m) => {
            if (m) r39SetMode(m);
            return { mode: R39_MODE, cfg: Object.assign({}, r39Mode()) };
          },
          r39bal: () => {
            const g = gameRef.current;
            const st = g.stats;
            return { mode: R39_MODE, atk: st.atk, awakenedTier: st.awakenedTier, cap: st.r39cap || null, last: g.r39last || null, comboBreaks: g.r39comboBreaks || 0, breaks: g.r39breaks || 0, guarded: g.r39guarded || 0, parryCritLeft: Math.max(0, (g.r39ParryCrit || 0) - g.tick), zoneK: R39_ZONE_K, enemies: g.enemies.map((e) => ({ unit: e.unit || e.mobRole, hp: e.hp, maxHp: e.maxHp, cb: e._cbN || 0, armor: e.superArmor || 0, brk: e.breakT || 0, k: e.r39k || null })) };
          },
          r39parry: () => justParry(),
          r39revive: () => {''')

open(P, "w", encoding="utf-8").write(s)
print("R39 P2 patch ok —", n, "edits")
