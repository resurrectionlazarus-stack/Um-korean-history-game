#!/usr/bin/env python3
"""R38-2B 「주인공 동작 확장 + 1.5배 구간 한국사 해설 · 매복 경고」 — shinsi-R38-2/index.html 위에 문자열 치환으로 적용.

사용: cp shinsi-R38-2/index.html shinsi-R38-2B/index.html && python -I tools/r38-2b/r38_2b_patch.py shinsi-R38-2B/index.html
규칙: 앵커(옛 원문)는 정확히 count번 나와야 함 — 아니면 즉시 멈춤. 바꾼 곳마다 // [R38-2B] 주석. 앵커는 모두 ASCII 코드 줄.
보존(절대 손대지 않음 — tools/r38/guard38.py shinsi-R38-2 shinsi-R38-2B 로 확인): 권율 걸음걸이 구간 · R37 엔진/훅 · 효과음 · MANIFEST ·
  R38-2A 밸런스 상수(R38_HP_K · R38_MOB_CD_K · R38_MID_CD · ACTIVE_CAP · 로밍 수).

① 주인공 동작 확장(신규 이미지 없음 · 기존 프레임 + 포즈 변환 + 고정 풀 FX)
   A. 이동 갈래 기술 — 방향키를 '막 누른'(10틱 안 · 자동 반복 제외) 채 공격: 공격하던 쪽 = 진격 베기(advance · atk2 · 전진 가속) · 반대쪽 = 회피 베기(retreat · atk1 · 적을 향한 채 뒤로 빠지며 · 무적 8틱).
      사슬은 이어진다(comboStep = min(N-1, pos)). 평소 달리며 치는 공격은 그대로(탭 판정).
   B. 피니시 플러리시 — 마지막 타(Lv.3+ 4타 · Lv.1~2 3타) 적중 순간 잔상 3 · 히트스톱 · 쉐이크 · 줌 1.04 · 마지막 프레임 6틱 잔심(_r31pose) · 시대별 FX(R38 고정 풀 · 할당 0).
   C. 연참 변주 — 시대별 전진량 · 잔상 · 먼지(R38B_RUSH).
   입력 잠금 계약: 새 콜백은 모두 cancelable(기본값) · 타이머 ≤ 18틱 · _brLock은 사슬이 끝나면 조용히 해제 + 90틱 상한 감시 · _r31pose 상한 감시 · r38lock() 플래그 노출.
② 1.5배 구간 서사 — 로밍 지점 발동 직후 주인공 위 매복 경고(70틱) → 30틱 뒤 단비 현장 해설(170틱). 시대당 지점마다 1회 · 말풍선은 덮어쓰기(겹침 없음) · 입력 · 일시정지와 무관.
③ R38-2A 결함 수정 — 로밍 발동 키 zi:k → era:zi:k(2시대부터 로밍이 안 뜨던 것) · 로밍 로그 상한 50.
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


STORY = '''  // [R38-2B] 1.5배 구간 단비 현장 해설 — [시대][가는 구역 zi 1~3][지점 k] · 초등 한국사 눈높이 1~2문장. 연도 · 인물 · 사건은 사실대로,
  //  보스 대결(거대 산군 · 소정방 vs 김유신 · 용골대 vs 권율 · 기갑 대장군)은 '게임 설정'. 바꾸려면 이 표만.
  var R38B_STORY = {
    1: {
      1: ["📜 석장리 사람들은 돌을 깨서 만든 주먹도끼로 사냥하고 가죽을 손질했어요. 불을 피워 추위도 이겨 냈지요.", "📜 구석기 사람들은 한곳에 오래 머물지 않고 먹을 것을 찾아 옮겨 다녔어요. 동굴과 바위 그늘이 집이었답니다."],
      2: ["📜 빙하기가 끝나고 날씨가 따뜻해지자 사람들은 강가에 모여 살기 시작했어요. 금강을 따라가면 신석기 마을이에요!", "📜 신석기 사람들은 돌을 갈아 더 날카로운 간석기를 만들고, 빗살무늬 토기에 음식을 담았어요."],
      3: ["📜 신석기 마을에서는 조와 수수를 심어 농사를 짓고 개와 돼지를 길렀어요. 움집에 모여 살았지요.", "📜 뼈바늘로 옷을 짓고 가락바퀴로 실을 뽑았어요. 조개껍데기로 목걸이도 만들었답니다.", "📜 거대한 짐승의 발자국이 보여요(게임 설정). 돌창과 간돌도끼를 믿고 마을을 지켜요!"]
    },
    2: {
      1: ["📜 고조선은 단군왕검이 세운 우리 역사 최초의 나라예요. 8조법으로 나라의 질서를 지켰지요.", "📜 기원전 3세기, 연나라 장수 진개가 쳐들어와 고조선은 서쪽 땅을 잃었어요. 패수 나루 쪽으로 물러나요!"],
      2: ["📜 기원전 194년, 연나라에서 건너온 위만이 준왕을 몰아내고 고조선의 왕이 됐어요. 철기 문화가 더 퍼졌지요.", "📜 고조선의 비파형 동검과 세형 동검은 우리 문화의 상징이에요. 왕검성이 가까워요!"],
      3: ["📜 기원전 109년, 한나라 무제가 큰 군대를 보내 고조선을 공격했어요. 1년 넘게 왕검성을 지켰답니다.", "📜 고조선 사람들은 성을 지키며 끝까지 싸웠어요. 하지만 안에서 분열이 생기고 말았지요.", "📜 기원전 108년 왕검성이 무너졌어요. 그래도 고조선의 문화는 여러 나라로 이어졌답니다!"]
    },
    3: {
      1: ["📜 660년, 신라와 당나라 연합군이 백제를 공격했어요. 황산벌에서 계백의 5천 결사대와 맞섰지요.", "📜 화랑 관창은 어린 나이에도 용감히 싸워 신라군의 사기를 높였어요. 황산벌이 가까워요!"],
      2: ["📜 백제가 무너진 뒤 신라는 고구려로 향했어요. 연개소문은 당나라의 침입을 여러 번 막아 낸 고구려의 지도자예요.", "📜 645년 안시성 싸움에서 고구려 백성들은 당 태종의 대군을 물리쳤어요. 성을 지키는 힘을 기억하세요!"],
      3: ["📜 668년 평양성이 함락되며 고구려가 무너졌어요. 하지만 당나라는 신라까지 차지하려 했지요.", "📜 신라는 당나라와 싸워 676년 매소성 · 기벌포 싸움에서 이겼어요. 삼국 통일을 이룬 거예요!", "📜 당나라 장수 소정방의 군대가 앞에 있어요(게임 설정). 김유신 장군, 마지막 싸움이에요!"]
    },
    4: {
      1: ["📜 993년 서희는 거란 장수 소손녕과 담판해 강동 6주를 얻었어요. 말로 나라를 지킨 거예요!", "📜 1019년 귀주대첩에서 강감찬 장군이 거란의 10만 대군을 크게 물리쳤어요. 이제 여진의 동북 9성으로 가요."],
      2: ["📜 1107년 윤관은 별무반을 이끌고 여진을 몰아내 동북 9성을 쌓았어요. 기병 신기군이 큰 힘이 됐지요.", "📜 여진은 1115년 금나라를 세웠어요. 고려는 평화를 지키려 애썼답니다. 앞쪽은 몽골 전선이에요!"],
      3: ["📜 1231년부터 30년 가까이 몽골이 여러 번 쳐들어왔어요. 고려는 강화도로 도읍을 옮기며 버텼지요.", "📜 1232년 처인성에서 승려 김윤후와 백성들이 몽골 장수 살리타이를 물리쳤어요.", "📜 1361년 홍건적이 개경을 빼앗았지만 이듬해 고려군이 되찾았어요. 개경 결전이에요!"]
    },
    5: {
      1: ["📜 1592년 임진왜란이 일어났어요. 이순신 장군의 수군과 곳곳의 의병이 나라를 지켰지요.", "📜 1593년 행주산성에서 권율 장군과 백성들이 화차로 왜군을 막아 냈어요. 행주대첩이에요!"],
      2: ["📜 전쟁 뒤 조선은 무너진 성과 마을을 다시 세웠어요. 하지만 북쪽에서 새 위협이 다가왔지요.", "📜 1636년 겨울, 청나라 군대가 얼어붙은 강을 건너 쳐들어왔어요. 병자호란의 시작이에요. 눈길을 조심하세요!"],
      3: ["📜 인조 임금은 남한산성에서 47일을 버텼어요. 추위와 굶주림 속에서도 성을 지켰지요.", "📜 1637년 삼전도에서 조선은 청나라에 항복했어요. 아픈 역사지만 기억해야 해요.", "📜 청나라 장수 용골대의 기마대가 앞에 있어요(게임 설정). 도원수 권율, 마지막 싸움이에요!"]
    },
    6: {
      1: ["📜 1866년 병인양요 — 프랑스 군함이 강화도로 쳐들어왔어요. 외규장각의 책들도 빼앗겼지요.", "📜 정족산성에서 양헌수 장군의 부대가 프랑스군을 물리쳤어요. 강화도를 지킨 거예요!"],
      2: ["📜 1871년 신미양요 — 이번엔 미국 군함이 강화도에 왔어요. 어재연 장군이 광성보에서 맞섰지요.", "📜 광성보의 병사들은 끝까지 싸웠어요. 빼앗겼던 어재연 장군의 깃발 '수자기'는 2007년에 돌아왔답니다."],
      3: ["📜 1919년 3월 1일, 온 나라가 '대한 독립 만세'를 외쳤어요. 그해 대한민국 임시정부도 세워졌답니다.", "📜 1920년 봉오동과 청산리에서 독립군이 일본군을 크게 이겼어요. 홍범도 · 김좌진 장군을 기억하세요!", "📜 1945년 8월 15일 광복! 경성 거리가 만세 소리로 가득했어요. 마지막 결전이에요!"]
    }
  };'''

# ───────── 1. 최상위 상수 · 해설 표 ─────────
rep('''  var R38_ROAM_CAP = 4;''', '''  var R38_ROAM_CAP = 4;
  // [R38-2B] 주인공 동작 확장 상수 — 방향키 탭 유효 10틱 · 잔심 6틱 · 회피 무적 8틱 · 갈래 잠금 상한 90틱 · 시대별 연참 변주(전진량 · 잔상 · 먼지)
  var R38B_DIR_TAP = 10;
  var R38B_HOLD = 6;
  var R38B_DODGE_INV = 8;
  var R38B_BRLOCK_MAX = 90;
  var R38B_RUSH = { 1: { vx: 8, dust: 1 }, 2: { vx: 6 }, 3: { vx: 6, ghosts: 3 }, 4: { vx: 6 }, 5: { vx: 7, dust: 1 }, 6: { vx: 5 } };
''' + STORY)

# ───────── 2. 방향키 '탭' 시각 기록(자동 반복 제외) ─────────
rep('''        if (e.key === "ArrowLeft" || k === "a") {
          gameRef.current.keys.left = true;''', '''        if (e.key === "ArrowLeft" || k === "a") {
          if (!e.repeat) gameRef.current.keys._dirT = gameRef.current.tick; // [R38-2B] 방향키 탭(이동 갈래 판정)
          gameRef.current.keys.left = true;''')
rep('''        if (e.key === "ArrowRight" || k === "d") {
          gameRef.current.keys.right = true;''', '''        if (e.key === "ArrowRight" || k === "d") {
          if (!e.repeat) gameRef.current.keys._dirT = gameRef.current.tick; // [R38-2B]
          gameRef.current.keys.right = true;''')

# ───────── 3. 갈래 선택(◀/▶ 탭) · 공격 방향 기록 · 라벨 표 · 카운터 ─────────
rep('''          if (g.keys.up && !g.keys.down) br = "launch";
          else if (g.keys.down && !g.keys.up) br = "slam";''', '''          if (g.keys.up && !g.keys.down) br = "launch";
          else if (g.keys.down && !g.keys.up) br = "slam";
          else if (g.keys._dirT != null && g.tick - g.keys._dirT <= R38B_DIR_TAP) {
            // [R38-2B] 이동 갈래: 방향키를 막 누른 채 공격 — 공격하던 쪽이면 진격 베기 · 반대쪽이면 회피 베기(달리며 치는 평소 공격은 탭이 아니라 그대로)
            const tapDir = g.keys.right && !g.keys.left ? 1 : g.keys.left && !g.keys.right ? -1 : 0;
            if (tapDir) br = tapDir === (p._lastAtkDir || p.facing) ? "advance" : "retreat";
          }''')
rep('''      p.comboStep = p.comboStep % (g.stats.level >= SKILL_LV.finisher ? 4 : 3) + 1;
      p.comboResetTimer = 58;''', '''      p.comboStep = p.comboStep % (g.stats.level >= SKILL_LV.finisher ? 4 : 3) + 1;
      p.comboResetTimer = 58;
      p._lastAtkDir = p.facing; // [R38-2B] 이동 갈래(회피 베기)가 되돌아볼 공격 방향''')
rep('''    const R36_BR = { launch: [''', '''    const R36_BR = { advance: ["\\uC9C4\\uACA9 \\uBCA0\\uAE30!", "#f472b6"], retreat: ["\\uD68C\\uD53C \\uBCA0\\uAE30!", "#a78bfa"], launch: [''')
rep('''      L[kind]++;''', '''      L[kind] = (L[kind] || 0) + 1; // [R38-2B] 새 갈래 종류도 센다''')

# ───────── 4. r36Branch: advance · retreat 갈래(lunge 바로 앞) ─────────
rep('''      } else {
        p._atkSrc = "dash";''', '''      } else if (kind === "advance" || kind === "retreat") {
        // [R38-2B] 이동 갈래 — 진격 베기(전진 가속 · atk2) / 회피 베기(공격하던 쪽을 보며 뒤로 빠지고 짧은 무적 · atk1). 사슬은 이어진다(comboStep = min(N-1, pos)).
        //  콜백은 취소 가능(기본값) · 타이머 ≤ 18틱 — 피격 · 막기가 먼저 끊을 수 있고, 연참 · 내리꽂기 중에는 갈래 선택 자체가 막혀 있다
        const adv = kind === "advance";
        // 회피 베기는 공격하던 쪽(_lastAtkDir)을 본다 — 탭한 방향키가 아직 눌려 있으면 이동 코드가 facing을 되돌리므로 적중 순간에 한 번 더 맞춘다(_brDir)
        p._brDir = adv ? p.facing : p._lastAtkDir || p.facing;
        p.facing = p._brDir;
        p.comboStep = Math.min(N - 1, pos);
        p._atkSrc = "branch";
        p._fin = false;
        p.atkAnim = adv ? "atk2" : "atk1";
        p.maxAttackTimer = p.attackTimer = axe ? 18 : 14;
        p.vx = p.facing * (adv ? (g.era === 5 ? 16 : 14) : -9);
        if (!adv) p.invincibleTimer = Math.max(p.invincibleTimer || 0, R38B_DODGE_INV);
        for (let i = 1; i <= 2; i++) p.ghosts.push({ x: p.x - p.facing * (adv ? 1 : -1) * i * 18, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i, name: p._assetFrame, alpha: 0.5 - i * 0.15 });
        spawnDust(p.x - p.facing * (adv ? 14 : -14), p.z, g.era === 5 && adv ? 7 : 4, 2.6);
        sfx("dash", { v: adv ? 0.5 : 0.4 });
        (g.r38bBranch || (g.r38bBranch = { advance: 0, retreat: 0 }))[kind]++;
        queueActiveFrame(adv ? 5 : 4, () => {
          const g2 = gameRef.current;
          const pp = g2.player;
          if (pp._brDir) pp.facing = pp._brDir;
          g2._comboStep = Math.min(3, pos);
          g2._cutAng = adv ? 0.35 : -0.3;
          pushSlashFx(pp.x + pp.facing * (adv ? 90 : 60), pp.z - pp.y - 56, adv ? 0.3 : -0.25, pp.facing, { len: adv ? 300 : 220, w: adv ? 6 : 5, dur: 260, sparks: adv ? 6 : 4 });
          const hit = checkMeleeHitbox(adv ? 190 : 150, adv ? 62 : 56, (adv ? 1.4 : 1.1) + pos * 0.2, adv ? 9 : 5, adv ? 4 : 2, 1, false);
          g2._comboStep = 0;
          g2._cutAng = null;
          if (hit && adv) kickDirShake(g2, pp.facing, 6);
        });
      } else {
        p._atkSrc = "dash";''')

# ───────── 5. 피니시 플러리시 · 연참 변주 ─────────
rep('''        const isFinisher = step === 4;''', '''        const isFinisher = step === 4;
        r38bFlair(g, p, isFinisher || step === 3 && g.stats.level < SKILL_LV.finisher); // [R38-2B] 마지막 타 플러리시(잔상 · 잔심 · 시대별 FX)''')
rep('''      p.vx = p.facing * (last ? 30 : 5);''', '''      // [R38-2B] 시대별 연참 변주(R38B_RUSH): 전진량 · 잔상 · 먼지
      const RV = R38B_RUSH[g.era] || {};
      p.vx = p.facing * (last ? 30 : RV.vx || 5);
      if (!last) {
        if (RV.ghosts) for (let i = 1; i <= RV.ghosts; i++) p.ghosts.push({ x: p.x - p.facing * i * 20, z: p.z + (k % 2 ? -1 : 1) * i * 4, y: p.y, facing: p.facing, anim: "run", fi: i, name: p._assetFrame, alpha: 0.5 - i * 0.12 });
        if (RV.dust) spawnDust(p.x - p.facing * 18, p.z, 3, 2.2);
        g.r38bRushVar = (g.r38bRushVar || 0) + 1;
      }''')

# ───────── 6. 입력 잠금 감시 편입 · 플래그 ─────────
rep('''      if (p.bufferAtk) {
        p._bufT = (p._bufT || 0) + 1;''', '''      // [R38-2B] 갈래 잠금은 사슬이 끝나면 조용히 풀고(의미 없음), 사슬 중에도 90틱이 넘으면 기록하며 해제 · 잔심 자세(_r31pose)의 종료 틱이 180틱 넘게 멀면 해제
      if (p._brLock) {
        if (!(p.comboResetTimer > 0)) {
          p._brLock = false;
          p._brT0 = null;
        } else {
          if (p._brT0 == null) p._brT0 = g.tick;
          if (g.tick - p._brT0 > R38B_BRLOCK_MAX) {
            p._brLock = false;
            p._brT0 = null;
            r38LockNote(g, "brLock");
          }
        }
      } else p._brT0 = null;
      if (p._r31pose && p._r31pose.until > g.tick + 180) {
        p._r31pose = null;
        r38LockNote(g, "pose");
      }
      if (p.bufferAtk) {
        p._bufT = (p._bufT || 0) + 1;''')
rep('''bufferAtk: !!p.bufferAtk, downTimer: p.downTimer,''', '''bufferAtk: !!p.bufferAtk, brLock: !!p._brLock, pose: !!(p._r31pose && g.tick < p._r31pose.until), downTimer: p.downTimer,''')

# ───────── 7. 플러리시 · 서사 함수(r38Roam 앞) · 로밍 키 · 로그 · 서사 훅 ─────────
rep('''    const r38Roam = (g, p) => {''', '''    // [R38-2B] 피니시 플러리시 — 마지막 타 적중 순간: 잔상 3 · 히트스톱 · 방향 쉐이크 · 줌 1.04(8틱) · 마지막 프레임 6틱 잔심(_r31pose · 기존 자세 고정 기능) · 시대별 고정 풀 FX(할당 0)
    const r38bFlair = (g, p, fin) => {
      if (!fin || p.rush || p.plunge) return;
      const era = g.era;
      const C = R30C(g);
      g.r38bFlair = (g.r38bFlair || 0) + 1;
      for (let i = 1; i <= 3; i++) p.ghosts.push({ x: p.x - p.facing * i * 16, z: p.z, y: p.y, facing: p.facing, anim: "run", fi: i, name: p._assetFrame, alpha: 0.5 - i * 0.12 });
      g.hitStop = Math.max(g.hitStop, 3);
      kickDirShake(g, p.facing, 6);
      g.targetZoom = 1.04;
      addTimer(8, () => {
        gameRef.current.targetZoom = 1;
      });
      if (p._assetFrame && p.y <= 0) p._r31pose = { name: p._assetFrame, until: g.tick + R38B_HOLD, lift: 2 };
      const fx = p.x + p.facing * 70;
      const fy = p.z - p.y - 58;
      if (era === 1) {
        addShock(fx, p.z, "#d6a85a", 110, 14);
        spawnDust(fx - p.facing * 20, p.z, 8, 3);
      } else if (era === 2) {
        r38Hfx(23, fx, p.z, 420, p.facing, 0, 1.6, C[0], 0);
        pushRibbon({ h: 62, dx: 40, rx: 150, ry: 36, rot: -0.9, a0: Math.PI - 0.2, a1: 0.2, w: 14, dur: 300, col: C[1] });
      } else if (era === 3) {
        pushRibbon({ h: 60, dx: 30, rx: 130, ry: 34, rot: 0.6, a0: Math.PI + 0.3, a1: -0.3, w: 12, dur: 280, col: C[0] });
        pushRibbon({ h: 60, dx: 30, rx: 130, ry: 34, rot: -0.6, a0: 0.3, a1: Math.PI + 0.3, w: 12, dur: 280, col: C[1] });
        r38Hfx(24, fx, fy, 160, p.facing, Math.random() * TAU, 1.5, C[0], 12);
      } else if (era === 4) {
        r38Hfx(24, fx, fy, 160, p.facing, Math.random() * TAU, 1.6, C[0], 14);
        addShock(fx, p.z, C[0], 90, 12);
      } else if (era === 5) {
        r38Sparks(fx, fy, 18, p.facing, 520, "#fb923c", 1.4);
        spawnDust(fx - p.facing * 10, p.z, 7, 2.8);
        r38Hfx(23, fx, p.z, 360, p.facing, 0, 1.4, "#fde68a", 0);
      } else {
        r38Hfx(24, fx, fy, 150, p.facing, Math.random() * TAU, 1.4, C[0], 12);
        r38Sparks(fx, fy, 10, p.facing, 480, "#fde047", 1.2);
      }
    };
    // [R38-2B] 1.5배 구간 서사 — 로밍 지점 발동 직후: 주인공 위 매복 경고(70틱) → 30틱 뒤 단비 현장 해설(170틱). 시대당 지점마다 1회(era:zi:k) ·
    //  말풍선은 덮어쓰기라 겹치지 않음 · 모달 아님 · 입력 · 버퍼 · 일시정지와 무관(타이머는 게임 틱) · __RELIC_DEV.r38story()
    const r38bStory = (g, zi, k, n) => {
      const era = g.era;
      const T = (R38B_STORY[era] && R38B_STORY[era][zi] || [])[k] || null;
      const right = Math.min(2, n);
      const left = n >= 3 ? 1 : 0;
      const warn = n <= 0 ? "\\u26A0\\uFE0F \\uC8FC\\uBCC0\\uC5D0 \\uC801\\uC774 \\uC544\\uC9C1 \\uB0A8\\uC544 \\uC788\\uC5B4\\uC694!" : right && left ? "\\u26A0\\uFE0F \\uC55E\\uCABD \\uC99D\\uC6D0 \\xB7 \\uB4A4\\uCABD \\uB9E4\\uBCF5! \\uD3EC\\uC704\\uB418\\uC9C0 \\uC54A\\uAC8C \\uC790\\uB9AC\\uB97C \\uC7A1\\uC544\\uC694!" : right ? `\\u26A0\\uFE0F \\uC55E\\uCABD\\uC5D0\\uC11C \\uC99D\\uC6D0 ${right}\\uBA85\\uC774 \\uC640\\uC694!` : "\\u26A0\\uFE0F \\uB4A4\\uCABD \\uB9E4\\uBCF5! \\uB3CC\\uC544\\uC11C\\uC11C \\uB9C9\\uC544\\uC694!";
      setPlayerBubble(warn, 70);
      if (T) addTimer(30, () => setCompanionBubble(T, 170));
      const S = g.r38story || (g.r38story = { log: [] });
      S.last = { era, zone: zi, k, warn, text: T, tick: g.tick };
      S.log.push(S.last);
      if (S.log.length > 50) S.log.splice(0, S.log.length - 50);
    };
    const r38Roam = (g, p) => {''')
rep('''        const key = zi + ":" + k;''', '''        const key = g.era + ":" + zi + ":" + k; // [R38-2B] 시대별로 따로(R38-2A 결함: 1시대에서 쓴 지점이 남아 2시대부터 로밍이 안 떴다)''')
rep('''        (g.r38roamLog || (g.r38roamLog = [])).push({ zone: zi, k, x: Math.round(px), n, tick: g.tick });''', '''        (g.r38roamLog || (g.r38roamLog = [])).push({ era: g.era, zone: zi, k, x: Math.round(px), n, tick: g.tick });
        if (g.r38roamLog.length > 50) g.r38roamLog.splice(0, g.r38roamLog.length - 50);
        r38bStory(g, zi, k, n); // [R38-2B] 매복 경고 + 단비 현장 해설''')

# ───────── 8. 점검 훅 ─────────
rep('''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),''', '''          r35bgm: (cmd, arg) => sfxRef.current && sfxRef.current.bgm(cmd, arg),
          // [R38-2B] 검증: 서사(마지막 대사 · 로그 · 발동 키 · 지금 말풍선) · 동작 확장 카운터(갈래 · 플러리시 · 연참 변주)
          r38story: () => {
            const g = gameRef.current;
            const S = g.r38story || { log: [] };
            const cp = g.companion;
            const p = g.player;
            return { last: S.last || null, log: S.log.slice(), done: Object.assign({}, g.r38roam || {}), comp: { text: cp.bubbleText || null, timer: cp.bubbleTimer || 0 }, player: { text: p.bubbleText || null, timer: p.bubbleTimer || 0 }, tick: g.tick, texts: Object.keys(R38B_STORY).map((e) => [e, Object.values(R38B_STORY[e]).reduce((a, b) => a + b.length, 0)]) };
          },
          r38b: () => {
            const g = gameRef.current;
            return { branch: Object.assign({}, g.r38bBranch || {}), flair: g.r38bFlair || 0, rushVar: g.r38bRushVar || 0, dirT: g.keys._dirT, lastAtkDir: g.player._lastAtkDir, consts: { tap: R38B_DIR_TAP, hold: R38B_HOLD, inv: R38B_DODGE_INV, brMax: R38B_BRLOCK_MAX }, rush: R38B_RUSH };
          },''')

open(P, "w", encoding="utf-8").write(s)
print("R38-2B patch ok —", n, "edits")
