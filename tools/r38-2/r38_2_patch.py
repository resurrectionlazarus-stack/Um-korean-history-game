#!/usr/bin/env python3
"""R38-2A 「입력 잠김 수정 + 전투 밸런스 + 로밍 스폰」 — shinsi-R38/index.html 위에 문자열 치환으로 적용.

사용: cp shinsi-R38/index.html shinsi-R38-2/index.html && python -I tools/r38-2/r38_2_patch.py shinsi-R38-2/index.html
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R38-2A] 주석. 앵커는 모두 ASCII 코드 줄.
보존(절대 손대지 않음 — tools/r38/guard38.py shinsi-R38 shinsi-R38-2 로 확인): 권율 걸음걸이 구간 · R37 엔진/훅 · 효과음 · MANIFEST.

① 입력 잠김(실플레이: 평타 · 일부 공격 키 무반응)
   원인 A: 질풍연참(rushSlash) 마무리 콜백(취소 불가 pendingHit)이 p.rush를 풀어 주는데, 연참 중 어퍼(L)가 pendingHit 한 칸을 덮어써 콜백이 사라짐
           → p.rush 영구 고착 → triggerEraWeaponCombo(J) · triggerEraDashSkill(K)이 입구에서 return. 어퍼만 살아 있음.
   원인 B: 키 판정이 e.key뿐이라 한/영 전환 뒤 글자 키(J K L U I E Q WASD)가 모두 무시됨(Space · 방향키만 삼).
   수정: 어퍼에 rush/plunge 가드 · queueActiveFrame은 취소 불가 콜백을 덮어쓰지 않음 · e.code 우선 키 정규화 · blur 때 bufferAtk 해제 ·
         틱 감시 r38LockWatch(rush 150틱 · plunge 지상 20틱 · special 240틱 · attackTimer max+40 · pendingHit 120틱 · guardTimer 180틱 · 죽은 적 grab · bufferAtk 60틱)
② 밸런스: R38_HP_K { mob 2.2 · mid 1.5 · boss 1.35 }(1시대 곰 hpMult 16 → 24) · 일반 몹 공격 간격 ×0.85(스폰 · 재장전 2곳 · 1시대 짐승) · 중간보스 공격 간격 0.78 → 0.72 ·
         ACTIVE_CAP 전 시대 7. 적 공격력 · 피격 배율 · 웨이브 표는 그대로.
③ 로밍 스폰: 구역 사이 걷는 구간에 시대당 7지점(Z1→Z2 2 · Z2→Z3 2 · Z3→Z4 3) × 3명(증원 2 오른쪽 밖 · 매복 1 왼쪽 밖) · 동시 로밍 4명 상한 · 격파 목표 +21.
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


# ───────── 1. 최상위 상수 · 키 정규화 ─────────
rep('''  var r38MapX = (x) => Math.round(x * R38_MAP_K);''', '''  var r38MapX = (x) => Math.round(x * R38_MAP_K);
  // [R38-2A] 키 정규화 — 한/영 전환 · Shift · CapsLock과 무관하게 물리 키(e.code)로 글자 · 숫자를 읽는다(없으면 e.key). 합성 이벤트도 code를 주면 같다
  var r38KeyNorm = (e) => {
    const c = e.code || "";
    if (c.length === 4 && c.startsWith("Key")) return c[3].toLowerCase();
    if (c.length === 6 && c.startsWith("Digit")) return c[5];
    return (e.key || "").toLowerCase();
  };
  // [R38-2A] 로밍 스폰 — 시대당 7지점 × 3명 = 21(격파 목표에 가산)
  var R38_ROAM_PTS = [[], [0.35, 0.7], [0.35, 0.7], [0.3, 0.55, 0.8]];
  var R38_ROAM_N = 3;
  var R38_ROAM_TOTAL = 21;
  var R38_ROAM_CAP = 4;''')

# ───────── 2. 키 핸들러(keydown · keyup) · blur ─────────
rep('''        const k = e.key.toLowerCase();''', '''        const k = r38KeyNorm(e); // [R38-2A] e.code 우선(한/영 전환에도 글자 키가 산다)''', 2)
rep('''        keys.left = keys.right = keys.up = keys.down = false;''', '''        keys.left = keys.right = keys.up = keys.down = false;
        // [R38-2A] 창을 떠날 때 버퍼된 공격도 비운다
        const pl = gameRef.current.player;
        if (pl) pl.bufferAtk = false;''')

# ───────── 3. 어퍼(L): 질풍연참 · 내리꽂기 중 금지(돌진과 같은 가드) ─────────
rep('''    const triggerEraUpperSkill = () => {
      if (syncRef.current.gameState !== "PLAYING" || gameRef.current.player.downTimer > 0 || gameRef.current.player.guardTimer > 0) return;
      const g = gameRef.current;
      const p = g.player;''', '''    const triggerEraUpperSkill = () => {
      if (syncRef.current.gameState !== "PLAYING" || gameRef.current.player.downTimer > 0 || gameRef.current.player.guardTimer > 0) return;
      const g = gameRef.current;
      const p = g.player;
      // [R38-2A] 질풍연참 · 내리꽂기 중 어퍼 금지 — 연참 마무리 콜백(pendingHit)을 덮어써 p.rush가 영구 고착되던 원인
      if (p.rush || p.plunge) {
        r38LockNote(g, "upperDuringRush");
        return;
      }''')

# ───────── 4. pendingHit 한 칸 보호 + 입력 잠김 감시 ─────────
rep('''    const queueActiveFrame = (delay, fn, cancelable = true) => {
      gameRef.current.player.pendingHit = { t: delay, fn, cancelable };
    };''', '''    // [R38-2A] 입력 잠김 감시 — 비정상으로 오래 남은 상태를 풀고 g.r38lock에 기록한다(원인 수정 뒤의 안전장치 · __RELIC_DEV.r38lock())
    const R38_LOCK_MAX = { rush: 150, plunge: 20, special: 240, attack: 40, pending: 120, guard: 180, buffer: 60 };
    const r38LockNote = (g, k) => {
      const L = g.r38lock || (g.r38lock = {});
      L[k] = (L[k] || 0) + 1;
      L.last = k;
      L.tick = g.tick;
    };
    const r38LockWatch = (g, p) => {
      if (p.rush) {
        if (p.rush.t0 == null) p.rush.t0 = g.tick;
        if (g.tick - p.rush.t0 > R38_LOCK_MAX.rush) {
          p.rush = null;
          p.comboStep = 0;
          r38LockNote(g, "rush");
        }
      }
      if (p.plunge && p.y <= 0) {
        p._plungeGround = (p._plungeGround || 0) + 1;
        if (p._plungeGround > R38_LOCK_MAX.plunge) {
          p.plunge = false;
          p._plungeGround = 0;
          r38LockNote(g, "plunge");
        }
      } else p._plungeGround = 0;
      if (g.special && g.tick - (g.special.tick0 || 0) > R38_LOCK_MAX.special) {
        g.special = null;
        r38LockNote(g, "special");
      }
      if (p.attackTimer > (p.maxAttackTimer || 0) + R38_LOCK_MAX.attack) {
        p.attackTimer = 0;
        r38LockNote(g, "attack");
      }
      if (p.pendingHit && p.pendingHit.t > R38_LOCK_MAX.pending) {
        p.pendingHit = null;
        r38LockNote(g, "pending");
      }
      if (p.guardTimer > R38_LOCK_MAX.guard) {
        p.guardTimer = 0;
        r38LockNote(g, "guard");
      }
      if (p.grab && (!p.grab.en || p.grab.en.state === "DYING" || g.enemies.indexOf(p.grab.en) < 0)) {
        releaseGrab(g, p, false);
        r38LockNote(g, "grab");
      }
      if (p.bufferAtk) {
        p._bufT = (p._bufT || 0) + 1;
        if (p._bufT > R38_LOCK_MAX.buffer) {
          p.bufferAtk = false;
          p._bufT = 0;
          r38LockNote(g, "buffer");
        }
      } else p._bufT = 0;
    };
    const queueActiveFrame = (delay, fn, cancelable = true) => {
      const pl = gameRef.current.player;
      // [R38-2A] 취소 불가 콜백(질풍연참 마무리 등)이 걸려 있으면 일반 공격 · 기술이 덮어쓰지 않는다 — 덮어쓰면 p.rush 해제 콜백이 사라져 입력이 영구 잠겼다
      if (pl.pendingHit && pl.pendingHit.cancelable === false && cancelable) {
        r38LockNote(gameRef.current, "queueRefused");
        return;
      }
      pl.pendingHit = { t: delay, fn, cancelable };
    };''')
rep('''      p.rush = { k: 0 };''', '''      p.rush = { k: 0, t0: g.tick }; // [R38-2A] 시작 틱(입력 감시 150틱 상한)''')
rep('''          p.pendingHit.t--;''', '''          p.pendingHit.t--; // [R38-2A] 감시는 아래 r38LockWatch''')
rep('''        if (p.pendingHit) {
          p.pendingHit.t--; // [R38-2A] 감시는 아래 r38LockWatch''', '''        r38LockWatch(g, p); // [R38-2A] 입력 잠김 감시(rush · plunge · special · attackTimer · pendingHit · guard · grab · buffer)
        if (p.pendingHit) {
          p.pendingHit.t--;''')

# ───────── 5. 밸런스 ─────────
rep('''  var R27_MOB_HP_K = 0.72;''', '''  var R27_MOB_HP_K = 0.72;
  // [R38-2A] '양학' 해소 — 일반 몹 체력 ×2.2(Lv.5 T3 기준 1콤보 → 2~3콤보) · 중간보스 ×1.5 · 시대 보스 ×1.35 · 일반 몹 공격 간격 ×0.85 · 중간보스 공격 간격 0.78 → 0.72
  //  적 공격력(ERA_DIFF) · 피격 배율(PLAYER_DMG_TAKEN) · 웨이브 표는 그대로(어린이 기준). 손잡이는 이 셋.
  var R38_HP_K = { mob: 2.2, mid: 1.5, boss: 1.35 };
  var R38_MOB_CD_K = 0.85;
  var R38_MID_CD = 0.72;''')
rep('''    if (!isBoss && !entity.isMidBoss) hpK *= R27_MOB_HP_K;''', '''    if (!isBoss && !entity.isMidBoss) hpK *= R27_MOB_HP_K;
    hpK *= entity.isMidBoss ? R38_HP_K.mid : isBoss ? R38_HP_K.boss : R38_HP_K.mob; // [R38-2A] 체력 배율(1시대 포함)''')
rep('''      const cdK = era >= 2 && !entity.isMidBoss ? R25_BOSS_CD : 0.78;''', '''      const cdK = era >= 2 && !entity.isMidBoss ? R25_BOSS_CD : R38_MID_CD; // [R38-2A] 중간보스 0.78 → 0.72''')
rep('''        attackCooldown: chain != null ? chain : S ? 46 + Math.floor(Math.random() * 30) : 40 + Math.random() * 25,''', '''        attackCooldown: chain != null ? chain : Math.round((S ? 46 + Math.floor(Math.random() * 30) : 40 + Math.random() * 25) * R38_MOB_CD_K), // [R38-2A] 첫 공격 간격 ×0.85''')
rep('''          en.attackCooldown = 58 + Math.floor(Math.random() * 20);''', '''          en.attackCooldown = Math.round((58 + Math.floor(Math.random() * 20)) * R38_MOB_CD_K); // [R38-2A]''')
rep('''        en.attackCooldown = UNIT_CD[tactic] + Math.floor(Math.random() * 24);''', '''        en.attackCooldown = Math.round((UNIT_CD[tactic] + Math.floor(Math.random() * 24)) * R38_MOB_CD_K); // [R38-2A] 재장전 ×0.85''')
rep('''                  en.attackCooldown = en.baseAttackCd || (en.elite ? 34 : 46);''', '''                  en.attackCooldown = Math.round((en.baseAttackCd || (en.elite ? 34 : 46)) * R38_MOB_CD_K); // [R38-2A] 1시대 짐승 재장전 ×0.85''')
rep('''      hpMult: 16,''', '''      hpMult: 24, // [R38-2A] 16 × 1.5(중간보스 배율과 같이)''')
rep('''  var ACTIVE_CAP = { 2: 7, 4: 7 };''', '''  var ACTIVE_CAP = { 2: 7, 3: 7, 4: 7, 5: 7, 6: 7 }; // [R38-2A] 전 시대 동시 7명(3 · 5 · 6시대 Z3 8명도 대기열로 — 60fps 보호)''')

# ───────── 6. 로밍 스폰 ─────────
rep('''    const r31HitBurst = (g, en, dir, hv, fin, vr) => {''', '''    // [R38-2A] 로밍 스폰 — 구역 사이 걷는 구간(1.5배로 늘어난 공백)에 매복 · 증원. 구역 zi(1~3)로 가는 길: 앞 구역 범위 끝 ~ 트리거 사이 비율 지점을 넘으면
    //  오른쪽 화면 밖 증원 2 + 왼쪽 화면 밖 매복 1(동시 로밍 4명 상한). 카메라 잠금 없음 · 격파 수는 그대로 인정(목표에 +21). 1시대는 늑대 · 하이에나.
    const r38Roam = (g, p) => {
      const zi = g.zoneIdx;
      if (zi < 1 || zi > 3 || g.bossActive) return;
      const pts = R38_ROAM_PTS[zi];
      const x0 = ZONE_CAM[zi - 1] + r38ZoneSpan(zi - 1);
      const x1 = ZONE_TRIG[zi];
      const done = g.r38roam || (g.r38roam = {});
      for (let k = 0; k < pts.length; k++) {
        const key = zi + ":" + k;
        if (done[key]) continue;
        const px = x0 + (x1 - x0) * pts[k];
        if (p.x < px) continue;
        done[key] = true;
        let roam = 0;
        for (let i = 0; i < g.enemies.length; i++) if (g.enemies[i].roam && g.enemies[i].state !== "DYING") roam++;
        const n = Math.max(0, Math.min(R38_ROAM_N, R38_ROAM_CAP - roam));
        const roles = ["WOLF", "HYENA", "WOLF"];
        for (let i = 0; i < n; i++) {
          const right = i < 2;
          const x = right ? g.cameraX + VIEW_W + 70 + i * 60 : g.cameraX - 80;
          const o = { flank: right ? 1 : -1 };
          if (g.era === 1) o.role = roles[i];
          spawnEnemyAt(x, 360 + Math.random() * 110, o);
          const en = g.enemies[g.enemies.length - 1];
          if (en) en.roam = true;
        }
        (g.r38roamLog || (g.r38roamLog = [])).push({ zone: zi, k, x: Math.round(px), n, tick: g.tick });
        if (n && !(g.era >= 2 && r37WarCry(n))) sfx("alarm");
      }
    };
    const r31HitBurst = (g, en, dir, hv, fin, vr) => {''')
rep('''          if (g.zoneIdx < 4 && p.x > ZONE_TRIG[g.zoneIdx]) engageZone(g.zoneIdx);''', '''          if (g.zoneIdx < 4 && p.x > ZONE_TRIG[g.zoneIdx]) engageZone(g.zoneIdx);
          else r38Roam(g, p); // [R38-2A] 구역 사이 로밍 스폰(매복 · 증원)''')
rep('''    if (era === 1) k += 1;''', '''    if (era === 1) k += 1;
    k += R38_ROAM_TOTAL; // [R38-2A] 로밍 스폰 21명''')

# ───────── 7. 점검 훅 ─────────
rep('''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),''', '''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),
          // [R38-2A] 검증: 입력 잠김 감시 카운터 + 지금 잠금 상태 · 밸런스 상수 · 로밍 기록 · 몹 표본 체력
          r38lock: () => {
            const g = gameRef.current;
            const p = g.player;
            return { counts: Object.assign({}, g.r38lock || {}), flags: { rush: !!p.rush, plunge: !!p.plunge, special: !!g.special, attackTimer: p.attackTimer, maxAttackTimer: p.maxAttackTimer, pending: !!p.pendingHit, pendingCancelable: p.pendingHit ? p.pendingHit.cancelable : null, guardTimer: p.guardTimer, grab: !!p.grab, bufferAtk: !!p.bufferAtk, downTimer: p.downTimer, comboStep: p.comboStep, lastAtkPress: g.lastAtkPress, tick: g.tick } };
          },
          r382: (unit) => {
            const g = gameRef.current;
            let sample = null;
            if (unit) {
              const n0 = g.enemies.length;
              spawnEnemyAt(g.cameraX + VIEW_W + 300, 420, { unit, keepPos: true });
              const en = g.enemies[g.enemies.length - 1];
              if (g.enemies.length > n0 && en) {
                sample = { unit, maxHp: en.maxHp, attackCooldown: en.attackCooldown, speed: +en.speed.toFixed(2), dmgMult: +en.dmgMult.toFixed(2) };
                g.enemies.pop();
              }
            }
            return { hpK: Object.assign({}, R38_HP_K), mobCdK: R38_MOB_CD_K, midCd: R38_MID_CD, cap: Object.assign({}, ACTIVE_CAP), roam: { pts: R38_ROAM_PTS, n: R38_ROAM_N, total: R38_ROAM_TOTAL, cap: R38_ROAM_CAP, done: Object.assign({}, g.r38roam || {}), log: (g.r38roamLog || []).slice() }, killGoal: eraKillGoal(g.era), sample };
          },''')

open(P, "w", encoding="utf-8").write(s)
print("R38-2A patch ok —", n, "edits")
